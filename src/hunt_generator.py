"""Generate bilingual nature hunts and render them to PDF."""
from __future__ import annotations

import datetime as dt
import logging
from pathlib import Path

from src.config import Config, get_config
from src.ollama_client import OllamaClient, ModelJSONError  # noqa: F401
from src.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.utils import validate_hunt, safe_filename
from src.tabpfn_filter import train_and_predict, fallback_allowed_types

logger = logging.getLogger(__name__)

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


class HuntGenerator:
    """Generate and render bilingual nature scavenger hunts."""

    def __init__(self, cfg: Config | None = None) -> None:
        """Initialize with a Config (loaded from disk if not given)."""
        self.cfg = cfg or get_config()
        self.client = OllamaClient(self.cfg)

    def generate(
        self,
        age: str,
        city: str,
        month: str,
        n: int | None = None,
        season_hint: str = "",
    ) -> dict:
        """Generate and validate a hunt for the given parameters."""
        n = n or self.cfg.hunt.default_item_count
        n = max(self.cfg.hunt.min_items, min(self.cfg.hunt.max_items, n))

        data_path = Path(self.cfg.paths.data_raw) / "weather_history.csv"
        try:
            allowed = train_and_predict(
                month=self._month_number(month),
                temp_c=25.0,
                rainfall_mm=50.0,
                humidity=60.0,
                data_path=data_path,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Seasonal filter failed: %s", exc)
            allowed = fallback_allowed_types()
        if not allowed:
            allowed = fallback_allowed_types()

        user = USER_PROMPT_TEMPLATE.format(
            age=age,
            city=city,
            month=month,
            lang="Hindi + English",
            n=n,
            season_hint=season_hint or "current season",
            allowed_types=", ".join(allowed),
        )
        result = self.client.generate_json(SYSTEM_PROMPT, user)
        validate_hunt(result, expected_items=n)
        return result

    def generate_pdf(self, hunt: dict, city: str, month: str) -> Path:
        """Render a validated hunt to a PDF and return the output path."""
        from src.pdf_builder import build_pdf

        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"kagaz_{safe_filename(city)}_{safe_filename(month)}_{stamp}.pdf"
        out = Path(self.cfg.paths.output_dir) / fname
        return build_pdf(hunt, out)

    @staticmethod
    def _month_number(name: str) -> int:
        """Map a month name or numeric string to 1..12; default to current month."""
        if not name:
            return dt.date.today().month
        text = str(name).strip()
        lower = text.lower()
        if lower in _MONTHS:
            return _MONTHS[lower]
        try:
            m = int(lower)
            if 1 <= m <= 12:
                return m
        except ValueError:
            pass
        return dt.date.today().month
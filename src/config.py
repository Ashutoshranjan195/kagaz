from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Load .env at import time; don't crash if missing
load_dotenv()


@dataclass(frozen=True)
class ModelConfig:
    name: str
    temperature: float
    timeout_seconds: int
    json_mode: bool
    max_retries: int
    host: str


@dataclass(frozen=True)
class PathsConfig:
    root: Path
    data_raw: Path
    data_processed: Path
    output_dir: Path
    assets_dir: Path
    fonts_dir: Path


@dataclass(frozen=True)
class HuntConfig:
    default_item_count: int
    min_items: int
    max_items: int


@dataclass(frozen=True)
class Config:
    model: ModelConfig
    paths: PathsConfig
    hunt: HuntConfig
    languages: tuple[str, ...]
    log_level: str


def _project_root() -> Path:
    """Return the project root directory (two levels up from this file)."""
    return Path(__file__).resolve().parent.parent


def _load_yaml(config_path: Path) -> dict:
    """Load and parse a YAML config file."""
    if not config_path.is_file():
        raise FileNotFoundError(
            f"Config file not found at expected location: {config_path}"
        )
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from YAML with environment variable overrides."""
    if config_path is None:
        config_path = _project_root() / "config.yaml"

    raw = _load_yaml(config_path)

    # Environment overrides with defaults
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model_name = os.getenv("MODEL_NAME", raw["model"]["name"])
    log_level = os.getenv("LOG_LEVEL", raw["logging"]["level"])

    root = _project_root()
    paths_cfg = PathsConfig(
        root=root,
        data_raw=root / raw["paths"]["data_raw"],
        data_processed=root / raw["paths"]["data_processed"],
        output_dir=root / raw["paths"]["output_dir"],
        assets_dir=root / raw["paths"]["assets_dir"],
        fonts_dir=root / raw["paths"]["fonts_dir"],
    )

    model_cfg = ModelConfig(
        name=model_name,
        temperature=raw["model"]["temperature"],
        timeout_seconds=raw["model"]["timeout_seconds"],
        json_mode=raw["model"]["json_mode"],
        max_retries=raw["model"]["max_retries"],
        host=ollama_host,
    )

    hunt_cfg = HuntConfig(
        default_item_count=raw["hunt"]["default_item_count"],
        min_items=raw["hunt"]["min_items"],
        max_items=raw["hunt"]["max_items"],
    )

    languages = tuple(raw["languages"])

    return Config(
        model=model_cfg,
        paths=paths_cfg,
        hunt=hunt_cfg,
        languages=languages,
        log_level=log_level,
    )


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Return cached configuration instance (loads once)."""
    return load_config()


def configure_logging(cfg: Config) -> None:
    """Configure root logger with level and format from config."""
    level = getattr(logging, cfg.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


if __name__ == "__main__":
    cfg = load_config()
    configure_logging(cfg)
    print(cfg)
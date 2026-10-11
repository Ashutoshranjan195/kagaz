from __future__ import annotations
import csv, random
from pathlib import Path

random.seed(42)

months_abbr = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]
ITEM_TYPES = ["spot","sound","smell","count","texture","collect_safe"]

# Seasonal probabilities per item type
# spot: ~0.75 all year
# sound: high Mar-May (~0.8), ~0.35 else
# smell: high Jun-Sep (~0.8), ~0.30 else
# count: ~0.55 all year
# texture: high Nov-Feb (~0.75), ~0.40 else
# collect_safe: high Oct-Dec (~0.8), ~0.35 else
prob_seen = {
    # spot - ~0.75 all year
    ("spot", 1): 0.75, ("spot", 2): 0.75, ("spot", 3): 0.75, ("spot", 4): 0.75,
    ("spot", 5): 0.75, ("spot", 6): 0.75, ("spot", 7): 0.75, ("spot", 8): 0.75,
    ("spot", 9): 0.75, ("spot", 10): 0.75, ("spot", 11): 0.75, ("spot", 12): 0.75,
    # sound - high Mar-May (~0.8), ~0.35 else
    ("sound", 1): 0.35, ("sound", 2): 0.35, ("sound", 3): 0.8, ("sound", 4): 0.8,
    ("sound", 5): 0.8, ("sound", 6): 0.35, ("sound", 7): 0.35, ("sound", 8): 0.35,
    ("sound", 9): 0.35, ("sound", 10): 0.35, ("sound", 11): 0.35, ("sound", 12): 0.35,
    # smell - high Jun-Sep (~0.8), ~0.30 else
    ("smell", 1): 0.3, ("smell", 2): 0.3, ("smell", 3): 0.3, ("smell", 4): 0.3,
    ("smell", 5): 0.3, ("smell", 6): 0.8, ("smell", 7): 0.8, ("smell", 8): 0.8,
    ("smell", 9): 0.8, ("smell", 10): 0.3, ("smell", 11): 0.3, ("smell", 12): 0.3,
    # count - ~0.55 all year
    ("count", 1): 0.55, ("count", 2): 0.55, ("count", 3): 0.55, ("count", 4): 0.55,
    ("count", 5): 0.55, ("count", 6): 0.55, ("count", 7): 0.55, ("count", 8): 0.55,
    ("count", 9): 0.55, ("count", 10): 0.55, ("count", 11): 0.55, ("count", 12): 0.55,
    # texture - high Nov-Feb (~0.75), ~0.40 else
    ("texture", 1): 0.4, ("texture", 2): 0.45, ("texture", 3): 0.4, ("texture", 4): 0.35,
    ("texture", 5): 0.3, ("texture", 6): 0.3, ("texture", 7): 0.3, ("texture", 8): 0.35,
    ("texture", 9): 0.75, ("texture", 10): 0.75, ("texture", 11): 0.75, ("texture", 12): 0.75,
    # collect_safe - high Oct-Dec (~0.8), ~0.35 else
    ("collect_safe", 1): 0.35, ("collect_safe", 2): 0.35, ("collect_safe", 3): 0.35,
    ("collect_safe", 4): 0.35, ("collect_safe", 5): 0.35, ("collect_safe", 6): 0.35,
    ("collect_safe", 7): 0.35, ("collect_safe", 8): 0.35, ("collect_safe", 9): 0.8,
    ("collect_safe", 10): 0.8, ("collect_safe", 11): 0.8, ("collect_safe", 12): 0.8,
}

rows = []
for month_idx, month_name in enumerate(months_abbr, 1):
    for item_type in ITEM_TYPES:
        base_prob = prob_seen.get((item_type, month_idx), 0.5)
        for _ in range(5):
            seen = 1 if random.random() < base_prob else 0
            # Add small uniform noise to weather params
            temp = round(20.0 + (month_idx - 6.5) * 2 + random.gauss(0, 1.5), 1)
            rainfall = round(max(0, 50 - month_idx * 4 + random.gauss(0, 10)), 1)
            humidity = round(max(0, 70 - month_idx * 3 + random.gauss(0, 5)), 1)
            day_length = round(12.0 - month_idx * 0.5 + random.gauss(0, 0.5), 1)
            rows.append([month_name, temp, rainfall, humidity, day_length, item_type, seen])

csv_path = Path("data/raw/weather_history.csv")
csv_path.parent.mkdir(parents=True, exist_ok=True)
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["month","avg_temp_c","rainfall_mm","humidity","day_length_hrs","item_type","seen"])
    writer.writerows(rows)
print(f"Generated {len(rows)} rows to {csv_path}")
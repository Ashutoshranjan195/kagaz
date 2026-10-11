import argparse
import sys
sys.path.insert(0, '.')
from src.config import get_config, configure_logging
from src.hunt_generator import HuntGenerator

parser = argparse.ArgumentParser(description="Kagaz hunt generator")
parser.add_argument("--city", default="Pune")
parser.add_argument("--age", default="6-8")
parser.add_argument("--month", default=None)
parser.add_argument("--n", default=6, type=int)
args = parser.parse_args()

if args.month is None:
    from datetime import datetime
    args.month = datetime.now().strftime("%B")

configure_logging(get_config())
gen = HuntGenerator(get_config())
hunt = gen.generate(args.age, args.city, args.month, args.n)
import json
print(json.dumps(hunt, indent=2))

pdf_path = gen.generate_pdf(hunt, args.city, args.month)
print(f"PDF saved to: {pdf_path}")

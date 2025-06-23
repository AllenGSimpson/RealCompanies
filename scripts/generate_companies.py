import csv
import unicodedata
import re
from pathlib import Path

# icons and backgrounds use fixed paths
ICON_PATH = "gfx/interface/icons/company_icons/custom_companies_placeholder.dds"

SRC = Path(__file__).resolve().parents[1]
CSV_PATH = SRC / 'companies.csv'
OUT_DIR = SRC / 'common' / 'company_types'
OUT_FILE = OUT_DIR / '00_real_companies_generated.txt'

# ensure output dir exists
OUT_DIR.mkdir(parents=True, exist_ok=True)

def slugify(name: str) -> str:
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ascii', 'ignore').decode('ascii')
    name = name.lower()
    name = name.replace('&', 'and')
    name = re.sub(r'[^a-z0-9]+', '_', name)
    name = re.sub(r'_+', '_', name)
    return name.strip('_')

def parse_industries(value: str | None):
    if not value:
        return []
    parts = [v.strip() for v in value.split(';') if v.strip()]
    return parts


def guess_background(buildings: list[str]) -> str:
    """Return a background name based on the building types."""
    lower = " ".join(buildings).lower()
    if any(word in lower for word in ["oil"]):
        return "comp_illu_oil_drills"
    if "plantation" in lower:
        return "comp_illu_plantation"
    if "farm" in lower:
        return "comp_illu_farm_wheat"
    if "mine" in lower:
        return "comp_illu_mining"
    if "railway" in lower:
        return "comp_illu_railways"
    if any(word in lower for word in ["shipyard", "port", "harbor"]):
        return "comp_illu_harbor_shipbuilding"
    if any(word in lower for word in [
        "steel", "motor", "arms", "artillery", "munition",
        "automotive", "military_shipyards", "power_plant",
    ]):
        return "comp_illu_manufacturing_heavy"
    return "comp_illu_manufacturing_light"

def main():
    rows = []
    with CSV_PATH.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Company'].startswith('#'):
                continue
            rows.append(row)

    with OUT_FILE.open('w', encoding='utf-8') as f:
        for row in rows:
            name = row['Company']
            primary = parse_industries(row['Primary Industries'])
            other = parse_industries(row.get('Other Industries', ''))
            slug = slugify(name)
            date = row.get('est. Date', '').strip()
            background = guess_background(primary + other)

            f.write(f"# {name}\n")
            f.write(f"company_{slug} = {{\n")
            f.write(f"    icon = \"{ICON_PATH}\"\n")
            f.write(
                f"    background = \"gfx/interface/icons/company_icons/company_backgrounds/{background}.dds\"\n"
            )
            if date:
                f.write(f"    # Founded {date}\n")
            f.write("    flavored_company = yes\n")
            if primary:
                f.write("    building_types = {\n")
                for b in primary:
                    f.write(f"        {b}\n")
                f.write("    }\n")
            if other:
                f.write("    extension_building_types = {\n")
                for b in other:
                    f.write(f"        {b}\n")
                f.write("    }\n")
            f.write("}\n\n")

if __name__ == '__main__':
    main()

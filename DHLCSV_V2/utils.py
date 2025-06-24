import csv
import os

MEMORY_DB = "data/sku_memory_db.csv"

def load_sku_memory():
    memory = {}
    if os.path.exists(MEMORY_DB):
        with open(MEMORY_DB, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = f"{row['SKU']}_{row['Brand']}_{row['Description']}".strip()
                memory[key] = {
                    "Country": row.get("Country", "").strip(),
                    "Weight": row.get("Weight", "").strip()
                }
    return memory

def save_sku_memory(sku, brand, desc, country=None, weight=None):
    key = f"{sku}_{brand}_{desc}".strip()
    updated = False
    rows = []

    if os.path.exists(MEMORY_DB):
        with open(MEMORY_DB, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_key = f"{row['SKU']}_{row['Brand']}_{row['Description']}".strip()
                if row_key == key:
                    if country:
                        row["Country"] = country
                    if weight:
                        row["Weight"] = weight
                    updated = True
                rows.append(row)

    if not updated:
        rows.append({
            "SKU": sku,
            "Brand": brand,
            "Description": desc,
            "Country": country or "",
            "Weight": weight or ""
        })

    with open(MEMORY_DB, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["SKU", "Brand", "Description", "Country", "Weight"])
        writer.writeheader()
        writer.writerows(rows)
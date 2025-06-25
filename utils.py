import csv
import os
import re

MEMORY_DB = "data/sku_memory_db.csv"

def get_default_weight(item_description):
    """Estimate default weight based on item description keywords"""
    desc_lower = item_description.lower()
    
    # Weight categories in kg
    if any(word in desc_lower for word in ['shoe', 'boot', 'sneaker', 'footwear']):
        return 1.3
    elif any(word in desc_lower for word in ['jacket', 'coat', 'blazer']):
        return 1.5
    elif any(word in desc_lower for word in ['shirt', 'pants', 'dress', 'skirt', 'trouser', 'jeans', 'sweater', 'hoodie']):
        return 0.7
    elif any(word in desc_lower for word in ['belt', 'wallet', 'bag', 'purse', 'accessory', 'jewelry', 'watch']):
        return 0.3
    else:
        return 0.5  # Default fallback

def find_best_match(sku, brand, item_description, memory_data):
    """Find the best matching record using priority: Full SKU > Partial keyword > Brand"""
    desc_lower = item_description.lower()
    
    # Priority 1: Full SKU match
    for record in memory_data:
        if record['SKU'] and record['SKU'].strip() == sku.strip():
            return record
    
    # Priority 2: Partial keyword match in Item Description
    desc_words = re.findall(r'\b\w+\b', desc_lower)
    best_match = None
    best_score = 0
    
    for record in memory_data:
        if not record['Item Description']:
            continue
            
        record_desc_lower = record['Item Description'].lower()
        record_words = re.findall(r'\b\w+\b', record_desc_lower)
        
        # Calculate match score based on common words
        common_words = set(desc_words) & set(record_words)
        if len(common_words) > 0:
            score = len(common_words) / max(len(desc_words), len(record_words))
            if score > best_score and score > 0.3:  # Minimum 30% match threshold
                best_score = score
                best_match = record
    
    if best_match:
        return best_match
    
    # Priority 3: Brand match (least reliable)
    for record in memory_data:
        if record['Brand'] and record['Brand'].strip().lower() == brand.strip().lower():
            return record
    
    return None

def load_sku_memory():
    """Load memory database with enhanced format"""
    memory_data = []
    if os.path.exists(MEMORY_DB):
        with open(MEMORY_DB, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                memory_data.append({
                    'SKU': row.get('SKU', '').strip(),
                    'Brand': row.get('Brand', '').strip(),
                    'Item Description': row.get('Item Description', '').strip(),
                    'Commodity Code': row.get('Commodity Code', '').strip(),
                    'Weight': row.get('Weight', '').strip(),
                    'Country of Origin': row.get('Country of Origin', '').strip()
                })
    return memory_data

def save_sku_memory(sku, brand, item_description, commodity_code=None, weight=None, country=None):
    """Save memory with enhanced format including commodity code"""
    rows = []
    updated = False
    
    # Load existing data
    if os.path.exists(MEMORY_DB):
        with open(MEMORY_DB, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Check if this is the same item
                if (row.get('SKU', '').strip() == sku.strip() and 
                    row.get('Brand', '').strip() == brand.strip() and
                    row.get('Item Description', '').strip() == item_description.strip()):
                    
                    # Update existing record
                    if commodity_code:
                        row['Commodity Code'] = commodity_code
                    if weight:
                        row['Weight'] = weight
                    if country:
                        row['Country of Origin'] = country
                    updated = True
                
                rows.append(row)
    
    # Add new record if not found
    if not updated:
        rows.append({
            'SKU': sku,
            'Brand': brand,
            'Item Description': item_description,
            'Commodity Code': commodity_code or '',
            'Weight': weight or '',
            'Country of Origin': country or ''
        })
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(MEMORY_DB), exist_ok=True)
    
    # Write back to file
    with open(MEMORY_DB, "w", newline="", encoding="utf-8") as f:
        fieldnames = ['SKU', 'Brand', 'Item Description', 'Commodity Code', 'Weight', 'Country of Origin']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def get_memory_values(sku, brand, item_description):
    """Get memory values for an item using enhanced matching logic"""
    memory_data = load_sku_memory()
    match = find_best_match(sku, brand, item_description, memory_data)
    
    if match:
        return {
            'commodity_code': match.get('Commodity Code', ''),
            'weight': match.get('Weight', ''),
            'country': match.get('Country of Origin', '')
        }
    
    # Return default weight if no match found
    return {
        'commodity_code': '',
        'weight': str(get_default_weight(item_description)),
        'country': ''
    }
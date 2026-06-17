import math

def to_desi(amount: float, unit: str) -> str:
    unit_clean = unit.lower().strip()
    
    # If the amount is 0 or None
    if not amount:
        return ""
        
    # Check count-based units
    if unit_clean in ["clove", "cloves", "piece", "pieces", "slice", "slices", "pcs", "pc"]:
        return f"{amount} adad (عدد)"
    if unit_clean in ["pinch", "pinches", "chutki"]:
        return f"{amount} chutki (چٹکی)"
    if unit_clean in ["cup", "cups", "pyali"]:
        return f"{amount} pyali (پیالی)"
    if unit_clean in ["tbsp", "tablespoon", "tablespoons"]:
        return f"{amount} کھانے کا چمچ (tbsp)"
    if unit_clean in ["tsp", "teaspoon", "teaspoons"]:
        return f"{amount} چائے کا چمچ (tsp)"
        
    # Standardize weights to grams
    grams = None
    if unit_clean in ["g", "gram", "grams"]:
        grams = amount
    elif unit_clean in ["kg", "kilogram", "kilograms"]:
        grams = amount * 1000
    elif unit_clean in ["oz", "ounce", "ounces"]:
        grams = amount * 28.35
    elif unit_clean in ["lb", "pound", "pounds"]:
        grams = amount * 453.6
        
    if grams is not None:
        if grams >= 1000:
            ser = round(grams / 1000, 2)
            return f"{ser} Ser (سیر / کلو)"
        elif grams >= 250:
            pau = round(grams / 250, 2)
            return f"{pau} Pau (پاؤ)"
        elif grams >= 60:
            chattank = round(grams / 60, 2)
            return f"{chattank} Chattank (چھٹانک)"
        elif grams >= 12:
            tola = round(grams / 12, 2)
            return f"{tola} Tola (تولہ)"
        else:
            return f"{round(grams, 1)} g (گرام)"
            
    # Standardize volume to milliliters
    ml = None
    if unit_clean in ["ml", "milliliter", "milliliters"]:
        ml = amount
    elif unit_clean in ["l", "liter", "liters"]:
        ml = amount * 1000
    elif unit_clean in ["fl oz", "fluid ounce", "fluid ounces"]:
        ml = amount * 29.57
        
    if ml is not None:
        if ml >= 250:
            cups = round(ml / 250, 2)
            return f"{cups} pyali (پیالی)"
        elif ml >= 15:
            tbsp = round(ml / 15, 2)
            return f"{tbsp} کھانے کا چمچ (tbsp)"
        else:
            tsp = round(ml / 5, 2)
            return f"{tsp} چائے کا چمچ (tsp)"
            
    return f"{amount} {unit}"

def format_ingredient(ing: dict) -> dict:
    """
    Takes a Spoonacular-like ingredient dict and returns a formatted dictionary with:
    - name: string
    - metric: formatted string
    - us: formatted string
    - desi: formatted string
    """
    name = ing.get("name", "").capitalize()
    
    # Check if we have measures (Spoonacular format)
    measures = ing.get("measures")
    if measures:
        metric_val = measures.get("metric", {})
        us_val = measures.get("us", {})
        
        m_amount = metric_val.get("amount", ing.get("amount"))
        m_unit = metric_val.get("unitShort", ing.get("unit", ""))
        
        u_amount = us_val.get("amount", ing.get("amount"))
        u_unit = us_val.get("unitShort", ing.get("unit", ""))
    else:
        # Default fallback
        m_amount = ing.get("amount")
        m_unit = ing.get("unit", "")
        u_amount = m_amount
        u_unit = m_unit
        
    # Format Metric string
    if m_amount:
        m_amount_str = f"{round(m_amount, 2):.2f}".rstrip('0').rstrip('.')
        metric_str = f"{m_amount_str} {m_unit}"
    else:
        metric_str = ing.get("original", name)
        
    # Format US string
    if u_amount:
        u_amount_str = f"{round(u_amount, 2):.2f}".rstrip('0').rstrip('.')
        us_str = f"{u_amount_str} {u_unit}"
    else:
        us_str = metric_str
        
    # Format Desi string
    if m_amount:
        desi_str = to_desi(m_amount, m_unit)
    else:
        desi_str = metric_str
        
    return {
        "name": name,
        "metric": metric_str,
        "us": us_str,
        "desi": desi_str,
        "original": ing.get("original", f"{metric_str} {name}")
    }

import json
from utils.openai_client import get_openai_client

def present_recipe(masterclass: dict, preferences: dict = None) -> dict:
    if preferences is None:
        preferences = {}
        
    output_language = preferences.get("output_language", "english")
    
    title = masterclass.get("recipe_title", "Unknown Recipe")
    ingredients = masterclass.get("ingredients", [])
    
    # 1. Always call OpenAI for Urdu translation for Title + Ingredients
    try:
        client = get_openai_client()
        system_prompt = (
            "You are a translator. Translate the recipe title and ingredient list to Urdu script. "
            "Return ONLY JSON: {\"title_urdu\": \"...\", \"ingredients_urdu\": [\"...\"]}"
        )
        user_prompt = f"Title: {title}\nIngredients: {', '.join(ingredients)}"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        translation = json.loads(content.strip())
        title_urdu = translation.get("title_urdu", title)
        ingredients_urdu = translation.get("ingredients_urdu", [])
    except Exception:
        title_urdu = title
        ingredients_urdu = []

    # 2. Phase Translation Logic based on output_language
    phases = masterclass.get("phases", [])
    show_urdu = False
    instructions_english_hidden = False
    
    if output_language == "english":
        show_urdu = False
    elif output_language in ["both", "urdu"]:
        show_urdu = True
        if output_language == "urdu":
            instructions_english_hidden = True
            
        try:
            client = get_openai_client()
            for phase in phases:
                system_prompt = "Translate these cooking instructions to Urdu script. Keep ingredient names recognizable. Return ONLY the translated text."
                user_prompt = phase.get("what_to_do", "")
                
                if user_prompt:
                    resp = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ]
                    )
                    phase["instructions_urdu"] = resp.choices[0].message.content.strip()
        except Exception:
            pass

    # 3. Estimate cost
    servings = masterclass.get("servings", 1)
    base_cost = 100
    protein_cost = 0
    rice_cost = 0
    
    ingredients_lower = " ".join(ingredients).lower()
    if "chicken" in ingredients_lower:
        protein_cost = 150
    elif "beef" in ingredients_lower or "mutton" in ingredients_lower:
        protein_cost = 200
        
    if "rice" in ingredients_lower:
        rice_cost = 50
        
    total_cost = (base_cost + protein_cost + rice_cost) * servings
    
    # 4. Difficulty
    total_time = masterclass.get("total_time", 0)
    if total_time < 25:
        difficulty = "Easy"
    elif total_time < 45:
        difficulty = "Medium"
    else:
        difficulty = "Hard"
        
    return {
        "output_language": output_language,
        "show_urdu": show_urdu,
        "instructions_english_hidden": instructions_english_hidden,
        "recipe_title": title,
        "title_urdu": title_urdu,
        "phases": phases,
        "ingredients": ingredients,
        "ingredients_urdu": ingredients_urdu,
        "estimated_cost": f"Rs. {total_cost}",
        "cooking_time": f"{total_time} minutes",
        "servings": servings,
        "difficulty": difficulty,
        "grocery_list": ingredients
    }

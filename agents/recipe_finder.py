import json
from utils.spoonacular import SpoonacularClient
from utils.openai_client import get_openai_client

def find_recipes(ingredients: list, preferences: dict = None) -> list:
    if preferences is None:
        preferences = {}
        
    cuisine = preferences.get("cuisine", "Pakistani,Indian")
    diet = preferences.get("diet", None)
    number = preferences.get("number", 8)
    
    try:
        spoonacular = SpoonacularClient()
        search_results = spoonacular.search_recipes(
            ingredients=ingredients,
            cuisine=cuisine,
            diet=diet,
            number=number
        )
        
        if search_results:
            enriched_recipes = []
            for recipe in search_results:
                details = spoonacular.get_recipe_details(recipe.get("id"))
                if not details:
                    continue
                
                enriched_recipe = {
                    "id": details.get("id"),
                    "title": details.get("title"),
                    "readyInMinutes": details.get("readyInMinutes"),
                    "servings": details.get("servings"),
                    "summary": details.get("summary"),
                    "analyzedInstructions": details.get("analyzedInstructions", []),
                    "nutrition": details.get("nutrition", {}),
                    "extendedIngredients": details.get("extendedIngredients", [])
                }
                enriched_recipes.append(enriched_recipe)
                
            if enriched_recipes:
                return enriched_recipes
            
        # Fallback to OpenAI if Spoonacular returns 0 results (or if details failed)
        client = get_openai_client()
        system_prompt = "You are a Pakistani/South Asian recipe expert."
        user_prompt = f"Suggest 3 simple Pakistani recipes using these ingredients: {ingredients}. Return ONLY a JSON array with fields: title, readyInMinutes, ingredients, steps (array of strings)."
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up markdown JSON blocks if present
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        ai_recipes = json.loads(content.strip())
        
        if isinstance(ai_recipes, list):
            for r in ai_recipes:
                r["source"] = "ai_fallback"
            return ai_recipes
        elif isinstance(ai_recipes, dict):
            # Try to extract from a generic key like 'recipes'
            for key in ai_recipes:
                if isinstance(ai_recipes[key], list):
                    for r in ai_recipes[key]:
                        if isinstance(r, dict):
                            r["source"] = "ai_fallback"
                    return ai_recipes[key]
                    
        return []
        
    except Exception as e:
        print(f"Error finding recipes: {e}")
        return []

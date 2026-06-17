import json
from dotenv import load_dotenv

from agents.ingredient_parser import parse_ingredients
from agents.recipe_finder import find_recipes
from agents.recipe_personalizer import personalize_recipes
from agents.recipe_teacher import generate_masterclass

load_dotenv()

def run_smoke_test():
    print("--- 1. Testing parse_ingredients ---")
    parsed = parse_ingredients("chicken, tomatoes, rice")
    print(json.dumps(parsed, indent=2))
    
    ingredients = parsed.get("ingredients", [])
    if not ingredients:
        print("Parsing failed. Exiting.")
        return
        
    print("\n--- 2. Testing find_recipes ---")
    recipes = find_recipes(ingredients)
    print(f"Found {len(recipes)} recipes.")
    
    print("\n--- 3. Testing personalize_recipes ---")
    prefs = {"spice_level": "medium", "max_time_minutes": 45}
    top_recipes = personalize_recipes(recipes, prefs)
    for i, r in enumerate(top_recipes):
        print(f"{i+1}. {r.get('title')} - Score: {r.get('personalization_score')}")
        
    if not top_recipes:
        print("No top recipes. Exiting.")
        return
        
    print("\n--- 4. Testing generate_masterclass ---")
    masterclass = generate_masterclass(top_recipes[0])
    print(f"Generated {len(masterclass.get('phases', []))} phases for {masterclass.get('recipe_title')}")
    print(json.dumps(masterclass, indent=2))
    
if __name__ == "__main__":
    run_smoke_test()

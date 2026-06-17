import os
import json
from utils.openai_client import get_openai_client

def generate_masterclass(recipe: dict) -> dict:
    try:
        # Extract steps
        analyzed = recipe.get("analyzedInstructions", [])
        steps = []
        if analyzed and len(analyzed) > 0:
            steps_list = analyzed[0].get("steps", [])
            for step in steps_list:
                steps.append(f"{step.get('number', '')}: {step.get('step', '')}")
        else:
            steps = recipe.get("steps", []) # Handle AI fallback format
            if not steps:
                steps = ["1: No steps provided."]
            
        steps_str = "\n".join(str(s) for s in steps)
        
        # Load or use inline system prompt
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "teacher_prompt.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read()
        else:
            system_prompt = (
                "You are a masterclass Pakistani cooking mentor. Transform recipe steps into a teaching timeline.\n"
                "For each logical cooking phase, return a JSON object with this structure:\n"
                "{\n"
                "  \"phases\": [\n"
                "    {\n"
                "      \"phase_number\": 1,\n"
                "      \"phase_name\": \"The Base Aromatics (Bhoona)\",\n"
                "      \"technique\": \"Caramelization\",\n"
                "      \"what_to_do\": \"...\",\n"
                "      \"the_lesson\": \"...\",\n"
                "      \"sensory_cue\": \"...\",\n"
                "      \"common_mistake\": \"...\",\n"
                "      \"panic_fix\": \"...\"\n"
                "    }\n"
                "  ]\n"
                "}\n"
                "Group steps into 3–5 phases. Use Desi cooking vocabulary (Bhoona, Dum, Roghan, Tadka). Return ONLY valid JSON."
            )
            
        client = get_openai_client()
        user_prompt = f"Recipe: {recipe.get('title', 'Unknown')}\nSteps: {steps_str}"
        
        response = client.chat.completions.create(
            model="gpt-4o",
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
            
        masterclass = json.loads(content.strip())
        
    except Exception as e:
        # Fallback if parsing fails
        masterclass = {
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Preparation and Cooking",
                    "technique": "General",
                    "what_to_do": "\n".join(str(s) for s in steps) if 'steps' in locals() else "Follow recipe steps.",
                    "the_lesson": "Take your time and follow the instructions.",
                    "sensory_cue": "Smells delicious.",
                    "common_mistake": "Rushing the process.",
                    "panic_fix": "Turn down the heat and assess."
                }
            ]
        }
        
    # Append required fields
    masterclass["recipe_title"] = recipe.get("title", "Unknown Recipe")
    masterclass["total_time"] = recipe.get("readyInMinutes", 0)
    masterclass["servings"] = recipe.get("servings", 1)
    
    # Handle both Spoonacular (extendedIngredients) and AI fallback (ingredients)
    extended_ingredients = recipe.get("extendedIngredients", [])
    from utils.measurement_converter import format_ingredient
    if extended_ingredients:
        masterclass["ingredients"] = [i.get("original", i.get("name", "")) for i in extended_ingredients]
        masterclass["ingredients_detailed"] = [format_ingredient(i) for i in extended_ingredients]
    else:
        raw_ings = recipe.get("ingredients", [])
        masterclass["ingredients"] = []
        masterclass["ingredients_detailed"] = []
        for ing in raw_ings:
            if isinstance(ing, dict):
                masterclass["ingredients"].append(f"{ing.get('amount', '')} {ing.get('unit', '')} {ing.get('name', '')}".strip())
                masterclass["ingredients_detailed"].append(format_ingredient(ing))
            else:
                masterclass["ingredients"].append(str(ing))
                masterclass["ingredients_detailed"].append(format_ingredient({"name": str(ing)}))
        
    return masterclass

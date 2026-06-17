import json
from utils.openai_client import get_openai_client

def get_panic_fix(phase: dict, problem_description: str) -> dict:
    try:
        client = get_openai_client()
        phase_name = phase.get("phase_name", "Unknown Phase")
        technique = phase.get("technique", "Unknown Technique")
        
        system_prompt = (
            "You are an expert Pakistani cooking troubleshooter. The user is mid-cook and something went wrong.\n"
            "Given the current cooking phase context and the problem, provide:\n"
            "1. What went wrong (the science/reason, 1–2 sentences)\n"
            "2. An immediate fix (clear actionable steps)\n"
            "3. How to prevent it next time (1 sentence)\n"
            "Return ONLY JSON: {\"what_went_wrong\": \"...\", \"immediate_fix\": \"...\", \"prevention\": \"...\"}"
        )
        
        user_prompt = f"Current phase: {phase_name} — Technique: {technique}\nUser's problem: {problem_description}"
        
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
            
        return json.loads(content.strip())
        
    except Exception:
        return {
            "what_went_wrong": "Unknown issue",
            "immediate_fix": "Reduce heat and stir gently. Add a splash of water if sticking.",
            "prevention": "Monitor heat closely during this phase."
        }

def get_common_problems(phase_name: str) -> list:
    name_lower = phase_name.lower()
    
    if "aromatics" in name_lower or "bhoona" in name_lower:
        return ["Onions are burning", "Onions won't brown", "Oil is smoking"]
    elif "activating" in name_lower or "spices" in name_lower:
        return ["Spices are sticking to pan", "Bitter taste", "Spices burnt"]
    elif "gravy" in name_lower:
        return ["Yogurt curdled", "Gravy is watery", "Oil not separating"]
    elif "protein" in name_lower or "meat" in name_lower or "chicken" in name_lower:
        return ["Meat is tough", "Chicken is dry", "Undercooked inside"]
    else:
        return ["Too salty", "Too spicy", "Burnt smell"]

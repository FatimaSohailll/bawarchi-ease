import json
import base64
import re
from utils.openai_client import get_openai_client

def parse_ingredients(user_input: str, image_bytes: bytes = None) -> dict:
    try:
        client = get_openai_client()
        
        if image_bytes:
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": 'Look at this image of a pantry or fridge. List every visible food ingredient. Return ONLY a JSON object like: {"ingredients": ["item1", "item2"]}'
                            },
                            {
                                "type": "image_url", 
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            )
            content = response.choices[0].message.content
        elif user_input:
            has_urdu_script = bool(re.search(r'[\u0600-\u06FF]', user_input))
            
            if has_urdu_script:
                system_prompt = (
                    "You are a translator and ingredient extractor. The user has written in Urdu script.\n"
                    "Translate to English and extract only food ingredients.\n"
                    "Return ONLY JSON: {\"ingredients\": [\"item1\", \"item2\"]}"
                )
            else:
                system_prompt = (
                    "You are a Pakistani cooking assistant and ingredient extractor.\n"
                    "The user may write in English or Roman Urdu (Urdu words in Latin script,\n"
                    "e.g. 'tamatar', 'dahi', 'gosht', 'murgh', 'pyaz').\n"
                    "Regardless of the input language, extract all food ingredients and return\n"
                    "their standard English names.\n"
                    "Return ONLY JSON: {\"ingredients\": [\"item1\", \"item2\"]}"
                )
                
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            content = response.choices[0].message.content
        else:
            return {"ingredients": []}

        # Clean up markdown JSON blocks if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        return json.loads(content.strip())
        
    except Exception as e:
        raise e


import os
import requests
from dotenv import load_dotenv

class SpoonacularClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("SPOONACULAR_API_KEY")
        if not self.api_key:
            raise ValueError("SPOONACULAR_API_KEY is missing from the environment. Please check your .env file.")
        self.base_url = "https://api.spoonacular.com/recipes"

    def search_recipes(self, ingredients: list, cuisine="Pakistani,Indian", diet=None, number=10):
        url = f"{self.base_url}/complexSearch"
        params = {
            "apiKey": self.api_key,
            "includeIngredients": ",".join(ingredients),
            "cuisine": cuisine,
            "number": number,
            "addRecipeNutrition": "true"
        }
        if diet:
            params["diet"] = diet

        try:
            response = requests.get(url, params=params)
            if response.status_code == 402:
                print("Warning: Spoonacular API quota exceeded (402).")
                return []
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching recipes: {e}")
            return []

    def get_recipe_details(self, recipe_id: int):
        url = f"{self.base_url}/{recipe_id}/information"
        params = {"apiKey": self.api_key}
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 402:
                print("Warning: Spoonacular API quota exceeded (402).")
                return {}
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching recipe details: {e}")
            return {}

    def test_connection(self):
        url = f"{self.base_url}/complexSearch"
        params = {"apiKey": self.api_key, "query": "chicken", "number": 1}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            print("Spoonacular OK")
        except requests.exceptions.RequestException as e:
            print(f"Error testing connection: {e}")

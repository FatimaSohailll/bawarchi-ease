def personalize_recipes(recipes: list, preferences: dict) -> list:
    if not preferences:
        preferences = {}
        
    # Extract preferences with defaults
    family_size = preferences.get("family_size", 4)
    spice_level = preferences.get("spice_level", "medium")
    max_time_minutes = preferences.get("max_time_minutes", 45)
    budget = preferences.get("budget", "medium")
    dietary_restrictions = preferences.get("dietary_restrictions", [])
    disliked_ingredients = preferences.get("disliked_ingredients", [])
    last_meals = preferences.get("last_meals", [])
    
    scored_recipes = []
    
    for recipe in recipes:
        score = 0
        
        # 1. time_score (30 pts)
        ready_in = recipe.get("readyInMinutes")
        if ready_in is None:
            ready_in = max_time_minutes # Assume it fits if not provided
            
        if ready_in <= max_time_minutes:
            time_score = 30
        else:
            excess = ready_in - max_time_minutes
            penalty = (excess / max_time_minutes) * 30 if max_time_minutes > 0 else 30
            time_score = max(0, 30 - penalty)
        score += time_score
        
        # 2. spice_score (20 pts)
        spice_keywords = ["chilli", "chili", "jalapeno", "hot", "spicy", "cayenne", "pepper"]
        text_to_check = str(recipe.get("title", "")).lower() + " " + str(recipe.get("summary", "")).lower()
        has_spice = any(kw in text_to_check for kw in spice_keywords)
        
        spice_score = 0
        if spice_level == "spicy":
            spice_score = 20 if has_spice else 0
        elif spice_level == "mild":
            spice_score = 20 if not has_spice else 0
        else:
            spice_score = 20 # medium gets full points as default
            
        score += spice_score
        
        # 3. diet_score (20 pts)
        diet_score = 20
        # Handle both Spoonacular format (extendedIngredients) and AI fallback format (ingredients array of strings)
        ingredients = recipe.get("extendedIngredients", [])
        if not ingredients and recipe.get("ingredients"):
            ing_strings = [str(i).lower() for i in recipe.get("ingredients", [])]
        else:
            ing_strings = [str(i.get("name", "")).lower() for i in ingredients]
            
        for disliked in disliked_ingredients:
            if any(disliked.lower() in ing for ing in ing_strings):
                diet_score = 0
                break
                
        # Hard filter if diet_score is 0 (hard dislike violation)
        if diet_score == 0:
            continue
            
        score += diet_score
        
        # 4. variety_score (15 pts)
        title = recipe.get("title", "").lower()
        if any(last_meal.lower() == title for last_meal in last_meals):
            variety_score = 0
        else:
            variety_score = 15
        score += variety_score
        
        # 5. popularity_score (15 pts)
        spoonacular_score = recipe.get("spoonacularScore", 0)
        popularity_score = (spoonacular_score / 100.0) * 15 if spoonacular_score else 0
        score += popularity_score
        
        # Determine top reason
        reasons = []
        if time_score == 30:
            reasons.append((30, f"This recipe fits perfectly within your {max_time_minutes}-minute time limit."))
        if spice_level == "spicy" and spice_score == 20:
            reasons.append((20, "This has the spicy kick you requested."))
        elif spice_level == "mild" and spice_score == 20:
            reasons.append((20, "This is a nice, mild dish just the way you like it."))
        if variety_score == 15 and last_meals:
            reasons.append((15, "This brings some fresh variety to your recent meals."))
            
        if reasons:
            reasons.sort(key=lambda x: x[0], reverse=True)
            why_recommended = reasons[0][1]
        else:
            why_recommended = "A fantastic match for your dietary preferences and taste."
            
        recipe["personalization_score"] = round(score, 1)
        recipe["why_recommended"] = why_recommended
        scored_recipes.append(recipe)
        
    scored_recipes.sort(key=lambda x: x["personalization_score"], reverse=True)
    return scored_recipes[:3]

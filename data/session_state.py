import json
import streamlit as st

def save_preferences_to_browser(preferences: dict):
    """
    Serializes and saves the allowed preference fields to URL query params
    as a workaround for Streamlit iframe limitations with localStorage.
    """
    allowed_keys = {
        "family_size", "spice_level", "max_time_minutes", "budget",
        "dietary_restrictions", "disliked_ingredients", "cuisine", "diet", "number", "output_language"
    }
    persisted = {k: v for k, v in preferences.items() if k in allowed_keys}
    st.query_params["prefs"] = json.dumps(persisted)

def load_preferences_from_browser():
    """Loads preferences from the 'prefs' URL query parameter."""
    raw = st.query_params.get("prefs", None)
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            return None
    return None

def load_or_default_preferences() -> dict:
    """
    Merges any preferences loaded from the browser into the current session state.
    Missing keys retain their default values.
    """
    loaded = load_preferences_from_browser()
    if loaded and isinstance(loaded, dict):
        for k, v in loaded.items():
            st.session_state["preferences"][k] = v
            
    return st.session_state["preferences"]

def init_session_state():
    """
    Initializes the Streamlit session state, setting up default preferences
    and transient session-only variables.
    """
    # 1. Setup default preferences
    if "preferences" not in st.session_state:
        st.session_state["preferences"] = {
            "family_size": 4,
            "spice_level": "medium",
            "max_time_minutes": 45,
            "budget": "medium",
            "dietary_restrictions": [],
            "disliked_ingredients": [],
            "cuisine": "Pakistani,Indian",
            "diet": None,
            "number": 8,
            "output_language": "english"
        }
        # Call on first load to restore preferences automatically
        load_or_default_preferences()

    # 2. Setup session-only variables (Not Persisted)
    session_only_defaults = {
        "ingredients": [],
        "recipes": [],
        "selected_recipe": None,
        "masterclass": None,
        "presented_card": None,
        "current_phase_index": 0,
        "last_meals": []
    }
    
    for key, default_val in session_only_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_val

def save_to_last_meals(title: str):
    """Appends a title to last_meals, keeping only the last 5."""
    if "last_meals" not in st.session_state:
        st.session_state["last_meals"] = []
    meals = st.session_state["last_meals"]
    meals.append(title)
    if len(meals) > 5:
        st.session_state["last_meals"] = meals[-5:]

def get_current_phase() -> dict:
    """Returns the current phase dict from the masterclass, or None."""
    masterclass = st.session_state.get("masterclass")
    if masterclass and "phases" in masterclass:
        phases = masterclass["phases"]
        idx = st.session_state.get("current_phase_index", 0)
        if 0 <= idx < len(phases):
            return phases[idx]
    return None

def advance_phase():
    """Increments current_phase_index up to the last phase."""
    masterclass = st.session_state.get("masterclass")
    if masterclass and "phases" in masterclass:
        max_idx = len(masterclass["phases"]) - 1
        current = st.session_state.get("current_phase_index", 0)
        if current < max_idx:
            st.session_state["current_phase_index"] = current + 1

def reset_cooking_session():
    """Resets phase index to 0 and clears masterclass and presented card."""
    st.session_state["current_phase_index"] = 0
    st.session_state["masterclass"] = None
    st.session_state["presented_card"] = None

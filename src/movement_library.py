import json
import os
from typing import Dict, List, Optional, Any

def get_movements_directory() -> str:
    """Get the path to the movements directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "..", "data", "movements")

def load_movement_categories() -> Dict[str, Dict[str, str]]:
    """Load movement categories from index.json."""
    movements_dir = get_movements_directory()
    index_path = os.path.join(movements_dir, "index.json")
    
    try:
        with open(index_path, 'r') as f:
            data = json.load(f)
            return data.get("categories", {})
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def load_movement(movement_name: str) -> Optional[Dict[str, Any]]:
    """Load a specific movement definition."""
    movements_dir = get_movements_directory()
    filename = f"{movement_name.lower().replace(' ', '-').replace('/', '-')}.json"
    
    # Try to find the movement in any category subdirectory
    categories = ["weightlifting", "gymnastics", "monostructural", "cardio"]
    
    for category in categories:
        movement_path = os.path.join(movements_dir, category, filename)
        try:
            with open(movement_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            continue
        except json.JSONDecodeError:
            continue
    
    # Fallback: try in root movements directory
    movement_path = os.path.join(movements_dir, filename)
    try:
        with open(movement_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

def get_all_movements() -> Dict[str, Dict[str, Any]]:
    """Load all movement definitions."""
    movements_dir = get_movements_directory()
    movements = {}
    
    if not os.path.exists(movements_dir):
        return movements
    
    # Scan category subdirectories
    categories = ["weightlifting", "gymnastics", "monostructural", "cardio"]
    
    for category in categories:
        category_path = os.path.join(movements_dir, category)
        if os.path.exists(category_path) and os.path.isdir(category_path):
            for filename in os.listdir(category_path):
                if filename.endswith('.json'):
                    movement_key = filename.replace('.json', '')
                    try:
                        with open(os.path.join(category_path, filename), 'r') as f:
                            movement_data = json.load(f)
                            movements[movement_key] = movement_data
                    except (FileNotFoundError, json.JSONDecodeError):
                        continue
    
    # Also scan root directory for any loose files
    for filename in os.listdir(movements_dir):
        if filename.endswith('.json') and filename != 'index.json':
            movement_key = filename.replace('.json', '')
            if movement_key not in movements:  # Don't override category files
                try:
                    with open(os.path.join(movements_dir, filename), 'r') as f:
                        movement_data = json.load(f)
                        movements[movement_key] = movement_data
                except (FileNotFoundError, json.JSONDecodeError):
                    continue
    
    return movements

def get_movements_by_category(category: str) -> Dict[str, Dict[str, Any]]:
    """Get all movements in a specific category."""
    all_movements = get_all_movements()
    return {
        key: movement for key, movement in all_movements.items() 
        if movement.get("category") == category
    }

def get_movement_execution_time(movement_name: str, intensity: str = None) -> float:
    """Get execution time for a movement at specified intensity."""
    movement = load_movement(movement_name)
    if not movement:
        return 2.0  # Default fallback
    
    variety = movement.get("variety", {})
    
    # If no intensity specified, use the first available intensity
    if intensity is None:
        intensity_keys = list(variety.keys())
        if intensity_keys:
            intensity = intensity_keys[0]
        else:
            return 2.0
    
    # Try to get the specified intensity, fall back to first available
    intensity_data = variety.get(intensity, {})
    if not intensity_data and variety:
        intensity_data = list(variety.values())[0]
    
    return intensity_data.get("execution_time", 2.0)

def convert_movement_to_workout_format(movement_name: str, count: int, intensity: str = None, movement_type: str = "S") -> Dict[str, Any]:
    """Convert a movement library entry to workout format."""
    movement = load_movement(movement_name)
    if not movement:
        return {
            "description": movement_name,
            "number": 2.0,
            "type": movement_type,
            "count": count
        }
    
    # If no intensity specified, use the first available
    variety = movement.get("variety", {})
    if intensity is None and variety:
        intensity = list(variety.keys())[0]
    elif intensity is None:
        intensity = "standard"
    
    execution_time = get_movement_execution_time(movement_name, intensity)
    
    return {
        "description": f"{movement['name']} ({intensity})",
        "number": execution_time,
        "type": movement_type,
        "count": count
    }
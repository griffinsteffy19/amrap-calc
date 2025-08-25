import json
import os
import glob
from typing import Dict, Optional, Any
try:
    from movement_library import load_movement, convert_movement_to_workout_format
except ImportError:
    from .movement_library import load_movement, convert_movement_to_workout_format

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

def _warning(message: str):
    """Display warning message via Streamlit if available, otherwise print."""
    if HAS_STREAMLIT:
        st.warning(message)
    else:
        print(f"Warning: {message}")

def _error(message: str):
    """Display error message via Streamlit if available, otherwise print."""
    if HAS_STREAMLIT:
        st.error(message)
    else:
        print(f"Error: {message}")

def get_workouts_directory() -> str:
    """Get the path to the workouts directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "..", "data", "workouts")

def load_workout_library() -> Dict[str, Dict[str, Any]]:
    """Load workout library from nested folder structure"""
    try:
        # Load the index file for category metadata
        workouts_dir = get_workouts_directory()
        index_path = os.path.join(workouts_dir, 'index.json')
        
        if not os.path.exists(index_path):
            _warning("Workout library index not found.")
            return {}
        
        with open(index_path, 'r') as f:
            index_data = json.load(f)
        
        # Load workouts from each category folder
        library_data = {}
        for category_key, category_info in index_data['categories'].items():
            category_path = os.path.join(workouts_dir, category_key)
            if os.path.exists(category_path) and os.path.isdir(category_path):
                # Create category structure
                category_data = {
                    'name': category_info['name'],
                    'description': category_info['description'],
                    'icon': category_info.get('icon', '📋'),
                    'workouts': {}
                }
                
                # Load all JSON files in the category folder
                workout_files = glob.glob(os.path.join(category_path, '*.json'))
                temp_workouts = {}
                for workout_file in workout_files:
                    workout_key = os.path.splitext(os.path.basename(workout_file))[0]
                    try:
                        with open(workout_file, 'r') as f:
                            workout_data = json.load(f)
                            temp_workouts[workout_key] = workout_data
                    except json.JSONDecodeError:
                        _warning(f"Error reading workout file: {workout_file}")
                    except Exception as e:
                        _warning(f"Error loading workout {workout_key}: {str(e)}")
                
                # Sort workouts alphabetically by their display name
                if temp_workouts:
                    sorted_items = sorted(temp_workouts.items(), key=lambda x: x[1].get('name', x[0]).lower())
                    category_data['workouts'] = {k: v for k, v in sorted_items}
                    library_data[category_key] = category_data
                else:
                    _warning(f"No valid workouts found in category: {category_key}")
            else:
                _warning(f"Category folder not found: {category_key}")
        
        return library_data
        
    except FileNotFoundError:
        _warning("Workout library folder not found.")
        return {}
    except json.JSONDecodeError:
        _error("Error reading workout library index. Please check the file format.")
        return {}
    except Exception as e:
        _error(f"Error loading workout library: {str(e)}")
        return {}

def load_workout_from_library(library_data: Dict[str, Dict[str, Any]], category_key: str, workout_key: str) -> Optional[Dict[str, Any]]:
    """Load a specific workout from the library"""
    try:
        workout = library_data[category_key]['workouts'][workout_key]
        
        # Process movements (handles both standard format and movement database references)
        processed_movements = process_workout_movements(workout['movements'])
        
        return {
            'tot_tm': workout['tot_tm'],
            'm': workout['m'],
            'movements': processed_movements,
            'name': workout['name'],
            'description': workout['description'],
            'workout_type': workout.get('workout_type', 'amrap'),
            'rounds': workout.get('rounds', 1),
            'time_cap': workout.get('time_cap')
        }
    except KeyError as e:
        _error(f"Error loading workout: {str(e)}")
        return None

def get_workout_categories() -> Dict[str, Dict[str, str]]:
    """Get workout categories from index.json."""
    workouts_dir = get_workouts_directory()
    index_path = os.path.join(workouts_dir, 'index.json')
    
    try:
        with open(index_path, 'r') as f:
            data = json.load(f)
            return data.get("categories", {})
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def get_workouts_by_category(category: str) -> Dict[str, Dict[str, Any]]:
    """Get all workouts in a specific category, sorted alphabetically by workout name."""
    library_data = load_workout_library()
    if category in library_data:
        workouts = library_data[category]['workouts']
        # Sort workouts by their display name (the 'name' field in the workout data)
        sorted_workouts = {}
        # Create list of (workout_key, workout_data) tuples sorted by workout name
        sorted_items = sorted(workouts.items(), key=lambda x: x[1].get('name', x[0]).lower())
        for workout_key, workout_data in sorted_items:
            sorted_workouts[workout_key] = workout_data
        return sorted_workouts
    return {}

def process_workout_movements(movements: list) -> list:
    """Process workout movements, converting movement database references to standard format."""
    processed_movements = []
    
    for movement in movements:
        # Check if this is a movement database reference
        if isinstance(movement, dict) and 'movement_name' in movement:
            # This is a reference to the movement database
            movement_name = movement['movement_name']
            variety = movement.get('variety', None)
            count = movement.get('count', 1)
            movement_type = movement.get('type', 'S')
            
            # Convert from movement database
            try:
                workout_movement = convert_movement_to_workout_format(movement_name, count, variety, movement_type)
                processed_movements.append(workout_movement)
            except Exception as e:
                # Fallback if movement not found in database
                _warning(f"Movement '{movement_name}' not found in database, using fallback: {str(e)}")
                fallback_movement = {
                    'description': movement.get('description', movement_name),
                    'number': movement.get('execution_time', 2.0),
                    'type': movement_type,
                    'count': count
                }
                processed_movements.append(fallback_movement)
        else:
            # This is a standard movement definition, use as-is
            processed_movements.append(movement)
    
    return processed_movements
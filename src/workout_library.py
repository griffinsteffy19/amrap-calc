import json
import os
import glob
from typing import Dict, Optional, Any

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
                for workout_file in workout_files:
                    workout_key = os.path.splitext(os.path.basename(workout_file))[0]
                    try:
                        with open(workout_file, 'r') as f:
                            workout_data = json.load(f)
                            category_data['workouts'][workout_key] = workout_data
                    except json.JSONDecodeError:
                        _warning(f"Error reading workout file: {workout_file}")
                    except Exception as e:
                        _warning(f"Error loading workout {workout_key}: {str(e)}")
                
                if category_data['workouts']:  # Only add category if it has workouts
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
        return {
            'tot_tm': workout['tot_tm'],
            'm': workout['m'],
            'movements': workout['movements'],
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
    """Get all workouts in a specific category."""
    library_data = load_workout_library()
    if category in library_data:
        return library_data[category]['workouts']
    return {}
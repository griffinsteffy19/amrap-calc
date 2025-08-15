import streamlit as st
import math
import json
import pandas as pd

def convert_pace_to_time_per_rep(pace_value, pace_unit, rep_size=1):
    """
    Convert various pace formats to time per rep in seconds
    
    Args:
        pace_value: The pace value (e.g., 2:00 for 2 minutes)
        pace_unit: The pace unit ('500m_pace', 'cal_hr', 'time_per_rep')
        rep_size: Size of one rep (e.g., meters for rowing, calories for bike)
    
    Returns:
        Time per rep in seconds
    """
    if pace_unit == 'time_per_rep':
        return pace_value
    elif pace_unit == '500m_pace':
        # Convert 500m pace to time per meter, then scale by rep_size
        time_per_500m = pace_value
        time_per_meter = time_per_500m / 500
        return time_per_meter * rep_size
    elif pace_unit == 'cal_hr':
        # Convert calories per hour to seconds per calorie, then scale by rep_size
        cal_per_second = pace_value / 3600
        time_per_cal = 1 / cal_per_second
        return time_per_cal * rep_size
    else:
        return pace_value

def parse_time_input(time_str):
    """Parse time input in formats like '2:30', '90', '1:23.5'"""
    if ':' in str(time_str):
        parts = str(time_str).split(':')
        if len(parts) == 2:
            minutes = float(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
    return float(time_str)

def load_workout_library():
    """Load workout library from nested folder structure"""
    import os
    import glob
    
    try:
        # Load the index file for category metadata
        index_path = os.path.join('workout_library', 'index.json')
        if not os.path.exists(index_path):
            st.warning("Workout library index not found.")
            return {}
        
        with open(index_path, 'r') as f:
            index_data = json.load(f)
        
        # Load workouts from each category folder
        library_data = {}
        for category_key, category_info in index_data['categories'].items():
            category_path = os.path.join('workout_library', category_key)
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
                        st.warning(f"Error reading workout file: {workout_file}")
                    except Exception as e:
                        st.warning(f"Error loading workout {workout_key}: {str(e)}")
                
                if category_data['workouts']:  # Only add category if it has workouts
                    library_data[category_key] = category_data
                else:
                    st.warning(f"No valid workouts found in category: {category_key}")
            else:
                st.warning(f"Category folder not found: {category_key}")
        
        return library_data
        
    except FileNotFoundError:
        st.warning("Workout library folder not found.")
        return {}
    except json.JSONDecodeError:
        st.error("Error reading workout library index. Please check the file format.")
        return {}
    except Exception as e:
        st.error(f"Error loading workout library: {str(e)}")
        return {}

def load_workout_from_library(library_data, category_key, workout_key):
    """Load a specific workout from the library"""
    try:
        workout = library_data[category_key]['workouts'][workout_key]
        return {
            'tot_tm': workout['tot_tm'],
            'm': workout['m'],
            'movements': workout['movements'],
            'name': workout['name'],
            'description': workout['description']
        }
    except KeyError as e:
        st.error(f"Error loading workout: {str(e)}")
        return None

def calculate_n(tot_tm, m, dmvmt, smvmt):
    """
    Calculate N using the quadratic formula for:
    TotTm = M * (1 + 2 + ... + N) * Dmvmt + (N * Smvmt)
    """
    # Coefficients for quadratic equation: a*N² + b*N + c = 0
    a = m * dmvmt
    b = m * dmvmt + 2 * smvmt
    c = -2 * tot_tm
    
    # Check if we have a valid quadratic equation
    if a == 0:
        if b == 0:
            # Special case: No D or S movements (only M-type movements)
            # For max-only workouts, return 1 as N (single round of max reps)
            return 1.0
        else:
            # Linear equation: b*N + c = 0
            return -c / b
    
    # Calculate discriminant
    discriminant = b**2 - 4*a*c
    
    if discriminant < 0:
        st.error("Error: No real solution (negative discriminant)")
        return None
    
    # Calculate both solutions
    n1 = (-b + math.sqrt(discriminant)) / (2 * a)
    n2 = (-b - math.sqrt(discriminant)) / (2 * a)
    
    # Return the positive solution
    if n1 > 0:
        return n1
    elif n2 > 0:
        return n2
    else:
        st.error("Error: No positive solution found")
        return None

def verify_solution(n, m, dmvmt, smvmt):
    """Verify the solution by calculating the total time"""
    triangular_sum = n * (n + 1) / 2
    calculated_total = m * triangular_sum * dmvmt + n * smvmt
    return calculated_total

def calculate_max_reps(tot_tm, n_result, m, movements, dmvmt_total, smvmt_total):
    """Calculate max reps for M-type movements based on remaining time"""
    # Calculate remaining time after accounting for static movements
    remaining_time = tot_tm - smvmt_total
    
    # Find max movements
    max_movements = [mov for mov in movements if mov.get('count', 1) == -1]
    
    total_max_reps = 0
    for max_mov in max_movements:
        if remaining_time > 0:
            # Calculate how many reps we can do with remaining time
            if max_mov['type'] == 'D':
                # For dynamic movements, consider the multiplier
                max_reps = remaining_time / (m * max_mov['number'])
            else:
                # For static movements
                max_reps = remaining_time / max_mov['number']
            
            total_max_reps += math.floor(max_reps)
            remaining_time = 0  # All remaining time is consumed
    
    return total_max_reps

def calculate_r(n_result, m, movements, dmvmt_total, smvmt_total, show_debug=False):
    """Calculate R based on the movements and remaining capacity"""
    n_floor = math.floor(n_result)
    r = 0
    
    # Calculate remaining using totals
    remaining = math.floor((n_result - n_floor) * (m * (n_floor + 1) * dmvmt_total + smvmt_total))
    
    if show_debug:
        st.write(f"**Debug Info:**")
        st.write(f"N = {n_result:.6f}, N_floor = {n_floor}")
        st.write(f"Total Dmvmt: {dmvmt_total}, Total Smvmt: {smvmt_total}")
        st.write(f"Remaining: {remaining:.6f}")
        st.write("---")
    
    for i, movement in enumerate(movements):
        mov_type = movement['type'].upper()
        mov_tm = movement['number']
        mov_desc = movement['description']
        
        if show_debug:
            st.write(f"**Movement {i+1}: {mov_desc}**")
            st.write(f"Type: {mov_type}, Number: {mov_tm}")
        
        # Set multiplier based on movement type
        if mov_type in ["S", "T"]:
            multiplier = 1
        else:  # mov_type == "D"
            multiplier = m
        
        # Check the condition for both D and S movements
        if mov_type in ["D", "S", "T"]:
            if remaining != 0 and remaining > (multiplier * (n_floor + 1) * mov_tm):
                # Add multiplier*(N_floor+1) to R
                addition = multiplier * (n_floor + 1)
                if show_debug:
                    st.write(f"Condition met: R += {addition:.6f}")
                if mov_type in ["D", "S"]:
                    r += addition
                else:
                    if show_debug:
                        st.write(f"Movement Type: {mov_type}, not adding to r")
                remaining -= (multiplier * (n_floor + 1) * mov_tm)
            else:
                # Add remaining/mov_tm to R
                if mov_tm != 0:  # Avoid division by zero
                    addition = remaining / mov_tm
                    if show_debug:
                        st.write(f"Condition not met: R += remaining/mov_tm = {addition:.6f}")
                    if mov_type in ["D", "S"]:
                        r += math.floor(addition)
                    else:
                        if show_debug:
                            st.write(f"Movement Type: {mov_type}, not adding to r")
                    remaining = 0
                    break
                else:
                    if show_debug:
                        st.warning(f"Warning: Movement number is 0, skipping calculation")
        
        if show_debug:
            st.write(f"Current R: {r:.6f}")
            st.write(f"Remaining: {remaining:.6f}")
            st.write("")
    
    return r

def main():
    st.title("AMRAP Movement Time Calculator")
    st.markdown("---")
    
    # Sidebar for input method selection
    st.sidebar.header("Input Method")
    input_method = st.sidebar.radio("Choose input method:", ["Workout Library", "Manual Entry", "JSON Upload"])
    
    # Initialize session state for movements
    if 'movements' not in st.session_state:
        st.session_state.movements = []
    
    movements = []
    dmvmt_total = 0
    smvmt_total = 0
    tot_tm = 0
    m = 1
    
    if input_method == "Workout Library":
        # Workout Library section
        st.header("🏋️ Workout Library")
        
        # Load workout library
        library_data = load_workout_library()
        
        if library_data:
            # Category selection
            st.subheader("Select Category")
            category_options = {key: f"{data.get('icon', '📋')} {data['name']}" for key, data in library_data.items()}
            category_key = st.selectbox(
                "Choose workout category:",
                options=list(category_options.keys()),
                format_func=lambda x: category_options[x],
                help="Different types of AMRAP workouts"
            )
            
            if category_key:
                category_data = library_data[category_key]
                icon = category_data.get('icon', '📋')
                st.info(f"{icon} {category_data['description']}")
                
                # Workout selection
                st.subheader("Select Workout")
                workout_options = {key: data['name'] for key, data in category_data['workouts'].items()}
                workout_key = st.selectbox(
                    "Choose workout:",
                    options=list(workout_options.keys()),
                    format_func=lambda x: workout_options[x]
                )
                
                if workout_key:
                    workout_data = category_data['workouts'][workout_key]
                    
                    # Display workout info
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Duration", f"{workout_data['tot_tm'] // 60} minutes")
                        st.metric("Multiplier", f"{workout_data['m']}")
                    with col2:
                        st.metric("Movements", len(workout_data['movements']))
                    
                    st.info(f"📝 **{workout_data['name']}**: {workout_data['description']}")
                    
                    # Load workout button
                    if st.button("🚀 Load This Workout", type="primary"):
                        # Clear existing movements
                        st.session_state.movements = []
                        
                        # Load workout data
                        for movement in workout_data['movements']:
                            # Add missing fields for compatibility
                            movement_copy = movement.copy()
                            if 'input_mode' not in movement_copy:
                                movement_copy['input_mode'] = 'Time per Rep'
                            if 'original_input' not in movement_copy:
                                movement_copy['original_input'] = str(movement_copy['number'])
                            if 'rep_size' not in movement_copy:
                                movement_copy['rep_size'] = 1
                            
                            st.session_state.movements.append(movement_copy)
                        
                        # Set parameters
                        st.session_state.tot_tm = workout_data['tot_tm']
                        st.session_state.m = workout_data['m']
                        
                        st.success(f"✅ Loaded '{workout_data['name']}' with {len(workout_data['movements'])} movements!")
                        st.info("💡 Scroll down to see the loaded workout and live calculations.")
                    
                    # Preview movements
                    if workout_data['movements']:
                        st.subheader("Movement Preview")
                        preview_data = []
                        for mov in workout_data['movements']:
                            count_display = "MAX" if mov.get('count', 1) == -1 else str(mov.get('count', 1))
                            total_time_val = mov['number'] * mov.get('count', 1) if mov.get('count', 1) != -1 else 0
                            total_time_display = "MAX" if mov.get('count', 1) == -1 else f"{total_time_val:.2f}"
                            
                            preview_data.append({
                                'Movement': mov['description'],
                                'Type': mov['type'],
                                'Time (s)': f"{mov['number']:.2f}",
                                'Count': count_display,
                                'Total Time': total_time_display
                            })
                        
                        df_preview = pd.DataFrame(preview_data)
                        st.dataframe(df_preview, use_container_width=True)
        else:
            st.warning("No workout library available. Please check that 'workout_library.json' exists.")
        
        # Load parameters from session state if workout was loaded
        if hasattr(st.session_state, 'tot_tm'):
            tot_tm = st.session_state.tot_tm
        if hasattr(st.session_state, 'm'):
            m = st.session_state.m
        
        # Use loaded movements
        movements = st.session_state.movements
        # Exclude max movements from initial calculation
        dmvmt_total = sum(mov['number'] * mov.get('count', 1) for mov in movements if mov['type'] == 'D' and mov.get('count', 1) != -1)
        smvmt_total = sum(mov['number'] * mov.get('count', 1) for mov in movements if mov['type'] in ['S', 'T'] and mov.get('count', 1) != -1)
    
    elif input_method == "Manual Entry":
        # Manual entry section
        st.header("Movement Entry")
        
        # Add movement form (dynamic, no form wrapper for reactivity)
        st.subheader("Add New Movement")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            movement_type = st.selectbox("Type", ["D", "S", "T", "M"], key="new_movement_type")
        
        with col2:
            if movement_type == "T":
                description = st.text_input("Description", value="Transition", disabled=True, key="new_description")
            elif movement_type == "M":
                description = st.text_input("Description", value="Max Reps", disabled=True, key="new_description")
            else:
                description = st.text_input("Description", key="new_description")
        
        with col3:
            # Input mode selection
            input_mode = st.selectbox("Input Mode", ["Time per Rep", "500m Pace", "Cal/Hr"], 
                                    help="Choose how to input timing", key="new_input_mode")
        
        with col4:
            if movement_type == "T":
                if input_mode == "Time per Rep":
                    time_input = st.number_input("Time (sec)", value=2.0, step=0.1, key="new_time")
                else:
                    time_input = st.text_input("Time/Pace", value="2.0", 
                                             help="e.g., 2:30 for 2:30/500m or 150 for 150 cal/hr", key="new_time")
            elif movement_type == "M":
                if input_mode == "Time per Rep":
                    time_input = st.number_input("Time (sec)", value=3.0, step=0.1, key="new_time")
                else:
                    time_input = st.text_input("Time/Pace", value="3.0", 
                                             help="e.g., 2:30 for 2:30/500m or 150 for 150 cal/hr", key="new_time")
            else:
                if input_mode == "Time per Rep":
                    time_input = st.number_input("Time (sec)", value=5.0, step=0.1, key="new_time")
                else:
                    time_input = st.text_input("Time/Pace", value="5.0", 
                                             help="e.g., 2:30 for 2:30/500m or 150 for 150 cal/hr", key="new_time")
        
        with col5:
            # Rep size input for pace modes
            if input_mode in ["500m Pace", "Cal/Hr"] and movement_type not in ["T"]:
                if input_mode == "500m Pace":
                    rep_size = st.number_input("Meters/Rep", value=1, step=1, min_value=1, 
                                             help="How many meters per rep", key="new_rep_size")
                else:  # Cal/Hr
                    rep_size = st.number_input("Cals/Rep", value=1, step=1, min_value=1, 
                                             help="How many calories per rep", key="new_rep_size")
            else:
                rep_size = 1
                st.write("") # Placeholder
                
        with col6:
            if movement_type == "S":
                movement_count = st.number_input("Count", value=1, step=1, min_value=1, key="new_count")
            elif movement_type == "M":
                st.write("Count: MAX")
                movement_count = -1  # Special indicator for max reps
            else:
                movement_count = 1  # Default for non-S movements
                st.write("") # Placeholder
        
        # Add movement button
        submitted = st.button("Add Movement", type="primary")
        
        if submitted and description:
            # Convert pace to time per rep
            try:
                if input_mode == "Time per Rep":
                    final_time = time_input
                else:
                    # Parse the pace input and convert
                    pace_value = parse_time_input(time_input)
                    pace_unit = {'500m Pace': '500m_pace', 'Cal/Hr': 'cal_hr'}[input_mode]
                    final_time = convert_pace_to_time_per_rep(pace_value, pace_unit, rep_size)
                
                new_movement = {
                    'description': description,
                    'number': final_time,
                    'type': movement_type,
                    'count': movement_count,
                    'input_mode': input_mode,
                    'original_input': str(time_input),
                    'rep_size': rep_size if input_mode != "Time per Rep" else 1
                }
                st.session_state.movements.append(new_movement)
                
                if movement_type == "S":
                    st.success(f"Added: {description} - {final_time:.2f}s x{movement_count} ({movement_type})")
                elif movement_type == "M":
                    st.success(f"Added: {description} - {final_time:.2f}s per rep (MAX until completion) ({movement_type})")
                else:
                    st.success(f"Added: {description} - {final_time:.2f}s ({movement_type})")
                    
                if input_mode != "Time per Rep":
                    st.info(f"Converted from {input_mode}: {time_input} → {final_time:.2f} seconds per rep")
                    
            except Exception as e:
                st.error(f"Error processing input: {str(e)}")
        
        # Edit existing movements with inputs
        if st.session_state.movements:
            st.subheader("Live Movement Editor")
            st.markdown("*Edit any field below to see results update instantly*")
            
            # Create columns for editing
            for i, movement in enumerate(st.session_state.movements):
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                
                with col1:
                    if movement['type'] in ['T', 'M']:
                        new_desc = st.text_input(f"Description", value=movement['description'], 
                                               disabled=True, key=f"desc_{i}")
                    else:
                        new_desc = st.text_input(f"Description", value=movement['description'], key=f"desc_{i}")
                
                with col2:
                    new_number = st.number_input(f"⏱️ {movement['description']} Time", 
                                               value=movement['number'], step=0.1, 
                                               min_value=0.1, key=f"time_{i}",
                                               help="Enter time to see live results update")
                
                with col3:
                    new_type = st.selectbox(f"Type", ["D", "S", "T", "M"], 
                                            index=["D", "S", "T", "M"].index(movement['type']), key=f"type_{i}")
                
                with col4:
                    if new_type == "S":
                        new_count = st.number_input(f"Count", value=movement.get('count', 1), 
                                                  step=1, min_value=1, key=f"count_{i}")
                    elif new_type == "M":
                        new_count = -1
                        st.write("Count: MAX")
                    else:
                        new_count = 1
                        st.write("Count: 1")
                
                with col5:
                    if st.button(f"🗑️", key=f"del_{i}", help="Delete this movement"):
                        st.session_state.movements.pop(i)
                        st.rerun()
                
                # Update the movement in real-time
                st.session_state.movements[i] = {
                    'description': new_desc if new_type not in ['T', 'M'] else ("Transition" if new_type == 'T' else "Max Reps"),
                    'number': new_number,
                    'type': new_type,
                    'count': new_count
                }
                
                # Show immediate impact
                if movement['number'] != new_number:
                    change = new_number - movement['number']
                    st.caption(f"Changed by {change:+.1f} seconds")
            
            # Recalculate totals after slider changes
            movements = st.session_state.movements
            # Exclude max movements from initial calculation
            dmvmt_total = sum(mov['number'] * mov.get('count', 1) for mov in movements if mov['type'] == 'D' and mov.get('count', 1) != -1)
            smvmt_total = sum(mov['number'] * mov.get('count', 1) for mov in movements if mov['type'] in ['S', 'T'] and mov.get('count', 1) != -1)
        
        # Display current movements with live editing
        if st.session_state.movements:
            st.subheader("Current Movements (Live Editing)")
            
            # Create a display dataframe with count information
            display_data = []
            for mov in st.session_state.movements:
                count = mov.get('count', 1)
                count_display = "MAX" if count == -1 else str(count)
                total_time_val = mov['number'] * count if count != -1 else 0
                total_time_display = "MAX" if count == -1 else f"{total_time_val:.2f}"
                
                # Add pace info if available
                pace_info = ""
                if mov.get('input_mode', 'Time per Rep') != 'Time per Rep':
                    pace_info = f" (from {mov.get('input_mode', '')}: {mov.get('original_input', '')})"
                
                display_data.append({
                    'Description': mov['description'],
                    'Type': mov['type'],
                    'Time (s)': f"{mov['number']:.2f}{pace_info}",
                    'Count': count_display,
                    'Total Time': total_time_display
                })
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True)
            
            # Clear movements button
            if st.button("Clear All Movements"):
                st.session_state.movements = []
                st.rerun()
            
            movements = st.session_state.movements
            # Exclude max movements from initial calculation
            dmvmt_total = sum(mov['number'] * mov.get('count', 1) for mov in movements if mov['type'] == 'D' and mov.get('count', 1) != -1)
            smvmt_total = sum(mov['number'] * mov.get('count', 1) for mov in movements if mov['type'] in ['S', 'T'] and mov.get('count', 1) != -1)
        
        # Other parameters
        st.header("Parameters")
        col1, col2 = st.columns(2)
        
        with col1:
            tot_tm = st.number_input("Total Time (TotTm)", value=100.0, step=1.0, min_value=1.0)
        with col2:
            m = st.number_input("Multiplier (M)", value=2.5, step=0.1, min_value=0.1)
    
    else:  # JSON Upload
        st.header("JSON Upload")
        
        # Show example JSON format
        with st.expander("Example JSON Format"):
            example_json = {
                "tot_tm": 100.0,
                "m": 2.5,
                "movements": [
                    {
                        "description": "Walking movement",
                        "number": 15.0,
                        "type": "S",
                        "count": 3
                    },
                    {
                        "description": "Running movement",
                        "number": 8.0,
                        "type": "D",
                        "count": 1
                    },
                    {
                        "description": "Transition",
                        "number": 2.0,
                        "type": "T",
                        "count": 1
                    },
                    {
                        "description": "Max Reps",
                        "number": 3.0,
                        "type": "M",
                        "count": -1
                    }
                ]
            }
            st.json(example_json)
        
        uploaded_file = st.file_uploader("Upload JSON file", type=['json'])
        
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                
                # Extract data
                movements = data.get('movements', [])
                tot_tm = data.get('tot_tm', 0)
                m = data.get('m', 1)
                
                # Ensure count field exists for all movements
                for mov in movements:
                    if 'count' not in mov:
                        mov['count'] = 1
                
                # Calculate totals with count (exclude max movements)
                dmvmt_total = sum(mov['number'] * mov.get('count', 1) for mov in movements if mov.get('type', '').upper() == 'D' and mov.get('count', 1) != -1)
                smvmt_total = sum(mov['number'] * mov.get('count', 1) for mov in movements if mov.get('type', '').upper() in ['S', 'T'] and mov.get('count', 1) != -1)
                
                # Display loaded data
                st.success("JSON file loaded successfully!")
                st.subheader("Loaded Movements")
                
                # Create display dataframe
                display_data = []
                for mov in movements:
                    count = mov.get('count', 1)
                    count_display = "MAX" if count == -1 else str(count)
                    total_time_val = mov.get('number', 0) * count if count != -1 else 0
                    total_time_display = "MAX" if count == -1 else f"{total_time_val:.2f}"
                    display_data.append({
                        'Description': mov.get('description', ''),
                        'Type': mov.get('type', ''),
                        'Time (s)': mov.get('number', 0),
                        'Count': count_display,
                        'Total Time': total_time_display
                    })
                
                df = pd.DataFrame(display_data)
                st.dataframe(df)
                
                st.subheader("Loaded Parameters")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Time", tot_tm)
                with col2:
                    st.metric("Multiplier", m)
                
            except json.JSONDecodeError:
                st.error("Invalid JSON file format")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    # Calculate button and results
    if movements and tot_tm > 0:
        st.markdown("---")
        
        # Summary with live updates and change indicators
        st.subheader("📊 Live Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Movements", len(movements))
        with col2:
            st.metric("Total Dmvmt", f"{dmvmt_total:.1f}", help="Sum of all D-type movements with count")
        with col3:
            st.metric("Total Smvmt", f"{smvmt_total:.1f}", help="Sum of all S and T-type movements with count")
        with col4:
            st.metric("Multiplier", f"{m:.1f}")
        
        # Real-time calculation indicator
        st.markdown("🔄 **Results update automatically as you edit values**")
        
        # Auto-calculate with live updates
        try:
            # Calculate N
            n_result = calculate_n(tot_tm, m, dmvmt_total, smvmt_total)
            
            if n_result is not None:
                # Results with live updates
                st.subheader("⚡ Live Results")
                n_floor = math.floor(n_result)
                
                # Calculate R (need to adjust movements for R calculation, excluding max movements)
                r_movements = []
                for mov in movements:
                    if mov.get('count', 1) != -1:  # Exclude max movements from R calculation
                        r_movements.append({
                            'description': mov['description'],
                            'number': mov['number'] * mov.get('count', 1),
                            'type': mov['type']
                        })
                
                r_result = calculate_r(n_result, m, r_movements, dmvmt_total, smvmt_total, show_debug=False)
                
                # Calculate max reps for M-type movements
                max_reps = calculate_max_reps(tot_tm, n_result, m, movements, dmvmt_total, smvmt_total)
                
                # Add max reps to the score
                total_r = r_result + max_reps
                
                # Display final score prominently with live updates
                st.markdown("### 🏆 Final Score (Updates Live)")
                score_col1, score_col2, score_col3 = st.columns([1, 2, 1])
                with score_col2:
                    if max_reps > 0:
                        st.markdown(f"## {n_floor} + {r_result} + {max_reps} (max)")
                        st.caption(f"Total: {n_floor + total_r}")
                    else:
                        st.markdown(f"## {n_floor} + {r_result}")
                
                # Live metrics with better formatting
                if max_reps > 0:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Calculated N", f"{n_result:.3f}")
                    with col2:
                        st.metric("Floor N", n_floor)
                    with col3:
                        st.metric("R Value", r_result)
                    with col4:
                        st.metric("Max Reps", max_reps)
                else:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Calculated N", f"{n_result:.3f}")
                    with col2:
                        st.metric("Floor N", n_floor)
                    with col3:
                        st.metric("R Value", r_result)
                
                # Show sensitivity - how score changes with small adjustments
                st.markdown("---")
                st.markdown("💡 **Tip**: Edit the values above to see how changes affect your score in real-time!")
                
                # Optional detailed view
                show_debug = st.checkbox("Show detailed calculations")
                
                if show_debug:
                    st.subheader("🔍 Debug Information")
                    
                    # Verification
                    verification = verify_solution(n_result, m, dmvmt_total, smvmt_total)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Verification", f"{verification:.6f}")
                        st.metric("Target TotTm", tot_tm)
                    with col2:
                        st.metric("Difference", f"{abs(verification - tot_tm):.6f}")
                        if abs(verification - tot_tm) < 0.001:
                            st.success("✅ Calculation verified!")
                    
                    # Detailed R calculation
                    calculate_r(n_result, m, r_movements, dmvmt_total, smvmt_total, show_debug=True)
            
        except Exception as e:
            st.error(f"⚠️ Calculation error: {str(e)}")
            
    elif not movements:
        st.info("👆 Add some movements above to see live calculations.")
    elif tot_tm <= 0:
        st.info("👆 Set a valid total time (TotTm > 0) using the slider above.")

if __name__ == "__main__":
    main()
import streamlit as st
import math
import json
import pandas as pd
from calculations import (
    convert_pace_to_time_per_rep, 
    parse_time_input, 
    calculate_amrap_results,
    calculate_movement_totals
)

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
                    
                    # Display workout info on one line
                    duration_minutes = workout_data['tot_tm'] // 60
                    num_movements = len(workout_data['movements'])
                    multiplier = workout_data['m']
                    
                    # Build info string
                    info_parts = [f"⏱️ {duration_minutes} min", f"📋 {num_movements} movements"]
                    if multiplier != 1.0:
                        info_parts.append(f"⚡ {multiplier}x multiplier")
                    
                    st.markdown(f"**{' • '.join(info_parts)}**")
                    
                    st.info(f"📝 **{workout_data['name']}**: {workout_data['description']}")
                    
                    # Auto-load workout data for immediate editing
                    if 'current_workout_key' not in st.session_state or st.session_state.current_workout_key != workout_key:
                        # Auto-load when workout selection changes
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
                        st.session_state.current_workout_key = workout_key
                    
                    # Show Final Score first if we have movements
                    if st.session_state.movements and hasattr(st.session_state, 'tot_tm') and st.session_state.tot_tm > 0:
                        dmvmt_total, smvmt_total, _ = calculate_movement_totals(st.session_state.movements)
                        tot_tm = st.session_state.tot_tm
                        m = st.session_state.m
                        
                        # Calculate and display final score prominently at the top
                        try:
                            results = calculate_amrap_results(tot_tm, m, st.session_state.movements)
                            if results['error'] is None:
                                st.markdown("### 🏆 Final Score")
                                score_col1, score_col2, score_col3 = st.columns([1, 2, 1])
                                with score_col2:
                                    # Determine workout type for appropriate score display
                                    has_max_movement = any(mov.get('count') == -1 for mov in st.session_state.movements)
                                    has_regular_movements = any(mov.get('count') != -1 for mov in st.session_state.movements)
                                    last_movement_is_max = len(st.session_state.movements) > 0 and st.session_state.movements[-1].get('count') == -1
                                    
                                    if has_max_movement and has_regular_movements and last_movement_is_max:
                                        # "Finish with Max" workout (like Rock) - show only max reps
                                        st.markdown(f"# {results['max_reps']}")
                                        max_movement_name = next(mov['description'] for mov in st.session_state.movements if mov.get('count') == -1)
                                        st.caption(f"{results['max_reps']} {max_movement_name.lower()}")
                                    elif has_max_movement and not has_regular_movements:
                                        # "Only Max" workout (like 12.1) - show only max reps
                                        st.markdown(f"# {results['max_reps']}")
                                        max_movement_name = next(mov['description'] for mov in st.session_state.movements if mov.get('count') == -1)
                                        st.caption(f"{results['max_reps']} {max_movement_name.lower()}")
                                    elif results['max_reps'] > 0:
                                        # Traditional AMRAP with max component - show full breakdown
                                        st.markdown(f"# {results['total_score']}")
                                        st.caption(f"{results['n_floor']} completed rounds + {results['r_result']} additional reps + {results['max_reps']} max reps")
                                    else:
                                        # Regular AMRAP without max component
                                        st.markdown(f"# {results['total_score']}")
                                        st.caption(f"{results['n_floor']} completed rounds + {results['r_result']} additional reps")
                                
                                st.markdown("---")
                                
                            else:
                                st.error(f"⚠️ Calculation error: {results['error']}")
                        except Exception as e:
                            st.error(f"⚠️ Calculation error: {str(e)}")
                    
                    # Combined Preview & Editor - Compact Table Format
                    if workout_data['movements']:
                        st.subheader("📝 Live Workout Editor")
                        st.markdown("*Edit movements below and see results update instantly*")
                        
                        # Table headers
                        header_cols = st.columns([0.3, 2, 1.2, 1.2, 0.8, 0.8, 0.4])
                        with header_cols[0]:
                            st.write("**#**")
                        with header_cols[1]:
                            st.write("**Description**")
                        with header_cols[2]:
                            st.write("**Input Mode**")
                        with header_cols[3]:
                            st.write("**Time/Pace**")
                        with header_cols[4]:
                            st.write("**Type**")
                        with header_cols[5]:
                            st.write("**Count**")
                        with header_cols[6]:
                            st.write("**Del**")
                        
                        # Interactive movement editing (table-like rows)
                        for i, movement in enumerate(st.session_state.movements):
                            col1, col2, col3, col4, col5, col6, col7 = st.columns([0.3, 2, 1.2, 1.2, 0.8, 0.8, 0.4])
                            
                            with col1:
                                st.write(f"{i+1}")
                            
                            with col2:
                                if movement['type'] == 'T':
                                    new_desc = st.text_input("Description", value=movement['description'], 
                                                           disabled=True, key=f"preview_desc_{i}", label_visibility="collapsed")
                                else:
                                    new_desc = st.text_input("Description", value=movement['description'], key=f"preview_desc_{i}", label_visibility="collapsed")
                            
                            with col3:
                                # Allow editing in original pace format if available
                                current_input_mode = movement.get('input_mode', 'Time per Rep')
                                edit_input_mode = st.selectbox("Input Mode", ["Time per Rep", "500m Pace", "Cal/Hr"],
                                                             index=["Time per Rep", "500m Pace", "Cal/Hr"].index(current_input_mode),
                                                             key=f"preview_input_mode_{i}", label_visibility="collapsed")
                            
                            with col4:
                                if edit_input_mode == "Time per Rep":
                                    new_time_input = st.number_input("Time", 
                                                                   value=float(movement['number']), step=0.1, 
                                                                   min_value=0.1, key=f"preview_time_{i}", label_visibility="collapsed")
                                    final_time = new_time_input
                                else:
                                    # Show original pace input if switching back to original format
                                    if edit_input_mode == current_input_mode and 'original_input' in movement:
                                        default_pace = movement['original_input']
                                    else:
                                        # Convert current time back to pace format as default
                                        if edit_input_mode == "500m Pace":
                                            rep_size = movement.get('rep_size', 1)
                                            time_per_meter = movement['number'] / rep_size
                                            pace_seconds = time_per_meter * 500
                                            mins = int(pace_seconds // 60)
                                            secs = pace_seconds % 60
                                            default_pace = f"{mins}:{secs:05.2f}" if mins > 0 else f"{pace_seconds:.2f}"
                                        else:  # Cal/Hr
                                            rep_size = movement.get('rep_size', 1)
                                            time_per_cal = movement['number'] / rep_size
                                            cal_per_hour = 3600 / time_per_cal
                                            default_pace = f"{cal_per_hour:.0f}"
                                    
                                    new_time_input = st.text_input("Pace", value=default_pace,
                                                                 placeholder="e.g., 2:30 or 180", 
                                                                 key=f"preview_pace_{i}", label_visibility="collapsed")
                                    
                                    # Convert pace to time per rep
                                    try:
                                        pace_value = parse_time_input(new_time_input)
                                        pace_unit = {'500m Pace': '500m_pace', 'Cal/Hr': 'cal_hr'}[edit_input_mode]
                                        rep_size = movement.get('rep_size', 1)
                                        final_time = convert_pace_to_time_per_rep(pace_value, pace_unit, rep_size)
                                    except:
                                        final_time = movement['number']  # Keep original if conversion fails
                            
                            with col5:
                                new_type = st.selectbox("Type", ["D", "S", "T", "M"], 
                                                        index=["D", "S", "T", "M"].index(movement['type']), key=f"preview_type_{i}", label_visibility="collapsed")
                            
                            with col6:
                                if new_type == "S":
                                    new_count = st.number_input("Count", value=int(movement.get('count', 1)), 
                                                              step=1, min_value=1, key=f"preview_count_{i}", label_visibility="collapsed")
                                elif new_type == "M":
                                    new_count = -1
                                    st.write("MAX")
                                else:
                                    new_count = 1
                                    st.write("1")
                            
                            with col7:
                                if st.button("🗑️", key=f"preview_del_{i}", help="Delete this movement"):
                                    st.session_state.movements.pop(i)
                                    st.rerun()
                            
                            # Update the movement in real-time
                            st.session_state.movements[i] = {
                                'description': new_desc if new_type != 'T' else "Transition",
                                'number': final_time,
                                'type': new_type,
                                'count': new_count,
                                'input_mode': edit_input_mode,
                                'original_input': str(new_time_input),
                                'rep_size': movement.get('rep_size', 1)
                            }
                            
                            # Show conversion info inline for pace inputs
                            if edit_input_mode != "Time per Rep":
                                with col4:
                                    st.caption(f"→ {final_time:.2f}s")
                            
                            # Show time change indicator
                            if movement['number'] != final_time:
                                change = final_time - movement['number']
                                with col4:
                                    st.caption(f"({change:+.1f}s)")
                        
                        # Parameters editing (collapsible) - only for library workouts
                        with st.expander("📊 Workout Parameters", expanded=False):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_tot_tm = st.number_input("Total Time (seconds)", value=float(st.session_state.tot_tm), step=1.0, min_value=1.0, key="preview_tot_tm")
                                st.session_state.tot_tm = new_tot_tm
                                tot_tm = new_tot_tm
                            with col2:
                                new_m = st.number_input("Multiplier (M)", value=float(st.session_state.m), step=0.1, min_value=0.1, key="preview_m")
                                st.session_state.m = new_m
                                m = new_m
                        
                        # Advanced Mode toggle - after editor
                        st.markdown("---")
                        advanced_mode = st.toggle("🔧 Advanced Mode", help="Show detailed metrics, calculations, and debugging info", key="preview_advanced_mode")
                        
                        if advanced_mode and st.session_state.movements:
                            try:
                                results = calculate_amrap_results(st.session_state.tot_tm, st.session_state.m, st.session_state.movements)
                                if results['error'] is None:
                                    # Advanced metrics in organized sections
                                    st.subheader("📊 Detailed Metrics")
                                    
                                    # Core calculation breakdown
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Total Time", f"{st.session_state.tot_tm}s", help="Workout duration")
                                    with col2:
                                        st.metric("Multiplier", f"{st.session_state.m:.1f}", help="Dynamic movement scaling factor")
                                    with col3:
                                        st.metric("Calculated N", f"{results['n_result']:.3f}", help="Exact number of rounds")
                                    with col4:
                                        st.metric("Total Movements", len(st.session_state.movements), help="Number of different movements")
                                    
                                    # Score breakdown
                                    st.subheader("🎯 Score Breakdown")
                                    if results['max_reps'] > 0:
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Complete Rounds", results['n_floor'], help="Full rounds completed")
                                        with col2:
                                            st.metric("Additional Reps", results['r_result'], help="Extra reps in partial round")
                                        with col3:
                                            st.metric("Max Reps", results['max_reps'], help="Max reps using remaining time")
                                    else:
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.metric("Complete Rounds", results['n_floor'], help="Full rounds completed")
                                        with col2:
                                            st.metric("Additional Reps", results['r_result'], help="Extra reps in partial round")
                                    
                                    # Movement analysis
                                    st.subheader("⚡ Movement Analysis")
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Dynamic Total", f"{results['dmvmt_total']:.1f}s", help="Time for dynamic movements with scaling")
                                    with col2:
                                        st.metric("Static Total", f"{results['smvmt_total']:.1f}s", help="Time for static movements")
                                    with col3:
                                        st.metric("Transition Total", f"{results['tmvmt_total']:.1f}s", help="Time for transitions")
                                    
                                    # Verification section
                                    st.subheader("✅ Calculation Verification")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Calculated Time", f"{results['verification']:.2f}s", help="Time calculated from N value")
                                    with col2:
                                        difference = results['verification_diff']
                                        if difference < 0.001:
                                            st.metric("Accuracy", "✅ Verified", help="Calculation is accurate")
                                        else:
                                            st.metric("Difference", f"{difference:.6f}s", help="Difference from target time")
                                else:
                                    st.error(f"⚠️ Calculation error: {results['error']}")
                            except Exception as e:
                                st.error(f"⚠️ Calculation error: {str(e)}")
        else:
            st.warning("No workout library available. Please check that 'workout_library.json' exists.")
        
        # Load parameters from session state if workout was loaded
        if hasattr(st.session_state, 'tot_tm'):
            tot_tm = st.session_state.tot_tm
        if hasattr(st.session_state, 'm'):
            m = st.session_state.m
        
        # Use loaded movements and provide editing interface
        movements = st.session_state.movements
        
        # Calculate movement totals using the new function
        dmvmt_total, smvmt_total, _ = calculate_movement_totals(movements)
    
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
                    if movement['type'] == 'T':
                        new_desc = st.text_input(f"Description", value=movement['description'], 
                                               disabled=True, key=f"desc_{i}")
                    else:
                        new_desc = st.text_input(f"Description", value=movement['description'], key=f"desc_{i}")
                
                with col2:
                    new_number = st.number_input(f"⏱️ {movement['description']} Time", 
                                               value=float(movement['number']), step=0.1, 
                                               min_value=0.1, key=f"time_{i}",
                                               help="Enter time to see live results update")
                
                with col3:
                    new_type = st.selectbox(f"Type", ["D", "S", "T", "M"], 
                                            index=["D", "S", "T", "M"].index(movement['type']), key=f"type_{i}")
                
                with col4:
                    if new_type == "S":
                        new_count = st.number_input(f"Count", value=int(movement.get('count', 1)), 
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
                    'description': new_desc if new_type != 'T' else "Transition",
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
            dmvmt_total, smvmt_total, _ = calculate_movement_totals(movements)
        
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
            dmvmt_total, smvmt_total, _ = calculate_movement_totals(movements)
        
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
                
                # Calculate movement totals using the new function
                dmvmt_total, smvmt_total, _ = calculate_movement_totals(movements)
                
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
    
    # Calculate button and results (skip for library mode as it's shown at top)
    if movements and tot_tm > 0 and input_method != "Workout Library":
        st.markdown("---")
        
        # Auto-calculate with live updates
        try:
            # Calculate all results using the new unified function
            results = calculate_amrap_results(tot_tm, m, movements)
            
            if results['error'] is None:
                # Simple, clean final score display
                st.markdown("---")
                st.markdown("### 🏆 Final Score")
                
                # Centered score display
                score_col1, score_col2, score_col3 = st.columns([1, 2, 1])
                with score_col2:
                    # Determine workout type for appropriate score display
                    has_max_movement = any(mov.get('count') == -1 for mov in movements)
                    has_regular_movements = any(mov.get('count') != -1 for mov in movements)
                    last_movement_is_max = len(movements) > 0 and movements[-1].get('count') == -1
                    
                    if has_max_movement and has_regular_movements and last_movement_is_max:
                        # "Finish with Max" workout (like Rock) - show only max reps
                        st.markdown(f"# {results['max_reps']}")
                        max_movement_name = next(mov['description'] for mov in movements if mov.get('count') == -1)
                        st.caption(f"{results['max_reps']} {max_movement_name.lower()}")
                    elif has_max_movement and not has_regular_movements:
                        # "Only Max" workout (like 12.1) - show only max reps
                        st.markdown(f"# {results['max_reps']}")
                        max_movement_name = next(mov['description'] for mov in movements if mov.get('count') == -1)
                        st.caption(f"{results['max_reps']} {max_movement_name.lower()}")
                    elif results['max_reps'] > 0:
                        # Traditional AMRAP with max component - show full breakdown
                        st.markdown(f"# {results['total_score']}")
                        st.caption(f"{results['n_floor']} completed rounds + {results['r_result']} additional reps + {results['max_reps']} max reps")
                    else:
                        # Regular AMRAP without max component
                        st.markdown(f"# {results['total_score']}")
                        st.caption(f"{results['n_floor']} completed rounds + {results['r_result']} additional reps")
                
                # Advanced Mode toggle
                st.markdown("---")
                advanced_mode = st.toggle("🔧 Advanced Mode", help="Show detailed metrics, calculations, and debugging info")
                
                if advanced_mode:
                    # Advanced metrics in organized sections
                    st.subheader("📊 Detailed Metrics")
                    
                    # Core calculation breakdown
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Time", f"{tot_tm}s", help="Workout duration")
                    with col2:
                        st.metric("Multiplier", f"{m:.1f}", help="Dynamic movement scaling factor")
                    with col3:
                        st.metric("Calculated N", f"{results['n_result']:.3f}", help="Exact number of rounds")
                    with col4:
                        st.metric("Total Movements", len(movements), help="Number of different movements")
                    
                    # Score breakdown
                    st.subheader("🎯 Score Breakdown")
                    if results['max_reps'] > 0:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Complete Rounds", results['n_floor'], help="Full rounds completed")
                        with col2:
                            st.metric("Additional Reps", results['r_result'], help="Extra reps in partial round")
                        with col3:
                            st.metric("Max Reps", results['max_reps'], help="Max reps using remaining time")
                    else:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Complete Rounds", results['n_floor'], help="Full rounds completed")
                        with col2:
                            st.metric("Additional Reps", results['r_result'], help="Extra reps in partial round")
                    
                    # Movement analysis
                    st.subheader("⚡ Movement Analysis")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Dynamic Total", f"{results['dmvmt_total']:.1f}s", help="Time for dynamic movements with scaling")
                    with col2:
                        st.metric("Static Total", f"{results['smvmt_total']:.1f}s", help="Time for static movements")
                    with col3:
                        st.metric("Transition Total", f"{results['tmvmt_total']:.1f}s", help="Time for transitions")
                    
                    # Verification section
                    st.subheader("✅ Calculation Verification")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Calculated Time", f"{results['verification']:.2f}s", help="Time calculated from N value")
                    with col2:
                        difference = results['verification_diff']
                        if difference < 0.001:
                            st.metric("Accuracy", "✅ Verified", help="Calculation is accurate")
                        else:
                            st.metric("Difference", f"{difference:.6f}s", help="Difference from target time")
                    
                    # Tips and info
                    st.info("💡 **Tip**: Edit movement times above to see how changes affect your score in real-time!")
                
                else:
                    # Simple mode - just show the helpful tip
                    st.info("💡 **Tip**: Edit movement times above to see how changes affect your score. Enable Advanced Mode for detailed breakdowns.")
                    
            else:
                st.error(f"⚠️ Calculation error: {results['error']}")
            
        except Exception as e:
            st.error(f"⚠️ Calculation error: {str(e)}")
            
    elif not movements:
        st.info("👆 Add some movements above to see live calculations.")
    elif tot_tm <= 0:
        st.info("👆 Set a valid total time (TotTm > 0) using the slider above.")

if __name__ == "__main__":
    main()
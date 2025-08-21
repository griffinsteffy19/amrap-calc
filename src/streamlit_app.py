import streamlit as st
import json
import pandas as pd
import os
import random
from calculations import (
    convert_pace_to_time_per_rep, 
    parse_time_input, 
    calculate_amrap_results,
    calculate_for_time_results,
    calculate_movement_totals
)
from movement_library import (
    load_movement_categories,
    get_all_movements,
    get_movements_by_category,
    convert_movement_to_workout_format
)
from workout_library import (
    load_workout_library,
    load_workout_from_library,
    process_workout_movements
)

def get_app_version():
    """Get the current app version from .VERSION file or return default."""
    try:
        # Try to read .VERSION file
        version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src/.VERSION')
        with open(version_file, 'r') as f:
            version = f.read().strip()
            # Add v prefix if not present
            if not version.startswith('v'):
                version = f'v{version}'
            return version
    except:
        pass
    
    # Fallback version
    return "v1.0.0-dev"


def main():
    st.title("Functional Performance Calculator")
    st.markdown("---")
    
    # Sidebar for mode selection
    st.sidebar.header("🎯 Workout Mode")
    st.sidebar.markdown("Choose how you want to create or analyze a workout:")
    
    mode_options = {
        "Workout Library": "🏋️ Browse & Edit Workouts\nLoad pre-built CrossFit workouts",
        "Movement Library": "📚 Explore Movements\nBrowse movement database", 
        "Manual Entry": "✏️ Build Custom Workout\nCreate your own workout from scratch"
    }
    
    # Create a more descriptive selection
    selected_mode = st.sidebar.radio(
        "Select Mode:",
        options=list(mode_options.keys()),
        format_func=lambda x: mode_options[x].split('\n')[0],
        help="Choose your preferred way to work with workouts"
    )
    
    # Show description for selected mode
    st.sidebar.markdown(f"*{mode_options[selected_mode].split(chr(10))[1]}*")
    
    # Add version information and links at bottom of sidebar
    st.sidebar.markdown("---")
    version = get_app_version()
    st.sidebar.markdown(f"**Version:** `{version}`")
    st.sidebar.caption("Functional Performance Calculator")
    
    # Add roadmap and GitHub links
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Project Links")
    st.sidebar.markdown("[🗺️ Development Roadmap](https://github.com/griffinsteffy19/functional-performance-calc/blob/develop/docs/ROADMAP.md)")
    
    # Create URLs with app version for better bug tracking
    import urllib.parse
    
    # Simplified approach - let templates handle most of the content
    bug_params = {
        'template': 'bug_report.md',
        'labels': 'bug',
        'title': '[BUG] Issue from Streamlit App',
        'body': f'**Reported from Streamlit App**\n\nApp Version: {version}\n\n'
    }
    
    feature_params = {
        'template': 'feature_request.md', 
        'labels': 'feature',
        'title': '[FEATURE] Request from Streamlit App',
        'body': f'**Requested from Streamlit App**\n\nApp Version: {version}\n\n'
    }
    
    # Build URLs with proper encoding
    bug_url = 'https://github.com/griffinsteffy19/functional-performance-calc/issues/new?' + urllib.parse.urlencode(bug_params)
    feature_url = 'https://github.com/griffinsteffy19/functional-performance-calc/issues/new?' + urllib.parse.urlencode(feature_params)
    
    st.sidebar.markdown(f"[🐛 Report Bug]({bug_url})")
    st.sidebar.markdown(f"[💡 Request Feature]({feature_url})")
    st.sidebar.markdown("[📖 Documentation](https://github.com/griffinsteffy19/functional-performance-calc/tree/develop/docs)")
    
    input_method = selected_mode
    
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
            # Initialize random workout selection if this is the first time in workout library mode
            if 'random_workout_initialized' not in st.session_state:
                # Pick a random category and workout
                all_categories = list(library_data.keys())
                random_category = random.choice(all_categories)
                
                # Pick a random workout from that category
                random_workouts = list(library_data[random_category]['workouts'].keys())
                if random_workouts:
                    random_workout = random.choice(random_workouts)
                    
                    # Store the random selections
                    st.session_state.random_category = random_category
                    st.session_state.random_workout = random_workout
                    st.session_state.random_workout_initialized = True
            
            # Add random workout button
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader("Select Category")
            with col2:
                if st.button("🎲 Random Workout", help="Pick a random workout from any category"):
                    # Pick a new random category and workout
                    all_categories = list(library_data.keys())
                    random_category = random.choice(all_categories)
                    
                    # Pick a random workout from that category
                    random_workouts = list(library_data[random_category]['workouts'].keys())
                    if random_workouts:
                        random_workout = random.choice(random_workouts)
                        
                        # Store the new random selections
                        st.session_state.random_category = random_category
                        st.session_state.random_workout = random_workout
                        st.rerun()  # Refresh to show the new selection
            
            category_options = {key: f"{data.get('icon', '📋')} {data['name']}" for key, data in library_data.items()}
            
            # Use random category as default if available
            default_category = getattr(st.session_state, 'random_category', list(category_options.keys())[0])
            default_index = list(category_options.keys()).index(default_category) if default_category in category_options else 0
            
            category_key = st.selectbox(
                "Choose workout category:",
                options=list(category_options.keys()),
                index=default_index,
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
                
                # Use random workout as default if we're in the randomly selected category
                default_workout = None
                default_workout_index = 0
                if (category_key == getattr(st.session_state, 'random_category', None) and 
                    hasattr(st.session_state, 'random_workout') and 
                    st.session_state.random_workout in workout_options):
                    default_workout = st.session_state.random_workout
                    default_workout_index = list(workout_options.keys()).index(default_workout)
                
                workout_key = st.selectbox(
                    "Choose workout:",
                    options=list(workout_options.keys()),
                    index=default_workout_index,
                    format_func=lambda x: workout_options[x]
                )
                
                if workout_key:
                    workout_data = category_data['workouts'][workout_key]
                    
                    # Display workout info on one line
                    workout_type = workout_data.get('workout_type', 'amrap')
                    workout_rounds = workout_data.get('rounds', 1)
                    num_movements = len(workout_data['movements'])
                    multiplier = workout_data['m']
                    
                    # Build info string
                    info_parts = []
                    
                    if workout_type == 'for_time':
                        if workout_rounds > 1:
                            info_parts.append(f"🔄 {workout_rounds} rounds")
                        info_parts.append(f"📋 {num_movements} movements per round")
                    else:
                        duration_minutes = workout_data['tot_tm'] // 60
                        info_parts.extend([f"⏱️ {duration_minutes} min", f"📋 {num_movements} movements"])
                    
                    if multiplier != 1.0:
                        info_parts.append(f"⚡ {multiplier}x multiplier")
                    
                    st.markdown(f"**{' • '.join(info_parts)}**")
                    
                    st.info(f"📝 **{workout_data['name']}**: {workout_data['description']}")
                    
                    # Auto-load workout data for immediate editing
                    if 'current_workout_key' not in st.session_state or st.session_state.current_workout_key != workout_key:
                        # Auto-load when workout selection changes
                        st.session_state.movements = []
                        
                        # Process movements (handles both standard format and movement database references)
                        processed_movements = process_workout_movements(workout_data['movements'])
                        
                        # Load processed workout data
                        for movement in processed_movements:
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
                        st.session_state.rounds = workout_data.get('rounds', 1)
                        st.session_state.time_cap = workout_data.get('time_cap')
                        st.session_state.current_workout_key = workout_key
                    
                    
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
                            st.write("**Variety**")
                        with header_cols[3]:
                            st.write("**Time/Rep**")
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
                            
                            # Check if this movement has movement data for variety selection
                            movement_name = None
                            if '(' in movement['description'] and ')' in movement['description']:
                                # Extract movement name from description like "Thruster (medium)"
                                base_name = movement['description'].split('(')[0].strip()
                                movement_name = base_name.lower().replace(' ', '-').replace('/', '-')
                            
                            with col3:
                                if movement['type'] == 'T':
                                    st.write("—")
                                    selected_variety = None
                                elif movement_name:
                                    # Load movement data to get varieties
                                    from movement_library import load_movement
                                    movement_data = load_movement(movement_name)
                                    if movement_data and 'variety' in movement_data:
                                        varieties = list(movement_data['variety'].keys())
                                        # Try to detect current variety from description
                                        current_variety = None
                                        if '(' in movement['description'] and ')' in movement['description']:
                                            current_variety_text = movement['description'].split('(')[1].split(')')[0]
                                            if current_variety_text in varieties:
                                                current_variety = current_variety_text
                                        
                                        if current_variety and current_variety in varieties:
                                            default_index = varieties.index(current_variety)
                                        else:
                                            default_index = 0
                                        
                                        selected_variety = st.selectbox("Variety", varieties, 
                                                                      index=default_index, 
                                                                      key=f"preview_variety_{i}", 
                                                                      label_visibility="collapsed")
                                    else:
                                        st.write("—")
                                        selected_variety = None
                                else:
                                    st.write("—")
                                    selected_variety = None
                            
                            with col4:
                                # Get auto-updated time based on variety selection
                                auto_time = None
                                if movement_name and selected_variety:
                                    from movement_library import get_movement_execution_time
                                    try:
                                        auto_time = get_movement_execution_time(movement_name, selected_variety)
                                    except:
                                        auto_time = None
                                
                                # Show time input with auto-update option
                                if auto_time is not None:
                                    # Use auto-calculated time as default, but allow manual override
                                    default_time = auto_time
                                    # Show indicator that time is auto-calculated
                                    help_text = f"Auto: {auto_time:.1f}s (editable)"
                                else:
                                    default_time = float(movement['number'])
                                    help_text = "Manual time entry"
                                
                                final_time = st.number_input("Time", 
                                                           value=default_time, step=0.1, 
                                                           min_value=0.1, key=f"preview_time_{i}", 
                                                           label_visibility="collapsed",
                                                           help=help_text)
                            
                            with col5:
                                new_type = st.selectbox("Type", ["D", "S", "T", "M"], 
                                                        index=["D", "S", "T", "M"].index(movement['type']), 
                                                        key=f"preview_type_{i}", label_visibility="collapsed")
                            
                            with col6:
                                if new_type == "S":
                                    new_count = st.number_input("Count", value=int(movement.get('count', 1)), 
                                                              step=1, min_value=1, key=f"preview_count_{i}", label_visibility="collapsed")
                                elif new_type == "D":
                                    new_count = st.number_input("Count", value=int(movement.get('count', 1)), 
                                                              step=1, min_value=1, key=f"preview_count_d_{i}", label_visibility="collapsed")
                                elif new_type == "M":
                                    new_count = -1
                                    st.write("MAX")
                                else:  # T type
                                    new_count = int(movement.get('count', 1))
                                    st.write(str(new_count))
                            
                            with col7:
                                if st.button("🗑️", key=f"preview_del_{i}", help="Delete this movement"):
                                    st.session_state.movements.pop(i)
                                    st.rerun()
                            
                            # Update the movement description if variety changed
                            if selected_variety and movement_name:
                                from movement_library import load_movement
                                movement_data = load_movement(movement_name)
                                if movement_data:
                                    updated_desc = f"{movement_data['name']} ({selected_variety})"
                                else:
                                    updated_desc = new_desc
                            else:
                                updated_desc = new_desc
                            
                            # Update the movement in real-time
                            st.session_state.movements[i] = {
                                'description': updated_desc if new_type != 'T' else "Transition",
                                'number': final_time,
                                'type': new_type,
                                'count': new_count
                            }
                        
                        # Parameters editing (collapsible) - only for library workouts
                        with st.expander("📊 Workout Parameters", expanded=False):
                            workout_type = workout_data.get('workout_type', 'amrap')
                            
                            if workout_type == 'for_time':
                                # For Time workouts need rounds, multiplier, and optional time cap
                                st.info("⏱️ For Time workouts predict completion time")
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    current_rounds = workout_data.get('rounds', 1)
                                    new_rounds = st.number_input("Rounds", value=int(current_rounds), step=1, min_value=1, key="preview_rounds")
                                    # Store rounds in session state for calculations
                                    st.session_state.rounds = new_rounds
                                with col2:
                                    new_m = st.number_input("Multiplier (M)", value=float(st.session_state.m), step=0.1, min_value=0.1, key="preview_m")
                                    st.session_state.m = new_m
                                    m = new_m
                                with col3:
                                    current_time_cap = workout_data.get('time_cap', 0)
                                    new_time_cap = st.number_input("Time Cap (sec)", value=int(current_time_cap), step=60, min_value=0, key="preview_time_cap", help="0 = no time cap")
                                    # Store time cap in session state for calculations (convert 0 to None)
                                    st.session_state.time_cap = new_time_cap if new_time_cap > 0 else None
                            else:
                                # AMRAP workouts need both time cap and multiplier
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    new_tot_tm = st.number_input("Total Time (seconds)", value=float(st.session_state.tot_tm), step=1.0, min_value=1.0, key="preview_tot_tm")
                                    st.session_state.tot_tm = new_tot_tm
                                    tot_tm = new_tot_tm
                                with col2:
                                    new_m = st.number_input("Multiplier (M)", value=float(st.session_state.m), step=0.1, min_value=0.1, key="preview_m")
                                    st.session_state.m = new_m
                                    m = new_m
                        
                        # Show Final Score after parameters are set
                        if st.session_state.movements and hasattr(st.session_state, 'tot_tm'):
                            dmvmt_total, smvmt_total, _ = calculate_movement_totals(st.session_state.movements)
                            tot_tm = st.session_state.tot_tm
                            m = st.session_state.m
                            
                            # Calculate and display final score with updated parameters
                            try:
                                # Check workout type
                                workout_type = workout_data.get('workout_type', 'amrap')
                                
                                if workout_type == 'for_time':
                                    # For Time workout - calculate predicted completion time
                                    workout_rounds = getattr(st.session_state, 'rounds', workout_data.get('rounds', 1))
                                    time_cap = getattr(st.session_state, 'time_cap', workout_data.get('time_cap'))
                                    results = calculate_for_time_results(st.session_state.movements, st.session_state.m, workout_rounds, time_cap)
                                    if results['error'] is None:
                                        st.markdown("### 🏆 Final Score")
                                        score_col1, score_col2, score_col3 = st.columns([1, 2, 1])
                                        with score_col2:
                                            if results.get('is_capped', False):
                                                st.markdown(f"# {results['cap_time_formatted']} + {int(results['remaining_reps'])} reps")
                                                st.caption(f"Would finish in {results['total_time_formatted']} without cap")
                                            else:
                                                st.markdown(f"# {results['total_time_formatted']}")
                                                if workout_rounds > 1:
                                                    time_per_round_min = int(results['time_per_round'] // 60)
                                                    time_per_round_sec = int(results['time_per_round'] % 60)
                                                    st.caption(f"{workout_rounds} rounds • {time_per_round_min}:{time_per_round_sec:02d} per round")
                                                else:
                                                    st.caption(f"Estimated completion time")
                                                if time_cap:
                                                    cap_min = int(time_cap // 60)
                                                    cap_sec = int(time_cap % 60)
                                                    st.caption(f"Time cap: {cap_min}:{cap_sec:02d}")
                                    else:
                                        st.error(f"⚠️ Calculation error: {results['error']}")
                                elif tot_tm > 0:
                                    # AMRAP workout - calculate rounds and reps (only if we have valid time)
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
                                                st.markdown(f"# {int(results['max_reps'])}")
                                                max_movement_name = next(mov['description'] for mov in st.session_state.movements if mov.get('count') == -1)
                                                st.caption(f"{int(results['max_reps'])} {max_movement_name.lower()}")
                                            elif has_max_movement and not has_regular_movements:
                                                # "Only Max" workout (like 12.1) - show only max reps
                                                st.markdown(f"# {int(results['max_reps'])}")
                                                max_movement_name = next(mov['description'] for mov in st.session_state.movements if mov.get('count') == -1)
                                                st.caption(f"{int(results['max_reps'])} {max_movement_name.lower()}")
                                            elif int(results['max_reps']) > 0:
                                                # Traditional AMRAP with max component - show rounds+reps format
                                                if int(results['r_result']) > 0:
                                                    st.markdown(f"# {int(results['n_floor'])}+{int(results['r_result'])}+{int(results['max_reps'])} ({int(results['total_reps'])} reps)")
                                                    st.caption(f"{int(results['n_floor'])} rounds + {int(results['r_result'])} reps + {int(results['max_reps'])} max reps")
                                                else:
                                                    st.markdown(f"# {int(results['n_floor'])}+{int(results['max_reps'])} ({int(results['total_reps'])} reps)")
                                                    st.caption(f"{int(results['n_floor'])} rounds + {int(results['max_reps'])} max reps")
                                            else:
                                                # Regular AMRAP without max component
                                                if int(results['r_result']) > 0:
                                                    st.markdown(f"# {int(results['n_floor'])}+{int(results['r_result'])} ({int(results['total_reps'])} reps)")
                                                    st.caption(f"{int(results['n_floor'])} rounds + {int(results['r_result'])} reps")
                                                else:
                                                    st.markdown(f"# {int(results['n_floor'])} ({int(results['total_reps'])} reps)")
                                                    st.caption(f"{int(results['n_floor'])} rounds")
                                    else:
                                        st.error(f"⚠️ Calculation error: {results['error']}")
                                    
                                st.markdown("---")
                                    
                            except Exception as e:
                                st.error(f"⚠️ Calculation error: {str(e)}")
                        
                        # Advanced Mode toggle - after editor
                        st.markdown("---")
                        advanced_mode = st.toggle("🔧 Advanced Mode", help="Show detailed metrics, calculations, and debugging info", key="preview_advanced_mode")
                        
                        if advanced_mode and st.session_state.movements:
                            try:
                                workout_type = workout_data.get('workout_type', 'amrap')
                                
                                if workout_type == 'for_time':
                                    # For Time advanced metrics
                                    workout_rounds = getattr(st.session_state, 'rounds', workout_data.get('rounds', 1))
                                    time_cap = getattr(st.session_state, 'time_cap', workout_data.get('time_cap'))
                                    results = calculate_for_time_results(st.session_state.movements, st.session_state.m, workout_rounds, time_cap)
                                    if results['error'] is None:
                                        st.subheader("📊 Time Breakdown")
                                        
                                        if workout_rounds > 1:
                                            st.info(f"Showing breakdown for {workout_rounds} rounds")
                                        
                                        # Show movement breakdown
                                        for movement in results['movement_breakdown']:
                                            col1, col2, col3, col4, col5 = st.columns(5)
                                            with col1:
                                                st.write(f"**{movement['description']}**")
                                            with col2:
                                                if workout_rounds > 1:
                                                    st.write(f"{movement['count']} × {workout_rounds} = {movement['count_with_rounds']} reps")
                                                else:
                                                    st.write(f"{movement['count']} reps")
                                            with col3:
                                                st.write(f"{movement['time_per_rep']:.1f}s per rep")
                                            with col4:
                                                st.write(f"{movement['total_time']:.1f}s per round")
                                            with col5:
                                                if workout_rounds > 1:
                                                    st.write(f"{movement['total_time_with_rounds']:.1f}s total")
                                                else:
                                                    st.write(f"{movement['total_time']:.1f}s total")
                                        
                                        # Total time summary
                                        if workout_rounds > 1:
                                            st.metric("Total Predicted Time", f"{results['total_time_seconds']:.0f}s ({results['total_time_formatted']}) for {workout_rounds} rounds")
                                            st.metric("Time Per Round", f"{results['time_per_round']:.0f}s")
                                        else:
                                            st.metric("Total Predicted Time", f"{results['total_time_seconds']:.0f}s ({results['total_time_formatted']})")
                                    else:
                                        st.error(f"⚠️ Calculation error: {results['error']}")
                                else:
                                    # AMRAP advanced metrics
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
                                        if int(results['max_reps']) > 0:
                                            col1, col2, col3 = st.columns(3)
                                            with col1:
                                                st.metric("Complete Rounds", int(results['n_floor']), help="Full rounds completed")
                                            with col2:
                                                st.metric("Additional Reps", int(results['r_result']), help="Extra reps in partial round")
                                            with col3:
                                                st.metric("Max Reps", int(results['max_reps']), help="Max reps using remaining time")
                                        else:
                                            col1, col2 = st.columns(2)
                                            with col1:
                                                st.metric("Complete Rounds", int(results['n_floor']), help="Full rounds completed")
                                            with col2:
                                                st.metric("Additional Reps", int(results['r_result']), help="Extra reps in partial round")
                                        
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
            st.warning("No workout library available. Please check that 'data/workouts/index.json' exists.")
        
        # Load parameters from session state if workout was loaded
        if hasattr(st.session_state, 'tot_tm'):
            tot_tm = st.session_state.tot_tm
        if hasattr(st.session_state, 'm'):
            m = st.session_state.m
        
        # Use loaded movements and provide editing interface
        movements = st.session_state.movements
        
        # Calculate movement totals using the new function
        dmvmt_total, smvmt_total, _ = calculate_movement_totals(movements)
    
    elif input_method == "Movement Library":
        # Movement Library section
        st.header("🗂️ Movement Library")
        
        # Clear movements when first entering movement library
        if 'last_input_method' not in st.session_state or st.session_state.last_input_method != "Movement Library":
            st.session_state.movements = []
            st.session_state.last_input_method = "Movement Library"
        
        # Initialize session state for movement library
        if 'selected_movements' not in st.session_state:
            st.session_state.selected_movements = []
        
        # Load movement categories
        categories = load_movement_categories()
        all_movements = get_all_movements()
        
        if categories and all_movements:
            # Category filter
            st.subheader("Browse Movements by Category")
            category_options = ["All"] + list(categories.keys())
            selected_category = st.selectbox(
                "Filter by category:",
                options=category_options,
                format_func=lambda x: "All Categories" if x == "All" else categories[x]["name"]
            )
            
            # Movement selection
            if selected_category == "All":
                available_movements = all_movements
            else:
                available_movements = get_movements_by_category(selected_category)
            
            if available_movements:
                st.subheader("Add Movements to Workout")
                
                # Movement selector
                movement_names = list(available_movements.keys())
                selected_movement = st.selectbox(
                    "Choose movement:",
                    options=movement_names,
                    format_func=lambda x: available_movements[x]["name"]
                )
                
                if selected_movement:
                    movement_data = available_movements[selected_movement]
                    
                    # Display movement info
                    st.info(f"**{movement_data['name']}** - {movement_data['description']}")
                    
                    # Intensity, type, and count selection
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        intensity_options = list(movement_data["variety"].keys())
                        selected_intensity = st.selectbox(
                            "Variety:",
                            options=intensity_options,
                            format_func=lambda x: f"{x.title()} ({movement_data['variety'][x]['execution_time']}s)"
                        )
                        
                        # Show intensity details
                        intensity_info = movement_data["variety"][selected_intensity]
                        st.caption(intensity_info["description"])
                        if "weight_range" in intensity_info:
                            st.caption(f"Weight: {intensity_info['weight_range']}")
                    
                    with col2:
                        movement_type = st.selectbox(
                            "Type:",
                            options=["S", "D", "T", "M"],
                            index=0,
                            help="S=Static, D=Dynamic, T=Transition, M=Max"
                        )
                    
                    with col3:
                        if movement_type == "M":
                            st.write("**Count:** MAX")
                            movement_count = -1
                        elif movement_type == "T":
                            st.write("**Count:** 1")
                            movement_count = 1
                        else:
                            movement_count = st.number_input(
                                "Count:",
                                min_value=1,
                                value=10,
                                help="Number of repetitions"
                            )
                    
                    # Add movement button
                    if st.button("➕ Add Movement"):
                        workout_movement = convert_movement_to_workout_format(
                            selected_movement, movement_count, selected_intensity, movement_type
                        )
                        st.session_state.movements.append(workout_movement)
                        st.success(f"Added {movement_data['name']} ({selected_intensity}) x{movement_count} ({movement_type})")
            
            # Show selected movements
            if st.session_state.movements:
                st.subheader("Current Workout")
                
                # Movement list with removal option
                for i, movement in enumerate(st.session_state.movements):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"{i+1}. {movement['description']} - {movement['count']} reps ({movement['number']}s each)")
                    with col2:
                        if st.button("🗑️", key=f"remove_{i}"):
                            st.session_state.movements.pop(i)
                            st.rerun()
                
                # Clear all button
                if st.button("🗑️ Clear All Movements"):
                    st.session_state.movements = []
                    st.rerun()
        
        movements = st.session_state.movements
        
        # Calculate movement totals using the new function
        dmvmt_total, smvmt_total, _ = calculate_movement_totals(movements)
    
    elif input_method == "Manual Entry":
        # Manual entry section
        st.header("Movement Entry")
        
        # Clear movements when first entering manual entry
        if 'last_input_method' not in st.session_state or st.session_state.last_input_method != "Manual Entry":
            st.session_state.movements = []
            st.session_state.last_input_method = "Manual Entry"
        
        # Workout loading option
        st.subheader("📋 Load Workout (Optional)")
        with st.expander("Load workout from library to customize"):
            # Load workout library
            library_data = load_workout_library()
            
            if library_data:
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    # Category selection
                    category_options = {key: f"{data.get('icon', '📋')} {data['name']}" for key, data in library_data.items()}
                    category_key = st.selectbox(
                        "Category:",
                        options=list(category_options.keys()),
                        format_func=lambda x: category_options[x],
                        key="manual_category"
                    )
                
                with col2:
                    # Workout selection
                    if category_key:
                        category_data = library_data[category_key]
                        workout_options = {key: data['name'] for key, data in category_data['workouts'].items()}
                        workout_key = st.selectbox(
                            "Workout:",
                            options=list(workout_options.keys()),
                            format_func=lambda x: workout_options[x],
                            key="manual_workout"
                        )
                
                with col3:
                    # Load button
                    if st.button("📥 Load Workout"):
                        if category_key and workout_key:
                            workout_data = load_workout_from_library(library_data, category_key, workout_key)
                            if workout_data:
                                # Load movements into manual editor
                                st.session_state.movements = []
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
                                st.session_state.rounds = workout_data.get('rounds', 1)
                                st.session_state.time_cap = workout_data.get('time_cap')
                                
                                st.success(f"✅ Loaded '{workout_data['name']}' with {len(workout_data['movements'])} movements")
                                st.rerun()
        
        # Movement addition section
        st.subheader("➕ Add New Movement")
        
        # Create tabs for different input methods
        database_tab, manual_tab = st.tabs(["📚 From Database", "✏️ Manual Entry"])
        
        movement_input_mode = "Use Movement Database"  # Default to database tab
        
        # Store the active tab for logic below
        if 'active_movement_tab' not in st.session_state:
            st.session_state.active_movement_tab = 0
        
        # Initialize variables that might be used later
        submitted = False
        description = ""
        
        # Database tab content
        with database_tab:
            st.markdown("*Choose a movement from our curated database with pre-configured execution times*")
            # Movement database integration
            all_movements = get_all_movements()
            categories = load_movement_categories()
            
            if all_movements and categories:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    # Category filter
                    category_options = ["All"] + list(categories.keys())
                    selected_category = st.selectbox(
                        "Category:",
                        options=category_options,
                        format_func=lambda x: "All Categories" if x == "All" else categories[x]["name"]
                    )
                
                with col2:
                    # Movement selection
                    if selected_category == "All":
                        available_movements = all_movements
                    else:
                        available_movements = get_movements_by_category(selected_category)
                    
                    if available_movements:
                        movement_names = list(available_movements.keys())
                        selected_movement = st.selectbox(
                            "Movement:",
                            options=movement_names,
                            format_func=lambda x: available_movements[x]["name"]
                        )
                
                with col3:
                    # Variety selection
                    if selected_movement:
                        movement_data = available_movements[selected_movement]
                        variety_options = list(movement_data["variety"].keys())
                        selected_variety = st.selectbox(
                            "Variety:",
                            options=variety_options,
                            format_func=lambda x: f"{x.title()} ({movement_data['variety'][x]['execution_time']}s)"
                        )
                
                with col4:
                    # Movement type selection
                    if selected_movement:
                        movement_type = st.selectbox(
                            "Type:",
                            options=["S", "D", "T", "M"],
                            index=0,
                            help="S=Static, D=Dynamic, T=Transition, M=Max"
                        )
                        
                        # Count input based on type
                        if movement_type == "M":
                            st.write("Count: MAX")
                            movement_count = -1
                        elif movement_type == "T":
                            st.write("Count: 1")
                            movement_count = 1
                        else:
                            movement_count = st.number_input("Count:", value=10, min_value=1)
                
                # Add movement from database
                if st.button("Add Movement from Database", type="primary"):
                    if selected_movement and selected_variety:
                        workout_movement = convert_movement_to_workout_format(
                            selected_movement, movement_count, selected_variety, movement_type
                        )
                        st.session_state.movements.append(workout_movement)
                        st.success(f"Added {movement_data['name']} ({selected_variety}) x{movement_count} ({movement_type})")
            else:
                st.warning("Movement database not available. Try manual entry instead.")
        
        # Manual tab content  
        with manual_tab:
            st.markdown("*Create custom movements with your own execution times and descriptions*")
            # Manual input (existing functionality)
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
            # Use loaded value if available, but ensure it meets minimum requirement
            default_tot_tm = st.session_state.get('tot_tm', 100.0)
            # For "For Time" workouts, tot_tm is 0, so use a sensible default
            if default_tot_tm <= 0:
                default_tot_tm = 100.0
                if 'tot_tm' in st.session_state and st.session_state.tot_tm == 0:
                    st.info("ℹ️ Loaded 'For Time' workout - set time limit for AMRAP calculation")
            tot_tm = st.number_input("Total Time (TotTm)", value=float(default_tot_tm), step=1.0, min_value=1.0)
        with col2:
            # Use loaded value if available
            default_m = st.session_state.get('m', 2.5)
            m = st.number_input("Multiplier (M)", value=float(default_m), step=0.1, min_value=0.1)
    
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
                        st.markdown(f"# {int(results['max_reps'])}")
                        max_movement_name = next(mov['description'] for mov in movements if mov.get('count') == -1)
                        st.caption(f"{int(results['max_reps'])} {max_movement_name.lower()}")
                    elif has_max_movement and not has_regular_movements:
                        # "Only Max" workout (like 12.1) - show only max reps
                        st.markdown(f"# {int(results['max_reps'])}")
                        max_movement_name = next(mov['description'] for mov in movements if mov.get('count') == -1)
                        st.caption(f"{int(results['max_reps'])} {max_movement_name.lower()}")
                    elif int(results['max_reps']) > 0:
                        # Traditional AMRAP with max component - show rounds+reps format
                        if int(results['r_result']) > 0:
                            st.markdown(f"# {int(results['n_floor'])}+{int(results['r_result'])}+{int(results['max_reps'])} ({int(results['total_reps'])} reps)")
                            st.caption(f"{int(results['n_floor'])} rounds + {int(results['r_result'])} reps + {int(results['max_reps'])} max reps")
                        else:
                            st.markdown(f"# {int(results['n_floor'])}+{int(results['max_reps'])} ({int(results['total_reps'])} reps)")
                            st.caption(f"{int(results['n_floor'])} rounds + {int(results['max_reps'])} max reps")
                    else:
                        # Regular AMRAP without max component
                        if int(results['r_result']) > 0:
                            st.markdown(f"# {int(results['n_floor'])}+{int(results['r_result'])} ({int(results['total_reps'])} reps)")
                            st.caption(f"{int(results['n_floor'])} rounds + {int(results['r_result'])} reps")
                        else:
                            st.markdown(f"# {int(results['n_floor'])} ({int(results['total_reps'])} reps)")
                            st.caption(f"{int(results['n_floor'])} rounds")
                
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
                    if int(results['max_reps']) > 0:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Complete Rounds", int(results['n_floor']), help="Full rounds completed")
                        with col2:
                            st.metric("Additional Reps", int(results['r_result']), help="Extra reps in partial round")
                        with col3:
                            st.metric("Max Reps", int(results['max_reps']), help="Max reps using remaining time")
                    else:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Complete Rounds", int(results['n_floor']), help="Full rounds completed")
                        with col2:
                            st.metric("Additional Reps", int(results['r_result']), help="Extra reps in partial round")
                    
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
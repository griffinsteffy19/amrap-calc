import streamlit as st
import math
import json
import pandas as pd

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
            st.error("Error: No valid solution (both coefficients are zero)")
            return None
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
    input_method = st.sidebar.radio("Choose input method:", ["Manual Entry", "JSON Upload"])
    
    # Initialize session state for movements
    if 'movements' not in st.session_state:
        st.session_state.movements = []
    
    movements = []
    dmvmt_total = 0
    smvmt_total = 0
    tot_tm = 0
    m = 1
    
    if input_method == "Manual Entry":
        # Manual entry section
        st.header("Movement Entry")
        
        # Add movement form
        with st.form("add_movement"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                description = st.text_input("Description")
            with col2:
                number = st.number_input("1 Rep Exec Time", value=0.0, step=0.1)
            with col3:
                movement_type = st.selectbox("Type", ["D", "S", "T"])
            
            submitted = st.form_submit_button("Add Movement")
            
            if submitted and description:
                new_movement = {
                    'description': description,
                    'number': number,
                    'type': movement_type
                }
                st.session_state.movements.append(new_movement)
                st.success(f"Added: {description} - {number} ({movement_type})")
        
        # Display current movements
        if st.session_state.movements:
            st.subheader("Current Movements")
            
            # Create a DataFrame for better display
            df = pd.DataFrame(st.session_state.movements)
            st.dataframe(df)
            
            # Clear movements button
            if st.button("Clear All Movements"):
                st.session_state.movements = []
                st.rerun()
            
            movements = st.session_state.movements
            dmvmt_total = sum(mov['number'] for mov in movements if mov['type'] == 'D')
            smvmt_total = sum(mov['number'] for mov in movements if mov['type'] in ['S', 'T'])
        
        # Other parameters
        st.header("Parameters")
        col1, col2 = st.columns(2)
        
        with col1:
            tot_tm = st.number_input("Total Time (TotTm)", value=0.0, step=1.0)
        with col2:
            m = st.number_input("Multiplier (M)", value=1.0, step=0.1)
    
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
                        "type": "S"
                    },
                    {
                        "description": "Running movement",
                        "number": 8.0,
                        "type": "D"
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
                
                # Calculate totals
                dmvmt_total = sum(mov['number'] for mov in movements if mov.get('type', '').upper() == 'D')
                smvmt_total = sum(mov['number'] for mov in movements if mov.get('type', '').upper() in ['S', 'T'])
                
                # Display loaded data
                st.success("JSON file loaded successfully!")
                st.subheader("Loaded Movements")
                df = pd.DataFrame(movements)
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
        
        # Summary
        st.subheader("Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Movements", len(movements))
        with col2:
            st.metric("Total Dmvmt", f"{dmvmt_total:.1f}")
        with col3:
            st.metric("Total Smvmt", f"{smvmt_total:.1f}")
        with col4:
            st.metric("Multiplier", f"{m:.1f}")
        
        # Debug option
        show_debug = st.checkbox("Show detailed calculations")
        
        if st.button("Calculate Score", type="primary"):
            # Calculate N
            n_result = calculate_n(tot_tm, m, dmvmt_total, smvmt_total)
            
            if n_result is not None:
                st.success("Calculation completed!")
                
                # Results
                st.subheader("Results")
                n_floor = math.floor(n_result)
                
                # Calculate R
                r_result = calculate_r(n_result, m, movements, dmvmt_total, smvmt_total, show_debug)
                
                # Display final score prominently
                st.markdown("### Final Score")
                st.markdown(f"## {n_floor} + {r_result}")
                
                if show_debug:
                    st.subheader("Debug Information")
                    
                    # Verification
                    verification = verify_solution(n_result, m, dmvmt_total, smvmt_total)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Calculated N", f"{n_result:.6f}")
                        st.metric("Floor N", n_floor)
                        st.metric("R", r_result)
                    
                    with col2:
                        st.metric("Verification", f"{verification:.6f}")
                        st.metric("Target TotTm", tot_tm)
                        st.metric("Difference", f"{abs(verification - tot_tm):.6f}")
    
    elif not movements:
        st.info("Please add some movements to calculate the score.")
    elif tot_tm <= 0:
        st.info("Please enter a valid total time (TotTm > 0).")

if __name__ == "__main__":
    main()
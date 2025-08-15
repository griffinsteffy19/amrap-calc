"""
AMRAP Movement Time Calculator - Core Calculation Logic

This module contains all the mathematical functions for calculating AMRAP workout results,
separated from the Streamlit UI logic.

Main Functions:
- calculate_amrap_results(): Complete AMRAP calculation with all results
- calculate_movement_totals(): Calculate totals for different movement types
- convert_pace_to_time_per_rep(): Convert pace formats to time per rep
- parse_time_input(): Parse time strings like "2:30"

This separation allows for:
- Easy testing of calculation logic
- Reuse in other applications (CLI, API, etc.)
- Clear separation of concerns between math and UI
"""

import math


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


def calculate_movement_totals(movements):
    """
    Calculate movement totals for different types
    
    Args:
        movements: List of movement dictionaries
        
    Returns:
        tuple: (dmvmt_total, smvmt_total, tmvmt_total)
    """
    dmvmt_total = sum(
        mov['number'] * mov.get('count', 1) 
        for mov in movements 
        if mov.get('type', '').upper() == 'D' and mov.get('count', 1) != -1
    )
    
    smvmt_total = sum(
        mov['number'] * mov.get('count', 1) 
        for mov in movements 
        if mov.get('type', '').upper() in ['S', 'T'] and mov.get('count', 1) != -1
    )
    
    tmvmt_total = sum(
        mov['number'] * mov.get('count', 1) 
        for mov in movements 
        if mov.get('type', '').upper() == 'T'
    )
    
    return dmvmt_total, smvmt_total, tmvmt_total


def calculate_n(tot_tm, m, dmvmt, smvmt):
    """
    Calculate N using the quadratic formula for:
    TotTm = M * (1 + 2 + ... + N) * Dmvmt + (N * Smvmt)
    
    Args:
        tot_tm: Total time in seconds
        m: Multiplier for dynamic movements
        dmvmt: Total dynamic movement time
        smvmt: Total static movement time
        
    Returns:
        float: The calculated N value, or None if no valid solution
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
        return None  # No real solution
    
    # Calculate both solutions
    n1 = (-b + math.sqrt(discriminant)) / (2 * a)
    n2 = (-b - math.sqrt(discriminant)) / (2 * a)
    
    # Return the positive solution
    if n1 > 0:
        return n1
    elif n2 > 0:
        return n2
    else:
        return None  # No positive solution


def verify_solution(n, m, dmvmt, smvmt):
    """
    Verify the solution by calculating the total time
    
    Args:
        n: The N value to verify
        m: Multiplier for dynamic movements
        dmvmt: Total dynamic movement time
        smvmt: Total static movement time
        
    Returns:
        float: The calculated total time
    """
    triangular_sum = n * (n + 1) / 2
    calculated_total = m * triangular_sum * dmvmt + n * smvmt
    return calculated_total


def calculate_max_reps(tot_tm, n_result, m, movements, dmvmt_total, smvmt_total):
    """
    Calculate max reps for M-type movements based on remaining time
    
    Args:
        tot_tm: Total time in seconds
        n_result: The calculated N value
        m: Multiplier for dynamic movements
        movements: List of movement dictionaries
        dmvmt_total: Total dynamic movement time
        smvmt_total: Total static movement time
        
    Returns:
        int: Total max reps possible
    """
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


def calculate_r(n_result, m, movements, dmvmt_total, smvmt_total):
    """
    Calculate R based on the movements and remaining capacity
    
    Args:
        n_result: The calculated N value
        m: Multiplier for dynamic movements
        movements: List of movement dictionaries (adjusted for R calculation)
        dmvmt_total: Total dynamic movement time
        smvmt_total: Total static movement time
        
    Returns:
        int: The R value (additional reps beyond floor(N))
    """
    n_floor = math.floor(n_result)
    r = 0
    
    # Calculate remaining using totals
    remaining = math.floor((n_result - n_floor) * (m * (n_floor + 1) * dmvmt_total + smvmt_total))
    
    # Process each movement to calculate R
    for i, movement in enumerate(movements):
        mov_type = movement['type'].upper()
        mov_tm = movement['number']
        
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
                if mov_type in ["D", "S"]:
                    r += addition
                remaining -= (multiplier * (n_floor + 1) * mov_tm)
            else:
                # Add remaining/mov_tm to R
                if mov_tm != 0:  # Avoid division by zero
                    addition = remaining / mov_tm
                    if mov_type in ["D", "S"]:
                        r += math.floor(addition)
                    remaining = 0
                    break
    
    return r


def calculate_amrap_results(tot_tm, m, movements):
    """
    Main function to calculate complete AMRAP results
    
    Args:
        tot_tm: Total time in seconds
        m: Multiplier for dynamic movements
        movements: List of movement dictionaries
        
    Returns:
        dict: Complete results including N, R, max_reps, and totals
    """
    # Calculate movement totals
    dmvmt_total, smvmt_total, tmvmt_total = calculate_movement_totals(movements)
    
    # Calculate N
    n_result = calculate_n(tot_tm, m, dmvmt_total, smvmt_total)
    
    if n_result is None:
        return {
            'error': 'No valid solution found',
            'n_result': None,
            'n_floor': 0,
            'r_result': 0,
            'max_reps': 0,
            'total_score': 0,
            'dmvmt_total': dmvmt_total,
            'smvmt_total': smvmt_total,
            'tmvmt_total': tmvmt_total,
            'verification': None
        }
    
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
    
    r_result = calculate_r(n_result, m, r_movements, dmvmt_total, smvmt_total)
    
    # Calculate max reps for M-type movements
    max_reps = calculate_max_reps(tot_tm, n_result, m, movements, dmvmt_total, smvmt_total)
    
    # Calculate total score
    total_r = r_result + max_reps
    total_score = n_floor + total_r
    
    # Verify solution
    verification = verify_solution(n_result, m, dmvmt_total, smvmt_total)
    verification_diff = abs(verification - tot_tm) if verification is not None else None
    
    return {
        'error': None,
        'n_result': n_result,
        'n_floor': n_floor,
        'r_result': r_result,
        'max_reps': max_reps,
        'total_r': total_r,
        'total_score': total_score,
        'dmvmt_total': dmvmt_total,
        'smvmt_total': smvmt_total,
        'tmvmt_total': tmvmt_total,
        'verification': verification,
        'verification_diff': verification_diff
    }
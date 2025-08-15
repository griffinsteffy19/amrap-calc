# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Overview

This is an AMRAP (As Many Reps As Possible) Movement Time Calculator built with Streamlit. The application solves quadratic equations to calculate optimal workout scores based on movement timing, multipliers, and total time constraints.

### Key Functions

- `calculate_n()` - Solves the quadratic equation for N using the formula: TotTm = M * (1 + 2 + ... + N) * Dmvmt + (N * Smvmt)
- `calculate_r()` - Calculates the R component based on remaining capacity and movement types
- `verify_solution()` - Validates calculated results against the original equation

## Running the Application

```bash
streamlit run streamlit_app.py
```

## Movement Types

The application supports four movement types:
- **D** (Dynamic): Uses multiplier M in calculations
- **S** (Static): Base execution time without multiplier, can have count > 1
- **T** (Time): Similar to Static but excluded from R calculations (transitions)
- **M** (Max): Maximum reps until AMRAP completion - consumes all remaining time

## Core Architecture

### Input Methods
1. **Manual Entry**: Interactive form for adding movements one by one
2. **JSON Upload**: Bulk import of movements and parameters

### Calculation Flow
1. Parse movements and calculate total Dmvmt and Smvmt times (excluding M-type movements)
2. Solve quadratic equation for N value using regular movements
3. Calculate R based on remaining capacity distribution across regular movements
4. Calculate max reps for M-type movements using remaining time after N rounds
5. Present final score as floor(N) + R + max_reps

### Session State
- `st.session_state.movements` - Maintains movement list across interactions

## Data Structure

Movement objects contain:
```python
{
    'description': str,  # Movement name/description
    'number': float,     # 1-rep execution time
    'type': str,        # 'D', 'S', 'T', or 'M'
    'count': int        # Number of reps (1 for D/T, variable for S, -1 for M)
}
```

JSON input format:

```json
{
    "tot_tm": float,     # Total time available
    "m": float,          # Multiplier for dynamic movements
    "movements": [...]   # Array of movement objects
}
```
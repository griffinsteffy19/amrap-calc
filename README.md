# AMRAP Movement Time Calculator

A Streamlit web application for calculating workout scores and predicted completion times for CrossFit-style workouts. Supports both **AMRAP** (As Many Rounds As Possible) and **For Time** workout formats with real-time score calculation.

## Features

### Three Input Modes
- **🏋️ Workout Library** - Choose from pre-built CrossFit workouts (Girl, Hero, Open, etc.)
- **🗂️ Movement Library** - Build custom workouts from standardized movements with intensity levels
- **✏️ Manual Entry** - Create workouts from scratch with full customization

### Workout Types
- **AMRAP Workouts** - Calculate rounds + reps achieved in a time limit
- **For Time Workouts** - Predict completion time with optional time caps
- **Real-time Updates** - Live score calculation as you edit parameters

### Movement Library
- **Intensity-Based Timing** - Movements have different execution times based on intensity
- **Category Organization** - Weightlifting, Gymnastics, and Monostructural movements
- **Realistic Scaling** - Light/Medium/Heavy for weights, Kipping/Strict for gymnastics, etc.

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd amrap-calc
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run src/streamlit_app.py
```

4. Open your browser to `http://localhost:8501`

## Usage

### Using the Workout Library
1. Select "Workout Library" from the sidebar
2. Choose a category (Girl, Hero, Open, etc.)
3. Pick a specific workout
4. Adjust parameters if needed
5. View real-time score calculations

### Building with Movement Library
1. Select "Movement Library" from the sidebar
2. Browse movements by category
3. Choose movement and intensity level
4. Set repetition count
5. Add to workout and see instant results

### Manual Entry
1. Select "Manual Entry" from the sidebar
2. Add movements one by one
3. Configure timing and repetitions
4. Set workout parameters (time limit, rounds, etc.)

## Project Structure

```
├── src/                          # Source code
│   ├── streamlit_app.py         # Main UI application
│   ├── calculations.py          # Mathematical calculation engine
│   ├── movement_library.py      # Movement data loading
│   └── workout_library.py       # Workout data loading
├── data/                         # Data files
│   ├── workouts/                # Pre-built workout database
│   │   ├── girl/               # Girl workouts (Fran, Annie, etc.)
│   │   ├── hero/               # Hero workouts (Murph, Chad, etc.)
│   │   ├── open/               # CrossFit Open workouts
│   │   └── classic/            # Classic AMRAP workouts
│   └── movements/               # Movement library
│       ├── weightlifting/      # Barbell/dumbbell movements
│       ├── gymnastics/         # Bodyweight movements
│       └── monostructural/     # Cardio movements
├── scripts/                     # Build and release scripts
├── docs/                        # Documentation
└── requirements.txt             # Python dependencies
```

## How It Works

### Calculation Engine
The app uses a mathematical model based on:
- **Quadratic formula** for calculating exact round completion
- **Movement types** that behave differently:
  - **Static (S)** - Consistent time per rep
  - **Dynamic (D)** - Gets harder over time (fatigue)
  - **Transition (T)** - Rest/setup time
  - **Max (M)** - Unlimited reps in remaining time

### Movement Categories vs Types
- **Categories** organize movements by equipment/style (weightlifting, gymnastics, monostructural)
- **Types** define calculation behavior (S/D/T/M) independent of category

### Intensity Levels
Different movement categories have appropriate intensity structures:
- **Weightlifting**: Light/Medium/Heavy (weight-based)
- **Gymnastics**: Kipping/Strict, Modified/Standard/Complex (technique-based)
- **Monostructural**: Easy/Moderate/Fast/Sprint (pace-based)

## Example Workouts

### Fran (Girl Workout)
- 21-15-9 Thrusters (95/65 lb) and Pull-ups
- For Time with predicted completion

### Murph (Hero Workout)  
- 1 mile Run, 100 Pull-ups, 200 Push-ups, 300 Squats, 1 mile Run
- For Time with 20/14 lb vest

### AMRAP Examples
- 7 minutes of Burpees
- 20 minutes of 5 Pull-ups, 10 Push-ups, 15 Squats

## Development

### Running in Development Mode
```bash
streamlit run src/streamlit_app.py --server.fileWatcherType watchdog
```

### Project Commands
See [CLAUDE.md](CLAUDE.md) for detailed development commands and architecture documentation.

### Adding New Workouts
1. Create JSON file in appropriate `data/workouts/` category
2. Follow existing workout format
3. Include movement definitions with timing

### Adding New Movements
1. Create JSON file in appropriate `data/movements/` category
2. Define intensity levels with execution times
3. Include scaling and description information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license here]

## Acknowledgments

- Built for the CrossFit community
- Inspired by real CrossFit workout programming
- Mathematical model based on empirical workout data
# AMRAP Movement Time Calculator

A comprehensive Streamlit web application for calculating workout scores and predicted completion times for CrossFit-style workouts. Features a sophisticated movement database, interactive workout library, and real-time calculations for both **AMRAP** (As Many Rounds As Possible) and **For Time** workout formats.

## ✨ Features

### 🎯 Three Workout Modes
- **🏋️ Browse & Edit Workouts** - Load pre-built CrossFit workouts with live editing capabilities
- **📚 Explore Movements** - Browse curated movement database with detailed variety information
- **✏️ Build Custom Workout** - Create workouts from scratch with full customization

### 💪 Enhanced Movement System
- **Movement Database Integration** - Centralized movement definitions with variety-based execution times
- **Live Workout Editor** - Real-time variety selection with automatic time updates
- **Smart Movement References** - Workouts reference movement database for consistency and maintainability

### 🏃 Workout Types
- **AMRAP Workouts** - Calculate rounds + reps achieved in a time limit
- **For Time Workouts** - Predict completion time with optional time caps and rounds
- **Real-time Updates** - Live score calculation as you edit parameters
- **Integer Display** - Clean rep counts without decimal places

### 📖 Comprehensive Movement Library
- **19+ Movements** - Covering all major CrossFit movement patterns
- **Variety-Based Timing** - Multiple execution times per movement (light/medium/heavy, kipping/strict, etc.)
- **Three Categories** - Weightlifting, Gymnastics, and Monostructural movements
- **Automatic Integration** - Workout library seamlessly references movement database

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

## 🚀 Usage

### 🏋️ Browse & Edit Workouts Mode
1. Select "Browse & Edit Workouts" from the sidebar
2. Choose a category (Girl, Hero, Open, Classic)
3. Pick a specific workout (loads automatically)
4. Use the **Live Workout Editor** to:
   - Change movement varieties (auto-updates execution times)
   - Manually override execution times if needed
   - Adjust rep counts and movement types
   - Modify workout parameters (rounds, time caps)
5. View real-time score calculations

### 📚 Explore Movements Mode
1. Select "Explore Movements" from the sidebar
2. Browse movements by category (Weightlifting, Gymnastics, Monostructural)
3. View detailed movement information, varieties, and scaling options
4. Use **"From Database"** tab to add movements to custom workouts
5. Use **"Manual Entry"** tab for completely custom movements

### ✏️ Build Custom Workout Mode
1. Select "Build Custom Workout" from the sidebar
2. Choose between database movements or manual entry
3. Add movements with appropriate varieties and rep counts
4. Load existing workouts from library for customization
5. Set workout parameters and see instant results

## 📁 Project Structure

```
├── VERSION                       # Version tracking file
├── src/                          # Source code
│   ├── streamlit_app.py         # Main UI application with enhanced interface
│   ├── calculations.py          # Mathematical calculation engine
│   ├── movement_library.py      # Movement database management
│   └── workout_library.py       # Workout data processing with movement references
├── data/                         # Data files
│   ├── workouts/                # Pre-built workout database (updated to reference movements)
│   │   ├── girl/               # Girl workouts (Fran, Annie, Cindy, etc.)
│   │   ├── hero/               # Hero workouts (Murph, Chad, Nate, etc.)
│   │   ├── open/               # CrossFit Open workouts (11.6, 12.1, 17.1, etc.)
│   │   ├── classic/            # Classic AMRAP workouts
│   │   └── example/            # Demo workouts
│   └── movements/               # Comprehensive movement library
│       ├── index.json          # Movement category definitions
│       ├── weightlifting/      # Barbell/dumbbell movements (thrusters, cleans, etc.)
│       ├── gymnastics/         # Bodyweight movements (pull-ups, burpees, etc.)
│       └── monostructural/     # Cardio movements (running, rowing, biking)
├── scripts/                     # Build and release scripts (updated for VERSION file)
│   ├── release.sh              # Standard release with VERSION file updates
│   ├── release-clean.sh        # Clean packaged release
│   └── release-github.sh       # GitHub release creation
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

### Variety Levels
Different movement categories have appropriate variety structures:
- **Weightlifting**: Light/Medium/Heavy (weight-based)
- **Gymnastics**: Kipping/Strict, Modified/Standard/Complex (technique-based)
- **Monostructural**: Easy/Moderate/Fast/Sprint (pace-based)

## 🆕 Recent Improvements

### Live Workout Editor
- **Real-time variety selection** - Change movement varieties and see execution times update instantly
- **Manual override capability** - Automatic times from database, but fully editable
- **Simplified interface** - Removed complex input modes in favor of intuitive tabs
- **Integer rep display** - Clean final scores without decimal places

### Enhanced Movement Database
- **Movement references** - Workouts now reference centralized movement definitions
- **Variety-based execution times** - Each movement variety has specific timing
- **Comprehensive coverage** - Added missing movements like pistol squats, ring HSPU, burpee box jump-overs
- **Consistent naming** - Singular movement file names (thruster.json, not thrusters.json)

### Improved User Interface
- **Descriptive mode selection** - Clear explanations of each workout mode
- **Tab-based movement input** - Intuitive separation of database vs manual entry
- **Version display** - Always know which version you're running
- **Better visual hierarchy** - Icons, descriptions, and progressive disclosure

### Developer Experience
- **VERSION file system** - Simplified version management without git dependencies
- **Updated release scripts** - All three release workflows now handle VERSION file automatically
- **Enhanced .releasefiles** - Proper inclusion of new src/ structure and VERSION file

## 💪 Example Workouts

### Fran (Girl Workout)
- **21-15-9** Thrusters (medium variety) and Pull-ups (kipping variety)
- **For Time** with predicted completion and round breakdown

### Murph (Hero Workout)  
- **1 mile Run** (moderate pace), 100 Pull-ups, 200 Push-ups, 300 Squats, 1 mile Run
- **For Time** with vest, showing detailed time predictions

### Cindy (Girl Workout)
- **20 minute AMRAP** of 5 Pull-ups, 10 Push-ups, 15 Air Squats
- Shows rounds + reps format with total rep count

### Open 11.6 
- **7 minute AMRAP** ascending ladder of Thrusters and Burpees
- Dynamic movement types that get harder over time

## 🔧 Development

### Running in Development Mode
```bash
streamlit run src/streamlit_app.py --server.fileWatcherType watchdog
```

### Project Commands
See [CLAUDE.md](CLAUDE.md) for detailed development commands and architecture documentation.

### Adding New Workouts
1. Create JSON file in appropriate `data/workouts/` category
2. Use movement references instead of hardcoded definitions:
   ```json
   {
     "movement_name": "thruster",
     "variety": "medium", 
     "type": "D",
     "count": 21
   }
   ```
3. Workouts automatically get movement timing from database

### Adding New Movements
1. Create JSON file in appropriate `data/movements/` category (use singular names)
2. Define variety levels with execution times:
   ```json
   {
     "name": "Thruster",
     "category": "weightlifting",
     "variety": {
       "light": {"execution_time": 2.0},
       "medium": {"execution_time": 2.5},
       "heavy": {"execution_time": 3.0}
     }
   }
   ```
3. Include scaling and description information

### Release Management
Three release scripts available:
- `./scripts/release.sh` - Standard release
- `./scripts/release-clean.sh` - Packaged release with archives
- `./scripts/release-github.sh` - GitHub release creation

All scripts automatically update the VERSION file and create proper git tags.

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
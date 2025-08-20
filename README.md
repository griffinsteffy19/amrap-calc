# Functional Performance Calculator

A comprehensive Streamlit web application for calculating workout scores and predicted completion times for functional fitness workouts. Features a sophisticated movement database, interactive workout library, and real-time calculations for both **AMRAP** (As Many Rounds As Possible) and **For Time** workout formats.

[![GitHub Project](https://img.shields.io/badge/GitHub-Project%20Board-blue?logo=github)](https://github.com/users/griffinsteffy19/projects/2)
[![Issues](https://img.shields.io/github/issues/griffinsteffy19/amrap-calc)](https://github.com/griffinsteffy19/amrap-calc/issues)
[![Development Roadmap](https://img.shields.io/badge/📋-Development%20Roadmap-green)](https://github.com/griffinsteffy19/amrap-calc/blob/develop/docs/ROADMAP.md)

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
git clone https://github.com/griffinsteffy19/amrap-calc.git
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
│   ├── ROADMAP.md              # Development roadmap and GitHub integration
│   └── ARCHITECTURE.md         # Frontend/backend separation architecture
└── requirements.txt             # Python dependencies
```

## 📋 Development Roadmap

We're actively developing the next generation of the Functional Performance Calculator with a comprehensive roadmap for frontend/backend separation, database integration, and enhanced features.

### 🗺️ **[View Full Roadmap →](https://github.com/griffinsteffy19/amrap-calc/blob/develop/docs/ROADMAP.md)**

### Current Phase: Architecture Foundation
- **Goal**: Separate frontend and backend concerns with clean API layer
- **Timeline**: Weeks 1-2 (Aug 21 - Sep 3, 2024)
- **Status**: 🚧 Planning & Design

### Upcoming Phases
- **Phase 2**: Database Migration (JSON → PostgreSQL)
- **Phase 3**: Django Backend with REST API
- **Phase 4**: User accounts, workout history, advanced search
- **Phase 5**: Mobile apps, analytics, community features

### 🚀 Get Involved
The app includes direct links to participate in development:

- **🐛 Report Bugs**: Found an issue? Report it directly from the app sidebar
- **💡 Request Features**: Have ideas? Submit feature requests with one click
- **📋 Track Progress**: Follow development on our [GitHub Project Board](https://github.com/users/griffinsteffy19/projects/2)
- **📖 Read Docs**: View detailed [architecture plans](https://github.com/griffinsteffy19/amrap-calc/blob/develop/docs/ARCHITECTURE.md)

## 🤝 Community & Contributing

### From the App
The Streamlit app includes integrated community features:
- **Version tracking** - Always shows current version (v1.3.3+)
- **Direct bug reporting** - One-click access to GitHub issues with app version pre-filled
- **Feature requests** - Submit ideas directly from the app interface
- **Roadmap access** - View development progress and upcoming features

### GitHub Integration
- **📋 [Project Board](https://github.com/users/griffinsteffy19/projects/2)** - Track all development progress
- **🏷️ [Milestones](https://github.com/griffinsteffy19/amrap-calc/milestones)** - Major release planning
- **🐛 [Issues](https://github.com/griffinsteffy19/amrap-calc/issues)** - Bug reports and feature requests
- **🔄 [Workflows](https://github.com/griffinsteffy19/amrap-calc/actions)** - Automated roadmap sync and releases

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
- **Integrated project links** - Direct access to roadmap, bug reports, and feature requests

### Developer Experience
- **VERSION file system** - Simplified version management without git dependencies
- **Updated release scripts** - All three release workflows now handle VERSION file automatically
- **Enhanced .releasefiles** - Proper inclusion of new src/ structure and VERSION file
- **GitHub integration** - Automated project board and issue tracking

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

We welcome contributions! Here are several ways to get involved:

### 🚀 Quick Start
1. **From the app**: Use sidebar links to report bugs or request features
2. **Check the roadmap**: Review our [development roadmap](https://github.com/griffinsteffy19/amrap-calc/blob/develop/docs/ROADMAP.md) for current priorities
3. **Pick an issue**: Browse [open issues](https://github.com/griffinsteffy19/amrap-calc/issues) and find one that matches your skills

### 💻 Development Process
1. **Fork the repository** and clone locally
2. **Create a feature branch** from `develop` branch:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and test thoroughly
4. **Follow existing patterns** - check ARCHITECTURE.md for coding standards
5. **Submit a pull request** targeting the `develop` branch

### 📋 Contribution Areas
- **🐛 Bug Fixes** - Fix issues reported by users
- **💡 New Features** - Implement roadmap items or approved feature requests
- **📖 Documentation** - Improve README, add code comments, update architecture docs
- **🧪 Testing** - Add test coverage for existing features
- **🎨 UI/UX** - Enhance the Streamlit interface and user experience
- **📊 Data** - Add new workouts or movements to the database

### 🏷️ Issue Labels
- `bug` - Something isn't working
- `feature` - New functionality requests
- `roadmap` - Items from the development roadmap
- `phase-1` through `phase-5` - Roadmap phases
- `priority-high/medium/low` - Issue priority levels

### 📋 Project Workflow
All contributions go through our [GitHub Project Board](https://github.com/users/griffinsteffy19/projects/2):
- **💡 Ideas** - New feature proposals for evaluation
- **📋 Backlog** - Approved issues ready for development
- **🚧 In Progress** - Currently being worked on
- **👀 Review** - Pending review and testing
- **✅ Done** - Completed work

### Development Commands
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed development setup and commands.

## License

[Add your license here]

## Acknowledgments

- Built for the CrossFit community
- Inspired by real CrossFit workout programming
- Mathematical model based on empirical workout data
# CrossFit Workout Library

This folder contains the CrossFit AMRAP workout library organized by traditional CrossFit categories, with each workout in its own JSON file.

## Structure

```
workout_library/
├── index.json                        # Category index and metadata
├── classic/                          # 🏋️ Classic CrossFit AMRAPs
│   ├── cindy.json
│   └── tabata_something.json
├── girl/                             # 👩 Girl workouts (female names)
│   ├── mary.json
│   ├── annie.json
│   └── barbara.json
├── hero/                             # 🎖️ Hero workouts (memorial)
│   ├── murph.json
│   └── dt.json
├── example/                          # 📚 Feature demonstrations
│   ├── pace_demo.json
│   ├── max_reps_demo.json
│   └── movement_types_demo.json
└── README.md                         # This file
```

## Adding New Categories

1. Create a new folder (e.g., `new_category/`)
2. Add workout JSON files to the folder
3. Add the category to `index.json`
4. Follow the existing format structure

## Adding New Workouts

1. Create a new JSON file in the appropriate category folder
2. Follow the workout file format below
3. Use a descriptive filename (e.g., `workout_name.json`)

## Workout File Format

```json
{
  "name": "Workout Display Name",
  "description": "Workout description with details",
  "tot_tm": 1200,  // Total time in seconds
  "m": 2.0,        // Multiplier for dynamic movements
  "movements": [   // Array of movement objects
    {
      "description": "Movement name",
      "number": 5.0,           // Time per rep in seconds
      "type": "S",             // D/S/T/M
      "count": 10,             // Reps (-1 for max)
      "input_mode": "Time per Rep",     // Optional
      "original_input": "5.0",          // Optional
      "rep_size": 1                     // Optional
    }
  ]
}
```

## Index File Format

```json
{
  "categories": {
    "category_key": {
      "file": "category_file.json",
      "name": "Display Name",
      "description": "Category description",
      "icon": "🏋️"
    }
  }
}
```

## Movement Types

- **D** (Dynamic): Uses multiplier, time scales with round number
- **S** (Static): Fixed time per rep, can have multiple reps
- **T** (Transition): Like static but excluded from R calculations
- **M** (Max): Maximum reps until time runs out

## Current Categories

- **🏋️ Classic CrossFit**: Foundational AMRAP workouts (Cindy, Tabata Something Else)
- **👩 Girl Workouts**: Named workouts with female names (Mary, Annie, Barbara)
- **🎖️ Hero Workouts**: Memorial workouts honoring fallen heroes (Murph, DT)
- **📚 Feature Examples**: Demonstrations of calculator features (Pace Demo, Max Reps Demo, Movement Types Demo)

## TODO: Additional Hero Workouts to Parse

The following hero workouts from heros.md need manual parsing due to complex formats or special requirements:

### Complex Multi-Round Workouts
- **The Seven** - 7 rounds, 7 different movements, specific weights
- **Badger** - Complex structure with multiple rounds  
- **Hansen** - Multiple round structure
- **Tyler** - Long workout with many movements
- **Stephen** - Complex round structure
- **Arnie** - Multiple movements and rounds
- **Adambrown** - Complex structure
- **Severin** - Multi-round format
- **Helton** - Complex movements
- **Thompson** - Multi-round structure
- **Bull** - Complex format
- **Holbrook** - Multiple rounds

### Workouts with Special Movement Requirements
- **War Frank** - May have unique movement specifications
- **McGhee** - Special format requirements
- **Nutts** - Complex movement structure
- **RJ** - Specific movement requirements
- **Luce** - Complex format
- **Johnson** - Multi-movement structure
- **Roy** - Special requirements
- **Coe** - Complex format
- **Jack** - Multi-round structure
- **Forrest** - Complex movements
- **Bulger** - Special format
- **Brenton** - Complex structure
- **Blake** - Multi-round format
- **Collin** - Complex movements
- **Whitten** - Special requirements
- **Rankel** - Complex format
- **Ledesma** - Multi-movement structure

### Simple Workouts (Now Completed)
- ✅ **Joshie** - 3 rounds with DB snatches and L pull-ups completed
- ✅ **Randy** - Single movement power snatches completed
- ✅ **Tommy V** - Thrusters and rope climbs completed  
- ✅ **Griff** - Runs and backwards runs completed
- ✅ **Erin** - 5 rounds with DB split cleans and pull-ups completed
- ✅ **Danny** - AMRAP with box jumps, push presses, pull-ups completed
- ✅ **Paul** - 5 rounds with double-unders, knees-to-elbows, overhead walk completed
- ✅ **Jerry** - Run-row-run format completed

### Already Created
- ✅ JT - 21-15-9 format completed
- ✅ Daniel - For time with runs and thrusters completed
- ✅ Josh - Overhead squats and pull-ups completed  
- ✅ Jason - Squats and muscle-ups completed
- ✅ DT - 5 rounds format completed
- ✅ Ryan - 5 rounds with muscle-ups and burpees completed  
- ✅ Michael - 3 rounds with run and bodyweight completed

### Existing Files (Already in system)
- ✅ Murph - Classic hero workout
- ✅ Garrett - Already exists
- ✅ Glen - Already exists  
- ✅ Chad - Already exists
- ✅ Nate - Already exists
- ✅ Rock - Already exists
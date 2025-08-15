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
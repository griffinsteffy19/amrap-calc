# AMRAP Calculator - Frontend/Backend Architecture

## Table of Contents
- [Current Architecture](#current-architecture)
- [Proposed Architecture](#proposed-architecture)
- [Directory Structure](#directory-structure)
- [Backend Design](#backend-design)
- [Database Design](#database-design)
- [Frontend Design](#frontend-design)
- [Data Flow](#data-flow)
- [Migration Strategy](#migration-strategy)
- [API Specifications](#api-specifications)
- [Benefits](#benefits)
- [Future Extensibility](#future-extensibility)
- [Implementation Timeline](#implementation-timeline)

## Current Architecture

### Overview
The AMRAP Calculator is currently implemented as a monolithic Streamlit application with some logical separation already in place:

```
src/
├── streamlit_app.py      # 700+ lines - UI logic mixed with business logic
├── calculations.py       # Mathematical calculations (well-separated)
├── movement_library.py   # Movement data access
└── workout_library.py    # Workout data access
```

### Current Issues
- **Tightly Coupled UI and Logic**: Business logic is embedded within Streamlit UI code
- **Testing Challenges**: Difficult to unit test business logic independently
- **Code Reuse Limitations**: Logic cannot be easily reused in other interfaces (CLI, API, etc.)
- **Maintenance Complexity**: UI changes can inadvertently affect business logic
- **File-Based Data Storage**: JSON files lack relationships, constraints, and query capabilities
- **Scalability Limitations**: No indexing or efficient searching across workouts/movements

## Proposed Architecture

### Architectural Principles
- **Separation of Concerns**: Clear boundaries between presentation, business logic, and data
- **Single Responsibility**: Each module has one clear purpose
- **Dependency Inversion**: High-level modules don't depend on low-level implementation details
- **API-First Design**: Backend functions as an internal API, easily extensible to REST

### High-Level Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │───▶│     Backend     │───▶│    Database     │
│   (Streamlit)   │    │ (Django/Services)│   │  (PostgreSQL)   │
│                 │    │                 │    │                 │
│ • Components    │    │ • API Layer     │    │ • Movements     │
│ • UI Logic      │    │ • Services      │    │ • Workouts      │
│ • State Mgmt    │    │ • Models        │    │ • Categories    │
│ • Validation    │    │ • Validation    │    │ • Users         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Evolution Path
The architecture supports a gradual migration from file-based storage to a full database:

**Phase 1**: JSON Files → Service Abstraction
**Phase 2**: Service Layer → Database Models  
**Phase 3**: Database Relations → Django Backend
**Phase 4**: REST API → Multiple Clients

## Directory Structure

### New Project Layout
```
amrap-calc/
├── backend/
│   ├── __init__.py
│   ├── api.py                    # Main backend interface
│   ├── models/
│   │   ├── __init__.py
│   │   ├── workout_models.py     # Workout, Movement data classes
│   │   ├── calculation_models.py # Request/Response models
│   │   └── validation.py         # Input validation
│   └── services/
│       ├── __init__.py
│       ├── workout_service.py    # Workout management
│       ├── movement_service.py   # Movement database operations
│       ├── calculation_service.py # Calculation logic wrapper
│       └── data_service.py       # Data access abstraction
├── frontend/
│   ├── __init__.py
│   ├── streamlit_app.py          # Main entry point (simplified)
│   ├── components/
│   │   ├── __init__.py
│   │   ├── workout_library_ui.py # Workout browsing interface
│   │   ├── movement_library_ui.py # Movement exploration
│   │   ├── manual_entry_ui.py    # Custom workout builder
│   │   └── results_display.py    # Results visualization
│   └── utils/
│       ├── __init__.py
│       ├── ui_helpers.py         # Common UI functions
│       └── state_management.py   # Session state helpers
├── src/                          # Legacy code (kept during migration)
└── data/                         # Unchanged JSON data
```

## Backend Design

### API Layer (`backend/api.py`)
Central interface providing all backend functionality:

```python
# Workout Operations
def get_workout_library() -> WorkoutLibrary
def get_workout_details(category: str, workout_id: str) -> Workout
def create_custom_workout(movements: List[Movement]) -> Workout

# Movement Operations  
def get_movement_categories() -> List[Category]
def get_movements_by_category(category: str) -> List[Movement]
def search_movements(query: str) -> List[Movement]

# Calculations
def calculate_amrap(request: AmrapRequest) -> AmrapResponse
def calculate_for_time(request: ForTimeRequest) -> ForTimeResponse

# Data Operations
def validate_workout(workout: Workout) -> ValidationResult
def process_movement_data(movements: List[Dict]) -> List[Movement]
```

### Service Layer
Each service handles specific business domains:

#### `WorkoutService`
- Workout CRUD operations
- Workout validation and processing
- Integration with data layer

#### `MovementService`
- Movement database operations
- Movement search and filtering
- Movement validation

#### `CalculationService` 
- Wraps existing `calculations.py`
- Adds validation and error handling
- Provides consistent interfaces

#### `DataService`
- File I/O operations
- Data caching
- Error handling for missing files

### Data Models
Type-safe data structures for all operations:

```python
@dataclass
class Movement:
    name: str
    description: str
    execution_time: float
    movement_type: MovementType
    count: int
    variety: Optional[str] = None

@dataclass
class Workout:
    name: str
    description: str
    movements: List[Movement]
    workout_type: WorkoutType
    total_time: int
    multiplier: float = 1.0

@dataclass
class AmrapRequest:
    movements: List[Movement]
    total_time: int
    multiplier: float = 1.0
```

## Database Design

### Database Schema Evolution

The current JSON-based data storage will be migrated to a relational database to support:
- **Data Integrity**: Foreign keys and constraints
- **Performance**: Indexes and query optimization
- **Relationships**: Proper connections between entities
- **Scalability**: Handle thousands of workouts and movements
- **User Data**: Personal workouts, history, and preferences

### Database Schema

#### Core Tables

```sql
-- Categories for organizing workouts and movements
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    key VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    icon VARCHAR(10) DEFAULT '📋',
    category_type VARCHAR(20) NOT NULL, -- 'workout' or 'movement'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Movement definitions
CREATE TABLE movements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL, -- URL-friendly version
    category_id INTEGER REFERENCES categories(id),
    description TEXT,
    movement_type VARCHAR(10) NOT NULL, -- 'S', 'D', 'T', 'M'
    base_execution_time FLOAT NOT NULL,
    scaling_notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Movement varieties (e.g., different weights, heights)
CREATE TABLE movement_varieties (
    id SERIAL PRIMARY KEY,
    movement_id INTEGER REFERENCES movements(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    execution_time FLOAT NOT NULL,
    scaling_notes TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Workout definitions
CREATE TABLE workouts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES categories(id),
    workout_type VARCHAR(20) NOT NULL DEFAULT 'amrap', -- 'amrap', 'for_time', 'emom'
    total_time INTEGER, -- in seconds, null for for_time workouts
    multiplier FLOAT DEFAULT 1.0,
    rounds INTEGER DEFAULT 1,
    time_cap INTEGER, -- in seconds, optional
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Many-to-many relationship between workouts and movements
CREATE TABLE workout_movements (
    id SERIAL PRIMARY KEY,
    workout_id INTEGER REFERENCES workouts(id) ON DELETE CASCADE,
    movement_id INTEGER REFERENCES movements(id),
    variety_id INTEGER REFERENCES movement_varieties(id) NULL,
    count INTEGER NOT NULL, -- -1 for max reps
    order_position INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### User and History Tables (Future Enhancement)

```sql
-- User accounts
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- User workout history
CREATE TABLE workout_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    workout_id INTEGER REFERENCES workouts(id),
    result_type VARCHAR(20) NOT NULL, -- 'amrap', 'for_time'
    total_reps INTEGER, -- for AMRAP workouts
    completion_time INTEGER, -- in seconds, for for_time workouts
    n_result FLOAT, -- calculated N value
    r_result INTEGER, -- additional reps
    max_reps INTEGER, -- max movement reps
    multiplier FLOAT,
    notes TEXT,
    completed_at TIMESTAMP DEFAULT NOW()
);

-- Custom user workouts
CREATE TABLE custom_workouts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    workout_type VARCHAR(20) NOT NULL,
    total_time INTEGER,
    multiplier FLOAT DEFAULT 1.0,
    rounds INTEGER DEFAULT 1,
    time_cap INTEGER,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Custom workout movements
CREATE TABLE custom_workout_movements (
    id SERIAL PRIMARY KEY,
    custom_workout_id INTEGER REFERENCES custom_workouts(id) ON DELETE CASCADE,
    movement_id INTEGER REFERENCES movements(id),
    variety_id INTEGER REFERENCES movement_varieties(id) NULL,
    count INTEGER NOT NULL,
    order_position INTEGER NOT NULL,
    notes TEXT
);
```

### Database Indexes

```sql
-- Performance indexes
CREATE INDEX idx_movements_category ON movements(category_id);
CREATE INDEX idx_movements_type ON movements(movement_type);
CREATE INDEX idx_movements_slug ON movements(slug);
CREATE INDEX idx_movements_active ON movements(is_active);

CREATE INDEX idx_workouts_category ON workouts(category_id);
CREATE INDEX idx_workouts_type ON workouts(workout_type);
CREATE INDEX idx_workouts_slug ON workouts(slug);
CREATE INDEX idx_workouts_active ON workouts(is_active);

CREATE INDEX idx_workout_movements_workout ON workout_movements(workout_id);
CREATE INDEX idx_workout_movements_order ON workout_movements(workout_id, order_position);

CREATE INDEX idx_movement_varieties_movement ON movement_varieties(movement_id);
CREATE INDEX idx_movement_varieties_default ON movement_varieties(movement_id, is_default);

-- Future user-related indexes
CREATE INDEX idx_workout_results_user ON workout_results(user_id);
CREATE INDEX idx_workout_results_workout ON workout_results(workout_id);
CREATE INDEX idx_workout_results_date ON workout_results(completed_at);
```

### Data Migration Strategy

#### Phase 1: Schema Creation
1. **Create Database Tables**: Set up the schema with proper constraints
2. **Add Seed Data**: Create basic categories from current JSON structure
3. **Data Validation**: Ensure all constraints and relationships work

#### Phase 2: JSON to Database Migration
```python
# Migration script structure
def migrate_categories():
    """Migrate workout and movement categories"""
    # Load from data/workouts/index.json and data/movements/index.json
    # Insert into categories table
    
def migrate_movements():
    """Migrate all movement definitions"""
    # Load from data/movements/**/*.json
    # Create movement records and varieties
    
def migrate_workouts():
    """Migrate all workout definitions"""  
    # Load from data/workouts/**/*.json
    # Create workout records and movement relationships

def validate_migration():
    """Ensure data integrity after migration"""
    # Verify all relationships exist
    # Check for missing data
    # Validate constraints
```

#### Phase 3: Django Model Integration
```python
# Django models that map to the database schema
class Category(models.Model):
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='📋')
    category_type = models.CharField(max_length=20)
    
class Movement(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=10)
    base_execution_time = models.FloatField()
    
class MovementVariety(models.Model):
    movement = models.ForeignKey(Movement, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    execution_time = models.FloatField()
    is_default = models.BooleanField(default=False)
```

### Database Benefits

#### Immediate Benefits
- **Data Integrity**: Foreign key constraints prevent orphaned records
- **Performance**: Indexed queries for fast searching and filtering
- **Relationships**: Proper connections between workouts, movements, and categories
- **Validation**: Database-level constraints ensure data quality

#### Long-term Benefits
- **User Management**: Personal accounts, workout history, and preferences
- **Advanced Queries**: Complex searches across multiple dimensions
- **Analytics**: Aggregate data for insights and trends
- **Scalability**: Handle thousands of users and workout records
- **Backup/Recovery**: Professional database management tools
- **Multi-tenancy**: Support multiple organizations or communities

## Frontend Design

### Component Architecture
Each UI section becomes a focused component:

#### `WorkoutLibraryUI`
- Workout browsing and selection
- Category navigation
- Random workout selection
- Live workout editing

#### `MovementLibraryUI`
- Movement exploration by category
- Movement search functionality
- Movement details display

#### `ManualEntryUI`
- Tab-based movement input
- Movement type selection
- Custom workout building

#### `ResultsDisplay`
- AMRAP results visualization
- For-Time predictions
- Calculation breakdowns

### State Management
Centralized session state management:

```python
class WorkoutState:
    def __init__(self):
        self.current_workout: Optional[Workout] = None
        self.selected_movements: List[Movement] = []
        self.calculation_results: Optional[Dict] = None
        
    def reset_workout(self) -> None
    def add_movement(self, movement: Movement) -> None
    def calculate_results(self) -> Dict
```

### UI Helpers
Common functionality across components:

```python
def format_time_display(seconds: int) -> str
def create_movement_selector(movements: List[Movement]) -> str
def display_error(message: str, error_type: str) -> None
def show_loading_spinner(message: str) -> None
```

## Data Flow

### Request Flow
```
User Input → Frontend Component → Backend API → Service Layer → Data Layer
                    ↓
Results Display ← Frontend Component ← API Response ← Service Layer ← Data Layer
```

### Example: AMRAP Calculation
1. **User Input**: Enters movements and time in UI
2. **Frontend**: Validates input, creates AmrapRequest
3. **API**: Routes request to CalculationService
4. **Service**: Processes request, calls calculation logic
5. **Response**: Returns structured AmrapResponse
6. **Frontend**: Displays results in ResultsDisplay component

## Migration Strategy

### Phase 1: Backend Foundation (Week 1-2)
- [ ] Create backend directory structure
- [ ] Define data models and validation
- [ ] Implement core API functions with file-based storage
- [ ] Wrap existing calculation logic
- [ ] Add comprehensive error handling
- [ ] Create database schema design
- [ ] Set up development database

### Phase 2: Database Migration (Week 3-4)
- [ ] Create database tables and indexes
- [ ] Write JSON-to-database migration scripts
- [ ] Migrate categories, movements, and workouts
- [ ] Validate data integrity and relationships
- [ ] Update service layer to use database
- [ ] Add Django models and admin interface
- [ ] Implement database-backed API endpoints

### Phase 3: Service Layer Enhancement (Week 5-6)
- [ ] Extract workout management logic
- [ ] Create movement service operations
- [ ] Implement advanced database queries
- [ ] Add search and filtering capabilities
- [ ] Create comprehensive unit tests
- [ ] Add performance monitoring and caching

### Phase 4: Frontend Refactoring (Week 7-8)
- [ ] Create component structure
- [ ] Extract UI components from monolithic app
- [ ] Implement state management system
- [ ] Replace direct calls with API calls
- [ ] Add proper error handling and loading states
- [ ] Implement real-time search and filtering

### Phase 5: Integration and Polish (Week 9-10)
- [ ] End-to-end integration testing
- [ ] Performance optimization and caching
- [ ] User authentication and personalization
- [ ] Documentation updates
- [ ] Legacy code removal
- [ ] Production deployment preparation

## API Specifications

### Workout Management

#### `get_workout_library()`
```python
Returns: WorkoutLibrary
{
    "categories": {
        "girl": {
            "name": "Girl Workouts",
            "description": "Classic CrossFit benchmarks",
            "workouts": {...}
        }
    }
}
```

#### `calculate_amrap(request: AmrapRequest)`
```python
Request: {
    "movements": [Movement],
    "total_time": int,
    "multiplier": float
}

Response: {
    "n_result": float,
    "n_floor": int, 
    "r_result": int,
    "total_reps": int,
    "verification": float,
    "error": Optional[str]
}
```

### Error Handling
Consistent error responses across all API functions:

```python
@dataclass
class ApiError:
    error_type: str
    message: str
    details: Optional[Dict] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
```

## Benefits

### Immediate Benefits
- **Cleaner Code**: Clear separation reduces cognitive load
- **Better Testing**: Business logic can be unit tested independently
- **Reduced Bugs**: Type safety and validation prevent runtime errors
- **Easier Maintenance**: Changes to UI don't affect business logic

### Long-term Benefits
- **Multiple Frontends**: Same backend can support CLI, web API, mobile app
- **Team Development**: Frontend and backend can be developed independently
- **Performance**: Caching and optimization can be added to service layer
- **Scalability**: Easy to add new features without affecting existing code

## Future Extensibility

### REST API Conversion
The backend API can be easily converted to REST endpoints:

```python
# Current internal API
result = calculate_amrap(AmrapRequest(...))

# Future REST API  
POST /api/v1/calculate/amrap
{
    "movements": [...],
    "total_time": 1200,
    "multiplier": 1.0
}
```

### Additional Interfaces
- **CLI Tool**: Command-line interface using same backend
- **Mobile App**: React Native app calling REST API
- **Webhook Integration**: External systems can trigger calculations
- **Batch Processing**: Process multiple workouts simultaneously

### Enhanced Features
- **User Accounts**: Personal workout history and preferences
- **Workout Templates**: Save and share custom workouts
- **Performance Tracking**: Historical performance analysis
- **Social Features**: Community workout sharing

## Implementation Timeline

### Week 1-2: Backend Foundation
- **Week 1, Days 1-3**: Directory structure, models, and validation
- **Week 1, Days 4-5**: Core API functions with file-based storage
- **Week 1, Days 6-7**: Error handling and logging
- **Week 2, Days 1-3**: Database schema design and setup
- **Week 2, Days 4-5**: Migration script development
- **Week 2, Days 6-7**: Basic service layer implementation

### Week 3-4: Database Migration
- **Week 3, Days 1-2**: Database table creation and constraints
- **Week 3, Days 3-4**: JSON-to-database migration execution
- **Week 3, Days 5-7**: Data validation and integrity checks
- **Week 4, Days 1-3**: Django model implementation
- **Week 4, Days 4-5**: Database-backed API endpoints
- **Week 4, Days 6-7**: Admin interface setup

### Week 5-6: Service Layer Enhancement
- **Week 5, Days 1-3**: Advanced database queries and operations
- **Week 5, Days 4-7**: Search, filtering, and performance optimization
- **Week 6, Days 1-3**: Comprehensive unit testing
- **Week 6, Days 4-7**: Caching and monitoring implementation

### Week 7-8: Frontend Refactoring
- **Week 7, Days 1-3**: Component structure and state management
- **Week 7, Days 4-7**: UI component extraction and modularization
- **Week 8, Days 1-3**: API integration and error handling
- **Week 8, Days 4-7**: Real-time features and UI polish

### Week 9-10: Integration and Production
- **Week 9, Days 1-3**: End-to-end integration testing
- **Week 9, Days 4-7**: Performance optimization and bug fixes
- **Week 10, Days 1-3**: Documentation and deployment prep
- **Week 10, Days 4-7**: Legacy cleanup and final validation

## Success Metrics

### Technical Metrics
- **Code Coverage**: >90% test coverage for backend services
- **Performance**: API response times <100ms for calculations
- **Error Rate**: <1% error rate in production usage
- **Maintainability**: Cyclomatic complexity <10 for all functions

### User Experience Metrics
- **Load Time**: Frontend loads in <2 seconds
- **Responsiveness**: UI interactions respond in <200ms
- **Reliability**: Zero crashes during normal operation
- **Feature Parity**: All existing functionality preserved

## Database Migration Summary

### Current JSON Structure → Database Tables

| Current JSON Files | Database Tables | Key Benefits |
|-------------------|-----------------|--------------|
| `data/workouts/index.json` | `categories` | Organized categories for both workouts and movements |
| `data/workouts/**/*.json` | `workouts` + `workout_movements` | Normalized workout definitions with proper relationships |
| `data/movements/index.json` | `categories` | Shared category system |
| `data/movements/**/*.json` | `movements` + `movement_varieties` | Flexible movement definitions with scaling options |

### Migration Validation Checklist

- [ ] **Data Completeness**: All JSON records successfully migrated
- [ ] **Relationship Integrity**: Foreign keys properly established
- [ ] **Performance Benchmarks**: Database queries faster than file operations
- [ ] **API Compatibility**: All existing API functions work with database backend
- [ ] **Admin Interface**: Django admin can manage all data effectively
- [ ] **Backup Strategy**: Database backup and recovery procedures tested

### Post-Migration Capabilities

1. **Advanced Queries**: Search workouts by movement type, time range, difficulty
2. **Data Relationships**: Find all workouts containing specific movements
3. **User Personalization**: Save workout history and preferences
4. **Analytics**: Aggregate workout statistics and trends
5. **Content Management**: Easy addition of new movements and workouts via admin
6. **API Performance**: Sub-100ms response times for all operations

This architecture provides a solid foundation for the AMRAP Calculator's future growth while maintaining all existing functionality and improving code quality significantly. The database migration transforms the application from a simple file-based tool into a scalable, professional fitness platform.
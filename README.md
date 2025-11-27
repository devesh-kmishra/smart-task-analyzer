# Smart Task Analyzer

This is a Django application that intelligently scores and prioritizes tasks based on multiple factors.

## Setup Instructions

**Prerequisites**

- Python 3.8 or higher
- pip (Python package manager)

1. **Clone the repository**

```
git clone https://github.com/devesh-kmishra/smart-task-analyzer.git
cd smart-task-analyzer
```

2. **Create and activate virtual environment**

```
# Windows
cd backend
python -m venv venv
venv\Scripts\activate

# Mac/Linux
cd backend
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```
pip install -r requirements.txt
```

4. **Set up environment variables**
   Create a `.env` file in the `backend` folder:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. **Run migrations**

```
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser (optional, for admin access)**

```
python manage.py createsuperuser
```

7. **Run the development server**

```
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000`

**Running Tests**

```
# Run all tests
python manage.py test

# Run with detailed output
python manage.py test --verbosity=2

# Run specific test class
python manage.py test tasks.tests.TaskScorerTestCase
```

## Algorithm Explanation

**Overview**  
The Smart Task Analyzer uses a weighted multi-factor scoring system to calculate a priority score (0-100) for each task. This approach balances multiple competing priorities rather than relying on a single metric, providing a more holistic view of task importance.

**Core Components**  
The algorithm evaluates four key factors, each contributing a weighted percentage to the final score:

1. **Urgency (35% weight)**  
   Urgency is calculated based on the task's due date relative to today. The scoring uses an exponential decay model where:

   - Overdue tasks receive the maximum urgency score (100)
   - Tasks due today score 95
   - Tasks due within a week decrease linearly (90 → 20)
   - Far-future tasks (30+ days) have minimal urgency

   This ensures that time-sensitive tasks receive appropriate attention while preventing distant deadlines from being ignored entirely.

2. **Importance (30% weight)**  
   User-defined importance ratings (1-10 scale) are directly converted to a 0-100 scale. This allows users to explicitly indicate which tasks align with their strategic goals, regardless of urgency. A task with importance 10 contributes 100 points to this factor, while importance 1 contributes only 10 points.

3. **Effort (20% weight)**  
   The effort score implements a "quick wins" philosophy by giving higher scores to tasks requiring less time. Tasks under 1 hour score 90, making them attractive targets for momentum-building. Medium-effort tasks (1-4 hours) score progressively lower, while long tasks (10+ hours) receive minimal effort scores. This encourages users to clear smaller tasks quickly while still accounting for necessary large projects.

4. **Dependencies (15% weight)**  
   Tasks that block other work receive priority boosts. The algorithm counts how many other tasks depend on the current task's completion:

   - Blocking 0 tasks: 0 points
   - Blocking 1 task: 30 points
   - Blocking 2 tasks: 60 points
   - Blocking 3+ tasks: 100 points

   This prevents bottlenecks by surfacing critical path tasks.

**Final Calculation**  
The final priority score is computed as:

```
Priority Score = (Urgency × 0.35) + (Importance × 0.30) + (Effort × 0.20) + (Dependencies × 0.15)
```

This weighted approach ensures that no single factor dominates the decision, while urgency and importance receive slightly more weight as they typically matter most in real-world scenarios.

**Alternative Strategies**  
Users can switch to alternative strategies that emphasize different factors:

- **Fastest Wins**: Sorts purely by estimated hours
- **High Impact**: Prioritizes importance ratings above all else
- **Deadline Driven**: Uses only the urgency calculation

These alternatives provide flexibility for different work contexts (e.g., "clearing the deck" days vs. strategic planning sessions).

## Design Decisions

1. **Default Weight Distribution (35/30/20/15)**

   **Decision**: Urgency and importance get the highest weights, with effort and dependencies as secondary factors.
   **Trade-off**: Opinionated defaults vs. universal applicability.
   **Rationale**: Based on common productivity principles (Eisenhower Matrix, GTD methodology), urgency and importance typically drive decisions most. However, user preferences model support has been included for future customization, recognizing that different users or contexts might need different weights.

2. **CSRF Exemption for API**

   **Decision**: Disable CSRF protection for API endpoints during development.
   **Trade-off**: Reduced security vs. development convenience.
   **Rationale**: For a local development project without authentication, the security risk is minimal. Production deployment would require proper CSRF token handling or session-based authentication.

## Time Breakdown

**Total Time**: Approximately 15-17 hours

- **Backend Development** (6-7 hours)
- **Frontend Development** (4-5 hours)
- **Bonus Features** (2-3 hours)
- **Testing and Documentation** (1-2 hours)

## Bonus Challenges

1. **Dependency Graph Visualization**

- Shows all tasks and their dependency relationships
- Highlights tasks involved in circular dependencies in red
- Displays warning alert when cycles are detected
- Uses graph traversal algorithm (DFS) to detect cycles
- Color-coded legend for normal vs. circular dependencies

2. **Eisenhower Matrix View**

   **Do First** (Urgent + Important): Red quadrant for critical tasks  
   **Schedule** (Not Urgent + Important): Blue quadrant for strategic work  
   **Delegate** (Urgent + Not Important): Yellow quadrant for tasks to potentially delegate  
   **Eliminate** (Neither): Green quadrant for low-value tasks

## Future Improvements

1. User Authentication & Multi-User Support
2. Task Editing & Management
3. Task Categories & Tags
4. Export tasks to CSV, JSON, or PDF

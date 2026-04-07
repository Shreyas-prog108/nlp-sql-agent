# 🗃️ NL2SQL Agent

An AI-powered Natural Language to SQL agent that converts plain English questions into SQL queries, executes them against a real database, and returns clean results.

## Tech Stack

- **Language**: Python 3.11+
- **LLM**: OpenAI gpt-5.4-nano
- **Database**: SQLite
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Libraries**: openai, python-dotenv, tabulate, pandas

## Features

- ✅ Natural language → SQL conversion
- ✅ Query execution with results in table format
- ✅ Plain English explanation of generated SQL
- ✅ Follow-up question suggestions
- ✅ Multi-turn conversation context
- ✅ Destructive query guardrails (blocks DROP, DELETE, UPDATE, etc.)
- ✅ Error handling with friendly messages
- ✅ Query execution time & row count
- ✅ REST API + Streamlit chat UI

## Database Schema

```
departments(id, name, location)
employees(id, name, department_id, salary, hire_date)
projects(id, name, employee_id, status, deadline)
```

- 5 departments, 20 employees, 20 projects
- Foreign key relationships between all tables
- Project statuses: `active`, `completed`, `overdue`

## Setup

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd nl2sql-agent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# 5. Seed the database
python run.py --seed
```

## Running

### Seed the database (first time or reset)
```bash
python run.py --seed
```

### Option A — Streamlit UI (Recommended for demo)
```bash
python run.py --ui
```
Opens a chat interface at `http://localhost:8501`

### Option B — FastAPI REST API
```bash
python run.py
```
API available at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`

#### API Usage
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many employees are in Engineering?"}'
```

## Example Questions & Outputs

### 1. "How many employees are in the Engineering department?"
```sql
SELECT COUNT(*) AS employee_count
FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE d.name = 'Engineering';
```
| employee_count |
|---|
| 4 |

### 2. "List all projects that are overdue."
```sql
SELECT p.name, e.name AS assigned_to, p.deadline
FROM projects p
JOIN employees e ON p.employee_id = e.id
WHERE p.status = 'overdue';
```

### 3. "Which department has the highest average salary?"
```sql
SELECT d.name, ROUND(AVG(e.salary), 2) AS avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.name
ORDER BY avg_salary DESC
LIMIT 1;
```

### 4. "Show employees hired after January 2023."
```sql
SELECT name, hire_date, salary
FROM employees
WHERE hire_date > '2023-01-01'
ORDER BY hire_date;
```

### Error Handling Example
**Input**: "Delete all employees"
**Output**: `🚫 Blocked: query contains destructive keyword 'DELETE'. Only SELECT queries are allowed.`

## Project Structure

```
nl2sql-agent/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI endpoints
│   ├── agent.py             # Core LLM agent logic
│   ├── database.py          # DB connection & execution
│   ├── guardrails.py        # Destructive query blocker
│   └── schema.py            # Schema context for LLM
├── ui/
│   └── streamlit_app.py     # Streamlit chat interface
├── db/
│   ├── setup.py             # Schema + seed script
│   └── company.db           # SQLite database (generated)
├── .env.example
├── requirements.txt
├── run.py                   # Entry point
└── README.md
```

## License

MIT
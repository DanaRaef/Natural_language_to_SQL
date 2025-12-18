# Natural Language to SQL with Visualization 🧠➡️📊

**Streamlit app that converts natural language questions into Azure SQL SELECT queries and visualizes the results.**

---

## Features ✅

- Translate natural language to *read-only* Azure SQL (SELECT) using an LLM
- Automatic validation and safety checks for SQL queries
- Auto-fix SQL errors by analyzing database schema and error messages
- Automatic chart selection driven by the LLM (line, bar, pie, scatter, KPI)
- Interactive Streamlit UI with database connect/disconnect and code preview

---

## Prerequisites 🔧

- Python 3.9+ (recommended)
- System Driver: Microsoft ODBC Driver 18 for SQL Server (install via Microsoft docs)
- An Azure SQL instance with network access from the machine running the app
- Local IP must be whitelisted in the Azure SQL Firewall settings.
- API keys for LLMs (OpenAI, Mistral)

---

## Environment variables / .env 📂

Create a `.env` file in the project root with the following variables:

```
USERNAME=<db_username>
PASSWORD=<db_password>
MISTRAL_API_KEY=<mistral_api_key>
OPENAI_API_KEY=<openai_api_key>
```

Notes:
- `USERNAME` and `PASSWORD` are used to connect to your Azure SQL DB.
- LLM keys are required to use the corresponding LLM models in the UI.

---

## Install & Run 🚀

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run streamlit_final.py
```

Open the URL printed by Streamlit (usually http://localhost:8501).

---

## How to use 🧭

- Use the **Database** sidebar to connect to your Azure SQL instance.
- Enter a natural language question into the text area and click **Run Query**.
- The app validates the request (ensures SELECT-only queries) and displays the results and the generated SQL.
- The app will choose an appropriate chart; if no suitable chart exists, it will show a helpful message.

---


## Development notes 🔧

- Main file: `streamlit_final.py`.
- Key components:
  - `validate_chain` ensures only read-only SELECT queries and returns JSON `{ status, reason, query }`.
  - `fix_sql_chain` attempts to repair SQL errors using the DB schema and error message.
  - `chart_xy_chain` recommends chart type and axes using a dataframe summary and a pydantic parser.
- Session state keys used: `engine`, `db`, `last_sql`, `model_name`.

---

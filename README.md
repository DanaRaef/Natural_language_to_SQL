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

- Python 3.10+ (recommended)
- macOS: Microsoft ODBC Driver 18 for SQL Server (install via Microsoft docs)
- An Azure SQL instance with network access from the machine running the app
- API keys for one or both LLMs (OpenAI, Mistral)

---

## Environment variables / .env 📂

Create a `.env` file in the project root with the following variables (do NOT commit secrets):

```
USERNAME=<db_username>
PASSWORD=<db_password>
MISTRAL_API_KEY=<optional_mistral_api_key>
OPENAI_API_KEY=<optional_openai_api_key>
```

Notes:
- `USERNAME` and `PASSWORD` are used to connect to your Azure SQL DB.
- LLM keys are required to use the corresponding model in the UI.

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

## Troubleshooting ⚠️

- Database connection errors:
  - Verify `USERNAME` and `PASSWORD` in `.env`.
  - Ensure the ODBC Driver is installed and network/firewall settings allow connectivity.
- LLM/API errors: ensure `OPENAI_API_KEY` or `MISTRAL_API_KEY` are set and valid.
- No results returned: the query might be valid but return zero rows—check the SQL shown in the app.

> Tip: Exception details are shown in the Streamlit UI to help debug connection and execution issues.

---

## Development notes 🔧

- Main file: `streamlit_final.py`.
- Key components:
  - `validate_chain` ensures only read-only SELECT queries and returns JSON `{ status, reason, query }`.
  - `fix_sql_chain` attempts to repair SQL errors using the DB schema and error message.
  - `chart_xy_chain` recommends chart type and axes using a dataframe summary and a pydantic parser.
- Session state keys used: `engine`, `db`, `last_sql`, `model_name`.

---

## Security & Privacy 🔐

- Do not commit `.env` or any secrets to version control.
- The app sends queries and schema metadata to LLM providers as part of the reasoning and validation—review provider policies if working with sensitive data.

---

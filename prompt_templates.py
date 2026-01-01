from langchain.prompts import ChatPromptTemplate

fix_sql_prompt = ChatPromptTemplate.from_template("""
The following T-SQL query has an error. Carefully analyze the query and fix it based on the error message.
Return ONLY the corrected T-SQL query without any explanations.
Error message:
{error}

Schema: 
{table_info}

T-SQL query:
"""
)

validate_sql_prompt = ChatPromptTemplate.from_template("""
You are an expert Azure T-SQL developer.

Decide if the user request is VALID or INVALID.

Rules:
- VALID only if:
  - READ-ONLY (SELECT only)
  - Supported by the provided schema
  - Its main goal is not to expose raw data, but to provide insights or aggregated information.
                                                    
- INVALID if:
  - INSERT, UPDATE, DELETE, DROP, ALTER
  - Any data modification
  - Unsupported schema usage

If VALID:
- Generate ONE Azure T-SQL SELECT query.
- Ensure correct syntax and schema usage.
- Select relevant columns only (eg. What is the count of churn reasons per churn month -> Retrieve only the churn_reasons_count and churn_month columns).
- use date columns only for dates.
- Review fact table carefully, If all data is in fact table,DO NOT join dimension tables.
- If fact table has its own date column, prefer it over joining dimension tables for date filtering.(eg. use 'paid_date' instead of joining 'date_dim' table).
- Optimize for performance.
                                                    

If INVALID:
- query must be null.

OUTPUT RULES (STRICT):
- Output ONLY valid JSON.
- No text before or after JSON.
- No explanations.
- No markdown.

Guidance:
- Try to map user terms to schema terms. (eg. "sales" -> "revenue", "customers" -> "subscribers")                                                                                                              
                                                       
JSON FORMAT:
{{
  "status": "VALID or INVALID",
  "reason": "Brief reason for validity or invalidity",
  "query": "T-SQL query or null"
}}

User request:
{question}

Database schema:
{table_info}

JSON Response:
""")

chart_xy_prompt = ChatPromptTemplate.from_template("""
You are a Data Visualization AI. Your goal is to map a dataset summary to the best possible chart configuration.

### INPUT DATA SUMMARY:
{df_summary}

### SELECTION LOGIC (Follow these steps in order):

1. IDENTIFY COLUMN TYPES:
   - Identify which columns are DATETIME, CATEGORICAL (object/string), or NUMERIC (int/float).

2. CHOOSE CHART TYPE:
   - IF (X is DATETIME) AND (Y is NUMERIC) -> "line"
   - IF (X is CATEGORICAL) AND (Y is NUMERIC) -> "bar" 
   - IF (X is NUMERIC) AND (Y is NUMERIC) -> "scatter"
   - IF (ONLY 1 column exists AND it is NUMERIC) OR (All values are a single aggregate) -> "kpi"
   - IF (Only CATEGORICAL column(s) exist) AND (No NUMERIC columns) -> "None"
   - IF (X is CATEGORICAL) AND (Dataset represents parts of a whole) -> "pie" 
   - IF (NO NUMERIC columns exist) -> "None"

3. ASSIGN AXES:
   - X: A single string (the column name).
   - Y: A LIST of strings (the numeric column names).

### CONSTRAINTS:
- You MUST return "bar" if there is one categorical column (like 'churn_reason') and one numeric column (like 'count').
- Use ONLY the exact column names provided in the summary.
- Output MUST be a single, valid JSON object.
- NO markdown (```json), NO whitespace before/after JSON, NO commentary.

### REQUIRED JSON FORMAT:
{{
  "chart_type": "line", "bar", "pie", "scatter", "kpi", or "None",
  "x": "column_name_string",
  "y": ["column_name_string"]
}}

JSON OUTPUT:
""")

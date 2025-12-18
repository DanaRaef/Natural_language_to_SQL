from langchain.prompts import ChatPromptTemplate

fix_sql_prompt = ChatPromptTemplate.from_template("""
The following SQL query has an error. Carefully analyze the query and fix it based on the error message.
Return ONLY the corrected SQL query without any explanations.
Error message:
{error}

Schema: 
{table_info}

SQL query:
"""
)

validate_sql_prompt = ChatPromptTemplate.from_template("""
You are an expert Azure SQL developer.

Decide if the user request is VALID or INVALID.

Rules:
- VALID only if:
  - READ-ONLY (SELECT only)
  - Supported by the provided schema
                                                    
- INVALID if:
  - INSERT, UPDATE, DELETE, DROP, ALTER
  - Any data modification
  - Unsupported schema usage

If VALID:
- Generate ONE Azure SQL SELECT query.

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
  "query": "SQL query or null"
}}

User request:
{question}

Database schema:
{table_info}

JSON Response:
""")

chart_xy_prompt = ChatPromptTemplate.from_template("""
You are a data visualization expert.

Your task:
Choose the BEST chart type AND the appropriate X and Y columns for the given dataframe.

Rules (STRICT):
- Choose chart_type ONLY from: line, bar, pie, scatter, kpi ,None
- Use ONLY column names that exist in the dataframe
- X must be a single column or null
- Y must be a list of column names or null

Chart selection guidance (STRICT):
- Time series → line chart: X must be DATETIME, Y must be NUMERIC
- Categorical comparison → bar chart: X CATEGORICAL, Y NUMERIC
- Pie chart → CATEGORICAL on X, NUMERIC on Y
- Scatter → NUMERIC X and NUMERIC Y
- KPI → single NUMERIC value, Y must contain exactly ONE NUMERIC column, X must be null
- If no suitable chart can be created, choose chart_type as None, and set X and Y to null

Additional rules:
- If multiple numeric columns exist for bar/pie/scatter, pick the most meaningful or the first one
- If one categorical column only exists and no numeric column, choose chart_type as None
- Output ONLY valid JSON, no explanations, no markdown, no extra text
                                                   

JSON FORMAT:
{{
  "chart_type": "line, bar, pie, scatter, kpi, None",
  "x": "X column name or null",
  "y": "Y column name(s) or null"
}}

Dataset summary:
{df_summary}

JSON output:
""")
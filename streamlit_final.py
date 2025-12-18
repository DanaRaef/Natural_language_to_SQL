import streamlit as st
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
from langchain.chat_models import init_chat_model
from langchain_mistralai import ChatMistralAI
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import List, Optional, Literal
import urllib
from prompt_templates import *

# ------------------- Load Environment -------------------
load_dotenv()

# ------------------- Database Setup -------------------
server = "myserverbbi.database.windows.net"
database = "telecom_bbi"
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

driver = "{ODBC Driver 18 for SQL Server}"

params = urllib.parse.quote_plus(
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=60;" 
    "ConnectRetryCount=3;"   
    "ConnectRetryInterval=10;"
)

conn_str = f"mssql+pyodbc:///?odbc_connect={params}"



# ------------------- LLM Initialization -------------------
mistral_llm = ChatMistralAI(
    model="mistral-large-2512",
    temperature=0,
    mistral_api_key=os.environ.get("MISTRAL_API_KEY"),
)

openai_llm = init_chat_model(
    model="gpt-4.1-mini",
    temperature=0,
    openai_api_key=os.environ["OPENAI_API_KEY"],
)

# ------------------- Pydantic Output Parsers -------------------
class ValidationOutput(BaseModel):
    status: str
    reason: str
    query: Optional[str] 

validation_parser = PydanticOutputParser(pydantic_object=ValidationOutput)

class ChartDecision(BaseModel):
    chart_type: Literal["line", "bar", "pie", "scatter", "kpi", "None"]
    x: Optional[str]
    y: Optional[List[str]]

chart_parser = PydanticOutputParser(pydantic_object=ChartDecision)


# ------------------- Chains -------------------
def define_chains(llm)-> tuple:
    fix_sql_chain = fix_sql_prompt | llm | StrOutputParser()
    validate_chain = validate_sql_prompt | llm | validation_parser
    chart_xy_chain = chart_xy_prompt | llm | chart_parser
    return fix_sql_chain, validate_chain, chart_xy_chain

# ------------------- Helper Functions -------------------
def init_db():
    try:
        engine = create_engine(conn_str, pool_pre_ping=True,connect_args={'timeout': 30})
        db = SQLDatabase.from_uri(conn_str)
        return engine, db
    except Exception as e:
        st.error("❌ Database connection failed")
        st.exception(e)
        return None, None

def fix_sql(error: str, table_info: str, fix_sql_chain) -> str:
    raw_sql = fix_sql_chain.invoke({"table_info": table_info, "error": error})
    return raw_sql.replace("```sql", "").replace("```", "").strip()


def execute_query(sql: str, retries: int = 3) -> Optional[pd.DataFrame]:
    engine = st.session_state.engine
    db = st.session_state.db

    for _ in range(retries):
        try:
            return pd.read_sql(sql, engine)
        except Exception as e:
            st.warning(f"SQL execution error: {e}. Attempting fix...")
            sql =  fix_sql(str(e), db.get_table_info(), fix_sql_chain)
    return None

def summarize_dataframe(df: pd.DataFrame, max_rows: int = 5) -> dict:
    return {
        "row_count": len(df),
        "columns": [
            {
                "name": col,
                "dtype": str(df[col].dtype),
                "cardinality": int(df[col].nunique()),
                "sample_values": df[col].dropna().unique()[:3].tolist()
            }
            for col in df.columns
        ]
    }

def llm_choose_chart_and_axes(df: pd.DataFrame) -> ChartDecision:
    summary = summarize_dataframe(df)
    decision: ChartDecision = chart_xy_chain.invoke({"df_summary": summary})
    print(decision)
    return decision

def render_chart(df: pd.DataFrame, decision: ChartDecision):
    if decision.chart_type == "line":
        fig = px.line(df, x=decision.x, y=decision.y)
        st.plotly_chart(fig)
    elif decision.chart_type == "bar":
        fig = px.bar(df, x=decision.x, y=decision.y)
        st.plotly_chart(fig)
    elif decision.chart_type == "pie":
        fig = px.pie(df, names=decision.x, values=decision.y[0])
        st.plotly_chart(fig)
    elif decision.chart_type == "scatter":
        fig = px.scatter(df, x=decision.x, y=decision.y[0])
        st.plotly_chart(fig)
    elif decision.chart_type == "kpi":
        # Show numeric summary
        metric_col = decision.y[0]
        value = df[metric_col].sum() if len(df) > 1 else df[metric_col].iloc[0]
        st.metric(label=metric_col, value=round(value,2))
    else:
        st.error("No suitable chart could be generated, Please use dataframe preview below.")

def run_pipeline(question: str) -> Optional[pd.DataFrame]:
    db = st.session_state.db

    table_info = db.get_table_info()
    validation = validate_chain.invoke({"table_info": table_info, "question": question})

    if validation.status != "VALID":
        st.error(validation.reason)
        return None

    sql_query = validation.query
    df = execute_query(validation.query)
    if df is None or df.empty:
        st.warning("No results returned.")
        return None
    decision = llm_choose_chart_and_axes(df)
    render_chart(df, decision)
    return sql_query , df


####################################################
# ------------------- Session State Init -------------------
if "engine" not in st.session_state:
    st.session_state.engine = None
    st.session_state.db = None
    st.session_state.last_sql = None


    # ------------------- Database Connection UI -------------------
st.sidebar.header("Database")

if st.session_state.db is None:
    if st.sidebar.button("Connect to Database"):
        engine, db = init_db()
        if engine and db:
            st.session_state.engine = engine
            st.session_state.db = db
            st.sidebar.success("🟢 Connected")
            st.rerun()
else:
    st.sidebar.success("🟢 Connected")
    if st.sidebar.button("Disconnect"):
        st.session_state.engine = None
        st.session_state.db = None
        st.sidebar.info("Disconnected")
        st.rerun()


if st.session_state.db is None:
    st.info("Please connect to the database to continue.")
    st.stop()
    # ------------------- Model Selection UI -------------------
st.sidebar.header("Settings")

# Initialize selected model in session_state if not present
if "model_name" not in st.session_state:
    st.session_state.model_name = "mistral-large-2512"  # default

# Model selection dropdown
st.session_state.model_name = st.sidebar.selectbox(
    "Select LLM model",
    options=["mistral-large-2512", "gpt-4.1-mini"],
    index=0
)
if st.session_state.model_name == "mistral-large-2512":
    llm = mistral_llm
else:
    llm = openai_llm
fix_sql_chain, validate_chain, chart_xy_chain = define_chains(llm)

    # ------------------- Process User Request -------------------
st.title("Natural Language to SQL with Visualization")

user_question = st.text_area("Enter your question:", height=100)

run_clicked = st.button("Run Query")

if run_clicked:
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Processing your request..."):
            result = run_pipeline(user_question)

        if result:
            sql_query, df_result = result

            st.session_state.last_sql = sql_query

            st.subheader("Query Results")
            st.dataframe(df_result)

            st.subheader("Generated SQL Query")
            st.code(sql_query, language="sql")

            

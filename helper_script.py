import tiktoken
from natural_lang_to_sql import init_db, mistral_llm, openai_llm
from prompt_templates import validate_sql_prompt
import time
import pandas as pd


def count_tokens(text: str, model: str = "gpt-4.1-mini") -> int: #calculate number of tokens in a text
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def estimate_tokens_cost(token_count: int, cost_per_1k_tokens: float = 0.0004) -> float: # estimate cost based on token count
    cost = (token_count / 1000) * cost_per_1k_tokens
    return cost

def measure_latency(llm, prompt: str) -> float: # calculate latency of LLM response
    start_time = time.time()
    llm_output = llm.invoke(prompt)
    end_time = time.time()
    return end_time - start_time, llm_output

def get_minified_schema(engine) -> str: 
    query = """
    SELECT 
        t.TABLE_NAME, 
        c.COLUMN_NAME, 
        c.DATA_TYPE
    FROM INFORMATION_SCHEMA.TABLES t
    JOIN INFORMATION_SCHEMA.COLUMNS c ON t.TABLE_NAME = c.TABLE_NAME
    WHERE t.TABLE_TYPE = 'BASE TABLE'
    AND t.TABLE_SCHEMA = 'dbo' -- or your specific schema
    ORDER BY t.TABLE_NAME;
    """
    df = pd.read_sql(query, engine)
    
    schema_parts = []
    # Group by table to create the "Table(col1, col2)" format
    for table_name, group in df.groupby('TABLE_NAME'):
        columns = ", ".join([f"{row['COLUMN_NAME']} ({row['DATA_TYPE']})" for _, row in group.iterrows()])
        schema_parts.append(f"{table_name}: {columns}")
    
    return "\n".join(schema_parts)

# intialize the DB connection 
engine, db = init_db()



if db: 
    # schema = db.get_table_info()
    schema = get_minified_schema(engine)
    token_count = count_tokens(schema)
    print(f"Schema tokens: {token_count}")

    cost_estimate = estimate_tokens_cost(token_count)
    print(f"Estimated cost for schema tokens: ${cost_estimate:.6f}")

#calculate OpenAI and Mistral latency 
sample_prompt = validate_sql_prompt.format_prompt(
    question="What is the total revenue per month for the latest year in the DB?",
    table_info=schema
).to_string()

# openai_latency = measure_latency(openai_llm, sample_prompt)
mistral_latency , llm_output = measure_latency(mistral_llm, sample_prompt)  
print(llm_output)
n_tokens = llm_output.response_metadata["token_usage"]["total_tokens"]
print(n_tokens)
cost = estimate_tokens_cost(n_tokens)

# # # print(f"OpenAI LLM Latency: {openai_latency:.2f} seconds for {n_tokens} tokens and estimated cost ${cost:.6f}")
print(f"Mistral LLM Latency: {mistral_latency:.2f} seconds for {n_tokens} tokens and estimated cost ${cost:.6f} , input tokens: {llm_output.response_metadata['token_usage']['prompt_tokens']}, output tokens: {llm_output.response_metadata['token_usage']['completion_tokens']}")

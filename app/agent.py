import os
from datetime import date
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from app.guardrails import check_sqlquery, check_user_intent
from app.db import execute_query

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "instance", "database.db")
DB_URI = f"sqlite:///{DB_PATH}"


db=SQLDatabase.from_uri(DB_URI)

llm=ChatOpenAI(
    model=os.getenv("OPENAI_MODEL","gpt-5.4-nano"),
    temperature=0.0,
    api_key=os.getenv("OPENAI_API_KEY"),
)

# SQL Generation Prompt
sql_prompt=ChatPromptTemplate.from_messages([
    ("system",
    """You are a SQLite expert. Given a user question, generate a syntactically correct SQLite SELECT query.
    Only return the raw SQL query, nothing else. No markdown, no explanation, no backticks.
 
    Database schema:
{table_info}
 
    Today's date: {today}
 
    Rules:
    - Only SELECT queries. Never write INSERT, UPDATE, DELETE, DROP, or any data-modifying statement.
    - Use JOINs when multiple tables are needed.
    - If the question is ambiguous, make a reasonable assumption.
    """),
    MessagesPlaceholder("history", optional=True),
    ("human", "{input}")
])

sql_chain=sql_prompt|llm

# Explanation Prompt + Follow-up Questions
explain_prompt=ChatPromptTemplate.from_messages([
    ("system", """You are a helpful data analyst. Given a SQL query and its results, provide:
 
    1. A brief plain-English explanation of what the query does (1-2 sentences).
    2. Exactly 3 follow-up questions the user might want to ask next.
 
    Format your response exactly like this:
    EXPLANATION: <your explanation>
    FOLLOW-UP QUESTIONS:
    1. <question>
    2. <question>
    3. <question>
    """),
    ("human", "SQL Query: {sql}\n\nResults: {results}\n\nOriginal question: {question}")
])


explain_chain=explain_prompt|llm



def parse_explanation(response:AIMessage)->tuple[str,list[str]]:
    """Parse the explanation and follow-up questions from the response."""
    explanation=""
    follow_up=[]
    if "EXPLANATION:" in response.content:
        expl_block=response.content.split("EXPLANATION:")[1]
        if "FOLLOW-UP" in expl_block:
            explanation=expl_block.split("FOLLOW-UP")[0].strip()
        else:
            explanation=expl_block.strip()

        if "FOLLOW-UP QUESTIONS:" in response.content:
            fu_block = response.content.split("FOLLOW-UP QUESTIONS:")[1].strip()
            follow_ups=[q.strip() for q in fu_block.split("\n") if q.strip().startswith("1.") or q.strip().startswith("2.") or q.strip().startswith("3.")]
 
    return explanation, follow_ups
 

def history_to_messages(history:list[dict]|None)->list:
    """Convert history to LangChain messages."""
    if not history:
        return []
    msgs=[]
    for h in history:
        if "role" in h and "content" in h:
            if h["role"] == "user":
                msgs.append(HumanMessage(content=h["content"]))
            elif h["role"] == "assistant":
                msgs.append(AIMessage(content=h["content"]))
    return msgs


def ask(question:str,history:list[dict]|None=None)->dict:
    # Step 0: Check user intent before hitting the LLM
    is_safe, intent_msg = check_user_intent(question)
    if not is_safe:
        return {
            "question": question, "sql": "", "explanation": "",
            "results": None, "follow_ups": [], "error": intent_msg,
        }

    # Step 1: Generate SQL via LangChain chain
    try:
        schema_info=db.get_table_info()
        lc_history=history_to_messages(history)
        response=sql_chain.invoke({
            "input":question,
            "history":lc_history,
            "table_info":schema_info,
            "today":date.today().isoformat()
        })
        sql=response.content.strip().strip("`").strip()
        if sql.lower().startswith("sql"):
            sql=sql[3:].strip()
    except Exception as e:
        return {
            "question": question,"sql": "","explanation": "",
            "results": None,"follow_ups": [], "error": f"LLM error: {str(e)}",
        }

    if not sql:
        return {
            "question": question, "sql": "", "explanation": "",
            "results": None, "follow_ups": [],
            "error": "Could not generate a SQL query for this question.",
        }
    
    # Step 2: Safety Check
    is_safe,safety_msg=check_sqlquery(sql)
    if not is_safe:
        return {
            "question": question, "sql": "", "explanation": "",
            "results": None, "follow_ups": [],
            "error": safety_msg,
        }
    
    # Step 3: Execute SQL and get results
    try:
        results=execute_query(sql)
    except Exception as e:
        return {
            "question": question, "sql": "", "explanation": "",
            "results": None, "follow_ups": [],
            "error": f"SQL execution error: {str(e)}",
        }
    
    # Step 4: Explain the results and generate follow-up questions
    try:
        explain_response=explain_chain.invoke({
            "sql":sql,
            "results":results,
            "question":question,
        })
        explanation,follow_ups=parse_explanation(explain_response)
    except Exception as e:
        return {
            "question": question, "sql": "", "explanation": "",
            "results": None, "follow_ups": [],
            "error": f"Explanation error: {str(e)}",
        }
    
    return {
        "question": question, "sql": sql, "explanation": explanation,
        "results": results, "follow_ups": follow_ups, "error": None,
    }
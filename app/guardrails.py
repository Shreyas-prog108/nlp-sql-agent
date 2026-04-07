"""
Blocking dangerous SQL queries and destructive user intent.
"""

import re

BLACKLIST_PATTERNS=["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
    "CREATE", "REPLACE", "GRANT", "REVOKE", "EXEC", "EXECUTE",
    "ATTACH", "DETACH"]

DESTRUCTIVE_INTENT_PATTERNS=[
    r"\bdelete\b", r"\bdrop\b", r"\btruncate\b", r"\bpurge\b", r"\bwipe\b",
    r"\bremove\s+(all|the|every|an?)\b", 
    r"\bupdate\s+\w",                     
    r"\binsert\s+(a|an|into|new)\b",
    r"\bset\s+\w+\s*="
]

sql_patt=re.compile(
    r"\b("+"|".join(BLACKLIST_PATTERNS)+r")\b",
    re.IGNORECASE
)

intent_patt=re.compile(
    "|".join(DESTRUCTIVE_INTENT_PATTERNS),
    re.IGNORECASE
)

def check_sqlquery(sql:str)->tuple[bool,str]:
    """Check if the generated SQL is safe to execute."""
    if not sql.upper().lstrip().startswith("SELECT"):
        return False, "Only SELECT queries are allowed. The generated query was not a SELECT statement."
    match=sql_patt.search(sql)
    if match:
        return False, f"Blocked dangerous SQL operation: {match.group().upper()}. Only SELECT queries are allowed."
    return True, "OK"

def check_user_intent(question:str)->tuple[bool,str]:
    """Check if the user's question has destructive intent before hitting the LLM."""
    match=intent_patt.search(question)
    if match:
        return False, f"This agent only answers read-only questions about the database. Requests to modify or delete data are not supported."
    return True, "OK"
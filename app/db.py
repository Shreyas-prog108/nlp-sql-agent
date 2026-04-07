import os
import sqlite3
import time
from typing import Any

db_path=os.path.join(os.path.dirname(__file__),'..', 'instance', 'database.db')

def get_connection()->sqlite3.Connection:
    conn=sqlite3.connect(db_path)
    conn.row_factory=sqlite3.Row
    return conn

def execute_query(sql:str)->dict[str,Any]:
    """
    Execute a SQL query and return the results with metadata.
    """
    conn=get_connection()
    try:
        start=time.perf_counter()
        cursor=conn.execute(sql)
        rows=cursor.fetchall()
        elapsed=(time.perf_counter()-start)*1000
        cols=[desc[0] for desc in cursor.description] if cursor.description else []
        data=[dict(row) for row in rows]
        return{
            "cols":cols,
            "rows":data,
            "row_count":len(data),
            "time_ms":round(elapsed, 2)   
        }
    finally:
        conn.close()

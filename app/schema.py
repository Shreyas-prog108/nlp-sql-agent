from app.db import get_connection

def get_schema_context()->str:
    """Return a human-readable schema string for the LLM prompt."""
    conn=get_connection()
    cursor=conn.cursor()
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables=[row[0] for row in cursor.fetchall()]

    schema_parts=[]
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns=cursor.fetchall()
        col_defs=[]
        for col in columns:
            # col: (cid, name, type, notnull, default, pk)
            col_str=f"{col[1]} {col[2]}"
            if col[5]:
                col_str+=" PRIMARY KEY"
            if col[3]:
                col_str+=" NOT NULL"
            col_defs.append(col_str)

        # Foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        fks=cursor.fetchall()
        for fk in fks:
            col_defs.append(f"FOREIGN KEY ({fk[3]}) REFERENCES {fk[2]}({fk[4]})")
        schema_parts.append(f"CREATE TABLE {table} (\n" + ",\n".join(col_defs) + "\n);")
    conn.close()

    sample_hint = """
    -- Status values in projects: 'active', 'completed', 'overdue'
    -- Today's date should be used when comparing deadlines
    """
    return "\n\n".join(schema_parts) + sample_hint
    
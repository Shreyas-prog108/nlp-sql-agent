import sys
import os
from db.setup import init_db

def main():
    db_path=os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
    if not os.path.exists(db_path) or "--seed" in sys.argv:
        init_db()
        if "--seed" in sys.argv:
            return

    if "--ui" in sys.argv:
        import subprocess
        ui_path=os.path.join(os.path.dirname(__file__), "ui", "streamlit.py")
        subprocess.run(["streamlit", "run", ui_path])
        return

    import uvicorn
    print("NLP-SQL Agent is running on http://localhost:8000")
    print("Access docs at http://localhost:8000/docs")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
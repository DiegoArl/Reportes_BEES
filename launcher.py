from streamlit.web import cli as stcli
import sys
import os

if __name__ == "__main__":
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    app_path = os.path.join(base_path, "app.py")

    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.headless=true",
        "--global.developmentMode=false"
    ]

    sys.exit(stcli.main())
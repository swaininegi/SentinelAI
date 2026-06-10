import os, subprocess, sys
BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

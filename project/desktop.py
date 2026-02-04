import webview
import subprocess
import time
import os
import sys
import multiprocessing

def start_streamlit():
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    python_exe = sys.executable
    app_path = os.path.join(bundle_dir, "app.py")
    
    cmd = [
        python_exe, "-m", "streamlit", "run", app_path,
        "--server.headless", "true",
        "--server.port", "8505",
        "--server.address", "localhost"
    ]
    
    env = os.environ.copy()
    env["IS_STREAMLIT_CHILD"] = "true"
    env["PYTHONPATH"] = bundle_dir
    return subprocess.Popen(cmd, env=env)

if __name__ == "__main__":
    multiprocessing.freeze_support()

    if os.environ.get("IS_STREAMLIT_CHILD") == "true":
        pass
    else:
        p = start_streamlit()
        
        time.sleep(10) 
        
        window = webview.create_window(
            'BICE Insight', 
            url='http://localhost:8505',
            width=1200, 
            height=800
        )
        
        try:
            webview.start()
        finally:
            p.terminate()
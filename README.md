# SentinelAI Ultra Pro
AI-Powered Cybersecurity, Phishing, Scam & Deepfake Detection Platform.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## One-click Windows run
Double click `RUN_SENTINELAI.bat`.

## Build Windows EXE on your PC
```bash
pip install pyinstaller
pyinstaller --onefile --name SentinelAI_Launcher launcher.py
```
Then open `dist/SentinelAI_Launcher.exe`.

Admin password: `sentinel@2026`

Note: Deepfake image/video/audio modules use lightweight forensic heuristics so the demo runs offline. They are useful for hackathon MVP demonstration and can be replaced by trained models later.

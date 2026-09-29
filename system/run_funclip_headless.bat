@echo off
REM Headless FunClip launcher (no browser) — start Gradio server for pipeline gradio_client calls
REM --listen sets inbrowser=False (funclip\launch_config.py) and binds 127.0.0.1...0.0.0.0
REM --lang en: English Paraformer (launch.py default is zh = garbled English). Later args win: bat --lang zh overrides.
cd /d "D:\FunClip"
call "D:\FunClip.venv\Scripts\activate.bat"
python funclip\launch.py --listen --lang en %*

Set-Location backend

.venv\Scripts\Activate.ps1

Start-Process powershell -ArgumentList "python -m uvicorn app:app --host 0.0.0.0 --port 5000 --reload"
python .\bot_tele.py
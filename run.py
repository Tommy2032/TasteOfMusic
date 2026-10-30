import sys
import os
import uvicorn

# If running without console (e.g. pythonw / background service), redirect to log
if sys.stdout is None or sys.stderr is None:
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = open(os.path.join(log_dir, "server.log"), "a", encoding="utf-8")
    if sys.stdout is None:
        sys.stdout = log_file
    if sys.stderr is None:
        sys.stderr = log_file

if __name__ == "__main__":
    print("==================================================")
    print("  TasteOfMusic — Сравнение плейлистов Яндекс Музыки")
    print("  Сервер запускается по адресу: http://127.0.0.1:8000")
    print("==================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)

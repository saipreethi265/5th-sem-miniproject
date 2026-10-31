# Digital Human Rights Assistant

A Flask-based educational prototype for human-rights awareness, issue guidance, complaint drafting, and case record management. It is not a substitute for a qualified lawyer or an official complaint authority.

## Requirements
- Python 3.10 or newer
- Flask 3.x

## Run on Windows
1. Extract this folder.
2. Open a terminal inside the project folder.
3. Create and activate a virtual environment (recommended):
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```
4. Install dependencies:
   ```powershell
   py -m pip install -r requirements.txt
   ```
5. Start the application:
   ```powershell
   py app.py
   ```
6. Open http://127.0.0.1:5000 in your browser.

## Run on macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:5000.

## Project files
- `app.py` — Flask routes and application startup
- `assistant.py` — issue classification and assistant responses
- `awareness.py` — human-rights awareness content
- `complaint.py` — complaint-letter drafting
- `database.py` — SQLite case storage and management
- `templates/index.html` — user interface
- `static/style.css` — page styling
- `static/app.js` — browser-side interaction
- `human_rights.db` — SQLite database

The database file is stored relative to this project folder by default, so the app can be launched from another working directory. Set the `DATABASE_PATH` environment variable to use a different database location.

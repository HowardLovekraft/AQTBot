## How to setup bot
### Using Poetry
1. Setup Poetry:
   - Type `poetry install`
   - Use created virtual environment
2. Setup env variables in AQT/env/venv.env:
   - Type Telegram Bot API token
   - Type Postgres parameters (dbname, password, port, etc.)
### Using venv (for Raspeberry Pi)
1. Setup venv:
    - `python -m venv venv`
    - Activate virtual environment:
      - `venv\Scripts\activate.bat` - Windows
      - `source venv/bin/activate` - Linux
   - Install dependencies:
     - `pip install -r requirements.txt`
   
2. Start bot (in virtual environment!):
   - `python AQT/main.py` - venv
   - `path/to/poetry/venv AQT/main.py` - Poetry
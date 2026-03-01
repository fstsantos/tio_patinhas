# finorg Bot

This repository contains a Telegram bot for tracking family earnings and spendings.

## Setup

1. Create a Python virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment variables
   - Copy `.env.example` to `.env` and fill in your values.
   - **DATABASE_URL** is used by SQLAlchemy to connect to your database and should look like:
     `mysql+pymysql://user:password@host/db_name`
   - `.env` is ignored by git; you can keep sensitive credentials here.

3. Run the bot:
```bash
python -m src.main
```

# Smart URL Analytics

A Flask-based web application for analyzing URL traffic insights, comparing domains, and keeping a searchable history of previous lookups.

## Features
- User registration and login
- URL analysis dashboard
- Side-by-side URL comparison
- Search history tracking
- CSV export of analytics results

## Tech Stack
- Python
- Flask
- Flask-Login
- Flask-SQLAlchemy
- PostgreSQL (optional via `DATABASE_URL`)

## Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the environment template and fill in the values:
   ```bash
   copy .env.example .env
   ```
4. Run the app:
   ```bash
   python app.py
   ```

## Environment Variables
- `DATABASE_URL` (optional if you want to use a full database URL)
- `DB_USERNAME`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `SECRET_KEY`

## GitHub Publishing
After adding your repository on GitHub, run:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands
- Run application: `python app.py` (Runs on port 5001)
- Install dependencies: `pip install -r requirements.txt`
- Run tests: `pytest`
- Run single test: `pytest <test_file_path>`

## Architecture & Structure
The project is a Flask web application for expense tracking.

- `app.py`: Main application entry point containing routes and Flask configuration.
- `database/`: Database layer.
    - `db.py`: Intended for database connection logic (`get_db`), initialization (`init_db`), and seeding (`seed_db`).
- `templates/`: Jinja2 HTML templates for the frontend.
- `static/`: Static assets (CSS and JS).

The application currently implements a landing page, registration, and login views, with several placeholder routes for authentication and expense management (Profile, Add/Edit/Delete expenses) intended for future implementation.

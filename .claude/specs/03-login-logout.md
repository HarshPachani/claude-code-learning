# Spec: Login and Logout

## Overview
This feature implements the authentication flow, allowing registered users to securely access their accounts and terminate their sessions. It is a critical step in the Spendly roadmap to ensure that user data (expenses) remains private and accessible only to the account owner.

## Depends on
- 01-database-setup
- 02-registration

## Routes
- `GET /login` — Display login form — public
- `POST /login` — Process login credentials and start session — public
- `GET /logout` — Terminate session and redirect to landing — logged-in

## Database changes
No database changes.

## Templates
- **Create:** None
- **Modify:** 
    - `login.html`: Update to include a proper HTML form that POSTs to `/login`.
    - `base.html`: Add conditional navigation links (e.g., "Login" vs "Logout" and "Profile") based on session state.

## Files to change
- `app.py`: Implement logic for `/login` (GET/POST) and `/logout`.
- `templates/login.html`: Add form.
- `templates/base.html`: Update navigation.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done
- [ ] User can view the login page.
- [ ] User can log in with valid email and password from the seeded database (`demo@spendly.com` / `demo123`).
- [ ] User sees an error message upon providing invalid credentials.
- [ ] Once logged in, the navigation bar shows "Logout" and "Profile" instead of "Login" and "Register".
- [ ] User can click "Logout" and be returned to the landing page as a guest.
- [ ] Attempting to access `/logout` while not logged in redirects to the login page.

---
# Spec: Date Filter for Profile Page

## Overview
Currently, the profile page displays all expenses for a user without any way to filter them by time. This feature introduces a date range filter (Start Date and End Date) to the profile page, allowing users to analyze their spending habits over specific periods. This improves the utility of the spending summary and transaction list.

## Depends on
- 05-backend-routes-for-profile-page

## Routes
No new routes. The existing `/profile` route will be modified to accept optional query parameters:
- `GET /profile?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` — filtered profile view (logged-in)

## Database changes
No database changes. The existing `expenses` table already contains a `date` column (TEXT) which will be used for filtering in SQL queries.

## Templates
- **Modify:** `templates/profile.html` — Add a date filter form (two date inputs and a submit button) at the top of the profile content.

## Files to change
- `app.py` — Update the `profile()` route to handle `start_date` and `end_date` query parameters and pass them to the query functions.
- `database/queries.py` — Update `get_summary_stats`, `get_recent_transactions`, and `get_category_breakdown` to accept optional start and end dates.

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
- Use `BETWEEN` or `>=` and `<=` operators in SQL for date filtering.
- Ensure the filter handles cases where only one date is provided or neither is provided.

## Definition of done
- [ ] Profile page loads normally without filters.
- [ ] Selecting a date range and submitting the filter updates the Total Spent, Transaction Count, Top Category, and Transaction List.
- [ ] No transactions are shown if the date range contains no expenses.
- [ ] The filter form is styled using project CSS variables and integrates visually with the profile page.
- [ ] URL reflects the applied filters (e.g., `/profile?start_date=2026-10-01&end_date=2026-10-31`).
---

```markdown
# Bowling WebApp

This repository contains a small Flask-based bowling reservation webapp. Project root: `C:\Code\ThisIsTheEnd`.

Summary
- The app is a Flask server that renders Jinja templates from `Templates/`, serves static files from `Styles/` and `Public/`, and stores data in the SQLite database at `Database/bowling.db`.
- Registration and login are handled server-side and user accounts are stored in the `users` table inside that SQLite DB (see `Database/init.sql`).

Quick start (recommended)
1. Activate the project's virtual environment (created for this workspace):

```powershell
# Windows PowerShell - run from project root
C:\Code\ThisIsTheEnd\.venv\Scripts\Activate.ps1
```

2. Install dependencies (if not already installed):

```powershell
python -m pip install -r .\requirements.txt
```

3. Create or initialize the database (only if `Database/bowling.db` is missing):

```powershell
python .\Database\create_db.py
```

4. Start the Flask development server (temporary dev secret shown below):

```powershell
$env:THISISTHEEND_SECRET = 'dev-secret'
C:\Code\ThisIsTheEnd\.venv\Scripts\python.exe .\server.py
```

5. Open the app in your browser: `http://127.0.0.1:5000/`

Notes about accounts and DB
- Accounts are stored in `Database/bowling.db` in the `users` table. The schema is in `Database/init.sql` and contains: `id`, `username`, `password`, `role`, `display_name`.
- New registrations hash the password using `werkzeug.security.generate_password_hash` and insert into `users` (role defaults to `client`).
- There are example demo accounts inserted by `init.sql`: `client` / `client123` and `employee` / `employee123` (these demo passwords are included in the seed SQL for convenience).

Templates and static files
- Templates: `Templates/*.html` (rendered by Flask/Jinja)
- Styles: `Styles/` (served by the `styles` route)
- Public: `Public/` (served by the `public` route)

Routes of interest
- `/` → `index` (renders `Templates/index.html`)
- `/login` → login page and POST handler
- `/register` → registration page and POST handler
- `/dashboard` → user dashboard (requires login)
- `/logout` → logout

Development notes
- If you only want to preview static HTML/CSS (no server-side rendering or auth), you can open files from `Templates/` using VS Code Live Server — but Jinja tags will not be evaluated (they are rendered only by Flask).
- For debugging, watch the terminal running `server.py` for error messages and Flask build errors (e.g. missing endpoints cause `url_for` BuildError).

Local SMTP Email Testing

For development, you can test email sending without delivering real emails by using Python’s built-in SMTP debugging server:

1. Open a terminal and run:
   ```
   python -m smtpd -c DebuggingServer -n localhost:1025
   ```
   This starts a local SMTP server on port 1025 that prints emails to the terminal.

2. In your Flask app, set the following mail configuration:
   ```python
   app.config['MAIL_SERVER'] = 'localhost'
   app.config['MAIL_PORT'] = 1025
   app.config['MAIL_USERNAME'] = None
   app.config['MAIL_PASSWORD'] = None
   app.config['MAIL_USE_TLS'] = False
   app.config['MAIL_USE_SSL'] = False
   ```

3. Restart your Flask app and send a test email. The email content will appear in the terminal running the SMTP server.

**Note:** This is for development only—no emails are actually sent.

If you want, I can add a short PowerShell script to automate setup and run commands.

### Testing Email Functionality

This app includes a test route to verify email sending in development:

- Visit [http://127.0.0.1:5000/test_mail](http://127.0.0.1:5000/test_mail) in your browser while the Flask server is running.
- This triggers the `/test_mail` route, which attempts to send a test email to `thisistheendpart2@outlook.com` using the local SMTP server (see above).
- If successful, you’ll see a flash message: `Test email sent successfully!` and the email content will appear in the terminal running the SMTP server.
- If there’s an error, a flash message will show the error details.

**Example output in SMTP debug terminal:**
```
---------- MESSAGE FOLLOWS ----------
From: test@localhost
To: thisistheendpart2@outlook.com
Subject: Test Email from ThisIsTheEnd

This is a test email sent from your Flask app.
------------ END MESSAGE ------------
```

This is useful for verifying that your Flask-Mail configuration and email templates work as expected during development.
```

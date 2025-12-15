# =========================
# Imports & Configuration
# =========================
# In dit bestand staan alle serverroutes en hulpfuncties voor de bowling-applicatie.
# Flask en andere benodigde modules importeren
from flask_mail import Mail, Message
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Pad naar de hoofdmap en database instellen
ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / 'Database' / 'bowling.db'

# Flask-applicatie initialiseren
app = Flask(__name__, template_folder='Templates')
app.secret_key = os.environ.get('THISISTHEEND_SECRET') or 'change-this-secret-in-production'

# =========================
# Mail Configuratie
# =========================
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 1025
app.config['MAIL_USERNAME'] = None
app.config['MAIL_PASSWORD'] = None
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'test@localhost'

# Flask-Mail initialiseren
mail = Mail(app)

# =========================
# Hulpfuncties
# =========================
# Maakt een verbinding met de SQLite database
def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

# =========================
# Hulpfuncties voor reserveringstijden
# =========================
from datetime import datetime
# Genereert een lijst met tijdopties voor een bepaalde dag
def get_time_options(day_of_week, for_end_time=False):
    start_hour = 14
    end_hour = 24 if day_of_week in (0, 6) else 22
    options = []
    last = end_hour if for_end_time else end_hour - 1
    for hour in range(start_hour, last + 1):
        options.append(f"{hour:02d}:00")
    return options

# Bepaalt de start- en eindtijdopties op basis van de datum en huidige starttijd
def get_start_end_time_options(date_str, current_start=None):
    """
    date_str: 'YYYY-MM-DD' (from reservation.start_iso[:10])
    current_start: 'HH:MM' (optional, for pre-selecting end times)
    Returns (start_options, end_options)
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_of_week = date_obj.weekday()
    except Exception:
        # fallback: standaard naar een doordeweekse dag
        day_of_week = 2
    start_options = get_time_options(day_of_week, for_end_time=False)
    end_options = get_time_options(day_of_week, for_end_time=True)
    # Filter eindopties zodat alleen tijden na current_start overblijven
    if current_start and current_start in end_options:
        idx = end_options.index(current_start)
        end_options = end_options[idx+1:]
    return start_options, end_options

# Probeert te redirecten met url_for, anders valt hij terug op een simpel pad
def safe_redirect(endpoint, **values):
    """Try redirecting using url_for, fall back to simple path '/endpoint'."""
    try:
        return redirect(url_for(endpoint, **values))
    except Exception:
        try:
            if isinstance(endpoint, str):
                if endpoint.startswith('/'):
                    return redirect(endpoint)
                if '/' in endpoint or '.' in endpoint:
                    return redirect('/' + endpoint)
        except Exception:
            pass
        try:
            return redirect(url_for('index'))
        except Exception:
            return redirect('/')

# =========================
# Small/Simple Routes
# =========================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/unknown')
def unknown():
    return render_template('unknown.html')

@app.route('/a_create')
def a_create():
    return render_template('a_create.html')

@app.route('/e_create')
def e_create():
    return render_template('e_create.html')

@app.route('/Styles/<path:filename>')
def styles(filename):
    return send_from_directory(str(ROOT / 'Styles'), filename)

# =========================
# Authentication & Account Routes
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    if not (username or email) or not password:
        flash('Username, e-mail, and password are required.')
        return safe_redirect('login')
    conn = get_db_connection()
    if email:
        cur = conn.execute('SELECT * FROM users WHERE email = ?', (email,))
    else:
        cur = conn.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    conn.close()
    if not user:
        flash('No account found with that username or e-mail.')
        return safe_redirect('login')
    stored = user['password']
    try:
        if check_password_hash(stored, password):
            pass_ok = True
        else:
            pass_ok = (stored == password)
    except Exception:
        pass_ok = (stored == password)
    if not pass_ok:
        flash('Incorrect password.')
        return safe_redirect('login')
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['email'] = user['email'] if 'email' in user.keys() else user['username']
    session['role'] = user['role']
    flash('Logged in successfully.')
    return safe_redirect('dashboard')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip() or None
    password = request.form.get('password', '')
    password_confirm = request.form.get('password_confirm', '')
    if not username or not password:
        flash('Username and password are required.')
        return redirect(url_for('register'))
    if password != password_confirm:
        flash('Passwords do not match.')
        return redirect(url_for('register'))
    if len(password) < 6:
        flash('Password must be at least 6 characters long.')
        return redirect(url_for('register'))
    conn = get_db_connection()
    cur = conn.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cur.fetchone():
        conn.close()
        flash('Username already exists.')
        return redirect(url_for('register'))
    hashed = generate_password_hash(password)
    role = request.form.get('role') or 'client'
    conn.execute('INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)',
                 (username, hashed, role, email))
    conn.commit()
    conn.close()
    flash('Account registered — please log in.')
    return redirect(url_for('login'))

@app.route('/settings', methods=['GET'])
def settings():
    user_id = session.get('user_id')
    if not user_id:
        flash('Not logged in.')
        return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if not user:
        flash('User not found.')
        return redirect(url_for('login'))
    return render_template('settings.html', user=user)

@app.route('/edit_account', methods=['POST'])
def edit_account():
    user_id = session.get('user_id')
    if not user_id:
        flash('Not logged in.')
        return redirect(url_for('login'))
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    if not username or not email:
        flash('Username and email are required.')
        return redirect(url_for('settings'))
    conn = get_db_connection()
    cur = conn.execute('SELECT id FROM users WHERE username = ? AND id != ?', (username, user_id))
    if cur.fetchone():
        conn.close()
        flash('Username is already taken.')
        return redirect(url_for('settings'))
    if password:
        hashed = generate_password_hash(password)
        conn.execute('UPDATE users SET username = ?, email = ?, password = ? WHERE id = ?', (username, email, hashed, user_id))
    else:
        conn.execute('UPDATE users SET username = ?, email = ? WHERE id = ?', (username, email, user_id))
    conn.commit()
    conn.close()
    session['username'] = username
    session['email'] = email
    flash('Account details updated.')
    return redirect(url_for('settings'))    

@app.route('/delete_account', methods=['POST'])
def delete_account():
    user_id = session.get('user_id')
    if not user_id:
        flash('Not logged in.')
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    session.clear()
    flash('Account deleted.')
    return redirect(url_for('index'))

@app.route('/clients')
def clients():
    conn = get_db_connection()
    users = conn.execute('SELECT username, email FROM users').fetchall()
    conn.close()
    clients = [{'username': user['username'], 'email': user['email']} for user in users]
    return render_template('clients.html', clients=clients)

# =========================
# Reservation Routes
# =========================
@app.route('/reservation')
def reservation():
    return render_template('reservation.html')

@app.route('/make_reservation', methods=['POST'])
def make_reservation():
    date = request.form.get('date')
    time = request.form.get('time')
    end_time = request.form.get('end_time')
    if not date or not time or not end_time:
        flash('Date, start time, and end time are required.')
        return redirect(url_for('reservation'))
    session['reservation'] = {'date': date, 'time': time, 'end_time': end_time}
    return redirect(url_for('extra'))

@app.route('/extra', methods=['GET'])
def extra():
    return render_template('extra.html')

@app.route('/save_extra', methods=['POST'])
def save_extra():
    extra = request.form.get('extra')
    if not extra:
        flash('Selecteer een extra optie.')
        return redirect(url_for('extra'))
    session['reservation_extra'] = extra
    return redirect(url_for('unknown'))

# Handle extra selection for anonymous users (from unknown.html)
@app.route('/save_unknown', methods=['POST'])
def save_unknown():
    extra = request.form.get('extra')
    # Only update session if extra is provided, otherwise keep previous value
    if extra:
        session['reservation_extra'] = extra
    # Save name and email for anonymous users
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    session['username'] = name
    session['email'] = email
    return redirect(url_for('lanes'))

@app.route('/lanes')
def lanes():
    reservation = session.get('reservation')
    available_lanes = list(range(1, 9))
    if reservation:
        date = reservation['date']
        start_time = reservation['time']
        end_time = reservation['end_time']
        from datetime import datetime, timedelta
        start_iso = f"{date}T{start_time}"
        if end_time == "24:00":
            from datetime import timedelta
            end_dt = datetime.strptime(f"{date}T00:00", "%Y-%m-%dT%H:%M") + timedelta(days=1)
            end_iso = end_dt.strftime("%Y-%m-%dT%H:%M")
        else:
            end_iso = f"{date}T{end_time}"
            end_dt = datetime.strptime(end_iso, "%Y-%m-%dT%H:%M")
        start_dt = datetime.strptime(start_iso, "%Y-%m-%dT%H:%M")
        conn = get_db_connection()
        lanes = []
        for lane in range(1, 9):
            table = f"lane_{lane}"
            cur = conn.execute(f"SELECT start_iso, duration_minutes FROM {table}")
            overlap = False
            for row in cur.fetchall():
                existing_start = datetime.strptime(row['start_iso'], "%Y-%m-%dT%H:%M")
                existing_end = existing_start + timedelta(minutes=row['duration_minutes'])
                if existing_start < end_dt and existing_end > start_dt:
                    overlap = True
                    break
            if not overlap:
                lanes.append(lane)
        conn.close()
        available_lanes = lanes
    return render_template('lanes.html', reservation=reservation, available_lanes=available_lanes)

@app.route('/select_lane', methods=['POST'])
def select_lane():
    lane = request.form.get('lane')
    reservation = session.get('reservation')
    extra = session.get('reservation_extra')
    user_id = session.get('user_id')
    name = session.get('username', 'anonymous')
    email = session.get('email', None)
    if not lane or not reservation:
        flash('Selecteer een baan en maak eerst een reservering.')
        return redirect(url_for('lanes'))
    date = reservation['date']
    start_time = reservation['time']
    end_time = reservation['end_time']
    from datetime import datetime, timedelta
    start_iso = f"{date}T{start_time}"
    if end_time == "24:00":
        from datetime import timedelta
        end_dt = datetime.strptime(f"{date}T00:00", "%Y-%m-%dT%H:%M") + timedelta(days=1)
        end_iso = end_dt.strftime("%Y-%m-%dT%H:%M")
    else:
        end_iso = f"{date}T{end_time}"
        end_dt = datetime.strptime(end_iso, "%Y-%m-%dT%H:%M")
    start_dt = datetime.strptime(start_iso, "%Y-%m-%dT%H:%M")
    duration = int((end_dt - start_dt).total_seconds() // 60)
    table = f"lane_{lane}"
    conn = get_db_connection()
    cur = conn.execute(f"SELECT * FROM {table} WHERE start_iso = ?", (start_iso,))
    if cur.fetchone():
        conn.close()
        flash(f'Baan {lane} is al gereserveerd voor dit tijdstip.')
        return redirect(url_for('lanes'))
    # Insert reservation with extra, name, and email
    conn.execute(f"INSERT INTO {table} (start_iso, duration_minutes, user_id, name, extra, email) VALUES (?, ?, ?, ?, ?, ?)",
                 (start_iso, duration, user_id, name, extra, email))
    conn.commit()
    conn.close()
    flash(f'Reservatie voor baan {lane} is opgeslagen!')
    return redirect(url_for('index'))

@app.route('/reservations')
def reservations():
    import sqlite3
    from flask import request
    from datetime import datetime
    filter_date = request.args.get('filter_date', '')
    now = datetime.now()
    if not filter_date:
        filter_date = now.strftime('%Y-%m-%d')
    conn = get_db_connection()
    reservations_data = {}
    for lane in range(1, 9):
        table = f'lane_{lane}'
        cur = conn.execute(f"SELECT * FROM {table} WHERE start_iso LIKE ? ORDER BY start_iso", (f'{filter_date}%',))
        reservations_data[table] = cur.fetchall()
    conn.close()
    return render_template('reservations.html', reservations=reservations_data, filter_date=filter_date, now=now)

@app.route('/results', methods=['GET'])
def results():
    user_id = session.get('user_id')
    if not user_id:
        flash('Niet ingelogd.')
        return redirect(url_for('login'))
    conn = get_db_connection()
    reservations = {}
    for lane in range(1, 9):
        table = f'lane_{lane}'
        cur = conn.execute(f'SELECT * FROM {table} ORDER BY start_iso')
        reservations[table] = cur.fetchall()
    conn.close()
    return render_template('results.html', reservations=reservations, user_id=user_id)

# Edit reservation (GET)
@app.route('/edit_reservation', methods=['GET'])
def edit_reservation():
    lane = request.args.get('lane')
    start_iso = request.args.get('start_iso')
    if not lane or not start_iso:
        flash('Ongeldige reservering.')
        return redirect(url_for('reservations'))
    table = f'lane_{lane}'
    conn = get_db_connection()
    res = conn.execute(f'SELECT * FROM {table} WHERE start_iso = ?', (start_iso,)).fetchone()
    conn.close()
    if not res:
        flash('Reservering niet gevonden.')
        return redirect(url_for('reservations'))
    # Generate time options
    date_str = res['start_iso'][:10]
    current_start = res['start_iso'][11:16]
    start_options, end_options = get_start_end_time_options(date_str, current_start)
    return render_template(
        'edit_reservation.html',
        reservation=res,
        lane=lane,
        start_options=start_options,
        end_options=end_options,
    )

# Delete reservation (POST)
@app.route('/delete_reservation', methods=['POST'])
def delete_reservation():
    lane = request.form.get('lane')
    start_iso = request.form.get('start_iso')
    if not lane or not start_iso:
        flash('Ongeldige reservering.')
        return redirect(url_for('reservations'))
    table = f'lane_{lane}'
    conn = get_db_connection()
    conn.execute(f'DELETE FROM {table} WHERE start_iso = ?', (start_iso,))
    conn.commit()
    conn.close()
    flash('Reservering verwijderd.')
    return redirect(url_for('reservations'))

# Update reservation (POST)
@app.route('/update_reservation', methods=['POST'])
def update_reservation():
    lane = request.form.get('lane')
    old_start_iso = request.form.get('start_iso')
    date = request.form.get('date')
    time = request.form.get('time')
    duration_minutes = request.form.get('duration_minutes')
    extra = request.form.get('extra')
    name = request.form.get('name')
    email = request.form.get('email')
    if not lane or not old_start_iso or not date or not time:
        flash('Ongeldige reservering.')
        return redirect(url_for('reservations'))
    if not name or not email:
        # Fetch previous reservation to get name/email if not provided
        table = f'lane_{lane}'
        conn = get_db_connection()
        prev = conn.execute(f'SELECT name, email FROM {table} WHERE start_iso = ?', (old_start_iso,)).fetchone()
        if not name and prev:
            name = prev['name']
        if not email and prev:
            email = prev['email']
        conn.close()
    new_start_iso = f"{date}T{time}"
    table = f'lane_{lane}'
    conn = get_db_connection()
    # Remove old reservation
    conn.execute(f'DELETE FROM {table} WHERE start_iso = ?', (old_start_iso,))
    # Insert updated reservation
    conn.execute(f"INSERT INTO {table} (start_iso, duration_minutes, extra, name, email) VALUES (?, ?, ?, ?, ?)",
                 (new_start_iso, duration_minutes, extra, name, email))
    conn.commit()
    conn.close()
    flash('Reservering bijgewerkt!')
    return redirect(url_for('reservations'))

# =========================
# Test & Utility Routes
# =========================
@app.route('/test_mail')
def test_mail():
    try:
        msg = Message(
            subject='Test Email from Flask App',
            recipients=['thisisatest@outlook.com'],
            body='This is a test email sent from your Flask app.'
        )
        mail.send(msg)
        flash('Test email sent successfully!')
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Failed to send test email: {e}')
    return redirect(url_for('index'))

# =========================
# App Entry Point
# =========================

if __name__ == '__main__':
    if not DB_PATH.exists():
        print('Database not found at', DB_PATH)
        print('Run: python Database/create_db.py')
    app.run(host='127.0.0.1', port=5000, debug=True)


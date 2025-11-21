
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Configuration
ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / 'Database' / 'bowling.db'

app = Flask(__name__, template_folder='Templates')
# Use environment variable for secret key in production. Replace default before deploy.
app.secret_key = os.environ.get('THISISTHEEND_SECRET') or 'change-this-secret-in-production'


def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def safe_redirect(endpoint, **values):
    """Try redirecting using url_for, fall back to simple path '/endpoint'."""
    try:
        return redirect(url_for(endpoint, **values))
    except Exception:
        # If the caller passed a raw path (starts with /) redirect to it directly.
        try:
            if isinstance(endpoint, str):
                if endpoint.startswith('/'):
                    return redirect(endpoint)
                # If it looks like a filename or contains a slash, build a path
                if '/' in endpoint or '.' in endpoint:
                    return redirect('/' + endpoint)
        except Exception:
            pass
        # As a final safe fallback redirect to the index route or root path.
        try:
            return redirect(url_for('index'))
        except Exception:
            return redirect('/')
        
        # Route for extra selection page
@app.route('/extra', methods=['GET'])
def extra():
    return render_template('extra.html')

# Handle extra selection POST
@app.route('/save_extra', methods=['POST'])
def save_extra():
    extra = request.form.get('extra')
    if not extra:
        flash('Selecteer een extra optie.')
        return redirect(url_for('extra'))
    session['reservation_extra'] = extra
    return redirect(url_for('alley'))

@app.route('/settings', methods=['GET'])
def settings():
    user_id = session.get('user_id')
    if not user_id:
        flash('Niet ingelogd.')
        return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if not user:
        flash('Gebruiker niet gevonden.')
        return redirect(url_for('login'))
    return render_template('settings.html', user=user)

@app.route('/edit_account', methods=['POST'])
def edit_account():
    user_id = session.get('user_id')
    if not user_id:
        flash('Niet ingelogd.')
        return redirect(url_for('login'))
    username = request.form.get('username', '').strip()
    display_name = request.form.get('display_name', '').strip()
    password = request.form.get('password', '')
    if not username or not display_name:
        flash('Gebruikersnaam en weergavenaam zijn verplicht.')
        return redirect(url_for('settings'))
    conn = get_db_connection()
    # Check if username is taken by another user
    cur = conn.execute('SELECT id FROM users WHERE username = ? AND id != ?', (username, user_id))
    if cur.fetchone():
        conn.close()
        flash('Gebruikersnaam is al in gebruik.')
        return redirect(url_for('settings'))
    if password:
        hashed = generate_password_hash(password)
        conn.execute('UPDATE users SET username = ?, display_name = ?, password = ? WHERE id = ?', (username, display_name, hashed, user_id))
    else:
        conn.execute('UPDATE users SET username = ?, display_name = ? WHERE id = ?', (username, display_name, user_id))
    conn.commit()
    conn.close()
    session['username'] = username
    session['display_name'] = display_name
    flash('Accountgegevens bijgewerkt.')
    return redirect(url_for('settings'))

@app.route('/delete_account', methods=['POST'])
def delete_account():
    user_id = session.get('user_id')
    if not user_id:
        flash('Niet ingelogd.')
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    session.clear()
    flash('Account verwijderd.')
    return redirect(url_for('index'))



@app.route('/')
def index():
    # index.html is expected in Templates/
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        flash('Username and password are required.')
        return safe_redirect('login')

    conn = get_db_connection()
    cur = conn.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    conn.close()

    if not user:
        flash('No account found with that username.')
        return safe_redirect('login')

    stored = user['password']
    # Accept either a werkzeug password hash or existing plaintext password value
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

    # Successful login
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['display_name'] = user['display_name'] if 'display_name' in user.keys() else user['username']
    session['role'] = user['role']
    flash('Logged in successfully.')
    return safe_redirect('dashboard')

# Handle lane selection POST
@app.route('/select_lane', methods=['POST'])
def select_lane():
    lane = request.form.get('lane')
    reservation = session.get('reservation')
    extra = session.get('reservation_extra')
    user_id = session.get('user_id')
    name = session.get('username', 'anonymous')
    if not lane or not reservation:
        flash('Selecteer een baan en maak eerst een reservering.')
        return redirect(url_for('alley'))
    # Compose reservation times
    date = reservation['date']
    start_time = reservation['time']
    end_time = reservation['end_time']
    # Calculate start_iso and duration_minutes
    from datetime import datetime, timedelta
    start_iso = f"{date}T{start_time}"
    # Handle 24:00 as 00:00 next day
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
    # Check for overlap in the selected lane
    conn = get_db_connection()
    cur = conn.execute(f"SELECT * FROM {table} WHERE start_iso = ?", (start_iso,))
    if cur.fetchone():
        conn.close()
        flash(f'Baan {lane} is al gereserveerd voor dit tijdstip.')
        return redirect(url_for('alley'))
    # Insert reservation with extra
    conn.execute(f"INSERT INTO {table} (start_iso, duration_minutes, user_id, name, extra) VALUES (?, ?, ?, ?, ?)",
                 (start_iso, duration, user_id, name, extra))
    conn.commit()
    conn.close()
    flash(f'Reservatie voor baan {lane} is opgeslagen!')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form.get('username', '').strip()
    display_name = request.form.get('display_name', '').strip() or None
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
    role = request.form.get('role', 'client') or 'client'
    conn.execute('INSERT INTO users (username, password, role, display_name) VALUES (?, ?, ?, ?)',
                 (username, hashed, role, display_name))
    conn.commit()
    conn.close()
    flash('Account registered — please log in.')
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    # admin_dashboard.html is expected in Templates/
    return render_template('admin_dashboard.html')

@app.route('/employee_dashboard')
def employee_dashboard():
    import sqlite3
    from flask import request
    filter_date = request.args.get('filter_date', '')
    conn = get_db_connection()
    reservations = {}
    for lane in range(1, 9):
        table = f'lane_{lane}'
        if filter_date:
            cur = conn.execute(f"SELECT * FROM {table} WHERE start_iso LIKE ? ORDER BY start_iso", (f'{filter_date}%',))
        else:
            cur = conn.execute(f'SELECT * FROM {table} ORDER BY start_iso')
        reservations[table] = cur.fetchall()
    conn.close()
    return render_template('employee_dashboard.html', reservations=reservations, filter_date=filter_date)

@app.route('/create')
def create():
    # create.html is expected in Templates/
    return render_template('create.html')


# Reservation form POST handler
@app.route('/make_reservation', methods=['POST'])
def make_reservation():
    date = request.form.get('date')
    time = request.form.get('time')
    end_time = request.form.get('end_time')
    if not date or not time or not end_time:
        flash('Date, start time, and end time are required.')
        return redirect(url_for('reservation'))
    # Temporarily save reservation in session
    session['reservation'] = {'date': date, 'time': time, 'end_time': end_time}
    return redirect(url_for('extra'))

# Reservation form page (GET)
@app.route('/reservation')
def reservation():
    return render_template('reservation.html')


# Alley page displays reservation and available lanes
@app.route('/alley')
def alley():
    reservation = session.get('reservation')
    available_lanes = list(range(1, 9))
    if reservation:
        date = reservation['date']
        start_time = reservation['time']
        end_time = reservation['end_time']
        from datetime import datetime, timedelta
        start_iso = f"{date}T{start_time}"
        # Handle 24:00 as 00:00 next day
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
            # Check for any overlap: (existing.start < requested.end) and (existing.end > requested.start)
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
    return render_template('alley.html', reservation=reservation, available_lanes=available_lanes)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))



# Serve static asset folders referenced in templates
@app.route('/Styles/<path:filename>')
def styles(filename):
    return send_from_directory(str(ROOT / 'Styles'), filename)

@app.route('/JavaScript/<path:filename>')
def javascript(filename):
    return send_from_directory(str(ROOT / 'JavaScript'), filename)


@app.route('/Assets/<path:filename>')
def assets(filename):
    return send_from_directory(str(ROOT / 'Assets'), filename)

@app.route('/Public/<path:filename>')
def public(filename):
    return send_from_directory(str(ROOT / 'Public'), filename)


if __name__ == '__main__':
    if not DB_PATH.exists():
        print('Database not found at', DB_PATH)
        print('Run: python Database/create_db.py')
    app.run(host='127.0.0.1', port=5000, debug=True)

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
    return redirect(url_for('alley'))

# Reservation form page (GET)
@app.route('/reservation')
def reservation():
    return render_template('reservation.html')

# Alley page displays reservation
@app.route('/alley')
def alley():
    reservation = session.get('reservation')
    return render_template('alley.html', reservation=reservation)

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

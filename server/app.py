from flask import Flask, request, session, redirect, url_for, render_template, flash
from userinfo import init_db, create_user, verify_user

app = Flask(__name__, template_folder='../client/templates')
app.secret_key = 'your-secret-key-change-me'
app.config['DATABASE'] = 'server/users.db'

# Initialize database before first request
@app.before_first_request
def initialize():
    init_db()

@app.route('/')
def index():
    """Home page showing different content based on auth status."""
    if 'username' in session:
        return f"Welcome {session['username']}!"
    if 'guest' in session:
        return "Welcome Guest!"
    return render_template("index.html")

@app.route('/login', methods=['GET'])
def login():
    """Show login page."""
    if 'username' in session:
        return redirect('/')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    """Process login form submission."""
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Username and password required')
        return redirect(url_for('login'))

    if verify_user(username, password):
        session['username'] = username
        return redirect('/')
    
    flash('Invalid credentials')
    return redirect(url_for('login'))

@app.route('/create', methods=['GET'])
def create_account():
    """Show account creation page."""
    if 'username' in session:
        return redirect('/')
    return render_template('create_account.html')

@app.route('/create', methods=['POST'])
def handle_create():
    """Process account creation."""
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Username and password required')
        return redirect(url_for('create_account'))

    if create_user(username, password):
        session['username'] = username
        return redirect('/')
    
    flash('Username already exists')
    return redirect(url_for('create_account'))

@app.route('/logout')
def logout():
    """Clear session and logout."""
    session.clear()
    return redirect('/')

@app.route('/guest')
def continue_as_guest():
    """Set guest session flag."""
    session['guest'] = True
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)

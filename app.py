from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import json
import bcrypt
import secrets
from functools import wraps
from utils import get_bitcoin_price, get_ether_price

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Change to a fixed key in production

# ============= AUTHENTICATION MIDDLEWARE =============
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated_function

# ============= HELPER FUNCTIONS =============
def load_users():
    with open("save.json", "r", encoding="utf-8") as file:
        return json.load(file)

def save_users(data):
    with open("save.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def load_bids():
    with open("bids.json", "r", encoding="utf-8") as file:
        return json.load(file)

def save_bids(data):
    with open("bids.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

# ============= ROUTES =============

@app.route('/')
def index():
    return redirect(url_for('signin'))

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_bytes = password.encode('utf-8')
        
        users = load_users()
        
        # Check if user exists and password matches
        if username in users and bcrypt.checkpw(password_bytes, users[username]["password"].encode('utf-8')):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('signin.html', error="Invalid username or password")
    
    return render_template('signin.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    password_bytes = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
    
    users = load_users()
    
    if username in users:
        return render_template('signin.html', error="User already exists")
    
    users[username] = {"password": hashed_password, "balance": 0}
    save_users(users)
    
    return redirect(url_for('signin'))

@app.route('/dashboard')
@login_required
def dashboard():
    username = session['username']
    users = load_users()
    bitcoin_price = get_bitcoin_price()
    ether_price = get_ether_price()
    
    return render_template(
        'dashboard.html',
        username=username,
        balance=users[username]['balance'],
        bitcoin_price=bitcoin_price,
        ether_price=ether_price
    )

@app.route('/transfer', methods=['POST'])
@login_required
def transfer():
    sender = session['username']
    recipient = request.form.get('username')
    try:
        amount = float(request.form.get('amount'))
    except (ValueError, TypeError):
        return "Error: Transfer amount must be a valid number.", 400
    
    if amount <= 0:
        return "Error: Transfer amount must be greater than zero.", 400
    
    users = load_users()
    
    if recipient not in users:
        return "Error: Recipient does not exist.", 400
    
    if users[sender]['balance'] < amount:
        return "Error: Insufficient balance.", 400
    
    users[recipient]['balance'] += amount
    users[sender]['balance'] -= amount
    save_users(users)
    
    return redirect(url_for('dashboard'))

@app.route('/auction')
@login_required
def auction():
    username = session['username']
    bids = load_bids()
    highest_bid = bids.get('max', 0) if bids else 0
    
    return render_template('auction.html', username=username, highest_bid=highest_bid)

@app.route('/bid', methods=['POST'])
@login_required
def bid():
    bidder = session['username']
    try:
        price = float(request.form.get('price'))
    except (ValueError, TypeError):
        return "Error: Bid price must be a valid number.", 400
    
    users = load_users()
    bids = load_bids()
    
    if price <= 0:
        return "Error: Bid price must be greater than zero.", 400
    
    if users[bidder]['balance'] < price:
        return "Error: Insufficient balance to bid.", 400
    
    current_highest = bids.get('max', 0) if bids else 0
    
    if price <= current_highest:
        return "Error: Bid price must be higher than current highest bid.", 400
    
    # Update bid
    if not bids:
        bids = {"list": [price], "max": price}
    else:
        bids["list"].append(price)
        bids["max"] = price
    
    # Deduct from balance
    users[bidder]['balance'] -= price
    
    save_bids(bids)
    save_users(users)
    
    return redirect(url_for('auction'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
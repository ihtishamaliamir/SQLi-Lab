from flask import Flask, request, render_template, session, redirect, url_for
import sqlite3
import database

app = Flask(__name__, static_folder='static', static_url_path='/static')

app.secret_key = 'supersecretkey'
DB_PATH = "vuln.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/favicon.ico')
def favicon():
    return '', 204


# ------------------- Home -------------------
@app.route('/')
def index():
    return render_template('index.html')
# ------------------- Lab 1: Hidden Data -------------------
@app.route('/lab1')
def lab1():
    category = request.args.get('category', '').strip()

    conn = get_db()
    c = conn.cursor()

    # If no input → show only released products
    if category == '':
        query = "SELECT * FROM products WHERE released = 1"
    else:
        query = f"""
        SELECT * FROM products
        WHERE category = '{category}'
           OR name LIKE '%{category}%'
        """

    c.execute(query)
    products = c.fetchall()
    conn.close()

    # Solved only if hidden products are actually exposed
    solved = any(p['released'] == 0 for p in products)

    return render_template(
        'lab1.html',
        products=products,
        query=query,
        solved=solved
    )
# ------------------- Lab 2: Login Bypass -------------------
@app.route('/lab2', methods=['GET', 'POST'])
def lab2():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute(query)
            user = c.fetchone()
            conn.close()
            if user:
                session['logged_in_user'] = user['username']
                # Successful login with bypass -> solved
                solved = True
                return redirect(url_for('lab2_my_account', solved=1))
            else:
                return render_template('lab2.html', error="Invalid credentials", solved=False)
        except Exception:
            return "Internal Server Error", 500
    return render_template('lab2.html', solved=False)

@app.route('/lab2/my-account')
def lab2_my_account():
    if 'logged_in_user' not in session:
        return redirect('/lab2')
    username = session['logged_in_user']
    solved = request.args.get('solved') == '1'
    return render_template('lab2_account.html', username=username, solved=solved)

@app.route('/lab2/update-email', methods=['POST'])
def lab2_update_email():
    if 'logged_in_user' not in session:
        return redirect('/lab2')
    new_email = request.form['email']
    return render_template('lab2_account.html', username=session['logged_in_user'], 
                           email=new_email, message="Email updated", solved=True)

@app.route('/lab2/logout')
def lab2_logout():
    session.pop('logged_in_user', None)
    return redirect('/lab2')

# ------------------- Lab 3: Column Count -------------------
@app.route('/lab3')
def lab3():
    category = request.args.get('category', '').strip()

    query = f"SELECT id, name, price FROM products WHERE category = '{category}'"

    conn = get_db()
    c = conn.cursor()

    try:
        c.execute(query)
        results = c.fetchall()
    except Exception:
        results = []
    conn.close()

    # Solve condition: UNION used with NULL payload (training trigger)
    solved = (
        'union' in category.lower()
        and 'null' in category.lower()
        and len(results) > 0
    )

    return render_template(
        'lab3.html',
        results=results,
        query=query,
        solved=solved
    )

# ------------------- Lab 4: Text Column -------------------
# ------------------- Lab 4: Text Column -------------------
@app.route('/lab4')
def lab4():
    category = request.args.get('category', '')

    query = f"SELECT id, name, price FROM products WHERE category = '{category}'"

    try:
        conn = get_db()
        c = conn.cursor()
        c.execute(query)
        results = c.fetchall()
        conn.close()

    except Exception:
        return "Internal Server Error", 500

    solved = (
    "'A'" in category.upper() and
    'UNION' in category.upper() and
    len(results) > 0
)

    return render_template(
        'lab4.html',
        results=results,
        query=query,
        solved=solved
    )

# ------------------- Lab 5: Retrieve Data from Other Table -------------------
@app.route('/lab5')
def lab5():
    category = request.args.get('category', '')

    query = f"SELECT name, description FROM products WHERE category = '{category}'"

    try:
        conn = get_db()
        c = conn.cursor()
        c.execute(query)
        results = c.fetchall()
        conn.close()

    except Exception:
        return "Internal Server Error", 500

    solved = (
        'UNION' in category.upper() and
        any(
            'administrator' in row['name'] or
            'carlos' in row['name']
            for row in results
        )
    ) if results else False

    return render_template(
        'lab5.html',
        results=results,
        query=query,
        solved=solved
    )

# ---------- LAB 6: Multiple values in single column ----------
@app.route('/lab6')
def lab6():
    category = request.args.get('category', '')
    query = f"SELECT name, price FROM products WHERE category = '{category}'"
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute(query)
        results = c.fetchall()
        conn.close()
        extracted_creds = []
        for row in results:
            # Check both name and price columns for colon
            name_str = str(row['name']) if row['name'] else ''
            price_str = str(row['price']) if row['price'] else ''
            if ':' in name_str:
                parts = name_str.split(':', 1)
                if len(parts) == 2:
                    extracted_creds.append({'username': parts[0], 'password': parts[1]})
            elif ':' in price_str:
                parts = price_str.split(':', 1)
                if len(parts) == 2:
                    extracted_creds.append({'username': parts[0], 'password': parts[1]})
    except Exception:
        return "Internal Server Error", 500
    return render_template('lab6.html', results=results, query=query, extracted_creds=extracted_creds)

@app.route('/lab6/verify', methods=['GET', 'POST'])
def lab6_verify():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT * FROM secret_users WHERE username = ? AND password = ?", (username, password))
            user = c.fetchone()
            conn.close()
            if user:
                # Pass the username to success template
                return render_template('lab6_success.html', username=username)
            else:
                return render_template('lab6_verify.html', error="Invalid credentials")
        except Exception:
            return "Internal Server Error", 500
    # GET request – blank form
    return render_template('lab6_verify.html')

@app.route('/lab6/logout')
def lab6_logout():
    session.pop('lab6_user', None)
    return redirect('/lab6')

# ------------------- Lab 7: Database Version (MySQL) -------------------
@app.route('/lab7')
def lab7():
    category = request.args.get('category', '')
    
    # If the payload tries to get @@version, show simulated version
    if '@@version' in category.lower():
        version_str = "8.0.42-0ubuntu0.20.04.1"
        # Fake result set with one row (version) and two NULLs to match UNION
        fake_results = [(version_str, "", "")]
        return render_template('lab7.html', results=fake_results,
                               query=category, simulated=True, solved=True)
    
    # Normal query (no injection)
    query = f"SELECT id, name, price FROM products WHERE category = '{category}'"
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute(query)
        results = c.fetchall()
        conn.close()
        solved = False
    except Exception:
        return "Internal Server Error", 500
    return render_template('lab7.html', results=results, query=query,
                           simulated=False, solved=solved)

# ------------------- Lab 8: Listing Database Contents -------------------
@app.route('/lab8')
def lab8():
    category = request.args.get('category', '')
    query = f"SELECT name, description FROM products WHERE category = '{category}'"
    try:
        conn = get_db()
        c = conn.cursor()
        if 'information_schema.tables' in category.lower():
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = c.fetchall()
            results = [(t['name'], "") for t in tables]
            solved = True
            return render_template('lab8.html', results=results, query=query, simulated=True, solved=solved)
        else:
            c.execute(query)
            results = c.fetchall()
            conn.close()
            solved = False
    except Exception:
        return "Internal Server Error", 500
    return render_template('lab8.html', results=results, query=query, simulated=False, solved=solved)

# ------------------- Reset Database -------------------
@app.route('/reset')
def reset():
    database.reset_db()
    return "Database reset successfully. <a href='/'>Go home</a>"

if __name__ == '__main__':
    database.init_db()
    app.run(debug=True)

import sqlite3
import os

DB_PATH = "vuln.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('DROP TABLE IF EXISTS products')
    c.execute('''CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        category TEXT,
        price REAL,
        released INTEGER
    )''')
    
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )''')
    
    c.execute('DROP TABLE IF EXISTS secret_users')
    c.execute('''CREATE TABLE secret_users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )''')
    
    products = [
        ("AbZorba Ball", "Amazing bouncing ball", "Toys", 69.82, 1),
        ("Folding Gadgets", "Foldable smartphone", "Tech gifts", 13.07, 1),
        ("Padding Pool Shoes", "Comfortable pool shoes", "Footwear", 34.59, 1),
        ("Gym Suit", "Professional gym suit", "Clothing", 23.94, 1),
        ("Caution Sign", "Bathroom warning sign", "Corporate gifts", 27.03, 0),
        ("Com-Tool", "Social communication tool", "Tech gifts", 34.40, 0),
        ("Giant Pillow Thing", "Enormous pillow", "Lifestyle", 99.99, 0),
    ]
    for p in products:
        c.execute("INSERT INTO products (name, description, category, price, released) VALUES (?,?,?,?,?)",
                  (p[0], p[1], p[2], p[3], p[4]))
    
    # Users table (Lab 2 bypass requires 'administrator' user)
    c.execute("INSERT INTO users (username, password) VALUES ('wiener', 'carlos')")
    c.execute("INSERT INTO users (username, password) VALUES ('carlos', 'montoya')")
    c.execute("INSERT INTO users (username, password) VALUES ('administrator', 'anything')")
    
    # Secret users table (Labs 5 & 6)
    c.execute("INSERT INTO secret_users (username, password) VALUES ('administrator', 's5nyvwp4y7hcgbzlg0u')")
    c.execute("INSERT INTO secret_users (username, password) VALUES ('carlos', '46jy2y8coo3dvqc0lwvt')")
    
    conn.commit()
    conn.close()

def reset_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()

if __name__ == "__main__":
    reset_db()

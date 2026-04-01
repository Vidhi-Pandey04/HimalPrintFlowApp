from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
import os
import secrets
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # generates a strong random key
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 365  # session expires in 2 hour
# Change these to your own username and password
APP_USERNAME = 'username'
APP_PASSWORD = 'yourpassword'
DB = 'himal.db'

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if (request.form.get('username') == APP_USERNAME and
                request.form.get('password') == APP_PASSWORD):
            session['logged_in'] = True
            session.permanent = True
            return redirect(url_for('dashboard'))
        error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_type TEXT NOT NULL,
            description TEXT,
            quantity INTEGER DEFAULT 1,
            design_cost REAL DEFAULT 0,
            printing_cost REAL DEFAULT 0,
            total REAL DEFAULT 0,
            discount REAL DEFAULT 0,
            status TEXT DEFAULT 'Pending',
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
    ''')
    conn.commit()
    conn.close()

ORDER_TYPES = [
    "Book Publishing", "School Diary", "School Register", "Banner", "Certificate","School Marksheet", "Janev Card", "Namkaran Card",
    "Wedding Card","Sharadh Card", "Poster", "Stamp", "Custom Printing", "Design Service","Annaprashan Card", "Bill Book", "Letter Head",
    "Rashid Book","Pamphlet","Register","Other"
]
STATUSES = ["Pending", "In Design", "Printing", "Delivered", "Completed" , "Cancelled"]

@app.route('/')
@login_required
def dashboard():
    conn = get_db()

    # --- Date filter params ---
    filter_type = request.args.get('filter', 'all')  # all, today, month, year, custom
    month       = request.args.get('month', '')       # YYYY-MM
    year        = request.args.get('year', '')        # YYYY
    date_from   = request.args.get('date_from', '')   # YYYY-MM-DD
    date_to     = request.args.get('date_to', '')     # YYYY-MM-DD

    now = datetime.now()

    # Build WHERE clause for date filtering
    date_clause = ''
    date_params = []

    if filter_type == 'today':
        date_clause = "AND DATE(o.created_at) = DATE('now','localtime')"
    elif filter_type == 'month':
        if month:
            date_clause = "AND strftime('%Y-%m', o.created_at) = ?"
            date_params = [month]
        else:
            date_clause = "AND strftime('%Y-%m', o.created_at) = strftime('%Y-%m', 'now','localtime')"
    elif filter_type == 'year':
        if year:
            date_clause = "AND strftime('%Y', o.created_at) = ?"
            date_params = [year]
        else:
            date_clause = "AND strftime('%Y', o.created_at) = strftime('%Y', 'now','localtime')"
    elif filter_type == 'custom' and date_from and date_to:
        date_clause = "AND DATE(o.created_at) BETWEEN ? AND ?"
        date_params = [date_from, date_to]

    def q(sql, params=[]):
        return conn.execute(sql, params).fetchone()

    def qall(sql, params=[]):
        return conn.execute(sql, params).fetchall()

    base = f"FROM orders o WHERE status != 'Cancelled' {date_clause}"

    total_orders    = q(f"SELECT COUNT(*) as c {base}", date_params)['c']
    pending         = q(f"SELECT COUNT(*) as c {base} AND status='Pending'", date_params)['c']
    in_design       = q(f"SELECT COUNT(*) as c {base} AND status='In Design'", date_params)['c']
    printing        = q(f"SELECT COUNT(*) as c {base} AND status='Printing'", date_params)['c']
    delivered       = q(f"SELECT COUNT(*) as c {base} AND status='Delivered'", date_params)['c']
    completed       = q(f"SELECT COUNT(*) as c {base} AND status='Completed'", date_params)['c']
    revenue         = q(f"SELECT COALESCE(SUM(total),0) as r {base} AND status='Completed'", date_params)['r']
    pending_revenue = q(f"SELECT COALESCE(SUM(total),0) as r {base} AND status NOT IN ('Completed','Cancelled')", date_params)['r']

    recent_orders = qall(f'''
        SELECT o.*, c.name as customer_name, c.phone
        FROM orders o JOIN customers c ON o.customer_id = c.id
        WHERE o.status != 'Cancelled' {date_clause}
        ORDER BY o.created_at DESC LIMIT 8
    ''', date_params)

    order_type_stats = qall(f'''
        SELECT order_type, COUNT(*) as count, COALESCE(SUM(total),0) as revenue
        {base}
        GROUP BY order_type ORDER BY count DESC
    ''', date_params)
    # Add bar width for progress bars (cap at 100%)
    max_count = order_type_stats[0]['count'] if order_type_stats else 1
    order_type_stats = [
        {**dict(row), 'bar_width': min(round(row['count'] / max_count * 100), 100)}
        for row in order_type_stats
    ]

    # Available years for the year dropdown (from actual data)
    years = qall("SELECT DISTINCT strftime('%Y', created_at) as yr FROM orders ORDER BY yr DESC")
    years = [row['yr'] for row in years if row['yr']]

    conn.close()
    return render_template('dashboard.html',
        total_orders=total_orders, pending=pending, in_design=in_design,
        printing=printing, delivered=delivered, completed=completed,
        revenue=revenue, pending_revenue=pending_revenue,
        recent_orders=recent_orders, order_type_stats=order_type_stats,
        filter_type=filter_type, month=month, year=year,
        date_from=date_from, date_to=date_to,
        years=years, now=now)

@app.route('/orders')
@login_required
def orders():
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    conn = get_db()
    query = '''SELECT o.*, c.name as customer_name, c.phone FROM orders o
               JOIN customers c ON o.customer_id = c.id WHERE 1=1'''
    params = []
    if status_filter:
        query += ' AND o.status = ?'
        params.append(status_filter)
    if search:
        query += ' AND (c.name LIKE ? OR c.phone LIKE ? OR o.order_type LIKE ? OR o.description LIKE ?)'
        params.extend([f'%{search}%']*4)
    query += ' ORDER BY o.created_at DESC'
    orders_list = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('orders.html', orders=orders_list, statuses=STATUSES,
                           status_filter=status_filter, search=search)

@app.route('/orders/new', methods=['GET', 'POST'])
@login_required
def new_order():
    if request.method == 'POST':
        data = request.form
        phone = data['phone'].strip()
        name = data['name'].strip()
        conn = get_db()

        # Upsert customer
        customer = conn.execute("SELECT * FROM customers WHERE phone=?", (phone,)).fetchone()
        if not customer:
            conn.execute("INSERT INTO customers (name, phone) VALUES (?,?)", (name, phone))
            conn.commit()
            customer = conn.execute("SELECT * FROM customers WHERE phone=?", (phone,)).fetchone()
        else:
            conn.execute("UPDATE customers SET name=? WHERE id=?", (name, customer['id']))
            conn.commit()

        # Parse item indices sent by the form
        raw_indices = data.get('item_indices', '')
        indices = [i.strip() for i in raw_indices.split(',') if i.strip()]

        last_order_id = None
        for idx in indices:
            order_type = data.get(f'order_type_{idx}', '').strip()
            if not order_type:
                continue  # skip empty rows
            qty       = int(data.get(f'quantity_{idx}', 1) or 1)
            design    = float(data.get(f'design_cost_{idx}', 0) or 0)
            printing  = float(data.get(f'printing_cost_{idx}', 0) or 0)
            discount  = float(data.get(f'discount_{idx}', 0) or 0)
            total     = design + (printing * qty) - discount
            if total < 0:
                total = 0
            desc      = data.get(f'description_{idx}', '')
            notes     = data.get(f'notes_{idx}', '')

            conn.execute('''INSERT INTO orders
                            (customer_id, order_type, description, quantity,
                             design_cost, printing_cost, discount, total, status, notes)
                            VALUES (?,?,?,?,?,?,?,?,?,?)''',
                         (customer['id'], order_type, desc, qty,
                          design, printing, discount, total, 'Pending', notes))
            conn.commit()
            last_order_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.close()

        # If multiple orders, go to orders list filtered by customer; else go to the single order
        if last_order_id:
            if len(indices) > 1:
                return redirect(url_for('customer_detail', customer_id=customer['id']))
            return redirect(url_for('order_detail', order_id=last_order_id))
        return redirect(url_for('orders'))

    conn = get_db()
    prefill_phone = request.args.get('phone', '')
    customer = None
    if prefill_phone:
        customer = conn.execute("SELECT * FROM customers WHERE phone=?", (prefill_phone,)).fetchone()
    conn.close()
    return render_template('new_order.html', order_types=ORDER_TYPES, customer=customer)

@app.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    conn = get_db()
    order = conn.execute('''SELECT o.*, c.name as customer_name, c.phone
                            FROM orders o JOIN customers c ON o.customer_id=c.id
                            WHERE o.id=?''', (order_id,)).fetchone()
    if not order:
        return redirect(url_for('orders'))
    history = conn.execute('''SELECT o.*, c.name as customer_name FROM orders o
                              JOIN customers c ON o.customer_id=c.id
                              WHERE c.id=? AND o.id!=? ORDER BY o.created_at DESC''',
                           (order['customer_id'], order_id)).fetchall()
    conn.close()
    return render_template('order_detail.html', order=order, statuses=STATUSES, history=history)

@app.route('/orders/<int:order_id>/status', methods=['POST'])
@login_required
def update_status(order_id):
    status = request.form.get('status')
    if status in STATUSES:
        conn = get_db()
        conn.execute("UPDATE orders SET status=?, updated_at=datetime('now','localtime') WHERE id=?",
                     (status, order_id))
        conn.commit()
        conn.close()
    return redirect(url_for('order_detail', order_id=order_id))

@app.route('/orders/<int:order_id>/delete', methods=['POST'])
@login_required
def delete_order(order_id):
    conn = get_db()
    conn.execute("DELETE FROM orders WHERE id=?", (order_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('orders'))

@app.route('/orders/<int:order_id>/bill')
@login_required
def bill(order_id):
    gst = request.args.get('gst', '0') == '1'
    conn = get_db()
    order = conn.execute('''SELECT o.*, c.name as customer_name, c.phone
                            FROM orders o JOIN customers c ON o.customer_id=c.id
                            WHERE o.id=?''', (order_id,)).fetchone()
    conn.close()
    if not order:
        return redirect(url_for('orders'))
    return render_template('bill.html', order=order, gst=gst)

@app.route('/customers')
@login_required
def customers():
    search = request.args.get('search', '')
    conn = get_db()
    if search:
        custs = conn.execute('''SELECT c.*, COUNT(o.id) as order_count,
                                COALESCE(SUM(o.total),0) as total_value
                                FROM customers c LEFT JOIN orders o ON c.id=o.customer_id
                                WHERE c.name LIKE ? OR c.phone LIKE ?
                                GROUP BY c.id ORDER BY c.name''',
                             (f'%{search}%', f'%{search}%')).fetchall()
    else:
        custs = conn.execute('''SELECT c.*, COUNT(o.id) as order_count,
                                COALESCE(SUM(o.total),0) as total_value
                                FROM customers c LEFT JOIN orders o ON c.id=o.customer_id
                                GROUP BY c.id ORDER BY c.name''').fetchall()
    conn.close()
    return render_template('customers.html', customers=custs, search=search)

@app.route('/customers/<int:customer_id>')
@login_required
def customer_detail(customer_id):
    conn = get_db()
    customer = conn.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
    if not customer:
        return redirect(url_for('customers'))
    orders_list = conn.execute('''SELECT * FROM orders WHERE customer_id=?
                                  ORDER BY created_at DESC''', (customer_id,)).fetchall()
    conn.close()
    return render_template('customer_detail.html', customer=customer, orders=orders_list)

@app.route('/api/customer_search')
@login_required
def customer_search():
    phone = request.args.get('phone', '')
    conn = get_db()
    customer = conn.execute("SELECT * FROM customers WHERE phone=?", (phone,)).fetchone()
    conn.close()
    if customer:
        return jsonify({'found': True, 'name': customer['name'], 'id': customer['id']})
    return jsonify({'found': False})

if __name__ == '__main__':
    init_db()
    # debug=False in production, never expose debug mode
    app.run(debug=False, host='127.0.0.1', port=5000)
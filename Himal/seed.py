from app import get_db, init_db
init_db()
conn = get_db()
conn.execute("INSERT OR IGNORE INTO customers (name, phone) VALUES ('Ramesh Sharma', '9876543210')")
conn.execute("INSERT OR IGNORE INTO customers (name, phone) VALUES ('Priya Verma', '9812345678')")
conn.execute("INSERT OR IGNORE INTO customers (name, phone) VALUES ('Ajay Wedding Hall', '9998887776')")
conn.commit()
c1 = conn.execute("SELECT id FROM customers WHERE phone='9876543210'").fetchone()[0]
c2 = conn.execute("SELECT id FROM customers WHERE phone='9812345678'").fetchone()[0]
c3 = conn.execute("SELECT id FROM customers WHERE phone='9998887776'").fetchone()[0]
conn.executemany("INSERT INTO orders (customer_id, order_type, description, quantity, design_cost, printing_cost, total, status) VALUES (?,?,?,?,?,?,?,?)", [
    (c1, 'Book Publishing', 'Class 10 Science Textbook, A4, 200 pages', 500, 2000, 12, 8000, 'In Design'),
    (c1, 'Poster', 'Election campaign poster, A1 size, full colour', 200, 500, 8, 2100, 'Completed'),
    (c2, 'School Diary', 'Ryan International School diary 2025-26', 1000, 3000, 15, 18000, 'Printing'),
    (c3, 'Wedding Card', 'Designer wedding invitation with envelope', 300, 1500, 10, 4500, 'Pending'),
    (c3, 'Stamp', 'Self-inking rubber stamp, 2 designs', 2, 0, 350, 700, 'Completed'),
])
conn.commit()
conn.close()
print("Sample data added!")

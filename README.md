# 🏔️ Himal PrintFlow

> A simple, practical billing and order management system built for printing and publishing businesses.

Himal PrintFlow helps you manage custom print orders, generate bills and GST invoices, track order status, and communicate with customers via WhatsApp — all from a clean desktop app that works completely offline.

---

## 📋 Table of Contents

- [About](#about)
- [Features](#features)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Running the App](#running-the-app)
- [Building the Desktop App](#building-the-desktop-app)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [Security](#security)
- [Database](#database)
- [Contributing](#contributing)
- [License](#license)

---

## About

Himal PrintFlow was built for a real printing and publishing business in Pithoragarh, Uttarakhand. Most billing software assumes a retail shop model — fixed products, fixed prices, walk-in customers. But a print business is different. Every order is custom. Customers communicate on WhatsApp. Prices depend on quantity, paper type, design complexity, and more.

This app is built around that workflow:

1. Customer calls or messages on WhatsApp
2. You create an order with their details
3. The order moves through design → printing → delivery
4. You generate a bill or GST invoice when ready
5. You send it to the customer directly via WhatsApp

No unnecessary complexity. No internet required. Just a clean, fast desktop app.

---

## Features

### 📦 Order Management
- Create orders with customer name and phone number
- Multiple items per order (e.g. posters + stamps in one go)
- Order types: Book Publishing, Wedding Card, Poster, Stamp, School Diary, Banner, Certificate, and more
- Auto-calculated totals: `Design Cost + (Printing Cost × Quantity)`
- Flat discount per item
- Internal notes per order (not shown on bill)
- Order status tracking: Pending → In Design → Printing → Delivered → Completed

### 👥 Customer Management
- Customers created automatically when an order is placed
- Phone number lookup — auto-fills name for returning customers
- Full order history per customer
- Lifetime value tracking
- "Regular customer" badge at 3+ orders

### 🧾 Billing
- Simple bill or GST Invoice (18% — CGST 9% + SGST 9%)
- Clean, printable format
- UPI QR code on every bill
- Discount shown separately on bill
- One-click print from browser

### 📱 WhatsApp Integration
- One-click pre-filled WhatsApp message with full order details
- Opens WhatsApp Web directly from order page
- Quick WhatsApp button on customer profile too

### 📊 Dashboard
- Revenue collected vs pipeline value
- Orders by status (Pending, In Design, Printing, Delivered, Completed)
- Orders by type with visual bar chart
- Date filters: Today, This Month, This Year, custom date range, specific month/year picker
- Recent orders table

### 🔒 Security
- Username and password login
- Session-based authentication
- Session persists until explicit logout
- All routes protected

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Database | SQLite |
| Desktop wrapper | PyWebView |
| Fonts | Syne (headings), DM Sans (body) — Google Fonts |
| Packaging | PyInstaller |

No external CSS frameworks. No JavaScript frameworks. No internet dependency at runtime.

---

## Project Structure

```
himal/
├── app.py                  # Flask app — all routes and business logic
├── desktop.py              # PyWebView wrapper — runs as desktop app
├── db_encrypt.py           # Utility to encrypt/decrypt database backups
├── requirements.txt        # Python dependencies
├── himal.db                # SQLite database (created on first run)
│
├── templates/
│   ├── base.html           # Sidebar layout, navigation
│   ├── login.html          # Login page
│   ├── dashboard.html      # Dashboard with stats and filters
│   ├── orders.html         # Orders list with search and filter
│   ├── new_order.html      # Create order form (multi-item)
│   ├── order_detail.html   # Order detail, status update, WhatsApp
│   ├── bill.html           # Printable bill / GST invoice
│   ├── customers.html      # Customer list
│   └── customer_detail.html # Customer profile and order history
│
└── static/
    ├── css/
    │   └── style.css       # All styles — custom design system
    ├── favicon.svg         # Browser tab icon
    ├── himal.ico           # Windows app icon
    └── qr.jpeg             # UPI QR code shown on bills
```

---

## Getting Started

### Prerequisites

- Python 3.8 or higher installed at `E:\py` (or your system Python)
- pip available

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/himal-printflow.git
cd himal-printflow
```

**2. Install dependencies**
```bash
# If using a custom Python path (e.g. E drive)
E:\py\python.exe -m pip install flask
E:\py\python.exe -m pip install pywebview
E:\py\python.exe -m pip install cryptography
E:\py\python.exe -m pip install pyinstaller
E:\py\python.exe -m pip install Pillow

# Or if Python is on your system PATH
pip install flask pywebview cryptography pyinstaller Pillow
```

**3. Set your login credentials**

Open `app.py` and find these lines near the top:
```python
APP_USERNAME = 'himal'
APP_PASSWORD = 'your_strong_password_here'
```
Change them to your own username and password before running.

**4. Add your UPI QR code**

Place your UPI QR code image as `static/qr.jpeg`. This will appear on all generated bills.

**5. Update business details in `bill.html`**

Find and update:
```html
📍 Your address here
📞 Your phone number
📧 your@email.com
GSTIN: YOUR-GSTIN-HERE
```

---

## Running the App

### As a web app (browser)
```bash
E:\py\python.exe app.py
```
Then open `http://127.0.0.1:5000` in your browser.

### As a desktop app (recommended)
```bash
E:\py\python.exe desktop.py
```
This opens the app in its own window — no browser needed.

### First run
The database (`himal.db`) is created automatically on first run. No setup needed.

---

## Building the Desktop App

To package into a standalone `.exe` that runs on any Windows machine without Python installed:

**Step 1 — Generate the app icon**
```bash
E:\py\python.exe -c "
from PIL import Image, ImageDraw
def draw_icon(size):
    img = Image.new('RGBA', (size, size), (0,0,0,0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0,0,size-1,size-1], radius=size//8, fill=(26,26,46,255))
    s = size
    d.polygon([(s//2, s//8), (s*13//16, s*3//4), (s*3//16, s*3//4)], fill=(232,93,38,255))
    d.polygon([(s//2, s//8), (s*9//16, s*5//16), (s*7//16, s*5//16)], fill=(255,255,255,200))
    d.polygon([(s*3//8, s*3//8), (s*9//16, s*3//4), (s*3//16, s*3//4)], fill=(255,122,69,160))
    return img
sizes = [256,128,64,48,32,16]
imgs = [draw_icon(s) for s in sizes]
imgs[0].save('static/himal.ico', format='ICO', append_images=imgs[1:], sizes=[(s,s) for s in sizes])
print('Icon created')
"
```

**Step 2 — Build the exe**
```bash
E:\py\python.exe -m PyInstaller --noconfirm --onefile --windowed --name "HimalPrintFlow" --icon=static/himal.ico --add-data "templates;templates" --add-data "static;static" desktop.py
```

**Step 3 — Find your app**

The built app will be at `dist/HimalPrintFlow.exe`.

> ⚠️ The `himal.db` database file is **not** bundled into the exe. It is created in the same folder as the exe on first run. Keep the exe and the db file together. Back up the db file regularly.

---

## Usage Guide

### Creating an Order

1. Click **New Order** in the sidebar or top bar
2. Enter the customer's phone number — if they've ordered before, their name fills in automatically
3. Fill in the order type, quantity, description, design cost, printing cost, and discount
4. Click **＋ Add Another Item** to add more items to the same order (e.g. poster + stamp)
5. The Order Summary table updates live as you type
6. Click **Create Order**

### Updating Order Status

Open any order → use the **Update Status** dropdown → click Update.

Statuses in order: `Pending → In Design → Printing → Delivered → Completed`

### Sending a WhatsApp Message

Open any order → click the green **WhatsApp** button in the top bar. This opens WhatsApp Web with a pre-filled message containing all order details.

### Generating a Bill

Open any order → click **Bill** (simple) or **GST Invoice** (with 18% tax breakdown) → click **Print** to print or save as PDF.

### Encrypting the Database (Backup)

```bash
# Encrypt a backup copy
E:\py\python.exe db_encrypt.py encrypt yourpassword

# Decrypt it later
E:\py\python.exe db_encrypt.py decrypt yourpassword
```

This creates `himal.db.enc` — a fully encrypted backup of your database. Store it safely.

---

## Configuration

### Billing formula

```
Item Total = Design Cost + (Printing Cost per unit × Quantity) − Discount
```

GST Invoice splits the total as:
```
Base Amount = Total ÷ 1.18
CGST (9%)   = (Total − Base) ÷ 2
SGST (9%)   = (Total − Base) ÷ 2
```

### Order types

Edit the `ORDER_TYPES` list in `app.py` to add or remove order types:
```python
ORDER_TYPES = [
    "Book Publishing", "School Diary", "School Register", "Banner",
    "Certificate", "School Marksheet", "Janev Card", "Namkaran Card",
    "Wedding Card", "Sharadh Card", "Poster", "Stamp", "Custom Printing",
    "Design Service", "Annaprashan Card", "Bill Book", "Letter Head",
    "Rashid Book", "Pamphlet", "Register", "Other"
]
```

### Order statuses

Edit the `STATUSES` list in `app.py`:
```python
STATUSES = ["Pending", "In Design", "Printing", "Delivered", "Completed", "Cancelled"]
```

---

## Security

- Login is required to access any page
- Sessions persist until the user explicitly logs out
- `SESSION_COOKIE_HTTPONLY = True` prevents JavaScript from reading the session cookie
- `SESSION_COOKIE_SAMESITE = 'Lax'` protects against cross-site request forgery
- `debug=False` in production — never expose the Flask debug mode
- The app runs on `127.0.0.1` only — not accessible from other devices on the network

> For additional security, change your `APP_PASSWORD` to something strong (12+ characters, mix of letters, numbers, symbols) and never commit it to a public repository.

---

## Database

The app uses SQLite with two tables:

**customers**
| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| name | TEXT | Customer name |
| phone | TEXT | Phone number (unique) |
| created_at | TEXT | First order date |

**orders**
| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| customer_id | INTEGER | Foreign key → customers |
| order_type | TEXT | Type of print job |
| description | TEXT | Custom description |
| quantity | INTEGER | Number of units |
| design_cost | REAL | One-time design charge |
| printing_cost | REAL | Per-unit printing charge |
| discount | REAL | Flat discount amount |
| total | REAL | Final calculated total |
| status | TEXT | Current order status |
| notes | TEXT | Internal notes |
| created_at | TEXT | Order creation time |
| updated_at | TEXT | Last status update time |

---

## Contributing

This project was built for a specific business but is designed to be easy to adapt. If you run a printing, publishing, or any custom-order business and want to use or adapt this:

1. Fork the repository
2. Make your changes
3. Update the business details in `bill.html`
4. Change your login credentials in `app.py`
5. Rebuild the exe

Pull requests are welcome for bug fixes and general improvements.

---

## License

MIT License — free to use, modify, and distribute.

---

*Built with ❤️ for Himal Printers and Publishers, Pithoragarh, Uttarakhand*
## Author
*Vidhi Pandey*

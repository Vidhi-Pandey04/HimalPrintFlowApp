import webview
import threading
from app import app, init_db

def run_flask():
    init_db()
    app.run(port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Start Flask in background thread
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()

    # Small delay to let Flask start
    import time
    time.sleep(1)

    # Open desktop window
    webview.create_window(
        title='Himal — Print & Publishing',
        url='http://127.0.0.1:5000',
        width=1200,
        height=800,
        min_size=(900, 600),
        resizable=True
    )
    webview.start(icon='static/himal.ico')
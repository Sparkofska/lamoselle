import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from lamoselle import app

app.run(
    host='0.0.0.0',
    port= 80,
    debug=True,
    use_reloader=False # prevents core from loading twice on startup
    )


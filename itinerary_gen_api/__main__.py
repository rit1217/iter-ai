from .api import app


app.run(use_reloader=True, host='0.0.0.0', port=3200)
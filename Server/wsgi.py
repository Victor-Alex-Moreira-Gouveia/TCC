from main import app

# Gunicorn expects a module-level 'app' callable
application = app

# Backwards compatibility - gunicorn commonly imports 'app'
# so we expose it directly as well
# 'wsgi:app' will find 'app' here
app = application

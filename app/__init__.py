from flask import Flask, g
from flask_login import current_user
from .app_factory import create_app
from .db_connect import close_db, get_db

app = create_app()

# Register Blueprints
from app.blueprints.auth import auth
from app.blueprints.dashboard import dashboard
from app.blueprints.rentals import rentals

app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(rentals)

# Import routes (for any non-blueprint routes)
from . import routes

@app.before_request
def before_request():
    g.db = get_db()
    if g.db is None:
        print("Warning: Database connection unavailable. Some features may not work.")

@app.after_request
def add_cache_control_headers(response):
    """
    Add cache control headers to prevent browser caching of protected pages.
    This ensures that after logout, users cannot access protected pages via back button.
    """
    if current_user.is_authenticated:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# Setup database connection teardown
@app.teardown_appcontext
def teardown_db(exception=None):
    close_db(exception)
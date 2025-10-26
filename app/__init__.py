from flask import Flask, g
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

# Setup database connection teardown
@app.teardown_appcontext
def teardown_db(exception=None):
    close_db(exception)
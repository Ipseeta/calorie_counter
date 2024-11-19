from flask import Blueprint, render_template, send_from_directory, current_app
import os

page_bp = Blueprint('page', __name__)

# Add your routes here 
@page_bp.route('/')
def index():
    return render_template('index.html')

@page_bp.route('/favicon.ico')
def favicon():
    print(f"favicon requested from {current_app.root_path}")
    return send_from_directory(
        os.path.join(current_app.root_path, 'static/favicon'),
        'favicon.ico', 
        mimetype='image/x-icon'
    )

@page_bp.route('/site.webmanifest')
def webmanifest():
    print(f"webmanifest requested from {os.path.join(current_app.root_path, 'static')}")
    return send_from_directory(
        os.path.join(current_app.root_path, 'static'),
        'site.webmanifest',
        mimetype='application/manifest+json'
    )
from flask import Blueprint, render_template

# Create a homepage Blueprint
homepage_bp = Blueprint('homepage_bp', __name__, template_folder='templates/homepage')

@homepage_bp.route('/')
def homepage():
    return "<h1>Homepage Test</h1>"


@homepage_bp.route('/test')
def test():
    return "<h1>Test page in the homepage</h1>"


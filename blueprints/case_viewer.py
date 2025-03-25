from flask import Blueprint, render_template

# Create a case_viewer Blueprint
case_viewer_bp = Blueprint('case_viewer', __name__, template_folder='templates/case_viewer')

@case_viewer_bp.route('/')
def homepage():
    return "<h1>Homepage Test</h1>"


@case_viewer_bp.route('/test')
def test():
    return "<h1>Test page in the homepage</h1>"


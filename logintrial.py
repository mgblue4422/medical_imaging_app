from flask import Flask, render_template, request, redirect, url_for, jsonify
from patients import patients_bp  # Import the patients blueprint


app = Flask(__name__)

# Register the patients blueprint
app.register_blueprint(patients_bp, url_prefix='/patients')
# Hjemmeside rute for login-skjemaet
@app.route('/')
def index():
    return render_template('login.html')  # Din login.html


# Login rute som håndterer POST-forespørsel
@app.route('/login', methods=['POST'])
def login():
    # Hent brukernavn og passord fra skjemaet
    username = request.form['username']
    password = request.form['password']

    # Enkel sjekk for brukernavn og passord (kan endres til databasevalidering)
    if username == 'admin' and password == 'admin':  # Eksempel på hardkodede verdier
        # Hvis pålogging er vellykket, send brukeren videre til BAC.html
        return redirect(url_for('bac'))  # Omdirigerer til BAC.html
    else:
        return "Invalid login", 403  # Feilmelding ved feil innlogging


# Rute for BAC.html
@app.route('/bac')
def bac():
    return render_template('BACtrial.html')  # Din BAC.html side



@app.route('/section/<section_name>')
def section(section_name):
    if section_name == 'home':
        return render_template('home.html')  # Render home.html

    elif section_name == 'patients':
        #return render_template('patients.html')
        return redirect(url_for('patients.patients'))  # Redirect to the patients blueprint
        #return '<h2>Patients Section</h2><p>This is where you can manage patients.</p>'#render_template('patients.html')  # Render patients.html
    elif section_name == 'analysis':
        return   '<h2>Analysis Section</h2><p>This is where you can perform analysis.</p>'#render_template('analysis.html')  # Render analysis.html
    else:
        return "Section not found", 404

if __name__ == '__main__':
    app.run(debug=True)

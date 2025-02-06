from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


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
    return render_template('BAC.html')  # Din BAC.html side


if __name__ == '__main__':
    app.run(debug=True)

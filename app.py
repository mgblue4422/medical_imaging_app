from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cases')
def cases():
    return render_template('cases.html')

@app.route('/segmentation/<case_id>')
def segmentation(case_id):
    return render_template('segmentation.html', case_id=case_id)

if __name__ == '__main__':
    app.run(debug=True)
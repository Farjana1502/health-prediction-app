from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai

# Gemini API Key
#genai.configure(api_key="")

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    dob = db.Column(db.String(20))
    email = db.Column(db.String(100))
    glucose = db.Column(db.Float)
    haemoglobin = db.Column(db.Float)
    cholesterol = db.Column(db.Float)
    remarks = db.Column(db.String(500))

# Create DB
with app.app_context():
    db.create_all()

# AI Prediction Function
def predict_health(glucose, haemoglobin, cholesterol):

    remarks = []

    if glucose > 140:
        remarks.append("High Diabetes Risk")

    if haemoglobin < 12:
        remarks.append("Possible Anemia")

    if cholesterol > 240:
        remarks.append("High Cholesterol")

    if len(remarks) == 0:
        return "Health Parameters Normal"

    return ", ".join(remarks)

# Home Page
@app.route('/')
def index():
    patients = Patient.query.all()
    return render_template('index.html', patients=patients)

# Add Patient
@app.route('/add', methods=['GET', 'POST'])
def add():

    if request.method == 'POST':

        fullname = request.form['fullname']
        dob = request.form['dob']
        email = request.form['email']
        glucose = float(request.form['glucose'])
        haemoglobin = float(request.form['haemoglobin'])
        cholesterol = float(request.form['cholesterol'])

        remarks = predict_health(
        glucose,
        haemoglobin,
        cholesterol
)

        patient = Patient(
            fullname=fullname,
            dob=dob,
            email=email,
            glucose=glucose,
            haemoglobin=haemoglobin,
            cholesterol=cholesterol,
            remarks=remarks
        )

        db.session.add(patient)
        db.session.commit()

        return redirect('/')

    return render_template('add_patient.html')

# Edit Patient
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    patient = Patient.query.get_or_404(id)

    if request.method == 'POST':

        patient.fullname = request.form['fullname']
        patient.dob = request.form['dob']
        patient.email = request.form['email']
        patient.glucose = float(request.form['glucose'])
        patient.haemoglobin = float(request.form['haemoglobin'])
        patient.cholesterol = float(request.form['cholesterol'])

        patient.remarks = predict_health(
        patient.glucose,
        patient.haemoglobin,
        patient.cholesterol
)

        db.session.commit()

        return redirect('/')

    return render_template('edit_patient.html', patient=patient)

# Delete Patient
@app.route('/delete/<int:id>')
def delete(id):

    patient = Patient.query.get_or_404(id)

    db.session.delete(patient)
    db.session.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
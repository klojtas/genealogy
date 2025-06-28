import os
from flask import Flask, render_template, request, redirect, url_for
from gedcom_handler import Gedcom

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_new_gedcom', methods=['GET', 'POST'])
def create_new_gedcom():
    if request.method == 'POST':
        filename = request.form['filename']
        if not filename.endswith('.ged'):
            filename += '.ged'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        Gedcom.create_empty_gedcom(filepath)
        return redirect(url_for('view_gedcom', filename=filename))
    return render_template('create_new_gedcom.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return redirect(url_for('view_gedcom', filename=filename))

@app.route('/gedcom/<filename>')
def view_gedcom(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return "Error: GEDCOM file not found.", 404
    gedcom = Gedcom(filepath)
    print(f"Individuals being passed to template: {gedcom.individuals}")
    print(f"Families being passed to template: {gedcom.get_families()}")
    return render_template('gedcom.html', filename=filename, individuals=gedcom.individuals, families=gedcom.get_families())

@app.route('/edit_individual/', defaults={'filename': None}, methods=['GET', 'POST'])
@app.route('/edit_individual/<filename>/<individual_id>', methods=['GET', 'POST'])
def edit_individual(filename, individual_id):
    if filename is None:
        return redirect(url_for('index'))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    gedcom = Gedcom(filepath)
    individual = gedcom.get_individual_by_id(individual_id)

    if request.method == 'POST':
        new_name = request.form['name']
        new_birth_date = request.form.get('birth_date', '')
        new_birth_place = request.form.get('birth_place', '')
        gedcom.update_individual(individual_id, new_name, new_birth_date, new_birth_place)
        gedcom.save_gedcom(filepath) # Save changes back to the file
        return redirect(url_for('view_gedcom', filename=filename))

    return render_template('edit_individual.html', filename=filename, individual=individual)

@app.route('/add_individual/', defaults={'filename': None}, methods=['GET', 'POST'])
@app.route('/add_individual/<filename>', methods=['GET', 'POST'])
def add_individual(filename):
    if filename is None:
        return redirect(url_for('index'))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    gedcom = Gedcom(filepath)

    if request.method == 'POST':
        name = request.form['name']
        sex = request.form['sex']
        birth_date = request.form.get('birth_date', '')
        birth_place = request.form.get('birth_place', '')
        gedcom.add_individual(name, sex, birth_date, birth_place)
        gedcom.save_gedcom(filepath)
        return redirect(url_for('view_gedcom', filename=filename))

    return render_template('add_individual.html', filename=filename)

@app.route('/delete_individual/', defaults={'filename': None}, methods=['POST'])
@app.route('/delete_individual/<filename>/<individual_id>', methods=['POST'])
def delete_individual(filename, individual_id):
    if filename is None:
        return redirect(url_for('index'))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    gedcom = Gedcom(filepath)
    gedcom.delete_individual(individual_id)
    gedcom.save_gedcom(filepath)
    return redirect(url_for('view_gedcom', filename=filename))

if __name__ == '__main__':
    app.run(debug=True)

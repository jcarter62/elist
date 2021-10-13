from flask import Flask, render_template, redirect, request, url_for, send_file, session, current_app
from flask_bootstrap import Bootstrap
from db import DB
from emp_picture import EmployeePicture
import os

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = app.config['SECRET_KEY']
Bootstrap(app)

# Upload folder
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.before_request
def load_config():
    app.config.from_object('config')
    return


@app.route('/')
def route_home():
    db = DB()
    employees = db.load_employees()
    context = {
        'employees': employees,
        'title': 'Employees - Home'
    }
    return render_template('home.html', context=context)


@app.route('/login')
def route_login():
    context = {
        "title": "Login"
    }
    return render_template('login.html', context=context)


@app.route('/login', methods=['POST'])
def route_login_post():

    context = {
        "title": "Login - post"
    }
    return render_template('login.html', context=context)


@app.route('/employee/<empid>')
def route_employee(empid):
    db = DB()
    employee = db.load_employee(empid)
    imageurl = '/image/' + employee['empid']

    # imageurl = url_for('static', filename='pictures' + str(employee['empid']) + '.jpg' )

    context = {
        'employee': employee,
        'title': 'Display Employee',
        'imageurl': imageurl
    }
    return render_template('employee.html', context=context)


@app.route('/image/<id>')
def route_image_id_name(id):
    empPict = EmployeePicture(id)
    imageurl = empPict.getimagepath()
    if imageurl <= '':
        imageurl =  os.path.join(empPict._current_app.root_path,'static','thumbnailgenerator.jpg')
    return send_file(imageurl)


@app.route('/edit/<empid>')
def route_edit_id(empid):
    db = DB()
    employee = db.load_employee(empid)
    context = {
        'employee': employee,
        'title': 'Add Employee'
    }
    return render_template('editemployee.html', context=context)


@app.route('/save', methods=['POST'])
def route_save_post():
    id = request.form['id']
    db = DB()
    emp = db.load_employee(id)
    emp['first_name'] = request.form['i_first_name']
    emp['last_name'] = request.form['i_last_name']
    emp['desk_phone'] = request.form['i_desk_phone']
    emp['mobile_phone'] = request.form['i_mobile_phone']
    emp['email'] = request.form['i_email']
    emp['title'] = request.form['i_title']
    emp['empid'] = request.form['i_empid']
    emp['location'] = request.form['i_location']
    emp['start_date'] = request.form['i_start_date']
    emp['end_date'] = request.form['i_end_date']
    db.update_employee(emp)

    url = '/employee/' + str(id)
    return redirect(url)


@app.route('/add')
def route_add():
    db = DB()
    id = db.create_new_employee()
    url = '/edit/' + str(id)
    return redirect(url)


@app.route('/upload/<id>')
def route_upload_id(id):
    db = DB()
    employees = db.load_employees()
    employee = None
    recordid = 0
    for e in employees:
        if e['empid'] == id:
            recordid = e['id']
            employee = e

    context = {
        'employee': employee,
        'title': 'Upload new image for Employee'
    }
    return render_template('upload_image.html', context=context)


@app.route('/upload-post', methods=['post'])
def route_upload_post():
    id = request.form['empid']
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        print(uploaded_file.filename)

    empPict = EmployeePicture(id)
    imagefolder = empPict.get_image_folder()
    fullpath = os.path.join(imagefolder, uploaded_file.filename)
    uploaded_file.save(fullpath)
    url = '/'
    return redirect(url)


@app.route('/maintenance')
def route_maintenance():
    context = {
        'title': 'Maintenance'
    }
    return render_template('maintenance.html', context=context)


@app.route('/export')
def route_export():
    from csvio import csvExport
    filename = csvExport().execute()
    return send_file(filename)


@app.route('/import-employees')
def route_import_employees():
    # ref: https://medevel.com/flask-tutorial-upload-csv-file-and-insert-rows-into-the-database/
    context = {
        "title": "Import CSV"
    }
    return render_template('importcsv.html', context=context)


@app.route('/import-employees', methods=['post'])
def route_import_employees_post():
    from csvio import csvImport
    file_path = ''

    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)

    imp = csvImport()
    data = imp.parseCSV(file_path)
    db = DB()
    db.load_from_array(data)

    return redirect('/')


@app.route('/delete', methods=['POST'])
def route_delete_empid_post():
    empid = request.form['empid']
    db = DB()
    db.delete_employee(empid)
    return redirect('/')


@app.route('/delete/<empid>')
def route_delete_empid_get(empid):
    db = DB()
    employee = db.load_employee(empid)
    if employee is None:
        return redirect('/')

    context = {
        "title": "Delete Record",
        "employee": employee
    }
    return render_template('del-employee.html', context=context)


if __name__ == '__main__':
    app.run()

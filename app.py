from flask import Flask, render_template, redirect, request, url_for
from flask_bootstrap import Bootstrap
from db import DB

app = Flask(__name__)
Bootstrap(app)

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

@app.route('/employee/<id>')
def route_employee(id):
    db = DB()
    employee = db.load_employee(id)

    imageurl = url_for('static', filename='pictures' + str(employee['empid']) )
    context = {
        'employee': employee,
        'title': 'Display Employee',
        'imageurl': imageurl
    }
    return render_template('employee.html', context=context)

@app.route('/edit/<id>')
def route_edit_id(id):
    db = DB()
    employee = db.load_employee(id)
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
    db.update_employee(emp)

    url = '/edit/' + str(id)
    return redirect(url)


@app.route('/add')
def route_add():
    db = DB()
    id = db.create_new_employee()
    url = '/edit/' + str(id)
    return redirect(url)


if __name__ == '__main__':
    app.run()

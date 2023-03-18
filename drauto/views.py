from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db import connection
from datetime import datetime
from drauto.backend_functions import generate_cl_string, findASalesPerson, findClient, getDiscountPrice, getPrice, \
    update_employee, update_mechanic, update_vehicle, car_update
from drauto.forms import EmployeeLoginForm, EmployeeUpdateForm
from drauto.models import Employee

# Create your views here.
cursor = connection.cursor()


def index(requests):
    return render(requests, 'drauto/index.html')


def client_login(requests):
    page = 'login'

    return render(requests, 'drauto/login_register_form.html')


def staff_login(request):
    page = 'login'

    if request.method == 'POST':
        form = EmployeeLoginForm(request.POST)
        if form.is_valid():
            emp_name = form.cleaned_data.get('emp_name')
            password = form.cleaned_data.get('password')
            user_type = 'E'

            user = authenticate(request, emp_name=emp_name, password_hash=password)
            if user is not None:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT dbo.ValidateLogin('{emp_name}', '{password}', '{user_type}')")
                    result = cursor.fetchone()[0]
                    if result == 1:
                        login(request, user)
                    else:
                        return redirect('/')
    else:
        print(form.errors.as_data())
        form = EmployeeLoginForm()

    context = {'page': page, 'form': form}
    return render(request, 'drauto/login_register_form.html', context)


def logout_user(requests):
    logout(requests)

    return redirect('/')


def register_form(requests):
    page = 'register'

    return render(requests, 'drauto/login_register_form.html', context)


def vehicle(requests):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM DrautoshopAddb.dbo.Vehicle")
        vehicle_list = cursor.fetchall()
        context = {
            'vehicle_list': vehicle_list,
        }

    return render(requests, 'drauto/vehicle.html', context)


def purchase(requests, vehicle_id):
    # if not requests.user.is_authenticated:
    #     return redirect('/')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM DrautoshopAddb.dbo.Vehicle")
        vehicle_list = cursor.fetchall()

        for v in vehicle_list:
            if v[0] == vehicle_id:
                # Store the values for the corresponding column names
                vehicle = {
                    'chassis_number': v[0],
                    'make': v[1],
                    'import_price_usd': v[2],
                    'car_year': v[3],
                    'markup_percent': v[4],
                    'colour': v[5],
                    'engine_number': v[6],
                    'model': v[7],
                    'car_type': v[8],
                    'condition': v[9],
                    'mileage': v[10],
                    'cc_rating': v[11],
                    'price': getPrice(v[0]),
                    'discount_price': getDiscountPrice(v[0]),
                    'isSold': v[12],
                }
                print(vehicle)
                break  # Exit the loop once the vehicle is found

        # If the vehicle is not found, set the purchase_id to 'Not Present'
        if not vehicle:
            vehicle = {'purchase_id': 'Not Present'}

    if requests.method == 'POST':
        payment_Method = requests.POST['paymentMethod']
        client_name = requests.POST['client_name']
        client_id = findClient(client_name)
        amount_paid = requests.POST['amountPaid']
        purchase_id = generate_cl_string('PI')
        price = vehicle.get('price')
        chassis_number = vehicle.get('chassis_number')
        emp_id = findASalesPerson()
        commission = .15

        # storing loging purchase

        with connection.cursor() as cursor:
            # cursor.execute(f"""EXEC sp_AddClientPurchase
            # '{purchase_id}',
            # '{client_id}',
            # '{chassis_number}',
            # '{emp_id}',
            # {price},
            # {commission},
            # GETDATE(),
            # {amount_paid},
            # '{payment_Method}';
            # """)

            cursor.execute(f"""INSERT INTO DrautoshopAddb.dbo.Client_Purchase(purchase_id, client_Id, chassis_number, emp_Id, price, commission, date_sold, amt_paid, payment_method)
                                 VALUES('{purchase_id}', '{client_id}', '{chassis_number}', '{emp_id}' ,'{price}','{commission}', GETDATE(), '{amount_paid}', '{payment_Method}');""")
            connection.commit()
            return redirect('/')

    context = {'vehicle': vehicle}
    return render(requests, 'drauto/purchase.html', context)


def contact(requests):
    return render(requests, 'drauto/contact_page.html')


def admin_views(requests):
    with connection.cursor() as cursor:
        cursor.execute("Select * From view_sales_by_salesman")
        sales_list = cursor.fetchall()

        cursor.execute("Select * From view_commision_made_on_purchases")
        commission_list = cursor.fetchall()

        cursor.execute("Select * From view_vehciles_bought_by_client")
        client_purchase_list = cursor.fetchall()

        cursor.execute("Select * From view_vehicles_bought_by_salesman")
        salesman_purchase_list = cursor.fetchall()

        cursor.execute("Select * From view_invoice")
        invoice_list = cursor.fetchall()
        print(invoice_list)

    context = {'sales_list': sales_list,
               'commission_list': commission_list,
               'client_purchase_list': client_purchase_list,
               'salesman_purchase_list': salesman_purchase_list,
               'invoice_list': invoice_list, }

    print(context)
    return render(requests, 'drauto/admin_page.html', context)


def services(requests):
    return render(requests, 'drauto/services.html')


def client_purchase(requests):
    with connection.cursor() as cursor:
        cursor.execute("Select * From view_invoice Where Client = '{client_name}'")
        invoice_list = cursor.fetchall()

    context = {'invoice': invoice_list}
    return render(requests, 'drauto/client_purchase.html', context)


def admin_control_employee(requests):
    with connection.cursor() as cursor:
        cursor.execute(
            "Select *, emergency_contact_number  From Employee LEFT JOIN  Emergency_Contact EC on EC.emp_id = Employee.emp_id ")
        employee_list = cursor.fetchall()

        cursor.execute(
            "SELECT *, EC.emergency_contact_number FROM Mechanic LEFT JOIN Emergency_Contact EC ON EC.emp_id = Mechanic.emp_id")
        mechanic_list = cursor.fetchall()

        cursor.execute(
            "SELECT *, EC.emergency_contact_number FROM Salesman LEFT JOIN Emergency_Contact EC ON EC.emp_id = Salesman.emp_id")
        salesman_list = cursor.fetchall()

        cursor.execute(
            "SELECT *, EC.emergency_contact_number FROM Admin_Personnel LEFT JOIN Emergency_Contact EC ON EC.emp_id = Admin_Personnel.emp_id")
        admin_list = cursor.fetchall()

        cursor.execute(
            "SELECT *, EC.emergency_contact_number FROM Supervisor LEFT JOIN Emergency_Contact EC ON EC.emp_id = Supervisor.emp_id")
        supervisor_list = cursor.fetchall()

    emp_id = None
    if requests.method == 'POST':
        if 'employee_update' in requests.POST:
            print(requests.POST)
            emp_id = requests.POST['employee_id']
            emp_emg_contact = requests.POST['emergency_contact_number']
            update_employee(requests, emp_id, emp_emg_contact)
            return redirect('admin_control_employee')
        if 'mechanic_update' in requests.POST:
            print(requests.POST)
            emp_id = requests.POST['employee_id']
            salary = requests.POST['salary']
            expertise = requests.POST['expertise']
            update_mechanic(requests, emp_id, salary, expertise)

    context = {'employee_list': employee_list,
               'mechanic_list': mechanic_list,
               'admin_list': admin_list,
               'salesman_list': salesman_list,
               'supervisor_list': supervisor_list,
               'emp_id': emp_id}
    return render(requests, 'drauto/admin_control_employee.html', context)


def admin_control_vehicle(requests):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM DrautoshopAddb.dbo.Vehicle")
        vehicle_list = cursor.fetchall()

        cursor.execute("SELECT * FROM DrautoshopAddb.dbo.Van")
        van_list = cursor.fetchall()

        cursor.execute("SELECT * FROM DrautoshopAddb.dbo.Car")
        car_list = cursor.fetchall()

        cursor.execute("SELECT * FROM DrautoshopAddb.dbo.Four_WD")
        fwd_list = cursor.fetchall()

    if requests.method == 'POST':
        if 'vehicle_update' in requests.POST:
            print(requests.POST)
            chassis_number = requests.POST['chassis_number']
            make = requests.POST['make']
            import_price_usd = requests.POST['import_price_usd']
            car_year = requests.POST['car_year']
            markup_percent = requests.POST['markup_percent']
            colour = requests.POST['colour']
            engine_number = requests.POST['engine_number']
            model = requests.POST['model']
            car_type = requests.POST['car_type']
            condition = requests.POST['condition']
            mileage = requests.POST['mileage']
            cc_rating = requests.POST['cc_rating']
            update_vehicle(requests,chassis_number,make,import_price_usd,car_year,
                           markup_percent,colour,engine_number,model,car_type,condition,
                           mileage,cc_rating)

        if 'car_update' in requests.POST:
            car_update()



    context = {'vehicle_list': vehicle_list,
               'van_list': van_list,
               'car_list': car_list,
               'fwd_list': fwd_list,}
    return render(requests, 'drauto/admin_control_vehicle.html', context)

from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db import connection

from drauto.backend_functions import generate_cl_string, findASalesPerson, findClient
from drauto.forms import EmployeeLoginForm

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
            cursor.execute(f"""INSERT INTO DrautoshopAddb.dbo.Client_Purchase(purchase_id, client_Id, chassis_number, emp_Id, price, commission, date_sold, amt_paid, payment_method)
                                VALUES('{purchase_id}', '{client_id}', '{chassis_number}', '{emp_id}' ,'{price}','{commission}', GETDATE(), '{amount_paid}', '{payment_Method}');""")
            connection.commit()
            return redirect('drauto/vehicle.html')

    context = {'vehicle': vehicle}
    return render(requests, 'drauto/purchase.html', context)


def log_payment(requests):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO DrautoshopAddb.dbo.Client_Purchase ()")
        vehicle_list = cursor.fetchall()
        context = {
            'vehicle_list': vehicle_list,
        }


def getPrice(chassis_number):
    # cursor.execute("SELECT DrautoshopAddb.dbo.GET_VEHICLES_SELL_PRICE() WHERE chassis_number = '{chassis_number}'")
    cursor.execute(
        f"SELECT Selling_Price FROM DrautoshopAddb.dbo.GET_VEHICLE_SELL_PRICE() WHERE chassis_number = '{chassis_number}'")
    data = cursor.fetchall()

    return data[0][0]


def getDiscountPrice(chassis_number):
    cursor.execute("SELECT DrautoshopAddb.dbo.GET_DISCOUNT('{chassis_number}')")
    data = cursor.fetchall()

    return data[0][0]


def contact(requests):
    return render(requests, 'drauto/contact_page.html')


def admin_views(requests):

    with connection.cursor() as cursor:
        cursor.execute("Select * From view_sales_by_salesman")
        sales_list = cursor.fetchall()


    context = {'sales_list': sales_list}
    return render(requests, 'drauto/admin_page.html', context)

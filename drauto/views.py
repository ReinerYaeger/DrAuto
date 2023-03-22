from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db import connection
from datetime import datetime
from drauto.backend_functions import  addon_update, assign_supervisor, authenticate_staff_login, findASalesPerson, findClient, fwd_update, generate_primarykey, getDiscountPrice, getPrice, part_change_update, register_client, repair_update, \
    update_employee, update_mechanic, update_salesman, update_vehicle, car_update, authenticate_client_login, van_update
from drauto.forms import EmployeeLoginForm, EmployeeUpdateForm
from drauto.models import Employee
from django.contrib.auth.decorators import login_required
# Create your views here.
cursor = connection.cursor()


def index(requests):
    return render(requests, 'drauto/index.html')


def client_login(requests):
    
    if requests.user.is_authenticated:
        return redirect("drauto/login_register_form.html")
    page = 'login'
    template_name = 'drauto/login_register_form.html'
    redirect_authenticated_user = True

    if requests.method == 'POST':
        if 'login' in requests.POST:
            client_name = requests.POST['client_name']
            password = requests.POST['password']

            user = authenticate_client_login(requests,client_name,password)

    context = {'page': page}
    return render(requests, 'drauto/login_register_form.html', context)


def staff_login(requests):
    if requests.user.is_authenticated:
        return redirect("/")
    page = 'staff_login'

    if requests.method == 'POST':
        if 'login' in requests.POST:
            emp_name = requests.POST['emp_name']
            password = requests.POST['password']

            user = authenticate_staff_login(requests,emp_name,password)
        

    context = {'page': page}
    return render(requests, 'drauto/login_register_form.html', context)


def logout_user(requests):
    logout(requests)

    return redirect('/')


def register_form(requests):
    if requests.user.is_authenticated:
        return redirect("/")
    page = 'register'
    
    if requests.method == "POST":
        if 'register' in requests.POST:
            client_username = requests.POST['username']
            email = requests.POST['email']
            residential_address = requests.POST['residential_address']
            password = requests.POST['password']
            phonenumber = requests.POST['phonenumber']
            
            register_client(requests,client_username,email,residential_address,password,phonenumber)
    
    

    return render(requests, 'drauto/login_register_form.html', {'page': page})

def vehicle(requests):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM DrautoshopAddb.dbo.Vehicle")
        vehicle_list = cursor.fetchall()
        context = {
            'vehicle_list': vehicle_list,
        }

    return render(requests, 'drauto/vehicle.html', context)

@login_required
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
        purchase_id = generate_primarykey('PI')
        price = vehicle.get('price')
        chassis_number = vehicle.get('chassis_number')
        emp_id = findASalesPerson()
        commission = (.15*price)+ price

        # storing loging purchase

            #SQL Stored Procedure  Being Used
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

@login_required
def admin_views(requests):
    
    #SQL Views
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
        
        cursor.execute(f"""SELECT wd.work_done_id, wd.emp_id, wd.hrs_worked,
                            A.addOn_description, A.cost,
                            P.part_name, P.part_description, P.cost AS part_cost,
                            R.repair_description, R.cost AS repair_cost
                                FROM Work_Done wd
                                LEFT JOIN Add_On A ON wd.work_done_id = A.work_done_id
                                LEFT JOIN Parts_Changed P ON wd.work_done_id = P.work_done_id
                                LEFT JOIN Repair R ON wd.work_done_id = R.work_done_id;""")
        work_done_list = cursor.fetchall()
        print(work_done_list)
        
        cursor.execute("EXEC get_top_selling_make")
        top_selling_list = cursor.fetchall()
        print(top_selling_list)
        
        cursor.execute("EXEC sp_GetEmployeePerformance")
        emp_performance = cursor.fetchall()
        print(emp_performance)

    context = {'sales_list': sales_list,
               'commission_list': commission_list,
               'client_purchase_list': client_purchase_list,
               'salesman_purchase_list': salesman_purchase_list,
               'invoice_list': invoice_list, 
               "work_done_list":work_done_list,
               "top_selling_list":top_selling_list,
               "emp_performance":emp_performance,}

    print(context)
    return render(requests, 'drauto/admin_page.html', context)


def services(requests):
    return render(requests, 'drauto/services.html')


#security
@login_required
def client_purchase(requests,client_name):
    #Using Sql View
    
    print(client_name)
    
    with connection.cursor() as cursor:
        cursor.execute(f"Select * From view_invoice Where client_name = '{client_name}'")
        invoice_list = cursor.fetchall()
        for row in cursor:
            invoice_list.append(row)
            print(row)

    if requests.method == "POST":
        if 'addon_update' in requests.POST:
            
            chassis_number =  requests.POST['chassis_number']
            addon_option = requests.POST['addon_option']
            cost = requests.POST['addon_cost']
            time = requests.POST['addon_time']
            addon_update(requests,chassis_number,addon_option,cost,time)
        if 'repair_update' in requests.POST:
            chassis_number =  requests.POST['chassis_number']
            repair_option = requests.POST['repair_option']
            cost = requests.POST['repair_cost']
            time = requests.POST['repair_time']
            repair_update(requests,chassis_number,repair_option,cost,time)
        if 'part_change_update' in requests.POST:
            chassis_number =  requests.POST['chassis_number']
            part_change_option = requests.POST['part_change_option']
            cost = requests.POST['part_change_cost']
            time = requests.POST['part_change_time']
            part_change_update(requests,chassis_number,part_change_option,cost,time)
        

    context = {'invoice_list': invoice_list}
    
    print("Last print ")
    print(invoice_list)
    return render(requests, 'drauto/client_purchase.html', context)

#security
@login_required
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
        print(supervisor_list)
        

    if requests.method == 'POST':
        if 'employee_update' in requests.POST:
            print(requests.POST)
            # emp_id = requests.POST['emp_id']
            emp_emg_contact = requests.POST['emergency_contact_number']
            emp_name =   requests.POST['emp_name']
            dob =  requests.POST['dob']
            password_hash = requests.POST['password_hash']
            update_employee(requests,emp_name,dob, emp_emg_contact,password_hash)
            return redirect('admin_control_employee')
        
        if 'assign_supervisor' in requests.POST:
            print(requests.POST)
            emp_id = requests.POST['employee_id']
            assign_supervisor(requests,emp_id)
            
        
        if 'mechanic_update' in requests.POST:
            print(requests.POST)
            emp_id = requests.POST['employee_id']
            salary = requests.POST['salary']
            expertise = requests.POST['expertise']
            update_mechanic(requests, emp_id, salary, expertise)
        if 'salesman_update' in requests.POST:
            print(requests.POST)
            emp_id = requests.POST['employee_id']
            travel_subsistence = requests.POST['travel_subsistence']
            update_salesman(requests,emp_id,travel_subsistence)
            

    context = {'employee_list': employee_list,
               'mechanic_list': mechanic_list,
               'admin_list': admin_list,
               'salesman_list': salesman_list,
               'supervisor_list': supervisor_list,
               #'emp_id': emp_id,
               }
    return render(requests, 'drauto/admin_control_employee.html', context)

#security
@login_required
def admin_control_vehicle(requests, emp_name):
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
            update_vehicle(requests, chassis_number, make, import_price_usd, car_year,
                           markup_percent, colour, engine_number, model, car_type, condition,
                           mileage, cc_rating,emp_name)

        if 'car_update' in requests.POST:
            chassis_number = requests.POST['chassis_number']
            seating_capacity = requests.POST['seating_capacity']
            car_update(chassis_number,seating_capacity)
            
        if 'fwd_update' in requests.POST:
            chassis_number = requests.POST['chassis_number']
            vehicle_size = requests.POST['vehicle_size']
            fuel_type = requests.POST['fuel_type']
            fwd_update(chassis_number,vehicle_size,fuel_type)
            
        if 'van_update' in requests.POST:
            chassis_number = requests.POST['chassis_number']
            haul_capacity = requests.POST['haul_capacity']
            maxlength_clearance = requests.POST['maxlength_clearance']
            van_update(chassis_number,haul_capacity,maxlength_clearance)

    context = {'vehicle_list': vehicle_list,
               'van_list': van_list,
               'car_list': car_list,
               'fwd_list': fwd_list, }
    return render(requests, 'drauto/admin_control_vehicle.html', context)

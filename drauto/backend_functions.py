from datetime import datetime
import random
import string

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render, redirect

from drauto.models import Employee, EmergencyContact


def generate_primarykey(prefix):
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return prefix + random_chars


def getEmpId(emp_name=None):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT client_id FROM Salesman WHERE emp_name = '{emp_name}'")
        connection.commit()
        return cursor.fetchone()[0]
        


def findASalesPerson(emp_id=None):
    if emp_id == None:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT TOP 1 emp_Id FROM Salesman ORDER BY NEWID()")
            connection.commit()
            return cursor.fetchone()[0]

    if emp_id is not None:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM Salesman WHERE emp_id = '{emp_id}'")
            
def findAMechanic(emp_id=None,emp_name=None):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT TOP 1 emp_Id FROM Mechanic ORDER BY NEWID()")
        connection.commit()
        return cursor.fetchone()[0]
        

def findClient(client_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT client_id FROM Client WHERE client_name = '{client_name}'")
        connection.commit()
        return cursor.fetchone()[0]


def getPrice(chassis_number):
    # cursor.execute("SELECT DrautoshopAddb.dbo.GET_VEHICLES_SELL_PRICE() WHERE chassis_number = '{chassis_number}'")
    
    #SQL Function Being Used 
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT Selling_Price FROM DrautoshopAddb.dbo.GET_VEHICLE_SELL_PRICE() WHERE chassis_number = '{chassis_number}'")
        data = cursor.fetchall()

        return data[0][0]


def getDiscountPrice(chassis_number):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT DrautoshopAddb.dbo.GET_DISCOUNT('{chassis_number}')")
        data = cursor.fetchall()

        return data[0][0]



######## Update Employess
def update_employee(requests,emp_name,dob, emp_emg_contact,password_hash,emp_id=None):
    
    with connection.cursor() as cursor:
        emp_id = generate_primarykey('EM')
        cursor.execute(f"""INSERT INTO DrautoshopAddb.dbo.Employee
                            (emp_Id, emp_name, date_employed, dob, password_hash)
                            VALUES('{emp_id}', '{emp_name}', GETDATE(), '{dob}', '{password_hash}');""")
        connection.commit()

        cursor.execute(
            f"""INSERT INTO DrautoshopAddb.dbo.Emergency_Contact(emergency_contact_number, emp_Id) VALUES('{emp_emg_contact}', '{emp_id}');""")
        connection.commit()
    return redirect('/')


def assign_supervisor(requests,emp_id):
    
    #Using sp stored Procedure from SQL
    with connection.cursor() as cursor:
        cursor.execute(f""" EXEC DrautoshopAddb.dbo.sp_AssignAsSupervisor '{emp_id}'""")
        connection.commit()
    return redirect('drauto/admin_control_employee')


def update_mechanic(requests, emp_id, salary, expertise):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM DrautoshopAddb.dbo.Mechanic WHERE emp_Id='{emp_id}'")
        record = cursor.fetchone()
        cursor.execute(f"SELECT * FROM DrautoshopAddb.dbo.Employee WHERE emp_Id='{emp_id}'")
        record2 = cursor.fetchone()

        if record:
            # Record exists, so update it
            cursor.execute(
                f"UPDATE DrautoshopAddb.dbo.Mechanic SET salary={salary}, expertise='{expertise}' WHERE emp_Id='{emp_id}'; ")
            connection.commit()
        elif record2:
            # Record doesn't exist, so insert it
            cursor.execute(
                f"INSERT INTO DrautoshopAddb.dbo.Mechanic (emp_Id, salary, expertise) VALUES ('{emp_id}', {salary}, '{expertise}');")
            connection.commit()
    return redirect('/')


def update_salesman(requests,emp_id,travel_subsistence):
    #Using SQL sp Stored Procedure
    
    with connection.cursor() as cursor:
        
        cursor.execute(f"SELECT * FROM DrautoshopAddb.dbo.Salesman WHERE emp_Id='{emp_id}'")
        record = cursor.fetchone()
        cursor.execute(f"SELECT * FROM DrautoshopAddb.dbo.Employee WHERE emp_Id='{emp_id}'")
        record2 = cursor.fetchone()
        
        if record:
            cursor.execute(f"""EXEC DrautoshopAddb.dbo.sp_IncreaseTravelSub 
                            '{emp_id}',
                            '{travel_subsistence}' """)
            connection.commit()
        elif record2:
            cursor.execute(f"""INSERT INTO DrautoshopAddb.dbo.Salesman
                                (emp_Id, travel_subsistence)
                                VALUES('{emp_id}', {travel_subsistence});""")
    return redirect('/')




         
######## Update Vechiles 
def update_vehicle(requests, chassis_number, make, import_price_usd, car_year,
                   markup_percent, colour, engine_number, model, car_type, condition,
                   mileage, cc_rating,emp_name):
    
    print(import_price_usd)
    with connection.cursor() as cursor:
        cursor.execute(
            f""" SELECT chassis_number FROM DrautoshopAddb.dbo.Vehicle WHERE  chassis_number = '{chassis_number}'""")
        record = cursor.fetchone()

        if record:
            query = (f"""UPDATE DrautoshopAddb.dbo.Vehicle
                                                       SET make='{make}', import_price_usd={import_price_usd}, car_year='{car_year}', markup_percent={markup_percent}, colour='{colour}', 
                                                       engine_number='{engine_number}', model='{model}', car_type='{car_type}', [condition]='{condition}', mileage={mileage}, cc_rating='{cc_rating}'
                                                       WHERE chassis_number='{chassis_number}';""")
            cursor.execute(query)
            connection.commit()
        else:
            query = (f"""INSERT INTO DrautoshopAddb.dbo.Vehicle
                    (chassis_number, make, import_price_usd, car_year, markup_percent, colour, engine_number,
                    model, car_type, condition, mileage, cc_rating, isSold) 
                    VALUES('{chassis_number}', '{make}', {import_price_usd}, '{car_year}', {markup_percent},
                    '{colour}', '{engine_number}', '{model}', '{car_type}', '{condition}', {mileage}, '{cc_rating}', 0);""")
            cursor.execute(query)
            
            
            # cursor.execute(f""""INSERT INTO DrautoshopAddb.dbo.Vehicle
            #                                        (chassis_number, make, import_price_usd, car_year, markup_percent, colour, engine_number,
            #                                         model, car_type, condition, mileage, cc_rating, isSold)
            #                                        VALUES('{chassis_number}', '{make}', {import_price_usd}, '{car_year}', {markup_percent},
            #                                         '{colour}', '{engine_number}', '{model}', '{car_type}', '{condition}', {mileage}, '{cc_rating}', 0);""")
            connection.commit()
            emp_id = getEmpId(emp_name)
            
            #Using Sql sp stored procedure And Transcation
            if markup_percent < 0:
                value = import_price_usd * markup_percent
            cursor.execute(f"""EXEC DrautoshopAddb.dbo.sp_INSERT_EMP_PURCHASE
                           '{chassis_number}', '{emp_id}', GETDATE(), '{value}', '{import_price_usd}' """)
            connection.commit()
            return redirect('/')

    return redirect('/')


def car_update(requests):
    return redirect('/')


#### WORK Done Functions

def addon_update(requests,chassis_number,addon_option,cost,time):
    
    mech_emp_id = findAMechanic()
    work_id = generate_primarykey('WD')
    with connection.cursor() as cursor:        
        cursor.execute(f"""INSERT INTO Work_Done (work_done_id, emp_Id, hrs_worked) 
                       Values ('{work_id}','{mech_emp_id}',{time})""")
        connection.commit()
        
        cursor.execute(f"""INSERT INTO Add_on (work_done_id, addOn_description ,cost) 
                       Values ('{work_id}','{addon_option}',{cost})""")
        connection.commit()
    return redirect("/")


def repair_update(requests,chassis_number,repair_option,cost,time):
    mech_emp_id = findAMechanic()
    work_id = generate_primarykey('WD')
    with connection.cursor() as cursor:        
        cursor.execute(f"""INSERT INTO Work_Done (work_done_id, emp_Id, hrs_worked) 
                       Values ('{work_id}','{mech_emp_id}',{time})""")
        connection.commit()
        
        cursor.execute(f"""INSERT INTO Repair (work_done_id, repair_description ,cost) 
                       Values ('{work_id}','{repair_option}',{cost})""")
        connection.commit()
    return redirect("/")
    


def part_change_update(requests,chassis_number,part_change_option,cost,time):
    mech_emp_id = findAMechanic()
    work_id = generate_primarykey('WD')
    with connection.cursor() as cursor:        
        cursor.execute(f"""INSERT INTO Work_Done (work_done_id, emp_Id, hrs_worked) 
                       Values ('{work_id}','{mech_emp_id}',{time})""")
        connection.commit()
        
        cursor.execute(f"""INSERT INTO Parts_Changed (work_done_id, part_name ,cost) 
                       Values ('{work_id}','{part_change_option}',{cost})""")
        connection.commit()
    return redirect("/")

def authenticate_client_login(requests, client_name, password):
    
    #SQL Function Being Used
    with connection.cursor() as cursor:
        cursor.execute("SELECT dbo.ValidateLogin(%s, %s, 'C')", (client_name, password))
        result = cursor.fetchone()[0]
        if result == 1:
            if not User.objects.filter(username=client_name).exists():
                user = User.objects.create_user(username=client_name, password=password)
            else:
                user = User.objects.get(username=client_name)
            
            login(requests, user)
        requests.session['is_authenticated'] = True
        requests.session['client_name'] = client_name
        requests.session.save()
    return redirect('/')
    # Don't reveal whether the user exists or not
    return HttpResponse("Invalid username or password", status=401)


def authenticate_staff_login(requests,emp_name,password):
    #SQL Function Being Used
    with connection.cursor() as cursor:
        cursor.execute("SELECT dbo.ValidateLogin(%s, %s, 'E')", (emp_name, password))
        result = cursor.fetchone()[0]
        if result == 1:
            if not User.objects.filter(username=emp_name).exists():
                user = User.objects.create_superuser(username=emp_name, password=password)
            else:
                user = User.objects.get(username=emp_name)
            
            login(requests, user)
        else:
            print("User not Present ")
        requests.session['is_authenticated'] = True
        requests.session['emp_name'] = emp_name
        requests.session.save()
    return redirect('/')


def register_client(requests,client_name,email,residential_address,password,phonenumber):
    
    #SQL Stored Procedure Being Used
    #  with connection.cursor() as cursor:
         
    #      stored_proc = """EXEC [dbo].[sp_AddClient] @client_Id=?,
    #                                                 @client_name=?,
    #                                                 @email=?
    #                                                 @residential_address=?
    #                                                 @phone_number=?"""
        
    #     params = (client_name,email,residential_address,password,phonenumber)
        
    #     cursor.execute(stored_proc,)
    with connection.cursor() as cursor:
        client_id = generate_primarykey("CL")
        cursor.execute(f"""EXEC sp_AddClient '{client_id}','{client_name}','{email}',
                        '{residential_address}','{password}',
                        '{phonenumber}' """)
            
    if not User.objects.filter(username=client_name).exists():
        user = User.objects.create_user(username=client_name, password=password)
        login(requests,user)
    else:
        print("User Already present")
    
    return redirect("/")

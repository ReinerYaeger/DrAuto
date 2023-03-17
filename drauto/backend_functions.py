import random
import string
from django.db import connection


def generate_cl_string(prefix):
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return prefix + random_chars


def findASalesPerson(emp_id=None):
    if emp_id == None:
        with connection.cursor() as cursor:
            cursor.execute("SELECT TOP 1 emp_Id FROM Salesman ORDER BY NEWID()")
            connection.commit()
            return cursor.fetchone()[0]

    if emp_id is not None:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM Salesman WHERE emp_id = '{emp_id}'")
            connection.commit()
            return cursor.fetchone()[0]

def findClient(client_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT client_id FROM Client WHERE client_name = '{client_name}'")
        connection.commit()
        return cursor.fetchone()[0]



from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import Employee


class EmployeeLoginForm(forms.Form):
    emp_name = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        emp_name = self.cleaned_data.get('emp_name')
        password = self.cleaned_data.get('password')

        if emp_name and password:
            employee = Employee.objects.filter(emp_name=emp_name).first()
            if not employee:
                raise forms.ValidationError('Invalid username or password')
            if not employee.check_password(password):
                raise forms.ValidationError('Invalid username or password')
        return super().clean()


class EmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['emp_name', 'date_employed', 'dob']
        labels = {
            'emp_name': 'Employee Name',
            'date_employed': 'Date Employed',
            'dob': 'Date of Birth',
        }
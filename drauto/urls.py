from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('client_login/', views.client_login, name='client_login'),
    path('staff_login/', views.staff_login, name='staff_login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_form, name='register'),
    path('contact/', views.contact, name='contact'),
    path('services/',views.services, name='services'),
    path('client_purchase/', views.client_purchase, name='client_purchase'),
    # path('client_purchase/<str:client_name>', views.client_purchase, name='client_purchase'),

    path('vehicle/', views.vehicle, name='vehicle'),
    path('vehicle/purchase/<str:vehicle_id>/', views.purchase, name='purchase'),
    # path('vehicle/purchase/<str:')

    path('admin_views/',views.admin_views,name='admin_views'),
    path('admin_control/', views.admin_control_employee, name='admin_control'),
    path('admin_control/employee', views.admin_control_employee, name='admin_control_employee'),
    path('admin_control/vehicle', views.admin_control_vehicle, name='admin_control_vehicle'),

    #path('admin_control/update_employee/<str:emp_id>', views.update_employee, name='update_employee'),

    # path('admin_control/update_employee/<str:emp_id>',views.update_employee,name='update_employee'),
    # path('admin_control/update_employee/<str:emp_id>',views.update_employee,name='update_employee'),
    # path('admin_control/update_employee/<str:emp_id>',views.update_employee,name='update_employee'),
    # path('admin_control/update_employee/<str:emp_id>',views.update_employee,name='update_employee'),


]
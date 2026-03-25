from django.urls import path
from . import views
urlpatterns = [
    path('', views.AdminLogin , name='adminlogin') , 
    path('adminhome/' , views.AdminHome , name='AdminHome'),
    path('users_view/' , views.User_View , name='User_View'),
    path('activate_user/<int:id>' , views.ActivateUser , name='ActivateUser'),
    path('Delete_User/<int:id>' , views.DeleteUser , name='DeleteUser')
]
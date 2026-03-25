from django.shortcuts import render , redirect
from django.contrib import messages
from User.models import User_SigUp


# Create your views here.
def AdminLogin(request):
    if request.method=='POST':
        name= request.POST.get('name')
        password = request.POST.get('password')
        print(name and password)
        if name=='admin' and password=='admin':
            return redirect('AdminHome')
        else:
            messages.error(request , 'Invalid Credentails! --Login with Proper Details--')
        

    return render(request , 'AdminLogin.html')

def AdminHome(request):
    return render(request , 'Admins/AdminHome.html')


def User_View(request):
    users = User_SigUp.objects.all()
    return render(request , 'Admins/User_View.html' , {'users':users})


def ActivateUser(request , id):
    user = User_SigUp.objects.get(id=id)
    if user.Status=='waiting':
     user.Status='active'
     user.save()
    return redirect('User_View')

def DeleteUser(request , id):
    user = User_SigUp.objects.get(id=id)
    if user:
        user.delete()
    return redirect('User_View')
  


    
       
from django import forms

from .models import User_SigUp

class User_SigupForm(forms.ModelForm):
    Name = forms.CharField(widget=(forms.TextInput(
                      attrs={'class':'form-control' , 
                       'placeholder':'Name' ,
                       'autocomplete' :'off', 
                       'title':'Only Alphabets' ,
                        'pattern':'[a-zA-Z]*' })),max_length=100)

    Address = forms.CharField(widget=(forms.TextInput(
                attrs={'class':'form-control' , 
                       'placeholder':'Address' ,
                       'autocomplete' :'off',                          
                         }))   ,max_length=100)
    
    Mobile = forms.CharField( widget=(forms.TextInput(
                attrs={'class':'form-control' , 
                       'placeholder':'Mobile' ,
                       'autocomplete' :'off', 
                       'title':'Only Numbers',
                        'patten':'[56789][0-9]{9}' } ) ),max_length=100)
    
    Email = forms.EmailField(widget=(forms.EmailInput(
                attrs={'class':'form-control' , 
                       'placeholder':'Email' ,
                       'autocomplete' :'off',
                        'title':'Enter Valid Email',
                        'patten':'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$' } )),max_length=100)
    
    Username = forms.CharField(widget=(forms.TextInput(
                attrs={'class':'form-control' ,
                        'placeholder':'Username' ,
                        'autocomplete' :'off', 
                        'title':'Only Alphabets' , 
                        'pattern':'[a-zA-Z]*' } ) ),max_length=100)
    
    Password = forms.CharField(widget=(forms.PasswordInput(
                   attrs={'class':'form-control' , 'placeholder':'Password' ,'autocomplete' :'off',
                        'title':'Must contain at least one number and one uppercase and lowercase letter, and at least 8 or more characters'
                          ,'patten': '(?=.\d)(?=.[a-z])(?=.*[A-Z]).{8,}' }
                          )),max_length=100)
    
    Status = forms.CharField(widget=(forms.HiddenInput(
        attrs={'class':'form-control' ,
                'placeholder':'Status' ,
                'autocomplete' :'off' })),max_length=100 , initial='waiting')

    class Meta:
        model = User_SigUp
        fields = '__all__'




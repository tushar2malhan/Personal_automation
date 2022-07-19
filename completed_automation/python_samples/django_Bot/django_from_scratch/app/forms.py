from .models import Queries

from django.forms import  ModelForm
from django import forms

class Myform(ModelForm):

    class Meta:
        model = Queries
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mention Your greetings'}),
        }
    

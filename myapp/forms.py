from django import forms

class ComplaintForm(forms.Form):
    complaint = forms.CharField(label='Enter your complaint', max_length=255)

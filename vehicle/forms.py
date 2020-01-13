from django import forms
from datetime import date
from dateutil.relativedelta import relativedelta
import datetime

# REGISTER FORM
class RegisterForm(forms.Form):
    # Get max birth date
    # Minimum age requirement in UK to drive a car is 17 years - https://www.1driver.co.uk/minimum-age-requirement.html
    maxBirthDate = date.today() - relativedelta(years=17)
    maxBirthDate = maxBirthDate.strftime("%Y-%m-%d")
    # First name
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'name': 'first_name', 'id': 'first_name',
               'placeholder': 'First Name', 'required': 'true'}))
    # Last name
    last_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'name': 'last_name', 'id': 'last_name',
               'placeholder': 'Last Name', 'required': 'true'}))
    # E-mail Address
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'name': 'email', 'id': 'email',
               'placeholder': 'E-mail Address', 'required': 'true'}))
    # Birthdate
    birth = forms.DateField(widget=forms.DateInput(
        attrs={'class': 'form-control', 'name': 'birth', 'id': 'birth', 'type': 'date',
               'value': maxBirthDate, 'max': maxBirthDate, 'min': '1910-01-01', 'required': 'true'}))
    #  Username
    username = forms.CharField(min_length=4, max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control', 'name': 'username', 'id': 'username',
               'placeholder': 'Username', 'required': 'true'}))
    # Password
    password = forms.CharField(min_length=8, max_length=15, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'name': 'password', 'id': 'password',
               'placeholder': 'Password', 'required': 'true'}))


# LOGIN FORM
class LoginForm(forms.Form):
    # Username
    username = forms.CharField(min_length=4, max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control', 'name': 'username', 'id': 'username',
               'placeholder': 'Username', 'required': 'true', 'autofocus': 'true'}))
    # Password
    password = forms.CharField(min_length=6, max_length=15, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'name': 'password', 'id': 'password',
               'placeholder': 'Password', 'required': 'true'}))


# BoOOKING FORM
class BookingForm(forms.Form):
    # Get today's date and tomorrow's date
    today = date.today()
    tomorrow = today + relativedelta(days=1)
    # Ensure form displays tomorrow's date if current time > 17
    now = datetime.datetime.now()
    if now.hour > 17:
        today = tomorrow
        tomorrow = today + relativedelta(days=1)
    # Time choices
    CHOICES = (
        ('8', '8:00'), ('9', '9:00'), ('10', '10:00'), ('11', '11:00'), ('12', '12:00'),
        ('13', '13:00'), ('14', '14:00'), ('15', '15:00'), ('16', '16:00'), ('17', '17:00'), ('18', '18:00')
    )
    # From date
    from_date = forms.DateField(widget=forms.DateInput(
        attrs={'class': 'form-control', 'name': 'from_date', 'id': 'from_date', 'type': 'date',
               'value': today, 'min': today, 'required': 'true'}))
    # From time
    from_time = forms.ChoiceField(choices=CHOICES, widget=forms.Select(
        attrs={'class': 'form-control', 'name': 'from_time', 'id': 'from_time', 'required': 'true'}))
    # To date
    to_date = forms.DateField(widget=forms.DateInput(
        attrs={'class': 'form-control', 'name': 'to_date', 'id': 'to_date', 'type': 'date',
               'value': tomorrow, 'min': today, 'required': 'true'}))
    # To time
    to_time = forms.ChoiceField(choices=CHOICES, widget=forms.Select(
        attrs={'class': 'form-control', 'name': 'to_time', 'id': 'to_time', 'required': 'true'}))
from django import forms
from django.core import validators
from markdownx.fields import MarkdownxFormField, MarkdownxWidget
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordResetForm, SetPasswordForm, UserChangeForm,
)
from django.db.models import Q
from .models import User, Blog, Comment
from groups.models import Group
import re

class RegistrationForm(forms.Form):

    first_name = forms.CharField(
        label='First Name', max_length=100, required=False, 
        validators=[validators.RegexValidator(r'^[a-zA-Z]*$', 'Only Alphabets are allowed.')],
        widget=forms.TextInput(attrs={'id': 'fname', 'placeholder': 'Enter First Name'})
    )
    last_name = forms.CharField(
        label="Last Name", max_length=100, required=False, 
        validators=[validators.RegexValidator(r'^[a-zA-Z]*$', 'Only Alphabets are allowed.')],
        widget=forms.TextInput(attrs={'id': 'lname', 'placeholder':'Enter Last Name'})
    )
    username = forms.CharField(
        label='Username', max_length=100, 
        validators=[
            validators.MinLengthValidator(5,'Username must be at least 5 characters long.'),
            validators.RegexValidator(r'^[^\W_](\w)*$', 'Username should not start with a special character.')
        ],
        widget=forms.TextInput(attrs={'id': 'uname', 'placeholder':'Enter Username'})
    )
    email = forms.EmailField(
        label='Email', 
        widget=forms.EmailInput(attrs={'id': 'email', 'placeholder':'Enter Email'})
    )
    password = forms.CharField(
        label='Password', validators=[validators.MinLengthValidator(8,'Password must be at least 8 characters long.')],
        widget=forms.PasswordInput(attrs={'id': 'pass1', 'placeholder':'Enter Password'})
    )
    confirm_password = forms.CharField(
        label='Confirm password', 
        widget=forms.PasswordInput(attrs={'id': 'pass2', 'placeholder':'Confirm Password'})
    )

    def clean_password(self):
        data = self.cleaned_data['password']
        if not any(char.isupper() for char in data):
            raise forms.ValidationError('Password must contain at least one uppercase letter.')
        if not any(char.islower() for char in data):
            raise forms.ValidationError('Password must contain at least one lowercase letter.')
        if not any(char.isdigit() for char in data):
            raise forms.ValidationError('Password must contain at least one digit.')
        if not re.search('[^A-Za-z0-9]', data):
            raise forms.ValidationError('Password must contain at least one special character.')
        return data
    
    def clean_username(self):
        data = self.cleaned_data['username']
        if User.objects.filter(username=data).exists():
            raise forms.ValidationError('Username already taken.')
        return data
    
    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already exists.')
        return data

    def clean(self):
        cleaned_data = super().clean()
        if 'password' in cleaned_data and cleaned_data['password'] != cleaned_data['confirm_password']:
            raise forms.ValidationError("Passwords don't match.")
        return cleaned_data


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        label='Username', max_length=100,
        widget=forms.TextInput(attrs={'id': 'uname',"class":"form-control", 'placeholder':'Enter email or username'})
    )
    password = forms.CharField(
        label='Password', 
        widget=forms.PasswordInput(attrs={'id': 'password',"class":"form-control", 'placeholder':'Enter password'})
    )
    error_messages = {
        "invalid_login": "Invalid username or password",
        "inactive": "User is not active",
    }
    
class UserModelForm(forms.ModelForm):
    """Registration Form"""
    class Meta:
        model = User
        fields = ["first_name","last_name","email","username","password","avatar"]
        widgets = {
            "first_name":forms.TextInput(attrs={"id":"fname","class":"form-control", "placeholder":"Enter First Name"}),
            "last_name":forms.TextInput(attrs={"id":"lname","class":"form-control", "placeholder":"Enter Last Name"}),
            "email":forms.EmailInput(attrs={"id":"email","class":"form-control", "placeholder":"Enter Email"}),
            "username":forms.TextInput(attrs={"id":"uname","class":"form-control", "placeholder":"Enter Username"}),
            "password":forms.PasswordInput(attrs={"id":"pass1","class":"form-control", "placeholder":"Enter Password"}),
            "avatar":forms.FileInput(attrs={"id":"avatar",}),
        }
    
    confirm_password = forms.CharField(
        label="Confirm Password",widget=forms.PasswordInput(attrs={'id':'pass2',"class":"form-control",'placeholder':'Confirm Password'})
    )

        
    def clean_password(self):
        data = self.cleaned_data['password']
        if len(data) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        if not any(char.isupper() for char in data):
            raise forms.ValidationError('Password must contain at least one uppercase letter.')
        if not any(char.islower() for char in data):
            raise forms.ValidationError('Password must contain at least one lowercase letter.')
        if not any(char.isdigit() for char in data):
            raise forms.ValidationError('Password must contain at least one digit.')
        if not re.search('[^A-Za-z0-9]', data):
            raise forms.ValidationError('Password must contain at least one special character.')
        return data

    def clean_username(self):
        data = self.cleaned_data['username']
        if User.objects.filter(username=data).exists():
            raise forms.ValidationError('Username already taken.')
        return data
    
    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already exists.')
        return data
    
    def clean(self):
        cleaned_data = super().clean()
        if 'password' in cleaned_data and cleaned_data['password'] != cleaned_data['confirm_password']:
            raise forms.ValidationError("Passwords don't match.")
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user
    

class EditUserProfileForm(UserChangeForm):
    
    class Meta:
        model = User
        fields = ["first_name","last_name","email","username","avatar"]
        widgets = {
            "first_name":forms.TextInput(attrs={"id":"userfname","class":"form-control", "placeholder":"Enter First Name"}),
            "last_name":forms.TextInput(attrs={"id":"userlname","class":"form-control", "placeholder":"Enter Last Name"}),
            "email":forms.EmailInput(attrs={"id":"useremail","class":"form-control", "placeholder":"Enter Email"}),
            "username":forms.TextInput(attrs={"id":"username","class":"form-control", "placeholder":"Enter Username"}),
            "avatar":forms.FileInput(attrs={"id":"avatar",}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EditUserProfileForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            self.fields['username'].initial = self.user.username
            self.fields['avatar'].initial = self.user.avatar

    
    def clean_username(self):
        data = self.cleaned_data['username']
        user = User.objects.filter(username=data).exists()
        if user and data != self.user.username:
            raise forms.ValidationError('Username already taken.')
        return data
    
    def clean_email(self):
        data = self.cleaned_data['email']
        user = User.objects.filter(email=data).exists()
        if user and data != self.user.email:
            raise forms.ValidationError('Email already exists.')
        return data
    

class CustomPasswordResetForm(PasswordResetForm):

    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control', 'placeholder': 'Enter your email'}),
    )


    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("There is no user registered with the specified email address.")
        return email

class CustomSetPasswordForm(SetPasswordForm):

    new_password1 = forms.CharField(
        label="New password",
        validators=[
            validators.MinLengthValidator(8, 'Password must be at least 8 characters long.'),
            validators.RegexValidator(
                regex=r"^(?=.*[a-z])",
                message="Password must contain at least one lowercase letter."
            ),
            validators.RegexValidator(
                regex=r"^(?=.*[A-Z])",
                message="Password must contain at least one uppercase letter."
            ),
            validators.RegexValidator(
                regex=r"^(?=.*\d)",
                message="Password must contain at least one digit."
            ),
            validators.RegexValidator(
                regex=r"^(?=.*[@$!%*?&#_])",
                message="Password must contain at least one special character."
            ),
        ],
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control','id':'pass1', 'placeholder': 'Enter new password'}),
    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control','id':'pass2','placeholder': 'Confirm new password'}),
    )
    error_messages = {
        "password_mismatch": "Passwords don't match.",
    }

class CustomPasswordChangeForm(CustomSetPasswordForm):

    old_password = forms.CharField(
        label="Old password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control','id':'old-pass', 'placeholder': 'Enter old password'}),
    )

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Incorrect password. Please enter it again.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        new_password = cleaned_data.get("new_password1")
        if old_password and new_password:
            if old_password == new_password:
                raise forms.ValidationError("New password must be different from the old password.")
        return new_password

class UserDeleteForm(forms.Form):
    confirm_delete = forms.BooleanField(required=True, label="Confirm deletion")

class BlogCreateForm(forms.ModelForm):

    class Meta:
        model = Blog
        fields = ["title", "content", "groups"]
        widgets = {
            "title":forms.TextInput(
                attrs={"id":"title","class":"form-control", "placeholder":"Enter Title"}
                ),
            "content":MarkdownxWidget(),
            "groups":forms.SelectMultiple(attrs={
                "class":"form-check-input, form-control",
                "id":"groups",
                "placeholder":"Enter Groups",
            })
        }
    
    def __init__(self, user, group=None, *args, **kwargs):
        super(BlogCreateForm, self).__init__(*args, **kwargs)
        self.fields['groups'].label = 'Groups'
        # self.fields['groups'].queryset = Group.objects.filter(members__in=[user])
        self.fields['groups'].initial = [group]
        self.user = user
    
    def save(self, commit=True):
        blog = super().save(commit=False)
        blog.author = self.user
        blog.save()            
        blog.groups.set(self.cleaned_data['groups'])
        if commit:
            blog.save()
        return blog

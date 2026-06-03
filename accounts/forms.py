from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('user', 'مستخدم عادي'),
        ('agent', 'وكيل عقاري'),
        ('developer', 'مطور عقاري'),
        ('advertiser', 'معلن'),
        ('promoter', 'مروج'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="الدور")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'phone', 'avatar', 'bio', 'company']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المستخدم'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'نبذة عنك'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم الشركة / الوكالة'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'avatar', 'bio', 'company']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
        }
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=100, required=True)
    face_image = forms.CharField(widget=forms.HiddenInput(), required=True)  # Mandatory

    class Meta:
        model = CustomUser
        fields = ("email", "name", "password1", "password2", "face_image")

    def clean_face_image(self):
        face_image = self.cleaned_data.get("face_image")
        if not face_image or face_image.strip() == '':
            raise forms.ValidationError("Face image is required for registration!")
        return face_image

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match!")
        if password1 and (len(password1) < 8 or not any(char in "!@#$%^&*" for char in password1)):
            raise forms.ValidationError("Password must be 8+ characters and include a special character!")
        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    face_image = forms.CharField(widget=forms.HiddenInput(), required=True)  # Mandatory

    def clean_face_image(self):
        face_image = self.cleaned_data.get("face_image")
        if not face_image or face_image.strip() == '':
            raise forms.ValidationError("Face image is required for login!")
        return face_image
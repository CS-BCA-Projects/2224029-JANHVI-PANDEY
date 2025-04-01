from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    face_image = forms.CharField(widget=forms.HiddenInput())  # Mandatory

    class Meta:
        model = CustomUser
        fields = ("email", "name", "password1", "password2", "face_image")

    def clean_face_image(self):
        face_image = self.cleaned_data.get("face_image")
        if not face_image:
            raise forms.ValidationError("Face image is required for registration!")
        return face_image

class LoginForm(forms.Form):  # AuthenticationForm se replace kiya, kyunki face mandatory hai
    email = forms.EmailField(label="Email")
    face_image = forms.CharField(widget=forms.HiddenInput())  # Mandatory

    def clean_face_image(self):
        face_image = self.cleaned_data.get("face_image")
        if not face_image:
            raise forms.ValidationError("Face image is required for login!")
        return face_image
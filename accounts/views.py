from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import RegisterForm, LoginForm
from .models import CustomUser, UserDocument, authenticate_face
import base64
import face_recognition
import numpy as np
import cv2

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            face_image_data = form.cleaned_data["face_image"]

            # Process Face Image
            img_data = base64.b64decode(face_image_data.split(',')[1])
            np_arr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if img is None:
                return render(request, "accounts/register.html", {"form": form, "error": "Invalid image!"})

            face_encodings = face_recognition.face_encodings(img)
            if not face_encodings:
                return render(request, "accounts/register.html", {"form": form, "error": "Face not detected!"})

            user.save()
            UserDocument.objects(email=user.email).update_one(
                set__face_encoding=face_encodings[0].tobytes(), upsert=True
            )
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            face_image_data = form.cleaned_data["face_image"]

            if authenticate_face(face_image_data, email):
                try:
                    user = CustomUser.objects.get(email=email)
                    login(request, user)
                    return redirect("home")
                except CustomUser.DoesNotExist:
                    return render(request, "accounts/login.html", {"form": form, "error": "User with this email does not exist!"})
            return render(request, "accounts/login.html", {"form": form, "error": "Face not recognized!"})
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")
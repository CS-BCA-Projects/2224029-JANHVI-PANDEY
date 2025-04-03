from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from .utils import save_face_image, verify_face
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import cv2

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        face_image_data = request.POST.get('face_image')

        if form.is_valid() and face_image_data:
            user = form.save()
            # Save face image
            save_face_image(user, face_image_data)
            # Add success message
            messages.success(request, "You are successfully registered for SnapShop! Please log in to continue.")
            return redirect('login')  # Redirect to login page
        else:
            messages.error(request, "Please correct the errors below or ensure you captured your face.")
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        face_image_data = request.POST.get('face_image')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            if face_image_data:
                # Verify face
                if verify_face(user, face_image_data):
                    login(request, user)
                    # Add success message
                    messages.success(request, "Welcome back! You are now logged in to SnapShop.")
                    return redirect('home')  # Redirect to home page
                else:
                    error = "Face verification failed. Please try again."
            else:
                error = "Please capture your face for verification."
        else:
            error = "Invalid email or password."

    return render(request, 'accounts/login.html', {'error': error})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm, LoginForm
from .utils import save_face_image, verify_face
from .models import CustomUser  # Custom model import

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        face_image_data = request.POST.get('face_image')

        print(f"[SERVER] Received POST data: {dict(request.POST)}")
        print(f"[SERVER] Received face_image_data: {face_image_data[:50] if face_image_data else 'None'}")
        if form.is_valid():
            if face_image_data:
                user = form.save()
                try:
                    save_face_image(user, face_image_data)
                    messages.success(request, "You are successfully registered for SnapShop! Please log in to continue.")
                    return redirect('accounts:login')
                except Exception as e:
                    messages.error(request, f"Error saving face image: {str(e)}")
                    print(f"[SERVER] Save face image error: {str(e)}")
            else:
                messages.error(request, "No face image captured. Please capture your face.")
                form.add_error('face_image', "Face image is required!")
                print("[SERVER] No face image data received.")
        else:
            messages.error(request, "Please correct the errors below or ensure you captured your face.")
            print("[SERVER] Form errors:", form.errors)
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        print(f"[SERVER] Received POST data in login: {dict(request.POST)}")
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            face_image_data = request.POST.get('face_image')

            print(f"[SERVER] Authenticating user: {email}, password: {password[:2]}..., face_image: {face_image_data[:50] if face_image_data else 'None'}")
            user = authenticate(request, username=email, password=password)
            if user is not None:
                print("[SERVER] User authenticated successfully.")
                if face_image_data:
                    try:
                        print("[SERVER] Verifying face...")
                        if verify_face(user, face_image_data):
                            print("[SERVER] Face verified successfully.")
                            login(request, user)
                            messages.success(request, "Welcome back! You are now logged in to SnapShop.")
                            return redirect('store:home')
                        else:
                            error = "Face verification failed. Please try again."
                            print("[SERVER] Face verification failed.")
                    except Exception as e:
                        error = f"Face verification error: {str(e)}"
                        print(f"[SERVER] Face verification exception: {str(e)}")
                else:
                    error = "Please capture your face for verification."
                    print("[SERVER] No face image data received.")
            else:
                error = "Invalid email or password."
                print("[SERVER] Authentication failed.")
        else:
            error = "Invalid form data. Please check your input."
            print("[SERVER] Login form errors:", form.errors)
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'error': error})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('accounts:login')
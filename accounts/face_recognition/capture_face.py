import face_recognition
import numpy as np
from django.core.files.base import ContentFile
import base64
from account.models import UserProfile

def save_face(user, image_data):
    """
    Save face encoding for a registered user.
    """
    image_data = base64.b64decode(image_data.split(',')[1])

    # Save image temporarily
    with open("temp.jpg", "wb") as f:
        f.write(image_data)

    input_image = face_recognition.load_image_file("temp.jpg")
    input_encodings = face_recognition.face_encodings(input_image)

    if not input_encodings:
        return False  # No face detected

    user_profile, created = UserProfile.objects.get_or_create(user=user)
    user_profile.face_encoding = input_encodings[0].tobytes()
    user_profile.save()

    return True

import face_recognition
import numpy as np
from account.models import UserProfile
import base64

def recognize_face(image_data):
    """
    Authenticate user using face recognition.
    """
    image_data = base64.b64decode(image_data.split(',')[1])

    # Save image temporarily
    with open("temp.jpg", "wb") as f:
        f.write(image_data)

    input_image = face_recognition.load_image_file("temp.jpg")
    input_encodings = face_recognition.face_encodings(input_image)

    if not input_encodings:
        return None  # No face detected

    input_encoding = input_encodings[0]

    # Check against stored faces
    for profile in UserProfile.objects.all():
        if profile.face_encoding:
            db_encoding = np.frombuffer(profile.face_encoding, dtype=np.float64)
            match = face_recognition.compare_faces([db_encoding], input_encoding)[0]
            if match:
                return profile.user  # Return matched user

    return None

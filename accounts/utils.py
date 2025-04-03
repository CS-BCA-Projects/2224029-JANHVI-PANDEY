import base64
import numpy as np
import cv2
import face_recognition
from mongoengine import DoesNotExist
from .models import UserDocument

def save_face_image(user, face_image_data):
    """
    Save the face encoding of the user to MongoDB.
    """
    try:
        # Convert Base64 to OpenCV Image
        img_data = base64.b64decode(face_image_data.split(',')[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Could not decode face image")

        # Get face encoding
        encodings = face_recognition.face_encodings(img)
        if not encodings:
            raise ValueError("No face detected in the image")

        # Save the encoding to MongoDB
        encoding = encodings[0].tobytes()  # Convert to bytes
        UserDocument.objects(email=user.email).update_one(
            set__face_encoding=encoding, upsert=True
        )
    except Exception as e:
        print(f"Error saving face image: {e}")
        raise

def verify_face(user, face_image_data):
    """
    Verify the face of the user by comparing with the stored encoding.
    """
    try:
        # Fetch the stored face encoding from MongoDB
        user_data = UserDocument.objects.get(email=user.email)
        if not user_data.face_encoding:
            return False

        known_encoding = np.frombuffer(user_data.face_encoding, dtype=np.float64)

        # Convert Base64 to OpenCV Image
        img_data = base64.b64decode(face_image_data.split(',')[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return False

        # Get face encoding of the new image
        unknown_encodings = face_recognition.face_encodings(img)
        if not unknown_encodings:
            return False

        # Compare the encodings
        result = face_recognition.compare_faces([known_encoding], unknown_encodings[0])
        return result[0]
    except DoesNotExist:
        return False
    except Exception as e:
        print(f"Face Verification Error: {e}")
        return False
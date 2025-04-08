import base64
from io import BytesIO
from PIL import Image
import numpy as np
import face_recognition
from django.core.files.base import ContentFile
from django.conf import settings
import os
from .models import UserDocument
from mongoengine.connection import get_db

def save_face_image(user, face_image_data):
    try:
        format, imgstr = face_image_data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f'face_{user.email}.{ext}')
        file_path = os.path.join(settings.MEDIA_ROOT, f'face_{user.email}.{ext}')
        os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(data.read())

        img_data = base64.b64decode(imgstr)
        input_img = Image.open(BytesIO(img_data)).convert('RGB')  # Force RGB conversion
        img_np = np.array(input_img)

        encodings = face_recognition.face_encodings(img_np)
        if encodings:
            face_encoding = encodings[0].tobytes()
            try:
                UserDocument.objects(email=user.email).update_one(
                    set__face_encoding=face_encoding,
                    upsert=True
                )
                print(f"[SERVER] Saved face encoding for {user.email}, length: {len(face_encoding)}")
            except Exception as e:
                print(f"[SERVER] Index conflict or error during save: {str(e)}")
                db = get_db()
                try:
                    db['UserDocument'].drop_index("email_1")
                    print("[SERVER] Dropped conflicting index 'email_1'")
                except Exception as drop_err:
                    print(f"[SERVER] Failed to drop index: {str(drop_err)}")
                UserDocument.objects(email=user.email).update_one(
                    set__face_encoding=face_encoding,
                    upsert=True
                )
                print(f"[SERVER] Recreated index and saved face encoding for {user.email}, length: {len(face_encoding)}")
            return True
        else:
            print("[SERVER] No face detected in the image during registration.")
            raise Exception("No face detected in the image during registration.")
    except Exception as e:
        print(f"[SERVER] Failed to save image: {str(e)}")
        raise Exception(f"Failed to save image: {str(e)}")

def verify_face(user, face_image_data):
    try:
        print(f"[SERVER] Verifying face for user: {user.email}")
        user_doc = UserDocument.objects(email=user.email).first()
        if not user_doc or not user_doc.face_encoding:
            print("[SERVER] No face encoding found in MongoDB for this user.")
            return False

        saved_encoding = np.frombuffer(user_doc.face_encoding, dtype=np.float64)
        print(f"[SERVER] Loaded saved encoding, length: {len(saved_encoding)}")

        format, imgstr = face_image_data.split(';base64,')
        img_data = base64.b64decode(imgstr)
        input_img = Image.open(BytesIO(img_data)).convert('RGB')  # Force RGB conversion
        input_img_np = np.array(input_img)
        input_encodings = face_recognition.face_encodings(input_img_np)
        if input_encodings:
            input_encoding = input_encodings[0]
            print(f"[SERVER] Detected input encoding, length: {len(input_encoding)}")
            results = face_recognition.compare_faces([saved_encoding], input_encoding)
            print(f"[SERVER] Face recognition result: {results[0]}")
            return results[0]
        else:
            print("[SERVER] No face detected in the input image.")
            return False
    except Exception as e:
        print(f"[SERVER] Verification failed with exception: {str(e)}")
        raise Exception(f"Verification failed: {str(e)}")
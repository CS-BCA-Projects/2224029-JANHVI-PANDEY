from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.conf import settings
import face_recognition
import numpy as np
import base64
import cv2
from mongoengine import Document, StringField, BinaryField, connect, DoesNotExist

# MongoDB Connection
connect(db="ecommerce_db", host=settings.MONGO_URI)

# MongoDB User Document
class UserDocument(Document):
    email = StringField(required=True, unique=True)
    name = StringField()
    face_encoding = BinaryField()  # Renamed for clarity

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email field is required")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Save to MongoDB
        UserDocument(email=email, name=extra_fields.get("name")).save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name="customuser_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            UserDocument.objects(email=self.email).update_one(
                set__name=self.name, upsert=True
            )
        except Exception as e:
            print(f"MongoDB Sync Error: {e}")

    def __str__(self):
        return self.email

# Face Recognition Authentication
def authenticate_face(face_image_base64, email):
    try:
        user_data = UserDocument.objects.get(email=email)
        if not user_data.face_encoding:
            return False

        known_encoding = np.frombuffer(user_data.face_encoding, dtype=np.float64)

        # Convert Base64 to OpenCV Image
        img_data = base64.b64decode(face_image_base64.split(',')[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return False

        unknown_encodings = face_recognition.face_encodings(img)
        if not unknown_encodings:
            return False

        result = face_recognition.compare_faces([known_encoding], unknown_encodings[0])
        return result[0]
    except DoesNotExist:
        return False
    except Exception as e:
        print(f"Face Auth Error: {e}")
        return False
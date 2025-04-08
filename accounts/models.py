from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.conf import settings
from mongoengine import Document, StringField, BinaryField, connect

# MongoDB Connection
connect(db="ecommerce_db", host=settings.MONGO_URI)

# MongoDB User Document
class UserDocument(Document):
    email = StringField(required=True, unique=True)
    name = StringField(max_length=255)  # Added name field
    face_encoding = BinaryField()

    meta = {
        'indexes': [
            {'fields': ['email'], 'unique': True, 'hidden': False}
        ]
    }
    
# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)

        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Sync with MongoDB
        UserDocument.objects(email=email).update_one(
            set__email=email,
            set__name=name,  # Sync name field
            upsert=True
        )
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, name, password, **extra_fields)

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
                set__email=self.email,
                set__name=self.name,  # Sync name field
                upsert=True
            )
        except Exception as e:
            print(f"MongoDB Sync Error: {e}")

    def __str__(self):
        return self.email
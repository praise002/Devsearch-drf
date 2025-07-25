from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError


from apps.common.manager import GetOrNoneManager

class CustomUserManager(BaseUserManager, GetOrNoneManager):
    # username_field + required_fields
    def create_user(self, first_name, last_name, email, password, **extra_fields): 
        if not (first_name and last_name) :
            raise ValidationError("You must submit a first_name and a last_name")
        
        user = self.model(
            first_name=first_name, last_name=last_name, email=email, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, first_name, last_name, email, password, **extra_fields): 
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        
        if extra_fields.get("is_staff") == False:
            raise ValidationError("Super users must have is_staff set to True")
        
        if extra_fields.get("is_superuser") == False:
            raise ValidationError("Super users must have is_superuser set to True")
        
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            **extra_fields
        )
        return user
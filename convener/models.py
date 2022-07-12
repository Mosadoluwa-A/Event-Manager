from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users require an email field')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        print(f"The type of the new user is {type(user)}")
        if password is None:
            import string
            letters = string.ascii_letters
            digits = string.digits
            symbols = string.punctuation
            pass_chars = letters + digits + symbols
            print(f"The length of the characters is {len(pass_chars)}")
            password = self.make_random_password(10, pass_chars)
            print(f"The password of the new user is {password}")
        user.set_password(password)
        user.save(using=self._db)
        subject = "Your Login Details"
        msg = f'''
               Your password is {password}
            Please verify your email via this link: 
            '''
        user.email_user(subject, msg)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def get_or_create_user(self, email):
        try:
            print(f"The email is {email}")
            user = self.model.objects.get(email=email)
            if user:
                print(f"The user is {user.email}")
            else:
                print("This user does not exist")
                user = self.create_user(email)
                print(f"The New user is {user.email}")
        except Exception as e:
            print(e)
        else:
            return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class Convener(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    class Meta:
        verbose_name = _('convener')


class Event(models.Model):
    name = models.CharField(max_length=100)
    convener = models.ForeignKey(Convener, on_delete=models.SET_NULL, null=True, related_name="events")
    location = models.TextField()
    total_mrun_slots = models.IntegerField(verbose_name="Total Mass Run Slots")
    total_cchal_slots = models.IntegerField(verbose_name="Total Chief Challenge Slots")
    STATUSES = (
        ("ongoing", "Ongoing"),
        ("concluded", "Concluded"),
    )
    status = models.CharField(max_length=10, choices=STATUSES, default=STATUSES[0])

    def __str__(self):
        return self.name

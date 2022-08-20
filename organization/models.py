from django.db import models
from convener.models import Convener, Event
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
import random
import string


class PIC(Convener):
    phone_no = models.BigIntegerField(null=True)

    class Meta:
        verbose_name = _('Person-In-Charge')
        verbose_name_plural = _('Persons-In-Charge')


def gen_code(size=3, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


class Organization(models.Model):
    name = models.CharField(max_length=100)
    person_in_charge = models.ForeignKey(PIC, on_delete=models.SET_NULL, null=True, related_name='organizations')
    events = models.ManyToManyField(Event)
    mrun_code = models.CharField(max_length=5, null=True)
    cchal_code = models.CharField(max_length=5, null=True)
    mrun_slots = models.IntegerField(default=5)
    cchal_slots = models.IntegerField(default=5)
    mrun_taken = models.IntegerField(default=0)
    cchal_taken = models.IntegerField(default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def reduce_mrun_slots(self):
        new_mrun_slots = self.mrun_slots - 1
        self.mrun_slots = new_mrun_slots
        self.save()

    def reduce_cchal_slots(self):
        new_cchal_slots = self.cchal_slots - 1
        self.cchal_slots = new_cchal_slots
        self.save()

    def update_event(self, event):
        new_total_cchal_slots = event.total_cchal_slots - self.cchal_slots
        new_total_mrun_slots = event.total_mrun_slots - self.mrun_slots
        try:
            event.total_cchal_slots = new_total_cchal_slots
            event.total_mrun_slots = new_total_mrun_slots
            event.save()
            return "Event successfully updated"
        except Exception as e:
            print(e)
            return "Update failed"

    def save(self, *args, **kwargs):

        if self.mrun_code is None and self.cchal_code is None:
            mass_run = "MR" + gen_code()
            chief_chal = "CC" + gen_code()
            self.mrun_code = mass_run
            self.cchal_code = chief_chal

        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class Participant(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    GENDER = (
        ('male', 'Male'),
        ('female', 'Female')
    )
    gender = models.CharField(max_length=10, choices=GENDER)
    country = CountryField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='participants')
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, related_name='participants')
    created = models.DateTimeField(auto_now_add=True)
    reg_id = models.IntegerField(blank=True, unique=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.first_name

    def get_full_name(self):
        return self.first_name + self.last_name

    def save(self, *args, **kwargs):
        if self.reg_id is None:
            regis_id = gen_code(size=5, chars=string.digits)
            self.reg_id = regis_id

        super().save(*args, **kwargs)


class Policy(models.Model):
    name = models.CharField(max_length=200)
    body = models.TextField()

    class Meta:
        verbose_name_plural = _('Policies')

    def __str__(self):
        return self.name

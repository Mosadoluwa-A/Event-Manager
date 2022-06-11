from django.db import models
from convener.models import Convener, Event
from django.utils.translation import gettext_lazy as _


class PIC(Convener):
    phone_no = models.BigIntegerField(null=True)

    class Meta:
        verbose_name = _('Person-In-Charge')
        verbose_name_plural = _('Persons-In-Charge')


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

    def save(self, *args, **kwargs):
        import random
        import string

        def gen_code(size=3, chars=string.ascii_uppercase + string.digits):
            return ''.join(random.choice(chars) for x in range(size))

        if self.mrun_code and self.cchal_code is None:
            mass_run = "MR" + gen_code()
            chief_chal = "CC" + gen_code()
            self.mrun_code = mass_run
            self.cchal_code = chief_chal

        super().save(*args, **kwargs)

from datetime import timedelta

from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


class Pool(models.Model):
    GERMAN = 'DE'
    ENGLISH = 'EN'
    KEYBOARD_CHOICES = (
        (GERMAN, 'German'),
        (ENGLISH, 'English'), )

    room_no = models.CharField(max_length=20, unique=True)
    keyboard_layout = models.CharField(
        max_length=2, choices=KEYBOARD_CHOICES, default=GERMAN)
    printer = models.BooleanField()
    pc_power_consumption = models.IntegerField()

    def __str__(self):
        return self.room_no


class Computer(models.Model):
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField(unique=True)

    def __str__(self):
        return self.ip


class ComputerDay(models.Model):
    computer = models.ForeignKey(
        Computer, on_delete=models.CASCADE, unique_for_date='date')
    date = models.DateField()
    duration = models.DurationField(editable=False, default=timedelta(0))

    def __str__(self):
        return "{} - {}".format(self.date, self.computer)


class Interval(models.Model):
    day = models.ForeignKey(ComputerDay, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{} - {}".format(self.start_time, self.day)


# Signal Recievers to trigger on changes
@receiver(pre_save, sender=Interval)
def update_day_duration_create(sender, instance, raw, **kwargs):
    # execute only if it is no import (raw data)
    if not raw:
        if instance.end_time:
            # if intervall end time was modified first remove the old intervall
            if instance.id:
                old_intervall = Interval.objects.get(pk=instance.id)
                if (old_intervall.end_time):
                    instance.day.duration -= (
                        old_intervall.end_time - old_intervall.start_time)
                    # add new/modified intervall to duration
            instance.day.duration += instance.end_time - instance.start_time
            instance.day.save()


@receiver(post_delete, sender=Interval)
def update_day_duration_delete(sender, instance, raw=False, **kwargs):
    # execute only if it is no import (raw data)
    if not raw:
        if (instance.end_time):
            instance.day.duration -= instance.end_time - instance.start_time
            instance.day.save()

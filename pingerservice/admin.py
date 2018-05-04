from ipaddress import ip_address

from datetime import datetime
from .tasks import get_day_limited_interval

from django import forms
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Computer, ComputerDay, Interval, Pool


class PoolResource(resources.ModelResource):
    class Meta:
        model = Pool


class ComputerResource(resources.ModelResource):
    class Meta:
        model = Computer


class IntervalResource(resources.ModelResource):
    def save_instance(self, instance, using_transactions, dry_run):
        if not dry_run:
            end_time = instance.end_time
            end_date = end_time.date()
            if instance.start_time.date() < end_date:
                limited_interval = get_day_limited_interval(instance, end_date)
                limited_interval.end_time = end_time
                limited_interval.save()

    class Meta:
        model = Interval


class IpRangeForm(forms.ModelForm):
    """
    This is a custom form for creating Pool instances it adds two
    IP address fields to specify a range for all computers instead
    of adding them one by one
    """
    range_start = forms.GenericIPAddressField(label='Start IP')
    range_end = forms.GenericIPAddressField(label='End IP')

    def save(self, commit=True):
        # first save pool instance so we can reference it
        self.instance.save()
        range_start = self.cleaned_data.get('range_start', None)
        range_end = self.cleaned_data.get('range_end', None)
        # Convert ip address text to int
        range_start_int = int(ip_address(range_start))
        range_end_int = int(ip_address(range_end))
        ip_int_range = range(range_start_int, range_end_int)
        for ip_int in ip_int_range:
            # convert int back to ip text
            ip_text = ip_address(ip_int).__str__()
            # create computer for self.instance (the pool we are editing)
            computer = Computer(ip=ip_text, pool=self.instance)
            computer.save()
        return super(IpRangeForm, self).save(commit=commit)

    class Meta:
        model = Pool
        fields = '__all__'


class ComputerInLine(admin.TabularInline):
    model = Computer
    extra = 1


class PoolAdmin(ImportExportModelAdmin):
    resource_class = PoolResource
    inlines = [ComputerInLine]
    #  form = IpRangeForm
    """A ModelAdmin that uses a different form class when adding an object."""

    def get_form(self, request, obj=None, **kwargs):
        if (obj is None):
            return IpRangeForm
        else:
            return super(PoolAdmin, self).get_form(request, obj, **kwargs)


class DayAdmin(admin.ModelAdmin):
    fields = [
        'computer',
        'date',
        'duration',
    ]
    readonly_fields = [
        'duration',
    ]


class ComputerAdmin(ImportExportModelAdmin):
    resource_class = ComputerResource


class IntervalAdmin(ImportExportModelAdmin):
    resource_class = IntervalResource


admin.site.register(Pool, PoolAdmin)
admin.site.register(ComputerDay, DayAdmin)
admin.site.register(Interval, IntervalAdmin)
admin.site.register(Computer, ComputerAdmin)

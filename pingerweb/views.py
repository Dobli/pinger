from django.shortcuts import render
from tablib import Dataset

from datetime import datetime
import pingerservice.models as m
from pingerservice import tasks
from pingerservice.admin import IntervalResource


# Create your views here.
def index(request):
    return render(request, 'pingerweb/index.html')


def pools(request):
    return render(request, 'pingerweb/pools.html')


# IMPORT EXTRA
def add_day_reference(row):
    date_format = "%Y-%m-%d %H:%M:%S"

    computer_id = row[1]
    entry_date = datetime.strptime(row[2], date_format).date()
    entry_pc = m.Computer.objects.get(pk=computer_id)
    day = tasks.get_day_or_create(entry_pc, entry_date)
    return day.id


def online(request):
    import logging
    logger = logging.getLogger(__name__)

    if request.method == 'POST':
        import json
        from pytz import timezone, utc
        localtz = timezone('Europe/Berlin')
        date_format = "%Y-%m-%d %H:%M:%S"
        jsonfile = request.FILES['myfile']
        intervals = json.load(jsonfile)
        i_count = len(intervals)
        i_counter = 0
        for i in intervals:
            i_counter += 1
            logger.info("{} from {}".format(i_counter, i_count))
            comp_id = i.get('computer')
            start = i.get('start_time')
            end = i.get('end_time')
            start_time = localtz.localize(
                    datetime.strptime(start, date_format)).astimezone(utc)
            end_time = localtz.localize(datetime.strptime(
                end, date_format)).astimezone(utc)
            pc = m.Computer.objects.get(pk=comp_id)
            entry_date = start_time.date()
            end_date = end_time.date()
            i_day = tasks.get_day_or_create(pc, entry_date)
            i = m.Interval(day=i_day, start_time=start_time)
            i.save()
            inter = tasks.get_day_limited_interval(i, end_date)
            inter.end_time = end_time
            inter.save()
        #  dataset = Dataset()
        #  interval_resource = IntervalResource()
        #  new_intervals = request.FILES['myfile']
        #  dataset.load(new_intervals.read())
        #  dataset.append_col(add_day_reference, header='day')
        #  result = interval_resource.import_data(dataset, dry_run=True)

        #  if not result.has_errors():
        #    #  interval_resource.import_data(dataset, dry_run=False)

    return render(request, 'pingerweb/online.html')


def consumption(request):
    return render(request, 'pingerweb/consumption.html')


def export(request):
    return render(request, 'pingerweb/export.html')

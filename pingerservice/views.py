import csv
from datetime import date, datetime, time, timedelta

from django.db.models import Sum
from django.http import HttpResponse, JsonResponse

from .models import Computer, ComputerDay, Interval, Pool


def start_ping(request):
    return HttpResponse("Starting Pinger Run")


# Private functions
def is_hour_in_intervall(hour, interval):
    hour_to_check = time(hour, 0, 0)
    interval_start = interval.start_time.time()

    # get either end time or end of day
    interval_end = time(
        23, 59, 59) if interval.end_time is None else interval.end_time.time()

    if hour_to_check >= interval_start and hour_to_check <= interval_end:
        return True
    else:
        return False


def generate_chart_data(pool_id, chart_date):
    """
    Generates chart data for a pool and date

    pool_id: id of the pool
    chart_date: date to check
    returns: dict containing chart data
    """
    hours = list(range(0, 24))
    hour_labels = ["{}:00".format(h) for h in hours]
    hour_data = [{'x': h, 'y': 0} for h in hours]

    pool = Pool.objects.get(pk=pool_id)

    # get all intervals for computers in selected pool / date
    intervals = Interval.objects.filter(
        day__computer__pool=pool, day__date=chart_date)

    # check for every hour how many intervalls it matches
    for hour in hours:
        for interval in intervals:
            if is_hour_in_intervall(hour, interval):
                hour_data[hour]["y"] += 1
    data = {
        "room_no": pool.room_no,
        "labels": hour_labels,
        "poolData": hour_data,
    }
    return data


def generate_chart_data_online(pool_id):
    """
    Generates chart data for currently online pcs in a pool

    pool_id: id of the pool
    returns: dict containing chart data (labels, count)
    """
    pool = Pool.objects.get(pk=pool_id)

    # get online pcs
    online_count = get_pcs_online_in_pool(pool)
    pc_count = get_number_of_pcs_in_pool(pool)

    room_no = pool.room_no
    data = {
        "room_no": room_no,
        "online": online_count,
        "offline": pc_count - online_count
    }
    return data


def get_number_of_pcs_in_pool(pool):
    """
    Retrun number of pcs in a pool
    """
    pc_count = Computer.objects.filter(pool=pool).count()
    return pc_count


def get_pcs_online_in_pool(pool):
    """
    Retrun number of currently NOT running pcs of a pool
    """
    # only running pcs have an open interval entry, filter for pool
    pc_count = Interval.objects.filter(
        day__computer__pool=pool, day__date=date.today(),
        end_time=None).count()
    return pc_count


# API calls
def pools(request, *args, **kwargs):
    """
    Return a list of all Pools as JSON List
    """
    pool_list = list(Pool.objects.values('room_no', 'pk'))
    data = {"pools": pool_list}
    return JsonResponse(data)


def chart_data_pool_date(request, pool_id, year, month, day):
    """
    Return chart data for a pool of a specific date

    :request: http request
    :pool_id: id of pool to check
    :year: year
    :month: month
    :day: day
    :returns: chart data

    """
    chart_date = date(int(year), int(month), int(day))
    data = generate_chart_data(pool_id, chart_date)
    return JsonResponse(data)


def chart_data_pool(request, pool_id):
    """
    Return data points of a day for a specific pool
    """
    data = generate_chart_data(pool_id, date.today())
    return JsonResponse(data)


def chart_data_pool_online(request, pool_id):
    """
    Return data of online and offline pc count in a specific pool
    """
    data = generate_chart_data_online(pool_id)
    return JsonResponse(data)


def generate_csv_data(request):
    """
    Generate csv data for a single pool from start to end date

    :request: http request
    :pool_id: id of pool
    :start_date: start date
    :end_date: end date
    :output_format: either ms or libre
    :returns: a csv file in http response

    """
    pool_ids = request.GET.getlist('pool_ids')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    output_format = request.GET.get('output_format')
    # pools to get data from, if empty choose all
    if pool_ids:
        pool_ids = [int(x) for x in pool_ids]
        pools = Pool.objects.filter(id__in=pool_ids)
    else:
        pools = Pool.objects.all()

    # format of expected date
    date_format = "%Y-%m-%d"
    if start_date:
        # convert start date string to date object
        s_date = datetime.strptime(start_date, date_format).date()
    else:
        s_date = date.today()
    if end_date:
        # convert end date string to date object
        e_date = datetime.strptime(end_date, date_format).date()
    else:
        e_date = date.today()
    # calculate day difference (+1 to include start / end)
    num_dates = (e_date - s_date).days + 1
    # create a list of dates ranging from start to end date
    export_dates = [s_date + timedelta(days=i) for i in range(0, num_dates)]

    # set the output format or default to libre output
    if not output_format:
        output_format = "unix"

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response[
        'Content-Disposition'] = 'attachment; filename="pinger_export.csv"'

    writer = csv.writer(response, dialect=output_format)
    # writer.writerow(export_dates)
    # create empty line list
    date_lines = []
    # create empty head line list
    head_line = ["Datum"]

    # Loop over pools for header
    for i in range(len(pools)):
        head_line.extend([
            "", "Raum Nr", "Summe der Laufzeit (in h)",
            "Durchschnittliche Laufzeit (in h)", "Verbrauch", "Anzahl Rechner"
        ])

    for counter, d in enumerate(export_dates):
        # add a line with the date
        date_lines.insert(counter, [d])
        # loop would start here
        for pool in pools:
            # get count of computers in this pool
            pool_count = Computer.objects.filter(pool=pool).count()
            # only complete durations (more than 0) should be considered
            min_duration = timedelta(0)
            # a queryset containing needed days
            pool_run_filter = ComputerDay.objects.filter(
                computer__pool=pool, duration__gt=min_duration, date=d)

            # number of running unique pools
            run_count = pool_run_filter.count()
            # get sum of pool runtime
            pool_run_sum = pool_run_filter.aggregate(
                Sum('duration')).get("duration__sum")
            # if sum is present calculate hours, else return 0
            if pool_run_sum:
                pool_run_sum = pool_run_sum.total_seconds() / 60 / 60
                # calculate avg from sum, Avg query seems broken
                pool_run_average = pool_run_sum / run_count
            else:
                pool_run_sum = 0.0
                pool_run_average = 0.0

            # get sum of pool power consumption
            pool_consume_sum = pool_run_sum * pool.pc_power_consumption

            # add values to a pool line
            pool_line = [
                "",
                pool.room_no,
                pool_run_sum,
                pool_run_average,
                pool_consume_sum,
                pool_count,
            ]
            # add pool line to date line
            date_lines[counter].extend(pool_line)

    writer.writerow(head_line)
    writer.writerows(date_lines)

    return response

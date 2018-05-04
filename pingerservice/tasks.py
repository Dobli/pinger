from datetime import date as system_date
from datetime import datetime, timedelta
from os import system as system_call
from platform import system as system_name

from celery import group, shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

from .models import Computer, ComputerDay, Interval

logger = get_task_logger(__name__)


@shared_task
def start_pinger_run():
    """
    Get all computers and start a ping task for each. The tasks are
    responsible to save their result.
    """
    computers = Computer.objects.all().values_list('pk', flat=True)
    ping_taks = group(
        ping_single_pc.s(computer_id) for computer_id in computers)
    ping_taks()


@shared_task
def ping_single_pc(computer_id):
    """
    Run ping task for a single pc and enter result into the database.
    """
    computer = Computer.objects.get(pk=computer_id)

    # get information if ping was a success and if there is an open interval
    success = ping(computer)
    has_open_interval = check_interval_running(computer)

    if not success and has_open_interval:
        close_open_intervals(computer)
    elif success and not has_open_interval:
        d = get_day_or_create(computer)
        i = Interval(day=d, start_time=timezone.now())
        i.save()
        get_day_limited_interval(i)

    result = 'FAILED'
    if success:
        result = 'SUCCEDED'
    logger.info("Ping to computer %s %s", computer, result)

    return success


def check_interval_running(computer):
    """
    Check whether an interval for this computer is already running.
    Retruns True when there is an unfinished interval
    """
    return Interval.objects.filter(
        end_time__isnull=True, day__computer=computer).exists()


def close_open_intervals(computer, end_time=None):
    """
    Search for open intervals of this computer and close them.
    Each open interval gets limited to the current day (not starting earlier,
    intervals of the past get closed at their starting day), then the end_time
    of the interval will be set
    """
    end_time = timezone.now() if end_time is None else end_time

    open_intervals = Interval.objects.filter(
        end_time__isnull=True, day__computer=computer)
    for interval in open_intervals:
        interval = get_day_limited_interval(interval)
        interval.end_time = end_time
        interval.save()


def get_day_limited_interval(interval, end_date=None):
    """
    Ensure that the interval closes within a day, if it overlaps
    create the next day instance and start from there.
    This will return either the input interval or the interval for
    the current day starting at 00:00:00
    """
    end_date = system_date.today() if end_date is None else end_date

    while interval.day.date != end_date:
        # set endtime of started interval to the end of the day
        interval.end_time = timezone.make_aware(
            datetime(interval.day.date.year, interval.day.date.month,
                     interval.day.date.day, 23, 59, 59))
        interval.save()
        # get the next date and a fitting day instance
        next_day_date = interval.day.date + timedelta(days=1)
        next_day = get_day_or_create(interval.day.computer, next_day_date)
        # get the datetime instance of the (beginning) next day
        beginning_datetime = timezone.make_aware(
            datetime(next_day_date.year, next_day_date.month,
                     next_day_date.day))
        # create new interval starting the next day
        interval = Interval(day=next_day, start_time=beginning_datetime)
        interval.save()
    return interval


def get_day_or_create(computer, date=None):
    """
    Return the todays day instance for this computer.
    If the instance is not present creat a new entry and return that.
    """
    if date is None:
        date = system_date.today()
    day, created = ComputerDay.objects.get_or_create(
        computer=computer, date=date)
    return day


def ping(computer):
    """
    Pings the computer (computer object), returns True if it is reachable.
    It may try multiple methods if one failes (e.g. if system ping
    is not working)
    """
    # return result of system ping (only option until now)
    return system_ping(computer.ip)


def system_ping(host):
    """
    Returns True if host (str) responds to a ping request.
    It uses system calls to the native ping command.
    On Windows Systems this may lead to unreliable results, as Windows ping
    treats destination host unreachable errors as 'true', productivity machine
    should run on Linux
    """
    # prepare parameters depending on OS timeout is 2 seconds
    parameters = ("-n 1 -w 2000" if system_name().lower() == "windows" else
                  "-c 1 -w 2 > /dev/null")

    # call ping with above parameters
    return system_call("ping " + host + " " + parameters) == 0

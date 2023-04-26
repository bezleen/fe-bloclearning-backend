import datetime
import pytz


def tzware_datetime():
    """
    Return a timezone aware datetime.

    :return: Datetime
    """
    return datetime.datetime.now(pytz.utc)


def tzware_timestamp():
    return int(tzware_datetime().timestamp())


def timedelta_months(months, compare_date=None):
    """
    Return a new datetime with a month offset applied.

    :param months: Amount of months to offset
    :type months: int
    :param compare_date: Date to compare at
    :type compare_date: date
    :return: datetime
    """
    if compare_date is None:
        compare_date = datetime.date.today()

    delta = months * 365 / 12
    compare_date_with_delta = compare_date + datetime.timedelta(delta)

    return compare_date_with_delta


def custom_tzware_datetime(year=None, month=None, day=None, hour=0, minute=0, second=0, microsecond=0):
    return datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=microsecond, tzinfo=pytz.utc)


def oid_to_datetime(oid):
    timestamp = int(str(oid)[:8], 16)
    dt = datetime.datetime.fromtimestamp(timestamp).astimezone(pytz.utc)
    return dt

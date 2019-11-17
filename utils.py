from collections import defaultdict
from contextlib import contextmanager
import datetime as dt
import time
from typing import List


@contextmanager
def time_it(action_name):
    """Context manager to time an operation"""
    start = time.time()
    yield
    end = time.time()
    print(f'==> {action_name} took {end-start} seconds')


def top(data, limit=3):
    """Retrieve the top [limit] elements of a list"""
    return list(reversed(sorted(data)[-limit:]))


def str_to_dict(input_str, filter_set):
    """
    Transform a string to a dict of characters with the count
    of each character
    """
    d = defaultdict(int)
    for c in input_str:
        if c in filter_set:
            d[c] += 1
    return d


def group_adjacent_dates(day_list: List[dt.date]):
    """
    Given a sorted list of dates, group them in adjacent segments
    """
    start = day_list[0]
    previous = start
    result = []
    for date in day_list[1:]:
        if date != previous + dt.timedelta(days=1):
            result.append(((previous - start).days, start, previous))
            start = date
        previous = date
    result.append(((previous - start).days + 1, start, previous))
    return result

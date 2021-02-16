"""
some useful utils for spider development
"""
import time
import chompjs


def parse_js_object(_str):
    return chompjs.parse_js_object(_str)


def time_to_stamp(_str, format='%Y-%m-%d %H:%M:%S', millisecond=False):
    _time = time.strptime(_str, format)
    stamp = time.mktime(_time)
    if millisecond:
        stamp *= 1000
    return int(stamp)


def stamp_to_time(stamp, format='%Y-%m-%d %H:%M:%S'):
    # for millisecond
    if len(str(stamp).split('.')[0]) >= 13:
        stamp = int(stamp / 1000)
    _time = time.localtime(stamp)
    return time.strftime(format, _time)


def convert_cookie_str(_str):
    """
    convert cookie str to dict
    """
    _list = [i.strip() for i in _str.split(';')]
    cookie_dict = dict()
    for i in _list:
        k, v = i.split('=', 1)
        cookie_dict[k] = v
    return cookie_dict


def convert_headers_str(_str):
    """
    convert headers str to dict
    """
    _list = [i.strip() for i in _str.split('\n')]
    headers_dict = dict()
    for i in _list:
        k, v = i.split(':', 1)
        headers_dict[k.strip()] = v.strip()
    return headers_dict


if __name__ == '__main__':
    print(time_to_stamp("2021-02-15 09:00:00"))
    print(stamp_to_time(time.time() * 1000))

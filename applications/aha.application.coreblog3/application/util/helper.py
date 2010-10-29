# -*- coding: utf-8 -*-

""" helper module """
import re
import new
from google.appengine.api import users
import urllib

def format_date(dt, shortfmt = 'short', format = None):
    """
    A helper function to format data.
    """
    fmt_dic = {
    'full':'%Y/%m/%d (%a) %H:%M:%S',
    'long':'%Y/%m/%d (%a) %H:%M',
    'short':'%Y/%m/%d %H:%M',
    'date_long':'%Y/%m/%d (%a)',
    'date_short':'%Y/%m/%d',
    'monthday_long':'%m/%d (%a)',
    'monthday_short':'%m/%d',
    'time_long':'%H:%M',
    'time_short':'%H:%M',
    'daytime_long':'%m/%d (%a) %H:%M',
    'daytime_short':'%m/%d %H:%M',
    'rfc822':'%a, %d %b %Y %H:%M:%S',
    'html5':'%Y-%m-%d %H:%M:%S',
    }

    if format:
        return dt.strftime(format)
    elif shortfmt in fmt_dic:
        return dt.strftime(fmt_dic[shortfmt])

    return str(dt)

def get_icon_from_type(type):
    """
    A helper function to obtain icon from type name of the object.
    """
    t = """<img src = "/style/img/%s_icon.png" width = "16" height = "16" alt = "%s" />"""
    return t % (type.lower(), type.lower())

def get_breadclumb(o):
    """
    a helper function to obtain bread clumb.
    """
    try:
        ol = []
        c = o.get_content()
        parent = c.get_parent()
        while parent:
            ol.append(parent)
            parent = parent.get_parent()
        ol.reverse()
        r = []
        for i in ol:
            r.append("""<a href = "%s/list">%s</a>""" % \
                        (i.get_path(), i.title or i.name))
        r.append(c.title or c.name)
        return ' &raquo; '.join(r)
    except:
        if hasattr(o, 'get_breadclumb'):
            return o.get_breadclumb()
        else:
            return ''

def get_current_user(controller):
    """
    A function to obtain current login user.
    """
    from aha import Config
    config = Config()
    authobj = config.auth_obj()
    user = authobj.get_user(controller)
    return user


def get_pagenation(current, total, page_size,
                   param_name = 'start', maxpages = 10):
    """
    A helper function to make list of pagenation
        current   : the item number of current page
        max       : total number of items
        page_size : item count in each page
    """
    pages = []
    if total > page_size:
        current_p = 0
        lstart = 0
        lend = total
        dd = 0
        showskip = False
        if total/page_size > maxpages:
            showskip = True
            lstart = (current/page_size-(maxpages/2))*page_size
            if lstart<0:
                lstart = 0
                showskip = False
            if lstart+maxpages*page_size >= total:
                lstart = (total/page_size-maxpages)*page_size
                showskip = False
            lend = ((lstart+(page_size*maxpages))/page_size)*page_size
            dd = lstart/page_size
        for n, p in enumerate(range(lstart, lend, page_size)):
            if p <= current < p+page_size:
                pages.append( ('current', str(n+1+dd)) )
                current_p = p
            else:
                pages.append( ('?start='+str(p), str(n+1+dd)) )
        if current_p >= page_size:
            if showskip:
                pos = max(current_p-(page_size*maxpages), 0)
                pages = [ ('?start=0', '1..') ]+pages
                pages = [ ('?start='+str(pos), '<<') ]+pages
            else:
                pages = [ ('?start='+str(current_p-page_size), '<') ]+pages
        else:
            pages = [ ('', '<<') ]+pages
        if current_p < total-page_size:
            if showskip:
                pos = min(current_p+(page_size*maxpages), 
                        (total/page_size)*page_size)
                pages += [ ('?start='+str((total/page_size)*page_size),
                          '..%s' % (total/page_size)) ]
                pages += [ ('?start='+str(pos), '>>') ]
            else:
                pages += [ ('?%s=%s'%(param_name, current_p+page_size), '>') ]
        else:
            pages += [ ('', '>>') ]
    return pages


def urlquote(s):
    """
    A function to obtain url-encoded string
    """
    return urllib.quote(s)


# making helper functions
# don't remove following codes.

from aha.controller.helper import helpers

hlps = dir()
for h in hlps:
    if not re.match('^__', h):
        method = eval('%s' % h)
        if callable(method):
            helpers.extend(h, method)

def main(): pass


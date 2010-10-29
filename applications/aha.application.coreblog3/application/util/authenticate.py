# -*- coding: utf-8 -*-

""" authenticate function """

import logging

from aha import Config
config = Config()
from model import SiteData


def admin(me, type = 1):
    """
    A authenticate function only to allow access for restricted users.
    """
    user = config.auth_obj().get_user(me)
    logging.debug('got user %s for authenticate' % user.get('nickname', 'n/a'))
    sd = SiteData.get_data()
    admins = [x for x in sd.admin_users.split('\r') if x]
    # adding initial user to admin user list
    try:
        admins.extend(config.initial_user)
    except:
        pass
    if not user or user.get('nickname', '') not in admins:
        return False
    return True



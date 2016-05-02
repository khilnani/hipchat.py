# coding: utf-8

"""
Description:
A python script to perform basic interactions with Hipchat.

License:
The MIT License (MIT)
Copyright (c) 2016 Nik Khilnani

Github:
https://github.com/khilnani/hipchat.py

Configuration:
Rename 'hipchat.sample.conf' to 'hipchat.conf' and update values

To use:
1 - In any app, use App Share, Run in Pythonista and then select this script.
2 - Run this script from within Pythonista or a unix/linux terminal/console.
"""

# https://developer.atlassian.com/hipchat/guide/hipchat-rest-api/api-access-tokens
# https://developer.atlassian.com/hipchat/guide/hipchat-rest-api/api-title-expansion
# https://www.hipchat.com/docs/apiv2

############################################################

import json
import re
# pip install requests[security] --upgrade
import logging
import sys
import urllib2
import getpass
# pip install python-dateutil
import dateutil.parser
import datetime
import requests

############################################################

CONF_FILE = 'hipchat.conf'
CACHE_FILE = 'hipchat_cache.json'

logger = None

__version__ = '0.1.0'
print 'Version: ' + __version__

############################################################

def pp(o):
    print json.dumps(o, indent=4, sort_keys=True)

def dp(dstr):
    d = None
    try:
        d = dateutil.parser.parse(dstr)
    except Exception as e:
        print(e)
    return d

def df(d):
    sf = ''
    try:
        sf = d.strftime('%b %d, %Y %H:%M:%S')
    except Exception as e:
        print (e)
    return sf

def dfiso(d):
    sf = ''
    try:
        sf = d.strftime('%Y/%m/%d %H:%M:%S')
    except Exception as e:
        print (e)
    return sf

def dt(ts):
    d = None
    try:
        d = datetime.datetime.utcfromtimestamp(float(ts))
    except Exception as e:
        print (e)
    return d

############################################################

def setup_logging(log_level='INFO'):
    global logger

    logging.addLevelName(9, 'TRACE')
    def trace(self, message, *args, **kws):
        if self.isEnabledFor(9):
            self._log(9, message, args, **kws)
    logging.Logger.trace = trace

    log_format = "%(message)s"
    logging.basicConfig(format=log_format)
    logger = logging.getLogger(__name__)

    if len(sys.argv) > 1:
        for ea in sys.argv:
            if ea in ('CRITICAL', 'ERROR', 'WARNING', 'INFO' , 'DEBUG', 'TRACE', 'NOTSET'):
                log_level = ea
                sys.argv.remove(ea)
                break

    logger.setLevel(log_level)
    print('Log Level: %s' % log_level )

def request_error(req):
    logger.error('HTTP Status %s ' % req.status_code)
#    logger.error(req.text)
#    logger.error(req.headers)

############################################################

def update_conf_info(token=None, email=None):
    api_url, base_url, useremail, access_token = get_conf_info()
    conf = {}

    if api_url:
        conf['API_URL'] = api_url
    if base_url:
        conf['BASE_URL'] = base_url
    if email:
        conf['USER_EMAIL'] = email
    elif useremail:
        conf['USER_EMAIL'] = useremail
    if token:
        conf['ACCESS_TOKEN'] = token
    elif access_token:
        conf['ACCESS_TOKEN'] = access_token

    try:
        with open(CONF_FILE, 'w') as conf_file:
            #print(conf)
            json.dump(conf, conf_file)
    except IOError:
        logger.error('Could not write %s' % CONF_FILE)
        sys.exit(1)

def get_conf_info():
    try:
        with open(CONF_FILE, 'r') as conf_file:
            conf = json.load(conf_file)
            api_url = conf['API_URL']
            base_url = conf['BASE_URL']
            try:
                useremail = conf['USER_EMAIL']
            except KeyError:
                useremail = None
            try:
                access_token = conf['ACCESS_TOKEN']
            except KeyError:
                access_token = None
            return (api_url, base_url, useremail, access_token)
    except IOError:
        logger.error('Could not find %s' % CONF_FILE)
        sys.exit(1)
    except ValueError:
        logger.error('Invalid JSON in %s' % CONF_FILE)
        sys.exit(1)

def get_cache():
    try:
        with open(CACHE_FILE, 'r') as c_file:
            c = json.load(c_file)
            try:
                rooms = c['ROOMS']
            except KeyError:
                 rooms = None
            try:
                users= c['USERS']
            except KeyError:
              users= None
            return (rooms, users)
    except IOError:
        logger.trace('Ignoring: Could not find %s' % CACHE_FILE)
    except ValueError:
        logger.error('Ignoring: Invalid JSON in %s' % CONF_FILE)

    return (None, None)

def update_cache(rooms=None, users=None):
    rms, us = get_cache()
    c = {}

    if rooms:
        c['ROOMS'] = rooms
    elif rms:
        c['ROOMS'] = rms

    if users:
        c['USERS'] = users
    elif us:
        c['USERS'] = us

    try:
        with open(CACHE_FILE, 'w') as c_file:
            #print(conf)
            json.dump(c, c_file)
    except IOError:
        logger.error('Could not write %s' % CACHE_FILE)
        sys.exit(1)

############################################################

def get(api_url, access_token, path):
    url = api_url + path
    if '?' not in url:
        url = url + '?'
    url = url + '&auth_token=' + access_token
    try:
        logger.trace('Getting ' + url)
        r = requests.get(url)
        valid = r.status_code >= 200 and r.status_code < 400
        if not valid:
            if r.status_code == 429:
                json_data = r.json()
                logger.error(json_data['error']['message'])
                sys.exit(1)
        return (valid, r)
    except ValueError as e:
        logger.error(e)
        request_error(r)
        sys.exit(e)
    except requests.exceptions.SSLError as e:
        logger.error(e)
        sys.exit(e)

def check_access_token(api_url, access_token):
    logger.info('Checking access token ...')
    path = 'user?auth_test=true'
    valid, r = get(api_url, access_token, path)
    return valid

def get_new_access_token(api_url, base_url, useremail=None):
    logger.info('Updating access token ...')
    if not useremail:
        useremail = raw_input('User email:')
    logger.info('Tip: Get a personal access token from: https://www.hipchat.com/account/api')
    access_token = getpass.getpass('Access token:')
    if access_token:
        update_conf_info(access_token, useremail)
    return access_token

############################################################

def get_rooms(api_url, access_token):
    logger.info('Getting rooms ...')
    path = 'room?expand=items&max-results=1000'
    rooms = {}
    valid, r = get(api_url, access_token, path)
    if valid:
        json_data = r.json()
        rooms = json_data['items']
    else:
        request_error(r)
    return rooms

def get_auto_join_rooms(api_url, access_token, id_or_email):
    logger.info('Getting auto-join rooms ...')
    path = 'user/%s/preference/auto-join?expand=items&max-results=1000' % id_or_email
    rooms = {}
    valid, r = get(api_url, access_token, path)
    if valid:
        json_data = r.json()
        rooms = json_data['items']
    else:
        request_error(r)
    return rooms

def get_users(api_url, access_token):
    logger.info('Getting users ...')
    path = 'user?expand=items&max-results=1000'
    users = {}
    valid, r = get(api_url, access_token, path)
    if valid:
        json_data = r.json()
        users = json_data['items']
    else:
        request_error(r)
    return users

def refresh_cache(api_url, access_token, id_or_email):
    logger.info('Reviewing cache ...')
    rooms, users = get_cache()
    if not rooms:
        rooms = get_auto_join_rooms(api_url, access_token, id_or_email)
        update_cache(rooms=rooms)
    logger.info('  Rooms: %s' % len(rooms))
    if not users:
        users= get_users(api_url, access_token)
        update_cache(users=users)
    logger.info('  Users: %s' % len(users))
    return (rooms, users)

def get_info_for_xmpp(rooms, users, xmpp_id):
    for r in rooms:
        if r['xmpp_jid'] == xmpp_id:
            return (r['id'], 'room', r['name'], None)
    for u in users:
        if u['xmpp_jid'] == xmpp_id:
            return (u['id'], 'user', u['name'], u['email'])
    return (None, None, None, None)

def unread_room(api_url, access_token, id_or_name, name, mid):
    path = 'room/%s/history/latest' % id_or_name
    valid, r = get(api_url, access_token, path)
    items = []
    if valid:
        found = False
        newer = False
        json_data = r.json()
        for item in json_data['items']:
            id = item['id']
            dutc = dp(item['date'])
            msg = item['message']
            fr = item['from']
            if fr:
                try:
                    uname = fr['name']
                except TypeError as e:
                    uname = fr
            if found:
                newer = True
            else:
                found = (id == mid)
            if found and not newer:
                logger.trace('  ++ %s on %s by %s: %s' % (id, df(dutc), uname, msg))
            if newer:
                logger.debug('  -- %s on %s by %s' % (id, df(dutc), uname))
                #print('By %s on %s:\n%s' % (uname, df(dutc), msg))
                items.append('By %s on %s:\n%s' % (uname, df(dutc), msg))
        if len(items) > 0:
            logger.info('  %s: %s new.' % (name, len(items)))
    else:
        request_error(r)
    return items

def unread_user(api_url, access_token, id_or_email, name, mid):
    path = 'user/%s/history/latest' % id_or_email
    valid, r = get(api_url, access_token, path)
    items = []
    if valid:
        found = False
        newer = False
        json_data = r.json()
        for item in json_data['items']:
            id = item['id']
            dutc = dp(item['date'])
            msg = item['message']
            fr = item['from']
            if fr:
                try:
                    uname = fr['name']
                except TypeError as e:
                    uname = fr
            if found:
                newer = True
            else:
                found = (id == mid)
            if found and not newer:
                logger.trace('  ++ %s on %s by %s: %s' % (id, df(dutc), uname, msg))
            if newer:
                logger.debug('  -- "%s on %s by %s' % (id, df(dutc), uname))
                #print('By %s on %s:\n%s' %  (uname, df(dutc), msg))
                items.append('By %s on %s:\n%s' % (uname, df(dutc), msg))
        if len(items) > 0:
            logger.info('  %s: %s new.' % (name, len(items)))
    else:
        request_error(r)
    return items

def get_unread_summary(api_url, access_token, rooms, users):
    logger.info('Looking for unread messages ...')
    # get last read messages
    # then, for each room or user, check the recent history
    # locate the last read message in the history, and collect newer ones
    path= 'readstate?expand=items.unreadCount'
    valid, r = get(api_url, access_token, path)
    items = {}
    i = 0
    if valid:
        json_data = r.json()
        for item in json_data['items']:
            mid = item['mid']
            ts = item['timestamp']
            d = dt(ts)
            xmpp_id= item['xmppJid']
            id, idtype, name, email = get_info_for_xmpp(rooms, users, xmpp_id)
            if id:
                i=i+1
                logger.debug('  %s. %s (%s)' % (i, name, dfiso(d)))
            logger.trace('  ## %s (%s): %s (%s) %s' % (id, xmpp_id, df(d), ts, mid))
            if id and idtype == 'room':
                #print('ROOM: %s (%s) MSG: %s (%s)' % (name, id, df(d), mid))
                _items = unread_room(api_url, access_token, id, name, mid)
                if len(_items) > 0:
                    items[name] = _items
            elif id and idtype =='user':
                #print('USER: %s (%s) MSG: %s (%s)' % (name, id, df(d), mid))
                _items = unread_user(api_url, access_token, id, name, mid)
                if len(_items) > 0:
                    items[name] = _items
            else:
                logger.trace('No user or room id found for xmpp_id: %s' % xmpp_id)
    logger.info('Done checking %s rooms/conversations.' % i)
    return items

def display_unread(items):
    logger.debug('Unread count: %s' % len(items))
    for key in items:
        print('-------------------------------------------')
        print key
        print('-------------------------------------------')
        for msg in items[key]:
            print msg
            print ''
        print ''

############################################################

def main():
    api_url, base_url, useremail, access_token = get_conf_info()

    if not check_access_token(api_url, access_token):
        access_token = get_new_access_token(api_url, base_url, useremail)
        if check_access_token(api_url, access_token):
            logger.error('The access token supplied is not valid.')
            sys.exit(1)
    rooms, users = refresh_cache(api_url, access_token, useremail)
    items = get_unread_summary(api_url, access_token, rooms, users)
    show_details = raw_input('Show details? (y/n): ')
    if show_details == 'y':
        display_unread(items)
    logger.info('Done.')

############################################################

if __name__ == '__main__':
    try:
        setup_logging()
        main()
    except KeyboardInterrupt as e:
        logger.error('User forced exit.')

############################################################

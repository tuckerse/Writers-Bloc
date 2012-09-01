from google.appengine.ext import db
from google.appengine.api import memcache
import UserHandler
import datetime
import logging

HOST_COOLDOWN = 60*5
DEFAULT_EXPIRE = 60*60

def retrieveCache(key, model):
    data = memcache.get(key)
    if data is not None:
        return data
    else:
        data = model.get_by_key_name(key)
        memcache.add(key, data, time=DEFAULT_EXPIRE)
        return data

def storeCache(data, key):
    if not memcache.replace(key, data):
        memcache.add(key, data, time=DEFAULT_EXPIRE)
    return data.put()

def deleteData(data, key):
    memcache.delete(key)
    db.delete(data)

def markPlayerHostedGame(user_id):
    user = retrieveCache(user_id, UserHandler.User)
    user.last_hosted = datetime.datetime.now()
    storeCache(user, user_id)

def canPlayerHost(user_id):
    user = retrieveCache(user_id, UserHandler.User)
    if user.last_hosted is None:
        user.last_hosted = (datetime.datetime.now() - datetime.timedelta(seconds=HOST_COOLDOWN*2))
        storeCache(user, user_id)
    logging.debug((datetime.datetime.now() - user.last_hosted).seconds)
    return (datetime.datetime.now() - user.last_hosted).seconds > HOST_COOLDOWN

def resetPlayerHost(user_id):
    user = retrieveCache(user_id, UserHandler.User)
    user.last_hosted = (datetime.datetime.now() - datetime.timedelta(seconds=HOST_COOLDOWN*2))
    storeCache(user, user_id)

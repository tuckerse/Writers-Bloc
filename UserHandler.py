from google.appengine.ext import db
from cacheLib import storeCache, retrieveCache

_USER_FIELDS = u'name,email,picture,friends'
class User(db.Model):
    user_id = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    picture = db.StringProperty(required=True)
    email = db.StringProperty()
    friends = db.StringListProperty()
    dirty = db.BooleanProperty()
    last_hosted = db.DateTimeProperty()
    rounds_afk = db.IntegerProperty()
    display_type = db.IntegerProperty()

    def refresh_data(self):
        """Refresh this user's data using the Facebook Graph API"""
        me = Facebook().api(u'/me',
            {u'fields': _USER_FIELDS, u'access_token': self.access_token})
        self.dirty = False
        self.name = me[u'name']
        self.email = me.get(u'email')
        self.picture = me[u'picture']
        self.friends = [user[u'id'] for user in me[u'friends'][u'data']]
        return storeCache(self, self.user_id)

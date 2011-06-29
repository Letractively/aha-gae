# -*- coding: utf-8 -*-

from wsgiref.handlers import format_date_time
from time import mktime
from google.appengine.ext.db import (Model, BlobProperty, DateTimeProperty,
                                     ReferenceProperty, StringProperty)
from plugin.microne.app import Microne
from plugin.twitteroauth.microne_config import initConfig
from plugin.twitteroauth.twitter_auth import TwitterOAuth

# instanciating the app.
app = Microne(__file__)
# configuring the twitter authentication.
initConfig(app, 'PUTYOUROWNCONSUMERKEY',
                'PUTYOUROWNCONSUMERSECRET')

class User(Model):
    """
    A model to store twitter user data.
    """
    username = StringProperty()
    name = StringProperty()
    profile_image_url = StringProperty()

    @classmethod
    def get_user(cls, username):
        """
        A method to obtain user by using username.
        It returns None in case no user is found.
        :param username: The username you want to get.
        """
        q = cls.all().filter('username =', username)
        return q.get()

    @classmethod
    def get_current_user(cls, app):
        """
        A method to obtain current login user.
        It returns None when no user is logging in.
        """
        tuser = TwitterOAuth.get_user(app.get_controller())
        if tuser:
            user = User.get_user(tuser['nickname'])
            return user
        return None

class Image(Model):
    """
    A model class to store image data.
    """
    data = BlobProperty()
    created_at = DateTimeProperty(auto_now = True)
    content_type = StringProperty()
    user = ReferenceProperty(reference_class = User)

NUMBER_OF_IMAGES = 10

@app.route('/')
@app.route('/{page:\d+}')
def index():
    """
    A function to show images.
    """
    images = []
    # getting images to show in the page.
    for img in Image.all().fetch(limit = NUMBER_OF_IMAGES):
        images.append(img)
    # put objects like list of images etc.
    #        so that the template can refer to them.
    c = app.context
    c['images'] = images
    c['user'] = User.get_current_user(app)
    c['message'] = app.session.get('message', '')
    app.session['message'] = ''
    app.session.put()
    # render output.
    app.render(template = 'index')


@app.route('/image/{key}')
def image():
    """
    A function to show single image.
    """
    image = Image.get(app.params.get('key', ''))
    if image:
        resp = app.response
        o = resp.out
        o.seek(0)
        o.write(image.data)
        resp.headers['Content-Type'] = 'image/jpeg'
        ctime = mktime(image.created_at.timetuple())
        resp.headers['Last-Modified'] = format_date_time(ctime)


def detect_image_mimetype(image):
    """
    A method to detect image type. It checks image header from raw data,
    returns content type.
    It handles PNG, JPEG, GIF, returns null string in case type is unknown.
    
    :param image: Image raw data to detect type.
    """
    if image[1:4] == 'PNG': return 'image/png'
    if image[0:3] == 'GIF': return 'image/gif'
    if image[6:10] == 'JFIF': return 'image/jpeg'
    return ''


@app.route('/post', conditions = dict(method = ['POST']))
@app.authenticate()
def post():
    """
    A function to receive image data and post it to datastore.
    """
    # getting current user
    user = User.get_current_user(app)
    message = ''
    imagedata = app.request.get("img")
    if user and imagedata:
        img_type = detect_image_mimetype(str(imagedata))
        if not img_type:
            message = 'PNG, JPEG, GIF would be welcome.'
        else:
            # put image to datastore.
            image = Image(data = imagedata, user=user,
                          content_type = img_type)
            image.put()
            message = 'A new image has been posted.'
    if not imagedata:
        message = 'No image data.'
    if not user:
        message = 'Please login.'
    app.session['message'] = message
    app.session.put()
    app.redirect('/')


@app.route('/login')
@app.authenticate()
def login():
    """
    A function to perform login to post images.
    """
    tuser = TwitterOAuth.get_user(app.get_controller())
    user = User.get_current_user(app)
    if not user:
        user = User(username = tuser['nickname'])
    user.name = tuser['realname']
    user.profile_image_url = tuser['icon_url']
    user.put()
    app.session['message'] = 'logged in'
    app.session.put()
    app.redirect('/')


@app.route('/logout')
@app.authenticate()
def logout():
    """
    A function to perform logout.
    """
    TwitterOAuth.clear_user(app.get_controller())
    app.session['message'] = 'logged out'
    app.session.put()
    app.redirect('/')



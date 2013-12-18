# encoding=utf8

import webapp2, datetime, os, jinja2, urllib

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext import blobstore  #Kuvat blobstoren kautta
from google.appengine.ext.webapp import blobstore_handlers

CHATS = ['main', 'book', 'flame', 'count']

CONTENT_HEADER = "text/html; charset=UTF-8"

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'])

# jinja2:ssa ei ole djangon 'now' avainsanaa
def get_current_time():
    return datetime.datetime.now().strftime("%H:%M")
    
JINJA_ENVIRONMENT.globals = {
    "get_current_time": get_current_time
}

def convertMessageTime(msg):
    seconds = (datetime.datetime.now() - msg.timestamp).total_seconds()
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    return '%s:%s:%s' % (int(h), int(m), int(s))
    

class ChatMessage(ndb.Model):
    user = ndb.StringProperty(required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    message = ndb.TextProperty(required=True)
    chat = ndb.StringProperty(required=True)

class UserProfile(ndb.Model):
    author = ndb.StringProperty()
    avatar = ndb.BlobProperty()      # kuvan upload db:hen, blob erilainen ndb:ssä, korjaa
    
class GenericChatPage(webapp2.RequestHandler):
    
    def get(self):
        requested_chat = self.request.get("chat", default_value=None)
        if requested_chat == None or requested_chat not in CHATS:
            template_values = {
                'title': u"Virhe! Huonetta ei löytynyt!",
                'chatname': requested_chat,
                'chats': CHATS
            }
            
            error_template = JINJA_ENVIRONMENT.get_template('error.html')
            page = error_template.render(template_values)
            self.response.write(page)
        else:
            messages = ndb.gql("SELECT * from ChatMessage WHERE chat = :1 "
                    "ORDER BY timestamp", requested_chat)
            msglist = messages.fetch()
            for msg in msglist:
                msg.deltatime = convertMessageTime(msg)
            
            template_values = {
                    'title': "Tervetuloa keskustelemaan huoneeseen: %s" %
                        requested_chat,
                    'msg_list': messages.fetch(),
                    'chat': requested_chat,
                    'chats': CHATS,
                    'USER': users.get_current_user().nickname()
            }
            
            template = JINJA_ENVIRONMENT.get_template('multichat.html')
            page = template.render(template_values)
            self.response.write(page)


class ChatRoomCountedHandler(webapp2.RequestHandler):
    
    def get(self):
        self.response.headers["Content-Type"] = CONTENT_HEADER
        messages = ndb.gql("SELECT * From ChatMessage "
            "ORDER BY timestamp DESC LIMIT 20")
        msglist = messages.fetch()
        for msg in msglist:
            msg.deltatime = int((datetime.datetime.now() - msg.timestamp).total_seconds())

        template_values = {
                'title': "Tervetuloa MarkCC's AppEngine Chat Room", 
                'msg_list': messages.fetch(),
                'chats': CHATS
        }
        
        template = JINJA_ENVIRONMENT.get_template('count.html')
        page = template.render(template_values)
        self.response.write(page)


class ChatRoomLandingPage(webapp2.RequestHandler):
    
    def get(self):
        user = users.get_current_user()
            
        if user:
            self.response.headers["Content-Type"] = CONTENT_HEADER
            messages = ndb.gql("SELECT * From ChatMessage "
                "ORDER BY timestamp DESC LIMIT 20")
            msglist = messages.fetch()
            for msg in msglist:
                msg.deltatime = convertMessageTime(msg)

            template_values = {
                    'title': "Tervetuloa keskustelemaan", 
                    'msg_list': messages.fetch(), 
                    'chats': CHATS
            }
            
            template = JINJA_ENVIRONMENT.get_template('landing.html')
            page = template.render(template_values)
            self.response.write(page)
        else:
            self.redirect(users.create_login_url(self.request.uri))

class ChatRoomPoster(webapp2.RequestHandler):
    
    def post(self):
        user = users.get_current_user()
        msgtext = self.request.get("message")
        chat = self.request.get("chat")
        msg = ChatMessage(user=user.nickname(), message=msgtext, chat=chat) 
        msg.put()
        # Now that we've added the message to the chat, we'll redirect
        # to the root page
        self.redirect('/enterchat?chat=%s' % chat)

class UserSettingsHandler(webapp2.RequestHandler):
    
#    def post(self):
#        setting = UserProfile(author=users.get_current_user().nickname())
#        setting.avatar = self.request.get("img")
#        setting.avatar = ndb.Blob(avatar)       # Blob ei toimi, katso mikä vastaa ndb:ssä
#        setting.put()
    
    def get(self):
#        upload_url = blobstore.create_upload_url('/upload')
#        self.response.headers["Content-Type"] = CONTENT_HEADER
#        template_values = {
#                    'title': "Settings", 
#            }
#        template = JINJA_ENVIRONMENT.get_template('usersettings.html')
#        page = template.render(template_values)
#        self.response.write(page)

#Placeholdertesti
        upload_url = blobstore.create_upload_url('/upload')
        self.response.out.write('<html><body>')
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit"
        name="submit" value="Submit"> </form></body></html>""")

#Placeholdertesti
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        self.redirect('/serve/%s' % blob_info.key())

#Placeholdertesti
class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)
        
app = webapp2.WSGIApplication([
    ('/', ChatRoomLandingPage), 
    ('/talk', ChatRoomPoster),
    ('/enterchat', GenericChatPage),
    ('/chatcount', ChatRoomCountedHandler),
    ('/settings', UserSettingsHandler),     #Vie placeholdertestiin
    ('/upload', UploadHandler),             #Placeholdertesti
    ('/serve/([^/]+)?', ServeHandler)       #Placeholdertesti
])

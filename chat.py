import tornado.ioloop
import tornado.web

import sockjs.tornado
from corduroy import Database, NotFound, relax

import json
import HTMLParser

db = Database('notes')
participants = set()

class IndexHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the chatroom page"""
    def get(self):
        self.render('index.html')


class ChatConnection(sockjs.tornado.SockJSConnection):
    """Chat connection implementation"""

    def on_open(self, info):
        # Send that someone joined
        pass
        #self.broadcast(participants, "Someone joined.")

        # Add client to the clients list
        participants.add(self)

    def on_message(self, message):
        # Broadcast message
        self.broadcast(participants, message)

    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        participants.remove(self)

        # self.broadcast(participants, "Someone left.")


class CallNewHandler(tornado.web.RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def get(self):
        self.post()

    @relax
    def post(self):
        message = {
            "callerid": self.get_argument("callerid"),
            "extension": self.get_argument("extension"),
        }
        message["html"] = message['callerid']

        if self.get_argument("next", None):
            self.redirect(self.get_argument("next"))
        else:
            self.write(message)

        # broadcast the new call information
        nextcaller_info = {u'records': [{u'address': [{u'city': u'Austin',
                             u'country': u'USA',
                             u'extended_zip': u'1234',
                             u'line1': u'123 Fake St',
                             u'line2': u'',
                             u'state': u'TX',
                             u'zip_code': u'11111'}],
               u'first_name': u'Caller',
               u'first_pronounced': u'Call her',
               u'id': u'3142jh14jksdf8789ag87',
               u'last_name': u'Notes',
               u'middle_name': u'',
               u'name': u'Caller Notes',
               u'phone': [{u'carrier': u'Stenius Mobile',
                           u'line_type': u'Mobile',
                           u'number': u'5551234567',
                           u'resource_uri': u'/v2.1/records/5551234567/'}],
               u'resource_uri': u'/v2.1/users/3142jh14jksdf8789ag87/'}]}

        try:
            doc = yield db.get(message["callerid"])
            notes = doc['notes']
            revision = doc['_rev']
        except NotFound:
            notes = 'These are the default notes!'
            revision = ''

        caller_info = {'nextcaller': nextcaller_info,
            'notes': notes,
            'revision': revision,
            "callerid": self.get_argument("callerid"),
            "extension": self.get_argument("extension"),
        }

        ChatRouter.broadcast(participants,json.dumps(caller_info))
        self.finish()

class NotesUpdater(tornado.web.RequestHandler):
    @relax
    def post(self):
        data = {
            "callerid": self.get_argument("callerid"),
            "revision": self.get_argument("revision"),
        }

        try:
            doc = yield db.get(data["callerid"])
            if doc['_rev'] != data['revision']:
                self.write(json.dumps(doc))
            else:
                doc.notes = json.loads(self.request.body)
                yield db.save(doc)
        except NotFound:
            doc = {'_id': data["callerid"], 'notes': self.request.body}
            yield db.save(doc)

        caller_info = {'doc': doc}
        self.write(json.dumps(caller_info))
        self.finish()

if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    # 1. Create chat router
    ChatRouter = sockjs.tornado.SockJSRouter(ChatConnection, '/chat')

    # 2. Create Tornado application
    # TODO: user better urls
    app = tornado.web.Application(
            [
                (r"/", IndexHandler),
                (r"/api/v1/call/new", CallNewHandler),
                (r"/api/v1/notes/save", NotesUpdater),
            ] + ChatRouter.urls
    )

    # 3. Make Tornado app listen on port 8080
    app.listen(8889)

    # 4. Start IOLoop
    tornado.ioloop.IOLoop.instance().start()

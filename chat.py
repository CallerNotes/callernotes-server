import tornado.ioloop
import tornado.web

import sockjs.tornado


class IndexHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the chatroom page"""
    def get(self):
        self.render('index.html')

participants = set()

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

        ChatRouter.broadcast(participants,message["html"])

if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    # 1. Create chat router
    ChatRouter = sockjs.tornado.SockJSRouter(ChatConnection, '/chat')

    # 2. Create Tornado application
    app = tornado.web.Application(
            [
                (r"/", IndexHandler),
                (r"/api/v1/call/new", CallNewHandler),
            ] + ChatRouter.urls
    )

    # 3. Make Tornado app listen on port 8080
    app.listen(8889)

    # 4. Start IOLoop
    tornado.ioloop.IOLoop.instance().start()

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
from tornado.escape import *

import csv
import json
import os
import os.path
import sys
import datetime
import time
import uuid
import redis

# ******************************************************************************
# Setting up some globals ******************************************************
print("\n*************Starting Tornado Web Service**************\n")

#Some can be read from Environmental variables (or not as they have a default)
BASE_PATH = os.getenv("BASE_PATH", "")
print("BASE_PATH: " + BASE_PATH)

# If WEB_SITE_PORT not redefined as an Environmental Variable us 9001
WEB_SITE_PORT = int(os.getenv('WEB_SITE_PORT', '9001'))
print("WEB PORT:", WEB_SITE_PORT)
REDIS_IP_ADDRESS = os.getenv("REDIS_IP_ADDRESS", "localhost")
print("REDIS IP ADDRESS:", REDIS_IP_ADDRESS)
print(file = sys.stderr)
print()

# These control how quickly websockets refresh
WEBSOCKET_REFRESH_RATE_MS = 10000

# Logging function good for debugging and recording events of importance.
# In a real system these might point to some thing besides printing the stdout
def applog(*a):
    print(*a, file = sys.stderr)

# ******************************************************************************
# **** Base Handler ************************************************************

class BaseHandler(tornado.web.RequestHandler):
    # This base handler is an extension of the orginal request handler to add
    # some features
    def get_current_user(self):
        return self.get_secure_cookie("user")

    def get_current_role(self):
        return self.get_secure_cookie("role")

    def isWriteAllowed(self):
        writeAllowed = ('"ADMIN"' in self.get_current_role()) or ('"WRITE"' in self.get_current_role())
        return(writeAllowed)

    def isAdminAllowed(self):
        adminAllowed = ('"ADMIN"' in self.get_current_role())
        return(adminAllowed)

    def returnError(self,error,write):
        # Create a JSON object
        resp_obj = {}
        resp_obj['rmessage'] = error
        resp_obj['status'] = error
        applog(error)
        # Send object back as response
        write(json.dumps(resp_obj))

# ******************************************************************************
# ******************************************************************************
# WebSocket Handler

def add_interaction_to_redis(redis_client, interaction, count):
    # Add source to data
    interaction["src-id"] = "web"
    #********************************
    # Take the string and publish to ui-stream on REDIS
    message = json.dumps(interaction)
    redis_client.publish('ui-stream', message)
    #********************************
    # Set a key value in Redis
    # Create the key in this order
    pref_order = ["src-id", "product-id", "product-name", "interaction-type", "timestamp"]
    list_to_join = []
    for field in pref_order:
        value = str(interaction[field])
        value = value.replace(":", "_") # Filter out any delimiter characters
        list_to_join.extend([field, value])
    entry_key = ':'.join(list_to_join) # Create the entry key
    # Send this to Redis
    redis_client.set(entry_key, count)
    #********************************
    # ZADD this to a set to make searching by datetime easier
    score = int(interaction['timestamp'])
    scored_data = entry_key
    z_key = "web_ts"
    redis_client.zadd(z_key, {scored_data: score})




    count += 1
    return count




class WebSocket_Handle(tornado.websocket.WebSocketHandler):

    def open(self):
        print("Web Socket is open")
        # Read data from a sub system at regular intervals
        dataOut = {"try this":1}
        # Because the connection was just activated write out the data to the
        # websocket connected to a client
        self.write_message(json.dumps(dataOut))
        # setup a future call back of this routine so that data can be
        # refreshed on the client side
        tornado.ioloop.IOLoop.instance().add_timeout(
            datetime.timedelta(microseconds = WEBSOCKET_REFRESH_RATE_MS * 1000),
            self.update)

        # Open connection to redis here and store the handle as a property of this class
        self.rh = redis.Redis(host=REDIS_IP_ADDRESS, port=6379, db=0)
        self.ps = self.rh.pubsub()
        print("REDIS is open :)")
        self.count = 0



        # Set this flag so that the websocket can be inform of its closing
        # if this in't done the socket might try transmitting on a close
        # connection and cause an error
        self.open = True

    def on_close(self):
        # Tell the possible future call back to update that the connection is
        # been closed.  If not done will result in errors.
        self.open = False

    def on_message(self, message):
        # Recieve messages from the client here
        data = json.loads(message)
        # Print it to standard out after converting it from a string to a object
        applog(data)
        if "obj_type" in data and data['obj_type'] == 'UPDATE':
            self.count = add_interaction_to_redis(self.rh, data, self.count)
        else:
            applog("WARNING: Message in MBOC_ExecutionAction_Handler not expected> %s\n" % message)
        
    def update(self):
        # Read data from a sub system at regular intervals
        dataOut = {"try this":1}

        if self.open:
            # If the connection is still active write out the data to the
            # websocket connected to a client
            self.write_message(json.dumps(dataOut))
            # setup a future call back of this routine so that data can be
            # refreshed on the client side
            tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(microseconds = WEBSOCKET_REFRESH_RATE_MS * 1000),
                self.update)

# ******************************************************************************
# ******************************************************************************
# Web Page Handler

class Main_Page_Handler(BaseHandler):
    def get(self):
        # Hand back from a get request with no fancy stuff
        self.render("index.html")

class NotFoundHandler(tornado.web.RequestHandler):
    def prepare(self):  # for all methods
        raise tornado.web.HTTPError(
            status_code=404,
            reason="Invalid resource path."
        )
        self.render("./public/404.html")


def prefix_with_base(url):
    if url:
        composed = "{0}/{1}".format(BASE_PATH, url)
    else:
        composed = BASE_PATH or "/"
    applog('Composed URL: ' + composed)
    return composed

p = prefix_with_base

# *** Settings, app setup and execution
settings = {
    "template_path": './public',
    "static_path":'./public',
    "debug":True,
    "cookie_secret": "A secret shared is not a secret",
    "login_url": "/auth/login/",
    "default_handler_class": NotFoundHandler
}

application = tornado.web.Application([
    #
    # Get Main Page
    (p(''), Main_Page_Handler),
    #
    # Websocket handlers
    (p('services/ws'),WebSocket_Handle),
    #
    # Anything not handled above and static in nature (in a file) handled here
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": "./public", "default_filename": "index.html"})
    ], **settings)


if __name__ == "__main__":
    # Start it all up

    application.listen(WEB_SITE_PORT)
    tornado.ioloop.IOLoop.current().start()

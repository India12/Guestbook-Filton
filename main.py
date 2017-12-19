#!/usr/bin/env python
import os
import jinja2
import webapp2
from models import Message
from google.appengine.api import users


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}

        user = users.get_current_user()
        params["user"] = user

        if user:
            logged_in = True
            logout_url = users.create_logout_url('/')
            params["logout_url"] = logout_url
            params["email"] = user.email()
            if user.email() == "turnsek.lucija@gmail.com":
                params["is_admin"] = True

        else:
            logged_in = False
            login_url = users.create_login_url('/')
            params["login_url"] = login_url

        params["logged_in"] = logged_in

        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))



class MainHandler(BaseHandler):
    def get(self):
        msg_list = Message.query(Message.deleted == False).order(-Message.dateTime).fetch()
        params = {"msg_list": msg_list}

        return self.render_template("main.html", params=params)

class SendMessageHandler(BaseHandler):
    def get(self):
        return self.render_template("send_message.html")
    def post(self):
        name = self.request.get("name")
        surname = self.request.get("surname")
        text = self.request.get("text")
        email = self.request.get("email")

        if not name:
            name = "Anonymous"

        if "<script>" in text:
            return self.write("Can't hack me :P")

        message = Message(name=name, surname=surname, text=text, email=email)
        message.put()

        return self.redirect_to("home-page")

class IndividualMessageHandler(BaseHandler):
    def get(self, message_id):
        user = users.get_current_user()
        ind_message = Message.get_by_id(int(message_id))


        #Another way of access control: (some parts are optional: first and last part)
        if not user:
            return self.write("You are not logged in!")
        #elif Message.email == user.email() or user.email() == "turnsek.lucija@gmail.com":      #isti ucinek?
        elif user.email() == ind_message.email or user.email() == "turnsek.lucija@gmail.com":
            ind_message = Message.get_by_id(int(message_id))
            params = {"ind_message": ind_message}
            return self.render_template("individual_message.html", params=params)
        else:
            return self.write("You are not an authorized to see this!")

class EditMessageHandler(BaseHandler):
    def get(self, message_id):
        ind_message = Message.get_by_id(int(message_id))
        params = {"ind_message": ind_message}

        return self.render_template("edit_message.html", params=params)

    def post(self, message_id):
        user = users.get_current_user()
        ind_message = Message.get_by_id(int(message_id))

        if user.email() == ind_message.email or user.email() == "turnsek.lucija@gmail.com":
            text = self.request.get("text")
            ind_message.text = text
            ind_message.put()

        params = {"ind_message": ind_message}

        return self.render_template("individual_message.html",  params=params)

class DeleteMessageHandler(BaseHandler):
    def get(self, message_id):
        ind_message = Message.get_by_id(int(message_id))
        params = {"ind_message": ind_message}

        return self.render_template("delete_message.html", params=params)

    def post(self, message_id):
        ind_message = Message.get_by_id(int(message_id))
        ind_message.deleted = True
        ind_message.put()

        return self.redirect_to("home-page")

class DeletedMessagesHandler(BaseHandler):
    def get(self):
        deleted_messages = Message.query(Message.deleted == True).order(-Message.dateTime).fetch()
        params = {"deleted_messages": deleted_messages}

        return self.render_template("deleted_messages.html", params=params)

class RestoreMessageHandler(BaseHandler):
    def get(self, message_id):
        ind_message_restore = Message.get_by_id(int(message_id))
        params = {"ind_message_restore": ind_message_restore}

        return self.render_template("restore_message.html", params=params)

    def post(self, message_id):
        ind_message_restore = Message.get_by_id(int(message_id))

        ind_message_restore.deleted = False
        ind_message_restore.put()

        return self.redirect_to("home-page")

class CompleteDeleteMessageHandler(BaseHandler):
    def get(self, message_id):
        compl_deleted_message = Message.get_by_id(int(message_id))
        params = {"compl_deleted_message": compl_deleted_message}

        return self.render_template("compl_deleted_message.html", params=params)

    def post(self, message_id):
        compl_deleted_message = Message.get_by_id(int(message_id))
        compl_deleted_message.key.delete()

        return self.redirect_to("deleted-messages")

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="home-page"),
    webapp2.Route('/leave_a_review', SendMessageHandler),
    webapp2.Route('/message/<message_id:\d+>', IndividualMessageHandler,),
    webapp2.Route('/message/<message_id:\d+>/edit', EditMessageHandler),
    webapp2.Route('/message/<message_id:\d+>/delete', DeleteMessageHandler),
    webapp2.Route('/message/<message_id:\d+>/compl_deleted_message', CompleteDeleteMessageHandler),
    webapp2.Route('/message/<message_id:\d+>/restore', RestoreMessageHandler),
    webapp2.Route('/deleted', DeletedMessagesHandler, name="deleted-messages"),
], debug=True)

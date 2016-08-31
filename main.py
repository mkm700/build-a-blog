#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

#Create the Blog table in the DB
class Blog(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add=True)

#query the database for posts using limit and offset, and return them
def get_posts(limit, offset):
    posts = db.GqlQuery("SELECT * FROM Blog "
                        "ORDER BY created DESC "
                        "LIMIT " + str(limit) +
                        "OFFSET " + str(offset))
    return posts

#Displays a list of blog posts on the home page
class MainHandler(webapp2.RequestHandler):

    def get(self):
        #Set how many posts to display per page
        limit = 5

        #check to see if page number is present in url and set page number
        if self.request.get("page"):
            page = int(self.request.get("page"))
        else:
            page = 1

        #calculate offset (which post to display first)
        offset = ((limit * page) - limit)


        #call the funstion to return the post data
        posts = get_posts(limit, offset)

        #determine the last page number based on total number of posts and limit
        numposts = posts.count()
        if numposts % limit == 0:
            lastpage = numposts / limit
        else:
            lastpage = (numposts / limit) + 1


        #render the page
        t = jinja_env.get_template("blog.html")
        response = t.render(posts=posts,page=page,lastpage=lastpage)
        self.response.write(response)


#Add a new Blog Post
class NewPostHandler(webapp2.RequestHandler):
    def get(self):
        t = jinja_env.get_template("newpost.html")
        response = t.render()
        self.response.write(response)

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            b = Blog(title = title, post = post)
            b.put()
            self.redirect(str(b.key().id()))
        else:
            error = "Please enter both a title and post text"
            t = jinja_env.get_template("newpost.html")
            response = t.render(title=title,post=post,error=error)
            self.response.write(response)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        id = int(id)
        post = Blog.get_by_id(id)
        if post:
            t = jinja_env.get_template("single.html")
            response = t.render(post=post,error="")
            self.response.write(response)
        else:
            error = "Sorry... no blog exists with that ID."
            t = jinja_env.get_template("single.html")
            response = t.render(post=post,error=error)
            self.response.write(response)

app = webapp2.WSGIApplication([
#???How do I redirect the index page to /blog???
#    ('/', MainHandler),
    ('/blog', MainHandler),
    ('/blog/newpost', NewPostHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)

"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

import os
import time
from app import app,db,login_manager,models
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response 
from flask_login import login_user, logout_user, current_user, login_required
from random import randint
from werkzeug.utils import secure_filename
import hashlib
import uuid
import json
import requests
from passlib.hash import pbkdf2_sha512

###
# Helper functions
###

def saltedhash(raw,salt):
    salted = raw + salt
    hash = pbkdf2_sha512.hash(salted)
    return hash

def verify(user,password):
    salt = models.Authentication.query.filter_by(userid=user.userid).first().salt
    salted = password+salt
    hash = models.Authentication.query.filter_by(userid=user.userid).first().hash
    return pbkdf2_sha512.verify(salted,hash)
    
def genID():
    return int(uuid.uuid4().int & (1<<16)-1)
    
def send_email(to_name, to_addr, subj, msg):
    
    from_name = 'noreply@title.manage'
    from_addr = 'noreply@title.manage'
    
    # Credentials
    username = 'thewishlyco@gmail.com'
    password = 'xzhhkglidexavsuf'
    
    message = """From: {} <{}>\nTo: {} <{}>\nSubject: {}\n\n{}"""
    message_to_send = message.format(from_name, from_addr, to_name, to_addr, subj, msg)
    
    # The actual mail send
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
    except smtplib.socket.gaierror:
        return False
        
    server.starttls()
    try:
        server.login(username, password)
    except SMTPAuthenticationError:
        server.quit()
        return False
    try:
        server.sendmail(from_addr, to_addr, message_to_send)
        return True
    except Exception:
        server.quit()
        return False
    finally:
        server.quit()
    
###
# Routing for your application.
#

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')

@app.route('/search/')
def search():
    """Render the website's search page."""
    return render_template('search.html')

@app.route('/register/')
def register():
    """Render the register page for new user"""
    return render_template('register.html')
    
@app.route('/title/new', methods=['POST','GET'])
def newtitle():
    """Render the website's new title page."""
    if request.method=="POST":
        print "pig"
        
    return render_template('newtitle.html')
        user = models.User(userid=id,firstname)
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        """Get data"""
        data = request.form
        username = data["username"]
        auth = models.Authentication.query.filter_by(username=username).first()
    
        if auth is None:
            flash("Username or password is incorrect")
            
        else:
            hpass = saltedhash(data["password"],auth.salt)
            if(auth.password == hpass):
                user = models.User.query.filter_by(userid=auth.userid).first()  
                login_user(user)
        
    return render_template('login.html')


@app.route('/user/new', methods=['GET','POST'])
def newuser():
    if request.method == "POST":
        """Get data"""
        data = request.form
        fname = data["fname"]
        lname = data["lname"]
        role = data["role"]
        email = data["email"]
        id = genID()
        
        user = models.User(userid=id,firstname=fname,lastname=lname,role=role,email=email)
        db.create_all()
        db.session.add(user)
        db.session.commit()
        
        data = request.get_json(force = True)
        to_name = lname+', '+fname
        to_addr = email
        link = app.config['SERVER_NAME']+'/user/register/'+id
        
        """Make Message"""
        msg = """ Dear {},\n Please follow the following link to complete your user registration: \n{}\n Thank you.""".format(to_name,link)
        subj = """Title Management System User Registration""".format(current_user.name)
        
        """Send Message"""
        
        send_email(to_name,to_addr,subj,msg)
        
    return render_template("newuser.html")
    
@app.route('/user/register/<userid>', methods=['GET','POST'])
def register(userid):
    if request.method == "POST":
        """Get data"""
        data = request.form
        uname = data["username"]
        pword = data["password"]
        salt =  uuid.uuid4().hex
        
###
# The functions below should be applicable to all Flask apps.
###

@login_manager.user_loader
def load_user(user_id):
    return  models.User.query.filter_by(userid=user_id).first()

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")
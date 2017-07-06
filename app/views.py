"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

import os
import time
from app import app,db,login_manager,models
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response, current_app, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from random import randint
from werkzeug.utils import secure_filename
import hashlib
import uuid
import json
import requests
from passlib.hash import pbkdf2_sha512
import smtplib


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
    
    from_name = current_user.name 
    from_addr = 'thewishlyco@gmail.com'
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
    
@app.route('api/search/',methods=['POST'])
def search():
    """Render the website's search page."""
    
    if request.method=='POST':
        
        data = request.get_json(force=True)
        keyword = data['keyword']
        
        query = models.Title.query.join(models.Publishing, models.Sales, models.Title.titleid == models.Publishing.titleid, models.Title.titleid == models.Sales.titleid).contains(keyword).all()
        
        data = []
        
        for result in query:
            data.append({'titleid':result.titleid,'title':result.title})
            
        out = {'error':None, 'data':data, 'message':'Success'}
        
        return jsonify(out)
        
    
    return render_template('search.html')
    
@app.route('/login',methods=['POST'])
def login():
    if request.method == "POST":
        """Get data"""
        data = request.form
        username = data["username"]
        auth = models.Authentication.query.filter_by(username=username).first()
    
        if auth is None:
            flash("Username or Password is incorrect.")
            
        else:
            hpass = saltedhash(data["password"],auth.salt)
            if(auth.password == hpass):
                user = models.Users.query.filter_by(userid=auth.userid).first()  
                login_user(user)
               
    else:
        flash("Username or Password is incorrect.")
        
    return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    redirect("home.html")

'''USER MANAGEMENT'''
    
@app.route('/user/new',methods=['GET','POST'])
@login_required
def newuser():
    if request.method == "POST":
        """Get data"""
        data = request.form
        
        fname = data["fname"]
        lname = data["lname"]
        role = data["role"]
        email = data["email"]
        uid = genID()
        
        """Create new user"""
        user = models.Users(userid=uid,firstname=fname,lastname=lname,role=role,email=email)
        db.create_all()
        db.session.add(user)
        db.session.commit()
        
        """Send registration email"""
        
        to_name = fname + " " + lname
        to_addr = email
        link = app.config['SERVER_NAME']+'/user/register/'+uid
        
        msg = """ Dear {},\n Please follow the following link to complete user registration:\n {} \n Regards, \n TitleMangementSystem """.format(to_name,link)
        subj = "Complete TitleManagementSystem User Registration"
        
        send_email(to_name,to_addr,subj,msg)
        
    return render_template("newuser.html")
        
@app.route('/user/register/<userid>',methods=['GET','POST'])
def register(userid):
    if request.method == "POST":
        """Get data"""
        data = request.form
        uname = data["username"]
        pword = data["password"]
        
        salt = uuid.uuid4().hex
        phash = saltedhash(pword,salt)
        
        """Create Authentication Profile"""
        auth = models.Authentication(userid=userid,hash=phash,salt=salt)
        db.create_all()
        db.session.add(auth)
        db.session.commit()
    
    return render_template("register.html")

@app.route('/users/manage',methods=['GET','POST'])
def manageusers():
    if request.method == "POST":
        """Get data"""
        data = request.form
        #to be completed
    
    return render_template("users.html")
    
'''TITLE MANAGEMENT'''
    
@app.route('/title/new', methods=['POST','GET'])
def newtitle():
    """Render the website's new title page."""
    folder = app.config['UPLOAD_FOLDER']
    
    if request.method=="POST":
        form = request.form
        title = form['title']
        subtitle = form['subtitle']
        description = form['description']
        status = 'IN PROGRESS'
        
        tid = genID()
        
        new = models.Title(titleid=tid,title=title,subtitle=subtitle,description=description,status=status)
        db.create_all()
        db.session.add(new)
        
        path = folder+'/'+tid
        
        if not os.path.exists(path):
            os.makedirs(path)
            db.commit()
    return render_template('newtitle.html')

        
@app.route('api/title/<titleid>',methods=['POST','GET'])
def titleinfo(titleid):
    
    title = models.Title.query.filter_by(titleid=titleid).first

    if request.method == 'GET':
        
        data = {'title':title.title, 'subttile':title.subtitle,'description':title.description,'status':title.status}
        
        out = {'error':None, 'data':data, 'message':'Success'}
    
        return jsonify(out)

@app.route('api/title/<stage>',methods=['POST','GET'])
def phaselist(stage):
    
    if request.method == 'GET':
        
        titles = models.Title.query.join(models.Has, models.Phase, models.Title.titleid == models.Has.titleid, models.Phase.phaseid == models.Has.phaseid ).filter_by(models.Phase.stage==stage).all()
        
        data = []
        
        for title in titles:
            
            record = {'title':title.title, 'subttile':title.subtitle,'description':title.description,'status':title.status}
            data.append(record)
        
        out = {'error':None, 'data':data, 'message':'Success'}
    
        return jsonify(out)
        
    if request.method == 'POST':
        
        criteria = request.get_json(force=True)
        status = criteria['status']
        
        data = []
        
        titles = models.Title.query.join(models.Has, models.Phase, models.Title.titleid == models.Has.titleid, models.Phase.phaseid == models.Has.phaseid ).filter_by(models.Phase.stage==stage, models.Title.status==status).all()
        
        for title in titles:
            
            record = {'title':title.title, 'subttile':title.subtitle,'description':title.description,'status':title.status}
            data.append(record)
        
        out = {'error':None, 'data':data, 'message':'Success'}
        
        return jsonify(out)
        
@app.route('/<titleid>/sales', methods = ['GET','POST'])
def sales(titleid):
    """Render the website's sales page."""
    
    record = models.Sales.query.filter_by(titleid == titleid).first()
    
    if request.method == "POST":
        """Get data"""
        data = request.form
        totalsales  = data['totalsales']
        internationalsales = data['internationalsales']
        regionalsales = data['regionalsales']
        
        if record.exists():
            
            record.totalsales = totalsales
            record.internationalsales = internationalsales
            record.regionalsales = regionalsales
            
        else:
            
            new = models.Sales(titleid = titleid, totalsales = totalsales, internationalsales=internationalsales, regionalsales = regionalsales)
            db.session.add(new)
            
        db.session.commit()
        
        
    return render_template('sales.html')

@app.route('/<titleid>/publishing')
def publishing(titleid):
    """Render the website's publishing info"""
    
    record = models.Publishing.query.filter_by(titleid==titleid).first()
        

    if request.method == "POST":
        """Get data"""
        data = request.form
        isbn = data['isbn']
        width = data['width']
        height = data['height']
        pagecount = data['pagecount']
        pubdate = data['pubdate']
        
        if record.exists():
            
            record.isbn = isbn
            record.width = width
            record.height = height
            record.pagecount = pagecount
            record.pubdate = pubdate
            
        else:
            
            new = models.Publishing(titleid=titleid,isbn=isbn,width=width,height=height,pagecount=pagecount,pubdate=pubdate)
            db.session.add(new)
            
        db.session.commit()
            
    return render_template('publishing.html')   

@app.route('api/<titleid>/activity  ',methods=['GET','POST'])
def activitylist(titleid):
    
    if request.method == 'GET':
        
        phaselist = models.Phase.query.join(models.Has, models.Phase.phaseid == models.Has.phaseid).add_columns(models.Phase.phaseid).filter_by(models.Has.titleid == titleid).all()
        actlist = models.Activity.query.join(models.Consists_Of, models.Activity.activityid == models.Consists_Of.activityid).filter_by(models.Has.phaseid in phaselist).all()
        
        data = []
        
        for activity in actlist:
            
            record = {'name':activity.name, 'startdate':activity.startdate,'duration':activity.duration,'completed':activity.completed}
            data.append(record)
        
        out = {'error':None, 'data':data, 'message':'Success'}
        
        return jsonify(out)
        
    if request.method == 'POST':
        
        criteria = request.get_json(force=True)
        showcomplete = criteria['showCompleted']
        
        phaselist = models.Phase.query.join(models.Has, models.Phase.phaseid == models.Has.phaseid).add_columns(models.Phase.phaseid).filter_by(models.Has.titleid == titleid).all()
        actlist = models.Activity.query.join(models.Consists_Of, models.Activity.activityid == models.Consists_Of.activityid).filter_by(models.Has.phaseid in phaselist, models.Activity.completed == showcomplete).all()
        
        data = []
        
        for activity in actlist:
            
            record = {'name':activity.name, 'startdate':activity.startdate,'duration':activity.duration,'completed':activity.completed}
            data.append(record)
        
        out = {'error':None, 'data':data, 'message':'Success'}
        
        return jsonify(out)
        
@app.route('api/<titleid>/activity/new',methods=['POST'])
def newActivity(titleid):
    
    if request.method == 'POST':
        
        criteria = request.get_json(force=True)
        stage = criteria['stage']
        
        data = criteria['data']
        
        phase = models.Phase.query.join(models.Has,models.Phase.phaseid==models.Has.phaseid).filter_by(models.Has.titleid == titleid, models.Phase.stage == stage).first()
        
        actid = genID()
        name = data['name']
        startdate = data['startdate']
        duration = data['duration']
        completed = False
        
        if criteria['isEvent'] == 'True':
            starttime = data['starttime']
            endtime = data['endtime']
            venue = data['venue']
            
            activity = models.Event(activityid=actid,name=name,startdate=startdate,duration=duration,completed=completed,starttime=starttime,endtime=endtime,venue=venue)
        
        else:
            
            activity = models.Activity(activityid=actid,name=name,startdate=startate,duration=duration,competed=completed)
            
        consists_of = models.Consists_Of(phaseid=phase.phaseid,activityid=activity.activityid)
        
        db.create_all()
        db.session.add(activity)
        db.session.add(consists_of)
        db.session.commit()
        
        out = {'error':None, 'data':[], 'message':'Success'}
        
        return jsonify(out)
        
'''ACTIVITY MANAGEMENT'''

@app.route('/<activityid>',methods=['GET','POST'])
def activity(activityid):
    """Render the website's activity page."""
    
    record = models.Activity.query.filter_by(activityid==activityid).first()
    event = models.Activity.query.filter_by(activityid==activityid).first()
    if request.method == "POST":
        """Get data"""
        data = request.form
        name = data['name']
        statdate = data['startdate']
        duration = data['duration']
        completed = data['completed']
        
        if record.exists():
            record.name = name
            record.statdate = statdate
            record.duration = duraion
            record.completed = completed
        
        if event.exists():
            
            event.starttime = data['starttime']
            event.endtime = data['endtime']
            event.venue = data['endtime']
        
    if event.exists():
        return render_template('event.html')
    else:
        return render_template('activity.html')

@app.route('api/<activityid>',methods = ['GET','POST'])
def activityinfo(activityid):
    
    activity = models.Activity.query.filter_by(activityid = activityid).first()
    
    if request.method == 'GET':
        
        event = models.Event.query.filter_by(activityid = activityid).first()
        
        if event.query.exists():
            data = {'name':event.name, 'startdate':event.startdate,'duration':event.duration,'completed':event.completed, 'starttime': event.starttime, 'endtime': event.endtime, 'venue': event.venue}
            
        else:
        
            data = {'name':activity.name, 'startdate':activity.startdate,'duration':activity.duration,'completed':activity.completed}
            
        out = {'error':None, 'data':data, 'message':'Success'}
        
        return jsonify(out)
        
@app.route('api/<activityid>/resources', methods = ['GET','POST'])
def resourcelist(activityid):
    
    resList = models.Resource.query.join(models.Uses,models.Resource.resourceid==models.Uses.resourceid).filter_by(models.Uses.activityid==activityid).all()
    
    if request.method == 'GET':
        data = []
        
        for resource in resList:
            
            human = models.HumanResource.query.filter_by(resourceid==resource.resourceid).first()
            
            if human.query.exists():
                
                data.append({'name':human.name, 'duration':human.duration, 'rate':human.rate})
            
            else:
                
                material = models.MaterialResource.query.filter_by(resourceid==resource.resourceid).first()
                data.append({'name':material.name,'qty':material.qty, 'unitcost':material.unitcost})
        
        out = {'error':None, 'data':data, 'message':'Success'}
        
        return jsonify(out)
        
@app.route('api/<activityid>/resources/new',methods=['POST'])
def addResource(activityid):
    
    if request.method == 'POST':
        data = request.get_json(force=True)
        
        name = data['name']
        resid = genID()
        if data['type']=='HumanResource':
            duration = data['duration']
            rate = data['rate']
            res = models.HumanResource(resourceid=resid,name=name,duration=duration,rate=rate)
            db.create_all()
            db.session.add(res)
            
        else:
            qty = data['qty']
            unitcost = data['unitcost']
            res = models.MaterialResource(resourceid=resid,name=name,qty=qty,unitcost=unitcost)
            db.create_all()
            db.session.add(res)
            
        uses = models.Uses(activityid=activityid,resourceid=resid)
        db.session.add(uses)
        db.session.commit()
        
         
        out = {'error':None, 'data':{}, 'message':'Success'}
        
        return jsonify(out)
        
'''FILE MANAGEMENT'''
        
@app.route('api/<titleid>/files', methods=['GET'])
@login_required
def files(titleid):
    
    return redirect('file://'+app.config["SERVER_NAME"]+'/'+app.config['UPLOAD_FOLDER']+'/'+titleid)
        
@app.route('<titleid>/files/add', methods=['GET','POST'])
def addfile(titleid):
    current = models.Phase.query.join(models.Has, models.Phase.phaseid == models.Has.phaseid).add_columns(models.Phase.phaseid).filter_by(models.Has.titleid == titleid,models.Phase.current == True).all()
    owns = models.Owns.query.filter_by(userid==current_user.userid).exists()
    
    file_folder = app.config['UPLOAD_FOLDER']
    
    if request.method == 'POST' and owns:
        
        data = request.get_jdon(force=True)
        name = data['name']
        version = data['version']
        
        file = request.files['file']
        filename = secure_filename(name+'_'+verrsion)
        file.save(os.path.join(file_folder+'/'+titleid, filename))
        
    return render_template('submitfile.html')
    
@app.route('api/<titleid>/files/<file>/delete',methods=['DELETE'])
def deletefile(titleid,file):
    current = models.Phase.query.join(models.Has, models.Phase.phaseid == models.Has.phaseid).add_columns(models.Phase.phaseid).filter_by(models.Has.titleid == titleid,models.Phase.current == True).all()
    owns = models.Owns.query.filter_by(userid==current_user.userid, phaseid==current.phaseid).exists()
    
    if request.method == 'DELETE' and owns and current_user.role in ['GeneralManager','LeadEditor']:
        
        path  = app.config['UPLOAD_FOLDER']+'/'+titleid+'/'+file
        os.remove(path)
        
        out = {'error':None, 'data':{}, 'message':'Success'}
        
        return jsonify(out)
        
        
@app.route('api/<titleid>/<file>',methods=['GET'])
def download(titleid,file):
    
    if request.method  == 'GET':
        
        uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
        return send_from_directory(directory=uploads, filename=file)
        

###
# The functions below should be applicable to all Flask apps.
###

@login_manager.user_loader
def load_user(user_id):
    return  models.Users.query.filter_by(userid=user_id).first()

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
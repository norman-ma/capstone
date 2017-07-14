"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

import os
import datetime
import sys
from app import app,db,login_manager,models
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response, current_app, send_from_directory,abort
from flask_login import login_user, logout_user, current_user, login_required
from random import randint
from werkzeug.utils import secure_filename
import hashlib
import uuid
import json
import requests
from passlib.hash import pbkdf2_sha512
import smtplib
import base64


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
    
    from_name = 'noreply@titlemanagementsystem.com'
    from_addr = 'noreply@titlemanagementsystem.com'
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

@app.route('/', methods = ['GET'])
def home():
    """Render website's home page."""
    return render_template('home.html')
        

@app.route('/home',methods=['GET'])
@login_required
def user():
    if current_user.role == 'GeneralManager':
        return render_template('general.html')
    elif current_user.role in ['LeadEditor','Publishing Assistant']:
        return render_template('editor.html')
    elif current_user.role in ['FinancialManager','Accountant']:
        return render_template('finance.html')
    elif current_user.role == 'MarketingManager':
        return render_template('marketing.html')
    
@app.route('/search',methods=['GET','POST'])
def search():
    """Render the website's search page."""
    
    if request.method=='GET':
        
        keyword = request.args.get('keyword')
        
        query = db.session.query(models.Title,models.By, models.Author, models.Publishing).join(models.By, models.Title.titleid == models.By.titleid).join(models.Author,models.Author.authorid == models.By.authorid).join(models.Publishing,models.Publishing.titleid==models.Title.titleid)
        
        titleq = query.filter(models.Title.title == keyword).all()
        subtitleq = query.filter(models.Title.subtitle == keyword).all()
        authorq = query.filter(models.Author.firstname == keyword or models.Author.lastname == keyword).all()
        isbnq = query.filter(models.Publishing.isbn == keyword).all()
        data = titleq+subtitleq+authorq+isbnq
        
        out = []
        
        for result in data:
            out.append({'id':result.Title.titleid,'title':result.Title.title,'author':result.Author.lastname+', '+result.Author.firstname[0], 'isbn':result.Publishing.isbn})
        
        return render_template('results.html',result=out)


'''LOGIN/LOGOUT'''    
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        """Get data"""
        data = request.form
        username = data["username"]
        auth = models.Authentication.query.filter_by(username=username).first()
    
        if not db.session.query(db.exists().where(models.Authentication.username==username)).scalar():
            flash("Username or Password is incorrect.")
            
        elif verify(auth,data['password']):
            user = models.Users.query.filter_by(userid=auth.userid).first()  
            login_user(user,remember = False)
            return redirect(url_for('user'))
        else:
            flash("Username or Password is incorrect.")
        
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

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
        
        """Send registration email"""
        
        to_name = fname + " " + lname
        to_addr = email
        link = request.url_root+'user/register/'+str(uid)
        
        msg = """ Dear {},\n Please follow the following link to complete user registration:\n {} \n Regards, \n TitleMangementSystem """.format(to_name,link)
        subj = "Complete TitleManagementSystem User Registration"
        
        if send_email(to_name,to_addr,subj,msg):
             db.session.commit()
        else:
            flash('There was an error, please try again')
        
    return render_template("newuser.html")
        
@app.route('/user/register/<userid>',methods=['GET','POST'])
def register(userid):
    
    if request.method == "POST":
        """Get data"""
        data = request.form
        uname = data["username"]
        pword = data["password"]
        confirm = data["cpassword"]
        
        if pword == confirm:
        
            salt = uuid.uuid4().hex
            phash = saltedhash(pword,salt)
            
            """Create Authentication Profile"""
            auth = models.Authentication(userid=userid,username=uname,hash=phash,salt=salt)
            db.create_all()
            db.session.add(auth)
            db.session.commit()
            
            return redirect(url_for('login'))
        
        else:
            flash('Passwords must match.')
    
    return render_template("register.html")

@app.route('/users/manage',methods=['GET','POST'])
@login_required
def manageusers():
    if request.method == "POST":
        """Get data"""
        data = request.form
        #to be completed
    
    return render_template("users.html")
    
'''TITLE MANAGEMENT'''
    
@app.route('/title/new', methods=['POST','GET'])
@login_required
def newtitle():
    """Render the website's new title page."""
    folder = app.config['UPLOAD_FOLDER']
    
    if request.method=="POST":
        
        form = request.form
        title = form['title']
        subtitle = form['subtitle']
        description = form['description']
        category = int(form['category'])
        status = 'IN PROGRESS'
        
        tid = genID()
        
        newtitle = models.Title(titleid=tid,title=title,subtitle=subtitle,description=description,status=status)
        db.session.add(newtitle)
        
        authorfname = form['authorfname']
        authorlname = form['authorlname']
        
        if(db.session.query(db.exists().where(db.and_(models.Author.firstname==authorfname, models.Author.lastname==authorlname)))).scalar():
            aid = models.Author.query.filter_by(firstname=authorfname,lastname=authorlname).first()
        else:
            aid = genID()
            newauth = models.Author(authorid=aid,firstname=authorfname,lastname=authorlname)
            db.session.add(newauth)
        
        by = models.By(titleid=tid, authorid=aid)
        db.session.add(by)
        
        phase1 = models.Phase(phaseid=genID(),budget=0,stage='Acquisition',current=True)
        has1 = models.Has(titleid=tid,phaseid=phase1.phaseid)
        db.session.add(phase1)
        db.session.add(has1)
        phase2 = models.Phase(phaseid=genID(),budget=0,stage='EditorialProduction',current=False)
        has2 = models.Has(titleid=tid,phaseid=phase2.phaseid)
        db.session.add(phase2)
        db.session.add(has2)
        phase3 = models.Phase(phaseid=genID(),budget=0,stage='SalesMarketing',current=False)
        db.session.add(phase1)
        has3 = models.Has(titleid=tid,phaseid=phase3.phaseid)
        db.session.add(phase3)
        db.session.add(has3)
        
        sales = models.Sales(titleid=tid,localsales=0,regionalsales=0,internationalsales=0,totalsales=0)
        db.session.add(sales)
        
        belongs_to = models.Belongs_to(titleid=tid,categoryid=category)
        db.session.add(belongs_to)
        
        path = folder+'/'+str(tid)
        
        if not os.path.exists(path):
            os.makedirs(path)
            db.session.commit()
            return redirect(url_for('titleinfo'),titleid=tid)
        else:
            flash('Title already exists')
            
    return render_template('newtitle.html')
    
@app.route('/api/title/<titleid>/edit',methods = ['POST'])
@login_required
def edittitle(titleid):
    
    if request.method == "POST":
        
        record = models.Title.query.filter_by(titleid=titleid).first()
        
        data = request.form
        
        if 'title' in data and data['title'] != '':
            record.title = data['title']
            
        if 'subtitle' in data and data['subtitle'] != '':
            record.subtitle = data['subtitle']
        
        if 'description' in data and data['description'] != '':
            record.description = data['description']
        
        if 'category' in data and data['category'] != '':
            record.category = data['category']
        
        if 'status' in data and data['status'] != '':
            record.status = data['status']
            
        db.session.add(record)
        db.session.commit()
        
        return redirect(url_for('titleinfo',titleid=titleid))
    
@app.route('/titles', methods=['GET'])
@login_required
def titlelist():
    
    titles = models.Title.query.all()
    
    tlist = []
    if request.method == 'GET':
        for t in titles:
            tlist.append({'id':t.titleid, 'title':t.title,'subtitle':t.subtitle,'status':t.status})
    
    return render_template('titles.html',result=tlist)
        
@app.route('/title/<titleid>',methods=['POST','GET'])
@login_required
def titleinfo(titleid):
    
    if not db.session.query(db.exists().where(models.Title.titleid==titleid)).scalar():
        abort(404)
    
    title = db.session.query(models.Title, models.By, models.Author, models.Belongs_to, models.Category,models.Has,models.Phase).join(models.By, models.Title.titleid == models.By.titleid).join(models.Author, models.Author.authorid == models.By.authorid).join(models.Belongs_to, models.Belongs_to.titleid == models.Title.titleid).join(models.Category,models.Category.categoryid == models.Belongs_to.categoryid).join(models.Has,models.Has.titleid == models.Title.titleid).join(models.Phase,models.Phase.phaseid == models.Has.phaseid).filter(models.Title.titleid == titleid,models.Phase.current == True).first()
    
    if db.session.query(db.exists().where(models.Publishing.titleid == titleid)).scalar():  
        pub = models.Publishing.query.filter_by(titleid=titleid).first()
    else:
        pub = None
    if db.session.query(db.exists().where(models.Sales.titleid == titleid)).scalar():
        sales = models.Sales.query.filter_by(titleid=titleid).first()
    else:
        sales = None
        
    if request.method == 'POST':
        
        data = request.form
        
        if db.session.query(db.exists().where(models.Title.titleid==titleid)).scalar():
            title.Title.title = data['title']
            title.Title.subtitle = data['subtitle']
            title.Title.description = data['description']
            title.Title.status = data['status']
            
            db.session.add(title)
            db.session.commit()
    
    return render_template('title.html',title=title, pub=pub,sales=sales)

@app.route('/api/titles',methods=['POST','GET'])
@login_required
def titles():
    
    if request.method == 'POST':
        
        criteria = request.get_json(force=True)
        state = criteria['state']
        stage = criteria['stage']

        data = []
        if stage=='' and state=='':
            titles = db.session.query(models.Title,models.Has,models.Phase).join(models.Has, models.Has.titleid == models.Title.titleid).join(models.Phase, models.Has.phaseid == models.Phase.phaseid).filter(models.Phase.current == True).all()
        elif stage=='' and state!='':
            titles = db.session.query(models.Title,models.Has,models.Phase).join(models.Has, models.Has.titleid == models.Title.titleid).join(models.Phase, models.Has.phaseid == models.Phase.phaseid).filter(models.Title.status == state,models.Phase.current == True).all()
        elif stage!='' and state=='':
            titles = db.session.query(models.Title,models.Has,models.Phase).join(models.Has, models.Has.titleid == models.Title.titleid).join(models.Phase, models.Has.phaseid == models.Phase.phaseid).filter(models.Phase.stage == stage,models.Phase.current == True).all()
        else:
            titles = db.session.query(models.Title,models.Has,models.Phase).join(models.Has, models.Has.titleid == models.Title.titleid).join(models.Phase, models.Has.phaseid == models.Phase.phaseid).filter(models.Phase.stage == stage, models.Title.status == state,models.Phase.current == True).all()
        
        for title in titles:
            
            record = {'id':title.Title.titleid, 'title':title.Title.title, 'subtitle':title.Title.subtitle,'description':title.Title.description,'status':title.Title.status,'stage':title.Phase.stage}
            print (record,sys.stderr)
            data.append(record)
        
        out = {'error':None, 'data':data, 'message':'Success'}
        
        return jsonify(out)
        
@app.route('/api/<titleid>/sales', methods = ['POST'])
@login_required
def sales(titleid):
    """Render the website's sales page."""
    
    if request.method == "POST":
        """Get data"""
        data = request.form
        
        if db.session.query(db.exists().where(models.Sales.titleid==titleid)).scalar():
            
            record = models.Sales.query.filter_by(titleid == titleid).first()
            if 'localsales' in data and data['localsales'] != '':
                record.localsales = data['localsales']
                
            if 'internationalsales' in data and data['internationalsales'] != '':    
                record.internationalsales = data['internationalsales']
            
            if 'regionalsales' in data and data['regionalsales'] != '':
                record.regionalsales = data['regionalsales']
            
            record.totalsales = record.localsales + record.regionalsales + record.internationalsales
            
            db.session.add(record)
            
        db.session.commit()
        
        return redirect(url_for('titleinfo',titleid=titleid))

@app.route('/api/<titleid>/publishing',methods=['POST'])
@login_required
def publishing(titleid):

    if request.method == "POST":
        """Get data"""
        
        data = request.form
        
        if db.session.query(db.exists().where(models.Publishing.titleid==titleid)).scalar():
            
            record = models.Publishing.query.filter_by(titleid=titleid).first()
            
            if 'isbn' in data and data['isbn'] != '':
                record.isbn = data['isbn']
            
            if 'width' in data and data['width'] != '':    
                record.width = data['width']
            
            if 'height' in data and data['heigh'] != '':
                record.height = data['height']
            
            if 'pagecount' in data and data['pagecount'] != '':
                record.pagecount = data['pagecount']
            
            if 'pubdate' in data and data['pubdate'] != '':
                record.pubdate = data['pubdate']
                
            db.session.add(record)
            
        else:
            
            isbn = data['isbn']
            width = data['width']
            height = data['height']
            pagecount = data['pagecount']
            pubdate = data['pubdate']
            
            new = models.Publishing(titleid=titleid,isbn=isbn,width=width,height=height,pagecount=pagecount,pubdate=pubdate)
            
            db.session.add(new)
            
        db.session.commit()
            
        return redirect(url_for('titleinfo',titleid=titleid))   

@app.route('/api/<titleid>/activity',methods=['GET','POST'])
@login_required
def activitylist(titleid):
    
    if request.method == 'POST':
        
        data = request.get_json(force=True)
        complete = data['complete']
        current = data['current']
        
        query = db.session.query(models.Title, models.Has, models.Phase, models.Consists_Of,models.Activity).join(models.Has,models.Title.titleid == models.Has.titleid).join(models.Phase,models.Phase.phaseid == models.Has.phaseid).join(models.Consists_Of,models.Consists_Of.phaseid == models.Phase.phaseid).join(models.Activity,models.Activity.activityid == models.Consists_Of.activityid).filter(models.Title.titleid == titleid)
        
        if complete and current:
            actlist = query.filter(models.Activity.completed == complete, models.Phase.current == True).all()
        elif complete:
            actlist = query.filter(models.Activity.completed == complete).all()
        elif current:
            actlist = query.filter(models.Activity.completed == complete, models.Phase.current == True).all()
        else:
            actlist = query.all()
        
        data = []
        
        for activity in actlist:
            
            total = activitytotal(activity.Activity.activityid)
            allocation = activityallocation(activity.Activity.activityid,total)
            
            record = {'id':activity.Activity.activityid, 'name':activity.Activity.name, 'startdate':activity.Activity.startdate.date().strftime("%a, %B %d, %Y"),'duration':activity.Activity.duration,'completed':activity.Activity.completed, 'total':total, 'allocation':allocation}
            
            data.append(record)
        
        out = {'error':None, 'data':data, 'message':'Success'}
        
        return jsonify(out)
        
@app.route('/<titleid>/activity/new',methods=['GET','POST'])
@login_required
def newactivity(titleid):
    
    if request.method == 'POST':
        
        data = request.form
        
        print (data,sys.stderr)
        
        phase = db.session.query(models.Phase,models.Has).join(models.Has, models.Phase.phaseid == models.Has.phaseid).filter(models.Has.titleid == titleid, models.Phase.current == True).first()
        
        actid = genID()
        name = data['name']
        startdate = data['startdate']
        duration = data['duration']
        completed = False
        
        if 'starttime' in data:
            
            starttime = data['starttime']
            endtime = data['endtime']
            venue = data['venue']
            
            activity = models.Event(activityid=actid,name=name,startdate=startdate,duration=duration,completed=completed,starttime=starttime,endtime=endtime,venue=venue)
        
        else:
            
            activity = models.Activity(activityid=actid,name=name,startdate=startdate,duration=duration,completed=completed)
            
        consists_of = models.Consists_Of(phaseid=phase.Phase.phaseid,activityid=activity.activityid)
        
        db.create_all()
        db.session.add(activity)
        db.session.add(consists_of)
        db.session.commit()
        
        return redirect(url_for('activity',activityid=actid))
        
    return render_template('newactivity.html',titleid=titleid)
    
@app.route('/api/<titleid>/milestones',methods=['GET'])
@login_required
def milestonelist(titleid):
    
    if request.method == 'GET':
        
        mlist = db.session.query(models.Title,models.Has,models.Phase,models.Includes,models.Milestone).join(models.Has,models.Title.titleid == models.Has.titleid).join(models.Phase,models.Has.phaseid == models.Phase.phaseid).join(models.Includes,models.Phase.phaseid == models.Includes.phaseid).join(models.Milestone,models.Includes.milestoneid == models.Milestone.milestoneid).filter(models.Phase.current == True, models.Title.titleid == titleid).all()

        out = []
       
        for milestone in mlist:
            
            if milestone.Milestone.achieved:
                achieved = 'Yes'
            else:
                achieved = 'No'
           
            record = {"id":milestone.Milestone.milestoneid, "name":milestone.Milestone.name, "date":milestone.Milestone.date.date().strftime("%a, %B %d, %Y"), "achieved": achieved}
            
            out.append(record)
        
        out = {'error':None, 'data':out, 'message':'Success'}
        
        return jsonify(out)
        
'''PHASE MANAGEMENT'''

@app.route('/api/phase/<phaseid>/budget', methods=['POST'])
@login_required
def setbudget(phaseid):
    
    phase = models.Phase.query.filter_by(phaseid=phaseid).first()
    
    titleid = db.session.query(models.Phase, models.Has).join(models.Has,models.Phase.phaseid==models.Has.phaseid).first().Has.titleid
    
    if request.method == 'POST':
        
        data = request.form
        
        print (data,sys.stderr)
        
        phase.budget = data["budget"]
        
        db.session.add(phase)
        db.session.commit()
        
        return redirect(url_for("titleinfo",titleid=titleid))
        
@app.route('/api/<titleid>/stage/next', methods=['POST'])
@login_required
def nextphase(titleid):
    
    phases = db.session.query(models.Title,models.Has,models.Phase).join(models.Has,models.Title.titleid == models.Has.titleid).join(models.Phase, models.Phase.phaseid == models.Has.phaseid).filter(models.Title.titleid==titleid)
    
    if request.method == 'POST':
        
        data = request.get_json(force=True)
        
        print (data,sys.stderr)
        
        nxt = data["next"]
        
        if nxt != None:
            cphase = phases.filter(models.Phase.current == True).first().Phase
            nphase = phases.filter(models.Phase.stage == nxt).first().Phase
            
            cphase.current = False
            nphase.current = True
            
            db.session.add(cphase)
            db.session.add(nphase)
                
        db.session.commit()
        
        return redirect(url_for('titleinfo',titleid=titleid))
        
    

'''MILESTONE MANAGEMENT'''
    
@app.route('/api/<titleid>/milestone/new',methods=['POST'])
@login_required
def newmilestone(titleid):
    
    if request.method == 'POST':
        
        data = request.form
        
        print (data,sys.stderr)
        
        phase = db.session.query(models.Phase,models.Has).join(models.Has, models.Phase.phaseid == models.Has.phaseid).filter(models.Has.titleid == titleid, models.Phase.current == True).first()
        
        milestoneid = genID()
        name = data['name']
        date = data['date']
        achieved = False
        
        milestone = models.Milestone(milestoneid=milestoneid,name=name,date=date,achieved=achieved)
            
        includes = models.Includes(phaseid=phase.Phase.phaseid,milestoneid=milestone.milestoneid)
        
        db.create_all()
        db.session.add(milestone)
        db.session.add(includes)
        db.session.commit()
        
        return redirect(url_for('titleinfo',titleid=titleid))
        
@app.route('/api/<titleid>/milestone/<milestoneid>/edit',methods=['POST'])
@login_required
def milestone(titleid,milestoneid):
        
        if request.method == 'POST':
        
            data = request.form
            
            print (data,sys.stderr)
            
            milestone = models.Milestone.query.filter_by(milestoneid=milestoneid).first()
            
            if 'date' in data and data['date'] != '':
                milestone.date = data['date']
            
            if 'achieved' in data and data['achieved'] != '':
                milestone.achieved = data['achieved']
                
            db.session.add(milestone)
            db.session.commit()
            
            return redirect(url_for('titleinfo',titleid=titleid))
        
'''ACTIVITY MANAGEMENT'''

def activitytotal(activityid):
    
    resList = db.session.query(models.Resource, models.Uses).join(models.Uses,models.Resource.resourceid == models.Uses.resourceid).filter(models.Uses.activityid == activityid).all()
    
    costs = []
    
    for r in resList:
        if db.session.query(db.exists().where(models.HumanResource.resourceid == r.Resource.resourceid)).scalar():
            h = models.HumanResource.query.filter_by(resourceid=r.Resource.resourceid).first()
            costs.append(h.rate * h.duration)
        else:
            m = models.MaterialResource.query.filter_by(resourceid=r.Resource.resourceid).first()
            costs.append(m.unitcost * m.qty)
    
    if costs == []:
        return 0
        
    return sum(costs)
    
def activityallocation(activityid,total):
    
    phasebudget = db.session.query(models.Phase,models.Consists_Of).join(models.Consists_Of,models.Consists_Of.phaseid == models.Phase.phaseid).filter(models.Consists_Of.activityid == activityid).first().Phase.budget
    
    if phasebudget == 0:
        return 0
    else:
        return (total/phasebudget)*100
        

@app.route('/activity/<activityid>',methods=['GET','POST'])
@login_required
def activity(activityid):
    """Render the website's activity page."""
    
    activity = models.Activity.query.filter_by(activityid=activityid).first()
    event = models.Event.query.filter_by(activityid=activityid).first()
    total = activitytotal(activityid)
    allocation = activityallocation(activityid,total)
    
    if request.method == "POST":
        """Get data"""
        data = request.form
        
        if db.session.query(db.exists().where(models.Activity.activityid==activityid)):
            activity.name = data['name']
            activity.statdate = data['startdate']
            activity.duration = data['duration']
            activity.completed = data['completed']
            db.session.add(activity)
        
        if db.session.query(db.exists().where(models.Event.activityid==activityid)):
            
            event.starttime = data['starttime']
            event.endtime = data['endtime']
            event.venue = data['endtime']
            db.session.add(event)
            
        db.commit()
        
    if db.session.query(db.exists().where(models.Event.activityid==activityid)).scalar():
        return render_template('event.html', event=event, total=total, allocation=allocation)
    else:
        return render_template('activity.html', activity=activity, total=total, allocation=allocation)

@app.route('/api/<activityid>',methods = ['GET','POST'])
@login_required
def activityinfo(activityid):
    
    activity = models.Activity.query.filter_by(activityid = activityid).first()
    
    if request.method == 'GET':
        
        event = models.Event.query.filter_by(activityid = activityid).first()
        total = activitytotal(activityid)
        allocation = activityallocation(activityid,total)
        
        if db.session.query(db.exists().where(models.Event.activityid==activityid)):
            data = {'name':event.name, 'startdate':event.startdate,'duration':event.duration,'completed':event.completed, 'starttime': event.starttime, 'endtime': event.endtime, 'venue': event.venue, 'totalcost': total, 'allocation': allocation}
            
        else:
        
            data = {'name':activity.name, 'startdate':activity.startdate,'duration':activity.duration,'completed':activity.completed}
            
        out = {'error':None, 'data':data, 'message':'Success'}
        
        return jsonify(out)
        
@app.route('/api/<activityid>/resources', methods = ['GET','POST'])
@login_required
def resourcelist(activityid):
    
    resList = db.session.query(models.Resource, models.Uses).join(models.Uses, models.Resource.resourceid == models.Uses.resourceid).filter(models.Uses.activityid == activityid).all()
    
    if request.method == 'GET':
        h = []
        m = []
        
        for resource in resList:
            
            human = models.HumanResource.query.filter_by(resourceid=resource.Resource.resourceid).first()
            
            if db.session.query(db.exists().where(models.HumanResource.resourceid==resource.Resource.resourceid)).scalar():
                
                h.append({'name':human.name, 'duration':human.duration, 'rate':human.rate, 'total': human.duration * human.rate})
            
            else:
                
                material = models.MaterialResource.query.filter_by(resourceid=resource.Resource.resourceid).first()
                m.append({'name':material.name,'qty':material.qty, 'unitcost':material.unitcost, 'total': material.unitcost * material.qty})
        
        data = {'human':h,'material':m}
        out = {'error':None, 'data':data, 'message':'Success'}
        
        return jsonify(out)
        
@app.route('/<activityid>/resources/new',methods=['GET','POST'])
@login_required
def newresource(activityid):
    
    if request.method == 'POST':
        data = request.form
        
        print (data,sys.stderr)
        
        name = data['name']
        resid = genID()
        
        if data['type']=='HumanResource':
            duration = data['duration']
            rate = data['rate']
            res = models.HumanResource(resourceid=resid,name=name,duration=duration,rate=rate)
            db.create_all()
            db.session.add(res)
            
        elif data['type']=='MaterialResource':
            qty = data['qty']
            unitcost = data['unitcost']
            res = models.MaterialResource(resourceid=resid,name=name,qty=qty,unitcost=unitcost)
            db.create_all()
            db.session.add(res)
        else:
            abort(400)
        
        uses = models.Uses(activityid=activityid,resourceid=resid)
        db.session.add(uses)
        db.session.commit()
        
        return redirect(url_for('activity',activityid=activityid))
        
    return render_template('newresource.html',activityid=activityid)
        
'''FILE MANAGEMENT'''
        
@app.route('/api/<titleid>/files', methods=['GET'])
@login_required
@login_required
def files(titleid):
    
    #return redirect('file://'+app.config["SERVER_NAME"]+'/'+app.config['UPLOAD_FOLDER']+'/'+titleid)
    
    return redirect(static_folder)
        
@app.route('/<titleid>/files/add', methods=['GET','POST'])
@login_required
def addfile(titleid):
    current = models.Phase.query.join(models.Has, models.Phase.phaseid == models.Has.phaseid).add_columns(models.Phase.phaseid).filter_by(models.Has.titleid == titleid,models.Phase.current == True).first
    owns = db.session.query(db.exists().where(models.Owns.userid==current_user.userid,models.Owns.phaseid==current.phaseid))
    
    file_folder = app.config['UPLOAD_FOLDER']
    
    if request.method == 'POST' and owns:
        
        data = request.get_jdon(force=True)
        name = data['name']
        version = data['version']
        
        file = request.files['file']
        filename = secure_filename(name+'_'+verrsion)
        file.save(os.path.join(file_folder+'/'+titleid, filename))
        
    return render_template('submitfile.html')
    
@app.route('/api/<titleid>/files/<file>/delete',methods=['DELETE'])
@login_required
def deletefile(titleid,file):
    current = models.Phase.query.join(models.Has, models.Phase.phaseid == models.Has.phaseid).add_columns(models.Phase.phaseid).filter_by(models.Has.titleid == titleid,models.Phase.current == True).first
    owns = db.session.query(db.exists().where(models.Owns.userid==current_user.userid,models.Owns.phaseid==current.phaseid))
    
    if request.method == 'DELETE' and owns and current_user.role in ['GeneralManager','LeadEditor']:
        
        path  = app.config['UPLOAD_FOLDER']+'/'+titleid+'/'+file
        os.remove(path)
        
        out = {'error':None, 'data':{}, 'message':'Success'}
        
        return jsonify(out)
        
        
@app.route('/api/<titleid>/<file>',methods=['GET'])
@login_required
def download(titleid,file):
    
    if request.method  == 'GET':
        
        uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER']+'/'+titleid)
        return send_from_directory(directory=uploads, filename=file)
        

###
# The functions below should be applicable to all Flask apps.
###

@login_manager.user_loader
def load_user(user_id):
    if db.session.query(db.exists().where(models.Users.userid == user_id)).scalar():
        return  models.Users.query.filter_by(userid=user_id).first()
    else:
        return None

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
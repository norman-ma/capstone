from . import db

class Users(db.Model):
    __table_args__ = {'extend_existing': True} 
    userid =  db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    role = db.Column(db.String(80))
    email = db.Column(db.String(80))
    auth = db.relationship('Authentication', backref='Users',lazy='select',uselist=False)
    owns = db.relationship('Owns',backref='Users',lazy='select')
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.userid)  # python 2 support
        except NameError:
            return str(self.userid)  # python 3 support

    def __repr__(self):
        return '<Users %r>' % (self.firstname)

class Authentication(db.Model):
    __table_args__ = {'extend_existing': True} 
    userid = db.Column(db.Integer, db.ForeignKey(Users.userid), primary_key=True)
    username = db.Column(db.String(80),unique=True)
    hash = db.Column(db.Text)
    salt = db.Column(db.String(80))

class Phase(db.Model):
    __table_args__ = {'extend_existing': True} 
    phaseid = db.Column(db.Integer,primary_key=True)
    budget = db.Column(db.Integer)
    stage = db.Column(db.String(80))
    current = db.Column(db.Boolean)
    owns = db.relationship('Owns',backref='Phase',lazy='select')
    consists_of = db.relationship('Consists_Of',backref='Phase',lazy='select')
    includes = db.relationship('Includes',backref='Phase',lazy='select')
    has = db.relationship('Has',backref='Phase',lazy='select')

class Owns(db.Model):
    __tablename__ = 'owns'
    __table_args__ = (db.PrimaryKeyConstraint('userid', 'phaseid'),{'extend_existing':True})
    userid = db.Column(db.Integer,db.ForeignKey(Users.userid))
    phaseid = db.Column(db.Integer,db.ForeignKey(Phase.phaseid))

class Activity(db.Model):
    activityid = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(80))
    startdate = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    completed = db.Column(db.Boolean)
    uses = db.relationship('Uses',backref='Activity',lazy='select')
    consists_of = db.relationship('Consists_Of',backref='Activity',lazy='select')

class Event(Activity):
    activityid = db.Column(db.Integer,db.ForeignKey(Activity.activityid),primary_key=True)
    starttime = db.Column(db.Time)
    endtime = db.Column(db.Time)
    venue = db.Column(db.String(80))

class Consists_Of(db.Model):
    __tablename__ = 'consists_of'
    __table_args__ = (db.PrimaryKeyConstraint('phaseid', 'activityid'),)
    phaseid = db.Column(db.Integer,db.ForeignKey(Phase.phaseid))
    activityid = db.Column(db.Integer,db.ForeignKey(Activity.activityid))

class Resource(db.Model):
    resourceid = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(80))
    uses = db.relationship('Uses',backref='Resource',lazy='select')

class HumanResource(Resource):
    resourceid = db.Column(db.Integer,db.ForeignKey(Resource.resourceid),primary_key=True)
    duration = db.Column(db.Integer)
    rate = db.Column(db.Float)

class MaterialResource(Resource):
    resourceid = db.Column(db.Integer,db.ForeignKey(Resource.resourceid),primary_key=True)
    qty = db.Column(db.Integer)
    unitcost = db.Column(db.Float)

class Uses(db.Model):
    __tablename__ = 'uses'
    __table_args__ = (db.PrimaryKeyConstraint('activityid', 'resourceid'),)
    activityid = db.Column(db.Integer,db.ForeignKey(Activity.activityid))
    resourceid = db.Column(db.Integer,db.ForeignKey(Resource.resourceid))

class Milestone(db.Model):
    milestoneid = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(80))
    date = db.Column(db.DateTime)
    includes = db.relationship('Includes',backref='Milestone',lazy='select')
    
    
class Includes(db.Model):
    __tablename__ = 'includes'
    __table_args__ = (db.PrimaryKeyConstraint('milestoneid', 'phaseid'),)
    phaseid = db.Column(db.Integer,db.ForeignKey(Phase.phaseid))
    milestoneid = db.Column(db.Integer,db.ForeignKey(Milestone.milestoneid))
 
class Title(db.Model):
    titleid = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(80))
    subtitle = db.Column(db.String(80))
    description = db.Column(db.Text)
    status = db.Column(db.String(80))
    belongs_to = db.relationship('Belongs_to',backref='Title',lazy='select')
    by = db.relationship('By',backref='Title',lazy='select')
    publishing = db.relationship('Publishing',backref='Title',lazy='select')
    sales = db.relationship('Sales',backref='Title',lazy='select')

class Has(db.Model):
    __tablename__ = 'has'
    __table_args__ = (db.PrimaryKeyConstraint('titleid', 'phaseid'),)
    titleid = db.Column(db.Integer,db.ForeignKey(Title.titleid))
    phaseid = db.Column(db.Integer,db.ForeignKey(Phase.phaseid))

class Author(db.Model):
    authorid = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    by = db.relationship('By',backref='Author',lazy='select')
    
class By(db.Model):
    __tablename__ = 'by'
    __table_args__ = (db.PrimaryKeyConstraint('authorid', 'titleid'),)
    authorid = db.Column(db.Integer,db.ForeignKey(Author.authorid))
    titleid = db.Column(db.Integer,db.ForeignKey(Title.titleid))

class Category(db.Model):
    categoryid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    belongs_to = db.relationship('Belongs_to',backref='Category',lazy='select', primaryjoin="Category.categoryid==Belongs_to.categoryid")
    
class Belongs_to(db.Model):
    __tablename__ = 'belongs_to'
    __table_args__ = (db.PrimaryKeyConstraint('titleid', 'categoryid'),)
    titleid = db.Column(db.Integer,db.ForeignKey(Title.titleid))
    categoryid = db.Column(db.Integer,db.ForeignKey(Category.categoryid))

class Publishing(db.Model):
	titleid = db.Column(db.Integer,db.ForeignKey(Title.titleid), primary_key=True)
	isbn = db.Column(db.String(13),unique=True)
	width = db.Column(db.Integer)
	height = db.Column(db.Integer)
	pagecount = db.Column(db.Integer)
	pubdate = db.Column(db.DateTime)
  
class Sales(db.Model):
    titleid = db.Column(db.Integer,db.ForeignKey(Title.titleid), primary_key=True)
    totalsales = db.Column(db.Float)
    internationalsales = db.Column(db.Float)
    localsales = db.Column(db.Float)
    regionalsales = db.Column(db.Float)
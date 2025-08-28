from datetime import datetime 
from flask_sqlalchemy import SQLAlchemy
db =SQLAlchemy()
class User(db.model):
    _tablename_="users"
    id=db.Column (db.integer,primarykey=True)
    name=db.column(db.string(120))
    email=db.Column(db.string(255),unique=True)
    password_hash= db.Column(db.String(255))
    class Campaign(db.Model):
        _tablename_="campaigns"
id=db.column(db.integer,primary_key=True)
User_id=db.column(db.integer,db.Foreignkey("users.id"),nullable=True)
name =db.column(db.string(200),nullable=False)
budget = db.column(db.Float,default=0.0)
spend=db.column(db.Float,default=0.0)
cpc=db.column(db.float,default=5.0)
created_at=db.column(db.DateTime,default=datetime.utcnow)
clicks=db.relationship("Conversion",backref="campaign",lazy=True,cascade="all,delete-orphan")
conversions=db.relationship("Conveersion",backref="campaign",lazy=True,cascade="all,delete-orphan")
class Click(db.Model):
    _tablename_="clicks"
    id=db.column(db.integer,primary_key=True)
    campaign_id=db.column(db.integer,db.Foreignkey("campaigns.id"),nullable=False)
    timestamp=db.Column(db.DateTime,default=datetime.utcnow)
    id_address =db.Column(db.Strings(64))
    class Conversion(db.Model):
    _tablename_ = "conversions"
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_info = db.Column(db.String(255))

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # seed a default campaign if none exist (handy for demo)
        if Campaign.query.count() == 0:
            demo = Campaign(name="Demo Campaign", budget=1000.0, cpc=4.0)
            db.session.add(demo)
            db.session.commit()

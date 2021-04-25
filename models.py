from database import db
import datetime

class Event(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(200))
    text = db.Column("text", db.String(100))
    date = db.Column("date", db.String(50))
    # can create a foreign key; referencing the id variable in the User class, so that is why it is lowercase u
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"),nullable=False)
    comments = db.relationship("Comment", backref="event", cascade="all, delete-orphan",lazy=True)
    def __init__(self, title, text, date, user_id):
        self.title = title
        self.text = text
        self.date = date
        self.user_id = user_id

class User(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    first_name = db.Column("first_name", db.String(100))
    last_name = db.Column("last_name", db.String(100))
    email = db.Column("email", db.String(100))
    password = db.Column(db.String(255), nullable=False)
    events = db.Column("events", db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    # events = db.relationship("Event", backref="user", lazy=True)
    comments = db.relationship("Comment", backref="user",lazy=True)

    def __init__(self, first_name, last_name, email, password, events):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.events = events
        self.registered_on = datetime.date.today()

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.VARCHAR, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, content, event_id, user_id):
        self.date_posted = datetime.date.today()
        self.content = content
        self.event_id = event_id
        self.user_id = user_id

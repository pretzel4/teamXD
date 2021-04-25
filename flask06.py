# FLASK Tutorial 1 -- We show the bare bones code to get an app up and running
# Working branch
# imports
import os                 #os is used to get environment variables IP & PORT
from flask import Flask   #Flask is the web app that we will customize
from flask import render_template
from flask import request
from werkzeug.utils import redirect
from flask import redirect, url_for
from database import db
from models import Event as Event
from models import User as User
from forms import RegisterForm
from flask import session
from forms import LoginForm
from models import Comment as Comment
from forms import RegisterForm, LoginForm, CommentForm
import bcrypt

app = Flask(__name__)     # create an app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_event_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SE3155'
#  Bind SQLAlchemy db object to this Flask app
db.init_app(app)

# Setup models
with app.app_context():
    db.create_all()   # run under the app context

events = {1: {'title': 'First event', 'text': 'This is my first event', 'date': '10-1-2020'},
             2: {'title': 'Second event', 'text':'This is my second event', 'date': '10-2-2020'},
             3: {'title': 'Third event', 'text': 'This is my third event', 'date': '10-3-2020'}}

@app.route('/events')
def get_events():

    if(session.get('user')):
        my_events = db.session.query(Event).filter_by(user_id=session['user_id']).all()
        return render_template('events.html', events=my_events, user=session['user'])
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form['email']).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = the_user.first_name
            session['user_id'] = the_user.id
            # render view
            return redirect(url_for('get_events'))

        # password check failed
        # set error message to alert user
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)

@app.route('/events/<event_id>')
def get_event(event_id):

    if session.get('user'):

        my_event = db.session.query(Event).filter_by(id=event_id,user_id=session['user_id']).one()
        form = CommentForm()
        return render_template('event.html', event=my_event, user=session['user'], form=form)
    else:
        return redirect(url_for('login'))

@app.route('/events/edit/<event_id>', methods=['GET', 'POST'])
def update_event(event_id):
    if session.get('user'):
        # check method used for request
        if request.method == 'POST':
            # get title data
            title = request.form['title']
            # get event data
            text = request.form['eventText']
            event = db.session.query(Event).filter_by(id=event_id)
            # update event data
            event.title = title
            event.text = text
            # update event in DB
            db.session.add(event)
            db.session.commit()

            return redirect(url_for('get_events'))
        else:


            # retrieve event from database
            my_event = db.session.query(Event).filter_by(id=event_id).one()

            return render_template('new.html', event=my_event, user=session['user'])
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # check if a user is saved in session
    if session.get('user'):
        session.clear()

    return redirect(url_for('index'))

@app.route('/events/delete/<event_id>',methods=['POST'])
def delete_event(event_id):
    if session.get('user'):
        # retrieve event from database
        my_event = db.session.query(Event).filter_by(id=event_id).one()
        db.session.delete(my_event)
        db.session.commit()

        return redirect(url_for('get_events'))
    else:
        return redirect(url_for('login'))

@app.route('/events/new', methods=['GET', 'POST'])
def new_event():
    # check method used for request
    print('request method is', request.method)
    if session.get('user'):
        if request.method == 'POST':
            # get title data
            title = request.form['title']
            # get event data
            text = request.form['eventText']
            # create date stamp
            from datetime import date
            today = date.today()
            # format date mm/dd/yyyy
            today = today.strftime("%m-%d-%Y")
            # create new event entry
            newEntry = Event(title, text, today, session['user_id'])

            db.session.add(newEntry)

            db.session.commit()

            return redirect(url_for('get_events'))

        else:
            return render_template('new.html', user=session['user'])
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # salt and hash password
        h_password = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())
        # get entered user data
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        events_list = request.form['events']
        # create user model
        new_user = User(first_name, last_name, request.form['email'], h_password, events_list)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session['user'] = first_name
        session['user_id'] = new_user.id  # access id value from user model of this newly added user
        # show user dashboard view
        return redirect(url_for('get_events'))

    # something went wrong - display register view
    return render_template('register.html', form=form)

@app.route('/events/<event_id>/comment', methods=['POST'])
def new_comment(event_id):
    if session.get('user'):
        comment_form = CommentForm()
        # validate_on_submit only validates using POST
        if comment_form.validate_on_submit():
            # get comment data
            comment_text = request.form['comment']
            new_record = Comment(comment_text, int(event_id), session['user_id'])
            db.session.add(new_record)
            db.session.commit()

        return redirect(url_for('get_event', event_id=event_id))

    else:
        return redirect(url_for('login'))

# @app.route is a decorator. It gives the function "index" special powers.
# In this case it makes it so anyone going to "your-url/" makes this function
# get called. What it returns is what is shown as the web page
@app.route('/')
@app.route('/index')
def index():
    if session.get('user'):
        return render_template('index.html', user=session['user'])
    return render_template("index.html")


@app.route('/profile')
def profile():
     if session.get('user'):
        return render_template('profile.html', user=session['user'])
        return redirect(url_for('login'))




app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)

# To see the web page in your web browser, go to the url,
#   http://127.0.0.1:5000
# 127.0.0.1
# Event that we are running with "debug=True", so if you make changes and save it
# the server will automatically update. This is great for development but is a
# security risk for production.

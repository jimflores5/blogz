from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:unit2wrapup@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'yrtsimehc' 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref = 'owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request         #Run this function before calling any request handlers.
def require_login():
    allowed_routes = ['login', 'register', 'blog', 'index']

    if request.endpoint not in allowed_routes and 'username' not in session:      #Checks to see if the user is logged in.
        return redirect('/')

@app.route('/', methods=['GET','POST'])
def index():
    if 'username' in session:
        users = User.query.all() 
        return render_template('index.html', users = users, username = session['username'], active = True)
    else:
        users = User.query.all() 
        return render_template('index.html', users = users, active = False)

    return render_template('index.html', users = users, username = session['username'], active = True)

@app.route('/newpost', methods=['GET','POST'])
def newpost():
    owner = User.query.filter_by(username = session['username']).first() 

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if title == '':
            flash('Please enter a title.', 'error')
            return render_template('new_entry.html',title=title, body=body, active = True)
        if body == '':
            flash('Please submit a blog entry.', 'error')
            return render_template('new_entry.html',title=title, body=body, active = True)
        
        new_entry = Blog(title, body, owner)
        db.session.add(new_entry)
        db.session.commit()

        return redirect("/singlepost?id="+str(new_entry.id))

    return render_template('new_entry.html', username = session['username'], active = True)

@app.route('/singleUser', methods=['GET','POST'])
def single_user():

    if request.args:
        owner = request.args.get('id')
        user = User.query.filter_by(id = owner).first()
        blogs = Blog.query.filter_by(owner_id = owner).all()
        if 'username' in session:
            return render_template('singleUser.html',entries=blogs, user = user, username = session['username'], active = True)
        else:
            return render_template('singleUser.html',entries=blogs, user = user, active = False)

    owner = User.query.filter_by(username = session['username']).first() 
    blogs = Blog.query.filter_by(owner = owner).all()    #Get only rows (objects) from the db Blog table that belong to this user.

    return render_template('singleUser.html',entries=blogs, username = session['username'], active = True)

@app.route('/singlepost', methods=['GET','POST'])
def single_entry():
    if request.args:
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        author = User.query.filter_by(id = blog.owner_id).first()

    return render_template('single_entry.html',entry=blog, author = author, username = session['username'], active = True)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST': #When the user clicks the 'login' button
        username = request.form['username']   #Pull data from the login form fields.
        password = request.form['password']
        user = User.query.filter_by(username = username).first() #Pulls the user data from the db.  The FIRST entry with the matching email is pulled.
        if user and user.password == password:  #Checks if the user is in the db and typed in the correct password.
            session['username'] = username   #The 'session" function will allow the site to 'remember' that a user is logged in.
            return redirect('/newpost')
        elif not user:
            flash('Incorrect username.', 'error') 
            return render_template("login.html", username = '')
        elif user.password != password:
            flash('Incorrect password.', 'error') 
            return render_template("login.html", username = user.username)            

    return render_template("login.html")

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST': #When the user clicks the 'Register' button
        username = request.form['username']   #Pull data from the register form fields.
        password = request.form['password']
        verify = request.form['verify']

        if username == '':
            flash('Please enter a user name.', 'error')
            return render_template("signup.html")
        elif len(username)<3 or len(username)>20:
            flash('User name must be 3 - 20 characters long.', 'error')
            return render_template("signup.html", username = username)
        elif " " in username:
            flash('Username cannot contain spaces.', 'error')
            return render_template("signup.html", username = username)

        if password == '':
            flash('Please enter a password.', 'error')
            return render_template("signup.html", username=username)
        elif len(password)<3 or len(password)>10:
            flash('Password must be 3 - 10 characters long.', 'error')
            return render_template("signup.html", username = username, password='')
        elif " " in password:
            flash('Password cannot contain spaces.', 'error')
            return render_template("signup.html", username = username, password='')
        elif verify =='':
            flash('Please verify your password.', 'error')
            return render_template("signup.html", username = username, password=password)
        elif verify != password:
            flash('Passwords do not match.', 'error')
            return render_template("signup.html", username = username, password=password)

        existing_user = User.query.filter_by(username = username).first() #Pulls the user data from the db.  The FIRST entry with the matching email is pulled.
        if not existing_user:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username

            return redirect('/newpost')
        else:
            flash(existing_user.username + ' already registered.', 'error')
            return render_template("signup.html", username = '')

    return render_template("signup.html")

@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    del session['username']    #Forgets the user.
    return redirect('/blog')

@app.route('/blog', methods=['GET','POST'])
def blog():
    if 'username' not in session:
        users = User.query.order_by('username').all()
        blogs = Blog.query.all()
        return render_template('blog.html',users=users, blogs = blogs, active = False)
    else: 
        users = User.query.order_by('username').all()
        blogs = Blog.query.all()
        return render_template('blog.html',users=users, blogs = blogs, username = session['username'], active = True)

if __name__ == '__main__':
    app.run()
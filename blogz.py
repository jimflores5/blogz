from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:unit2wrapup@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['GET','POST'])
def index():
    
    return render_template('index.html')

@app.route('/newpost', methods=['GET','POST'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        title_error = ''
        body_error = ''

        if title == '':
            title_error = 'Please enter a title.'
        if body == '':
            body_error = 'Please submit a blog entry.'
        
        if title_error == '' and body_error == '':
            new_entry = Blog(title,body)
            db.session.add(new_entry)
            db.session.commit()

            return redirect("/singlepost?id="+str(new_entry.id))

        else:
            return render_template('new_entry.html',title=title, body=body,title_error=title_error,body_error=body_error)

    return render_template('new_entry.html')

@app.route('/blog', methods=['GET','POST'])
def blog_list():
    blogs=Blog.query.all()
    return render_template('blog.html',entries=blogs)

@app.route('/singlepost', methods=['GET','POST'])
def single_entry():
    if request.args:
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)

    return render_template('single_entry.html',entry=blog)

if __name__ == '__main__':
    app.run()
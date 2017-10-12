from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blogfrog8@localhost:8889/build-a-blog'
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
        new_entry = Blog(title,body)
        db.session.add(new_entry)
        db.session.commit()
        return redirect('/')
    
    return render_template('new_entry.html')

@app.route('/blog', methods=['GET','POST'])
def blog_list():
    blogs=Blog.query.all()
    return render_template('blog.html',entries=blogs)

#@app.route('/delete-task', methods=['POST'])
#def delete_task():

 #   task_id = int(request.form['task-id'])
  #  task = Task.query.get(task_id)
   # task.completed = True
    #db.session.add(task)
    #db.session.commit()

    #return redirect('/')

    #   titles=Blog.query.all()

if __name__ == '__main__':
    app.run()
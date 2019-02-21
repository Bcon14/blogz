from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref = 'username')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        

    def __repr__(self):
        return '<Username %r>' % self.username

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'register','index','/']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/signup', methods =['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        #TODO - validate user data
        if username == '':
            flash('Requires a username')
        if password == '':
            flash('Requires a password')
        if verify == '':
            flash('Requires a verify password')
        
        if password == verify:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                return redirect('/login')
            else:
                flash('Duplicate user')
        else:
            flash("Passwords dont match!")
    session['username'] = username
    return render_template('signup.html')



@app.route('/login', methods =['POST', 'GET'])
def login():
    username = request.form['username']
    password = request.form['password']
    username = User.query.filter_by(username=username).first()
    if username and username.password == password:
        session['username'] = username
        flash('Logged in')
        return redirect('/newpost')
    else:
        flash('Password is not vaild')
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blogs = Blog.query.all()
    blog_id = request.args.get('id')
    if not blog_id:
        return render_template('blog.html',blogs = blogs)
    else:
        blog = Blog.query.get(blog_id)
        blog_title = blog.title
        blog_body = blog.body
        return render_template('/blog_post.html', title=blog_title, body=blog_body)


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    username = request.form['username']
    password = request.form['password']
    owner = User.query.filter_by(username=username).first()

    return render_template('add_blog_form.html')


@app.route('/blog_post', methods=['POST'])
def blog_post():
    
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        if blog_title == '' or blog_body == '':
            return redirect('/newpost')
        else:
            new_blog = Blog(blog_title , blog_body, )
            db.session.add(new_blog)
            db.session.commit()
            return render_template('/blog_post.html', title=blog_title, body=blog_body)
        
@app.route('/', methods=['POST'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
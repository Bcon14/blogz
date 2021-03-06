from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'ys&zP3B'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref = 'owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password


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
    allowed_routes = ['login', 'register','index','/', 'signup']
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
            return redirect('/signup')
        if password == verify:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username , password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/blog')
            else:
                flash('Duplicate user')
                return redirect('/login')
        else:
            flash("Passwords dont match!")

    return render_template('signup.html')



@app.route('/login', methods =['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if username and user.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        else:
            flash('Password is not vaild')
        return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if 'user' in request.args:
        user_id = request.args.get('user')
        user = User.query.get(user_id)
        blogs_user = Blog.query.filter_by(owner=user).all()
        return render_template('singleUser.html', blogs=blogs_user, user=user)


    blogs = Blog.query.all()
    blog_id = request.args.get('id')
    if not blog_id:
        blog = Blog.query.filter_by()
        return render_template('blog.html',blogs=blogs)
    else:
        blog = Blog.query.get(blog_id)
        blog_title = blog.title
        blog_body = blog.body
        return render_template('/blog_post.html', title=blog_title, body=blog_body)


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
        return render_template('add_blog_form.html')


@app.route('/blog_post', methods=['POST'])
def blog_post():
    
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        
        if blog_title == '' or blog_body == '':
            return redirect('/newpost')
        else:
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(blog_title , blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return render_template('/blog_post.html', title=blog_title, body=blog_body)
        
@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    user_id = request.args.get('id')
    if not user_id:
        return render_template('index.html', users=users)
    else:
        user = User.query.get(user_id)
        blogs = Blog.query.filter_by(user=user)
        return render_template('index.html', blogs=blogs, user=user)



if __name__ == '__main__':
    app.run()
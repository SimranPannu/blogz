from flask import Flask, request, redirect, render_template, flash ,url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'key'


#Blog class
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(120))
    description = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title,description,owner):
       self.title = title
       self.description = description
       self.owner = owner

#User Class
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50),unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login','signup','index','blogs']
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash('Please log in first.')
        return redirect('/login')



@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    user_id = request.args.get('user') 

    return render_template('index.html', users = users)


@app.route('/newpost',methods=['POST', 'GET'])
def AddBlog(): 
    blog_title = ""
    blog_description = ""
    title_error =""
    description_error =""

    owner = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        blog_title= request.form['blog_title']
        blog_description=request.form['blog_description']
        
         
        if blog_title =="":
            title_error = "Please enter the title of your blog!"
        if blog_description =="":
            description_error = "Please enter the description for your blog!"
    if blog_title != "" and blog_description !="":
        new_blog=Blog(blog_title,blog_description,owner)
        db.session.add(new_blog)
        db.session.commit()
        #blog_id = Blog.query.order_by(Blog.id.desc()).first()
        user=owner
        return redirect('/blog?id={id}&user={user}'.format(id=new_blog.id,user=user.username))
        

            
            
    return render_template('newpost.html', title = "Add a new post", blog_title=blog_title, blog_description = blog_description, title_error=title_error, description_error=description_error)

@app.route('/login', methods=['POST', 'GET'])
def login():
    username = ""
    password = ""
    username_error = ""
    password_error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username = username).first()
        
        if not existing_user:
            username_error = "User does not exist."
        if username == "":
                username_error = "Please enter your username."

        if password == "":
            password_error = "Please enter your password."

        if existing_user:
            if existing_user.password == password:
                session['username'] = existing_user.username
                return redirect('/newpost')
            else:
                password_error="password does not match,try again"

    return render_template('login.html', username = username, username_error = username_error, password_error = password_error)


@app.route('/signup', methods=['POST','GET'])
def signup():
    username= ""
    password= ""
    verify = ""
    password_error = ""
    username_error = ""
    verify_error = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_username = User.query.filter_by(username=username).first()
        print(username)

        #validation

        if "" in username:
            username_error= "Username cannot be blank"
        elif len(username)<3:
            username_error ="Name must be atleast 3 characters long"
        else:
            username_error= ""

        #password
        if "" in password:
            password_error = "Password cannot be blank"
        elif len(password)<3:
            password_error ="Password must be 3 characters long"
        else:
            password_error =""

        if "" in verify:
            verify_error="Field cannot be blank."
        elif password != verify:
             password_error = "Passwords must match."
             verify_error = "Passwords must match."
        else:
            verify_error=""

        if not username_error and not password_error and not verify_error:    
            if not existing_username:
                new_user = User(username,password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                username_error = "Username already exists."

    return render_template('signup.html',username=username, password_error=password_error, username_error=username_error, verify_error=verify_error)


@app.route("/blog", methods=['GET'])
def blogs():
    blog_id = request.args.get('id')
    #user_id = request.args.get('user')
    
    # Recent blog posts order to top.
    blog = Blog.query.order_by(Blog.id.desc()).all()
    #if session:
        #user = User.query.filter_by(username = session['username']).first()

    if blog_id :
        
        blogs = Blog.query.filter_by(id= blog_id)
        
        return render_template('post.html', blogs = blogs,blog_id=blog_id)

    if "user" in request.args :
        user_id = request.args.get('user')
        blog = Blog.query.filter_by(owner_id = user_id).all()
        #user = User.query.filter_by(username = author).first()
        #blog = user.blogs
        return render_template('singleUser.html',  blog = blog,user_id=user_id)
    
    return render_template('blog.html',title="Blogz!",blog=blog)


@app.route("/logout", methods=['POST','GET'])
def logout():
    del session['username']
    return redirect('/blog')   
    
if __name__ == '__main__':
    app.run()

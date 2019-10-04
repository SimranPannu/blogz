from flask import Flask, request, redirect, render_template, flash ,url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'key'

blogs = []
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(120))
    description = db.Column(db.String(1000))

    def __init__(self, title, description):
       self.title = title
       self.description = description

@app.route('/newpost',methods=['POST', 'GET'])
def AddBlog():
    blog_title = ""
    blog_description = ""
    title_error =""
    description_error =""
    if request.method == 'POST':
        blog_title= request.form['blog_title']
        blog_description=request.form['blog_description']
        
         
        if blog_title =="":
            title_error = "Please enter the title of your blog!"
        if blog_description =="":
            description_error = "Please enter the description for your blog!"
    if blog_title != "" and blog_description !="":
            new_blog=Blog(blog_title,blog_description)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/?id={id}'.format(id=new_blog.id))
            
            
    return render_template('newpost.html', title = "Add a new post", blog_title=blog_title, blog_description = blog_description, title_error=title_error, description_error=description_error)


@app.route('/', methods=['POST', 'GET'])
def index():
    
    blog_id = request.args.get('id')

    if blog_id:
        blogs=Blog.query.filter_by(id=blog_id).first() 
        return render_template('post.html',title="Build-a-blog!",blogs=blogs)
    else:
        blogs = Blog.query.order_by(Blog.id).all()
        return render_template('blog.html',title="Build-a-blog!",blogs = blogs)


if __name__ == '__main__':
    app.run()

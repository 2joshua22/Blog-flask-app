from flask import Flask, render_template,url_for,flash,request,redirect
from forms import UserForm,LoginForm,PostForm,NameForm,PasswordForm, SearchForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin,login_user,current_user,logout_user,LoginManager,login_required 
from flask_ckeditor import CKEditor
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
import os
import confidential

app=Flask(__name__)

app.config['SECRET_KEY']=confidential.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI']=confidential.SQLALCHEMY_DATABASE_URI_mysql
app.config["UPLOAD_FOLDER"]="C:/_Web development/_Projects/blog-flask-app/static/images"

db=SQLAlchemy(app)
migrate=Migrate(app,db)
app.app_context().push()
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"
ckeditor=CKEditor(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.context_processor
def base():
    form=SearchForm()
    return dict(Form=form,Admin_id=confidential.admin_id)

@app.route('/admin')
@login_required
def admin():
    if current_user.id==confidential.admin_id:
        userlist=Users.query.order_by(Users.date_added)
        return render_template("admin.html",Userlist=userlist)
    else:
        flash("You are not authorized as admin here")
        return redirect(url_for('dashboard'))

@app.route('/search',methods=["POST"])
def search():
    posts=Post.query
    form=SearchForm()
    if form.validate_on_submit():
        searched=form.searched.data
        posts=posts.filter(Post.content.like("%"+searched+"%"))
        posts=posts.order_by(Post.title).all()
        return render_template('search.html',Form=form,Searched=searched,Posts=posts)

# @app.route('/random')
# def time():
#     return {"date":datetime.utcnow()}

# @app.route('/time')
# def time_info():
#     data={"date":datetime.utcnow(),"day":datetime.utcnow().day,"month":datetime.today().month,"year":datetime.today().year,"time_zone":datetime.today().tzinfo,"hour":datetime.today().hour,"minute":datetime.today().minute,"second":datetime.today().second,"week_day":datetime.utcnow().isoweekday()}
#     return data

@app.route('/about',methods=['GET','POST'])
def about():
    return render_template('about.html')

# @app.route('/test/',methods=['GET','POST'])
# def test_password():
#     email=None
#     password=None
#     password_check=None
#     passed=None
#     form=PasswordForm()
#     if form.validate_on_submit():
#         email=form.email.data
#         password=form.password_hash.data
#         form.email.data=''
#         form.password_hash.data=''
        
#         password_check=Users.query.filter_by(email=email).first()
#         passed=check_password_hash(password_check.password_hash,password)
    
#     return render_template('test_password.html',Email=email,Password=password, Form=form, Password_check=password_check,Passed=passed)

# @app.route('/user')
# def user1():
#     name="sam joshua"
#     html="<strong>Hello</strong>"
#     l=[1,2,3,"a"]
#     return render_template("user1.html",L=l)

@app.route('/')
# def index():
#     return "<h1>Hello World<h1>"
def index():
    # raise Exception("Can't connect to database")
    return render_template('index.html')

# @app.route('/user/<name>')
# # def user(name):
# #     return "<h1>Hello {}!!!</h1>".format(name)
# def user(name):
#     return render_template("user.html",Name=name)


@app.route('/user/add',methods=['GET','POST'])
def add_user():
    name=None
    form=UserForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(email=form.email.data).first() #each user should have unique email id. 
        if user==None:
            hashed_password=generate_password_hash(form.password_hash.data)
            user=Users(username=form.username.data,name=form.name.data,email=form.email.data,about_author=form.about_author.data,password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
        flash("Your Response is saved successfully!!!")
        return redirect(url_for('login'))  
    return render_template('user_add.html',Form=form)

@app.route('/update/<int:id>',methods=['GET','POST'])
@login_required
def update(id):
    form=UserForm()
    user_to_update=Users.query.get_or_404(id)
    form.about_author.data=user_to_update.about_author
    if request.method=="POST":
        user_to_update.name=request.form["name"]
        user_to_update.email=request.form["email"]
        user_to_update.about_author=request.form["about_author"]
        user_to_update.username=request.form["username"]
        if request.files["profile_pic"]:
            form_profile_pic_data=request.files["profile_pic"]
            
            pic_filename=secure_filename(form_profile_pic_data.filename)
            pic_name=str(uuid.uuid1())+"_"+pic_filename
            saver=request.files["profile_pic"]
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'],pic_name))
            user_to_update.profile_pic=pic_name
            try:
                db.session.commit()
                flash("The User Details is Updated Successfully!!!") 
                return render_template("update.html",Form=form,User_to_update=user_to_update,id=id)
            except:
                db.session.commit()
                flash("Whoops, there is a problem... try again!") 
                return render_template("update.html",Form=form,User_to_update=user_to_update,id=id)
        else:
            db.session.commit()
            flash("The User Details is Updated Successfully!!!") 
            return render_template("update.html",Form=form,User_to_update=user_to_update,id=id)

    return render_template("update.html",Form=form,User_to_update=user_to_update,id=id)

@app.route('/delete/<id>')
@login_required
def delete(id):
    if id==current_user.id:
        user=Users.query.get_or_404(id)
        try:
            db.session.delete(user)
            db.session.commit()
            flash("The User is Deleted successfully!!!")
            return redirect(url_for('add_user'))
        except:
            flash("Whoops, there is a problem... Try again!") 
            return redirect(url_for('add_user'))
    if current_user.id==confidential.admin_id:
        user=Users.query.get_or_404(id)
        try:
            db.session.delete(user)
            db.session.commit()
            flash("The User is Deleted successfully!!!")
            return redirect(url_for('admin'))
        except:
            flash("Whoops, there is a problem... Try again!") 
            return redirect(url_for('admin'))
    else:
        flash("Whoops, You can not Delete Other's Profile") 
        return redirect(url_for('dashboard'))    

@app.route('/login',methods=["GET","POST"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(username=form.username.data).first()
        if user: 
            if check_password_hash(user.password_hash,form.password.data):
                login_user(user)
                flash("Logged in Successfully")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Paassword, Try again...")
        else:
            flash("The user not found, Try again...")
    return render_template("login.html",Form=form)

@app.route('/dashboard',methods=["GET","POST"])
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route('/logout',methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    flash("Your are Successfully Logged out!!!")
    return redirect(url_for('login'))

@app.route('/add-post',methods=['POST','GET'])
@login_required
def add_post():
    form=PostForm()
    if form.validate_on_submit():
        poster=current_user.id
        post=Post(title=form.title.data,content=form.content.data,poster_id=poster,slug=form.slug.data)
        db.session.add(post)
        db.session.commit()
        flash("Blog Post is Posted Successfully!!!")
        return redirect(url_for('posts'))
    return render_template("add_post.html",Form=form)

@app.route('/posts')
def posts():
    posts=Post.query.order_by(Post.date_posted)
    return render_template('posts.html',Posts=posts)

@app.route('/post/<int:id>')
def post(id):
    post=Post.query.get_or_404(id)
    return render_template('post.html',Post=post)

@app.route('/post/edit/<int:id>',methods=["GET","POST"])
@login_required
def edit_post(id):
    admin=Users.query.get_or_404(confidential.admin_id)
    post=Post.query.get_or_404(id)
    form=PostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        post.slug=form.slug.data
        post.content=form.content.data
        db.session.commit()
        flash("Post Has Been Updated!")
        return redirect(url_for('post',id=post.id))
    if current_user.id==post.poster.id or admin.is_authenticated:
        form.title.data=post.title
        form.slug.data=post.slug
        form.content.data=post.content
        return render_template('edit_post.html',Form=form,Id=id)
    else:
        flash("You are not Authorized to Edit Other's post")
        return redirect(url_for('posts'))

@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    admin=Users.query.get_or_404(confidential.admin_id)
    post_to_delete=Post.query.get_or_404(id)
    if current_user.id==post_to_delete.poster.id or admin.is_authenticated:
        try:    
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("The Block Post is Deleted Successfully!")
        except:
            flash("Error during The Blog deletion, Try Again...")
    else:
        flash("You are not authorized to delete other posts!!!")
    return redirect(url_for('posts'))
 
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"),404

@app.errorhandler(500)
def InternalServerError(error):
    return render_template("500.html"),500

class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(250))
    content=db.Column(db.Text())
    date_posted=db.Column(db.DateTime,default=datetime.utcnow)
    slug=db.Column(db.String(250))
    poster_id=db.Column(db.Integer,db.ForeignKey("users.id"))

class Users(db.Model, UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(40),nullable=False,unique=True)
    name=db.Column(db.String(40),nullable=False)
    email=db.Column(db.String(40),nullable=False,unique=True)
    about_author=db.Column(db.Text(),nullable=False)
    date_added=db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic=db.Column(db.String(300),nullable=True)
    posts=db.relationship('Post',backref='poster')

    password_hash=db.Column(db.String(120))

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute!")
    
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)
    
    def verify_password(self,password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return '<Name %r>' % self.name

if __name__=="__main__":
    app.run(debug=True)


from flask import Flask, render_template,redirect, session,request, url_for
from flask_sqlalchemy import SQLAlchemy
import json
import os
from werkzeug.utils import secure_filename


with open('config.json','r') as c:
    params = json.load(c)["params"]
local_server = False
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]
db = SQLAlchemy(app)
app.config['UPLOAD_PATH'] = 'static/uploads'

class Frontend(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    # val = db.Column(db.Integer)
    skill = db.Column(db.String(80), unique=True, nullable=False)
    level = db.Column(db.String(80), unique=True, nullable=False)

class Backend(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    # val = db.Column(db.Integer)
    skill = db.Column(db.String(80), unique=True, nullable=False)
    level = db.Column(db.String(80), unique=True, nullable=False)




@app.route("/")
def home():
    path = 'static/uploads/'
    uploads = sorted(os.listdir(path), key=lambda x: os.path.getctime(path+x))        # Sorting as per image upload date and time
    print(uploads)
    #uploads = os.listdir('static/uploads')
    uploads = ['uploads/' + file for file in uploads]
    uploads.reverse()


    backend = Backend.query.all()
    frontend = Frontend.query.all()
    return render_template("index.html",backends=backend,frontends = frontend,uploads=uploads, params=params)


@app.route("/admin", methods=["GET","POST"])
def login():
    if "user" in session and session['user']==params['admin_user']:
        return render_template("dashboard/index.html", params=params)

    if request.method=="POST":
        username = request.form.get("uname")
        print(username)
        userpass = request.form.get("upass")
        print(userpass)
        if username==params['admin_user'] and userpass==params['admin_password']:
            # set the session variable
            session['user']=username
            return render_template("dashboard/index.html", params=params)

        else:
            return "<h1 style='color: red;'>YOU ARE NOT ALLOWED!</h1>"
    else:
        return render_template("login.html", params=params)

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect("/admin")

@app.route("/backend", methods=["POST","GET"])
def backend():
     if "user" in session and session['user']==params['admin_user']:
        if request.method == "POST":
            skill = request.form['skill']
            level = request.form['level']
            entry = Backend(skill=skill,level=level)
            db.session.add(entry)
            db.session.commit()
        post = Backend.query.all()
        return render_template("dashboard/backend.html",posts=post)
     else:
        return render_template("not.html")
@app.route("/frontend", methods=["POST","GET"])
def frontend():
     if "user" in session and session['user']==params['admin_user']:
        if request.method == "POST":
            skill = request.form['skill']
            level = request.form['level']
            entry = Frontend(skill=skill,level=level)
            db.session.add(entry)
            db.session.commit()
        post = Frontend.query.all()
        return render_template("dashboard/frontend.html",posts=post)

@app.route("/upload", methods=['GET','POST'])
def upload_project():
    if "user" in session and session['user']==params['admin_user']:
        if request.method == 'POST':
            f = request.files['file']
            print(f.filename)
            #f.save(secure_filename(f.filename))
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            return redirect("/posts")
    # return render_template("dashboard/posts.html", params=params)
    return render_template('not.html')

@app.route("/del/frontend/<sno>")
def del_frontend(sno):
    if "user" in session and session['user']==params['admin_user']:

#           obj = User.query.filter_by(id=123).one()
#           session.delete(obj)
#           session.commit()
        var = Frontend.query.filter_by(sno=sno).one()
        db.session.delete(var)
        db.session.commit()
        return redirect("/frontend")

@app.route("/del/backend/<sno>")
def del_backend(sno):
    if "user" in session and session['user']==params['admin_user']:
        var = Backend.query.filter_by(sno=sno).one()
        db.session.delete(var)
        db.session.commit()
        return redirect("/backend")

@app.route('/posts', methods=["GET","POST"])
def main_post():
    if "user" in session and session['user']==params['admin_user']:
        return render_template("dashboard/post.html")


if __name__ == "__main__":
    app.run(debug=True)
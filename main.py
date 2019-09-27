from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json, os, math
from flask_mail import Mail
from werkzeug import secure_filename 

with open('./templates/config.json', 'r') as c:
    params = json.load(c) ["params"]
local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
MAIL_SERVER = 'smtp.gmail.com',
MAIL_PORT = '465',
MAIL_USE_SSL = True, 
MAIL_USERNAME = params['gmail-user'],
MAIL_PASSWORD = params['gmail-pass']

	)
mail = Mail(app)
if(local_server):
	app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
	app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]


 
db = SQLAlchemy(app)

class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),  nullable=False)
    email = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(120),  nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
   
class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50),  nullable=False)
    tag_line = db.Column(db.String(50),  nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120),  nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img = db.Column(db.String(12), nullable=True)
    





@app.route('/')
def home():
	post = Post.query.filter_by().all()
	last = math.ceil(len(post)/int(params['num_of_post']))
	page = request.args.get('page')
	
	if(not str(page).isnumeric()):
		page = 1
	page = int(page)	
	post = post[(page-1)*int(params['num_of_post']):(page-1)*int(params['num_of_post'])+int(params['num_of_post'])]	
	if(page==1):
		prev = "#"
		next = "/?page="+ str(page+1)
	elif(page==last):
		prev = "/?page="+ str(page - 1)
		next = "#"
	else:
		prev = "/?page="+ str(page - 1)
		next = "/?page="+ str(page+1)
		
		

		
	
	#[0:params['num_of_post']]
	return render_template('index.html', params=params,post=post, prev=prev,next=next)




@app.route('/login', methods=['GET','POST'])
def login():
	print('ligin1')
	if('user' in session and session['user'] == params['admin_user']):
		post = Post.query.all()
		print('ligin2')
		return render_template('admin_dash.html',params=params,post=post)

	if(request.method == 'POST'):
		print('login in process')
		username = request.form.get('username')
		upass = request.form.get('userpass')
		post = Post.query.all()
		if(username == params['admin_user'] and upass == params['admin_pass']):
			session['user'] = username
			return render_template('admin_dash.html',params=params,post=post)
	return render_template('login.html', params=params)

@app.route('/about')
def about():
	return render_template('about.html',params=params)

@app.route('/contact', methods=['GET','POST'])
def contact():
	print('hi')
	if(request.method == 'POST'):
		print('hipost')
		name = request.form.get('name')
		email = request.form.get('email')
		phone_num = request.form.get('phone_num')
		message = request.form.get('message')
		entry = Contact(name=name,email=email,phone_num=phone_num,message=message,date=datetime.now())
		db.session.add(entry)
		db.session.commit()
		mail.send_message('New message from ' + name,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = message + "\n" + phone_num + email
                          )
	return render_template('contact.html',params=params)	

@app.route('/post/<string:post_slug>', methods=['GET'])
def post_route(post_slug):
	print(post_slug)
	post = Post.query.filter_by(slug=post_slug).first()
	print(post)
	return render_template('post.html',params=params, post=post)	


@app.route('/edit/<string:sno>', methods=['GET','POST'])
def edit(sno):
	print("Enter_1")
	if('user' in session and session['user'] == params['admin_user']):
		if request.method == 'POST':
			print("Enter_2")
			box_tag_line = request.form.get('tag_line')
			box_title = request.form.get('title')
			box_slug = request.form.get('slug')
			box_content = request.form.get('content')
			box_image = request.form.get('image')
			box_date = datetime.now()
			print('########')
			print(box_title,box_tag_line,box_slug,box_content,box_image)

			if(sno == '0'):
				print("Enter_3") 
				edited_post = Post(title=box_title,tag_line=box_tag_line,slug=box_slug,content=box_content,date=datetime.now(),img=box_image)
				print(edited_post)
				db.session.add(edited_post)
				db.session.commit()
			else:
				print(sno)
				post = Post.query.filter_by(sno=sno).first()
				print(post)
				post.title = box_title
				post.tag_line = box_tag_line
				post.slug = box_slug
				post.content = box_content
				post.img = box_image
				post.date = box_date
				db.session.commit()
				return redirect('/edit/'+sno)
		post = Post.query.filter_by(sno=sno).first()		
		return render_template('edit.html',params=params, post=post)

	
@app.route('/uploader', methods=['GET','POST'])
def uploader():
	if('user' in session and session['user'] == params['admin_user']):
		if request.method == 'POST':
			print('HELELEL')
			f = request.files['upload_file']
			f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename) ))
			return "Uploaded SuccessFull"

@app.route('/logout')
def logout():
	session.pop('user')	
	return redirect('/login')


@app.route('/delete/<string:sno>')
def delete(sno):
	if('user' in session and session['user'] == params['admin_user']):
		post = Post.query.filter_by(sno=sno).first()
		db.session.delete(post)
		db.session.commit()	
	return redirect('/login')

        

app.run(debug=True)
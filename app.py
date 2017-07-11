from flask import Flask, render_template, request, flash, session, redirect, url_for, send_file, send_from_directory
from dbconnect import connection
from flask_wtf import Form
from wtforms import StringField, BooleanField, validators, PasswordField
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
from functools import wraps
from flask_mail import Mail, Message


app = Flask(__name__)
app.config['SECRET_KEY'] = 'very very secret dont tell anyone lol' # for flask sessions and wtforms



class RegistrationForm(Form):
	username = StringField("Username", [validators.Length(min = 4, max = 20)])
	email = StringField("Email ID", [validators.Length(min = 6, max = 50)])
	password = PasswordField("Password", [validators.Required(), validators.EqualTo('confirm', message="Passwords must match.")])
	confirm = PasswordField("Confirm Password")
	accept_tos = BooleanField("I accept the <a href=\"tos\">terms of service</a>.", [validators.Required()])



def login_required(f): # This is decorator. Else we could also include the below if else condition on every page where login is required
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash("You need to log in first.")
			return redirect(url_for('login'))
	return wrap




@app.route("/")
def index():
	return render_template("index.html")


@app.route("/file-downloads/")
def file_downloads():
	return render_template("downloads.html")

@app.route("/return-file/")
def return_file():
	return send_file("/Users/Dhruv/Desktop/learn-flask/static/try.png")




@app.route("/dashboard/")
def dashboard():
	return render_template("dashboard.html")




@app.route("/login/", methods=["POST","GET"])
def login():
	error = ''
	try:
		c, conn = connection()

		if request.method == "POST":

			x = c.execute("SELECT * FROM users WHERE username = (%s)", (thwart(request.form["username"]),))

			if int(x) == 0:
				error = 'username does not exist.'
				return render_template("login.html", error=error)

			dataAll = c.fetchone()
			print dataAll
			data = dataAll[2]

			if sha256_crypt.verify(request.form["password"], data):
				session["logged_in"] = True
				session["username"] = request.form["username"]

				flash("logged in now yay!")
				return redirect(url_for("dashboard"))

			else:
				error = 'invalid creds, try again.'

		conn.close()
		gc.collect()

		return render_template("login.html", error=error)

	except Exception, e:
		return str(e)




@app.errorhandler(404)
def page_not_found(e):
	return "sad, but not found :("




@app.route("/register/", methods = ["GET","POST"])
def register():
	try:
		form = RegistrationForm()

		if request.method == "POST" and form.validate():

			username = form.username.data
			email = form.email.data
			password = sha256_crypt.encrypt(str(form.password.data))
			c, conn = connection()
			x = c.execute("SELECT * FROM users WHERE username = (%s)", (thwart(username),))

			if int(x) > 0:
				flash("Username already exists.")
				c.close()
				conn.close()
				gc.collect()
				return render_template("register.html", form=form)

			else:
				c.execute("INSERT INTO users (username, password, email, tracking) VALUES (%s, %s, %s, %s)", (thwart(username), thwart(password), thwart(email), thwart("/introduction-to-python-programming/")))
				conn.commit() # saving the database after insertion of above row
				flash("Thanks for registering!")
				c.close()
				conn.close()
				gc.collect() # Garbage collection - reduces memory wastage

				# session is a dictionary
				session["logged_in"] = True
				session["username"] = username

				return redirect(url_for("dashboard"))

		return render_template("register.html", form=form)

	except Exception, e:
		return str(e)



@app.route("/logout/")
@login_required
def logout():
	session.clear()
	flash("you have been logged out.")
	gc.collect()
	return redirect(url_for("index"))



if __name__ == '__main__':
	app.run(debug=True)







	
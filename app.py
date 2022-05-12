import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_instructions")
def get_instructions():
    instructions = mongo.db.instructions.find()
    return render_template("instructions.html", instructions=instructions)


@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        # check if username exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username taken!")
            return redirect(url_for("sign_up"))

        signup = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(signup)

        # Create user session cookie
        session["user"] = request.form.get("username").lower()
        flash("Sign Up Successful!")
        return redirect(url_for("account", username=session["user"]))

    return render_template("signup.html")


@app.route("/signin", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        # Checks if username already exisits in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # Checks to see if hashed password matches the user input field
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(
                        request.form.get("username")))
                    return redirect(url_for(
                        "account", username=session["user"]))
            else:
                # Executes if password does not match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("sign_in"))

        else:
            # Executes if username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("sign_in"))

    return render_template("signin.html")


@app.route("/account/<username>", methods=["GET", "POST"])
def account(username):
    # fetches the session user's username from the database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("account.html", username=username)

    return redirect(url_for("signin"))


@app.route("/signout")
def sign_out():
    flash("You have been signed out successfully")
    session.pop("user")
    return redirect(url_for("sign_in"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP", "0.0.0.0"),
            port=int(os.environ.get("PORT", "5000")),
            debug=True)

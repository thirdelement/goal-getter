import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId #Enables rendering of ObjectID so we can find docs in MongoDB
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env #we are not pushing env.py to GitHub.  When in Heroku we need to only import
                            #env if the os can find an existing file path for the file itself.  Otherwise
                            #Heroku will throw an error.
app = Flask(__name__) #create a new instance of Flask stored in a variable call 'app'

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME") #grab db name
app.config["MONGO_URI"] = os.environ.get("MONGO_URI") # configure the connection string aka MONGO_URI
app.secret_key = os.environ.get("SECRET_KEY") # secret_key required for some functions in Flask

mongo = PyMongo(app) #set up an instance of PyMongo and add the 'app' into that using a constructor method.
                     #This is the Flask 'app' object defined above.  It's final step to ensure our Flask app is c
                     #communicating with MongoDB.
@app.route("/") #a routing is a string that when we attach to a URL will redirect to a particular function in our Flask app.
@app.route("/get_goals")
def get_goals():
    goals = list(mongo.db.goals.find())
    return render_template("goals.html", goals=goals)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #check if username already exists in dbe
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))
        
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "email": request.form.get("email").lower()
        }
        mongo.db.users.insert_one(register)

        #put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!") 
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #check if username exists in db
        existing_user = mongo.db.users.find_one({"username": request.form.get("username").lower()})

        if existing_user:
            #ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for("profile", username=session["user"]))
            else:
                #invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            #username doesn't exist
            flash("Incorrect username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    #grab the session users's username from the db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
    #if session cookie is truthy then render the page
        return render_template("profile.html", username=username)
    #if session cookie is not truthy (e.g. has been deleted)
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_goal", methods=["GET", "POST"])
# The POST method is needed to create a new goal
def add_goal():
    if request.method == "POST":
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        goal = {
            "goal_name": request.form.get("goal_name"),
            "target_date": request.form.get("target_date"), 
            "category_name": request.form.get("category_name"),
            "succeed_description": request.form.get("succeed_description"),
            "effort": request.form.get("effort"), 
            "created_by": session["user"]
        }
        mongo.db.goals.insert_one(goal)
        flash("Goal successfully added")
        return redirect(url_for("get_goals"))    
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_goal.html", categories=categories)


@app.route("/edit_goal/<goal_id>", methods=["GET", "POST"])
def edit_goal(goal_id):
    if request.method == "POST":
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        submit = {
            "goal_name": request.form.get("goal_name"),
            "target_date": request.form.get("target_date"), 
            "category_name": request.form.get("category_name"),
            "succeed_description": request.form.get("succeed_description"),
            "effort": request.form.get("effort"), 
            "created_by": session["user"]
        }
        mongo.db.goals.update({"_id": ObjectId(goal_id)}, submit)
        flash("Goal successfully updated")

    goal = mongo.db.goals.find_one({"_id": ObjectId(goal_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_goal.html", goal=goal, categories=categories)


@app.route("/delete_goal/<goal_id>")
def delete_goal(goal_id):
    mongo.db.goals.remove({"_id": ObjectId(goal_id)})
    flash("Task successfully deleted")
    return redirect(url_for("get_goals"))


@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


if __name__ == "__main__":                  #Tell our app how and where to run our app
    app.run(host=os.environ.get("IP"),      #use the hidden variables in the env.py file
            port=int(os.environ.get("PORT")), # convert port to an integer
            debug=True)                     #set debug to True so we can see errors.  Set to false at go live
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

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/get_goals")
def get_goals():
    goals = list(mongo.db.goals.find())
    return render_template("goals.html", goals=goals)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    goals = list(mongo.db.goals.find({"$text": {"$search": query}}))
    return render_template("goals.html", goals=goals)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #check if username already exists in dbe
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash(u"Username already exists", 'warning')
            return redirect(url_for("register"))
        
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
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
        existing_user = mongo.db.users.find_one({
            "username": request.form.get("username").lower()})

        if existing_user:
            #ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username").capitalize()))
                return redirect(url_for("profile", username=session["user"]))
            else:
                #invalid password match
                flash(u"Incorrect Username and/or Password", 'warning')
                return redirect(url_for("login"))

        else:
            #username doesn't exist
            flash(u"Incorrect Username and/or Password", 'warning')
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
        #grab the session user's username from the db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    goals = list(mongo.db.goals.find(
        {"created_by": session["user"]}).sort("_id", -1))

    if session["user"]:
        #if session cookie is truthy then render the page
        return render_template("profile.html", username=username, goals=goals)
        #if session cookie is not truthy (e.g. has been deleted)
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_goal", methods=["GET", "POST"])
def add_goal():
    is_complete = "checked" if request.form.get(
            "is_complete") else "unchecked"
    share = "unchecked" if request.form.get("share") else "checked"
    meet_goal = "checked" if request.form.get("meet_goal") else "unchecked"
    goal = {
            "goal_name": request.form.get("goal_name"),
            "target_date": request.form.get("target_date"), 
            "category_name": request.form.get("category_name"),
            "succeed_description": request.form.get("succeed_description"),
            "effort": request.form.get("effort"), 
            "previous_action": request.form.get("previous_action"),
            "confidence_level": request.form.get("confidence_level"),
            "holding_back_description": request.form.get(
                "holding_back_description"),
            "believe_description": request.form.get("believe_description"),
            "course_of_action": request.form.getlist("course_of_action"),
            "chosen_coa": request.form.get("course_of_action"),
            "target_date2": request.form.get("target_date2"),
            "meet_goal": meet_goal, 
            "obstacles": request.form.get("obstacles"),
            "what_support": request.form.get("what_support"),
            "how_support": request.form.get("how_support"),
            "likelihood": request.form.get("likelihood"),
            "share": share, 
            "is_complete": is_complete,
            "created_by": session["user"]
        }

    if request.method == "POST":
        mongo.db.goals.insert_one(goal)
        flash("Goal, Reality and Options added")
        return redirect(url_for('edit_goal', goal_id=goal[
                    "_id"]))  

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_goal.html", goal=goal, categories=categories)


@app.route("/edit_goal/<goal_id>", methods=["GET", "POST"])
def edit_goal(goal_id):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    is_complete = "checked" if request.form.get(
            "is_complete") else "unchecked"
    share = "checked" if request.form.get("share") else "unchecked"
    meet_goal = "checked" if request.form.get("meet_goal") else "unchecked"
    goal = mongo.db.goals.find_one({"_id": ObjectId(goal_id)})

    if request.method == "POST":
        submit = {"$set": {
            "goal_name": request.form.get("goal_name"),
            "target_date": request.form.get("target_date"), 
            "category_name": request.form.get("category_name"),
            "succeed_description": request.form.get("succeed_description"),
            "effort": request.form.get("effort"), 
             "previous_action": request.form.get("previous_action"),
            "confidence_level": request.form.get("confidence_level"),
            "holding_back_description": request.form.get(
                "holding_back_description"),
            "believe_description": request.form.get("believe_description"),
            "course_of_action": request.form.getlist("goal.course_of_action"),
            "chosen_coa": request.form.get("course_of_action"),
            "target_date2": request.form.get("target_date2"),
            "meet_goal": meet_goal, 
            "obstacles": request.form.get("obstacles"),
            "what_support": request.form.get("what_support"),
            "how_support": request.form.get("how_support"),
            "likelihood": request.form.get("likelihood"),
            "share": share, 
            "is_complete": is_complete,
            "created_by": session["user"]
        }}
        mongo.db.goals.update_one({"_id": ObjectId(goal_id)}, submit)

        if meet_goal == "unchecked":
            flash(u"You need to select Meets goal", 'error')
            return redirect(url_for(
                "edit_goal", goal_id=goal[
                    "_id"], _external=True, _scheme="https"))
        else:
            flash("Goal successfully updated")
            return redirect(url_for(
                "profile", username=username, _external=True, _scheme="https"))
        
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_goal.html", goal=goal, categories=categories) 
    

@app.route("/delete_goal/<goal_id>")
def delete_goal(goal_id):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    mongo.db.goals.remove({"_id": ObjectId(goal_id)})
    flash("Goal successfully deleted")
    return redirect(url_for(
                "profile", username=username))


@app.route("/complete_goal/<goal_id>")
def complete_goal(goal_id):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    is_complete = "unchecked" if request.form.get(
            "is_complete") else "checked"
    submit = {"$set": {
            "is_complete": is_complete}}
    mongo.db.goals.update_one({"_id": ObjectId(goal_id)}, submit)
    print(request.endpoint)
    flash(u"Congratulations! Goal successfully completed.", "success")
    return redirect(url_for('profile', username=username))


@app.route("/complete_sharedgoal/<goal_id>")
def complete_sharedgoal(goal_id):
    is_complete = "unchecked" if request.form.get(
            "is_complete") else "checked"
    submit = {"$set": {
            "is_complete": is_complete}}
    mongo.db.goals.update_one({"_id": ObjectId(goal_id)}, submit)
    print(request.endpoint)
    flash(u"Congratulations! Goal successfully completed.", "success")
    return redirect(url_for("get_goals"))


@app.route("/moveto_inprogress/<goal_id>")
def moveto_inprogress(goal_id):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    is_complete = "checked" if request.form.get(
            "is_complete") else "unchecked"
    submit = {"$set": {
            "is_complete": is_complete}}
    mongo.db.goals.update_one({"_id": ObjectId(goal_id)}, submit)
    flash("Goal moved to In Progress.")
    return redirect(url_for('profile', username=username)) 


@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")

@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Category successfully updated")
        return redirect(url_for("get_categories"))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    #In production mode include some defensive programming such as prompting the user to confirm deletion, 
    #instead of immediately deleting.
    flash("Category successfully deleted")
    return redirect(url_for("get_categories"))


if __name__ == "__main__":                  #Tell our app how and where to run our app
    app.run(host=os.environ.get("IP"),      #use the hidden variables in the env.py file
            port=int(os.environ.get("PORT")), # convert port to an integer
            debug=True)                     #set debug to True so we can see errors.  Set to false at go live
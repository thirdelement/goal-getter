import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId 
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env 

# Create Flask instance
app = Flask(__name__) 

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME") 
app.config["MONGO_URI"] = os.environ.get("MONGO_URI") 
app.secret_key = os.environ.get("SECRET_KEY") 

mongo = PyMongo(app) 


# Routes


@app.route("/") 
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
        # Check if username already exists in database
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

        # Put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!") 
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Check if username exists in database
        existing_user = mongo.db.users.find_one({
            "username": request.form.get("username").lower()})

        if existing_user:
            # Ensure hashed password matches user input
            if check_password_hash(existing_user[
                    "password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username").capitalize()))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # Invalid password match
                flash(u"Incorrect Username and/or Password", 'warning')
                return redirect(url_for("login"))

        else:
            # Username doesn't exist
            flash(u"Incorrect Username and/or Password", 'warning')
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # Check if user logged in
    if "user" not in session:
        flash(u"You need to Log In to access that area!", 'error')

        return redirect(url_for("login"))
    
    elif request.method != "POST":
        # Grab the session user's username from the database
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
        goals = list(mongo.db.goals.find(
            {"created_by": session["user"]}).sort("_id", -1))

        if session["user"]:
            # If session cookie is truthy then render the page
            return render_template(
                "profile.html", username=username, goals=goals)
            # If session cookie is not truthy (e.g. has been deleted)
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # Remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_goal", methods=["GET", "POST"])
def add_goal():
    categories = mongo.db.categories.find().sort("category_name", 1)

    # Check if user logged in. Credit: https://github.com/Edb83/self-isolution
    if "user" not in session:
        flash(u"You need to Log In to access that area!", 'error')

        return redirect(url_for("login"))

    elif request.method != "POST":
        return render_template(
            "add_goal.html", categories=categories)

    else:
        is_complete = "checked" if request.form.get(
                "is_complete") else "unchecked"
        share = "" if request.form.get("share") else "checked"
        meet_goal = "checked" if request.form.get("meet_goal") else ""
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
        mongo.db.goals.insert_one(goal)
        flash("Goal, Reality and Options added")
        return redirect(url_for('edit_goal', goal_id=goal[
                    "_id"]))  

    
@app.route("/edit_goal/<goal_id>", methods=["GET", "POST"])
def edit_goal(goal_id):
    categories = mongo.db.categories.find().sort("category_name", 1)
    goal = mongo.db.goals.find_one({"_id": ObjectId(goal_id)})

    # Check if user logged in
    if "user" not in session:
        flash(u"You need to Log In to access that area!", 'error')

        return redirect(url_for("login"))
    
    elif request.method != "POST":
        return render_template(
            "edit_goal.html", goal=goal, categories=categories) 

    else:
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
        is_complete = "checked" if request.form.get(
                "is_complete") else "unchecked"
        share = "checked" if request.form.get("share") else ""
        meet_goal = "checked" if request.form.get("meet_goal") else ""
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
        # If the meet_goal switch is unchecked 
        if meet_goal == "":
            flash(u"You need to select Meets goal", 'error')
            return redirect(url_for(
                "edit_goal", goal_id=goal[
                    "_id"], _external=True, _scheme="https"))
        # If the submit button on the Options tab is clicked
        # Credit: 
        # https://stackoverflow.com/questions/43811779/use-many-submit-buttons-in-the-same-form
        elif 'submit-options' in request.form:
            return redirect(url_for(
                "edit_goal", goal_id=goal[
                    "_id"], _external=True, _scheme="https"))
        else:
            flash("Goal successfully updated")
            return redirect(url_for(
                "profile", username=username, _external=True, _scheme="https"))
        
    
@app.route("/delete_goal/<goal_id>")
def delete_goal(goal_id):
    # Check if user logged in
    if "user" not in session:
        flash(u"You need to Log In to access that area!", 'error')

        return redirect(url_for("login"))
    # Delete goal
    elif request.method != "POST":
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
        mongo.db.goals.remove({"_id": ObjectId(goal_id)})
        flash("Goal successfully deleted")
        return redirect(url_for(
                    "profile", username=username))


@app.route("/complete_goal/<goal_id>")
def complete_goal(goal_id):
    # Check if user logged in
    if "user" not in session:
        flash(u"You need to Log In to access that area!", 'error')

        return redirect(url_for("login"))
    # Complete goal
    elif request.method != "POST":
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


@app.route("/moveto_inprogress/<goal_id>")
def moveto_inprogress(goal_id):
    # Check if user logged in
    if "user" not in session:
        flash(u"You need to Log In to access that area!", 'error')

        return redirect(url_for("login"))
    # Move goal to In Progress
    elif request.method != "POST":
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
    # Check if user logged in
    if "user" not in session:
        flash(u"You need to Log In to access that area!", 'error')

        return redirect(url_for("login"))
    # Check if user is the Admin
    elif session["user"].lower() != "admin":
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
        flash(u"Admin access only!", 'error')

        return redirect(url_for('profile', username=username))
    # Show categories
    else:
        categories = list(mongo.db.categories.find().sort("category_name", 1))
        return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    # Check if user logged in
    if "user" not in session:
        flash(u"You need to Log In to access that area!", 'error')

        return redirect(url_for("login"))
    # Check if user is the Admin
    elif session["user"].lower() != "admin":
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
        flash(u"Admin access only!", 'error')

        return redirect(url_for('profile', username=username))
    # Add category
    elif request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    # Check if user logged in
    if "user" not in session:
        flash(u"You need to Log In to access that area!", 'error')

        return redirect(url_for("login"))
    # Check if user is the Admin 
    elif session["user"].lower() != "admin":
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
        flash(u"Admin access only!", 'error')

        return redirect(url_for('profile', username=username))
    # Edit category
    elif request.method == "POST":
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
    # Check if user logged in
    if "user" not in session:
        flash(u"You need to Log In to access that area!", 'error')

        return redirect(url_for("login"))
    # Check if user is the Admin 
    elif session["user"].lower() != "admin":
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
        flash(u"Admin access only!", 'error')

        return redirect(url_for('profile', username=username))
    # Delete category
    else:
        mongo.db.categories.remove({"_id": ObjectId(category_id)})
        flash("Category successfully deleted")
        return redirect(url_for("get_categories"))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')
    # Credit: https://www.geeksforgeeks.org/python-404-error-handling-in-flask/


if __name__ == "__main__":                  
    app.run(host=os.environ.get("IP"),      
            port=int(os.environ.get("PORT")), 
            debug=False)                     
    

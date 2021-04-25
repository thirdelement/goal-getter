import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId #Enables rendering of ObjectID so we can find docs in MongoDB
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
    goals = mongo.db.goals.find()
    return render_template("goals.html", goals=goals)


if __name__ == "__main__":                  #Tell our app how and where to run our app
    app.run(host=os.environ.get("IP"),      #use the hidden variables in the env.py file
            port=int(os.environ.get("PORT")), # convert port to an integer
            debug=True)                     #set debug to True so we can see errors.  Set to false at go live
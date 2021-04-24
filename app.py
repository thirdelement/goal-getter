import os
from flask import Flask
if os.path.exists("env.py"):
    import env #we are not pushing env.py to GitHub.  When in Heroku we need to only import
                            #env if the os can find an existing file path for the file itself.  Otherwise
                            #Heroku will throw an error.
app = Flask(__name__) 


@app.route("/")
def hello():
    return "Hello World ... again!"


if __name__ == "__main__":                  #Tell our app how and where to run our app
    app.run(host=os.environ.get("IP"),      #use the hidden variables in the env.py file
            port=int(os.environ.get("PORT")), # convert port to an integer
            debug=True)                     #set debug to True so we can see errors.  Set to false at go live
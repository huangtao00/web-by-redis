from flask import Flask
from flask import render_template
from flask import request


app=Flask(__name__)

@app.route("/",methods=["GET","POST"])
def index():
    if request.method=="POST":
        print ("you post me")
        return ("you post me")
    return render_template("index.html")



if __name__=="__main__":
    app.run(debug=True)

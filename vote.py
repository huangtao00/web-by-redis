#!coding:utf8
from flask import Flask,redirect,url_for
from flask import render_template
from flask import request
from flask import flash


app=Flask(__name__)
app.secret_key = 'some_secret'
@app.route("/",methods=["GET","POST"])
def index():
    if request.method=="POST":
        article={}
        keys=["title","author","link"]
        for key in keys:
            article[key]=request.form[key]
        flash("发表文章\"{}\"成功！".format(article["title"]))
        return redirect(url_for('index'))
    return render_template("index.html")



if __name__=="__main__":
    app.run(debug=True)

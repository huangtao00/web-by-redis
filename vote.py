#!coding:utf8
from flask import Flask,redirect,url_for
from flask import render_template
from flask import request
from flask import flash
import datetime
import redis
def save_aritle_redis(article):
    r=redis.StrictRedis(host="localhost",port=6379,decode_responses=True)
    #以下代码要保证atomic
    counter=r.incr("counter")
    for key, value in article.items():
        r.hset("article:"+str(counter),key,value)


def get_ten_article(page=1):
    r=redis.StrictRedis(host="localhost",port=6379,decode_responses=True)
    counter=r.get("counter")
    if page*10>counter

app=Flask(__name__)
app.secret_key = 'some_secret'
@app.route("/",methods=["GET","POST"])
def index():
    if request.method=="POST":
        article={}
        keys=["title","author","link","time"]
        now=datetime.datetime.now()
        now=now.strftime("%Y-%m-%d-%H-%M")
        for key in keys:
            if key !="time":
                article[key]=request.form[key]
            else:
                article[key]=now
        save_aritle_redis(article)
        flash("发表文章\"{}\"成功！".format(article["title"]))
        return redirect(url_for('index'))
    return render_template("index.html")



if __name__=="__main__":
    app.run(debug=True)

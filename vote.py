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

import math
def get_articles(page=1,articelsperpage=6):
    r=redis.StrictRedis(host="localhost",port=6379,decode_responses=True)
    counter=r.get("counter")
    if counter:
        articlelist=[]
        counter=int(counter)
        allpages=math.ceil(counter/articelsperpage)
        curpage=allpages-page+1
        if  curpage==1: #no next page
            #get article page*10-10+1 to counter artice
            start,end=1,counter-(allpages-1)*articelsperpage+1
        else: #have next page
            #get articel page*10-10+1 to page*10+1
            if curpage==allpages:
                end=counter
            else:  #11 11-4
                end=counter-(page-1)*articelsperpage
                print (counter)
                print (end)
            start=end-articelsperpage+1
            end=end+1
        #cur  8 7 6 5 4 3 2 1
        if curpage<allpages:
            previouspage=range(1,page)
        else:
            previouspage=False
        if curpage>1:
            nextpage=range(page+1,allpages+1)
        else:
            nextpage=False
        for i in range(start,end):
            article="article:"+str(i)
            onearticle=r.hgetall(article)
            onearticle["index"]=i
            articlelist.append(onearticle)
        articlelist.reverse()
        return articlelist,nextpage,previouspage
app=Flask(__name__)
app.secret_key = 'some_secret'
@app.route("/",methods=["GET","POST"])
@app.route("/page/<int:index>",methods=["GET","POST"])
def index(index=1):
    if request.method=="POST":
        #save article to redis
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
    # show newest articles
    allarticles,nextpage,prepage=get_articles(page=index)
    pagenav=dict({"pre":prepage,"cur":index,"next":nextpage})
    return render_template("index.html",articles=allarticles,pagenav=pagenav)



if __name__=="__main__":
    app.run(debug=True)

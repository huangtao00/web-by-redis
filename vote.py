#!coding:utf8
from flask import Flask,redirect,url_for
from flask import render_template
from flask import request
from flask import flash,jsonify
import datetime
import redis
import math

def save_aritle_redis(article):
    r=redis.StrictRedis(host="localhost",port=6379,decode_responses=True)
    #以下代码要保证atomic
    counter=r.incr("counter")
    for key, value in article.items():
        r.hset("article:"+str(counter),key,value)
def get_article_rank_by_score():
    r=redis.StrictRedis(host="localhost",port=6379,decode_responses=True)
    article_rank_by_score=r.zrange("time",0,-1,True,withscores=True)
    if article_rank_by_score:
        return article_rank_by_score
    else:
        return False
def get_top_aritle(n=5):
    article_list=get_article_rank_by_score()
    if article_list:
        n=min(n,len(article_list))
        top_article_list=article_list[:n]
        only_article_name_list=[]
        r=redis.StrictRedis(host="localhost",port=6379,decode_responses=True)
        for i in top_article_list:
            article_id=i[0]
            only_article_name_list.append(r.hget(article_id,"title"))
        return only_article_name_list
    else:
        return False


def calc_articles_score():
    r=redis.StrictRedis(host="localhost",port=6379,decode_responses=True)
    counter=r.get("counter")
    for i in range(1,int(counter)+1):
        article_id="article:"+str(i)
        vote=int(r.hget(article_id,"vote"))
        uptime=float(r.hget(article_id,"uptime"))
        score=uptime+vote*432
        r.zadd("time",score,article_id)
    article_rank_by_score=r.zrange("time",0,-1,True,withscores=True)
    return article_rank_by_score

def get_articles(page=1,articelsperpage=3):
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
                # print (counter)
                # print (end)
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
            # print (onearticle)
            # if "vote" not in onearticle.keys():
            #     r.hset(article,"vote","0")
            #     # onearticle["vote"]=0
            articlelist.append(onearticle)
        articlelist.reverse()
        return articlelist,nextpage,previouspage
    else:
        return (False,False,False)
app=Flask(__name__)
app.secret_key = 'some_secret'
@app.route("/api/vote/")
def api_add_vote():
    article_id=request.args.get("id").replace("art","")
    #incr redis score
    vote_score=incrbyscore(article_id)
    artitle_rank=calc_articles_score() #upate article vote score rank
    # print (artitle_rank)
    return jsonify({"vote":["vote"+str(article_id),vote_score]})
def incrbyscore(article_id,incrment=1):
    r=redis.StrictRedis(host="localhost",port=6379,decode_responses=True)
    result=r.hincrby("article:"+str(article_id), "vote", incrment)
    return result




@app.route("/",methods=["GET","POST"])
@app.route("/page/<int:index>",methods=["GET","POST"])
def index(index=1):
    if request.method=="POST":
        #save article to redis
        article={}
        keys=["title","author","link","time","uptime","vote"]
        now=datetime.datetime.now()
        now=now.strftime("%Y-%m-%d-%H-%M")
        uptime=round(datetime.datetime.timestamp(datetime.datetime.utcnow()),2)
        for key in keys:
            if key not in ["time","uptime","vote"]:
                article[key]=request.form[key]
            else:
                if key=="time":
                    article[key]=now
                if key=="uptime":
                    article[key]=uptime
                if key=="vote":
                    article["vote"]=0
        save_aritle_redis(article)
        flash("发表文章\"{}\"成功！".format(article["title"]))
        return redirect(url_for('index'))
    # show newest articles
    allarticles,nextpage,prepage=get_articles(page=index)
    pagenav=dict({"pre":prepage,"cur":index,"next":nextpage})
    top_article=get_top_aritle(5)
    return render_template("index.html",articles=allarticles,pagenav=pagenav,top_article=top_article)



if __name__=="__main__":
    app.run(debug=True)

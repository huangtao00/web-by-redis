ONE_WEEK_IN_SECONDS=24*60*60
VOTE_SCORE= 432 # 200 vote numbers equal to  ONE_WEEK_IN_SECONDS
def article_vote(con,user,article):
    """
    user vote for article
    """
    uptime=con.zscore("time",article)
    if time.time()-uptime>ONE_WEEK_IN_SECONDS: # time flies over one week,can not vote this article
        return
    article_id=ariicle.partition[:][-1]
    if con.sadd("voted:"+article_id,user): #if this user not vote for this article
        con.zincrby("score:",article,VOTE_SCORE) #incr this article vote score in order set
        con.hincrby(article,"votes",1) # incr this article vote numbers
def post_article(conn,user,title,link):
    article_id=str(conn.incr("article:"))
    voted="voted:"+article_id
    conn.sadd(voted,user)
    con.expire(voted,ONE_WEEK_IN_SECONDS)
    now=time.time()
    article="article:"+article_id
    conn.hmset(article,{
    "title":title,
    "link":link,
    "poster":user,
    "time":now,
    "votes":1,
    })
    conn.zadd("score:",article,now+VOTE_SCORE)
    conn.zadd("time:",article,now)
    return article_id

ARTICELS_PER_PAGE=50
#base score or time to get your article
def get_articles(conn,page,order="score:"):
    start=(page-1)*ARTICELS_PER_PAGE
    end=start+ARTICELS_PER_PAGE-1
    ids=conn.zrevrange(order,start,end)
    articles=[]
    for id in ids:
        article_data=con.hgetall(id)
        article_data["id"]=id
        articles.append(article_data)
    return articles
def add_remove_groups(conn,article_id,to_add=[],to_remove=[]):
    article="article:"+article_id
    for group in to_add:
        conn.sadd("group:"+group,article)
    for group in to_remove:
        conn.srem("group:"+group,article)

def get_group_articles(conn,group,page,oder="score:"):
    key=order+group
    if not conn.exists(key):
        conn.zinterstore(key,["group:"+group,order],
        aggregate="max")
        conn.expire(key,60)
    return get_articles(conn,page,key)

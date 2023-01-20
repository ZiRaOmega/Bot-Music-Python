import praw

#Here i used the praw library to connect to reddit and fetch PrograamingHumor subreddit and return the first post

def JokefromReddit():
    #connect to reddit
    reddit = praw.Reddit(client_id='paXC2ZsdM_2-uGDNyoerNw',
                         client_secret='uC79rgQmD-xrF0lpGT-Cd5opFVEvcQ',
                         user_agent='user_agent')
    #fetch the subreddit
    jokes = reddit.subreddit('ProgrammerHumor')
    joke = jokes.hot(limit=1)
    #So joke must be 1 len long
    
    #return the first post
    return joke
        
def CheckRedditConnection():
    arrJoke=[]
    #Connect to reddit
    reddit = praw.Reddit(client_id='paXC2ZsdM_2-uGDNyoerNw',
                         client_secret='uC79rgQmD-xrF0lpGT-Cd5opFVEvcQ',
                         user_agent='user_agent')
    JOKES = reddit.subreddit('ProgrammerHumor')
    #get the 10 hot posts
    JOKE = JOKES.hot(limit=10)
    joke = JOKES.hot(limit=1)
    for j in JOKE:
        arrJoke.append(j)
    if joke:
        return True, arrJoke
    else:
        return False
if CheckRedditConnection():
    tf, arrJoke = CheckRedditConnection()
    for jok in arrJoke:
        print(jok.url)
        print(" ")
    print("Connected to Reddit")
else:
    print("Not Connected to Reddit")
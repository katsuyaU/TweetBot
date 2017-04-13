#!/bin/env/python3
import tweepy
import json
import datetime
import time
import sys

accont = json.load(open("ID.json"))
AUTH = tweepy.OAuthHandler(accont["consumer_key"] , accont["consumer_secret"])
AUTH.set_access_token(accont["access_token"] , accont["access_token_secret"])
TWITTER = tweepy.API(AUTH)

def print_tweet(status):
    with open("log.log" , "w") as log:
        if getattr(status , "retweeted_status" , None):
            name = status.user.name 
            status = status.retweeted_status
            status.user.name = status.user.name + "--- Retweeted By " + name
        print("***" , file=log)
        print(status.user.name , end=" " , file=log)
        print("@" + status.user.screen_name , file=log)
        print(status.text , file=log)
        print(status.created_at + datetime.timedelta(hours=9) , file=log)
        print(get_status_url(status) , file=log)
        print("***" , file=log)

def get_status_url(status):
    s = "https://twitter.com/{0}/status/{1}".format( status.user.screen_name ,  status.id)
    return str(s)


def result_hashtag(hashtags , status):
    if sys.argv[1] in hashtags:
        print("=>hashtagを検出")
        s = "{0}(@{1})さんが鍵を借りました！\n\n{2}".format(status.user.name , status.user.screen_name , get_status_url(status))
        TWITTER.update_status(s)
 
class Listener(tweepy.StreamListener):
    def on_status(self , status):
        print_tweet(status)
        if status.entities["hashtags"]:
            hashtags = [json["text"] for json in status.entities["hashtags"] ]
            print(hashtags)
            result_hashtag(hashtags , status)

        return True
    def on_timeout(self):
        print("***Timeout...***")
        return True



def main():
    print("start")

    while True:
        now_hour = datetime.datetime.now().hour
        if 0 <= now_hour and now_hour <= 8:
            with open("sleep.log" , "w") as log:
                print("(˘ω˘)ｽﾔｧ({0})".format(datetime.datetime.now()) , file = log)
            time.sleep(2 * 3600 )# 二時間
            with open("sleep.log" , "a") as log:
                print("(ﾟωﾟ)ﾊｯ({0})".format(datetime.datetime.now()) , file = log)
        else:
            try:
                stream = tweepy.Stream(auth = TWITTER.auth , listener = Listener())
                stream.userstream()
            except Exception as e:
                with open("error.log" , "w") as log:
                    print("error!" , datetime.datetime.now())
                    print("-------------" , file=log)
                    print(e , file=log)
                    print(datetime.datetime.now() , file=log)
                    print("-------------" , file=log)
            finally: #5分
                time.sleep(1 * 60 * 5)
    
if __name__ == "__main__":
    main()
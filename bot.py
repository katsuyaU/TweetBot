#!/usr/bin/env python3
import datetime
import json
import sys
import time
import traceback
from contextlib import contextmanager
from datetime import datetime, time
from time import sleep

import tweepy

accont = json.load(open("account.json"))
AUTH = tweepy.OAuthHandler(accont["consumer_key"] , accont["consumer_secret"])
AUTH.set_access_token(accont["access_token"] , accont["access_token_secret"])
TWITTER = tweepy.API(AUTH)

@contextmanager
def tag(tag : str):
    """ログファイルにタグとログを残すための関数"""
    with open("bot.log" , "a") as f:
        def func(*args):
            print("[{}]({})".format(tag , datetime.now()) , *args , file = f)
        yield func


def main():
    with tag("HASHTAG_確認") as log:
        log("#" + sys.argv[1])
    while True:
        now = datetime.now()
        if now.weekday() == 0: #月曜日のとき
            print("[RESET]" , file = open("bot.log" , "w"))
            with tag("MONDAY") as log:
                log("一週間の始まり")
                log("今週も頑張っていきましょう！")
        with tag("START") as log:
            log(now.time())
        if is_within_a_sleeptime(now.time()):
            with tag("SLEEP") as log:
                log("(˘ω˘)ｽﾔｧ({})".format(now))
            sleep(3 * 3600 )# 3時間
            with tag("SLEEP") as log:
                log("(ﾟωﾟ)ﾊｯ({})".format(datetime.now()) )
        else:
            try:
                stream = tweepy.Stream(auth = TWITTER.auth , listener = Listener())
                stream.userstream()
            except:
                with tag("ERROR") as log:
                    log("\n" + traceback.format_exc())
            finally: #5分
                sleep(1 * 60 * 5)

def is_within_a_sleeptime(now : time) -> bool:
    """botがsleeptimeに入っている時間かを確認する"""
    return time(18) < now or now < time(8)

def print_tweet(status : tweepy.Status):
    """最新のツイートをtweet.logに記録する関数"""
    with open("tweet.log" , "w") as log:
        if getattr(status , "retweeted_status" , None):
            name = status.user.name 
            status = status.retweeted_status
            status.user.name = status.user.name + "--- Retweeted By " + name
        print("***" , file=log)
        print(status.user.name , end=" " , file=log)
        print("@" + status.user.screen_name , file=log)
        print(status.text , file=log)
        print(datetime.now() , file=log)
        print(get_status_url(status) , file=log)
        print("***" , file=log)

def get_status_url(status : tweepy.Status) -> str:
    return "https://twitter.com/{0}/status/{1}".format( status.user.screen_name ,  status.id)

def result_hashtag(hashtags, status : tweepy.Status):
    with tag("CHECK_HASHTAGS") as log:
        log(*hashtags)
        if sys.argv[1] in hashtags:
            log(sys.argv[1] , "を検出")
            s = "{0}(@{1})さんが鍵を借りました！\n\n{2}".format(status.user.name , status.user.screen_name , get_status_url(status))
            tweet = TWITTER.update_status(s)
            log("\n" + status.user.name + "\n@{}\n".format(status.user.screen_name) + status.text)
            log("\n" + tweet.user.name + "\n@{}\n".format(tweet.user.screen_name) +  tweet.text)

 
class Listener(tweepy.StreamListener):
    def on_status(self , status):
        if status.entities["hashtags"]:
            hashtags = [json["text"] for json in status.entities["hashtags"] ]
            result_hashtag(hashtags , status)
        print_tweet(status)
        if is_within_a_sleeptime(datetime.now().time()):
            raise Exception("正常に終了")
        return True
    def on_timeout(self):
        with tag("TIMEOUT") as log:
            log("***Timeout...***")
        return True


if __name__ == "__main__":
    main()

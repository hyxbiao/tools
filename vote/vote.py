#!/usr/bin/python

import time
import sys
from datetime import datetime
import socket
import urllib
import urllib2
import cookielib
import json
import os.path
import re

#sdafb=0; OX_plg=swf|sl|pdf|wmp|shk|pm; __atuvc=1%7C30

def makeCookie(name, value):
    return cookielib.Cookie(
        version=0, 
        name=name, 
        value=value,
        port=None, 
        port_specified=False,
        domain="www.soompi.com", 
        domain_specified=True, 
        domain_initial_dot=False,
        path="/", 
        path_specified=True,
        secure=False,
        expires=None,
        discard=False,
        comment=None,
        comment_url=None,
        rest=None
    )

def readAccounts(filename):
    #f = open(filename, "r")
    #accounts = json.load(f)
    #print accounts
    if not os.path.isfile(filename):
        print "%s is not exists!" % filename
        return []
    with open(filename, "r") as f:
        data = f.readlines()
        f.close()
    accounts = []
    for item in data:
        item = item.strip()
        if not item:
            continue
        try:
            user, pwd = re.split("\t|\s+", item)
            accounts.append([user, pwd])
        except:
            continue
    return accounts

def checkUser(user, pwd):
    return True
    filename = "result/%s" % user
    if not os.path.isfile(filename):
        return True
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            f.close()
    except e:
        return True
    if not lines:
        return True
    last_line = lines[-1].strip()
    fmt = '%Y-%m-%d %H:%M:%S'
    interval = datetime.now() - datetime.strptime(last_line, fmt)
    if interval.days == 0:
        print "Account: \"%s\" had voted in %s!" % (user, last_line)
        return False
    return True

def hadVoted(user):
    filename = "result/%s" % user
    with open(filename, "a") as f:
        t = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(t + "\n")
        f.close()
    pass

def visitHome(cookie):
    url = "http://www.soompi.com/seoul-international-drama-awards-2014-vote/"

    header={
        "User-Agent": "Mozilla-Firefox5.0",
        "Host": "www.soompi.com",
    }
    cjhandler=urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(cjhandler)
    urllib2.install_opener(opener)

    req = urllib2.Request(url, None, header)
    res = urllib2.urlopen(req)
    return res

def checkIsVoted(cookie):
    url = "http://www.soompi.com/seoul-international-drama-awards-2014-vote/"

    header={
        "User-Agent": "Mozilla-Firefox5.0",
        "Host": "www.soompi.com",
    }
    cjhandler=urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(cjhandler)
    urllib2.install_opener(opener)

    req = urllib2.Request(url, None, header)
    res = urllib2.urlopen(req)
    if res.code != 200:
        return False
    content = res.read()
    m = re.search('voted = (\d)', content)
    if m:
        #print "voted: %s" % m.group(1)
        return int(m.group(1)) == 1
    else:
        return False
    return False

def addCookie(cookie):
    cookie.set_cookie(makeCookie("OX_plg", "swf|sl|pdf|wmp|shk|pm"))
    cookie.set_cookie(makeCookie("__atuvc", "1%7C30"))
    cookie.set_cookie(makeCookie("sdafb", "0"))

def visitLogin(cookie):
    url = "http://www.soompi.com/login/?redirect_to=%2Fseoul-international-drama-awards-2014-vote%2F%23voting"
    pass

def addCookie(cookie):
    cookie.set_cookie(makeCookie("OX_plg", "swf|sl|pdf|wmp|shk|pm"))
    cookie.set_cookie(makeCookie("__atuvc", "1%7C30"))
    cookie.set_cookie(makeCookie("sdafb", "0"))

def visitLogin(cookie):
    url = "http://www.soompi.com/login/?redirect_to=%2Fseoul-international-drama-awards-2014-vote%2F%23voting"

    header={
        "User-Agent": "Mozilla-Firefox5.0",
        "Host": "www.soompi.com",
    }
    cjhandler=urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(cjhandler)
    urllib2.install_opener(opener)

    req = urllib2.Request(url, None, header)
    res = urllib2.urlopen(req)
    return res

def login(cookie, user, pwd):
    url = "http://www.soompi.com/login/?action=login"
    data={
        "client_id": "163414424111",
        "redirect_uri": "http%3A%2F%2Fwww.soompi.com%2Fwp-content%2Fplugins%2Fsocial-connect%2Ffacebook%2Fcallback.php",
        "redirect_uri": "http://www.soompi.com/wp-content/plugins/social-connect/twitter/connect.php",
        "redirect_uri": "http://www.soompi.com/wp-content/plugins/social-connect/google/connect.php",
        "redirect_uri": "http://www.soompi.com/wp-content/plugins/social-connect/yahoo/connect.php",
        "redirect_uri": "http://www.soompi.com/wp-content/plugins/social-connect/wordpress/connect.php",
        "log": user,
        "pwd": pwd,
        "wp-submit": "Log In",
        "redirect_to": "/seoul-international-drama-awards-2014-vote/#voting",
        "testcookie": "1",
        "instance": ""
    }
    header={
        "User-Agent": "Mozilla-Firefox5.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "www.soompi.com",
        "Origin": "http://www.soompi.com",
        "Referer": "http://www.soompi.com/login/?redirect_to=%2Fseoul-international-drama-awards-2014-vote%2F%23voting"
    }
    postdata = urllib.urlencode(data)

    #cj = cookielib.CookieJar()
    cjhandler=urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(cjhandler)
    urllib2.install_opener(opener)

    req = urllib2.Request(url, postdata, header)
    res = urllib2.urlopen(req)
    if res.code != 200:
        return False
    content = res.read(1024)
    if re.search('<title>Login', content):
        return False
    return True

def vote(cookie, url, data):
    header={
        "User-Agent": "Mozilla-Firefox5.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "www.soompi.com",
        "Origin": "http://www.soompi.com",
    }
    postdata = urllib.urlencode(data)

    #cj = cookielib.CookieJar()
    cjhandler=urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(cjhandler)
    urllib2.install_opener(opener)

    req = urllib2.Request(url, postdata, header)
    res = urllib2.urlopen(req)
    return res

def voteActor(cookie):
    url = "http://www.soompi.com/seoul-international-drama-awards-2014-vote/"
    data={
        "category": "drama",
        "myVotes": "213"
    }
    header={
        "User-Agent": "Mozilla-Firefox5.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "www.soompi.com",
        "Origin": "http://www.soompi.com",
    }
    postdata = urllib.urlencode(data)

    #cj = cookielib.CookieJar()
    cjhandler=urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(cjhandler)
    urllib2.install_opener(opener)

    req = urllib2.Request(url, postdata, header)
    res = urllib2.urlopen(req)
    return res

def run(user, pwd):
    print "Account user: %s, pwd: %s" % (user, pwd)
    if not checkUser(user, pwd):
        return False, 1

    cookie = cookielib.CookieJar()

    res = visitHome(cookie)
    if res.code != 200:
        print "Access home fail"
        return False, 2

    addCookie(cookie)

    #visitLogin(cookie)
    #print "Access login, cookie: ", cookie
    res = login(cookie, user, pwd)
    if not res:
        print "User: %s Login fail" % user
        return False, 3

    res = checkIsVoted(cookie)
    if res:
        print "User: %s had voted" % user
        return False, 4

    url = "http://www.soompi.com/seoul-international-drama-awards-2014-vote/"
    data={
        "category": "drama",
        "myVotes": "213"
    }
    res = vote(cookie, url, data)
    if res.code == 200:
        print "Vote drama success"
    else:
        print "Vote drama fail"

    url = "http://www.soompi.com/seoul-international-drama-awards-2014-vote/?category=actor&last=drama"
    data={
        "category": "actor",
        "myVotes": "222"
    }
    res = vote(cookie, url, data)
    if res.code == 200:
        print "Vote actor success"
    else:
        print "Vote actor fail"

    url = "http://www.soompi.com/seoul-international-drama-awards-2014-vote/?category=actress&last=actor"
    data={
        "category": "actress",
        "myVotes": "225"
    }
    res = vote(cookie, url, data)
    if res.code == 200:
        print "Vote actress success"
    else:
        print "Vote actress fail"

    hadVoted(user)
    return True, 0

def main():
    socket.setdefaulttimeout(30)

    sleep_time = 0
    if len(sys.argv) > 1:
        sleep_time = int(sys.argv[1])

    voted_dir="./result"
    if not os.path.isdir(voted_dir):
        os.mkdir(voted_dir)

    filename = "vote.txt"
    accounts = readAccounts(filename)

    total = len(accounts)
    success = 0
    fail_accounts = []

    for item in accounts:
        user = item[0]
        pwd = item[1]
        retry = 3
        ret = False
        while retry > 0:
            ret, status = run(user, pwd)
            if ret or status == 4:
                break
            print "User: %s Vote fail, retry!" % user
            retry -= 1
        if ret:
            success += 1
        else:
            fail_accounts.append([user, pwd])

        if sleep_time != 0:
            time.sleep(sleep_time)

    rf = open("finish.txt", "w")
    print "\n\n------------------- FINISH -------------------"
    for item in fail_accounts:
        user = item[0]
        pwd = item[1]
        txt = "User: %s vote fail!" % user
        print txt
        rf.write(txt + "\n")
    txt = "\nAccounts total: %d, success: %d, fail: %d" % (total, success, total-success)
    print txt
    rf.write(txt + "\n")
    rf.close()

    wait = raw_input()
    return 


if __name__ == '__main__':
    main()

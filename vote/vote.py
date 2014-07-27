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
from random import random
from random import randint

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
    except Exception, e:
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

def visitHome(cookie, ip):
    url = "http://www.soompi.com/seoul-international-drama-awards-2014-vote/"

    header={
        "User-Agent": "Mozilla-Firefox5.0",
        "Host": "www.soompi.com",
        "X-Forwarded-For": ip,
    }
    try:
        cjhandler=urllib2.HTTPCookieProcessor(cookie)
        opener = urllib2.build_opener(cjhandler)
        urllib2.install_opener(opener)

        req = urllib2.Request(url, None, header)
        res = urllib2.urlopen(req)
    except Exception, e:
        print "[Error] %s" % str(e)
        return False
    return res

def checkIsVoted(cookie, ip):
    url = "http://www.soompi.com/seoul-international-drama-awards-2014-vote/"

    header={
        "User-Agent": "Mozilla-Firefox5.0",
        "Host": "www.soompi.com",
        "X-Forwarded-For": ip,
    }
    try:
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
    except Exception, e:
        print "[Error] %s" % str(e)
        return False
    return False

def addCookie(cookie):
    cookie.set_cookie(makeCookie("OX_plg", "swf|sl|pdf|wmp|shk|pm"))
    cookie.set_cookie(makeCookie("__atuvc", "1%7C30"))
    cookie.set_cookie(makeCookie("sdafb", "0"))

def visitLogin(cookie, ip):
    url = "http://www.soompi.com/login/?redirect_to=%2Fseoul-international-drama-awards-2014-vote%2F%23voting"

    header={
        "User-Agent": "Mozilla-Firefox5.0",
        "Host": "www.soompi.com",
        "X-Forwarded-For": ip
    }
    cjhandler=urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(cjhandler)
    urllib2.install_opener(opener)

    req = urllib2.Request(url, None, header)
    res = urllib2.urlopen(req)
    return res

def userLogin(cookie, ip, user, pwd):
    url = "http://www.soompi.com/login/?action=login"
    #client_id = "%d" % int(random() * sys.maxint)
    data={
        "client_id": "163414424111",
        #"client_id": client_id,
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
        "Referer": "http://www.soompi.com/login/?redirect_to=%2Fseoul-international-drama-awards-2014-vote%2F%23voting",
        "X-Forwarded-For": ip,
    }
    try:
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
    except Exception, e:
        print "[ERROR] %s" % str(e)
        return False
    return True

def vote(cookie, ip, url, data):
    header={
        "User-Agent": "Mozilla-Firefox5.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "www.soompi.com",
        "Origin": "http://www.soompi.com",
        "X-Forwarded-For": ip,
    }
    try:
        postdata = urllib.urlencode(data)

        #cj = cookielib.CookieJar()
        cjhandler=urllib2.HTTPCookieProcessor(cookie)
        opener = urllib2.build_opener(cjhandler)
        urllib2.install_opener(opener)

        req = urllib2.Request(url, postdata, header)
        res = urllib2.urlopen(req)
    except Exception, e:
        print "[ERROR] %s" % str(e)
        return False
    return res

def checkVoteDone(cookie, ip, url):
    header={
        "User-Agent": "Mozilla-Firefox5.0",
        "Host": "www.soompi.com",
        "Origin": "http://www.soompi.com",
        "X-Forwarded-For": ip,
    }
    #cj = cookielib.CookieJar()
    cjhandler=urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(cjhandler)
    urllib2.install_opener(opener)

    req = urllib2.Request(url, None, header)
    res = urllib2.urlopen(req)
    return res

def getIp():
    #a = 10 if randint(0, 1) == 0 else 192
    a = 10 if randint(0, 1) == 0 else 192
    b = randint(100, 254)
    c = randint(1, 254)
    d = randint(1, 254)
    ip = "%d.%d.%d.%d" % (a, b, c, d)
    return ip

def run(user, pwd):
    print "Account user: %s, pwd: %s" % (user, pwd)
    if not checkUser(user, pwd):
        return False, 1

    cookie = cookielib.CookieJar()

    ip = getIp()
    #print "IP: ", ip

    res = visitHome(cookie, ip)
    if not res or res.code != 200:
        print "Access home fail"
        return False, 2

    #addCookie(cookie)

    #visitLogin(cookie)
    #print "Access login, cookie: ", cookie
    res = userLogin(cookie, ip, user, pwd)
    if not res:
        print "User: %s Login fail" % user
        return False, 3

    res = checkIsVoted(cookie, ip)
    if res:
        print "User: %s had voted" % user
        return False, 4

    url = "http://www.soompi.com/seoul-international-drama-awards-2014-vote/"
    data={
        "category": "drama",
        "myVotes": "213"
    }
    res = vote(cookie, ip, url, data)
    if not res or res.code == 200:
        print "Try to vote drama"
    else:
        print "Vote drama fail"
        return False, 5

    url = "http://www.soompi.com/seoul-international-drama-awards-2014-vote/?category=actor&last=drama"
    data={
        "category": "actor",
        "myVotes": "222"
    }
    res = vote(cookie, ip, url, data)
    if not res or res.code == 200:
        print "Try to vote actor"
    else:
        print "Vote actor fail"
        return False, 6

    url = "http://www.soompi.com/seoul-international-drama-awards-2014-vote/?category=actress&last=actor"
    data={
        "category": "actress",
        "myVotes": "225"
    }
    res = vote(cookie, ip, url, data)
    if not res or res.code == 200:
        print "Try to vote actress"
    else:
        print "Vote actress fail"
        return False, 7

    url = "http://www.soompi.com/seoul-international-drama-awards-2014-vote/?category=drama&last=actress"
    res = checkVoteDone(cookie, ip, url)
    data = res.read()
    with open("./debug/debug_home_%s.html" % user, "w") as f:
        f.write(data)
        f.close()
    if re.search("You're all done voting", data):
        hadVoted(user)
        return True, 0

    return False, 10

def runBatch(accounts, sleep_time, voted_accounts):
    success = 0
    fail_accounts = []

    for item in accounts:
        user = item[0]
        pwd = item[1]
        retry = 3
        ret, status = False, 0
        while retry > 0:
            ret, status = run(user, pwd)
            if ret or status == 4:
                break
            print "User: %s Vote fail, retry!" % user
            retry -= 1
        if ret:
            success += 1
            print "User: %s vote success!" % user
        elif status == 4:
            voted_accounts.append([user, pwd])
        else:
            fail_accounts.append([user, pwd])

        if sleep_time != 0:
            time.sleep(sleep_time)

    return success, fail_accounts

def main():
    socket.setdefaulttimeout(30)

    sleep_time = 0
    if len(sys.argv) > 1:
        sleep_time = int(sys.argv[1])

    voted_dir="./result"
    if not os.path.isdir(voted_dir):
        os.mkdir(voted_dir)

    debug_dir="./debug"
    if not os.path.isdir(debug_dir):
        os.mkdir(debug_dir)

    filename = "vote.txt"
    accounts = readAccounts(filename)

    total = len(accounts)
    success = 0
    voted_accounts = []
    retry = 3
    while retry > 0:
        nsuccess, fail_accounts = runBatch(accounts, sleep_time, voted_accounts)
        success += nsuccess
        if len(fail_accounts) == 0:
            break
        accounts = fail_accounts
        retry -= 1

    rf = open("finish.txt", "w")
    print "\n\n------------------- Had Voted -------------------"
    for item in voted_accounts:
        user = item[0]
        pwd = item[1]
        txt = "[Voted] %s" % user
        print txt
        rf.write(txt + "\n")
    print "\n------------------- Fail -------------------"
    for item in fail_accounts:
        user = item[0]
        pwd = item[1]
        txt = "[Fail ] %s" % user
        print txt
        rf.write(txt + "\n")
    txt = "\nAccounts total: %d, success: %d, fail: %d, had voted: %d" % (total, success, len(fail_accounts), len(voted_accounts))
    print txt
    rf.write(txt + "\n")
    rf.close()

    wait = raw_input()
    return 


if __name__ == '__main__':
    main()

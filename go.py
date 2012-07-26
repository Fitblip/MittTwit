import json
import urllib2
import sys
import time
import pickle

def getFollowerCount(user):
    post = 'screen_name=%s' % user
    req = urllib2.Request('http://api.twitter.com/1/users/lookup.json', post)
    httpData = urllib2.urlopen(req).read()
    return json.loads(httpData)[0]['followers_count']

def lookupIDs(cursor):
    data = urllib2.urlopen('https://api.twitter.com/1/followers/ids.json?cursor=%d&screen_name=MittRomney' % cursor ).read()
    jsonData = json.loads(data)
    return jsonData

def postLookup(ids):
    post = 'include_entities=true&user_id='
    for id in ids:
        if id != ids[-1]:
            post += str(id) + ','
        else:
            post += str(id)
    req = urllib2.Request('http://api.twitter.com/1/users/lookup.json', post)
    # We try to make the connection, but if we fail, wait 10 seconds and continue
    try:
        httpData = urllib2.urlopen(req).read()
        jsonData = json.loads(httpData)
    except urllib2.HTTPError, error:
        time.sleep(25)
        httpData = urllib2.urlopen(req).read()
        jsonData = json.loads(httpData)
    except:
        time.sleep(10)
        httpData = urllib2.urlopen(req).read()
        jsonData = json.loads(httpData)
    return jsonData

def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

# Get all IDs and store them into ids
def getAllIDs():
    cursor = -1
    id_count = 5000
    ids = []
    for i in range(0,(follower_count / 5000)):
        returnList = lookupIDs(cursor)
        print "Getting [%d/%d] IDs" % (i+1,(follower_count/5000))
        ids += returnList['ids']
        cursor = returnList['next_cursor']
        id_count += 5000
        time.sleep(25)

#
# Total followers = 814,303
# IDs == 163 pages.
# Total reqs == 50*163 => 8150 requests
# 8150 / 150 => 54.33 hours
#
#

def contains(small, big):
    for i in xrange(len(big)-len(small)+1):
        for j in xrange(len(small)):
            if big[i+j] != small[j]:
                break
        else:
            return i, i+len(small)
    return False

class searchTwitter():
    def __init__(self):
        self.ids = []
        try:
            with open('mitt.followers.done.txt') as f:
                self.done = f.read().splitlines()
                self.done = [int(column) for column in  self.done]
        except:
            self.done = []
        # Parse out request into main JSON
        with open('mitt.ids.txt') as f:
            self.ids = list(pickle.load(f))
        self.follower_count = len(self.ids)
    def search(self):
        self.init=100
        # Break up list of ID's into 100 id chunks to be posted
        for chunk in chunks(self.ids,100):
            if not contains(chunk,self.done):
                print "[%d/%d] Searching" % (self.init,self.follower_count),
                sys.stdout.flush()
                time.sleep(5)
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(5)
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(5)
                sys.stdout.flush()
                sys.stdout.write('.')
                time.sleep(5)
                sys.stdout.flush()
                sys.stdout.write('.')
                time.sleep(5)
                print '.'
                datas = postLookup(chunk)
                with open('mitt.followers.txt','a') as f:
                    for follower in datas:
                        f.write(json.dumps(follower)+'\n')
                self.init += 100
                with open('mitt.followers.done.txt','a') as f:
                    for id in chunk:
                        f.write(str(id)+'\n')
                self.done += chunk
            else:
                print "[%d/%d] Chunk already done" % (self.init,self.follower_count)
                self.init += 100

if __name__ == "__main__":
    searcher = searchTwitter()
    searcher.search()

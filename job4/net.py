import re
import bs4
import urllib
import urllib2
from cookielib import CookieJar

login_url = 'http://www.cc98.org/login.asp'
reply_url = 'http://www.cc98.org/SaveReAnnounce.asp'

class Replyer(object):
    
    def __init__(self, username, password):
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(CookieJar()))
        self.opener.open(login_url, urllib.urlencode(dict(
            username=username,
            password=password,
            action='chk'
        )))

    def info(self, url):
        soup = bs4.BeautifulSoup(self.opener.open(url).read(), 'lxml')
        keys = ('RootID', 'followup', 'UserName', 'passwd', 'star', 'signflag')
        d = {key: soup.find(attrs={'name': key})['value'] for key in keys}
        d = {

            'method' = 'fastreply',
            'Expression' = 'face7.gif',
            'BoardID' = re.search(r'BoardID=(\d+)', soup.find(attrs={'name': 'frmAnnounce'})['action']).group(1)
        }
        d['method'] = 'fastreply'
        d['Expression'] = 'face7.gif'
        d['BoardID'] = re.search(r'BoardID=(\d+)', soup.find(attrs={'name': 'frmAnnounce'})['action']).group(1)
        return d
    
    def reply(self, url):
        d = self.info(url)
        d['Content'] = self.content(url)
        data = self.opener.open(urllib2.Request(
            reply_url, 
            headers={'Referer': 'http://www.cc98.org'}, 
            data=urllib.urlencode(d)
        )).read()
        return d['Content']
    
    def content(self, url):
        return 'from net'

#with open('password') as f:
    #password = f.read().strip()
    
r = Replyer('hyz98', 'huan9hu1')
print r.reply('http://www.cc98.org/dispbbs.asp?boardID=509&ID=4223610&page=1')
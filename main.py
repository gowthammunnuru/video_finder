
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
import tornado.options
import os.path,os
from tornado.options import define, options
import json
from bson import json_util
import sqlite3,datetime,itertools
from operator import itemgetter
from dateformat import FancyDateTimeDelta,FancyTimeDelta
from getVideosList import getVideos
import re

location = os.environ["STUDIO"]
if location == "TTP":
    site_url = 'http://streaming.ddu-india.com/studio/train/streaming/'
else:
    site_url = 'http://web.anim.dreamworks.com/studio/train/streaming/'

define("port", default=80, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        settings = {
            "login_url": "/home",
			'template_path': os.path.join(base_dir, "template"),
			'static_path': os.path.join(base_dir, "static"),
			'debug':True,
		}
        tornado.web.Application.__init__(self, [
            tornado.web.url(r'/', Index, name="home"),
            tornado.web.url(r'/lVideos', LatestVideos, name="latestVideos"),
            tornado.web.url(r'/Departments', Departments, name="deptVideos"),
            tornado.web.url(r'/Videos', Videos, name="getVideos"),
            tornado.web.url(r'/search.json', Search, name="Search"),
            tornado.web.url(r'/search_pre.json', Search_Pre, name="Search_Pre"),
            
        ], **settings)

class Index(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
        
class LatestVideos(tornado.web.RequestHandler):
    def get(self):
        stdate = self.get_argument("stdate")
        enddate = self.get_argument("enddate")
        try:
            searchval = self.get_argument("searchval")
        except:
            searchval = ''
        latestVideosdict = self.latestVideosMsg(stdate,enddate,searchval)
        actualList = []
        for i in latestVideosdict:
            actualList.append(list(i))
        actualList = sorted(actualList,key=itemgetter(2),reverse=True)
        for j in actualList:
            if not os.path.exists('/studio/train/streaming/'+j[5]+'/Film.php'):
                base_folder_name = os.path.basename(j[5])
                if os.path.exists('/studio/train/streaming/'+j[5]+'/'+base_folder_name+'.html'):
                    j.append(site_url+j[5]+'/'+base_folder_name+'.html')
                elif os.path.exists('/studio/train/streaming/'+j[5]+'/'+'Player.html'):
                    j.append(site_url+j[5]+'/Player.html')
		else:
                    j.append('------')
	    else:
                j.append(site_url+j[5]+'/Film.php')
            if not os.path.exists('/studio/train/streaming/'+j[5]+'/slate.png'):        
                j[5] = 'static/media/Training.png'
            else:
                j[5] = site_url+j[5]+'/slate.png'
            if ':' not in j[3]:
                j[3] = "{0}".format(datetime.timedelta(seconds=int(float(j[3]))))

            if ':' in j[3]:
                time_object = FancyTimeDelta(j[3])
                j.append(j[3])
                j[3] = time_object.final_val
            date_object = j[2].split('-')
            date_object[0],date_object[1],date_object[2] = date_object[1],date_object[2],date_object[0]
            j[2] = '-'.join(date_object)
            '''
            j.append('http://web.anim.dreamworks.com/studio/train/streaming/'+j[2]+'/Film.php')
            if os.path.exists('/studio/train/streaming/'+j[2]+'/slate.png'):        
                j[2] = 'http://web.anim.dreamworks.com/studio/train/streaming/'+j[2]+'/slate.png'
            else:
                j[2] = 'static/media/Training.png'
            '''
        omit = {'-----'}
	actualList = [item for item in actualList if all(x not in omit for x in item)]
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(actualList))

    def find_word(self, text, search):
        try:
            result = re.findall('\\b'+search+'\\b', text, re.IGNORECASE)
        except Exception as e:
	    result = []
        if len(result)>0:
           return True
        else:
           return False

    def latestVideosMsg(self,stdate,enddate,searchval):
        if not stdate and not enddate:
            startDay = startDay - datetime.timedelta(days=31)
            endDay = datetime.date.today()
            searchval = ''
        else:
            startDay = stdate
            endDay = enddate
            searchvl = searchval      
        date_object = startDay.split('-')
        date_object[0],date_object[1],date_object[2] = date_object[2],date_object[0],date_object[1]
        startDay = '-'.join(date_object)
        date_object1 = endDay.split('-')
        date_object1[0],date_object1[1],date_object1[2] = date_object1[2],date_object1[0],date_object1[1]
        endDay = '-'.join(date_object1)
        bList = []
        connSqlite = sqlite3.connect(os.getcwd()+'/newdb.sqlite3')#sqlite3.connect('/studio/train/streaming/bin/Video_Finder/newdb.sqlite3')
        cursor = connSqlite.cursor()
        cursor.execute('Select * from Course_Details where recordDate between ? AND ?',(startDay,endDay))
        for i in cursor.fetchall():
            if searchvl == 'null':
                bList.append(i)
            else:
                if self.find_word(i[0],searchvl):
                    bList.append(i)
        connSqlite.close()
        return bList

class Departments(tornado.web.RequestHandler):
    def get(self):
        if os.path.isdir('/studio/train/streaming/Learning_Minutes'):
            deptList = {'Categories':['Animation', 'ArtDev', 'CFX', 'CharTD', 'Core Classes', 'Crowds', 'FX', 'IMF', 'Layout', 'Learning Minutes', 'Light', 'Matt Paint', 'Mari', 'Modeling',\
                                  'Surfacing', 'TDs', 'Torch']}
        else:
            deptList = {'Categories':['Animation', 'ArtDev', 'CFX', 'CharTD', 'Core Classes', 'Crowds', 'FX', 'IMF', 'Layout', 'Light', 'Matt Paint', 'Mari', 'Modeling',\
                                  'Surfacing', 'TDs', 'Torch']}
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(deptList))

class Videos(tornado.web.RequestHandler):
    def get(self):
        # import pdb; pdb.set_trace()
        dept = self.get_argument("dept")
        try:
            searchval = self.get_argument("searchval")
        except:
            searchval = 'null'      
        getVideosobject = getVideos(dept+'/',searchval)
        actualList = []
        for i in getVideosobject.Videosdict:
            actualList.append(list(i))
        if searchval == 'Learning Minutes':
            pass
        else:
            actualList = sorted(actualList,key=itemgetter(2),reverse=True)
        for j in actualList:
            if not os.path.exists('/studio/train/streaming/'+j[5]+'/Film.php'):
                base_folder_name = os.path.basename(j[5])
                if os.path.exists('/studio/train/streaming/'+j[5]+'/'+base_folder_name+'.html'):
                    j.append(site_url+j[5]+'/'+base_folder_name+'.html')
                elif os.path.exists('/studio/train/streaming/'+j[5]+'/'+'Player.html'):
                    j.append(site_url+j[5]+'/Player.html')
		else:
                    j.append('-----')
	    else:
                j.append(site_url+j[5]+'/Film.php')
            if not os.path.exists('/studio/train/streaming/'+j[5]+'/slate.png'):        
                j[5] = 'static/media/Training.png'
            else:
                j[5] = site_url+j[5]+'/slate.png'
            if ':' not in j[3]:
                j[3] = "{0}".format(datetime.timedelta(seconds=int(float(j[3]))))

            if ':' in j[3]:
                time_object = FancyTimeDelta(j[3])
                j.append(j[3])
                j[3] = time_object.final_val
            '''
            date_object = FancyDateTimeDelta(j[2])
            j[2] = date_object.final_val
            '''
            date_object = j[2].split('-')
            date_object[0],date_object[1],date_object[2] = date_object[1],date_object[2],date_object[0]
            j[2] = '-'.join(date_object)
        omit = {'-----'}
	actualList = [item for item in actualList if all(x not in omit for x in item)]
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(actualList,default=json_util.default)) 

class Search(tornado.web.RequestHandler):
    def get(self):
        search = self.get_argument("query")
        if search=='':
            self.render('404.html')
        actualList = []
        criteria = self.search_data(search)        
        for i in criteria:
            actualList.append(list(i))
        
        actualList = sorted(actualList,key=itemgetter(2),reverse=True)
        for j in actualList:
            if not os.path.exists('/studio/train/streaming/'+j[5]+'/Film.php'):
                base_folder_name = os.path.basename(j[5])
                if os.path.exists('/studio/train/streaming/'+j[5]+'/'+base_folder_name+'.html'):
                    j.append(site_url+j[5]+'/'+base_folder_name+'.html')
                elif os.path.exists('/studio/train/streaming/'+j[5]+'/'+'Player.html'):
                    j.append(site_url+j[5]+'/Player.html')
		else:
                    j.append('-----')
	    else:
                j.append(site_url+j[5]+'/Film.php')
            if not os.path.exists('/studio/train/streaming/'+j[5]+'/slate.png'):        
                j[5] = 'static/media/Training.png'
            else:
                j[5] = site_url+j[5]+'/slate.png'
            if ':' not in j[3]:
                j[3] = "{0}".format(datetime.timedelta(seconds=int(float(j[3]))))

            if ':' in j[3]:
                time_object = FancyTimeDelta(j[3])
                j.append(j[3])
                j[3] = time_object.final_val
            ''' time format as few days ago'''
            # date_object = FancyDateTimeDelta(j[2])
            # j[2] = date_object.final_val
            date_object = j[2].split('-')
            date_object[0],date_object[1],date_object[2] = date_object[1],date_object[2],date_object[0]
            j[2] = '-'.join(date_object)
        omit = {'-----'}
	actualList = [item for item in actualList if all(x not in omit for x in item)]
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(actualList,default=json_util.default))

    def find_word(self, text, search):
        result = re.findall('\\b'+search+'\\b', text, re.IGNORECASE)
        
        if len(result)>0:
           return True
        else:
           return False

    def search_data(self, query):
        bList,dVariable,originalList = [],0,[]
        connSqlite = sqlite3.connect(os.getcwd()+'/newdb.sqlite3')#sqlite3.connect('/studio/train/streaming/bin/Video_Finder/newdb.sqlite3')
        cursor = connSqlite.cursor()
        cursor.execute('Select * from Course_Details')
        
        for i in cursor.fetchall():        
            if self.find_word(i[1],query):
                bList.append(i)
                 
        cursor.execute('Select * from Course_Details where courseName like ?',('%'+query+'%',)) 
        for j in cursor.fetchall():
            bList.append(j)
        connSqlite.close() 
        return sorted(set(bList), key=lambda kv: kv[0], reverse=True)


class Search_Pre(tornado.web.RequestHandler):
    def get(self):
        search = self.get_argument("query")
        if search=='':
            self.render('404.html')
        actualList = []
        criteria = self.search_data(search)        
        for i in criteria:
            actualList.append(list(i))        
        actualList = sorted(actualList,key=itemgetter(2),reverse=True)
        for j in actualList:
            if not os.path.exists('/studio/train/streaming/'+j[5]+'/Film.php'):
                base_folder_name = os.path.basename(j[5])
                if os.path.exists('/studio/train/streaming/'+j[5]+'/'+base_folder_name+'.html'):
                    j.append(site_url+j[5]+'/'+base_folder_name+'.html')
                elif os.path.exists('/studio/train/streaming/'+j[5]+'/'+'Player.html'):
                    j.append(site_url+j[5]+'/Player.html')
		else:
                    j.append('-----')
	    else:
                j.append(site_url+j[5]+'/Film.php')
            if not os.path.exists('/studio/train/streaming/'+j[5]+'/slate.png'):        
                j[5] = 'static/media/Training.png'
            else:
                j[5] = site_url+j[5]+'/slate.png'
            if ':' not in j[3]:
                j[3] = "{0}".format(datetime.timedelta(seconds=int(float(j[3]))))

            if ':' in j[3]:
                time_object = FancyTimeDelta(j[3])
                j.append(j[3])
                j[3] = time_object.final_val
            date_object = j[2].split('-')
            date_object[0],date_object[1],date_object[2] = date_object[1],date_object[2],date_object[0]
            j[2] = '-'.join(date_object)

        omit = {'-----'}
	actualList = [item for item in actualList if all(x not in omit for x in item)]
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(actualList,default=json_util.default))

    def find_word(self, text, search):
        try:
            result = re.findall('\\b'+search+'\\b', text, re.IGNORECASE)
        except Exception as e:
            result = [] 
        if len(result)>0:
           return True
        else:
           return False

    def search_data(self, query):
        bList,dVariable,originalList = [],0,[]
        connSqlite = sqlite3.connect(os.getcwd()+'/newdb.sqlite3')#sqlite3.connect('/studio/train/streaming/bin/Video_Finder/newdb.sqlite3')
        cursor = connSqlite.cursor()
        cursor.execute('Select * from Course_Details')
        for i in cursor.fetchall():            
            if self.find_word(i[4],query):
                bList.append(i)
                
        cursor.execute('Select * from Course_Details where presenterName like ?',('%'+query+'%',))
        for j in cursor.fetchall():
            bList.append(j)
        return sorted(set(bList), key=lambda kv: kv[0], reverse=True)


def main():
    tornado.options.parse_command_line()
    Application().listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

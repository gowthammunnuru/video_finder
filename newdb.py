import sys,gst
import sqlite3,re,os
from BeautifulSoup import BeautifulSoup
import studioenv
from studio import io
import subprocess
import dateutil.parser as dateparser
from random import randint
#------------------------------------------------------------------------------
#
# Absolute path for ffmpeg binary which will give the length of a video file
#
#------------------------------------------------------------------------------
_ffmpeg2 = "/rel/third_party/ffmpeg/2.2.1/bin/ffmpeg"

getCurrentDirectory = os.getcwd()
baseOfWorkingDirectory = os.path.basename(getCurrentDirectory)

if baseOfWorkingDirectory == 'Video_Finder' and '/studio/train/streaming' in getCurrentDirectory:
    folderToExecute = '/studio/train/streaming/bin/Video_Finder'
elif baseOfWorkingDirectory != 'Video_Finder' and '/studio/train/streaming' in getCurrentDirectory:
    folderToExecute = '/studio/train/streaming/bin/Video_Finder'
else:
    folderToExecute = os.path.dirname(sys.argv[0])
    if folderToExecute == '':
    	folderToExecute = getCurrentDirectory

print folderToExecute,'-------------'

def readDuration( mediaFilePath):
        """
        Get the duration of a media file.  I've tested this on .flv, .f4v, .mp4, and .ogv files.  It fails on .swf files.
        Note; This might be easier with ffmpeg ... but I didn't know we have this in-house.  However, we do have gstreamer.
        So I modified something I found on: http://stackoverflow.com/questions/2440554/how-do-i-find-the-length-of-media-with-gstreamer
        """
        durationSeconds = _gstDuration(mediaFilePath)
        if durationSeconds == 0:
            durationSeconds = _ffmpegDuration(mediaFilePath)
            if durationSeconds == 0:
                pass
            else:
                pass
        return durationSeconds

def _gstDuration( mediaFilePath):
        player = gst.parse_launch("filesrc name=source ! decodebin2 ! fakesink")
        player.get_by_name("source").set_property("location", mediaFilePath)
        player.set_state(gst.STATE_PLAYING)
        player.get_state(timeout=3*gst.SECOND)
        format = gst.Format(gst.FORMAT_TIME)
        try:
            duration = player.query_duration(format)[0]
        except:
            return 0
        player.set_state(gst.STATE_NULL)
        return float(duration / gst.SECOND)

def _ffmpegDuration (mediaFilePath):
        cmd = "%s -i %s" % (_ffmpeg2, mediaFilePath)
        cmdOut = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        errValue = cmdOut.stderr.read().strip()
        try:
            matches = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),", errValue, re.DOTALL).groupdict()
            duration = int(matches['hours'])*60*60 + int(matches['minutes'])*60 + round(float(matches['seconds']))
        except Exception as e:
            return 0
        return duration

def getApproxCreation(abspath):
    withDate = []
    try:
        for root, dirs, files in os.walk(abspath): # Crawling through the directory
            for f in files: # Iterating through the files which is a list
                try:
                    withDate.append(datetime.fromtimestamp(os.path.getmtime(root+f)).date()) # getting the last modified time of a respective file
                except Exception as f:
                    withDate.append('')
        withDate = [x for x in withDate if x] 
        withDate.sort() # Sorting by Date
        date =  withDate[0] # Choose the first one (Oldest one)
    except Exception as e:
        date = "???"
    return date

def videoDatestamp(videopath):
    # We compute the date using two methods:
    # Method 1: Parse the directory name for a date;
    # Method 2: Find the Approximate creation of the directory.
    # If Method 1 produces an answer, we return it, but warn if Method 2 is older.
    # If Method 1 fails, we return the results of Method 2.
    
    # Note: If performance was a concern, we would only compute Method 2 if
    # Method 1 fails.  But for the purpose of this script I compute both anyway,
    # as performance is not an issue ... and it makes a good check.
    
    # Method 1: try and parse it from the directory name.  Note: This seems 
    # convoluted because there is a wide variety of date formats in our video names.  
    # E.g. 8-17-13 vs. 8_17_13 vs. Day_2_8-17-13 vs. Day_2_8_17_2013.
    from datetime import datetime, timedelta, date
    dirpath = os.path.dirname(videopath)
    # Lets try a series of compiled regex's.
    dateYYYYRE = re.compile('.*?(\d+)[-_](\d+)[-_](20\d\d).*')  # Four-digit year.
    dateDashRE = re.compile('.*?(\d+)-(\d+)-(\d\d).*')  # Dashes.
    dateUscoreRE = re.compile('.*?(\d+)_(\d+)_(\d\d).*')  # Underscores.
    m = dateYYYYRE.match(dirpath)
    if not m:
        m = dateDashRE.match(dirpath)
    if not m:
        m = dateUscoreRE.match(dirpath)
    if m:       # Matches one of the above formats.
        dateStr = "%s-%s-%s" % (m.group(1), m.group(2), m.group(3))
        try:
            date1 = dateparser.parse(dateStr, fuzzy=True).date()
        except:
            date1 = "???"
    else:
        dateStr = "(Same)"
        date1 = "???"
        
    # Method 2: Get Approximate creation of the directory.
    if os.path.isabs(videopath):
        abspath = videopath
    else:
        abspath = "%s/%s" % (streaming_dir, videopath)
        
    date2 = getApproxCreation(abspath)

    # Compare the two values, and return Method 1 if it succeeded.
    ## print "%s \t%s \t%s \t%s" % (date1, date2, videopath, dateStr)       ## Useful for debugging.
    try:
        if str(date1) != "???" and str(date2) != "???" and str(date2) < str(date1):
            print "Warning: Player file date (%s) is older than date in name (%s): %s" % (date2, date1, videopath)
    except:
        print "Warning: Player file date (%s) is older than date in name (%s): %s" % (date2, date1, videopath)
        
    if str(date1) != "???":
        return date1
    else:
        if date2 == "???":
            date2 = ''
        return date2

def vidIDGen(courseName):
    courseEx = courseName.split('_')
    courseID1 = courseEx[0].replace(' ','')[0:3]
    if len(courseEx) == 1:
        courseID2 = courseEx[0].replace(' ','')[-3:]
    else:
        courseID2 = courseEx[1].replace(' ','')[0:3]
    return courseID1+courseID2+str(randint(1000,9999))

def vidChapIDGen(chapName):
    courseEx = chapName.split(' ')
    if (len(courseEx[0]) >= 3) and (not bool(re.search(r'\d', courseEx[0]))):
        courseID1 = courseEx[0].replace(' ','')[0:3]
    elif bool(re.search(r'\d', courseEx[0])):
        if not len(courseEx) == 1:
            courseID1 = courseEx[1].replace(' ','')[0:3]
        else:
            courseID1 = courseEx[0].replace(' ','')[0:3]
    else:
        courseID1 = courseEx[0].replace(' ','')[0:1]
    if len(courseEx) == 1:
        courseID2 = courseEx[0].replace(' ','')[-3:]
    else:
        courseID2 = courseEx[1].replace(' ','')[0:3]
    return courseID1+courseID2+str(randint(1000,9999))

def findDate( path ):

    # First, make sure the pathStr is an abspath.
    pathStr = os.path.abspath(path)

    # Then find the player file in the directory.
    if os.path.isdir(pathStr):
        dirStr = pathStr
    else:
        dirStr = os.path.dirname(pathStr)

    """
    Look something that looks like a date (recording date) in the directory name.
    """
    dirString = os.path.basename(dirStr)
    dirString = re.sub(r'(.*?)[Vv][Ii][Dd][-_]*\d+.*', r'\1', dirString)   # Remove any vid ticket ... looks like year.
    from datetime import datetime, timedelta, date
    tomorrow = date.today() + timedelta(days=1)
    try:
        dtParsed = dateparser.parse(dirString, fuzzy=True, default=tomorrow)
    except:
        io.warn ("Unable to find date in directory name %s" % dirString)
        return ""
    if dtParsed == tomorrow:
        return ""
    else:        
        return dtParsed.isoformat()

def addTime( values , a ):
    listDuration = []
    if a == 0 :
        listDuration = []

def getData(content,connSqlite='null'):
    
    count = 0
    import datetime
    for i in content:
        count = count+1
        xmlLoc = i+"videoXMLData.xml"
        if os.path.exists(xmlLoc):
            xmlContent = BeautifulSoup(open (xmlLoc, 'r').read())
            try:
                videoTitle = xmlContent.videotitle.string
            except Exception as e:
                print xmlLoc,'Video Title is not there'
                videoTitle = None
            try:
                courseName = xmlContent.videotitle.string.replace('_',' ')
            except Exception as e:
                print xmlLoc,'Course Name is not there'
                courseName = None
            try:
                coursePresenter = xmlContent.videopresenter.string
            except Exception as e:
                print xmlLoc,'Course Presenter is not there'
                coursePresenter = None
            try:
                testpubdate = xmlContent.videopubdate.string
            except Exception as e:
                print xmlLoc,'Published Date is not there'
                testpubdate = None
            if not testpubdate:
                altdate = videoDatestamp(i)
            else:
                testpubdate = (re.sub(r'[^A-Za-z0-9- ,]+', '', testpubdate)).strip(' ')                
                if any(c.isalpha() for c in testpubdate):
                    try:
                        dateWithAlphs = datetime.datetime.strptime(str(testpubdate), "%B %d, %Y").date()
                        testpubdate = str(dateWithAlphs)
                    except Exception as dateError:
                        print dateError
                else:
                    result = re.findall(r'(.*?)[Vv][Ii][Dd][-_]*\d+.*', i, re.IGNORECASE)
                    testpubdateJustIncase = ''
                    if len(result)>0:
                        testpubdateJustIncase = findDate(i)  
                    else:
                        pass
		    if not testpubdateJustIncase:
			pass
		    elif testpubdateJustIncase == testpubdate:
			pass
		    else:
			testpubdate = testpubdateJustIncase
                if testpubdate:
                    testpubdate = re.sub(r'(\d\d\d\d)-(\d\d)-(\d\d)', r'\2-\3-\1', testpubdate)
                    a = testpubdate.split('-')
                    a[0],a[1],a[2] = a[2],a[0],a[1]
                    altdate = '-'.join(a)                    
                else:
                    altdate = None
            chap_duration,courseDur,abc = [],0,0
            for chapter in xmlContent.findAll('chapter'):
                try:
                    chap_uri = chapter.find('chapuri').string
                    chap_dura = chapter.find('chapdur').string                    
                    if chap_dura:
                        if chap_uri:                        
                            chap_uri = re.sub(r'[^A-Za-z0-9-_,.]+', '', chap_uri).strip(' ')
                        if ':' in chap_dura:
                            chap_dura = re.sub(r'[^0-9:]+', '', chap_dura).strip(' ')                           
                            durationWithColon = datetime.datetime.strptime(str(chap_dura), "%H:%M:%S")
                            dt1 = datetime.timedelta(hours=durationWithColon.hour,minutes=durationWithColon.minute,seconds=durationWithColon.second)
                            chap_duration.append(dt1)                                
                        else:
                            chap_duration.append(float(chap_dura))
                    else:
                        if chap_uri:                        
                            chap_uri = re.sub(r'[^A-Za-z0-9-_,.]+', '', chap_uri).strip(' ')
                        chap_duration.append(readDuration(i+chap_uri))                
                except Exception as e:
                    print xmlLoc,'Chapter URI or Chapter Duration is not there',e,chap_dura
                    chap_uri, chap_duration = None,[]            
            if chap_duration:
                try:
                    courseDur = str(sum(chap_duration, datetime.timedelta()))
                except:
                    courseDur = sum(chap_duration)
            if videoTitle:
                videoTitle = (re.sub(r'[^A-Za-z0-9- ,]+', '', videoTitle)).strip(' ')
            if courseName:
                courseName = (re.sub(r'[^A-Za-z0-9- ,]+', '', courseName)).strip(' ')
            if coursePresenter:
                if ',' in coursePresenter:
                    coursePresenter = ((re.sub(r'[^A-Za-z0-9- ,]+', '', coursePresenter)).strip(' ')).split(',')
                else:
                    coursePresenter = ((re.sub(r'[^A-Za-z0-9- ,]+', '', coursePresenter)).strip(' ')).split(' ')
            if videoTitle:
                courseVidID = vidIDGen(videoTitle)
            coursePath = i.replace('/studio/train/streaming/','')[:-1]
        
        if courseVidID:
            # if coursePresenter:
            if altdate:
                if courseDur:
                    if courseName:
                        if coursePath:
                            print courseVidID,coursePresenter,altdate,courseDur,courseName,coursePath
                            updatingDatabase(courseVidID , courseName , altdate , courseDur , coursePresenter , coursePath , count , connSqlite)
        connSqlite.commit()

def getData_core(content,connSqlite='null'):
    
    count = 0
    import datetime
    for i in content:
        count = count+1
        xmlLoc = i+"videoXMLData.xml"
        if os.path.exists(xmlLoc):
            xmlContent = BeautifulSoup(open (xmlLoc, 'r').read())
            try:
                videoTitle = xmlContent.videotitle.string
            except Exception as e:
                print xmlLoc,'Video Title is not there'
                videoTitle = None
            try:
                courseName = xmlContent.videotitle.string.replace('_',' ')
            except Exception as e:
                print xmlLoc,'Course Name is not there'
                courseName = None
            try:
                coursePresenter = xmlContent.videopresenter.string
            except Exception as e:
                print xmlLoc,'Course Presenter is not there'
                coursePresenter = None
            try:
                testpubdate = xmlContent.videopubdate.string
            except Exception as e:
                print xmlLoc,'Published Date is not there'
                testpubdate = None
            if not testpubdate:
                altdate = videoDatestamp(i)
            else:
                testpubdate = (re.sub(r'[^A-Za-z0-9- ,]+', '', testpubdate)).strip(' ')                
                if any(c.isalpha() for c in testpubdate):
                    try:
                        dateWithAlphs = datetime.datetime.strptime(str(testpubdate), "%B %d, %Y").date()
                        testpubdate = str(dateWithAlphs)
                    except Exception as dateError:
                        print dateError
                else:
                    result = re.findall(r'(.*?)[Vv][Ii][Dd][-_]*\d+.*', i, re.IGNORECASE)
                    testpubdateJustIncase = ''
                    if len(result)>0:
                        testpubdateJustIncase = findDate(i)  
                    else:
                        pass
		    if not testpubdateJustIncase:
			pass
		    elif testpubdateJustIncase == testpubdate:
			pass
		    else:
			testpubdate = testpubdateJustIncase                               
                if testpubdate:
                    testpubdate = re.sub(r'(\d\d\d\d)-(\d\d)-(\d\d)', r'\2-\3-\1', testpubdate)
                    a = testpubdate.split('-')
                    a[0],a[1],a[2] = a[2],a[0],a[1]
                    altdate = '-'.join(a)                    
                else:
                    altdate = None
                            
            chap_duration,courseDur,abc = [],0,0
            for chapter in xmlContent.findAll('chapter'):
                try:
                    chap_uri = chapter.find('chapuri').string
                    chap_dura = chapter.find('chapdur').string                    
                    if chap_dura:
                        if chap_uri:                        
                            chap_uri = re.sub(r'[^A-Za-z0-9-_,.]+', '', chap_uri).strip(' ')
                        if ':' in chap_dura:
                            chap_dura = re.sub(r'[^0-9:]+', '', chap_dura).strip(' ')                           
                            durationWithColon = datetime.datetime.strptime(str(chap_dura), "%H:%M:%S")
                            dt1 = datetime.timedelta(hours=durationWithColon.hour,minutes=durationWithColon.minute,seconds=durationWithColon.second)
                            chap_duration.append(dt1)                                
                        else:
                            chap_duration.append(float(chap_dura))
                    else:
                        if chap_uri:                        
                            chap_uri = re.sub(r'[^A-Za-z0-9-_,.]+', '', chap_uri).strip(' ')
                        chap_duration.append(readDuration(i+chap_uri))                
                except Exception as e:
                    print xmlLoc,'Chapter URI or Chapter Duration is not there',e,chap_dura
                    chap_uri, chap_duration = None,[]            
            if chap_duration:
                try:
                    courseDur = str(sum(chap_duration, datetime.timedelta()))
                except:
                    courseDur = sum(chap_duration)
            if videoTitle:
                videoTitle = (re.sub(r'[^A-Za-z0-9- ,]+', '', videoTitle)).strip(' ')
            if courseName:
                courseName = (re.sub(r'[^A-Za-z0-9- ,]+', '', courseName)).strip(' ')
            if coursePresenter:
                if ',' in coursePresenter:
                    coursePresenter = ((re.sub(r'[^A-Za-z0-9- ,]+', '', coursePresenter)).strip(' ')).split(',')
                else:
                    coursePresenter = ((re.sub(r'[^A-Za-z0-9- ,]+', '', coursePresenter)).strip(' ')).split(' ')
            if videoTitle:
                courseVidID = vidIDGen(videoTitle)
            coursePath = i.replace('/studio/train/streaming/','')[:-1]
        if courseVidID:
            if coursePresenter:
                if altdate:
                    if courseDur:
                        if courseName:
                            if coursePath:
                                print courseVidID,coursePresenter,altdate,courseDur,courseName,coursePath
                                updatingDatabase_core(courseVidID , courseName , altdate , courseDur , coursePresenter , coursePath , count , connSqlite)
        connSqlite.commit()

def updatingDatabase_core(courseVidID , courseName , altdate , courseDur , coursePresenter , coursePath, count, connSqlite):
    if len(coursePresenter) == 1:
        connSqlite.execute("INSERT INTO Core_Course_Details (courseVidID, courseName , recordDate, TRT, presenterName, fileLocation) VALUES (?,?,?,?,?,?)",(courseVidID,courseName,altdate,courseDur,coursePresenter[0],coursePath))
    elif len(coursePresenter) == 2:
        connSqlite.execute("INSERT INTO Core_Course_Details (courseVidID, courseName , recordDate, TRT, presenterName, fileLocation) VALUES (?,?,?,?,?,?)",(courseVidID,courseName,altdate,courseDur,coursePresenter[0]+' '+coursePresenter[1],coursePath))
    elif len(coursePresenter) > 2:
        coursePresenter = ' '.join(coursePresenter)
        connSqlite.execute("INSERT INTO Core_Course_Details (courseVidID, courseName , recordDate, TRT, presenterName, fileLocation) VALUES (?,?,?,?,?,?)",(courseVidID,courseName,altdate,courseDur,coursePresenter,coursePath))
    print count,'----'

def updatingDatabase(courseVidID , courseName , altdate , courseDur , coursePresenter , coursePath, count, connSqlite):
	try:
            if len(coursePresenter) == 1:
                    connSqlite.execute("INSERT INTO Course_Details (courseVidID, courseName , recordDate, TRT, presenterName, fileLocation) VALUES (?,?,?,?,?,?)",(courseVidID,courseName,altdate,courseDur,coursePresenter[0],coursePath))
            elif len(coursePresenter) == 2:
                    connSqlite.execute("INSERT INTO Course_Details (courseVidID, courseName , recordDate, TRT, presenterName, fileLocation) VALUES (?,?,?,?,?,?)",(courseVidID,courseName,altdate,courseDur,coursePresenter[0]+' '+coursePresenter[1],coursePath))
            elif len(coursePresenter) > 2:
                    coursePresenter = ' '.join(coursePresenter)
                    connSqlite.execute("INSERT INTO Course_Details (courseVidID, courseName , recordDate, TRT, presenterName, fileLocation) VALUES (?,?,?,?,?,?)",(courseVidID,courseName,altdate,courseDur,coursePresenter,coursePath))
	except:
            connSqlite.execute("INSERT INTO Course_Details (courseVidID, courseName , recordDate, TRT, presenterName, fileLocation) VALUES (?,?,?,?,?,?)",(courseVidID,courseName,altdate,courseDur,coursePresenter,coursePath))
	print count    

def updateFullDatebase(value):
    # This function will be called from mvl_create.py if 
    # the day is Friday
    # 
    # Update the sqlite database completely
    # By deleting the database and creating the tables freshly
    if value == 'complete':
        os.system(folderToExecute+'/xmlList/findStructure')
        os.system('mv '+os.getcwd()+'/fullXMLList.txt '+folderToExecute+'/xmlList/')
        os.system('chmod 666 '+folderToExecute+'/xmlList/fullXMLList.txt')
        os.system('rm -rf '+folderToExecute+'/newdb.sqlite3')
        connSqlite = sqlite3.connect(folderToExecute+'/newdb.sqlite3')
        connSqlite.execute('CREATE TABLE Course_Details (courseVidID TEXT, courseName TEXT, recordDate date, TRT TEXT, presenterName TEXT,fileLocation TEXT )')
        connSqlite.execute('CREATE TABLE Core_Course_Details (courseVidID TEXT, courseName TEXT, recordDate date, TRT TEXT, presenterName TEXT,fileLocation TEXT )')
        connSqlite.commit()
        os.system('chmod 775 '+folderToExecute+'/newdb.sqlite3')
        fullListXMLfile = folderToExecute+'/xmlList/fullXMLList.txt'
        corecoursefile = folderToExecute+'/xmlList/coreclass.txt'
        with open(fullListXMLfile) as f:
            content = f.read().splitlines()
        getData(content,connSqlite)
        with open(corecoursefile) as g:
            core_content = g.read().splitlines()
        getData_core(core_content,connSqlite)
        connSqlite.commit()
        connSqlite.close()
    else:
        if not os.path.exists(folderToExecute+'/xmlList/fullXMLList.txt'):
            updateFullDatebase('complete')
        else:
            os.system('mv '+folderToExecute+'/xmlList/fullXMLList.txt '+folderToExecute+'/xmlList/fullXMLList_old.txt')
            os.system('chmod 666 '+folderToExecute+'/xmlList/fullXMLList_old.txt')
            os.system(folderToExecute+'/xmlList/findStructure')
            os.system('mv '+os.getcwd()+'/fullXMLList.txt '+folderToExecute+'/xmlList/')
            os.system('chmod 666 '+folderToExecute+'/xmlList/fullXMLList.txt')
            old_file = folderToExecute+'/xmlList/fullXMLList_old.txt'
            new_file = folderToExecute+'/xmlList/fullXMLList.txt'
            old_lines = file(old_file).read().split('\n')
            new_lines = file(new_file).read().split('\n')

            old_lines_set = set(old_lines)
            new_lines_set = set(new_lines)

            new_added_lines = old_lines_set.union(new_lines_set) - old_lines_set.intersection(new_lines_set)

            if os.path.exists(folderToExecute+'/xmlList/newfullXMLList.txt'):
                os.system('rm '+folderToExecute+'/xmlList/newfullXMLList.txt')

            for line in new_added_lines:
                os.system('echo '+line.strip()+' >> '+folderToExecute+'/xmlList/newfullXMLList.txt')

            os.system('chmod 666 '+folderToExecute+'/xmlList/newfullXMLList.txt')
            connSqlite = sqlite3.connect(folderToExecute+'/newdb.sqlite3')
            fullListXMLfile = folderToExecute+'/xmlList/newfullXMLList.txt'
            corecoursefile = folderToExecute+'/xmlList/coreclass.txt'

            if os.path.exists(fullListXMLfile):
                with open(fullListXMLfile) as f:
                    content = f.read().splitlines()
                getData(content,connSqlite)
                connSqlite.commit()
                connSqlite.close()
            else:
                print "Hurray !! Database is upto date :-)"
    

if sys.argv:
    if sys.argv[1] == '-complete':
        updateFullDatebase('complete')
    elif sys.argv[1] == '-update':
        updateFullDatebase('update')
else:
    updateFullDatebase(update)
    
    

#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sqlite3
import re,itertools

class getVideos():
    def __init__(self,toSearch,searchval):
        self.toSearch = toSearch
        self.searchval = searchval
        if self.toSearch == 'Matt Paint/':
            self.toSearch='Matte_Paint'
        elif self.toSearch == 'Learning Minutes/':
            self.toSearch='Learning_Minutes'
        if self.toSearch=="Core Classes/":
            self.Videosdict = self.getVideosMsg_Core()
        else:
            self.Videosdict = self.getVideosMsg()
        
    def find_word(self, text, search):
        result = re.findall('\\b'+search+'\\b', text)
        if len(result)>0:
           return True
        else:
           return False

    def find_word_case(self, text, search):
        result = re.findall('\\b'+search+'\\b', text, re.IGNORECASE)
        if len(result)>0:
           return True
        else:
           return False

    def getVideosMsg(self):
        animationdictionary,bList = {},[]
        connSqlite = sqlite3.connect(os.getcwd()+'/newdb.sqlite3')#sqlite3.connect('/studio/train/streaming/bin/Video_Finder/newdb.sqlite3')
        cursor = connSqlite.cursor()
        cursor.execute('Select * from Course_Details')        
        for i in cursor.fetchall():
            if self.find_word(i[5],self.toSearch):
                if self.searchval == 'null':
                    bList.append(i)
                else:
                    if self.find_word_case(i[1],self.searchval):
                      bList.append(i)
        connSqlite.close()
        return sorted(bList, key=lambda kv: kv[0], reverse=True)

    def getVideosMsg_Core(self):
        animationdictionary,bList = {},[]
        connSqlite = sqlite3.connect(os.getcwd()+'/newdb.sqlite3')#sqlite3.connect('/studio/train/streaming/bin/Video_Finder/newdb.sqlite3')
        cursor = connSqlite.cursor()
        cursor.execute('Select * from Core_Course_Details')        
        for i in cursor.fetchall():
            if self.searchval == 'null':
                bList.append(i)
            else:
                if self.find_word_case(i[1],self.searchval):
                  bList.append(i)
        connSqlite.close() 
        return sorted(bList, key=lambda kv: kv[0], reverse=True)

# v = getVideos('FX/')
# print v.Videosdict

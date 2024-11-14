# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 19:14:52 2020

@author: swseo
"""

class StompMSG(object):
    def __init__(self, msg):
        self.msg = msg
        sp = self.msg.split("\n")
        self.destination = sp[1].split(":")[1]
        self.content = sp[2].split(":")[1]
        self.subs = sp[3].split(":")[1]
        self.id = sp[4].split(":")[1]
        self.len = sp[5].split(":")[1]
        # sp[6] is just a \n
        self.message = ''.join(sp[7:])[0:-1]  # take the last part of the message minus the last character which is \00
        
    def getstompmessage(self):
        return self.message
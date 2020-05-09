# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 11:33:29 2019

@author: Raghav Utpat
"""

#import time.sleep
import os
import sqlite3
import subprocess
from datetime import datetime,time
import xml.etree.ElementTree as et


LIST_FILE = "exelist.txt"
TIMETABLE = "timetable.txt"
PYTHON_PATH = "%USERPROFILE%\\anaconda3\\python.exe"
TASK_STARTED = "started.py"
TASK_REMIND = "remind.py"
TASK_BATCH_FILE = "task.bat"
TASK_SETTINGS = "tasksettings.xml"
CWD = os.getcwd()

conn = sqlite3.connect('focus.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS tasks 
               (taskid integer PRIMARY KEY AUTOINCREMENT,
                tname text,starttime text,endtime text,isSuccess integer)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS tags 
               (tagid integer PRIMARY KEY AUTOINCREMENT,
                tag text UNIQUE)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS tag_tasks 
               (taskid integer,tagid integer,
                foreign key(taskid) references tasks(taskid),
                foreign key(tagid) references tasks(tagid))''')
               
               
if not os.path.exists(TASK_BATCH_FILE):
    with open(TASK_BATCH_FILE,"w") as f:
        f.write("@echo off")
        f.write("pushd %~dp0")
        f.write("echo %1")
        f.write("echo %2")
        f.write("%USERPROFILE%\\anaconda3\\python.exe remind.py %1 %2")
        

def editXML(**kwargs):
    ns = {'task':'http://schemas.microsoft.com/windows/2004/02/mit/task'}
    tree = et.parse(TASK_SETTINGS)
    root = tree.getroot()
    if 'path' in kwargs:
        comm = root.find('.//task:Command',ns)
        comm.text = kwargs.get('path')
    if 'start_time' in kwargs:
        timetrigger=root.find('.//task:StartBoundary',ns)
        start_time = kwargs.get('start_time')
        timetrigger.text = datetime.now().strftime(f'%Y-%m-%dT{start_time}')
    if 'batch_args' in kwargs:
        args = root.find('.//task:Arguments',ns)
        batch_args = kwargs.get('batch_args')
        args.text = ' '.join([str(i) for i in batch_args])
    tree.write(TASK_SETTINGS)
        
    
    
                

def read():
    print("Hello")
    if not os.path.exists(TIMETABLE):
        with open(TIMETABLE,"w") as f:
            f.write("#Write your timetable in this file\n#All lines starting with # will be ignored\n")
            for i in range(24):
                f.write(f"{{{i}:00-{i+1}:00}} = {{Task{i}:Tag1,Tag2}}{{Task{i+1}:Tag1,Tag3}}\n")
                        
    else:
        with open(TIMETABLE,"r+")as f:
            tt_text = f.read().split('\n')
            for line in tt_text:
                line = line.lstrip()
                try:
                    if line[0]=='#':
                        pass
                    elif line == '':
                        pass                
                    elif line[0] =='{':
                        task_details = line.split('=')
                        task_details = [task_details[i].strip()[1:-1] for i in range(len(task_details))] #trim all whitespaces and remove curly braces
                        time_det = task_details[0].split('-')
                        time_det = [time_det[i].strip() for i in range(len(time_det))]
                        time_det[0] = time(int(time_det[0].split(':')[0]),int(time_det[0].split(':')[1])).strftime("%H:%M:00")
                        time_det[1] = time(int(time_det[1].split(':')[0]),int(time_det[1].split(':')[1])).strftime("%H:%M:00")
                        tasklist = task_details[1].split('}{')
                        #details = {}
                        for i in range(len(tasklist)):
                            task = tasklist[i].split(':')[0]
                            taglist = tasklist[i].split(':')[1]
                            taglist = taglist.split(',')
                            details = (task,time_det[0],time_det[1],)
                            cursor.execute('INSERT INTO tasks values(NULL,?,?,?,NULL)',details)
                            taskid=cursor.lastrowid
                            batch_path = os.path.join(CWD, TASK_BATCH_FILE)
                            editXML(path=batch_path)
                            batch_args = (1,taskid)
                            editXML(start_time=time_det[0],batch_args=batch_args)
                            subprocess.run(["schtasks","/create","/tn","Focus"+str(taskid),"/xml",TASK_SETTINGS])
                            batch_args = (2,taskid)
                            editXML(start_time=time_det[1],batch_args=batch_args)                                            
                            subprocess.run(["schtasks","/create","/tn","Focus"+str(taskid)+"fdbk","/xml",TASK_SETTINGS])
                            for tag in taglist:
                                tagid = []
                                try :
                                    tag_tuple = (tag,)
                                    cursor.execute('INSERT INTO tags values(NULL,?)',tag_tuple)
                                    tagid.append(cursor.lastrowid)
                                except sqlite3.IntegrityError :
                                    tag_tuple = (tag,)
                                    cursor.execute('SELECT tagid from tags WHERE tag = ?',(tag_tuple))
                                    out = cursor.fetchall()[0]
                                    tagid.append(out[0])
                                print(tagid[0])
                                id_tuple = (taskid,tagid[0])
                                #insert into common table
                                cursor.execute('INSERT INTO tag_tasks values(?,?)',id_tuple)               
                except IndexError:
                    print("IndexError")
    conn.commit()

def display():
    cursor.execute('SELECT * from tasks')
    print(cursor.fetchall())
    cursor.execute('SELECT * from tags')
    print(cursor.fetchall())
    cursor.execute('SELECT * from tag_tasks')
    print(cursor.fetchall())


if not os.path.exists(LIST_FILE):
    print("This program will help you focus on work/studying by reminding you what you were supposed to be doing")
    print("\nWould you like to add a few programs that distract you ?")
    print("The program will then remind you whenever you start using these programs")
    ans = input("(if you choose n now you can still add EXEs later)\n[y/n]:")
    if ans == 'y' or ans == 'Y':
        binlist = []
        print("Please enter a list of EXEs \n(like notepad.exe for notepad or TESV.exe for skyrim)")
        print("You can change this list whenever you want")
        print("Enter 0 to stop")
        while True:
            inp = input()
            if inp=='0':
                break
            binlist.append(inp)
        sfile = open(LIST_FILE,"w")
        for binary in binlist:
            sfile.write("%s\n" %binary)
        sfile.close()
        print(binlist)
    if ans == 'n' or ans == 'N':
        sfile = open(LIST_FILE,"w")
        sfile.write("Empty")
        sfile.close()        

else:
    print("What would you like to do")
    print("1 - Read the timetable")
    print("2 - Start a task")
    print("3 - Delete a task")
    print("4 - Edit a task")
    print("5 - Show all tasks")
    print("6 - Exit")
    choice = int(input("Enter choice : "))
    print(choice)
    if choice == 1:
        print("Hi")
        read()
    elif choice == 2:
        start()
    elif choice == 3:
        delete()
    elif choice == 4:
        modify()
    elif choice == 5:
        display()
    #else:
     #   pass
    
conn.close()
                    
                
                    

# def quickstart():
    
#     name = input("Enter task name : ")
#     print("When do you want to start this task -- ")
#     date = input("Enter start date (MM/DD/YYYY) -1 for current date : ")
#     time = input("Enter start time (hh:mm in 24h format) : ")
#     duration = input("How many hours is the task going to last : ")
#     frequency = input("How frequent, in minutes, do you want the reminders(enter -1 for once only) : ")
    
#     #create a task to inform user that their task has begun
#     if(date==-1):
#         subprocess.run(["schtasks","/create","/tn",name+"_started","/tr",PYTHON_PATH+" "+TASK_STARTED+" "+name,"/sc","once","/st",time])
#     else:    
#         subprocess.run(["schtasks","/create","/tn",name+"_started","/tr",PYTHON_PATH+" "+TASK_STARTED+" "+name,"/sc","once","/sd",date,"/st",time])
    
#     #add reminder after each duration
#     if(frequency==-1):
#         subprocess.run(["schtasks","/create","/tn",name+"_reminder","/tr",PYTHON_PATH+" "+TASK_REMIND+" "+name,"/sc","once","/sd",date,"/st",time])
#     else:
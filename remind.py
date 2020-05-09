# -*- coding: utf-8 -*-
"""
Created on Sun May  3 04:13:53 2020

@author: Raghav Utpat
"""

import sqlite3
#from os import getcwd
import sys
import subprocess

conn = sqlite3.connect('focus.db')
cursor = conn.cursor()

def start():
    taskid =[]
    try:
        taskid.append(sys.argv[2])
    except IndexError:
        print("Error : no taskid provided")
    cursor.execute('SELECT tname from tasks where taskid = ?',(taskid[0],))
    tname = cursor.fetchall()[0]
    cursor.execute('SELECT endtime from tasks where taskid = ?',(taskid[0],))
    endtime = cursor.fetchall()[0]
    print("########################################")
    print("Hey you gotta do this task right now !!!\n")
    print(tname[0])
    print("\n########################################\n")
    print(f"Task ends at {endtime[0]}\n")
    print("\nGood Luck")
    
def feedback():
    taskid =[]
    try:
        taskid.append(int(sys.argv[2]))
    except IndexError:
        print("Error : no taskid provided")
    
    cursor.execute('SELECT tname from tasks where taskid = ?',(taskid[0],))
    tname = cursor.fetchall()[0]
    print("########################################")
    print(f"\nTask {tname[0]} is over !!!\n")
    print("\n########################################\n")
    while (1) :
        print("Did you end up finishing it in time or did you get distracted ?")
        print("1 - Did it :)")
        print("0 - Couldn't do it")
        compstatus = int(input("Enter choice : "))
        if compstatus == 1 or compstatus == 0:
            cursor.execute('UPDATE tasks SET isSuccess = ? WHERE taskid = ?',(compstatus,sys.argv[2]))
        if compstatus == 1 :
            print("Great work!!")
            break
        elif compstatus == 0 :
            print("Good luck for the next one!!")
            break
        else :
            print("Please enter a valid value")
    subprocess.run(["schtasks","/delete","/tn","Focus"+str(taskid[0]),"/f"])

if int(sys.argv[1])==1:
    start()
elif int(sys.argv[1])==2:
    feedback()

conn.commit()
conn.close()

'''
Created on Dec 20, 2015

@author: Lebs
'''

import sqlite3, calcGPAByWeb, requests
from email.mime.text import MIMEText

courses = []

def notifyByMail(username, text):
    key = ''
    sandbox = ''
    recipient = username + '@edu.vamk.fi'

    request_url = 'https://api.mailgun.net/v2/' + sandbox +'/messages'
    request = requests.post(request_url, auth=('api', key), data={
        'from': 'im@likai.ren',
        'to': recipient,
        'subject': 'VAMK GPA CALCULATOR',
        'text': text
    })

def check(username, password, coursesHashOld):
    try:
        opener = calcGPAByWeb.login(username, password)
        coursesSource = calcGPAByWeb.getSource(opener, 'Suoritukset')
        courses = calcGPAByWeb.getCourses(coursesSource)
        coursesHashNew = calcGPAByWeb.getMd5(str(courses))
        if coursesHashOld == coursesHashNew:
            return 2    # no update
        else:
            update(username, password, coursesHashNew) # update
            return 1
    except Exception as e:
        return 0        # wrong password

def check2(username, password, coursesHash):    # check the password twice
    global courses, count
    code = check(username, password, coursesHash)
    if code == 0:   # wrong password, then try the second time
        count = count + 1
        if count == 2: # tried twice and failed, delete the user
            deleleUser(username)
            return 0
        else:
            print('wrong password 1')
            return check2(username, password, coursesHash)
    return code

def update(username, password, coursesHash): 
    with sqlite3.connect('/var/www/likai.ren/vamk-gpa/db/subscribedUsers.db.sqlite') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET courses_hash = ? WHERE username = ?', (coursesHash, username))
        conn.commit()
        notifyByMail(username, 'You have new course(s) grade updated. check here: https://likai.ren/vamk-gpa')


def deleleUser(username):
    with sqlite3.connect('/var/www/likai.ren/vamk-gpa/db/subscribedUsers.db.sqlite') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        conn.commit()
        notifyByMail(username, 'You have been deleted from the subscribed users beacause of the wrong password. subscribe again at https://likai.ren/vamk-gpa')

if __name__ == '__main__':
    with sqlite3.connect('/var/www/likai.ren/vamk-gpa/db/subscribedUsers.db.sqlite') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        data= cursor.fetchall()
        if len(data) == 0:
            print('no user!')
        else:
            for user in data:
                count = 0
                id, username, password, coursesHash = user
                print(username, end=" ")
                code = check2(username, password, coursesHash)
                if code == 1:
                    print('update')
                elif code == 2:
                    print('no update') 
                else:
                    print('wrong password 2')  
                    

        

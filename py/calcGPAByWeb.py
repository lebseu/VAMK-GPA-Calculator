#!/usr/bin/python3
'''
Created on May 21, 2015

@author: Likai
'''
import re, urllib, http.cookiejar, sys, time, hashlib, sqlite3, checkUpdate

def login(stuID, password):
    loginCookie = http.cookiejar.LWPCookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(loginCookie))
    startUrl = 'https://secure.puv.fi/wille/elogon.asp'
    loginUrl = 'https://secure.puv.fi/wille/elogon.asp?dfUsername?dfPassword?dfUsernameHuoltaja'
    loginData = urllib.parse.urlencode({'dfUsernameHidden' : stuID , 'dfPasswordHidden' : password}).encode()
    leftFrameUrl = "https://secure.puv.fi/wille/emainval.asp"
    
    opener.open(startUrl)
    opener.open(loginUrl, loginData)
    opener.open(leftFrameUrl)
    
    return opener
    

def getSource(opener, choice):
    requestData = urllib.parse.urlencode({'rbRajaus' : 'rb' + choice , 'dfOpjakso' : '' , 'dfArviointipvm' : ''}).encode()
    requestUrl = 'https://secure.puv.fi/wille/eWilleNetLink.asp?Link=https://secure.puv.fi/willenet/Hops' + choice + '.aspx&Hyv=1&Opjakso=&ArvPvm='
    return opener.open(requestUrl, requestData).read().decode('utf-8')

def getCourses(source):
    courses = re.findall(r'a>(.*?)<.*?>(\d+,\d+) [CO].*?>(.)<', source)
    return courses
   
def getReportHtml(courses):
    reportHtml = ''
    gpa = 0
    creditsDict = {'n': 0, 'm': 0, 's': 0} # credits
    gradesList = [0, 0, 0, 0, 0, 0, 0, 0] # counts

    alt = 0         #css
    if courses != []:
        reportHtml += '<div id="gpa" class="block"><h2>GPA (projects excluded)</h2><div id="gpaValue"></div></div>'
        reportHtml += '<div id="courses" class="block"><h2>Completions <i class="fa fa-table fa" onclick="$(\'#coursesTable\').tableExport({type:\'excel\',escape:\'false\', tableName:\'transcript_vamk\'});"></i></h2><div id="coursesBlock"><table id="coursesTable" class="tablesorter"><thead><tr><th class="tableHeader">Course</th><th class="tableHeader">Credit</th><th class="tableHeader">Grade</th></tr></thead><tbody>'
        for course in courses:
            alt += 1
            name = course[0]
            credit = eval(course[1].replace(',', '.'))
            grade = course[2]
            if alt%2 == 1:
                reportHtml += '<tr><td>' + name + '</td><td>' + str(credit) + '</td><td>' + grade + '</td></tr>'
            else:
                reportHtml += '<tr class="alt"><td>' + name + '</td><td>' + str(credit) + '</td><td>' + grade + '</td></tr>'
            if grade == 'M':
                gradesList[6] += 1
                creditsDict['m'] += credit
            elif grade == 'S':
                gradesList[7] += 1
                creditsDict['s'] += credit
            elif eval(grade) == 0:
                gradesList[0] += 1
            else:
                gpa += credit * eval(grade)
                creditsDict['n'] += credit
                gradesList[eval(grade)] += 1
        gpa /= creditsDict['n']
        totalCourses = sum(gradesList)
        reportHtml += '</tbody></table></div></div>'
        reportHtml += '<div id="getGpa" style="display: none;">{:4.3f}</div>'.format(gpa)
        reportHtml += '<div id="summary" class="block"><h2>Summary</h2>'
        reportHtml += '<div id="summaryBlock"><ul><li> T credits: {:5}</li>'.format(creditsDict['n'] + creditsDict['m'] + creditsDict['s'])
        reportHtml += '<li> N credits:{:5}</li>'.format(creditsDict['n'])
        reportHtml += '<li> M credits:     {:5}</li>'.format(creditsDict['m'])
        reportHtml += '<li> S credits:     {:5}</li>'.format(creditsDict['s'])
        reportHtml += '<li> Grades distribution:<br><ul>'
        for i in range(6):
            reportHtml +='<li>Grade {}: {:4} ({:6.2%})</li>'.format(i, gradesList[i], gradesList[i] / totalCourses)
        reportHtml += '<li>Grade {}: {:4} ({:6.2%})</li>'.format('M', gradesList[6], gradesList[6] / totalCourses)
        reportHtml += '<li>Grade {}: {:4} ({:6.2%})</li></ul></li></ul></div></div>'.format('S', gradesList[7], gradesList[7] / totalCourses)
        reportHtml += '<div id="notice" class="block"><h2>Notice</h2>'
        reportHtml += '<div id="noticeBlock">5 = Excellent, '
        reportHtml += '4 = Good, '
        reportHtml += '3 = Good, '
        reportHtml += '2 = Satisfactory, '
        reportHtml += '1 = Satisfactory, '
        reportHtml += '0 = Fail, '
        reportHtml += 'T = Total, '
        reportHtml += 'N = Normal, '
        reportHtml += 'S = Pass, '
        reportHtml += 'M = Credit Transfer</div></div>'
    else:
        reportHtml += '<div class="block"><ul><li>No course!</li></ul><br></div>'

    return reportHtml

def getMd5(text):
    return hashlib.md5(text.encode()).hexdigest()

def addSubscribedUser(username, password, courses):
    courses_hash = getMd5(str(courses))
    with sqlite3.connect('/var/www/likai.ren/vamk-gpa/db/subscribedUsers.db.sqlite') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        data= cursor.fetchall()
        if len(data) == 0:
            cursor.execute('INSERT INTO users (username, password, courses_hash) VALUES (?, ?, ?)', (username, password, courses_hash))
            conn.commit()
            checkUpdate.notifyByMail(username, 'Subscribed successfully!')
        else:
            cursor.execute('UPDATE users SET password = ?, courses_hash = ? WHERE username = ?', (password, courses_hash, username))
            conn.commit()
            checkUpdate.notifyByMail(username, 'Password was updated successfully!')

if __name__ == '__main__':
    try:

        stuID = sys.argv[1].lower()
        password = sys.argv[2]

        isSubscribed = sys.argv[3]
        if stuID == '' or password == '':
            raise Exception
        opener = login(stuID, password)
#        projectsSource = getSource(opener, 'Projektit')
#        courses += getCourses(projectsSource)
        coursesSource = getSource(opener, 'Suoritukset')
        courses = getCourses(coursesSource)
        reportHtml = getReportHtml(courses)
        with open('/var/www/likai.ren/vamk-gpa/log/log.txt', 'a+') as f:
            f.write(time.strftime("%c") + ', ' + stuID + '\n')
        print(reportHtml)

        # for subscribed users only
        if isSubscribed == '1':
            addSubscribedUser(stuID, password, courses);





    except Exception as e:
        #print('<div class="block"><ul><li>Error! Wrong student ID or password.<br></div></li></ul>')
        print('<div class="block"><ul><li>' + str(e) + '<br></div></li></ul>')
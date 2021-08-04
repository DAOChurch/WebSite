from flask import Flask
from flask import request
import sqlite3
import smtplib
import random,hashlib
from email.mime.text import MIMEText
from email.utils import formataddr
app = Flask(__name__)

email_account = 'service@dao.church'
email_pass = 'oreHvR3wRcbkWnBs'
sender = email_account

salt = ''.join(random.sample(['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k','j','i','h','g','f','e','d','c','b','a','@','1','#','*'], 8))

@app.route('/api/f',methods=['POST'])
def hello_world():
    smtp_obj = smtplib.SMTP_SSL('smtp.exmail.qq.com',465)
    smtp_obj.login(email_account,email_pass)  
    con = sqlite3.connect('email.db') 
    cur = con.cursor()
    mail = request.get_json()['email']
    SELECT_DATA = {'mail':mail.upper()}
    cur.execute('SELECT * FROM EMAIL WHERE MAIL=:mail',SELECT_DATA)
    if(len(cur.fetchall())!=0):
        return "EMAIL ACTIVE"
    e_mail = mail.split('@')
    e_mail = e_mail[0] + '@' + salt + e_mail[1]
    e_mail = e_mail.encode('utf-8')
    address = 'http://www.dao.church/api/verify/'+mail+'?verifyCode='+hashlib.sha256(e_mail).hexdigest()[8:24]
    message = MIMEText(f'''<div><a href={address}>Click to verify</a></div>''',"html","utf-8")
    message['From'] = formataddr(['DAOChurch Team',sender])
    message['To'] = formataddr(['Dear comrade',mail])
    message['Subject'] = "This is a confirmatory mail for your email address."
    try:
        smtp_obj.sendmail(sender,[mail],message.as_string())
        cur.close()
        con.close()
        smtp_obj.quit()
    except Exception as e:
        print(e)
        return 'error'
    return 'success'

@app.route('/api/verify/<mail>')
def do_something(mail):
    try:
        code = request.args.get('verifyCode','')
    except KeyError:
        return "URL Error,Please Don't Change The Verify URL"
    e_mail = mail.split('@')
    e_mail = e_mail[0] + '@' + salt + e_mail[1]
    e_mail = e_mail.encode('utf-8')
    res = hashlib.sha256(e_mail).hexdigest()[8:24]
    if(res!=code):
        return "Verify Error.Your mail is error"
    INSERT_DATA = {'mail':mail.upper()}
    try:
        con = sqlite3.connect('email.db') 
        cur = con.cursor()
        cur.execute('INSERT INTO EMAIL VALUES (:mail)',INSERT_DATA)
        con.commit()
        cur.close()
        con.close()
    except Exception as e:
        return 'Database Error'
    return 'Verify Successfully!'
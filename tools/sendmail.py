import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def SendMail(user,password,receive,filepath):
    # 发送邮箱服务器
    smtpserver = "smtp.163.com"
    # 发送邮件主题和内容
    subject = "From GitHub Actions"
    content = "<html><h1 style='color:red'>Micropython For Esp32C3 Firmware</h1></html>"
    #附件
    send_file = open(filepath, "rb").read()
    att = MIMEText(send_file, "base64", 'utf-8')
    att['Content-Type'] = 'application/octet-stream'
    att['Content-Disposition'] = 'attachment;filename="{}"'.format(filepath.split('/')[-1])

    msgRoot = MIMEMultipart()
    msgRoot.attach(MIMEText(content, 'html', 'utf-8'))
    msgRoot['Subject'] = subject
    msgRoot['From'] = user
    msgRoot['To'] = receive
    msgRoot.attach(att)

    # SSL协议端口号要使用465
    smtp = smtplib.SMTP_SSL(smtpserver, 465)

    # HELO向服务器标志用户身份
    smtp.helo(smtpserver)

    # 服务器返回结果确认
    smtp.ehlo(smtpserver)

    # 登录邮箱服务器用户名密码
    smtp.login(user, password)

    print("Send email start...")
    smtp.sendmail(sender, receive, msgRoot.as_string())
    smtp.quit()
    print("email send end!")


# 发送邮箱用户名密码
#user = os.environ.get('MAILUSER')
#password = os.environ.get('MAILPWD')

# 发送和接收邮箱
sender = user
receive = user
filepath=r"ports/esp32/build-GENERIC_C3/firmware.bin"

SendMail(user,password,receive,filepath)

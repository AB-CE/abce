import smtplib


def email(msg):
    fromaddr = 'davoudtaghawinejad@gmail.com'
    toaddrs = 'davoudtaghawinejad@gmail.com'
    username = 'davoudtaghawinejad'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, 'ghuaqmiwyxruvzio')
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()


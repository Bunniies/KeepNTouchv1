import os 

class Config(object):
    SECRET_KEY = 'cXjCnwAeojwfoEehwgfdrwefsADnrnsEmls'
    SQLALCHEMY_DATABASE_URI='sqlite:///website.db'
    UPLOADED_PHOTOS_DEST = os.getcwd()+"/static"
    MAIL_SERVER='smtp.mail.com'
    MAIL_PORT=587
    MAIL_TLS=True
    MAIL_USERNAME='keepntouch@engineer.com'
    MAIL_PASSWORD='keepntouch'

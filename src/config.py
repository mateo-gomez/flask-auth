class Config:
    SECRET_KEY = 'jLal_gs?$#H+*!234'


class DevelopmentConfig(Config):
    DEBUG=True
    MONGO_URI = 'mongodb://localhost:27017/flask_login'

config = {
    'development': DevelopmentConfig
}
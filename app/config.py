import configparser

config = configparser.ConfigParser()
config.read("app/config.ini")

DB_USER = config["DATABASE"]["DB_USER"]
DB_PASSWORD = config["DATABASE"]["DB_PASSWORD"]
DB_HOST = config["DATABASE"]["DB_HOST"]
DB_NAME = config["DATABASE"]["DB_NAME"]

SECRET_KEY = config['JWT']['SECRET_KEY']
ALGO = config['JWT']['ALGO']

REDIS_HOST = config["REDIS"]["REDIS_HOST"]
REDIS_PORT = int(config["REDIS"]["REDIS_PORT"]) 
REDIS_DB = int(config["REDIS"]["REDIS_DB"])

AZURE_DEPLOYMENT = config["AZURE"]["AZURE_DEPLOYMENT"]
API_VERSION = config["AZURE"]["API_VERSION"]
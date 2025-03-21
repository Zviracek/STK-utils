import configparser as config
def readConfig():
    conf = config.ConfigParser()
    conf.read('Config.ini')
    return conf
# workspace
WORKSPACE_NAME = "example"

# mongo params for production env
MONGO_PARAMS = {
    'host': 'localhost',
    'port': 27017,
    'username': 'admin',
    'password': '654321'
}

# mongo params for testing env
MONGO_PARAMS_DEBUG = {
    'host': 'localhost',
    'port': 27017,
    'username': 'admin',
    'password': '654321'
}

# db to store data crawled
MONGO_CRAWLER_DB = 'crawler'

# db to store statistic info
MONGO_STATISTIC_DB = 'crawler_statistic'

# choose fields in statistic info, [] refers to 'ALL'
MONGO_STATISTIC_FIELDS = []

# dir to store files
ATTACH_FILE_PATH = '/data/crawlers/'

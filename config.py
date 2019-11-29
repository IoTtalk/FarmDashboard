DEBUG = False

FLASK_SECRET_KEY = 'FDSDFGHksoyHisHtheHauthorHFDSWERE' # use random string, for example, "FDSDFGHksoyHisHtheHauthorHFDSWERE" 

# DB_CONFIG = '<database>[+<orm_lib>]://[<user>[:<password>]]<host>[:<port>]/[db_name][?charset=utf8]'
# ex: DB_CONFIG = 'mysql+pymysql://user:pass@localhost:3306/db_name?charset=utf8'
# ex: DB_CONFIG = 'sqlite+pysqlite:///db.sqlite3'
DB_CONFIG = ''
DB_POOL_RECYCLE = 600
DB_POOL_SIZE = 20
QUERY_LIMIT = 100
REQUEST_TIMEOUT = 10

CSM_HOST = '8.8.8.8'  # IoTtalk server's 'IP' or 'DomainName' only, for example, '8.8.8.8' or 'google.com', please do not attach the prefix 'http://' or 'https://'.

demo_token = { #The data format is '<Field Name>':'<token>', examples are shown as follows.
    'FieldName1':'65761609-0f1e-4b72-adcf-1ed092454d53',
    'FieldName2':'68842ce7-7892-48d8-9519-b97bf49fa9bd',
}

demo_field = 'should be disablded.'
from os import environ

# Test Environment
IS_TEST = environ.get('IS_TEST', False)

# Database Credentials
MYSQL_ROOT_PASSWORD = environ.get('MYSQL_ROOT_PASSWORD')
MYSQL_DATABASE = environ.get('MYSQL_DATABASE')
MYSQL_USER = environ.get('MYSQL_USER')
MYSQL_PASSWORD = environ.get('MYSQL_PASSWORD')
MYSQL_HOST = environ.get('MYSQL_HOST', 'mariadb')
if MYSQL_PASSWORD: 
    DATABASE_URL = f'mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}'  # noqa: E501
else:
    DATABASE_URL = f'mysql://{MYSQL_USER}@{MYSQL_HOST}/{MYSQL_DATABASE}'

CONTINGENCIA = environ.get('CONTINGENCIA', 'False').lower() == 'true'

# Ministerio de Hacienda DTE Credentials
AUTH_URL = environ.get('AUTH_URL')
NIT = environ.get('NIT')
NRC = environ.get('NRC')
AUTH_PASSWORD = environ.get('AUTH_PASSWORD')

if not CONTINGENCIA:
    RECEPTION_URL = environ.get('RECEPTION_URL')
else:
    RECEPTION_URL = environ.get('RECEPTION_URL_CONTINGENCIA')

CONSULTAS_URL = environ.get('CONSULTAS_URL')
CONTINGENCIA_URL = environ.get('CONTINGENCIA_URL')
ANULACION_URL = environ.get('ANULACION_URL')

# SVFE Signature config
SIGNATURE_URL = environ.get('SIGNATURE_URL')
SIGNATURE_PASSWORD = environ.get('SIGNATURE_PASSWORD')

# PDF Generation config
GENERATOR_URL = environ.get('GENERATOR_URL')

# Hacienda's environment
HACIENDA_ENV = environ.get('HACIENDA_ENV', '00')


#SMTP Credentials
SMTP_HOST = environ.get('SMTP_HOST')
SMTP_PORT = environ.get('SMTP_PORT')
SMTP_USER = environ.get('SMTP_USER')
SMTP_PASSWORD = environ.get('SMTP_PASSWORD')
DEFAULT_RECEIVER = environ.get('DEFAULT_RECEIVER')
DISABLE_EMAIL = environ.get('DISABLE_EMAIL', 'False').lower() == 'true'

DBF = environ.get('ARCHIVO_DBF', "C:\\DBF\\DTE.DBF")
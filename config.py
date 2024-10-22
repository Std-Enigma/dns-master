import os

from appdirs import user_data_dir

APP_NAME = "dns-master"

# Common paths
HOME_DIRECTORY = os.path.expanduser("~")
USER_DATA_DIRECTORY = user_data_dir(APP_NAME)
DATABASE_NAME = "dns_configs.db"
DATABASE_PATH = os.path.join(USER_DATA_DIRECTORY, DATABASE_NAME)

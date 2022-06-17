# YOU CAN DELETE IF YOU ARE NOT FORKING/DEV THIS PROJECT
from dotenv import load_dotenv
import os
load_dotenv()

# baidu
APP_ID = '' #你的appid
SECRET_KEY = '' #你的密钥
# youdao
APP_KEY = '' # 应用ID
APP_SECRET = '' # 应用秘钥
# deepl
DEEPL_AUTH_KEY = os.getenv("DEEPLKEY") # CHANGE BY 'YOURKEY' IF YOU ARE NOT FORKING/DEV THIS PROJECT

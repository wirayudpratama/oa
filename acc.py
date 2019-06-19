import os
import pyrebase
from linebot import (LineBotApi, WebhookHandler)

namaBot = "yudha"
line_bot_api = LineBotApi(os.environ.get('BK50nyBRSOcibwYdcx4jXEM3y7ooxJ1+F0tHy86CY8IeJcn00PzfNSi1eaM5PD32fVzWWwitfz9gw/05MMUoAz5anLzleoZU1/MF5zU7ZTApopWtICcRjUuj1E0Z8Rhk+zI90vHspM0AkCuEH0ga5gdB04t89/1O/w1cDnyilFU='))
handler = WebhookHandler(os.environ.get('6aac06ec8ec6cbcf95973a62368d08d8'))
google_key = os.environ.get('GOOGLE_API_KEY')
owner = 'u81a15ce8e621e30cb0f627aafc4e8b57'

config = {
    "apiKey": os.environ.get('FIREBASE_API_KEY'),
    "authDomain": os.environ.get('FIREBASE_AUTH_DOMAIN'),
    "databaseURL": os.environ.get('FIREBASE_LINK_DATABASE'),
    "storageBucket": os.environ.get('FIREBASE_STORAGE_BUCKET')
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

quiz_db = {
	"apiKey": os.environ.get('QUIZ_API_KEY'),
    "authDomain": os.environ.get('QUIZ_AUTH_DOMAIN'),
    "databaseURL": os.environ.get('QUIZ_LINK_DATABASE'),
    "storageBucket": os.environ.get('QUIZ_STORAGE_BUCKET')
}

quiz = pyrebase.initialize_app(quiz_db)
qz = quiz.database()

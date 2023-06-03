import pyrebase
from getpass import getpass


firebaseConfig = {
  "apiKey": "AIzaSyAYkWpFXiGKcoTfdrQPULd1Gvsr2pMXstM",
  "authDomain": "ckure-db.firebaseapp.com",
  "databaseURL": "https://ckure-db-default-rtdb.firebaseio.com",
  "projectId": "ckure-db",
  "storageBucket": "ckure-db.appspot.com",
  "messagingSenderId": "379512987829",
  "appId": "1:379512987829:web:02d01cfa08a1186bea5efc",
  "measurementId": "G-M4RNLKWGW7",
  "serviceAccount": "serviceAccountKey.json"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# RECORD ID AND NAME
userID = ''
userName=''
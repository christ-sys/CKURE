from os import path
from pyexpat import model
import firebase_admin
from firebase_admin import credentials, firestore, auth




cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

reportTime=''

#FETCHING DATA 
def get_company():
    company=[]
    company_ref = db.collection('cars').get()
    for compA in company_ref:
        company.append(compA.id)
    return company

def get_model(compny):
    models=[]
    model_ref = db.collection('cars').document(compny).collection('data').get()
    for model in model_ref:
        modeldocu = model.to_dict()
        models.append(modeldocu['Model'])
    return models

def get_history(userID):
    data=[]
    # reports = db.collection('reports').get()
    reports = db.collection('reports').where('report_sender', '==', userID).get()

    for e in reports:
            data.append([e.get('Date'),e.get('Location')])
    
    return data



# STORING DATA
def store_userCar(ref,data):
    userCarRef = db.collection(ref).document('CarInfo').set(data)
        
def store_userData(ref,data):
    userCarRef = db.collection(ref).document('UserInfo').set(data)







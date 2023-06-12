import firebase_admin
from google.cloud import firestore
from firebase_admin import credentials, firestore, auth
from datetime import datetime
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
email="ckure.org@mail.com"
import csv
def get_user_data(email):
    user = auth.get_user_by_email(email)
    user_id = user.uid
    db = firestore.client()
    doc_ref = db.collection(u'users').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict(),user_id
    else:
        return None
# print(get_user_data(email))
def get_all_users():
    users = []
    docs = db.collection('users').get()
    for doc in docs:
        user_data = doc.to_dict()
        user_data['id'] = doc.id
        users.append(user_data)
    return users
def insurance_all_users():
    users = []
    docs = db.collection('users').get()
    for doc in docs:
        user_data = doc.to_dict()
        user_data['id'] = doc.id
        users.append(user_data)
    insured_users = [user for user in users if user.get('insured') == True] # Filter users where insured == true
    return insured_users
def get_user_details(userid):
    doc_ref = db.collection('users').document(userid)
    doc_snapshot = doc_ref.get()
    if doc_snapshot.exists:
        user_details = doc_snapshot.to_dict()
        return user_details
def update_user_details(user_id, user_data):
    user_ref = db.collection("users").document(user_id)
    user_ref.set(user_data)  # Update the car data in Firestore
    return user_data
# print(get_user_details("59oe6qF2LoRFtgPqQhEejzJtKeP2"))
def export_users_to_csv(users, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=users[0].keys())
        writer.writeheader()
        for user in users:
            writer.writerow(user)
# users = get_all_users()
# export_users_to_csv(users, 'users.csv')

def get_all_reports():
    reports = []
    docs = db.collection('reports').get()
    for doc in docs:
        report_data = doc.to_dict()
        report_data['id'] = doc.id
        reports.append(report_data)
    return reports
def get_claim_details(claimid):
    doc_ref = db.collection('claims').document(claimid)
    doc_snapshot = doc_ref.get()
    if doc_snapshot.exists:
        claim_details = doc_snapshot.to_dict()
        return claim_details
def get_all_claims():
    claims = []
    docs = db.collection('claims').get()
    for doc in docs:
        claim_data = doc.to_dict()
        claim_data['id'] = doc.id
        claims.append(claim_data)
    return claims
def get_all_reports():
    reports = []
    docs = db.collection('reports').get()
    for doc in docs:
        report_data = doc.to_dict()
        report_data['id'] = doc.id
        reports.append(report_data)
    return reports
def export_reports_to_csv(reports, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=reports[0].keys())
        writer.writeheader()
        for report in reports:
            writer.writerow(report)
def get_claims():
    claims_ref = db.collection('claims')
    query = claims_ref.where('approved', '==', False)
    claims_docs = query.stream()
    claim_pending = [claim.id for claim in claims_docs]
    return claim_pending
def get_approved_claims():
    claims_ref = db.collection('claims')
    query = claims_ref.where('approved', '==', True)
    claims_docs = query.stream()
    claim_approved = [claim.id for claim in claims_docs]
    return claim_approved
def get_reports():
    claims_ref = db.collection('reports')
    query = claims_ref.where('status', '==', "Pending")
    claims_docs = query.stream()
    claim_pending = [claim.id for claim in claims_docs]
    return claim_pending
def get_approved_reports_pnp():
    reports_ref = db.collection('reports')
    query = reports_ref.where('status', '==', "PNP_Approved")
    reports_docs = query.stream()
    report_approved = [report.id for report in reports_docs]
    return report_approved
def get_report_details(report_id):
    doc_ref = db.collection('reports').document(report_id)
    doc_snapshot = doc_ref.get()
    if doc_snapshot.exists:
        report_details = doc_snapshot.to_dict()
        return report_details
# reports = get_all_reports()
# export_reports_to_csv(reports, 'reports.csv')
def get_vehicle():
    veh_ref = db.collection('cost_estimation')
    veh = veh_ref.stream()
    veh_types = [veh_type.id for veh_type in veh] 
    return veh_types
def get_brand():
    cars_ref = db.collection('cars')
    cars_docs = cars_ref.stream()
    car_brand = [car.id for car in cars_docs]
    return car_brand
def get_model(brand_id):
    models_ref = db.collection("cars").document(brand_id).collection("data")
    model_counts = {}
    
    for doc in models_ref.stream():
        model_data = doc.to_dict()
        model = model_data.get("Model")
        if model:
            model_counts[model] = model_counts.get(model, 0) + 1
    
    return model_counts
def get_cars(brand_id,model):
    cars_ref = db.collection("cars").document(brand_id).collection("data")
    cars = []
    query = cars_ref.where("Model", "==", model)
    for doc in query.stream():
        car_data = doc.to_dict()
        cars.append(car_data)
    return cars
def get_car_by_id(brand_id,object_id):
    car_ref = db.collection("cars").document(brand_id).collection("data").document(object_id)
    car_data = car_ref.get().to_dict()
    return car_data
# print(get_car_by_id("Kia", "57u2DoGmCW"))
def update_car(brand_id, object_id, car_data):
    car_ref = db.collection("cars").document(brand_id).collection("data").document(object_id)
    car_ref.set(car_data)  # Update the car data in Firestore
    return car_data

def delete_car(brand_id, object_id):
    car_ref = db.collection("cars").document(brand_id).collection("data").document(object_id)
    car_ref.delete()  # Delete the car document from Firestore

###############################################
def get_severity(brand, model, part):
    severity_ref = db.collection('cost_estimation').document('Car').collection(brand).document(model).collection(part)
    severity = severity_ref.stream()
    severity_level = [level.id for level in severity]
    return severity_level

def get_damage(brand, model, part, severity):
    cost_ref = db.collection('cost_estimation').document('Car').collection(brand).document(model).collection(part)
    docs = cost_ref.list_documents()
    estimated_cost = []
    for doc in docs:
        if doc.id != severity:
            continue
        cost_doc = doc.get().to_dict()
        estimated_cost.append(cost_doc)
    return estimated_cost


###CASA####
def getReport_CASA():
    report_ref = db.collection('reports')
    query = report_ref.where('Status', '==', "Pending")
    report_docs = query.stream()
    report_pending = [report.id for report in report_docs]
    return report_pending

def updateItemCost(costArray,id):
    report_ref = db.collection('reports').document(id)
    report_ref.update({'Costs': costArray})
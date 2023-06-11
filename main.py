# LIBRARY AND MODULE IMPORTS
import hashlib
import random
import string
import time
from datetime import datetime

import numpy as np
from keras.models import load_model
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image as rawImage
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.icon_definitions import md_icons
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import (MDFlatButton, MDRectangleFlatButton,
                               MDRectangleFlatIconButton)
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list.list import *
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.recycleview import RecycleView
from kivymd.uix.sliverappbar import *
from kivymd.uix.snackbar import Snackbar
from PIL import Image
from PIL import Image as pilImage
from PIL import ImageOps
from pytz import timezone
from roboflow import Roboflow
import pytz
import os
import firebaseauth
import firestoredb

Window.size = (350, 630)
Builder.load_file("login.kv")
Builder.load_file("signup.kv")
Builder.load_file("carDetails.kv")
Builder.load_file("insuranceDetails.kv")
Builder.load_file("home.kv")
Builder.load_file("myCar.kv")
Builder.load_file("myInsurance.kv")
Builder.load_file("blotter.kv")
Builder.load_file("result.kv")
Builder.load_file("myReports.kv")
Builder.load_file("submitted.kv")

class Submitted(Screen):
    pass
class CustomRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
class CustomCard(BoxLayout):
    image_source = StringProperty()
    category = StringProperty()
    part = StringProperty()
    severity = StringProperty()
    cost=StringProperty()
    damage = StringProperty()
    confidence = StringProperty()
class Result(Screen):
    def back(self, button):
        screen_manager.transition.direction='right'
        screen_manager.current = "home"
class someCard(MDCard):
    text=StringProperty()
class SignUp(Screen):
    def __init__(self, **kw):
        super(SignUp, self).__init__(**kw)
        self.app_bar = MDSliverAppbarHeader(
            MDRectangleFlatIconButton(
                text="Back to login",
                text_color= "white",
                font_size = "20dp",
                icon="arrow-left",
                line_color= [0, 0, 0, 0],
                theme_icon_color= "Custom",
                icon_color="white",
                on_release=lambda x: self.back(),
                pos_hint= {"center_x": .03, "center_y": .95}
            )
        )
        self.add_widget(self.app_bar)


        genderLst = ['Male', 'Female']
        gender= [
             {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.genderCallback(x),
            } for i in genderLst
        ]

        self.GenderMenu = MDDropdownMenu(
            caller=self.ids.gender,
            items=gender,
            width_mult=4,
            elevation=0,
            position="center"
        )
    def validate_password(self):
        password = self.ids.password.text
        # Minimum length check
        if len(password) < 8:
            self.ids.password.error = True
            return
        # Special character check
        if not any(char.isalnum() for char in password):
            self.ids.password.error = True
            return
        # Uppercase letter check
        if not any(char.isupper() for char in password):
            self.ids.password.error = True
            return
        # Number check
        if not any(char.isdigit() for char in password):
            self.ids.password.error = True
            return
        # All checks passed
        self.ids.password.error = False

    def genderCallback(self,text_item):
        self.ids.gender.text=text_item

    def calculateAge(self,dob):
        currDate = datetime.now(timezone('Asia/Manila'))
        age = currDate.year-dob.year-((currDate.month, currDate.day) < (dob.month, dob.day))
        return age
    
    def dateSelect_ok(self,instance,value,date_range):
        mydate = value.strftime("%B %d, %Y")
        self.ids.dob.text = str(mydate)
        myage = self.calculateAge(value)
        self.ids.age.text= str(myage)
    
    def dateSelect_cancel(self,instance,value):
        self.ids.dob.text = ''
        self.ids.age.text =''

    def showCalendar(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.dateSelect_ok, on_cancel=self.dateSelect_cancel)
        date_dialog.open()
    
    def reg_user(self):
        email = self.ids.email.text
        password = self.ids.password.text
        pass_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        name = self.ids.name.text
        contact = self.ids.contact.text
        address = self.ids.address.text
        dob = self.ids.dob.text
        age = self.ids.age.text
        gender = self.ids.gender.text
        license_id = self.ids.license.text
        profession = self.ids.business.text
        try:
            user = firebaseauth.auth.create_user_with_email_and_password(email, password)
            user_uid = user['localId']
            data={
                "email": email,
                "name": name,
                "phone": contact,
                "address": address,
                "dob": dob,
                "age": age,
                "gender": gender,
                "password": pass_hash,
                "license_id": license_id,
                "profession": profession
            }   
            user_ref = firestoredb.db.collection('users').document(user_uid)
            user_ref.set({})
            user_doc = firestoredb.db.collection('users').document(user_uid).collection('Account').document('UserInfo').set(data)
            # Pass the user ID to the CarDetails screen
            car_details_screen = self.manager.get_screen('car_details')
            car_details_screen.user_id = user_uid
            insurance_details_screen = self.manager.get_screen('insurance_details')
            insurance_details_screen.user_id = user_uid

            self.manager.current = 'car_details'
            print(user_uid) 
        except Exception as e:
            Snackbar(
                text="Registration Failed",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(Window.width - (10 * 2)) / Window.width
            ).open()
        
    def back(self):
        self.manager.current = "login"
class Login(Screen):
    def myCredentials(self,user_id):
        if user_id:
            myScr = screen_manager.get_screen("home")
            myCar = screen_manager.get_screen("myCar")
            myInsurance = screen_manager.get_screen("myInsurance")
            myReport = screen_manager.get_screen("createReport")
            
            current_cred = firestoredb.db.collection('users').document(user_id).collection('Account').document('UserInfo').get()
            myCurrCred = current_cred.to_dict()
            
            myCar_cred = firestoredb.db.collection('users').document(user_id).collection('Account').document('CarInfo').get()
            myCarInfo = myCar_cred.to_dict()
            
            myInsurance_cred = firestoredb.db.collection('users').document(user_id).collection('Account').document('InsuranceInfo').get()
            myInsuranceInfo = myInsurance_cred.to_dict()
                        
            #STORE USERNAME
            firebaseauth.userName = myCurrCred.get('name')
            myScr.ids.name.text = myCurrCred.get('name')
            myScr.ids.email.text = myCurrCred.get('email')
            myScr.ids.address.text = myCurrCred.get('address')
            myScr.ids.contact.text = myCurrCred.get('phone')
            myScr.ids.age.text = myCurrCred.get('age')
            myScr.ids.dob.text = myCurrCred.get('dob')
            myScr.ids.gender.text = myCurrCred.get('gender')
            # MY CAR INFO
            myCar.ids.vehicle_type.text = myCarInfo.get('vehicle_type')
            myCar.ids.file_no.text = myCarInfo.get('file_no')
            myCar.ids.plate_no.text = myCarInfo.get('plate_no')
            myCar.ids.engine.text = myCarInfo.get('engine_no')
            myCar.ids.chassis.text = myCarInfo.get('chassis_no')
            myCar.ids.denomination.text = myCarInfo.get('denomination')
            myCar.ids.piston.text = myCarInfo.get('piston')
            myCar.ids.cylinders.text = myCarInfo.get('cylinders')
            myCar.ids.fuel.text = myCarInfo.get('fuel')
            myCar.ids.model.text = myCarInfo.get('model')
            myCar.ids.year.text = myCarInfo.get('year')
            myCar.ids.body_type.text = myCarInfo.get('body_type')
            myCar.ids.color.text = myCarInfo.get('color')
            myCar.ids.grosswt.text = myCarInfo.get('grosswt')
            myCar.ids.netwt.text = myCarInfo.get('netwt')
            myCar.ids.shppngwt.text = myCarInfo.get('shppngwt')
            myCar.ids.netcap.text = myCarInfo.get('netcap')
            # MY CAR INSURANCE
            myInsurance.ids.insured_type.text = myInsuranceInfo.get('insured_type')
            myInsurance.ids.agent.text = myInsuranceInfo.get('agent')
            myInsurance.ids.policy_no.text = myInsuranceInfo.get('policy_no')
            myInsurance.ids.date.text = myInsuranceInfo.get('date')
            myInsurance.ids.start.text = myInsuranceInfo.get('start')
            myInsurance.ids.end.text = myInsuranceInfo.get('end')


    def checkNewUser(self,user_id):
        VArec_ref ='users/'+user_id+'/Account'
        specifics_ref=firestoredb.db.collection(VArec_ref).document('CarInfo').get()
        indicator = specifics_ref.to_dict()
        if not indicator:
            return 'car_details'
        else:
            return 'home'

    def verify_user(self):
        email = self.ids.email.text
        password = self.ids.password.text
        try:
            user = firebaseauth.auth.sign_in_with_email_and_password(email, password)
            firebaseauth.userID = user['localId']
            
            #DETERMINE LANDING PAGE ON SIGN IN
            self.manager.current=self.checkNewUser(firebaseauth.userID) 

            #UPDATE USER PROFILE
            self.myCredentials(firebaseauth.userID)

        except Exception as e:
            print(str(e))
            Snackbar(
                text=str(e),
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(Window.width - (10 * 2)) / Window.width
            ).open()
class CarDetails(Screen):
    def __init__(self, **kw):
        super(CarDetails,self).__init__(**kw)
        vehicleType = ['PRIVATE', 'COMMERCIAL']
        vehicle= [
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.vehicleCallback(x),
            } for i in vehicleType
        ]

        self.VehicleMenu = MDDropdownMenu(
            caller=self.ids.vehicle_type,
            items=vehicle,
            width_mult=4,
            elevation=0,
            position="center"
        )
    def vehicleCallback(self,text_item):
        self.ids.vehicle_type.text=text_item
        
    current_date = time.strftime("%d-%m-%Y")
    current_time = time.strftime("%I:%M")
    def saveCarDetails(self):
        user_id = self.user_id
        if user_id:
            try:
                data = {
                    "vehicle_type": self.ids.vehicle_type.text,
                    "file_no": self.ids.file_no.text,
                    "plate_no": self.ids.plate_no.text,
                    "engine_no": self.ids.engine_no.text,
                    "chassis_no": self.ids.chassis_no.text,
                    "denomination": self.ids.denomination.text,
                    "piston": self.ids.piston.text,
                    "cylinders": self.ids.cylinders.text,
                    "fuel": self.ids.fuel.text,
                    "model": self.ids.model.text,
                    "year": self.ids.year.text,
                    "body_type": self.ids.body_type.text,
                    "color": self.ids.color.text,
                    "grosswt": self.ids.grosswt.text,
                    "netwt": self.ids.netwt.text,
                    "shppngwt": self.ids.shppngwt.text,
                    "netcap": self.ids.netcap.text,
                }
                user_ref = firestoredb.db.collection('users').document(user_id).collection('Account').document('CarInfo')
                user_ref.set(data)  # Save the car details for the user
                # insurance_details_screen = self.manager.get_screen('insurance_details')
                # insurance_details_screen.user_id = self.manager.get_screen('').user_uid
                self.manager.current = "insurance_details"
                Snackbar(
                    text="Car details saved",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=(Window.width - (10 * 2)) / Window.width
                ).open()
            except Exception as e:
                # handle the exception
                Snackbar(
                    text="Failed to save car details: " + str(e),
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=(Window.width - (10 * 2)) / Window.width
                ).open()
class InsuranceDetails(Screen):
    def __init__(self, **kw):
        super(InsuranceDetails,self).__init__(**kw)
        insuredType = ['IN-HOUSE', 'STERLING']
        insurance= [
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.insuranceCallback(x),
            } for i in insuredType
        ]

        self.InsuranceMenu = MDDropdownMenu(
            caller=self.ids.insured_type,
            items=insurance,
            width_mult=4,
            height=2,
            elevation=0,
            position="center"
        )
    def insuranceCallback(self,text_item):
        self.ids.insured_type.text=text_item
    current_date = time.strftime("%d-%m-%Y")
    current_time = time.strftime("%I:%M")
    def saveInsuranceDetails(self):
        user_id = self.user_id
        if user_id:
            try:
                data = {
                    "insured_type": self.ids.insured_type.text,
                    "agent": self.ids.agent.text,
                    "policy_no": self.ids.policy_no.text,
                    "date": self.ids.date.text,
                    "start": self.ids.start.text,
                    "end": self.ids.end.text,
                }
                user_ref = firestoredb.db.collection('users').document(user_id).collection('Account').document('InsuranceInfo')
                user_ref.set(data)  
                self.manager.current='login'

                Snackbar(
                    text="Registration Successful!",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=(Window.width - (10 * 2)) / Window.width
                ).open()
            except Exception as e:
                # handle the exception
                Snackbar(
                    text="Failed to save details: " + str(e),
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=(Window.width - (10 * 2)) / Window.width
                ).open()
class Home(Screen, MDBoxLayout):
    #PROFILE SCREEN
    def calculateAge(self,dob):
        currDate = datetime.now(timezone('Asia/Manila'))
        age = currDate.year-dob.year-((currDate.month, currDate.day) < (dob.month, dob.day))
        return age
    
    def dateSelect_ok(self,instance,value,date_range):
        mydate = value.strftime("%B %d, %Y")
        self.ids.dob.text = str(mydate)
        myage = self.calculateAge(value)
        self.ids.age.text= str(myage)


    def dateSelect_cancel(self,instance,value):
        self.ids.dob.text = ''
        self.ids.age.text =''

    def showCalendar(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.dateSelect_ok, on_cancel=self.dateSelect_cancel)
        date_dialog.open()

    def updateUserInfo(self):
        try:
            data={
                "name":self.ids.name.text,
                "email":self.ids.email.text,
                "address":self.ids.address.text,
                "phone":self.ids.contact.text,
                "dob": self.ids.dob.text,
                "age":self.ids.age.text,
                "gender":self.ids.gender.text,
            }

            user_uid = firebaseauth.userID
            # firestoredb.store_userData(ref,data)
            user_doc = firestoredb.db.collection('users').document(user_uid).collection('Account').document('UserInfo').set(data)
            Snackbar(
            text="Information Updated",
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=(Window.width - (10 * 2)) / Window.width
            ).open()
        
        except:
            Snackbar(
                text="Could not update information",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(Window.width - (10 * 2)) / Window.width
            ).open()
    #MAIN SCREEN
    def Update_DataSrc(self, imgsrc):
        #CREATE A DICTIONARY FOR THE IMAGE AND RESULT
        image_data = {
            'image_source':imgsrc,
            'cost':'0'
            }
        #UPDATE DICTIONARY
        image_data=Ckure.performDetections(image_data)
        #TO UPDATE IMAGE SOURCE
        rv = screen_manager.get_screen('result').ids.rv
        data = rv.data
        data.append(image_data)
        rv.refresh_from_data()
        Ckure.total_cost(data)
    def Camera(self):
        self.cam = self.ids['camera']
        myImg = rawImage()
        timeStr = time.strftime("%Y%m%d_%H%M%S")
        self.cam.export_to_png("assets/Ckure {}.png".format(timeStr))
        myImg.source = "assets/Ckure {}.png".format(timeStr)
        
        # TRIM IMAGE AND RELOAD IMAGE
        captured_image = pilImage.open(myImg.source) 
        crop_image = captured_image.crop(captured_image.getbbox())
        crop_image.save(myImg.source)
        myImg.reload()
        
        # self.Update_DataSrc(myImg.source)
        print('MyID: ' + firebaseauth.userID)
        
        # Perform predictions on the captured image
        rf = Roboflow(api_key="6riPgDH2G6Wn2Lqa4MTC")
        model = rf.workspace().project("ckure").version(4).model
        response = model.predict(myImg.source, confidence=40, overlap=30).json()

        if not response['predictions']:
            data_list = {
                'image_source': myImg.source,
                'damage': 'No predictions found!',
                'confidence': 'No predictions found!'
            }
            # Delete the image file
            if os.path.exists(data_list['image_source']):
                os.remove(data_list['image_source'])
            dialog = MDDialog(
                title="No Predictions Found",
                text="No damage predictions were found for the image.",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
        else:
            # Navigate to the results page
            self.manager.current = 'result'
            # Update the image source and perform detections
            self.Update_DataSrc(myImg.source)
class MyCar(Screen):
    def __init__(self, **kwargs):
        super(MyCar, self).__init__(**kwargs)
        self.app_bar = MDSliverAppbarHeader(
            MDRectangleFlatIconButton(
                text="My Car Details",
                text_color= "white",
                font_style="Body1",
                font_size = "20dp",
                icon="arrow-left",
                line_color= [0, 0, 0, 0],
                theme_icon_color= "Custom",
                icon_color="white",
                on_release=lambda x: self.back(),
                pos_hint= {"center_x": .03, "center_y": .95}
            )
        )
        self.add_widget(self.app_bar)
    def updateCarInfo(self):
        try:
            data = {
                "vehicle_type": self.ids.vehicle_type.text,
                "file_no": self.ids.file_no.text,
                "plate_no": self.ids.plate_no.text,
                "engine_no": self.ids.engine.text,
                "chassis_no": self.ids.chassis.text,
                "denomination": self.ids.denomination.text,
                "piston": self.ids.piston.text,
                "cylinders": self.ids.cylinders.text,
                "fuel": self.ids.fuel.text,
                "model": self.ids.model.text,
                "year": self.ids.year.text,
                "body_type": self.ids.body_type.text,
                "color": self.ids.color.text,
                "grosswt": self.ids.grosswt.text,
                "netwt": self.ids.netwt.text,
                "shppngwt": self.ids.shppngwt.text,
                "netcap": self.ids.netcap.text,
            }

            user_uid = firebaseauth.userID
            user_doc = firestoredb.db.collection('users').document(user_uid).collection('Account').document('CarInfo').set(data)

            Snackbar(
            text="Car Information Updated",
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=(Window.width - (10 * 2)) / Window.width
            ).open()
        
        except:
            Snackbar(
                text="Could not update information",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(Window.width - (10 * 2)) / Window.width
            ).open()
    def back(self):
        self.manager.transition.direction='right'
        self.manager.current = "home"
class MyInsurance(Screen):
    def __init__(self, **kwargs):
        super(MyInsurance, self).__init__(**kwargs)
        self.app_bar = MDSliverAppbarHeader(
            MDRectangleFlatIconButton(
                text="My Car Insurance",
                text_color= "white",
                font_style="Body1",
                font_size = "20dp",
                icon="arrow-left",
                line_color= [0, 0, 0, 0],
                theme_icon_color= "Custom",
                icon_color="white",
                on_release=lambda x: self.back(),
                pos_hint= {"center_x": .03, "center_y": .95}
            )
        )
        self.add_widget(self.app_bar)
        insuredType = ['IN-HOUSE', 'STERLING']
        insurance= [
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.insuranceCallback(x),
            } for i in insuredType
        ]

        self.InsuranceMenu = MDDropdownMenu(
            caller=self.ids.insured_type,
            items=insurance,
            width_mult=4,
            height=2,
            elevation=0,
            position="center"
        )
    def insuranceCallback(self,text_item):
        self.ids.insured_type.text=text_item
    def updateInsuranceInfo(self):
        try:
            data = {
                "insured_type": self.ids.insured_type.text,
                "agent": self.ids.agent.text,
                "policy_no": self.ids.policy_no.text,
                "date": self.ids.date.text,
                "start": self.ids.start.text,
                "end": self.ids.end.text,
            }

            user_uid = firebaseauth.userID
            user_doc = firestoredb.db.collection('users').document(user_uid).collection('Account').document('InsuranceInfo').set(data)

            Snackbar(
            text="Insurance Updated",
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=(Window.width - (10 * 2)) / Window.width
            ).open()
        
        except:
            Snackbar(
                text="Could not update information",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(Window.width - (10 * 2)) / Window.width
            ).open()
    def back(self):
        self.manager.transition.direction='right'
        self.manager.current = "home"
class Report(Screen):
    ph_tz = pytz.timezone('Asia/Manila')
    current_date= time.strftime("%B %d, %Y")
    current_time = time.strftime("%I:%M:%S %p")   
    def submitreport(self):
        rv = screen_manager.get_screen('result').ids.rv
        data = rv.data
        user_uid = firebaseauth.userID
        cloud_path=user_uid+"/"+time.strftime("%d-%m-%Y")
        img_urls=[]
        costs=[]
        parts=[]
        storage = firebaseauth.firebase.storage()
        for img in data:
            local_path = img['image_source']
            imgfname = local_path.split('/')
            img_cloud_path=cloud_path+"/"+imgfname[1]
            storage.child(img_cloud_path).put(local_path)
            img_urls.append(storage.child(img_cloud_path).get_url(None))
            costs.append(img['cost'])
            parts.append(img['damage'])
        try:
            user_uid = firebaseauth.userID
            blotterDetails={
                "ImgRef":img_urls,
                "Costs":costs,
                "PanelsPart":parts,
                "Date":self.ids.date.text,
                "Time":self.ids.time.text,
                "Location":self.ids.location.text,
                "Driver_Name":self.ids.accused_name.text,
                "Driver_Address":self.ids.accused_address.text,
                "Driver_Age":self.ids.accused_age.text,
                "Driver_Gender":self.ids.accused_gender.text,
                "Driver_License":self.ids.licensenum.text,
                "Vehicle":self.ids.vehicle.text,
                "Plate_number":self.ids.platenum.text,
                "Witness_Name":self.ids.witness_name.text,
                "Witness_Address":self.ids.witness_address.text,
                "Witness_Age":self.ids.witness_age.text,
                "Witness_Gender":self.ids.witness_gender.text,
                "report_sender":user_uid,
                "status": 'Pending'
            }
            VADetails.update(blotterDetails)
            Ckure.on_submit_report(Ckure)
            print(VADetails)
            self.manager.current = 'submitted'
        
        except:
            Snackbar(
                text="Could no submit your report!",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(Window.width - (10 * 2)) / Window.width
            ).open()
        
    def back(self, button):
        screen_manager.transition.direction='right'
        screen_manager.current = "result"
class MyReports(Screen):
    approved_count = NumericProperty(0)
    pending_count = NumericProperty(0)

    def on_pre_enter(self):
        user_uid = firebaseauth.userID
        reports = firestoredb.db.collection('reports')
        reports_query = reports.where('report_sender', '==', user_uid).get()
        reports_list = self.ids.validated
        reports_list.clear_widgets()
        pending_list = self.ids.pending
        pending_list.clear_widgets()
        
        approved_count = 0
        pending_count = 0
        
        for report in reports_query:
            report_data = report.to_dict()
            date = "Date: " + report_data['Date']
            time = "Time: " + report_data['Time']
            location = "Location: " + report_data['Location']
            
            if report_data['status'] == "Approved":
                item = ThreeLineListItem(text=date, secondary_text=time, tertiary_text=location)
                item.bind(on_release=lambda instance: self.show_report_details(report_data))
                reports_list.add_widget(item)
                approved_count += 1
                if approved_count==0:
                    image_widget = FitImage(source="assets/No data.png")
                    reports_list.add_widget(image_widget)
            elif report_data['status'] == "Pending":
                item = ThreeLineListItem(text=date, secondary_text=time, tertiary_text=location)
                item.bind(on_release=lambda instance: self.show_report_details(report_data))
                pending_list.add_widget(item)
                pending_count += 1
                if pending_count==0:
                    image_widget = FitImage(source="assets/No data.png")
                    reports_list.add_widget(image_widget)
        
        self.approved_count = approved_count
        self.pending_count = pending_count
    def show_report_details(self, report_data):
        dialog_text = "Date: {}\nTime: {}\nLocation: {}\nStatus: {}".format(
            report_data['Date'], report_data['Time'], report_data['Location'], report_data['status']
        )
        
        dialog_buttons = [
            MDFlatButton(
                text="Close",
                theme_text_color="Custom",
                text_color="#323B4E",
                on_release=lambda x: dialog.dismiss(),
            )
        ]
        
        if report_data['status'] == "Approved":
            dialog_buttons.insert(0, MDFlatButton(
                text="Submit Claim",
                theme_text_color="Custom",
                text_color="#323B4E",
                on_release=lambda x: self.submit_claim(),
            ))

        dialog = MDDialog(
            title="Report Details",
            text=dialog_text,
            buttons=dialog_buttons,
        )
        dialog.open()

    def back(self, button):
        screen_manager.transition.direction='right'
        screen_manager.current = "home"
class MyCLaims(Screen):
    def on_pre_enter(self):
        user_uid = firebaseauth.userID
        claims = firestoredb.db.collection('claims')
        claims_query = claims.where('claimant_id', '==', user_uid).get()
        claims_list = self.ids.validated
        claims_list.clear_widgets()
        pending_list = self.ids.pending
        pending_list.clear_widgets()
        for claim in claims_query:
            claim_data = claim.to_dict()
            print(claim_data)
            date = "Date: " + claim_data['Date']
            time = "Time: " + claim_data['Time']
            location = "Location: " + claim_data['Location']
            if claim_data['status']=="Approved":
                item = ThreeLineListItem(text=date , secondary_text=time, tertiary_text=location)
                claims_list.add_widget(item)
            elif claim_data['status']=="Pending":
                item = ThreeLineListItem(text=date , secondary_text=time, tertiary_text=location)
                pending_list.add_widget(item)
    def back(self, button):
        screen_manager.transition.direction='right'
        screen_manager.current = "home"
class Ckure(MDApp):
    image_list= []
    global VADetails
    VADetails={}

    def build(self):
        global screen_manager
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("splashscreen.kv"))
        screen_manager.add_widget(Login(name='login'))
        screen_manager.add_widget(SignUp(name='signup'))
        screen_manager.add_widget(CarDetails(name='car_details'))
        screen_manager.add_widget(InsuranceDetails(name='insurance_details'))
        screen_manager.add_widget(Home(name='home'))
        screen_manager.add_widget(MyCar(name='myCar'))
        screen_manager.add_widget(MyReports(name='myReports'))
        screen_manager.add_widget(MyInsurance(name='myInsurance'))
        screen_manager.add_widget(Result(name='result'))
        screen_manager.add_widget(Report(name='createReport'))
        screen_manager.add_widget(Submitted(name='submitted'))

        return screen_manager
    def on_start(self):
        Clock.schedule_once(self.login, 12)

    def login(self, *args):
        screen_manager.current = "login"
    #DELETING IMAGE DATASET
    
    #CALCULATE TOTAL AMOUNT TO BE PAID
    def total_cost(data_list):
        total_cost=0
        for data in data_list:
            for key,val in data.items():
                if key=='cost':
                    total_cost+=int(val)
    #DETECTION
    def performDetections(data_list):
        rf = Roboflow(api_key="6riPgDH2G6Wn2Lqa4MTC")
        model = rf.workspace().project("ckure").version(4).model
        response = model.predict(data_list['image_source'], confidence=40, overlap=30).json()

        if not response['predictions']:
            data_list['damage'] = 'No predictions found!'
            data_list['confidence'] = 'No predictions found!'
            dialog = MDDialog(
                title="No Predictions Found",
                text="No damage predictions were found for the image.",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
        else:
            predictions = [(round(pred['confidence'] * 100, 2), pred['class']) for pred in response['predictions']]
            predictions.sort(reverse=True)  # Sort predictions by confidence in descending order
            max_confidence = predictions[0][0]
            max_damage = predictions[0][1]
            data_list['damage'] = max_damage
            data_list['confidence'] = f"{max_confidence}%"
            model.predict(data_list['image_source'], confidence=40, overlap=30).save("prediction2.jpg")
                
        return data_list

    def delete(self, x):
        rv = screen_manager.get_screen('result').ids.rv
        data = rv.data
        for element in data:
            for key, value in element.items():
                if value == x:
                    myindex = data.index(element)
                    del data[myindex]
                    break
        # screen_manager.current='home'
    def generate_objectId(self, length):
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string
    
    # GENERATE REPORT
    def on_submit_report(self):
        reportTime = time.strftime("%d-%m-%Y")
        reportID= self.generate_objectId(self, 10)
        user_id = firebaseauth.userID
        VArec_ref ='reports'
        firestoredb.reportTime=reportTime
    
        try:
            #SAVE REPORT TO DB
            specifics_ref=firestoredb.db.collection(VArec_ref).document(reportID).set(VADetails)
            #SAVE IMAGE TO STORAGE
            storage = firebaseauth.firebase.storage()

            rv = screen_manager.get_screen('result').ids.rv
            data = rv.data
            cloud_path=user_id+"/"+reportTime
        
            for img in data:
                local_path = img['image_source']
                imgfname = local_path.split('/')
                img_cloud_path=cloud_path+"/"+imgfname[1]
                storage.child(img_cloud_path).put(local_path)


        except Exception as e:
            Snackbar(
                text="Submission Failed",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(Window.width - (10 * 2)) / Window.width
            ).open()
    
    
    def show_alert_dialog(self):
        self.dialog = MDDialog(
				# title = "Are you sure you want to proceed?",
				text = "Are you sure you want to proceed?",
				buttons =[
					MDFlatButton(
						text="NO", text_color=self.theme_cls.primary_color,on_release=self.close_dialog
						),
					MDRectangleFlatButton(
						text="YES", text_color=self.theme_cls.primary_color,on_release=self.proceed
						),
					],
				)
        self.dialog.open()
    def logout(self, button):
        screen_manager.get_screen('login').ids.email.text = ''
        screen_manager.get_screen('login').ids.password.text = ''
        screen_manager.current='login'
Ckure().run()
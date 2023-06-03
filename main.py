# LIBRARY AND MODULE IMPORTS
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.clock import Clock
from kivy.uix.image import Image as rawImage
from kivy.properties import StringProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.recycleview import RecycleView
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton,MDRectangleFlatIconButton

from kivymd.uix.sliverappbar import *
from kivymd.icon_definitions import md_icons
from datetime import datetime
from pytz import timezone
from PIL import Image, ImageOps
from PIL import Image as pilImage
from keras.models import load_model  # TensorFlow is required for Keras to work
import hashlib
import time
import numpy as np


# FILE_IMPORTS
import firebaseauth
import firestoredb





# CODING STARTS HERE
# ==================
# Window.size = (300, 500)
Window.size = (350, 630)
Builder.load_file("login.kv")
Builder.load_file("signup.kv")
Builder.load_file("carDetails.kv")
Builder.load_file("home.kv")
Builder.load_file("result.kv")
Builder.load_file("reportCar.kv")
Builder.load_file("driverdetails.kv")
Builder.load_file("submitted.kv")
Builder.load_file("agreement.kv")
Builder.load_file("success.kv")




#============================================
# =============SUCCESS PAGE================
class Success(Screen):
    def back(self, button):
        screen_manager.transition.direction='right'
        screen_manager.current = "agreement"


#============================================
# =============AGREEMENT PAGE================
class Agreement(Screen):
    pass


#============================================
# =============SUBMITTED PAGE================
class Submitted(Screen):
    def update_agreemnt(self):
        print(VADetails)
        DriverX = VADetails[2].get('Name')
        time = VADetails[0].get('Time')
        date =VADetails[0].get('Date')
        cost=VADetails[0].get('Amount')
        location =VADetails[0].get('Location')
        part = VADetails[0].get('Parts')

        uname = firebaseauth.userName

        letter = screen_manager.get_screen('agreement').ids.letter    
        letter.add_widget(MDLabel(text='{0} shall pay an amount of {1} to {2} for the cost of repair of the damaged {3} caused by collision at {4} last {5}, {6}'.format(DriverX,cost,uname,part,location,date,time)))

        
    def back(self, button):
        screen_manager.transition.direction='right'
        screen_manager.current = "driverdetails"



#============================================
# ================DRIVER PAGE================
class driverDetails(Screen):
    def details(self):
        screen_manager.current="driverdetails"
    
    
    def back(self, button):
        screen_manager.transition.direction='right'
        screen_manager.current = "report"
    
    def submit_rep(self):
        driver={
            "Address":self.ids.address.text,
            "License_number":self.ids.license.text,
            "Name":self.ids.name.text,
            "Phone_number":self.ids.contact.text,
            "Gender":self.ids.gender.text,
        }
        
        VADetails.append(driver)
        Ckure.on_submit_report(Ckure)
        print("Recorded")


#============================================
# ================REPORT PAGE================
class Report(Screen):
    current_date= time.strftime("%d-%m-%Y")
    current_time = time.strftime("%I:%M")

    def __init__(self, **kw):
        super().__init__(**kw)

        #INITIALIZE WHAT CAR COMPANY
        company_lst = firestoredb.get_company()
        companies= [
             {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.companiesCallbak(x),
            } for i in company_lst
        ]

        self.CompanyMenu = MDDropdownMenu(
            caller=self.ids.company,
            items=companies,
            width_mult=4,
            position="center"
        )

    def checkCompany(self, instance, focused):
        if focused:
            if self.ids.company.text!="":
                self.ModelMenu.open()

    def modelCallback(self, text_item):
        self.ids.model.text=text_item

    def companyCallback(self, text_item):
        self.ids.insurancecomp.text=text_item

    def companiesCallbak(self,text_item):
        self.ids.model.text=""
        self.ids.company.text=text_item
        model_lst=firestoredb.get_model(text_item)

        models=[
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.modelCallback(x)

            } for i in model_lst
        ]

        self.ModelMenu = MDDropdownMenu(
            caller=self.ids.model,
            items=models,
            width_mult=4,
            position="center"
        )
    
    
    def report(self):
        rv = screen_manager.get_screen('result').ids.rv
        data = rv.data
        parts =""
        for element in data:
            for key, value in element.items():
                if key == 'part':
                    parts+='{} '.format(value)

        mycost = screen_manager.get_screen('result').ids.cost.text

        #GENERATE LISTS FOR VADETAILS LIST
        CarDetails={
            "Insurance_company":self.ids.insurancecomp.text,
            "Model":self.ids.model.text,
            "Plate_number":self.ids.platenum.text,
            "Policy_number": self.ids.policynum.text,
        }
        
        VaSpecifics={
            "Time":self.ids.time.text,
            "Date":self.ids.date.text,
            "Location":self.ids.location.text,
            "Amount": mycost,
            "Parts": parts,
            "UserID": firebaseauth.userID,
            "Status": 'Pending'
        }
        
        VADetails.append(VaSpecifics)
        VADetails.append(CarDetails)
        
    def back(self, button):
        screen_manager.transition.direction='right'
        screen_manager.current = "result"

class driverDetails(Screen):
    def details(self):
        screen_manager.current="driverdetails"
    
    
    def back(self, button):
        screen_manager.transition.direction='right'
        screen_manager.current = "reportCar"
    
    def submit_rep(self):
        driver={
            "Address":self.ids.address.text,
            "License_number":self.ids.license.text,
            "Name":self.ids.name.text,
            "Phone_number":self.ids.contact.text,
            "Gender":self.ids.gender.text,
        }
        
        VADetails.append(driver)
        Ckure.on_submit_report(Ckure)
        print("Recorded")



#============================================
# ================RESULT PAGE================

class CustomRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = [{'image_source':str(i['image_source']),'category':i['category'],'part':i['part'],'severity':i['severity'],'cost':i['cost']} for i in Ckure.image_list]

# CUSTOM WIDGET FOR THE ITEMS IN THE RECYCLEVIEW
class CustomCard(MDCard):
    image_source = StringProperty()
    category = StringProperty()
    part = StringProperty()
    severity = StringProperty()
    cost=StringProperty()

class Result(Screen):
    def back(self, button):
        screen_manager.transition.direction='right'
        screen_manager.current = "home"

    def save():
        RecordAmount = 1000



#============================================
# ================HOME PAGE================

class someCard(MDCard):
    text=StringProperty()

class ContentNavigationDrawer(MDBoxLayout):
    pass

class Home(Screen, MDBoxLayout):
    sm = ObjectProperty()
    nav_drawer = ObjectProperty()

    #HISTORY SCREEN
    def __init__(self, **kw):
        super().__init__(**kw)
        # panels_data = [
        #     {"text": "Panel 1 for mahahabang text and di na kasya sa box"},
        #     {"text": "Panel 2"},
        #     {"text": "Panel 3"},
        # ]

        # for i in panels_data:
        #     self.ids.historyList.add_widget(someCard(text=i["text"]))
    

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
                "contact":self.ids.contact.text,
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
            'category':'Front',
            'part':'Bumper',
            'severity':'Minor',
            'cost':'0'
            }
        
        #UPDATE DICTIONARY

        image_data=Ckure.performDetections(image_data)

        #TO UPDATE IMAGE SOURCE
        rv = screen_manager.get_screen('result').ids.rv
        data = rv.data
        data.append(image_data)
        rv.refresh_from_data()
        Ckure.total_cost(Ckure,data)

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

        self.Update_DataSrc(myImg.source)

        print('MyID: ' + firebaseauth.userID)

        #MOVE TO NEXT PAGE UPON CAPTURING
        screen_manager.transition.direction='left'
        self.manager.current = 'result'

#============================================
# ================CAR DETAILS PAGE================
class CarDetails(Screen):
    current_date= time.strftime("%d-%m-%Y")
    current_time = time.strftime("%I:%M")

    def __init__(self, **kw):
        super().__init__(**kw)
        
        #INITIALIZE CAR BRAND
        company_lst = firestoredb.get_company()
        companies= [
             {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.companiesCallbak(x),
            } for i in company_lst
        ]
        self.CompanyMenu = MDDropdownMenu(
            caller=self.ids.company,
            items=companies,
            width_mult=4,
            position="center"
        )
        
    def checkCompany(self, instance, focused):
        if focused:
            if self.ids.company.text!="":
                self.ModelMenu.open()
    
    def modelCallback(self, text_item):
        self.ids.model.text=text_item

    def companiesCallbak(self,text_item):
        self.ids.model.text=""
        self.ids.company.text=text_item
        model_lst=firestoredb.get_model(text_item)

        models=[
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.modelCallback(x)

            } for i in model_lst
        ]

        self.ModelMenu = MDDropdownMenu(
            caller=self.ids.model,
            items=models,
            width_mult=4,
            position="center"
        )

    def saveCarDetails(self):
        userRef = 'users/'+firebaseauth.userID+'/Account'

        try:
            data={
                "company":self.ids.company.text,
                "model":self.ids.model.text,
                "plate": self.ids.platenum.text,
                "policy_number":self.ids.policynum.text
            }
            firestoredb.store_userCar(userRef,data)
            Snackbar(
                text="Car details saved",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(Window.width - (10 * 2)) / Window.width
            ).open()

        
        except Exception as e:
            Snackbar(
                text="Saving Failed",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(Window.width - (10 * 2)) / Window.width
            ).open()



#============================================
# ================SIGNUP PAGE================

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
            position="center"
        )

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
            }   
            user_ref = firestoredb.db.collection('users').document(user_uid)
            user_ref.set({})
            user_doc = firestoredb.db.collection('users').document(user_uid).collection('Account').document('UserInfo').set(data)
            self.manager.current = 'login'
            print('Registration Success!')
        except Exception as e:
            Snackbar(
                text="Registration Failed",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(Window.width - (10 * 2)) / Window.width
            ).open()
        
    def back(self):
        self.manager.transition.direction='right'
        self.manager.current = "login"
    

#============================================
# ================LOGIN PAGE================

class Login(Screen):

    def myCredentials(self,user_id):
        if user_id:
            myScr = screen_manager.get_screen("home")
            current_cred = firestoredb.db.collection('users').document(user_id).collection('Account').document('UserInfo').get()
            myCurrCred = current_cred.to_dict()
                        
            #STORE USERNAME
            firebaseauth.userName = myCurrCred.get('name')

            myScr.ids.name.text = myCurrCred.get('name')
            myScr.ids.email.text = myCurrCred.get('email')
            myScr.ids.address.text = myCurrCred.get('address')
            myScr.ids.contact.text = myCurrCred.get('contact')
            myScr.ids.age.text = myCurrCred.get('age')
            myScr.ids.dob.text = myCurrCred.get('dob')
            myScr.ids.gender.text = myCurrCred.get('gender')


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


# STARTING CLASS
# =================
class Ckure(MDApp):
    image_list= []
    global VADetails
    VADetails=[]

    def build(self):
        global screen_manager

        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("splashscreen.kv"))
        screen_manager.add_widget(Login(name='login'))
        screen_manager.add_widget(SignUp(name='signup'))
        screen_manager.add_widget(CarDetails(name='car_details'))
        screen_manager.add_widget(Home(name='home'))
        screen_manager.add_widget(Result(name='result'))
        screen_manager.add_widget(Report(name='reportCar'))
        screen_manager.add_widget(driverDetails(name='driverdetails'))
        screen_manager.add_widget(Submitted(name='submitted'))
        screen_manager.add_widget(Agreement(name='agreement'))
        screen_manager.add_widget(Success(name='success'))

        return screen_manager
    
    #DELETING IMAGE DATASET
    def delete(self,x):
        rv = screen_manager.get_screen('result').ids.rv
        data = rv.data

        for element in data:
            for key, value in element.items():
                if value == x:
                    myindex=data.index(element)

        del data[myindex]
        self.total_cost(data)
        rv.refresh_from_data()


    #CALCULATE TOTAL AMOUNT TO BE PAID
    def total_cost(self,x_list):
        total_cost=0
        for e in x_list:
            for key,val in e.items():
                if key=='cost':
                    total_cost+=int(val)
        
        #REFERENCE TO THE RESULT COST
        mycost = screen_manager.get_screen('result').ids.cost
        mycost.text = "Php " + str(total_cost)

    #DETECTION
    def performDetections(data_list):

        # Disable scientific notation for clarity
        np.set_printoptions(suppress=True)

        # Load the model
        severity_model = load_model("models/severity/severity_model.h5", compile=False)
        parts_model = load_model("models/parts/parts_model.h5", compile=False)

        # Load the labels
        severity_class_names = open("models/severity/severity_labels.txt", "r").readlines()
        parts_class_names = open("models/parts/parts_labels.txt", "r").readlines()

        # Create the array of the right shape to feed into the keras model
        # The 'length' or number of images you can put into the array is
        # determined by the first position in the shape tuple, in this case 1
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

        # Replace this with the path to your image
        image = Image.open(data_list['image_source']).convert("RGB")

        # resizing the image to be at least 224x224 and then cropping from the center
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

        # turn the image into a numpy array
        image_array = np.asarray(image)

        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

        # Load the image into the array
        data[0] = normalized_image_array

        # PART DETECTION
        part_prediction = parts_model.predict(data)
        index = np.argmax(part_prediction)
        # data_part = parts_class_names[index]
        data_list['part']=parts_class_names[index][2:].strip()
        print("Index of part is", index)        
        
        #CATEGORY DETECTION
        categoryList={
            'Front':{0,6,4,7,10}, 
            'Rear':{1,5,8,11},
            'Side':{2,3,9}}
        
        for category,values in categoryList.items():
            if index in values:
                data_list['category'] = category

        # SEVERITY DETECTION
        severity_prediction = severity_model.predict(data)
        index = np.argmax(severity_prediction)
        data_severity = severity_class_names[index]
        data_list['severity'] = data_severity[2:]

        #COST DETECTION
        costs = {'minor':100,'moderate':10000,'severe':1000000}
        mycost = costs.get(data_list['severity'].strip(),'0')
        data_list['cost']=str(mycost)

        return data_list

    # GENERATE REPORT
    def on_submit_report(self):
        reportTime = time.strftime("%d-%m-%Y")
        # self.VAdetails['amount'] = self.total_cost
        user_id = firebaseauth.userID
        VArec_ref ='reports'
        amount = screen_manager.get_screen('result').ids.cost.text
        VADetails[0]['Cost']=amount[4:]
        firestoredb.reportTime=reportTime
    
        try:
            
            # print('submitted!')
            # ADD INFO ON VARECORD
            # firestoredb.recordVA(VArec_ref,VADetails[0])
            specifics_ref=firestoredb.db.collection(VArec_ref).document(reportTime).set(VADetails[0])
            # ADD COLLECTION
            driverdtls_ref = firestoredb.db.collection(VArec_ref).document(reportTime).collection('details').document('Driver').set(VADetails[2])
            cardtls_ref = firestoredb.db.collection(VArec_ref).document(reportTime).collection('details').document('Vehicle').set(VADetails[1])

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

    def close_dialog(self, obj):
        VArec_ref ='reports'
        VADetails[0]['Status']='Disagreed'
        specifics_ref=firestoredb.db.collection(VArec_ref).document(firestoredb.reportTime).set(VADetails[0])
        self.dialog.dismiss()

    def proceed(self, obj):
        VArec_ref ='reports'
        VADetails[0]['Status']='Agreed'
        specifics_ref=firestoredb.db.collection(VArec_ref).document(firestoredb.reportTime).set(VADetails[0])

        self.dialog.dismiss()
        screen_manager.transition.direction='left'
        screen_manager.current = "success"

    def logout(self, button):
        screen_manager.get_screen('login').ids.email.text = ''
        screen_manager.get_screen('login').ids.password.text = ''
        screen_manager.current='login'

    def on_start(self):
        Clock.schedule_once(self.login, 5)

    def login(self, *args):
        screen_manager.current = "login"

Ckure().run()
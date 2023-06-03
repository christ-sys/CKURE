import calendar
from datetime import datetime
import os
import sys

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import *
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.utils import *
from kivymd.app import MDApp
from kivymd.effects.fadingedge.fadingedge import FadingEdgeEffect
from kivymd.uix.bottomsheet import *
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import *
from kivymd.uix.card import MDCard
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.expansionpanel import *
from kivymd.uix.label import *
from kivymd.uix.list import *
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField

sys.path.append('project/imports')
from datetime import datetime

import firebaseauth
import firestoredb
import pytz

import random
import string

Window.size = (350, 680)
Builder.load_file("login.kv")
Builder.load_file("dashboard.kv")
Builder.load_file("accounts.kv")
Builder.load_file("car_brand.kv")
Builder.load_file("car_models.kv")
Builder.load_file("cars.kv")
Builder.load_file("cardetails.kv")
Builder.load_file("estimate.kv")
Builder.load_file("reports.kv")
class AdminLogin(Screen):
    email = 'ckure.org@mail.com'
    def show_password(self,checkbox,value):
        if value:
            self.ids.password.password=False
            self.ids.show_password.text="Hide Password"
        else:
            self.ids.password.password=True
            self.ids.show_password.text="Show Password"
    def verify_admin(self):
        email = self.ids.email.text
        password = self.ids.password.text
        try:
            # user = firebaseauth.auth.create_user_with_email_and_password(email, password)
            user = firebaseauth.auth.sign_in_with_email_and_password(email, password)
            # custom_token = firebaseauth.auth.create_custom_token(uid)
            # user = firebaseauth.auth.sign_in_with_custom_token(custom_token)
            AdminLogin.email = email
            self.manager.current='dashboard'
        except Exception as e: 
            print(e)
            # dialog = MDDialog(title="Error", text="User Not Found!")
            # dialog.open()
class Dashboard(Screen):
    current_time = StringProperty()
    def count_users(self):
        users_col = firestoredb.get_all_users()
        total = len(users_col)
        return str(total)
    def count_reports(self):
        reports_col = firestoredb.get_all_reports()
        total = len(reports_col)
        return str(total)
    def date_today(self):
        today = datetime.now().date()
        return str(today)
class Estimation(Screen):
    dropdown_item = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        car_make = firestoredb.get_make()
        # car_model = firestoredb.get_car_models(brand)
        cars = [
            {
                "text": f"{cars_make}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{cars_make}": self.make_callback(x)
                
            } for cars_make in car_make
        ]
        self.cars_make_name = MDDropdownMenu(
            caller=self.ids.cars,
            items=cars,
            width_mult=2.5,
            elevation=0,
            max_height=dp(140),
        )
        # models
    def make_callback(self, text_item):
        self.cars_make_name.dismiss()
        self.ids.cars.text=text_item
    def model_callback(self, text_item):
        pass
class Brand(Screen):
    def brand(self):
        brands = firestoredb.get_brand()
        layout = GridLayout(cols=1, spacing='10dp', padding='20dp', size_hint_y=None)
        for brand in brands:
            item = OneLineRightIconListItem(text=brand, on_release=self.on_brand_selected)
            item.add_widget(IconRightWidget(icon='chevron-right'))
            layout.add_widget(item)
        return layout
    def on_enter(self):
        grid = self.ids.grid
        grid.clear_widgets()
        box_layout = self.brand()
        grid.add_widget(box_layout)
    def on_brand_selected(self, brand_item):
        brand_id = brand_item.text  
        models = firestoredb.get_model(brand_id)
        models_screen = self.manager.get_screen("car_models")
        models_screen.clear_models()
        models_screen.set_brand(brand_id)
        models_screen.initialize_models(models)
        self.manager.current = "car_models"
    def generate_objectId(self, length):
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

    def add_brand(self):
        brand_textfield = MDTextField(
            id="brand_textfield",
            hint_text="Brand",
            mode="fill",
            pos_hint={"center_x": 0.5},
        )
        cat_textfield = MDTextField(
            id="cat_textfield",
            hint_text="Category",
            mode="fill",
            pos_hint={"center_x": 0.5},
        )
        model_textfield = MDTextField(
            id="model_textfield",
            hint_text="Model",
            mode="fill",
            pos_hint={"center_x": 0.5},
        )
        year_textfield = MDTextField(
            id="year_textfield",
            hint_text="Year",
            mode="fill",
            pos_hint={"center_x": 0.5},
        )

        save_button = MDFlatButton(text="Save", on_release=lambda *args: self.save_brand(brand_textfield, cat_textfield, model_textfield, year_textfield, dialog))
        dialog = MDDialog(
            title="Add Brand",
            type="custom",
            content_cls=MDBoxLayout(orientation="vertical", spacing="18dp", size_hint_y=None, height="250dp"),
            buttons=[save_button],
        )
        
        dialog.content_cls.add_widget(brand_textfield)
        dialog.content_cls.add_widget(cat_textfield)
        dialog.content_cls.add_widget(model_textfield)
        dialog.content_cls.add_widget(year_textfield)
        
        dialog.open()

    def save_brand(self, brand_textfield, cat_textfield, model_textfield, year_textfield, dialog):
        brand = brand_textfield.text.strip()
        category = cat_textfield.text.strip()
        model = model_textfield.text.strip()
        year = year_textfield.text.strip()
        objectId = self.generate_objectId(10)
        if not brand:
            brand_textfield.error = True
            brand_textfield.helper_text = "Please fill this field"
            return
        car_data = {
            "Make": brand,
            "Category": category,
            "Model": model,
            "Year": int(year),
            "objectID": objectId,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        car_ref = firestoredb.db.collection("cars").document(brand)
        car_ref.set({})
        car_doc = firestoredb.db.collection("cars").document(brand).collection("data").document(objectId)
        car_doc.set(car_data)
        dialog.dismiss()
        self.reload_page()
    def reload_page(self):
        grid = self.ids.grid
        grid.clear_widgets()
        box_layout = self.brand()
        grid.add_widget(box_layout)
class Model(Screen):
    def initialize_models(self, models):
        layout = GridLayout(cols=1, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))  
        for model, count in models.items():
            item = TwoLineRightIconListItem(text=model, secondary_text=f"{count}", on_release=self.on_model_selected)
            item.add_widget(IconRightWidget(icon='chevron-right'))
            layout.add_widget(item)
        
        scrollview = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        scrollview.add_widget(layout)
        
        grid = self.ids.grid
        grid.clear_widgets()
        grid.add_widget(scrollview)
    def on_model_selected(self, model_item):
        brand_id = self.selected_brand
        model = model_item.text  
        models_screen = self.manager.get_screen("car_models")
        cars = firestoredb.get_cars(brand_id, model)
        cars_screen = self.manager.get_screen("cars")
        cars_screen.initialize_cars(cars)
        self.manager.current = "cars"
    def clear_models(self):
        grid = self.ids.grid
        grid.clear_widgets()
    def set_brand(self, brand):
        self.selected_brand = brand
    def back(self, button):
        self.manager.transition.direction='right'
        self.manager.current = "car_brand"
class Cars(Screen):
    def initialize_cars(self, cars):
        layout = GridLayout(cols=1, spacing='10dp', padding='20dp', size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))  
        
        for car in cars:
            make = car.get('Make', '')
            category = car.get('Category', '')
            # model = car.get('Model', '')
            year = car.get('Year', '')
            object_id = car.get('objectId','')
            
            item = ThreeLineListItem(text=make, secondary_text=category, tertiary_text=f"{year}", on_release=self.on_car_selected)
            item.object_id = object_id
            layout.add_widget(item)
        
        scrollview = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        scrollview.add_widget(layout)
        
        grid = self.ids.grid
        grid.clear_widgets()
        grid.add_widget(scrollview)
    def on_car_selected(self, car_item):
        object_id = car_item.object_id 
        brand_id = self.manager.get_screen('car_models').selected_brand
        car = firestoredb.get_car_by_id(brand_id, object_id)
        cardetails_screen = self.manager.get_screen("cardetails")
        cardetails_screen.display_car(car)
        self.manager.current = "cardetails"
    def back(self, button):
        self.manager.transition.direction='right'
        self.manager.current = "car_models"
class Cardetails(Screen):
    def display_car(self,car):
        self.ids.category_label.text = car.get('Category', '')
        self.ids.make_label.text = car.get('Make', '')
        self.ids.year_label.text = str(car.get('Year', ''))
        self.ids.model_label.text = car.get('Model', '')
    def back(self, button):
        self.manager.transition.direction='right'
        self.manager.current = "cars"
class Reports(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_tables = None
        self.create_table()
    def create_table(self):
        self.data_tables = MDDataTable(
            size_hint=(0.9, 0.7),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            elevation=1,
            use_pagination=True,
            check=True,
            column_data=[
                ("Report No.", dp(40)),
                ("Date", dp(30)),
                ("Time", dp(30))
            ],
            row_data=self.all_reports(),
        )
        # self.data_tables.bind(on_row_press=self.row_clicked)
        self.add_widget(self.data_tables)

    def all_reports(self):
        reports = firestoredb.get_all_reports()
        report_row =[]
        for report in reports:
        # Philippine time zone
            date_obj = report['dateTime']
            ph_tz = pytz.timezone('Asia/Manila')
            dateTime_obj_ph = date_obj.astimezone(ph_tz)
            date_str_ph = dateTime_obj_ph.strftime('%Y-%m-%d')
            time_str_ph = dateTime_obj_ph.strftime('%I:%M:%S %p')
            # time_str_ph = dateTime_obj_ph.strftime('%I:%M:%S.%f %p %Z')
            row = [ report['id'], 
                   date_str_ph,
                   time_str_ph]
            report_row.append(row)
        return report_row
class Accounts(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_tables = None
        self.create_table()
    def create_table(self):
        self.data_tables = MDDataTable(
            size_hint=(0.9, 0.7),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            elevation=1,
            use_pagination=True,
            check=True,
            column_data=[
                ("Name", dp(60)),
                ("Email", dp(60)),
                ("Gender", dp(30)),
                ("Address", dp(30)),
                ("Birthday", dp(30)),
                ("Age", dp(10)),
                ("Phone", dp(30)),
            ],
            row_data=self.all_users(),
        )
        self.data_tables.bind(on_row_press=self.row_clicked)
        self.add_widget(self.data_tables)

    def all_users(self):
        users = firestoredb.get_all_users()
        user_row =[]
        for user in users:
            row = [
                user['name'],
                user['email'],
                user['gender'],
                user['address'],
                user['dob'],
                user['age'],
                user['phone'],
            ]
            user_row.append(row)
        return user_row
    def row_clicked(self, data_tables,row):
        
        self.dialog=MDDialog(
            title="Delete User",
            text="Are you sure to delete user?",
            size_hint=(0.8,0.2),
            buttons=[
                MDRaisedButton(
                    text="Yes",
                    md_bg_color="#ff0000"
                ),
                MDRaisedButton(
                    text="No",
                )
            ]
        )
        self.dialog.open()
    def close_dialog(self):
        self.dialog.dismiss()
    def edit_user(self, instance):
        pass
    def delete_user(self, instance):
        pass
class ContentNavigationDrawer(MDBoxLayout):
    sm = ObjectProperty()
    nav_drawer = ObjectProperty()
    name_label = ObjectProperty()
    email_label = ObjectProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = None
        Clock.schedule_once(self.get_user_info)
        self.panels = []
        self.panel_expanded = False

    def get_user_info(self, dt):
        try:
            user_record = firestoredb.auth.get_user_by_email(AdminLogin.email)
            local_id = user_record.uid
            user_doc = firestoredb.db.collection('users').document(local_id).get()
            user_data = user_doc.to_dict()
            self.name_label.text = user_data.get('name', '')
            self.name_label.secondary_text = user_data.get('email', '')
            
        except Exception as e:
            print(e)
            # handle exception
class AdminApp(MDApp):
    def build(self):
        global screen_manager
        screen_manager = ScreenManager()
        screen_manager.add_widget(AdminLogin(name='adminLogin'))
        screen_manager.add_widget(Dashboard(name='dashboard'))
        # screen_manager.add_widget(Estimation(name='estimation'))
        screen_manager.add_widget(Brand(name="car_brand"))
        screen_manager.add_widget(Model(name="car_models"))
        screen_manager.add_widget(Cars(name="cars"))
        screen_manager.add_widget(Cardetails(name="cardetails"))
        screen_manager.add_widget(Reports(name='reports'))
        screen_manager.add_widget(Accounts(name='accounts'))
        self.theme_cls.theme_style = "Light"
        return screen_manager
    
    def back(self, button):
        screen_manager.transition.direction='right'
        screen_manager.current = "dashboard"
    def logout(self):
        screen_manager.get_screen('adminLogin').ids.email.text = ''
        screen_manager.get_screen('adminLogin').ids.password.text = ''
        screen_manager.current='adminLogin'
    # AUTO RELOAD
    AUTORELOADER_PATHS = [
        (".",{"recursive": True})
    ]
AdminApp().run()
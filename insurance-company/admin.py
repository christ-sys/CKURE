import calendar
import os
import sys
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import *
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.utils import *
from kivymd.app import MDApp
from kivymd.effects.fadingedge.fadingedge import FadingEdgeEffect
from kivymd.uix.backdrop.backdrop import *
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
from kivymd.uix.recycleview import RecycleView
from kivymd.uix.sliverappbar import *
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.tab.tab import *
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.tooltip.tooltip import MDTooltip

sys.path.append('project/imports')
import random
import string
from datetime import datetime

import firebaseauth
import firestoredb
import pytz

# Window.size = (350, 630)
Builder.load_file("login.kv")
Builder.load_file("dashboard.kv")
Builder.load_file("accounts.kv")
Builder.load_file("userdetails.kv")
Builder.load_file("car_brand.kv")
Builder.load_file("car_models.kv")
Builder.load_file("cars.kv")
Builder.load_file("cardetails.kv")
# Builder.load_file("estimate.kv")
Builder.load_file("claims.kv")
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
    def count_claims(self):
        claims_col = firestoredb.get_all_claims()
        total = len(claims_col)
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
        variant_textfield = MDTextField(
            id="variant_textfield",
            hint_text="Variant",
            mode="fill",
            pos_hint={"center_x": 0.5},
        )
        save_button = MDFlatButton(text="Save", on_release=lambda *args: self.save_brand(brand_textfield, cat_textfield, model_textfield, year_textfield, variant_textfield, dialog))
        dialog = MDDialog(
            title="Add Brand",
            type="custom",
            content_cls=MDBoxLayout(orientation="vertical", spacing="18dp", size_hint_y=None, height="320dp"),
            buttons=[save_button],
        )
        
        dialog.content_cls.add_widget(brand_textfield)
        dialog.content_cls.add_widget(cat_textfield)
        dialog.content_cls.add_widget(model_textfield)
        dialog.content_cls.add_widget(year_textfield)
        dialog.content_cls.add_widget(variant_textfield)
        dialog.open()

    def save_brand(self, brand_textfield, cat_textfield, model_textfield, year_textfield, variant_textfield, dialog):
        brand = brand_textfield.text.strip()
        category = cat_textfield.text.strip()
        model = model_textfield.text.strip()
        year = year_textfield.text.strip()
        variant = variant_textfield.text.strip()
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
            "objectId": objectId,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
            "Variant": variant
        }
        
        car_ref = firestoredb.db.collection("cars").document(brand)
        car_ref.set({})
        car_doc = firestoredb.db.collection("cars").document(brand).collection("data").document(objectId)
        car_doc.set(car_data)
        dialog.dismiss()
        self.reload_page()
        self.show_snackbar("Added Successfully")
    def show_snackbar(self, text):
        snackbar = Snackbar(text=text, duration=2.5)
        snackbar.open()
    def reload_page(self):
        grid = self.ids.grid
        grid.clear_widgets()
        box_layout = self.brand()
        grid.add_widget(box_layout)
class Model(Screen):
    def initialize_models(self, models):
        sorted_models = sorted(models.keys())
        
        layout = GridLayout(cols=1, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))  
        for model in sorted_models:
            count = models[model]
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
        layout = GridLayout(cols=1,size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height')) 
        
        for car in cars:
            make = car.get('Make', '')
            category = car.get('Category', '')
            # model = car.get('Model', '')
            year = car.get('Year', '')
            variant = car.get('Variant', '')
            object_id = car.get('objectId','')
            item = ThreeLineAvatarIconListItem(text=make, secondary_text=category, tertiary_text=f"{year}", on_release=self.on_car_selected)
            item.add_widget(IconRightWidget(icon='chevron-right'))
            item.add_widget(IconLeftWidget(icon='car'))
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
        car = firestoredb.get_car_by_id(brand_id,object_id)
        cardetails_screen = self.manager.get_screen("cardetails")
        cardetails_screen.display_car(car)
        self.manager.current = "cardetails"
    def back(self, button):
        self.manager.transition.direction='right'
        self.manager.current = "car_models"
class Cardetails(Screen):
    def __init__(self, **kwargs):
        super(Cardetails, self).__init__(**kwargs)
        self.app_bar = MDSliverAppbarHeader(
            MDRectangleFlatIconButton(
                text="Details",
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
    car = None  # Define the car attribute
    def display_car(self, car):
        self.car = car  
        self.ids.category_label.text = car.get('Category', '')
        self.ids.make_label.text = car.get('Make', '')
        self.ids.year_label.text = str(car.get('Year', ''))
        self.ids.model_label.text = car.get('Model', '')
        self.ids.variant_label.text = car.get('Variant', '')
    def edit(self):
        cat_textfield = MDTextField(
            id="cat_textfield",
            hint_text="Category",
            mode="fill",
            pos_hint={"center_x": 0.5},
            text=self.car.get('Category', '')  
        )
        model_textfield = MDTextField(
            id="model_textfield",
            hint_text="Model",
            mode="fill",
            pos_hint={"center_x": 0.5},
            text=self.car.get('Model', '') 
        )
        year_textfield = MDTextField(
            id="year_textfield",
            hint_text="Year",
            mode="fill",
            pos_hint={"center_x": 0.5},
            text=str(self.car.get('Year', ''))
        )
        variant_textfield = MDTextField(
            id="variant_textfield",
            hint_text="Variant",
            mode="fill",
            pos_hint={"center_x": 0.5},
            text=str(self.car.get('Variant', '')) 
        )

        save_button = MDFlatButton(text="Save", on_release=lambda *args: self.save_edit(cat_textfield.text, model_textfield.text, year_textfield.text, variant_textfield.text, dialog))
        dialog = MDDialog(
            title="Edit Car",
            type="custom",
            content_cls=MDBoxLayout(orientation="vertical", spacing="18dp", size_hint_y=None, height="280dp"),
            buttons=[save_button],
        )

        dialog.content_cls.add_widget(cat_textfield)
        dialog.content_cls.add_widget(model_textfield)
        dialog.content_cls.add_widget(year_textfield)
        dialog.content_cls.add_widget(variant_textfield)

        dialog.open()
    def save_edit(self, category, model, year, variant, dialog):
        self.car['Category'] = category
        self.car['Model'] = model
        self.car['Year'] = year
        self.car['Variant'] = variant
        self.car['updatedAt'] = datetime.now()
        self.ids.category_label.text = category
        self.ids.year_label.text = str(year)
        self.ids.model_label.text = model
        self.ids.variant_label.text = variant
        # Update the car details
        brand_id = self.manager.get_screen('car_models').selected_brand
        object_id = self.car['objectId']
        firestoredb.update_car(brand_id, object_id, self.car)
        dialog.dismiss()
        self.show_snackbar("Details Updated Successfully")
    def delete(self):
        confirm_dialog = MDDialog(
            title="Confirm Delete",
            text="Are you sure you want to delete this car?",
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    on_release=lambda *args: confirm_dialog.dismiss()
                ),
                MDFlatButton(
                    text="Delete",
                    on_release=lambda *args: self.delete_car(confirm_dialog)
                ),
            ],
        )
        confirm_dialog.open()

    def delete_car(self, confirm_dialog):
        brand_id = self.manager.get_screen('car_models').selected_brand
        object_id = self.car['objectId']
        # Delete the car from Firestore
        firestoredb.delete_car(brand_id, object_id)
        confirm_dialog.dismiss()
        self.manager.transition.direction='left'
        self.manager.current = "car_brand"
        self.show_snackbar("Car deleted successfully")
    def show_snackbar(self, text):
        snackbar = Snackbar(text=text, duration=2.5)
        snackbar.open()
    def back(self):
        self.manager.transition.direction='right'
        self.manager.current = "cars"
class Claims(Screen):
    pass
class Accounts(Screen):
    def on_pre_enter(self):
        users = firestoredb.get_all_users()
        user_list = self.ids.user_list
        user_list.clear_widgets()
        for user in users:
            item = OneLineListItem(text=user['name'])
            item.bind(on_release=lambda x, user_id=user['id']: self.switch_to_user_profile(user_id))
            user_list.add_widget(item)
    def switch_to_user_profile(self, user_id):
        app = MDApp.get_running_app()
        app.root.current = 'userProfile'
        app.root.get_screen('userProfile').show_user_profile(user_id)
class UserProfile(Screen):
    def __init__(self, **kwargs):
        super(UserProfile, self).__init__(**kwargs)
        self.dialog = None
        self.user_data = {}
        self.user_id = None

    def show_user_profile(self, user_id):
        self.user_id = user_id
        self.user_data = firestoredb.get_user_details(user_id)
        self.update_labels()

    def edit(self):
        name_field = MDTextField(
            hint_text="Name",
            text=self.user_data['name'],
            mode="fill",
        )

        email_field = MDTextField(
            hint_text="Email",
            text=self.user_data['email'],
            mode="fill",
        )
        contact_field = MDTextField(
            hint_text="Phone",
            text=self.user_data['phone'],
            mode="fill",
        )
        address_field = MDTextField(
            hint_text="Address",
            text=self.user_data['address'],
            mode="fill",
        )
        gender_field = MDTextField(
            hint_text="Gender",
            text=self.user_data['gender'],
            mode="fill",
        )
        age_field = MDTextField(
            hint_text="Age",
            text=self.user_data['age'],
            mode="fill",
        )
        content_box = MDBoxLayout(
            orientation="vertical",
            spacing="18dp",
            size_hint_y=None,
            height="380dp",
        )
        content_box.add_widget(name_field)
        content_box.add_widget(email_field)
        content_box.add_widget(contact_field)
        content_box.add_widget(address_field)
        content_box.add_widget(gender_field)
        content_box.add_widget(age_field)
        save_button = MDFlatButton(text="Save", on_release=lambda *args: self.save_profile(name_field.text, email_field.text, contact_field.text, address_field.text, gender_field.text, age_field.text))
        cancel_button = MDFlatButton(text="Cancel",on_release=lambda x: self.dialog.dismiss())
        self.dialog = MDDialog(
            elevation = 0,
            title="Edit User",
            type="custom",
            content_cls=content_box,
            buttons=[save_button,cancel_button]
        )

        self.dialog.open()
    def save_profile(self,name,email,contact,address,gender,age):
        self.user_data['name'] = name
        self.user_data['email'] = email
        self.user_data['phone'] = contact
        self.user_data['address'] = address
        self.user_data['gender'] = gender
        self.user_data['age'] = age
        self.ids.name_label.text = name
        self.ids.email_label.text = email
        self.ids.phone_label.text = contact
        self.ids.address_label.text = address
        self.ids.gender_label.text = gender
        self.ids.age_label.text = age
        firestoredb.update_user_details(self.user_id, self.user_data)
        
        self.dialog.dismiss()
        self.show_snackbar("User Details Updated Successfully")
        self.update_labels()


    def update_labels(self):
        name_title = self.ids.name_title
        name_label = self.ids.name_label
        email_label = self.ids.email_label
        age_label = self.ids.age_label
        address_label = self.ids.address_label
        birthday_label = self.ids.birthday_label
        gender_label = self.ids.gender_label
        phone_label = self.ids.phone_label

        name_title.title = self.user_data.get('name', '')
        name_label.text = self.user_data.get('name', '')
        email_label.text = self.user_data.get('email', '')
        age_label.text = self.user_data.get('age', '')
        address_label.text = self.user_data.get('address', '')
        birthday_label.text = self.user_data.get('dob', '')
        gender_label.text = self.user_data.get('gender', '')
        phone_label.text = self.user_data.get('phone', '')


    def show_snackbar(self, text):
        snackbar = Snackbar(text=text, duration=2.5)
        snackbar.open()
    def back(self, button):
        self.manager.transition.direction='right'
        self.manager.current = "accounts"
class ContentNavigationDrawer(MDBoxLayout):
    sm = ObjectProperty()
class AdminApp(MDApp):
    def build(self):
        self.title = "ABC - Insurance"
        global screen_manager
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("splashscreen.kv"))
        screen_manager.add_widget(AdminLogin(name='adminLogin'))
        screen_manager.add_widget(Dashboard(name='dashboard'))
        # screen_manager.add_widget(Estimation(name='estimation'))
        screen_manager.add_widget(Brand(name="car_brand"))
        screen_manager.add_widget(Model(name="car_models"))
        screen_manager.add_widget(Cars(name="cars"))
        screen_manager.add_widget(Cardetails(name="cardetails"))
        screen_manager.add_widget(Claims(name='claims'))
        screen_manager.add_widget(Accounts(name='accounts'))
        screen_manager.add_widget(UserProfile(name='userProfile'))
        self.theme_cls.theme_style = "Light"
        return screen_manager
    def on_start(self):
        Clock.schedule_once(self.login, 12)
    def login(self, *args):
        screen_manager.current = "adminLogin"
    
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
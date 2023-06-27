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
from kivy.uix.image import AsyncImage, Image
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.utils import *
from kivymd.app import MDApp
from kivymd.effects.fadingedge.fadingedge import FadingEdgeEffect
from kivymd.toast import toast
from kivymd.uix.backdrop.backdrop import *
from kivymd.uix.bottomsheet import *
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import *
from kivymd.uix.card import MDCard
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.expansionpanel import *
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import *
from kivymd.uix.list import *
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.recycleview import RecycleView
from kivymd.uix.segmentedcontrol import (MDSegmentedControl,
                                         MDSegmentedControlItem)
from kivymd.uix.sliverappbar import *
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.tab import *
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.tooltip.tooltip import MDTooltip

sys.path.append('imports')
import random
import string
from datetime import datetime

import pytz
from kivymd.uix.bottomnavigation.bottomnavigation import *

import firebaseauth
import firestoredb

Window.size = (350, 630)
Builder.load_file("admin.kv")
Builder.load_file("dashboard.kv")
Builder.load_file("claims.kv")
Builder.load_file("claim_details.kv")

class ContentNavigationDrawer(MDBoxLayout):
    sm = ObjectProperty()
class AdminLogin(Screen):
    def verify_admin(self):
        email = self.ids.email.text
        password = self.ids.password.text
        try:
            user = firebaseauth.auth.sign_in_with_email_and_password(email, password)
            self.manager.current='dashboard'
        except:
            self.show_error_dialog()

    def show_error_dialog(self):
        ok_button = MDFlatButton(text="OK", on_release=self.dismiss_dialog)
        self.dialog = MDDialog(
            title="Error",
            text="INVALID ACCOUNT",
            buttons=[ok_button]
        )
        self.dialog.open()
    def dismiss_dialog(self, *args):
        self.dialog.dismiss()
class Dashboard(Screen):
    current_time = StringProperty()
    def count_users(self):
        users_col = firestoredb.insurance_all_users()
        total = len(users_col)
        return str(total)
    def count_claims(self):
        claims_col = firestoredb.get_all_claims()
        total = len(claims_col)
        return str(total)
    def date_today(self):
        today = datetime.now().date()
        return str(today)
class Claims(Screen):
    reports = []
    def on_pre_enter(self):
        claims = firestoredb.get_all_claims()
        claims_list = self.ids.pending
        claims_list.clear_widgets()
        approved_list = self.ids.validated
        approved_list.clear_widgets()
        ph_tz = pytz.timezone('Asia/Manila')
        for claim in claims:
            claimant_text = "Claimant: " + str(claim['Assured_Name'])
            claim_id_text = "Claim ID: " + str(claim['Assured_UID'])
            insured_veh = "Policy No.: " + str(claim['InsuredVeh_policy_no'])
            if claim['Status'] == "Pending":
                item = ThreeLineRightIconListItem(text=claimant_text, secondary_text=claim_id_text, tertiary_text=insured_veh)
                item.add_widget(IconRightWidget(icon="chevron-right"))
                item.bind(on_release=lambda x, claim_id=claim['id']: self.on_select(claim_id))
                claims_list.add_widget(item)
            elif claim['Status'] == "Approved":
                item = ThreeLineRightIconListItem(text=claimant_text, secondary_text=claim_id_text, tertiary_text=insured_veh)
                approved_list.add_widget(item)
    def on_select(self, claim_id):
        app = MDApp.get_running_app()
        app.root.current = 'claimDetails'
        app.root.get_screen('claimDetails').claim_details(claim_id)
    def back(self, button):
        self.manager.transition.direction='right'
        self.manager.current = "dashboard"
        
class ClaimDetails(Screen):
    def __init__(self, **kwargs):
        super(ClaimDetails, self).__init__(**kwargs)
        self.claim_data = {}
        self.claim_id = None
    def claim_details(self, claim_id):
        self.claim_id = claim_id
        self.claim_data = firestoredb.get_claim_details(claim_id)
        self.claim_labels()
    def claim_labels(self):
        ph_tz = pytz.timezone('Asia/Manila')
        claimant_label = self.ids.claimant_label
        license_no = self.ids.license_no
        address = self.ids.address
        # contact = self.ids.contact
        policy_no = self.ids.policy_no
        vehicle_type = self.ids.vehicle_type
        file_no = self.ids.file_no
        plate_no = self.ids.plate_no
        engine_no = self.ids.engine_no
        chassis_no = self.ids.chassis_no
        model = self.ids.model
        year = self.ids.year
        body_type = self.ids.body_type
        color = self.ids.color
        title = self.ids.title
        estimator = self.ids.estimator
        date_est = self.ids.date_est
        time_est = self.ids.time_est
        submitted_at = self.ids.submitted_at
        submitted_on = self.ids.submitted_on
        
        title.title = self.claim_data.get('Assured_Name', '')
        claimant_label.text = self.claim_data.get('Assured_Name', '')
        license_no.text = self.claim_data.get('Assured_License_No','')
        address.text = self.claim_data.get('Assured_Address','')
        # contact.text = self.claim_data.get('Assured_Contact')
        policy_no.text = self.claim_data.get('InsuredVeh_policy_no','')
        vehicle_type.text = self.claim_data.get('InsuredVeh_vehicle_type','')
        file_no.text = self.claim_data.get('InsuredVeh_file_no','')
        plate_no.text = self.claim_data.get('InsuredVeh_plate_no','')
        engine_no.text = self.claim_data.get('InsuredVeh_engine_no','')
        chassis_no.text = self.claim_data.get('InsuredVeh_chassis_no','')
        model.text = self.claim_data.get('InsuredVeh_model','')
        year.text = self.claim_data.get('InsuredVeh_year','')
        body_type.text = self.claim_data.get('InsuredVeh_body_type','')
        color.text = self.claim_data.get('InsuredVeh_color','')
        estimator.text = self.claim_data.get('estimator')
        date_est.text = self.claim_data.get('Date_Estimated')
        time_est.text = self.claim_data.get('Time_Estimated')
        submitted_at.text = self.claim_data.get('Submitted_at')
        submitted_on.text = self.claim_data.get('Submitted_on')
        image_urls = self.claim_data.get('ImgRef')
        panels = self.claim_data.get('PanelsPart')
        costs = self.claim_data.get('Costs')
        total_cost = 0
        for cost in costs:
            total_cost += float(cost)
        self.ids.img_container.clear_widgets()
        for index,(url, panel, cost) in enumerate (zip(image_urls, panels, costs)):
            image_item = AsyncImage(source=url, size_hint=(1, None), size=("200dp", "200dp"))
            panels = MDLabel(
                text=panel,
                font_style="Button",
                disabled=True
                )
            costs = MDTextField(
                text=str(cost),
                disabled=True,
                icon_left='currency-php'
                )
            self.ids.img_container.add_widget(image_item)
            self.ids.img_container.add_widget(panels)
            self.ids.img_container.add_widget(costs)
        # Display total cost
        total_item = TwoLineIconListItem(
            text="Total Cost",
            font_style="H6",
            secondary_text=str(total_cost),
            pos_hint={"center_y": .5},
            _no_ripple_effect=True)
        total_item.add_widget(IconLeftWidget(icon="currency-php"))
        self.ids.img_container.add_widget(total_item)
    def approve(self):
        # Retrieve the claim by ID
        claim_ref = firestoredb.db.collection('claims').document(self.claim_id)
        claim = claim_ref.get().to_dict()
        insurance_estimator = self.ids.insurance_estimator.text
        # Update the approved value for the claim
        claim['Status'] = "Approved"
        claim['validated'] = insurance_estimator
        # Save the updated claim to the database
        claim_ref.set(claim)
        self.show_snackbar("Claim Approved")
        self.manager.transition.direction='right'
        self.manager.current = "claims"
        
    def show_snackbar(self, text):
        snackbar = Snackbar(text=text, duration=2.5)
        snackbar.open()
        
    def back(self, button):
        self.manager.transition.direction='right'
        self.manager.current = "claims"
class AdminApp(MDApp):
    def build(self):
        self.title = "Insurance"
        global screen_manager
        screen_manager = Factory.ScreenManager()
        screen_manager.add_widget(Builder.load_file("splashscreen.kv"))
        screen_manager.add_widget(AdminLogin(name='adminLogin'))
        screen_manager.add_widget(Dashboard(name='dashboard'))
        screen_manager.add_widget(Claims(name='claims'))
        screen_manager.add_widget(ClaimDetails(name='claimDetails'))
        self.theme_cls.theme_style = "Light"
        return screen_manager
    def on_start(self):
        Clock.schedule_once(self.login, 8)
    def login(self, *args):
        screen_manager.current = "adminLogin"
    def back(self, button):
        screen_manager.transition.direction='right'
        screen_manager.current = "dashboard"
    def logout(self):
        screen_manager.get_screen('adminLogin').ids.email.text = ''
        screen_manager.get_screen('adminLogin').ids.password.text = ''
        screen_manager.current='adminLogin'
if __name__ == "__main__":
    AdminApp().run()
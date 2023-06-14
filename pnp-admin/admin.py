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
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.imagelist import *

sys.path.append('imports')
from datetime import datetime

import firebaseauth
import firestoredb
import pytz

import random
import string

Window.size = (350, 630)
Builder.load_file("pnplogin.kv")
Builder.load_file("dashboard.kv")
Builder.load_file("accounts.kv")
Builder.load_file("reports.kv")
Builder.load_file("reportDetails.kv")
class AdminLogin(Screen):
    def verify_admin(self):
        email = self.ids.email.text
        password = self.ids.password.text
        try:
            user = firebaseauth.auth.sign_in_with_email_and_password(email, password)
            self.manager.current='dashboard'
        except:
            self.show_error_dialog()
            self.manager.current='dashboard'

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
class Reports(Screen):
    def count_reports(self):
        reports_col = firestoredb.get_reports()
        total = len(reports_col)
        return str(total)
    def approved_reports(self):
        reports_col = firestoredb.get_approved_reports_pnp()
        total = len(reports_col)
        return str(total)
    def on_pre_enter(self):
        reports = firestoredb.get_all_reports()
        reports_list = self.ids.pending
        reports_list.clear_widgets()
        approved_list = self.ids.approved_report
        approved_list.clear_widgets()
        ph_tz = pytz.timezone('Asia/Manila')
        for report in reports:
            name_text = "Name: " + str(report['Driver_Name'])
            report_id_text = "Report ID: " + str(report['report_sender'])
            date_text = "Time: " + str(report['Time'])
            if report['status'] == "Pending":
                item = ThreeLineRightIconListItem(text=name_text, secondary_text=report_id_text, tertiary_text=date_text)
                item.add_widget(IconRightWidget(icon="chevron-right"))
                item.bind(on_release=lambda x, report_id=report['id']: self.on_select(report_id))
                reports_list.add_widget(item)
            elif report['status'] == "PNP_Approved":
                item = ThreeLineRightIconListItem(text=name_text, secondary_text=report_id_text, tertiary_text=date_text)
                approved_list.add_widget(item)
    def on_select(self, report_id):
        app = MDApp.get_running_app()
        app.root.current = 'reportDetails'
        screen_manager.transition.direction='left'
        app.root.get_screen('reportDetails').report_details(report_id)

class InformationTab(MDBoxLayout, MDTabsBase):
    pass

class ImageTab(MDBoxLayout, MDTabsBase):
    pass


class ReportDetails(Screen):
    def __init__(self, **kwargs):
        super(ReportDetails, self).__init__(**kwargs)
        self.report_data = {}
        self.report_id = None
    
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        tab_name = tab_text.split(" ")[-1]

        container = self.ids.ImgContainer
        container.clear_widgets()

        for img,panel in zip(self.report_data.get('ImgRef',''),self.report_data.get('PanelsPart','')):
            mytile = MDSmartTile(
                id="tile",
                radius=24,
                source=img,
                box_radius = [0, 0, 24, 24],
                box_color = [1, 1, 1, .2],
                pos_hint = {"center_x": .5, "center_y": .5},
                size_hint = (1,None),
                size = ("150dp", "150dp"),
            )
            mytile.add_widget(OneLineListItem(
                text=panel,
                pos_hint= {"center_y": .5},
                _no_ripple_effect = True,
                text_color = '#ffffff'
                ))
            container.add_widget(mytile)

    def report_details(self, report_id):
        self.report_id = report_id
        self.report_data = firestoredb.get_report_details(report_id)
        self.report_labels()
    def report_labels(self):
        ph_tz = pytz.timezone('Asia/Manila')
        self.ids.date_label.secondary_text=self.report_data.get('Date', '')
        self.ids.time_label.secondary_text=self.report_data.get('Time', '')
        self.ids.sender_label.secondary_text=self.report_data.get('report_sender', '')
        self.ids.location_label.secondary_text=self.report_data.get('Location', '')
        self.ids.status_label.secondary_text=self.report_data.get('status', '')
        
        #driver
        self.ids.name_label.secondary_text=self.report_data.get('Driver_Name', '')
        self.ids.daddress_label.secondary_text=self.report_data.get('Driver_Address', '')
        self.ids.age_label.secondary_text=self.report_data.get('Driver_Age', '')
        self.ids.gender_label.secondary_text=self.report_data.get('Driver_Gender', '')
        self.ids.licence_label.secondary_text=self.report_data.get('Driver_License', '')
        self.ids.vehicle_label.secondary_text=self.report_data.get('Vehicle', '')
        self.ids.plate_label.secondary_text=self.report_data.get('Plate_number', '')

        #witness
        self.ids.wname_label.secondary_text=self.report_data.get('Witness_Name', '')
        self.ids.waddress_label.secondary_text=self.report_data.get('Witness_Address', '')
        self.ids.wage_label.secondary_text=self.report_data.get('Witness_Age', '')
        self.ids.wgender_label.secondary_text=self.report_data.get('Witness_Gender', '')
        
    def approve(self):
        # Retrieve the report by ID
        report_ref = firestoredb.db.collection('reports').document(self.report_id)
        report = report_ref.get().to_dict()

        # Update the approved value for the report
        report['status'] = "PNP_Approved"

        # Save the updated report to the database
        report_ref.set(report)
        self.show_snackbar("Report Approved")
        self.manager.transition.direction='right'
        self.manager.current = "reports"
    def show_snackbar(self, text):
        snackbar = Snackbar(text=text, duration=2.5)
        snackbar.open()
        
    def back(self, button):
        self.manager.transition.direction='right'
        self.manager.current = "reports"
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
class ContentNavigationDrawer(MDBoxLayout):
    sm = ObjectProperty()
    nav_drawer = ObjectProperty()
class PNP(MDApp):
    def build(self):
        self.title = "PNP"
        global screen_manager
        screen_manager = Factory.ScreenManager()
        screen_manager.add_widget(AdminLogin(name='adminLogin'))
        screen_manager.add_widget(Dashboard(name='dashboard'))
        screen_manager.add_widget(Reports(name='reports'))
        screen_manager.add_widget(ReportDetails(name='reportDetails'))
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
PNP().run()
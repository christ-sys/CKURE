import sys
import os
import pytz

from kivy.properties import *

from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import *
from kivymd.uix.button import *
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager

sys.path.append('./imports')
import firebaseauth
import firestoredb


Window.size = (350, 630)
Builder.load_file("casalogin.kv")
Builder.load_file("pnpReport.kv")
Builder.load_file("reportDetails.kv")

# ReportDetails

class Content(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        repairlst=['Repair', 'Replacement']

        repairType= [
             {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.repairType_callBack(x),
            } for i in repairlst
        ]

        self.repairMenu = MDDropdownMenu(
            caller=self.ids.rtype,
            items=repairType,
            width_mult=4,
            position="center"
        )

    def repairType_callBack(self,item):
        self.ids.rtype.text=item

class ReportDetails(Screen):
    dialog = None
    def __init__(self, **kwargs):
        super(ReportDetails, self).__init__(**kwargs)
        self.report_data = {}
        self.report_id = None

    def report_details(self, report_id):
        self.report_id = report_id
        self.report_data = firestoredb.get_report_details(report_id)
        self.report_labels()
    def report_labels(self):
        ph_tz = pytz.timezone('Asia/Manila')
        name_label = self.ids.name_label
        time_label = self.ids.time_label
        title = self.ids.title
        title.title = self.report_data.get('Name', '')
        name_label.secondary_text = self.report_data.get('Name', '')
        time_label.secondary_text = self.report_data.get('Time', '')
    
    def estimated_cost(self,labor, replace):
        sum = int(labor) + int(replace)
        return sum
        

    def show_confirmation_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Estimations",
                type="custom",
                content_cls=Content(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        # text_color=self.theme_cls.primary_color,
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        on_release=self.ok_dialog
                        # text_color=self.theme_cls.primary_color,
                    ),
                ],
            )
        self.dialog.open()

    def ok_dialog(self, *args):
        # self.dialog.dismiss()
        lcost = self.dialog.content_cls.ids.lcost.text
        rcost = self.dialog.content_cls.ids.rcost.text
        amount = self.estimated_cost(lcost,rcost)
        self.ids.pricing.secondary_text = "Php.{}".format(amount)
        self.dialog.dismiss()

    def back(self, button):
        self.manager.transition.direction='right'
        self.manager.current = "pnpreports"
# ============================================
# =================HOME PAGE=================
class PnpReports(Screen):
    def count_reports(self):
        reports_col = firestoredb.get_reports()
        total = len(reports_col)
        return str(total)
    def approved_reports(self):
        reports_col = firestoredb.get_approved_reports()
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
            name_text = "Name: " + str(report['Name'])
            report_id_text = "Report ID: " + str(report['id'])
            date_text = "Time: " + str(report['Time'])
            if report['Status'] == "Pending":
                item = ThreeLineRightIconListItem(text=name_text, secondary_text=report_id_text, tertiary_text=date_text)
                item.add_widget(IconRightWidget(icon="chevron-right"))
                item.bind(on_release=lambda x, report_id=report['id']: self.on_select(report_id))
                reports_list.add_widget(item)
            elif report['Status'] == "Approved":
                item = ThreeLineRightIconListItem(text=name_text, secondary_text=report_id_text, tertiary_text=date_text)
                approved_list.add_widget(item)

    def on_select(self, report_id):
        app = MDApp.get_running_app()
        app.root.current = 'reportDetails'
        app.root.get_screen('reportDetails').report_details(report_id)
        self.manager.transition.direction='left'


# ============================================
# =================LOGIN PAGE=================
class CasaLogin(Screen):
    email = 'ckure.org@mail.com'
    password='password123'
    
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
            CasaLogin.email = email
            self.manager.current='dashboard'
        except Exception as e: 
            Snackbar(
                text="Invalid Credentials",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(Window.width - (10 * 2)) / Window.width
            ).open()

# ============================================
# =================MENU DRAWER PAGE=================
class ContentNavigationDrawer(MDBoxLayout):
    sm = ObjectProperty()
    nav_drawer = ObjectProperty()

# ============================================
# =================MAIN CLASS=================
class AdminApp(MDApp):
    def build(self):
        self.title = "NISSAN"
        global screen_manager
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("splashscreen.kv"))
        screen_manager.add_widget(CasaLogin(name='casaLogin'))
        screen_manager.add_widget(PnpReports(name='pnpreports'))
        screen_manager.add_widget(ReportDetails(name='reportDetails'))
        self.theme_cls.theme_style = "Light"
        return screen_manager
    







    def on_start(self):
        Clock.schedule_once(self.login, 5)
    def login(self, *args):
        screen_manager.current = "pnpreports"
    

    # AUTO RELOAD
    AUTORELOADER_PATHS = [
        (".",{"recursive": True})
    ]
AdminApp().run()
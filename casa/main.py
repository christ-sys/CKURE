from sqlite3 import dbapi2
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
from kivymd.uix.imagelist import *
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.tab import MDTabsBase


from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager

# from main import CustomCard

sys.path.append('./imports')
import firebaseauth
import firestoredb


Window.size = (350, 630)
Builder.load_file("casalogin.kv")
Builder.load_file("casaReport.kv")
Builder.load_file("reportDetails.kv")

# ReportDetails
class InformationTab(MDBoxLayout, MDTabsBase):
    pass

class ImageTab(MDBoxLayout, MDTabsBase):
    pass

class Content(BoxLayout):
    index = 0
    amount = 0
    costs = []
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
        

        if item=="Repair":
            self.ids.rcost.text="N/A"
        else:
            self.ids.rcost.text="0"


class CustomCard(MDCard):
    pass

class ReportDetails(Screen):
    dialog = None
    def __init__(self, **kwargs):
        super(ReportDetails, self).__init__(**kwargs)
        self.report_data = {}
        self.report_id = None

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        container = self.ids.SmartTilecontainer
        container.clear_widgets()
        costs = self.report_data.get('Costs',0)
        amount=0
        for item in costs:
            amount+=int(item)

        priceCard = CustomCard()
        box=MDBoxLayout(orientation='vertical')
        amount = "{:,.2f}".format(amount)
        priceLabel = MDLabel(font_size='18dp',bold=True, text= "Estimated Total Cost \n Php. {}".format(str(amount)),theme_text_color="Custom", text_color="white",halign="center")
        box.add_widget(priceLabel)
        priceCard.add_widget(box)
        container.add_widget(priceCard)
        

        for index,(img,panel,cost) in enumerate(zip(self.report_data.get('ImgRef',''),self.report_data.get('PanelsPart',''), self.report_data.get('Costs',''))):
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
            mytile.add_widget(TwoLineListItem(
                text=panel,
                secondary_text = str(cost),
                pos_hint= {"center_y": .5},
                _no_ripple_effect = True,
                text_color = '#ffffff',
                secondary_text_color = '#808080'
                ))
            mytile.bind(on_release=lambda *args, idx=index: self.show_confirmation_dialog(idx))
            container.add_widget(mytile)
    def report_details(self, report_id):
        self.report_id = report_id
        self.report_data = firestoredb.get_report_details(report_id)
        self.report_labels()

    def report_labels(self):
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
        

        

            
    def show_confirmation_dialog(self, index, *args):
        myidx=index
        Content.index = index
        if not self.dialog:
            self.dialog = MDDialog(
                title="Estimations",
                type="custom",
                content_cls=Content(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        on_release=lambda *args:self.dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        on_release=lambda *args,idx=myidx: self.ok_dialog(idx)
                    ),
                ],
            )
        self.dialog.open()
    
    def ok_dialog(self, indx):
        indx = Content.index
        hours = self.dialog.content_cls.ids.lcost.text
        rcost = self.dialog.content_cls.ids.rcost.text
        type = self.dialog.content_cls.ids.rtype.text

        amount = self.estimated_cost(type,hours,rcost)
        Content.amount+=amount
        myrecord_ref = firestoredb.db.collection('reports').document(self.report_id).get()
        myrecord =myrecord_ref.to_dict()
        costs = myrecord['Costs']
        costs[indx]= amount
        firestoredb.updateItemCost(costs,self.report_id)
        # self.ids.pricing.text =  "Estimated Total Cost \n Php. {}.00".format(str(Content.amount)) 
        self.dialog.dismiss()
        self.report_details(self.report_id)
        tab2 = self.ids.tabs.get_tab_list()[0]
        self.ids.tabs.switch_tab(tab2)

    def estimated_cost(self,type,hours,replace):
        x = 4500
        y = 5500
        labor = 560 * int(hours)
        sum = x + y + labor
        if type=="Replacement":
            sum+=int(replace)
        return sum
        
    def submit_Estimation(self):
        # Retrieve the report by ID
        report_ref = firestoredb.db.collection('reports').document(self.report_id)
        report = report_ref.get().to_dict()

        # Update the approved value for the report
        report['status'] = "CASA_Approved"

        # Save the updated report to the database
        report_ref.set(report)


    
        

    def back(self, button):
        self.manager.transition.direction='right'
        self.manager.current = "casa_reports"
        
        Content.index = 0
        Content.amount = 0
        Content.costs = []
        

# ============================================
# =================HOME PAGE=================
class CasaReports(Screen):
    def count_reports(self):
        reports_col = firestoredb.getReport_CASA()
        total = len(reports_col)
        return str(total)
    def approved_reports(self):
        reports_col = firestoredb.get_approved_reports_casa()
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
            if report['status'] == "PNP_Approved":
                item = ThreeLineRightIconListItem(text=name_text, secondary_text=report_id_text, tertiary_text=date_text)
                item.add_widget(IconRightWidget(icon="chevron-right"))
                item.bind(on_release=lambda x, report_id=report['id']: self.on_select(report_id))
                reports_list.add_widget(item)
            elif report['status'] == "CASA_Approved":
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
        screen_manager.add_widget(CasaReports(name='casa_reports'))
        screen_manager.add_widget(ReportDetails(name='reportDetails'))
        self.theme_cls.theme_style = "Light"
        return screen_manager
    


    def on_start(self):
        Clock.schedule_once(self.login, 5)
    def login(self, *args):
        screen_manager.current = "casa_reports"
    

    # AUTO RELOAD
    AUTORELOADER_PATHS = [
        (".",{"recursive": True})
    ]
AdminApp().run()
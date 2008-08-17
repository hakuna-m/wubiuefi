import ui
from wizard import Wizard

class Page1(Wizard.Page):
    def on_init(self):
        self.add_navigation_buttons()
        self.button1 = ui.Button(self, 0 , 0, 100, 100, text="ok")
        self.button2 = ui.DefaultButton(self, 10 , 200, 100, 100, text="cancel")
        self.button2.on_click = self.button2_click
        self.button2.set_text("hola")

    def button2_click(self):
        self.hide()
        self.application.show_next_page()

class Page2(Wizard.Page):
    def on_init(self):
        self.add_navigation_buttons()
        self.bitmap = ui.Bitmap(self, 0, 0, 300, 300, "bm")
        self.cb1 = ui.ComboBox(self, 0 , 0, 100, 100)
        self.pb = ui.ProgressBar(self, 10, 100, 200, 20)
        self.edit2 = ui.Edit(self, 10 , 200, 100, 20)
        self.button3 = ui.DefaultButton(self, 10 , 300, 100, 20, "back")
        self.button3.on_click = self.on_click
        self.button4 = ui.DefaultButton(self, 10 , 320, 100, 20, "step")
        self.button4.on_click = self.pb.step
        self.pb.set_position(50)
        self.cb1.add_item("item1")
        self.cb1.add_item("item2")
        self.g = ui.GroupBox(self,200,200,200,200,"hola group")
        self.check1 = ui.RadioButton(self, 210, 230, 100, 20, "check")
        self.check2 = ui.RadioButton(self, 210, 260, 100, 20, "me")
        self.check1.on_click = self.is_checked
        self.check2.on_click = self.is_checked
        self.bitmap.set_image(r"c:\path\to\bmp")
        self.pb.on_change = self.pb_change
        self.pbpos = ui.Label(self, 110, 100, 200, 20, "pos")

    def pb_change(self):
        pos = self.pb.get_position()
        self.pbpos.set_text(str(pos))

    def is_checked(self):
        print self.check2.is_checked()

    def on_click(self):
        self.hide()
        self.application.show_previous_page()

class Page3(Wizard.Page):
    def on_init(self):
        self.add_navigation_buttons()
        self.tabs = ui.Tab(self, 10, 10, 300, 300, "tabs")
        self.tab1 = ui.Panel(self.tabs,30, 30, 250, 250)
        self.tabs.add_item("hola", self.tab1, 0)
        self.tab2 = ui.Panel(self.tabs,30, 30, 240, 240)
        self.tabs.add_item("aaa", self.tab2, 0)

class HelloWorld(ui.MainDialogWindow):
    def on_init(self):
        self.label = ui.Label(self, 50, 80, 100, 20, "Hello World")

#~ ui.set_frontend()
wizard = Wizard(text="Wizard example", width=600, height=400)
wizard.add_page(Page1)
wizard.add_page(Page2)
wizard.add_page(Page3)
wizard.show_page(0)
wizard.run()
#~ application = ui.Application(Page3, width=200, height=200, text="Hello hello")
#~ application.run()


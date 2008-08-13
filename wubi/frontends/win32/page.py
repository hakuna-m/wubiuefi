from lib.winui import ui
import os
import logging
log = logging.getLogger("WinuiPage")


class Page(ui.Page):
    '''
    Base Page class
    Adds some handy methods
    '''

    def on_init(self):
        x, y, width, height = self.parent.get_client_rect()
        self.resize(width, height)
        self.width = width
        self.height = height

    def insert_header(self, title, subtitle, bmp_file):
        '''
        Inserts a header with image, title and subtitle
        '''
        hbh = 57
        hbw = 150
        self.header = ui.Panel(
            self,
            0, 0 , self.width, hbh)
        if bmp_file:
            self.header.image = ui.Bitmap(
                self.header,
                0, 0, hbw, hbh)
            self.header.image.set_image(
                os.path.join(self.application.info.imagedir, bmp_file))
        if title:
            self.header.title = ui.Label(
                self.header,
                hbw + 20, 10, self.width - 200, 20,
                text = title)
        if subtitle:
            self.header.subtitle = ui.Label(
                self.header,
                hbw + 20, 30, self.width - 200, 20,
                text = subtitle)
        self.header.height = hbh

    def insert_main(self):
        '''
        Panel containing client widgets
        '''
        top = 0
        height = self.height
        if hasattr(self, "header"):
            top += self.header.height
            height -= self.header.height
        elif hasattr(self, "navigation"):
            height -= self.navigation.height
        self.main = ui.Panel(
            self,
            0, top, self.width, height)
        log.debug(str((0, top, self.width, height)))
        self.main.height = height

    def insert_navigation(self, button1_text=None, button2_text=None, button3_text=None, default=None):
        '''
        Inserts navigation buttons starting from the leftmost button
        '''
        nbw = 100
        nbh = 24
        self.navigation = ui.Panel(
            self,
            0, self.height - nbh - 20, self.width, nbh + 20)

        for i,text in enumerate((button1_text, button2_text, button3_text)):
            if not text: continue
            if default and i + 1 == default:
                Button = ui.DefaultButton
            else:
                Button = ui.Button
            n = 0
            for other in (button1_text, button2_text, button3_text)[i:]:
                if other:
                    n += 1
            button = Button(
                self.navigation,
                self.width -(nbw + 10) * n, 10, nbw, nbh,
                text=text)
            setattr(self.navigation, "button%s" % ( i + 1), button)
            self.navigation.height = nbh + 20

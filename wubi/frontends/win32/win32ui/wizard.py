#
# Copyright (c) 2007, 2008 Agostino Russo
#
# Written by Agostino Russo <agostino.russo@gmail.com>
# Mostly copied from win32con.py
#
# win32.ui is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or (at your option) any later version.
#
# win32.ui is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# DESCRIPTION: 
# wizard dialog class
#


import ui

class Wizard(ui.Application):
    _main_window_class_ = ui.MainDialogWindow
    
    def on_init(self):
        self.current_page_index = 0
        self.pages = []
    
    def add_page(self, page_class):
        crect = self.main_window.get_client_rect()
        self.pages.append(page_class(self.main_window, *crect))
    
    def cancel(self):
        if self.ask_confirmation("Are you sure you want to quit?", "Quitting"):
            self.quit()
    
    def show_page(self, page_index):
        if self.current_page_index == page_index:
            self.pages[page_index].show()
            return
        page_index = min(page_index, len(self.pages) -1)
        page_index = max(page_index, 0)
        old_page = self.pages[self.current_page_index]
        old_page.hide()
        new_page = self.pages[page_index]
        self.current_page_index = page_index
        new_page.show()
    
    def show_previous_page(self):
        self.show_page(self.current_page_index - 1)
        
    def show_next_page(self):
        self.show_page(self.current_page_index + 1)
    
    class Page(ui.Page):
        def add_navigation_buttons(self):
            x, y, width, height = self.get_client_rect()
            self.button_cancel = ui.Button(self, width - 100 , height - 34, 90, 24, text="cancel")
            self.button_next = ui.DefaultButton(self, width - 210 , height - 34, 90, 24, text="next >>")
            self.button_back = ui.Button(self, width - 310 , height - 34, 90, 24, text="<< back")
            self.button_next.on_click = self.application.show_next_page
            self.button_back.on_click = self.application.show_previous_page
            self.button_cancel.on_click = self.application.cancel

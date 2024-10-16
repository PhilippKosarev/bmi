# window.py
#
# Copyright 2024 philipp
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# SPDX-License-Identifier: GPL-2.0-or-later

from gi.repository import Adw, Gtk, Gdk, Gio

class BmiWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'BmiWindow'

    label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load GSettings and connect to the action after closing the app window
        self.settings = Gio.Settings.new_with_path("io.github.philippkosarev.bmi", "/io.github.philippkosarev.bmi/")
        self.connect("close-request", self.on_close_window)
        
        # Basic window properties
        self.set_title("BMI")
        self.set_default_size(0, 230)
        self.set_resizable(False)

        # Window structure
        self.content = Adw.ToolbarView()
        self.set_content(self.content)

        # Headerbar
        self.header = Adw.HeaderBar()
        self.content.add_top_bar(self.header)

        self.about_button = Gtk.Button()
        self.about_button.set_tooltip_text("Show About")
        self.about_button.set_icon_name("help-about-symbolic")
        self.about_button.connect('clicked', self.show_about)
        self.header.pack_start(self.about_button)

        self.separator = Gtk.Separator()
        self.header.pack_start(self.separator)

        self.forget_button = Gtk.ToggleButton()
        self.forget_button.set_icon_name("user-trash-full-symbolic")
        self.forget_button.set_tooltip_text("Forget values on close")
        self.forget_button.set_active(self.settings["forget"])
        self.header.pack_start(self.forget_button)

        # Main box
        self.drag = Gtk.WindowHandle()
        self.content.set_content(self.drag)
        self.toast_overlay = Adw.ToastOverlay()
        self.drag.set_child(self.toast_overlay)
        self.main_box = Gtk.Box(valign=Gtk.Align.START, spacing=12)
        self.main_box.set_margin_start(16)
        self.main_box.set_margin_end(30)
        self.toast_overlay.set_child(self.main_box)

        # User inputs
        self.left_page = Adw.PreferencesPage(halign=Gtk.Align.FILL, valign=Gtk.Align.CENTER)
        self.left_page.set_hexpand(True)
        self.left_page.set_vexpand(True)
        self.left_page.set_size_request(270, 0)
        self.main_box.append(self.left_page)

        self.left_group = Adw.PreferencesGroup()
        self.left_page.add(self.left_group)

        self.height_adjustment = Adw.SpinRow()
        self.height_adjustment.set_title("CM")
        self.height_adjustment.set_digits(1)
        adjustment = Gtk.Adjustment(lower= 50, upper=267, step_increment=1, page_increment=10, value=self.settings["height"])
        self.height_adjustment.set_adjustment(adjustment)
        self.height_adjustment.connect('changed', self.on_value_changed)
        self.left_group.add(self.height_adjustment)

        self.weight_adjustment = Adw.SpinRow()
        self.weight_adjustment.set_title("KG")
        self.weight_adjustment.set_digits(1)
        adjustment = Gtk.Adjustment(lower= 10, upper=650, step_increment=1, page_increment=10, value=self.settings["weight"])
        self.weight_adjustment.set_adjustment(adjustment)
        self.weight_adjustment.connect('changed', self.on_value_changed)
        self.left_group.add(self.weight_adjustment)

        # Icon
        self.center_box = Gtk.Box(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        self.main_box.append(self.center_box)
        self.icon = Gtk.Image()
        self.icon.set_from_icon_name("go-next-symbolic")
        self.icon.set_pixel_size(42)
        self.center_box.append(self.icon)

        # Results
        self.right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, spacing=6)
        self.right_box.set_hexpand(True)
        self.right_box.set_vexpand(True)
        self.right_box.set_size_request(175, 0)
        self.main_box.append(self.right_box)

        self.result_label = Gtk.Label()
        self.result_label.set_css_classes(["title-2"])
        self.result_label.set_label("BMI:")
        self.right_box.append(self.result_label)

        self.result_button = Gtk.Button(halign=Gtk.Align.CENTER)
        self.result_button.set_tooltip_text("Copy BMI")
        self.result_button.set_css_classes(["pill", "title-1"])
        self.result_button.connect('clicked', self.on_result_button_pressed)
        self.result_button.set_size_request(100, 0)
        self.right_box.append(self.result_button)

        self.result_feedback_label = Gtk.Label()
        self.right_box.append(self.result_feedback_label)

        self.on_value_changed(self)
    
    # Action after clicking on the button that shows the BMI result
    def on_result_button_pressed(self, _button):
        clipboard = Gdk.Display.get_default().get_clipboard()
        Gdk.Clipboard.set(clipboard, self.bmi);
        self.toast = Adw.Toast()
        self.toast.set_title("Result copied")
        self.toast.set_timeout(1)
        self.toast_overlay.add_toast(self.toast)

    def calc_bmi(self):
        self.bmi = self.height_adjustment.get_value() / 100 # converting cm to meters
        self.bmi = self.bmi ** 2
        self.bmi = self.weight_adjustment.get_value() / self.bmi
    
    # Action after changed values of self.height_adjustment and self.width_adjustment
    def on_value_changed(self, _scroll):
        self.calc_bmi()
        print(self.bmi)
        self.result_button.set_label(str(int(self.bmi)))
        if self.bmi < 18:
            self.result_feedback_label.set_css_classes(["title-2", "accent"])
            self.result_feedback_label.set_label("Underweight")
        if self.bmi >= 18:
            self.result_feedback_label.set_css_classes(["title-2", "success"])
            self.result_feedback_label.set_label("Healthy")
        if self.bmi >= 25:
            self.result_feedback_label.set_css_classes(["title-2", "warning"])
            self.result_feedback_label.set_label("Overweight")
        if self.bmi >= 30:
            self.result_feedback_label.set_css_classes(["title-2", "error"])
            self.result_feedback_label.set_label("Obese")
        if self.bmi >= 40:
            self.result_feedback_label.set_css_classes(["title-2"])
            self.result_feedback_label.set_label("Extremely obese")

        self.height_adjustment.set_title("CM")
        self.weight_adjustment.set_title("KG")
        if self.height_adjustment.get_value() == 267:
            self.height_adjustment.set_title("Robert Wadlow")
        if self.weight_adjustment.get_value() == 650:
            self.weight_adjustment.set_title("Jon Brower Minnoch")
    
    # Show the About app dialog
    def show_about(self, _button):
        self.about = Adw.AboutWindow(application_name='BMI',
                                application_icon='io.github.philippkosarev.bmi',
                                developer_name='Philipp Kosarev',
                                version='v1.4',
                                developers=['Philipp Kosarev'],
                                artists=['Philipp Kosarev'],
                                copyright='© 2024 Philipp Kosarev',
                                license_type="GTK_LICENSE_GPL_2_0",
                                website="https://github.com/philippkosarev/bmi",
                                issue_url="https://github.com/philippkosarev/bmi/issues")
        self.about.present()
        
    # Action after closing the app window
    def on_close_window(self, widget, *args):
        if self.forget_button.get_active() == True:
            self.settings["height"] = 175
            self.settings["weight"] = 65
        else:
            self.settings["height"] = self.height_adjustment.get_value()
            self.settings["weight"] = self.weight_adjustment.get_value()
        self.settings["forget"] = self.forget_button.get_active()

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
import math

class BmiWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'BmiWindow'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_finished = False

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
        self.header.pack_end(self.about_button)

        self.mode_dropdown = Gtk.DropDown()
        modes_list = Gtk.StringList()
        modes = ["BMI (Basic)", "BMI (Advanced)"]
        for mode in modes:
            modes_list.append(mode)
        self.mode_dropdown.set_model(modes_list)
        self.mode_dropdown.connect('notify::selected-item', self.on_dropdown_value_changed)
        self.mode_dropdown.get_first_child().set_css_classes(["flat"])
        self.mode_dropdown.set_selected(self.settings["mode"])
        # self.header.pack_start(self.mode_dropdown)
        self.header.set_title_widget(self.mode_dropdown)

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
        self.main_box.set_margin_end(16)
        self.toast_overlay.set_child(self.main_box)

        # User inputs
        self.inputs_page = Adw.PreferencesPage(halign=Gtk.Align.FILL, valign=Gtk.Align.START)
        self.inputs_page.set_hexpand(True)
        self.inputs_page.set_vexpand(True)
        self.inputs_page.set_size_request(270, 0)
        self.main_box.append(self.inputs_page)

        self.inputs_group = Adw.PreferencesGroup(title="Inputs")
        self.inputs_page.add(self.inputs_group)

        self.adjustment = Gtk.Adjustment(lower= 50, upper=267, step_increment=1, page_increment=10, value=self.settings["height"])
        self.create_input_row("height_adjustment", "Height", self.adjustment, "Height in centimetres", False)

        self.adjustment = Gtk.Adjustment(lower= 10, upper=650, step_increment=1, page_increment=10, value=self.settings["weight"])
        self.create_input_row("weight_adjustment", "Waist", self.adjustment, "Weight in kilograms", False)

        # Advanced user inputs
        self.advanced_inputs_page = Adw.PreferencesPage(halign=Gtk.Align.FILL, valign=Gtk.Align.START)
        self.advanced_inputs_page.set_hexpand(True)
        self.advanced_inputs_page.set_vexpand(True)
        self.advanced_inputs_page.set_size_request(270, 0)
        self.main_box.append(self.advanced_inputs_page)

        self.advanced_inputs_group = Adw.PreferencesGroup(title="Advanced inputs")
        self.advanced_inputs_page.add(self.advanced_inputs_group)

        self.gender_adjustment = Adw.ComboRow(title="Gender")
        self.gender_adjustment.connect('notify::selected-item', self.on_dropdown_value_changed)
        self.gender_adjustment.set_tooltip_text("Affects healthy/unhealthy thresholds for Waist to Hip ratio")
        gender_list = Gtk.StringList()
        self.gender_adjustment.set_model(gender_list)
        genders = ["Average", "Female", "Male"]
        for gender in genders:
            gender_list.append(gender)
        self.gender_adjustment.set_selected(self.settings["gender"])
        self.advanced_inputs_group.add(self.gender_adjustment)

        self.adjustment = Gtk.Adjustment(lower= 2, upper=123, step_increment=1, page_increment=10, value=self.settings["age"])
        self.create_input_row("age_adjustment", "Age", self.adjustment, "Affects healthy/unhealthy thresholds for Waist to Height ratio", True)
        self.age_adjustment.set_digits(0)

        self.adjustment = Gtk.Adjustment(lower= 10, upper=650, step_increment=1, page_increment=10, value=self.settings["waist"])
        self.create_input_row("waist_adjustment", "Waist", self.adjustment, "Waist circumference in centimeters", True)

        self.adjustment = Gtk.Adjustment(lower= 10, upper=650, step_increment=1, page_increment=10, value=self.settings["hip"])
        self.create_input_row("hip_adjustment", "Hip", self.adjustment, "Hip circumference in centimeters", True)

        # Arrow icon
        self.center_box = Gtk.Box(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        self.main_box.append(self.center_box)
        self.icon = Gtk.Image()
        self.icon.set_from_icon_name("go-next-symbolic")
        self.icon.set_pixel_size(42)
        self.center_box.append(self.icon)

        # Simple results
        self.right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, spacing=6)
        self.right_box.set_hexpand(True)
        self.right_box.set_vexpand(True)
        self.right_box.set_size_request(175, 0)
        self.right_box.set_margin_end(16)
        self.main_box.append(self.right_box)

        self.result_label = Gtk.Label()
        self.result_label.add_css_class("title-2")
        self.result_label.set_label("BMI:")
        self.right_box.append(self.result_label)

        self.bmi_button = Gtk.Button(halign=Gtk.Align.CENTER)
        self.bmi_button.set_tooltip_text("Copy BMI")
        self.bmi_button.set_css_classes(["pill", "title-1"])
        self.bmi_button.connect('clicked', self.clipboard_copy)
        self.bmi_button.set_size_request(100, 0)
        self.right_box.append(self.bmi_button)

        self.result_feedback_label = Gtk.Label()
        self.result_feedback_label.add_css_class("title-2")
        self.right_box.append(self.result_feedback_label)

        # Advanced results
        self.right_page = Adw.PreferencesPage(halign=Gtk.Align.FILL, valign=Gtk.Align.START)
        self.right_page.set_hexpand(True)
        self.right_page.set_vexpand(True)
        self.right_page.set_size_request(270, 0)
        self.main_box.append(self.right_page)

        self.right_group = Adw.PreferencesGroup(title="Results")
        self.right_page.add(self.right_group)

        self.create_result_row("result_bmi_row", "BMI", "Body Mass Index")
        self.create_result_row("result_waist_to_height_row", "Waist / Height", "Waist to height ratio")
        self.create_result_row("result_waist_to_hip_row", "Waist / Hip", "Waist to hip ratio")
        self.create_result_row("result_bri_row", "BRI", "Body Roundness Index")

        self.init_finished = True

        # Updating values before launch
        self.on_value_changed(self)

    # Creates a spin row and adds it to self.inputs_group
    def create_input_row(self, widgetName, title, adjustment, tooltip, advanced):
        setattr(self, widgetName, Adw.SpinRow())
        self.widget = getattr(self, widgetName)

        self.widget.set_title(title)
        self.widget.set_tooltip_text(tooltip)
        self.widget.set_digits(1)
        self.widget.set_adjustment(adjustment)
        self.widget.connect('changed', self.on_value_changed)
        if advanced == True:
            self.advanced_inputs_group.add(self.widget)
        else:
            self.inputs_group.add(self.widget)

    # Creates an action row with a label and adds it to self.right_group
    def create_result_row(self, widgetName, title, tooltip):
        setattr(self, widgetName, Adw.ActionRow())
        setattr(self, f"{widgetName}_label", Gtk.Label())
        self.widget = getattr(self, widgetName)
        self.label = getattr(self, f"{widgetName}_label")
    
        self.widget.set_activatable(True)
        self.widget.set_title(title)
        self.widget.connect("activated", self.clipboard_copy)
        self.widget.set_tooltip_text(tooltip)
        self.widget.add_css_class("heading")
        self.widget.add_css_class("monospace")
        self.label.set_css_classes(["title-3"])
        self.label.set_label("21")
        self.widget.add_suffix(self.label)
        self.right_group.add(self.widget)

    def clipboard_copy(self, widget):
        if widget.get_name() == "AdwActionRow": # Hackiest way ever, but it works 🤷
            value = widget.get_first_child().get_first_child().get_next_sibling().get_next_sibling().get_next_sibling().get_first_child().get_label()
            # Explanation: AdwActionRow has a box inside a box of which the 4th child is the "suffixes", inside it is the result label
        if widget.get_name() == "GtkButton":
            value = widget.get_label();
        print(f"Copied: {value}")
        value = str(value) # Gdk Clipboard only accepts strings
        clipboard = Gdk.Display.get_default().get_clipboard()
        Gdk.Clipboard.set(clipboard, value);
        self.toast = Adw.Toast()
        self.toast.set_title("Result copied")
        self.toast.set_timeout(1)
        self.toast_overlay.add_toast(self.toast)

    def calculate(self, param):
        if param == "bmi":
            self.value = self.height_adjustment.get_value() / 100 # converting cm to meters
            self.value = self.value ** 2
            self.value = self.weight_adjustment.get_value() / self.value
            # print("BMI: ", self.value) # For debugging
            return self.value
        elif param == "waist_to_height":
            self.value = self.waist_adjustment.get_value() / self.height_adjustment.get_value()
            # print("Waist to height Ratio: ", self.value) # For debugging
            return self.value
        elif param == "waist_to_hip":
            self.value = self.waist_adjustment.get_value() / self.hip_adjustment.get_value()
            # print("Waist to hip Ratio: ", self.value) # For debugging
            return self.value
        elif param == "bri":
            self.value = (self.waist_adjustment.get_value() / (math.pi*2))**2
            self.value = self.value / ((self.height_adjustment.get_value() / 2)**2)
            self.value = 364.2 - 365.5 * math.sqrt(1 - self.value)
            # print("BRI: ", self.value) # For debugging
            return self.value

    # just calls on_value_changed when a different mode is selected
    def on_dropdown_value_changed(self, dropdown, _pspec):
        self.on_value_changed(self)

    # Action after changed values of self.height_adjustment and self.width_adjustment
    def on_value_changed(self, _scroll):
        if self.init_finished == False:
            return
        self.update_results()
        if self.mode_dropdown.get_selected() == 0:
            self.advanced_inputs_page.set_visible(False)
            self.right_page.set_visible(False)
            self.right_box.set_visible(True)
            self.inputs_group.set_title("")

            self.inputs_page.set_size_request(270, 0)
        else:
            self.advanced_inputs_page.set_visible(True)

            self.right_page.set_visible(True)
            self.right_box.set_visible(False)
            self.inputs_group.set_title("Inputs")

            self.inputs_page.set_size_request(270, 320)

    def set_result(self, widget, value, over, css_class, label):
        if value >= over:
            widget.remove_css_class("accent")
            widget.remove_css_class("success")
            widget.remove_css_class("warning")
            widget.remove_css_class("error")
            if widget.get_name() == "GtkLabel":
                widget.set_label(label)
                widget.add_css_class(css_class)
            if widget.get_name() == "AdwActionRow":
                widget.set_subtitle(label)
                widget.add_css_class(css_class)

    def update_results(self):
        self.age = self.age_adjustment.get_value()
        self.gender = self.gender_adjustment.get_selected_item().get_string()

        # Thresholds table (works by principle "if more than or equal to")
        bmi_healthy = 18.5
        bmi_overweight = 25
        bmi_obese = 30
        bmi_extremely_obese = 40

        self.waist_to_height_unhealthy = 0.5
        if self.age > 40:
            self.waist_to_height_unhealthy = ((self.age-40)/100)+0.5
        if self.age > 50:
            self.waist_to_height_unhealthy = 0.6

        self.waist_to_hip_overweight = 0.85
        self.waist_to_hip_obese = 0.925
        if self.gender == "Female":
            self.waist_to_hip_overweight = 0.8
            self.waist_to_hip_obese = 0.85
        if self.gender == "Male":
            self.waist_to_hip_overweight = 0.9
            self.waist_to_hip_obese = 1

        # Updating bmi
        self.bmi = self.calculate("bmi")
        self.bmi_button.set_label(str(int(self.bmi)))
        self.result_bmi_row_label.set_label(str(round(self.bmi, 1)))

        self.set_result(self.result_bmi_row, self.bmi, 0, "accent", "Underweight")
        self.set_result(self.result_bmi_row, self.bmi, bmi_healthy, "success", "Healthy")
        self.set_result(self.result_bmi_row, self.bmi, bmi_overweight, "warning", "Overweight")
        self.set_result(self.result_bmi_row, self.bmi, bmi_obese, "error", "Obese")
        self.set_result(self.result_bmi_row, self.bmi, bmi_extremely_obese, "", "Extremely obese")

        self.set_result(self.result_feedback_label, self.bmi, 0, "accent", "Underweight")
        self.set_result(self.result_feedback_label, self.bmi, bmi_healthy, "success", "Healthy")
        self.set_result(self.result_feedback_label, self.bmi, bmi_overweight, "warning", "Overweight")
        self.set_result(self.result_feedback_label, self.bmi, bmi_obese, "error", "Obese")
        self.set_result(self.result_feedback_label, self.bmi, bmi_extremely_obese, "", "Extremely obese")

        self.height_adjustment.set_title("Height")
        self.weight_adjustment.set_title("Weight")
        if self.height_adjustment.get_value() == 267:
            self.height_adjustment.set_title("Robert Wadlow")
        if self.weight_adjustment.get_value() == 650:
            self.weight_adjustment.set_title("Jon Brower Minnoch")

        # Updating waist to height ratio
        self.waist_to_height = self.calculate("waist_to_height")
        self.result_waist_to_height_row_label.set_label(str(round(self.waist_to_height, 2)))
        self.set_result(self.result_waist_to_height_row, self.waist_to_height, 0, "success", "Healthy")
        self.set_result(self.result_waist_to_height_row, self.waist_to_height, self.waist_to_height_unhealthy, "warning", "Unhealthy")

        # Updating waist to hip ratio
        self.waist_to_hip = self.calculate("waist_to_hip")
        self.result_waist_to_hip_row_label.set_label(str(round(self.waist_to_hip, 2)))
        self.set_result(self.result_waist_to_hip_row, self.waist_to_hip, 0, "success", "Healthy")
        self.set_result(self.result_waist_to_hip_row, self.waist_to_hip, self.waist_to_hip_overweight, "warning", "Overweight")
        self.set_result(self.result_waist_to_hip_row, self.waist_to_hip, self.waist_to_hip_obese, "error", "Obese")

        # Updating BRI
        self.bri = self.calculate("bri")
        self.result_bri_row_label.set_label(str(round(self.bri, 2)))
        self.set_result(self.result_bri_row, self.bri, 0, "accent", "Very lean")
        self.set_result(self.result_bri_row, self.bri, 3.41, "success", "Healthy")
        self.set_result(self.result_bri_row, self.bri, 4.45, "warning", "Overweight")
        self.set_result(self.result_bri_row, self.bri, 5.46, "warning", "Obese")
        self.set_result(self.result_bri_row, self.bri, 6.91, "", "Extremely obese")

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
        self.settings["height"] = self.height_adjustment.get_value()
        self.settings["weight"] = self.weight_adjustment.get_value()

        self.settings["mode"] = self.mode_dropdown.get_selected()
        self.settings["gender"] = self.gender_adjustment.get_selected()
        self.settings["age"] = self.age_adjustment.get_value()
        self.settings["waist"] = self.weight_adjustment.get_value()
        self.settings["hip"] = self.weight_adjustment.get_value()
        self.settings["forget"] = self.forget_button.get_active()

        if self.forget_button.get_active() == True:
            self.settings.reset("height")
            self.settings.reset("weight")

            self.settings.reset("gender")
            self.settings.reset("age")
            self.settings.reset("waist")
            self.settings.reset("hip")
            print("Input values were reset")

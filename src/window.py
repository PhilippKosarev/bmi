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

app_id = "io.github.philippkosarev.bmi"

class BmiWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'BmiWindow'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_finished = False

        # Loading GSettings and connecting action after closing the app window
        self.settings = Gio.Settings.new_with_path(app_id, "/io/github/philippkosarev/bmi/")
        self.connect("close-request", self.on_close_window)
        # Loading custom css
        self.provider = Gtk.CssProvider();
        self.provider.load_from_resource("style.css");
        
        # Basic window properties
        self.set_title("BMI")
        self.set_default_size(0, 230)
        self.set_resizable(False)

        # Start of the widget structure
        self.content = Adw.ToolbarView()
        self.set_content(self.content)

        # Headerbar
        self.header = Adw.HeaderBar()
        self.content.add_top_bar(self.header)
        # About button
        self.about_button = Gtk.Button()
        self.about_button.set_tooltip_text("Show About")
        self.about_button.set_icon_name("help-about-symbolic")
        self.about_button.connect('clicked', self.show_about)
        self.header.pack_end(self.about_button)
        # Mode dropdown
        self.mode_dropdown = Gtk.DropDown()
        modes_list = Gtk.StringList()
        modes = ["BMI (Basic)", "BMI (Advanced)"]
        for mode in modes:
            modes_list.append(mode)
        self.mode_dropdown.set_model(modes_list)
        self.mode_dropdown.connect('notify::selected-item', self.on_dropdown_value_changed)
        self.mode_dropdown.get_first_child().set_css_classes(["flat"])
        self.mode_dropdown.set_selected(self.settings["mode"])
        self.header.set_title_widget(self.mode_dropdown)
        # Forget button
        self.forget_button = Gtk.ToggleButton()
        self.forget_button.set_icon_name("user-trash-full-symbolic")
        self.forget_button.set_tooltip_text("Forget values on close")
        self.forget_button.set_active(self.settings["forget"])
        self.header.pack_start(self.forget_button)

        # WindowHandle to make the whole window draggable
        self.drag = Gtk.WindowHandle()
        self.content.set_content(self.drag)
        # Toast overlay layer
        self.toast_overlay = Adw.ToastOverlay()
        self.drag.set_child(self.toast_overlay)
        # Main box
        self.main_box = Gtk.Box(valign=Gtk.Align.CENTER, spacing=12)
        self.main_box.set_margin_start(16)
        self.main_box.set_margin_end(16)
        self.main_box.set_margin_bottom(16)
        self.toast_overlay.set_child(self.main_box)

        # Basic inputs root page
        self.inputs_page = Adw.PreferencesPage(halign=Gtk.Align.FILL, valign=Gtk.Align.START)
        self.inputs_page.set_hexpand(True)
        self.inputs_page.set_vexpand(True)
        self.inputs_page.set_size_request(270, 170)
        self.main_box.append(self.inputs_page)
        # Basic inputs page
        self.inputs_group = Adw.PreferencesGroup(title="Inputs")
        self.inputs_page.add(self.inputs_group)
        # Height input row
        self.adjustment = Gtk.Adjustment(lower= 50, upper=267, step_increment=1,page_increment=10, value=self.settings["height"])
        self.create_input_row("height_adjustment", "Height", self.adjustment, "Height in centimetres", False)
        # Weight input row
        self.adjustment = Gtk.Adjustment(lower= 10, upper=650, step_increment=1, page_increment=10, value=self.settings["weight"])
        self.create_input_row("weight_adjustment", "Waist", self.adjustment, "Weight in kilograms", False)

        # Advanced inputs root page
        self.advanced_inputs_page = Adw.PreferencesPage(halign=Gtk.Align.FILL, valign=Gtk.Align.START)
        self.advanced_inputs_page.set_hexpand(True)
        self.advanced_inputs_page.set_vexpand(True)
        self.advanced_inputs_page.set_size_request(290, 320)
        self.main_box.append(self.advanced_inputs_page)
        # Advanced input group
        self.advanced_inputs_group = Adw.PreferencesGroup(title="Advanced inputs")
        self.advanced_inputs_page.add(self.advanced_inputs_group)
        # Gender input row
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
        # Age input row
        self.adjustment = Gtk.Adjustment(lower= 5, upper=123, step_increment=1, page_increment=10, value=self.settings["age"])
        self.create_input_row("age_adjustment", "Age", self.adjustment, "Affects healthy/unhealthy thresholds for Waist to Height ratio", True)
        self.age_adjustment.set_digits(0)
        # Waist circumference input row
        self.adjustment = Gtk.Adjustment(lower= 25, upper=650, step_increment=1, page_increment=10, value=self.settings["waist"])
        self.create_input_row("waist_adjustment", "Waist", self.adjustment, "Waist circumference in centimeters", True)
        # Hip circumference input row
        self.adjustment = Gtk.Adjustment(lower= 25, upper=650, step_increment=1, page_increment=10, value=self.settings["hip"])
        self.create_input_row("hip_adjustment", "Hip", self.adjustment, "Hip circumference in centimeters", True)

        # Arrow icon
        self.icon = Gtk.Image(icon_name="go-next-symbolic")
        self.icon.set_pixel_size(42)
        self.main_box.append(self.icon)

        # Simple results root box
        self.right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, valign=Gtk.Align.CENTER, spacing=6)
        self.right_box.set_hexpand(True)
        self.right_box.set_vexpand(True)
        self.right_box.set_size_request(175, 0)
        self.right_box.set_margin_end(16)
        self.main_box.append(self.right_box)
        # 'BMI:' label
        self.result_label = Gtk.Label(label="BMI:")
        self.result_label.add_css_class("title-2")
        self.right_box.append(self.result_label)
        # The button which shows the BMI number
        self.bmi_button = Gtk.Button(halign=Gtk.Align.CENTER)
        self.bmi_button.set_tooltip_text("Copy BMI")
        self.bmi_button.set_css_classes(["pill", "title-1"])
        self.bmi_button.connect('clicked', self.clipboard_copy)
        self.bmi_button.set_size_request(100, 0)
        self.right_box.append(self.bmi_button)
        # The label which shows feedback (Underweight/Overweight)
        self.result_feedback_label = Gtk.Label()
        self.result_feedback_label.add_css_class("title-2")
        self.right_box.append(self.result_feedback_label)

        # Advanced results root page
        self.right_page = Adw.PreferencesPage(halign=Gtk.Align.FILL)
        self.right_page.set_size_request(290, 0)
        self.main_box.append(self.right_page)
        # Advanced results group
        self.right_group = Adw.PreferencesGroup(title="Results")
        self.right_page.add(self.right_group)
        # Result rows
        self.create_result_row("result_bmi_row", "BMI", "Body Mass Index")
        self.create_result_row("result_waist_to_height_row", "Waist / Height", "Waist to height ratio")
        self.create_result_row("result_waist_to_hip_row", "Waist / Hip", "Waist to hip ratio")
        self.create_result_row("result_bri_row", "BRI", "Body Roundness Index")

        # Hiding/showing advanced inputs/results & updating values before showing the window
        self.init_finished = True
        self.update_mode()
        self.update_results()

    # Creates a spin row and adds it to either self.inputs_group or advanced_inputs_group
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

    # Copying text from result widget
    def clipboard_copy(self, widget):
        # Copying the result label from a result row
        if widget.get_name() == "AdwActionRow":
            value = widget.get_first_child().get_first_child() \
            .get_next_sibling().get_next_sibling().get_next_sibling() \
            .get_first_child().get_label()
            # Hackiest way ever, but it works 🤷
            # Explanation: AdwActionRow has a box inside a box of which the 4th
            #              child is the "suffixes", inside it is the result label
        # Copying a button's label
        if widget.get_name() == "GtkButton":
            value = widget.get_label();
        value = str(value) # Gdk Clipboard only accepts strings
        clipboard = Gdk.Display.get_default().get_clipboard()
        print(f"Copied: {value}")
        Gdk.Clipboard.set(clipboard, value);
        # Creating and showing a toast
        self.toast = Adw.Toast(title="Result copied", timeout=1)
        self.toast_overlay.add_toast(self.toast)

    # Action, called after value of self.mode_dropdown changes
    def on_dropdown_value_changed(self, dropdown, _pspec):
        self.update_mode()

    # Action, called after value of self.height_adjustment or other adjustments changes
    def on_value_changed(self, _scroll):
        self.update_results()

    # Hides or shows simple and advanced input and output widgets depending on the selected mode
    def update_mode(self):
        if self.init_finished == False:
            return
        if self.mode_dropdown.get_selected() == 0:
            self.advanced_inputs_page.set_visible(False)
            self.right_page.set_visible(False)
            self.right_box.set_visible(True)
            self.inputs_group.set_title("")
        else:
            self.advanced_inputs_page.set_visible(True)
            self.right_page.set_visible(True)
            self.right_box.set_visible(False)
            self.inputs_group.set_title("Inputs")

    # A more convenient way to set result colours and text on the self.result_feedback_label and self.result_rows
    def set_result(self, widget, value, over, css_class, label):
        if value >= over:
            widget.remove_css_class("light-blue")
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
        # Widgets call their action on creation so this prevents them from complaining
        # when the action tries to do something with the widgets which have not been created yet
        if self.init_finished == False:
            return
        # Getting adjustment values which determine some of the results' thresholds
        self.age = self.age_adjustment.get_value()
        self.gender = self.gender_adjustment.get_selected_item().get_string()

        # Thresholds table (works by the principle "equal or more than")
        bmi_underweight = 0
        bmi_underweight3 = 0
        bmi_underweight2 = 16
        bmi_underweight1 = 17
        bmi_healthy = 18.5
        bmi_overweight = 25
        bmi_obese1 = 30
        bmi_obese2 = 35
        bmi_obese3 = 40
        bmi_obese = 40

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
        self.bmi = self.height_adjustment.get_value() / 100 # converting cm to meters
        self.bmi = self.bmi ** 2
        self.bmi = self.weight_adjustment.get_value() / self.bmi
        self.bmi_button.set_label(str(int(self.bmi)))
        self.result_bmi_row_label.set_label(str(round(self.bmi, 1)))

        # The BMI thresholds for under 20s looks like a sine wave so I tried
        # using that to calculate the bmi threshold, but unsuccessful so far
        # which is why the age_adjustment's lower boundary is 18
        # if self.gender == "Female" and self.age < 20:
        #     age_curve = self.age
        #     age_curve = (age_curve-5)/(19-5) # normalizing
        #     age_curve = math.sin(age_curve * math.pi - math.pi / 2) # sine waving
        #     age_curve = (age_curve + 1)/2 # normalizing again

            # Underweight
        #     bmi_underweight = age_curve * (17.2 - 13.1)
        #     bmi_underweight = bmi_underweight + 13.1
        #     print(round(bmi_underweight, 2))

            # Underweight
        #     bmi_healthy = age_curve * (17.2 - 13.1)
        #     bmi_healthy = bmi_healthy + 13.1

            # Overweight
        #     bmi_overweight = age_curve * (25.1 - 16.9)
        #     bmi_overweight = bmi_overweight + 16.9

        self.set_result(self.result_bmi_row, self.bmi, bmi_underweight3, "light-blue", "Underweight [Severe]")
        self.set_result(self.result_bmi_row, self.bmi, bmi_underweight2, "light-blue", "Underweight [Moderate]")
        self.set_result(self.result_bmi_row, self.bmi, bmi_underweight1, "light-blue", "Underweight [Mild]")
        self.set_result(self.result_bmi_row, self.bmi, bmi_healthy, "success", "Healthy")
        self.set_result(self.result_bmi_row, self.bmi, bmi_overweight, "warning", "Overweight")
        self.set_result(self.result_bmi_row, self.bmi, bmi_obese1, "error", "Obese [Class 1]")
        self.set_result(self.result_bmi_row, self.bmi, bmi_obese2, "error", "Obese [Class 2]")
        self.set_result(self.result_bmi_row, self.bmi, bmi_obese3, "error", "Obese [Class 3]")

        self.set_result(self.result_feedback_label, self.bmi, bmi_underweight3, "light-blue", "Underweight")
        self.set_result(self.result_feedback_label, self.bmi, bmi_underweight1, "light-blue", "Underweight")
        self.set_result(self.result_feedback_label, self.bmi, bmi_healthy, "success", "Healthy")
        self.set_result(self.result_feedback_label, self.bmi, bmi_overweight, "warning", "Overweight")
        self.set_result(self.result_feedback_label, self.bmi, bmi_obese1, "error", "Obese")
        self.set_result(self.result_feedback_label, self.bmi, bmi_obese3, "error", "Extremely obese")

        self.height_adjustment.set_title("Height")
        self.weight_adjustment.set_title("Weight")
        if self.height_adjustment.get_value() == 267:
            self.height_adjustment.set_title("Robert Wadlow")
        if self.weight_adjustment.get_value() == 650:
            self.weight_adjustment.set_title("Jon Brower Minnoch")

        # Updating waist to height ratio
        self.waist_to_height = self.waist_adjustment.get_value() / self.height_adjustment.get_value()
        self.result_waist_to_height_row_label.set_label(str(round(self.waist_to_height, 2)))
        self.set_result(self.result_waist_to_height_row, self.waist_to_height, 0, "success", "Healthy")
        self.set_result(self.result_waist_to_height_row, self.waist_to_height, self.waist_to_height_unhealthy, "warning", "Unhealthy")

        # Updating waist to hip ratio
        self.waist_to_hip = self.waist_adjustment.get_value() / self.hip_adjustment.get_value()
        self.result_waist_to_hip_row_label.set_label(str(round(self.waist_to_hip, 2)))
        self.set_result(self.result_waist_to_hip_row, self.waist_to_hip, 0, "success", "Healthy")
        self.set_result(self.result_waist_to_hip_row, self.waist_to_hip, self.waist_to_hip_overweight, "warning", "Overweight")
        self.set_result(self.result_waist_to_hip_row, self.waist_to_hip, self.waist_to_hip_obese, "error", "Obese")

        # Updating BRI
        self.bri = (self.waist_adjustment.get_value() / (math.pi*2))**2
        self.bri = self.bri / ((self.height_adjustment.get_value() / 2)**2)
        self.bri = 364.2 - 365.5 * math.sqrt(1 - self.bri)
        self.result_bri_row_label.set_label(str(round(self.bri, 2)))
        self.set_result(self.result_bri_row, self.bri, 0, "light-blue", "Very lean")
        self.set_result(self.result_bri_row, self.bri, 3.41, "success", "Healthy")
        self.set_result(self.result_bri_row, self.bri, 4.45, "warning", "Overweight")
        self.set_result(self.result_bri_row, self.bri, 5.46, "warning", "Obese")
        self.set_result(self.result_bri_row, self.bri, 6.91, "error", "Extremely obese")

    # Show the About app dialog
    def show_about(self, _button):
        self.about = Adw.AboutWindow(application_name='BMI',
        application_icon='io.github.philippkosarev.bmi',
        developer_name='Philipp Kosarev',
        version='v2.0',
        developers=['Philipp Kosarev'],
        artists=['Philipp Kosarev'],
        copyright='© 2024 Philipp Kosarev',
        license_type="GTK_LICENSE_GPL_2_0",
        website="https://github.com/philippkosarev/bmi",
        issue_url="https://github.com/philippkosarev/bmi/issues")
        self.about.present()
        
    # Action after closing the app window
    def on_close_window(self, widget, *args):
        # Setting gsettings values to adjustments to use them on next launch
        self.settings["height"] = self.height_adjustment.get_value()
        self.settings["weight"] = self.weight_adjustment.get_value()
        self.settings["mode"] = self.mode_dropdown.get_selected()
        self.settings["gender"] = self.gender_adjustment.get_selected()
        self.settings["age"] = self.age_adjustment.get_value()
        self.settings["waist"] = self.waist_adjustment.get_value()
        self.settings["hip"] = self.hip_adjustment.get_value()
        self.settings["forget"] = self.forget_button.get_active()

        # Resets adjustments if forget button is active
        if self.forget_button.get_active() == True:
            self.settings.reset("height")
            self.settings.reset("weight")
            self.settings.reset("gender")
            self.settings.reset("age")
            self.settings.reset("waist")
            self.settings.reset("hip")

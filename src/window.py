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

# Imports
from gi.repository import Adw, Gtk, Gdk, Gio
import math

# Shorthand vars
app_id = "io.github.philippkosarev.bmi"
# Alignment
start = Gtk.Align.START
end = Gtk.Align.END
center = Gtk.Align.CENTER
fill = Gtk.Align.FILL
# Orientations
horizontal = Gtk.Orientation.HORIZONTAL
vertical = Gtk.Orientation.VERTICAL

class BmiWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'BmiWindow'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Loading GSettings and connecting action after closing the app window
        self.settings = Gio.Settings.new_with_path(app_id, "/io/github/philippkosarev/bmi/")
        self.connect("close-request", self.on_close_window)

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
        self.about_button = Gtk.Button(icon_name="help-about-symbolic")
        self.about_button.set_tooltip_text("Show About")
        self.about_button.connect('clicked', self.show_about)
        self.header.pack_end(self.about_button)
        # Mode dropdown
        self.mode_dropdown = Gtk.DropDown()
        modes_list = Gtk.StringList()
        modes = ["BMI (Basic)", "BMI (Advanced)"]
        for mode in modes:
            modes_list.append(mode)
        self.mode_dropdown.set_model(modes_list)
        self.mode_dropdown.set_selected(self.settings["mode"])
        self.mode_dropdown.connect('notify::selected-item', self.on_dropdown_value_changed)
        self.mode_dropdown.get_first_child().set_css_classes(["flat"])
        self.header.set_title_widget(self.mode_dropdown)
        # Metric/Imperial button
        self.units_button = Gtk.ToggleButton(icon_name="ruler-angled-symbolic")
        self.units_button.set_active(self.settings["imperial"])
        self.units_button.connect('toggled', self.on_units_button)
        self.units_button.set_tooltip_text("Switch to imperial")
        self.header.pack_start(self.units_button)
        # Forget button
        self.forget_button = Gtk.ToggleButton(icon_name="user-trash-full-symbolic")
        self.forget_button.set_active(self.settings["forget"])
        self.forget_button.set_tooltip_text("Forget values on close")
        self.header.pack_start(self.forget_button)

        # WindowHandle to make the whole window draggable
        self.drag = Gtk.WindowHandle()
        self.content.set_content(self.drag)
        # Toast overlay layer
        self.toast_overlay = Adw.ToastOverlay()
        self.drag.set_child(self.toast_overlay)
        # Main box
        self.main_box = Gtk.Box(valign=center)
        self.main_box.set_margin_start(16)
        self.main_box.set_margin_end(16)
        self.main_box.set_margin_bottom(16)
        self.toast_overlay.set_child(self.main_box)

        # Basic inputs root page
        self.inputs_page = Adw.PreferencesPage(halign=center)
        self.inputs_page.set_hexpand(True)
        self.inputs_page.set_vexpand(True)
        self.inputs_page.set_size_request(300, 170)
        self.main_box.append(self.inputs_page)
        # Basic inputs group
        self.inputs_group = Adw.PreferencesGroup(title="Inputs")
        self.inputs_page.add(self.inputs_group)
        # Height input row
        self.height_adjustment = Gtk.Adjustment(lower=50, upper=267, step_increment=1, page_increment=10)
        self.create_input_row("height_input_row", "Height", self.height_adjustment, 0, "Affects BMI and BRI", False)
        # Weight input row
        self.weight_adjustment = Gtk.Adjustment(lower=10, upper=650, step_increment=1, page_increment=10)
        self.create_input_row("weight_input_row", "Weight", self.weight_adjustment, 0, "Affects BMI", False)

        # Advanced inputs root page
        self.advanced_inputs_page = Adw.PreferencesPage(halign=center)
        self.advanced_inputs_page.set_hexpand(True)
        self.advanced_inputs_page.set_vexpand(True)
        self.advanced_inputs_page.set_size_request(300, 330)
        self.main_box.append(self.advanced_inputs_page)
        # Advanced input group
        self.advanced_inputs_group = Adw.PreferencesGroup(title="Advanced inputs")
        self.advanced_inputs_page.add(self.advanced_inputs_group)
        # Gender input row
        self.gender_adjustment = Adw.ComboRow(title="Gender")
        self.gender_adjustment.set_tooltip_text("Affects healthy/unhealthy thresholds for Waist to Hip ratio")
        gender_list = Gtk.StringList()
        self.gender_adjustment.set_model(gender_list)
        genders = ["Average", "Female", "Male"]
        for gender in genders:
            gender_list.append(gender)
        self.gender_adjustment.set_selected(self.settings["gender"])
        self.gender_adjustment.connect('notify::selected-item', self.on_dropdown_value_changed)
        self.advanced_inputs_group.add(self.gender_adjustment)
        # Age input row
        self.age_adjustment = Gtk.Adjustment(lower=18, upper=123, step_increment=1, page_increment=10)
        self.create_input_row("age_input_row", "Age", self.age_adjustment, 0, "Affects healthy/unhealthy thresholds for Waist to Height ratio", True)
        self.age_input_row.set_digits(0)
        self.age_input_row.set_subtitle("Years")
        # Waist circumference input row
        self.waist_adjustment = Gtk.Adjustment(lower= 25, upper=650, step_increment=1, page_increment=10)
        self.create_input_row("waist_input_row", "Waist", self.waist_adjustment, 0, "Affects Waist to Height ratio, Waist to Hip ratio and BRI", True)
        # Hip circumference input row
        self.hip_adjustment = Gtk.Adjustment(lower= 25, upper=650, step_increment=1, page_increment=10)
        self.create_input_row("hip_input_row", "Hip", self.hip_adjustment, 0, "Affects Waist to Hip ratio", True)

        # Arrow icon
        self.icon = Gtk.Image(icon_name="go-next-symbolic", pixel_size=32)
        self.icon.set_margin_start(24)
        self.main_box.append(self.icon)

        # Simple results root box
        self.right_box = Gtk.Box(orientation=vertical, valign=center, spacing=6)
        self.right_box.set_size_request(190, 0)
        self.right_box.set_margin_start(8)
        self.right_box.set_margin_end(8)
        self.main_box.append(self.right_box)
        # 'BMI:' label
        self.result_label = Gtk.Label(label="BMI:")
        self.result_label.add_css_class("title-2")
        self.right_box.append(self.result_label)
        # The button which shows the BMI number
        self.bmi_button = Gtk.Button(halign=center)
        self.bmi_button.set_tooltip_text("Copy BMI")
        self.bmi_button.set_css_classes(["pill", "title-1"])
        self.bmi_button.connect('clicked', self.clipboard_copy)
        self.bmi_button.set_size_request(110, 0)
        self.right_box.append(self.bmi_button)
        # The label which shows feedback (Underweight/Overweight)
        self.result_feedback_label = Gtk.Label()
        self.result_feedback_label.add_css_class("title-2")
        self.right_box.append(self.result_feedback_label)

        # Advanced results root page
        self.right_page = Adw.PreferencesPage(halign=center)
        self.right_page.set_size_request(300, 330)
        self.right_page.set_margin_start(12)
        self.main_box.append(self.right_page)
        # Advanced results group
        self.right_group = Adw.PreferencesGroup(title="Results")
        self.right_page.add(self.right_group)
        # Result rows
        self.create_result_row("result_bmi_row", "BMI", "Body Mass Index")
        self.create_result_row("result_waist_to_height_row", "Waist / Height", "Waist to height ratio")
        self.create_result_row("result_waist_to_hip_row", "Waist / Hip", "Waist to hip ratio")
        self.create_result_row("result_bri_row", "BRI", "Body Roundness Index")

        # Setting values for input rows
        self.height_input_row.set_value(self.settings["height"])
        self.weight_input_row.set_value(self.settings["mass"])
        self.waist_input_row.set_value(self.settings["waist"])
        self.hip_input_row.set_value(self.settings["hip"])
        self.age_input_row.set_value(self.settings["age"])

        self.distance_rows = [self.height_input_row, self.waist_input_row, self.hip_input_row]
        self.mass_rows = [self.weight_input_row]
        self.metrics_rows = self.distance_rows + self.mass_rows
        # Connecting input rows
        for row in self.metrics_rows:
            row.connect('changed', self.on_input_changed)

        # Almost done
        self.update_all()

        # Converting to imperial if needed
        forget = self.settings.get_value("forget")
        imperial = self.settings.get_value("imperial")
        if imperial:
            self.on_units_button(self)

    def update_all(self):
        # Updating results
        self.update_inputs()
        self.update_results()
        self.update_feedback_thresholds()
        self.update_result_labels()
        # Updating widgets
        self.update_mode()
        self.update_units_labels()

    def update_inputs(self):
        # Getting relevant values
        self.imperial = self.units_button.get_active()
        self.height = self.height_input_row.get_value()
        self.mass = self.weight_input_row.get_value()
        self.waist = self.waist_input_row.get_value()
        self.hip = self.hip_input_row.get_value()
        self.gender = self.gender_adjustment.get_selected_item().get_string()
        self.age = self.age_input_row.get_value()
        # Converting imperial to metric
        if self.imperial:
            self.height = self.in_to_cm(self.height)
            self.mass = self.lb_to_kg(self.mass)
            self.waist = self.in_to_cm(self.waist)
            self.hip = self.in_to_cm(self.hip)

        self.height_input_row.set_title("Height")
        self.weight_input_row.set_title("Weight")
        if self.height == 267:
            self.height_input_row.set_title("Robert Wadlow")
        if self.mass == 650:
            self.weight_input_row.set_title("Jon Brower Minnoch")

    def update_results(self):
        # Aliasing
        height = self.height
        mass = self.mass
        waist = self.waist
        hip = self.hip
        # Calculating BMI
        self.bmi = mass / ((height / 100) ** 2)
        # Calculating Waist to Height ratio
        self.waist_to_height = waist / height
        # Calculating Waist to Hip ratio
        self.waist_to_hip = waist / hip
        # Calculating BRI
        self.bri = 364.2 - (365.5 * math.sqrt((1 - (waist / (math.pi * height)) ** 2)))

    # Creates a spin row and adds it to either self.inputs_group or advanced_inputs_group
    def create_input_row(self, widgetName, title, adjustment, digits, tooltip, advanced):
        # Creating AdwSpinRow with name widgetName
        setattr(self, widgetName, Adw.SpinRow())
        self.widget = getattr(self, widgetName)
        # Customizing the SpinRow
        self.widget.set_title(title)
        self.widget.set_tooltip_text(tooltip)
        self.widget.set_adjustment(adjustment)
        self.widget.set_digits(digits)
        # Deciding where to add the row
        if advanced == True: self.advanced_inputs_group.add(self.widget)
        else: self.inputs_group.add(self.widget)

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
        print(f"Copied result '{value}'")
        Gdk.Clipboard.set(clipboard, value);
        # Creating and showing a toast
        self.toast = Adw.Toast(title="Result copied", timeout=1)
        self.toast_overlay.add_toast(self.toast)

    # Action, called after value of self.mode_dropdown changes
    def on_dropdown_value_changed(self, dropdown, _pspec):
        self.update_mode()
        self.update_results()

    # Action, called after value of self.height_input_row or other inputs changes
    def on_input_changed(self, _scroll):
        self.update_inputs()
        self.update_results()
        self.update_feedback_thresholds()
        self.update_result_labels()

    # Hides or shows simple and advanced input and output widgets depending on the selected mode
    def update_mode(self):
        mode = self.mode_dropdown.get_selected()
        if mode == 0:
            self.advanced_inputs_page.set_visible(False)
            self.right_page.set_visible(False)
            self.right_box.set_visible(True)
            self.inputs_group.set_title("")
        else:
            self.advanced_inputs_page.set_visible(True)
            self.right_page.set_visible(True)
            self.right_box.set_visible(False)
            self.inputs_group.set_title("Inputs")

    # Called by self.units_button
    def on_units_button(self, _button):
        # Getting relevant vars
        self.update_inputs()
        # Calling functions
        self.update_units_labels()
        self.convert_input_adjustments()
        self.convert_input_values()
        self.update_results()

    # Changes input rows' subtitles to cm/kg or in/ft
    def update_units_labels(self):
        # Setting subtitles and converting values
        if self.imperial is False:
            for row in self.distance_rows:
                row.set_subtitle("Centimetres")
            for row in self.mass_rows:
                row.set_subtitle("Kilograms")
        else:
            for row in self.distance_rows:
                row.set_subtitle("Inches")
            for row in self.mass_rows:
                row.set_subtitle("Pounds")
    # For easier conversions
    def in_to_cm(self, value): value *= 2.54; return value
    def cm_to_in(self, value): value *= 0.3937008; return value
    def kg_to_lb(self, value): value *= 2.204623; return value
    def lb_to_kg(self, value): value *= 0.4535924; return value
    # Converts input rows' values
    def convert_input_values(self):
        # Converting
        if self.imperial is False:
            for row in self.distance_rows:
                row.set_value(self.in_to_cm(row.get_value()))
            for row in self.mass_rows:
                row.set_value(self.lb_to_kg(row.get_value()))
        else:
            for row in self.distance_rows:
                row.set_value(self.cm_to_in(row.get_value()))
            for row in self.mass_rows:
                row.set_value(self.kg_to_lb(row.get_value()))
    # Updating input rows' adjustments
    def convert_input_adjustments(self):
        def row_get_upper(row): return row.get_adjustment().get_upper()
        def row_get_lower(row): return row.get_adjustment().get_lower()
        if self.imperial is False:
            for row in self.distance_rows:
                new_upper = self.in_to_cm(row_get_upper(row))
                row.get_adjustment().set_upper(new_upper)
                new_lower = self.in_to_cm(row_get_lower(row))
                row.get_adjustment().set_lower(new_lower)
            for row in self.mass_rows:
                new_upper = self.lb_to_kg(row_get_upper(row))
                row.get_adjustment().set_upper(new_upper)
                new_lower = self.lb_to_kg(row_get_lower(row))
                row.get_adjustment().set_lower(new_lower)
        else:
            for row in self.distance_rows:
                new_upper = self.cm_to_in(row_get_upper(row))
                row.get_adjustment().set_upper(new_upper)
                new_lower = self.cm_to_in(row_get_lower(row))
                row.get_adjustment().set_lower(new_lower)
            for row in self.mass_rows:
                new_upper = self.kg_to_lb(row_get_upper(row))
                row.get_adjustment().set_upper(new_upper)
                new_lower = self.kg_to_lb(row_get_lower(row))
                row.get_adjustment().set_lower(new_lower)

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

    def update_feedback_thresholds(self):
        # Works if value is equal or more than specified
        # BMI thresholds
        self.bmi_underweight3 = 0
        self.bmi_underweight2 = 16
        self.bmi_underweight1 = 17
        self.bmi_healthy = 18.5
        self.bmi_overweight = 25
        self.bmi_obese1 = 30
        self.bmi_obese2 = 35
        self.bmi_obese3 = 40
        # Waist to Height thresholds
        if self.age > 40:
            self.waist_to_height_unhealthy = ((self.age-40)/100)+0.5
        elif self.age > 50:
            self.waist_to_height_unhealthy = 0.6
        else:
            self.waist_to_height_unhealthy = 0.5
        # Waist to Hip thresholds
        if self.gender == "Female":
            self.waist_to_hip_overweight = 0.8
            self.waist_to_hip_obese = 0.85
        elif self.gender == "Male":
            self.waist_to_hip_overweight = 0.9
            self.waist_to_hip_obese = 1
        else:
            self.waist_to_hip_overweight = 0.85
            self.waist_to_hip_obese = 0.925
        # BRI thresholds
        self.bri_underweight2 = 0
        self.bri_underweight1 = 3.41
        self.bri_healthy = 4.45
        self.bri_overweight1 = 5.46
        self.bri_overweight2 = 6.91

    def update_result_labels(self):
        # Converting results to strings
        def round_to_str(value, digits): return str(round(value, digits))
        simple_bmi_result = str(int(round(self.bmi, 0)))
        advanced_bmi_result = round_to_str(self.bmi, 1)
        advanced_waist_to_height_result = round_to_str(self.waist_to_height, 2)
        advanced_waist_to_hip_result = round_to_str(self.waist_to_hip, 2)
        advanced_bri_result = round_to_str(self.bri, 2)

        # Setting simple BMI results
        self.bmi_button.set_label(simple_bmi_result)
        def set_result_for_bmi_label(over, css_class, label):
            self.set_result(self.result_feedback_label, self.bmi, over, css_class, label)
        set_result_for_bmi_label(self.bmi_underweight3, "light-blue", "Underweight")
        set_result_for_bmi_label(self.bmi_healthy, "success", "Healthy")
        set_result_for_bmi_label(self.bmi_overweight, "warning", "Overweight")
        set_result_for_bmi_label(self.bmi_obese1, "error", "Obese")
        set_result_for_bmi_label(self.bmi_obese3, "error", "Extremely obese")
        # Setting advanced BMI results
        self.result_bmi_row_label.set_label(advanced_bmi_result)
        def set_result_for_bmi_row(over, css_class, label):
            self.set_result(self.result_bmi_row, self.bmi, over, css_class, label)
        set_result_for_bmi_row(self.bmi_underweight3, "light-blue", "Underweight [Severe]")
        set_result_for_bmi_row(self.bmi_underweight2, "light-blue", "Underweight [Moderate]")
        set_result_for_bmi_row(self.bmi_underweight1, "light-blue", "Underweight [Mild]")
        set_result_for_bmi_row(self.bmi_healthy, "success", "Healthy")
        set_result_for_bmi_row(self.bmi_overweight, "warning", "Overweight")
        set_result_for_bmi_row(self.bmi_obese1, "error", "Obese [Class 1]")
        set_result_for_bmi_row(self.bmi_obese2, "error", "Obese [Class 2]")
        set_result_for_bmi_row(self.bmi_obese3, "error", "Obese [Class 3]")

        # Setting advanced Waist to Height results
        self.result_waist_to_height_row_label.set_label(advanced_waist_to_height_result)
        def set_result_for_bri_row(over, css_class, label):
            self.set_result(self.result_waist_to_height_row, self.waist_to_height, over, css_class, label)
        set_result_for_bri_row(0, "success", "Healthy")
        set_result_for_bri_row(self.waist_to_height_unhealthy, "warning", "Unhealthy")

        # Setting advanced Waist to Hip results
        self.result_waist_to_hip_row_label.set_label(advanced_waist_to_hip_result)
        def set_result_for_waist_to_hip_row(over, css_class, label):
            self.set_result(self.result_waist_to_hip_row, self.waist_to_hip, over, css_class, label)
        set_result_for_waist_to_hip_row(0, "success", "Healthy")
        set_result_for_waist_to_hip_row(self.waist_to_hip_overweight, "warning", "Overweight")
        set_result_for_waist_to_hip_row(self.waist_to_hip_obese, "error", "Obese")

        # Setting advanced BRI results
        self.result_bri_row_label.set_label(advanced_bri_result)
        def set_result_for_bri_row(over, css_class, label):
            self.set_result(self.result_bri_row, self.bri, over, css_class, label)
        set_result_for_bri_row(self.bri_underweight2, "light-blue", "Very lean")
        set_result_for_bri_row(self.bri_underweight1, "success", "Healthy")
        set_result_for_bri_row(self.bri_healthy, "warning", "Overweight")
        set_result_for_bri_row(self.bri_overweight1, "warning", "Obese")
        set_result_for_bri_row(self.bri_overweight2, "error", "Extremely obese")

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
        self.settings["mode"] = self.mode_dropdown.get_selected()
        self.settings["forget"] = self.forget_button.get_active()
        self.settings["imperial"] = self.units_button.get_active()
        # Body metrics
        self.settings["height"] = round(self.height, 0)
        self.settings["mass"] = round(self.mass, 0)
        self.settings["waist"] = round(self.waist, 0)
        self.settings["hip"] = round(self.hip, 0)
        # Age and gender
        self.settings["age"] = self.age_input_row.get_value()
        self.settings["gender"] = self.gender_adjustment.get_selected()
        # Resets adjustments if forget button is active
        body_metrics=["height", "mass", "gender", "age", "waist", "hip"]
        if self.settings["forget"] is True:
            for body_metric in body_metrics:
                self.settings.reset(body_metric)

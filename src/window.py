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
from gi.repository import Gtk, Adw, Gdk, Gio
import math
from .bmi_widgets import *

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
        self.about_button.set_tooltip_text(_("Show About"))
        self.about_button.connect('clicked', self.show_about)
        self.header.pack_end(self.about_button)
        # Mode dropdown
        self.mode_dropdown = Gtk.DropDown()
        modes_list = Gtk.StringList()
        modes = [f"BMI ({_('Basic')})", f"BMI ({_('Advanced')})"]
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
        self.units_button.set_tooltip_text(_("Switch to imperial units"))
        self.header.pack_start(self.units_button)
        # Forget button
        self.forget_button = Gtk.ToggleButton(icon_name="user-trash-full-symbolic")
        self.forget_button.set_active(self.settings["forget"])
        self.forget_button.set_tooltip_text(_("Forget input values after closing"))
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
        self.inputs_group = Adw.PreferencesGroup(title=_("Inputs"))
        self.inputs_page.add(self.inputs_group)
        # Basic inputs
        basic_inputs = [
          # Height input
          {'title': _('Height'), 'type': 'distance',
          'setting_key': 'height', 'min': 50, 'max': 267,
          'tooltip': _('Affects BMI and BRI')},
          # Weight input
          {'title': _('Weight'), 'type': 'weight',
          'setting_key': 'mass', 'min': 15, 'max': 650,
          'tooltip': _('Affects BMI')},
        ]
        self.add_inputs_to_group(basic_inputs, self.inputs_group)
        self.inputs = basic_inputs

        # Advanced inputs root page
        self.advanced_inputs_page = Adw.PreferencesPage(halign=center)
        self.advanced_inputs_page.set_hexpand(True)
        self.advanced_inputs_page.set_vexpand(True)
        self.advanced_inputs_page.set_size_request(300, 330)
        self.main_box.append(self.advanced_inputs_page)
        # Advanced input group
        self.advanced_inputs_group = Adw.PreferencesGroup(title=_("Advanced inputs"))
        self.advanced_inputs_page.add(self.advanced_inputs_group)
        # Advanced inputs
        advanced_inputs = [
          # Gender input
          {'title': _('Gender'), 'type': 'gender',
         'setting_key': 'gender', 'options': [_("Average"), _("Female"), _("Male")],
         'tooltip': _('Affects healthy/unhealthy thresholds for Waist to Hip ratio')},
          # Age input
          {'title': _('Age'), 'type': 'time',
         'setting_key': 'age', 'min': 18, 'max': 123,
         'tooltip': _('Affects healthy/unhealthy thresholds for Waist to Height ratio')},
          # Waist circumference
          {'title': _('Waist'), 'type': 'distance',
         'setting_key': 'waist', 'min': 25, 'max': 800,
         'tooltip': _('Affects Waist to Height ratio, Waist to Hip ratio and BRI')},
          # Hip circumference
          {'title': _('Hip'), 'type': 'distance',
          'setting_key': 'hip', 'min': 25, 'max': 800,
          'tooltip': _('Affects Waist to Hip ratio')},
        ]
        self.add_inputs_to_group(advanced_inputs, self.advanced_inputs_group)
        self.inputs = self.inputs + advanced_inputs

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
        self.result_label = Gtk.Label(label=_("BMI:"))
        self.result_label.add_css_class("title-2")
        self.right_box.append(self.result_label)
        # The button which shows the BMI number
        self.bmi_button = Gtk.Button(halign=center)
        self.bmi_button.set_tooltip_text(_("Copy BMI"))
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
        self.right_page.set_margin_start(24)
        self.main_box.append(self.right_page)
        # Advanced results group
        self.right_group = Adw.PreferencesGroup(title=_("Results"))
        self.right_page.add(self.right_group)

        self.create_result_row("result_bmi_row", _("BMI"), _("Body Mass Index"))
        self.create_result_row("result_waist_to_height_row", _("Waist / Height"), _("Waist to height ratio"))
        self.create_result_row("result_waist_to_hip_row", _("Waist / Hip"), _("Waist to hip ratio"))
        self.create_result_row("result_bri_row", _("BRI"), _("Body Roundness Index"))
        # Results
        # results = {
        # 'bmi_basic': {
        #     'widget': self.result_feedback_label,
        #     'label':  self.bmi_button,
        #     'value':  int(round(self.bmi, 0)),
        #     'thresholds': [
        #       {'text': _('Underweight'),     'value': 0,    'style': 'light-blue'},
        #       {'text': _('Healthy'),         'value': 18.5, 'style': 'success'},
        #       {'text': _('Overweight'),      'value': 25,   'style': 'warning'},
        #       {'text': _('Obese'),           'value': 30,   'style': 'error'},
        #       {'text': _('Extremely obese'), 'value': 40,   'style': 'error'},
        #     ]
        #   },
        #   'bmi': {
        #     'widget': self.result_bmi_row,
        #     'label': self.result_bmi_row_label,
        #     'value':  round(self.bmi, 1),
        #     'thresholds': [
        #       {'text': _('Underweight [Severe]'),   'value': 0,    'style': 'light-blue'},
        #       {'text': _('Underweight [Moderate]'), 'value': 16,   'style': 'light-blue'},
        #       {'text': _('Underweight [Mild]'),     'value': 17,   'style': 'light-blue'},
        #       {'text': _('Healthy'),                'value': 18.5, 'style': 'success'},
        #       {'text': _('Overweight'),             'value': 25,   'style': 'warning'},
        #       {'text': _('Obese [Class 1]'),        'value': 30,   'style': 'error'},
        #       {'text': _('Obese [Class 2]'),        'value': 35,   'style': 'error'},
        #       {'text': _('Obese [Class 3]'),        'value': 40,   'style': 'error'},
        #     ]
        #   },
        #   'whtr': {
        #     'widget': self.result_waist_to_height_row,
        #     'label': self.result_waist_to_height_row_label,
        #     'value':  round(self.waist_to_height, 2),
        #     'thresholds': [
        #       {'text': _('Healthy'),   'value': 0,                    'style': 'success'},
        #       {'text': _('Unhealthy'), 'value': get_whtr_unhealthy(), 'style': 'warning'},
        #     ]
        #   },
        #   'whr': {
        #     'widget': self.result_waist_to_hip_row,
        #     'label': self.result_waist_to_hip_row_label,
        #     'value':  round(self.waist_to_hip, 2),
        #     'thresholds': [
        #       {'text': _('Healthy'),    'value': 0,                      'style': 'success'},
        #       {'text': _('Overweight'), 'value': get_whr_threshold()[0], 'style': 'warning'},
        #       {'text': _('Obese'),      'value': get_whr_threshold()[1], 'style': 'error'},
        #     ]
        #   },
        #   'bri': {
        #     'widget': self.result_bri_row,
        #     'label': self.result_bri_row_label,
        #     'value':  round(self.bri, 2),
        #     'thresholds': [
        #       {'text': _('Very lean'),     'value': 0,    'style': 'light-blue'},
        #       {'text': _('Lean'),          'value': 3.41, 'style': 'success'},
        #       {'text': _('Average'),       'value': 4.45, 'style': 'success'},
        #       {'text': _('Above average'), 'value': 5.46, 'style': 'warning'},
        #       {'text': _('High'),          'value': 6.91, 'style': 'error'},
        #     ]
        #   },
        # }

        # Setting remembered values for input rows and connecting them
        for item in self.inputs:
          widget = item.get('widget')
          key = item.get('setting_key')
          value = self.settings[key]
          widget.set_value(value)
          widget.set_callback(self.update_results)
        # Updating all
        self.update_results()
        self.update_mode()
        # Switching to imperial if needed
        if self.units_button.get_active():
            self.on_units_button(self)

    def add_inputs_to_group(self, inputs, group):
      iteration = 0
      for item in inputs:
        row_type = inputs[iteration].get('type')
        if row_type == 'weight': row = WeightRow()
        elif row_type == 'distance': row = DistanceRow()
        elif row_type == 'time': row = TimeRow()
        elif row_type == 'gender':
          options = inputs[iteration].get('options')
          row = GenderRow(options)
        if row_type == 'weight' or row_type == 'distance' or row_type == 'time':
          title = inputs[iteration].get('title')
          row.set_title(title)
          lower = inputs[iteration].get('min')
          upper = inputs[iteration].get('max')
          row.set_range(lower, upper)
        tooltip = inputs[iteration].get('tooltip')
        row.set_tooltip(tooltip)
        row.set_group(group)
        inputs[iteration]['widget'] = row
        iteration += 1

    def get_input(self, metric: str):
      for item in self.inputs:
        key = item.get('setting_key')
        if key == metric:
          widget = item.get('widget')
          value = widget.get_value()
          return value
      print(f"No such input as '{metric}'")
      exit(-1)

    def set_imperial(self, imperial: bool):
      for item in self.inputs:
        widget = item.get('widget')
        if imperial:
          widget.set_imperial(True)
        else:
          widget.set_imperial(False)

    # Called after value of an input row changes
    def update_results(self):
      height = self.get_input('height')
      mass = self.get_input('mass')
      waist = self.get_input('waist')
      hip = self.get_input('hip')
      # Calculating BMI
      self.bmi = mass / ((height / 100) ** 2)
      # Calculating Waist to Height ratio
      self.waist_to_height = waist / height
      # Calculating Waist to Hip ratio
      self.waist_to_hip = waist / hip
      # Calculating BRI
      try:
        self.bri = 364.2 - (365.5 * math.sqrt((1 - (waist / (math.pi * height)) ** 2)))
      except ValueError:
        self.bri = 0
      # Sometimes '1 - (self.waist / (math.pi * height)' < 0 so sqrt() errors out
      self.update_result_labels()

    # Hides or shows simple and advanced input and output widgets depending on the selected mode
    def update_mode(self):
      if self.mode_dropdown.get_selected() == 0:
        self.advanced_inputs_page.set_visible(False)
        self.right_page.set_visible(False)
        self.right_box.set_visible(True)
        self.inputs_group.set_title("")
      else:
        self.advanced_inputs_page.set_visible(True)
        self.right_page.set_visible(True)
        self.right_box.set_visible(False)
        self.inputs_group.set_title(_("Inputs"))

    # Action, called after value of self.mode_dropdown changes
    def on_dropdown_value_changed(self, dropdown, _pspec):
        self.update_mode()
        self.update_results()

    # Called by self.units_button
    def on_units_button(self, _button):
        self.convert_inputs()
        self.update_results()
        self.update_result_labels()
        self.set_imperial(self.units_button.get_active())

    # Converting row adjustment limits and values
    def convert_inputs(self):
        # Helper functions
        def row_get_limits(row):
            return [row.get_adjustment().get_lower(), row.get_adjustment().get_upper()]
        def row_set_range(row, limits):
            row.get_adjustment().set_lower(limits[0])
            row.get_adjustment().set_upper(limits[1])
        # Defining conversions
        if self.units_button.get_active() is False:
            convert_distance = self.in_to_cm
            convert_mass = self.lb_to_kg
        else:
            convert_distance = self.cm_to_in
            convert_mass = self.kg_to_lb
        # Setting limits and values
        for row in self.distance_rows:
            limits = row_get_limits(row)
            for i in range(len(limits)): limits[i] = round(convert_distance(limits[i]), 1)
            row_set_range(row, limits)
            row.set_value(convert_distance(round(row.get_value(), 1)))

    def get_thresholds(self):
        age = self.get_input('age')
        gender = self.get_input('gender')
        # Getting dynamic values
        def get_whtr_unhealthy():
          if age > 40:   return ((age-40)/100)+0.5
          elif age > 50: return 0.6
          else:          return 0.5
        def get_whr_threshold():
          if gender == 0:   return [0.85, 0.925]
          if gender == 1:   return [0.8, 0.85]
          elif gender == 2: return [0.9, 1]
          else:
            print('Unhandled gender value.')
            exit(-1)
        # Returning results
        return {
          'bmi_basic': {
            'widget': self.result_feedback_label,
            'label':  self.bmi_button,
            'value':  int(round(self.bmi, 0)),
            'thresholds': [
              {'text': _('Underweight'),     'value': 0,    'style': 'light-blue'},
              {'text': _('Healthy'),         'value': 18.5, 'style': 'success'},
              {'text': _('Overweight'),      'value': 25,   'style': 'warning'},
              {'text': _('Obese'),           'value': 30,   'style': 'error'},
              {'text': _('Extremely obese'), 'value': 40,   'style': 'error'},
            ]
          },
          'bmi': {
            'widget': self.result_bmi_row,
            'label': self.result_bmi_row_label,
            'value':  round(self.bmi, 1),
            'thresholds': [
              {'text': _('Underweight [Severe]'),   'value': 0,    'style': 'light-blue'},
              {'text': _('Underweight [Moderate]'), 'value': 16,   'style': 'light-blue'},
              {'text': _('Underweight [Mild]'),     'value': 17,   'style': 'light-blue'},
              {'text': _('Healthy'),                'value': 18.5, 'style': 'success'},
              {'text': _('Overweight'),             'value': 25,   'style': 'warning'},
              {'text': _('Obese [Class 1]'),        'value': 30,   'style': 'error'},
              {'text': _('Obese [Class 2]'),        'value': 35,   'style': 'error'},
              {'text': _('Obese [Class 3]'),        'value': 40,   'style': 'error'},
            ]
          },
          'whtr': {
            'widget': self.result_waist_to_height_row,
            'label': self.result_waist_to_height_row_label,
            'value':  round(self.waist_to_height, 2),
            'thresholds': [
              {'text': _('Healthy'),   'value': 0,                    'style': 'success'},
              {'text': _('Unhealthy'), 'value': get_whtr_unhealthy(), 'style': 'warning'},
            ]
          },
          'whr': {
            'widget': self.result_waist_to_hip_row,
            'label': self.result_waist_to_hip_row_label,
            'value':  round(self.waist_to_hip, 2),
            'thresholds': [
              {'text': _('Healthy'),    'value': 0,                      'style': 'success'},
              {'text': _('Overweight'), 'value': get_whr_threshold()[0], 'style': 'warning'},
              {'text': _('Obese'),      'value': get_whr_threshold()[1], 'style': 'error'},
            ]
          },
          'bri': {
            'widget': self.result_bri_row,
            'label': self.result_bri_row_label,
            'value':  round(self.bri, 2),
            'thresholds': [
              {'text': _('Very lean'),     'value': 0,    'style': 'light-blue'},
              {'text': _('Lean'),          'value': 3.41, 'style': 'success'},
              {'text': _('Average'),       'value': 4.45, 'style': 'success'},
              {'text': _('Above average'), 'value': 5.46, 'style': 'warning'},
              {'text': _('High'),          'value': 6.91, 'style': 'error'},
            ]
          },
        }

    def update_result_labels(self):
        def clear_css(widget):
            widget.remove_css_class("light-blue")
            widget.remove_css_class("success")
            widget.remove_css_class("warning")
            widget.remove_css_class("error")
        results = self.get_thresholds()
        # bmi = results.get('bmi').get('thresholds')
        # for item in bmi:
        #   val = item.get('value')
        #   uhuh = val * ((self.height / 100) ** 2)
        #   uhuh = round(uhuh, 1)
        #   print( uhuh )
        for item in results:
          widget = results.get(item).get('widget')
          label = results.get(item).get('label')
          value = results.get(item).get('value')
          label.set_label(str(value))
          thresholds = results.get(item).get('thresholds')
          for threshold in thresholds:
              threshold_value = threshold.get('value')
              text = threshold.get('text')
              style = threshold.get('style')
              if value >= threshold_value:
                  clear_css(widget)
                  if widget.get_name() == "GtkLabel":
                      widget.set_label(text)
                      widget.add_css_class(style)
                  if widget.get_name() == "AdwActionRow":
                      widget.set_subtitle(text)
                      widget.add_css_class(style)

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
        self.toast = Adw.Toast(title=_("Result copied"), timeout=1)
        self.toast_overlay.add_toast(self.toast)

    # For easier conversions
    def in_to_cm(self, value): value *= 2.54; return value
    def cm_to_in(self, value): value *= 0.3937008; return value
    def kg_to_lb(self, value): value *= 2.204623; return value
    def lb_to_kg(self, value): value *= 0.4535924; return value

    # Show the About app dialog
    def show_about(self, _button):
        self.about = Adw.AboutWindow(
        application_name = 'BMI',
        application_icon = 'io.github.philippkosarev.bmi',
        developer_name   = 'Philipp Kosarev',
        version          = 'v3.0',
        developers       = ['Philipp Kosarev'],
        artists          = ['Philipp Kosarev'],
        copyright        = '© 2024 Philipp Kosarev',
        license_type     = "GTK_LICENSE_GPL_2_0",
        website          = "https://github.com/philippkosarev/bmi",
        issue_url        = "https://github.com/philippkosarev/bmi/issues"
        ); self.about.present()

    # Action after closing the app window
    def on_close_window(self, widget, *args):
        # Setting gsettings values to adjustments to use them on next launch
        self.settings["mode"] = self.mode_dropdown.get_selected()
        self.settings["forget"] = self.forget_button.get_active()
        self.settings["imperial"] = self.units_button.get_active()
        # Body metrics
        for item in self.inputs:
          key = item.get('setting_key')
          value = item.get('widget').get_value()
          self.settings[key] = value
        # Age and gender
        # Resets adjustments if forget button is active
        body_metrics=["height", "mass", "gender", "age", "waist", "hip"]
        if self.settings["forget"] is True:
            for body_metric in body_metrics:
                self.settings.reset(body_metric)

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

        # Basic results root box
        self.right_box = Gtk.Box(orientation=vertical, valign=center, spacing=6)
        self.right_box.set_size_request(190, 0)
        self.right_box.set_margin_start(8)
        self.right_box.set_margin_end(8)
        self.main_box.append(self.right_box)

        # Advanced results root page
        self.right_page = Adw.PreferencesPage(halign=center)
        self.right_page.set_size_request(300, 330)
        self.right_page.set_margin_start(24)
        self.main_box.append(self.right_page)
        # Advanced results group
        self.right_group = Adw.PreferencesGroup(title=_("Results"))
        self.right_page.add(self.right_group)

        # Results
        def get_bmi():
          mass = self.get_input('mass')
          height = self.get_input('height')
          return mass / ((height / 100) ** 2)
        def get_whtr():
          waist = self.get_input('waist')
          height = self.get_input('height')
          return waist / height
        def get_whr():
          waist = self.get_input('waist')
          hip = self.get_input('hip')
          return waist / hip
        def get_bri():
          waist = self.get_input('waist')
          height = self.get_input('height')
          try:
            bri = 364.2 - (365.5 * math.sqrt((1 - (waist / (math.pi * height)) ** 2)))
          except ValueError:
          # Sometimes '1 - (self.waist / (math.pi * height)' < 0 so sqrt() errors out
            bri = 0
          return bri
        # Getting dynamic values
        def get_whtr_unhealthy():
          age = self.get_input('age')
          if age > 40:   return ((age-40)/100)+0.5
          elif age > 50: return 0.6
          else:          return 0.5
        def get_whr_threshold():
          gender = self.get_input('gender')
          if gender == 0:   return [0.85, 0.925] # Average
          if gender == 1:   return [0.8, 0.85] # Female
          elif gender == 2: return [0.9, 1] # Male
          else:
            print('Unhandled gender value.')
            exit(-1)
        self.basic_results = [
          {
            'title': _('BMI'),
            'tooltip': _('Body Mass Index'),
            'calc_func':  get_bmi,
            'thresholds': [
              {'text': _('Underweight'),     'value': 0,    'style': 0},
              {'text': _('Healthy'),         'value': 18.5, 'style': 1},
              {'text': _('Overweight'),      'value': 25,   'style': 2},
              {'text': _('Obese'),           'value': 30,   'style': 3},
              {'text': _('Extremely obese'), 'value': 40,   'style': 3},
            ]
          }
        ]
        # Adding result to basic results page
        self.basic_results = self.add_results(self.basic_results, 'basic', self.right_box)
        self.results = self.basic_results
        # Advanced results
        self.advanced_results = [
        { 'title': _('BMI'),
          'tooltip': _('Body Mass Index'),
          'calc_func':  get_bmi,
          'digits': 1,
          'thresholds': [
            {'text': _('Underweight [Severe]'),   'value': 0,    'style': 0},
            {'text': _('Underweight [Moderate]'), 'value': 16,   'style': 0},
            {'text': _('Underweight [Mild]'),     'value': 17,   'style': 0},
            {'text': _('Healthy'),                'value': 18.5, 'style': 1},
            {'text': _('Overweight'),             'value': 25,   'style': 2},
            {'text': _('Obese [Class 1]'),        'value': 30,   'style': 3},
            {'text': _('Obese [Class 2]'),        'value': 35,   'style': 3},
            {'text': _('Obese [Class 3]'),        'value': 40,   'style': 3},
          ]
        }, {
          'title': _('Waist / Height'),
          'tooltip': _('Waist to height ratio'),
          'calc_func':  get_whtr,
          'digits': 2,
          'thresholds': [
            {'text': _('Healthy'),   'value': 0,                    'style': 1},
            {'text': _('Unhealthy'), 'value': get_whtr_unhealthy(), 'style': 2},
          ]
        }, {
          'title': _('Waist / Hip'),
          'tooltip': _('Waist to hip ratio'),
          'calc_func':  get_whr,
          'digits': 2,
          'thresholds': [
            {'text': _('Healthy'),    'value': 0,                      'style': 1},
            {'text': _('Overweight'), 'value': get_whr_threshold()[0], 'style': 2},
            {'text': _('Obese'),      'value': get_whr_threshold()[1], 'style': 3},
          ]
        }, {
          'title': _('BRI'),
          'tooltip': _('Body Roundness Index'),
          'calc_func':  get_bri,
          'digits': 2,
          'thresholds': [
            {'text': _('Very lean'),     'value': 0,    'style': 0},
            {'text': _('Lean'),          'value': 3.41, 'style': 1},
            {'text': _('Average'),       'value': 4.45, 'style': 1},
            {'text': _('Above average'), 'value': 5.46, 'style': 2},
            {'text': _('High'),          'value': 6.91, 'style': 3},
          ]
        }]
        # Adding result rows to advanced results page
        self.advanced_results = self.add_results(self.advanced_results, 'advanced', self.right_group)
        self.results = self.results + self.advanced_results

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
        row_type = item.get('type')
        if row_type == 'weight': row = WeightRow()
        elif row_type == 'distance': row = DistanceRow()
        elif row_type == 'time': row = TimeRow()
        elif row_type == 'gender':
          options = item.get('options')
          row = GenderRow(options)
        if row_type == 'weight' or row_type == 'distance' or row_type == 'time':
          title = item.get('title')
          row.set_title(title)
          row.set_range(item.get('min'), item.get('max'))
        row.set_tooltip(item.get('tooltip'))
        row.set_group(group)
        inputs[iteration]['widget'] = row
        iteration += 1

    def add_results(self, results, result_type, parent):
      counter = 0
      for result in results:
        if result_type == 'basic':
          widget = BasicResult()
        elif result_type == 'advanced':
          widget = ResultRow()
        else:
          print(f"Unhandled result widget type '{widget}'")
          exit(-1)
        widget.set_title(result.get('title'))
        widget.set_tooltip(result.get('tooltip'))
        widget.set_parent(parent)
        results[counter]['widget'] = widget
        counter += 1
      return results

    # Gets input from an input row
    def get_input(self, metric: str):
      for item in self.inputs:
        key = item.get('setting_key')
        if key == metric:
          return item.get('widget').get_value()
      print(f"No such input as '{metric}'")
      exit(-1)

    # Action, called after value of self.mode_dropdown changes
    def on_dropdown_value_changed(self, dropdown, _pspec):
      self.update_mode()
      self.update_results()

    # Called by self.units_button
    def on_units_button(self, _button):
      self.set_imperial(self.units_button.get_active())
      self.update_results()

    def set_imperial(self, imperial: bool):
      for item in self.inputs:
        widget = item.get('widget')
        widget_name = widget.get_name()
        if widget_name == 'WeightRow' or widget_name == 'DistanceRow':
          if imperial:
            widget.set_imperial(True)
          else:
            widget.set_imperial(False)

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
        self.inputs_group.set_title(_("Inputs"))

    def update_results(self):
      for item in self.results:
        widget = item.get('widget')
        value = item.get('calc_func')()
        digits = item.get('digits')
        widget.set_result(value, digits)
        thresholds = item.get('thresholds')
        for threshold in thresholds:
          threshold_value = threshold.get('value')
          text = threshold.get('text')
          style = threshold.get('style')
          if value >= threshold_value:
            widget.set_feedback(text)
            widget.set_style(style)

    # Show the About app dialog
    def show_about(self, _button):
        self.about = Adw.AboutDialog(
        application_name = 'BMI',
        application_icon = 'io.github.philippkosarev.bmi',
        developer_name   = 'Philipp Kosarev',
        version          = 'v3.0',
        translator_credits = _('Sultaniiazov David https://github.com/x1z53'),
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

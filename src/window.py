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
from gi.repository import Gtk, Adw, Gio, Gdk
import math, re

# Internal imports
from .distance_row import DistanceRow
from .mass_row import MassRow
from .time_row import TimeRow
from .gender_row import GenderRow
from .result_row import ResultRow
from .calculator import Calculator
calc = Calculator()

clipboard = Gdk.Display.get_default().get_clipboard()

# Shorthand vars
vertical = Gtk.Orientation.VERTICAL
horizontal = Gtk.Orientation.HORIZONTAL
adw_lenght_units = {
  'px': Adw.LengthUnit.PX,
  'sp': Adw.LengthUnit.SP,
  'pt': Adw.LengthUnit.PT,
}


# Helper functions
def eval_breakpoint(window, adw_breakpoint):
  width = window.get_size(horizontal)
  height = window.get_size(vertical)
  condition = adw_breakpoint.get_condition().to_string()
  condition = condition.replace('min-width:', 'width >')
  condition = condition.replace('max-width:', 'width <')
  condition = condition.replace('min-height:', 'height >')
  condition = condition.replace('max-height:', 'height <')
  condition = condition.split('and')
  for statement in condition:
    combined = re.search('([0-9]).*', statement).group().strip()
    units = combined[-2] + combined[-1] # Last 2 chars (i.e. px, sp or pt)
    value = float(combined.removesuffix(units))
    units = adw_lenght_units.get(units)
    pixels = math.ceil( Adw.LengthUnit.to_px(units, value) )
    statement = statement.replace(combined, str(pixels))
    if eval(statement) is False:
      return False
  return True

def get_nth_child(parent, n):
  child = parent.get_first_child()
  for widget in range(n-1):
    child = child.get_first_child()
  return child

def get_groups(page):
  group = get_nth_child(page, 5).get_next_sibling()
  groups = [group]
  while True:
    group = group.get_next_sibling()
    if group is not None:
      groups.append(group)
    else:
      return groups


@Gtk.Template(resource_path='/io/github/philippkosarev/bmi/window.ui')
class BmiWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'BmiWindow'

    # Important Widgets
    toast_overlay = Gtk.Template.Child()
    clamp = Gtk.Template.Child()
    orientable_box = Gtk.Template.Child()
    ## Breakpoints
    simple_breakpoint = Gtk.Template.Child()
    advanced_breakpoint = Gtk.Template.Child()
    ## Clamps
    advanced_inputs_clamp = Gtk.Template.Child()
    ## Groups
    basic_inputs_group = Gtk.Template.Child()
    advanced_inputs_group = Gtk.Template.Child()
    results_group = Gtk.Template.Child()
    ## Result rows
    bmi_result_row = Gtk.Template.Child()
    whtr_result_row = Gtk.Template.Child()
    whr_result_row = Gtk.Template.Child()
    bri_result_row = Gtk.Template.Child()

    def __init__(self, settings, **kwargs):
      super().__init__(**kwargs)
      # Settings
      self.settings = settings
      window_size = self.settings['window-size']
      self.set_default_size(window_size[0], window_size[1])
      self.set_advanced_mode(self.settings['advanced-mode'])
      # Connecting
      self.connect("close-request", self.on_close_window)
      # Adding basic inputs
      basic_inputs = [
        # Height input
        {'title': _('Height'), 'widget': DistanceRow(),
        'key': 'height', 'min': 50, 'max': 270,
        'tooltip': _('Affects BMI and BRI')},
        # Weight input
        {'title': _('Weight'), 'widget': MassRow(),
        'key': 'mass', 'min': 15, 'max': 650,
        'tooltip': _('Affects BMI')},
      ]
      self.add_inputs_to_group(basic_inputs, self.basic_inputs_group)

      # Adding advanced inputs
      advanced_inputs = [
        # Gender input
        {'title': _('Gender'), 'widget': GenderRow(),
       'key': 'gender',
       'tooltip': _('Affects healthy/unhealthy thresholds for Waist to Hip ratio')},
        # Age input
        {'title': _('Age'), 'widget': TimeRow(),
       'key': 'age', 'min': 18, 'max': 130,
       'tooltip': _('Affects healthy/unhealthy thresholds for Waist to Height ratio')},
        # Waist circumference
        {'title': _('Waist'), 'widget': DistanceRow(),
       'key': 'waist', 'min': 25, 'max': 800,
       'tooltip': _('Affects Waist to Height ratio, Waist to Hip ratio and BRI')},
        # Hip circumference
        {'title': _('Hip'), 'widget': DistanceRow(),
        'key': 'hip', 'min': 25, 'max': 800,
        'tooltip': _('Affects Waist to Hip ratio')},
      ]
      self.add_inputs_to_group(
        advanced_inputs, self.advanced_inputs_group
      )
      # All inputs
      self.inputs = basic_inputs + advanced_inputs

      # Advanced results
      self.results = [
        {
          'widget': self.bmi_result_row,
          'digits': 1,
          'calc_func':  calc.bmi,
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
        },
        {
          'widget': self.whtr_result_row,
          'calc_func':  calc.whtr,
          'digits': 2,
          'thresholds': [
            {'text': _('Healthy'),   'value': 0,                        'style': 1},
            {'text': _('Unhealthy'), 'value': calc.whtr_unhealthy, 'style': 2},
          ]
        },
        {
          'widget': self.whr_result_row,
          'calc_func':  calc.whr,
          'digits': 2,
          'thresholds': [
            {'text': _('Healthy'),    'value': 0,                   'style': 1},
            {'text': _('Overweight'), 'value': calc.whr_overweight, 'style': 2},
            {'text': _('Obese'),      'value': calc.whr_obese,      'style': 3},
          ]
        },
        {
          'widget': self.bri_result_row,
          'digits': 2,
          'calc_func':  calc.bri,
          'thresholds': [
            {'text': _('Very lean'),     'value': 0,    'style': 0},
            {'text': _('Lean'),          'value': 3.41, 'style': 1},
            {'text': _('Average'),       'value': 4.45, 'style': 1},
            {'text': _('Above average'), 'value': 5.46, 'style': 2},
            {'text': _('High'),          'value': 6.91, 'style': 3},
          ]
        }
      ]
      # Adding result rows to advanced results page
      self.add_results_to_group(self.results, self.results_group)

      # Setting measurement system from settings
      self.set_imperial(bool(self.settings["measurement-system"]))

      # Setting up adaptive ui
      self.simple_breakpoint.connect('apply', self.on_simple_breakpoint_apply)
      self.simple_breakpoint.connect('unapply', self.on_simple_breakpoint_unapply)
      self.advanced_breakpoint.connect('apply', self.on_advanced_breakpoint_apply)
      self.advanced_breakpoint.connect('unapply', self.on_advanced_breakpoint_unapply)

    def on_simple_breakpoint_apply(self, adw_breakpoint = None):
      if self.settings['advanced-mode']:
        return
      self.set_ui_orientation(horizontal)

    def on_simple_breakpoint_unapply(self, adw_breakpoint = None):
      if self.settings['advanced-mode']:
        return
      self.set_ui_orientation(vertical)

    def on_advanced_breakpoint_apply(self, adw_breakpoint = None):
      self.set_ui_orientation(horizontal)

    def on_advanced_breakpoint_unapply(self, adw_breakpoint = None):
      self.set_ui_orientation(vertical)

    def set_ui_orientation(self, orientation: horizontal or vertical):
      self.orientable_box.set_orientation(orientation)
      if orientation is horizontal:
        self.orientable_box.set_spacing(24);
      else:
        self.orientable_box.set_spacing(16);

    def update_breakpoints(self):
      if eval_breakpoint(self, self.advanced_breakpoint):
        self.on_advanced_breakpoint_apply()
      else:
        self.on_advanced_breakpoint_unapply()
      if eval_breakpoint(self, self.simple_breakpoint):
        self.on_simple_breakpoint_apply()
      else:
        self.on_simple_breakpoint_unapply()


    def set_advanced_mode(self, mode: bool):
      self.advanced_inputs_clamp.set_visible(mode)
      self.whtr_result_row.set_visible(mode)
      self.whr_result_row.set_visible(mode)
      self.bri_result_row.set_visible(mode)
      self.update_breakpoints()

    def add_inputs_to_group(self, inputs, group):
      for item in inputs:
        row = item.get('widget')
        row.set_title(item.get('title'))
        if ('min' in item) and ('max' in item):
          row.set_range(item.get('min'), item.get('max'))
        row.set_value(self.settings[item.get('key')])
        row.set_tooltip(item.get('tooltip'))
        row.set_group(group)
        row.set_callback(self.update_result)

    def add_results_to_group(self, results, group):
      for item in results:
        row = item.get('widget')
        row.set_callback(self.copy_result)
      return results

    def update_result(self, row):
      # Getting inputs
      inputs = {}
      for item in self.inputs:
        key = item.get('key')
        widget = item.get('widget')
        value = widget.get_value()
        inputs[key] = value
      # Updating results
      for item in self.results:
        # Setting result
        widget = item.get('widget')
        calc_func = item.get('calc_func')
        digits = item.get('digits')
        value = calc_func(inputs)
        thresholds = item.get('thresholds')
        widget.set_result(value, digits, inputs, thresholds)

    def copy_result(self, row):
      value = str(row.get_value())
      Gdk.Clipboard.set(clipboard, value);
      print(f"Copied result '{value}'")
      self.show_toast(_("Result copied"))

    def show_toast(self, text):
      self.toast_overlay.dismiss_all()
      toast = Adw.Toast(title=text, timeout=1)
      self.toast_overlay.add_toast(toast)

    def set_imperial(self, imperial: bool):
      for item in self.inputs:
        widget = item.get('widget')
        widget_name = widget.get_name()
        if widget_name == 'DistanceRow' or widget_name == 'MassRow':
          if imperial:
            widget.set_imperial(True)
          else:
            widget.set_imperial(False)

    # Action after closing the app window
    def on_close_window(self, widget, *args):
      # Setting gsettings values to adjustments to use them on next launch
      window_width = self.get_size(Gtk.Orientation.HORIZONTAL)
      window_height = self.get_size(Gtk.Orientation.VERTICAL)
      self.settings['window-size'] = (window_width, window_height)
      # Setting input values
      if self.settings["remember-inputs"]:
        for item in self.inputs:
          key = item.get('key')
          value = item.get('widget').get_value()
          self.settings[key] = value
      else:
        for item in self.inputs:
          key = item.get('key')
          self.settings.reset(key)

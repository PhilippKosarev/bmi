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
    if not eval(statement):
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
    if group is None:
      return groups
    groups.append(group)

def get_metric_row_value(row):
  row_name = row.get_name()
  if row_name == 'DistanceRow':
    value = row.get_centimetres()
  elif row_name == 'MassRow':
    value = row.get_kilograms()
  else:
    value = row.get_value()
  return value

@Gtk.Template(resource_path='/io/github/philippkosarev/bmi/window.ui')
class BmiWindow(Adw.ApplicationWindow):
  __gtype_name__ = 'BmiWindow'

  # Important Widgets
  toast_overlay = Gtk.Template.Child()
  clamp = Gtk.Template.Child()
  orientable_box = Gtk.Template.Child()
  simple_breakpoint = Gtk.Template.Child()
  advanced_breakpoint = Gtk.Template.Child()
  advanced_inputs_clamp = Gtk.Template.Child()
  ## Input rows
  height_input_row = Gtk.Template.Child()
  weight_input_row = Gtk.Template.Child()
  gender_input_row = Gtk.Template.Child()
  age_input_row = Gtk.Template.Child()
  waist_input_row = Gtk.Template.Child()
  hip_input_row = Gtk.Template.Child()
  ## Result rows
  bmi_result_row = Gtk.Template.Child()
  whtr_result_row = Gtk.Template.Child()
  whr_result_row = Gtk.Template.Child()
  bri_result_row = Gtk.Template.Child()

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.get_app = self.get_application
    settings = self.get_app().get_settings()
    # Configuring inputs
    self.input_rows = {
      'height': self.height_input_row,
      'mass':   self.weight_input_row,
      'gender': self.gender_input_row,
      'age':    self.age_input_row,
      'waist':  self.waist_input_row,
      'hip':    self.hip_input_row,
    }
    self.set_imperial(bool(settings['measurement-system']))
    for key in self.input_rows:
      row = self.input_rows.get(key)
      value = settings[key]
      row.set_value(value)
      row.connect(row.get_signal(), self.update_inputs)
    # Configuring results
    self.result_rows = [
      self.bmi_result_row,
      self.whtr_result_row,
      self.whr_result_row,
      self.bri_result_row,
    ]
    for row in self.result_rows:
      row.set_callback(self.copy_result)
    # Setting result thresholds and calc functions
    self.bmi_result_row.set_calc_func(calc.bmi)
    self.bmi_result_row.set_thresholds([
      {'text': _('Underweight [Severe]'),   'value': 0,    'style': 0},
      {'text': _('Underweight [Moderate]'), 'value': 16,   'style': 0},
      {'text': _('Underweight [Mild]'),     'value': 17,   'style': 0},
      {'text': _('Healthy'),                'value': 18.5, 'style': 1},
      {'text': _('Overweight'),             'value': 25,   'style': 2},
      {'text': _('Obese [Class 1]'),        'value': 30,   'style': 3},
      {'text': _('Obese [Class 2]'),        'value': 35,   'style': 3},
      {'text': _('Obese [Class 3]'),        'value': 40,   'style': 3},
    ])
    self.whtr_result_row.set_calc_func(calc.whtr)
    self.whtr_result_row.set_thresholds([
      {'text': _('Healthy'),   'value': 0,                   'style': 1},
      {'text': _('Unhealthy'), 'value': calc.whtr_unhealthy, 'style': 2},
    ])
    self.whr_result_row.set_calc_func(calc.whr)
    self.whr_result_row.set_thresholds([
      {'text': _('Healthy'),    'value': 0,                   'style': 1},
      {'text': _('Overweight'), 'value': calc.whr_overweight, 'style': 2},
      {'text': _('Obese'),      'value': calc.whr_obese,      'style': 3},
    ])
    self.bri_result_row.set_calc_func(calc.bri)
    self.bri_result_row.set_thresholds([
      {'text': _('Very lean'),     'value': 0,    'style': 0},
      {'text': _('Lean'),          'value': 3.41, 'style': 1},
      {'text': _('Average'),       'value': 4.45, 'style': 1},
      {'text': _('Above average'), 'value': 5.46, 'style': 2},
      {'text': _('High'),          'value': 6.91, 'style': 3},
    ])

    # Connecting stuff
    self.connect("close-request", self.on_close_window)
    self.simple_breakpoint.connect('apply', self.on_simple_breakpoint_apply)
    self.simple_breakpoint.connect('unapply', self.on_simple_breakpoint_unapply)
    self.advanced_breakpoint.connect('apply', self.on_advanced_breakpoint_apply)
    self.advanced_breakpoint.connect('unapply', self.on_advanced_breakpoint_unapply)

    # Setting properties from settings
    window_width, window_height = settings['window-size']
    self.set_default_size(window_width, window_height)
    self.set_advanced_mode(settings['advanced-mode'])

    # Updating inputs, calculating results and setting results
    self.update_inputs()
    settings.connect('changed', self.on_settings_changed)

  def on_simple_breakpoint_apply(self, adw_breakpoint = None):
    if self.get_app().get_settings()['advanced-mode']:
      return
    self.set_ui_orientation(horizontal)

  def on_simple_breakpoint_unapply(self, adw_breakpoint = None):
    if self.get_app().get_settings()['advanced-mode']:
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

  def update_inputs(self, *args):
    inputs = {}
    for key in self.input_rows:
      row = self.input_rows.get(key)
      value = get_metric_row_value(row)
      inputs[key] = value
    self.update_results(inputs)

  def update_results(self, inputs: dict):
    for row in self.result_rows:
      row.update(inputs)

  def copy_result(self, row):
    value = str(row.get_value())
    Gdk.Clipboard.set(clipboard, value);
    self.show_toast(_("Result copied"))

  def show_toast(self, text):
    self.toast_overlay.dismiss_all()
    toast = Adw.Toast(title=text, timeout=1)
    self.toast_overlay.add_toast(toast)

  def set_imperial(self, measurement_system: int):
    imperial = bool(measurement_system)
    for key in self.input_rows:
      row = self.input_rows.get(key)
      if row.get_name() in ('DistanceRow', 'MassRow'):
        row.set_imperial(imperial)

  def on_settings_changed(self, settings: Gio.Settings, key: str):
    update_functions = {
      'advanced-mode': self.set_advanced_mode,
      'measurement-system': self.set_imperial,
    }
    if key in update_functions:
      function = update_functions.get(key)
      value = settings[key]
      function(value)

  # Action after closing the app window.
  def on_close_window(self, widget, *args):
    settings = self.get_app().get_settings()
    # Setting gsettings values to adjustments to use them on next launch
    settings['window-size'] = (self.get_size(horizontal), self.get_size(vertical))
    # Setting input values
    if settings["remember-inputs"]:
      for key in self.input_rows:
        row = self.input_rows.get(key)
        value = row.get_value()
        settings[key] = value
    else:
      for key in self.input_rows:
        settings.reset(key)

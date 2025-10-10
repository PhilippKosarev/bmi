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
import math, re, copy

# Internal imports
from . import widgets
from .calculator import Calculator

# Shorthand vars
calc = Calculator()
clipboard = Gdk.Display.get_default().get_clipboard()
horizontal = Gtk.Orientation.HORIZONTAL
vertical = Gtk.Orientation.VERTICAL
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


@Gtk.Template(resource_path='/io/github/philippkosarev/bmi/window/window.ui')
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
    self.input_rows = [
      self.height_input_row,
      self.weight_input_row,
      self.gender_input_row,
      self.age_input_row,
      self.waist_input_row,
      self.hip_input_row,
    ]
    for row in self.input_rows:
      key = row.get_key()
      row.set_value(settings[key])
      row.connect(row.get_signal(), self.update_results)
    # Configuring results
    self.result_rows = [
      self.bmi_result_row,
      self.whtr_result_row,
      self.whr_result_row,
      self.bri_result_row,
    ]
    for row in self.result_rows:
      row.connect('activated', self.copy_result)
      row.connect('info-clicked', self.on_result_row_info_clicked)
    self.result_row_info = {
      self.bmi_result_row: {
        'calc-function': calc.bmi,
        'context': {
          'calc-function': calc.bmi_and_height_to_weight,
          'description': _("With the same height, this is what weight you need to get different BMI thresholds"),
        },
        'thresholds': [
          {'text': _('Underweight [Severe]'),   'value': 0,    'style': 0},
          {'text': _('Underweight [Moderate]'), 'value': 16,   'style': 0},
          {'text': _('Underweight [Mild]'),     'value': 17,   'style': 0},
          {'text': _('Healthy'),                'value': 18.5, 'style': 1},
          {'text': _('Overweight'),             'value': 25,   'style': 2},
          {'text': _('Obese [Class 1]'),        'value': 30,   'style': 3},
          {'text': _('Obese [Class 2]'),        'value': 35,   'style': 3},
          {'text': _('Obese [Class 3]'),        'value': 40,   'style': 3},
        ],
      },
      self.whtr_result_row: {
        'calc-function': calc.whtr,
        'thresholds': [
          {'text': _('Healthy'),   'value': 0,                   'style': 1},
          {'text': _('Unhealthy'), 'value': calc.whtr_unhealthy, 'style': 2},
        ],
      },
      self.whr_result_row: {
        'calc-function': calc.whr,
        'thresholds': [
          {'text': _('Healthy'),    'value': 0,                   'style': 1},
          {'text': _('Overweight'), 'value': calc.whr_overweight, 'style': 2},
          {'text': _('Obese'),      'value': calc.whr_obese,      'style': 3},
        ],
      },
      self.bri_result_row: {
        'calc-function': calc.bri,
        'thresholds': [
          {'text': _('Very lean'),     'value': 0,    'style': 0},
          {'text': _('Lean'),          'value': 3.41, 'style': 1},
          {'text': _('Average'),       'value': 4.45, 'style': 1},
          {'text': _('Above average'), 'value': 5.46, 'style': 2},
          {'text': _('High'),          'value': 6.91, 'style': 3},
        ],
      },
    }
    # Setting stuff from settings
    window_width, window_height = settings['window-size']
    self.set_default_size(window_width, window_height)
    self.set_advanced_mode(settings['advanced-mode'])
    self.set_imperial(settings['measurement-system'])
    self.update_results()
    # Connecting stuff
    settings.connect('changed', self.on_settings_changed)
    self.simple_breakpoint.connect('apply', self.on_simple_breakpoint_apply)
    self.simple_breakpoint.connect('unapply', self.on_simple_breakpoint_unapply)
    self.advanced_breakpoint.connect('apply', self.on_advanced_breakpoint_apply)
    self.advanced_breakpoint.connect('unapply', self.on_advanced_breakpoint_unapply)
    self.connect("close-request", self.on_close_request)

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

  def get_inputs(self):
    settings = self.get_app().get_settings()
    inputs = {}
    for row in self.input_rows:
      if hasattr(row, 'get_centimetres'):
        value = row.get_centimetres()
      elif hasattr(row, 'get_kilograms'):
        value = row.get_kilograms()
      else:
        value = row.get_value()
      key = row.get_key()
      inputs[key] = value
      if settings['remember-inputs']:
        settings[key] = value
      else:
        settings.reset(key)
    return inputs

  def calc_row_values(self, row: widgets.ResultRow, inputs: dict) -> tuple:
    info = self.result_row_info.get(row)
    calc_function = info.get('calc-function')
    result = calc_function(inputs)
    thresholds = copy.deepcopy(info.get('thresholds'))
    for i in range(len(thresholds)):
      threshold = thresholds[i]
      value = threshold.get('value')
      if callable(value):
        thresholds[i]['value'] = value(inputs)
    return result, thresholds

  def update_results(self, *args):
    inputs = self.get_inputs()
    for row in self.result_row_info:
      result, thresholds = self.calc_row_values(row, inputs)
      row.set_result(result)
      row.set_feedback(result, thresholds)

  def on_result_row_info_clicked(self, row: widgets.ResultRow, button: Gtk.Button):
    settings = self.get_app().get_settings()
    dialog = widgets.ResultDialog(row)
    inputs = self.get_inputs()
    result, thresholds = self.calc_row_values(row, inputs)
    dialog.set_result(result)
    dialog.set_feedback(result, thresholds)
    if 'context' in self.result_row_info.get(row):
      description, thresholds = self.get_row_context(row)
      dialog.set_context(description, thresholds, bool(settings['measurement-system']))
    dialog.present(self)

  def get_row_context(self, row: widgets.ResultRow) -> tuple:
    settings = self.get_app().get_settings()
    info = self.result_row_info.get(row)
    thresholds = copy.deepcopy(info.get('thresholds'))
    context_info = info.get('context')
    description = context_info.get('description')
    calc_function = context_info.get('calc-function')
    inputs = self.get_inputs()
    for i in range(len(thresholds)):
      threshold = thresholds[i]
      value = calc_function(inputs, threshold.get('value'))
      thresholds[i]['value'] = value
    return description, thresholds

  def copy_result(self, row: widgets.ResultRow):
    value = row.get_result()
    Gdk.Clipboard.set(clipboard, value);
    self.show_toast(_("Result copied"))

  def show_toast(self, text):
    self.toast_overlay.dismiss_all()
    toast = Adw.Toast(title=text, timeout=1)
    self.toast_overlay.add_toast(toast)

  def set_imperial(self, measurement_system: int):
    imperial = bool(measurement_system)
    for row in self.input_rows:
      if hasattr(row, 'imperial'):
        row.set_imperial(imperial)

  # Handles changes to settings.
  def on_settings_changed(self, settings: Gio.Settings, key: str):
    update_functions = {
      'advanced-mode': self.set_advanced_mode,
      'measurement-system': self.set_imperial,
      'remember-inputs': self.update_results,
    }
    if key in update_functions:
      function = update_functions.get(key)
      value = settings[key]
      function(value)

  # Action after closing the app window.
  def on_close_request(self, *args):
    settings = self.get_app().get_settings()
    settings['window-size'] = self.get_size(horizontal), self.get_size(vertical)

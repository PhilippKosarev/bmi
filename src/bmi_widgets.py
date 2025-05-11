from gi.repository import Gtk, Adw, Gdk

# Helper functions
def in_to_cm(value): value *= 2.54; return value
def cm_to_in(value): value *= 1 / 2.54; return value
def kg_to_lb(value): value *= 2.204623; return value
def lb_to_kg(value): value *= 0.4535924; return value

class InputRow:
  def __init__(self):
    super(InputRow, self).__init__()
    self.row = Adw.SpinRow()
    self.row.set_numeric(True)
    self.adjustment = Gtk.Adjustment(step_increment=1, page_increment=10)
    self.row.set_adjustment(self.adjustment)
    self.row.set_digits(1)
    self.row.connect('changed', self.callback)
    self.function = None

  def update_range(self):
    if self.imperial:
      lower = self.range.get('lower').get('imperial')
      upper = self.range.get('upper').get('imperial')
    else:
      lower = self.range.get('lower').get('metric')
      upper = self.range.get('upper').get('metric')
    self.row.set_range(lower, upper)

  def get_range(self):
    return [self.range.get('lower').get('metric'), self.range.get('upper').get('metric')]

  def set_title(self, title: str):
    self.row.set_title(title)

  def set_tooltip(self, tooltip: str):
    self.row.set_tooltip_text(tooltip)

  def set_callback(self, function):
    self.function = function

  def callback(self, widget):
    if self.function is not None:
      exec(f"self.function()")

  def set_group(self, group):
    group.add(self.row)

# Distance input row (cm/in)
class DistanceRow(InputRow):
  def __init__(self):
    super(DistanceRow, self).__init__()
    self.row.set_subtitle(_('Centimetres'))
    self.imperial = False
    self.range = {
      'lower': {'metric': 0, 'imperial': cm_to_in(0)},
      'upper': {'metric': 0, 'imperial': cm_to_in(0)},
    }

  def set_value(self, value):
    self.row.set_value(value)

  def get_value(self):
    value = self.row.get_value()
    if self.imperial is True:
      value = in_to_cm(value)
    return value

  def set_range(self, lower, upper):
    self.range = {
    'lower': {'metric': lower, 'imperial': round(cm_to_in(lower), 0)},
    'upper': {'metric': upper, 'imperial': round(cm_to_in(upper), 0)},
    }
    self.update_range()

  def set_imperial(self, imperial: bool):
    if self.imperial is imperial:
      return
    value = self.row.get_value()
    if imperial is True:
      value = cm_to_in(value)
      self.row.set_subtitle(_('Inches'))
    else:
      value = in_to_cm(value)
      self.row.set_subtitle(_('Centimetres'))
    value = round(value, 0)
    self.imperial = imperial
    self.update_range()
    self.set_value(value)


# Weight input row (kg/lb)
class WeightRow(InputRow):
  def __init__(self):
    super(WeightRow, self).__init__()
    self.row.set_subtitle(_('Kilograms'))
    self.imperial = False
    self.range = {
      'lower': {'metric': 0, 'imperial': 0},
      'upper': {'metric': 0, 'imperial': 0},
    }

  def set_value(self, value):
    self.row.set_value(value)

  def get_value(self):
    value = self.row.get_value()
    if self.imperial is True:
      value = lb_to_kg(value)
    return value

  def set_range(self, lower, upper):
    self.range = {
      'lower': {'metric': lower, 'imperial': round(kg_to_lb(lower), 0)},
      'upper': {'metric': upper, 'imperial': round(kg_to_lb(upper), 0)},
    }
    self.update_range()

  def set_imperial(self, imperial: bool):
    if self.imperial is imperial:
      return
    value = self.row.get_value()
    if imperial is True:
      value = kg_to_lb(value)
      self.row.set_subtitle(_('Pounds'))
    else:
      value = lb_to_kg(value)
      self.row.set_subtitle(_('Kilograms'))
    value = round(value, 0)
    self.imperial = imperial
    self.update_range()
    self.set_value(value)


# Time input row (years)
class TimeRow(InputRow):
  def __init__(self):
    super(TimeRow, self).__init__()
    self.row.set_subtitle(_('Years'))

  def set_value(self, value):
    return self.row.set_value(value)

  def get_value(self):
    return self.row.get_value()

  def set_range(self, lower, upper):
    self.row.set_range(lower, upper)


# Gender input row
class GenderRow():
  def __init__(self, options: list):
    self.row = Adw.ComboRow()
    self.row.set_title(_("Gender"))
    self.gender_list = Gtk.StringList()
    self.function = None
    for item in options:
        self.gender_list.append(item)
    self.row.set_model(self.gender_list)
    self.row.connect('notify::selected-item', self.callback)

  def set_callback(self, function):
    self.function = function

  def callback(self, widget, parameter):
    if self.function is not None:
      exec(f"self.function()")

  def set_value(self, value: int):
    return self.row.set_selected(value)

  def get_value(self):
    return self.row.get_selected()

  def set_group(self, group):
    group.add(self.row)

  def set_tooltip(self, tooltip: str):
    self.row.set_tooltip_text(tooltip)


clipboard = Gdk.Display.get_default().get_clipboard()
class ResultRow:
  def __init__(self):
    self.row = Adw.ActionRow()
    self.row.add_css_class("heading")
    self.row.set_activatable(True)

    self.label = Gtk.Label(label='0.0')
    self.label.set_css_classes(["title-3"])
    self.set_style(0)
    self.row.add_suffix(self.label)

    self.toast_overlay = None
    self.function = None
    self.row.connect("activated", self.callback)

  def copy_result(self, value: str):
    print(f"Copied result '{value}'")
    Gdk.Clipboard.set(clipboard, value);
    # Creating and showing a toast
    if self.toast_overlay is not None:
      self.toast = Adw.Toast(title=_("Result copied"), timeout=1)
      self.toast_overlay.add_toast(self.toast)

  def callback(self, widget):
    self.copy_result(self.label.get_label())
    if self.function is not None:
      exec(self.function)

  def get_label(self):
    return self.label

  def get_toast_overlay(self):
    widget = self.row.get_parent()
    while True:
      name = widget.get_name()
      if name == 'AdwToastOverlay':
        return widget
      try:
        widget = widget.get_parent()
      except:
        print("No toast overlay found.")

  def set_title(self, title: str):
    self.row.set_title(title)

  def set_tooltip(self, tooltip: str):
    self.row.set_tooltip_text(tooltip)

  def set_style(self, style: int):
    self.row.remove_css_class("light-blue")
    self.row.remove_css_class("success")
    self.row.remove_css_class("warning")
    self.row.remove_css_class("error")
    if style == 0: self.row.add_css_class('light-blue')
    elif style == 1: self.row.add_css_class('success')
    elif style == 2: self.row.add_css_class('warning')
    elif style == 3: self.row.add_css_class('error')

  def set_callback(self, function):
    self.function = function

  def set_group(self, group):
    group.add(self.row)
    self.toast_overlay = self.get_toast_overlay()

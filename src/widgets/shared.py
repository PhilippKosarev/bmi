# Imports
from gi.repository import Gtk, Adw, Gio
from enum import Enum

# Variables:

# Should always be in the same order as the StringList of gender_input_row.
class Gender(Enum):
  AVERAGE = 0
  FEMALE = 1
  MALE = 2

styles = [
  'light-blue',
  'success',
  'warning',
  'error',
]

# Functions:

# Gets the nth child of a given widget, if not found raises AttributeError.
def get_nth_child(widget: Gtk.Widget, pos: int) -> Gtk.Widget or None:
  last_widget = widget
  for i in range(pos):
    if hasattr(widget, 'get_child'):
      widget = widget.get_child()
    elif hasattr(widget, 'get_first_child'):
      widget = widget.get_first_child()
    else:
      widget = None
    if widget is None:
      raise AttributeError('child', last_widget)
    last_widget = widget
  return widget

# Returns a list of all children of a given widgets.
def get_children(widget: Gtk.Widget) -> list:
  child = get_nth_child(widget, 1)
  if child is None:
    return []
  children = [child]
  while True:
    child = child.get_next_sibling()
    if child is None:
      return children
    children.append(child)

# Required because settings[key] = value does not return the `success` bool,
# unlike the setter functions, which are all type-specific.
def set_settings_value(settings: Gio.Settings, key: str, value):
  functions = {
    bool: settings.set_boolean,
    int: settings.set_int,
  }
  function = functions.get(type(value))
  return function(key, value)

def set_style(widget: Gtk.Widget, style_index: int):
  for style in styles:
    widget.remove_css_class(style)
  if style_index is not None:
    widget.add_css_class(styles[style_index])

# Conversion functions
def kg_to_lb(value: float) -> float:
  return value * 2.2046226218

def lb_to_kg(value: float) -> float:
  return value * 1 / kg_to_lb(1)

def in_to_cm(value):
  return value * 2.54

def cm_to_in(value):
  return value * (1 / in_to_cm(1))

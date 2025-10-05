# Imports
from gi.repository import Gtk, Adw, Gio
from enum import Enum

# Enums:

# Should always be in the same order as the StringList of gender_input_row.
class Gender(Enum):
  AVERAGE = 0
  FEMALE = 1
  MALE = 2

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

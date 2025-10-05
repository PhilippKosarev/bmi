# Imports
from gi.repository import Gtk, Adw, Gio, GObject

# Internal imports
from . import widgets
from .widgets.shared import *

# Internal functions
def on_settings_changed(self, param):
  set_inital_row_values(self)
  trigger_rows(self)

def set_inital_row_values(self):
  settings = self.get_settings()
  if settings is None:
    return
  for row in self.get_rows():
    key = row.get_key()
    value = settings[key]
    row.set_value(value)

def trigger_rows(self):
  for row in self.get_rows():
    self._on_row_value_changed(row)

@Gtk.Template(resource_path='/io/github/philippkosarev/bmi/preferences/preferences.ui')
class BmiPreferences(Adw.PreferencesDialog):
  __gtype_name__ = 'BmiPreferences'

  # Properties
  settings = GObject.Property(
    nick = 'settings',
    blurb = 'The assigned Gio.Settings',
    type = Gio.Settings,
  )

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.connect('notify::settings', on_settings_changed)
    for row in self.get_rows():
      row.connect(row.get_signal(), self._on_row_value_changed)

  def get_settings(self) -> Gio.Settings:
    return self.settings

  def set_settings(self, settings: Gio.Settings):
    self.settings = settings

  def _on_row_value_changed(self, row: Adw.ActionRow, param = None):
    settings = self.get_settings()
    if settings is None:
      return
    key = row.get_key()
    value = row.get_value()
    success = set_settings_value(settings, key, value)
    if not success:
      row.set_value(settings[key])
      toast = Adw.Toast(title=_("Error setting preferences value"))
      self.add_toast(toast)
      print(f"Error setting '{key}' to '{value}'.")

  def get_pages(self) -> list:
    navigation_view = self.get_child().get_child()
    navigation_stack = navigation_view.get_navigation_stack()
    page = list(navigation_stack)[0]
    child = page.get_child()
    toolbar_view = child.get_child()
    stack = toolbar_view.get_content()
    toolbar_view = list(stack)[0]
    view_stack = toolbar_view.get_content()
    return [page.get_child() for page in list(view_stack.get_pages())]

  def get_groups(self) -> list:
    groups = []
    for page in self.get_pages():
      box = get_nth_child(page, 4)
      children = get_children(box)
      groups += [
        widget for widget in children
        if isinstance(widget, Adw.PreferencesGroup)
      ]
    return groups

  def get_rows(self) -> list:
    rows = []
    for group in self.get_groups():
      rows += group.get_rows()
    return rows

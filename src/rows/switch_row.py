# Imports
from gi.repository import Gtk, Adw, Gio, GObject

# Internal imports
from .base_row import BaseRow

# Shorthands vars
center = Gtk.Align.CENTER

class SwitchRow(BaseRow):
  __gtype_name__ = 'SwitchRow'

  active = GObject.Property(
    nick = 'active',
    blurb = "The row's switch state",
    type = bool, default = False,
  )

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.switch = Gtk.Switch(valign=center, can_focus=False)
    self.add_suffix(self.switch)
    self.set_activatable_widget(self.switch)
    self.switch.connect('notify::active', self._on_switch_toggled)
    self.get_value = self.get_active
    self.set_value = self.set_active

  def get_active(self) -> bool:
    return self.active

  def set_active(self, active: bool):
    self.switch.set_active(active)

  def get_signal(self):
    return 'notify::active'

  def _on_switch_toggled(self, switch: Gtk.Switch, param):
    self.active = switch.get_active()

# Imports
from gi.repository import Gtk, Adw, Gio

# Shorthands vars
center = Gtk.Align.CENTER

class PreferencesSwitch(Adw.ActionRow):
    __gtype_name__ = 'PreferencesSwitch'

    def __init__(self, **kwargs):
      super().__init__(**kwargs)
      # Configuring the switch
      self.switch = Gtk.Switch(valign=center, can_focus=False)
      self.add_suffix(self.switch)
      self.set_activatable_widget(self.switch)
      # Object vars
      self.callback = None
      self.settings = None
      self.key = None

    def get_active(self):
      return self.switch.get_active()

    def set_active(self, active):
      self.switch.set_active(active)

    def on_switch_toggled(self, switch, param):
      active = self.get_active()
      if (self.settings is not None) and (self.key is not None):
        success = self.settings.set_boolean(self.key, active)
        if success is False:
          value = self.settings.get_boolean(self.key)
          self.set_active(value)
          return
      if self.callback is not None:
        self.callback(self, active)

    def set_callback(self, callback):
      self.callback = callback

    def set_setting(self, settings, key):
      self.settings = settings
      self.key = key
      self.set_active(settings.get_boolean(key))
      self.switch.connect('state-set', self.on_switch_toggled)

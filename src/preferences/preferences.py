# Imports
from gi.repository import Gtk, Adw, Gio

# Internal imports
from .preferences_switch import PreferencesSwitch

@Gtk.Template(resource_path='/io/github/philippkosarev/bmi/preferences/preferences.ui')
class BmiPreferences(Adw.PreferencesWindow):
    __gtype_name__ = 'BmiPreferences'

    # Important Widgets
    advanced_mode_row = Gtk.Template.Child()
    measurement_system_row = Gtk.Template.Child()
    remember_inputs_row = Gtk.Template.Child()

    def __init__(self, window, settings, **kwargs):
      super().__init__(**kwargs)
      # Object vars
      self.window = window
      self.settings = settings
      # Setting up setting rows
      ## Advanced Mode
      self.advanced_mode_row.set_setting(self.settings, 'advanced-mode')
      self.advanced_mode_row.set_callback(self.on_mode_changed)
      ## Measurement system
      self.measurement_system_row.set_selected(self.settings['measurement-system'])
      self.measurement_system_row.connect('notify::selected', self.on_measurements_changed)
      ## Remember inputs
      self.remember_inputs_row.set_setting(self.settings, 'remember-inputs')

    def on_mode_changed(self, row, active):
      self.window.set_advanced_mode(active)

    def on_measurements_changed(self, row, param):
      selected = self.measurement_system_row.get_selected()
      success = self.settings.set_int('measurement-system', selected)
      if success is False:
        value = self.settings['measurement-system']
        self.measurement_system_row.set_selected(value)
        return
      self.window.set_imperial(bool(selected))

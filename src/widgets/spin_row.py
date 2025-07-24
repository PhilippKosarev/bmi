# Imports
from gi.repository import GObject, Gtk, Adw

# Biggest and smallest signed integers GTK accepts
max_size = 2_147_483_647
min_size = -max_size

# Shorthand vars
center = Gtk.Align.CENTER

class SpinRow(Adw.ActionRow):
  __gtype_name__ = 'SpinRow'

  value = GObject.Property(type=int, default=0)
  lower = GObject.Property(type=int, default=min_size)
  upper = GObject.Property(type=int, default=max_size)
  digits = GObject.Property(type=int, default=0)
  callback = None

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    # Setting up self
    self.set_activatable(True)
    self.set_css_classes(['spin'])
    climb_rate = 1
    step_increment = 1
    page_increment = 10
    self.adjustment = Gtk.Adjustment.new(
      self.value, self.lower, self.upper, step_increment, page_increment, 0,
    )
    self.spin_button = Gtk.SpinButton(xalign=1, valign=center, hexpand=True)
    self.spin_button.configure(self.adjustment, climb_rate, self.digits)
    self.spin_button.set_hexpand(True)
    self.add_suffix(self.spin_button)
    # Connecting
    self.connect('notify::value', self.update_value)
    self.connect('notify::lower', self.update_lower)
    self.connect('notify::upper', self.update_upper)
    self.connect('notify::digits', self.update_digits)
    self.spin_button.connect('value-changed', self.on_value_changed)

  def update_value(self, row, param):
    self.adjustment.set_value(self.value)

  def update_lower(self, row, param):
    self.adjustment.set_lower(self.lower)

  def update_upper(self, row, param):
    self.adjustment.set_upper(self.upper)

  def update_digits(self, row, param):
    self.spin_button.set_digits(self.digits)

  def set_callback(self, callback):
    self.callback = callback

  def on_value_changed(self, spin_button):
    if self.callback is not None:
      self.callback(self)

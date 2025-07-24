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
  digits = GObject.Property(type=int, default=1)
  callback = None

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    # Setting up self
    self.set_size_request(260, 60)
    self.set_activatable(True)
    self.set_css_classes(['spin'])
    climb_rate = 1
    self.step_increment = 1
    self.page_increment = 10
    self.adjustment = Gtk.Adjustment.new(
      self.value, self.lower, self.upper, self.step_increment, self.page_increment, 0,
    )
    self.spin_button = Gtk.SpinButton(xalign=1, valign=center, hexpand=True)
    self.spin_button.configure(self.adjustment, climb_rate, self.digits)
    self.spin_button.set_hexpand(True)
    self.add_suffix(self.spin_button)
    # Connecting
    self.connect('notify::value', self.configure)
    self.connect('notify::lower', self.configure)
    self.connect('notify::upper', self.configure)
    self.connect('notify::digits', self.update_digits)
    self.spin_button.connect('value-changed', self.on_value_changed)

  def configure(self, row, param):
    self.adjustment.configure(
      self.value, self.lower, self.upper, self.step_increment, self.page_increment, 0
    )
    lower_width_chars = len(str(self.lower)) + self.digits
    upper_width_chars = len(str(self.upper)) + self.digits
    if lower_width_chars > upper_width_chars:
      self.spin_button.set_width_chars(lower_width_chars)
    else:
      self.spin_button.set_width_chars(upper_width_chars)

  def set_value(self, value):
    self.value = value

  def get_value(self):
    return self.adjustment.get_value()

  def set_digits(self, digits: int):
    self.digits = digits

  def update_digits(self, row, param):
    self.spin_button.set_digits(self.digits)

  def set_callback(self, callback):
    self.callback = callback

  def on_value_changed(self, spin_button):
    if self.callback is not None:
      self.callback(self)

  def get_name(self):
    return self.__class__.__name__

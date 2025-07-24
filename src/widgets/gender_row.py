# Imports
from gi.repository import Gtk, Adw

genders = [
  {'id': 'average', 'title': _("Average")},
  {'id': 'female',  'title': _("Female")},
  {'id': 'male',    'title': _("Male")},
]

def gender_id_to_int(gender_id):
  iteration = 0
  for item in genders:
    item_id = item.get('id')
    if gender_id == item_id:
      return iteration
    iteration += 1
  raise IndexError(f"Attempted to set gender row value to '{value}'")

# Class
class GenderRow(Adw.ComboRow):
  __gtype_name__ = 'GenderRow'
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.set_size_request(260, 60)
    self.set_title(_("Gender"))
    self.string_list = Gtk.StringList()
    for item in genders:
      title = item.get('title')
      self.string_list.append(title)
    self.set_model(self.string_list)
    self.connect('notify::selected-item', self.on_item_selected)
    # Object vars
    self.callback = None

  def set_value(self, value: int or str):
    if type(value) is int:
      return self.set_selected(value)
    if type(value) is str:
      gender_id = gender_id_to_int(value)
      return self.set_selected(gender_id)

  def get_value(self, return_type: int or str = str):
    if return_type is int:
      return self.get_selected()
    if return_type is str:
      return genders[self.get_selected()].get('id')

  def set_callback(self, callback):
    self.callback = callback

  def on_item_selected(self, row, param):
    if self.callback is not None:
      self.callback(self)

  def get_name(self):
    return 'GenderRow'

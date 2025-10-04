# main.py
#
# Copyright 2024 philipp
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# SPDX-License-Identifier: GPL-2.0-or-later

# Imports
import sys, gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GObject

# Internal imports
from .window import BmiWindow
from .preferences import BmiPreferences

# The main application singleton class
class BmiApplication(Adw.Application):

  settings = GObject.Property(
    nick = 'settings',
    blurb = "The application's Gio.Settings",
    type = Gio.Settings,
  )

  def __init__(self, version: str):
    super().__init__(
      application_id='io.github.philippkosarev.bmi',
      flags = Gio.ApplicationFlags.DEFAULT_FLAGS,
      version = version,
    )
    self.get_id = self.get_application_id
    self.set_settings(Gio.Settings.new(self.get_id()))
    # Application-wide shortcuts
    self.create_action('preferences', self.show_preferences, ['<primary>comma'])
    self.create_action('about', self.show_about, ['F1'])
    self.create_action('quit', self.on_quit, ['<primary>q', '<primary>w'])

  def set_settings(self, settings: Gio.Settings):
    self.settings = settings

  def get_settings(self) -> Gio.Settings:
    return self.settings

  # Shows the preferences dialog.
  def show_preferences(self, action, param):
    preferences = BmiPreferences()
    preferences.set_settings(self.get_settings())
    preferences.present(self.props.active_window)

  # Shows the about dialog.
  def show_about(self, action, param):
    # Creating about dialog
    about = Adw.AboutDialog(
      application_name  = 'BMI',
      application_icon  = self.get_id(),
      version           = self.get_version(),
      developer_name    = 'Philipp Kosarev',
      developers = [
        'Philipp Kosarev https://github.com/PhilippKosarev',
        'vikdevelop https://github.com/vikdevelop',
      ],
      artists = [
        'Philipp Kosarev https://github.com/PhilippKosarev',
      ],
      copyright    = '© 2024 Philipp Kosarev',
      license_type = 'GTK_LICENSE_GPL_2_0',
      website      = "https://github.com/philippkosarev/bmi",
      issue_url    = "https://github.com/philippkosarev/bmi/issues",
    )
    about.add_credit_section(
      _("Translators"),
      [
        'Sultaniiazov David https://github.com/x1z53',
        'Maksym Dilanian https://github.com/maksym-dilanian',
      ],
    )
    about.present(self.props.active_window)

  def on_quit(self, action, param):
    self.win.on_close_window(widget='')
    self.quit()

  # Called when the application is activated.
  def do_activate(self):
    # We raise the application's main window, creating it if necessary.
    self.win = self.props.active_window
    if not self.win:
      self.win = BmiWindow(application=self)
    self.win.present()

  def create_action(self, name, callback, shortcuts=None):
    action = Gio.SimpleAction.new(name, None)
    action.connect('activate', callback)
    self.add_action(action)
    if shortcuts:
      self.set_accels_for_action(f'app.{name}', shortcuts)

# The application's entry point.
def main(version):
  app = BmiApplication(version)
  return app.run(sys.argv)

pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'bmi' / 'widgets'

widget_sources = [
  '__init__.py',
  'widgets/shared.py',
  'widgets/preferences_dialog.py',
  'widgets/page.py',
  'widgets/group.py',
  'widgets/spin_row.py',
  'widgets/distance_row.py',
  'widgets/mass_row.py',
  'widgets/time_row.py',
  'widgets/gender_row.py',
  'widgets/result_row.py',
  'rows/base_row.py',
  'rows/switch_row.py',
  'rows/dropdown_row.py',
]

install_data(bmi_sources, install_dir: moduledir)
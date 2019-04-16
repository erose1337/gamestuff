import ast

import cefparser

def set_theme_colors(self, filename):
    self.show_status("Importing color options...")
    theme = cefparser.parse_filename(filename)
    theme_colors = self.theme.theme_colors
    for profile, values in theme["Theme Profiles"].iteritems():
        for key, value in values.iteritems():
            values[key] = ast.literal_eval(value)
            try:
                r, g, b, a = values[key]
            except TypeError:
                pass
            else:
                _color = theme_colors[profile][key]
                _color.r = r
                _color.g = g
                _color.b = b
                _color.a = a
                values[key] = _color
        theme_colors[profile].update(values)
    self.theme.update_theme_users()
    self.hide_status()

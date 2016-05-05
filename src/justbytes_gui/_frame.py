# Copyright (C) 2016 Anne Mulhern
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
# Anne Mulhern <mulhern@cs.wisc.edu>

"""
Highest level code for module.
"""
import abc
import Tkinter

from six import add_metaclass

import justbytes

from ._errors import GUIValueError

from ._gadgets import ChoiceEntry
from ._gadgets import JustEntry
from ._gadgets import MaybeEntry

from ._selectors import ChoiceSelector
from ._selectors import JustSelector
from ._selectors import MaybeSelector


@add_metaclass(abc.ABCMeta)
class Config(object):
    """
    Top level class for configuration gadgets.
    """
    # pylint: disable=too-few-public-methods

    CONFIG = abc.abstractproperty(doc="associated configuration")
    _FIELD_MAP = abc.abstractproperty(doc="map from field names to gadgets")

    def get(self):
        """
        Get a dictionary of values associated with this gadget.

        :returns: a dictionary of value
        :rtype: dict of str * object
        """
        kwargs = dict()

        for config_attr in sorted(self._FIELD_MAP.keys()):
            try:
                kwargs[config_attr] = self._field_vars[config_attr].get()
            except ValueError:
                raise GUIValueError(
                   "value for %s could not be converted" % config_attr
                )

        return kwargs

    def __init__(self, master, label_str):
        self._field_vars = dict()

        self.VALUE = Tkinter.LabelFrame(master, text=label_str)
        self.VALUE.pack({"side": "left"})

        for config_attr in sorted(self._FIELD_MAP.keys()):
            (label_text, widget_selector) = self._FIELD_MAP[config_attr]
            if isinstance(widget_selector, JustSelector):
                entry = JustEntry(
                   self.VALUE,
                   getattr(self.CONFIG, config_attr),
                   label_text,
                   widget_selector.python_type
                )
            elif isinstance(widget_selector, MaybeSelector):
                entry = MaybeEntry(
                   self.VALUE,
                   getattr(self.CONFIG, config_attr),
                   label_text,
                   widget_selector.python_type
                )
            elif isinstance(widget_selector, ChoiceSelector):
                entry = ChoiceEntry(
                   self.VALUE,
                   getattr(self.CONFIG, config_attr),
                   label_text,
                   widget_selector.choices
                )
            entry.widget.pack({"side": "top"})
            self._field_vars[config_attr] = entry

class StripConfig(Config):
    """
    Configuration gadget for stripping options.
    """
    # pylint: disable=too-few-public-methods

    CONFIG = justbytes.RangeConfig.DISPLAY_CONFIG.strip_config

    _FIELD_MAP = {
       "strip": ("Strip all trailing zeros?", JustSelector(bool)),
       "strip_exact": ("Strip trailing zeros if exact?", JustSelector(bool)),
       "strip_whole":
          (
             "Strip trailing zeros if exact whole number?",
             JustSelector(bool)
          )
    }


class DigitsConfig(Config):
    """
    Configuration for property of digits.
    """
    # pylint: disable=too-few-public-methods

    CONFIG = justbytes.RangeConfig.DISPLAY_CONFIG.digits_config

    _FIELD_MAP = {
       "separator": ("Separator:", JustSelector(str)),
       "use_caps": ("Use capital letters?", JustSelector(bool)),
       "use_letters": ("Use letters for digits?", JustSelector(bool))
    }


class MiscDisplayConfig(Config):
    """
    Miscellaneous display options.
    """
    # pylint: disable=too-few-public-methods

    CONFIG = justbytes.RangeConfig.DISPLAY_CONFIG

    _FIELD_MAP = {
       "show_approx_str":
          ("Indicate if value is approximate?", JustSelector(bool)),
       "show_base": ("Prefix with indicator for base?", JustSelector(bool))
    }


class ValueConfig(Config):
    """
    Configuration for choosing the value to display.
    """
    # pylint: disable=too-few-public-methods

    CONFIG = justbytes.RangeConfig.VALUE_CONFIG

    _FIELD_MAP = {
       "base": ("Base:", JustSelector(int)),
       "binary_units": ("Use IEC units?", JustSelector(bool)),
       "exact_value": ("Get exact value?", JustSelector(bool)),
       "max_places":
          ("Maximum number of digits right of radix:", MaybeSelector(int)),
       "rounding_method":
          (
             "Rounding method:",
             ChoiceSelector([
                (justbytes.ROUND_DOWN, "down"),
                (justbytes.ROUND_HALF_DOWN, "half down"),
                (justbytes.ROUND_HALF_UP, "half up"),
                (justbytes.ROUND_HALF_ZERO, "half 0"),
                (justbytes.ROUND_TO_ZERO, "to 0"),
                (justbytes.ROUND_UP, "up")
             ])
          )
    }


class RangeFrame(Tkinter.Frame):
    """
    Simple class to display a single Range value.
    """
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        self.value = None
        self.pack()

    def show(self):
        try:
            value_config = justbytes.ValueConfig(**self.VALUE.get())
        except (GUIValueError, justbytes.RangeError) as err:
            self.ERROR_STR.set(err)
            return

        self.ERROR_STR.set("")
        display_config = justbytes.RangeConfig.DISPLAY_CONFIG
        self.DISPLAY_STR.set(self.value.getString(value_config, display_config))

    def createWidgets(self):
        show = Tkinter.Button(self, text="Show", command=self.show)
        show.pack({"side": "bottom"})

        quit = Tkinter.Button(self, text="Quit", command=self.quit)
        quit.pack({"side": "bottom"})

        self.DISPLAY_STR = Tkinter.StringVar()
        self.DISPLAY_STR.set(str(self.value))
        display = Tkinter.Label(
           self,
           textvariable=self.DISPLAY_STR,
           font=("Helvetica", 32)
        )
        display.pack({"side": "top"})

        self.ERROR_STR = Tkinter.StringVar()
        self.ERROR_STR.set("")
        error = Tkinter.Label(self, textvariable=self.ERROR_STR, fg="red")
        error.pack({"side": "top"})

        self.VALUE = ValueConfig(self, "Value")

        self.DISPLAY = Tkinter.LabelFrame(self, text="Display")
        self.DISPLAY.pack({"side": "left"})

        self.DIGITS = DigitsConfig(self.DISPLAY, "Digits Options")

        self.STRIP = StripConfig(self.DISPLAY, "Strip Options")
        self.MISC = \
           MiscDisplayConfig(self.DISPLAY, "Miscellaneous Display Options")


def show(a_range):
    """
    Start a simple GUI to show display options for ``a_range``.

    :param Range a_range: the range to display
    """
    root = Tkinter.Tk()
    frame = RangeFrame(master=root)
    frame.value = a_range
    frame.createWidgets()
    frame.mainloop()
    root.destroy()

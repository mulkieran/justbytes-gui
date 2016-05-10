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
import decimal
import Tkinter

from six import add_metaclass

import justbytes

from ._errors import GUIValueError

from ._gadgets import Entry

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
            except (ValueError, decimal.InvalidOperation):
                raise GUIValueError(
                   "value for \"%s\" could not be converted" % config_attr
                )

        return kwargs

    def set(self, config):
        """
        Set the members according to ``config``.

        :param config: a configuration
        :type config: a justbytes configuration
        """
        for config_attr in self._FIELD_MAP.keys():
            self._field_vars[config_attr].set(getattr(config, config_attr))

    widget = property(lambda s: s.VALUE, doc="top level widget")

    def __init__(self, master, label_str):
        """
        Initializer.

        :param Tkinter.Widget master: the master widget
        :param str label_str: how to label the top-level widget
        """
        self._field_vars = dict()

        self.VALUE = Tkinter.LabelFrame(master, text=label_str)

        for config_attr in sorted(self._FIELD_MAP.keys()):
            (label_text, widget_selector) = self._FIELD_MAP[config_attr]
            entry = Entry.getWidget(
               self.VALUE,
               widget_selector,
               getattr(self.CONFIG, config_attr),
               label_text
            )
            entry.widget.pack({"side": "top"})
            self._field_vars[config_attr] = entry


class BaseConfig(Config):
    """
    Configuration gadget for base display.
    """
    # pylint: disable=too-few-public-methods

    CONFIG = justbytes.RangeConfig.DISPLAY_CONFIG.base_config

    _FIELD_MAP = {
       "use_prefix": ("Display base prefix?", JustSelector(bool)),
       "use_subscript": ("Display base subscript?", JustSelector(bool))
    }


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
          ("Indicate if value is approximate?", JustSelector(bool))
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
          (
             "Maximum number of digits right of radix:",
             MaybeSelector(JustSelector(int))
          ),
       "min_value":
          (
             "Bounding factor for non-fractional part:",
              JustSelector(decimal.Decimal)
          ),
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
          ),
       "unit":
          (
             "Unit:",
             MaybeSelector(
                ChoiceSelector(
                   [(u, str(u)) for u in justbytes.UNITS()]
                )
             )
          )
    }


class RangeFrame(Tkinter.Frame):
    """
    Simple class to display a single Range value.
    """
    # pylint: disable=too-many-instance-attributes

    def _get_button_frame(self):
        """
        Make the bottom button frame.

        :returns: the enclosing frame for the buttons
        :rtype: Tkinter.Frame
        """
        button_frame = Tkinter.Frame(self)

        quit_button = \
           Tkinter.Button(button_frame, text="Quit", command=self.quit)
        quit_button.pack({"side": "right"})

        reset_button = \
           Tkinter.Button(button_frame, text="Reset", command=self.reset)
        reset_button.pack({"side": "right"})

        show_button = \
           Tkinter.Button(button_frame, text="Show", command=self.show)
        show_button.pack({"side": "right"})

        return button_frame

    def __init__(self, master=None):
        """
        Initializer.

        :param Tkinter.Widget master: the master
        """
        Tkinter.Frame.__init__(self, master)
        self.value = None
        self.pack()

        button_frame = self._get_button_frame()
        button_frame.pack({"side": "bottom"})

        self.DISPLAY_STR = Tkinter.StringVar()
        display_label = Tkinter.Label(
           self,
           textvariable=self.DISPLAY_STR,
           font=("Helvetica", 32)
        )
        display_label.pack({"side": "top"})

        self.ERROR_STR = Tkinter.StringVar()
        self.ERROR_STR.set("")
        error = Tkinter.Label(self, textvariable=self.ERROR_STR, fg="red")
        error.pack({"side": "top"})

        self.VALUE = ValueConfig(self, "Value")
        self.VALUE.widget.pack({"side": "left"})

        display = Tkinter.LabelFrame(self, text="Display")
        display.pack({"side": "left"})

        self.BASE = BaseConfig(display, "Base Options")
        self.BASE.widget.pack({"side": "top"})
        self.DIGITS = DigitsConfig(display, "Digits Options")
        self.DIGITS.widget.pack({"side": "top"})
        self.STRIP = StripConfig(display, "Strip Options")
        self.STRIP.widget.pack({"side": "top"})
        self.MISC = MiscDisplayConfig(display, "Miscellaneous Display Options")
        self.MISC.widget.pack({"side": "top"})

    def reset(self):
        """
        Reset to defaults and show.
        """
        self.VALUE.set(justbytes.ValueConfig())

        display_config = justbytes.DisplayConfig()
        self.BASE.set(display_config.base_config)
        self.DIGITS.set(display_config.digits_config)
        self.STRIP.set(display_config.strip_config)
        self.MISC.set(display_config)

        self.show()

    def show(self):
        """
        Show the resulting string.
        """
        try:
            base_config = justbytes.BaseConfig(**self.BASE.get())
            value_config = justbytes.ValueConfig(**self.VALUE.get())
            digits_config = justbytes.DigitsConfig(**self.DIGITS.get())
            strip_config = justbytes.StripConfig(**self.STRIP.get())
            display_config = justbytes.DisplayConfig(
               base_config=base_config,
               digits_config=digits_config,
               strip_config=strip_config,
               **self.MISC.get()
            )
        except (GUIValueError, justbytes.RangeError) as err:
            self.ERROR_STR.set(err)
            return

        self.ERROR_STR.set("")
        self.DISPLAY_STR.set(self.value.getString(value_config, display_config))


def show(a_range):
    """
    Start a simple GUI to show display options for ``a_range``.

    :param Range a_range: the range to display
    """
    root = Tkinter.Tk()
    root.wm_title("Justbytes Range Viewer")
    frame = RangeFrame(master=root)
    frame.value = a_range
    frame.show()
    frame.mainloop()
    root.destroy()

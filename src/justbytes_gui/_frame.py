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

from six import add_metaclass

import Tkinter

import justbytes


@add_metaclass(abc.ABCMeta)
class GUIError(Exception):
    """
    Superclass of all errors for this package.
    """
    pass


class GUIValueError(GUIError):
    """
    Raised if argument value is bad.
    """
    pass


@add_metaclass(abc.ABCMeta)
class WidgetSelector(object):
    """
    An object, containing the information to select a widget.
    """
    pass

class JustSelector(WidgetSelector):
    """
    Widget only has to represent a single type.
    """

    def __init__(self, python_type):
        """
        Initializer.

        :param type python_type: the python type being handled
        """
        self.python_type = python_type


def getVar(python_type):
    """
    Returns a Tkinter variable for the given python type.

    :param type python_type: the python type
    :returns: appropriate Tkinter *Var object
    :rtype: Tkinter.Variable
    """
    if python_type == bool:
        return Tkinter.BooleanVar()
    if python_type == float:
        return Tkinter.DoubleVar()
    if python_type == int:
        return Tkinter.IntVar()
    if python_type == str:
        return Tkinter.StringVar()
    raise GUIValueError("Unexpected python_type %s" % python_type)


def getWidget(master, widget_selector, config, config_attr):
   """
   Get the widget for this python type.

   :param Tkinter.Widget master: the master widget
   :param WidgetSelector widget_selector: the widget_selector

   :returns: an appropriate variable and widget
   :rtype: tuple of Tkinter.Variable * Tkinter.Widget
   """
   if isinstance(widget_selector, JustSelector):
       python_type = widget_selector.python_type
       var = getVar(python_type)
       var.set(getattr(config, config_attr))
       if python_type == bool:
           return (var, Tkinter.Checkbutton(master, variable=var))
       if python_type in (int, float, str):
           return (var, Tkinter.Entry(master, textvariable=var))

   raise GUIValueError("Unexpected python_type %s" % python_type)


def getField(master, config, config_attr, label_text, widget_selector):
    """
    Get the significant parts of the field.

    :param Tkinter.Widget master: the master of this field
    :param object config: a justbytes configuration object
    :param str config_attr: the configuration attribute for this field
    :param str label_text: text to apply to the label
    :param WidgetSelector widget_selector: the widget selector

    :returns: the parts that make up the user input for the field
    :rtype: tuple of Tkinter.Variable * Tkinter.Widget * Tkinter.Label
    """
    label = Tkinter.Label(master, text=label_text)
    (var, widget) = getWidget(master, widget_selector, config, config_attr)
    return (var, widget, label)


class ValueConfig(object):

    CONFIG = justbytes.RangeConfig.VALUE_CONFIG

    _FIELD_MAP = {
       "base": ("Base:", JustSelector(int)),
       "binary_units": ("Use IEC units?", JustSelector(bool)),
       "exact_value": ("Get exact value?", JustSelector(bool))
    }

    def __init__(self):
        self._field_vars = dict()

    def create(self, master):
        self.VALUE = Tkinter.LabelFrame(master, text="Value")
        self.VALUE.pack({"side": "left"})

        for (index, config_attr) in enumerate(sorted(self._FIELD_MAP.keys())):
            (label_text, widget_selector) = self._FIELD_MAP[config_attr]
            (var, widget, label) = getField(
               self.VALUE,
               self.CONFIG,
               config_attr,
               label_text,
               widget_selector
            )
            label.grid(row=index, column=0)
            widget.grid(row=index, column=1)
            self._field_vars[config_attr] = var

    def get(self):
        kwargs = dict()

        for config_attr in sorted(self._FIELD_MAP.keys()):
            (_, widget_selector) = self._FIELD_MAP[config_attr]
            value = self._field_vars[config_attr].get()
            if isinstance(widget_selector, JustSelector):
                python_type = widget_selector.python_type
                try:
                    kwargs[config_attr] = python_type(value)
                except ValueError:
                    args = (config_attr, python_type)
                    raise GUIValueError(
                       "%s value must be convertible to %s" % args
                    )
            else:
                kwargs[config_attr] = value

        return kwargs


class RangeFrame(Tkinter.Frame):
    """
    Simple class to display a single Range value.
    """
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        self.value = None
        self.pack()

    def createStripOptions(self, master):
        config = justbytes.RangeConfig.DISPLAY_CONFIG.strip_config

        self.STRIP = Tkinter.LabelFrame(master, text="Strip")
        self.STRIP.pack({"side": "left"})

        self.STRIP_LABEL = Tkinter.Label(self.STRIP, text="Strip trailing zeros?")
        self.STRIP_CHECKBUTTON = Tkinter.Checkbutton(self.STRIP)
        if config.strip:
            self.STRIP__CHECKBUTTON.select()
        else:
            self.STRIP_CHECKBUTTON.deselect()
        self.STRIP_LABEL.grid(row=0, column=0)
        self.STRIP_CHECKBUTTON.grid(row=0, column=1)

    def createDigitsOptions(self, master):
        config = justbytes.RangeConfig.DISPLAY_CONFIG.digits_config

        self.DIGITS = Tkinter.LabelFrame(master, text="Digits")
        self.DIGITS.pack({"side": "left"})

        self.USE_CAPS_LABEL = Tkinter.Label(self.DIGITS, text="Use caps?")
        self.USE_CAPS_CHECKBUTTON = Tkinter.Checkbutton(self.DIGITS)
        if config.use_caps:
            self.USE_CAPS_CHECKBUTTON.select()
        else:
            self.USE_CAPS_CHECKBUTTON.deselect()
        self.USE_CAPS_LABEL.grid(row=0, column=0)
        self.USE_CAPS_CHECKBUTTON.grid(row=0, column=1)

        self.USE_LETTERS_LABEL = Tkinter.Label(self.DIGITS, text="Use letters?")
        self.USE_LETTERS_CHECKBUTTON = Tkinter.Checkbutton(self.DIGITS)
        if config.use_letters:
            self.USE_LETTERS_CHECKBUTTON.select()
        else:
            self.USE_LETTERS_CHECKBUTTON.deselect()
        self.USE_LETTERS_LABEL.grid(row=1, column=0)
        self.USE_LETTERS_CHECKBUTTON.grid(row=1, column=1)

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
        self.SHOW = Tkinter.Button(self, text="Show", command=self.show)
        self.SHOW.pack({"side": "bottom"})

        self.QUIT = Tkinter.Button(self, text="Quit", command=self.quit)
        self.QUIT.pack({"side": "bottom"})

        self.DISPLAY_STR = Tkinter.StringVar()
        self.DISPLAY_STR.set(str(self.value))
        self.DISPLAY = Tkinter.Label(
           self,
           textvariable=self.DISPLAY_STR,
           font=("Helvetica", 32)
        )
        self.DISPLAY.pack({"side": "top"})

        self.ERROR_STR = Tkinter.StringVar()
        self.ERROR_STR.set("")
        self.ERROR = Tkinter.Label(self, textvariable=self.ERROR_STR, fg="red")
        self.ERROR.pack({"side": "top"})

        self.VALUE = ValueConfig()
        self.VALUE.create(self)

        self.DISPLAY = Tkinter.LabelFrame(self, text="Display")
        self.DISPLAY.pack({"side": "left"})

        self.createDigitsOptions(self.DISPLAY)
        self.createStripOptions(self.DISPLAY)


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

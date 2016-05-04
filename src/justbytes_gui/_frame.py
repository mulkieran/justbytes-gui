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

import Tkinter

import justbytes


class GUIValueError(Exception):
    pass


class ValueConfig(object):

    CONFIG = justbytes.RangeConfig.VALUE_CONFIG

    def create(self, master):
        self.VALUE = Tkinter.LabelFrame(master, text="Value")
        self.VALUE.pack({"side": "left"})

        self.BASE_LABEL = Tkinter.Label(self.VALUE, text="Base:")
        self.BASE_ENTRY = Tkinter.Entry(self.VALUE)
        self.BASE_ENTRY.insert(0, self.CONFIG.base)
        self.BASE_LABEL.grid(row=0, column=0)
        self.BASE_ENTRY.grid(row=0, column=1)

        self.BINARY_UNITS_LABEL = \
           Tkinter.Label(self.VALUE, text="Use IEC units?")
        self.BINARY_UNITS_VAR = Tkinter.BooleanVar()
        self.BINARY_UNITS_VAR.set(self.CONFIG.binary_units)
        self.BINARY_UNITS_CHECKBUTTON = \
           Tkinter.Checkbutton(self.VALUE,variable=self.BINARY_UNITS_VAR)
        self.BINARY_UNITS_LABEL.grid(row=1, column=0)
        self.BINARY_UNITS_CHECKBUTTON.grid(row=1, column=1)

    def get(self):
        kwargs = dict()

        try:
            kwargs['base'] = int(self.BASE_ENTRY.get())
        except ValueError:
            raise GUIValueError("base value must be an integer greater than 1")

        kwargs['binary_units'] = self.BINARY_UNITS_VAR.get()

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

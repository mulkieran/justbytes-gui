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
Hierarchy of gadgets.
"""
import Tkinter

from ._errors import GUIValueError

from ._util import getVar


class JustEntry(object):
    """
    Entry for JustSelector.
    """

    def __init__(self, master, value, label_text, python_type):
        """
        Initializer.

        :param Tkinter.Widget master: the master of the top frame
        :param object value: the value of the configuration field
        :param str label_text: the label for the field
        :param type python_type: the simple type of the field

        :raises GUIValueError:
        """
        self.FRAME = Tkinter.LabelFrame(master, text=label_text)
        self.VAR = getVar(python_type)
        self.VAR.set(value)

        if python_type == bool:
            field = Tkinter.Checkbutton(self.FRAME, variable=self.VAR)
            field.pack()
            return

        if python_type in (int, float, str):
            field = Tkinter.Entry(self.FRAME, textvariable=self.VAR)
            field.pack()
            return

        raise GUIValueError("Unexpected python_type %s" % python_type)

    widget = property(lambda s: s.FRAME, doc="top-level widget")

    def get(self):
        """
        Get the value.

        :returns: the current value for the widget, converted to the type
        :rtype: object

        :raises ValueError:
        """
        return self.VAR.get()

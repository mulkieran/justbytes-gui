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
import abc
import Tkinter

from decimal import Decimal
from six import add_metaclass

from ._errors import GUIValueError

from ._util import getVar


@add_metaclass(abc.ABCMeta)
class Entry(object):
    """
    Top level class for gadgets.
    """
    # pylint: disable=too-few-public-methods

    @abc.abstractmethod
    def get(self):
        """
        Get the value.

        :returns: the current value for the widget, converted to the type
        :rtype: object

        :raises ValueError:
        """
        raise NotImplementedError() # pragma: no cover

    widget = abc.abstractproperty(doc="top-level widget")

class JustEntry(Entry):
    """
    Entry for JustSelector.
    """
    # pylint: disable=too-few-public-methods

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
        self.PYTHON_TYPE = python_type

        if python_type == bool:
            button = Tkinter.Checkbutton(self.FRAME, variable=self.VAR)
            button.pack()
            return

        if python_type in (int, str, Decimal):
            entry = Tkinter.Entry(self.FRAME, textvariable=self.VAR)
            entry.pack()
            return

        raise GUIValueError("Unexpected python_type %s" % python_type)

    widget = property(lambda s: s.FRAME, doc="top-level widget")

    def get(self):
        return self.PYTHON_TYPE(self.VAR.get())


class MaybeEntry(Entry):
    """
    Entry for maybe situation.
    """
    # pylint: disable=too-few-public-methods

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
        Tkinter.Label(self.FRAME, text="None:").pack({"side": "left"})

        self.NONE_VAR = getVar(bool)
        self.NONE_VAR.set(value is None)
        button = Tkinter.Checkbutton(self.FRAME, variable=self.NONE_VAR)
        button.pack({"side": "left"})

        Tkinter.Label(self.FRAME, text="OR").pack({"side": "left"})

        self.VAR = getVar(python_type)
        self.VAR.set(value)
        entry = Tkinter.Entry(self.FRAME, textvariable=self.VAR)
        entry.pack({"side": "left"})

    widget = property(lambda s: s.FRAME, doc="top-level widget")

    def get(self):
        return None if self.NONE_VAR.get() else self.VAR.get()


class ChoiceEntry(Entry):
    """
    Entry for ChoiceSelector.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, master, value, label_text, choices):
        """
        Initializer.

        :param Tkinter.Widget master: the master of the top frame
        :param object value: the value of the configuration field
        :param str label_text: the label for the field
        :param choices: the list of choices available, with names
        :type choices: list of object * str

        :raises GUIValueError:
        """
        self.FRAME = Tkinter.LabelFrame(master, text=label_text)
        self.VAR = getVar(int)
        self._CHOICES = dict()
        self._INDICES = []

        for (index, (choice, choice_name)) in enumerate(choices):
            b = Tkinter.Radiobutton(
               self.FRAME,
               text=choice_name,
               variable=self.VAR,
               value=index
            )
            b.pack(anchor=Tkinter.W)
            self._CHOICES[choice] = index
            self._INDICES.append(choice)

        if value is None:
            self.VAR.set(-1)
        else:
            self.VAR.set(self._CHOICES[value])

    widget = property(lambda s: s.FRAME, doc="top-level widget")

    def get(self):
        index = self.VAR.get()
        if index == -1:
            return None
        else:
            return self._INDICES[index]

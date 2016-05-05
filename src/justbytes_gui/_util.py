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

from ._errors import GUIValueError 

from ._selectors import JustSelector


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


def convertValue(value, widget_selector):
    """
    Convert a value according to its widget selector.

    :param object value: value to convert
    :param WidgetSelector widget_selector: the widget selector
    :returns: converted value
    :rtype: object
    """
    if isinstance(widget_selector, JustSelector):
        return value

    raise GUIValueError("Unexpected WidgetSelector %s" % widget_selector)

#===================================================================
# Module with functions to save & restore qt widget values
# Written by: Alan Lilly 
# Website: http://panofish.net
#===================================================================


from PyQt4.QtGui import *
import inspect


def strtobool(astr):
    return astr == True


def guisave(self):
    # Save geometry
    settings = self.settings
    for name, obj in inspect.getmembers(self.ui):
        if isinstance(obj, QComboBox):
            name = obj.objectName()  # get combobox name
            index = obj.currentIndex()  # get current index from combobox
            text = obj.itemText(index)  # get the text for current index
            settings.setValue(name, text)  # save combobox selection to registry

        if isinstance(obj, QLineEdit):
            name = obj.objectName()
            value = obj.text()
            settings.setValue(name, value)  # save ui values, so they can be restored next time

        if isinstance(obj, QCheckBox):
            name = obj.objectName()
            state = obj.isChecked()
            settings.setValue(name, state)

        if isinstance(obj, QRadioButton):
            name = obj.objectName()
            value = obj.isChecked()  # get stored value from registry
            settings.setValue(name, value)

        if isinstance(obj, QSpinBox):
            name = obj.objectName()
            state = obj.value()
            settings.setValue(name, state)

def guidebug(self):
    # debug UI
    settingsDebug = []
    settings = self.settings
    for name, obj in inspect.getmembers(self.ui):
        if isinstance(obj, QComboBox):
            name = obj.objectName()  # get combobox name
            index = obj.currentIndex()  # get current index from combobox
            text = obj.itemText(index)  # get the text for current index\
            settingsDebug.append((name, text))

        if isinstance(obj, QLineEdit):
            name = obj.objectName()
            value = obj.text()
            settingsDebug.append((name, value))

        if isinstance(obj, QCheckBox):
            name = obj.objectName()
            state = obj.isChecked()
            settingsDebug.append((name, state))

        if isinstance(obj, QRadioButton):
            name = obj.objectName()
            value = obj.isChecked()  # get stored value from registry
            settingsDebug.append((name, value))

        if isinstance(obj, QSpinBox):
            name = obj.objectName()
            state = obj.value()
            settingsDebug.append((name, state))

    with open("settingsLog_" + str(self.deviceName.text()) + ".txt", "a") as f:
        for key, value in settingsDebug:
            f.write("[" + str(key) + "] " + str(value) + "\n")
        f.write("\n")

def guirestore(self):
    settings = self.settings
    for name, obj in inspect.getmembers(self.ui):
        if isinstance(obj, QComboBox):
            index = obj.currentIndex()  # get current region from combobox
            # text   = obj.itemText(index)   # get the text for new selected index
            name = obj.objectName()

            value = (settings.value(name))

            if value == "":
                continue

            index = obj.findText(value)  # get the corresponding index for specified string in combobox

            if index == -1:  # add to list if not found
                obj.insertItems(0, [value])
                index = obj.findText(value)
                obj.setCurrentIndex(index)
            else:
                obj.setCurrentIndex(index)  # preselect a combobox value by index

        if isinstance(obj, QLineEdit):
            name = obj.objectName()
            value = (settings.value(name))  # get stored value from registry
            obj.setText(value.toString())  # restore lineEditFile

        if isinstance(obj, QCheckBox):
            name = obj.objectName()
            value = settings.value(name)  # get stored value from registry
            if value != None:
                obj.setChecked(strtobool(value))  # restore checkbox

        if isinstance(obj, QRadioButton):
            name = obj.objectName()
            value = settings.value(name)  # get stored value from registry
            if value != None:
                obj.setChecked(strtobool(value))

        if isinstance(obj, QSpinBox):
            name = obj.objectName()
            value = settings.value(name)
            if value != None:
                obj.setValue(value.toInt()[0]) # toInt returns tuple??
#!/bin/sh
set -x

if [ -e /host/ubuntu ]; then
    zip -r /host/ubuntu2/installation-logs.zip /var/log
fi
if [ -e /isodevice/ubuntu ]; then
    zip -r /isodevice/ubuntu2/installation-logs.zip /var/log
fi

msg="The installation failed. Logs have been saved in: /ubuntu2/installation-logs.zip.\n\nNote that in verbose mode, the logs may include the password.\n\nThe system will now reboot."
if [ -x /usr/bin/zenity ]; then
    zenity --error --text "$msg"
elif [ -x /usr/bin/kdialog ]; then
    kdialog --msgbox "$msg"
elif [ -x /usr/bin/Xdialog ]; then
    Xdialog --msgbox "$msg"
fi

reboot

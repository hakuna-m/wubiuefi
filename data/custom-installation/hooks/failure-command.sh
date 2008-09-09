#!/bin/sh
set -x

if [ -e /host/ubuntu ]; then
    zip -r /host/ubuntu/installation-logs.zip /var/log
fi
if [ -e /isodevice/ubuntu ]; then
    zip -r /isodevice/ubuntu/installation-logs.zip /var/log
fi

msg="The installation failed. Logs have been saved in: /ubuntu/installation-logs.zip.\n\nNote that in verbose mode, the logs may include the password.\n\nThe system will now reboot."
if [ -x /usr/bin/zenity ]; then
    zenity --error --text "$msg"
elif [ -x /usr/bin/kdialog ]; then
    kdialog --msgbox "$msg"
elif [ -x /usr/bin/Xdialog ]; then
    Xdialog --msgbox "$msg"
fi

reboot

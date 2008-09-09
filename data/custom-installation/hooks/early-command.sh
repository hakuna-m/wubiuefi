#!/bin/sh
set -x

debug(){	
	if [ -x /sbin/usplash_write ]; then
		/sbin/usplash_write "QUIT"
	fi
	modprobe -Qb i8042
	modprobe -Qb atkbd
	echo "DEBUG"
	PS1='(initramfs) ' /bin/sh -i </dev/console >/dev/console 2>&1
}

#~ mount -o remount,rw /root/isodevice || true
#~ mount -o remount,ro /root/cdrom || true
#~ mount -o remount,rw /root || true

#load extra templates
#~ chroot /root /lib/partman/debconf-loadtemplate partman-auto-loop /lib/partman/extra.templates || true

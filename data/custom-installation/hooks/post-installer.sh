#!/bin/sh
set -x

if [ -f /custom-installation/patch/loop-remount ]; then
	mkdir -p /target/etc/initramfs-tools/hooks
	cp  /custom-installation/patch/loop-remount /target/etc/initramfs-tools/hooks/loop-remount
	chmod +x  /target/etc/initramfs-tools/hooks/loop-remount
fi

##
## Replacement for package lupin-support
##
if [ -f /custom-installation/patch/grub-install ]; then
	mkdir -p /target/usr/local/sbin
	cp /custom-installation/patch/grub-install /target/usr/local/sbin/grub-install
	chmod +x /target/usr/local/sbin/grub-install
fi
if [ -f /custom-installation/patch/grub-mkimage-lupin ] ; then
	mkdir -p /target/usr/local/sbin
	cp /custom-installation/patch/grub-mkimage-lupin /target/usr/local/sbin/grub-mkimage-lupin
	chmod +x /target/usr/local/sbin/grub-mkimage-lupin
fi
if [ -f /custom-installation/patch/10_lupin ] ; then
	mkdir -p /target/etc/grub.d
	cp /custom-installation/patch/10_lupin /target/etc/grub.d/10_lupin
	chmod +x /target/etc/grub.d/10_lupin
fi

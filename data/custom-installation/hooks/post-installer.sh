#!/bin/sh
set -x

if [ -f /custom-installation/patch/loop-remount ]; then
	mkdir -p /target/etc/initramfs-tools/hooks
	cp  /custom-installation/patch/loop-remount /target/etc/initramfs-tools/hooks/loop-remount
	chmod +x  /target/etc/initramfs-tools/hooks/loop-remount
fi

if [ -f /custom-installation/patch/grub-install ] && [ -f /custom-installation/patch/grub-install-efi ] ; then
	mkdir -p /target/usr/local/sbin
	cp /custom-installation/patch/grub-install /target/usr/local/sbin/grub-install
	chmod +x /target/usr/local/sbin/grub-install
	if [ -d /sys/firmware/efi ]; then
		cp /custom-installation/patch/grub-install-efi /target/usr/local/sbin/grub-install-efi
		chmod +x /target/usr/local/sbin/grub-install-efi
	fi
        cp /custom-installation/patch/grub-mkimage-lupin /target/usr/local/sbin/grub-mkimage-lupin
	chmod +x /target/usr/local/sbin/grub-mkimage-lupin
fi


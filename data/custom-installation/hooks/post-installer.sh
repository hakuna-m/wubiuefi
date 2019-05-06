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
	if [ -d /sys/firmware/efi ]; then
		chmod +x /target/usr/local/sbin/grub-install
		cp /custom-installation/patch/grub-install-efi /target/usr/local/sbin/grub-install-efi
		chmod +x /target/usr/local/sbin/grub-install-efi
	fi
	if [ -f /custom-installation/patch/grub-install ] ; then
		cp /custom-installation/patch/grub-mkimage-lupin /target/usr/local/sbin/grub-mkimage-lupin
		chmod +x /target/usr/local/sbin/grub-mkimage-lupin
	fi
	if [ -f /custom-installation/patch/lupin-grub-install ] ; then
		mkdir -p /target/etc/grub.d
		cp /custom-installation/patch/lupin-grub-install /target/etc/grub.d/10_lupin_grub_install
		chmod +x /target/etc/grub.d/10_lupin_grub_install
	fi
fi

arch=$(dpkg --print-architecture)
if [ ! -f /etc/grub.d/10_lupin ] && [ -f /custom-installation/packages/lupin-support/*$arch.deb ] ; then
	mkdir -p /var/cache/driver-updates
	cp /custom-installation/packages/lupin-support/*$arch.deb /var/cache/driver-updates/.
fi

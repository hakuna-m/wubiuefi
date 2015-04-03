#!/bin/sh
set -x

if [ -f /custom-installation/patch/loop-remount ]; then
	mkdir -p /target/etc/initramfs-tools/hooks
	cp  /custom-installation/patch/loop-remount /target/etc/initramfs-tools/hooks/loop-remount
	chmod +x  /target/etc/initramfs-tools/hooks/loop-remount
fi

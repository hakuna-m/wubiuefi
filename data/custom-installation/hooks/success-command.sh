#!/bin/sh
set -x

#Override target
if [ -d /custom-installation ]; then 
    cp -af /custom-installation/target-override/* /target/ || true
    rm -rf /custom-installation/target-override* || true
fi

#usplash.conf is sometimes incorrect 
#https://bugs.launchpad.net/ubuntu/+source/ubiquity/+bug/150930
#better wrong geometry than black screen
#~ echo '
#~ xres=1024
#~ yres=768
#~ ' > /etc/usplash.conf

#Install external packages
if [ -d /custom-installation/packages ]; then 
    cp -af /custom-installation/packages /target/tmp/custom-packages || true
    mount -o bind /proc /target/proc || true
    mount -o bind /dev /target/dev || true 
    for package in $(ls /custom-installation/packages); do
        package=$(basename $package)
        chroot /target /usr/bin/dpkg -i /tmp/custom-packages/$package || true
    done
    umount /target/proc || true
    umount /target/dev || true 
fi

#remove preseed file and menu.lst
#rm /host/ubuntu/install/custom-installation/preseed.cfg || true
#rm /host/ubuntu/install/boot/grub/menu.lst || true
rm -rf /host/ubuntu/install || true


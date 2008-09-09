#!/bin/sh
set -x

modules='
megaraid
aacraid
libata
sd_mod
scsi_mod
ehci-hcd
uhci-hcd
ohci-hcd
libusual
usb-storage
ahci
ata_piix
pata_sis
pdc_adma
sata_inic162x
sata_mv
sata_nv
sata_promise
sata_qstor
sata_sil24
sata_sil
sata_sis
sata_svw
sata_sx4
sata_uli
sata_via
sata_vsc
nls_utf8
nls_cp437
nls_iso8859-1
'

#~ for module in $modules; do
	#~ modprobe $module || true
#~ done

1. Introdution

This utility is used to install GRUB4DOS to the MBR of hard disk or image file.

grubinst.exe is a console mode program. It mimics the behavior of the DOS/Linux
utility bootlace.com from TinyBit's GRUB4DOS package. But unlike bootlace.com,
grubinst is writen completely in C and can be compiled to run in OSs like
Windows NT/2K/XP, Linux and FreeBSD.

grubinst_gui.exe is a GUI frontend to grubinst.exe. It provides a friendly
interface to users who are not familiar whith the command line environment.
Currently, grubinst_gui.exe only runs in Windows OSs.

Please note that these utilities only install MBR, it DOES NOT copy GRLDR to
your partition or configure menu.lst, neither does it modify boot.ini to enable
booting from the NT boot manager. To know more about such things, please refers
to README_GRUB4DOS.txt which contains information about the GRUB4DOS package.

Also note that the current version of grubinst doesn't support modify the MBR
of hard disk in Windows 95/98/ME. For those OSs, bootlace.com should be used
instead.

2. Features of grubinst

2.1 Use special name to represent devices

In grubinst, you can use special filename to represent hard disks and floppies.

(hdN)
Hard disk device N. In Linux, (hd0) - (hd3) equals to /dev/hda - /dev/hdd. In
FreeBSD, (hd0) - (hd3) equals to /dev/ad0 - /dev/ad3. In Windows, (hdN) equals
to \\.\PHYSICALDRIVEN

(hdN,P)
Partition P on hard disk N. Primary partition is 0-3, extended partition starts
at 4.

(fdN)
Floppy device N. In Linux/FreeBSD, (fdN) equals to /dev/fdN. In Windows, (fd0)
and (fd1) equals to drive A: and B:.

(fdN,P)
Partition P on floppy N.

Note 1. bootlace.com use numbers to represent devices. Floppies starts with 0,
and hard disks starts with 0x80.

Note 2. In bash/csh shell, () have special meaning. So you need to wrap the
device name with "" or ''.

Note 3. The 6-series of FreeBSD doesn't allow you to access a hard disk device
which has been open. This means you can't modify the MBR of your currently used
hard disk. Older series of FreeBSD don't have this problem.

2.2 Save/Restore function

Normally, the original MBR is only one sector long, it's stored in the second
sector of the new GRLDR MBR. You can restore it using --restore-prevmbr option.
However, if the original MBR is longer than one sector, for instance, you have
other boot manager installed, then GRLDR MBR dones't have room to hold it. In
this case, you should use --save=FILENAME to save the original MBR to an
external file, and use --restore=FILENAME to restore it.

Starts from version 1.1, --save=FILENAME and --restore=FILENAME also works for
partition boot sector. --restore-prevmbr doesn't work with partitions.

Note 1. In version 1.0.1, --save=FN and --restore=FN are called --save-mbr=FN
and --restore-mbr=FN, I remove the mbr part becase it now works for mbr and
boot sector.

Example 1. Install GRLDR to MBR/BS, and save the original MBR/BS to an external
file.

	grubinst --save=FILENAME DEVICE_OR_FILE

Example 2. Restore MBR from previous one sector MBR

	grubinst --restore_prevmbr DEVICE_OR_FILE

Example 3. Restore MBR/BS from external file

	grubinst --restore=FILENAME DEVICE_OR_FILE

2.3 Partition and floppy support (New in version 1.1)

You can use --list-part to list all partitions in device or file.

	grubinst --list-part DEVICE_OR_FILE

This option is diagnostic, it won't actually install GRLDR.

To install GRLDR to partition, just use the proper partition name, or use
--install-partition=I option to set the partition number. You don't need to
worry about file system type, as they are probed automatically. Support file
system are FAT12, FAT16, FAT32, NTFS and Ext2.

To install GRLDR to floppy image, you need to use the --floppy option.

Note 1. If you install GRLDR Boot Record to a floppy or a partition, the floppy
or partition will boot solely grldr, and your original IO.SYS(DOS/Win9x/Me) and
NTLDR(WinNT/2K/XP) will become unbootable. This is because the original boot
record of the floppy or partition was overwritten. There is no such problem
when installing GRLDR Boot Record onto the MBR. Update: Some NTLDR/IO.SYS/
KERNEL.SYS files can be directly chainloaded in the latest GRUB4DOS.

Note 2. You can use --start-sector=B option to specific the absolute address of
the start sector of partition, but we don't recommend it, as grubinst can
extract the information from the partition table in MBR.

Note 3. You can use --verbose option to see more information about the
partition on which you install GRLDR. It is good pratice to first use
--read-only and --verbose to verify the partition before actually installing
GRLDR.

	grubinst --read-only --verbose (hd0,0)

Output:

	Part Fs: 0B (FAT32)
	Part Leng: 1542240
	Start sector: 1028160
	Image type: FAT32
	Read only mode

Note 4. Option --floppy=N do exactly the same thing as --install-partition=I.
It's here just to improve the compatibility with bootlace.com.

2.4 Short options (New in version 1.1)

Some options have short counterparts.

-h		--help
-v		--verbose
-l		--list-part
-s=FN		--save=FN
-r=FN		--restore=FN
-r		--restore-prevmbr
-t		--read-only
-t=T		--timeout=T
-k=K		--hot-key=K
-f		--floppy
-p=I		--install-partition=I
-o		--output
-b=FN		--boot-file=FN
-2		--grub2

Note 1. In order to achive compatiblility between gcc and vc6, I don't use the
getopt function to parse options. Therefore, combining short options doesn't
work. For example, -vl is not equal to -v -l.

2.5 Key code translation (New in version 1.1)

In option --hot-key=K, you can use symbol names instead of raw codes. Raw code
is still accepted, but they need to start with the hexadecimal prefix 0x.

Support key names are: A-Z, 0-9, F1-F12, - = [ ] ; ' . \ , / , BACKSPACE, DEL,
DOWN, END, ENTER, ESC, HOME, INS, KEY-5, KEY-*, KEY--, KEY-+, KEY-/, LEFT,
PGDN, PGUP, PRRTSC, RIGHT, SPACE, TAB and UP.

Support prefix are: shift-, ctrl- and alt-.

Note 1. You can't use more that one prefix. For example ctrl-alt-A is not
valid.

Note 2. Some character have special meaning to shell, so you need to wrap them
with "" or '' ('' can't be used in cmd.exe) . For example,

	grubinst "--hot-key=;"	DEVICE_OR_FILE

or

	grubinst "--hot-key=ctrl-\\" DEVICE_OR_DEVICE

Note 3. Key name is case insensitive. Therefore, ctrl-a, CTRL-A and Ctrl-A are
all the same.

Note 4. To see the raw code of a key name, you can use --verbose option. For
example:

	grubinst --verbose --hot-key=ctrl-a

Output:
	Key CTRL-A : 0x1E01
	grubinst: No filename specified

You can ignore the error message as we are not actually installing GRLDR.

2.6 Change boot file name and load segment (New in 1.1 beta6)

You can 

2.7 Grub2 support (New in 1.1 beta6)

2.8 Loading via NT boot manager

2.9 Usage

Usage:
	grubinst  [OPTIONS]  DEVICE_OR_FILE

OPTIONS:

	--help,-h		Show usage information

	--pause			Pause before exiting (used by GUI)

	--version		Show version information

	--verbose,-v		Verbose output

	--list-part,-l		List all logical partitions in DEVICE_OR_FILE

	--save=FN,-s=FN		Save the orginal MBR/BS to FN

	--restore=FN,-r=FN	Restore MBR/BS from previously saved FN

	--restore-prevmbr,-r	Restore previous MBR saved in the second sector
				of DEVICE_OR_FILE

	--read-only,-t		do everything except the actual write to the
				specified DEVICE_OR_FILE. (test mode)

	--no-backup-mbr		do not copy the old MBR to the second sector of
				DEVICE_OR_FILE.

	--force-backup-mbr	force the copy of old MBR to the second sector
				of DEVICE_OR_FILE.(default)

	--mbr-enable-floppy	enable the search for GRLDR on floppy.(default)

	--mbr-disable-floppy	disable the search for GRLDR on floppy.

	--mbr-enable-osbr	enable the boot of PREVIOUS MBR with invalid
				partition table (usually an OS boot sector).
				(default)

	--mbr-disable-osbr	disable the boot of PREVIOUS MBR with invalid
				partition table (usually an OS boot sector).

	--duce			disable the feature of unconditional entrance
				to the command-line.

	--boot-prevmbr-first	try to boot PREVIOUS MBR before the search for
				GRLDR.

	--boot-prevmbr-last	try to boot PREVIOUS MBR after the search for
				GRLDR.(default)

	--preferred-drive=D	preferred boot drive number, 0 <= D < 255.

	--preferred-partition=P	preferred partition number, 0 <= P < 255.

	--time-out=T,-t=T	wait T seconds before booting PREVIOUS MBR. if
				T is 0xff, wait forever. The default is 5.

	--hot-key=K,-k=K	if the desired key K is pressed, start GRUB
				before booting PREVIOUS MBR. K is a word
				value, just as the value in AX register
				returned from int16/AH=1. The high byte is the
				scan code and the low byte is ASCII code. The
				default is 0x3920 for space bar.

	--floppy,-f		if DEVICE_OR_FILE is floppy, use this option.

	--floppy=N		if DEVICE_OR_FILE is a partition on a hard
				drive, use this option. N is used to specify
				the partition number: 0,1,2 and 3 for the
				primary partitions, and 4,5,6,... for the
				logical partitions.

	--sectors-per-track=S	specifies sectors per track for --floppy.
				1 <= S <= 63, default is 63.

	--heads=H		specifies number of heads for --floppy.
				1 <= H <= 256, default is 255.

	--start-sector=B	specifies hidden sectors for --floppy=N.

	--total-sectors=C	specifies total sectors for --floppy.
				default is 0.

	--lba			use lba mode for --floppy. If the floppy BIOS
				has LBA support, you can specify --lba here.
				It is assumed that all floppy BIOSes have CHS
				support. So you would rather specify --chs.
				If neither --chs nor --lba is specified, then
				the LBA indicator(i.e., the third byte of the
				boot sector) will not be touched.

	--chs			use chs mode for --floppy. You should specify
				--chs if the floppy BIOS does not support LBA.
				We assume all floppy BIOSes have CHS support.
				So it is likely you want to specify --chs.
				If neither --chs nor --lba is specified, then
				the LBA indicator(i.e., the third byte of the
				boot sector) will not be touched.

	--install-partition=I	Install the boot record onto the boot area of
	-p=I			partition number I of the specified hard drive
				or harddrive image DEVICE_OR_FILE.

        --boot-file=F,-b=F      Change the name of boot file.

        --load-seg=S            Change load segment for boot file.

        --grub2,-2              Load grub2 kernel g2ldr instead of grldr.

        --output,-o             Save embeded grldr.mbr to DEVICE_OR_FILE.

Example 1: Install GRLDR MBR to the first hard disk

	grubinst (hd0)

Example 2: Install GRLDR MBR to the disk image disk.dsk

	grubinst disk.dsk

Example 3: Install GRLDR to the first primary partition

	grubinst (hd0,0)

or

	grubinst --install-partition=0 (hd0)

or

	grubinst --start-sector=63 --install-partition=0 (hd0)

If the first partition starts from sector 63. This kind of usage is not
recommended, as the value specified in --start-sector will overwrite the one
extracted from the partition table.

Example 4. Install GRLDR to a floppy device or image

	grubinst (fd0)

	grubinst --floppy floppy.img

If you use floppy device, you can omit the --floppy option.

Example 5: Load GRUB only if you press CRTL-F1 in the first 10 second of
booting.

	grubinst --boot-prevmbr-first --hot-key=ctrl-f1 --time-out=10 (hd0)

Example 6: Same as above, but use short options.

	grubinst --boot-prevmbr-first -k=ctrl-f1 -t=10 (hd0)

3. Features of grubinst_gui

a) Save/Restore operation

The operation of save/restore boxes is described as follows:

If neither "Restore from file" nor "Restore from PrevMBR" is cheked, the
program would backup the original MBR/BS to FILENAME if it's set in the
"Save File".

If "Restore from file" is checked, the program would restore the MBR/BS from
FILENAME which is set in "Save File". FILENAME must not be empty, otherwise an
error message is printed. In this case, the setting of "Restore from PrevMBR"
is ignored.

If "Restore from file" is not checked, but "Restore from PrevMBR" is, the
program would restore from previous MBR which is saved in the second sector
of GRLDR MBR. If "Save File" box is not empty, it would be the name of file
to store the currently used MBR, which in the case is the GRLDR MBR.

b) Partition list (New in version 1.1)

After you select a image file or disk/floppy device, you can press the
"Refresh" button alongside the "Part List" dropdown list to get the partition
information. For example, for disk image aa.dsk, the list will be something
like this:

	Whole disk (MBR)
	0: 0E(FAT16X) [15M]

For FAT12 floppy image aa.img, the list will be something like this:

	Whole disk (FAT12/FAT16)

You can choose the partition by selecting the corresponding item from the list.

After you change the image/device name, the list will be reset. You need to
press the button again if you want to get the partition list of the new
image/device.

c) Test run (New in version 1.1)

You can use "Test" button to see the command line options that will be passed
to grubinst.exe, without actually making the call. This can be handy if you
want to know about the correspondence between grubinst options and the various
checkboxes in the GUI.

d) Chinese support (new in version 1.1)

The GUI will display Chinese interface if your user locale is set to simplified
Chinese. But you can alter its behaviour by using a option:

	grubinsi_gui --lang=eng

Display English interface, regardless your user locale setting.

	grubinst_gui --lang=chs

Display simplified Chinese interface, regardless your user locale setting.

In order to display Chinese characters properly, your system locale must also
be set to simplified Chinese.

4. Compilation

To compile the program, you need the GCC toolkit in Linux, FreeBSD or other
unix platform, and mingw or Visual C++ 6.0 in Windows NT/2K/XP.

To compile using GCC toolkit:

	make

To compile using Visual C++ 6.0:

	nmake -f Makefile.vc6

Here are some notes when you are using the GCC toolkit.

Note 1. If mingw is detected, make will build the GUI program grubinst_gui.
Otherwise, it will only build the console mode program grubinst.

Note 2. In Windows, Linux and FreeBSD, partition whose start address go beyond
the 4G limit is supported (However, some BIOSes may not boot from such
partitions). In other systems, the 4G limit issue depends on the size of
off_t.

Note 3. Two internal utility, bin2h and ver2h, has two forms. This first is
a perl script, which can be used directly, but it requires the perl
interpreter. The other is a C program, which works in all circumstance, but it
needs compilation. Makefile can detect whether or not perl exists, and use it
if found. If you want to use the C program even if you have perl, you can set
USE_PERL to n:

	make USE_PERL=n

Note 4. You can compile the resource script grubinst_gui.rc in two way. One
is to use windres from mingw, the other is to use rc from vc6. By default, rc
is used if it's detected. However, if you want to use windres no matter what,
set USE_RC to n:

	make USE_RC=n

Also note that rc expects your INCLUDE environment variable being set to the
paths of vc6 include files.

Note 5. To compile the Chinese resource properly, you must use rc from vc6, and
your system locale must be set to simplified Chinese at the time of the
compilation.

5. Website

http://grub4dos.sourceforge.net/
grubinst and WINGRUB homepage

http://grub4dos.jot.com/
Latest GRUB4DOS package by TinyBit

http://www.znpc.net/bbs
Nice forum on GRUB4DOS, but it's in chinese

http://grub.linuxeden.com/
Misc information by TinyBit, also in chinese

Please refer to http://grub4dos.sourceforge.net/wiki/ for DOCs on GRUB4DOS.

Main project page:	https://gna.org/projects/grub4dos/

Download site:		http://download.gna.org/grub4dos/
Download site:		http://grub4dos.sourceforge.net/
Download site:		http://sarovar.org/projects/grub4dos/
Download site:		http://grub4dos.nufans.net/
Download site:		http://sites.google.com/site/grubdos/
Download site:		http://grub4dos.jot.com/

Get the latest source code by using anonymous svn in this way:

	svn co svn://svn.gna.org/svn/grub4dos/trunk grub4dos

or in this way:

	svn co http://svn.gna.org/svn/grub4dos/trunk grub4dos

View the source code online with your web browser at:

	http://svn.gna.org/viewcvs/grub4dos/trunk/

GRUB4DOS mailing list:

	grub4dos-devel@gna.org

Subscription page:

	https://mail.gna.org/listinfo/grub4dos-devel/

Discussion forum(Official technical support site):

	http://www.boot-land.net/forums/index.php?showforum=66

------------------------------------------------------------------------------

Usage:
		GRUB [--bypass] [--time-out=T] [--hot-key=K] [--config-file=FILE]
		
		The FILE, for example, can be (hd0,0)/menu.lst
		
		In CONFIG.SYS, the line looks like:
		
			install=c:\some\where\grub.exe --config-file=FILE
		
		If no options present, GRUB.EXE simply uses
		
			(hd0,0)/menu.lst
		
		as the configure file, if it exists. (Notice! We finally
		changed the default file from (hd0,0)/boot/grub/menu.lst to
		(hd0,0)/menu.lst) (Changed 2006-12-23. See Update 3 below.)
		
		The partition (hd0,0) can be of a Windows partition or a Linux
		partition, or any other partition type supported by GRUB.

		Only GRUB-style filename is acceptable here for FILE. A DOS
		filename won't work(it is certain we should use GRUB-style
		filenames because DOS-filenames won't access a file in a
		Linux ext2 partition for example).(See Update 2 below)

		Update: FILE can be the contents of a menu. Use semi-colon
		to delimitate the embedded commands here in FILE. The FILE
		can be enclosed with a pair of double-quotes. For example:

			GRUB --config-file="root (hd0,0);chainloader +1"

		This command will boot the system in (hd0,0).

		Another example:

			GRUB --config-file="reboot"

		This command will reboot the machine.

		One more example:

			GRUB --config-file="halt"

		This command will halt the machine.

		if --bypass is specified, GRUB will exit to DOS when
		timeout reached.

		The option `--time-out=T' specifies the timeout value in
		seconds. T defaults to 5 if --bypass is specified and defaults
		to 0 if --bypass is not specified.

		The default hot key value is 0x3920(for space bar). If this
		key is pressed, GRUB will boot normally. If another key is
		pressed, GRUB will terminate immediately and return back to
		DOS. See "int 16 keyboard scan codes" below.

		Each option can be specified only once at most.

		Update 2: DOS filenames have been supported(patched by John
		Cobb). If the beginning two characters of FILE are "#@", then
		the rest of FILE is taken as a DOS filename. Example:

			GRUB --config-file="#@c:\menu.lst"

		Only the beginning 4KB of the DOS file will be used. The file
		should be an uncompressed text file.

		Note: You may also use the `direct DOS file access' with the
		SHELL or INSTALL line in CONFIG.SYS, but should not use it
		with the DEVICE line. The DOS document said that a DOS device
		driver should not call the `open file' DOS call.

		Update 3(2006-12-23): By default, GRUB.EXE will locate its
		config file in the following order:

			(DOS file) .\menu.lst, the MENU.LST in the current dir.

			(DOS file) \menu.lst, the MENU.LST in the root dir of
						the current drive.
			(GRUB file) /menu.lst, the MENU.LST in the root dir of
						the boot device.

		The default boot device is still (hd0,0).


--------------------------------------------------------

Update 1:	Version 0.2.0 also brings out a new thing, GRUB for NTLDR,
		which could be used to boot into GRUB from the boot menu
		of Windows NT/2000/XP. Copy GRLDR to the root directory of
		drive C: of Windows NT/2000/XP and append to C:\BOOT.INI
		this line:

			C:\GRLDR="Start GRUB"

		That will be done. The GRLDR should be in the same directory
		as BOOT.INI and NTLDR. Note that BOOT.INI is usually hidden
		and you must unhide it before you can see it. The filename
		GRLDR shouldn't be changed. If GRLDR is in a NTFS partition,
		it should be copied to the root directory of another non-NTFS
		partition(and likewise should the menu.lst file be). If GRLDR
		is compressed, e.g., in a NTFS partition, it will not work.

		Even if the drive letter of this disk has been changed to
		other than C by the Windows device manager, it seems you still
		have to use the letter C here in BOOT.INI, otherwise, NTLDR
		will fail to locate the GRLDR file.

		And what's more, if you are booting NTLDR from a floppy, you
		will have to write the GRLDR line in A:\BOOT.INI like this:

			C:\GRLDR="Start GRUB"

		and shouldn't use the letter A like this:

			A:\GRLDR="Start GRUB"

		(Note that in the case when BOOT.INI is on floppy A, the
		notation "C:\GRLDR" actually refer to the file A:\GRLDR).


Update 2:	GRUB for Linux is also introduced along with 0.2.0. You can
		boot grub using a linux loader KEXEC, LILO, SYSLINUX or another
		GRUB. (GRUB4LIN has merged into GRUB.EXE)

		To boot GRUB off Linux, use this pair of commands:

			kexec -l grub.exe
			kexec -e

		To boot GRUB via GRUB, use commands like the following:

			kernel (hd0,0)/grub.exe
			boot

		To boot GRUB via LILO, use these lines in lilo.conf:

			image=/boot/grub.exe
			label=grub.exe

		To boot GRUB via SYSLINUX, use these lines in syslinux.cfg:

			label grub.exe
				kernel grub.exe

		LOADLIN may encounter problems when loading grub.exe, because
		grub.exe requires some unchanged original BIOS interrupt
		vectors, but DOS has destroyed them, and loadlin does not
		recover them before it transfers control to grub.exe.
		
Update 3:	Beginning at version 0.4.0, GRUB for DOS supports memdrives.
		Example:

			# boot into a floppy image
			map --mem (hd0,0)/floppy.img (fd0)
			map --hook
			chainloader (fd0)+1
			rootnoverify (fd0)
			map --floppies=1
			boot

		Because the image will be copied to a memory area, the image
		itself can be non-contiguous and even gzipped.

		Another Example:

			map --mem=-2880 (hd0,0)/floppy.img (fd0)

		This memdrive (fd0) will occupy at least 1440 KB of memory.
		This is useful when the size of a 1.44M-floppy image is less
		than 1440 KB.

		One more example:

			map --mem --read-only (hd0,0)/hd.img (hd1)

		This memdrive is a hard drive, and read-only. That means you
		will not be able to write data to the memdrive (hd1).

		You can use many memdrives and many ordinary virtual emulated
		disk-based drives at the same time.

		If the BIOS does not support int15/EAX=e820h, you will not be
		able to use any memdrives.

Update 4:	For memdrive emulation, a single-partition image can be used
		instead of a whole-harddrive image. Example:

			map --mem (hd0,7)/win98.img (hd0)
			map --hook
			chainloader (hd0)+1
			rootnoverify (hd0)
			map --harddrives=1
			boot

		Here win98.img is a partition image without the leading MBR
		and partition table in it. Surely GRUB for DOS will build an
		MBR and partition table for the memdrive (hd0).

Update 5:	Now GRLDR can be used as a no-emulation-mode bootable CD-ROM
		boot image. Example for Linux users:

			mkdir iso_root
			cp grldr iso_root
			mkisofs -R -b grldr -no-emul-boot -boot-load-seg 0x1000 -o bootable.iso iso_root

		As an alternative, grldr can also be used the same way as
		stage2_eltorito. The -boot-info-table option is allowed but you
		can omit it:

			mkdir iso_root
			cp grldr iso_root
			mkisofs -R -b grldr -no-emul-boot -boot-load-size 4 -o grldr.iso iso_root

		Also note that the bootable.iso above must be created with the
		-boot-load-seg 0xHHHH option where HHHH is greater than or
		equal to 1000(hex). If HHHH < 1000(hex), QEMU will hang. This
		is a bug in QEMU. The grldr.iso can be created with or without
		-boot-load-seg 0xHHHH option.

		The menu.lst file should be placed in the root dir of the CD.

Update 6:	The Chinese special build is in the "chinese" subdirectory.
		(patched by Gandalf, 2005-06-27)

		The Chinese special build also has scdrom builtin.
		(update: scdrom has been dropped since 2006-07-20)

Update 7:	Added memory drive (md). Like (nd) for network drive and (cd)
		for CD-ROM drive, a new drive (md) is implemented for accessing
		the whole memory as a disk drive. (md) only works for systems
		with BIOS int15/EAX=E820h support.

		The cat command now has a few new options: --hex for hexdump,
		and --locate=STRING for string search in file.

		Typical examples:

			cat --hex (hd0)+1

		It will display the MBR sector in hex form.

			cat --hex (md)+2

		It will display 1KB of your memory(in fact, it is the real-mode
		IDT table), also in hexdump form.
		
			cat --hex (md)0x800+1

		It will display 1 sector of your extended memory.

			cat --hex (hd0,0)+1

		It will display the first sector of partition (hd0,0). Usually
		this sector contains the boot record of an operating system.

Update 8:	Added ram drive (rd). The (md) device accesses the memory
		starting at physical address 0. But (rd) accesses memory
		starting at any base address. The base and length of the ram
		drive can be specified through the map command. "help map" for
		details. You can even specify the BIOS drive number used for
		the (rd) drive, e.g., map --ram-drive=0xf0. The default drive
		number for (rd) is 0x7F which is a floppy. If (rd) is a hard
		drive image, you should change the drive number to a value
		greater than or equal to 0x80(but should avoid using 0xffff,
		because 0xffff is for the (md) device).

Update 9:	Directly boot NTLDR of WinNT/2K/XP and IO.SYS of Win9x/ME and
		KERNEL.SYS of FreeDOS. Examples:

			chainloader --edx=0xPPYY (hd0,0)/ntldr
			boot

			chainloader --edx=0xYY (hd0,0)/io.sys
			boot

			chainloader --ebx=0xYY (hd0,0)/kernel.sys
			boot

		Hex YY specifies the boot drive number, and hex PP specifies
		the boot partition number of NTLDR. If the boot drive is
		floppy, PP should be the hex value ff, i.e., decimal 255.

		For KERNEL.SYS of FreeDOS, the --edx won't work,
		use --ebx please.

		The option --edx ( --ebx ) can be omitted if the file is in
		its normal place. But in some cases, those options are needed.

		If, e.g., the ntldr file is in an ext2 partition called
		(hd2,8) while you want it to think of the Windows partition
		(hd0,7) as the boot partition, then --edx is required:

			chainloader --edx=0x0780 (hd2,8)/ntldr

		For DOS kernels(i.e., IO.SYS and KERNEL.SYS), the boot
		partition number is meaningless, so you only need to specify
		the correct boot drive number YY(but specifying the boot
		partition number is harmless).

		The above PPYY can also be specified by using a root or
		rootnoverify command after the chainloader command. Examples:

			chainloader (hd2,6)/kernel.sys
			rootnoverify (hd0)	<-------- YY=80
			boot

			chainloader (hd0,0)/ntldr
			rootnoverify (hd0,5)	<-------- YY=80, PP=05
			boot

		Tip: CMLDR (the ComMand LoaDeR, which is used to load the
		Windows Fault Recovery Console) can be chainloaded as well
		as NTLDR.

		Bean has successfully decompressed and booted IO.SYS of WinME.
		Thanks for the great job!

--------------------------------------------------------

	There is no full documentation in English at present. Here are some
	examples showing the usage of disk emulation commands:

1.	Emulates HD partition C: as floppy drive A: and boot win98 from C:

		map --read-only (hd0,0)+1 (fd0)
		chainloader (hd0,0)+1
		rootnoverify (hd0)
		boot

	In the above example, (hd0,0) is drive C: with win98 on it. After win98
	boot complete, you will find that A: contains all files of C:, and if
	you delete files in A:, the files in C: will also disappear.

	At the map command line, the notation (hdm,n)+1 is interpreted to
	represent the whole partition (hdm,n), not just the first sector of the
	partition.

2.	Emulates HD partition C: as floppy drive A: and boot win98 from A:

		map --read-only (hd0,0)+1 (fd0)
		map --hook
		chainloader (fd0)+1
		rootnoverify (fd0)
		map --floppies=1
		boot

	After the "map --hook" command, the emulation takes effect instantly
	even in the GRUB command line.
	
	Note that the (fd0) in "chainloader (fd0)+1" is the emulated virtual
	floppy A:, not the real floppy diskette(because map is hooked now).


3.	Emulates an image file as floppy drive A: and boot win98 from C:

		map --read-only (hd0,0)/floppy.img (fd0)
		chainloader (hd0,0)+1
		rootnoverify (hd0)
		map --floppies=1
		map --harddrives=1
		boot

4.	Emulates an HD partition as the first hard disk and boot DOS from it:

		map --read-only (hd2,6)+1 (hd0)
		map --hook
		chainloader (hd0,0)+1
		rootnoverify (hd0)
		map --harddrives=1
		boot

	In this example, (hd2,6)+1 represents an extended logical DOS partition
	of the third BIOS hard disk (hd2).

	If a DOS partition is used to emulate a hard disk, GRUB for DOS will
	first try to locate the partition table, usually 63 sectors ahead of
	the DOS partition. GRUB for DOS will refuse the emulation if the
	partition table is not there.

5.	Emulates an image file as the first hard disk and boot DOS from it:

		map --read-only (hd0,0)/harddisk.img (hd0)
		chainloader --load-length=512 (hd0,0)/harddisk.img
		rootnoverify (hd0)
		map --harddrives=1
		boot

	If an image file is used to emulate a hard disk, the image file must
	contain an MBR. In other word, the first sector of HARDDISK.IMG must
	contain the partition table of the emulated virtual hard disk.

Note:	Counters for floppies and harddrives in the BIOS Data Area remain
	unchanged during the mapping. You should manually set them to proper
	values with `map --floppies=' and/or `map --harddrives=', especially,
	e.g., when there is no real floppy drive attached to the mother board.
	If not doing so, DOS might fail to start.

	`map --status' can report the values. Note also that `map --floppies='
	and `map --harddrives=' can be used independently without the
	appearance of mappings.

	0.4.2 has introduced a new variable, memdisk_raw, to simulate the
	memdisk-like raw mode. If the BIOS has no int15/87h, or if it has
	buggy int15/87h support, you should set this variable before any
	memdrives are used. Here is an example:

		map --memdisk-raw=1
		map --mem (hd0,0)/floppy.img (fd0)
		map --hook
		chainloader (fd0)+1
		rootnoverify (fd0)
		boot

	If you encountered a memdrive failure without using
	map --memdisk-raw=1, you should have a try with `map --memdisk-raw=1'.

	If you `map --memdisk-raw=0' later, you should afterwards do a
	`map --unhook'(and followed by a `map --hook' if needed).

	Update: memdisk_raw now defaults to 1. You should `map --memdisk-raw=0'
	if you want to use int15/87h to access memdrives.

--------------------------------------------------------
	
	Floppies/harddisks of any size can be emulated with GRUB for DOS 0.2.0.
	
	Image file must be contiguous, or else GRUB for DOS will refuse it.

	The `blocklist' command can list fragments or pieces of a file.

	Type "help map" at the GRUB prompt to get a brief description of the
	command.

	The form 
	
		map ... (fd?)
	
	is a floppy emulation, and the form
	
		map ... (hd?)
	
	is a hard disk emulation.

	When a HARD DISK emulation is used, better not start Windows for
	security reasons. Windows may even destroy all data and all information
	on all your real hard disks!!!!!!!!
	
	Update for --mem: when --mem is used, it seems rather safe even after
	entering Windows. Win98 can operate the memdrive normally.

	Windows NT/2000/XP does not recognize the emulated drives no matter
	whether the --mem option is present.



******************************************************************************
***   Explanation of the grldr-bootable floppies or harddisk partitions    ***
******************************************************************************

1. Ext2 Boot Sector/Boot Record Layout (for loading grldr)
------------------------------------------------------------------------------
An EXT2/EXT3 volume can be GRUB-bootable. Copy grldr and an optional menu.lst
to the root dir of the EXT2/EXT3 volume, and build the boot sector based on the
fifth sector of grldr(some fields need to be changed as detailed in the
following table). And then the EXT2/EXT3 volume is GRUB-bootable.

Update:	bootlace.com is a DOS/Linux utility that can install the GRLDR boot
record onto the first sector of an EXT2/EXT3 volume.

Offset	Length	Description
======	======	==============================================================
00h	2	Machine code for short jump over the data.

02h	1	LBA indicator. Valid values are 0x02 for CHS mode, or 0x42 for
		LBA mode.

		If the BIOS int13 supports LBA, this byte can be safely set to
		0x42.

		Some USB BIOSes might have bugs when using CHS mode, so the
		format program should set this byte to 0x42. It seems that
		(generally) all USB BIOSes have LBA support.

		If the format program does not know whether the BIOS has LBA
		support, it may operate this way:

		if (partition_start + total_sectors_in_partition) exceeds the
		CHS addressing ability(especially when it is greater than
		1024*256*63), the caller should set this byte to 0x42,
		otherwise, set to 0x02.

		Note that Windows98 uses the value 0x0e as the LBA indicator.

		Update: this byte of LBA indicator is ignored. The boot
		record can probe the LBA support of BIOS.

03h	10	OEM name string (of OS which formatted the disk).
		Update: this field is now used for error message of "I/O error"

0Dh	1	Sectors per block. Valid values are 2, 4, 8, 16 and 32.

0Eh	2	Bytes per block. Valid values are 0x400, 0x800, 0x1000, 0x2000
		and 0x4000.

10h	4	Pointers in pointers-per-block blocks, that is, number of
		blocks covered by a double-indirect block.

		Valid values are 0x10000, 0x40000, 0x100000, 0x400000 and
		0x1000000.

14h	4	Pointers per block, that is, number of blocks covered by an
		indirect block.

		Valid values are 0x100, 0x200, 0x400, 0x800, 0x1000.

18h	2	Sectors per track.

1Ah	2	Number of heads/sides.

1Ch	4	Number of hidden sectors (those preceding the boot sector).

		Also referred to as the starting sector of the partition.

		For floppies, it should be 0.

20h	4	Total number of sectors in the filesystem(or in the partition).

24h	1	BIOS drive number of the boot device.

		Actually this byte is ignored for read. The boot code will
		write DL onto this byte. The BIOS or the caller should set
		drive number in DL.

		We assume all BIOSes pass correct drive number in DL.
		Buggy BIOSes are not supported!!

25h	1	Partition number of this partition on the boot drive.

		0, 1, 2, 3 are primary partitions.
		4, 5, 6, ... are logical partitions in the extended partition.

		0xff is for whole drive. So for floppies, it should be 0xff.

26h	2	inode size in bytes. (Notice! We use the formerly reserved
		word here for inode size!)

28h	4	Number of inodes per group.

		Normally a 1.44M floppy has only one group, and the total
		number of inodes is 184. So the value should be	184 or
		greater.

2Ch	4	The block number for group descriptors.

		Valid values are 2 for 1024-byte blocks, and 1 otherwise.

		The value here is equal to (s_first_data_block + 1).

30h	1	code for "cld"(0xFC).

31h	2	code for "xor ax,ax"(0x31, 0xC0).

33h	1	code for "nop"(0x90) or "cwd"(0x99)

34h	458	The rest of the machine code.

1FEh	2	Boot Signature AA55h.


2. FAT12/FAT16 Boot Sector/Boot Record Layout (for loading grldr)
------------------------------------------------------------------------------
A FAT12/16 volume can be GRUB-bootable. Copy grldr and an optional menu.lst to
the root dir of the FAT12/16 volume, and build the boot sector based on the
fourth sector of grldr(some fields need to be changed as detailed in the
following table). And then the FAT12/16 volume is GRUB-bootable.

Update:	bootlace.com is a DOS/Linux utility that can install the GRLDR boot
record onto the boot sector of an FAT12/16 volume.

Offset	Length	Description
======	======	==============================================================
00h	2	Machine code for short jump over the data.

02h	1	LBA indicator. Valid values are 0x90 for CHS mode, or 0x0e for
		LBA mode.

		If the BIOS int13 supports LBA, this byte can be safely set to
		0x0e.

		Some USB BIOSes might have bugs when using CHS mode, so the
		format program should set this byte to 0x0e. It seems that
		(generally) all USB BIOSes have LBA support.

		If the format program does not know whether the BIOS has LBA
		support, it may operate this way:

		if (partition_start + total_sectors_in_partition) exceeds the
		CHS addressing ability(especially when it is greater than
		1024*256*63), the caller should set this byte to 0x0e,
		otherwise, set to 0x90.

		Update: this byte of LBA indicator is ignored. The boot
		record can probe the LBA support of BIOS.

		Update(2006-07-31): Though GRLDR won't use this LBA-indicator
		byte, Windows 98 uses it. Usually this byte should be 0x90 for
		CHS mode(especially for floppies). If this byte is not set
		properly, Windows 98 will not recognize the floppy or
		partition. This problem was reported by neiljoy. Many thanks!

03h	8	OEM name string (of OS which formatted the disk).

0Bh	2	Bytes per sector. Must be 512.

0Dh	1	Sectors per cluster. Valid values are 1, 2, 4, 8, 16, 32, 64
		and 128. But a cluster size larger than 32K should not occur.

0Eh	2	Reserved sectors(number of sectors before the first FAT,
		including the boot sector), usually 1.

10h	1	Number of FATs(nearly always 2).

11h	2	Maximum number of root directory entries.

13h	2	Total number of sectors (for small disks only, if the disk is
		too big this is set to 0 and offset 20h is used instead).

15h	1	Media descriptor byte, pretty meaningless now (see below).

16h	2	Sectors per FAT.

18h	2	Sectors per track.

1Ah	2	Total number of heads/sides.

1Ch	4	Number of hidden sectors (those preceding the boot sector).

		Also referred to as the starting sector of the partition.

		For floppies, it should be 0.

20h	4	Total number of sectors for large disks.

24h	1	BIOS drive number of the boot device.

		Actually this byte is ignored for read. The boot code will
		write DL onto this byte. The BIOS or the caller should set
		drive number in DL.

		We assume all BIOSes pass correct drive number in DL.
		Buggy BIOSes are not supported!!

25h	1	Partition number of this filesystem in the boot drive.

		This byte is ignored for read. The boot code will write
		partition number onto this byte. See offset 41h below.

26h	1	Signature (must be 28h or 29h to be recognised by NT).

27h	4	Volume serial number.

2Bh	11	Volume label.

36h	8	File system ID. "FAT12   ", "FAT16   " or "FAT     ".

3Eh	1	code for "cli".

3Fh	1	code for "cld".

40h	1	code for "mov dh, imm8".

41h	1	Partition number of this partition on the boot drive.

		0, 1, 2, 3 are primary partitions.
		4, 5, 6, ... are logical partitions in the extended partition.

		0xff is for whole drive. So for floppies, it should be 0xff.

42h	442	The rest of the machine code.

1FCh	4	Boot Signature AA550000h. (Win9x uses 4 bytes as magic value)


3. FAT32 Boot Sector/Boot Record Layout (for loading grldr)
------------------------------------------------------------------------------
A FAT32 volume can be GRUB-bootable. Copy grldr and an optional menu.lst to
the root dir of the FAT32 volume, and build the boot sector based on the
third sector of grldr(some fields need to be changed as detailed in the
following table). And then the FAT32 volume is GRUB-bootable.

Update:	bootlace.com is a DOS/Linux utility that can install the GRLDR boot
record onto the boot sector of an FAT32 volume.

Offset	Length	Description
======	======	==============================================================
00h	2	Machine code for short jump over the data.

02h	1	LBA indicator. Valid values are 0x90 for CHS mode, or 0x0e for
		LBA mode.

		If the BIOS int13 supports LBA, this byte can be safely set to
		0x0e.

		Some USB BIOSes might have bugs when using CHS mode, so the
		format program should set this byte to 0x0e. It seems that
		(generally) all USB BIOSes have LBA support.

		If the format program does not know whether the BIOS has LBA
		support, it may operate this way:

		if (partition_start + total_sectors_in_partition) exceeds the
		CHS addressing ability(especially when it is greater than
		1024*256*63), the caller should set this byte to 0x0e,
		otherwise, set to 0x90.

		Update: this byte of LBA indicator is ignored. The boot
		record can probe the LBA support of BIOS.

		Update(2006-07-31): Though GRLDR won't use this LBA-indicator
		byte, Windows 98 uses it. Usually this byte should be 0x90 for
		CHS mode(especially for floppies). If this byte is not set
		properly, Windows 98 will not recognize the floppy or
		partition. This problem was reported by neiljoy. Many thanks!

03h	8	OEM name string (of OS which formatted the disk).

0Bh	2	Bytes per sector. Must be 512.

0Dh	1	Sectors per cluster. Valid values are 1, 2, 4, 8, 16, 32, 64
		and 128. But a cluster size larger than 32K should not occur.

0Eh	2	Reserved sectors(number of sectors before the first FAT,
		including the boot sector), usually 1.

10h	1	Number of FATs(nearly always 2).

11h	2	(Maximum number of root directory entries)Must be 0.

13h	2	(Total number of sectors for small disks only)Must be 0.

15h	1	Media descriptor byte, pretty meaningless now (see below).

16h	2	(Sectors per FAT)Must be 0.

18h	2	Sectors per track.

1Ah	2	Total number of heads/sides.

1Ch	4	Number of hidden sectors (those preceding the boot sector).

		Also referred to as the starting sector of the partition.

		For floppies, it should be 0.

20h	4	Total number of sectors for large disks.

24h	4	FAT32 sectors per FAT.

28h	2	If bit 7 is clear then all FATs are updated, otherwise bits
		0-3 give the current active FAT, all other bits are reserved.

2Ah	2	High byte is major revision number, low byte is minor revision
		number, currently both are 0.

2Ch	4	Root directory starting cluster.

30h	2	File system information sector.

32h	2	If non-zero this gives the sector which holds a copy of the
		boot record, usually 6.

34h	12	Reserved, set to 0.

40h	1	BIOS drive number of the boot device.

		80h is first HDD, 00h is first FDD.

		Actually this byte is ignored for read. The boot code will
		write DL onto this byte. The BIOS or the caller should set
		drive number in DL.

		We assume all BIOSes pass correct drive number in DL.
		Buggy BIOSes are not supported!!

41h	1	Partition number of this filesystem in the boot drive.

		This byte is ignored for read. The boot code will write
		partition number onto this byte. See offset 5Dh below.

42h	1	Signature (must be 28h or 29h to be recognised by NT).

43h	4	Volume serial number.

47h	11	Volume label.

52h	8	File system ID. "FAT32   ".

5Ah	1	opcode for "cli".

5Bh	1	opcode for "cld".

5Ch	1	opcode for "mov dh, imm8".

5Dh	1	Partition number of this partition on the boot drive.

		0, 1, 2, 3 are primary partitions.
		4, 5, 6, ... are logical partitions in the extended partition.

		0xff is for whole drive. So for floppies, it should be 0xff.

5Eh	414	The rest of the machine code.

1FCh	4	Boot Signature AA550000h. (Win9x uses 4 bytes as magic value)


4. NTFS Boot Sector/Boot Record Layout (for loading grldr)
------------------------------------------------------------------------------
An NTFS volume can be GRUB-bootable. Copy grldr and an optional menu.lst to
the root dir of the NTFS volume, and build the boot sector based on the
6th-9th sectors of grldr(some fields need to be changed as detailed in the
following table). And then the NTFS volume is GRUB-bootable.

Update:	bootlace.com is a DOS/Linux utility that can install the GRLDR boot
record onto the leading 4 sectors of an NTFS volume.

Offset	Length	Description
======	======	==============================================================
00h	2	Machine code for short jump over the data.

02h	1	LBA indicator. Valid values are 0x90 for CHS mode, or 0x0e for
		LBA mode.

		If the BIOS int13 supports LBA, this byte can be safely set to
		0x0e.

		Some USB BIOSes might have bugs when using CHS mode, so the
		format program should set this byte to 0x0e. It seems that
		(generally) all USB BIOSes have LBA support.

		If the format program does not know whether the BIOS has LBA
		support, it may operate this way:

		if (partition_start + total_sectors_in_partition) exceeds the
		CHS addressing ability(especially when it is greater than
		1024*256*63), the caller should set this byte to 0x0e,
		otherwise, set to 0x90.

		Update: this byte of LBA indicator is ignored. The boot
		record can probe the LBA support of BIOS.

		Update(2006-07-31): Though GRLDR won't use this LBA-indicator
		byte, Windows 98 uses it. Usually this byte should be 0x90 for
		CHS mode(especially for floppies). If this byte is not set
		properly, Windows 98 will not recognize the floppy or
		partition. This problem was reported by neiljoy. Many thanks!

03h	8	OEM name string (of OS which formatted the disk).

0Bh	2	Bytes per sector. Must be 512.

0Dh	1	Sectors per cluster. Valid values are 1, 2, 4, 8, 16, 32, 64
		and 128. But a cluster size larger than 32K should not occur.

0Eh	2	(Reserved sectors)Unused.

10h	1	(Number of FATs)Must be 0.

11h	2	(Maximum number of root directory entries)Must be 0.

13h	2	(Total number of sectors for small disks only)Must be 0.

15h	1	Media descriptor byte, pretty meaningless now (see below).

16h	2	(Sectors per FAT)Must be 0.

18h	2	Sectors per track.

1Ah	2	Total number of heads/sides.

1Ch	4	Number of hidden sectors (those preceding the boot sector).

		Also referred to as the starting sector of the partition.

		For floppies, it should be 0.

20h	4	(Total number of sectors for large disks)Must be 0.

24h	4	(FAT32 sectors per FAT) - Usually 80 00 80 00, A value of
		80 00 00 00 has been seen on a USB thumb drive which is
		formatted with NTFS under Windows XP. Note this is removable
		media and is not partitioned, the drive as a whole is NTFS
		formatted.

28h	8	Number of sectors in the volume.

30h	8	LCN of VCN 0 of the $MFT.

38h	8	LCN of VCN 0 of the $MFTMirr.

40h	4	Clusters per MFT Record.

44h	4	Clusters per Index Record.

48h	8	Volume serial number.

50h	4	Checksum, usually 0.

54h	1	opcode for "cli".

55h	1	opcode for "cld".

56h	1	opcode for "mov dh, imm8".

57h	1	Partition number of this partition on the boot drive.

		0, 1, 2, 3 are primary partitions.
		4, 5, 6, ... are logical partitions in the extended partition.

		0xff is for whole drive. So for floppies, it should be 0xff.

58h	420	The rest of the machine code in the first sector.

1FCh	4	Boot Signature AA550000h. (Win9x uses 4 bytes as magic value)

200h	1536	The rest of the machine code in the last 3 sectors.

------------------------------------------------------------------------------

Appendix A: File System Information Sector of FAT32(not used by grldr)

Offset	Length	Description
======	======	==============================================================
0h	4	Leading Signature 41615252h.

4h	480	Reserved, set to 0.

1E4h	4	FSI structure signature 61417272h.

1E8h	4	Contains the last known count of free clusters, if this is
		equal to FFFFFFFFh, then the count is unknown.

1ECh	4	Cluster number at which you should begin a search for a free
		cluster, if this is equal to FFFFFFFFh then the field has not
		been set.

1F0h	12	Reserved, set to 0.

1FCh	4	Trailing Signature AA550000h.

------------------------------------------------------------------------------

Appendix B: Media Descriptor Byte(not used by grldr)

The Media descriptor byte is meaningless because of the duplications, F0h for
example.

Byte	Type of disk	Sectors	Heads	Tracks	Capacity
----	------------	-------	-----	------	--------
FFh	5 1/4"		8	2	40	320KB
FEh	5 1/4"		8	1	40	160KB
FDh	5 1/4"		9	2	40	360KB
FCh	5 1/4"		9	1	40	180KB
FBh	both		9	2	80	640KB
FAh	both		9	1	80	320KB
F9h	5 1/4"		15	2	80	1200KB
F9h	3 1/2"		9	2	80	720KB
F0h	3 1/2"		18 	2	80	1440KB
F0h	3 1/2"		36 	2	80	2880KB
F8h	hard disk	NA	NA	NA	NA

******************************************************************************
***   grldr.mbr - How to write it to Master Boot Track of the hard disk    ***
******************************************************************************

grldr.mbr contains code that can be used as Master Boot Record. The code is
responsible for searching all partitions for grldr and when found, loading it.
Currently supported partition types are: FAT12/FAT16/FAT32, NTFS, EXT2/EXT3.
Logical partitions in the extended partition are supported, provided that the
extended partition type is Microsoft-compatible. In fact, the Linux extended
partition type(0x85) is not fully tested for the search mechanism.

How to write GRLDR.MBR to the Master Boot Track of a hard disk?

First, read the Windows disk signature and partition information bytes
(72 bytes in total, from offset 0x01b8 to 0x01ff of the MBR sector), and put
them on the same range from offset 0x01b8 to 0x01ff of the beginning sector of
GRLDR.MBR.

Optionally, if the MBR in the hard disk is a single sector MBR created by
Microsoft FDISK, it may be copied onto the second sector of GRLDR.MBR.

The second sector of GRLDR.MBR is called "previous MBR". When GRLDR not found,
"previous MBR" will be started.

No other steps needed, after all necessary changes stated above have been made,
now simply write GRLDR.MBR on to the Master Boot Track. That's all.

Note: The Master Boot Track means the first track of the hard drive.

Note: The bootstrap code of GRLDR.MBR only finds GRLDR file in the root dir of
a partition. You'd better place menu.lst file accompanying with GRLDR(i.e., in
the same root dir of the same partition as GRLDR).

The filename "grldr" in an ext2 partition must be in lower case letters, and
the file type of grldr must be plain regular. Other types, e.g., a symbolic
link, won't work.

Update:	bootlace.com is a DOS/Linux utility for installing grldr.mbr to MBR.
The whole grldr.mbr is embedded in the body of the bootlace.com utility, so
bootlace.com can be used independently. See below.

******************************************************************************
***               grldr.mbr - Details about the control bytes              ***
******************************************************************************

Six bytes can be used to control the boot process of GRLDR.MBR.

Offset	Length	Description
======	======	==============================================================
02h	1	bit0=1: disable the search for GRLDR on floppy
		bit0=0: enable the search for GRLDR on floppy

		bit1=1: disable the boot of PREVIOUS MBR with invalid
			partition table(usually an OS boot sector)
		bit1=0: enable the boot of PREVIOUS MBR with invalid
			partition table(usually an OS boot sector)

		bit2=1: disable the feature of unconditional entrance to
			the command-line(See below `--duce')
		bit2=0: enable the feature of unconditional entrance to
			the command-line(See below `--duce')

		bit3=1: disable geometry tune(See below `--chs-no-tune')
		bit3=0: enable geometry tune(See below `--chs-no-tune')

		bit4 - bit6: reserved

		bit7=1: try to boot PREVIOUS MBR after the search for GRLDR
		bit7=0: try to boot PREVIOUS MBR before the search for GRLDR

03h	1	timeout in seconds to wait for a key press. 0xff stands for
		waiting all the time(endless).

04h	2	hot-key code. high byte is scan code, low byte is ASCII code.
		the default value is 0x3920, which stands for the space bar.
		if this key is pressed, GRUB will be started prior to the boot
		of previous MBR. See "int 16 keyboard scan codes" below.

06h	1	preferred boot drive number, 0xff for no-drive
07h	1	preferred partition number, 0xff for whole drive

		if the preferred boot drive number is 0xff, the order of the
		search for GRLDR will be:

			(hd0,0), (hd0,1), ..., (hd0,L),(L=max partition number) 
			(hd1,0), (hd1,1), ..., (hd1,M),(M=max partition number)
			... ... ... ... ... ... ... ... 
			(hdX,0), (hdX,1), ..., (hdX,N),(N=max partition number)
						       (X=max harddrive number)
			(fd0)

		otherwise, if the preferred boot drive number is Y(not equal to
		0xff) and the preferred partition number is K, then the order of
		the search for GRLDR will be:

			(Y) if K=0xff; or (Y,K) otherwise
			(hd0,0), (hd0,1), ..., (hd0,L),(L=max partition number) 
			(hd1,0), (hd1,1), ..., (hd1,M),(M=max partition number)
			... ... ... ... ... ... ... ... 
			(hdX,0), (hdX,1), ..., (hdX,N),(N=max partition number)
						       (X=max harddrive number)
			(fd0)

		Note: if Y < 0x80, then (Y) is floppy, else (Y) is harddrive,
		      and (Y,K) is partition number K on harddrive (Y).


******************************************************************************
***        bootlace.com - Install GRLDR.MBR bootstrap code to MBR          ***
******************************************************************************

BOOTLACE.COM installs GRLDR.MBR boot record to the MBR of a harddrive or of a
harddrive image file, or to the boot sector of a floppy or a floppy image.

Usage:

	bootlace.com  [OPTIONS]  DEVICE_OR_FILE

OPTIONS:

	--read-only		do everything except the actual write to the
				specified DEVICE_OR_FILE.

	--restore-mbr		restore the previous mbr.

	--mbr-no-bpb		do not copy BPB in the boot sector of the
				leading FAT partition to MBR.

	--no-backup-mbr		do not copy the old MBR to the second sector of
				DEVICE_OR_FILE.

	--force-backup-mbr	force the copy of old MBR to the second sector
				of DEVICE_OR_FILE.

	--mbr-enable-floppy	enable the search for GRLDR on floppy.

	--mbr-disable-floppy	disable the search for GRLDR on floppy.

	--mbr-enable-osbr	enable the boot of PREVIOUS MBR with invalid
				partition table(usually an OS boot sector).

	--mbr-disable-osbr	disable the boot of PREVIOUS MBR with invalid
				partition table(usually an OS boot sector).

	--duce			disable the feature of unconditional entrance
	                        to the command-line.

				Normally one can unconditionally get the
				command-line console by a keypress of `C',
				bypassing all config-files(including the
				preset-menu). This is a security hole. So we
				need this option to disable the feature.

				DUCE is for Disable Unconditional Command-line
				Entrance.

	--chs-no-tune		disable the feature of geometry tune.

	--boot-prevmbr-first	try to boot PREVIOUS MBR before the search for
				GRLDR.

	--boot-prevmbr-last	try to boot PREVIOUS MBR after the search for
				GRLDR.

	--preferred-drive=D	preferred boot drive number, 0 <= D < 255.

	--preferred-partition=P	preferred partition number, 0 <= P < 255.

	--serial-number=SN	setup a new serial number for the hard drive.
				SN must be non-zero.

	--time-out=T		wait T seconds before booting PREVIOUS MBR. if
				T is 0xff, wait forever. The default is 5.
	
	--hot-key=K		if the desired key K is pressed, start GRUB
				before booting PREVIOUS MBR. K is a word
				value, just as the value in AX register
				returned from int16/AH=1. The high byte is the
				scan code and the low byte is ASCII code. The
				default is 0x3920 for space bar. See "int 16
				keyboard scan codes" below.

	--floppy		if DEVICE_OR_FILE is floppy, use this option.

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

	--fat12			FAT12 is allowed to be installed for --floppy.

	--fat16			FAT16 is allowed to be installed for --floppy.

	--fat32			FAT32 is allowed to be installed for --floppy.

	--vfat			FAT12/16/32 are allowed to be installed for
				--floppy.

	--ntfs			NTFS is allowed to be installed for --floppy.

	--ext2			EXT2 is allowed to be installed for --floppy.

	--install-partition=I	Install the boot record onto the boot area of
				partition number I of the specified hard drive
				or harddrive image DEVICE_OR_FILE.

DEVICE_OR_FILE:	Filename of the device or the image file. For DOS, a BIOS drive
number(hex 0xHH or decimal DDD) can be used to access the drive. BIOS drive
number 0 is for the first floppy, 1 is for the second floppy; 0x80 is for the
first hard drive, 0x81 is for the second hard drive, etc.

Note: BOOTLACE.COM writes only the boot code to MBR. The boot code needs to
load GRLDR as the second(and last) stage of the GRUB boot process. Therefore
GRLDR should be copied to the root directory of one of the supported
partitions, either before or after a successful execution of BOOTLACE.COM.
Currently only partitions with filesystem type of FAT12, FAT16, FAT32, NTFS,
EXT2 or EXT3 are supported.

Note 2: If DEVICE_OR_FILE is a harddisk device or a harddisk image file, it
must contain a valid partition table, otherwise, BOOTLACE.COM will fail. If
DEVICE_OR_FILE is a floppy device or a floppy image file, then it must contain
a supported filesystem(i.e., either of FAT12/FAT16/FAT32/NTFS/EXT2/EXT3).

Note 3: If DEVICE_OR_FILE is a floppy device or a floppy image file, and it
was formated EXT2/EXT3, then you should specify --sectors-per-track and
--heads explicitly.


Important!! If you install GRLDR Boot Record to a floppy or a partition, the
floppy or partition will boot solely grldr, and your original
IO.SYS(DOS/Win9x/Me) and NTLDR(WinNT/2K/XP) will become unbootable. This is
because the original boot record of the floppy or partition was overwritten.
There is no such problem when installing GRLDR Boot Record onto the MBR.
Update: Some NTLDR/IO.SYS/KERNEL.SYS files can be directly chainloaded in the
latest GRUB4DOS.

Tip: If the filename begins in a dash(-) or a digit, you may prefix a dirname
(./) or (.\) to it.

Examples:

	Installing GRLDR boot code to MBR under Linux:

		bootlace.com  /dev/hda

	Installing GRLDR boot code to MBR under DOS:

		bootlace.com  0x80

	Installing GRLDR boot code to a harddisk image under DOS or Linux:

		bootlace.com  hd.img

	Installing GRLDR boot code to floppy under Linux:

		bootlace.com  --floppy --chs /dev/fd0

	Installing GRLDR boot code to floppy under DOS:

		bootlace.com  --floppy --chs 0x00

	Installing GRLDR boot code to a floppy image under DOS or Linux:

		bootlace.com  --floppy --chs floppy.img

BOOTLACE.COM cannot function well under Windows NT/2000/XP/2003. It is expected
(and designed) to run under DOS/Win9x and Linux. Update: For image FILES,
bootlace.com function well under Windows NT/2000/XP/2003. For devices,
bootlace.com will not work under Windows NT/2000/XP/2003 because bootlace.com
is a DOS utility and Windows NT/2000/XP/2003 does not allow bootlace.com to
access devices.

******************************************************************************
***        kexec-tools should be patched for the 1.101 release             ***
******************************************************************************

The file kexec-tools-1.101-patch is a patch to the kexec-tools-1.101 release.
Kexec might fail to load grub.exe without this patch.

The home page of kexec-tools is:

	http://www.xmission.com/~ebiederm/files/kexec/

Note: The Linux kernel should be KEXEC enabled before kexec can be run.

			!! Important Update !!

The patch `kexec-tools-1.101-patch' is not needed now and has been deleted.
Even worse, it fails in `kexec -l grub.exe --initrd=imgfile'. So please
do not use it any more.

******************************************************************************
***           Direct transition to DOS/Win9x from within Linux             ***
******************************************************************************

By using kexec, we can easily boot into DOS/Win9x from a running Linux system.

If WIN98.IMG is a bootable hard-disk image, do as follows:

kexec -l grub.exe --initrd=WIN98.IMG --command-line="--config-file=map (rd) (hd0); map --hook; chainloader (hd0)+1; rootnoverify (hd0)"

kexec -e

If DOS.IMG is a bootable floppy image, do this way:

kexec -l grub.exe --initrd=DOS.IMG --command-line="--config-file=map (rd) (fd0); map --hook; chainloader (fd0)+1; rootnoverify (fd0)"

kexec -e

Note that in this manner, we can boot DOS/Win9x without using a real DOS/Win9x
disk. We need no FAT partition but an image file.

We have noticed that Linux itself can act as a big boot manager by using kexec
and grub.exe. This may be convenient to developers who write installation or
bootstrap or initialization programs.

Certainly, grub.exe and the bootable disk image can also be loaded by a running
GRUB or LILO or syslinux. Examples:

1. Loaded by GRUB:

	kernel (hd0,0)/grub.exe --config-file="map (rd) (fd0); map --hook; chainloader (fd0)+1; rootnoverify (fd0)"
	initrd (hd0,0)/DOS.IMG
	boot

2. Loaded by LILO:

	image=/boot/grub.exe
		label=grub.exe
		initrd=/boot/DOS.IMG
		append="--config-file=map (rd) (fd0); map --hook; chainloader (fd0)+1; rootnoverify (fd0)"

3. Loaded by SYSLINUX:

	label grub.exe
		kernel grub.exe
		append initrd=DOS.IMG --config-file="map (rd) (fd0); map --hook; chainloader (fd0)+1; rootnoverify (fd0)"

Note: If the above `map (rd) (...)' failed, you may use `map (rd)+1 (...)'
instead and try again.

******************************************************************************
***               Keyboard BIOS Scan Code/ASCII code tables                ***
******************************************************************************

Keyboard bios scan code and ascii character code tables can be obtained from
the web by, for example, googling for "3920 372A 4A2D 4E2B 352F". Here are 2
main results:

1. From "http://heim.ifi.uio.no/~stanisls/helppc/scan_codes.html":

INT 16 - Keyboard Scan Codes

       Key	 Normal    Shifted   w/Ctrl    w/Alt

	A	  1E61	    1E41      1E01	1E00
	B	  3062	    3042      3002	3000
	C	  2E63	    2E43      2E03	2E00
	D	  2064	    2044      2004	2000
	E	  1265	    1245      1205	1200
	F	  2166	    2146      2106	2100
	G	  2267	    2247      2207	2200
	H	  2368	    2348      2308	2300
	I	  1769	    1749      1709	1700
	J	  246A	    244A      240A	2400
	K	  256B	    254B      250B	2500
	L	  266C	    264C      260C	2600
	M	  326D	    324D      320D	3200
	N	  316E	    314E      310E	3100
	O	  186F	    184F      180F	1800
	P	  1970	    1950      1910	1900
	Q	  1071	    1051      1011	1000
	R	  1372	    1352      1312	1300
	S	  1F73	    1F53      1F13	1F00
	T	  1474	    1454      1414	1400
	U	  1675	    1655      1615	1600
	V	  2F76	    2F56      2F16	2F00
	W	  1177	    1157      1117	1100
	X	  2D78	    2D58      2D18	2D00
	Y	  1579	    1559      1519	1500
	Z	  2C7A	    2C5A      2C1A	2C00

       Key	 Normal    Shifted   w/Ctrl    w/Alt

	1	  0231	    0221		7800
	2	  0332	    0340      0300	7900
	3	  0433	    0423		7A00
	4	  0534	    0524		7B00
	5	  0635	    0625		7C00
	6	  0736	    075E      071E	7D00
	7	  0837	    0826		7E00
	8	  0938	    092A		7F00
	9	  0A39	    0A28		8000
	0	  0B30	    0B29		8100

       Key	 Normal    Shifted   w/Ctrl    w/Alt

	-	  0C2D	    0C5F      0C1F	8200
	=	  0D3D	    0D2B		8300
	[	  1A5B	    1A7B      1A1B	1A00
	]	  1B5D	    1B7D      1B1D	1B00
	;	  273B	    273A		2700
	'	  2827	    2822
	`	  2960	    297E
	\	  2B5C	    2B7C      2B1C	2600 (same as Alt L)
	,	  332C	    333C
	.	  342E	    343E
	/	  352F	    353F

	Key	 Normal    Shifted   w/Ctrl    w/Alt

	F1	  3B00	    5400      5E00	6800
	F2	  3C00	    5500      5F00	6900
	F3	  3D00	    5600      6000	6A00
	F4	  3E00	    5700      6100	6B00
	F5	  3F00	    5800      6200	6C00
	F6	  4000	    5900      6300	6D00
	F7	  4100	    5A00      6400	6E00
	F8	  4200	    5B00      6500	6F00
	F9	  4300	    5C00      6600	7000
	F10	  4400	    5D00      6700	7100
	F11	  8500	    8700      8900	8B00
	F12	  8600	    8800      8A00	8C00

	Key	    Normal    Shifted	w/Ctrl	  w/Alt

	BackSpace    0E08      0E08	 0E7F	  0E00
	Del	     5300      532E	 9300	  A300
	Down Arrow   5000      5032	 9100	  A000
	End	     4F00      4F31	 7500	  9F00
	Enter	     1C0D      1C0D	 1C0A	  A600
	Esc	     011B      011B	 011B	  0100
	Home	     4700      4737	 7700	  9700
	Ins	     5200      5230	 9200	  A200
	Keypad 5		4C35	 8F00
	Keypad *     372A		 9600	  3700
	Keypad -     4A2D      4A2D	 8E00	  4A00
	Keypad +     4E2B      4E2B		  4E00
	Keypad /     352F      352F	 9500	  A400
	Left Arrow   4B00      4B34	 7300	  9B00
	PgDn	     5100      5133	 7600	  A100
	PgUp	     4900      4939	 8400	  9900
	PrtSc				 7200
	Right Arrow  4D00      4D36	 7400	  9D00
	SpaceBar     3920      3920	 3920	  3920
	Tab	     0F09      0F00	 9400	  A500
	Up Arrow     4800      4838	 8D00	  9800


- Some key combinations are not available on all systems.  The PS/2
  includes many that aren't available on the PC, XT and AT.
- To retrieve the character from a scan code logical AND the word
  with 0x00FF.
- see  INT 16  MAKE CODES



2. From "http://www.hoppie.nl/ivan/keycodes.txt":



     Keystroke                  Keypress code
--------------------------------------------------
     Esc                        011B
     1                          0231
     2                          0332
     3                          0433
     4                          0534
     5                          0635
     6                          0736
     7                          0837
     8                          0938
     9                          0A39
     0                          0B30
     -                          0C2D
     =                          0D3D
     Backspace                  0E08
     Tab                        0F09
     q                          1071
     w                          1177
     e                          1265
     r                          1372
     t                          1474
     y                          1579
     u                          1675
     i                          1769
     o                          186F
     p                          1970
     [                          1A5B
     ]                          1B5D
     Enter                      1C0D
     Ctrl                         **
     a                          1E61
     s                          1F73
     d                          2064
     f                          2166
     g                          2267
     h                          2368
     j                          246A
     k                          256B
     l                          266C
     ;                          273B
     '                          2827
     `                          2960
     Shift                        **
     \                          2B5C
     z                          2C7A
     x                          2D78
     c                          2E63
     v                          2F76
     b                          3062
     n                          316E
     m                          326D
     ,                          332C
     .                          342E
     /                          352F
     Gray *                     372A
     Alt                          **
     Space                      3920
     Caps Lock                    **
     F1                         3B00
     F2                         3C00
     F3                         3D00
     F4                         3E00
     F5                         3F00
     F6                         4000
     F7                         4100
     F8                         4200
     F9                         4300
     F10                        4400
     F11                        8500
     F12                        8600
     Num Lock                     **
     Scroll Lock                  **
     White Home                 4700
     White Up Arrow             4800
     White PgUp                 4900
     Gray -                     4A2D
     White Left Arrow           4B00
     Center Key                 4C00
     White Right Arrow          4D00
     Gray +                     4E2B
     White End                  4F00
     White Down Arrow           5000
     White PgDn                 5100
     White Ins                  5200
     White Del                  5300
     SysReq                       **
     Key 45 [1]                 565C
     Enter (number keypad)      1C0D
     Gray /                     352F
     PrtSc                        **
     Pause                        **
     Gray Home                  4700
     Gray Up Arrow              4800
     Gray Page Up               4900
     Gray Left Arrow            4B00
     Gray Right Arrow           4D00
     Gray End                   4F00
     Gray Down Arrow            5000
     Gray Page Down             5100
     Gray Insert                5200
     Gray Delete                5300

     Shift Esc                  011B
     !                          0221
     @                          0340
     #                          0423
     $                          0524
     %                          0625
     ^                          075E
     &                          0826
     * (white)                  092A
     (                          0A28
     )                          0B29
     _                          0C5F
     + (white)                  0D2B
     Shift Backspace            0E08
     Shift Tab (Backtab)        0F00
     Q                          1051
     W                          1157
     E                          1245
     R                          1352
     T                          1454
     Y                          1559
     U                          1655
     I                          1749
     O                          184F
     P                          1950
     {                          1A7B
     }                          1B7D
     Shift Enter                1C0D
     Shift Ctrl                   **
     A                          1E41
     S                          1F53
     D                          2044
     F                          2146
     G                          2247
     H                          2348
     J                          244A
     K                          254B
     L                          264C
     :                          273A
     "                          2822
     ~                          297E
     |                          2B7C
     Z                          2C5A
     X                          2D58
     C                          2E43
     V                          2F56
     B                          3042
     N                          314E
     M                          324D
     <                          333C
     >                          343E
     ?                          353F
     Shift Gray *               372A
     Shift Alt                    **
     Shift Space                3920
     Shift Caps Lock              **
     Shift F1                   5400
     Shift F2                   5500
     Shift F3                   5600
     Shift F4                   5700
     Shift F5                   5800
     Shift F6                   5900
     Shift F7                   5A00
     Shift F8                   5B00
     Shift F9                   5C00
     Shift F10                  5D00
     Shift F11                  8700
     Shift F12                  8800
     Shift Num Lock               **
     Shift Scroll Lock            **
     Shift 7 (number pad)       4737
     Shift 8 (number pad)       4838
     Shift 9 (number pad)       4939
     Shift Gray -               4A2D
     Shift 4 (number pad)       4B34
     Shift 5 (number pad)       4C35
     Shift 6 (number pad)       4D36
     Shift Gray +               4E2B
     Shift 1 (number pad)       4F31
     Shift 2 (number pad)       5032
     Shift 3 (number pad)       5133
     Shift 0 (number pad)       5230
     Shift . (number pad)       532E
     Shift SysReq                 **
     Shift Key 45 [1]           567C
     Shift Enter (number pad)   1C0D
     Shift Gray /               352F
     Shift PrtSc                  **
     Shift Pause                  **
     Shift Gray Home            4700
     Shift Gray Up Arrow        4800
     Shift Gray Page Up         4900
     Shift Gray Left Arrow      4B00
     Shift Gray Right Arrow     4D00
     Shift Gray End             4F00
     Shift Gray Down Arrow      5000
     Shift Gray Page Down       5100
     Shift Gray Insert          5200
     Shift Gray Delete          5300

     Ctrl Esc                   011B
     Ctrl 1                       --
     Ctrl 2 (NUL)               0300
     Ctrl 3                       --
     Ctrl 4                       --
     Ctrl 5                       --
     Ctrl 6 (RS)                071E
     Ctrl 7                       --
     Ctrl 8                       --
     Ctrl 9                       --
     Ctrl 0                       --
     Ctrl -                     0C1F
     Ctrl =                       --
     Ctrl Backspace (DEL)       0E7F
     Ctrl Tab                   9400
     Ctrl q (DC1)               1011
     Ctrl w (ETB)               1117
     Ctrl e (ENQ)               1205
     Ctrl r (DC2)               1312
     Ctrl t (DC4)               1414
     Ctrl y (EM)                1519
     Ctrl u (NAK)               1615
     Ctrl i (HT)                1709
     Ctrl o (SI)                180F
     Ctrl p (DEL)               1910
     Ctrl [ (ESC)               1A1B
     Ctrl ] (GS)                1B1D
     Ctrl Enter (LF)            1C0A
     Ctrl a (SOH)               1E01
     Ctrl s (DC3)               1F13
     Ctrl d (EOT)               2004
     Ctrl f (ACK)               2106
     Ctrl g (BEL)               2207
     Ctrl h (Backspace)         2308
     Ctrl j (LF)                240A
     Ctrl k (VT)                250B
     Ctrl l (FF)                260C
     Ctrl ;                       --
     Ctrl '                       --
     Ctrl `                       --
     Ctrl Shift                   **
     Ctrl \ (FS)                2B1C
     Ctrl z (SUB)               2C1A
     Ctrl x (CAN)               2D18
     Ctrl c (ETX)               2E03
     Ctrl v (SYN)               2F16
     Ctrl b (STX)               3002
     Ctrl n (SO)                310E
     Ctrl m (CR)                320D
     Ctrl ,                       --
     Ctrl .                       --
     Ctrl /                       --
     Ctrl Gray *                9600
     Ctrl Alt                     **
     Ctrl Space                 3920
     Ctrl Caps Lock               --
     Ctrl F1                    5E00
     Ctrl F2                    5F00
     Ctrl F3                    6000
     Ctrl F4                    6100
     Ctrl F5                    6200
     Ctrl F6                    6300
     Ctrl F7                    6400
     Ctrl F8                    6500
     Ctrl F9                    6600
     Ctrl F10                   6700
     Ctrl F11                   8900
     Ctrl F12                   8A00
     Ctrl Num Lock                --
     Ctrl Scroll Lock             --
     Ctrl White Home            7700
     Ctrl White Up Arrow        8D00
     Ctrl White PgUp            8400
     Ctrl Gray -                8E00
     Ctrl White Left Arrow      7300
     Ctrl 5 (number pad)        8F00
     Ctrl White Right Arrow     7400
     Ctrl Gray +                9000
     Ctrl White End             7500
     Ctrl White Down Arrow      9100
     Ctrl White PgDn            7600
     Ctrl White Ins             9200
     Ctrl White Del             9300
     Ctrl SysReq                  **
     Ctrl Key 45 [1]            --  
     Ctrl Enter (number pad)    1C0A
     Ctrl / (number pad)        9500
     Ctrl PrtSc                 7200
     Ctrl Break                 0000
     Ctrl Gray Home             7700
     Ctrl Gray Up Arrow         8DE0
     Ctrl Gray Page Up          8400
     Ctrl Gray Left Arrow       7300
     Ctrl Gray Right Arrow      7400
     Ctrl Gray End              7500
     Ctrl Gray Down Arrow       91E0
     Ctrl Gray Page Down        7600
     Ctrl Gray Insert           92E0
     Ctrl Gray Delete           93E0

     Alt Esc                    0100
     Alt 1                      7800
     Alt 2                      7900
     Alt 3                      7A00
     Alt 4                      7B00
     Alt 5                      7C00
     Alt 6                      7D00
     Alt 7                      7E00
     Alt 8                      7F00
     Alt 9                      8000
     Alt 0                      8100
     Alt -                      8200
     Alt =                      8300
     Alt Backspace              0E00
     Alt Tab                    A500
     Alt q                      1000
     Alt w                      1100
     Alt e                      1200
     Alt r                      1300
     Alt t                      1400
     Alt y                      1500
     Alt u                      1600
     Alt i                      1700
     Alt o                      1800
     Alt p                      1900
     Alt [                      1A00
     Alt ]                      1B00
     Alt Enter                  1C00
     Alt Ctrl                     **
     Alt a                      1E00
     Alt s                      1F00
     Alt d                      2000
     Alt f                      2100
     Alt g                      2200
     Alt h                      2300
     Alt j                      2400
     Alt k                      2500
     Alt l                      2600
     Alt ;                      2700
     Alt '                      2800
     Alt `                      2900
     Alt Shift                    **
     Alt \                      2B00
     Alt z                      2C00
     Alt x                      2D00
     Alt c                      2E00
     Alt v                      2F00
     Alt b                      3000
     Alt n                      3100
     Alt m                      3200
     Alt ,                      3300
     Alt .                      3400
     Alt /                      3500
     Alt Gray *                 3700
     Alt Space                  3920
     Alt Caps Lock                **
     Alt F1                     6800
     Alt F2                     6900
     Alt F3                     6A00
     Alt F4                     6B00
     Alt F5                     6C00
     Alt F6                     6D00
     Alt F7                     6E00
     Alt F8                     6F00
     Alt F9                     7000
     Alt F10                    7100
     Alt F11                    8B00
     Alt F12                    8C00
     Alt Num Lock                 **
     Alt Scroll Lock              **
     Alt Gray -                 4A00
     Alt Gray +                 4E00
     Alt 7 (number pad)           # 
     Alt 8 (number pad)           # 
     Alt 9 (number pad)           # 
     Alt 4 (number pad)           # 
     Alt 5 (number pad)           # 
     Alt 6 (number pad)           # 
     Alt 1 (number pad)           # 
     Alt 2 (number pad)           # 
     Alt 3 (number pad)           # 
     Alt Del                      --
     Alt SysReq                   **
     Alt Key 45 [1]               --
     Alt Enter (number pad)     A600
     Alt / (number pad)         A400
     Alt PrtSc                    **
     Alt Pause                    **
     Alt Gray Home              9700
     Alt Gray Up Arrow          9800
     Alt Gray Page Up           9900
     Alt Gray Left Arrow        9B00
     Alt Gray Right Arrow       9D00
     Alt Gray End               9F00
     Alt Gray Down Arrow        A000
     Alt Gray Page Down         A100
     Alt Gray Insert            A200
     Alt Gray Delete            A300

  -------------------------------------------------------------------------

Footnotes

        [1]   In the United States, the 101/102-key keyboard is shipped
              with 101 keys. Overseas versions have an additional key
              sandwiched between the left Shift key and the Z key. This
              additional key is identified by IBM (and in this table) as
              "Key 45."

        [**]  Keys and key combinations marked ** are used by the ROM BIOS
              but do not put values into the keyboard buffer.

        [--]  Keys and key combinations marked -- are ignored by the ROM
              BIOS.




3. From "http://heim.ifi.uio.no/~stanisls/helppc/make_codes.html":


INT 9 - Hardware Keyboard Make/Break Codes

	Key	     Make  Break		Key    Make  Break

	Backspace     0E    8E			F1	3B    BB
	Caps Lock     3A    BA			F2	3C    BC
	Enter	      1C    9C			F3	3D    BD
	Esc	      01    81			F4	3E    BE
	Left Alt      38    B8			F7	41    C1
	Left Ctrl     1D    9D			F5	3F    BF
	Left Shift    2A    AA			F6	40    C0
	Num Lock      45    C5			F8	42    C2
	Right Shift   36    B6			F9	43    C3
	Scroll Lock   46    C6			F10	44    C4
	Space	      39    B9			F11	57    D7
	Sys Req (AT)  54    D4			F12	58    D8
	Tab	      0F    8F

		    Keypad Keys		       Make   Break

		    Keypad 0  (Ins)		52	D2
		    Keypad 1  (End) 		4F	CF
		    Keypad 2  (Down arrow)	50	D0
		    Keypad 3  (PgDn)		51	D1
		    Keypad 4  (Left arrow)	4B	CB
		    Keypad 5			4C	CC
		    Keypad 6  (Right arrow)	4D	CD
		    Keypad 7  (Home)		47	C7
		    Keypad 8  (Up arrow)	48	C8
		    Keypad 9  (PgUp)		49	C9
		    Keypad .  (Del) 		53	D3
		    Keypad *  (PrtSc)		37	B7
		    Keypad -			4A	CA
		    Keypad +			4E	CE

	       Key    Make  Break	       Key    Make  Break

		A      1E    9E 		N      31    B1
		B      30    B0 		O      18    98
		C      2E    AE 		P      19    99
		D      20    A0 		Q      10    90
		E      12    92 		R      13    93
		F      21    A1 		S      1F    9F
		G      22    A2 		T      14    94
		H      23    A3 		U      16    96
		I      17    97 		V      2F    AF
		J      24    A4 		W      11    91
		K      25    A5 		X      2D    AD
		L      26    A6 		Y      15    95
		M      32    B2 		Z      2C    AC

	       Key    Make  Break	       Key    Make  Break

		1      02    82 		-      0C    8C
		2      03    83 		=      0D    8D
		3      04    84 		[      1A    9A
		4      05    85 		]      1B    9B
		5      06    86 		;      27    A7
		6      07    87 		'      28    A8
		7      08    88 		`      29    A9
		8      09    89 		\      2B    AB
		9      0A    8A 		,      33    B3
		0      0B    8B 		.      34    B4
						/      35    B5


Enhanced Keyboard Keys (101/102 keys)

	Control Keys		  Make		  Break

	Alt-PrtSc (SysReq)	  54		  D4
	Ctrl-PrtSc		  E0 37 	  E0 B7
	Enter			  E0 1C 	  E0 9C
	PrtSc			  E0 2A E0 37	  E0 B7 E0 AA
	Right Alt		  E0 38 	  E0 B8
	Right Ctrl		  E0 1D 	  E0 9D
	Shift-PrtSc		  E0 37 	  E0 B7
	/			  E0 35 	  E0 B5
	Pause			  E1 1D 45 E1 9D C5  (not typematic)
	Ctrl-Pause (Ctrl-Break)   E0 46 E0 C6	     (not typematic)

	- Keys marked as "not typematic" generate one stream of bytes
	  without corresponding break scan code bytes (actually the
	  break codes are part of the make code).


			Normal Mode or
			Shift w/Numlock
	Key		 Make	 Break	   |----- Numlock on ------.
					      Make	    Break
	Del		 E0 53	 E0 D3	   E0 2A E0 53	 E0 D3 E0 AA
	Down arrow	 E0 50	 E0 D0	   E0 2A E0 50	 E0 D0 E0 AA
	End		 E0 4F	 E0 CF	   E0 2A E0 4F	 E0 CF E0 AA
	Home		 E0 47	 E0 C7	   E0 2A E0 47	 E0 C7 E0 AA
	Ins		 E0 52	 E0 D2	   E0 2A E0 52	 E0 D2 E0 AA
	Left arrow	 E0 4B	 E0 CB	   E0 2A E0 4B	 E0 CB E0 AA
	PgDn		 E0 51	 E0 D1	   E0 2A E0 51	 E0 D1 E0 AA
	PgUp		 E0 49	 E0 C9	   E0 2A E0 49	 E0 C9 E0 AA
	Right arrow	 E0 4D	 E0 CD	   E0 2A E0 4D	 E0 CD E0 AA
	Up arrow	 E0 48	 E0 C8	   E0 2A E0 48	 E0 C8 E0 AA

	Key	      |--Left Shift Pressed--.	  |--Right Shift Pressed--.
			 Make	       Break	      Make	    Break
	Del	      E0 AA E0 53   E0 D3 E0 2A    E0 B6 E0 53	 E0 D3 E0 36
	Down arrow    E0 AA E0 50   E0 D0 E0 2A    E0 B6 E0 50	 E0 D0 E0 36
	End	      E0 AA E0 4F   E0 CF E0 2A    E0 B6 E0 4F	 E0 CF E0 36
	Home	      E0 AA E0 47   E0 C7 E0 2A    E0 B6 E0 47	 E0 C7 E0 36
	Ins	      E0 AA E0 52   E0 D2 E0 2A    E0 B6 E0 52	 E0 D2 E0 36
	Left arrow    E0 AA E0 4B   E0 CB E0 2A    E0 B6 E0 4B	 E0 CB E0 36
	PgDn	      E0 AA E0 51   E0 D1 E0 2A    E0 B6 E0 51	 E0 D1 E0 36
	PgUp	      E0 AA E0 49   E0 C9 E0 2A    E0 B6 E0 49	 E0 C9 E0 36
	Right arrow   E0 AA E0 4D   E0 CD E0 2A    E0 B6 E0 4D	 E0 CD E0 36
	Up arrow      E0 AA E0 48   E0 C8 E0 2A    E0 B6 E0 48	 E0 C8 E0 36
	/	      E0 AA E0 35   E0 B5 E0 2A    E0 B6 E0 35	 E0 B5 E0 36


	- The PS/2 models have three make/break scan code sets.  The first
	  set matches the PC & XT make/break scan code set and is the one
	  listed here.	Scan code sets are selected by writing the value F0
	  to the keyboard via the 8042 (port 60h).  The following is a brief
	  description of the scan code sets (see the PS/2 Technical Reference
	  manuals for more information on scan code sets 2 and 3):

	/  set 1, each key has a base scan code.  Some keys generate
	   extra scan codes to generate artificial shift states.  This
	   is similar to the standard scan code set used on the PC and XT.
	/  set 2, each key sends one make scan code and two break scan
	   codes bytes (F0 followed by the make code).	This scan code
	   set is available on the IBM AT also.
	/  set 3, each key sends one make scan code and two break scan
	   codes bytes (F0 followed by the make code) and no keys are
	   altered by Shift/Alt/Ctrl keys.
	/  typematic scan codes are the same as the make scan code

	- Some Tandy 1000's do not handle Alt key combinations when multiple
	  shift keys are pressed.  The Alt-Shift-H combination loses the Alt.
	- extended keys like (F11, F12) can only be read with systems that
	  have extended keyboard BIOS support (or INT 9 extensions);  to
	  read these special keys on these systems INT 16,10 must be used


******************************************************************************
***                         GRLDR  Error messages                          ***
******************************************************************************

1. Missing MBR-helper.

	The helper function in the sectors that immediately follow the MBR is
	not present, or it has been erased by a virus or by Windows XP/Vista.

	Run the bootlace.com utility to fix the problem.

2. Buggy BIOS!

	Your BIOS is too buggy. It even has no support for INT13/AH=8.

	No solution except flashing your BIOS. Buggy BIOSes will encounter
	more and more problems with grub4dos in the future.

3. This partition is NTFS but with unknown boot record. Please install
Microsoft NTFS boot sectors to this partition correctly, or create an
FAT12/16/32 partition and place the same copy of GRLDR and MENU.LST there.

	The boot record was changed or erased by Microsoft Windows XP Service
	Pack 2.

	You may install the old boot record introduced with the	original clean
	Windows 2K/XP. As another solution, you may create an FAT partition
	for your system, and copy GRLDR and your MENU.LST to its root dir.

	While the startup code of grldr might fail to load GRLDR in NTFS
	partitions, it always successfully loads GRLDR in FAT partitions(and
	even in ext2/ext3 partitions).

	Note that NTLDR only loads the startup code of grldr(i.e., the leading
	16 sectors of grldr), not the whole grldr file.

	Thus, C:\GRLDR must exist(here C: can be NTFS), since it is used for
	BOOT.INI and NTLDR. If C: is NTFS, X:\GRLDR should exist as well,
	where X: stands for a certain FAT partition.


******************************************************************************
***                             Known BIOS bugs                            ***
******************************************************************************

1. Some newer Dell machines have no int13/AH=43h support. You may encounter
	failure when trying to write-access an emulated disk.

	Note: This bug is serious! The old "root+setup" installation method
	(in real mode grub environment) uses INT13 to write the first sector
	of stage2. It will fail for the buggy DELL machine when stage2 is
	accessed with LBA mode.

2. Some newer machines have no int15/AH=87h support. You may encounter failure
	when accessing a memdrive.

3. Some buggy BIOSes won't boot bootable.iso(See above).(qemu can boot it fine)

4. Some BIOSes have no int15/AH=24h(gate A20 control) support. It will
	encounter problems with GRUB4DOS in the future.

5. Some USB BIOSes have a buggy int13/AH=08h function which returns incorrect
	geometry in CX and DH registers. They will encounter various failure.

	Note: The int13/AH=08h function call is very important for the normal
	CHS-mode int13 disk access. If there is no other way to determine the
	geometry, a USB BIOS programmer should probe the first sector of the
	USB storage device and give a right geometry for the int13/AH=08h call.
	A good BIOS programmer should implement EBIOS functions for USB storage
	devices, especially functions 41h, 42h, 43h and 48h, which are very
	important for BIOS-based programs or systems such as GRUB and DOS.

6. Reports say some newer Dell machines violently destroyed the int0d vector
	and will cause failure or even hang the machine when running GRUB.EXE
	from DOS.


******************************************************************************
***                             Known Problems                             ***
******************************************************************************

1.	Running GRUB.EXE from a DOS box of Windows 9x/Me could hang the
	machine, especially for some systems with USB support. You may
	encounter the same problem when running GRUB.EXE through KEXEC under
	Linux.

Note:	You don't have to run GRUB.EXE from protected mode of Win9x, which
	could hang the machine; Instead, you usually want to run GRUB.EXE
	after you have done a "Restart the computer in MS-DOS mode", which
	is safe enough.

2.	The default chainloader action will keep A20 on. Some buggy DOS XMS
	memory managers could hang the machine. You may use the --disable-a20
	option in the chainloader line and try again. Anyway, you should avoid
	using those buggy memory managers.

3.	THTF BIOS L4S5M Ver 1.1a(dated 2002-1-10) has a buggy int15 which
	causes hang at the boot of a multi boot kernel(memdisk for example).

4.	A Chinese DOS system software, the TechWay SCS, will not work with
	newer versions of GRUB.EXE. In general, TSRs that take antitracking
	measures will not work with GRUB.EXE any more.


******************************************************************************
***        List of binary files and their corresponding source files       ***
******************************************************************************

binary file	main source file	other included source or binary files
-------------   ----------------	-------------------------------------

bootlace.com	bootlacestart.S		bootlace.inc, grldrstart.S

grldr		grldrstart.S		pre_stage2(binary, See note below)

grldr.mbr	mbrstart.S		grldrstart.S

grub.exe	dosstart.S		pre_stage2(binary, See note below)

hmload.com	hmloadstart.S

-----------------------------------------------------------------------------

Note: pre_stage2 is the main body of GNU GRUB and it is simply appended to
grldrstart/dosstart in binary format to form our grldr/grub.exe.

Note: The GRUB file(WITHOUT .EXE suffix) is a static-linked ELF executable
program for Linux, normally called the GRUB Shell. The GRUB Shell is a boot-
manager, but not a boot-loader(the "boot" command won't work in GRUB Shell). 
GRUB.EXE(with KEXEC) can be used as a bootloader running directly under Linux.

******************************************************************************
***             Memory Layout for Quiting to DOS from GRUB.EXE             ***
******************************************************************************

The quit command is implemented to return to DOS in the instance that GRUB.EXE
is started off DOS.

1. Before GRUB.EXE transfers control to pre_stage2, it will copy 640KB of
conventional memory to physical address 0x200000(i.e., 2MB), and write 4 long
integers immediately follows the backup copy of the conventional memory:
	At 0x2A0000:	0x50554B42, it is the "BKUP" signature.

	At 0x2A0004:	Gate A20 status under DOS: non-zero means A20 on;
			zero means A20 off. Update: A20 always on, see below.

	At 0x2A0008:	high word is boot-CS, low word is boot-IP. The quit
			command uses this entry point to return to DOS.

	At 0x2A000C:	CheckSum: the sum of all long integers in the memory
			range from 0x200000 to 0x2A000F is 0.

2. If the above memory structure is corrupted by a grub command, the quit
command will issue an error message and refuse to exit from grub.

3. Because GRUB may corrupt extended memory, you should better avoid using
extended memory under DOS before running GRUB.EXE.

4. Gate A20 will be enabled by GRUB.EXE. Hopefully this would hurt nothing.


******************************************************************************
***             Memory usage in conventional/low memory area               ***
******************************************************************************

1. boot.c, fsys_reiserfs.c: 8K below 0x68000.

2. fsys_ext2fs.c, fsys_minix.c: 1K below 0x68000.

3. fsys_jfs.c: 4K + 256 bytes below 0x68000.

4. fsys_reiserfs.c: 202 bytes at 0x600.

5. fsys_xfs.c: 188 bytes at 0x600.

6. fsys_xfs.c: (logical block size) bytes below 0x68000.

7. geometry tune: 0x50000 - 0x5ffff.

******************************************************************************
***                Command-line Length about GRUB.EXE                      ***
******************************************************************************

GRUB.EXE now can be started in CONFIG.SYS with the **DEVICE** command:

	DEVICE=grub.exe [--config-file="FILENAME_OR_COMMANDS"]

1. If GRUB.EXE is invoked with DEVICE command and FILENAME_OR_COMMANDS is a
collection of some GRUB commands separated by semi-colon, then the length of
FILENAME_OR_COMMANDS can be nearly 4KB ----Supprise? But true!  MS-DOS 7+
even allows a much longer line, but 4KB seems enough for our use of GRUB.EXE.
This is very useful when we want to embed a big menu into the command line.
Note that GRLDR hasn't yet supported any command-line arguments.

2. If GRUB.EXE is invoked with INSTALL command, the option length has a limit
of 80 characters(including the leading "--config-file=" part). An overflow may
hang up MS-DOS immediately.

3. If GRUB.EXE is invoked with SHELL command, the option length has a limit of
126 characters(including the leading "--config-file=" part). Overflow won't
hang up MS-DOS, but the line will be cut short. This limit is the same as that
in the console-DOS-prompt or in a BAT file.

4. The DOS editor EDIT does not allow to create a line of 4KB long. So use
another editor, for example, vi for Linux, please.

5. The DEVICE=GRUB.EXE line can be used together with other DEVICE commands
such as DEVICE=HIMEM.SYS and DEVICE=EMM386.EXE. The GRUB.EXE line should
occur before the EMM386.EXE line in order to avoid the rejection by EMM386.
Update: Since 0.4.2, GRUB.EXE works well even after EMM386.EXE is loaded.

6. In any case mentioned above, you can return back to DOS by quit command.

7. Memory usage about command-line menu: The 4KB command-line menu starts at
physical address 0x0800 and ends at 0x17FF.

******************************************************************************
***          New Syntax for the DEFAULT/SAVEDEFAULT Commands               ***
******************************************************************************

In addition to the original usage of "default NUM" and "default saved", now
there is a new usage of "default FILE", like this:

		default (hd0,0)/default

Note that FILE must have a valid DEFAULT file format. A sample DEFAULT file
is included in the release. You may copy it to wherever you like, but you
should avoid modifying its content manually. The DEFAULT file may be used
in this way:

(1) First, you should copy a default file with valid format to somewhere in
your operating system.

(2) Secondly, you should use the "default FILE" command of GRUB to announce
the use of FILE as our new default file for being written by "savedefault".

(3) Then, you may use "savedefault" command to save the desired entry number
into this new default file.

(4) OK, at next boot, you may read the saved entry number by using the same
"default FILE" command as mentioned in above (2).

And the SAVEDEFAULT command now accept an options `--wait=T', like this:

		savedefault --wait=5

If `--wait=T' is specified and T is non-zero, savedefault will prompt
the user with a message just before it writes to disk. The write operation
will be cancelled in T seconds if the `Y' key was not pressed.

Here is a sample menu.lst file:

#--------------------begin menu.lst---------------------------------------
color black/cyan yellow/cyan
timeout 30
default /default

title find and load NTLDR of Windows NT/2K/XP
find --set-root /ntldr
chainloader /ntldr
savedefault --wait=2

title find and load CMLDR, the Recovery Console of Windows NT/2K/XP
fallback 2
find --set-root /cmldr
chainloader /cmldr
#####################################################################
# write string "cmdcons" to memory 0000:7C03 in 2 steps:
#####################################################################
# step 1. Write 4 chars "cmdc" at 0000:7C03
write 0x7C03 0x63646D63
# step 2. Write 3 chars "ons" and an ending null at 0000:7C07
write 0x7C07 0x00736E6F
savedefault --wait=2

title find and load IO.SYS of Windows 9x/Me
find --set-root /io.sys
chainloader /io.sys
savedefault --wait=2

title floppy (fd0)
chainloader (fd0)+1
rootnoverify (fd0)
savedefault --wait=2

title find and boot Linux with menu.lst already installed
find --set-root /sbin/init
savedefault --wait=2
configfile /boot/grub/menu.lst

title find and boot Mandriva with menu.lst already installed
find --set-root /etc/mandriva-release
savedefault --wait=2
configfile /boot/grub/menu.lst

title back to dos
savedefault --wait=2
quit

title commandline
savedefault --wait=2
commandline

title reboot
savedefault --wait=2
reboot

title halt
savedefault --wait=2
halt
#--------------------end menu.lst---------------------------------------

Note 1:	The file DEFAULT must exist and have a proper format as stated above.
	Or else, the default/savedefault commands won't function well.

Note 2:	The file DEFAULT which is in the same dir as a certain MENU.LST file
	is called associated with the MENU.LST file.

Note 3:	The associated DEFAULT file will take effect automatically if there
	are no `default' commands present.

Note 4:	Just before a menu file gains control(e.g., it is the associated
	MENU.LST of a GRLDR file, or it was specified via
	`grub.exe --config-file=(DEVICE)/PATH/YOUR_MENU_FILE', or it was
	specified by the `configfile' command of grub), its associated
	DEFAULT file will be used if present, until an explicit `default'
	command is encountered.

******************************************************************************
***                   The New `cdrom' Command Syntax                       ***
******************************************************************************

1. Initialize the ATAPI CDROM devices:

	grub> cdrom --init

   This will display the number of atapi cdroms found: atapi_dev_count

2. Stop the ATAPI CDROM devices:

	grub> cdrom --stop

   This will set atapi_dev_count to 0.

3. Add IO ports for searching the atapi cdrom devices. For example:

	grub> cdrom --add-io-ports=0x03F601F0

After running `cdrom --init' and `map --hook', the cdroms can be accessed
through devices (cd0), (cd1), ...

Note 1: If the system does not fully support the ATAPI CD-ROM specifications,
	you will encounter failure when trying to access the (cdX) devices.

Note 2: After doing a `cdrom --stop', you should do a `map --unhook'. Of
	course you may `map --hook' again if there are mapped drives.

Note 3: After adding IO ports, you should do a `map --unhook' followed by a
	`cdrom --init' and then followed by a `map --hook'.

	By default, these ports are used for searching cdroms(so they needn't
	be added):

		0x03F601F0, 0x03760170, 0x02F600F0,
		0x03860180, 0x6F006B00, 0x77007300.

Note 4: The BIOS might have offered a cdrom interface. It would be (cd). After
	`cdrom --init' and `map --hook', we might have our (cd0), (cd1), ...
	available. It is likely that one of them could access the same media
	as the BIOS-offered (cd).

Note 5: You may access the (cd) and (cdX)'es in the blocklist way. Example:

		cat --hex (cd0)16+2

	The cdrom sectors are big sectors with a size of 2048 bytes.

Note 6:	The iso9660 filesystem driver has Rock-Ridge extension support, but
	has no Joliet extension support. So you may encounter failure when
	you attempt to read files on a Joliet CD.

Note 7: The (cd) or (cdX)'es can be booted now. Examples:

		chainloader (cd)
		boot

		chainloader (cd0)
		boot

		chainloader (cd1)
		boot

	You should already have access to the CD sectors before you can
	chainload it.

******************************************************************************
***                   About the New `setvbe' Command                       ***
******************************************************************************

Gerardo Richarte contributed the `setvbe' code and the following comment:

	New command is `setvbe', and can be used to change the video mode
	before executing the kernel.

	For example, you can do

		setvbe 1024x768x32

	this will scan the list of available modes and set it, and
	automatically append a `video=' option to each subsequent kernel
	command-line. The appended `video=' option is like this:

		video=1024x768x32@0xf0000000,4096

	where 0xf0000000 is the video framebuffer address as reported by vbe,
	and 4096 is the size of a scanline in bytes (also as reported by vbe).

	This is really useful if you want to give some graphics support to your
	OS, but you don't want to implement any video functionality other than
	writing a pixel to video memory.


******************************************************************************
***                   About the DOS utility `hmload'                       ***
******************************************************************************

This program was written by John Cobb (Queen Mary, University of London).

John Cobb's note:

	To make use of the ram drive feature I wrote a program `hmload' to load
	an arbitrary file to an arbitrary address in high memory. The program
	is not very sophisticated and relies on XMS to turn on the A20 line.
	(Also one must be very careful to steer clear of any areas of memory
	already in use).

	Under Linux we generated a disk image `dskimg' (with the kernel and
	Initrd and a partition table).

	Using this our boot procedure looked something like this:

	hmload -fdskimg -a128
	fixrb
	<unload network drivers>
	grub

		map --ram-drive=0x81
		map --rd-base=0x8000000
		map --rd-size=0x400000
		root (rd,0)
		kernel /kernel root=/dev/ram0 rw ip=bootp ramdisk_size=32768 ...
		initrd /initrd
		boot

See http://sysdocs.stu.qmul.ac.uk/sysdocs/Comment/GrubForDOS/ for details.

Update 2007-12-05:

	Now the MAP command can handle gzipped (rd) image. One can use this
	feature with the hmload utility. For example,

	step 1. Load the gzipped image under DOS at a relatively low address:

		hmload -fdskimg.gz -a16

	step 2. Unload network drivers.

	step 3. Run GRUB.EXE.

	step 4. At the grub prompt, run these commands:

		map --rd-base=0x1000000	# set rd-base address to be 16M
		map --rd-size=<the accurate size of dskimg.gz in bytes>
		map (rd)+1 (hd0)	# This will decompress (rd) and place
					# the decompressed image at the top end
					# of the extended memory. The (rd)+1
					# here has special meaning and stands
					# for the whole (rd) device. You must
					# use (rd)+1 instead of (rd).
		map --hook
		root (hd0,0)
		kernel /kernel root=/dev/ram0 rw ip=bootp ramdisk_size=32768 ...
		initrd /initrd
		map --unhook
		map (hd0) (hd0)		# Delete the map; this is needed.
		boot


******************************************************************************
***                      Notes on the use of stack                         ***
******************************************************************************

The protected-mode and real-mode stack are merged at physical address 0x2000.

All functions should use at most 2K stack space(0x1800-0x2000). So each
subfunction should use as little stack as possible to avoid stack-overflow.

Don't use recursive functions because they could expend too much stack space.

The original protected mode stack at 0x68000(expand-down) is free now and can
be reused for any purposes.


******************************************************************************
***                  A bug was found in the CDROM driver                   ***
******************************************************************************

It seems the cdrom must be connected as the master device of an IDE controller.

If cdrom is slave, the driver will fail to read the cdrom sectors. Hope someone

could fix this problem.


******************************************************************************
***                        BIOS and the (cd) drive                         ***
******************************************************************************

When BIOS boots a no-emulation-mode bootable CD-ROM, it allocates a BIOS drive
number to the CD. If the boot image of the CD-ROM is grldr or stage2_eltorito,
then GRUB can access the CD-ROM media through the drive number allocated by
BIOS. The device name of the CD-ROM is (cd).

BIOS can allocate a BIOS drive number to a no-emulation-mode CDROM even when
the CDROM is not bootable. QEMU has done so. At boot time, GRUB4DOS will
search drives 0x80-0xFF for a possible no-emulation-mode CDROM drive allocated
by BIOS. So if BIOS offered a CDROM interface of int13 EBIOS functions 41h-4Eh,
then the (cd) device will be automatically available in GRUB4DOS.


******************************************************************************
***              The way of disk emulation changed greatly                 ***
******************************************************************************

The way of disk emulation has changed greatly since 0.4.2 final. Please don't
mix newer versions with older versions when disk emulation features are used.

The newer versions won't automatically unhook emulations established in a
previous grub4dos environment. The GRUB.EXE of an older version will
automatically dismiss emulations established earlier, before transferring
control to the main grub program(i.e., pre_stage2).


******************************************************************************
***            FreeDOS EMM386 v2.26 (2006-08-27) VCPI problem              ***
******************************************************************************

The VCPI function "AX=DE0Ch - Switch From Protected Mode to V86 Mode" of
FreeDOS EMM386 v2.26 was not implemented properly(it always hangs). As an
alternative, you can use Microsoft's EMM386 instead.

Even while emm386 is running, grub.exe can be started. But if you try to quit
to DOS from grub4dos by using the `quit' command, the VCPI function DE0C will
be called. If EMM386 is of Microsoft, everything goes ok. If EMM386 is of
FreeDOS, the machine will hang.


******************************************************************************
***                 New options for map were added                         ***
******************************************************************************

Along with 0.4.2 final, there are two new options for the map command. They
are --safe-mbr-hook=SMH and --int13-scheme=SCH. Both are related with disk
emulation for use(as smoothly as possible) in the Win9x environment.

SMH can take either of the two values 0 and 1. By default, SMH is 1. If you
encountered problems of disk emulation under Win9x, you may insert a line of

	map --safe-mbr-hook=0

before the `boot' command and try again.

Also SCH may take either 0 or 1 at present. By default, SCH is 1. If you
encountered disk emulation problems under Win9x, you may insert a line of

	map --int13-scheme=0

before the `boot' command and try again.

Note by the way. Like --safe-mbr-hook and --int13-scheme, the MAP command has
a few other options that are used for setting global variables. They are here:

	map --floppies=M

M can be 0, 1, or 2. MAP will set a proper value at 0040:0010 by using M.

	map --harddrives=N

N can be between 0 and 127(inclusive). MAP will set 0040:0075 to N.

	map --memdisk-raw=RAW

RAW default to 1. If RAW=0, `int15/ah=87h' will be used to access memdrives.

	map --ram-drive=RD

RD default to 0x7F which is a floppy. If the RAM DRIVE is a hard drive image
(with partition table in the first sector), you should set RD >= 0x80 and RD
< 0xFF.

	map --rd-base=ADDR

	map --rd-size=SIZE

ADDR specifies the physical base address of the ramdisk image. SIZE specifies
the size in bytes of the ramdisk image. ADDR default to 0. SIZE is also default
to 0, but a size of 0 means 4GB, not a zero-long disk. The RAM DRIVE can be
accessed in the GRUB environment using the (rd) device.


******************************************************************************
***                   About the new map option --in-situ                   ***
******************************************************************************

--in-situ is used with hard drive images or hardrive partitions. With an
in-situ map, we can typically use a logical partition as a primary partition.

In-situ map is a whole drive map. It only virtualize the partition table and
the number of hidden sectors in the BPB of the DOS Boot Record.

While disk emulation may encounter various problems with win9x, the in-situ map
works fine with win9x.

Note that --in-situ will not change the real partition table.

Example:

	map --in-situ (hd0,4)+1 (hd0)


******************************************************************************
***                      The PARTNEW Command Syntax                        ***
******************************************************************************

Besides the mappings in the above section, you may instead choose to create a
new primary partition with the PARTNEW command. PARTNEW can generate a primary
partition entry (in the partition table) for a logical partition.

For example,

	partnew (hd0,3) 0x07 (hd0,4)+1

where the file (hd0,4)+1 stands for the whole partition (hd0,4). This command
will create a new primary partition (hd0,3) whose type is 0x07 and whose
contents/data is the same as that of the logical partition (hd0,4).

Just like a whole logical partition, a contiguous partition image file can
also be used with PARTNEW:

	partnew (hd0,3) 0x00 (hd0,0)/my_partition.img

The type 0x00 indicates a type-auto-detection of the image MY_PARTITION.IMG.
The above command will create a new primary partition (hd0,3) with a proper
type and with contents/data being exactly that of the contiguous file
(hd0,0)/my_partition.img.

PARTNEW will automatically correct the "hidden sectors" in the BPB and the
modification will be permanent. And PARTNEW modifies the partition table
permanently.

In addition to creating new partition entries, PARTNEW can also be used to
delete(erase, or wipe) a primary partition entry. For example,

	partnew (hd0,3) 0 0 0

which will empty the last entry in the partition table in MBR. Generally,
you should use the form of "partnew PARTITION 0 0 0" to erase the entry.
Note that only the entry would be erased, and the data stored in the partition
will not be touched.

******************************************************************************
***              Newly implemented operators `&&' and `||'                 ***
******************************************************************************

This implementation is very simple. It does not handle operator nesting.

Usage of `&&':

	command1 && command2

Description:

	If command1 returns true, then command2 will be executed.

Usage of `||':

	command1 || command2

Description:

	If command1 returns false, then command2 will be executed.

Examples:

	is64bit && default 0
	is64bit || default 1

******************************************************************************
***          Three new commands is64bit, errnum and errorcheck             ***
******************************************************************************

is64bit and errnum retrieve the value of is64bit and errnum respectively.

errorcheck controls whether or not the error will be handled. By default,
errorcheck is on, and menu script execution will stop on error. If errorcheck
is off, the script will continue to execute upto a boot command. A boot command
will turn the errorcheck on.


******************************************************************************
***              Use numeric keys to select a menu entry                   ***
******************************************************************************

If, for example, you intend to goto entry #25, you may press 2 followed by 5.


******************************************************************************
***           Use the INSERT key to debug step by step at startup          ***
******************************************************************************

Some buggy machines could fail to enter grub4dos environment. They might hang
or reboot unexpectedly. Press INSERT as quickly as possible on startup, and
you can get a chance to single-step the boot process and see how far it can
go, and then report bugs.


******************************************************************************
***             The debug command syntax has been changed                  ***
******************************************************************************

The DEBUG command now can be used to control the verbosity of command output:

		debug [ on | off | normal | status | INTEGER ]

0 or off for silent
1 or normal for normal
2 to 0x7FFFFFFF or on for verbose


******************************************************************************
***                     GRUB4DOS and Windows Vista                         ***
******************************************************************************

First, use the following command to create a boot entry:

	bcdedit /create /d "GRUB for DOS" /application bootsector

The result will look like this:

The entry {05d33150-3fde-11dc-a457-00021cf82fb0} was successfully created.

The long string {05d33150-3fde-11dc-a457-00021cf82fb0} is the id for this
entry.

Then, use the following commands to set boot parameters:

	bcdedit /set {id} device boot
	bcdedit /set {id} path \grldr.mbr
	bcdedit /displayorder {id} /addlast

Please replace {id} with the actual id returned from the previous command.

Finally, copy GRLDR.MBR to C:\ or wherever your boot drive is, and copy GRLDR
and menu.lst to the root directory of any FAT16/FAT32/EXT2/NTFS partition.

Note: A boot partition should be the active primary partition with BOOTMGR
      inside. The `device boot' indicates grldr.mbr should be in the boot
      partition.

Lianjiang has written down a script to automate the tasks:

	@echo off
	rem by lianjiang
	cls
	echo.
	echo   Please run as administrator
	echo.
	pause
	set gname=GRUB for DOS
	set vid=
	set timeout=5
	bcdedit >bcdtemp.txt
	type bcdtemp.txt | find "\grldr.mbr" >nul && echo. && echo  BCD entry existing, no need to install. && pause && goto exit
	bcdedit  /export "Bcd_Backup" >nul
	bcdedit  /create /d "%gname%" /application bootsector >vid.ini
	for,/f,"tokens=2 delims={",%%i,In (vid.ini) Do (
                  set vida=%%i
	)
	for,/f,"tokens=1 delims=}",%%i,In ("%vida%") Do (
                  set vid={%%i}
	)
	echo %vid%>vid.ini
	bcdedit  /set %vid% device boot >nul
	bcdedit  /set %vid% path \grldr.mbr >nul
	bcdedit  /displayorder %vid% /addlast >nul
	bcdedit  /timeout  %timeout% >nul
	if exist grldr.mbr copy grldr.mbr %systemdrive%\ /y && goto exit
	echo.
	echo   Please copy grldr.mbr to %systemdrive%\
	echo.
	pause
	:exit
	del bcdtemp.txt >nul
-------------------------------------------------------------------
Update: Fujianabc pointed out that

	bcdedit  /set %vid% device boot >nul

should be changed to

	bcdedit  /set %vid% device partition=%SystemDrive% >nul
-------------------------------------------------------------------

You still need to copy grldr yourself.

Notice: It's possible to modify the BCD entry from a different OS, you just
need to specify the location of BCD:

	bcdedit /store D:\boot\BCD ...

Notice: These commands need elevated privileges, they should be used inside
cmd.exe which is started with "Run as administrator".

Notice: People has reported that some version of Vista doesn't support
creating file in C:\ with no extension, even with administrator privileges.
This means grldr can't be placed in C:\. You can solve this by either copy
grldr to another partition, or rename grldr to something like grub.bin. Please
see the following section on how to do this.


******************************************************************************
***                      How to rename grldr                               ***
******************************************************************************

grldr and grldr.mbr use internal boot file name to decide which file to load,
so if you want to change the name, you must also change the embeded setting.
You can do this with the help of grubinst, which can be downloaded at:

http://download.gna.org/grubutil/

grubinst can generate customized grldr.mbr:

	grubinst -o -b=mygrldr C:\mygrldr.mbr

grubinst can also edit existing grldr/grldr.mbr:

	grubinst -e -b=mygrldr C:\mygrldr

	grubinst -e -b=mygrldr C:\mygrldr.mbr

In this case, you must use a grubinst that is compatible with the version of
grub4dos, otherwise the edit will fail.

So, in order to load mygrldr instead of grldr, you can use one of the
following methods:

1. Use customized grldr.mbr to load mygrldr. In this case, you need to change
the embeded boot file name in grldr.mbr. The name of grldr.mbr can be changed
at will.

2. Use mygrldr directly. In this case, you need to change the embeded boot
file name in mygrldr to match its new name.

Notice: The boot file name must conform to the 8.3 naming convention.


******************************************************************************
***                          PXE device                                    ***
******************************************************************************

If PXE service is found at startup, GRUB4DOS will create a virtual device
(pd), through which files from the tftp server can be accessed. You can setup
a diskless boot environment using the following steps:

Client side

You need to boot from PXE ROM.

Server side

You need to configure a dhcp server and a tftp server. In the dhcp server, use
grldr as boot file.

You may also want to load a different menu.lst for different client. GRUB4DOS
will scan the following location for configuration file:

	[/mybootdir]/menu.lst/01-88-99-AA-BB-CC-DD
	[/mybootdir]/menu.lst/C000025B
	[/mybootdir]/menu.lst/C000025
	[/mybootdir]/menu.lst/C00002
	[/mybootdir]/menu.lst/C0000
	[/mybootdir]/menu.lst/C000
	[/mybootdir]/menu.lst/C00
	[/mybootdir]/menu.lst/C0
	[/mybootdir]/menu.lst/C
	[/mybootdir]/menu.lst/default

Here, we assume the network card mac for the client machine is
88:99:AA:BB:CC:DD, and the ip address is 192.0.2.91 (C000025B). /mybootdir is
the directory of the boot file, for example, if boot file is /tftp/grldr, then
mybootdir=tftp.

If none of the above files is present, grldr will use its embeded menu.lst.

This is a menu.lst to illstrate how to use files from the tftp server.

	title Create ramdisk using map
	map --mem (pd)/floppy.img (fd0)
	map --hook
	rootnoverify (fd0)
	chainloader (fd0)+1

	title Create ramdisk using memdisk
	kernel (pd)/memdisk
	initrd (pd)/floppy.img

You can see that the menu.lst is very similar to normal disk boot, you just
need to replace device like (hd0,0) with (pd).

There are some differences between disk device and pxe device:

1. You can't list files in the pxe device.

2. The blocklist command will not work with a file in the pxe device.

3. You must use --mem option if you want to map a file in the pxe device.

When you use chainloader to load file from the pxe device, there is a option
you can use:

	chainloader --raw (pd)/BOOT_FILE

Option --raw works just like --force, but it load file in one go. This can
improve performance in some situation.

You can use the pxe command to control the pxe device.

1. pxe

	If used without any parameter, pxe command will display current
	settings.

2. pxe blksize N

	Set the packet size for tftp transmission. Minimum value is 512,
	maximum value is 1432. This parameter is used primarily for very old
	tftp server where packet larger than 512 byte is not supported.

3. pxe basedir /dir

	Set the base directory for files in the tftp server. If

		pxe basedir /tftp

	then all files in the pxe device is related to directory /tftp, for
	example, (pd)/aa.img correspond to /tftp/aa.img in the server.

	The default value of base directory is the directory of the boot file,
	for example, if boot file is /tftp/grldr, then default base directory
	is /tftp.

4. pxe keep

	Keep the PXE stack. The default behaviour of GRUB4DOS is to unload
	the PXE stack just before it exits.

5. pxe unload

	Unload the PXE stack immediately.



******************************************************************************
***                  New Feature of Relative Path Support                  ***
******************************************************************************

Use the `root' or `rootnoverify' command to specify the `working directory'.

For example:

		root  (hd0,0)/boot/grub

This specifies that the working dir is (hd0,0)/boot/grub. So all subsequent
filenames of the form "/..." will actually refer to (hd0,0)/boot/grub/...

That is to say:

		cat  /menu.lst

will be equivalent to

		cat  (hd0,0)/boot/grub/menu.lst



******************************************************************************
***                 Notation For The Current Root Device                   ***
******************************************************************************


The notation `()' can be used to access the current root device. You may use
`find --set-root ...' to set the current root device, but the find command
does not set the `working dir' of the root device. In this case you should
use `()' to set the working dir after the find command:

		root  ()/boot/grub

Update 2008-05-01:

	FIND can also set the `working directory' now. For example:

		find  --set-root=/tmp  /boot/grub/menu.lst

	It is equivalent to this pair of commands:

		find  --set-root  /boot/grub/menu.lst
		root  ()/tmp


******************************************************************************
***                   The new map option --a20-keep-on                     ***
******************************************************************************


Along with 0.4.3 final, map has a new option --a20-keep-on which is related to
A20 control after a memdrive sector access. Usage:

	map --a20-keep-on=0

It should be used before the "map --hook" command.

By default, A20 will be always on after an RAM INT13 sector access. If
"map --a20-keep-on=0" is used, the A20 status after the INT13 call will be the
same as that before the INT13 call.


******************************************************************************
***                  The CDROM emulation (virtualization)                  ***
******************************************************************************

The CDROM emulation is sometimes called ISO emulation. Here is an example:

	map  (hd0,0)/myiso.iso  (hd32)
	map  --hook
	chainloader  (hd32)
	boot

if myiso.iso is not contiguous and you have enough memory, add a --mem option:

	map  --mem  (hd0,0)/myiso.iso  (hd32)
	map  --hook
	chainloader  (hd32)
	boot

Note: (hd32) is a grub drive number equivalent to (0xA0). If a virtual drive is
specified with a drive number greater than or equal to 0xA0, then it will be
treated as a cdrom (i.e., with 2048-byte big sectors).

Like normal disk emulations, the CDROM emulation also (mainly) works with
real-mode OSes. After a protected-mode OS kernel (such as
WinNT/2K/XP/VISTA/LINUX) gains control, the OS would have no ability to access
the virtual CDROM through BIOS int13.

DOS/Win9x users may google for ELTORITO.SYS and use it in CONFIG.SYS as a
device driver for the virtual cdrom.

Example usage of eltorito.sys in CONFIG.SYS:

	device=eltorito.sys /D:oemcd001

Corresponding MSCDEX command which can be placed in AUTOEXEC.BAT:

	MSCDEX /D:oemcd001 /L:D


Due to some bugs found in eltorito.sys, the driver could fail to load. If you
encounter such problems, then you may replace (hd32) with (0xFF) for the
virtual cdrom drive number and try again.


******************************************************************************
***                  The New Command CHECKRANGE                            ***
******************************************************************************

Checkrange checks whether or not the return value of a command is in the
specified range or ranges.

Usage:		checkrange  RANGE  COMMAND

Here are some examples for RANGE:

	3 is a range containing only the number 3
	3:3 is equivalent to 3
	3:8 is a range containing the numbers 3, 4, 5, 6, 7, 8
	3,4,5,6,7,8 is equivalent to 3:8
	3:5,6:8 is also equivalent to 3:8
	3,4:7,8 is also equivalent to 3:8

Note: You should not insert spaces into a range.

Here is an example showing where the checkrange can be used:

	checkrange 0x05,0x0F,0x85 parttype (hd0,1) || hide (hd0,1)

which means: if (hd0,1) is not an extended partition, then hide it.


******************************************************************************
***                       The New Command TPM                              ***
******************************************************************************

The "tpm --init" uses 512-byte data at 0000:7C00 as buffer to initialise TPM.

Before you boot VISTA's BOOTMGR, you might have to use the "tpm --init"
command on some machines. Normally you want to issue the "tpm --init" command
after a CHAINLOADER command.


******************************************************************************
***               Delimitors or comments between titles                    ***
******************************************************************************

It is possible to use titles as delimitors or comments. A title(or menu item)
is called unbootable if all of its menu commands are not boot-sensitive.

The following commands are boot-sensitive(and others are not boot-sensitive):

	boot
	bootp
	chainloader
	configfile
	embed
	commandline
	halt
	install
	kernel
	pxe
	quit
	reboot
	setup

An unbootable title will be skipped when the user presses the Up Arrow or Down
Arrow keys. Even the unbootable menu item can get accessed(and executed) by
using the Left Arrow and/or Right Arrow keys. Examples:

	title This is an UNBOOTABLE entry(so this line is also a comment)
		pause --wait=0 This title is a comment. Nothing to do.
		pause --wait=0 You can use non-boot-sensitive commands here
		pause --wait=0 of any kind and as many as you would like.
		help
		help root
		help chainloader
		help parttype
		clear
	title ------------------------------------------------------------
		pause --wait=0 This title is a delimitor. Nothing to do.
		pause --wait=0 You can use non-boot-sensitive commands here
		pause --wait=0 of any kind and as many as you would like.
		clear
		help
		help boot
	title ============================================================
		pause --wait=0 This title is a delimitor. Nothing to do.
		pause --wait=0 You can use non-boot-sensitive commands here
		pause --wait=0 of any kind and as many as you would like.
		help
		clear
		help pause
	title ************************************************************
		pause --wait=0 This title is a delimitor. Nothing to do.
		pause --wait=0 You can use non-boot-sensitive commands here
		pause --wait=0 of any kind and as many as you would like.
		help kernel
		help
		clear

Note: An unbootable menu item must contain at least one command. If there
are no commands for a title, the title will be simply discarded and disappear.


******************************************************************************
***                           Bifurcate drives                             ***
******************************************************************************

Some machines apply different actions to a drive between CHS and LBA mode.
When you read sectors using standard BIOS call int13/AH=02h, you might find
out the drive is a floppy. But when you read sectors using extended BIOS
call(EBIOS) int13/AH=42h, you could know the drive is a cdrom. Such a drive
is called bifurcate.

A bifurcate drive can have two drive numbers: one is the normal BIOS drive
number between 00 and FF in hexa, and this drive uses only CHS mode disk
access(standard BIOS int13/AH=02h); the other is the normal BIOS drive number
(Bitwise) OR'ed by 0x100(i.e., 256 in decimal), and this drive uses only
LBA mode disk access(EBIOS int13/AH=42h). For example, if the drive 0x00
(i.e., the first floppy) is bifurcate, then the drive (0x00) uses CHS mode
to access its sectors, and the drive (0x100) uses LBA (meaning EBIOS) mode
to access its sectors.

The geometry command can report the disk access mode for bifurcate drives as
BIF instead of the conventional CHS or LBA.

Known bifurcate drives. Virtual PC and some real machines are found to create
a bifurcate floppy drive when they boot from a floppy-emulation mode bootable
cdrom. The "geometry (fd0)" will show

	drive 0x00(BIF): C/H/S=...Sector Count/Size=.../512

and "geometry (0x100)" will show

	drive 0x100(BIF): C/H/S=...Sector Count/Size=.../2048

Actually (0x100) can access the whole cdrom, you may "ls (0x100)/" and find
your files on the cdrom(not the files inside the booted floppy image). Of
course "ls (fd0)/" will list the files inside the booted floppy image.

Note that only some (real or virtual) machines have this action, others
will not produce bifurcate drives.


******************************************************************************
***                       GRLDR as PXE boot file                           ***
******************************************************************************

GRLDR can be used as the PXE boot file on a remote/network server. The (pd)
device is used to access files on the server. When GRLDR is booted through
network, it will use its preset menu as the config file. However, you may use
a "pxe detect" command, which acts the same way as PXELINUX:

    * First, it will search for the config file using the hardware type (using
      its ARP type code) and address, all in hexadecimal with dash separators;
      for example, for an Ethernet (ARP type 1) with address 88:99:AA:BB:CC:DD
      it would search for the filename 01-88-99-AA-BB-CC-DD. 

    * Next, it will search for the config file using its own IP address in
      upper case hexadecimal, e.g. 192.0.2.91 -> C000025B. If that file is not
      found, it will remove one hex digit and try again. At last, it will try
      looking for a file named default (in lower case). As an example, if the
      boot file name is /mybootdir/grldr, the Ethernet MAC address is
      88:99:AA:BB:CC:DD and the IP address 192.0.2.91, it will try following
      files (in that order): 

       /mybootdir/menu.lst/01-88-99-AA-BB-CC-DD
       /mybootdir/menu.lst/C000025B
       /mybootdir/menu.lst/C000025
       /mybootdir/menu.lst/C00002
       /mybootdir/menu.lst/C0000
       /mybootdir/menu.lst/C000
       /mybootdir/menu.lst/C00
       /mybootdir/menu.lst/C0
       /mybootdir/menu.lst/C
       /mybootdir/menu.lst/default

You cannot directly map an image file on (pd). You must map it in memory using
the --mem option. For example,

	map --mem (pd)/images/floppy.img (fd0)
	map --hook
	chainloader (fd0)+1
	rootnoverify (fd0)
	boot

One more example,

	map --mem (pd)/images/cdimage.iso (0xff)
	map --hook
	chainloader (0xff)
	boot


******************************************************************************
***                       New program badgrub.exe                          ***
******************************************************************************

The new program badgrub.exe is intended to serve 'bad' machines(typically some
DELL models) that cannot run the normal grub.exe.


******************************************************************************
***                           Conditional find                             ***
******************************************************************************

The new find syntax allows to find a device conditionally.

	find [OPTIONS] [FILENAME] [CONDITION]

CONDITION is a normal grub command which returns TRUE or FALSE.

	Example 1:

		find

	This will list all partitions, all floppies and the (cd).

	Example 2:

		find +1

	This will list all devices with a known filesystem.

	Example 3:

		find checkrange 0xAF parttype

	This will list all partitions with ID=0xAF.

	Example 4:

		find /ntldr checkrange 0x07 parttype

	This will list all partitions with ID=0x07 and existing /ntldr.



******************************************************************************
***                    How to build grldr boot images                      ***
******************************************************************************

1. build 1.44M floppy image ext2grldr.img

	dd if=/dev/zero of=ext2grldr.img bs=512 count=2880
	mke2fs ext2grldr.img
	mkdir ext2tmp
	mount -o loop ext2grldr.img ext2tmp
	cp default ext2tmp
	cp menu.lst ext2tmp
	cp grldr ext2tmp
	umount ext2tmp
	bootlace.com --floppy --chs --sectors-per-track=18 --heads=2 --start-sector=0 --total-sectors=2880 ext2grldr.img

2. build 1.44M floppy image fat12grldr.img

	dd if=/dev/zero of=fat12grldr.img bs=512 count=2880
	mkdosfs fat12grldr.img
	mkdir fat12tmp
	mount -o loop fat12grldr.img fat12tmp
	cp default fat12tmp
	cp menu.lst fat12tmp
	cp grldr fat12tmp
	umount fat12tmp
	bootlace.com --floppy --chs fat12grldr.img

3. build iso9660 CDROM image grldr.iso

	mkdir iso_root
	cp grldr iso_root
	cp menu.lst iso_root
	mkisofs -R -b grldr -no-emul-boot -boot-load-size 4 -o grldr.iso iso_root


******************************************************************************
***           Use bootlace.com to install partition boot record            ***
******************************************************************************

Since bootlace.com has not implemented the --install-partition option, you
need to use the already implemented --floppy=PartitionNumber option instead.

Hear is a way you might want to follow:

Step 1. Get the boot sectors of the partition and save to a file MYPART.TMP.
	For NTFS, you need to get the beginning 16 sectors. For other type of
	filesystems, you only need to get one sector, but getting more sectors
	is also ok.

Step 2. Run this:

	bootlace.com --floppy=Y --sectors-per-track=S --heads=H --start-sector=B --total-sectors=C --vfat --ext2 --ntfs MYPART.TMP

	where we suppose MYPART.TMP is for (hdX,Y) and the partition number Y
	should be specified as in the --floppy=Y option.

	Note that for FAT12/16/32/NTFS partitions, you can omit these options:

		 --sectors-per-track, --heads, --start-sector, --total-sectors,
		 --vfat and --ext2.

	For NTFS partitions, you must specify --ntfs option.

	For ext2 partitions, you can omit --vfat, --ntfs and --ext2 options,
	but other options should be specified.

Step 3. Put MYPART.TMP back on to the boot sector(s) of your original partition
	(hdX,Y).


Note: Only a few file systems(FAT12/16/32/NTFS/ext2/ext3) are supported by now.

Note2: Under Linux you may directly write the partition. That is to say, Step
	1 and Step 3 are not needed. Simply use its device name instead of
	MYPART.TMP.

Note3: grubinst has the feature of installing grldr boot code onto a partiton
	boot area.

******************************************************************************
***                Use a single key to select menu item                    ***
******************************************************************************

Some machines have a simplified keyboard. The keyborad might have only the
number keys 0 .. 9 plus a few other keys. When the menu displayed, the user
can strike a key for 8 times. When the menu handler detects the continuous
single keypress, it will assume the user want to use this key to select a menu
item and boot. This single key will act as the RIGHT-ARROW key for the user to
select a menu item. And 5 seconds later after the user stops the keypress,
the selected menu item will automatically boot. Any normal keys can be used as
a single key for this purpose, except for a few functional keys like b, e,
Enter, etc. Once another key is pressed, the feature of Single-Key-Selection
will disappear immediately.


******************************************************************************
***             Parameter file for bootlace running under DOS              ***
******************************************************************************

You may move all or part of the command-line arguments into a file. The file
can have multi lines. Just like SPACEs and TABs, the CRs and LFs can also
delimit the commandline arguments in the parameter file.

Example:

		bootlace < my_parafile
		bootlace --read-only my_mbr < my_other_options

Note:	Pipes do not work. You have to use the input-redirection operator(<).


******************************************************************************
***                  Use bootlace to create a triple MBR                   ***
******************************************************************************

This is typically used for USB drives, though it also works with hard drives.

Steps to create triple MBR:

1. Do a fresh FDISK to create a FAT12/16/32 partition starting at sector 95
(in LBA, that is, the begginning sector(MBR) is sector 0).

2. Install grldr boot sector onto the boot sector of this partition. See
section "Use bootlace.com to install partition boot record" above.

3. Get 96 sectors of the drive starting at sector 0(MBR), and save to file
MYMBR96.TMP.

4. Run bootlace.com:

	bootlace.com MYMBR96.TMP

5. Put MYMBR96.TMP back onto the drive starting at MBR(sector 0).

Note: If the drive already has a triple MBR, then bootlace will cancel it
and restore the original partition layout.


******************************************************************************
***                    Use 'pxe detect' in preset-menu                     ***
******************************************************************************

Now the "pxe" command has a new subcommand "detect":

		pxe detect [BLOCK_SIZE] [MENU_FILE]

BLOCK_SIZE specifies the block size for PXE. If it is not specified or it is
0, then grub4dos will go through a probing process and get a proper value
for data transfer.

MENU_FILE specifies the config file on the PXE server. If omitted, a standard
config file in the menu.lst sub-dir will gain control. For a description on
the config files in the menu.lst sub-dir, please refer to the section
"GRLDR as PXE boot file" above.
If MENU_FILE starts in a "/", then the MENU_FILE on the PXE server will gain
control, else(if MENU_FILE does not start in a "/") no menu will be executed.

Normally you want to use a "pxe blksize ..." or a "pxe detect ..." command
before you access the (pd) device, since the default blocksize of 512 might
not work on your system.


******************************************************************************
***                    Use 'configfile' in preset-menu                     ***
******************************************************************************

Now the preset menu holds the highest priority. It will gain control prior to
the menu.lst on the boot device. If a 'configfile' command occurs in the menu
init command group, then control will go to the menu.lst on the boot device.



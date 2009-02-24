/*
 *  bootlacestart.S -- A utility for installing GRLDR boot sectors to MBR/OSBR
 *  Copyright (C) 2005  Tinybit(tinybit@163.net)
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

/*
 * This program is used to generate the GRLDR-INSTALL file.
 *
 * Use the following shell command to generate the GRLDR-INSTALL file:
 *
 * 	cp bootlacestart bootlace.com
 *
 */

/* Use the following command to compile and build:
 *
 *	gcc -o bootlacestart.exec -nostdlib -I. -I.. -I../stage1 -Wl,-N -Wl,-s bootlacestart.S
 *
 */

//#define ABS(x) (x-_start+0x08048000)
//#define ABS(x) (x)

#define __DOT_COM

	.text
	.globl	_start
        
_start:

	/* command-line arguments:
	 *	bootlace.com  [OPTIONS]  DEVICE_OR_FILE
	 */

	# ELF header begin

	.byte	0x7F, 0x45, 0x4C, 0x46	# ELF magic number
					// 7F 45 = jg dos_entry_point
					// 4C = decw %sp
					// 46 = incw %si

#if 0
	.byte	0x01			# 32-bit
	.byte	0x01			# little-endian
					// 01 01 = addw %ax, (%bx, %di)
#else
	.byte	0x01			# 32-bit
	.byte	0xC0			# corrupt-endian!
					# Sorry!
					# We have to use this for DOS code!
					// 01 C0 = addw %ax, %ax
#endif

	.byte	0x01			# version

#ifdef __DOT_COM

	.byte	0xC0			# pad char
					// 01 C0 = addw %ax, %ax

	//.byte	0xFA			# pad char
	//				// cli
	.byte	0x90			# pad char
					// nop

	.byte	0x44			# pad char
					// incw	%sp

	//.byte	0xFB			# pad char
	//				// sti
	.byte	0x90			# pad char
					// nop

	.byte	0x4E			# pad char
					// decw	%si

	.byte	0x90			# pad char
					// nop

	.byte	0x90			# pad char
					// nop

	.byte	0xEB, 0x24		# pad char
					// jmp	invalid_dos_exec

#endif

	. = _start + 0x10

	.word	2			# e_type = Executable
	.word	3			# e_machine = i386
	.long	1			# e_version
	.long	_start_linux		# e_entry
	.long	(_ph_offset - _start)	# e_phoff
	.long	(_sh_offset - _start)	# e_shoff(section header table)
	.long	0			# e_flags
	.word	0x34			# e_ehsize (ELF header size)
	.word	0x20			# e_phentsize(prog header entry size)
	.word	1			# e_phnum(prog header entry count)
	.word	0x28			# e_shentsize
	.word	5			# e_shnum
	.word	4			# e_shstrndx

	# ELF header end

	. = _start + 0x34		// aux dos entry point

#ifdef __DOT_COM

//invalid_dos_exec:

	/* this is real mode dos code */

	.code16

#define __DOS_16
#include "bootlace.inc"


bios_drive_number:
	.long	0xff

#if 0
msg_invalid_dos:

	.ascii	"\r\nError: Unsupported DOS. The DOS exec function call(int21/AX=4B00) did not\r\ntransfer flags of GREATER-THAN to this program. Report this problem to the\r\nmaintainers of GRUB FOR DOS.\r\n\r\n\0"
#endif

	.align	0x10
#endif

_ph_offset:

	.long	1				# p_type
	.long	(_start_linux - _start)		# p_offset
	.long	_start_linux			# p_vaddr
	.long	_start_linux			# p_paddr
	.long	(pre_stage2_start - _start_linux)	# p_filesz
	.long	(pre_stage2_start - _start_linux + (0xBE00 + 0x200))	# p_memszz //mbr_63_sectors
	.long	7				# p_flags
	.long	0x200				# p_align


	.align	0x200

_start_linux:

	/* this is protected mode linux code */

	.code32

#undef __DOS_16
#include "bootlace.inc"

option_restore_mbr:
	.ascii	"--restore-mbr\0"

option_no_backup_mbr:
	.ascii	"--no-backup-mbr\0"

option_force_backup_mbr:
	.ascii	"--force-backup-mbr\0"

option_mbr_enable_floppy:
	.ascii	"--mbr-enable-floppy\0"

option_mbr_disable_floppy:
	.ascii	"--mbr-disable-floppy\0"

option_mbr_enable_osbr:
	.ascii	"--mbr-enable-osbr\0"

option_mbr_disable_osbr:
	.ascii	"--mbr-disable-osbr\0"

option_mbr_no_bpb:
	.ascii	"--mbr-no-bpb\0"

option_duce:
	.ascii	"--duce\0"

option_chs_no_tune:
	.ascii	"--chs-no-tune\0"

option_boot_prevmbr_first:
	.ascii	"--boot-prevmbr-first\0"

option_boot_prevmbr_last:
	.ascii	"--boot-prevmbr-last\0"

option_preferred_drive:
	.ascii	"--preferred-drive=\0"

option_preferred_partition:
	.ascii	"--preferred-partition=\0"

option_serial_number:
	.ascii	"--serial-number=\0"

option_install_partition:
	.ascii	"--install-partition=\0"

option_sectors_per_track:
	.ascii	"--sectors-per-track=\0"

option_heads:
	.ascii	"--heads=\0"

option_start_sector:
	.ascii	"--start-sector=\0"

option_total_sectors:
	.ascii	"--total-sectors=\0"

option_floppy_partition:
	.ascii	"--floppy=\0"

option_time_out:
	.ascii	"--time-out=\0"

option_hot_key:
	.ascii	"--hot-key=\0"

option_read_only:
	.ascii	"--read-only\0"

option_floppy:
	.ascii	"--floppy\0"

option_lba:
	.ascii	"--lba\0"

option_chs:
	.ascii	"--chs\0"

option_fat12:
	.ascii	"--fat12\0"

option_fat16:
	.ascii	"--fat16\0"

option_fat32:
	.ascii	"--fat32\0"

option_ntfs:
	.ascii	"--ntfs\0"

option_ext2:
	.ascii	"--ext2\0"

option_vfat:
	.ascii	"--vfat\0"

msg_start:

	/* messages begins at here */

msg_ebios_read_failure:

	.ascii	"\r\nWarning: EBIOS read failure!\r\n\r\n\0"

msg_ebios_write_failure:

	.ascii	"\r\nWarning: EBIOS write failure! Now try standard CHS write, but not reliable.\r\n\r\n\0"

msg_no_ebios_support:

	.ascii	"\r\nWarning: EBIOS not present! It is not reliable running under DOS without EBIOS.\r\n\r\n\0"

msg_stdin_too_long:

	.ascii	"\r\nError: The standard input is too long.\r\n\r\n\0"

msg_too_many_parameters:

	.ascii	"\r\nError: Too many parameters in command line.\r\n\r\n\0"

msg_no_args:

	.ascii	"\r\nError: No command-line arguments specified.\r\n\r\n\0"

msg_too_many_files:

	.ascii	"\r\nError: More than one files specified.\r\n\r\n\0"

msg_no_file:

	.ascii	"\r\nError: No device or file specified.\r\n\r\n\0"

msg_option_restore_mbr:
	.ascii	"\r\nError: Specified --restore-mbr twice.\r\n\r\n\0"

msg_option_restore_mbr_with_other:
	.ascii	"\r\nError: Specified --restore-mbr with other options than --read-only.\r\n\r\n\0"

msg_invalid_prev_mbr:
	.ascii	"\r\nError: previous MBR is invalid, or it is the GRLDR MBR.\r\n\r\n\0"

msg_option_backup_mbr:
	.ascii	"\r\nError: Specified an option twice for backing up MBR.\r\n\r\n\0"

msg_option_backup_mbr_with_floppy:
	.ascii	"\r\nError: Specified --floppy with backing up MBR.\r\n\r\n\0"

msg_option_backup_mbr_with_partition:
	.ascii	"\r\nError: Specified --install-partition with backing up MBR.\r\n\r\n\0"

msg_option_mbr_floppy:
	.ascii	"\r\nError: Specified an option twice for searching floppy.\r\n\r\n\0"

msg_option_mbr_floppy_with_floppy:
	.ascii	"\r\nError: Specified --floppy with MBR searching floppy.\r\n\r\n\0"

msg_option_mbr_floppy_with_partition:
	.ascii	"\r\nError: Specified --install-partition with MBR searching floppy.\r\n\r\n\0"

msg_option_mbr_osbr:
	.ascii	"\r\nError: Specified an option twice for booting osbr.\r\n\r\n\0"

msg_option_mbr_osbr_with_floppy:
	.ascii	"\r\nError: Specified --floppy with booting osbr.\r\n\r\n\0"

msg_option_mbr_osbr_with_partition:
	.ascii	"\r\nError: Specified --install-partition with booting osbr.\r\n\r\n\0"

msg_option_mbr_bpb:
	.ascii	"\r\nError: Specified an option twice for mbr-bpb.\r\n\r\n\0"

msg_option_mbr_bpb_with_floppy:
	.ascii	"\r\nError: Specified --floppy with  mbr-bpb.\r\n\r\n\0"

msg_option_mbr_bpb_with_partition:
	.ascii	"\r\nError: Specified --install-partition with mbr-bpb.\r\n\r\n\0"

msg_option_duce:
	.ascii	"\r\nError: Specified --duce twice.\r\n\r\n\0"

msg_option_duce_with_floppy:
	.ascii	"\r\nError: Specified --floppy with --duce.\r\n\r\n\0"

msg_option_duce_with_partition:
	.ascii	"\r\nError: Specified --install-partition with --duce.\r\n\r\n\0"

msg_option_chs_no_tune:
	.ascii	"\r\nError: Specified --chs-no-tune twice.\r\n\r\n\0"

msg_option_chs_no_tune_with_floppy:
	.ascii	"\r\nError: Specified --floppy with --chs-no-tune.\r\n\r\n\0"

msg_option_chs_no_tune_with_partition:
	.ascii	"\r\nError: Specified --install-partition with --chs-no-tune.\r\n\r\n\0"

msg_option_boot_prevmbr:
	.ascii	"\r\nError: Specified an option twice for booting prevmbr.\r\n\r\n\0"

msg_option_boot_prevmbr_with_floppy:
	.ascii	"\r\nError: Specified --floppy with booting prevmbr.\r\n\r\n\0"

msg_option_boot_prevmbr_with_partition:
	.ascii	"\r\nError: Specified --install-partition with booting prevmbr.\r\n\r\n\0"

msg_option_preferred_drive:
	.ascii	"\r\nError: Specified an option twice for preferred drive.\r\n\r\n\0"

msg_option_preferred_drive_with_floppy:
	.ascii	"\r\nError: Specified --floppy with preferred drive.\r\n\r\n\0"

msg_option_preferred_drive_with_partition:
	.ascii	"\r\nError: Specified --install-partition with preferred drive.\r\n\r\n\0"

msg_option_preferred_partition:
	.ascii	"\r\nError: Specified an option twice for preferred partition.\r\n\r\n\0"

msg_option_preferred_partition_with_floppy:
	.ascii	"\r\nError: Specified --floppy with preferred partition.\r\n\r\n\0"

msg_option_preferred_partition_with_partition:
	.ascii	"\r\nError: Specified --install-partition with preferred partition.\r\n\r\n\0"

msg_option_serial_number:
	.ascii	"\r\nError: Specified an option twice for disk serial number.\r\n\r\n\0"

msg_option_serial_number_with_floppy:
	.ascii	"\r\nError: Specified --floppy with disk serial number.\r\n\r\n\0"

msg_option_serial_number_with_partition:
	.ascii	"\r\nError: Specified --install-partition with disk serial number.\r\n\r\n\0"

msg_option_install_partition:
	.ascii	"\r\nError: Specified an option twice for install partition.\r\n\r\n\0"

msg_option_install_partition_with_floppy:
	.ascii	"\r\nError: Specified --floppy with install partition.\r\n\r\n\0"

msg_option_install_partition_not_implemented:
	.ascii	"\r\nSorry! --install-partition not yet implemented with this release.\r\n\r\n\0"

msg_option_time_out:
	.ascii	"\r\nError: Specified an option twice for time out.\r\n\r\n\0"

msg_option_time_out_with_floppy:
	.ascii	"\r\nError: Specified --floppy with time out.\r\n\r\n\0"

msg_option_time_out_with_partition:
	.ascii	"\r\nError: Specified --install-partition with time out.\r\n\r\n\0"

//msg_option_time_out_without_prevmbr:
//	.ascii	"\r\nError: Specified --time-out without specifying --boot-prevmbr-first.\r\n\r\n\0"

msg_option_hot_key:
	.ascii	"\r\nError: Specified an option twice for hot key.\r\n\r\n\0"

msg_option_hot_key_with_floppy:
	.ascii	"\r\nError: Specified --floppy with hot key.\r\n\r\n\0"

msg_option_hot_key_with_partition:
	.ascii	"\r\nError: Specified --install-partition with hot key.\r\n\r\n\0"

//msg_option_hot_key_without_prevmbr:
//	.ascii	"\r\nError: Specified --hot-key without specifying --boot-prevmbr-first.\r\n\r\n\0"

msg_option_sectors_per_track:
	.ascii	"\r\nError: Specified an option twice for sectors per track.\r\n\r\n\0"

msg_option_sectors_per_track_with_partition:
	.ascii	"\r\nError: Specified --install-partition with sectors per track.\r\n\r\n\0"

msg_option_sectors_per_track_for_mbr:
	.ascii	"\r\nError: Specified --sectors-per-track for a hard drive.\r\n\r\n\0"

msg_option_heads:
	.ascii	"\r\nError: Specified an option twice for heads.\r\n\r\n\0"

msg_option_heads_with_partition:
	.ascii	"\r\nError: Specified --install-partition with --heads.\r\n\r\n\0"

msg_option_heads_for_mbr:
	.ascii	"\r\nError: Specified --heads for a hard drive.\r\n\r\n\0"

msg_option_start_sector:
	.ascii	"\r\nError: Specified an option twice for start sector.\r\n\r\n\0"

msg_option_start_sector_with_partition:
	.ascii	"\r\nError: Specified --install-partition with --start-sector.\r\n\r\n\0"

msg_option_start_sector_for_mbr:
	.ascii	"\r\nError: Specified --start-sector for a hard drive.\r\n\r\n\0"

msg_option_total_sectors:
	.ascii	"\r\nError: Specified an option twice for total sectors.\r\n\r\n\0"

msg_option_total_sectors_with_partition:
	.ascii	"\r\nError: Specified --install-partition with --total-sectors.\r\n\r\n\0"

msg_option_total_sectors_for_mbr:
	.ascii	"\r\nError: Specified --total-sectors for a hard drive.\r\n\r\n\0"

msg_option_read_only:
	.ascii	"\r\nError: Specified an option twice for read only.\r\n\r\n\0"

msg_option_floppy:
	.ascii	"\r\nError: Specified an option twice for --floppy.\r\n\r\n\0"

msg_option_lba:
	.ascii	"\r\nError: Specified an option twice for lba-chs mode.\r\n\r\n\0"

msg_option_lba_for_mbr:
	.ascii	"\r\nError: Specified --lba for a hard drive.\r\n\r\n\0"

msg_option_fstypes_for_mbr:
	.ascii	"\r\nError: Specified file system types for a hard-drive mbr device.\r\n\r\n\0"

msg_partition_without_drive:
	.ascii	"\r\nError: Preferred partition without preferred drive.\r\n\r\n\0"

msg_partition_start:
	.ascii	"\r\nError: For a single partition you must specify --start-sector to non-zero.\r\n\r\n\0"

msg_floppy_start:
	.ascii	"\r\nError: For a real floppy you must specify --start-sector to 0.\r\n\r\n\0"

msg_invalid_number:
	.ascii	"\r\nError: Invalid number format or invalid value for the specified option.\r\n\r\n\0"

msg_invalid_option:
	.ascii	"\r\nError: Invalid option.\r\n\r\n\0"

msg_open_file_rw:
	.ascii	"\r\nError: Cannot open file for read/write access.\r\n\r\n\0"

msg_open_file_ro:
	.ascii	"\r\nError: Cannot open file for read-only access.\r\n\r\n\0"

msg_read_file:
	.ascii	"\r\nError: Read file failed.\r\n\r\n\0"

msg_lseek_file:
	.ascii	"\r\nError: Rewind file(lseek) failed.\r\n\r\n\0"

msg_write_file:
	.ascii	"\r\nError: Write file failed.\r\n\r\n\0"

msg_close_file:
	.ascii	"\r\nFatal! Close file failed. Please backup your disk in case it becomes unusable.\r\n\r\n\0"

msg_boot_signature_mbr:
	.ascii	"\r\nError: No boot signature(55 AA). Must specify --floppy explicitly for floppy.\r\n\r\n\0"

msg_invalid_partition_table:
	.ascii	"\r\nError: Invalid partition table. Must specify --floppy explicitly for floppy.\r\n\r\n\0"

msg_floppy_partition_table:
	.ascii	"\r\nError: Specified --floppy for DEVICE_OR_FILE that has a valid partition table.\r\n\r\n\0"

msg_sectors_per_track:
	.ascii	"\r\nError: Too few sectors to hold GRLDR.MBR.\r\n\r\n\0"

msg_geometry_S:
	.ascii	"\r\nDisk geometry calculated according to the partition table:\r\n\r\n"
	.ascii	"        Sectors per track = \0"
msg_geometry_H:
	.ascii	", Number of heads = \0"
msg_success:
	.ascii	"\r\n\r\nSuccess.\r\n\r\n\0"
msg_success_create_triple_mbr:
	.ascii	"\r\n\r\nSuccess. Triple MBR installed.\r\n\r\n\0"
msg_success_cancel_triple_mbr:
	.ascii	"\r\n\r\nTriple MBR cancelled. Original partition layout restored.\r\n\r\n\0"

msg_fstype_fat32_deny:
	.ascii	"\r\n\r\nError: Filesystem type is FAT32 but --fat32 was not specified.\r\n\r\n\0"

msg_fstype_fat32_allow:
	.ascii	"\r\n\r\nFilesystem type is FAT32.\r\n\r\n\0"

msg_fstype_ntfs_deny:
	.ascii	"\r\n\r\nError: Filesystem type is NTFS but --ntfs was not specified.\r\n\r\n\0"

msg_fstype_ntfs_allow:
	.ascii	"\r\n\r\nFilesystem type is NTFS.\r\n\r\n\0"

msg_fstype_fat12_deny:
	.ascii	"\r\n\r\nError: Filesystem type is FAT12 but --fat12 was not specified.\r\n\r\n\0"

msg_fstype_fat12_allow:
	.ascii	"\r\n\r\nFilesystem type is FAT12.\r\n\r\n\0"

msg_fstype_fat16_deny:
	.ascii	"\r\n\r\nError: Filesystem type is FAT16 but --fat16 was not specified.\r\n\r\n\0"

msg_fstype_fat16_allow:
	.ascii	"\r\n\r\nFilesystem type is FAT16.\r\n\r\n\0"

msg_fstype_ext2_deny:
	.ascii	"\r\n\r\nError: Filesystem type is EXT2 but --ext2 was not specified.\r\n\r\n\0"

msg_fstype_ext2_allow:
	.ascii	"\r\n\r\nFilesystem type is EXT2.\r\n\r\n\0"

msg_unsupported_fstype:
	.ascii	"\r\n\r\nError: Unsupported filesystem type.\r\n\r\n\0"

msg_fstype_mbr_deny:
	.ascii	"\r\n\r\nError: Cannot overwrite the MBR of a harddrive(or HD image) with --floppy.\r\n\r\n\0"

//msg_no_ntfs_boot_record:
//	.ascii	"\r\n\r\nError: Filesystem type is NTFS, but no ntfs boot record was found.\r\n\r\n\0"

msg_no_enough_memory:
	.ascii	"\r\n\r\nError: No enough memory.\r\n\r\n\0"

msg_usage:

	.ascii	"BOOTLACE writes GRLDR BOOT RECORD to MBR or to the boot area of a file system.\r\n"
	.ascii	"Usage:  bootlace.com  [OPTIONS]  DEVICE_OR_FILE\r\n"
	.ascii	"Options: --read-only, --floppy[=N], --boot-prevmbr-first, --boot-prevmbr-last,\r\n"
	.ascii	"--no-backup-mbr, --force-backup-mbr, --mbr-enable-floppy, --mbr-disable-floppy,\r\n"
	.ascii	"--mbr-enable-osbr, --mbr-disable-osbr, --duce, --time-out=T, --hot-key=K, \r\n"
	.ascii	"--preferred-drive=D, --preferred-partition=P, --sectors-per-track=S, --heads=H,\r\n"
	.ascii	"--start-sector=B, --total-sectors=C, --install-partition=I, --lba, --chs,\r\n"
	.ascii	"--fat12, --fat16, --fat32, --vfat, --ntfs, --ext2, --serial-number=SN,\r\n"
	.ascii	"--restore-mbr, --mbr-no-bpb, --chs-no-tune\r\n"
	.ascii	"DEVICE_OR_FILE: Filename of the device or image. For DOS, a BIOS drive number\r\n"
	.ascii	"(in hex 0xHH or decimal DDD format)can be used to access the drive.\r\n\0"

msg_end:

	.align	4

Cmax:	.long	0
Hmax:	.long	0
Smax:	.long	0
i:	.long	0
j:	.long	0
X:	.long	0
Y:	.long	0
C:			# long, but high word is always 0
	.word	0, 0
	.word	0, 0
	.word	0, 0
	.word	0, 0
	.word	0, 0
	.word	0, 0
	.word	0, 0
	.word	0, 0
	.word	0, 0
H:
	.long	0
	.long	0
	.long	0
	.long	0
	.long	0
	.long	0
	.long	0
	.long	0
H8:	.long	0
L:
	.long	0, 0
	.long	0, 0
	.long	0, 0
	.long	0, 0
	.long	0, 0
	.long	0, 0
	.long	0, 0
	.long	0, 0
L8:	.long	0, 0
probed_sectors_per_track:
	.long	0
probed_heads:
	.long	0
mbr_free_sectors:
	.long	0

number_digits:
	.ascii	"          \0"	/* 10 spaces */
delimit_space:
	.ascii	"    \0"	/* 4 spaces */
delimit_newline:
	.ascii	"\n\0"

	.align	4

restore_mbr:
	.long	0
backup_mbr:

	/*	0	no backup, Will not touch PREV_MBR
	 *	1	autobackup
	 *	2	forcebackup. Will overwrite the old PREV_MBR
	 */

	.long	1	/* default is autobackup */

mbr_floppy:

	/*	0	enable floppy
	 *	1	disable floppy
	 *	2	enable floppy
	 */

	.long	0	/* default is enable floppy */

mbr_osbr:

	/*	0	enable osbr
	 *	1	disable osbr
	 *	2	enable osbr
	 */

	.long	0	/* default is enable osbr */

mbr_bpb:

	/*	0	enable bpb
	 *	1	disable bpb
	 *	2	enable bpb
	 */

	.long	0	/* default is enable bpb */

duce:
	/*	0	enable unconditional command-line entrance
	 *	1	disable unconditional command-line entrance
	 *	2	enable unconditional command-line entrance
	 */

	.long	0	/* default is enable unconditional command-line entrance */

chs_no_tune:
	/*	0	enable geometry tune
	 *	1	disable geometry tune
	 *	2	enable geometry tune
	 */

	.long	0	/* default is enable geometry tune */

boot_prevmbr:

	/*	0	boot prevmbr last
	 *	1	boot prevmbr first
	 *	2	boot prevmbr last
	 */

	.long	0	/* default is boot prevmbr last */

preferred_drive:

	.long	0xff	/* default is No Drive */

preferred_partition:

	.long	0xff	/* default is Whole drive */

serial_number:

	.long	0

install_partition:

	.long	0xffffffff	/* default is partition 0xff */

sectors_per_track:

	.long	0xffffff3f	/* default is 63 */

heads:

	.long	0xffff00ff	/* default is 255 */

start_sector:

	.long	0xffffffff	/* default is invalid */

total_sectors:

	.long	0	/* default is invalid */

time_out:

	.long	0xffffff05	/* low byte default is 5 seconds */

hot_key:

	.long	0xffff3920	/* low word default is space bar */

read_only:

	/*	0	read only
	 *	2	read/write
	 */

	.long	2	/* default is read/write */

floppy:

	/* 0xffffffff for hard drive image(with leading MBR)
	 * 0x000000ff for floppy image
	 * value < 0xff for partition image
	 */

	.long	0xffffffff	/* default is for hard drive MBR */

lba:

	/* 1 for lba, 0 for chs, -1 for `not specified'. */

	.long	0xffffffff	/* default is `not specified' */

fstypes:

	/* bit 0: fat12 */
	/* bit 1: fat16 */
	/* bit 2: fat32 */
	/* bit 3: ntfs */
	/* bit 4: ext2 */

	.long	0xfffffff7	/* default is all types except ntfs */

sectors_to_write:

	/* default is number of sectors in GRLDR.MBR */

	.long	((pre_stage2_start - _start1) / 512)

restore_partition_layout:
	.long	0

ebios_support:
	.long	0

current_partition:
	.long	0

	.align	0x200

#define GRLDR_INSTALL
#include "grldrstart.S"

	.code32

	//.bss

	.align	0x200

mbr_63_sectors:

	//. = . + ((63+32+1)*512)

	.align	0x200

_string_table:

	.ascii	"\0"

	.ascii	".shstrtab\0"

	.ascii	".text\0"

	.ascii	".data\0"

	.ascii	".bss\0"

	.align	4

_sh_offset:

	# SHT_UNDEF section

	.long	0			# sh_name = No name
	.long	0			# sh_type = Inactive
	.long	0			# sh_flags = No flags
	.long	0			# sh_addr = No address
	.long	0			# sh_offset = No file offset
	.long	0			# sh_size = No size
	.long	0			# sh_link = No link information
	.long	0			# sh_info = No auxiliary information
	.long	0			# sh_addralign = No alignment
	.long	0			# sh_entsize = No entries

	# .text

	.long	0x0b			# sh_name
	.long	1			# sh_type = SHT_PROGBITS
	.long	7			# sh_flags = WRITE,ALLOC, EXEC

	.long	(_start_linux - _start + 0x08048000)
					# sh_addr(in process space)

	.long	(_start_linux - _start)
					# sh_offset(from beginning of file)

	.long	(pre_stage2_start - _start_linux)
					# sh_size

	.long	0			# sh_link
	.long	0			# sh_info
	.long	0x200			# sh_addralign
	.long	0			# sh_entsize

	# .data

	.long	0x11			# sh_name
	.long	1			# sh_type = SHT_PROGBITS
	.long	3			# sh_flags = WRITE, ALLOC

	.long	(pre_stage2_start - _start + 0x08048000)
					# sh_addr(in process space)

	.long	(pre_stage2_start - _start)
					# sh_offset(from beginning of file)

	.long	0			# sh_size (no data present)
	.long	0			# sh_link
	.long	0			# sh_info
	.long	4			# sh_addralign
	.long	0			# sh_entsize

	# .bss

	.long	0x17			# sh_name
	.long	8			# sh_type = SHT_NOBITS
	.long	3			# sh_flags = WRITE, ALLOC

	.long	(pre_stage2_start - _start + 0x08048000)
					# sh_addr(in process space)

	.long	(pre_stage2_start - _start)
					# sh_offset(from beginning of file)

	.long	(0xbe00 + 0x200)	# sh_size	//mbr_63_sectors
	.long	0			# sh_link
	.long	0			# sh_info
	.long	0x200			# sh_addralign
	.long	0			# sh_entsize

	# .shstrtab

	.long	1			# sh_name
	.long	3			# sh_type = SHT_STRTAB
	.long	0			# sh_flags = no write,no alloc,no exec
	.long	0			# sh_addr = not present in memory

	.long	(_string_table - _start)
					# sh_offset (where strtab begins at)

	.long	(_sh_offset - _string_table)
					# sh_size (size of the string table)

	.long	0			# sh_link
	.long	0			# sh_info
	.long	1			# sh_addralign
	.long	0			# sh_entsize












//-------------------------------------------------------------------

#if 0	/* begin backup sh.S for MandrakeISOinstall-10.0 */

/* Use the following command to compile and build:
 *
 *	gcc -s -nostdlib -o sh sh.S
 *
 */

	.globl _start
	.text

_start:

	/* fork() */
	xorl    %eax, %eax
	incl	%eax
	incl	%eax
	int     $0x80
	testl	%eax, %eax
	jz	1f
	/* exit(0) */
	xorl    %ebx, %ebx
	xorl    %eax, %eax
	incl    %eax
	int     $0x80

1:
#if 0
	/* setpgid(0,0) */
	xorl    %ebx, %ebx
	xorl    %ecx, %ecx
	xorl    %eax, %eax
	movb	$57, %al
	int     $0x80
#else
	/* setsid() */
	xorl    %eax, %eax
	movb	$66, %al
	int     $0x80
#endif
1:
	/* sleep(1) */
	xorl    %eax, %eax
	movb	$162, %al
	movl	$(time_sleep), %ebx
	xorl    %ecx, %ecx
	int     $0x80
	
	/* access("/bin/sh", F_OK) */
	xorl    %eax, %eax
	movb	$33, %al
	movl	$(shell_path), %ebx
	xorl    %ecx, %ecx
	int     $0x80
	orl	%eax, %eax
	jnz	1b	/* loop when not exist */

	/* execve("/bin/sh", argv, NULL) */
	xorl    %eax, %eax
	movb	$11, %al
	movl	$(shell_path), %ebx
	movl	$(argv), %ecx
	movl	$(envp), %edx
	int     $0x80
	
	/* exit(1) */
	xorl    %ebx, %ebx
	incl	%ebx
	xorl    %eax, %eax
	incl    %eax
	int     $0x80

time_sleep:
	.long	1
	.long	0

shell_path:
	.string	"/bin/sh"
arg0:
	.string	"mix_ISOs"
arg1:
	.string	"/tmp/mix_ISOs"
argv:
	.long	arg0
	.long	arg1
envp:
	.long	0

#endif	/* end backup sh.S for MandrakeISOinstall-10.0 */

	.align	1


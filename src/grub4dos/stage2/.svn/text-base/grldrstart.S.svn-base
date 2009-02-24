/*
 *  grldrstart.S -- Startup code for GRLDR
 *  Copyright (C) 2004-2007  Tinybit(tinybit@tom.com)
 *  Copyright (C) 2007  Bean(bean@windrv.net)
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
 * This program is used to generate the GRLDR file.
 *
 * Use the following shell command to generate the GRLDR file:
 *
 * 	cat grldrstart pre_stage2 > grldr
 *
 */

#define ASM_FILE
#include <shared.h>
#define ASM_FILE
	
#ifndef STAGE1_5
#include <stage2_size.h>
#else
#error cannot compile with STAGE1_5
#endif

#ifdef GRLDR_MBR
	.file	"mbrstart.S"
#elif defined(GRLDR_INSTALL)
	.file	"bootlacestart.S"
#else
	.file	"grldrstart.S"
#endif

#ifdef GRLDR_INSTALL
	//.data
#else
	.text

	.globl	start, _start

start:
_start:
#endif

_start1:

	/* Tell GAS to generate 16-bit real mode instructions */

	.code16

	. = _start1 + 0x00

	/* 1 byte at offset 0x00 will be overwritten for storing the EBIOS
	 * indicator later. This is safe because the jmp instruction only
	 * get executed once. The write happens after the jmp instruction
	 * have got executed.
	 *
	 * The value written would be 0x42 for EBIOS present(LBA) and 0x02
	 * for non-present(CHS).
	 *
	 */

	/* No cli, we use stack! BIOS or caller usually sets SS:SP=0000:0400 */

	jmp	1f	/* FAT32/NTFS routine comes to offset 0 */

	. = _start1 + 0x02

	.byte	0x80	/* bit0=1: disable GRLDR search on floppy */
			/* bit1=1: disable the boot of the previous MBR with
			 *	   invalid partition table */
			/* bit2=1: disable the feature of unconditional
			 *	   entrance to the command-line */
			/* bit3=1: disable geometry tune */
			/* bit7=1: disable the boot of the previous MBR prior
				   to the search for GRLDR */

	/* GRLDR.MBR uses offset 0x03 to indicate a timer counter. */

	/* 0xff indicates waiting forever,
	 * other value specifies the time in seconds to wait */

	. = _start1 + 0x03

#ifdef GRLDR_MBR
	.byte	0	// use 0 instead of 5 for grldr.mbr to work as usual.
#elif defined(GRLDR_INSTALL)
	.byte	5	// for bootlace.com
#else
	.byte	5	// for grldr
#endif

	/* a key press to wait. if AX returned from int16 equals this word,
	 * the desired action will occur. */

	. = _start1 + 0x04

	.word	0x3920		/* the space bar */

	. = _start1 + 0x06

	.byte	0xff	/* preferred boot drive number, 0xff for no-drive(i.e., drive not defined) */
	.byte	0xff	/* preferred partition number, 0xff for whole drive(a floppy that has no partition table) */

	. = _start1 + 8

	/* 2 bytes at offset 0x08 will be overwritten for storing the geometry
	 * reported by INT 13/AH=8.
	 *
	 * lo byte = Sectors Per Track
	 * hi byte = Max Head Number(=number of heads minus 1)
	 *
	 * If INT 13/AH=8 returns error, then the word here will be 0xFFFF. 
	 *
	 */

#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))

	/* filled in by mkisofs using the -boot-info-table option */

#;bi_pvd:	.long 0xDEADBEEF	/* LBA of primary volume descript */
#;bi_file:	.long 0xDEADBEEF	/* LBA of boot file */
#;bi_length:	.long 0xDEADBEEF	/* Length of boot file */
#;bi_csum:	.long 0xDEADBEEF	/* Checksum of boot file */
#;bi_reserved:	.space (10*4)		/* Reserved */

	. = _start1 + 0x40

#else

	/* filled in with BPB in case the drive(typically USB) is treated as floppy by buggy BIOSes */

	. = _start1 + 0x60

#endif	/* ! defined(GRLDR_MBR) && (! defined(GRLDR_INSTALL)) */

1:
	call	1f

#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))

	. = _start1 + 0x43

#else

	. = _start1 + 0x63

#endif	/* ! defined(GRLDR_MBR) && (! defined(GRLDR_INSTALL)) */

1:
	popw	%bx			/* Instruction Pointer of 1b */

#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))

	subw	$(1b - _start1), %bx	/* CS:BX=_start1 */

#else

	subw	$(1b - _start1), %bx	/* CS:BX=_start1 */

#endif	/* ! defined(GRLDR_MBR) && (! defined(GRLDR_INSTALL)) */

	shrw	$4, %bx
	movw	%cs, %ax
	addw	%ax, %bx		/* BX:0000=_start1 */

#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))

	/* we are booted from BOOT.INI, or whole GRLDR image already loaded */

	/* Let CS:0000=_start1 */
	pushw	%bx			/* BX:0000=_start1 */

	#;pushw	$(1f - _start1)
	.byte	0x6A, (1f - _start1)

	lret
	. = . - (. - _start1) / 0x80
1:
	addw	$((grldr_signature - _start1 + 4 + STAGE2_SIZE - 4) >> 4), %bx
	movw	%bx, %ds

	cmpl	$0xCE1A02B0, ((STAGE2_SIZE - 4) & 0x0F)
	pushw	%cs
	popw	%ds			/* DS:0000=_start1 */
	je	grldr_real_start	/* whole image loaded. boot it! */

	/* bad! we might be loaded by a buggy BIOS with a no-emulation-mode
	 * bootable CD. The buggy BIOS might load only 1 CD-ROM sector(2048
	 * bytes) of our grldr image. So we need this check.
	 */

	/* Our cdrom_check code begins at 0x1BE and overlaps the partition
	 * table. Just in case someone replace it with a partition table and
	 * use this sector as an MBR, we do this additional test for safety.
	 */

	/* We should avoid using opcode 0x00 and 0x80 at cdrom_check. */

	/* Note that if cdrom_check code is present, then we are booting from
	 * no-emulation mode cdrom.
	 */

	testb	$0x7F, cdrom_check - _start1	/* is it 0x00 or 0x80? */
	jz	1f			/* yes, cdrom_check not found */
	call	cdrom_check		/* no, cdrom_check is present */
1:
//	/* DS:0000=_start1 */
//
//	/* Let CS:0000=_start1 */
//	pushw	%ds
//
//	#;pushw	$(1f - _start1)
//	.byte	0x6A, (1f - _start1)
//
//	lret
//	. = . - (. - _start1) / 0x80
//1:
#else
	/* BX:0000=_start1 */

	movw	%bx, %ds

	/* Let CS:0000=_start1 */
	pushw	%bx

	#;pushw	$(1f - _start1)
	.byte	0x6A, (1f - _start1)

	lret
	. = . - (. - _start1) / 0x80
1:
#endif

	/* CS:0000=DS:0000=_start1 */

	/* we are loaded by BIOS or another boot loader */

#define GRLDR_CS 0x2000		/* grldr code segment */
				/* hope this segment never be used by all */
				/*	subsequent partition boot records */
#if 0
	/* for single sector boot record */
#define	MONITOR	0x7e10
#else
	/* for 4-sector NTFS boot record */
#define	MONITOR	0x8410
#endif

//	cli
	pushw	$GRLDR_CS
	popw	%ss
	movw	$0x9000, %sp	/* SS:SP=0x9d000, keep away from EBDA data */
//	sti
	
	/* Extended BIOS Data Area should not take up space below 0x9d000 */
	
	/* 
	 * 0x07c00-0x07dff	This sector. Another boot loader load us here
	 * 0x0d000-0x14dff	partition/floppy boot track(bootsector,etc)
	 * 0x94000-0x9bdff	master boot track(MBR,etc,usually 63 sectors)
	 * 0x9be00-0x9c3ff	3 sectors for temp extended partition entries
	 * 0x9c400-0x9cfff	6 sectors for stack
	 */

#define FS_BOOT	0xd00		/* segment of partition boot track */

	xorw	%cx, %cx
	pushw	%cx		/* CX=0 */
	movw	$0x0080, %dx
//	pushw	%dx
	movb	$8, %ah		/* read drive parameters changes DX,ES,DI,BX */
	call	int13
//	stc
//	int	$0x13
//	popw	%dx
	popw	%ax		/* AX=0 */

	pushw	%ss		/* SS=0x9400 */
	popw	%es		/* ES=0x9400 */

	jc	1f

	andb	$63, %cl	/* AL=sectors per track, CF cleared */

	stc
	jz	1f

	xchgw	%ax, %cx	/* this moves CL to AL, and CX=0 */
	movb	$0x02, %ah
	movw	%ax, %bp	/* save AX to BP: read 1 track */
	xorw	%bx, %bx	/* ES already has a known value of 0x9400 */
	incw	%cx
//	pushw	%dx
	call	int13
//	stc
//	int	$0x13		/* read master boot track to ES:0000 */
//	popw	%dx
	jc	1f
	negb	%ah		/* set CF=1 if non-zero */
1:
	pushw	%cs		/* DS=0 */
	popw	%ds		/* DS=CS */
	pushfw			/* CF=1 on error */
	
	/* CS=DS=old segment. ES=SS=new segment. */

	/* Move the code and error messages from DS:0000 to 9400:0000, do not
	 * touch the partition table
	 */
	xorw	%si, %si
	xorw	%di, %di
	movw	$223, %cx	/* 223 words = 446 bytes = 0x1be bytes */
	cld
	repz movsw		/* SI=DI=0x1be, CX=0 */

	/********************************************************************/
	/*  At this moment we are still not sure whether the helper is ok.  */
	/********************************************************************/

disk_serial_number_structure:

#if (defined(GRLDR_MBR)) || (defined(GRLDR_INSTALL))

	/********************************************************************/
	/* This piece of code is structured! It contains address 0x1FFC and */
	/* a disk serial number that can be created by grub4dos installers. */
	/********************************************************************/

	movw	$0x1FFC, %bx		/* .byte 0xBB, 0xFC, 0x1F */

	/* if the boot loader has loaded more than one sector, we use them */
	movl	$0x93cb4d05, %eax	/* date-time for disk serial number */

		/* "MOV EAX"(0x66, 0xB8) followed by the changeable S.N. */
#else
	movw	$(grldr_signature - _start1), %bx	/* BX=0x1FFC */

	/* if the boot loader has loaded more than one sector, we use them */
	movl	$0xAA555247, %eax	/* "GR" 0x55 0xAA */
#endif

disk_serial_number_structure_end:

//#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))
	cmpl	%eax, (%bx)		/* DS=old segment of 07C0:0000 */
	jne	1f

	/* The MOVE_HELPER code is in the old segment of 07C0:0000 */

	call	move_helper	/* SI=0x1be, CX=0 */
1:
//#endif

	/* Jump to new segment! */
#if 1
	ljmp	$GRLDR_CS, $(1f - _start1)
#else
	pushw	%ss		/* 0x9400 */

	//pushw	$(1f - _start1)
	.byte	0x6A, (1f - _start1)

	lret
	. = . - (. - _start1) / 0x80
#endif
1:

	/* We are at the new segment. CS=ES=SS=new segment. */

	/* But DS is still old segment. */

	pushw	%ss
	popw	%ds

	/* CS=DS=ES=SS=new segment. */

	//movw	$0x01be, %si

	/* check the existence of helper */
	cmpl	%eax, (%bx)

#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))

	jne	Error_or_prev_MBR	/* Missing helper */

#else

	je	1f

	/* try to load helper from floppy */

	pushal

	movw	0x18, %cx	/* BPB sectors per track at offset 0x18 */

	cmpw	$0x3F, %cx
	ja	3f

	/* CH=0 */

	movb	$(((pre_stage2_start - _start1) >> 9) - 1), %al
	cmpb	%al, %cl
	jbe	3f

	//decw	%ax		/* skip the first sector already loaded */
	
	movw	$3, %di		/* retry 3 times on read failure */
2:
	movb	$2, %ah		/* BIOS disk read */
	cwd			/* DX=0 for floppy head 0 */
	movw	$0x200, %bx	/* ES:BX immediately follow this sector */
	movb	$2, %cl		/* CH=0,skip the first sector already loaded */

	call	read_disk_with_reset_and_dec_di
	jnc	3f

	jnz	2b
3:
	popal
	cmpl	%eax, (%bx)		/* helper loaded? */

	jne	Error_or_prev_MBR	/* Missing helper */

	/* Helper is loaded from floppy, so we set floppy as preferred. */
	//movw	$0xff00, 0x06
	//movw	%cx, 0x06	/* CX=0 */
	call	set_floppy_preferred
1:
#endif

	popfw			/* CF=1 on error */
	jc	try_floppy	/* harddisk (hd0) failed, try floppy (fd0) */

	/*********************************/
	/* Helper is successfully loaded */
	/*********************************/
1:
	pushw	%cs
	popw	%ds
	lodsw
	movb	%ah, %dh	/* head number */
	lodsw
	movw	%ax, %cx	/* sector and cylinder number */
	andb	$63, %al
	//stc
	jz	helper_call_c
	
	/* use BP to calculate the sectors to read within 1 track */
	subw	%bp, %ax
	decw	%ax		/* decb	%al */
	negb	%al		/* AL=sectors upto the end of the track */
7:
	movw	$3, %di		/* retry 3 times on read failure */
2:
	movb	$2, %ah
	pushw	$FS_BOOT
	popw	%es		/* ES=FS_BOOT */
	xorw	%bx, %bx	/* read partition boot track to FS_BOOT:0000 */

#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))
	pushaw
//	int	$0x13		/* read partition boot track to FS_BOOT:0000 */
	call	int13
	popaw

	jnc	helper_call

	pushaw
	xorw	%ax, %ax
//	int	$0x13
	call	int13
	popaw
	decw	%di
#else
	call	read_disk_with_reset_and_dec_di
	jnc	helper_call
#endif

	jnz	2b

helper_call_c:

	stc

helper_call:
	/* find GRLDR in this partition
	 * before the call:
	 *	CF=1		: indicates an invalid or corrupt entry
	 *	CF=0		: indicates a valid entry
	 *
	 * on return:
	 * 	CF=1		: means "below", try next entry
	 *	CF=0,ZF=1	: means "equal", helper did nothing, so we need
	 *			  a further try to boot via NT bootsector
	 *	CF=0,ZF=0	: means "above", helper succeeded, boot it now
	 */
	call	helper_start	/* change to jmp 6f if helper not present */
	ja	filesystem_boot	/* helper succeeded, directly boot it */
6:

add_sub_si:

	/* extended partition check routine will adjust this to
	 *
	 *	0x83, 0xEE, 0x04 for "subw $4, %si"
	 *
	 *			 or
	 *
	 *	0x83, 0xC6, 0xFC for "addw $-4, %si" 
	 *
	 * so that SI keeps the value 0x1fe.
	 */
	addw	$12, %si	/* 0x83, 0xC6, 0x0C */

	. = add_sub_si + 3

	/* extended partition check routine will adjust the word 0x1fe at
	 * (add_sub_si + 5). The value 0x1ff or greater indicates there are
	 * entries need to be treated. The value 0x1fe indicates no entries
	 * left, and the floppy should be checked.
	 */

	cmpw	$0x01fe, %si	/* 0x81, 0xFE, 0xfe, 0x01 */
				/* All entries checked done? */
	jb	1b		/* No, check the next entry */
	ja	5f		/* floppy already checked. Fail and hang */

try_floppy:

	movw	$0x31b2, %si	/* a value big enough */
	movb	$8, %ah		/* read drive parameters changes DX,ES,DI,BX */
	cwd			/* DL=0 for floppy */
	pushw	%dx		/* DX=0 */
//	int	$0x13
	call	int13
	popw	%ax		/* AX=0 */
	jc	5f		/* floppy failure, issue "Error" and hang */
	cwd			/* DX=0 */
	xchgw	%ax, %cx	/* this moves CL to AL, and CX=0 */
	andb	$63, %al	/* AL=sectors per track */
	jz	5f		/* invalid value. floppy failure. hangs */
	//movw	$1, %cx
	incw	%cx
	jmp	7b

5:
Error_or_prev_MBR:

	/* GRLDR not found, print "Error" or launch previous MBR */
	movw	$(message_string - _start1), %si

	call	print_message	/* CS:SI points to message string */
3:	jmp	3b

int13:
	pushw	%ds
	pushw	%es
//	pushw	%bx
	pushw	%dx
	pushw	%si
	pushw	%di
	pushw	%bp
	stc
	int	$0x13
	popw	%bp
	popw	%di
	popw	%si
	popw	%dx
//	popw	%bx
	popw	%es
	popw	%ds
	ret

#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))
filesystem_boot:
	/* The partition boot record successfully modified, just boot it */

	/*
	 * The boot might fail, but we want to take back the control.
	 * So we save the registers now.
	 */
	pushw	%ds
	pushw	%es
	pushal

	/* DS=CS=GRLDR_CS, ES=FS_BOOT */

	/* save GRLDR_CS */

	movw	%es, %bx	# save old ES to BX

	cli
	lgdt	gdt - _start1
	movl	%cr0, %eax
	orb	$1, %al
	movl	%eax, %cr0

	movw	$8, %si
	movw	%si, %es

	xorl	%esi, %esi
	xorl	%edi, %edi
	movl	$(0x9000 / 4), %ecx

	cld
	repz movsl

	movw	$16, %si
	movw	%si, %es

	andb	$0xfe, %al
	movl	%eax, %cr0

	movw	%bx, %es	# restore ES from BX

	/* move FS_BOOT:0000 to 0:7c00 */
#if 0
	/* for single sector boot record */
	movw	$0x0200, %cx	/* move 2 sectors, the old FS_BOOT:0000 will keep untouched.  */
#else
	/* for 4-sector NTFS boot record */
	movw	$0x0400, %cx	/* move 4 sectors, the old FS_BOOT:0000 will keep untouched.  */
#endif
	xorw	%si, %si
	pushw	%si	/* SI=0, for the segment of 0000:7c00 */
	movw	$0x7c00, %di
	pushw	%di	/* DI=0x7c00, for the offset of 0000:7c00 */
	pushw	%es	/* ES=FS_BOOT */
	popw	%ds	/* DS=FS_BOOT */
	pushw	%si	/* SI=0 */
	popw	%es	/* ES=0 */
	cld
	repz movsw

	movw	$MONITOR, %di
	movw	$(restore_GRLDR_CS - _start1), %si
	movw	$((gdt_end - restore_GRLDR_CS) / 4), %cx
	cld
	repz cs movsl		/* CS segment override prefix(=0x2E) */

	pushw	%es	/* ES=0 */
	popw	%ds	/* DS=0 */
	sti
	lret	//ljmp	$0, $0x7c00
#endif

try_next_partition:

	cli
	movw	$GRLDR_CS, %ax
	movw	%ax, %ss
	movw	$(0x9000-36), %sp
	sti

	/* restore the registers and continue */
	popal
	popw	%es
	popw	%ds
	jmp	add_sub_si

#if (defined(GRLDR_MBR)) || (defined(GRLDR_INSTALL))
read_disk_with_reset_and_dec_di:
	pushaw
//	int	$0x13
	call	int13
	popaw

	jnc	3f

	pushaw
	xorw	%ax, %ax
//	int	$0x13
	call	int13
	popaw
	decw	%di
	stc
3:
	ret
#endif

	/* prints string CS:SI (modifies AX BX SI) */
3:
	//xorw	%bx, %bx	/* video page 0 */
	movb	$0x0e, %ah	/* print char in AL */
	int	$0x10		/* via TTY mode */

print_message:

	lodsb	%cs:(%si), %al	/* get token */
	cmpb	$0, %al		/* end of string? */
	jne	3b
	ret

message_string:

#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))
	.ascii	"\r\nMissing helper.\0"
#else
	.ascii	"\r\nMissing MBR-helper.\0"
#endif

#;buggy_bios_string:
#;
#;	.ascii	"\r\nBuggy BIOS!\0"

	/* Make sure the above code does not occupy the partition table */

#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))
	/* offset value here must be less than or equal to 0x1be */
	. = . - ((. - _start1) / 0x1bf)
#else
	/* offset value here must be less than or equal to 0x1b8 */
	. = . - ((. - _start1) / 0x1b9)
#endif

	/* The following code may occupy the same area as the partition table */

#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))

	/* we are not booted from MBR. So we can reuse the area of partition
	 * table for our code.
	 */

	. = _start1 + 0x1be

cdrom_check:

	/* DS=CS points to the sector start. */

	/* BX segment points to near the end of GRLDR image. */

	popw	%ax	/* old return IP */

	/* set BX as the new safe stack. */
	movw	%bx, %ss
	movw	$0xFFF0, %sp

	pushw	%ax	/* old return IP */

	/* check if DL is no-emulation-mode bootable CDROM. */
	pushw	%ds

	cmpb	$0x80, %dl
	jb	1f	/* not a valid no-emulation-mode cdrom drive number */

	cmpw	$0xAA55, 0x7FE		/* 2048 bytes loaded? */
	jne	1f

//	cmpw	$0xAA55, 0x5FE		/* 2048 bytes loaded? */
//	jne	1f

	movw	$0x0180, %si
	movw	$0x4B01, %ax
	pushw	$0x0040
	//.byte	0x6A, 0x40
	popw	%ds
	pushw	%ds
	popw	%es
	movb	$0x13, (%si)
	call	int13
//	pushw	%ds
//	pushw	%dx
//	int	$0x13
//	popw	%dx
//	popw	%ds

	/* ignore CF */
#;	jc	2f	/* not in emulation mode */
	xorl	%eax, %eax
	xorw	%bp, %bp
	testb	$0x0F, 1(%si)	/* boot media type is No Emulation? */
	jnz	2f	/* no, it simulates floppy or hard disk. */
	cmpb	%dl, 2(%si)	/* drive number */
	jnz	2f	/* invalid drive */

	/* OK! it is no-emulation-mode cdrom drive. */
	movl	4(%si), %eax	/* LBA of GRLDR */
	incw	%bp

2:
	jmp	cdrom_helper
1:
	popw	%ds
	ret

#else

	. = _start1 + 0x1fe	/* boot signature */

#endif	/* ! defined(GRLDR_MBR) && (! defined(GRLDR_INSTALL)) */

/* partition entries in the extended partitions will overwrite code here upto
 * 0x3fd.
 *
 * the extended partition entries will occupy a temp area at 0x9be00-0x9c3ff 
 */

#if (defined(GRLDR_MBR)) || (defined(GRLDR_INSTALL))
	.word	0xaa55
#endif

	. = _start1 + 0x200

/* if it is in the Master Boot Track, the second sector can be used to backup
 * the previously working MBR, typically, the MS MBR. if the backup copy of
 * the MBR cannot boot(because, e.g., it depends on another sector of code
 * that does not exist for now), then please do not set the ending signature
 * to 0xAA55, that is to say, if the signature is already 0xAA55, you should
 * change it to another value(for example, 0x0000).
 */

#if (! defined(GRLDR_INSTALL))
#if 0
print_cl:
	pushaw

	movw	%cx, %ax
	movb	$16, %cl
	divb	%cl		# quo=AL, rem=AH
	orw	$0x3030, %ax

	cmpb	$0x39, %ah
	jbe	1f
	addb	$7, %ah
1:
	cmpb	$0x39, %al
	jbe	1f
	addb	$7, %al
1:
	movb	%ah, %cl

	xorw	%bx, %bx

	movb	$0x0e, %ah
	int	$0x10

	movb	$0x0e, %ah
	movb	%cl, %al
	int	$0x10

	movw	$0x0e20, %ax
	int	$0x10

	popaw
	ret
#else
#if 0
	.word	5, 0x47, 0x52, 0x4c, 0x44, 0x52, 4, 0x24
	.word	0x49, 0x33, 0x30, 0xe000, 0, 0x3000, 0, 0
#else
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90

	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
#endif
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90

	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90

	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90

	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
#endif
	. = _start1 + 0x256	/* cmdcons comes here */

#if 0
	jmp	1f
#else
	.byte	0x90, 0x90
#endif

	. = _start1 + 0x258

	.byte	0x90, 0x90

	. = _start1 + 0x25a

	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90
	.byte	0x90, 0x90

	. = _start1 + 0x26a
1:
	//movw	%cs, %ax
	//movw	%ax, %ds
	//jmp	single_boot_sector

	/* a value < 0x80 here means we are not booted from no-emulation-mode
	 * bootable CD.
	 */
	movb	$0x7F, %dl
	jmp	_start1

#endif	/* (! defined(GRLDR_INSTALL)) */

#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))
cdrom_helper:

	/* IP and old_DS is on the stack. */

	/* DS=ES=40h */

	/* Stack is high and safe. */

	/* EAX is LBA. if EAX==0, LBA is unknown. */

	/* check if the first sector is the same as the current one */

	/* load the first sector onto the sector immediately follows */
1:
	pushw	%cs
	popw	%bx		/* BX=CS=old_DS=load_segment */
	addw	$0x0080, %bx	/* buffer segment */
	movw	%bx, %es	/* ES changed! */
	call	load_cd_sector

	/* compare the two sectors */
	movw	$0x200, %cx
	xorw	%si, %si
	xorw	%di, %di
	cld
	cs repz cmpsl
	je	load_the_rest	/* 1st sector is ok, continue */
not_grldr:
	testw	%bp, %bp
	jz	2f
	xorw	%bp, %bp
	xorl	%eax, %eax
2:
	incl	%eax
	jnz	1b		/* try next */

cd_no_grldr:

	popw	%ds		/* DS=load_segment */

	# Here we use error message and routine in FAT32 boot sector
	# which is also inside the 2048-byte CD sector.

	movw	$(msg_BootError_32 - _start1), %si
	jmp	boot_error_32
	
load_cd_sector:
	/* input:	EAX	LBA
	 *		BX	buffer segment(buffer offset=0)
	 *		DS	0x40 (or another safe one)
	 * output:
	 *		SI			changed(=0x1A0)
	 *		16 bytes at DS:SI	destroyed
	 */

	movw	$0x1A0, %si

	/* disk address packet */
	movl	$0x00010010, (%si)	/* load 1 sector each time. */
	movw	$0, 4(%si)		/* buffer offset=0 */
	movw	%bx, 6(%si)		/* buffer segment */
	movl	%eax, 8(%si)		/* LBA lo 32 bits */
	movl	$0, 12(%si)		/* LBA hi 32 bits */

//	pushw	%ds
//	pushw	%es
	pushal
	movb	$0x42, %ah
	call	int13
//	int	$0x13
	popal
//	popw	%es
//	popw	%ds
	ret

load_the_rest:

	/* load all sectors (except the first one) */

	/* EAX = first sector(LBA) of GRLDR */

	pushl	%eax

	pushw	%cs
	popw	%bx		/* BX=CS=old_DS=load_segment */
//	movw	%bx, %es
	/* 6144 = 0x1800 = 3 sectors > 4KB, this is for the additional 4KB-preset-menu at the end of grldr */
	movw	$((grldr_signature - _start1 + 4 + STAGE2_SIZE - 1 + 6144) / 2048), %cx	/* sectors to load */
1:
	incl	%eax		/* next sector */
	addw	$0x0080, %bx	/* buffer segment */

	call	load_cd_sector

	loop	1b

	/* loading is completed. BX=segment of the last sector. */

	subw	$0x0181, %bx	/* decw	%bx */
	movw	%bx, %ds

	popl	%eax
//	subl	$((grldr_signature - _start1 + 4 + STAGE2_SIZE - 1 + 6144) / 2048), %eax

	/* check the ending signature */
	cmpl	$0xCE1A02B0, ((grldr_signature - _start1 + 4 + STAGE2_SIZE - 1) % 2048) + 13
	jne	not_grldr
#;	je	grldr_real_start	/* yes. boot it! */

#;	/* it is not our grldr image, return and use MBR-helper. */
#;
#;4:
#;	//jmp	grldr_real_start
#;	popw	%ds
#;	ret

grldr_real_start:

	#; FAT_12_16 no longer be used. So comment out.
	#;je	1f	/* jc	1f */
	#;//ZF=0	/* CF cleared, so we are coming from FAT_12_16 */
	#;popw	%dx		/* discard the cluster number */
	#;popw	%dx		/* this is our boot_drive/boot_partition */
	#;1:

	#; The partition number for no-emulation-mode bootable CDROM will be
	#; set to 0xFF later(in common.c). So comment out.
	#;cli
	#;movw	%cs, %ax
	#;cmpw	$0x1000, %ax
	#;jne	1f
	#;
	#;/* CS=0x1000, may be booted from ext2 or no-emulation-mode CDROM */
	#;
	#;cmpw	$0x1000, %di
	#;jne	2f
	#;cmpw	$0x7c00, %bp
	#;jne	2f
	#;movw	%es, %ax
	#;cmpw	$0x1000, %ax
	#;jbe	2f
	#;cmpw	$0x7c00, %si
	#;jbe	2f
	#;movl	%edx, %eax
	#;shrl	$16, %eax
	#;jnz	2f
	#;jecxz	1f		// booted from ext2 partition
	#;2:
	#;// booted from no-emulation-mode bootable CDROM
	#;movb	$0xff, %dh	// partition 0xff means whole drive(for CDROM)
	#;			#; if needed, 0xfe can be used as an indicator
	#;			#; here for the bootable CDROM and changed to
	#;			#; 0xff later.
	#;1:
	#;
	#;//if not booted from CDROM, don't touch the boot partition number(dh)

	cli
	xorw	%ax, %ax
	movw	%ax, %ss
	movw	$0x0400, %sp	/* tmp use real-mode IDT as stack */
	movw	%cs, %bp	/* save CS to BP */
	call	1f
1:
	popw	%bx		/* BX=Instruction Pointer of 1b */
	subw	$(1b - _start1), %bx
	movw	%bx, %cx
	shrw	$4, %bx
	addw	%bp, %bx
	pushw	%bx		/* new CS */
	andw	$0x000f, %cx
	addw	$(1f - _start1), %cx
	pushw	%cx		/* new IP */
	lret
1:
	movw	%ds, %cx	/* CX==BP==0x7C0 for pxe enabled */
	pushw	%cs
	popw	%ds

	/* CS=DS=BX, CS:0000 = _start1 */

	addw	$((pre_stage2_start - _start1) >> 4), %bx

	/* BX:0000 = pre_stage2_start */

	cmpw	$0x7C0, %bp
	jne	1f
	cmpw	%bp, %cx
	je	2f
1:
	/* disable pxe */
	orb	$0x01, (pre_stage2_start - _start1 + 5)
2:
	cmpw	$0x820, %bx
	jb	2f

	movw	$((0x8200 - (pre_stage2_start - _start1) - 0x400) >> 4), %cx

	/* Now CS(=DS) >= CX+0x40 */

	movw	%cx, %es
	xorw	%di, %di
	xorw	%si, %si

	/////////////////////////////////////////////////////////////
	//
	//                    CS
	//                    DS          0x820     BX
	//                    _start1---------------pre_stage2_start
	//          CX+0x40---------------0x820
	//   CX
	//   ES
	//
	/////////////////////////////////////////////////////////////

	movw	$0x200, %cx	/* move 2 sectors */
	cld
	repz movsw

	pushw	%es		/* ES:0000 = _start */
	pushw	$(1f - _start)
	lret			/* CS=ES, CS:0000 = _start1 */
1:

	/* move BX:0000 to 0820:0000 upward since BX >= 0x820 */

	cld

	movw	%bx, %ds
	movw	$0x820, %bx
	movw	%bx, %es

	xorw	%si, %si
	xorw	%di, %di

	movw	$6, %bx		/* 64K pages: 0x20000 - 0x7ffff */
1:
	movw	$0x8000, %cx
	repz movsw
	movw	%ds, %ax
	addw	$0x1000, %ax
	movw	%ax, %ds
	movw	%es, %ax
	addw	$0x1000, %ax
	movw	%ax, %es
	decw	%bx
	jnz	1b

	jmp	3f
2:

	/* move BX:0000 to 0820:0000 downward since BX < 0x820 */

	std

	addw	$0x7000, %bx
	movw	%bx, %ds
	movw	$0x7820, %bx
	movw	%bx, %es

	movw	$0xfffe, %si
	movw	%si, %di

	movw	$8, %bx		/* 64K pages: 0x08200 - 0x881ff */
1:
	movw	$0x8000, %cx
	repz movsw
	movw	%ds, %ax
	subw	$0x1000, %ax
	movw	%ax, %ds
	movw	%es, %ax
	subw	$0x1000, %ax
	movw	%ax, %es
	decw	%bx
	jnz	1b

	cld

3:

	/* put the config file name */
	xorw	%ax, %ax
	movw	%ax, %es
	movw	%ax, %ds

	xorl	%ebp, %ebp
	
	movb	%dh, 0x820A	/* this is the boot partition number */

	#; clear saved_entryno so that force_cdrom_as_boot_device be cleared
	#; later in common.c

	movl	%ebp, 0x820C	/* EBP=0, clear saved_entryno */

	movw    $0x0010, %cx	/* set max length of grub version string */
	movw    $0x8212, %di	/* version string */
	cld
	/* AL is already 0. Locate the end of version string */
	repnz scasb	/* find the location of the default config file name */

	jcxz	1f	/* failed, will not use the default config file name */

	movw    $0x4e, %cx	/* max length of config file name */

	movw	%cs, %si	/* CS:0000 = _start1 */
	shlw	$4, %si		/* 0000:SI = _start1 */

	addw	$(default_config_file - _start1), %si

	//movw	$(default_config_file + 0x8200 - pre_stage2_start), %si
	cld
	repz movsb	/* move file name to the config-file field of stage2 */
1:

	movw	$0x0003, %ax	/* set display mode: 80*25 color text */
	int	$0x10

	//xorw	%bx, %bx
	//movw	$(launch_pre_stage2 - _start1), %si
	//call	print_message	/* CS:SI points to message string */

	//xorw	%ax, %ax
	//movw	%ax, %ss
	//movw	$0x2000, %sp

	//sti

	ljmp	$0, $0x8200

//launch_pre_stage2:
//	.ascii	"\r\nBooting GRLDR...\r\n"

//	.byte	0		/* mark the end of ascii zero string */

default_config_file:
	.ascii	"/menu.lst"

	.byte	0		/* mark the end of ascii zero string */
#endif	/* ! defined(GRLDR_MBR) && (! defined(GRLDR_INSTALL)) */

	. = _start1 + 0x400

#define ALTERNATIVE_KERNEL


/*
 * The following is based on FreeDOS, modified heavily by Tinybit in Feb, 2004
 *
 * Merges LBA and CHS boot sectors to ONE FAT32 boot sector!
 *
 * Memory layout for GRLDR FAT32 single stage boot process:
 *
 *	...
 *	|-------| 1FE0:7E00
 *	|BOOTSEC| (GRUB does not use this relocation area)
 *	|RELOC.	| (overwritten by kernel loaded)
 *	|-------| 1FE0:7C00
 *	...
 *	|-------|
 *	|KERNEL	| (overwrites bootsec reloc.)
 *	|LOADED	| (holds 1 sector directory buffer before kernel load)
 *	|-------| 2000:0000
 *	...
 *	|-------| 0000:7E00
 *	|BOOTSEC| GRUB always run inside this sector,
 *	|ORIGIN | no relocation.
 *	|-------| 0000:7C00
 *	...
 *	|-------| 0060:0200
 *	|  FAT  | (only 1 sector buffered)
 *	|-------| 0060:0000
 *	...
 *
 */

/*
; This is an LBA-enabled FreeDOS FAT32 boot sector (single sector!).
; You can use and copy source code and binaries under the terms of the
; GNU Public License (GPL), version 2 or newer. See www.gnu.org for more.

; Based on earlier work by FreeDOS kernel hackers, modified heavily by
; Eric Auer and Jon Gentle in 7 / 2003.
;
; Features: Uses LBA and calculates all variables from BPB/EBPB data,
; thus making partition move / resize / image-restore easier. FreeDOS
; can boot from FAT32 partitions which start > 8 GB boundary with this
; boot sector. Disk geometry knowledge is not needed for booting.
;
; Windows uses 2-3 sectors for booting (sector stage, statistics sector,
; filesystem stage). Only using 1 sector for FreeDOS makes multi-booting
; of FreeDOS and Windows on the same filesystem easier.
;
; Requirements: LBA BIOS and 386 or better CPU. Use the older CHS-only
; boot sector if you want FAT32 on really old PCs (problems: you cannot
; boot from > 8 GB boundary, cannot move / resize / ... without applying
; SYS again if you use the CHS-only FAT32 boot sector).
;
; FAT12 / FAT16 hints: Use the older CHS-only boot sector unless you
; have to boot from > 8 GB. The LBA-and-CHS FAT12 / FAT16 boot sector
; needs applying SYS again after move / resize / ... a variant of that
; boot sector without CHS support but with better move / resize / ...
; support would be good for use on LBA harddisks.


; Memory layout for the FreeDOS FAT32 single stage boot process:

;	...
;	|-------| 1FE0:7E00
;	|BOOTSEC|
;	|RELOC.	|
;	|-------| 1FE0:7C00
;	...
;	|-------| 2000:0200
;	|  FAT  | (only 1 sector buffered)
;	|-------| 2000:0000
;	...
;	|-------| 0000:7E00
;	|BOOTSEC| overwritten by the kernel, so the
;	|ORIGIN | bootsector relocates itself up...
;	|-------| 0000:7C00
;	...
;	|-------|
;	|KERNEL	| maximum size 134k (overwrites bootsec origin)
;	|LOADED	| (holds 1 sector directory buffer before kernel load)
;	|-------| 0060:0000
;	...
*/

#define BOOTGRUB	/* undef this if compiled for loading FreeDOS */
//#undef BOOTGRUB

#ifdef	BOOTGRUB
#define LOADSEG		0x2000
#define FATSEG		0x0060
#else
#define LOADSEG		0x0060
#define FATSEG		0x2000
#endif

Entry_32:
	jmp	1f

	. = Entry_32 + 0x02

	/* The default mode is CHS. This is for maximum compatiblity with
	 * small-sized disks, e.g., floppies.
	 *
	 * Valid values are 0x90 for CHS mode, or 0x0e for LBA mode.
	 *
	 * If the BIOS int13 supports LBA, this byte can be safely set to 0x0e.
	 *
	 * Some USB BIOSes might have bugs when using CHS mode, so the format
	 * program should set this byte to 0x0e. It seems that (generally) all
	 * USB BIOSes have LBA support.
	 *
	 * If the format program does not know whether the BIOS has LBA
	 * support, it may operate this way:
	 *
	 * if (partition_start + total_sectors_in_partition) exceeds the CHS
	 * addressing ability(especially when it is greater than 1024*256*63),
	 * the caller should set this byte to 0x0e, otherwise, set to 0x90.
	 */

	.byte	0x90	/* for CHS. Another possible value is 0x0e for LBA */


	. = Entry_32 + 0x03

#ifdef	BOOTGRUB
	.ascii	"GRLDR   "	/* OEM name string (of OS which formatted the disk). */
#endif

	. = Entry_32 + 0x0b

	.word	0x200		/* bytes per sector. Must be 512 */

	. = Entry_32 + 0x0d

	/* Sectors per cluster. Valid values are 1, 2, 4, 8, 16, 32, 64 and 128.
	 * But a cluster size larger than 32K should not occur.
	 */

	.byte	1		/* sectors per cluster */

	. = Entry_32 + 0x0e

	/* Reserved sectors(number of sectors before the first FAT,
	 * including the boot sector), usually 1.
	 */

	.word	1		/* reserved sectors */

	. = Entry_32 + 0x10

	/* Number of FATs(nearly always 2). */

	.byte	2		/* number of FATs */

	. = Entry_32 + 0x11

	/* (Maximum number of root directory entries)Must be 0. */

	.word	0		/* Max dir entries for FAT12/FAT16 */

	. = Entry_32 + 0x13

	/* (Total number of sectors for small disks only)Must be 0. */

	.word	0		/* total sectors for FAT12/FAT16 */

	. = Entry_32 + 0x15

	/* Media descriptor byte, pretty meaningless now. */

	.byte	0xf8		/* media descriptor */

	. = Entry_32 + 0x16

	/* (Sectors per FAT)Must be 0. */

	.word	0		/* sectors per FAT for FAT12/FAT16 */

	. = Entry_32 + 0x18

	.word	18		/* sectors per track */

	. = Entry_32 + 0x1a

	.word	2		/* number of heads */

	. = Entry_32 + 0x1c

	/* Number of hidden sectors (those preceding the boot sector).
	 * Also referred to as the starting sector of the partition.
	 * For floppies, it should be 0.
	 */

	.long	0		/* hidden sectors */

	. = Entry_32 + 0x20

	/* Total number of sectors in the filesystem. */

	.long	0		/* total sectors for FAT32 */

	. = Entry_32 + 0x24

	/* FAT32 sectors per FAT. */

	.long	0

	. = Entry_32 + 0x28

	/* If bit 7 is clear then all FATs are updated, otherwise bits 0-3
	 * give the current active FAT, all other bits are reserved.
	 * This word is not used by grldr boot code.
	 */

	.word	0

	. = Entry_32 + 0x2a

	/* High byte is major revision number, low byte is minor revision
	 * number, currently both are 0.
	 * This word is not used by grldr boot code.
	 */

	.word	0

	. = Entry_32 + 0x2c

	/* Root directory starting cluster. */

	.long	0

	. = Entry_32 + 0x30

	/* File system information sector number.
	 * This word is not used by grldr boot code.
	 */

	.word	0

	. = Entry_32 + 0x32

	/* If non-zero this gives the sector which holds a copy of the
	 * boot record, usually 6.
	 * This word is not used by grldr boot code.
	 */

	.word	6

	. = Entry_32 + 0x34

	/* Reserved, 12 bytes, set to 0. */

	.long	0
	.long	0
	.long	0

	. = Entry_32 + 0x40

	/* drive number of the boot device.
	 * This byte is ignored for read. The program will write DL onto
	 * this byte. The caller should set drive number in DL. 
	 * We assume all BIOSes pass correct drive number in DL.
	 * That is to say, buggy BIOSes are not supported!!
	 */

	.byte	0

	. = Entry_32 + 0x41

	/* partition number of this filesystem in the boot drive.
	 * This byte is ignored for read. The boot code will write partition
	 * number onto this byte. See Entry + 0x5d below. 
	 */

	.byte	0

	. = Entry_32 + 0x42

	/* Signature (must be 28h or 29h to be recognised by NT). */

	.byte	0x29		/* extended boot signature for FAT12/FAT16 */

	. = Entry_32 + 0x43

	.long	0x0AC4AF63	/* volume serial number */

	. = Entry_32 + 0x47

	.ascii	"NO NAME    "	/* volume label, 11 bytes. */

	. = Entry_32 + 0x52

	.ascii	"FAT32   "	/* filesystem ID, 8 bytes. */

/*
;	bp is initialized to 7c00h
; %define bsOemName	bp+0x03	; OEM label (8)
%define bsBytesPerSec	bp+0x0b ; bytes/sector (dw)
%define bsSecPerClust	bp+0x0d	; sectors/allocation unit (db)
%define bsResSectors	bp+0x0e	; # reserved sectors (dw)
%define bsFATs		bp+0x10	; # of fats (db)
; %define bsRootDirEnts	bp+0x11	; # of root dir entries (dw, 0 for FAT32)
			; (FAT32 has root dir in a cluster chain)
; %define bsSectors	bp+0x13	; # sectors total in image (dw, 0 for FAT32)
			; (if 0 use nSectorHuge even if FAT16)
; %define bsMedia	bp+0x15	; media descriptor: fd=2side9sec, etc... (db)
; %define sectPerFat	bp+0x16	; # sectors in a fat (dw, 0 for FAT32)
			; (FAT32 always uses xsectPerFat)
%define sectPerTrack	bp+0x18	; # sectors/track
; %define nHeads	bp+0x1a	; # heads (dw)
%define nHidden		bp+0x1c	; # hidden sectors (dd)
; %define nSectorHuge	bp+0x20	; # sectors if > 65536 (dd)
%define xsectPerFat	bp+0x24	; Sectors/Fat (dd)
			; +0x28 dw flags (for fat mirroring)
			; +0x2a dw filesystem version (usually 0)
%define xrootClst	bp+0x2c	; Starting cluster of root directory (dd)
			; +0x30 dw -1 or sector number of fs.-info sector
			; +0x32 dw -1 or sector number of boot sector backup
			; (+0x34 .. +0x3f reserved)
%define drive		bp+0x40	; Drive number
			bp+0x41	; partition number for GRLDR

%define fat_sector	bp+0x44		; last accessed FAT sector (dd)
					; (overwriting unused bytes)
%define fat_start	bp+0x48		; first FAT sector (dd)
					; (overwriting unused bytes)
%define data_start	bp+0x4c		; first data sector (dd)
					; (overwriting unused bytes)

*/
		/* not used: [0x42] = byte 0x29 (ext boot param flag)
		 * [0x43] = dword serial
		 * [0x47] = label (padded with 00, 11 bytes)
		 * [0x52] = "FAT32",32,32,32 (not used by Windows)
		 * ([0x5a] is where FreeDOS parts start)
		 */

	. = Entry_32 + 0x5a
1:
	cli
	cld

#ifdef	BOOTGRUB

	. = Entry_32 + 0x5c

	/* the byte at offset 0x5d stores the real partition number for read.
	 * the format program or the caller should set it to a correct value.
	 * For floppies, it should be 0xff, which stands for whole drive.
	 */

	movb	$0xff, %dh	/* boot partition number */

	cmpb	$0xff, %dh	/* is floppy? */
	jne	1f
	movb	$0, %dl		/* yes, let drive number = 0 */
1:
#endif

	xorw	%ax, %ax
	movw	$0x7c00, %bp

#ifndef	BOOTGRUB
	movw	%ax, %ds
	movw	$0x1fe0, %ax
	movw	%ax, %es
	movw	%bp, %si	/* move from 0000:7c00 */
	movw	%bp, %di	/* move to 1fe0:7c00 */
	movw	$0x0100, %cx	/* one sector to move */
	repz movsw
	ljmp	$0x1fe0, $(1f - Entry_32 + 0x7c00)
1:
#endif
	movw	%ax, %ss	/* stack and BP-relative moves up, too */
	leaw	-0x20(%bp), %sp
	sti
	movw	%dx, 0x40(%bp)	/* BIOS passes drive number in DL */

	pushw	%ss
	movb	$0x41, %ah
	movw	$0x55AA, %bx
	int	$0x13
	popw	%ds
	jc	1f		/* No EBIOS */
	cmpw	$0xAA55, %bx
	jne	1f		/* No EBIOS */
	testb	$1, %cl
	jz	1f		/* No EBIOS */
	/* EBIOS supported */
	movb	$0x42, (ebios_32 - 1 - Entry_32 + 0x7c00)
1:
	pushw	%ss
	popw	%es

/* figure out where FAT and DATA area starts
 * (modifies EAX EDX, sets fat_start and data_start variables)
 */
	xorl	%eax, %eax
	movl	%eax, 0x44(%bp)	/* init buffer status */

	/* first, find fat_start */
	movw	0x0e(%bp), %ax	/* reserved sectors */
	addl	0x1c(%bp), %eax	/* hidden sectors */
	movl	%eax, 0x48(%bp)	/* first FAT sector */
	movl	%eax, 0x4c(%bp)	/* first data sector, initial value */

	/* next, find data_start */
	movl	0x10(%bp), %eax	/* number of fats, no movzbl needed: the */
				/* 2 words at 0x11(%bp) are 0 for fat32. */
	mull	0x24(%bp)	/* sectors per fat (EDX=0) */
	addl	%eax, 0x4c(%bp)	/* first DATA sector */

/* Searches for the file in the root directory.
 * Returns:	EAX = first cluster of file
 */

	movl	0x2c(%bp), %eax	/* root dir cluster */

1:
	pushl	%eax		/* save cluster */
	call	cluster_to_lba_32
		/* EDX is sectors per cluster, EAX is sector number */
	movw	$(msg_BootError_32 - Entry_32 + 0x7c00), %si
	jc	boot_error_32	/* EOC encountered */

2:
	lesw	(loadseg_off_32 - Entry_32)(%bp), %bx	/* load to loadseg:0 */
	call	readDisk_32

	xorw	%di, %di

	/* Search for kernel file name, and find start cluster */
3:
	movw	$11, %cx
	movw	$(filename_32 - Entry_32 + 0x7c00), %si
	repz cmpsb
	jz	1f	/* note that di now is at dirent+11 */

	addw	$0x20, %di
	andw	$-0x20, %di	/* 0xffe0 */
	cmp	0x0b(%bp), %di	/* bytes per sector */
	jnz	3b		/* next directory entry */

	decw	%dx	/* initially DX holds sectors per cluster */
	jnz	2b	/* loop over sectors in cluster */

	popl	%eax		/* restore current cluster */
	call	next_cluster_32
	jmp	1b		/* read next cluster */

#ifndef ALTERNATIVE_KERNEL
loadseg_off_32:
	.word	0
	.word	LOADSEG
#endif

1:
	/* kernel directory entry is found */
	pushw	%es:(0x14-11)(%di)	/* get cluster number HI */
	pushw	%es:(0x1a-11)(%di)	/* get cluster number LO */
	popl	%eax			/* convert to 32bit */

	xorw	%bx, %bx	/* read kernel at ES:BX=LOADSEG:0 */

/* read kernel */

2:
	pushl	%eax
	call	cluster_to_lba_32
		/* EDX is sectors per cluster, EAX is sector number */
	jnc	1f
	
	/* EOC encountered - done */
#ifdef	BOOTGRUB
	movw	0x40(%bp), %dx	/* boot_drive and boot_partition */
#else
	movb	0x40(%bp), %bl	/* FreeDOS kernel uses BL, not DL, for drive */
#endif
	ljmp	*(loadseg_off_32 - Entry_32)(%bp)

1:
	call	readDisk_32
	decw	%dx	/* initially DX holds sectors per cluster */
	jnz	1b	/* loop over sectors in cluster */

	popl	%eax
	call	next_cluster_32
	jmp	2b
		
/* given a cluster number, find the number of the next cluster in
 * the FAT chain. Needs fat_start.
 * input:	EAX - cluster
 *		EDX = 0
 * output:	EAX - next cluster
 *		EDX = undefined
 */

next_cluster_32:
	pushw	%es
	/* pushw	%di */
	pushw	%bx		/* hi word of EBX never used */

#if 1
	/* xorl	%edx, %edx */
	shll	$2, %eax	/* 32bit FAT */
	movzwl	0x0b(%bp), %ebx	/* bytes per sector */
	divl	%ebx		/* residue is in EDX */
	/* movw	%dx, %di */
#else	
	shll	$2, %eax	/* 32bit FAT */
	;xchgw	%ax, %di	/* movw	%ax, %di */
	movw	%ax, %di
	;shlw	$2, %di		/* 32bit FAT */

	pushw	%cx
	movw	0x0b(%bp), %bx	/* bytes per sector */
	bsfw	%bx, %cx
	;decw	%cx
	;decw	%cx
	decw	%bx
	andw	%bx, %di	/* mask to sector size */
	shrl	%cl, %eax
	popw	%cx
#endif	
	addl	0x48(%bp), %eax	/* add the first FAT sector number.  */ 
				/* EAX=absolute sector number */
	movw	$FATSEG, %bx
	movw	%bx, %es
	xorw	%bx, %bx

	/* is it the last accessed and already buffered FAT sector? */
	cmpl	0x44(%bp), %eax
	jz	1f
	movl	%eax, 0x44(%bp)	/* mark sector EAX as buffered */
	call	readDisk_32	/* read sector EAX to buffer */
1:
#if 1
	//.byte	0x67, 0x26, 0x80, 0x62, 0x03, 0x0f
	addr32 andb	$0x0f, %es:3(%edx)	/* mask out top 4 bits */

	//.byte	0x67, 0x66, 0x26, 0x8b, 0x02
	addr32 movl	%es:(%edx), %eax	/* read next cluster number */
#else
	andb	$0x0f, %es:3(%di)	/* mask out top 4 bits */
	movl	%es:(%di), %eax	/* read next cluster number */
#endif
	popw	%bx
	/* popw	%di */
	popw	%es
	ret

/* Convert cluster number to the absolute sector number
 * ... or return carry if EndOfChain! Needs data_start.
 * input:	EAX - target cluster
 * output:	EAX - absolute sector
 *		EDX - [bsSectPerClust] (byte)
 *		carry clear
 *		(if carry set, EAX/EDX unchanged, end of chain)
 */

cluster_to_lba_32:
	cmpl	$0x0ffffff8, %eax	/* check End Of Chain */
	cmc
	jb	1f			/* carry is stored if EOC */

	/* sector = (cluster-2) * clustersize + data_start */
	decl	%eax
	decl	%eax

	movzbl	0x0d(%bp), %edx		/* sectors per cluster */
	pushw	%dx			/* only DX would change */
	mull	%edx			/* EDX = 0 */
	popw	%dx
	addl	0x4c(%bp), %eax		/* data_start */
	/* here, carry is cleared (unless parameters are wrong) */
1:
	ret

/* Read a sector from disk, using LBA or CHS
 * input:	EAX - 32-bit DOS sector number
 *		ES:BX - destination buffer
 *		(will be filled with 1 sector of data)
 * output:	ES:BX points one byte after the last byte read.
 *		EAX - next sector
 */
 
readDisk_32:
	pushal
	xorl	%edx, %edx	/* EDX:EAX = LBA */
	pushl	%edx		/* hi 32bit of sector number */
	pushl	%eax		/* lo 32bit of sector number */
	pushw	%es		/* buffer segment */
	pushw	%bx		/* buffer offset */
	pushw	$1		/* 1 sector to read */
	pushw	$16		/* size of this parameter block */

	xorl	%ecx, %ecx
	pushl	0x18(%bp)	/* lo:sectors per track, hi:number of heads */
	popw	%cx		/* ECX = sectors per track */
	divl	%ecx		/* residue is in EDX */
				/* quotient is in EAX */
	incw	%dx		/* sector number in DL */
	popw	%cx		/* ECX = number of heads */
	pushw	%dx		/* push sector number into stack */
	xorw	%dx, %dx	/* EDX:EAX = cylinder * TotalHeads + head */
	divl	%ecx		/* residue is in EDX, head number */
				/* quotient is in EAX, cylinder number */
	xchgb	%dl, %dh	/* head number should be in DH */
				/* DL = 0 */
	popw	%cx		/* pop sector number from stack */
	xchgb	%al, %ch	/* lo 8bit cylinder should be in CH */
				/* AL = 0 */
	shlb	$6, %ah		/* hi 2bit cylinder ... */
	orb	%ah, %cl	/* ... should be in CL */
	
	movw	$0x201, %ax	/* read 1 sector */
ebios_32: /* ebios_32 - 1 points to 0x02 that can be changed to 0x42 */

	movw	%sp, %si	/* DS:SI points to disk address packet */
	movb	0x40(%bp), %dl	/* hard disk drive number */
	pushw	%es
	pushw	%ds
	int	$0x13
	popw	%ds
	popw	%es
	popaw			/* remove parameter block from stack */
	popal
	jc	disk_error_32	/* disk read error, jc 1f if caller handles */
	incl 	%eax		/* next sector */
	addw	0x0b(%bp), %bx	/* bytes per sector */
	jnc	1f		/* 64K bound check */
	pushw	%dx
	movw	%es, %dx
	addb	$0x10, %dh	/* add 1000h to ES */
				/* here, carry is cleared */
	movw	%dx, %es
	popw	%dx
1:
	/* carry stored on disk read error */
	ret

//	. = . - (. - readDisk_32)/91

msg_DiskReadError_32:

	.ascii	"disk error\0"

msg_BootError_32:

	.ascii	"No "

filename_32:

#ifdef	BOOTGRUB
	.ascii	"GRLDR      \0"
#else
	.ascii	"KERNEL  SYS\0"
#endif

#ifdef ALTERNATIVE_KERNEL
filename_end_32:

	. = Entry_32 + 0x1e8

loadseg_off_32:
	.word	0
	.word	LOADSEG

	. = Entry_32 + 0x1ec

boot_image_ofs_32:

	.word (filename_32 - Entry_32)+(filename_end_32 - filename_32 - 1)*2048
#endif

	. = Entry_32 + 0x1ee

disk_error_32:

	movw	$(msg_DiskReadError_32 - Entry_32 + 0x7c00), %si

boot_error_32:

/* prints string DS:SI (modifies AX BX SI) */

//print_32:
1:
	lodsb	(%si), %al	/* get token */
	//xorw	%bx, %bx	/* video page 0 */
	movb	$0x0e, %ah	/* print it */
	int	$0x10		/* via TTY mode */
	cmpb	$0, %al		/* end of string? */
	jne	1b		/* until done */

	/* The caller will change this to
	 *	ljmp	$0x9400, $(try_next_partition - _start1)
	 */

1:	jmp	1b

	. = Entry_32 + 0x1fc

	.word	0, 0xAA55 /* Win9x uses all 4 bytes as magic value here */

	. = Entry_32 + 0x200

	. = _start1 + 0x600

	//.arch	i8086, nojumps
	.arch	i186, nojumps
/*
 * The following is based on FreeDOS, modified heavily by Tinybit in Feb, 2004
 *
 * Merges FAT12 and FAT16 boot sectors to ONE FAT boot sector!
 *
 * Memory layout for GRLDR FAT single stage boot process:
 *
 *	+--------+
 *	|        |
 *	|GRLDR   | also used as max 128k FAT buffer
 *	|LOADED  | before GRLDR loading starts
 *	|--------| 2000:0000
 *	|        |
 *	|--------| 0000:7E00
 *	|BOOTSECT|
 *	|ORIGIN  |
 *	|--------| 0000:7C00
 *	|        |
 *	|--------| 0000:3000
 *	|CLUSTER |
 *	|LIST    |
 *	|--------| 0000:2000
 *	|        |
 *	+--------+
 */

/*
;
; File:
;                            boot.asm
; Description:
;                           DOS-C boot
;
;                       Copyright (c) 1997;
;                           Svante Frey
;                       All Rights Reserved
;
; This file is part of DOS-C.
;
; DOS-C is free software; you can redistribute it and/or
; modify it under the terms of the GNU General Public License
; as published by the Free Software Foundation; either version
; 2, or (at your option) any later version.
;
; DOS-C is distributed in the hope that it will be useful, but
; WITHOUT ANY WARRANTY; without even the implied warranty of
; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
; the GNU General Public License for more details.
;
; You should have received a copy of the GNU General Public
; License along with DOS-C; see the file COPYING.  If not,
; write to the Free Software Foundation, 675 Mass Ave,
; Cambridge, MA 02139, USA.
;
;
;	+--------+ 1FE0:7E00
;	|BOOT SEC|
;	|RELOCATE|
;	|--------| 1FE0:7C00
;	|        |
;	|--------| 1FE0:3000
;	| CLUSTER|
;	|  LIST  |
;	|--------| 1FE0:2000
;	|        |
;	|--------| 0000:7E00
;	|BOOT SEC| overwritten by max 128k FAT buffer
;	|ORIGIN  | and later by max 134k loaded kernel
;	|--------| 0000:7C00
;	|        |
;	|--------|
;	|KERNEL  | also used as max 128k FAT buffer
;	|LOADED  | before kernel loading starts
;	|--------| 0060:0000
;	|        |
;	+--------+
*/

#ifdef	BOOTGRUB
#define LOADSEG_12_16   0x2000
#define FATBUF          0x2000        /* offset of temp buffer for FAT chain */
#else
#define LOADSEG_12_16   0x0060
#define FATBUF          0x2000        /* offset of temp buffer for FAT chain */
#endif

Entry_12_16:
	jmp     1f

	. = Entry_12_16 + 0x02

	/* The default mode is CHS. This is for maximum compatiblity with
	 * small-sized disks, e.g., floppies.
	 *
	 * Valid values are 0x90 for CHS mode, or 0x0e for LBA mode.
	 *
	 * If the BIOS int13 supports LBA, this byte can be safely set to 0x0e.
	 *
	 * Some USB BIOSes might have bugs when using CHS mode, so the format
	 * program should set this byte to 0x0e. It seems that (generally) all
	 * USB BIOSes have LBA support.
	 *
	 * If the format program does not know whether the BIOS has LBA
	 * support, it may operate this way:
	 *
	 * if (partition_start + total_sectors_in_partition) exceeds the CHS
	 * addressing ability(especially when it is greater than 1024*256*63),
	 * the caller should set this byte to 0x0e, otherwise, set to 0x90.
	 */

	.byte	0x90	/* for CHS. Another possible value is 0x0e for LBA */


	. = Entry_12_16 + 0x03

#ifdef	BOOTGRUB
	.ascii	"GRLDR   "
#endif

	. = Entry_12_16 + 0x0b

	.word	0x200		/* bytes per sector */

	. = Entry_12_16 + 0x0d

	.byte	1		/* sectors per cluster */

	. = Entry_12_16 + 0x0e

	.word	1		/* reserved sectors */

	. = Entry_12_16 + 0x10

	.byte	2		/* number of FATs */

	. = Entry_12_16 + 0x11

	.word	224		/* Max dir entries */

	. = Entry_12_16 + 0x13

	.word	2880		/* total sectors in the filesystem */

	. = Entry_12_16 + 0x15

	.byte	0xf0		/* media descriptor */

	. = Entry_12_16 + 0x16

	.word	9		/* sectors per FAT */

	. = Entry_12_16 + 0x18

	.word	18		/* sectors per track */

	. = Entry_12_16 + 0x1a

	.word	2		/* number of heads */

	. = Entry_12_16 + 0x1c

	.long	0		/* hidden sectors */

	. = Entry_12_16 + 0x20

	.long	0		/* total sectors for large partitions */

	. = Entry_12_16 + 0x24

	/* drive number of the boot device.
	 * This byte is ignored for read. The program will write DL onto
	 * this byte. The caller should set drive number in DL. 
	 * We assume all BIOSes pass correct drive number in DL.
	 * That is to say, buggy BIOSes are not supported!!
	 */

	.byte	0

	. = Entry_12_16 + 0x25

	/* partition number of this filesystem in the boot drive.
	 * This byte is ignored for read. The boot code will write partition
	 * number onto this byte. See Entry_12_16 + 0x41 below. 
	 */

	.byte	0

	. = Entry_12_16 + 0x26

	.byte	0x29		/* extended boot signature */

	. = Entry_12_16 + 0x27

	.long	0x0AC4AF63	/* volume serial number */

	. = Entry_12_16 + 0x2b

	.ascii	"NO NAME    "	/* volume label */

	. = Entry_12_16 + 0x36

	.ascii	"FAT12   "	/* filesystem ID */

/*
;       bp is initialized to 7c00h
%define bsOemName       bp+0x03      ; OEM label
%define bsBytesPerSec   bp+0x0b      ; bytes/sector
%define bsSecPerClust   bp+0x0d      ; sectors/allocation unit
%define bsResSectors    bp+0x0e      ; # reserved sectors
%define bsFATs          bp+0x10      ; # of fats
%define bsRootDirEnts   bp+0x11      ; # of root dir entries
%define bsSectors       bp+0x13      ; # sectors total in image
%define bsMedia         bp+0x15      ; media descrip: fd=2side9sec, etc...
%define sectPerFat      bp+0x16      ; # sectors in a fat
%define sectPerTrack    bp+0x18      ; # sectors/track
%define nHeads          bp+0x1a      ; # heads
%define nHidden         bp+0x1c      ; # hidden sectors
%define nSectorHuge     bp+0x20      ; # sectors if > 65536
%define drive           bp+0x24      ; drive number
			bp+0x25      ; partition number for GRLDR
%define extBoot         bp+0x26      ; extended boot signature
%define volid           bp+0x27
%define vollabel        bp+0x2b
%define filesys         bp+0x36

%define RootDirSecs     bp+0x26         ; # of sectors root dir uses
					; (overwriting unused bytes)
%define fat_start       bp+0x28         ; first FAT sector
					; (overwriting unused bytes)
%define root_dir_start  bp+0x2c         ; first root directory sector
					; (overwriting unused bytes)
%define data_start      bp+0x30         ; first data sector
					; (overwriting unused bytes)
%define data_clusters   bp+0x34         ; # of clusters in data area
					; (overwriting unused bytes)
			bp+0x36		; bytes per FAT( > 0x1800 means FAT16)
					; (overwriting unused bytes)
*/
		/* not used: [0x26] = byte 0x29 (ext boot param flag)
		 * [0x27] = dword serial
		 * [0x2b] = label (padded with 00, 11 bytes)
		 * [0x36] = "FAT12" or "FAT16",32,32,32 (not used by Windows)
		 * ([0x3e] is where FreeDOS parts start)
		 */

	. = Entry_12_16 + 0x3e
1:
	cli
	cld

#ifdef	BOOTGRUB

	. = Entry_12_16 + 0x40

	/* the byte at offset 0x41 stores the real partition number for read.
	 * the format program or the caller should set it to a correct value.
	 * For floppies, it should be 0xff, which stands for whole drive.
	 */

	movb	$0xff, %dh	/* boot partition number */

	cmpb	$0xff, %dh	/* is floppy? */
	jne	1f
	movb	$0, %dl		/* yes, let drive number = 0 */
1:
#endif

	xorw	%ax, %ax
	movw	$0x7c00, %bp

#ifdef	BOOTGRUB

	movw	%ax, %ss	/* stack and BP-relative moves up, too */
	leaw	-0x20(%bp), %sp

	sti			/* after stack setup, we can use stack */

	movw	%dx, 0x24(%bp)	/* BIOS passes drive number in DL */

	pushaw			/* AX=0 */

	movb	$0x41, %ah
	movw	$0x55AA, %bx
	pushw	%dx
	int	$0x13
	popw	%dx
	pushw	%ss		/* SS=0 */
	popw	%ds		/* DS=0 */

	jc	1f		/* No EBIOS */
	cmpw	$0xAA55, %bx
	jne	1f		/* No EBIOS */
	testb	$1, %cl
	jz	1f		/* No EBIOS */
	testb	%dl, %dl	/* floppy? */
	jns	1f		/* yes, only use CHS for FAT12/16 on floppy. */
	/* EBIOS supported */
	movb	$0x42, (ebios_12_16 - 1 - Entry_12_16 + 0x7c00)
1:
	popaw			/* AX=0 */

	movw	%ax, %es	/* ES=0 */

	/* AX=SS=DS=ES=0, BP=0x7C00 */

#else
	movw	%ax, %ds
	movw	%bp, %si	/* move from 0000:7c00 */
	movw	%bp, %di	/* move to 1fe0:7c00 */
	movb	%dl, 0x24(%si)	/* BIOS passes drive number in DL */
//	xchgw	%ax, %dx	/* let DX = 0 */
	movw	$0x1fe0, %ax
	movw	%ax, %es
	movw	$0x0100, %cx	/* one sector to move */
	repz movsw
				/* CX = 0 */
	ljmp	$0x1fe0, $(1f - Entry_12_16 + 0x7c00)
1:
	movw	%ax, %ss	/* stack and BP-relative moves up, too */
	leaw	-0x20(%bp), %sp

	sti			/* after stack setup, we can use stack */

	pushw	%ax		/* AX=0x1FE0 */
	movb	$0x41, %ah
	movw	$0x55AA, %bx
	int	$0x13
	popw	%ds		/* DS=0x1FE0 */

	jc	1f		/* No EBIOS */
	cmpw	$0xAA55, %bx
	jne	1f		/* No EBIOS */
	testb	$1, %cl
	jz	1f		/* No EBIOS */
	/* EBIOS supported */
	movb	$0x42, (ebios_12_16 - 1 - Entry_12_16 + 0x7c00)
1:
	xorw	%ax, %ax	/* AX=0 */

#endif

	/* GET DRIVE PARMS: Calculate start of some disk areas */
1:
#if 0
	.arch	i486, nojumps

	movzwl	0x0e(%bp), %ebx	/* reserved sectors */
	addl	0x1c(%bp), %ebx	/* hidden sectors */
	movl	%ebx, 0x28(%bp)	/* ---- FAT start */

	movzbl	0x10(%bp), %eax	/* number of FATs */
	movzwl	0x16(%bp), %ecx	/* sectors per FAT */
	mull	%ecx		/* EDX=0, EAX=total sectors for FAT */
	addl	%eax, %ebx
	movl	%ebx, 0x2c(%bp)	/* ---- RootDir start */

	/* Calculate how many sectors the root directory occupies */

	movzwl	0x0b(%bp), %ecx	/* bytes per sector, should be 512 */

	movzwl	0x11(%bp), %eax	/* max number of RootDir entries */
	shll	$5, %eax	/* total bytes RootDir occupies */
	addl	%ecx, %eax
	decl	%eax
	/* xorl	%edx, %edx */	/* EDX=0 */
	divl	%ecx		/* EAX=AX=sectors for RootDir */

	movw	%ax, 0x26(%bp)	/* sectors for RootDir */

	addl	%eax, %ebx
	movl	%ebx, 0x30(%bp)	/* ---- DataArea start */

	. = . - (. - 1b)/66

	.arch	i186, nojumps
#else
	movw	0x1c(%bp), %si	/* number of hidden sectors(lo) */
	movw	0x1e(%bp), %di	/* number of hidden sectors(hi) */
	addw	0x0e(%bp), %si	/* number of reserved sectors */
	adcw	%ax, %di	/* DI:SI = first FAT sector */
				/* AX = 0 */

	movw	%si, 0x28(%bp)	/* FAT start sector(lo) */
	movw	%di, 0x2a(%bp)	/* FAT start sector(hi) */

	//xchgw	%ax, %dx	/* let AX = 0 */
	movb	0x10(%bp), %al	/* number of FATs */
	/* cbw */
	mulw	0x16(%bp)	/* sectors per FAT */
				/* DX:AX = total number of FAT sectors */
				/* DX = 0 since no too many FAT sectors */
	addw	%ax, %si
	adcw	%dx, %di	/* DI:SI = root directory start sector */
	movw	%si, 0x2c(%bp)	/* root directory starting sector(lo) */
	movw	%di, 0x2e(%bp)	/* root directory starting sector(hi) */

	/* Calculate how many sectors the root directory occupies */

	movw	0x0b(%bp), %bx	/* bytes per sector */
	movb	$5, %cl		/* divide BX by 32 */
	shrw	%cl, %bx	/* BX = directory entries per sector */

	movw	0x11(%bp), %ax	/* max number of root dir entries */
	addw	%bx, %ax
	decw	%ax
	/* xorw	%dx, %dx */	/* assuming DX = 0 */
	divw	%bx		/* AX = sectors per root directory */
	cwd			/* DX = 0 */

	movw	%ax, 0x26(%bp)	/* number of sectors the root dir occupies */

	addw	%ax, %si	/* DI:SI = first data sector */
	adcw	%dx, %di	/* assuming DX = 0 */

	movw	%si, 0x30(%bp)	/* data starting sector(lo) */
	movw	%di, 0x32(%bp)	/* data starting sector(hi) */

	. = . - (. - 1b)/63

#endif


#ifdef USE_TOTAL_CLUSTERS
	movw	0x13(%bp), %cx	/* total sectors(small) */
	jcxz	1f
	movw	%cx, 0x20(%bp)	/* total sectors(large)(lo) */
	movw	%dx, 0x22(%bp)	/* total sectors(large)(hi), assuming DX = 0 */
1:	
	movw	0x20(%bp), %ax	/* total sectors(large) */
	movw	0x22(%bp), %bx
	addw	0x1c(%bp), %ax	/* number of hidden sectors */
	adcw	0x1e(%bp), %bx
	subw	%si, %ax	/* data starting sector */
	sbbw	%di, %bx	/* BX:AX = total sectors in the data area */
	movb	0x0d(%bp), %dl	/* sectors per cluster(DH=0) */
	xchgw	%bx, %dx	/* DX:AX = total sectors in the data area */
				/* BX = sectors per cluster */
	divw	%bx		/* AX = total clusters in the data area */
	movw	%ax, 0x34(%bp)	/* total clusters in the data area */
#else
	movw	$0xffff, 0x36(%bp)	/* bytes per FAT( > 0x1800 means FAT16) */
	movw	0x16(%bp), %ax	/* sectors per FAT */
	mulw	0x0b(%bp)	/* bytes per sector */
	jc	1f
	movw	%ax, 0x36(%bp)
1:
#endif
	/* Searches for the file in the root directory
	 *
	 * Returns:
	 *	AX = first cluster of file
	 */

	/* First, read the whole root directory into the temporary buffer */

	movw	0x2c(%bp), %ax	/* root directory starting sector(lo) */
	movw	0x2e(%bp), %dx	/* root directory starting sector(hi) */
	movw	0x26(%bp), %cx	/* number of sectors the root dir occupies */
	lesw	(loadseg_off_12_16 - Entry_12_16)(%bp), %bx
				/* ES:BX = loadseg:0 */

//	pushw	%es
	call	readDisk_12_16	/* CX=0, AX,DX,ES changed */
//	popw	%es

	lesw	(loadseg_off_12_16 - Entry_12_16)(%bp), %di
				/* ES:DI = loadseg:0 */


	/* Search for kernel file name, and find start cluster */

	/* BX=0, CX=0 */

//	pushw	%cx
//	popw	%di

1:
	movw	$(filename_12_16 - Entry_12_16 + 0x7c00), %si	/* filename */

	movb	$11, %cl	/* length of kernel filename */

	pushw	%di
	repz cmpsb
	popw	%di

	jz	1f

	addw	$0x20, %di	/* next entry */
	jz	2f		/* or jc 2f, exceeding 64K */

	/* if the entry begins in 0, this also ends the dir. */

	cmpb	%ch, %es:(%di)	/* CH=0 */
	jnz	1b
2:
	movw	$(msg_BootError_12_16 - Entry_12_16 + 0x7c00), %si
	jmp	boot_error_12_16	/* fail if not found */

#ifndef ALTERNATIVE_KERNEL
loadseg_off_12_16:	.word	0
loadseg_seg_12_16:	.word	LOADSEG_12_16
#endif

1:

/****************************************************************************/

	/* BX=0, CX=0 */

	######################################################################
	# Reads the FAT chain and stores it in a temporary buffer in the
	# first 64KB.  The FAT chain is stored an array of 16-bit cluster
	# numbers, ending with 0.
	#
	# The file must fit in conventional memory, so it can't be larger
	# than 640KB. The sector size must be at least 512 bytes, so the
	# FAT chain can't be larger than around 3KB.
	######################################################################

	/********************************************************************/
	/* First, load the complete FAT into memory. The FAT can't be       */
	/* larger than 128KB, so it should fit in the temporary buffer.     */
	/********************************************************************/

	pushw	%es:0x1a(%di)	/* save first cluster number of file */

//	lesw	(loadseg_off_12_16 - Entry_12_16)(%bp), %bx
//				/* ES:BX = loadseg:0 */
	movw	0x16(%bp), %cx	/* sectors per FAT */
	movw	0x28(%bp), %ax	/* FAT start sector(lo) */
	movw	0x2a(%bp), %dx	/* FAT start sector(hi) */

	pushw	%es		/* ES=0x2000 */
	call	readDisk_12_16	/* CX=0, AX,DX,ES changed */
	popw	%ds		/* DS=0x2000 */

	popw	%ax		/* restore first cluster number of file */

	/********************************************************************/
	/* Then, extract the clusters of the file from the FAT              */
	/********************************************************************/

	/* Set ES:DI to the temporary storage for the FAT chain */

	pushw	%ds		/* ES=0x2000 */

	pushw	%ss
	popw	%es
	movw	$FATBUF, %di

	/* BX=0, CX=0 */
2:
	stosw			/* store cluster number */
	movw	%ax, %si	/* SI = cluster number */

	//////////////////////////////////////////////////////////////
	//
	// FAT16 can occupy 128KB, so the segment must be adjusted
	//
	//////////////////////////////////////////////////////////////

	popw	%dx		/* DX=0x2000, segment for FAT16 */
	pushw	%dx
	addw	%si, %si	/* multiply cluster number by two */
	jnc	1f
	addb	$0x10, %dh	/* overflow. Add 0x1000 to segment value */
1:

#ifdef USE_TOTAL_CLUSTERS
	cmpw	$0x0ff7, 0x34(%bp)	/* total clusters in the data area */
#else
	cmpw	$0x1801, 0x36(%bp)	/* bytes per FAT */
#endif
	jnb	3f

	/******** FAT12 ********/

	addw	%ax, %si	/* multiply cluster number by 3 ... */
	shrw	$1, %si		/* ... and divide by 2 */
	lodsw

	/* If the cluster number was even, the cluster value is now in
	 * bits 0-11 of AX. If the cluster number was odd, the cluster
	 * value is in bits 4-15, and must be shifted right 4 bits. If
	 * the number was odd, CF was set in the last shift instruction.
	 */

	jnc	1f
	movb	$4, %cl		/* CL=4 */
	shrw	%cl, %ax
1:
	andb	$0x0f, %ah	/* mask off the highest 4 bits */
	cmpw	$0x0ff7, %ax	/* check for EOF */
	jmp	4f

3:
	/******** FAT16 ********/

	movw	%dx, %ds	/* DS:SI points to next cluster */
	lodsw			/* AX = next cluster */

	cmpw	$0xfff7, %ax	/* check for EOF */
4:
	jbe	2b		/* continue if not EOF */

	/* Mark end of FAT chain with 0, so we have a single
	 * EOF marker for both FAT12 and FAT16 systems.
	 */

	xorw	%ax, %ax
	stosw

/****************************************************************************/

	/* Load the file into memory, one cluster at a time */

	popw	%es		/* ES=0x2000 */
//	lesw	(loadseg_off_12_16 - Entry_12_16)(%bp), %bx
//				/* ES:BX = loadseg:0 */
	pushw	%ss
	popw	%ds		/* DS=SS */
	movw	$FATBUF, %si	/* set DS:SI to the FAT chain */

1:
	/* CH=0 */

	lodsw			/* AX = next cluster to read */
	subw	$2, %ax		/* cluster numbers start with 2 */
	jc	1f		/* the cluster should be 0 for EOC */

	movb	0x0d(%bp), %cl	/* CH=0, CX=sectors per cluster */
	mulw	%cx
	addw	0x30(%bp), %ax	/* data starting sector(lo) */
	adcw	0x32(%bp), %dx	/* data starting sector(hi) */
				/* DX:AX = first sector to read */

	call	readDisk_12_16	/* CX=0, AX,DX,ES changed */

	jmp	1b		/* read next cluster */

1:
	/* EOC encountered - done */
#ifdef	BOOTGRUB
	movw	0x24(%bp), %dx	/* boot_drive and boot_partition */
#else
	movb	0x24(%bp), %bl	/* FreeDOS kernel uses BL, not DL, for drive */
#endif
	ljmp	*(loadseg_off_12_16 - Entry_12_16)(%bp)	/* boot it! */

/****************************************************************************/

/* Read a number of sectors into memory.
 *
 * Call with:	DS=SS
 *		DX:AX = 32-bit DOS sector number
 *		   CX = number of sectors to read
 * 		ES:BX = destination buffer
 *
 * Returns:	CX=0
 *		ES increased, BX untouched
 *		ES:BX points one byte after the last byte read.
 * 		DX:AX = next sector number after read
 *		All other registers preserved
 */
 
readDisk_12_16:
2:
	pushfw
	pushaw
	xorw	%cx, %cx
	pushw	%cx		/* hi word of hi dword */
	pushw	%cx		/* lo word of hi dword */
	pushw	%dx		/* hi word of lo dword */
	pushw	%ax		/* lo word of lo dword */
	pushw	%es		/* buffer segment */
	pushw	%bx		/* buffer offset */
	incw	%cx
	pushw	%cx		/* 1 sector to read */
	movb	$16, %cl
	pushw	%cx		/* size of this parameter block */

	xchgw	%ax, %cx	/* save AX to CX */

	/*
	 * translate sector number to BIOS parameters
	 *
	 * LBA = sector-1			offset in track
	 *     + head * sectPerTrack		offset in cylinder
	 *     + cyl * sectPerTrack * nHeads	offset in platter
	 *
	 */
#if 1
	pushw	%bx

	pushw	%dx
	movw	0x18(%bp), %ax	/* sectors per track */
	movw	%ax, %bx
	mulw	0x1a(%bp)	/* nHeads */
				/* DX=0, AX=sectors per cylinder */
	xchgw	%ax, %cx	/* restore AX from CX, and save AX to CX */
				/* CX=nHeads * sectPerTrack <= 256*63 */
				/* AX=LBA lo word */
	popw	%dx		/* DX:AX=LBA */

#else

	pushw	%bx
	movw	0x18(%bp), %ax	/* sectors per track */
	movw	%ax, %bx
	mulb	0x1a(%bp)	/* nHeads, but maybe a word value 0x100 */
	jnz	1f
	movb	%bl, %ah	/* nHeads=0x100, so AX=sectPerTrack*0x100 */
1:
	xchgw	%ax, %cx	/* restore AX from CX, and save AX to CX */
		/* DX:AX = LBA, CX = nHeads * sectPerTrack <= 256*63 */
#endif

	divw	%cx	 /* AX = cyl, DX = sector-1 + head * sectPerTrack */
	xchgw	%ax, %dx /* DX = cyl, AX = sector-1 + head * sectPerTrack */
	divb	%bl	/* sectors per track */
			 /* DX = cyl, AL = head, AH = sector-1 */
#if 1
	xchgb	%al, %ah /* DX = cyl, AH = head, AL = sector-1 */
	incw	%ax	 /* DX = cyl, AH = head, AL = sector */
	xchgw	%ax, %dx /* AX = cyl, DH = head, DL = sector */
	xchgw	%ax, %cx /* CX = cyl, DH = head, DL = sector */
	xchgb	%cl, %ch	/* set cyl number low 8 bits in CH */
	rorb	$1, %cl		/* move cyl high bits into bits 7-6 */
	rorb	$1, %cl		/*	(assumes top = 0)             */
	orb	%dl, %cl	/* merge sector into cylinder */
#else
	movw	%dx, %cx /* CX = cyl, AL = head, AH = sector-1 */

	/*
	 * the following manipulations are necessary in order to properly place
	 * parameters into registers.
	 * CH = cylinder number low 8 bits
	 * CL<7-6> = cylinder high two bits
	 * CL<5-0> = sector
	 */
	movb	%al, %dh	/* save head into DH for BIOS */
	xchgb	%cl, %ch	/* set cyl number low 8 bits in CH */
	rorb	$1, %cl		/* move cyl high bits into bits 7-6 */
	rorb	$1, %cl		/*	(assumes top = 0)	*/
	incb	%ah		/* AH = sector number */
	orb	%ah, %cl	/* merge sector into cylinder */
#endif
	popw	%bx
	
	movw	$0x0201, %ax	/* read 1 sector */
ebios_12_16: /* ebios_12_16 - 1 points to 0x02 that can be changed to 0x42 */

	movw	%sp, %si	/* DS:SI points to disk address packet */
	movb	0x24(%bp), %dl	/* drive number */

	pushw	%es
	pushw	%ds
	int	$0x13
	popw	%ds

jc_code_begin:
	jc	disk_error_12_16	/* caller could change it to NOPs */
jc_code_end:

	/* increment ES */
	popw	%bx		/* old ES on stack */
	leaw	0x20(%bx), %bx	/* LEA does not touch flags */
	movw	%bx, %es

	popaw			/* remove parameter block from stack */
	popaw
	popfw			/* restore IF, DF */
	incw 	%ax		/* next sector */
	jnz	1f
	incw	%dx
1:
	loop	2b

	ret

//	. = . - (. - readDisk_12_16)/99

msg_DiskReadError_12_16:

	.ascii	"disk error\0"

msg_BootError_12_16:

	.ascii	"No "

filename_12_16:

#ifdef	BOOTGRUB
	.ascii	"GRLDR      \0"
#else
	.ascii	"KERNEL  SYS\0"
#endif

#ifdef ALTERNATIVE_KERNEL
filename_end_12_16:

	. = Entry_12_16 + 0x1e8

loadseg_off_12_16:	.word	0
loadseg_seg_12_16:	.word	LOADSEG_12_16

	. = Entry_12_16 + 0x1ec

boot_image_ofs_12_16:

	.word (filename_12_16 - Entry_12_16)+(filename_end_12_16 - filename_12_16 - 1)*2048
#endif

	. = Entry_12_16 + 0x1ee

disk_error_12_16:

	movw	$(msg_DiskReadError_12_16 - Entry_12_16 + 0x7c00), %si

boot_error_12_16:

/* prints string DS:SI (modifies AX BX SI) */

//print_12_16:
1:
	lodsb	(%si), %al	/* get token */
	//xorw	%bx, %bx	/* video page 0 */
	movb	$0x0e, %ah	/* print it */
	int	$0x10		/* via TTY mode */
	cmpb	$0, %al		/* end of string? */
	jne	1b		/* until done */

	/* The caller will change this to
	 *	ljmp	$0x9400, $(try_next_partition - _start1)
	 */

1:	jmp	1b

	. = Entry_12_16 + 0x1fc

	.word	0, 0xAA55 /* Win9x uses all 4 bytes as magic value here */

	. = Entry_12_16 + 0x200

	. = _start1 + 0x800




	.arch	i486, nojumps

/*
 #; Ext2 boot sector for GRLDR
 */


#define	DEBUG	call	debug_print
#undef DEBUG

	//. = _start1 + 0x800

Entry_ext2:

	jmp     1f

	. = Entry_ext2 + 0x02

	/* The default mode is CHS. This is for maximum compatiblity with
	 * small-sized disks, e.g., floppies.
	 *
	 * Valid values are 0x02 for CHS mode, or 0x42 for LBA mode.
	 *
	 * If the BIOS int13 supports LBA, this byte can be safely set to 0x42.
	 *
	 * Some USB BIOSes might have bugs when using CHS mode, so the format
	 * program should set this byte to 0x42. It seems that (generally) all
	 * USB BIOSes have LBA support.
	 *
	 * If the format program does not know whether the BIOS has LBA
	 * support, it may operate this way:
	 *
	 * if (partition_start + total_sectors_in_partition) exceeds the CHS
	 * addressing ability(especially when it is greater than 1024*256*63),
	 * the caller should set this byte to 0x42, otherwise, set to 0x02.
	 */

	.byte	0x02	/* for CHS. Another possible value is 0x42 for LBA */

	. = Entry_ext2 + 0x03

#if 0

	.ascii	"ext2 grldr"

#else

msg_DiskReadError_ext2:

	.ascii	"I/O error\0"

#endif

	. = Entry_ext2 + 0x0d

	/* sectors per block. Valid values are 2, 4, 8, 16, 32.	 */

	.byte	2

	. = Entry_ext2 + 0x0e

	/* bytes per block.
	 * Valid values are 0x400, 0x800, 0x1000, 0x2000, 0x4000.
	 */

	.word	1024		/* bytes per block, at most 16K */

	. = Entry_ext2 + 0x10

	/* pointers in pointers-per-block blocks, that is, number of blocks
	 * covered by a double-indirect block.
	 * Valid values are 0x10000, 0x40000, 0x100000, 0x400000, 0x1000000.
	 */

	.long	0x10000	/* number of blocks covered by double-indirect block */
			/* low word=0 */

	. = Entry_ext2 + 0x14

	/* pointers per block, that is, number of blocks covered by an indirect
	 * block. Valid values are 0x100, 0x200, 0x400, 0x800, 0x1000.
	 */

	.long	0x100		/* high word=0, low byte=0 */

	. = Entry_ext2 + 0x18

	/* this is default for 1.44M floppy, the caller should set it to 
	 * a correct value */

	.word	18	/* sectors per track */

	. = Entry_ext2 + 0x1a

	/* this is default for 1.44M floppy, the caller should set it to 
	 * a correct value */

	.word	2	/* number of heads */

	. = Entry_ext2 + 0x1c

	/* this is default for 1.44M floppy, the caller should set it to 
	 * a correct value */

	.long	0		/* hidden sectors */

	. = Entry_ext2 + 0x20

	/* total sectors in the filesystem(or in the partition).
	 * This value is informative. The code does not use it.
	 */

	/* this is default for 1.44M floppy, the caller should set it to 
	 * a correct value */

	.long	2880

	. = Entry_ext2 + 0x24

	/* This byte is ignored for read. The program will write DL onto
	 * this byte. The caller should set drive number in DL. 
	 * We assume all BIOSes pass correct drive number in DL.
	 * That is to say, buggy BIOSes are not supported!!
	 */

	.byte	0		/* drive number */

	. = Entry_ext2 + 0x25

	/* this is default for floppies, the caller should set it to 
	 * a correct value for hard-drive partitions */

	.byte	0xff		/* partition number, 0xff for whole drive */

	. = Entry_ext2 + 0x26

	.word	0x80		/* inode size */

	. = Entry_ext2 + 0x28

	/* this is default for 1.44M floppy, the caller should set it to 
	 * a correct value */

	.long	2048		/* s_inodes_per_group */

	. = Entry_ext2 + 0x2c

	/* block number for group descriptors = s_first_data_block + 1.
	 * Valid values are 2 for 1024-byte blocks, and 1 for otherwise.
	 */

	/* this is default for 1.44M floppy, the caller should set it to 
	 * a correct value */

	.long	2		/* block number for group descriptors */

	. = Entry_ext2 + 0x30
1:
	cld			/* 0xFC */

	xorw	%ax, %ax	/* 0x31, 0xC0; CF=0, ZF=1 */

	/* this byte `nop' will be changed to `cwd' by bootlace for floppy */
	nop			/* 0x90=nop, 0x99=cwd */
				/* cwd will set DL=0 forcibly for floppy A: */

	movw	%ax, %ss	/* constant SS=0 */
	movw	$0x7c00, %sp

	movw	%sp, %bp	/* constant BP=0x7c00 */

	pushw	%ax		/* 0x0000 at 0000:7bfe */
	movw	$0x1000, %bx
	pushw	%bx		/* 0x1000 at 0000:7bfc */
	pushw	%ax		/* 0x0000 at 0000:7bfa */
				/* SP=0x7bfa */

	/* the 6 bytes in the stack are used by read_block():
	 *	0000	----	-2(%bp)
	 *	1000	----	-4(%bp)
	 *	0000	----	-6(%bp)
	 * Don't touch them!
	 */

	movb	%dl, 0x24(%bp)	/* BIOS passes drive number in DL */

	pushw	%ss
	movb	$0x41, %ah
	movw	$0x55AA, %bx
	int	$0x13
	popw	%ds		/* constant DS=0 */
	jc	1f		#; No EBIOS

	//testb	$1, %cl
	//jz	1f		#; No EBIOS
#if 0
	/* gcc-4.0.1 does not generate 2-byte code. */
	rcrb	$1, %cl		#; also can be rorb $1, %cl
#else
	.byte	0xD0, 0xD9	#; ror cl: D0 C9
#endif
	jnc	1f		#; No EBIOS

	movb	$0x42, (ebios_ext2 - 1 - Entry_ext2 + 0x7c00)
1:
	xorl	%eax, %eax	/* CF=0, ZF=1 */

#if 0
	/* the INC touches ZF flag, so use MOV instead */

	incw	%ax
	incw	%ax		/* EAX=2=inode number for root dir */
#else

	/* MOV keeps all flags untouched, so it is better than INC */

	movb	$2, %al		/* EAX=2=inode number for root dir */
#endif

	/* CF=0, ZF=1 because MOV and PUSH do not touch Flags */

	/* read root dir to 0000:1000, and grldr to 1000:0000 */

4:
	/* EAX holds the inode number: for root dir or grldr */

	/* These 3 PUSHes is intended to place 1000:0000 onto the stack for
	 * grldr. For root dir, the stack is not used since CF is cleared.
	 * Although there is no corresponding POPs, this is safe enough
	 * because the program comes here only twice: the first is for
	 * the root dir, and the second is for grldr.
	 *
	 * For root dir, CF=0 and ZF=1. For grldr, CF=1.
	 */

	pushw	%di		/* 0x1000, see "jz 4b" below. */
	pushw	%ss		/* 0x0000 */
	pushfw

	/* SP=0x7bf4 for root dir, or 0x7bee for grldr */

	decl	%eax		/* EAX=(inode - 1) */

	/* inode numbers are far less than 0x7fffffff, so it is safe to
	 * initialise EDX with CDQ */

	cdq			/* let EDX=0 */

	divl	0x28(%bp)	/* s_inodes_per_group */
				/* EAX=group number */
	pushl	%edx		/* EDX=inode number in the group */

	/* group numbers are far less than 0x7fffffff, so it is safe to
	 * initialise EDX with CDQ */

	cdq			/* let EDX=0 */
	shll	$5, %eax	/* EAX=relative displacement of the group descriptor */
	divl	0x0e(%bp)	/* bytes per block */
				/* EAX=relative block number for the group descriptor */
				/* DX=displacement in the block */
				/* EDX high=0 */

	pushw	%dx		/* we don't care about EDX high word, because it is 0 */

	addl	0x2c(%bp), %eax	/* EAX=absolute block number for the group descriptor */
				/* CF=0, ZF=0 */

	call	read_block	/* 0000:1000 points to the block data containing the group descriptor */
				/* ES changed and > 0, BX=0x1000 */
				/* ECX=EDX=0 */
				/* CF=0, ZF=0 */

	popw	%si		/* DS:[BX+SI] points to the group descriptor */
				/* DS:[BX+SI+8] points to the starting block number of the group inode table */

	popl	%eax		/* inode number in the group */
//	shll	$7, %eax	/* inode struct size = 0x80 */
//				/* EAX=relative displacement of the inode struct */
//				/* EDX=0 */
	movw	0x26(%bp), %dx	/* EDX=inode size */
	mull	%edx		/* EDX:EAX=relative displacement of the inode struct */

	divl	0x0e(%bp)	/* bytes per block */
				/* EAX=relative block number for the inode struct */
	pushw	%dx		/* DX=displacement of the inode struct in the block */
				/* EDX high=0 */

	addl	8(%bx, %si), %eax	/* EAX=absolute block number for the inode struct */
					/* CF=0, ZF=0 */

	call	read_block	/* 0000:1000 points to the block data containing the inode struct */
				/* ES changed and > 0, BX=0x1000 */
				/* ECX=EDX=0 */
				/* CF=0, ZF=0 */

	popw	%si		/* DS:[BX+SI] points to the inode struct */

	addw	%bx, %si	/* DS:SI points to the inode struct */

	/* Move the inode struct to a known safe area(0000:0fa8 - 0000:0fff),
	 * that is, 0x58 bytes immediately before 0000:1000. We care about only
	 * the beginning 0x58 bytes of the 0x80-byte inode struct, the last
	 * 0x28 bytes are ignored. The area from 0xfa8+0x28 to 0xfa8+0x57
	 * stores 12 direct block pointers.
	 *  
	 *  
	 * At address   Initial value               Stores what?
	 * ==========   =============   ======================================
	 * 0xfa8+0x04      (const)           the size of the file in bytes
	 * 
	 * 0xfa8+0x08    total blocks           blocks left to read
	 * 
	 * 0xfa8+0x0c         0           serial number of the block to read
	 * 
	 */

	pushw	%ss
	popw	%es				/* ES=0 */

	leaw	-0x58(%bx), %di			/* BX=0x1000, so DI=0x0fa8 */
	//movw	$0x0fa8, %di
	movb	$0x2c, %cl			/* 0x2c words = 0x58 bytes */

	repz movsw				/* now ECX=0, BX=0x1000=DI */

	movl	%ecx, (0x0c - 0x58)(%di)	/* block serial number of the file */
						/* ECX=0 means first block */
						/* DI=0x1000 */

	movl	(0x04 - 0x58)(%di), %eax	/* i_size, the file size */
	decl	%eax

	divl	0x0e(%bp)			/* bytes per block */
						/* EDX=various */
	incl	%eax
	movl	%eax, (0x08 - 0x58)(%di)	/* total blocks for file data */

	/*
	 * 0000:1000	trebly indirect block
	 * 0000:8000	indirect block
	 * 0000:c000	double indirect block
	 * 1000:0000	the file data
	 */

	/* now DS:SI points to indirect block number */

	lodsl					/* indirect block number */
	testl	%eax, %eax
	jz	1f

	//pushw	%ss
	//popw	%es				/* ES=0 */
	movb	$0x80, %bh			/* ES:BX=0000:8000 */
#if 0
	stc
	call	read_block
#else
	call	read_block_c
#endif
						/* ES changed and > 0, BX=0x8000 */
						/* ECX=EDX=0 */
						/* ZF=0, CF=0 */

	/* now DS:SI points to double indirect block number */

	lodsl					/* double indirect block number */
	testl	%eax, %eax
	jz	1f

#if 0
	pushw	%ss
	popw	%es				/* ES=0 */
	movb	$0xc0, %bh			/* ES:BX=0000:c000 */
	stc
	call	read_block
#else
	movb	$0xc0, %bh			/* ES:BX=0000:c000 */
	call	read_block_c
#endif
						/* ES changed and > 0, BX=0xc000 */
						/* ECX=EDX=0 */
						/* ZF=0, CF=0 */
	
	/* now DS:SI points to trebly indirect block number */

	lodsl					/* trebly indirect block number */
	testl	%eax, %eax			/* CF=0, TEST always clears CF */
	jz	1f
						/* ZF=0 */
	//pushw	%ss
	//popw	%es				/* ES=0 */
	//movb	$0x10, %bh			/* ES:BX=0000:1000 */
	//stc
	call	read_block			/* 0000:1000 points to the block data */
						/* ES changed and > 0, BX=0x1000 */
						/* ECX=EDX=0 */
						/* ZF=0, CF=0 */

	/* the block at 0000:1000, which contains the indirect block numbers,
	 * is just overwritten by the trebly indirect block */
	
1:
	/* get absolute block number by block serial number */

	movl	(0x0c - 0x58)(%di), %ebx	/* block serial number of the file */
	subl	$12, %ebx
	jc	3f				/* direct block: block serial number < 12 */

	pushw	%bx
	subl	0x14(%bp), %ebx
	popw	%ax
	jnc	2f

	/* indirect block: 12 <= block serial number < 12 + 0x14(%bp) */

	//addw	0x14(%bp), %bx
	addb	$(0x70 / 4), %ah
	//xchgw	%ax, %bx
	jmp	8f

2:
	pushl	%ebx
	subl	0x10(%bp), %ebx
	jc	7f	/* EBX on the stack is < 0x10(%bp). double indirect block: */
			/* 12 + 0x14(%bp) <= block serial number < 12 + 0x14(%bp) + 0x10(%bp) */

	/* trebly indirect block: block serial number >= 12 + 0x14(%bp) + 0x10(%bp) */

	popl	%eax		/* discard the stack */
	xchgl	%eax, %ebx	/* move EBX to EAX */
				/* EDX=0 */
	divl	0x10(%bp)
				/* EAX=indirect block number, < 0x14(%bp) */
				/* EDX=block number, < 0x10(%bp) */

	pushl	%edx		/* EDX < 0x10(%bp) */
	testl	%edx, %edx
	jnz	7f

	/* EDX=0, so we need to load the double indirect block */

	shlw	$2, %ax
	xchgw	%ax, %bx

	/* get the double indirect block number from the trebly indirect
	 * block data */

	movl	(%bx, %di), %eax

//6:
	movw	$0xc000, %bx			/* ES:BX=0000:c000 */

	//pushw	%ss
	//popw	%es				/* ES=0 */
	//stc
	call	read_block_c	/* 0000:c000 points to the block data */
				/* ES changed and > 0, BX=0xc000 */
				/* ECX=EDX=0 */
				/* CF=0, ZF=0 */
7:
	popl	%eax		/* EAX < 0x10(%bp) */
	cdq			/* let EDX=0 (notice the above jc 7f and jnz 7f) */
	divl	0x14(%bp)
				/* EAX=indirect block number, < 0x14(%bp) */
				/* EDX=block number, < 0x14(%bp) */

	pushw	%dx		/* EDX < 0x14(%bp) */
	testw	%dx, %dx
	jnz	7f

	/* if DX=0, we need to load the indirect block */

	//addb	$(0xb0 / 4), %ah
	shlw	$2, %ax
	xchgw	%ax, %bx

	/* get the indirect block number from the double indirect block data */

	movl	0xb000(%bx, %di), %eax
	//movl	(%bx, %di), %eax
//5:
	movw	$0x8000, %bx			/* ES:BX=0000:8000 */

	//pushw	%ss
	//popw	%es				/* ES=0 */
	//stc
	call	read_block_c	/* 0000:8000 points to the block data */
				/* ES changed and > 0, BX=0x8000 */
				/* ECX=EDX=0 */
				/* CF=0, ZF=0 */
7:
	popw	%ax		/* AX < 0x14(%bp) */
8:
	xchgw	%ax, %bx
3:
	shlw	$2, %bx
	movl	(%bx, %di), %eax

	/* got it! EAX=absolute block number */

	/* read block data to 1000:0000. For root dir, read each block to
	 * 1000:0000(overwrite the previous read). For grldr, read blocks
	 * one by one to the area starting at 1000:0000. 
	 */

	popfw
	popw	%bx
	popw	%es
	pushfw

	/* CF=0 and ZF=1 for reading root dir, CF=1 for reading grldr */

	call	read_block	/* 1000:0000 points to the block data */
				/* ES changed and > 0x1000, BX=0 */
				/* ECX=EDX=0 */
				/* CF=0, ZF=0 */

	popfw
	pushw	%es
	pushw	%bx
	pushfw

	jc	3f		/* CF=1, we are reading grldr */

	/* We have just read a block of the root dir to 1000:0000. 
	 * So we check all dir entries in the block to see if anyone
	 * matches grldr.
	 */

	xorw	%si, %si
	pushw	%ss
	popw	%es		/* ES=0 */

2:
	pushw	%ds		/* DS=0 */
	movw	%di, %ds	/* DS=0x1000 */
	movw	$(filename_ext2 - Entry_ext2 + 0x7c00), %di

	pushw	%si
	lodsl			/* This is possible inode number for grldr */
	pushl	%eax		/* This is possible inode number for grldr */
	lodsw
	xchgw	%ax, %dx	/* rec_len */
	lodsw			/* AL=name_len, should be 5 for grldr */
				/* AH=file_type(1 for regular file) */
#if 0
	cmpw	$0x0105, %ax
	jnz	5f
	movb	%al, %cl	/* CH is already 0 */
	repz cmpsb
#else
	decb	%ah
	//jnz	5f
	xchgw	%ax, %cx	/* CX=name_len */
	repz cmpsb
	jnz	5f
	xchgw	%ax, %cx	/* movb	$0, %al */
	scasb
#endif
5:
	popl	%eax		/* This is possible inode number for grldr */
	popw	%si

	/* DS=0x1000, EAX=inode number */

	movw	%ds, %di	/* DI=0x1000 */
	popw	%ds		/* DS=0 */

	stc			/* indicates the new inode is for grldr */

	jz	4b		/* grldr is found with EAX=inode number */

	addw	%dx, %si
	cmpw	0x0e(%bp), %si	/* bytes per block */
	jb	2b

	/* file not found in this block, continue */

	/* We are lucky that CF=0, which indicates we are dealing with
	 * the root dir.
	 */

3:

	/* CF=1 for grldr, CF=0 for root dir. */

	incl	(0x0c - 0x58)(%di)
	decl	(0x08 - 0x58)(%di)
	jnz	1b

#if 0
	/* The above 2 instructions INC and DEC do not touch CF, so we
	 * can omit this POP-PUSH pair.
	 */

	popfw
	pushfw
#endif

	movw	$(msg_No_grldr_ext2 - Entry_ext2 + 0x7c00), %si

	jnc	boot_error_ext2		/* grldr not found in the root dir */

	/* All grldr blocks have been loaded to memory starting at 1000:0000,
	 * Before the boot, we pass boot_drive and boot_partition to grldr.
	 */

	/* ES>0x1000, BX=0, ECX=EDX=0, DI=0x1000, SS=0, SI>0x7c00, DS=0
	 * BP=0x7c00, SP<=0x7c00
	 */

	movw	0x24(%bp), %dx

	/* boot it now! */

	pushw	%di		/* 0x1000 */
	pushw	%ss		/* 0x0000 */
	lret

read_block_c:

	pushw	%ss
	popw	%es				/* ES=0 */
	stc
	
/* read_block - read a block
 * input:	CF	  - indicator for overlap or consecution
 *		EAX 	  = block number
 *		ES:BX	  - buffer
 *
 * output:	if CF is cleared on input, ES:BX is initialized to 0000:1000
 *		ES:BX	  - buffer filled with data
 *		ES, EAX	  - Changed
 *		ECX	  = 0
 *		EDX	  = 0
 *		ZF    = 0
 *		CF    = 0
 */

read_block:

	jc	1f

	.byte	0xC4, 0x5E, 0xFC	/* lesw -4(%bp), %bx */
					/* ES:BX=0000:1000 */
	jnz	1f

	//at this time, the gcc cannot generate 3 byte code
	.byte	0xC4, 0x5E, 0xFA	/* lesw -6(%bp), %bx */
					/* ES:BX=1000:0000 */
	//. = . - (. - read_block) / 6
1:
	movzbl	0x0d(%bp), %ecx	/* CX=sectors per block */
				/* ECX high=0 */
	. = . - (. - 1b) / 6
 	mull	%ecx		/* EAX=relative sector number */
				/* EDX=0 */
	. = . - (. - 1b) / 9
	addl	0x1c(%bp), %eax	/* EAX=absolute sector number */

#if 1
	/* pass through, saving 4 bytes(call and ret) */
#else
	call	readDisk_ext2
	ret
#endif

/* Read sectors from disk, using LBA or CHS
 * input:	EAX   = 32-bit LBA sector number
 *		CX    = number of sectors to read
 *		ECX high word  = 0
 *		ES:BX = destination buffer
 *
 * output:	No return on error
 *		BX not changed
 *		ES    = ES + 0x20 * CX
 *		EAX   = EAX + CX
 *		ZF    = 0
 *		CF    = 0
 */
 
readDisk_ext2:
2:
	pushal
	//xorl	%edx, %edx	/* EDX:EAX = LBA */
	pushl	%edx		/* hi 32bit of sector number */
	pushl	%eax		/* lo 32bit of sector number */
	pushw	%es		/* buffer segment */
	pushw	%bx		/* buffer offset */
	pushw	$1		/* 1 sector to read */
	pushw	$16		/* size of this parameter block */

	//xorl	%ecx, %ecx
	pushl	0x18(%bp)	/* lo:sectors per track, hi:number of heads */
	popw	%cx		/* ECX = sectors per track */
	divl	%ecx		/* residue is in EDX */
				/* quotient is in EAX */
				/* EDX high=0, DH=0 */
	incw	%dx		/* DL=sector number */
	popw	%cx		/* ECX = number of heads */
	pushw	%dx		/* push sector number into stack */
	xorw	%dx, %dx	/* EDX:EAX = cylinder * TotalHeads + head */
	divl	%ecx		/* residue is in EDX, head number */
				/* quotient is in EAX, cylinder number */
				/* EDX high=0, EAX high=0 */


	xchgb	%dl, %dh	/* head number should be in DH */
				/* DL = 0 */
	popw	%cx		/* pop sector number from stack */
	xchgb	%al, %ch	/* lo 8bit cylinder should be in CH */
				/* AL = 0 */
	shlb	$6, %ah		/* hi 2bit cylinder ... */
	orb	%ah, %cl	/* ... should be in CL */
	
	incw	%ax		/* AL=1, read 1 sector */

	/* Instead of 0x0e, the LBA indicator at 2(%bp) is 
	 *
	 *	0x42 for LBA
	 *
	 * and
	 *
	 *	0x02 for CHS
	 */
#if 0
	movb	$0x42, %ah
	/* ebios_ext2 - 1 points to 0x42 that can be changed to 0x02 */
#else
	movb	$0x02, %ah
	/* ebios_ext2 - 1 points to 0x02 that can be changed to 0x42 */
#endif
ebios_ext2:

	//andb	2(%bp), %ah

	movw	%sp, %si	/* DS:SI points to disk address packet */
	movb	0x24(%bp), %dl	/* drive number */
	pushw	%es
	pushw	%ds
	int	$0x13
	popw	%ds
	popw	%bx
	jc	disk_error_ext2
	leaw	0x20(%bx), %bx
	movw	%bx, %es
	popaw			/* remove parameter block from stack */
	popal
	incl 	%eax		/* next sector, here ZF=0 */
	loop	2b
	ret

	//. = . - (. - readDisk_ext2)/74

//msg_DiskReadError_ext2:
//
//	.ascii	"disk error\0"

msg_No_grldr_ext2:

	.ascii	"No "

filename_ext2:
	.ascii	"grldr\0"

	. = Entry_ext2 + 0x1ee

filename_end_ext2:

	.word (filename_ext2 - Entry_ext2)+(filename_end_ext2 - filename_ext2 - 1)*2048

	. = Entry_ext2 + 0x1f0

disk_error_ext2:

	movw	$(msg_DiskReadError_ext2 - Entry_ext2 + 0x7c00), %si

boot_error_ext2:

/* prints string DS:SI (modifies AX BX SI) */

//print_ext2:
1:
	lodsb	(%si), %al	/* get token */
	//xorw	%bx, %bx	/* video page 0 */
	movb	$0x0e, %ah	/* print it */
	int	$0x10		/* via TTY mode */
	cmpb	$0, %al		/* end of string? */
	jne	1b		/* until done */
#if 1

	/* The caller will change this to
	 *	ljmp	$0x9400, $(try_next_partition - _start1)
	 */

1:	jmp	1b

#else
	/* boot failed, try to hand over the control to supervisor */
	ldsw	(1f + 3 - Entry_ext2)(%bp), %si
	lodsl
	cmpl	$0x9400b8fa, %eax
1:	jnz	1b	/* no supervisor, hang up. */
	ljmp	$0x9400, $(try_next_partition - _start1)

	//. = . - (. - disk_error_ext2) / 30
#endif

	. = Entry_ext2 + 0x1fe

	.word	0xAA55

	. = _start1 + 0xA00

#define INSIDE_GRLDR

//#include "ntfsbs.S"
//-----------------begin of "ntfsbs.S"-----------------------
/*
 *  GRUB Utilities --  Utilities for GRUB Legacy, GRUB2 and GRUB for DOS
 *  Copyright (C) 2007 Bean (bean123@126.com)
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

/* NTFS boot sector for loading GRLDR , written by bean
 *
 * This file can be compiled as standalone boot sector, or it can be embeded in
 * GRLDR.MBR at 0xA00 , right after the ext2 boot sector
 *
 * To compile the standalone ntfsbs.bin:
 *     gcc -c -o ntfsbs.o ntfsbs.S
 *     gcc -nostdlib -Wl,-N -Wl,-Ttext -Wl,7C00 -o ntfsbs_exec ntfsbs.o
 *     objcopy -O binary ntfsbs_exec ntfsbs.bin
 *
 * To install the standalone ntfsbs.bin:
 *     grubinst --restore=ntfsbs.bin DEVICE_OR_FILE
 *
 * Where DEVICE_OR_FILE specify a NTFS partition
 *
 * Limitations:
 *  1. Don't support >1K MFT record size, >4K INDEX record size
 *  2. Don't support encrypted file
 *  3. Don't support >4K non-resident attribute list and $BITMAP
 *
 */

#ifndef INSIDE_GRLDR

	.text

	.code16
#endif

#define AT_STANDARD_INFORMATION	0x10
#define AT_ATTRIBUTE_LIST	0x20
#define AT_FILENAME		0x30
#define AT_OBJECT_ID		0x40
#define AT_SECURITY_DESCRIPTOR	0x50
#define AT_VOLUME_NAME		0x60
#define AT_VOLUME_INFORMATION	0x70
#define AT_DATA			0x80
#define AT_INDEX_ROOT		0x90
#define AT_INDEX_ALLOCATION	0xA0
#define AT_BITMAP		0xB0
#define AT_SYMLINK		0xC0
#define AT_EA_INFORMATION	0xD0
#define AT_EA			0xE0

#define MAX_MFT_SIZE	1		// 1<<(1+9) = 1024
#define MAX_IDX_SIZE	3		// 1<<(3+9) = 4096

#define LOADSEG_NT	0x2000

#define MMFT_BASE	0x2000
#define MMFT_EMFT	(MMFT_BASE +1024)
#define MMFT_EBUF	(MMFT_BASE + 2048)

#define CMFT_BASE	(MMFT_BASE + 6144)
#define CMFT_EMFT	(CMFT_BASE + 1024)
#define CMFT_EBUF	(CMFT_BASE + 2048)

#define INDX_BASE	(CMFT_BASE + 6144)

#define SBUF_BASE	(INDX_BASE + 4096)

#define NTFS_Large_Structure_Error_Code	1
#define NTFS_Corrupt_Error_Code		2
#define NTFS_Run_Overflow_Error_Code	3
#define NTFS_No_Data_Error_Code		4
#define NTFS_Decompress_Error_Code	5

#define NT_FG_COMP	1
#define NT_FG_MMFT	2
#define NT_FG_ALST	4
#define NT_FG_GPOS	8

#define nt_boot_drive	-2(%bp)
#define nt_blocksize	-4(%bp)
#define nt_spc		-5(%bp)
#define nt_mft_size	-6(%bp)
#define nt_idx_size	-7(%bp)
#define nt_mft_start	-12(%bp)
#define nt_remain_len	-16(%bp)
//#define nt_file_count	-18(%bp)

#define nt_flag		(%di)
#define nt_attr_cur	2(%di)
#define nt_attr_nxt	4(%di)
#define nt_attr_end	6(%di)
#define nt_curr_vcn	8(%di)
#define nt_curr_lcn	0x10(%di)
#define nt_attr_ofs	0x14(%di)
#define nt_target_vcn	0x18(%di)
#define nt_read_count	0x1C(%di)
#define nt_vcn_offset	0x20(%di)

#define nt_emft_buf	1024(%di)
#define nt_edat_buf	2048(%di)

	.arch	i586

Entry_nt:
	jmp	1f

	. = Entry_nt + 0x02

	.byte	0x90	/* for CHS. Another possible value is 0x0e for LBA */

	.ascii	"NTFS    "

	.word	0	/* 0B - Bytes per sector */
	.byte	0	/* 0D - Sectors per cluster */
	.word	0	/* 0E - reserved sectors, unused */
	.byte	0	/* 10 - number of FATs, unused */
	.word	0	/* 11 - Max dir entries for FAT12/FAT16, unused */
	.word	0	/* 13 - total sectors for FAT12/FAT16, unused */
	.byte	0xF8	/* 15 - Media descriptor */
	.word	0	/* 16 - sectors per FAT for FAT12/FAT16, unused */
	.word	255	/* 18 - Sectors per track */
	.word	63	/* 1A - Number of heads */
nt_part_ofs:
	.long	0	/* 1C - hidden sectors */
	.long	0	/* 20 - total sectors for FAT32, unused */
	.long	0x800080
			/* 24 - Usually 80 00 80 00, A value of 80 00 00 00 has
			 * been seen on a USB thumb drive which is formatted
			 * with NTFS under Windows XP. Note this is removable
			 * media and is not partitioned, the drive as a whole
			 * is NTFS formatted.
		 	 */
	.long	0,0	/* 28 - Number of sectors in the volume */
	.long	0,0	/* 30 - LCN of VCN 0 of the $MFT */
	.long	0,0	/* 38 - LCN of VCN 0 of the $MFTMirr */
	.long	0	/* 40 - Clusters per MFT Record */
	.long	4	/* 44 - Clusters per Index Record */
	.long	0,0	/* 48 - Volume serial number */
	.long	0	/* 50 - Checksum, usually 0 */

1:

	. = Entry_nt + 0x54

	cli
	cld

	. = Entry_nt + 0x56

	/* the byte at offset 0x57 stores the real partition number for read.
	 * the format program or the caller should set it to a correct value.
	 * For floppies, it should be 0xff, which stands for whole drive.
	 */

	movb	$0xff, %dh	/* boot partition number */

	xorw	%ax, %ax
	movw	$0x7c00, %bp

	movw	%ax, %ss	/* stack and BP-relative moves up, too */
	leaw	-0x20(%bp), %sp
	sti

	movw	%dx, nt_boot_drive

	pushw	%ax		/* AX=0 */

	/* Test if your BIOS support LBA mode */
	movb	$0x41, %ah
	movw	$0x55AA, %bx
	int	$0x13

	popw	%ds		/* DS=0 */

	jc	1f		/* No EBIOS */
	cmpw	$0xAA55, %bx
	jne	1f		/* No EBIOS */
	testb	$1, %cl
	jz	1f		/* No EBIOS */
	/* EBIOS supported */
	movb	$0x42, (ebios_nt - 1 - Entry_nt)(%bp)
1:

	pushw	%ss		/* SS=0 */
	popw	%es		/* ES=0 */

	cmpl	$0x42555247, (nt_sector_mark - Entry_nt)(%bp)
	jz	1f			// Must be called from GRLDR.MBR

	movw	$0x7E00, %bx
	movl	(nt_part_ofs - Entry_nt)(%bp), %eax
	incl	%eax
	call	readDisk_nt		// Load the second sector from disk
	call	readDisk_nt		// Load the third sector from disk
	call	readDisk_nt
1:

	xorl	%eax, %eax
	movw	0xb(%bp), %ax		// Bytes per sector (blocksize)
	movw	%ax, nt_blocksize

	call	convert_to_power_2
	movb	%cl, %bl
	movb	0xd(%bp), %al		// Sectors per cluster
	call	convert_to_power_2
	movb	%cl, %ch
	addb	%bl, %ch
	subb	$9, %ch			// 1<<ch = sectors per cluster
	movb	%ch, nt_spc
	movb	0x44(%bp), %al 		// Index record size (high bits of eax is 0)
	call	convert_size

	cmpb	$MAX_IDX_SIZE, %cl
	jbe	1f

NTFS_Large_Structure_Error:
	movb	$NTFS_Large_Structure_Error_Code, %al
	jmp	NTFS_Error

1:
	movb	%cl, nt_idx_size

	movb	0x40(%bp), %al 		// MFT record size
	call	convert_size

	cmpb	$MAX_MFT_SIZE, %cl
	jnz	NTFS_Large_Structure_Error

	movb	%cl, nt_mft_size

	movl	0x30(%bp), %eax
	//movl	0x34(%bp), %edx

	movb	%ch, %cl		// ch still contains nt_spc

	//shldl	%cl, %eax, %edx
	//orl	%edx, %edx
	//jnz	NTFS_Large_Structure_Error

	shll	%cl, %eax
	addl	(nt_part_ofs - Entry_nt)(%bp), %eax
	movl	%eax, nt_mft_start

	movw	$1, %dx
	movb	nt_mft_size, %cl
	shlw	%cl, %dx
	movw	%dx, %cx

	movw	$MMFT_BASE, %bx
	pushw	%bx
1:
	call	readDisk_nt
	loop	1b

	popw	%bx
	cmpw	$0x4946, (%bx)		// "FI"
	jnz	NTFS_Corrupt_Error

	// dx should still contain the number of sectors in the MFT record
	movw	%dx, %cx
	call	ntfs_fixup

	movw	%bx, %di
	movb	$AT_DATA, %al		// find $DATA

	call	ntfs_locate_attr
	jc	NTFS_Corrupt_Error

	movw	$CMFT_BASE, %bx
	xorl	%eax, %eax
	movb	$0x5, %al
	call	ntfs_read_mft
	movw	%bx, %di

	jmp	ntfs_search

// Convert the size of MFT and IDX block
// Input:
//     eax: size
//     ch: spc
// Output:
//     cl: convert value
convert_size:
	orb	%al, %al
	js	1f
	movb	%ch, %cl
	jmp	2f			// Jump to 2 in convert_to_power_2
1:
	negb	%al
	subb	$9, %al
	movb	%al, %cl
	ret

// Convert number to a power of 2
// Input:
//     eax
// Output:
//     cl: 1<<cl = eax
//     eax: 0

convert_to_power_2:
	xorb	%cl, %cl
2:
	incb	%cl
	shrl	$1, %eax
	jnc	2b
	decb	%cl
	ret

// Fixup the "FILE" and "INDX" record
// Input:
//     DS:BX - data buffer
//     CX - buffer length in sectors
//

ntfs_fixup:
	push	%bx
	push	%di
	movw	%bx, %di

	movw	6(%bx), %ax		// Size of Update Sequence
	decw	%ax
	movw	%ax, %bx

	mulw	nt_blocksize
	shlw	$9, %cx
	cmpw	%ax, %cx
	jnz	NTFS_Corrupt_Error	// blocksize * count != size

	movw	%bx, %cx		// cx = count

	movw	%di, %bx
	addw	4(%bx), %bx		// Offset to the update sequence
	movw	(%bx), %ax		// Update Sequence Number
	subw	$2, %di

1:
	addw	nt_blocksize, %di
	addw	$2, %bx
	cmpw	(%di), %ax
	jnz	NTFS_Corrupt_Error
	movw	(%bx), %dx
	movw	%dx, (%di)
	loop	1b

	popw	%di
	popw	%bx
	ret

NTFS_Corrupt_Error:
	movb	$NTFS_Corrupt_Error_Code, %al
	jmp	NTFS_Error

/* Read a sector from disk, using LBA or CHS
 * input:	EAX - 32-bit DOS sector number
 *		ES:BX - destination buffer
 *		(will be filled with 1 sector of data)
 * output:	ES:BX points one byte after the last byte read.
 *		EAX - next sector
 */

readDisk_nt:

	pushal
	xorl	%edx, %edx	/* EDX:EAX = LBA */
	pushl	%edx		/* hi 32bit of sector number */
	pushl	%eax		/* lo 32bit of sector number */
	pushw	%es		/* buffer segment */
	pushw	%bx		/* buffer offset */
	pushw	$1		/* 1 sector to read */
	pushw	$16		/* size of this parameter block */

	xorl	%ecx, %ecx
	pushl	0x18(%bp)	/* lo:sectors per track, hi:number of heads */
	popw	%cx		/* ECX = sectors per track */
	divl	%ecx		/* residue is in EDX */
				/* quotient is in EAX */
	incw	%dx		/* sector number in DL */
	popw	%cx		/* ECX = number of heads */
	pushw	%dx		/* push sector number into stack */
	xorw	%dx, %dx	/* EDX:EAX = cylinder * TotalHeads + head */
	divl	%ecx		/* residue is in EDX, head number */
				/* quotient is in EAX, cylinder number */
	xchgb	%dl, %dh	/* head number should be in DH */
				/* DL = 0 */
	popw	%cx		/* pop sector number from stack */
	xchgb	%al, %ch	/* lo 8bit cylinder should be in CH */
				/* AL = 0 */
	shlb	$6, %ah		/* hi 2bit cylinder ... */
	orb	%ah, %cl	/* ... should be in CL */

	movw	$0x201, %ax	/* read 1 sector */
ebios_nt: /* ebios_nt - 1 points to 0x02 that can be changed to 0x42 */

//	cmpb	$0x0e, 2(%bp)	/* force LBA? */
//	jnz	1f		/* no, continue */
//	movb	$0x42, %ah	/* yes, use extended disk read */
//1:
	movw	%sp, %si	/* DS:SI points to disk address packet */
	movb	nt_boot_drive, %dl	/* hard disk drive number */

	int	$0x13

	popaw			/* remove parameter block from stack */
	popal
	jc	disk_error_nt	/* disk read error, jc 1f if caller handles */
	incl 	%eax		/* next sector */
	addw	0x0b(%bp), %bx	/* bytes per sector */
	jnc	1f		/* 64K bound check */
	pushw	%dx
	movw	%es, %dx
	addb	$0x10, %dh	/* add 1000h to ES */
				/* here, carry is cleared */
	movw	%dx, %es
	popw	%dx
1:
	/* carry stored on disk read error */
	ret


msg_DiskReadError_nt:

	.ascii	"0\0"

NTFS_Error:
	addb	%al, (msg_DiskReadError_nt - Entry_nt)(%bp)
	jmp	disk_error_nt

msg_NTFS_Not_Found_Error:
	.ascii "No "

nt_boot_image:
	.ascii "grldr\0"

// Kernel load address, located at 0x1E8
	. = Entry_nt + 0x1e8

nt_boot_image_end:

nt_loadseg_off:
	.word	0
	.word	LOADSEG_NT

// Boot image offset and length, located at 0x1EE
// Lower 11 bit is offset, higher 5 bit is length
	. = Entry_nt + 0x1ec

nt_boot_image_ofs:
	.word (nt_boot_image - Entry_nt)+(nt_boot_image_end - nt_boot_image-1)*2048

	. = Entry_nt + 0x1ee

disk_error_nt:

	movw	$(msg_DiskReadError_nt - Entry_nt + 0x7c00), %si

boot_error_nt:

/* prints string DS:SI (modifies AX BX SI) */

//print_32:
1:
	lodsb	(%si), %al	/* get token */
	//xorw	%bx, %bx	/* video page 0 */
	movb	$0x0e, %ah	/* print it */
	int	$0x10		/* via TTY mode */
	cmpb	$0, %al		/* end of string? */
	jne	1b		/* until done */

	/* The caller will change this to
	 *	ljmp	$0x9400, $(try_next_partition - _start1)
	 */

1:	jmp	1b

	. = Entry_nt + 0x1fc

	.word	0, 0xAA55

// Here starts sector #2

// Input:
//     DI - current mft
ntfs_search:
	//movw	$0, nt_file_count
	call	ntfs_init_attr
	movb	$AT_INDEX_ROOT, %al

1:
	call	ntfs_find_attr
	jc	NTFS_Not_Found_Error

	cmpl	$0x180400,  8(%si)	// resident
					// namelen = 4
					// name offset = 0x18
	jnz	1b
	//cmpl	$0x490024, 0x18(%si)	// "$I"
	//jnz	1b
	//cmpl	$0x300033, 0x1C(%si)
	//jnz	1b			// "30"
	//testw	$0xC001, 12(%si)	// not compressed, encrypted or sparse
	//jnz	1b

	addw	0x14(%si), %si		// jump to attribute
	cmpb	$0x30, (%si)
	jnz	1b			// test if it index filenames

	addw	$0x10, %si		// skip the index root
	addw	(%si), %si

	call	ntfs_find_grldr
	jnc	ntfs_final

	call	ntfs_init_attr
	movb	$AT_BITMAP, %al
1:
	call	ntfs_find_attr
	jc	NTFS_Not_Found_Error
	movw	9(%si), %bx
	cmpb	$4, %bl
	jnz	1b
	//shrw	$4, %bx
	//cmpl	$0x490024, (%bx, %si)	// "$I"
	//jnz	1b
	cmpb	$0, 8(%si)
	jnz	1f
	pushw	0x10(%si)
	addw	0x14(%si), %si
	pushw	%si
	jmp	2f
1:
	pushw	0x30(%si)
	xorl	%edx, %edx
	movl	0x28(%si), %ecx
	cmpw	$4096, %cx
	ja	NTFS_Not_Found_Error
	shrl	$9, %ecx
	movw	$SBUF_BASE, %bx
	pushw	%bx
	call	ntfs_read_data
2:

	movb	$AT_INDEX_ALLOCATION, %al

1:
	call	ntfs_locate_attr
	jc	NTFS_Not_Found_Error

	cmpl	$0x400401, 8(%si)	// non-resident
					// namelen = 4
					// name offset = 0x40
	jnz	1b
	//cmpl	$0x490024, 0x40(%si)	// "$I"
	//jnz	1b
	//cmpl	$0x300033, 0x44(%si)
	//jnz	1b			// "30"
	//testw	$0xC001, 12(%si)	// not compressed, encrypted or sparse
	//jnz	1b

	movb	nt_idx_size, %cl
	xorl	%ebx, %ebx
	movb	$1, %bl
	shll	%cl, %ebx		// ebx - index size
	xorl	%edx, %edx		// edx - index offset


	popw	%si
	popw	%cx

1:
	pushw	%cx
	lodsb	(%si), %al

	movw	$8, %cx
2:
	pushw	%cx
	pushw	%ax
	testb	$1, %al
	jz	3f
	pushw	%si
	pushl	%edx
	pushl	%ebx

	movl	%ebx, %ecx
	movw	$INDX_BASE, %bx
	call	ntfs_read_attr
	jc	NTFS_Not_Found_Error
	cmpw	$0x4E49, (%bx)		// "IN"
	jnz	NTFS_Not_Found_Error
	call	ntfs_fixup
	movw	%bx, %si
	addw	$0x18, %si
	addw	(%si), %si

	call	ntfs_find_grldr
	jnc	ntfs_final_0

	popl	%ebx
	popl	%edx
	popw	%si

3:
	addl	%ebx, %edx

	popw	%ax
	shrb	$1, %al
	popw	%cx
	loop	2b

	popw	%cx
	loop	1b

	//pushw	nt_file_count
	//call	hex_out

NTFS_Not_Found_Error:
	leaw	(msg_NTFS_Not_Found_Error - Entry_nt)(%bp), %si
	jmp	boot_error_nt

ntfs_final_0:
	//addw	$16, %sp

// Input:
//     DI - current mft
//     SI - index entry
ntfs_final:
	cmpw	$0, 4(%si)
	jnz	NTFS_Large_Structure_Error

	movl	(%si), %eax
	movw	%di, %bx
	call	ntfs_read_mft

	movb	$AT_DATA, %al
	call	ntfs_locate_attr
	jc	NTFS_No_Data_Error

	cmpb	$1, 8(%si)		// non-resident / resident
	jz	1f

	movw	0x10(%si), %cx		// Resident
	lesw	(nt_loadseg_off - Entry_nt)(%bp), %di
	addw	0x14(%si), %si
	rep	movsb	(%si), %es:(%di)
	jmp	2f

1:

	xorl	%edx, %edx
	movl	0x28(%si), %ecx		// Use allocate size instead of real size
	shrl	$9, %ecx

	lesw	(nt_loadseg_off - Entry_nt)(%bp), %bx
	call	ntfs_read_data


2:

	//movb	$1, (do_pause - Entry_nt)(%bp)
	//call	pause

	movw	nt_boot_drive, %dx
	ljmp	*(nt_loadseg_off - Entry_nt)(%bp)

NTFS_No_Data_Error:
	movb	$NTFS_No_Data_Error_Code, %al
	jmp	NTFS_Error

// Try to find GRLDR in the index
// Input:
//     DS:SI - points to index entry
// Output:
//     CF - status

ntfs_find_grldr:
	movw	%si, %bx
	testb	$2, 0xC(%bx)
	jz	1f
	stc
	ret
1:
	//incw	nt_file_count

	xorb	%ch, %ch

	pushw	%si
	leaw	(nt_boot_image - Entry_nt)(%bp), %si
	addw	$0x52, %bx		// The value at 0xA(%bx) is wrong sometimes (0x4C)
	movb	-2(%bx), %cl
1:
	lodsb	(%si), %al
	movb	(%bx), %ah
	cmpb	$'A', %ah
	jb	2f
	cmpb	$'Z', %ah
	ja	2f
	addb	$('a'-'A'), %ah		// Convert to lowercase
2:

	cmpb	%ah, %al
	jnz	3f			// Not match

	incw	%bx
	incw	%bx
	loop	1b

	cmpb	$0,(%si)
	jnz	3f

	popw	%si
	clc
	ret				// Match found

3:

	popw	%si
	addw	8(%si), %si

	jmp	ntfs_find_grldr

// Locate an attribute
// Input:
//     DI - pointer to buffer
//     AL - attribute
ntfs_locate_attr:
	call	ntfs_init_attr
	call	ntfs_find_attr
	jc	1f
2:
	testb	$NT_FG_ALST, nt_flag
	jnz	2f
	call	ntfs_find_attr
	jnc	2b
	call	ntfs_init_attr
	call	ntfs_find_attr
2:
	clc
1:
	ret

// Prepare to find attribute
// Input:
//     DI - pointer to buffer
ntfs_init_attr:
	pushw	%ax
	xorw	%ax, %ax
	movw	%ax, nt_flag
	movw	%ax, nt_attr_end
	movw	nt_attr_ofs, %ax
	addw	%di, %ax
	movw	%ax, nt_attr_nxt
	popw	%ax
	cmpw	$MMFT_BASE, %di
	jnz	1f
	orb	$NT_FG_MMFT, nt_flag
1:
	ret

// Find an attribute
// Input:
//     DI - pointer to buffer
//     AL - attribute
// Output:
//     SI - current item
//     CF - status
ntfs_find_attr:
	movw	nt_attr_nxt, %bx
	testb	$NT_FG_ALST, nt_flag
	jnz	6f
1:
	movw	%bx, %si
	cmpb	$0xFF, (%si)
	jz	3f

	cmpb	$AT_ATTRIBUTE_LIST, (%si)
	jnz	2f
	movw	%si, nt_attr_end
2:
	addw	4(%bx), %bx
	cmpb	%al, (%si)
	jnz	1b
	movw	%bx, nt_attr_nxt
	movw	%si, nt_attr_cur
2:
	ret
3:
	cmpw	$1, nt_attr_end
	jb	2b
	movw	nt_attr_end, %si
	cmpb	$0, 8(%si)
	jnz	4f
	movw	%si, %bx
	addw	0x14(%bx), %bx
	addw	4(%si), %si
	jmp	5f
4:
	movl	0x28(%si), %ecx
	shrl	$9, %ecx
	cmpw	$8, %cx
	ja	NTFS_Corrupt_Error
	leaw	nt_edat_buf, %bx
	pushw	%ax
	xorl	%edx, %edx
	call	ntfs_read_data
	popw	%ax
	jc	2b
	movw	0x30(%si), %si
	addw	%bx, %si
5:
	movw	%si, nt_attr_end
	orb	$NT_FG_ALST, nt_flag
	testb	$NT_FG_MMFT, nt_flag
	jz	6f
	call	ntfs_fix_mmft
6:
	movw	%bx, %si
	cmpw	nt_attr_end, %bx
	jb	1f
7:
	stc
	ret
1:
	addw	4(%bx), %bx
	cmpb	%al, (%si)
	jnz	6b

	pushw	%ax
	pushw	%es
	pushw	%ds
	popw	%es
	movw	%si, nt_attr_cur
	movw	%bx, nt_attr_nxt
	movl	0x10(%si), %eax
	leaw	nt_emft_buf, %bx
	testb	$NT_FG_MMFT, nt_flag
	jnz	2f
	call	ntfs_read_mft
	jmp	3f
2:
	pushw	%bx
	call	readDisk_nt
	movl	0x14(%si), %eax
	call	readDisk_nt
	popw	%bx
	cmpw	$0x4946, (%bx)			// "FI"
	jnz	NTFS_Corrupt_Error
	movw	$2, %cx
	call	ntfs_fixup
3:
	popw	%es
	popw	%ax
	addw	0x14(%bx), %bx
4:
	cmpb	$0xFF, (%bx)
	jz	7b
	cmpb	%al, (%bx)
	jz	5f
	addw	4(%bx), %bx
	jmp	4b
5:
	movw	%bx, %si
	ret

// Fix $MFT
// Input:
//     DI - pointer to buffer
//     BX - attr cur
ntfs_fix_mmft:
	pushw	%ax
	orb	$NT_FG_GPOS, nt_flag

1:
	cmpw	nt_attr_end, %bx
	jae	NTFS_Corrupt_Error
	cmpb	%al, (%bx)
	jz	2f
	addw	4(%bx), %bx
	jmp	1b
2:

	movw	%bx, nt_attr_cur

	movl	nt_mft_start, %eax
	movl	%eax, 0x10(%bx)
	incl	%eax
	movl	%eax, 0x14(%bx)
1:
	addw	4(%bx), %bx

	cmpw	nt_attr_end, %bx
	jae	2f
	cmpb	$AT_DATA, (%bx)
	jnz	2f

	movl	0x10(%bx), %edx
	movb	nt_mft_size, %cl
	shll	%cl, %edx

	call	ntfs_read_attr

	orl	%eax, %eax
	jz	NTFS_Corrupt_Error
	movl	%eax, 0x10(%bx)
	movl	%edx, 0x14(%bx)
	jmp	1b
2:
	movw	nt_attr_cur, %bx
	andb	$(~NT_FG_GPOS), nt_flag
	popw	%ax

	ret

// Read MFT record
// Input:
//     DS:BX - buffer
//     EAX - mft number
ntfs_read_mft:
	pushw	%di
	movw	$MMFT_BASE, %di
	movb	nt_mft_size, %cl
	shll	%cl, %eax
	movl	%eax, %edx
	movl	$1, %eax
	shll	%cl, %eax
	movl	%eax, %ecx
	call	ntfs_read_attr
	jc	NTFS_Corrupt_Error
	cmpw	$0x4946, (%bx)			// "FI"
	jnz	NTFS_Corrupt_Error
	call	ntfs_fixup
	popw	%di
	ret

// Read attribute
// Input:
//     DI - pointer to buffer
//     ES:BX - buffer
//     EDX - start sector
//     ECX - sector count
// Output:
//     CF - status
ntfs_read_attr:
	pushw	nt_attr_cur
	pushl	%edx
	pushl	%ecx
	pushw	%bx

	movw	nt_attr_cur, %si
	movb	(%si), %al

	testb	$NT_FG_ALST, nt_flag
	jz	2f
	movw	%si, %bx
	movb	nt_spc, %cl
	shrl	%cl, %edx

1:
	cmpw	nt_attr_end, %bx
	jae	2f
	cmpb	%al, (%bx)
	jnz	2f
	cmpl	%edx, 8(%bx)
	ja	2f
	movw	%bx, %si
	addw	4(%bx), %bx
	jmp	1b
2:

	movw	%si, nt_attr_nxt
	call	ntfs_find_attr

	popw	%bx
	popl	%ecx
	popl	%edx
	jc	1f
	call	ntfs_read_data
	clc
1:
	popw	nt_attr_cur
	ret

// Read data
// Input:
//     DI: pointer to buffer
//     SI: current item
//     ES:BX: buffer
//     EDX: start sector
//     ECX: sector count
ntfs_read_data:
	pushw	%cx
	pushw	%bx
	testb	$1, 8(%si)
	jz	NTFS_Corrupt_Error
	movb	0xC(%si), %al
	andb	$1, %al
	orb	%al, nt_flag

	movl	%ecx, nt_read_count
	movb	nt_spc, %cl

	movl	%edx, %eax
	shrl	%cl, %eax
	movl	%eax, nt_target_vcn
	shll	%cl, %eax
	subl	%eax, %edx
	movl	%edx, nt_vcn_offset

	xorw	%dx, %dx		// edx - next VCN
	movl	%edx, nt_curr_lcn

	movl	0x10(%si), %edx

	addw	0x20(%si), %si
1:
	call	ntfs_runlist_read_block

	cmpl	nt_target_vcn, %edx
	jbe	1b
1:
	movb	nt_spc, %cl

	orl	%eax, %eax		// sparse
	jz	2f

	movl	nt_target_vcn, %eax
	subl	nt_curr_vcn, %eax
	addl	nt_curr_lcn, %eax

	shll	%cl, %eax
	addl	nt_vcn_offset, %eax

	testb	$NT_FG_GPOS, nt_flag
	jz	3f
	pushl	%eax
	incl	%eax
	subl	nt_curr_vcn, %edx
	addl	nt_curr_lcn, %edx
	shll	%cl, %edx
	cmpl	%eax, %edx
	jnz	4f
	pushw	%cx
	call	ntfs_runlist_read_block
	popw	%cx
	movl	nt_curr_lcn, %eax
	shll	%cl, %eax
4:
	movl	%eax, %edx
	popl	%eax
	addl	(nt_part_ofs - Entry_nt)(%bp), %edx
3:

	addl	(nt_part_ofs - Entry_nt)(%bp), %eax

2:
	testb	$NT_FG_GPOS, nt_flag
	jnz	1f

	pushl	%ebx
	movl	%edx, %ebx
	subl	nt_target_vcn, %ebx
	shll	%cl, %ebx
	movl	%ebx, %ecx
	popl	%ebx

	subl	nt_vcn_offset, %ecx
	movl	$0, nt_vcn_offset
	cmpl	nt_read_count, %ecx
	jbe	2f
	movl	nt_read_count, %ecx
2:

	pushl	%ecx

	orl	%eax, %eax
	jnz	3f
	call	ntfs_sparse_block
	jmp	4f

3:
	call	readDisk_nt
	loop	3b

4:
	popl	%ecx
	subl	%ecx, nt_read_count
	jbe	1f

	movl	%edx, nt_target_vcn
	call	ntfs_runlist_read_block
	jmp	1b

1:
	popw	%bx
	popw	%cx
	ret

// Read run list data
// Input:
//     CL = number of bytes
// Output:
//     EAX = read bytes
//     SI points to the next unhandled byte

ntfs_runlist_read_data:
	pushw	%cx
	orb	%cl, %cl
	jnz	1f
	popw	%cx
	xorl	%eax, %eax
	ret
1:
	lodsb	(%si), %al
	rorl	$8, %eax
	decb	%cl
	jnz	1b

	popw	%cx
	negb	%cl
	add	$4, %cl
	shlb	$3, %cl
	ret

NTFS_Run_Overflow_Error:
	movb	$NTFS_Run_Overflow_Error_Code, %al
	jmp	NTFS_Error

// Read run list block
// Output:
//     EDX = Next VCN
//     SI points to the next unhandled byte

ntfs_runlist_read_block:
	lodsb	(%si), %al
	movb	%al, %cl
	movb	%cl, %ch
	andb	$0xF, %cl		// cl - Size of length field
	jz	1f
	shrb	$0x4, %ch		// ch - Size of offset field

	call	ntfs_runlist_read_data
	shrl	%cl, %eax

	movl	%edx, nt_curr_vcn
	addl	%eax, %edx

	movb	%ch, %cl
	call	ntfs_runlist_read_data
	sarl	%cl, %eax

	addl	%eax, nt_curr_lcn

	ret

1:
	testb	$NT_FG_ALST, nt_flag
	jz	NTFS_Run_Overflow_Error

	pushl	%edx
	pushw	%bx
	movw	nt_attr_cur, %si
	movb	(%si), %al
	call	ntfs_find_attr
	jc	NTFS_Run_Overflow_Error
	cmpb	$0, 8(%si)
	jz	NTFS_Run_Overflow_Error
	movl	$0, nt_curr_lcn
	popw	%bx
	popl	%edx
	addw	0x20(%si), %si
	jmp	ntfs_runlist_read_block

// Convert seg:ofs to linear address
// Input:
//     On stack: seg:ofs
// Output:
//     eax:
seg_to_lin:
	pushw	%bp
	movw	%sp, %bp
	xorl	%eax, %eax
	xchgw	6(%bp), %ax
	shll	$4, %eax
	addl	4(%bp), %eax
	popw	%bp
	ret	$4

// Convert linear address to seg:ofs
// Input:
//     on stack: linear address
// Output:
//     On stack: seg:ofs
lin_to_seg:
	pushw	%bp
	movw	%sp, %bp
	shll	$12, 4(%bp)
	shrw	$12, 4(%bp)
	popw	%bp
	ret

fix_segs:
	pushw	%ds
	pushw	%si
	call	seg_to_lin
	pushl	%eax
	call	lin_to_seg
	popw	%si
	popw	%ds

fix_es_di:
	pushw	%es
	pushw	%di
	call	seg_to_lin
	pushl	%eax
	call	lin_to_seg
	popw	%di
	popw	%es
	ret

// Handle sparse block
//     DI: points to buffer
//     ES:BX: points to buffer
//     ECX: number of sectors
//     EDX: next VCN

ntfs_sparse_block:
	pushw	%di
	pushl	%edx

	shll	$9, %ecx		// ecx - totel number of bytes

	testb	$1, nt_flag		// Not compressed
	jz	2f

	xorl	%edx, %edx
	movb	nt_target_vcn, %dl
	andb	$0xF, %dl
	jz	2f

	movw	%bx, %di

	pushw	%cx

	movb	nt_spc, %cl
	addb	$9, %cl
	shll	%cl, %edx		// edx: offset from the start of cluster

	push	%es
	push	%di
	call	seg_to_lin
	subl	%edx, %eax		// eax: linear address

	movl	$16, nt_remain_len
	shll	%cl, nt_remain_len

	popw	%cx

	addl	%edx, %ecx
	subl	nt_remain_len, %ecx

	pushl	%ecx
	call	ntfs_decomp_block
	popl	%ecx

	addl	nt_remain_len, %ecx

	jecxz	1f

	movw	%di, %bx

2:
	movw	%bx, %di
	movl	%ecx, %edx
	xorl	%eax, %eax
	movl	%eax, %ecx
	call	fix_es_di

3:
	movw	$0x8000, %cx
	cmpl	%edx, %ecx
	jbe	4f
	movw	%dx, %cx
4:
	pushw	%cx
	shrw	$2, %cx

	rep	stosl	%eax, %es:(%di)
	call	fix_es_di
	popw	%cx
	subl	%ecx, %edx
	jnz	3b

1:
	movw	%di, %bx

	popl	%edx
	popw	%di

	ret

// Decompress block
// Input:
//     eax: linear address at the beginning of the compressed block
// Output:
//     ES:DI: points to the end of the block
ntfs_decomp_block:
	pushw	%ds
	pushw	%si

	pushl	%eax
	call	lin_to_seg
	popw	%si
	popw	%ds
	movl	nt_remain_len, %edx
	addl	%edx, %eax
	pushl	%eax
	call	lin_to_seg
	popw	%di
	popw	%es

	pushw	%es
	pushw	%di
	pushw	%ds
	pushw	%si

	xorl	%ecx, %ecx

1:
	movw	$0x8000, %cx
	cmpl	%edx, %ecx
	jbe	2f
	movw	%dx, %cx
2:
	pushw	%cx
	shrw	$2, %cx
	rep	movsl	(%si), %es:(%di)
	call	fix_segs
	popw	%cx
	subl	%ecx, %edx
	jnz	1b

	popw	%di
	popw	%es
	popw	%si
	popw	%ds

1:
	xorl	%edx, %edx			// edx - copied bytes

	lodsw	(%si), %ax
	testb	$0x80, %ah
	jnz	2f
	movw	$0x800, %cx
	rep	movsw	(%si), %es:(%di)
	movw	$0x1000, %dx
	jmp	7f				// The block is not compressed

2:
	movw	%ax, %cx
	andw	$0xFFF, %cx
	incw	%cx				// ecx = block length
	addw	%si, %cx			// cx: end marker
	xorb	%bh, %bh

3:
	cmpw	$0x1000, %dx
	ja	NTFS_Decompress_Error

	orb	%bh, %bh
	jnz	4f
	lodsb	(%si), %al
	movb	%al, %bl			// bl: tag, bh: count
	movb	$8, %bh
4:

	testb	$1, %bl
	jz	5f

	movw	%dx, %ax
	decw	%ax

	pushw	%cx
	pushw	%bx

	movb	$12, %cl
6:
	cmpw	$0x10, %ax
	jb	6f
	shrw	$1, %ax
	decb	%cl
	jmp	6b
6:

	lodsw	(%si), %ax
	movw	%ax, %bx
	shrw	%cl, %bx			// bx: delta

	pushw	%dx
	movw	$1, %dx
	shlw	%cl, %dx
	decw	%dx
	andw	%dx, %ax
	popw	%dx

	addw	$3, %ax
	movw	%ax, %cx			// cx: length
	negw	%bx
	decw	%bx

6:
	movb	%es:(%bx, %di), %al
	stosb	%al, %es:(%di)
	incw	%dx
	loop	6b

	popw	%bx
	popw	%cx
	jmp	4f

5:
	movsb	(%si), %es:(%di)
	incw	%dx
4:
	shrb	$1, %bl
	decb	%bh

	cmpw	%cx, %si
	jb	3b

7:
	call	fix_segs

	subl	%edx, nt_remain_len	// End of block
	jz	1f

	cmpw	$0x1000, %dx
	je	1b

1:

	popw	%si
	popw	%ds
	ret

NTFS_Decompress_Error:
	pushw	%ss
	popw	%ds
	movb	$NTFS_Decompress_Error_Code, %al
	jmp	NTFS_Error

/*
do_pause:
	.byte	0

pause:
	cmpb	$0, (do_pause - Entry_nt)(%bp)
	jnz	1f
	ret
1:
	xorw	%bp, %bp
1:
	jmp	1b
*/

/*
hex_out:
	pushw	%bp
	movw	%sp, %bp
	pushaw
	movb	$0xE, %ah
 	movw	$7, %bx
	movw	$4, %cx
	movw	4(%bp), %dx
1:
	rol	$4, %dx
	movb	%dl, %al
	andb	$0xF, %al
	cmpb	$10, %al
	jb	2f
	subb	$('0'-'A'+10), %al
2:
	addb	$'0', %al
	int	$0x10
	loop	1b
	movb	$' ', %al
	int	$0x10
	popaw
	popw	%bp
	ret	$2
*/

	. = Entry_nt + 0x7fc

nt_sector_mark:
	.long	0x42555247		// "GRUB"
//----------------- end  of "ntfsbs.S"-----------------------

	. = _start1 + 0x1200

	.arch	i586, jumps

#ifdef DEBUG

	. = Entry_ext2 + 0x201

debug_print:

	pushfl
	pushal
	movl	%eax, %ebp
	call	2f
#if 0
	popal
	pushal
	movl	%ebx, %ebp
	call	2f
	popal
	pushal
	movl	%ecx, %ebp
	call	2f
	popal
	pushal
	movl	%edx, %ebp
	call	2f
	popal
	pushal
	movl	%esi, %ebp
	call	2f
	popal
	pushal
	movl	%edi, %ebp
	call	2f
	popal
	popfl
	pushfl
	pushal
	pushfl
	popl	%ebp		/* flags */
	call	2f
	movw	%ds, %bp
	shll	$16, %ebp
	movw	%es, %bp
	call	2f
	movw	$0x0e0d, %ax	/* print CR */
	int	$0x10		/* via TTY mode */
	movw	$0x0e0a, %ax	/* print LF */
	int	$0x10		/* via TTY mode */
#endif
	popal
	popfl
	ret
2:
	movw	$7, %cx
1:
	xorw	%bx, %bx	/* video page 0 */
	movl	%ebp, %eax
	shrl	%cl, %eax
	shrl	%cl, %eax
	shrl	%cl, %eax
	shrl	%cl, %eax
	andb	$0x0f, %al
	addb	$0x30, %al
	movb	$0x0e, %ah	/* print char in AL */
	int	$0x10		/* via TTY mode */

	decw	%cx
	testw	%cx, %cx
	jns	1b

	movw	$0x0e20, %ax	/* print space */
	int	$0x10		/* via TTY mode */
	ret
#endif

#if 1
	/* restore GRLDR_CS */

	/* this code is executed at 0000:MONITOR, which must be a 16-byte
	 * aligned address. The address 0000:MONITOR should be designed in
	 * a way that could avoid memory confliction with volume boot records
	 * (currently FAT12/16/32/NTFS/EXT2/3 are built in).
	 */

	/* CS=code */

	.align 16

restore_GRLDR_CS:
2:
	call	1f
1:
	popw	%bx		# instruction pointer of 1b
	movw	%cs, %ax
	shrw	$4, %bx
	addw	%ax, %bx	# BX=segment value of this code
	pushw	%bx
	pushw	$(1f - 2b)
	lret
1:
	/* modify gdt base */
	xorl	%eax, %eax
	movw	%bx, %ax
	shll	$4, %eax
	addl	$(gdt -2b), %eax
	movl	%eax, %cs:(gdt - 2b + 2)
	
	movw	$GRLDR_CS, %bx
	movw	%bx, %es
	movw	%ds, %bx	# save old DS to BX

	cli
	lgdt	%cs:(gdt - 2b)
	movl	%cr0, %eax
	orb	$1, %al
	movl	%eax, %cr0

	movw	$8, %si
	movw	%si, %ds

	xorl	%esi, %esi
	xorl	%edi, %edi
	movl	$(0x9000 / 4), %ecx

	cld
	repz movsl

	movw	$16, %si
	movw	%si, %ds

	andb	$0xfe, %al
	movl	%eax, %cr0

	movw	%bx, %ds	# restore DS from BX

	ljmp	$GRLDR_CS, $(try_next_partition - _start1)

#endif

# Descriptor tables
#
# NOTE: The intel manual says gdt should be sixteen bytes aligned for
# efficiency reasons.  However, there are machines which are known not
# to boot with misaligned GDTs, so alter this at your peril!  If you alter
# GDT_ENTRY_BOOT_CS (in asm/segment.h) remember to leave at least two
# empty GDT entries (one for NULL and one reserved).
#
# NOTE:	On some CPUs, the GDT must be 8 byte aligned.  This is
# true for the Voyager Quad CPU card which will not boot without
# This directive.  16 byte aligment is recommended by intel.
#
	.align 16
gdt:
	/* this is the default null entry in GDT */
	.word	gdt_end - gdt - 1		# gdt limit
	.long	(GRLDR_CS * 16 + gdt - _start1)	# linear address of gdt
	.word	0				# pad 2 bytes

	/* real mode data segment base=0x200000 */
	.word	0xFFFF, 0
	.byte	0x20, 0x92, 0, 0

	/* real mode data segment base=0 */
	.word	0xFFFF, 0
	.byte	0, 0x92, 0, 0

gdt_end:

helper_start:

	/* helper function begins here
	 * before the call:
	 *	CF=1		: indicates an invalid or corrupt entry
	 *	CF=0		: indicates a valid entry
	 *
	 * on return:
	 * 	CF=1		: means "below", try next entry
	 *	CF=0,ZF=1	: means "equal", helper did nothing, so we need
	 *			  a further try to boot via NT bootsector
	 *	CF=0,ZF=0	: means "above", helper succeeded, boot it now
	 */

	sti

	/* DS=SS=0x9400 */
	pushw	%cs
	popw	%ds

	pushw	$FS_BOOT
	popw	%es

	/* ES=FS_BOOT */

	/* Format of partition information blocks.
	 *
	 * Offset   Length in bytes	Field
	 *  00h		1		Set to 80h if this partition is active.
	 *  01h		1		Partition's starting head.
	 *  02h		2		Partition's starting sector and track.
	 *  04h(SI)	1		Partition's ID number.
	 *  05h		1		Partition's ending head.
	 *  06h		2		Partition's ending sector and track.
	 *  08h		4		Starting LBA.
	 *  0Ch		4		Partition's length in sectors.
	 */

	pushw	%ds		/* DS=0x9400 */
	pushw	%es		/* ES=FS_BOOT */
	pushal
	pushfw

#if (defined(GRLDR_MBR)) || (defined(GRLDR_INSTALL))
	testb	$0x0C, %cs:0x02
	jz	1f

	pushw	%es		/* ES=FS_BOOT */
	/* set the DUCE indicator */
	xorw	%ax, %ax
	movw	%ax, %es
	movw	$0x5FC, %di
	movl	$0x45435544, %eax
	movb	%cs:0x02, %al
	andb	$0x0C, %al
	orb	$0x40, %al
	stosl
	popw	%es
1:
	testb	$0x80, %cs:0x02	/* boot previous MBR first? */
	jnz	2f		/* no, continue to find GRLDR */

	/* yes, call the routine for booting the previous MBR.
	 * it will not return on success.
	 * on failure, it will return here
	 */

	/* before we call the routine, we will check if the user want to
	 * skip this step and continue to find the GRLDR
	 */
	/* if timeout==0, don't display the message */
  	cmpb    $0, %cs:0x03
  	je      1f
	/* Press ... to start GRUB, any other key to boot previous MBR ... */
	movw	$(press_hot_key_pre - _start1), %si
	call	print_message
	movw	$(press_hot_key_name - _start1), %si
	call	print_message
	movw	$(press_hot_key_sub - _start1), %si
	call	print_message
1:
	call	sleep_5_seconds
	jc	3f		/* desired hot-key pressed */
	call	boot_prev_mbr	//Error_modify
	jmp	3f
2:
	/* before we find GRLDR, give the user a chance to boot_prev_mbr. */
	/* if timeout==0, don't display the message */
  	cmpb    $0, %cs:0x03
  	je      1f
	/* Press ... to boot previous MBR, any other key to start GRUB ... */
	movw	$(press_hot_key_pre - _start1), %si
	call	print_message
	movw	$(press_hot_key_name - _start1), %si
	call	print_message
	movw	$(press_hot_key_sub1 - _start1), %si
	call	print_message
1:
	call	sleep_5_seconds
	jnc	3f
	/* desired hot-key pressed */
	andb	$0x7F, %cs:0x02
	call	boot_prev_mbr	//Error_modify
3:
	/* modify code at 2b to be "jmp 4f" */
	movw	$(0xEB | ((4f - 2b - 2) << 8)), (2b - _start1)
	orb	$0x80, %cs:0x02
4:
#endif
	popfw
	popal
	popw	%es
	popw	%ds

	pushw	%ds		/* DS=0x9400 */
	pushw	%es		/* ES=FS_BOOT */
	pushal
	pushfw

	//cmpb	$0x0e, 0x00	/* EBIOS previously checked OK? */
	//jbe	1f		/* yes, skip the check */
	movb	$0x02, 0x00	/* initialise this byte to 0x02 */
	movb	$0x41, %ah	/* EBIOS check existence */
	movw	$0x55aa, %bx
//	int	$0x13
	call	int13
	jc	1f		/* No EBIOS */
	cmpw	$0xaa55, %bx
	jnz	1f		/* No EBIOS */
	testb	$1, %cl
	jz	1f		/* No EBIOS */
	movb	$0x42, 0x00	/* LBA supported, save 0x42 to 9400:0000 */
1:
	popfw
	popal
	popw	%es
	popw	%ds

	pushw	%ds		/* DS=0x9400 */
	pushw	%es		/* ES=FS_BOOT */
	pushal
	pushfw

	pushaw
	cmpw	$0x1c2, %si
	jne	1f

	/* initialize partition number and partition entries end */
	movw	$0xffff, 0x1bc		/* hd partition number */
	movw	$0x01fe, 0x1ba		/* partition entries end */
1:
	pushw	%dx

	pushw	%ds
	pushw	%es
	call	geometry_tune
	popw	%es
	popw	%ds

	testb	%dl, %dl
	jns	1f			/* floppy, use normal CHS mode */

	cmpw	$0x1f2, %si		/* is it a primary partition? */
	ja	2f			/* no, it is an extended partition */
	movl	4(%si), %eax
	movl	%eax, 8(%si)		/* parent part_start saved here */
	xorl	%eax, %eax
	movl	%eax, 4(%si)		/* current part_start(0) saved here */
2:
	//movl	-4(%si), %eax
	//cmpl	$0xfffffe00, %eax	/* check the starting CHS */
	//jb	1f			/* use normal CHS mode */

	cmpw	$0xFFFF, 0x08		/* geometry determined? */
	jne	3f			/* yes, skip */

	/* get CHS total number of sectors */
	pushw	%es
	pushw	%ds
	movb	$8, %ah		/* read drive parameters changes DX,ES,DI,BX */
	//movb	$0x80, %dl	/* BIOS drive number is in DL */
	int	$0x13
	popw	%ds
	popw	%es
	jc	3f		/* failed */
	testb	$63, %cl
	jz	3f		/* failed */

	movb	%dh, 0x09	/* Hmax */
	andb	$63, %cl	/* sectors per track */
	movb	%cl, 0x08	/* Smax */

3:

	/* check the partition's starting LBA */
	movl	4(%si), %ebx
	addl	8(%si), %ebx	/* EBX=start_LBA */

	testl	%ebx, %ebx
	je	1f

	cmpb	$0x42, 0x00	/* EBIOS present? */
	je	3f		/* yes, skip the CHS mode int13 fix */

	/******************************************************************/
	/* read the boot sectors once again using CHS translated from LBA */
	/******************************************************************/

	movw	$0, %bp
	movw	0x08, %ax
	movw	%ax, %dx
	movb	$0, %dh
	movw	%dx, 0x18	/* sectors per track in 0x18(%bp) */
	movb	%ah, %dl
	incw	%dx
	movw	%dx, 0x1a	/* number of heads in 0x1a(%bp) */

	popw	%ax		/* AX=orig DX which holds drive number DL */
	pushw	%ax

	movb	%al, 0x24	/* drive number in 0x24(%bp) */

	pushw	(jc_code_begin - _start1)	/* save original code */

	/* modify jc_code_begin in readDisk_12_16 */
	movw	$(0xEB | ((jc_code_end - jc_code_begin - 2) << 8)), (jc_code_begin - _start1)

	pushw	%es
	pushl	%ebx

	pushl	%ebx
	popw	%ax
	popw	%dx		/* DX:AX=LBA */

	xorw	%bx, %bx	/* buffer in ES:BX=FS_BOOT:0 */
	movw	$63, %cx	/* number of sectors to read in CX */

	call	readDisk_12_16	/* CX=0, AX,DX,ES changed */

	popl	%ebx
	popw	%es

	popw	(jc_code_begin - _start1)	/* restore original code */

	/*******************************************************/
	/* load partition boot track to FS_BOOT using LBA mode */
	/*******************************************************/

	cmpb	$0x42, 0x00	/* EBIOS present? */
	jne	1f		/* no, skip the LBA mode int13 call */
3:
	popw	%ax		/* AX=orig DX which holds drive number DL */
	pushw	%ax
	xorw	%dx, %dx
	pushw	%dx		/* DX=0, higher 4 bytes of starting LBA */
	pushw	%dx
//	pushl	%edx		/* EDX=0, higher 4 bytes of starting LBA */
	pushl	%ebx		/* lower 4 bytes of starting LBA */
	pushw	%es		/* ES=FS_BOOT */
	pushw	%dx		/* DX=0, ES:0 is the buffer */
	//pushl	$0x003f0010	/* transfer 63 sectors */
	pushw	$0x3f		/* transfer 63 sectors */
	pushw	$0x10		/* size of disk address packet */
	xchgw	%ax, %dx	/* restore drive number DL from AL */
	movb	$0x42, %ah	/* extended read */
	movw	%sp, %si	/* DS:SI points to disk address packet */
//	int	$0x13		/* ignore the read failure */
	call	int13
	popaw			/* adjust the stack */
	jc	1f
	popw	%dx
	popaw

	//popw	%ax		/* discard flags in the stack */
	popfw
	clc

	pushfw			/* push new flags with CF=0 */
	pushaw
	pushw	%dx
1:
	popw	%dx
	popaw

	popfw
	popal
	popw	%es
	popw	%ds

	pushw	%ds		/* DS=0x9400 */
	pushw	%es		/* ES=FS_BOOT */
	pushal
	pushfw

	pushw	%si

	pushfw
	pushw	%es
//---------------------------------------------------------
	/* print "Try (hd0,n): " or "Try (fd0): "*/
	pushw	%ds
	popw	%es		/* ES=DS=CS=0x9400 */

	cld			/* for stosb */
	xorw	%ax, %ax
	testb	%dl, %dl
	jns	1f		/* floppy */
	/* hard drive */
#if 0
	movw	%si, %ax
	subw	$0x1c2, %ax
	shrw	$4, %ax
	cmpw	$0x1fe, %si	/* is in MBR? */
	jb	1f		/* yes */
	/* no, it is an entry in an extended partition */
	movb	$0xFC, (add_sub_si + 2 - _start1)	/* addw	$-4, %si */
	incw	0x1bc		/* logical partition number */
	movb	0x1bc, %al
#else
	incw	0x1bc		/* logical partition number */
	movw	0x1bc, %ax
	cmpb	$4, %al
	jb	1f
	movb	$0xFC, (add_sub_si + 2 - _start1)	/* addw	$-4, %si */
#endif
1:
	/* AL=partition number, AH=0 */
	pushw	%ax

	movw	$(partition_message - _start1 + 7), %di	/* drive type */
	movb	%dl, %al
	shrb	$7, %al		/* drive type: floppy=0, harddrive=1 */
	shlb	$1, %al
	addw	$0x6466, %ax	/* "fd" or "hd" */
	stosw
	movb	%dl, %al
	andb	$0x7f, %al	/* drive number */
	aam		/* convert binary to decimal, AH=high, AL=low */
	testb	%ah, %ah
	jz	1f
	addb	$0x30, %ah
	movb	%ah, (%di)
	incw	%di
1:
	addb	$0x30, %al
	stosb

	popw	%ax

	testb	%dl, %dl
	jns	2f		/* floppy */
	/* this is a hard drive, the partition number is in AL */
	movb	$0x2c, (%di)	/* "," */
	incw	%di
	aam		/* convert binary to decimal, AH=high, AL=low */
	testb	%ah, %ah
	jz	1f
	addb	$0x30, %ah
	movb	%ah, (%di)
	incw	%di
1:
	addb	$0x30, %al
	stosb
2:
	movl	$0x00203a29, (%di)	/* "): \0" */

	movw	$(partition_message - _start1), %si
	call	print_message	/* CS:SI points to message string */
//---------------------------------------------------------
	popw	%es
	popfw
	//stc
	jc	invalid_or_null		/* invalid or null entry */

	xorw	%si, %si
	pushw	%es
	popw	%ds

	/* DS=ES=FS_BOOT */

	/* First, check for ext2 filesystem */

	cmpw	$0xEF53, 0x438		/* Magic signature */
	jnz	1f
	xorl	%eax, %eax
	cmpl	%eax, 0x400		/* s_inodes_count */
	jz	1f
	cmpl	%eax, 0x404		/* s_blocks_count */
	jz	1f
//	cmpw	%ax, 0x458		/* s_inode_size, usually 0x80 */
//	jz	1f
	cmpl	%eax, 0x420		/* s_blocks_per_group */
	jz	1f
	cmpl	%eax, 0x428		/* s_inodes_per_group */
	jz	1f
	movl	0x414, %eax		/* s_first_data_block */
	movw	%ax, %bx		/* BX=1 for 1K block, 0 otherwise */
	shrl	$1, %eax		/* must be 0 */
	jnz	1f
	movl	0x418, %ecx		/* s_log_block_size */
	cmpl	$4, %ecx		/* max size of block is 16K */
	ja	1f
	negw	%cx			/* CF=0 for 1K block, CF=1 otherwise */
	adcw	%ax, %bx		/* EAX=0 */
	decw	%bx
	jnz	1f

	/* BX = 0 */
	/* EAX= 0 */

	movw	$0x80, %ax		/* EXT2_GOOD_OLD_INODE_SIZE */
	movw	%ax, %cs:0x826		/* inode size */
	movl	0x44C, %ecx		/* ECX=s_rev_level */
	jecxz	3f			/* EXT2_GOOD_OLD_REV */
	movw	0x458, %ax		/* AX=s_inode_size */
	testw	%ax, %ax
	jz	1f			/* invalid inode size */
	pushw	%ax
	pushw	%dx
	movb	0x418, %cl		/* s_log_block_size */
	addb	$10, %cl
	xorw	%dx, %dx		/* DX=0 */
	incw	%dx			/* DX=1 */
	shlw	%cl, %dx		/* DX=block size in bytes */
	xchgw	%ax, %cx		/* CX=s_inode_size */
	xchgw	%ax, %dx		/* AX=block size in bytes */
	xorw	%dx, %dx		/* DX:AX=block size in bytes */
	divw	%cx			/* quo=AX, rem=DX */
	testw	%dx, %dx
	popw	%dx
	popw	%ax
	jnz	1f			/* invalid inode size */
	movw	%ax, %cs:0x826		/* inode size */
3:
	/* BX = 0 */

	/* super block is sane */

	//pushw	%cs
	//popw	%ds
	///* DS=SS=0x9400 */
	///* ES=FS_BOOT */
	cld
	movw	$0x800, %si
	xorw	%di, %di
	movw	$0x0200, %cx	/* yes, we need 2 sectors if enable debug */

	repz cs movsw		/* CS segment override prefix(=0x2E) */

	/* modify the boot partition number */

	/* the boot partition number is at offset 0x25 for ext2 */

	testb	%dl, %dl
	jns	3f			/* no modification for floppy */
	movw	$0x25, %di
	movw	%cs:0x1bc, %ax		/* partition number */
	stosb
3:
	/* fix for ext2 partition: hidden_sectors, offset 0x1c */
	popw	%si			/* DI points to old entry in MBR */
	pushw	%si
	xorl	%eax, %eax		/* let hidden_sectors=0 for floppy */
	testb	%dl, %dl
	jns	3f			/* floppy */
	movl	%cs:4(%si), %eax
	addl	%cs:8(%si), %eax
3:
	/* BX = 0 */

	movl	%eax, %es:0x1c(%bx)	/* adjust hidden_sectors for EXT2 */

	/* fix for ext2 partition: EBIOS indicator, offset 0x02 */

	movb	%cs:0x00(%bx), %al
	movb	%al, %es:0x02(%bx)

	/* fix for ext2 partition: sectors per block, offset 0x0d */
	/* fix for ext2 partition: bytes per block, offset 0x0e */
	/* fix for ext2 partition: dwords per block(dpb), offset 0x14 */
	/* fix for ext2 partition: square of dpb, offset 0x10 */

	movb	%es:0x418, %cl		/* s_log_block_size */
	//incw	%cx
	movl	$2, %eax
	shlw	%cl, %ax
	movb	%al, %es:0x0d(%bx)
	shlw	$9, %ax			/* block size is word wide */
	movw	%ax, %es:0x0e(%bx)
	shrw	$2, %ax
	movl	%eax, %es:0x14(%bx)
	addb	$8, %cl
	shll	%cl, %eax
	movl	%eax, %es:0x10(%bx)


	/* fix for ext2 partition: sectors per track, offset 0x18 */
	/* fix for ext2 partition: number of heads, offset 0x1a */
	movw	%cs:0x08(%bx), %ax	/* BX=0 */
	cmpw	$0xFFFF, %ax
	jz	3f
	movb	%al, %es:0x18(%bx)
	shrw	$8, %ax
	incw	%ax
	movw	%ax, %es:0x1a(%bx)
3:

#if 0
	pushw	%ds
	pushw	%es
	pushw	%bx
	pushw	%dx
	movb	$8, %ah		/* read drive parameters changes DX,ES,DI,BX */
	movb	$0x80, %dl	/* BIOS drive number is in DL */
	int	$0x13
//	call	int13
	xchgw	%ax, %dx	/*movw	%dx, %ax*/ //AH=max head number
	popw	%dx
	popw	%bx
	popw	%es
	popw	%ds
	jc	3f
	andb	$63, %cl
	jz	3f
	movb	%cl, %es:0x18(%bx)
	shrw	$8, %ax		//AX=max head number
	incw	%ax		//AX=total heads
	movw	%ax, %es:0x1a(%bx)
3:
//#else
	testb	%dl, %dl
	jns	3f			/* floppy */
	popw	%di			/* DI points to old entry in MBR */
	pushw	%di
	movw	%cs:1(%di), %ax
	andb	$63, %ah
	movb	%ah, %es:0x18
	xorb	%ah, %ah
	incw	%ax
	movw	%ax, %es:0x1a
3:
#endif
	
	/* fix for ext2 partition: s_inodes_per_group, offset 0x28 */
	movl	%es:0x428, %eax		/* s_inodes_per_group */
	movl	%eax, %es:0x28(%bx)

	/* fix for ext2 partition: block number for group descriptors, offset 0x2c */
        /* At which block the group descriptors begin? */
	movl	%es:0x414, %eax		/* s_first_data_block */
	incw	%ax
	movl	%eax, %es:0x2c(%bx)

	/* fix for ext2 partition: on error go back to supervisor, offset 0x01fc */
	movw	$0x01fc, %si
	movw	%si, %di
	lodsw
	cmpw	$0xFEEB, %ax /* EB FE is jmp back to itself(infinite loop) */
	jnz	3f
	decw	%ax		/* AL=0xEA, ljmp */
	stosb
	//movw	$(try_next_partition - _start1), %ax
	movw	$MONITOR, %ax
	stosw
	//movw	%cs, %ax	/* AX=0x9400 */
	xorw	%ax, %ax
	stosw			/* the last byte 0x00 is in the next sector! */
//	addw	$0x0f, %di
//	movw	$(restore_GRLDR_CS - _start1), %si
//	movw	$((gdt_end - restore_GRLDR_CS) / 4), %cx
//	.byte	0x2e		/* %cs: prefix */
//	repz movsl
3:

	movw	$(EXT2_message - _start1), %si
	call	print_message	/* CS:SI points to message string */

	clc
	jmp	move_entries_and_return

1:
	#; It is not EXT2. Check for FAT12/16/32/NTFS.

	/* DS=ES=FS_BOOT */

	cmpw	$0x200, 0x0b(%si)	/* bytes per sector */
	jne	1f			/* not a normal BPB */
	movb	0x0d(%si), %al		/* sectors per cluster */
	testb	%al, %al
	jz	1f			/* invalid if = 0 */
	movb	%al, %cl
	movw	$128, %ax
	divb	%cl			/* quo=AL, rem=AH */
	testb	%ah, %ah
	jnz	1f			/* invalid if not 2^n */
	movw	0x18(%si), %ax		/* sectors per track */
	testw	%ax, %ax
	jz	1f			/* invalid if = 0 */
	cmpw	$63, %ax
	ja	1f			/* invalid if > 63 */
	movw	0x1a(%si), %ax		/* number of heads */
	decw	%ax			/* Max head number, should be a byte */
	testb	%ah, %ah		/* should be 0 */
	jnz	1f			/* invalid if number of heads > 256 */
	cmpb	$0xf0, 0x15(%si)	/* media descriptor */
	jb	1f

	cmpb	$0x42, %cs:0x00		/* EBIOS present? */
	jne	3f
	//movb	$0x41, %ah		/* EBIOS check existence */
	//movw	$0x55aa, %bx
	//int	$0x13
	//jc	3f			/* No EBIOS */
	//cmpw	$0xaa55, %bx
	//jnz	3f			/* No EBIOS */
	//testb	$1, %cl
	//jz	3f			/* No EBIOS */
	movb	$0x0e, 0x02(%si)	/* force LBA */
3:
	cld
	movw	$0x0600, %bx		/* FAT12/FAT16 */
	movw	$0x003c, %cx		/* FAT12/FAT16 */

	movb	0x10(%si), %al		/* number of FATs(NTFS:0, FAT:1,2) */
	cmpb	$2, %al
	ja	1f			/* abnormal FAT */
	movw	0x11(%si), %ax		/* max root entries */
	testw	%ax, %ax
	jnz	2f			/* FAT12/FAT16 */

	/* FAT32 or NTFS */
	movw	0x13(%si), %ax		/* total sectors(small) */
	testw	%ax, %ax
	jnz	1f			/* invalid FAT32 BPB */
	movw	0x16(%si), %ax		/* sectors per FAT(small) */
	testw	%ax, %ax
	jnz	1f			/* invalid FAT32 BPB */
	movb	0x10(%si), %al		/* number of FATs(NTFS:0, FAT:1,2) */
	testb	%al, %al
	jz	8f

	/* FAT32 */
	movl	0x20(%si), %eax		/* FAT32 total sectors */
	testl	%eax, %eax
	jz	1f
	movl	0x24(%si), %eax		/* FAT32 sectors per FAT */
	testl	%eax, %eax
	jz	1f
	movw	$0x0400, %bx		/* FAT32 */
	movw	$0x0058, %cx		/* FAT32 */
	movw	$(FAT32_message - _start1), %si	/* SI changed!! */
	jmp	7f
8:
	/* NTFS */
	movl	0x20(%si), %eax		/* FAT32 total sectors */
	testl	%eax, %eax
	jnz	1f
	//movw	0x11(%si), %ax		/* max root entries */
	//testw	%ax, %ax
	//jnz	1f
	movw	0x0e(%si), %ax		/* reserved sectors */
	testw	%ax, %ax
	jnz	1f

	/* fix for ntfs partition: sectors per track, offset 0x18 */
	/* fix for ntfs partition: number of heads, offset 0x1a */
	movw	%cs:0x08(%si), %ax	/* SI=0 */
	cmpw	$0xFFFF, %ax
	jz	3f
	movb	%al, 0x18(%si)		/* DS=ES */
	shrw	$8, %ax
	incw	%ax
	movw	%ax, 0x1a(%si)
3:
	/* BUG fix for extended NTFS partition */
	popw	%si			/* SI points to old entry in MBR */
	pushw	%si
	xorl	%eax, %eax		/* let hidden_sectors=0 for floppy */
	testb	%dl, %dl
	jns	3f			/* floppy */
	movl	%cs:4(%si), %eax
	addl	%cs:8(%si), %eax
3:
	movl	%eax, 0x1c		/* adjust hidden_sectors for NTFS */

	movb	%dl, 0x24		/* adjust drive number for NTFS */

#if 1
	// Load NTFS using internal boot sector at 0xA00

	movw	$(NTFS5_message - _start1), %si
	call	print_message	/* CS:SI points to message string */

	movw	$0xA00, %bx
	movw	$0x52, %cx

	pushw	%cs
	popw	%ds

	/* DS=SS=0x9400 */
	/* ES=FS_BOOT */

	movw	%bx, %si
	xorw	%di, %di
	lodsw
	stosw
	addw	%cx, %si
	addw	%cx, %di
	movw	$0x800, %cx
	subw	%di, %cx

	repz movsb

	/* modify the boot partition number */
	movb	%es:1, %al
	addb	$5, %al			/* AL is less than 0x80 */
	cbw				/* AH=0 */
	xchgw	%ax, %di		/* move AX to DI */
	movb	$0xff, %al		/* partition=whole drive for floppy */
	testb	%dl, %dl
	jns	3f			/* no modification for floppy */
	movb	0x1bc, %al		/* partition number */
3:
	stosb

	/* fix for NTFS partition: on error go back to supervisor, offset 0x01fa */

	movw	$0x01fa, %di
	movw	%es:(%di), %ax
	cmpw	$0xFEEB, %ax /* EB FE is jmp back to itself(infinite loop) */
	jnz	3f
	decw	%ax		/* AL=0xEA, ljmp */
	stosb
	//movw	$(try_next_partition - _start1), %ax
	movw	$MONITOR, %ax
	stosw

	//movw	%cs, %ax	/* AX=0x9400 */
	xorw	%ax, %ax
	stosw			/* DI=0x01ff */
3:
	clc
	jmp	move_entries_and_return

#else

	/* modify the boot partition number */
	movb	$0xB6, %al		/* 0xB6="MOV DH,imm8" */
	movb	%cs:0x1bc, %ah
	testb	%dl, %dl
	js	3f
	movb	$0xff, %ah /* partition number for floppy is whole drive */
3:
	/* before the call:
	 *		AH= partition number
	 *		AL= 0xB6	; 0xB6 is opcode of "MOV DH,imm8"
	 *		DL= drive number
	 *
	 * on return:	CF=0 if there is NTFS boot record;
	 *		CF=1 otherwise. 
	 *		CF of flags_orig on the stack will set if CF=1
	 */

	call	modify_NTFS_boot_record
	//jnc	move_entries_and_return
	//movw	$(NTFS5_message - _start1), %si
	////jmp	4f
	//call	print_message	/* CS:SI points to message string */
	//stc
	jmp	move_entries_and_return

#endif

2:
	/* FAT12/FAT16 */
	xorw	%si, %si
	movb	0x10(%si), %al		/* number of FATs(NTFS:0, FAT:1,2) */
	testb	%al, %al
	jz	1f
	movw	0x16(%si), %ax		/* sectors per FAT(small) */
	testw	%ax, %ax
	jz	1f
	movw	$(FAT16_message - _start1), %si
	cmpw	$12, %ax
	ja	7f
	movw	$(FAT12_message - _start1), %si
7:
	pushw	%bx
	pushw	%cx
	call	print_message	/* CS:SI points to message string */
	popw	%cx
	popw	%bx

	/* fix for fat 12/16/32: sectors per track, offset 0x18 */
	/* fix for fat 12/16/32: number of heads, offset 0x1a */
	xorw	%si, %si
	movw	%cs:0x08(%si), %ax	/* SI=0 */
	cmpw	$0xFFFF, %ax
	jz	3f
	movb	%al, 0x18(%si)		/* DS=ES */
	shrw	$8, %ax
	incw	%ax
	movw	%ax, 0x1a(%si)
3:
	/* BUG fix for extended FAT12/16/32 partition */
	popw	%di			/* DI points to old entry in MBR */
	pushw	%di
	xorl	%eax, %eax		/* let hidden_sectors=0 for floppy */
	testb	%dl, %dl
	jns	3f			/* floppy */
	movl	%cs:4(%di), %eax
	addl	%cs:8(%di), %eax
3:
	movl	%eax, 0x1c		/* adjust hidden_sectors for FAT */

	pushw	%cs
	popw	%ds
	/* DS=SS=0x9400 */
	/* ES=FS_BOOT */
	movw	%bx, %si
	xorw	%di, %di
	lodsw
	stosw
	addw	%cx, %si
	addw	%cx, %di
	movw	$0x0200, %cx
	subw	%di, %cx
	repz movsb
	/* modify the boot partition number */
	movb	%es:1, %al
	addb	$5, %al			/* AL is less than 0x80 */
	cbw				/* AH=0 */
	xchgw	%ax, %di		/* move AX to DI */
	movb	$0xff, %al		/* partition=whole drive for floppy */
	testb	%dl, %dl
	jns	3f			/* no modification for floppy */
	movb	0x1bc, %al		/* partition number */
3:
	stosb

	/* fix for FAT12/16/32 partition: on error go back to supervisor, offset 0x01fa */
	//pushw	%es
	//popw	%ds
	movw	$0x01fa, %di
	//movw	%di, %si
	//lodsw
	movw	%es:(%di), %ax
	cmpw	$0xFEEB, %ax /* EB FE is jmp back to itself(infinite loop) */
	jnz	3f
	decw	%ax		/* AL=0xEA, ljmp */
	stosb
	//movw	$(try_next_partition - _start1), %ax
	movw	$MONITOR, %ax
	stosw
	//movw	%cs, %ax	/* AX=0x9400 */
	xorw	%ax, %ax
	stosw			/* DI=0x01ff */
3:

	clc
	jmp	move_entries_and_return
1:
	#; It is not FAT12/16/32/NTFS. Check for extended partition.

	/* DS=ES=FS_BOOT */

	pushw	%cs
	popw	%es

	/* ES=SS=0x9400 */
	/* DS=FS_BOOT */

	popw	%si
	pushw	%si
	cmpb	$0x05, %es:(%si)	/* extended */
	je	1f
	cmpb	$0x0f, %es:(%si)	/* Win95 extended (LBA) */
	je	1f
	cmpb	$0x15, %es:(%si)	/* hidden extended */
	je	1f
	cmpb	$0x1f, %es:(%si)	/* hidden win95 extended (LBA) */
	je	1f
	cmpb	$0x85, %es:(%si)	/* Linux extended */
	je	1f
	movw	$(non_MS_message - _start1), %si
4:
	call	print_message	/* CS:SI points to message string */
	stc
	jmp	move_entries_and_return
1:
	/* extended partition entry */
	cmpw	$0x1fe, %si
	jb	1f
	decw	%es:0x1bc	/* count the partitions in extended zone */
1:
	movw	$(extended_message - _start1), %si
	call	print_message	/* CS:SI points to message string */
	movw	$0x1be, %si
	movw	$4, %cx
5:
	//xorl	%eax, %eax
	//cmpl	%eax, (%si)
	//jnz	2f
	movl	(%si), %eax
	cmpw	2(%si), %ax	/* Is EAX high word equal to AX? */
	jnz	2f
	cmpb	%al, %ah	/* Is AL=AH? */
	jnz	2f

	/* now all 4 bytes in EAX are equal to each other. */
	cmpl	%eax, 4(%si)
	jnz	2f
	cmpl	%eax, 8(%si)
	jnz	2f
	cmpl	%eax, 12(%si)
	jz	3f	/* entry with 16 dups of a byte means empty entry */
2:
	movb	(%si), %al
	shlb	$1, %al
	jnz	1f
	//jnz	3f		/* invalid entry is treated as empty entry */
	movb	2(%si), %al
	and	$63, %al	/* starting sector number */
	jz	1f
	//jz	3f		/* invalid entry is treated as empty entry */
	movb	6(%si), %al
	and	$63, %al	/* ending sector number */
	jz	1f
	//jz	3f		/* invalid entry is treated as empty entry */
	movl	8(%si), %eax	/* starting LBA */
	testl	%eax, %eax
	jz	1f
	//jz	3f		/* invalid entry is treated as empty entry */
	movl	12(%si), %eax	/* total number of sectors in partition */
	testl	%eax, %eax
	jz	1f
3:
	addw	$16, %si
	loop	5b
	cmpw	$0xaa55, (%si)
	jnz	1f

	movw	$0x1be, %si
	movw	$4, %cx
	popw	%bx	/* the old SI points to extended partition ID in MBR */
	pushw	%bx
5:
#if 1
	//xorl	%eax, %eax
	//cmpl	%eax, (%si)
	//jnz	2f
	movl	(%si), %eax
	cmpw	2(%si), %ax	/* Is EAX high word equal to AX? */
	jnz	2f
	cmpb	%al, %ah	/* Is AL=AH? */
	jnz	2f

	/* now all 4 bytes in EAX are equal to each other. */
	cmpl	%eax, 4(%si)
	jnz	2f
	cmpl	%eax, 8(%si)
	jnz	2f
	cmpl	%eax, 12(%si)
	jz	3f	/* entry with 16 dups of a byte means empty entry */
2:
	/* now it is an acceptable entry */
	movw	%es:0x1ba, %di	/* partition entries end */
	/* ensure our stack not to be overwritten by the partition entries */
	cmpw	$0x83f0, %di
	ja	3f		/* try next */
	/* ensure our code not to be overwritten by the partition entries */
	cmpw	$0x3fe, %di
	jne	6f
	/* more entries stores at 0x9be00-0x9c3ff */
	movw	$0x7e00, %di
	movw	%di, %es:0x1ba
6:
	addw	$16, %es:0x1ba	/* increment partition entries end */

	lodsl
	stosl
	lodsl
	stosl

	xchgw	%ax, %dx	/* save AL(the partition ID)to DL */

	lodsl
        xchgl	%eax, %edx	/* restore AL from DL(the partition ID), */
				/* and save EAX to EDX */
	cmpb	$0x05, %al
	je	6f
	cmpb	$0x0f, %al
	je	6f
	cmpb	$0x15, %al
	je	6f
	cmpb	$0x1f, %al
	je	6f
	cmpb	$0x85, %al
	je	6f
	/* normal partition, copied to 0x941fe-0x943fb */
	addl	%es:4(%bx), %edx	/* current partition start */
6:
	/* extended partition, copied to 0x941fe-0x943fb */
        xchgl	%eax, %edx	/* restore or update EAX from EDX */
	stosl
	lodsl				/* adjust SI only */
	movl	%es:8(%bx), %eax	/* parent partition start ... */
	stosl				/* ... stored here */
	jmp	2f
3:
	addw	$16, %si
#endif
	//. = 5b + 0x7c
2:
	loop	5b

	/* extended partition is not a normal one, so set carry to try next */
	stc
	jmp	move_entries_and_return

invalid_or_null:
1:
	movw	$(invalid_message - _start1), %si
	call	print_message	/* CS:SI points to message string */
	stc

move_entries_and_return:
	popw	%si
	pushfw
	pushw	%cs
	popw	%ds
	pushw	%cs
	popw	%es
	pushw	%si
	cmpw	$0x202, %si
	jne	1f
	/* move entries backward 1 entry */
	movw	$0x1fe, %di
	movw	$0x20e, %si
	movw	$0xf8, %cx		/* 0x1f0 bytes = 0xf8 words */
	cld				/* move upward */
	repz movsw
	movw	$0x3ee, %di
	movw	$0x7e00, %si
	movw	$0x8, %cx		/* 0x10 bytes = 0x8 words */
	cld				/* move upward */
	repz movsw
	movw	$0x7e00, %di
	movw	$0x7e10, %si
	movw	$0x2f8, %cx		/* 0x5f0 bytes = 0x2f8 words */
	cld				/* move upward */
	repz movsw
	cmpw	$0x7e10, 0x1ba
	jne	2f
	movw	$0x40e, 0x1ba
2:
	subw	$0x10, 0x1ba
	
1:
	popw	%si
	movw	$0x1fe, %ax
	movw	$(add_sub_si + 5 - _start1), %di
	movw	%ax, (%di)		/* 0x1fe */
	cmpw	$0x31b2, %si		/* floppy? */
	je	4f			/* yes */
	incw	(%di)			/* 0x1ff */
	cmpw	%ax, 0x1ba		/* AX=0x1fe */
	jne	1f
	decw	(%di)			/* 0x1fe */
	//cmpw	$0x31b2, %si		/* floppy? */
	//je	4f	// 1f		/* yes */
	cmpw	$0x1f2, %si
	ja	2f			/* logical partition */
	jb	1f			/* primary partition 0, 1, 2 */
	/* primary partition 3 */
	cmpw	$0x0003, 0x1bc		/* are there any logical partitions? */
	ja	1f			/* yes */
2:
inc_hard_drive:

	/* all partitions on the drive have been checked, try next drive.
	 *
	 * the current stack is:
	 *
	 * SP + 38	: DS
	 * SP + 36	: ES
	 * SP + 32	: EAX
	 * SP + 28	: ECX
	 * SP + 24	: EDX
	 * SP + 20	: EBX
	 * SP + 16	: ESP_temp
	 * SP + 12	: EBP
	 * SP +  8	: ESI
	 * SP +  4	: EDI
	 * SP +  2	: flags_orig
	 * SP		: flags
	 *
	 */

	/* get total hard drives */
	xorw	%ax, %ax
	movw	%ax, %ds
	movb	0x475, %dh
	pushw	%cs
	popw	%ds
//	cmpb	$16, %dh
//	jnb	2f
//	movb	$16, %dh
//2:
	orb	$0x80, %dh	/* CF=0, DH=Max harddrive number + 1 */
	//xchgw	%ax, %cx	/* CL=Max harddrive number + 1, CH=0 */
	movw	%sp, %bp
	movb	24(%bp), %dl	/* BIOS drive number is in DL */
2:
	jnc	3f
	call	print_message	/* CS:SI points to message string */
	movw	$(drive_number_string - _start1), %si
	movb	%dl, %al
	andb	$0x7f, %al
	aam			/* AH=high decimal, AL=low decimal */
	addw	$0x3030, %ax
	xchgb	%al, %ah
	movw	%ax, 32(%si)
	call	print_message	/* CS:SI points to message string */
3:
	incw	%dx		/* !!!! Next drive !!!! */
	cmpb	%dh, %dl
	jnb	2f		/* all drives checked, try floppy finally */

	pushw	%bx
	movb	$8, %ah		/* read drive parameters changes DX,ES,DI,BX */
	call	int13
	jc	3f		/* try next hard drive */
	andb	$63, %cl	/* CL=sectors per track, CF cleared */
	stc
	jz	3f		/* try next hard drive */
	popw	%bx
	movb	%dl, %ch	/* DL saved at BP high byte in the stack */
	pushw	%cx		/* push new BX onto stack */
	movw	$0x201, %ax	/* read 1 sector */
	movw	$0x7e00, %bx	/* read MBR to 9400:7e00 */
	movw	$1, %cx
	xorb	%dh, %dh
	call	int13
	sti
3:
	popw	%bx		/* BL=sectors per track, BH=DL */

	movw	$(Error_while_reading_string - _start1), %si
	jc	2b		/* read failure, try next hard drive */

	/* on seccessful return, should be: ah=0 for OK, al=1 for 1 sector */
	//decw	%ax		/* some BIOSes return incorrect AL */
	testb	%ah, %ah
	stc
	jnz	2b

	/* The new partition table might be empty or invalid.
	 * Move the new partition table onto the old one while checking
	 */

	//movb	%dl, %bh	/* DL saved at BP high byte in the stack */

	movw	$0x7fbe, %si
	movw	$0x01be, %di

3:
	cmpw	$0x1fe, %di
	jnb	3f

	xorl	%ecx, %ecx

	lodsl
	stosl
	orl	%eax, %ecx
	lodsl
	stosl
	orl	%eax, %ecx
	lodsl
	stosl
	orl	%eax, %ecx
	lodsl
	stosl
	orl	%eax, %ecx
	jecxz	3b		/* null entry, check next */

	//lodsw
	//stosw
	movb	-16(%si), %al
	shlb	$1, %al
	stc
	xchgw	%ax, %si	/* save SI to AX */
	movw	$(partition_boot_indicator_string - _start1), %si
	jnz	2b
	xchgw	%ax, %si	/* restore SI from AX */
	//lodsw
	//stosw
	movb	-14(%si), %al
	andb	$63, %al
	stc
	xchgw	%ax, %si	/* save SI to AX */
	movw	$(partition_sectors_per_track_string - _start1), %si
	jz	2b
	xchgw	%ax, %si	/* restore SI from AX */
	//lodsw
	//stosw
	//lodsw
	//stosw
	movb	-10(%si), %al
	andb	$63, %al
	stc
	xchgw	%ax, %si	/* save SI to AX */
	movw	$(partition_sectors_per_track_string - _start1), %si
	jz	2b
	xchgw	%ax, %si	/* restore SI from AX */
	//lodsl
	//stosl
	movl	-8(%si), %eax
	testl	%eax, %eax
	stc
	xchgw	%ax, %si	/* save SI to AX */
	movw	$(partition_start_sector_string - _start1), %si
	jz	2b
	xchgw	%ax, %si	/* restore SI from AX */

	//lodsl
	//stosl
	movl	-4(%si), %eax
	testl	%eax, %eax
	stc
	xchgw	%ax, %si	/* save SI to AX */
	movw	$(partition_end_sector_string - _start1), %si
	jz	2b
	xchgw	%ax, %si	/* restore SI from AX */

	jmp	3b
3:
	cmpw	$0xAA55, (%si)
	stc
	xchgw	%ax, %si	/* save SI to AX */
	movw	$(no_boot_signature_string - _start1), %si
	jnz	2b
	xchgw	%ax, %si	/* restore SI from AX */
	//lodsw
	//stosw			/* store boot signature */

	/* Now the partition table is OK */

	movw	%bx, 12(%bp)	/* adjust BP in the stack */

	movw	$0x1b2, 8(%bp)	/* adjust SI in the stack */

	/* temp change the code:	call	self_modify_once
	 *
	 * "call self_modify_once" at add_sub_si is:
	 *
	 *	.byte	0xE8
	 *	.word	(self_modify_once - add_sub_si - 3)
	 *
	 */
	movb	$0xE8, (add_sub_si - _start1)
	movw	$(self_modify_once - add_sub_si - 3), (add_sub_si + 1 - _start1)

	/* initialize partition number and partition entries end */
	movw	$0xffff, 0x1bc		/* hd partition number */
	movw	$0x01fe, 0x1ba		/* partition entries end */

	jmp	1f
2:
	/* get here if all drives have been checked */
#if 0
	movw	$0x202, 8(%bp)	/* adjust SI in the stack */

	/* restore the original code:	addw	$-4, %si */
	movw	$0xC683, (add_sub_si  - _start1)	/* 0x83, 0xC6 */
	movb	$0xFC, (add_sub_si + 2 - _start1)	/* 0xFC */
#endif
4:
	//--------------------------------------------------------------------
	/* change the code:	jmp	Error_modify
	 *
	 * "jmp Error_modify" at Error_or_prev_MBR:
	 *
	 *	.byte	0xE9
	 *	.word	(Error_modify - Error_or_prev_MBR - 3)
	 *
	 */
	movb	$0xE9, (Error_or_prev_MBR - _start1)
	movw	$(Error_modify - Error_or_prev_MBR - 3), (Error_or_prev_MBR + 1 - _start1)
	//--------------------------------------------------------------------

	//--------------------------------------------------------------------
	/* floppy search disabled ? */
#if 0
	testb	$1, 0x02		/* test bit0 of the third byte */
	jz	1f			/* zero means floppy search enabled */
	/* 0x1fd or below means disable floppy search */
	decw	(add_sub_si + 5 - _start1)
#else
	movb	0x02, %al
	andb	$0x01, %al
	subb	%al, (add_sub_si + 5 - _start1)
#endif
	//--------------------------------------------------------------------

1:
#if 0
	popfw
	lahf			/* Load Flags into AH Register. */
				/* AH = SF:ZF:xx:AF:xx:PF:xx:CF */
				/* CF will be moved to ZF */
	movb	%ah, %al
	andb	$1, %al		/* CF=0 */
	shlb	$6, %al		/* move CF to ZF */
	popfw
	lahf			/* Load Flags into AH Register. */
				/* AH = SF:ZF:xx:AF:xx:PF:xx:CF */
	andb	$0xbf, %ah	/* 0xbf= binary 1011 1111. It clears ZF */
	orb	%al, %ah
#else
	popw	%ax		/* AX=Flags */
	popfw			/* Flags_orig */
	lahf			/* Load Flags_orig into AH Register. */
				/* AH = SF:ZF:xx:AF:xx:PF:xx:CF */
	shlb	$2, %ah
	rorw	$2, %ax		/* move CF of Flags to ZF of Flags_orig */
#endif

	sahf			/* update flags */
				/* current CF is the CF of Flags_orig */
				/* current ZF is the CF of Flags */
	jc	1f		/* CF=1 means failed in loading bootsector */
	popal			/* get drive number DL */
	pushal
	pushfw
	cmpb	$0xff, %cs:0x06
	jz	2f
	movb	%cs:0x1bc, %dh
	testb	%dl, %dl
	js	3f
	movb	$0xff, %dh	/* partition # for floppy is "whole drive" */
3:
	cmpw	%cs:0x06, %dx
	jz	2f
	popfw
	stc
	pushfw
2:
	popfw
1:
	popal
	popw	%es
	popw	%ds
	ret

self_modify_once:
	/* when we get here, SI should be 0x1b2, and BP high holds DL */ 
	addw	$12, %si	/* 0x83, 0xC6, 0x0C */
	movw	%bp, %ax
	movb	%ah, %dl

	/* note: DS=0x9400 */

	/* restore the original code:	addw	$12, %si */
	movw	$0xC683, (add_sub_si  - _start1)	/* 0x83, 0xC6 */
	movb	$0x0C, (add_sub_si + 2 - _start1)	/* 0x0C */
	ret

Error_modify:
	cmpb	$0xff, %cs:0x06	/* preferred drive? */
	jz	1f		/* not active. Turn to the final step. */

	/* preferred drive is already handled, so de-activate it now. */
	movb	$0xff, %cs:0x06

	/* we will do the second pass, from drive 0x80. */
	movb	$0x7f, %dl	/* this will become 0x80 after inc. */

	/* pass "error" to PUSHF, simulating a load failure, in order
	 * to try the first entry after return from the helper function.
	 */

	stc

	pushw	$(helper_call + 3 - _start1)	/* return address */
	pushw	%cs		/* 0x9400, it is for DS. */
	pushw	$FS_BOOT	/* 0x0d00, it is for ES. */
	pushal
	//pushl	%eax
	//pushl	%ecx
	//pushl	%edx
	//pushl	%ebx
	//pushl	%esp
	//pushl	%ebp
	//pushl	%esi
	//pushl	%edi
	pushfw			/* CF=1 */
	pushfw

	pushw	%cs
	popw	%es		/* ES=0x9400 */

	/* redo from start: DL will be 0x80 after inc. */
	jmp	inc_hard_drive
1:
boot_prev_mbr:

	/* prepare to boot the previous MBR */

	/* at this moment DS=0x9400, ES=$FS_BOOT or ES=0x9400 */
	xorw	%ax, %ax
	//pushw	%ax	/* AX=0, for the segment of 0000:7c00 */
	movw	%ax, %es	/* ES=0x0000 */
	movw	%ax, %ds	/* DS=0x0000 */
//	pushw	%ds
//	pushw	%es
	movw	$0x0202, %ax	/* read 2 sectors ... */
	movw	$0x7A00, %bx	/* ... to 0000:7A00 */
	//pushw	%bx	/* BX=0x7c00, for the offset of 0000:7c00 */
	movw	$0x0001, %cx	/* from the first sector ... */
	movw	$0x0080, %dx	/* ... of the first hard drive */
//	stc
//	int	$0x13
	call	int13
	sti
//	popw	%es
//	popw	%ds
	jc	1f
	testb	%ah, %ah
	jnz	1f
	cmpw	$0xAA55, 0x7dfe
	jne	1f
	cmpw	$0xAA55, 0x7bfe
	jne	1f

	/* has a valid partition table ? */
	movw	$0x7dbe, %si
3:
	cmpw	$0x7dfe, %si
	jnb	3f		/* partition table is OK */
	movw	$4, %cx

	movw	%si, %di
2:
	lodsl
	negl	%eax
	jc	2f
	loop	2b
	/* empty entry, check next */
	jmp	3b
2:
	/* non-empty entry */
	movw	%di, %si

	lodsw
	shlb	$1, %al
	jnz	2f
	lodsw
	andb	$63, %al
	jz	2f
	lodsw
	lodsw
	andb	$63, %al
	jz	2f
	lodsl
	negl	%eax
	jnc	2f
	lodsl
	negl	%eax
	jc	3b
2:
	stc		/* invalid partition table */
3:
	pushfw

	/* disable the boot of non-MBR bootsector ? */
	testb	$2, %cs:0x02		/* test bit1 of the third byte */
	jz	2f			/* zero means non-MBR enabled */
	popfw
	jc	1f	/* invalid partition table, print "Error" */	

	/* the partition table is valid */
	pushfw

2:
	/* the check passed, and the boot is permitted */
	popfw

	jc	2f	/* invalid partition table */

	/* use partition table in MBR instead */

	/* copy 72 bytes at 0000:7bb8 to 0000:7db8 */

	movw	$0x7bb8, %si
	movw	$0x7db8, %di
	movw	$36, %cx
	cld
	repz movsw

2:
	testb	$0x80, %cs:0x02		/* test bit 7 of the third byte */
	jz	2f			/* zero means boot prev-MBR first */

	/* Cannot find GRLDR. Press space bar to hold the screen, any other key to boot previous MBR ... */
	movw	$(Cannot_find_GRLDR_string - _start1), %si
	call	print_message	/* CS:SI points to message string */
	movw	$(nt_boot_image - _start1), %si
	call	print_message	/* CS:SI points to message string */
	movw	$(press_space_bar_string - _start1), %si
	movw	$0x3920, %cs:0x04	/* reset hot-key to space bar */
	movb	$15, %cs:0x03		/* reset time out to 15 seconds */
	call	print_message	/* CS:SI points to message string */
	movw	$(prev_MBR_string - _start1), %si
	call	print_message	/* CS:SI points to message string */
3:
	call	sleep_5_seconds		/* the hot-key is SPACE */
	/* if hot-key is pressed, wait forever until another key is pressed. */
	movb	$0xff, %cs:0x03
	jc	3b		/* desired hot-key is pressed */
2:
	/* boot the previous MBR */

	/* clear the DUCE indicator */
	movl	$0, 0x5FC	/* DS=ES=0 */

	//movb	$0x80, %dl
	ljmp	$0, $0x7c00
1:
	/* no previous MBR, print "Error" */
	///* Note the 0000:7C00 is on the stack */
	//popw	%ax	/* AX=0x0000 */
	//popw	%ax	/* AX=0x7C00 */

	testb	$0x80, %cs:0x02	/* are we called prior to the GRLDR search? */
	jnz	1f		/* no, it is a failure at last */
	/* yes, so return to the caller */
	/* Invalid previous MBR. Press any key to start GRUB ... */
	movw	$(continue_string - _start1), %si
	call	print_message	/* CS:SI points to message string */
	call	sleep_5_seconds
	ret
1:
	movw	$(message_string_helper - _start1), %si
	call	print_message	/* CS:SI points to message string */
	movw	$(nt_boot_image - _start1), %si
	call	print_message	/* CS:SI points to message string */
	movw	$(ctrl_alt_del_string - _start1), %si
	call	print_message	/* CS:SI points to message string */
1:	jmp	1b	/* hang */

sleep_5_seconds:
	/* sleep 5 seconds */

	/* sleep forever if %cs:0x03 is 0xff */

	/* calculate the timeout ticks */

	pushw	%ds
	pushl	%esi
	pushl	%edx

	movl	$0xffffffff, %edx
	movzbl	%cs:0x03, %eax
	cmpb	$0xff, %al
	je	1f
	movl	$18, %edx	/* 18.2 ticks per second. We simply use 18. */
	mulw	%dx		/* EDX=0, EAX=ticks */
	xchgw	%ax, %dx	/* EAX=0, EDX=ticks */
1:
	xorw	%ax, %ax
	movw	%ax, %ds
	movl	0x46c, %eax	/* initial tick */
	movl	%eax, %ecx	/* ECX=initial tick */
	testl	%edx, %edx
	js	1f
	addl	%edx, %eax	/* EAX=timeout tick */
	pushl	%eax

	movzbl	%cs:0x03, %eax
	orl	%eax, %eax
	jz	3f

	movw	$(hot_key_timeout_pre - _start1), %si
	pushl	%eax
	call	print_message
	popl	%eax

	movw	$(hot_key_timeout_num - _start1), %si
	call	print_decimal
3:
	movl	%ecx, %esi
	addl	$18, %esi

	popl	%eax
	jmp	3f
1:
	movl	%edx, %eax	/* EAX=0xffffffff */
	movl	%edx, %esi
3:
	movl	0x46c, %ebx	/* EBX=current tick */
	cmpl	%ecx, %ebx
	jnb	2f

	/* current tick is less than initial tick, this means the ticks have
	 * overflowed to the next day, and EBX is rather small. */
	xorl	%ecx, %ecx
	movl	%edx, %eax
	movl	$18, %esi
2:
	/* check if there is any key press. */
	pushl	%eax
	movb	$1, %ah
	int	$0x16
	pushw	%ax
	pushfw

	movb	$0x11, %ah
	int	$0x16
	jnz	1f
	popfw
	jnz	2f

	/* no, there is no key press. */

	popw	%ax
	popl	%eax

	cmpl	%esi, %ebx
	jb	4f
	pushl	%esi
	pushl	%eax
	pushl	%edx


	subl	%esi, %eax
	xorl	%edx, %edx
	movl	$18, %esi
	divl	%esi

	movw	$(hot_key_timeout_num - _start1), %si
	pushl	%ebx
	call	print_decimal
	popl	%ebx

	popl	%edx
	popl	%eax
	popl	%esi
	addl	$18, %esi
4:
	cmpl	%eax, %ebx	/* timeout? */
	jbe	3b		/* no, continue to wait */

	/* timeout reached, CF=0, no key pressed. */
	popl	%edx
	popl	%esi
	popw	%ds
	ret
1:
	popfw
2:
	/* yes, there is a key press. */
#if 0
	/* clear the keyboard buffer */
	movb	$1, %ah
	int	$0x16
	jz	1f	/* no keys, end */
	movb	$0, %ah
	int	$0x16	/* discard the key */
	jmp	1b
1:
#endif

	/* check if it is the desired key. */

	xorw	%cs:0x04, %ax	/* CF=0 */
	popw	%ax
	je	1f
	xorw	%cs:0x04, %ax	/* CF=0 */
	jne	2f		/* not desired, return CF=0 */

	/* remove the desired key from the keyboard buffer. */

	movb	$0, %ah
	int	$0x16	/* discard the key */
	jmp	3f
1:
	/* remove the desired key from the keyboard buffer. */

	movb	$0x10, %ah
	int	$0x16	/* discard the key */
3:
	stc	/* CF=1, the desired key pressed */
2:
	popl	%eax
	popl	%edx
	popl	%esi
	popw	%ds
	ret

out_decimal:
	/*
	 * input: EAX = number, CS:SI = buffer
	 */

	pushl	%edx
	pushl	%ecx
	pushw	%bx

	movl	$10, %ecx
	movw	%si, %bx

1:
	xorl	%edx, %edx
	divl	%ecx
	addb	$'0', %dl
	movb	%dl, %cs:(%si)
	incw	%si
	orl	%eax, %eax
	jnz	1b

	pushw	%si

1:
	decw	%si
	cmpw	%bx, %si
	jbe	1f
	movb	%cs:(%si), %al
	xchgb	%al, %cs:(%bx)
	movb	%al, %cs:(%si)
	incw	%bx
	jmp	1b
1:

	popw	%si

	popw	%bx
	popl	%ecx
	popl	%edx
	ret

print_decimal:
	pushw	%si
	call	out_decimal

1:
	cmpb	$'\b', %cs:(%si)
	jz	2f
	movb	$' ', %cs:(%si)
	incw	%si
	jmp	1b
2:
	popw	%si
	call	print_message
	ret

#if 0
modify_NTFS_boot_record:

	/* before the call:
	 *		AH= partition number
	 *		AL= 0xB6	; 0xB6 is opcode of "MOV DH,imm8"
	 *		DL= drive number
	 *
	 * on return:	CF=0 if there is NTFS boot record;
	 *		CF=1 otherwise. 
	 *		CF of flags_orig on the stack will set if CF=1
	 */

	/* 
	 *
	 * the current stack is:
	 *
	 * SP + 40	: DS
	 * SP + 38	: ES
	 * SP + 34	: EAX
	 * SP + 30	: ECX
	 * SP + 26	: EDX
	 * SP + 22	: EBX
	 * SP + 18	: ESP_temp
	 * SP + 14	: EBP
	 * SP + 10	: ESI
	 * SP +  6	: EDI
	 * SP +  4	: flags_orig
	 * SP +  2	: SI		; SI points to old entry in MBR
	 * SP		: return_IP
	 *
	 */

	/* DS=ES=FS_BOOT */

	/* change NTLDR to GRLDR */

	/* check GR or NT or anything else */

	pushw	%ax

	movw	$0x200, %si
	lodsw
	cmpw	$5, %ax
	jne	1f		/* failure */
	lodsw
	testb	%ah, %ah	/* high byte of unicode ASCII should be 0 */
	jne	1f		/* failure */

	/* 'N' should be a capital letter */

	cmpb	$0x41, %al	/* Less than 'A' */
	jb	1f		/* failure */
	cmpb	$0x5A, %al	/* Greater than 'Z'*/
	ja	1f		/* failure */

	xchgw	%ax, %cx	/* save AX to CX. CL='N' */

	lodsw
	testb	%ah, %ah	/* high byte of unicode ASCII should be 0 */
	jne	1f		/* failure */

	/* 'T' should be a capital letter */

	cmpb	$0x41, %al	/* Less than 'A' */
	jb	1f		/* failure */
	cmpb	$0x5A, %al	/* Greater than 'Z'*/
	ja	1f		/* failure */

	movb	%al, %ch	/* save AL to CH. CH='T' */

	lodsw
	cmpw	$0x4C, %ax	/* 'L' */
	jne	1f		/* failure */
	lodsw
	cmpw	$0x44, %ax	/* 'D' */
	jne	1f		/* failure */
	lodsw
	cmpw	$0x52, %ax	/* 'R' */
	jne	1f		/* failure */
	lodsw
	cmpw	$0x04, %ax	/* length of "$I30" */
	jne	1f		/* failure */
	lodsw
	cmpw	$0x24, %ax	/* '$' */
	jne	1f		/* failure */
	lodsw
	cmpw	$0x49, %ax	/* 'I' */
	jne	1f		/* failure */
	lodsw
	cmpw	$0x33, %ax	/* '3' */
	jne	1f		/* failure */
	lodsw
	cmpw	$0x30, %ax	/* '0' */
	jne	1f		/* failure */

	
	/* assume it is NT bootsector. first, find "NTLDR". CX holds "NT" */
	movw	$0x0100, %di
	movb	%cl, %al	/* AL="N" */
	movb	$1, %ah		/* AH=Carry for SAHF below */
	movl	$0x52444c00, %ebx	/* "LDR" */
	movb	%ch, %bl		/* 'T' */
	movw	$0x00fa, %cx

	/* now AL holds 'N' and BL holds 'T' */

	//cld			/* already upward */
3:
	repnz scasb		/* find "N" */
	jcxz	4f		/* gets the end, exit */
	cmpl	%ebx, (%di)	/* is it "NTLDR"? */
	jnz	3b		/* no, continue to find */

	/* "NTLDR" is found, so we believe it is NT boot sector. */

	movw	$0x5247, -1(%di)	/* change "NT" to "GR" */

	/* CF=0 for now */

	lahf			/* Load Flags into AH */
				/* AH = SF:ZF:xx:AF:xx:PF:xx:CF */
				/* AH = binary xxxxxxx0 */
	jmp	3b
4:
	sahf		/* Store AH into flags SF ZF xx AF xx PF xx CF */

	/* CF=0 means "NTLDR" is found, CF=1 means "NTLDR" is not found. */

	jc	1f		/* failure */

	movl	$0x00520047, 0x202	/* change to "G R L D R" */

	/* check NT 4.0 */

	movw	$0x406, %si
	movl	(%si), %ebx		/* NT 4.0 */
	cmpl	$0x03E8B800, %ebx	/* MOV AX, 03E8 */
	jnz	3f

	movl	0x84, %ebx
	cmpl	$0x680007E8, %ebx	/* call 008e; push (0D00) */
	jnz	3f

//	movw	0x154, %bx		/* CR LF at end of "A disk read error occurred." */
//	cmpw	$0x0A0D, %bx		/* CR LF */
//	jnz	3f
//	movw	0x180, %bx		/* CR LF at end of "A kernel file is missing from the disk." */
//	cmpw	$0x0A0D, %bx		/* CR LF */
//	jnz	3f
//	movw	0x1A8, %bx		/* CR LF at end of "A kernel file is too discontiguous." */
//	cmpw	$0x0A0D, %bx		/* CR LF */
//	jnz	3f
//	movw	0x1F8, %bx		/* CR LF at end of "NTLDR is compressed." */
//	cmpw	$0x0A0D, %bx		/* CR LF */
//	jnz	3f

	movl	0xE8, %ebx
	cmpl	$0x13CD80B2, %ebx	/* "B2 80"="mov DL, 80", "CD 13"="int 13" */
	jnz	3f

	popw	%ax
	movw	%ax, 4(%si)

	movl	$0x68909090, %ebx	/* nop;nop;nop;push (0D00) */
	movl	%ebx, 0x84

//	/* change CRLF in NTFS error messages to spaces */
//	movw	$0x2020, %bx		/* change CRLF to 2 spaces */
//	movw	%bx, 0x154
//	movw	%bx, 0x180
//	movw	%bx, 0x1A8
//	movw	%bx, 0x1F8

	movb	%dl, 0xE9		/* modify drive number */

	/* modify NTFS boot record */
	movb	$0xea, %al	/* ljmp, hand over the control to supervisor */
	movb	%al, 0x122
	//movw	$(try_next_partition - _start1), %ax	/* offset for ljmp */
	movw	$MONITOR, %ax	/* offset for ljmp */
	movw	%ax, 0x123
	//movw	%cs, %ax	/* AX=0x9400, segment for ljmp */
	xorw	%ax, %ax
	movw	%ax, 0x125

	movw	$(NTFS4_message - _start1), %si
	call	print_message	/* CS:SI points to message string */
	clc
	ret
3:
	/* check NT 5.0 */

	movw	$0x44b, %si
	movl	(%si), %ebx		/* NT 5.0 */
	cmpl	$0x03E8B800, %ebx	/* MOV AX, 03E8 */
	jz	2f

	movw	$0x479, %si
	movl	(%si), %ebx		/* NT 5.1 SP2 */
	cmpl	$0x03E8B800, %ebx	/* MOV AX, 03E8 */
	jnz	1f
2:
	movl	0x71, %ebx
	cmpl	$0x680053E8, %ebx	/* call 00C7; push (0D00) */
	jnz	1f

	//movw	0x183, %bx		/* CR LF at begin of "A disk read error occurred." */
	movb	0x1F8, %bl
	movb	$1, %bh
	movw	(%bx), %bx
	cmpw	$0x0A0D, %bx		/* CR LF */
	jnz	1f
	//movw	0x1A0, %bx		/* CR LF at begin of "NTLDR is missing." */
	movb	0x1F9, %bl
	movb	$1, %bh
	movw	(%bx), %bx
	cmpw	$0x0A0D, %bx		/* CR LF */
	jnz	1f
	//movw	0x1B3, %bx		/* CR LF at begin of "NTLDR is compressed." */
	movb	0x1FA, %bl
	movb	$1, %bh
	movw	(%bx), %bx
	cmpw	$0x0A0D, %bx		/* CR LF */
	jnz	1f

	popw	%ax
	movw	%ax, 4(%si)

	movl	$0x68909090, %ebx	/* nop;nop;nop;push (0D00) */
	movl	%ebx, 0x71

	/* change CRLF in NTFS error messages to spaces */
	movw	$0x2020, %ax
	movb	0x1F8, %bl
	movb	$1, %bh
	movw	%ax, (%bx)	// 0x183
	movb	0x1F9, %bl
	movb	$1, %bh
	movw	%ax, (%bx)	// 0x1A0
	movb	0x1FA, %bl
	movb	$1, %bh
	movw	%ax, (%bx)	// 0x1B3

	/* modify NTFS boot record */
	movb	$0xEA, %al	/* ljmp, hand over the control to supervisor */
	movb	%al, 0x167
	//movw	$(try_next_partition - _start1), %ax	/* offset for ljmp */
	movw	$MONITOR, %ax	/* offset for ljmp */
	movw	%ax, 0x168
	//movw	%cs, %ax	/* AX=0x9400, segment for ljmp */
	xorw	%ax, %ax
	movw	%ax, 0x16A

	cmpw	$0x44b, %si
	jne	2f
	movw	$(NTFS5_message - _start1), %si
	jmp	3f
2:
	movw	$(NTFS5p_message - _start1), %si
3:
	call	print_message	/* CS:SI points to message string */
	clc
	ret
1:
	/* NTFS boot record not found. */

	movw	$(NTFS_no_boot_record_message - _start1), %si
	call	print_message	/* CS:SI points to message string */

	popw	%ax
	popl	%eax			/* return_IP and SI */
	popfw
	stc
	pushfw
	pushl	%eax			/* return_IP and SI */
	ret
#endif

//#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))
move_helper:
	
	/* called only once and only when the boot loader loaded this code */
	pushw	%si
	pushw	%bx
	pushl	%eax

	movw	$0x0003, %ax	/* set display mode: 80*25 color text */
	int	$0x10

	movw	$0x200, %si	/* move from the 2nd sector */
	movw	%si, %di
	movw	$0x3E00, %cx	/* move 0x3E=62 sectors */
	cld
	repz movsw

	popl	%eax
	popw	%bx
	popw	%si
	ret
//#endif

#if (defined(GRLDR_MBR)) || (defined(GRLDR_INSTALL))
set_floppy_preferred:
	movw	$0xff00, 0x06	/* preferred drive=0, partition=0xff */
	andb	$0xFE, 0x02	/* bit0=0, enable GRLDR search on floppy */
	ret

filesystem_boot:
	/* The partition boot record successfully modified, just boot it */

	/*
	 * The boot might fail, but we want to take back the control.
	 * So we save the registers now.
	 */
	pushw	%ds
	pushw	%es
	pushal

	/* DS=CS=GRLDR_CS, ES=FS_BOOT */

	/* save GRLDR_CS */

	movw	%es, %bx	# save old ES to BX

	cli
	lgdt	gdt - _start1
	movl	%cr0, %eax
	orb	$1, %al
	movl	%eax, %cr0

	movw	$8, %si
	movw	%si, %es

	xorl	%esi, %esi
	xorl	%edi, %edi
	movl	$(0x9000 / 4), %ecx

	cld
	repz movsl

	movw	$16, %si
	movw	%si, %es

	andb	$0xfe, %al
	movl	%eax, %cr0

	movw	%bx, %es	# restore ES from BX

	/* move FS_BOOT:0000 to 0:7c00 */
#if 0
	/* for single sector boot record */
	movw	$0x0200, %cx	/* move 2 sectors, the old FS_BOOT:0000 will keep untouched.  */
#else
	/* for 4-sector NTFS boot record */
	movw	$0x0400, %cx	/* move 4 sectors, the old FS_BOOT:0000 will keep untouched.  */
#endif
	xorw	%si, %si
	pushw	%si	/* SI=0, for the segment of 0000:7c00 */
	movw	$0x7c00, %di
	pushw	%di	/* DI=0x7c00, for the offset of 0000:7c00 */
	pushw	%es	/* ES=FS_BOOT */
	popw	%ds	/* DS=FS_BOOT */
	pushw	%si	/* SI=0 */
	popw	%es	/* ES=0 */
	cld
	repz movsw

	movw	$MONITOR, %di
	movw	$(restore_GRLDR_CS - _start1), %si
	movw	$((gdt_end - restore_GRLDR_CS) / 4), %cx
	cld
	repz cs movsl		/* CS segment override prefix(=0x2E) */

	pushw	%es	/* ES=0 */
	popw	%ds	/* DS=0 */
	sti
	lret	//ljmp	$0, $0x7c00
#endif

geometry_tune:

	/* on call:
	 *		CS=DS=SS
	 *		ES=FS_BOOT
	 *
	 * on return:
	 *		CL	max sector number
	 *		DH	max head number
	 *		DS	changed
	 *		ES	changed
	 *		AX	changed
	 *		BX	changed
	 *		CX	changed
	 *   byte at CS:[08]	updated on success(Smax)
	 *   byte at CS:[09]	updated on success(Hmax)
	 */


	testb	%dl, %dl		/* floppy? */
	jns	1f			/* yes, continue to tune. */

	cmpw	$0x1c2, %si		/* first run on this hard drive? */
	jne	2f			/* no, avoid tuning again. */
1:
	movw	$0xffff, 0x08

#if (defined(GRLDR_MBR)) || (defined(GRLDR_INSTALL))
	cmpb	$0x42, 0x00	/* EBIOS present? */
	je	2f		/* yes, skip the tune */

	#; real geometry tune follows. if you wish to disable the tune,
	#; just do a 'ret' here.
	//ret		#; disable the tune

	testb	$0x08, 0x02	/* chs-no-tune */
	jnz	2f

	/* check if the code is loaded completely */

	cmpl	$0xAA555247, (grldr_signature - _start1) /* "GR" 0x55 0xAA */
	je	real_geometry_tune

#endif
2:
	ret

press_space_bar_string:
	.ascii	"\r\nPress space bar\0"

press_hot_key_pre:
	.ascii "\r\nPress \0"

press_hot_key_sub:
	.ascii	" to start GRUB, any other key to boot previous MBR ...\0"
press_hot_key_sub1:
	.ascii	" to boot previous MBR, any other key to start GRUB ...\0"

hot_key_timeout_pre:
	.ascii "\r\nTimeout : \0"

hot_key_timeout_num:
	.ascii "   \b\b\b\0"

continue_string:
	.ascii	"\r\nInvalid previous MBR. Press any key to start GRUB ...\0"

Cannot_find_GRLDR_string:
	.ascii	"\r\nCannot find \0"

prev_MBR_string:
	.ascii	" to hold the screen, any other key to boot previous MBR ...\0"

Error_while_reading_string:
	.ascii	"\r\nError while reading MBR of \0"

drive_number_string:
	.ascii	" in partition table of drive (hd0 ) \0"

partition_boot_indicator_string:
	.ascii	"\r\nInvalid boot indicator\0"

partition_sectors_per_track_string:
	.ascii	"\r\nInvalid sectors_per_track\0"

partition_start_sector_string:
	.ascii	"\r\nInvalid start_sector\0"

partition_end_sector_string:
	.ascii	"\r\nInvalid end_sector\0"

no_boot_signature_string:
	.ascii	"\r\nNo boot signature\0"

message_string_helper:
	.ascii	"\r\nError: Cannot find \0"
ctrl_alt_del_string:
	.ascii	" in all drives. Press Ctrl+Alt+Del to restart.\0"

partition_message:
	.ascii	"\r\nTry (hd0,0 ) : \0"

EXT2_message:
	.ascii	"EXT2: \0"

#if 0
NTFS4_message:
	.ascii	"NTFS4: \0"
NTFS5p_message:
	.ascii	"NTFS5p: \0"
#endif

NTFS5_message:
	.ascii	"NTFS5: \0"
FAT32_message:
	.ascii	"FAT32: \0"
FAT16_message:
	.ascii	"FAT16: \0"
FAT12_message:
	.ascii	"FAT12: \0"
non_MS_message:
	.ascii	"non-MS: skip \0"
extended_message:
	.ascii	"Extended: \0"
invalid_message:
	.ascii	"invalid or null \0"

#if (defined(GRLDR_MBR)) || (defined(GRLDR_INSTALL))

	//. = . + (0x3e8 - ((. - _start1) % 0x200)) % 0x200
	. = _start1 + 0x1FE8

press_hot_key_name:

	/* hot key name, the address is (grldr_signature - 16) */

	.ascii  "hot-key\0"

	/* grldr.mbr is larger than 8K. */

	######################################################################
	# The installer should setup the long integer at offset 0x1FFC as
	# the unique disk signature. The same signature value must be also
	# placed into the disk_serial_number_structure in the first sector(the
	# MBR sector). You can easily locate the structure through the pointer
	# at offset 0x1FF8.
	#
	# For GRLDR.MBR the default disk serial number is the grldr.mbr
	# signature(0x93cb4d05). You should change it according to the
	# date-time value just at the time when you run the installer.
	######################################################################

	. = _start1 + 0x1FF8

	/* point to disk serial number in the first sector, i.e., the MBR
	 * sector. The program never access this pointer. It can be used by
	 * an external program to easily locate the disk serial number at MBR.
	 */

	.word	disk_serial_number_structure - _start1 + 5

	. = _start1 + 0x1FFA

	/* version of grldr.mbr. It has a copy at (grldr_signature - 2) */

	.word   4

	. = _start1 + 0x1FFC

	.long	0x93cb4d05		/* date-time for disk serial number */

	. = _start1 + 0x2000

real_geometry_tune:

//////////////////////////////////////////////////////////////////////////////

	/* initialize passed-in values */

	pushaw

	xorl	%eax, %eax
	movl	%eax, %cs:(Sectors_passed_in - _start1)
	movl	%eax, %cs:(Heads_passed_in - _start1)

	movb	$8, %ah		/* read drive parameters changes DX,ES,DI,BX */
	//movb	$0x80, %dl	/* BIOS drive number is in DL */
	int	$0x13
	jc	1f		/* failed */
	testb	$63, %cl
	jz	1f		/* failed */

	andb	$63, %cl	/* sectors per track */

	movb	%cl, %cs:(Sectors_passed_in - _start1)
	incb	%dh
	movb	%dh, %cs:(Heads_passed_in - _start1)	/* 0 for 256 */
1:
	popaw

	/* print BIOS geometry */

	movzbw	%cs:(Sectors_passed_in - _start1), %cx
	pushw	%cx
	movzbw	%cs:(Heads_passed_in - _start1), %cx
	pushw	%cx
	movzbw	%dl, %cx
	pushw	%cx
	pushw	$(BIOS_geom_string - _start1)
	call	realmode_printf
	addw	$8, %sp

//////////////////////////////////////////////////////////////////////////////

	/* get maximum sector number */

	movw	$63, %cx	/* cylinder=0, sector=Max possible */
1:
	movw	$0x5000, %ax
	movw	%ax, %es
	movw	%ax, %ds
	xorw	%bx, %bx
	movw	$0x201, %ax	/* read 1 sector */
	movb	$0, %dh		/* head=0 */
	pushaw
	movw	%bx, %si
	movw	%bx, %di
	int	$0x13
	popaw
	jnc	1f		/* found Max sector */
	loop	1b
2:
	movb	$1, %ah		/* failure */
	ret
1:

	/* CX=Max Sector */
	movw	%cx, %cs:(Smax_tuned - _start1)

//////////////////////////////////////////////////////////////////////////////

	/* check if we can read sectors across the track boundary */

	movb	$0, %cs:(cross_track - _start1)

	movw	$1, %cx		/* sector 1, cylinder 0 */
	movb	$0, %dh		/* head 0 */
	movb	%cs:(Smax_tuned - _start1), %al	/* sectors to read */
	incw	%ax		/* read 1 more sector */
	movb	$2, %ah		/* READ */
	movw	$0x5000, %bx
	movw	%bx, %es
	movw	%bx, %ds
	xorw	%bx, %bx
	pushaw
	movw	%bx, %si
	movw	%bx, %di
	int	$0x13
	popaw
	jc	1f		/* cross-track read is not supported */

	/* read again normally */

	movb	%cs:(Smax_tuned - _start1), %al	/* sectors to read */
	movb	$2, %ah		/* READ */
	movw	$0x5800, %bx
	movw	%bx, %es
	movw	%bx, %ds
	xorw	%bx, %bx
	pushaw
	movw	%bx, %si
	movw	%bx, %di
	int	$0x13
	popaw
	jc	2b		/* failure */

	/* compare the two tracks */

	pushw	%cx
	pushw	%si
	pushw	%di
	movw	%cs:(Smax_tuned - _start1), %cx	/* sectors */
	shlw	$7, %cx				/* dwords */
	movw	$0x5000, %ax
	movw	%ax, %ds
	movw	$0x5800, %ax
	movw	%ax, %es
	xorw	%si, %si
	xorw	%di, %di
	cld
	repz cmpsl
	popw	%di
	popw	%si
	popw	%cx
	jne	1f		/* cross-track read is not supported */
	movb	$1, %cs:(cross_track - _start1)
1:

//////////////////////////////////////////////////////////////////////////////

	/* get maximum head number */

	movb	$0xFF, %dh	/* head=Max possible */
1:
	movw	$0x5000, %ax
	movw	%ax, %es
	movw	%ax, %ds
	xorw	%bx, %bx
	movw	$0x201, %ax	/* read 1 sector */
	movw	$1, %cx		/* cylinder=0, sector=1 */
	pushaw
	movw	%bx, %si
	movw	%bx, %di
	int	$0x13
	popaw
	jnc	1f		/* found Max head */
	decb	%dh
	cmpb	$0xFF, %dh
	jne	1b
	movb	$1, %ah		/* failure */
	ret
1:

	/* DH=Max head */
	movb	%dh, %cs:(Hmax_tuned - _start1)

//////////////////////////////////////////////////////////////////////////////

	/* tune Hmax */

	/* First, try the passed-in value */
	movb	%cs:(Heads_passed_in - _start1), %dh
	testb	%dh, %dh
	jz	1f		/* the passed-in heads = 0x100 */

	call	tune_heads
	jb	2f		/* failure */
	ja	4f		/* success */
1:
	movb	$1, %dh		/* Hmax: 1 - 255 */
1:
	call	tune_heads
	jb	2f		/* failure */
	ja	4f		/* success */

	cmpb	%cs:(Hmax_tuned - _start1), %dh
	ja	2f		/* this should not happen */
	je	5f

	incb	%dh		/* Next Hmax */
	jnz	1b

	/* Hmax=0xFF */
4:
	/* got Hmax=DH-1 */

	decb	%dh
	movb	%dh, %cs:(Hmax_tuned - _start1)
5:
	/* Hmax is tuned ok. */

//////////////////////////////////////////////////////////////////////////////

	/* tune Smax */

	/* First, try the passed-in value */
	movb	%cs:(Sectors_passed_in - _start1), %cl
	
	cmpb	$8, %cl
	jb	1f

	cmpb	$0, %cs:(cross_track - _start1)
	jnz	4f
	cmpb	%cs:(Smax_tuned - _start1), %cl
	jnb	1f
4:
	call	tune_sectors
	jb	2f		/* failure */
	ja	4f		/* success */
1:
	movb	$8, %cl		/* Smax: 8 - 63 */
1:
	call	tune_sectors
	jb	2f		/* failure */
	ja	4f		/* success */

	incw	%cx		/* Next Smax */
	cmpb	%cs:(Smax_tuned - _start1), %cl
	jb	1b

4:
	/* got Smax=CL */

	movb	%cl, %cs:(Smax_tuned - _start1)

	/* Smax is tuned ok. */

//////////////////////////////////////////////////////////////////////////////

	/* print tuned geometry */

	movzbw	%cs:(Smax_tuned - _start1), %cx
	pushw	%cx
	movzbw	%cs:(Hmax_tuned - _start1), %cx
	incw	%cx
	pushw	%cx
	movzbw	%dl, %cx
	pushw	%cx
	pushw	$(TUNE_geom_string - _start1)
	call	realmode_printf
	addw	$8, %sp

	/* return with success */

	movw	%cs:(Smax_tuned - _start1), %cx
	movb	%cs:(Hmax_tuned - _start1), %dh
	movb	%cl, %cs:0x08	/* Smax */
	movb	%dh, %cs:0x09	/* Hmax */
	movb	$0, %ah		/* success */
	ret
2:
	movb	$1, %ah		/* failure */
	ret

//////////////////////////////////////////////////////////////////////////////

tune_heads:

	/* input:	DH = MaxHead + 1 */

	movb	$0, %ch		/* cylinder: 0 - 3 */
2:
	/* read ending track of this cylinder */

	movb	$1, %cl		/* sector 1=the leading sector */
	movb	$2, %ah		/* READ */
	movb	%cs:(Smax_tuned - _start1), %al	/* sectors to read */
	movw	$0x5000, %bx
	movw	%bx, %es
	movw	%bx, %ds
	xorw	%bx, %bx
	pushaw
	movw	%bx, %si
	movw	%bx, %di
	int	$0x13
	popaw
	jc	2f		/* failure */

	/* read beginning track of the next cylinder */

	incb	%ch		/* next cylinder */

	pushw	%dx		/* save DH */

	movb	$0, %dh

	movb	$1, %cl		/* sector 1=the leading sector */
	movb	$2, %ah		/* READ */
	movb	%cs:(Smax_tuned - _start1), %al	/* sectors to read */
	movw	$0x5800, %bx
	movw	%bx, %es
	movw	%bx, %ds
	xorw	%bx, %bx
	pushaw
	movw	%bx, %si
	movw	%bx, %di
	int	$0x13
	popaw
	popw	%dx		/* restore DH */
	jc	2f		/* failure */

	/* compare the two tracks */

	pushw	%cx
	pushw	%si
	pushw	%di
	movw	%cs:(Smax_tuned - _start1), %cx	/* sectors */
	shlw	$7, %cx				/* dwords */
	movw	$0x5000, %ax
	movw	%ax, %ds
	movw	$0x5800, %ax
	movw	%ax, %es
	xorw	%si, %si
	xorw	%di, %di
	cld
	repz cmpsl
	popw	%di
	popw	%si
	popw	%cx
	jne	3f		/* Next Hmax */

	cmpb	$4, %ch
	jb	2b		/* Next cylinder */

	/* all passed, DH-1 is the final Hmax */
	cmpb	$0, %dh
	je	2f		/* failure */
	ret			/* Flag: above */
3:
	cmpb	%dh, %dh	/* Flag: equal */
	ret
2:
	stc			/* Flag: below */
	ret

//////////////////////////////////////////////////////////////////////////////

tune_sectors:

	/* input:	CL = MaxSector */

	movw	$10, %cs:(Smax_count - _start1)

	movb	$0, %ch		/* cylinder: 0 - 7 */
	movb	$0, %dh		/* head: 0 - Hmax */
6:
	/* read ending sector of this track. */

	movw	$0x202, %ax	/* read 2 sectors */
	movw	$0x5000, %bx
	movw	%bx, %es
	movw	%bx, %ds
	xorw	%bx, %bx
	pushaw
	movw	%bx, %si
	movw	%bx, %di
	int	$0x13
	popaw
	jc	2f		/* failure */

	/* read beginning sector of the next track. */

	incb	%dh		/* next track */

	pushw	%cx		/* save CL */

	movb	$1, %cl		/* sector 1=the leading sector */

	movw	$0x201, %ax	/* read 1 sector */
	movw	$0x5800, %bx
	movw	%bx, %es
	movw	%bx, %ds
	xorw	%bx, %bx
	pushaw
	movw	%bx, %si
	movw	%bx, %di
	int	$0x13
	popaw
	popw	%cx		/* restore CL */
	jc	2f		/* failure */

	/* compare the two sectors */

	pushw	%cx
	pushw	%si
	pushw	%di
	movw	$0x80, %cx	/* 1 sector == 0x80 dwords */
	movw	$0x5020, %ax
	movw	%ax, %ds
	movw	$0x5800, %ax
	movw	%ax, %es
	xorw	%si, %si
	xorw	%di, %di
	cld
	repz cmpsl
	popw	%di
	popw	%si
	popw	%cx
	jne	3f		/* Next Smax */

	decw	%cs:(Smax_count - _start1)
	jz	6f

	cmpb	%cs:(Hmax_tuned - _start1), %dh
	jb	6b		/* Next track */

	movb	$0, %dh
	incb	%ch
	cmpb	$7, %ch
	jb	6b		/* Next track */
6:
	/* all passed, CL is the final Smax */
	cmpb	$1, %cl
	jbe	2f		/* failure */
	ret			/* Flag: above */
3:
	cmpb	%cl, %cl	/* Flag: equal */
	ret
2:
	stc			/* Flag: below */
	ret

#;============================================================================

/* void realmode_printf(const char *format, ...)
 *
 * input:	format is offset in CS segment
 * 
 * Usage example:
 * 
 * 		pushw	IntegerN
 *		 ... ... ... ...
 * 		pushw	Integer2
 * 		pushw	Integer1
 * 		pushw	$format_string - _start1
 *		call	realmode_printf
 * 		addw	$(2*(N+1)), %sp
 * 
 * where int13_handle should be the base of the CS segment,
 * and format_string like this:
 *
 * format_string:
 *		 .string "Int1=%x, Int2=%x, ..., IntN=%x\r\n"
 *
 * Currently only %d, %x and %X are implemented.
 */

realmode_printf:
	pushaw
	movw	%sp, %bp
	# bp+18:	format
	# bp+20:	variables
	addw	$18, %bp
	movw	(%bp), %si		# points to format string
	addw	$2, %bp			# (%bp) is the first variable
1:
	cs lodsb
	testb	%al, %al
	jz	1f
	cmpb	$'%', %al
	jne	2f

	#; %d, %x, %X

	cs lodsb
	testb	%al, %al
	jz	1f
	cmpb	$'d', %al
	movw	$10, %bx		# base 10
	jz	4f
	cmpb	$'x', %al
	jz	3f
	cmpb	$'X', %al
	jne	1b			# unkown directive, continue
3:
	/* print hexa number */
	movw	$16, %bx		# base 16
4:
	/* print decimal or hexa number */
	pushl	%edi

	xorl	%edi, %edi
	xorw	%cx, %cx		# count the digits
	movw	(%bp), %ax
5:
	xorw	%dx, %dx
	divw	%bx			# AX=quo, DX=rem
	movw	%dx, %di
	rorl	$4, %edi
	incw	%cx
	testw	%ax, %ax		# end?
	jnz	5b

	/* print the digits in EDI */
	xorw	%bx, %bx	/* video page 0 */
5:
	roll	$4, %edi
	movw	%di, %ax		# get digit in AL
	andb	$0x0f, %al
	cmpb	$9, %al
	jbe	6f
	addb	$7, %al			# A, B, C, D, E, F
6:
	addb	$0x30, %al
	movb	$0x0e, %ah	/* print it */
	int	$0x10		/* via TTY mode */
	loop	5b

	popl	%edi

	addw	$2, %bp			# (%bp) is the next variable
	jmp	1b			# continue
2:
	/* print char in AL */
	xorw	%bx, %bx	/* video page 0 */
	movb	$0x0e, %ah	/* print it */
	int	$0x10		/* via TTY mode */
	jmp	1b			# continue
1:
	popaw
	ret

#;============================================================================
//////////////////////////////////////////////////////////////////////////////

BIOS_geom_string:
	.string	"\r\nBIOS: Drive=0x%X, H=%d, S=%d\r\n"
TUNE_geom_string:
	.string	"TUNE: Drive=0x%X, H=%d, S=%d\r\n"

	.align	4

Sectors_passed_in:
	.long	0
Heads_passed_in:
	.long	0
Smax_tuned:
	.word	0
Hmax_tuned:
	.word	0
Smax_count:
	.word	0
cross_track:
	.byte	0

//////////////////////////////////////////////////////////////////////////////

#endif	/* end of real_geometry_tune */

#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))
	######################################################################
	# External modifiers may setup a long integer at offset 0x1FFC as the
	# unique disk signature. The same signature value must be also placed
	# into the disk_serial_number_structure in the first sector(the MBR
	# sector). You can easily locate the structure through the pointer at
	# offset 0x1FF8.
	#
	# For GRLDR the default disk serial number is the grldr signature
	# ("GR" 0x55 0xAA). Generally you needn't change it, though you are
	# allowed to change it through an external modifier.
	######################################################################

	. = _start1 + 0x1FF8

	/* point to disk serial number in the first sector, i.e., the MBR
	 * sector. The program never access this pointer. It can be used by
	 * an external program to easily locate the disk serial number at MBR.
	 */

	.word	disk_serial_number_structure - _start1 + 5

	. = _start1 + 0x1FFA
#else
	. = . + (0x3fa - ((. - _start1) % 0x200)) % 0x200
#endif

	/* version word of grldr.mbr, the address is (grldr_signature - 2) */

	.word   4

grldr_signature:
	.byte	0x47, 0x52, 0x55, 0xaa	/* signature for helper */

	.align	0x200

#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))

	/* pre_stage2 start at 0x2000 for grldr */

	. = _start1 + 0x2000

#endif

#if defined(GRLDR_MBR)
	/* if the size is less than 8192, let it be 8192 */
	. = . + (0x2000 - (. - _start1)) * (0x4000 / (. - _start1 + 0x2001))
#endif

pre_stage2_start:



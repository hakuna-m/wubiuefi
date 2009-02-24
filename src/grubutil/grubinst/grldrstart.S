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
//#include <shared.h>
#define ASM_FILE

#ifndef STAGE1_5
//#include <stage2_size.h>
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

	/* 1 byte at offset 0x00 will be overwritten for the EBIOS indicator
	 * later. This is safe because the jmp instruction only get executed
	 * once. The write happens after the jmp instruction have got
	 * executed.
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
			/* bit7=1: disable the boot of the previous MBR prior
				   to the search for GRLDR */

	/* GRLDR.MBR uses offset 0x03 to indicate a timer counter. */

	/* 0xff indicates waiting forever,
	 * other value specifies the time in seconds to wait */

	. = _start1 + 0x03

	.byte	5

	/* a key press to wait. if AX returned from int16 equals this word,
	 * the desired action will occur. */

	. = _start1 + 0x04

	.word	0x3920		/* the space bar */

	. = _start1 + 0x06

	.byte	0xff	/* preferred boot drive number, 0xff for no-drive(i.e., drive not defined) */
	.byte	0xff	/* preferred partition number, 0xff for whole drive(a floppy that has no partition table) */

	. = _start1 + 8

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

	pushw	%bx			/* BX:0000=_start1 */
	addw	$((grldr_signature - _start1 + 4 + STAGE2_SIZE - 4) >> 4), %bx
	movw	%bx, %ds

	cmpl	$0xCE1A02B0, ((STAGE2_SIZE - 4) & 0x0F)
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
	/* DS:0000=_start1 */

	/* Let CS:0000=_start1 */
	pushw	%ds

	#;pushw	$(1f - _start1)
	.byte	0x6A, (1f - _start1)

	lret
	. = . - (. - _start1) / 0x80
1:
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
	testb	$0x04, 0x02
	jz	1f

	/* set the DUCE indicator */
	xorw	%ax, %ax
	movw	%ax, %es
	movw	$0x5FC, %di
	movl	$0x45435544, %eax
	stosl
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
	pushw	%dx
	movb	$8, %ah		/* read drive parameters changes DX,ES,DI */
	stc
	int	$0x13
	popw	%dx
	popw	%ax		/* AX=0 */

	pushw	%ss		/* SS=0x9400 */
	popw	%es		/* ES=0x9400 */

	jc	Error1

	andb	$63, %cl	/* AL=sectors per track, CF cleared */

	stc
	jz	Error1

	xchgw	%ax, %cx	/* this moves CL to AL, and CX=0 */
	movb	$0x02, %ah
	movw	%ax, %bp	/* save AX to BP: read 1 track */
	xorw	%bx, %bx	/* ES already has a known value of 0x9400 */
	incw	%cx
	pushw	%dx
	stc
	int	$0x13		/* read master boot track to ES:0000 */
	popw	%dx
	jc	Error1
	negb	%ah		/* set CF=1 if non-zero */
Error1:
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

	movw	$(grldr_signature - _start1), %bx

	/* if the boot loader has loaded more than one sector, we use them */
	movl	$0xAA555247, %eax	/* "GR" 0x55 0xAA */
//#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))
	cmpl	%eax, (%bx)		/* DS=old segment! */
	jne	1f

	/* The MOVE_HELPER code is in the old segment! */

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

	movw	0x18, %ax	/* BPB sectors per track at offset 0x18 */

	cmpw	$0x3F, %ax
	ja	3f

	cmpb	$((pre_stage2_start - _start1) >> 9), %al
	jb	3f

	decw	%ax		/* skip the first sector already loaded */

	movw	$3, %di		/* retry 3 times on read failure */
2:
	movb	$2, %ah		/* BIOS disk read */
	cwd			/* DX=0 for floppy head 0 */
	movw	$0x200, %bx	/* ES:BX immediately follow this sector */
	movw	$2, %cx		/* skip the first sector already loaded */

	pushaw
	int	$0x13
	popaw

	jnc	3f

	pushaw
	xorw	%ax, %ax
	int	$0x13
	popaw

	decw	%di
	jnz	2b
3:
	popal
	cmpl	%eax, (%bx)		/* helper loaded? */

	jne	Error_or_prev_MBR	/* Missing helper */

1:
#endif

	popfw			/* CF=1 on error */
	jc	try_floppy	/* harddisk (hd0) failed, try floppy (fd0) */
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
	xorw	%bx, %bx

	pushaw
	int	$0x13		/* read partition boot track to FS_BOOT:0000 */
	popaw

	jnc	helper_call

	pushaw
	xorw	%ax, %ax
	int	$0x13
	popaw

	decw	%di
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
	movb	$0x08, %ah	/* read drive parameters changes DX,ES,DI */
	cwd			/* DL=0 for floppy */
	pushw	%dx		/* DX=0 */
	int	$0x13
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
Error2:
	call	print_message	/* CS:SI points to message string */
3:	jmp	3b

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
	movw	$0x0200, %cx	/* move 2 sectors, the old FS_BOOT:0000 will
				 * keep untouched.  */
#else
	/* for 4-sector NTFS boot record */
	movw	$0x0400, %cx	/* move 4 sectors, the old FS_BOOT:0000 will
				 * keep untouched.  */
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

	/* DS points to the sector start, but CS does not. */

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
	int	$0x13

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


#endif	/* ! defined(GRLDR_MBR) && (! defined(GRLDR_INSTALL)) */

	. = _start1 + 0x1fe	/* boot signature */

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
	popw	%bx		/* BX = old_DS = load_segment */
	pushw	%bx
	movw	%bx, %es
	addw	$0x0080, %bx	/* buffer segment */
	call	load_cd_sector

	/* compare the two sectors */
	movw	$0x200, %cx
	movw	%bx, %ds
	xorw	%si, %si
	xorw	%di, %di
	cld
	repz cmpsl
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
	 */

	movw	$0x1A0, %si

	/* disk address packet */
	movl	$0x00010010, (%si)	/* load 1 sector each time. */
	movw	$0, 4(%si)		/* buffer offset=0 */
	movw	%bx, 6(%si)		/* buffer segment */
	movl	%eax, 8(%si)		/* LBA lo 32 bits */
	movl	$0, 12(%si)		/* LBA hi 32 bits */

	pushal
	movb	$0x42, %ah
	int	$0x13
	popal
	ret

load_the_rest:

	/* load all sectors (except the first one) */

	/* EAX = first sector(LBA) of GRLDR */

	popw	%bx		/* BX = old_DS = load_segment */
	pushw	%bx
	movw	%bx, %es
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
	pushw	%cs
	popw	%ds

	/* CS=DS=BX, CS:0000 = _start1 */

	addw	$((pre_stage2_start - _start1) >> 4), %bx

	/* BX:0000 = pre_stage2_start */

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

	xorw	%bx, %bx
	movw	$(launch_pre_stage2 - _start1), %si
	call	print_message	/* CS:SI points to message string */

	xorw	%ax, %ax
	movw	%ax, %ss
	movw	$0x2000, %sp

	sti

	ljmp	$0, $0x8200

launch_pre_stage2:
	.ascii	"\r\n\r\nBooting GRLDR...\r\n"

	.byte	0		/* mark the end of ascii zero string */

default_config_file:
//#ifndef PRESET_MENU_STRING
	.ascii	"/menu.lst"
//#else
//	.ascii	"[default menu is disabled]"
//#endif

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
	movw	%ax, %ds
	movw	$0x7c00, %bp

#ifdef	BOOTGRUB
	movw	%ax, %es
#else
	movw	$0x1fe0, %ax
	movw	%ax, %es
	movw	%bp, %si	/* move from 0000:7c00 */
	movw	%bp, %di	/* move to 1fe0:7c00 */
	movw	$0x0100, %cx	/* one sector to move */
	repz movsw
	ljmp	$0x1fe0, $(1f - Entry_32 + 0x7c00)
1:
	movw	%ax, %ds
#endif
	movw	%ax, %ss	/* stack and BP-relative moves up, too */
	leaw	-0x20(%bp), %sp
	sti
	movw	%dx, 0x40(%bp)	/* BIOS passes drive number in DL */

	movb	$0x41, %ah
	movw	$0x55AA, %bx
	int	$0x13
	jc	1f		/* No EBIOS */
	cmpw	$0xAA55, %bx
	jne	1f		/* No EBIOS */
	testb	$1, %cl
	jz	1f		/* No EBIOS */
	/* EBIOS supported */
	movb	$0x42, (ebios_32 - 1 - Entry_32 + 0x7c00)
1:

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
	movl	0x10(%bp), %eax	/* number of fats, no movzbl needed: the
				   2 words after 0x10(%bp) are 0 for fat32 */
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
	addl	0x48(%bp), %eax	/* add the first FAT sector number.
				   EAX is absolute sector number now */
	movw	$FATSEG, %bx
	movw	%bx, %es
	xorw	%bx, %bx

	cmpl	0x44(%bp), %eax	/* is it the last accessed and already buffered
				   FAT sector? */
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

//	cmpb	$0x0e, 2(%bp)	/* force LBA? */
//	jnz	1f		/* no, continue */
//	movb	$0x42, %ah	/* yes, use extended disk read */
//1:
	movw	%sp, %si	/* DS:SI points to disk address packet */
	movb	0x40(%bp), %dl	/* hard disk drive number */
	int	$0x13
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

	. = . - (. - readDisk_32)/91

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
	movw	%ax, %ds
	movw	$0x7c00, %bp

#ifdef	BOOTGRUB
	movw	%ax, %es
	movw	%ax, %ss	/* stack and BP-relative moves up, too */
	leaw	-0x20(%bp), %sp
	sti
	movw	%dx, 0x24(%bp)	/* BIOS passes drive number in DL */
				/* AX=0 */
//	xchgw	%ax, %dx	/* let DX = 0 */
//	xorw	%cx, %cx	/* CX = 0 */
#else
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
	movw	%ax, %ds
	movw	%ax, %ss	/* stack and BP-relative moves up, too */
	leaw	-0x20(%bp), %sp
	sti
				/* AX=0x1fe0 */
#endif

	movb	$0x41, %ah
	movw	$0x55AA, %bx
	int	$0x13
	jc	1f		/* No EBIOS */
	cmpw	$0xAA55, %bx
	jne	1f		/* No EBIOS */
	testb	$1, %cl
	jz	1f		/* No EBIOS */
	/* EBIOS supported */
	movb	$0x42, (ebios_12_16 - 1 - Entry_12_16 + 0x7c00)
1:
//	xorw	%cx, %cx
	xorw	%ax, %ax

	/* GET DRIVE PARMS: Calculate start of some disk areas */

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
	/* xorw	%dx, %dx */	/* assuming DX = 0 */
	divw	%bx		/* AX = sectors per root directory */
				/* DX = 0 since normally no residue */

	movw	%ax, 0x26(%bp)	/* number of sectors the root dir occupies */

	addw	%ax, %si	/* DI:SI = first data sector */
	adcw	%dx, %di	/* assuming DX = 0 */

	movw	%si, 0x30(%bp)	/* data starting sector(lo) */
	movw	%di, 0x32(%bp)	/* data starting sector(hi) */
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
	movw	$0xffff, 0x36(%bp)
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
	movw	0x26(%bp), %di	/* number of sectors the root dir occupies */
	lesw	(loadseg_off_12_16 - Entry_12_16)(%bp), %bx
				/* ES:BX = loadseg:0 */
	call	readDisk_12_16

	lesw	(loadseg_off_12_16 - Entry_12_16)(%bp), %di
				/* ES:DI = loadseg:0 */


	/* Search for kernel file name, and find start cluster */

1:
	movw	$11, %cx
	movw	$(filename_12_16 - Entry_12_16 + 0x7c00), %si
	pushw	%di
	repz cmpsb
	popw	%di
	movw	%es:0x1a(%di), %ax	/* get cluster number from dir entry */
	jz	1f

	addw	$0x20, %di	/* go to next directory entry */
	cmpb	%ch, %es:(%di)	/* if the first byte of the name is 0,     */
				/* there is no more files in the directory */
				/* assuming CH = 0 */
	jnz	1b
	movw	$(msg_BootError_12_16 - Entry_12_16 + 0x7c00), %si
	jmp	boot_error_12_16	/* fail if not found */

#ifndef ALTERNATIVE_KERNEL
loadseg_off_12_16:	.word	0
loadseg_seg_12_16:	.word	LOADSEG_12_16
#endif

1:
	pushw	%ax		/* store first cluster number */
				/* CX = 0 */


	/* Reads the FAT chain and stores it in a temporary buffer in the first
	 * 64KB.  The FAT chain is stored an array of 16-bit cluster numbers,
	 * ending with 0.
	 *
	 * The file must fit in conventional memory, so it can't be larger than
	 * 640KB. The sector size must be at least 512 bytes, so the FAT chain
	 * can't be larger than around 3KB.
	 *
	 * Call with:	AX = first cluster in chain
	 */

	/* Load the complete FAT into memory. The FAT can't be larger
	 * than 128 kb, so it should fit in the temporary buffer.
	 */

	lesw	(loadseg_off_12_16 - Entry_12_16)(%bp), %bx
				/* ES:BX = loadseg:0 */
	movw	0x16(%bp), %di	/* sectors per FAT */
	movw	0x28(%bp), %ax	/* FAT start sector(lo) */
	movw	0x2a(%bp), %dx	/* FAT start sector(hi) */
	call	readDisk_12_16
	popw	%ax		/* restore first cluster number */

	/* Set ES:DI to the temporary storage for the FAT chain */
	pushw	%ds
	popw	%es
	movw	(loadseg_seg_12_16 - Entry_12_16)(%bp), %ds
	movw	$FATBUF, %di

2:
	stosw			/* store cluster number */
	movw	%ax, %si	/* SI = cluster number */
	addw	%si, %si	/* multiply cluster number by two */
	movw	(loadseg_seg_12_16 - Entry_12_16)(%bp), %dx
				/* segment for FAT16 */
	jnc	1f
	addb	$0x10, %dh	/* overflow. Add 0x1000 to segment value */
1:

#ifdef USE_TOTAL_CLUSTERS
	cmpw	$0x0ff7, 0x34(%bp)	/* total clusters in the data area */
#else
	cmpw	$0x1801, 0x36(%bp)	/* bytes per FAT */
#endif
	jnb	3f

	/* This is a FAT12 disk */

	addw	%ax, %si	/* multiply cluster number by 3 ... */
	shrw	$1, %si		/* ... and divide by 2 */
	lodsw

	/* If the cluster number was even, the cluster value is now in
	 * bits 0-11 of AX. If the cluster number was odd, the cluster
	 * value is in bits 4-15, and must be shifted right 4 bits. If
	 * the number was odd, CF was set in the last shift instruction.
	 */

	jnc	1f
	movb	$4, %cl
	shrw	%cl, %ax
1:
	andb	$0x0f, %ah	/* mask off the highest 4 bits */
	cmpw	$0x0ff7, %ax	/* check for EOF */
	jmp	4f

3:
	/* This is a FAT16 disk. The maximal size of a 16bit FAT
	 * is 128KB, so it may not fit within a single 64KB segment
	 */

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

	pushw	%cs
	popw	%ds

	/* Loads the file into memory, one cluster at a time */

	lesw	(loadseg_off_12_16 - Entry_12_16)(%bp), %bx
				/* ES:BX = loadseg:0 */
	movw	$FATBUF, %si	/* set DS:SI to the FAT chain */

2:
	lodsw			/* AX = next cluster to read */
	orw	%ax, %ax
	jnz	1f

	/* EOC encountered - done */
#ifdef	BOOTGRUB
	movw	0x24(%bp), %dx	/* boot_drive and boot_partition */
#else
	movb	0x24(%bp), %bl	/* FreeDOS kernel uses BL, not DL, for drive */
#endif
	ljmp	*(loadseg_off_12_16 - Entry_12_16)(%bp)	/* boot it! */

1:
	decw	%ax		/* cluster numbers start with 2 */
	decw	%ax

	movw	0x0d(%bp), %di	/* sectors per cluster */
	andw	$0xff, %di	/* DI = sectors per cluster */
	mulw	%di
	addw	0x30(%bp), %ax	/* data starting sector(lo) */
	adcw	0x32(%bp), %dx	/* data starting sector(hi) */
				/* DX:AX = first sector to read */
	call	readDisk_12_16
	jmp	2b		/* read next cluster */

/* Reads a number of sectors into memory.
 *
 * Call with:	DX:AX = 32-bit DOS sector number
 *		   DI = number of sectors to read
 * 		ES:BX = destination buffer
 *
 * Returns:	CF set on error
 *		ES:BX points one byte after the last byte read.
 * 		DX:AX = next sector number after read
 */

readDisk_12_16:
2:
	pushaw
	xorw	%cx, %cx
	pushw	%cx
	pushw	%cx
	pushw	%dx
	pushw	%ax
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
	pushw	%bx
	movw	0x18(%bp), %ax	/* sectors per track */
	movw	%ax, %bx
	mulb	0x1a(%bp)	/* nHeads, but maybe a word value 0x100 */
	jnz	1f
	movb	%bl, %ah	/* nHeads=0x100, so AX=sectPerTrack*0x100 */
1:
	xchgw	%ax, %cx	/* restore AX from CX, and save AX to CX */
		/* DX:AX = LBA, CX = nHeads * sectPerTrack <= 256*63 */
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
	rorb	$1, %cl		/*	(assumes top = 0)             */
	incb	%ah		/* AH = sector number */
	orb	%ah, %cl	/* merge sector into cylinder */
#endif
	popw	%bx

	movw	$0x0201, %ax	/* read 1 sector */
ebios_12_16: /* ebios_12_16 - 1 points to 0x02 that can be changed to 0x42 */

//	cmpb	$0x0e, 2(%bp)	/* force LBA? */
//	jnz	1f		/* no, continue */
//	movb	$0x42, %ah	/* yes, use extended disk read */
//1:
	movw	%sp, %si	/* DS:SI points to disk address packet */
	movb	0x24(%bp), %dl	/* drive number */
	int	$0x13
//	stc			#; only for testing the buggy Virtual PC
	popaw			/* remove parameter block from stack */
	popaw
	jc	disk_error_12_16	/* disk read error, jc 1f if caller handles */
	incw 	%ax		/* next sector */
	jnz	1f
	incw	%dx
1:
	addw	0x0b(%bp), %bx	/* bytes per sector */
	jnc	1f		/* 64K bound check */
	pushw	%dx
	movw	%es, %dx
	addb	$0x10, %dh	/* add 1000h to ES */
				/* here, carry is cleared */
	movw	%dx, %es
	popw	%dx
1:
	decw	%di
	jnz	2b

	/* carry stored on disk read error */
	ret

	. = . - (. - readDisk_12_16)/99

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

	.word	0		/* reserved for future use */

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
	movw	%ax, %ds	/* constant DS=0 */

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

	movb	$0x41, %ah
	movw	$0x55AA, %bx
	int	$0x13
#if 0
	jnc	1f
	/* No EBIOS */
	movb	$0x02, (ebios_ext2 - 1 - Entry_ext2 + 0x7c00)
#else
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
#endif
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
	shll	$7, %eax	/* inode struct size = 0x80 */
				/* EAX=relative displacement of the inode struct */
				/* EDX=0 */

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
	jc	7f		/* EBX on the stack is < 0x10(%bp). double indirect block:
				 * 12 + 0x14(%bp) <= block serial number < 12 + 0x14(%bp) + 0x10(%bp)
				 */

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
	int	$0x13
	jc	disk_error_ext2
	movw	%es, %ax
	addw	$0x20, %ax	/* here, carry is cleared */
	movw	%ax, %es
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

#include "ntfsbs.S"

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

	//pushw	%si
	//stc
	//jc	invalid_or_null		/* invalid or null entry */
#if 0
	/* backup 63 sectors at FS_BOOT:0 to 63 sectors at FS_BOOT:8000
	 * this piece of code is no longer useful.
	 */
	pushw	%es
	popw	%ds
	xorw	%si, %si
	movw	$0x8000, %di
	movw	$0x3f00, %cx
	cld
	repz movsw
#endif

#if (defined(GRLDR_MBR)) || (defined(GRLDR_INSTALL))
	testb	$0x80, %cs:0x02	/* boot previous MBR first? */
	jnz	2f		/* no, continue to find GRLDR */

	/* yes, call the routine for booting the previous MBR.
	 * it will not return on success.
	 * on failure, it will return here
	 */

	/* before we call the routine, we will check if the user want to
	 * skip this step and continue to find the GRLDR
	 */
#if 0
	movw	$(press_space_bar_string - _start1), %si
	cmpw	$0x3920, %cs:0x04
	je	1f
	movw	$(press_hot_key_string - _start1), %si
1:
	/* if timeout==0, don't display the message */

	cmpb	$0, %cs:0x03
	je	1f
	call	print_message	/* CS:SI points to message string */
	movw	$(press_any_key_string - _start1), %si
	call	print_message	/* CS:SI points to message string */
#else
  	cmpb    $0, %cs:0x03
  	je      1f
	movw	$(press_hot_key_pre - _start1), %si
	call	print_message
	movw	$(press_hot_key_name - _start1), %si
	call	print_message
	movw	$(press_hot_key_sub - _start1), %si
	call	print_message
#endif
1:
	call	sleep_5_seconds
	jc	1f		/* desired hot-key pressed */
	call	boot_prev_mbr	//Error_modify
1:
	orb	$0x80, %cs:0x02
2:
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
	int	$0x13
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

	/* get CHS total number of sectors */
	pushw	%es
	pushw	%ds
	movb	$8, %ah		/* read drive parameters changes DX,ES,DI */
	//movb	$0x80, %dl	/* BIOS drive number is in DL */
	int	$0x13
	popw	%ds
	popw	%es
	jc	3f
	testb	$63, %cl
	jnz	2f
3:
	/* failed to get drive parameters, use maximum value */
#if 0
	popw	%dx
	pushw	%dx
	cmpb	$0x80, %dl
	jne	3f
	pushw	%ds
	xorw	%ax, %ax
	movw	%ax, %ds
	cmpb	$0, 0x475
	popw	%ds
	je	3f

3:
#endif
	movw	$0xffff, %cx
	movw	%cx, %dx
2:
	//xorl	%eax, %eax
	movzbl	%dh, %eax
	incw	%ax
	movzbl	%cl, %edx
	andb	$63, %dl
	mulw	%dx		/* DX=0, AX=product */
	shrb	$6, %cl
	xchgb	%cl, %dh
	xchgb	%ch, %dl
	incw	%dx		/* DX=total cylinders */
	mull	%edx		/* EDX=0, EAX=product */

	/* check the partition's starting LBA */
	movl	4(%si), %ebx
	addl	8(%si), %ebx	/* EBX=start_LBA */

	testl	%ebx, %ebx
	je	1f

	///* we always use LBA mode */
	////cmpl	%eax, %ebx
	////jb	1f		/* use normal CHS mode */
	cmpb	$0x42, 0x00	/* EBIOS present? */
	jne	1f		/* no, skip the LBA mode int13 call */

	/* load partition boot track to FS_BOOT using LBA mode */
	popw	%ax		/* AX=orig DX which holds drive number DL */
	pushw	%ax
	pushl	%edx		/* EDX=0, higher 4 bytes of starting LBA */
	pushl	%ebx		/* lower 4 bytes of starting LBA */
	pushw	%es		/* ES=FS_BOOT */
	pushw	%dx		/* DX=0, ES:0 is the buffer */
	//pushl	$0x003f0010	/* transfer 63 sectors */
	pushw	$0x3f		/* transfer 63 sectors */
	pushw	$0x10		/* size of disk address packet */
	xchgw	%ax, %dx	/* restore drive number DL from AL */
	movb	$0x42, %ah	/* extended read */
	movw	%sp, %si	/* DS:SI points to disk address packet */
	int	$0x13		/* ignore the read failure */
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
	negw	%cx			/* CF clear for 1K block, set otherwise */
	adcw	%ax, %bx		/* EAX=0 */
	decw	%bx
	jnz	1f

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
#if 1
	pushw	%ds
	pushw	%es
	pushw	%bx
	pushw	%dx
	movb	$8, %ah		/* read drive parameters changes DX,ES,DI,BX */
	movb	$0x80, %dl	/* BIOS drive number is in DL */
	int	$0x13
	movw	%dx, %ax
	popw	%dx
	popw	%bx
	popw	%es
	popw	%ds
	jc	3f
	andb	$63, %cl
	jz	3f
	movb	%cl, %es:0x18(%bx)
	shrw	$8, %ax
	incw	%ax
	movw	%ax, %es:0x1a(%bx)
3:
#else
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
	movw	$(FAT32_message - _start1), %si
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

	call	print_message	/* CS:SI points to message string */
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
        xchgl	%eax, %edx	/* restore AL from DL(the partition ID)
				 * and save EAX to EDX */
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
	movw	$0x1ff, (add_sub_si + 5 - _start1)
	cmpw	$0x1fe, 0x1ba
	jne	1f
	decw	(add_sub_si + 5 - _start1)
	cmpw	$0x31b2, %si		/* floppy? */
	je	1f			/* yes */
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
	movw	%ax, 9(%si)
	call	print_message	/* CS:SI points to message string */
3:
	incw	%dx
	cmpb	%dh, %dl
	jnb	2f		/* all drives checked, try floppy finally */

	pushw	%bx
	pushw	%dx
	pushw	%es
	movb	$8, %ah		/* read drive parameters changes DX, ES, DI */
	int	$0x13
	popw	%es
	jc	3f		/* try next hard drive */
	//xchgw	%ax, %cx	/* this moves CL to AL */
	andb	$63, %cl	/* CL=sectors per track, CF cleared */
	stc
	jz	3f		/* try next hard drive */
	popw	%dx		/* get DL */
	popw	%bx
	movb	%dl, %ch	/* DL saved at BP high byte in the stack */
	pushw	%cx		/* push new BX onto stack */
	pushw	%dx
	//movb	$0x02, %ah
	//movw	%ax, %si	/* save AX to SI: read 1 track */
	movw	$0x201, %ax	/* read 1 sector */
	movw	$0x7e00, %bx	/* read MBR to 9400:7e00 */
	movw	$1, %cx
	//popw	%dx
	//pushw	%dx
	xorb	%dh, %dh
	stc
	int	$0x13
	sti
3:
	popw	%dx
	popw	%bx		/* BL=sectors per track, BH=DL */

	//movw	%si, %bx	/* BL=sectors per track */

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
	pushw	%ds
	pushw	%es
	movw	$0x0202, %ax	/* read 2 sectors ... */
	movw	$0x7A00, %bx	/* ... to 0000:7A00 */
	//pushw	%bx	/* BX=0x7c00, for the offset of 0000:7c00 */
	movw	$0x0001, %cx	/* from the first sector ... */
	movw	$0x0080, %dx	/* ... of the first hard drive */
	stc
	int	$0x13
	sti
	popw	%es
	popw	%ds
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

	movw	$(Cannot_find_GRLDR_string - _start1), %si
	call	print_message	/* CS:SI points to message string */
//#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))
	movw	$(press_space_bar_string - _start1), %si
	cmpw	$0x3920, %cs:0x04
	je	3f
	movw	$0x3920, %cs:0x04
	#;movw	$(press_hot_key_string - _start1), %si
3:
	call	print_message	/* CS:SI points to message string */
	movw	$(prev_MBR_string - _start1), %si
	call	print_message	/* CS:SI points to message string */
//#else
//	movw	$(press_hot_key_pre - _start1), %si
//	call	print_message
//	movw	$(press_hot_key_name - _start1), %si
//	call	print_message
//	movw	$(press_hot_key_sub - _start1), %si
//	call	print_message
//#endif
3:
	call	sleep_5_seconds
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
	movw	$(continue_string - _start1), %si
	call	print_message	/* CS:SI points to message string */
	call	sleep_5_seconds
	ret
1:
	movw	$(message_string_helper - _start1), %si
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

	movw	$0x200, %si
	movw	%si, %di
	movw	$0xf00, %cx
	cld
	repz movsw

	popl	%eax
	popw	%bx
	popw	%si
	ret
//#endif

#if (defined(GRLDR_MBR)) || (defined(GRLDR_INSTALL))
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
	movw	$0x0200, %cx	/* move 2 sectors, the old FS_BOOT:0000 will
				 * keep untouched.  */
#else
	/* for 4-sector NTFS boot record */
	movw	$0x0400, %cx	/* move 4 sectors, the old FS_BOOT:0000 will
				 * keep untouched.  */
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

press_space_bar_string:
	.ascii	"\r\nPress space bar\0"

press_hot_key_pre:
	.ascii "\r\nPress \0"

press_hot_key_sub:
	.ascii	" to start GRUB, any other key to boot previous MBR ...\0"

hot_key_timeout_pre:
	.ascii "\r\nTimeout : \0"

hot_key_timeout_num:
	.ascii "   \b\b\b\0"

continue_string:
	.ascii	"\r\nInvalid previous MBR. Press any key to start GRUB ...\0"

Cannot_find_GRLDR_string:
	.ascii	"\r\nCannot find GRLDR.\0"

prev_MBR_string:
	.ascii	" to hold the screen, any other key to boot previous MBR ...\0"

Error_while_reading_string:
	.ascii	"\r\nError while reading MBR of \0"

drive_number_string:
	.ascii	"drive (hd0 ) \0"

partition_boot_indicator_string:
	.ascii	"\r\nInvalid boot indicator in partition table of \0"

partition_sectors_per_track_string:
	.ascii	"\r\nInvalid sectors_per_track in partition table of \0"

partition_start_sector_string:
	.ascii	"\r\nInvalid start_sector in partition table of \0"

partition_end_sector_string:
	.ascii	"\r\nInvalid end_sector in partition table of \0"

no_boot_signature_string:
	.ascii	"\r\nNo boot signature in partition table of \0"

message_string_helper:
	.ascii	"\r\nError: Cannot find GRLDR in all devices. Press Ctrl+Alt+Del to restart.\0"

partition_message:
	.ascii	"\r\nTry (hd0,0 ) : \0"

EXT2_message:
	.ascii	"EXT2: \0"
NTFS4_message:
	.ascii	"NTFS4: \0"
NTFS5_message:
	.ascii	"NTFS5: \0"
NTFS5p_message:
	.ascii	"NTFS5p: \0"
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
NTFS_no_boot_record_message:
	.ascii	"This partition is NTFS but with unknown boot record. Please\r\ninstall Microsoft NTFS boot sectors to this partition correctly, or create an\r\nFAT12/16/32 partition and place the same copy of GRLDR and MENU.LST there.\0"

#if (! defined(GRLDR_MBR)) && (! defined(GRLDR_INSTALL))
	. = _start1 + 0x1ffa
#else
	. = . + (0x3ec - ((. - _start1) % 0x200)) % 0x200

press_hot_key_name:

	/* hot key name, the address is (grldr_signature - 16) */

	.ascii  "hot-key\0"

	. = press_hot_key_name + 14

	//. = . + (0x3fa - ((. - _start1) % 0x200)) % 0x200
#endif

	/* version word of grldr.mbr, the address is (grldr_signature - 2) */

	.word   2

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



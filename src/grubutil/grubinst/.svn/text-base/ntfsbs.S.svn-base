/*
 *  GRUB Utilities --  Utilities for GRUB Legacy, GRUB2 and GRUB for DOS
 *  Copyright (C) 2007 Bean (bean123ch@gmail.com)
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/* NTFS boot sector for loading GRLDR , written by bean
 *
 * This file can be compiled as standaolne boot sector, or it can be embeded in
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
	.word	63	/* 18 - Sectors per track */
	.word	255	/* 1A - Number of heads */
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
	movw	%ax, %ds
	movw	$0x7c00, %bp
	movw	%ax, %es

	movw	%ax, %ss	/* stack and BP-relative moves up, too */
	leaw	-0x20(%bp), %sp
	sti

	movw	%dx, nt_boot_drive

	/* Test if your BIOS support LBA mode */
	movb	$0x41, %ah
	movw	$0x55AA, %bx
	int	$0x13
	jc	1f		/* No EBIOS */
	cmpw	$0xAA55, %bx
	jne	1f		/* No EBIOS */
	testb	$1, %cl
	jz	1f		/* No EBIOS */
	/* EBIOS supported */
	movb	$0x42, (ebios_nt - 1 - Entry_nt)(%bp)
1:

	movb	$8, %ah
	int	$0x13
	andb	$0x3F, %cl
	movb	%cl, 0x18(%bp)
	incb	%dh
	movb	%dh, 0x1A(%bp)
	pushw	%ds
	popw	%es

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
	xorl	%eax, %eax
	movb	$0x5, %al
	call	ntfs_read_mft
	movw	%bx, %di

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

/*
 *  dosstart.S -- DOS EXE and Linux kernel startup code for GNU GRUB
 *  Copyright (C) 2003-2007  Tinybit(tinybit@tom.com)
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

/* Note for License: Since we have copied the Linux kernel code and the
 * Linux kernel follows GPL2, so only GPL2 is adoptable and it rules here.
 */

/*
 * This program is used to generate the grub.exe file, which can boot off DOS
 * directly or, in another way, boot off Linux through KEXEC.
 *
 * Use the following shell command to generate the grub.exe file:
 *
 * 	cat dosstart pre_stage2 > grub.exe
 *
 */

#define ASM_FILE
#include <shared.h>
#include <stage2_size.h>
	
//#define ABS_PSP(x)	(x - _start - 0x100)
//#define ABS_PSP(x)	(x - _start + 0x0E0)
#define ABS_PSP(x)	(x - _start - 0x200)
#define ABS_START(x)	(x - _start - 0x200)
//#define ABS_START(x)	(x - _start - 0x020)
#define ABS_FINAL(x)	(x - pre_stage2_start + 0x200)

/* HMA_backup immediately follows the main body of stage2, para aligned */

//#define HMA_backup	((STAGE2_SIZE + pre_stage2_start - _start - 0x100 + 15) / 16)
//#define HMA_backup	((STAGE2_SIZE + pre_stage2_start - _start + 0x0E0 + 15) / 16)
#define HMA_backup	(ABS_PSP(STAGE2_SIZE + 0x1010 + pre_stage2_start + 15) / 16)
	
#ifdef	BAD_BIOS
	.file	"badgrubstart.S"
#else
	.file	"dosstart.S"
#endif

	.text

	/* Tell GAS to generate 16-bit instructions so that this code works
	   in real mode. */
	.code16

	.globl	start, _start
//start:
_start:

	/* 1 sector of EXE header is used by DOS. Actually only the leading
	 * 32 bytes are used for EXE header. At offset 0x20(=32) begins the
	 * DOS device driver structure. And at offset 0x1f1(=497) begins
	 * the Linux kernel structure.
	 */

	/*
	 * The dos startup code counts N=(pre_stage2_start-_start)/512 sectors:
	 *
	 * 1 sector for DOS EXE header, followed by (N-1) sectors of code.
	 * Of the (N-1) code sectors, the first (N-2) sectors are preparational
	 * sectors, and the last sector is called the FINAL sector. The
	 * FINAL sector contains code that finally launches the stage2 code.
	 * So pay special attention to the FINAL sector. Do not destroy
	 * the FINAL sector upon memory move operations.
	 */

	.byte	0x4d, 0x5a	/* 'MZ', the EXE magic number.  */

	/* EXE file last sector in bytes */
	.word	((STAGE2_SIZE + 0x1010 + pre_stage2_start - _start) % 512)

#define exe_sectors ((STAGE2_SIZE + 0x1010 + pre_stage2_start - _start + 511) / 512 )

	.word exe_sectors	/* total sectors the EXE file occupies */

	.word 0			/* relocation table entries */

	.word 0x0002		/* header size in 16-byte paragraphs. */
				/* 0x0002 paragraphs == 32 bytes */

	.word 0x1000 + 0x0300 + 0x0040	#; MinAlloc paragraphs:
					#; 64KB for HMA_backup
					#; 12KB for VCPI page_info
					#;  1KB for restoring EBDA

	.word 0x1000 + 0x0300 + 0x0040	#; MaxAlloc paragraphs:
					#; no more memory needed, so
					#; MaxAlloc == MinAlloc

	.word 0x001E		/* initial SS, relative to START segment */

	.word ABS_START(dos_stack)	/* initial SP, rich room for stack */
	.word 0				/* checksum, ignored by dos */
	.word ABS_START(_dos_start)	/* initial IP */
	.word 0x001E			/* initial CS, relative to START segment */
	.word 0x001C		/* displacement of the relocation table */
	.word 0			/* overlay serial number. 0 for main program */

	/* DOS program begins at _dos_start. CS==SS==START, DS==ES==PSP */

	/* For DOS device driver, _START + 0x20 locates CS:0000 */

#-----------------------------------------------------------------------------
#		DOS device driver structure begins here
#-----------------------------------------------------------------------------

	. = _start + 0x20

#if 0

#             SKELETON.ASM - A SKELETON DEVICE DRIVER V1.0
#                     (C) COPYRIGHT 1994 G.KLEIN
#
#This file contains structures, sample code and information intended
# to aid in building a device driver. It is set up as a skeleton, i.e.
# hardly any working code is provided. Only the Initialisation command
# is implemented - it displays a signon message and the commandline
# it was loaded from (excluding the "device[high]=" part). Sample code
# is provided both to let the driver load as to let it unload itself
# from memory after the initialisation command is processed. There is
# also a bit of code showing how to implement the driver as an EXE file,
# with different code depending on weather it is loaded from config.sys
# or from the command prompt.
#Although the major part of this file contains structures and other info,
# is assembles to a "working" device driver. It can be loaded from
# config.sys, and displays a signon message. When run from the commandline,
# it also displays a (different) message. It has been tested with and
# assembles "out of the box" under TASM V2.0 and MASM V5.0.
#The contents of this file is copyrighted. It may be used freely for
# whatever purpose you see it fit. Although a big effort has been made
# to ensure all information in this file is correct, no guarantees can
# be given. Any comments you may have on this file or the (correctness of)
# the information therein are welcome. Here is how you can reach me:
#
#          Fidonet:  Gertjan Klein @ 2:280/901.14
#         Internet:  gklein@hacktic.nl (Gertjan Klein)
# as of Sept. 1994:  gklein@xs4all.nl (Gertjan Klein)


#####################################################################

#Some structures describing the request headers for the various commands.
# In the comment field, a "<" means this is input to the command, and ">"
# means this is output from the command. It is indicated weather the
# command applies to block (B) or character (C) device drivers, or both
# (B/C). If a command is defined later then version 2.0, the DOS version
# in which it first appears is placed in parenthesis. This also applies
# to the fields in the request headers.

rh0             struc                   #0 - Initialisation (B/C)
rh0_len         db      ?               # < Length of packet
rh0_unit        db      ?               #Unused
rh0_cmd         db      0               # < Device driver command
rh0_stat        dw      ?               # > Status returned by device driver
rh0_rsvd        db      8 dup (?)       #Reserved
rh0_units       db      ?               # > Number of units (B)
rh0_break       dd      ?               # < End of driver memory (5.0+)
	                                # > Break address (new end drvr mem)
rh0_bpb         dd      ?               # < Pointer to cmdline (inc. name)
	                                # > Pointer to BPB pointers array (B)
rh0_drv_ltr     db      ?               # < First available drive (B, 3.0+)
rh0_msgflag     dw      ?               # > 1 To make DOS show errors (5.0+)
rh0             ends

rh1             struc                   #1 - Media Check (B)
rh1_len         db      ?               # < Length of packet
rh1_unit        db      ?               # < Unit code
rh1_cmd         db      1               # < Device driver command
rh1_stat        dw      ?               # > Status returned by device driver
rh1_rsvd        db      8 dup (?)       #Reserved
rh1_media       db      ?               # < Current media descriptor
rh1_md_stat     db      ?               # > Media status (changed/not/?)
rh1_volID       dd      ?               # > Ptr to Volume ID (3.0+)
rh1             ends

rh2             struc                   #2 - Get BPB (B)
rh2_len         db      ?               # < Length of packet
rh2_unit        db      ?               # < Unit code
rh2_cmd         db      2               # < Device driver command
rh2_stat        dw      ?               # > Status returned by device driver
rh2_rsvd        db      8 dup (?)       #Reserved
rh2_media       db      ?               # < Current media descriptor
rh2_buff        dd      ?               # < Pointer to buffer
rh2_bpb         dd      ?               # > Pointer to BPB
rh2             ends

rh3             struc                   #3 - IOCTL input (B/C)
rh3_len         db      ?               # < Length of packet
rh3_unit        db      ?               # < Unit code (B)
rh3_cmd         db      3               # < Device driver command
rh3_stat        dw      ?               # > Status returned by device driver
rh3_rsvd        db      8 dup (?)       #Reserved
rh3_media       db      ?               #Unused
rh3_buff        dd      ?               # < Pointer to buffer
rh3_count       dw      ?               # < Transfer count (bytes)
	                                # > Nr of bytes read
rh3             ends

rh4             struc                   #4 - Input (B/C)
rh4_len         db      ?               # < Length of packet
rh4_unit        db      ?               # < Unit code (B)
rh4_cmd         db      4               # < Device driver command
rh4_stat        dw      ?               # > Status returned by device driver
rh4_rsvd        db      8 dup (?)       #Reserved
rh4_media       db      ?               # < Media descriptor byte (B)
rh4_buff        dd      ?               # < Pointer to data transfer area
rh4_count       dw      ?               # < Transfer count (B:sectors,C:bytes)
	                                # > Nr of sectors/bytes read
rh4_start       dw      ?               # < Start sector number (B)
rh4_volID       dd      ?               # > Pointer to volume ID (B, 5.0+)
rh4_HugeStart   dd      ?               # < 32-bits start sector (B, 5.0+)
	                                #   (if rh4_count = 0FFFFh)
rh4             ends

rh5             struc                   #5 - Non-destructive input (C)
rh5_len         db      ?               # < Length of packet
rh5_unit        db      ?               #Unused
rh5_cmd         db      5               # < Device driver command
rh5_stat        dw      ?               # > Status returned by device driver
rh5_rsvd        db      8 dup (?)       #Reserved
rh5_char        db      ?               # > Character returned
rh5             ends

rh6             struc                   #6 - Input status (C)
rh6_len         db      ?               # < Length of packet
rh6_unit        db      ?               #Unused
rh6_cmd         db      6               # < Device driver command
rh6_stat        dw      ?               # > Status returned by device driver
rh6_rsvd        db      8 dup (?)       #Reserved
rh6             ends

rh7             struc                   #7 - Input flush (C)
rh7_len         db      ?               # < Length of packet
rh7_unit        db      ?               #Unused
rh7_cmd         db      7               # < Device driver command
rh7_stat        dw      ?               # > Status returned by device driver
rh7_rsvd        db      8 dup (?)       #Reserved
rh7             ends

rh8             struc                   #8 - Output (B/C)
rh8_len         db      ?               # < Length of packet
rh8_unit        db      ?               # < Unit code (B)
rh8_cmd         db      8               # < Device driver command
rh8_stat        dw      ?               # > Status returned by device driver
rh8_rsvd        db      8 dup (?)       #Reserved
rh8_media       db      ?               # < Media descriptor byte (B)
rh8_buff        dd      ?               # < Pointer to data transfer area
rh8_count       dw      ?               # < Transfer count (B:sectors,C:bytes)
	                                # > Nr of sectors/bytes read
rh8_start       dw      ?               # < Start sector number (B)
rh8_volID       dd      ?               # > Pointer to volume ID (B, 5.0+)
rh8_HugeStart   dd      ?               # < 32-bits start sector (B, 5.0+)
	                                #   (if rh8_count = 0FFFFh)
rh8             ends

rh9             struc                   #9 - Output with verify (B/C)
rh9_len         db      ?               # < Length of packet
rh9_unit        db      ?               # < Unit code (B)
rh9_cmd         db      9               # < Device driver command
rh9_stat        dw      ?               # > Status returned by device driver
rh9_rsvd        db      8 dup (?)       #Reserved
rh9_media       db      ?               # < Media descriptor byte (B)
rh9_buff        dd      ?               # < Pointer to data transfer area
rh9_count       dw      ?               # < Transfer count (B:sectors,C:bytes)
	                                # > Nr of sectors/bytes read
rh9_start       dw      ?               # < Start sector number (B)
rh9_volID       dd      ?               # > Pointer to volume ID (B, 5.0+)
rh9_HugeStart   dd      ?               # < 32-bits start sector (B, 5.0+)
	                                #   (if rh9_count = 0FFFFh)
rh9             ends

rh0A            struc                   #0Ah - Output status (C)
rh0A_len        db      ?               # < Length of packet
rh0A_unit       db      ?               #Unused
rh0A_cmd        db      0ah             # < Device driver command
rh0A_stat       dw      ?               # > Status returned by device driver
rh0A_rsvd       db      8 dup (?)       #Reserved
rh0A            ends

rh0B            struc                   #0Bh - Output flush (C)
rh0B_len        db      ?               # < Length of packet
rh0B_unit       db      ?               #Unused
rh0B_cmd        db      0bh             # < Device driver command
rh0B_stat       dw      ?               # > Status returned by device driver
rh0B_rsvd       db      8 dup (?)       #Reserved
rh0B            ends

rh0C            struc                   #0Ch - IOCTL output (B/C)
rh0C_len        db      ?               # < Length of packet
rh0C_unit       db      ?               # < Unit code (B)
rh0C_cmd        db      0ch             # < Device driver command
rh0C_stat       dw      ?               # > Status returned by device driver
rh0C_rsvd       db      8 dup (?)       #Reserved
rh0C_media      db      ?               #Unused
rh0C_buff       dd      ?               # < Pointer to buffer
rh0C_count      dw      ?               # < Transfer count (bytes)
	                                # > Nr of bytes written
rh0C            ends

rh0D            struc                   #0Dh - Open (B/C) (3.0+)
rh0D_len        db      ?               # < Length of packet
rh0D_unit       db      ?               # < Unit code (B)
rh0D_cmd        db      0dh             # < Device driver command
rh0D_stat       dw      ?               # > Status returned by device driver
rh0D_rsvd       db      8 dup (?)       #Reserved
rh0D            ends

rh0E            struc                   #0Eh - Close (B/C) (3.0+)
rh0E_len        db      ?               # < Length of packet
rh0E_unit       db      ?               # < Unit code (B)
rh0E_cmd        db      0eh             # < Device driver command
rh0E_stat       dw      ?               # > Status returned by device driver
rh0E_rsvd       db      8 dup (?)       #Reserved
rh0E            ends

rh0F            struc                   #0Fh - Removable media (B) (3.0+)
rh0F_len        db      ?               # < Length of packet
rh0F_unit       db      ?               # < Unit code
rh0F_cmd        db      0fh             # < Device driver command
rh0F_stat       dw      ?               # > Status returned by device driver
rh0F_rsvd       db      8 dup (?)       #Reserved
rh0F            ends

rh10            struc                   #10h - Output until busy (C) (3.0+)
rh10_len        db      ?               # < Length of packet
rh10_unit       db      ?               #Unused
rh10_cmd        db      10h             # < Device driver command
rh10_stat       dw      ?               # > Status returned by device driver
rh10_rsvd       db      8 dup (?)       #Reserved
rh10_media      db      ?               #Unused
rh10_buff       dd      ?               # < Pointer to buffer
rh10_count      dw      ?               # < Transfer count (B:sectors,C:bytes)
	                                # > Nr of sectors/bytes written
rh10            ends

#Commands 11h and 12h are undefined

rh13            struc                   #13h - Generic IOCTL (3.2+:B, 3.3+:B/C)
rh13_len        db      ?               # < Length of packet
rh13_unit       db      ?               # < Unit code (B)
rh13_cmd        db      13h             # < Device driver command
rh13_stat       dw      ?               # > Status returned by device driver
rh13_rsvd       db      8 dup (?)       #Reserved
rh13_major      db      ?               # < Category
rh13_minor      db      ?               # < Minor function
rh13_SI         dw      ?               # < Contents of SI register
rh13_DI         dw      ?               # < Contents of DI register
rh13_pkt        dd      ?               # < Pointer to generic IOCTL req.
rh13            ends

#Commands 14 to 16 are undefined

rh17            struc                   #17h - Get device (B) (3.2+)
rh17_len        db      ?               # < Length of packet
rh17_unit       db      ?               # < Unit number to check
	                                # > Last active drive (or 0)
rh17_cmd        db      17h             # < Device driver command
rh17_stat       dw      ?               # > Status returned by device driver
rh17_rsvd       db      8 dup (?)       #Reserved
rh17            ends

rh18            struc                   #18h - Set device (B) (3.2+)
rh18_len        db      ?               # < Length of packet
rh18_unit       db      ?               # < Unit to make active
rh18_cmd        db      18h             # < Device driver command
rh18_stat       dw      ?               # > Status returned by device driver
rh18_rsvd       db      8 dup (?)       #Reserved
rh18            ends

rh19            struc                   #19h - IOCTL query (B/C) (5.0+)
rh19_len        db      ?               # < Length of packet
rh19_unit       db      ?               # < Unit code (B)
rh19_cmd        db      19h             # < Device driver command
rh19_stat       dw      ?               # > Status returned by device driver
rh19_rsvd       db      8 dup (?)       #Reserved
rh19_major      db      ?               # < Category
rh19_minor      db      ?               # < Minor function
rh19_SI         dw      ?               # < Contents of SI register
rh19_DI         dw      ?               # < Contents of DI register
rh19_pkt        dd      ?               # < Pointer to IOCTL query req.
rh19            ends

#endif

nxtdev:	.long	-1			#Pointer to next device driver in chain
attr:	.word	0x8000			#Attribute: character device
strat:	.word	strategy - nxtdev	#Address of strategy routine
intr:	.word	interrupt - nxtdev	#Address of interrupt routine
dname:	.ascii	"GRUB4DOS"		#Name of the device driver (C), or
	                                # (1 byte:) number of devices (B)

#The attribute word is defined as follows:
# Bit  0:   (C): 1 if driver is stdin
#      1:   (C): 1 if driver is stdout
#           (B): 1 if driver supports 32-bit sector addressing
#                  (commands 4, 8 and 9)
#      2:   (C): 1 if driver is NUL device (only allowed for DOS's own driver)
#      3:   (C): 1 if driver is clock device
#      4:   (C): 1 if driver supports fast character I/O (int 29h)
#      5:          undefined
#      6: (C/B): 0 if driver supports commands 17h and 18h and/or 13h
#                  (get/set logical drive and generic IOCTL)
#      7: (C/B): 1 if driver supports IOCTL query (command 19h)
#      8:          undefined
#      9:          undefined
#     10:          undefined
#     11: (C/B): 1 if driver supports commands 0dh, 0eh and 0fh
#                  (Open/close device and removable media)
#     12:   (C): 1 if driver supports output until busy (command 10h)
#           (B): 1 if driver requires first FAT sector for build BPB
#                  (command 2)
#     13:          undefined
#     14: (C/B): 1 if driver supports IOCTL read and write (commands 3
#                  and 0ch)
#     15:   (C): 1 if driver supports a character device
#           (B): 0 if driver supports a block device

ReqHeader:
RhOffs:		.word	0		#Saved offset of request header
RhSeg:		.word	0		#Saved segment of request header

strategy:
	movw	%es, %cs:(RhSeg - nxtdev)	#Save request header segment
	movw	%bx, %cs:(RhOffs - nxtdev)	#Save request header offset
	lret					#Return to caller

#The following command table is initialised to the exit routines to
# use when the command is not implemented. In this skeleton, only Init
# is implemented. Change the pointers as you add routines.
#Normally, at least the following routines are required:
# For character device drivers: 0,4,5,6,7,8,9,0ah,0bh
# For block devices           : 0,1,2,4,8,9

//cmdtab:	.word	Init - nxtdev		# 0  Initialisation command
//	.word	Exit_Done - nxtdev	# 1  Media_check
//	.word	Exit_Done - nxtdev	# 2  Build BPB
//	.word	Exit_UC - nxtdev	# 3  IOCtl in
//	.word	Exit_Done - nxtdev	# 4  Input
//	.word	Exit_Busy - nxtdev	# 5  Non-destructive input
//	.word	Exit_Done - nxtdev	# 6  Input status
//	.word	Exit_Done - nxtdev	# 7  Input flush
//	.word	Exit_Done - nxtdev	# 8  Output
//	.word	Exit_Done - nxtdev	# 9  Output with verify
//	.word	Exit_Done - nxtdev	#0Ah Output status
//	.word	Exit_Done - nxtdev	#0Bh Output flush
//	.word	Exit_UC - nxtdev	#0Ch IOCtl out
//	.word	Exit_Done - nxtdev	#0Dh Device open (3.0+)
//	.word	Exit_Done - nxtdev	#0Eh Device close (3.0+)
//	.word	Exit_UC - nxtdev	#0Fh Removable media (3.0+)
//	.word	Exit_UC - nxtdev	#10h Output till busy (3.0+)
//	.word	Exit_UC - nxtdev	#11h (Unused)
//	.word	Exit_UC - nxtdev	#12h (Unused)
//	.word	Exit_UC - nxtdev	#13h Generic IOCTL (3.2:B, 3.3+:B/C)
//	.word	Exit_UC - nxtdev	#14h (Unused)
//	.word	Exit_UC - nxtdev	#15h (Unused)
//	.word	Exit_UC - nxtdev	#16h (Unused)
//	.word	Exit_UC - nxtdev	#17h Get logical device (3.2+)
//	.word	Exit_UC - nxtdev	#18h Set logical device (3.2+)
//	.word	Exit_UC - nxtdev	#19h IOCTL query (5.0+)

interrupt:
	pushfw
	cli
	cld
	pushaw
	pushw	%ds			#Save segment registers
	pushw	%es

	movw	%cs, %ax		#Make DS point to us
	movw	%ax, %ds

	lesw	ReqHeader - nxtdev, %bx	#Get ptr to request header in ES:BX
	movb	%es:2(%bx), %al		#Get command

//	cmpb	$0x19, %al		#Check if within range
//	ja      Exit_UC                 # no: set unknown command bit and exit
//	shlb	$1, %al			# yes: make word index
//	xorb	%ah, %ah
//	movw	%ax, %di		#Place it in index register
//	jmp	*(cmdtab - nxtdev)(%di)	# and jump to apropriate routine
	testb	%al, %al
	jz	Init
//Exit_Busy:
//	orw	$0x0200, %es:3(%bx)
//	jmp	Exit_Done
//Exit_UC:
	orw	$0x8103, %es:3(%bx)	#Set ERROR, DONE and UNKNOWN COMMAND
exit:
	popw	%es			#Restore segment registers
	popw	%ds
	popaw
	popfw
	lret				#Return to caller

Init:
#if 0
	/* Display CS and the original value at break address. */
	movw	%cs, %bp
	call	display_word

	movw	$0x0e0d, %ax
	int	$0x10
	movw	$0x0e0a, %ax
	int	$0x10

	lesw	ReqHeader - nxtdev, %bx	#Get ptr to request header in ES:BX
	movl	%es:14(%bx), %esi		#Set zero break address
	movl	%esi, %ebp
	shrl	$16, %ebp
	call	display_word
	movl	%esi, %ebp
	call	display_word

	movw	$0x0e0d, %ax
	int	$0x10
	movw	$0x0e0a, %ax
	int	$0x10

#endif

#if 0
	/* Show commandline (including driver name) */
	movb	$3, %ah			#Read cursor position
	xorb	%bh, %bh		# for video page 0
	int	$0x10			#(BIOS) (Returned in dx)
	lesw	ReqHeader - nxtdev, %bx	#Get ptr to request header in ES:BX
	lesw	%es:18(%bx), %bp	#Get pointer to commandline in ES:BP
	movw	%bp, %di		#Get pointer in ES:DI too
	movb	$0x0A, %al		#Terminating character of commandline
	movw	$2048, %cx		#Search max 2048 bytes
	cld
	repnz scasb			#Search for it
	movw	%di, %cx		#Get pointer to end of string
	subw	%bp, %cx		#Calculate length
	movw	$0x1301, %ax		#Write string in teletype mode
	movw	$2, %bx			# with attribute green
	int	$0x10			#(BIOS)
#endif

#if 1
	/* DS=CS */
	lesw	ReqHeader - nxtdev, %bx	#Get ptr to request header in ES:BX
	ldsw	%es:18(%bx), %si	#Get pointer to commandline in DS:SI

	movw	$0x0080, %di		#Command line will be moved to here
					#as if it is in a PSP
	movw	%cs, %ax
	addw	$((start - nxtdev) >> 4), %ax
	movw	%ax, %es

	cld
	xorw	%ax, %ax
	stosb				#store 0 at offset 0x0080, this is an
					#indicator for device driver than EXE

	/* DS:SI points to driver name */
	movw	$0xfff, %cx		/* move at most 4095 bytes */

	/* first, skip all blank characters. */

1:
	lodsb
	cmpb	$0x20, %al		/* 0x20 is space bar */
	je	1b
	cmpb	$0x09, %al		/* 0x09 is TAB */
	je	1b
	decw	%si

	/* secondly, skip the name of the driver. */

1:
	lodsb
	cmpb	$0x20, %al		/* 0x20 is space bar */
	ja	1b

	/* finally, copy the rest of the command line. */

1:
	cmpb	$0x0A, %al		/* 0x0A is LF */
	jne	2f
	movb	$0x0D, %al		/* 0x0D is CR */
2:
	cmpb	$0x0D, %al		/* 0x0D is CR */
	je	3f

	cmpb	$0x09, %al		/* 0x09 is the TAB key. */
	jne	2f
	movb	$0x20, %al
2:
	stosb
	lodsb
	loop	1b
3:
	movb	$0x00, %al		/* Ends in a NULL */
	stosb				/* the last char stored is NULL */

#endif

	movw	%cs, %ax
	movw	%ax, %ds
	lesw	ReqHeader - nxtdev, %bx	#Get ptr to request header back

	orw	$0x810C, %es:3(%bx)	#Set ERROR and DONE bits
					#          and OTHER ERROR code
	movb	$0, %es:13(%bx)		#Clear UNITS byte for CHAR device
	andw	$0x7FFF, attr - nxtdev	#Clear CHAR bit in device attrib eord

	xorw	%ax, %ax
	xchgw	%ax, %es:14(%bx)	#Set zero break address

	/* MS-DOS will initialize the break address as XXXX:0000. */

	testw	%ax, %ax		#Is it MS-DOS 5.0+ ?
	movw	%cs, %ax
	xchgw	%ax, %es:16(%bx)	#Set break address segment
	jnz	1f			#no, do not check the end address.

	/* yes, check the memory available for this device driver. */

	movw	%cs, %bx		#the driver start segment
	cmpw	%bx, %ax		#Is the end address too low?
	jbe	1f			#yes, do not check the end address.
	cmpw	$0xe000, %ax		#Is the end address too high?
	jae	1f			#yes, do not check the end address.

	/* check if we have 64K room available at the end of the driver image.
	 * This 64K space will be used for backup the HMA. Exit here if no
	 * enough memory. And 12K room for VCPI page_info, and additional
	 * 1K room for restoring EBDA from (nearly)bottom to (nearly)top of
	 * the conventional memory.
	 */

	movw	%cs, %bx		#the driver start segment

	addw	$((exe_sectors * 0x20) + 0x1000 + 0x0300 + 0x0040), %bx
					#0x1000 paragraphs = 64K (HMA_backup)
					#0x0300 paragraphs = 12K (page_info)
					#0x0040 paragraphs = 1K (EBDA)

	jc	2f			#load too high, failure
	cmpw	%bx, %ax
	jnb	1f			#check passed, continue
2:
	/* print error message. */
	movb	$3, %ah				#Read cursor position
	xorb	%bh, %bh			# for video page 0
	int	$0x10				#(BIOS) (Returned in dx)
	movw	$0x1301, %ax			#Write string in teletype mode
	movb	$3, %bl				# with attribute cyan
	movw	$(nomem_end - nomem), %cx	# length of string
	movw	$(nomem - nxtdev), %bp		# start of string
	pushw	%cs				# in es:bp
	popw	%es
	int	$0x10				#(BIOS)

	jmp     exit
1:
	//jmp	2b

#if 1

	/* Because our stack will be changed, we must backup all registers. */

	movw	%cs, %ax
	//movw	%ax, %ds		# DS=CS

//	/* DS=CS=device driver start. Adjust the exit address. */
//	movw	%ax, (device_driver_exit_cs - nxtdev)

	addw	$((start - nxtdev) >> 4), %ax
	movw	%ax, %es	/* ES:0000 now points to START */

	cld

	xorw	%di, %di
	stosl			/* EAX */
	movl	%ebx, %eax
	stosl			/* EBX */
	movl	%ecx, %eax
	stosl			/* ECX */
	movl	%edx, %eax
	stosl			/* EDX */
	movl	%edi, %eax
	stosl			/* EDI */
	movl	%esp, %eax
	stosl			/* ESP */
	movl	%ebp, %eax
	stosl			/* EBP */
	movw	%ss, %ax
	stosw			/* SS */
	movw	%fs, %ax
	stosw			/* FS */
	movw	%gs, %ax
	stosw			/* GS */

	pushfl
	popl	%eax
	stosl			/* EFLAGS */

	movl	%esi, %eax
	stosl			/* ESI */

	/* modify the stack */
	cli
	movw	%es, %ax	/* ES:0000 now points to START */
	movw	%ax, %ds
	movw	%ax, %ss
	movw	$ABS_START(dos_stack), %sp

	/* far jump to _dos_start1. */

	/* Note: DS=ES=CS tells _dos_start we are from device driver. */

	pushw	%es
	pushw	$ABS_START(_dos_start1)
	lret

	/* if need be, we could come back here from _dos_start1. */

device_driver_exit:

//	/* far jump to load CS */
//
//	.byte	0xEA		/* opcode for ljmp */
//	.word	(device_driver_exit1 - nxtdev)
//				/* offset for destination */
//device_driver_exit_cs:
//	.word	0		/* filled with driver CS */
//
//device_driver_exit1:
	cli
	cld
	movw	%cs, %ax
	movw	%ax, %ds
	movw	$(start - nxtdev), %si
	lodsl			/* EAX */
	lodsl			/* EBX */
	xchgl	%eax, %ebx
	lodsl			/* ECX */
	xchgl	%eax, %ecx
	lodsl			/* EDX */
	xchgl	%eax, %edx
	lodsl			/* EDI */
	xchgl	%eax, %edi
	lodsl			/* ESP */
	xchgl	%eax, %esp
	lodsl			/* EBP */
	xchgl	%eax, %ebp
	lodsw			/* SS */
	movw	%ax, %ss
	lodsw			/* FS */
	movw	%ax, %fs
	lodsw			/* GS */
	movw	%ax, %gs

	/* SS:SP has been restored, so it is safe to use stack. */

	lodsl			/* EFLAGS */
	pushl	%eax
	popfl

	/* direction flag here is UPWARD as we saved it before. */

	/* Another note: the direction flag does not matter, because
	 * this is the last LODS instruction executed before we exit.
	 */

	lodsl			/* ESI */
	xchgl	%eax, %esi

	jmp	exit

#endif

#if 0
display_word:
	/* routine for display hex value of BP */
	xorw	%bx, %bx
	movw	%bp, %ax
	shrw	$12, %ax
	cmpb	$9, %al
	jbe	1f
	addb	$7, %al
1:
	addb	$0x30, %al
	movb	$0x0e, %ah
	int	$0x10

	movw	%bp, %ax
	shrw	$8, %ax
	andb	$0x0f, %al
	cmpb	$9, %al
	jbe	1f
	addb	$7, %al
1:
	addb	$0x30, %al
	movb	$0x0e, %ah
	int	$0x10

	movw	%bp, %ax
	shrw	$4, %ax
	andb	$0x0f, %al
	cmpb	$9, %al
	jbe	1f
	addb	$7, %al
1:
	addb	$0x30, %al
	movb	$0x0e, %ah
	int	$0x10

	movw	%bp, %ax
	andb	$0x0f, %al
	cmpb	$9, %al
	jbe	1f
	addb	$7, %al
1:
	addb	$0x30, %al
	movb	$0x0e, %ah
	int	$0x10
	ret
#endif

nomem:
	.ascii	"\r\nError: No enough memory to run GRUB.EXE with the DEVICE command in CONFIG.SYS\r\n"
nomem_end:

#-----------------------------------------------------------------------------
#		DOS device driver structure ends here
#-----------------------------------------------------------------------------

#undef ENTRY
#define __ASSEMBLY__
#define __KERNEL__
#define __BIG_KERNEL__
#define SVGA_MODE NORMAL_VGA
	
/* stolen from linux-2.6.13.1/arch/i386/boot/bootsect.S */

/*
 *	bootsect.S		Copyright (C) 1991, 1992 Linus Torvalds
 *
 *	modified by Drew Eckhardt
 *	modified by Bruce Evans (bde)
 *	modified by Chris Noe (May 1999) (as86 -> gas)
 *	gutted by H. Peter Anvin (Jan 2003)
 *
 * BIG FAT NOTE: We're in real mode using 64k segments.  Therefore segment
 * addresses must be multiplied by 16 to obtain their respective linear
 * addresses. To avoid confusion, linear addresses are written using leading
 * hex while segment addresses are written as segment:offset.
 *
 */

#include <asm/boot.h>

SETUPSECTS	= 4			/* default nr of setup-sectors */
BOOTSEG		= 0x07C0		/* original address of boot-sector */
INITSEG		= DEF_INITSEG		/* we move boot here - out of the way */
SETUPSEG	= DEF_SETUPSEG		/* setup starts here */
SYSSEG		= DEF_SYSSEG		/* system loaded at 0x10000 (65536) */
SYSSIZE		= DEF_SYSSIZE		/* system size: # of 16-byte clicks */
					/* to be loaded */
ROOT_DEV	= 0 			/* ROOT_DEV is now written by "build" */
SWAP_DEV	= 0			/* SWAP_DEV is now written by "build" */

#ifndef SVGA_MODE
#define SVGA_MODE ASK_VGA
#endif

#ifndef RAMDISK
#define RAMDISK 0
#endif

#ifndef ROOT_RDONLY
#define ROOT_RDONLY 1
#endif

//.code16
//.text

//.global _start
//_start:

#if 0
	# Normalize the start address
	jmpl	$BOOTSEG, $(start2 - _start)

start2:
	movw	%cs, %ax
	movw	%ax, %ds
	movw	%ax, %es
	movw	%ax, %ss
	movw	$0x7c00, %sp
	sti
	cld

	movw	$(bugger_off_msg - _start), %si

msg_loop:
	lodsb
	andb	%al, %al
	jz	die
	movb	$0xe, %ah
	movw	$7, %bx
	int	$0x10
	jmp	msg_loop

die:
	# Allow the user to press a key, then reboot
	xorw	%ax, %ax
	int	$0x16
	int	$0x19

	# int 0x19 should never return.  In case it does anyway,
	# invoke the BIOS reset code...
	ljmp	$0xf000,$0xfff0


bugger_off_msg:
	.ascii	"Direct booting from floppy is no longer supported.\r\n"
	.ascii	"Please use a boot loader program instead.\r\n"
	.ascii	"\n"
	.ascii	"Remove disk and press any key to reboot . . .\r\n"
	.byte	0
#endif	

#-----------------------------------------------------------------------------
#		Linux kernel structure begins here
#-----------------------------------------------------------------------------

	# Kernel attributes; used by setup


#if 0

	.org 497

setup_sects:	.byte SETUPSECTS

#else
	. = _start + 0x1f1

setup_sects:	.byte ((startup_32 - _start) >> 9) - 1

#endif

root_flags:	.word ROOT_RDONLY
syssize:	.word SYSSIZE
swap_dev:	.word SWAP_DEV
ram_size:	.word RAMDISK
vid_mode:	.word SVGA_MODE
root_dev:	.word ROOT_DEV

#if 1

boot_flag:	.word 0xAA55

#else

	/* the sector is not bootable since it begins in a EXE header. */

boot_flag:	.word 0

#endif

	. = _start + 0x200

	/* For Linux kernel and DOS EXE, START locates CS:0000 */
	/* For DOS EXE, START also locates CS:0000 */

#-----------------------------------------------------------------------------
#	DOS device driver and EXE use 9 sectors here for storing registers and
#	the 4096-byte command line. The command line is at offset 0x0081.
#-----------------------------------------------------------------------------

/* stolen from linux-2.6.13.1/arch/i386/boot/setup.S */

/*
 *	setup.S		Copyright (C) 1991, 1992 Linus Torvalds
 *
 * setup.s is responsible for getting the system data from the BIOS,
 * and putting them into the appropriate places in system memory.
 * both setup.s and system has been loaded by the bootblock.
 *
 * This code asks the bios for memory/disk/other parameters, and
 * puts them in a "safe" place: 0x90000-0x901FF, ie where the
 * boot-block used to be. It is then up to the protected mode
 * system to read them from there before the area is overwritten
 * for buffer-blocks.
 *
 * Move PS/2 aux init code to psaux.c
 * (troyer@saifr00.cfsat.Honeywell.COM) 03Oct92
 *
 * some changes and additional features by Christoph Niemann,
 * March 1993/June 1994 (Christoph.Niemann@linux.org)
 *
 * add APM BIOS checking by Stephen Rothwell, May 1994
 * (sfr@canb.auug.org.au)
 *
 * High load stuff, initrd support and position independency
 * by Hans Lermen & Werner Almesberger, February 1996
 * <lermen@elserv.ffm.fgan.de>, <almesber@lrc.epfl.ch>
 *
 * Video handling moved to video.S by Martin Mares, March 1996
 * <mj@k332.feld.cvut.cz>
 *
 * Extended memory detection scheme retwiddled by orc@pell.chi.il.us (david
 * parsons) to avoid loadlin confusion, July 1997
 *
 * Transcribed from Intel (as86) -> AT&T (gas) by Chris Noe, May 1999.
 * <stiker@northlink.com>
 *
 * Fix to work around buggy BIOSes which don't use carry bit correctly
 * and/or report extended memory in CX/DX for e801h memory size detection 
 * call.  As a result the kernel got wrong figures.  The int15/e801h docs
 * from Ralf Brown interrupt list seem to indicate AX/BX should be used
 * anyway.  So to avoid breaking many machines (presumably there was a reason
 * to orginally use CX/DX instead of AX/BX), we do a kludge to see
 * if CX/DX have been changed in the e801 call and if so use AX/BX .
 * Michael Miller, April 2001 <michaelm@mjmm.org>
 *
 * New A20 code ported from SYSLINUX by H. Peter Anvin. AMD Elan bugfixes
 * by Robert Schwebel, December 2001 <robert@schwebel.de>
 */

#include <linux/config.h>
#include <asm/segment.h>
#include <linux/version.h>
#include <linux/compile.h>
#include <asm/boot.h>
#include <asm/e820.h>
#include <asm/page.h>
	
/* Signature words to ensure LILO loaded us right */
#define SIG1	0xAA55
#define SIG2	0x5A5A

INITSEG  = DEF_INITSEG		# 0x9000, we move boot here, out of the way
SYSSEG   = DEF_SYSSEG		# 0x1000, system loaded at 0x10000 (65536).
SETUPSEG = DEF_SETUPSEG		# 0x9020, this is the current segment
				# ... and the former contents of CS

DELTA_INITSEG = SETUPSEG - INITSEG	# 0x0020

.code16
.globl begtext, begdata, begbss, endtext, enddata, endbss

.text
begtext:
.data
begdata:
.bss
begbss:
.text

start:
	jmp	trampoline

# This is the setup header, and it must start at %cs:2 (old 0x9020:2)

		.ascii	"HdrS"		# header signature
		.word	0x0203		# header version number (>= 0x0105)
					# or else old loadlin-1.5 will fail)
realmode_swtch:	.word	0, 0		# default_switch, SETUPSEG
start_sys_seg:	.word	SYSSEG
		.word	kernel_version - start
					# pointing to kernel version string
					# above section of header is compatible
					# with loadlin-1.5 (header v1.5). Don't
					# change it.

type_of_loader:	.byte	0		# = 0, old one (LILO, Loadlin,
					#      Bootlin, SYSLX, bootsect...)
					# See Documentation/i386/boot.txt for
					# assigned ids
	
# flags, unused bits must be zero (RFU) bit within loadflags
loadflags:
LOADED_HIGH	= 1			# If set, the kernel is loaded high
CAN_USE_HEAP	= 0x80			# If set, the loader also has set
					# heap_end_ptr to tell how much
					# space behind setup.S can be used for
					# heap purposes.
					# Only the loader knows what is free
#ifndef __BIG_KERNEL__
		.byte	0
#else
		.byte	LOADED_HIGH
#endif

setup_move_size: .word  0x8000		# size to move, when setup is not
					# loaded at 0x90000. We will move setup 
					# to 0x90000 then just before jumping
					# into the kernel. However, only the
					# loader knows how much data behind
					# us also needs to be loaded.

code32_start:				# here loaders can put a different
					# start address for 32-bit code.
#ifndef __BIG_KERNEL__
		.long	0x1000		#   0x1000 = default for zImage
#else
		.long	0x100000	# 0x100000 = default for big kernel
#endif

ramdisk_image:	.long	0		# address of loaded ramdisk image
					# Here the loader puts the 32-bit
					# address where it loaded the image.
					# This only will be read by the kernel.

ramdisk_size:	.long	0		# its size in bytes

bootsect_kludge:
		.long	0		# obsolete

heap_end_ptr:	.word	modelist-start+1024
					# (Header version 0x0201 or later)
					# space from here (exclusive) down to
					# end of setup code can be used by setup
					# for local heap purposes.

pad1:		.word	0
cmd_line_ptr:	.long 0			# (Header version 0x0202 or later)
					# If nonzero, a 32-bit pointer
					# to the kernel command line.
					# The command line should be
					# located between the start of
					# setup and the end of low
					# memory (0xa0000), or it may
					# get overwritten before it
					# gets read.  If this field is
					# used, there is no longer
					# anything magical about the
					# 0x90000 segment; the setup
					# can be located anywhere in
					# low memory 0x10000 or higher.

ramdisk_max:	.long (-__PAGE_OFFSET-(512 << 20)-1) & 0x7fffffff
					# (Header version 0x0203 or later)
					# The highest safe address for
					# the contents of an initrd

trampoline:	call	start_of_setup
		.align 16
					# The offset at this point is 0x240
		.space	(0xeff-0x240+1)	# E820 & EDD space (ending at 0xeff)
# End of setup header #####################################################

start_of_setup:
# Bootlin depends on this being done early
	movw	$0x01500, %ax
	movb	$0x81, %dl
	int	$0x13

#ifdef SAFE_RESET_DISK_CONTROLLER
# Reset the disk controller.
	movw	$0x0000, %ax
	movb	$0x80, %dl
	int	$0x13
#endif

# Set %ds = %cs, we know that SETUPSEG = %cs at this point
	movw	%cs, %ax		# aka SETUPSEG
	movw	%ax, %ds
# Check signature at end of setup
	cmpw	$SIG1, setup_sig1 - start
	jne	bad_sig

	cmpw	$SIG2, setup_sig2 - start
	jne	bad_sig

	jmp	good_sig1

no_sig_mess: .string	"No setup signature found ..."

good_sig1:
	jmp	good_sig

# We now have to find the rest of the setup code/data
bad_sig:
	movw	%cs, %ax			# SETUPSEG
	subw	$DELTA_INITSEG, %ax		# INITSEG
	movw	%ax, %ds
	xorb	%bh, %bh
	movb	(497), %bl			# get setup sect from bootsect
	subw	$4, %bx				# LILO loads 4 sectors of setup
	shlw	$8, %bx				# convert to words (1sect=2^8 words)
	movw	%bx, %cx
	shrw	$3, %bx				# convert to segment
	addw	$SYSSEG, %bx
	movw	%bx, %cs:(start_sys_seg - start)
# Move rest of setup code/data to here
	movw	$2048, %di			# four sectors loaded by LILO
	subw	%si, %si
	pushw	%cs
	popw	%es
	movw	$SYSSEG, %ax
	movw	%ax, %ds
	rep
	movsw
	movw	%cs, %ax			# aka SETUPSEG
	movw	%ax, %ds
	cmpw	$SIG1, setup_sig1 - start
	jne	no_sig

	cmpw	$SIG2, setup_sig2 - start
	jne	no_sig

	jmp	good_sig

no_sig:
	lea	no_sig_mess - start, %si
	call	prtstr

no_sig_loop:
	hlt
	jmp	no_sig_loop

good_sig:
	movw	%cs, %ax			# aka SETUPSEG
	subw	$DELTA_INITSEG, %ax 		# aka INITSEG
	movw	%ax, %ds
# Check if an old loader tries to load a big-kernel
	testb	$LOADED_HIGH, %cs:loadflags - start # Do we have a big kernel?
	jz	loader_ok			# No, no danger for old loaders.

	cmpb	$0, %cs:type_of_loader - start	# Do we have a loader that
						# can deal with us?
	jnz	loader_ok			# Yes, continue.

	pushw	%cs				# No, we have an old loader,
	popw	%ds				# die. 
	lea	loader_panic_mess - start, %si
	call	prtstr

	jmp	no_sig_loop

loader_panic_mess: .string "Wrong loader, giving up..."

loader_ok:

#; GRUB4DOS needn't get memory size
	jmp	get_mem_size_end 

# Get memory size (extended mem, kB)

	xorl	%eax, %eax
	movl	%eax, (0x1e0)
#ifndef STANDARD_MEMORY_BIOS_CALL
	movb	%al, (E820NR)
# Try three different memory detection schemes.  First, try
# e820h, which lets us assemble a memory map, then try e801h,
# which returns a 32-bit memory size, and finally 88h, which
# returns 0-64m

# method E820H:
# the memory map from hell.  e820h returns memory classified into
# a whole bunch of different types, and allows memory holes and
# everything.  We scan through this memory map and build a list
# of the first 32 memory areas, which we return at [E820MAP].
# This is documented at http://www.acpi.info/, in the ACPI 2.0 specification.

#define SMAP  0x534d4150

meme820:
	xorl	%ebx, %ebx			# continuation counter
	movw	$E820MAP, %di			# point into the whitelist
						# so we can have the bios
						# directly write into it.

jmpe820:
	movl	$0x0000e820, %eax		# e820, upper word zeroed
	movl	$SMAP, %edx			# ascii 'SMAP'
	movl	$20, %ecx			# size of the e820rec
	pushw	%ds				# data record.
	popw	%es
	int	$0x15				# make the call
	jc	bail820				# fall to e801 if it fails

	cmpl	$SMAP, %eax			# check the return is `SMAP'
	jne	bail820				# fall to e801 if it fails

#	cmpl	$1, 16(%di)			# is this usable memory?
#	jne	again820

	# If this is usable memory, we save it by simply advancing %di by
	# sizeof(e820rec).
	#
good820:
	movb	(E820NR), %al			# up to 128 entries
	cmpb	$E820MAX, %al
	jae	bail820

	incb	(E820NR)
	movw	%di, %ax
	addw	$20, %ax
	movw	%ax, %di
again820:
	cmpl	$0, %ebx			# check to see if
	jne	jmpe820				# %ebx is set to EOF
bail820:


# method E801H:
# memory size is in 1k chunksizes, to avoid confusing loadlin.
# we store the 0xe801 memory size in a completely different place,
# because it will most likely be longer than 16 bits.
# (use 1e0 because that's what Larry Augustine uses in his
# alternative new memory detection scheme, and it's sensible
# to write everything into the same place.)

meme801:
	stc					# fix to work around buggy
	xorw	%cx,%cx				# BIOSes which don't clear/set
	xorw	%dx,%dx				# carry on pass/error of
						# e801h memory size call
						# or merely pass cx,dx though
						# without changing them.
	movw	$0xe801, %ax
	int	$0x15
	jc	mem88

	cmpw	$0x0, %cx			# Kludge to handle BIOSes
	jne	e801usecxdx			# which report their extended
	cmpw	$0x0, %dx			# memory in AX/BX rather than
	jne	e801usecxdx			# CX/DX.  The spec I have read
	movw	%ax, %cx			# seems to indicate AX/BX 
	movw	%bx, %dx			# are more reasonable anyway...

e801usecxdx:
	andl	$0xffff, %edx			# clear sign extend
	shll	$6, %edx			# and go from 64k to 1k chunks
	movl	%edx, (0x1e0)			# store extended memory size
	andl	$0xffff, %ecx			# clear sign extend
 	addl	%ecx, (0x1e0)			# and add lower memory into
						# total size.

# Ye Olde Traditional Methode.  Returns the memory size (up to 16mb or
# 64mb, depending on the bios) in ax.
mem88:

#endif
	movb	$0x88, %ah
	int	$0x15
	movw	%ax, (2)

get_mem_size_end: 

# Set the keyboard repeat rate to the max
	movw	$0x0305, %ax
	xorw	%bx, %bx
	int	$0x16

#; grub4dos needn't get video, hd, mouse, APM, edd
#;	jmp	get_misc_info_end
#;
#;# Check for video adapter and its parameters and allow the
#;# user to browse video modes.
#;	call	video				# NOTE: we need %ds pointing
#;						# to bootsector
#;
#;# Get hd0 data...
#;	xorw	%ax, %ax
#;	movw	%ax, %ds
#;	ldsw	(4 * 0x41), %si
#;	movw	%cs, %ax			# aka SETUPSEG
#;	subw	$DELTA_INITSEG, %ax		# aka INITSEG
#;	pushw	%ax
#;	movw	%ax, %es
#;	movw	$0x0080, %di
#;	movw	$0x10, %cx
#;	pushw	%cx
#;	cld
#;	rep
#; 	movsb
#;# Get hd1 data...
#;	xorw	%ax, %ax
#;	movw	%ax, %ds
#;	ldsw	(4 * 0x46), %si
#;	popw	%cx
#;	popw	%es
#;	movw	$0x0090, %di
#;	rep
#;	movsb
#;# Check that there IS a hd1 :-)
#;	movw	$0x01500, %ax
#;	movb	$0x81, %dl
#;	int	$0x13
#;	jc	no_disk1
#;	
#;	cmpb	$3, %ah
#;	je	is_disk1
#;
#;no_disk1:
#;	movw	%cs, %ax			# aka SETUPSEG
#;	subw	$DELTA_INITSEG, %ax 		# aka INITSEG
#;	movw	%ax, %es
#;	movw	$0x0090, %di
#;	movw	$0x10, %cx
#;	xorw	%ax, %ax
#;	cld
#;	rep
#;	stosb
#;is_disk1:
#;# check for Micro Channel (MCA) bus
#;	movw	%cs, %ax			# aka SETUPSEG
#;	subw	$DELTA_INITSEG, %ax		# aka INITSEG
#;	movw	%ax, %ds
#;	xorw	%ax, %ax
#;	movw	%ax, (0xa0)			# set table length to 0
#;	movb	$0xc0, %ah
#;	stc
#;	int	$0x15				# moves feature table to es:bx
#;	jc	no_mca
#;
#;	pushw	%ds
#;	movw	%es, %ax
#;	movw	%ax, %ds
#;	movw	%cs, %ax			# aka SETUPSEG
#;	subw	$DELTA_INITSEG, %ax		# aka INITSEG
#;	movw	%ax, %es
#;	movw	%bx, %si
#;	movw	$0xa0, %di
#;	movw	(%si), %cx
#;	addw	$2, %cx				# table length is a short
#;	cmpw	$0x10, %cx
#;	jc	sysdesc_ok
#;
#;	movw	$0x10, %cx			# we keep only first 16 bytes
#;sysdesc_ok:
#;	rep
#;	movsb
#;	popw	%ds
#;no_mca:
#;#ifdef CONFIG_X86_VOYAGER
#;	movb	$0xff, 0x40	# flag on config found
#;	movb	$0xc0, %al
#;	mov	$0xff, %ah
#;	int	$0x15		# put voyager config info at es:di
#;	jc	no_voyager
#;	movw	$0x40, %si	# place voyager info in apm table
#;	cld
#;	movw	$7, %cx
#;voyager_rep:
#;	movb	%es:(%di), %al
#;	movb	%al,(%si)
#;	incw	%di
#;	incw	%si
#;	decw	%cx
#;	jnz	voyager_rep
#;no_voyager:	
#;#endif
#;# Check for PS/2 pointing device
#;	movw	%cs, %ax			# aka SETUPSEG
#;	subw	$DELTA_INITSEG, %ax		# aka INITSEG
#;	movw	%ax, %ds
#;	movw	$0, (0x1ff)			# default is no pointing device
#;	int	$0x11				# int 0x11: equipment list
#;	testb	$0x04, %al			# check if mouse installed
#;	jz	no_psmouse
#;
#;	movw	$0xAA, (0x1ff)			# device present
#;no_psmouse:
#;
#;#if defined(CONFIG_X86_SPEEDSTEP_SMI) || defined(CONFIG_X86_SPEEDSTEP_SMI_MODULE)
#;	movl	$0x0000E980, %eax		# IST Support 
#;	movl	$0x47534943, %edx		# Request value
#;	int	$0x15
#;
#;	movl	%eax, (96)
#;	movl	%ebx, (100)
#;	movl	%ecx, (104)
#;	movl	%edx, (108)
#;#endif
#;
#;#if defined(CONFIG_APM) || defined(CONFIG_APM_MODULE)
#;# Then check for an APM BIOS...
#;						# %ds points to the bootsector
#;	movw	$0, 0x40			# version = 0 means no APM BIOS
#;	movw	$0x05300, %ax			# APM BIOS installation check
#;	xorw	%bx, %bx
#;	int	$0x15
#;	jc	done_apm_bios			# Nope, no APM BIOS
#;	
#;	cmpw	$0x0504d, %bx			# Check for "PM" signature
#;	jne	done_apm_bios			# No signature, no APM BIOS
#;
#;	andw	$0x02, %cx			# Is 32 bit supported?
#;	je	done_apm_bios			# No 32-bit, no (good) APM BIOS
#;
#;	movw	$0x05304, %ax			# Disconnect first just in case
#;	xorw	%bx, %bx
#;	int	$0x15				# ignore return code
#;	movw	$0x05303, %ax			# 32 bit connect
#;	xorl	%ebx, %ebx
#;	xorw	%cx, %cx			# paranoia :-)
#;	xorw	%dx, %dx			#   ...
#;	xorl	%esi, %esi			#   ...
#;	xorw	%di, %di			#   ...
#;	int	$0x15
#;	jc	no_32_apm_bios			# Ack, error. 
#;
#;	movw	%ax,  (66)			# BIOS code segment
#;	movl	%ebx, (68)			# BIOS entry point offset
#;	movw	%cx,  (72)			# BIOS 16 bit code segment
#;	movw	%dx,  (74)			# BIOS data segment
#;	movl	%esi, (78)			# BIOS code segment lengths
#;	movw	%di,  (82)			# BIOS data segment length
#;# Redo the installation check as the 32 bit connect
#;# modifies the flags returned on some BIOSs
#;	movw	$0x05300, %ax			# APM BIOS installation check
#;	xorw	%bx, %bx
#;	xorw	%cx, %cx			# paranoia
#;	int	$0x15
#;	jc	apm_disconnect			# error -> shouldn't happen
#;
#;	cmpw	$0x0504d, %bx			# check for "PM" signature
#;	jne	apm_disconnect			# no sig -> shouldn't happen
#;
#;	movw	%ax, (64)			# record the APM BIOS version
#;	movw	%cx, (76)			# and flags
#;	jmp	done_apm_bios
#;
#;apm_disconnect:					# Tidy up
#;	movw	$0x05304, %ax			# Disconnect
#;	xorw	%bx, %bx
#;	int	$0x15				# ignore return code
#;
#;	jmp	done_apm_bios
#;
#;no_32_apm_bios:
#;	andw	$0xfffd, (76)			# remove 32 bit support bit
#;done_apm_bios:
#;#endif
#;
#;#include "edd.S"
#;
#;get_misc_info_end:

# Now we want to move to protected mode ...
	cmpw	$0, %cs:realmode_swtch - start
	jz	rmodeswtch_normal

	lcall	*%cs:realmode_swtch - start

	jmp	rmodeswtch_end

rmodeswtch_normal:
	pushw	%cs
	call	default_switch

rmodeswtch_end:
# we get the code32 start address and modify the below 'jmpi'
# (loader may have changed it)
	movl	%cs:code32_start - start, %eax
	movl	%eax, %cs:code32 - start

# Now we move the system to its rightful place ... but we check if we have a
# big-kernel. In that case we *must* not move it ...
	testb	$LOADED_HIGH, %cs:loadflags - start
	jz	do_move0			# .. then we have a normal low
						# loaded zImage
						# .. or else we have a high
						# loaded bzImage
	jmp	end_move			# ... and we skip moving

do_move0:
	movw	$0x100, %ax			# start of destination segment
	movw	%cs, %bp			# aka SETUPSEG
	subw	$DELTA_INITSEG, %bp		# aka INITSEG
	movw	%cs:start_sys_seg - start, %bx	# start of source segment
	cld
do_move:
	movw	%ax, %es			# destination segment
	incb	%ah				# instead of add ax,#0x100
	movw	%bx, %ds			# source segment
	addw	$0x100, %bx
	subw	%di, %di
	subw	%si, %si
	movw 	$0x800, %cx
	rep
	movsw
	cmpw	%bp, %bx			# assume start_sys_seg > 0x200,
						# so we will perhaps read one
						# page more than needed, but
						# never overwrite INITSEG
						# because destination is a
						# minimum one page below source
	jb	do_move

end_move:
# then we load the segment descriptors
	movw	%cs, %ax			# aka SETUPSEG
	movw	%ax, %ds
		
# Check whether we need to be downward compatible with version <=201
	cmpl	$0, cmd_line_ptr - start
	jne	end_move_self		# loader uses version >=202 features
	cmpb	$0x20, type_of_loader - start
	je	end_move_self		# bootsect loader, we know of it

# Boot loader doesnt support boot protocol version 2.02.
# If we have our code not at 0x90000, we need to move it there now.
# We also then need to move the params behind it (commandline)
# Because we would overwrite the code on the current IP, we move
# it in two steps, jumping high after the first one.
	movw	%cs, %ax
	cmpw	$SETUPSEG, %ax
	je	end_move_self

	cli					# make sure we really have
						# interrupts disabled !
						# because after this the stack
						# should not be used
	subw	$DELTA_INITSEG, %ax		# aka INITSEG
	movw	%ss, %dx
	cmpw	%ax, %dx
	jb	move_self_1

	addw	$INITSEG, %dx
	subw	%ax, %dx			# this will go into %ss after
						# the move
move_self_1:
	movw	%ax, %ds
	movw	$INITSEG, %ax			# real INITSEG
	movw	%ax, %es
	movw	%cs:setup_move_size - start, %cx
	std					# we have to move up, so we use
						# direction down because the
						# areas may overlap
	movw	%cx, %di
	decw	%di
	movw	%di, %si
	subw	$(move_self_here - start+0x200), %cx
	rep
	movsb
	ljmp	$SETUPSEG, $(move_self_here - start)

move_self_here:
	movw	$(move_self_here - start+0x200), %cx
	rep
	movsb
	movw	$SETUPSEG, %ax
	movw	%ax, %ds
	movw	%dx, %ss
end_move_self:					# now we are at the right place

#
# Enable A20.  This is at the very best an annoying procedure.
# A20 code ported from SYSLINUX 1.52-1.63 by H. Peter Anvin.
# AMD Elan bug fix by Robert Schwebel.
#
	movw	$(a20_control_begin_string - start), %si
	call	prtstr

	movw	$0x00ff, %cx		# try so many times on failure
	movw	$0x0101, %dx		# non-zero means `enable'
	call	enable_disable_a20
	jz	3f
	movw	$(a20_control_fail_string - start), %si
	call	prtstr
1:
	hlt
	jmp	1b
3:
	movw	$(a20_control_ok_string - start), %si
	call	prtstr

# set up gdt and idt
	lidt	idt_48 - start			# load idt with 0,0
	xorl	%eax, %eax			# Compute gdt_base
	movw	%ds, %ax			# (Convert %ds:gdt to a linear ptr)
	shll	$4, %eax
	addl	$gdt - start, %eax
	movl	%eax, (gdt_48 - start+2)
	lgdt	gdt_48 - start			# load gdt with whatever is
						# appropriate

# make sure any possible coprocessor is properly reset..
	xorw	%ax, %ax
	outb	%al, $0xf0
	call	delay

	outb	%al, $0xf1
	call	delay

# well, that went ok, I hope. Now we mask all interrupts - the rest
# is done in init_IRQ().
	movb	$0xFF, %al			# mask all interrupts for now
	outb	%al, $0xA1
	call	delay
	
	movb	$0xFB, %al			# mask all irq's but irq2 which
	outb	%al, $0x21			# is cascaded

# Well, that certainly wasn't fun :-(. Hopefully it works, and we don't
# need no steenking BIOS anyway (except for the initial loading :-).
# The BIOS-routine wants lots of unnecessary data, and it's less
# "interesting" anyway. This is how REAL programmers do it.
#
# Well, now's the time to actually move into protected mode. To make
# things as simple as possible, we do no register set-up or anything,
# we let the gnu-compiled 32-bit programs do that. We just jump to
# absolute address 0x1000 (or the loader supplied one),
# in 32-bit protected mode.
#
# Note that the short jump isn't strictly needed, although there are
# reasons why it might be a good idea. It won't hurt in any case.
	movw	$1, %ax				# protected mode (PE) bit
	lmsw	%ax				# This is it!
	jmp	flush_instr

flush_instr:
	xorw	%bx, %bx			# Flag to indicate a boot
	xorl	%esi, %esi			# Pointer to real-mode code
	movw	%cs, %si
	subw	$DELTA_INITSEG, %si
	shll	$4, %esi			# Convert to 32-bit pointer

# jump to startup_32 in arch/i386/boot/compressed/head.S
#	
# NOTE: For high loaded big kernels we need a
#	jmpi    0x100000,__BOOT_CS
#
#	but we yet haven't reloaded the CS register, so the default size 
#	of the target offset still is 16 bit.
#	However, using an operand prefix (0x66), the CPU will properly
#	take our 48 bit far pointer. (INTeL 80386 Programmer's Reference
#	Manual, Mixing 16-bit and 32-bit code, page 16-6)

	.byte 0x66, 0xea			# prefix + jmpi-opcode
code32:	.long	0x1000				# will be set to 0x100000
						# for big kernels
	.word	__BOOT_CS

# Here's a bunch of information about your current kernel..
kernel_version:	.ascii	UTS_RELEASE
		.ascii	" ("
		.ascii	LINUX_COMPILE_BY
		.ascii	"@"
		.ascii	LINUX_COMPILE_HOST
		.ascii	") "
		.ascii	UTS_VERSION
		.byte	0

# This is the default real mode switch routine.
# to be called just before protected mode transition
default_switch:
	cli					# no interrupts allowed !
	movb	$0x80, %al			# disable NMI for bootup
						# sequence
	outb	%al, $0x70
	lret

#-----------------------------------------------------------------------------
#	DOS device driver and EXE will use this code to enable/disable A20
#-----------------------------------------------------------------------------

	// to asure the command-line menu will not overwrite our code here

	. = start + 0x1000 + 0x82 + (. - (start + 0x1000 + 0x82)) * (1 & (. > (start + 0x1000 + 0x82)))

	. = . - ((0x1000 + 0x81) / (. - start))

	/* print ASCIZ string DS:SI (modifies AX BX SI) */
1:
	xorw	%bx, %bx	/* video page 0 */
	movb	$0x0e, %ah	/* print char in AL */
	int	$0x10		/* via TTY mode */

prtstr:

	lodsb			/* get token */
	cmpb	$0, %al		/* end of string? */
	jne	1b
	ret

//# Routine to print asciiz string at ds:si
//prtstr:
//2:
//	lodsb
//	andb	%al, %al
//	jz	2f
//
//	call	1f	//prtchr
//	jmp	2b
//
//2:
//	ret
//
//# Space printing
//prtsp2:	call	prtspc		# Print double space
//prtspc:	movb	$0x20, %al	# Print single space (note: fall-thru)
//
//# Part of above routine, this one just prints ascii al
//prtchr:
//1:
//	pushw	%ax
//	pushw	%cx
//	movw	$7,%bx
//	movw	$0x01, %cx
//	movb	$0x0e, %ah
//	int	$0x10
//	popw	%cx
//	popw	%ax
//	ret
//
//beep:
//	movb	$0x07, %al
//	jmp	1b	//prtchr
	
a20_control_begin_string:
	.ascii	"\r\nkernel grub.exe: Trying to turn on A20 gate ...\r\n\0$"

a20_control_ok_string:
	.ascii	"\r\nkernel grub.exe: A20 gate turned on OK!\r\n\0$"

a20_control_fail_string:
	.ascii	"\r\nkernel grub.exe: A20 gate not responding!\r\n\0$"

#include "a20.inc"

# Read the cmos clock. Return the seconds in al
gettime:
	pushw	%cx
	movb	$0x02, %ah
	int	$0x1a
	movb	%dh, %al			# %dh contains the seconds
	andb	$0x0f, %al
	movb	%dh, %ah
	movb	$0x04, %cl
	shrb	%cl, %ah
	aad
	popw	%cx
	ret

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
	.fill GDT_ENTRY_BOOT_CS,8,0

	.word	0xFFFF				# 4Gb - (0x100000*0x1000 = 4Gb)
	.word	0				# base address = 0
	.word	0x9A00				# code read/exec
	.word	0x00CF				# granularity = 4096, 386
						#  (+5th nibble of limit)

	.word	0xFFFF				# 4Gb - (0x100000*0x1000 = 4Gb)
	.word	0				# base address = 0
	.word	0x9200				# data read/write
	.word	0x00CF				# granularity = 4096, 386
						#  (+5th nibble of limit)
gdt_end:
	.align	4
	
	.word	0				# alignment byte
idt_48:
	.word	0				# idt limit = 0
	.word	0, 0				# idt base = 0L

	.word	0				# alignment byte
gdt_48:
	.word	gdt_end - gdt - 1		# gdt limit
	.word	0, 0				# gdt base (filled in later)

# Include video setup & detection code

#;#include "video.S"
# Setup signature -- must be last
setup_sig1:	.word	SIG1
setup_sig2:	.word	SIG2

# After this point, there is some free space which is used by the video mode
# handling code to store the temporary mode table (not used by the kernel).

modelist:

.text
endtext:
.data
enddata:
.bss
endbss:


/* stolen from linux-2.6.13.1/arch/i386/boot/compressed/head.S */

/*
 *  linux/boot/head.S
 *
 *  Copyright (C) 1991, 1992, 1993  Linus Torvalds
 */

/*
 *  head.S contains the 32-bit startup code.
 *
 * NOTE!!! Startup happens at absolute address 0x00001000, which is also where
 * the page directory will exist. The startup code will be overwritten by
 * the page directory. [According to comments etc elsewhere on a compressed
 * kernel it will end up at 0x1000 + 1Mb I hope so as I assume this. - AC]
 *
 * Page 0 is deliberately kept safe, since System Management Mode code in 
 * laptops may need to access the BIOS data stored there.  This is also
 * useful for future device drivers that either access the BIOS via VM86 
 * mode.
 */

/*
 * High loaded stuff by Hans Lermen & Werner Almesberger, Feb. 1996
 */
.text

#include <linux/linkage.h>
#include <asm/segment.h>

	. = _start + 0x2000

	.code32

	.align 0x200

	.globl startup_32

	
//#define debug_putchar(x) movw $(x | ((x << 12) & 0xF000) | (((x << 8) & 0x0F00) ^ 0xC00)), (0xB8140 + (((x - 0x30) % 80) * 2))
#define debug_putchar(x)

startup_32:
	cld
	cli
	movl	$(__BOOT_DS), %eax
	movl	%eax, %ds
	movl	%eax, %es
	movl	%eax, %fs
	movl	%eax, %gs
	movl	%eax, %ss

	debug_putchar('0')
//	movw	$0x0C30, 0xB80A0

	/* we use space near the end of real mode IDT for temp stack */
	movl	$0x400, %esp

	xorl	%eax,%eax
/*
 * Initialize eflags.  Some BIOS's leave bits like NT set.  This would
 * confuse the debugger if this code is traced.
 * XXX - best to initialize before switching to protected mode.
 */
	//pushl	$0
	pushl	%eax		# EAX=0
	popfl			# cli, cld by the way

1:	incl	%eax		# check that A20 really IS enabled
	movl	%eax,0x000000	# loop forever if it isn't
	cmpl	%eax,0x100000
	je	1b

	debug_putchar('1')
//	movw	$0x1D31, (0xB80A0 + (1 * 2))

	call	1f		# just calculate the EIP register
1:
	popl	%ebp		# EBP=linear address of 1b, i.e., current EIP
	subl	$(1b - startup_32), %ebp # EBP=linear address of startup_32

#if 0
	# debug, move conventional mem to 0x1000000

	pushw	%cs
	pushw	%ds
	pushw	%es
	pushw	%ss
	pushw	%fs
	pushw	%gs
	pushal
	movl	$0x1000000, %edi
	xorl	%esi, %esi
	movl	$0x400000, %ecx
	cld
	rep movsl
	popal
	popw	%gs
	popw	%fs
	popw	%ss
	popw	%es
	popw	%ds
	popw	%cx
#endif

	/* memory layout:
	 *
	 *	0x0600-0x07FF		this sector is not used
	 *	0x0800-0x09FF		this sector stores command line
	 *	0x0A00-0x0DFF		2 sectors for real mode variables
	 *	0x0E00-0x0FFF		the current sector will be copied here
	 *	0x1000-0x8000		the rest sectors
	 *
	 * Note: The first page(4KB) is not used by Linux, so it is a safe
	 * place to store our code and data.
	 */

	cld				# can be omitted(already done by popfl)

	pushl	%esi			# points to boot_params

	/* move 1 sector of commandline onto 0x00000800-0x000009FF */

	movl	$0x00000800, %edi
	movl	0x228(%esi), %esi	# 0x228 is offset for cmd_line_ptr
	movl	$0x00000080, %ecx	# move 1 sector
	repz movsl

	popl	%esi			# points to boot_params

	debug_putchar('2')

	/* move 2-sector real mode variables onto 0x00000A00-0x00000DFF */

	movl	$0x00000A00, %edi
	movl	$0x00000100, %ecx	# move 2 sectors
	repz movsl

	debug_putchar('3')

	/* move 1 sector of the init code here to a safe place 0x00000E00 */

	movl	$0x00000E00, %edi
	movl	%ebp, %esi		# EBP=linear address of startup_32
	movl	$0x00000080, %ecx	# move 1 sector
	repz movsl

	debug_putchar('4')

	/* jump to new code in the sector starting at 0x00000E00 */

	/* just to learn various jumps */
#if 1
	# this way we needn't touch CS register
#if 1
	# and this way we needn't touch the stack
#if 0
	# and this even won't touch any registers
	# but unfortunately we don't know the
	# relative displacement
	// jmp	(1f - 0x????????)
#else
	# but this way we need to touch a register
	movl	$(1f - startup_32 + 0x00000E00), %eax
	jmp	*%eax		# Oh, don't use `jmp *(%eax)' by mistake!
				# Should use register indirect addressing,
				# not memory indirect addressing.
#endif
#else
	# and, this way we need the stack
	movl	$(1f - startup_32 + 0x00000E00), %eax
	pushl	%eax
	ret
#endif

#else
	# jump to new code. __BOOT_CS is this segment, and still 32 bit

	ljmp	$(__BOOT_CS), $(1f - startup_32 + 0x00000E00)
#endif

1:

	debug_putchar('5')

	/* We are executed in low memory rang 0x0E00 to 0x0FFF, and now
	 * it is safe to copy the rest code to 0x00001000
	 */

	movl	$((_dos_start - startup_32 - 0x200) / 4), %ecx
	repz movsl

	debug_putchar('6')

	/* default boot device: DH=partition number, DL=drive number */
	movl	$0x80, %edx

	/* At last, move pre_stage2 to 0x00008200 */

	movl	$0x00008200, %edi
	movl	$0x00020000, %ecx	# move 0x80000 bytes(512KB)
	movl	%ebp, %esi		# EBP=linear address of startup_32
	addl    $(pre_stage2_start - startup_32), %esi
					# ESI points to pre_stage2_start
	cmpl	$0x00008200, %esi
	jb	1f

	cld
	repz movsl
	jmp	2f

1:
	addl	$0x7fffc, %edi
	addl	$0x7fffc, %esi

	std				# downward
					# remember to clear it later!

	rep movsl			# EDI=0x00008200

	cld				# now clear it so we are safe
2:
	debug_putchar('7')

//----------------------------------------------------------------------------
	# resolve the commandline arguments and move preset_menu to 0x00000800

	# commandline has been copied to the sector starting at 0x00000800

	/* ECX = 0 */

	movl	$0x00000200, %ecx	# find the option in 1 sector
	//movb	$2, %ch			# ECX=0x200
	movl	$0x00000800, %esi	# starting at physical address 0x800

	/* look for a non-blank char */

	cld
3:
	lodsb
	cmpb	$0, %al
	je	4f			# end string, failure
	cmpb	$0x20, %al
	je	2f
	cmpb	$0x09, %al
	jne	1f
2:
	loop	3b			# load next byte, ECX decreased
	jmp	4f			#; all are blanks, failure
1:
	decl	%esi			# found, let ESI point to it
//	incl	%ecx

	/* This is a leading non-blank char. Check if it matches the option.
	 * option_config_file points to constant string "--config-file="
	 */
 
	movl	$(option_config_file - startup_32 + 0xE00), %edi

	pushl	%ecx

	movl	$(option_config_file_end - option_config_file), %ecx
	movl	%esi, %eax		# save ESI
	cld
	repz cmpsb			#; ESI, EDI both changed

	popl	%ecx

	je	1f			# success

	/* No match. Then look for a blank char. */
	movl	%eax, %esi		# restore ESI
	incl	%esi			# let ESI points to the char next to
					# the leading non-blank char.

	decl	%ecx

	cld
3:
	lodsb
	cmpb	$0, %al
	je	4f			# end string, failure
	cmpb	$0x20, %al
	je	2b			# Blank found, try again
	cmpb	$0x09, %al
	je	2b			# Blank found, try again
	loop	3b

4:
	/* failure: the option "--config-file" was not found. */

	debug_putchar('8')

	stc
	jmp	normal_config_file

1:
	debug_putchar('9')

	/* success: the option "--config-file" was found. */

	xorl	%ebx, %ebx
	cmpb	$0x22, (%esi)	/* 0x22 is the double quote char */
	jne	1f
	incl	%esi
	incl	%ebx		/* EBX=1 means a leading double quote exists */
1:
	cmpb	$0x28, (%esi)	/* 0x28 is "(" */
	je	normal_config_file	# CF=0
	cmpb	$0x2F, (%esi)	/* 0x2F is "/" */
	je	normal_config_file	# CF=0

	# locate the end of the commandline preset_menu

	movl	$0x000009ff, %ecx	# end of the sector
	subl	%esi, %ecx		# length of menu

	movl	$0x00000800, %edi

	testl	%ebx, %ebx		# quoted?
	jz	1f			# no

	/* change the double quote to NULL */

	pushl	%edi
	pushl	%ecx

	movl	%esi, %edi		# EDI points to source menu string
	movb	$0x22, %al		# locate the double quote
	cld
	repnz scasb
	jnz	4f			# not found, continue
	decl	%edi			# EDI points to the double quote
	movb	$0, (%edi)		# change to 0 in source string
4:
	popl	%ecx
	popl	%edi

	/* Move the command-line menu to 0x800, and change semi-colon
	 * to LF by the way.
	 */
1:
	cld
	lodsb
	cmpb	$0x3B, %al	/* semi-colon */
	jne	3f
	movb	$0x0A, %al	/* change to LF */
3:
	stosb
	cmpb	$0, %al
	je	4f
	loop	1b
4:

	# the config_file should be disabled

	movb	$0, (default_config_file - startup_32 + 0xE00)

	jmp	4f

normal_config_file:

	# clear preset_menu value at 0x820C to 0
	movl	$0, 0x0000820C

	jc	4f		/* no `--config-file=' option specified. */

	/* ESI points to the first byte of the filename. if it is not `(',
	 * then don't touch the boot device.
	 */

	xorl	%eax, %eax
	movl	%esi, %edi	/* save ESI */
	cmpb	$0x28, (%esi)	/* 0x28 is "(" */
	jne	1f
	lodsb
	lodsb
	cmpb	$0x30, %al	/* 0x30 is "0" */
	jb	4f		/* invalid config file */
	cmpb	$0x39, %al	/* 0x39 is "9" */
	jbe	2f		/* BIOS drive number */
	cmpb	$0x66, %al	/* 0x66 is "f" */
	je	3f
	movb	$0x80, %ah	/* for hard drive */
	cmpb	$0x68, %al	/* 0x68 is "h" */
	je	3f
	lodsb
	cmpb	$0x64, %al	/* 0x64 is "d" */
	je	1f
	jmp	4f		/* invalid config file */
3:
	/* hard drive or floppy */
	lodsb
	cmpb	$0x64, %al	/* 0x64 is "d" */
	jne	4f		/* invalid config file */
	
	lodsb
	cmpb	$0x30, %al	/* 0x30 is "0" */
	jb	4f		/* invalid config file */
	cmpb	$0x39, %al	/* 0x39 is "9" */
	ja	4f		/* invalid config file */
	
2:
	movl	$0x7f, %ebx	/* Max drive number */
	call	parse_number	/* parse drive number */
	jc	4f
	xchgl	%eax, %ebx	/* save drive number to EAX */
				/* BH=0 for floppy, and 0x80 for hard drive */
	orb	%bh, %al	/* adjust hard drive number */
	movb	$0xff, %bl	/* partition number for floppy */
	testb	%bh, %bh	/* floppy, skip the partition number parsing. */
	jz	5f
	movl	$0x7f, %ebx	/* Max partition number */
	call	parse_number	/* parse partition number */
	jc	4f
5:
				/* partition number is in BL */
	xchgl	%eax, %edx	/* save drive number to DL */
	movb	%bl, %dh	/* save partition number to DH */

	/* From now on, remember not to change DX until launching GRUB */

1:
	# move the specified config-file to default_config_file

	movl	%edi, %esi	/* restore ESI */
	movl	$0x4d, %ecx
	movl	$(default_config_file - startup_32 + 0xE00), %edi
	//cld
	repz movsb
4:
	debug_putchar('A')

//----------------------------------------------------------------------------

	//cld
	cli
	movl	$(head_idt_48 - startup_32 + 0xE00), %esi
					# ESI=linear address of idt_48
	lidt    (%esi)		# load idt at idt_48 with limit=0x3ff, base=0

	movl	$(head_gdt - startup_32 + 0xE00), %eax
					# EAX=linear address of gdt
	movl	$(head_gdt_48 - startup_32 + 0xE00), %esi
					# ESI=linear address of gdt_48
	movl    %eax, 2(%esi)		# let gdt_base = linear address of gdt
	lgdt    (%esi)			# load gdt at gdt_48

	# switch to 16bit protected mode code segment

	ljmp	$0x10 /*(__BOOT_CS)*/ , $(to_realmode - startup_32 + 0xE00)

//----------------------------------------------------------------------------
parse_number:

	/* input:	ESI	points to the number
	 *		EBX	upper limit of the number
	 * output:	EBX	the value of the number
	 *		ESI	points to the next byte after the delimiter
	 *		EBP	changed
	 *		CF=1	failure
	 *		CF=0	success
	 */

	pushl	%edx
	pushl	%eax
	pushl	%ebx		/* upper limit */
	cld
	movl	$16, %ebp	/* initialize EBP for hex */
	//movl	%edi, %esi
	movl	$0xffffffff, %edx
	xorl	%ebx, %ebx
	lodsw
	cmpw	$0x5830, %ax	/* 0X */
	je	2f
	cmpw	$0x7830, %ax	/* 0x */
	je	2f

	/* decimal */
	decl	%esi
	decl	%esi
	movl	$10, %ebp
2:
	xorl	%eax, %eax
	lodsb
	cmpb	$0, %al
	je	4f		/* CF=0 */
	cmpb	$0x2C, %al	/* 0x2C= `,' ends the drive number. */
	je	4f		/* CF=0 */
	cmpb	$0x29, %al	/* 0x29= `)' ends partition number. */
	je	4f		/* CF=0 */
	cmpb	$0x30, %al
	jb	3f
	cmpb	$0x39, %al
	jbe	1f
	cmpl	$16, %ebp	/* Is hex? */
	jb	3f		/* no, failure */
	orb	$0x20, %al
	cmpb	$0x61, %al
	jb	3f
	cmpb	$0x66, %al
	ja	3f
	subb	$0x27, %al
1:
	subb	$0x30, %al
	pushl	%eax
	movl	%ebx, %eax
	mull	%ebp
	movl	%eax, %ebx
	popl	%eax
	jc	3f
	addl	%eax, %ebx
	jc	3f
	popl	%eax
	pushl	%eax		/* upper limit */
	cmpl	%eax, %ebx
	ja	3f
	jmp	2b

4:
	testl	%edx, %edx	/* CF=0 */
	jz	1f		/* return success */
3:
	/* return failure */
	stc
1:
	popl	%eax		/* upper limit */
	popl	%eax
	popl	%edx
	ret

//----------------------------------------------------------------------------
option_config_file:
	.ascii	"--config-file="
option_config_file_end:

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
head_gdt:
//	.fill GDT_ENTRY_BOOT_CS,8,0

	# GDT entry 0(NULL entry)
	.word	0				# alignment byte
head_gdt_48:
	.word	head_gdt_end - head_gdt - 1	# gdt limit
	.word	0, 0				# gdt base (filled in later)

	# GDT entry 1(not used)
	.word	0				# alignment byte
head_idt_48:
	.word	0x3ff				# idt limit = 0x3ff
	.word	0, 0				# idt base = 0L

	# GDT entry 2(__BOOT_CS)
	.word	0xFFFF				# limit 64Kb - (0x10000 = 64Kb)
	.word	0				# base address = 0
	.word	0x9A00				# code read/exec
	.word	0x0000				# granularity = 1, 386
						#  (+5th nibble of limit)

	# GDT entry 3(__BOOT_DS)
	.word	0xFFFF				# limit 64Kb - (0x10000 = 64Kb)
	.word	0				# base address = 0
	.word	0x9200				# data read/write
	.word	0x0000				# granularity = 1, 386
						#  (+5th nibble of limit)
head_gdt_end:

	/* Here comes the initial stack pointer of DOS executable.
	 * Note that grub as a dos EXE would call init_pic below, so the
	 * stack should be here to avoid overwriting the code in init_pic.
	 */

	/* Also note that the stack pointer should be dword aligned */

	.align	4

dos_stack:
	
	.code16

	# real mode startup code for pre_stage2
	# load all segment registers

to_realmode:
	cli
	movw	$(__BOOT_DS), %ax
	movw	%ax, %ds
	movw	%ax, %es
	movw	%ax, %fs
	movw	%ax, %gs
	movw	%ax, %ss
	movl	%cr0, %eax
	andl	$0x00000011, %eax	/* turn off paging */
//	orl	$0x60000000, %eax	/* cache disabled! */
	movl	%eax, %cr0
	movl	%eax, %cr3	/* reload page dir to asure paging off */
//	movl	%cr0, %ebx
//	andl	$0x60000000, %ebx	/* test if wbinvd is supported */
//	jz	1f
//	wbinvd
//1:
	andb	$0x10, %al		/* mask off the PE bit */
	movl	%eax, %cr0

	/* far jump to load the real mode CS */
	ljmp	$0, $(1f - startup_32 + 0xE00)
1:
	/* Now we are in real mode */
	xorw	%ax, %ax
	movw	%ax, %ds
	movw	%ax, %es
	movw	%ax, %fs
	movw	%ax, %gs
	movw	%ax, %ss
	movl	$0x400, %esp		/* clear high word of ESP */
	xorl	%ebp, %ebp

	pushw	%dx			/* boot drive and partition number */

	call	init_pic

	popw	%dx			/* boot drive and partition number */

	# old code, should be deleted later
	// /* ensure this is in the sector starting at 0000:0A00 */
	//
	// . = . - ((0xA00 - 1)/ (. - startup_32 + 0x800))
	//
	// /* It is right time to move the menu sector at 0x600 onto 0x800 */
	// movw	$0x600, %si
	// movw	$0x800, %di
	// movw	$0x080, %cx		/* move 1 sector */
	// cld
	// repz movsl

	/* put the config file name */
	
	movw    $0x0010, %cx	/* set max length of grub version string */
	movw    $0x8212, %di	/* version string */
	xorw	%ax, %ax	/* AL=0. Locate the end of version string */

	/* pre_stage2_start+0xA holds the boot partition number. The default
	 * partition number is 0(and default drive number is 0x80 in DL)
	 */
	movb	%dh, -8(%di)	/* 0x820A, the boot partition number */
	orb	$2, -13(%di)	/* 0x8205, disable keyboard intervention */

	cld
	repnz scasb	/* find the location of the default config file name */
	jcxz	1f	/* failed, will not use the default config file name */

	movw    $0x4e, %cx	/* max length of config file name */
	movw	$(default_config_file - startup_32 + 0xE00), %si
	cld
	repz movsb	/* move file name to the config-file field of stage2 */
1:
	//sti

	movw	$0x0003, %ax	/* set display mode: 80*25 color text */
	int	$0x10

	movw	$(launch_pre_stage2 - startup_32 + 0xE00), %si
	call	print_message

	xorw	%ax, %ax
	movw	%ax, %ss
	movw	$0x2000, %sp
	//movb	$0x80, %dl	/* default boot_drive is (hd0) */

	//sti
	ljmp	$0, $0x8200	//jmp	pre_stage2_start

init_pic:

#if 1		/* enabled 2008-05-23 */
	/* this is needed for booting via win98 */

	xorw	%ax, %ax

	/* init DMA, stolen from bochs(rombios.c) */

	#; first reset the DMA controllers
	outb	%al, $0x0D	#; disable DMA-1
	outb	%al, $0xDA	#; disable DMA-2
	movl	$2, %ecx		# delay at least 2 microseconds
	call	iodelay

	#; then initialize the DMA controllers
	movb	$0xC0, %al	#; cascade mode of channel 4 enabled
	outb	%al, $0xD6	#; DMA-2 mode register
	movb	$0x00, %al	#; unmask channel 4
	outb	%al, $0xD4	#; DMA-2 mask register
	movl	$2, %ecx		# delay at least 2 microseconds
	call	iodelay
#endif

	/* initialize PIC. */

	//outb(0xff, PIC_MASTER_IMR);	/* mask all of 8259A-1 */
	//outb(0xff, PIC_SLAVE_IMR);	/* mask all of 8259A-2 */

#if 1	/* marked off 2007-10-07, enabled 2008-05-23 */
	/* send clear_mask command to slave and master */
	movb	$0x48, %al
	call	send_command_to_slave_and_master

	/* send EOI command to slave and master */
	movb	$0x20, %al
	call	send_command_to_slave_and_master

	/* set IRQ15 and IRQ7 to least privilege */
	movb	$0xC7, %al
	call	send_command_to_slave_and_master
#endif


#if 1	/* marked off 2007-10-07, enabled 2008-05-23 */
	########################################################################################
	## make sure any possible coprocessor is properly reset..
	########################################################################################

	xorw	%ax, %ax
	movw	$0xF0, %dx	# write a byte of 0 to port F0 will clear the busy bit of math coprocessor
	call	outb_and_delay

	movw	$0xF1, %dx	# write a byte of 0 to port F1 will reset coprocessor and switch it to real mode
	call	outb_and_delay
#endif

	########################################################################################
	## Now we mask all interrupts
	########################################################################################

	movb	$0xFF, %al	# mask all interrupts for now
	movw	$0xA1, %dx
	call	outb_and_delay
	
	movb	$0xFB, %al	# mask all irq's but irq2 which is cascaded
	movw	$0x21, %dx
	call	outb_and_delay

	/*
	 * outb_p - this has to work on a wide range of PC hardware.
	 */

	cli

	//outb_p(0x11, PIC_MASTER_CMD);	/* ICW1: select 8259A-1 init */
	movb	$0x11, %al
	movw	$0x20, %dx
	call	outb_and_delay

	//outb_p(0x20 + 0, PIC_MASTER_IMR);	/* ICW2: 8259A-1 IR0-7 mapped to 0x20-0x27 */
	movb	$0x08, %al
	movw	$0x21, %dx
	call	outb_and_delay

	//outb_p(1U << PIC_CASCADE_IR, PIC_MASTER_IMR);	/* 8259A-1 (the master) has a slave on IR2 */
	movb	$0x04, %al
	movw	$0x21, %dx
	call	outb_and_delay

	/* Yes, the normal EOI should be used for real mode OS. */

#if 0 //if (auto_eoi)	/* master does Auto EOI */
	//outb_p(MASTER_ICW4_DEFAULT | PIC_ICW4_AEOI, PIC_MASTER_IMR);
	movb	$0x03, %al
	movw	$0x21, %dx
	call	outb_and_delay
#else //else		/* master expects normal EOI */
	//outb_p(MASTER_ICW4_DEFAULT, PIC_MASTER_IMR);
	movb	$0x01, %al
	movw	$0x21, %dx
	call	outb_and_delay
#endif

	//outb_p(0x11, PIC_SLAVE_CMD);	/* ICW1: select 8259A-2 init */
	movb	$0x11, %al
	movw	$0xA0, %dx
	call	outb_and_delay

	//outb_p(0x20 + 8, PIC_SLAVE_IMR);	/* ICW2: 8259A-2 IR0-7 mapped to 0x28-0x2f */
	movb	$0x70, %al
	movw	$0xA1, %dx
	call	outb_and_delay

	//outb_p(PIC_CASCADE_IR, PIC_SLAVE_IMR);	/* 8259A-2 is a slave on master's IR2 */
	movb	$0x02, %al
	movw	$0xA1, %dx
	call	outb_and_delay

	//outb_p(SLAVE_ICW4_DEFAULT, PIC_SLAVE_IMR); /* (slave's support for AEOI in flat mode is to be investigated) */
	movb	$0x01, %al
	movw	$0xA1, %dx
	call	outb_and_delay

#if 0 //if (auto_eoi)
		/*
		 * in AEOI mode we just have to mask the interrupt
		 * when acking.
		 */
		//i8259A_irq_type.ack = disable_8259A_irq;
#else //else
		//i8259A_irq_type.ack = mask_and_ack_8259A;
#endif

	//udelay(100);		/* wait for 8259A to initialize */
	movl	$100, %ecx		# delay at least 100 microseconds
	call	iodelay

	//outb(cached_master_mask, PIC_MASTER_IMR);	/* restore master IRQ mask */
	//outb(cached_slave_mask, PIC_SLAVE_IMR);	/* restore slave IRQ mask */

	cli

	movb    $0x00, %al		# enable all IRQs
	movw	$0x21, %dx
	call	outb_and_delay

	movb    $0x00, %al		# enable all the cascaded IRQs
	movw	$0xA1, %dx
	call	outb_and_delay

	//udelay(100);		/* wait for 8259A to initialize */
	movl	$100, %ecx		# delay at least 100 microseconds
	call	iodelay

	/* end initialize PIC. */

	/* FIXME: init edge-level-control-registers(IO ports 0x4D0, 0x4D1) for EISA */

#if 1		/* enabled 2008-05-23 */
	/* this is needed for booting via win98 */

	/* EISA 8259-1 */
	/* init system timer 0 (stolen from bochs rombios.c) */

	//movb	$0x34, %al	# system timer 0, 16-bit binary count, mode 2
	movb	$0x36, %al	# system timer 0, 16-bit binary count, mode 3
				# system timer 0 should be in mode 3

	movw	$0x43, %dx
	call	outb_and_delay

	movb	$0x00, %al	# maximum count of 0000H = 18.2Hz
	movw	$0x40, %dx
	call	outb_and_delay	# write lo byte 00
	call	outb_and_delay	# write hi byte 00
#endif

#if 0	/* marked off 2008-05-23 */
	/* disable NMI */
	orb	$0x80, %al
	outb	%al, $0x70
	movl	$2, %ecx		# delay at least 2 microseconds
	call	iodelay
#endif

	/* init PCI (stolen from bochs rombios.c) */

#if 0
	call	pcibios_init_iomem_bases
	call	pcibios_init_irqs
#endif

#if 0
	/* this is needed for booting via win98 */

	/* EISA 8259-1 */
	movw	$0x4D0, %dx
	inb	%dx, %al
	movw	$0x21, %dx	# mask off level-triggerred IRQs
	call	outb_and_delay

	/* EISA 8259-2 */
	movw	$0x4D1, %dx
	inb	%dx, %al
	movw	$0xA1, %dx	# mask off level-triggerred IRQs
	call	outb_and_delay
#endif

#if 1	/* marked off 2007-10-07, enabled 2008-05-23 */
	movb	$0x20, %al	#; send EOI to 8259A-2
	movw	$0xA0, %dx
	call	outb_and_delay

	movb	$0x20, %al	#; send EOI to 8259A-1
	movw	$0x20, %dx
	call	outb_and_delay
#endif

#if 0
	movw	$0x461, %dx
	inb	%dx, %al
	andb	$0xF0, %al
	call	outb_and_delay
#endif

#if 0
	movb	$0x0C, %al
	outb	%al, $0xA1
	xorw	%cx, %cx
1:	loop	1b

	movb	$0x08, %al
	outb	%al, $0x21
	xorw	%cx, %cx
1:	loop	1b
#endif

#if 0
	/* reset mouse */
	movw	$0xC201, %ax
	int	$0x15

	/* disable mouse */
	movw	$0xC200, %ax
	xorw	%bx, %bx	/* BH=0 means disable */
	int	$0x15

	/* set mouse handler address */
	movw	$0xC207, %ax
	xorw	%bx, %bx	/* ES:BX=0000:0000 to cancel the handler */
	int	$0x15

	/* disable monitor clock (Watch-Dog) */
	movw	$0xC300, %ax
	int	$0x15
#endif

	ret


#if 0
	.align 16

pci_routing_table_structure:
	.byte	0x24, 0x50, 0x49, 0x52	#; "$PIR" signature
	.byte	0, 1	#; version
	.word	32 + (6 * 16)	#; table size
	.byte	0	#; PCI interrupt router bus
	.byte	0x08	#; PCI interrupt router DevFunc
	.word	0x0000	#; PCI exclusive IRQs 
	.word	0x8086	#; compatible PCI interrupt router vendor ID
	.word	0x7000	#; compatible PCI interrupt router device ID
	.word	0,0	#; Miniport data
	.byte	0,0,0,0,0,0,0,0,0,0,0	#; reserved
	.byte	0x07	#; checksum
	#;	first slot entry PCI-to-ISA (embedded)
	.byte	0	#; pci bus number
	.byte	0x08	#; pci device number (bit 7-3)
	.byte	0x60	#; link value INTA#: pointer into PCI2ISA config space
	.word	0xdef8	#; IRQ bitmap INTA# 
	.byte	0x61	#; link value INTB#
	.word	0xdef8	#; IRQ bitmap INTB# 
	.byte	0x62	#; link value INTC#
	.word	0xdef8	#; IRQ bitmap INTC# 
	.byte	0x63	#; link value INTD#
	.word	0xdef8	#; IRQ bitmap INTD#
	.byte	0	#; physical slot (0 = embedded)
	.byte	0	#; reserved
	#;	second slot entry: 1st PCI slot
	.byte	0	#; pci bus number
	.byte	0x10	#; pci device number (bit 7-3)
	.byte	0x61	#; link value INTA#
	.word	0xdef8	#; IRQ bitmap INTA# 
	.byte	0x62	#; link value INTB#
	.word	0xdef8	#; IRQ bitmap INTB# 
	.byte	0x63	#; link value INTC#
	.word	0xdef8	#; IRQ bitmap INTC# 
	.byte	0x60	#; link value INTD#
	.word	0xdef8	#; IRQ bitmap INTD#
	.byte	1	#; physical slot (0 = embedded)
	.byte	0	#; reserved
	#;	third slot entry: 2nd PCI slot
	.byte	0	#; pci bus number
	.byte	0x18	#; pci device number (bit 7-3)
	.byte	0x62	#; link value INTA#
	.word	0xdef8	#; IRQ bitmap INTA# 
	.byte	0x63	#; link value INTB#
	.word	0xdef8	#; IRQ bitmap INTB# 
	.byte	0x60	#; link value INTC#
	.word	0xdef8	#; IRQ bitmap INTC# 
	.byte	0x61	#; link value INTD#
	.word	0xdef8	#; IRQ bitmap INTD#
	.byte	2	#; physical slot (0 = embedded)
	.byte	0	#; reserved
	#;	4th slot entry: 3rd PCI slot
	.byte	0	#; pci bus number
	.byte	0x20	#; pci device number (bit 7-3)
	.byte	0x63	#; link value INTA#
	.word	0xdef8	#; IRQ bitmap INTA# 
	.byte	0x60	#; link value INTB#
	.word	0xdef8	#; IRQ bitmap INTB# 
	.byte	0x61	#; link value INTC#
	.word	0xdef8	#; IRQ bitmap INTC# 
	.byte	0x62	#; link value INTD#
	.word	0xdef8	#; IRQ bitmap INTD#
	.byte	3	#; physical slot (0 = embedded)
	.byte	0	#; reserved
	#;	5th slot entry: 4rd PCI slot
	.byte	0	#; pci bus number
	.byte	0x28	#; pci device number (bit 7-3)
	.byte	0x60	#; link value INTA#
	.word	0xdef8	#; IRQ bitmap INTA# 
	.byte	0x61	#; link value INTB#
	.word	0xdef8	#; IRQ bitmap INTB# 
	.byte	0x62	#; link value INTC#
	.word	0xdef8	#; IRQ bitmap INTC# 
	.byte	0x63	#; link value INTD#
	.word	0xdef8	#; IRQ bitmap INTD#
	.byte	4	#; physical slot (0 = embedded)
	.byte	0	#; reserved
	#;	6th slot entry: 5rd PCI slot
	.byte	0	#; pci bus number
	.byte	0x30	#; pci device number (bit 7-3)
	.byte	0x61	#; link value INTA#
	.word	0xdef8	#; IRQ bitmap INTA# 
	.byte	0x62	#; link value INTB#
	.word	0xdef8	#; IRQ bitmap INTB# 
	.byte	0x63	#; link value INTC#
	.word	0xdef8	#; IRQ bitmap INTC# 
	.byte	0x60	#; link value INTD#
	.word	0xdef8	#; IRQ bitmap INTD#
	.byte	5	#; physical slot (0 = embedded)
	.byte	0	#; reserved
#endif

pci_irq_list:
	.byte	11, 10, 9, 5

pcibios_init_sel_reg:

	# input:
	#	BX	hi 16 bit of address
	#	DL	lo  8 bit of address
	# output:
	#	register was selected
	#	DX	0x0cf8

	pushl	%eax
	movl	$0x800000, %eax
	movw	%bx, %ax
	shll	$8, %eax
	andb	$0xfc, %dl
	orb	%dl, %al
	movw	$0x0cf8, %dx
	outl	%eax, %dx
	popl	%eax
	ret

pcibios_init_iomem_bases:
	pushw	%bp
	movw	%sp, %bp
	movl	$0xe0000000, %eax	#; base for memory init
	pushl	%eax
	movw	$0xc000, %ax		#; base for i/o init
	pushw	%ax
	movw	$0x0010, %ax		#; start at base address #0
	pushw	%ax
	movw	$0x0008, %bx		#; hi 16-bit

pci_init_io_loop1:
	movb	$0x00, %dl		#; lo 8-bit
	call	pcibios_init_sel_reg
	movw	$0x0cfc, %dx
	inw	%dx, %ax
	cmpw	$0xffff, %ax
	jz	next_pci_dev
	movb	$0x04, %dl		#; disable i/o and memory space access
	call	pcibios_init_sel_reg
	movw	$0x0cfc, %dx
	inb	%dx, %al
	andb	$0xfc, %al
	outb	%al, %dx

pci_init_io_loop2:
	movb	-8(%bp), %dl
	call	pcibios_init_sel_reg
	movw	$0x0cfc, %dx
	inl	%dx, %eax
	testb	$0x01, %al
	jnz	init_io_base
	movl	%eax, %ecx
	movl	$0xffffffff, %eax
	outl	%eax, %dx
	inl	%dx, %eax
	cmpl	%ecx, %eax
	je	next_pci_base
	xorl	$0xffffffff, %eax
	movl	%eax, %ecx
	movl	-4(%bp), %eax
	outl	%eax, %dx
	addl	%ecx, %eax		#; calculate next free mem base
	addl	$0x01000000, %eax
	andl	$0xff000000, %eax
	movl	%eax, -4(%bp)
	jmp	next_pci_base

init_io_base:
	movw	%ax, %cx
	movw	$0xffff, %ax
	outw	%ax, %dx
	inw	%dx, %ax
	cmpw	%cx, %ax
	je	next_pci_base
	xorw	$0xfffe, %ax
	movw	%ax, %cx
	movw	-6(%bp), %ax
	outw	%ax, %dx
	addw	%cx, %ax		#; calculate next free i/o base
	addw	$0x0100, %ax
	andw	$0xff00, %ax
	movw	%ax, -6(%bp)

next_pci_base:
	movb	-8(%bp), %al
	addb	$0x04, %al
	cmpb	$0x28, %al
	je	enable_iomem_space
	movb	%al, -8(%bp)
	jmp	pci_init_io_loop2

enable_iomem_space:
	movb	$0x04, %dl		#; enable i/o and memory space access if available
	call	pcibios_init_sel_reg
	movw	$0x0cfc, %dx
	inb	%dx, %al
	orb	$0x07, %al
	outb	%al, %dx

next_pci_dev:
	movb	$0x10, -8(%bp)
	incw	%bx
	cmpw	$0x0100, %bx
	jne	pci_init_io_loop1
	movw	%bp, %sp
	popw	%bp
	ret

pcibios_init_set_elcr:
	pushw	%ax
	pushw	%cx
	movw	$0x04d0, %dx
	testb	$0x08, %al
	jz	is_master_pic
	incw	%dx
	andb	$0x07, %al

is_master_pic:
	movb	%al, %cl
	movb	$0x01, %bl
	shlb	%cl, %bl
	inb	%dx, %al
	orb	%bl, %al
	outb	%al, %dx
	popw	%cx
	popw	%ax
	ret

pcibios_init_irqs:
	pushw	%ds
	pushw	%bp

	movw	$0xf000, %ax
	movw	%ax, %ds		# DS=0xF000

	movw	$0x04d0, %dx		#; reset ELCR1 + ELCR2
	movb	$0x00, %al
	outb	%al, %dx
	incw	%dx
	outb	%al, %dx

	/* find pci_routing_table_structure in ROM range F0000-FFFF0 */

	cld
	xorw	%si, %si
1:
	lodsl
	addw	$12, %si		#; points to next paragraph
	jc	pci_init_end		#; PCI IRQ Routing Table not found
	cmpl	$0x52495024, %eax	#; "$PIR" signature
	jnz	1b			#; try next paragraph

	/* table size must be larger than 32 and must be a multiple of 16 */
	movw	-10(%si), %ax
	cmpw	$32, %ax
	jb	1b			#; try next paragraph
	testb	$0x0F, %al
	jnz	1b			#; try next paragraph

	/* sum of all bytes in the PCI IRQ Routing Table should be 0 */

	pushw	%si
	movw	%ax, %cx		#; table size
	subw	$16, %si		#; points to table
	xorw	%ax, %ax
2:
	lodsb
	addb	%al, %ah
	loop	2b
	testb	%ah, %ah
	popw	%si
	jnz	1b			#; try next paragraph

	subw	$16, %si		#; points to table
	movb	8(%si), %bh
	movb	9(%si), %bl
	movb	$0x00, %dl
	call	pcibios_init_sel_reg
	movw	$0x0cfc, %dx
	inl	%dx, %eax

	cmpl	12(%si), %eax		#; check irq router
	jne	pci_init_end

	movb	34(%si), %dl
	call	pcibios_init_sel_reg

	pushw	%bx			#; save irq router bus + devfunc

	movw	$0x0cfc, %dx
	movw	$0x8080, %ax
	outw	%ax, %dx		#; reset PIRQ route control
	incw	%dx
	incw	%dx
	outw	%ax, %dx
	movw	6(%si), %ax
	subw	$0x20, %ax
	shrw	$4, %ax
	movw	%ax, %cx
	addw	$0x20, %si		#; set pointer to 1st entry

	movw	%sp, %bp

	/* calculate pointer value pci_irq_list relative to CS segment */
	call	1f
1:
	popw	%ax			/* AX=instruction pointer of 1b */

	subw	$(1b - pci_irq_list), %ax	/* AX=instruction pointer of pci_irq_list */
	pushw	%ax			#; save pointer to stack

	xorw	%ax, %ax
	pushw	%ax			#; push 0

pci_init_irq_loop1:
	movb	(%si), %bh
	movb	1(%si), %bl

pci_init_irq_loop2:
	movb	$0x00, %dl
	call	pcibios_init_sel_reg
	movw	$0x0cfc, %dx
	inw	%dx, %ax
	cmpw	$0xffff, %ax
	jnz	pci_test_int_pin
	testb	$0x07, %bl
	jz	next_pir_entry
	jmp	next_pci_func

pci_test_int_pin:
	movb	$0x3c, %dl
	call	pcibios_init_sel_reg
	movw	$0x0cfd, %dx
	inb	%dx, %al
	andb	$0x07, %al
	jz	next_pci_func
	decb	%al			#; determine pirq reg
	movb	$0x03, %dl
	//mulb	%dl, %al
	mulb	%dl
	addb	$0x02, %al
	xorb	%ah, %ah
	movw	%ax, %bx
	movb	(%bx, %si), %al
	movb	%al, %dl
	movw	(%bp), %bx
	call	pcibios_init_sel_reg
	movw	$0x0cfc, %dx
	andb	$0x03, %al
	addb	%al, %dl
	inb	%dx, %al
	cmpb	$0x80, %al
	jb	pirq_found

	movw	-2(%bp), %bx		#; pci_irq_list pointer
	movb	%cs:(%bx), %al
	outb	%al, %dx
	incw	%bx
	movw	%bx, -2(%bp)		#; points to next irq
	call	pcibios_init_set_elcr

pirq_found:
	movb	(%si), %bh
	movb	1(%si), %bl
	addb	-3(%bp), %bl		#; pci function number
	movb	$0x3c, %dl
	call	pcibios_init_sel_reg
	movw	$0x0cfc, %dx
	outb	%al, %dx

next_pci_func:
	incb	-3(%bp)
	incb	%bl
	testb	$0x07, %bl
	jnz	pci_init_irq_loop2

next_pir_entry:
	addw	$0x10, %si
	movb	$0x00, -3(%bp)
	loop	pci_init_irq_loop1
	movw	%bp, %sp
	popw	%bx

pci_init_end:
	popw	%bp
	popw	%ds
	ret




send_command_to_slave_and_master:
	movw	$0xA0, %dx
	call	outb_and_delay
	movw	$0x20, %dx
	call	outb_and_delay
	ret


outb_and_delay:
	outb	%al, %dx
	movl	$2, %ecx		# delay at least 2 microseconds
	call	iodelay
	ret

iodelay:
	/* input:	ECX - microseconds to delay */

	/* On a 4GHz CPU, we needs roughly 4G/1000000=4000 clocks
	 * for a microsecond.
	 */

	shll	$14, %ecx	/* 2**14=4096*4, 4 times of a microsecond */
1:
	addr32 loop	1b
	ret

	/* prints string DS:SI (modifies AX BX SI) */
3:
	//xorw	%bx, %bx	/* video page 0 */
	movb	$0x0e, %ah	/* print char in AL */
	int	$0x10		/* via TTY mode */

print_message:

	lodsb	(%si), %al	/* get token */
	cmpb	$0, %al		/* end of string? */
	jne	3b
	ret


launch_pre_stage2:
	.ascii	"\r\n\r\nLaunching GRUB...\r\n"

	.byte	0		/* mark the end of ascii zero string */

default_config_file:
	.ascii	"/menu.lst"
default_config_file_end:

	.byte	0		/* mark the end of ascii zero string */

	. = default_config_file + 0x4d

	.byte	0		/* mark the end of ascii zero string */

	// . = _start + 0x2400

	.align 0x200

#-----------------------------------------------------------------------------
#		Linux kernel structure ends here
#-----------------------------------------------------------------------------

//////////////////////////////////////////////////////////////////////////////

#-----------------------------------------------------------------------------
#			DOS EXE code begins here
#
#	Segment base of CS and SS is START: CS:0000=SS:0000=START=(PSP+0x2E0)
#	Segment base of DS and ES is PSP  : DS:0000=ES:0000=PSP=(START-0x2E0)
#
#-----------------------------------------------------------------------------

//dos_stack:
_dos_start:

	/* Code from startup_32 to _dos_start will be copied to 0x0E00-0x8000
	 * when grub.exe is used as a linux kernel. So check the length here
	 */

	. = . - ((_dos_start - startup_32) / (0x8000 - 0x0E00 + 1))

	/* first, move command line to CS:0081 */

	//cli			/* marked off 2008-08-04 */

	cld			/* move upward */
	movw	$0x80, %si
	movw	%cs, %ax
	movw	%ax, %es
	movw	%si, %di
	movw	%si, %cx	/* move 0x80 bytes */
	repz movsb

	movw	%ax, %ds

	/* non-zero indicates EXE rather than device driver */ 
	movb	$1, 0x80
	movb	$0x00, 0xff	/* end it with NULL */

_dos_start1:
	/* At here DS=ES=CS=SS */

	sti			/* added 2008-08-04, and marked off cli */
	//cli			/* disable interrupt for usb keyboard hack */

	/* XXX: Maybe we should better mask off all IRQs
	 * and disable NMI here
	 */

//----------------------------------------------------------------------------
	/* change all TABs to spaces, and the first CR/LF char to NULL */

	cld			/* load upward */
	movw	$0x0081, %si	/* get command line */
	movw	$0x1000, %cx	/* max length of command line */
1:
	lodsb
	cmpb	$0x00, %al	/* NULL */
	je	1f
	cmpb	$0x0D, %al	/* CR */
	je	1f
	cmpb	$0x0A, %al	/* LF */
	je	1f
	cmpb	$0x09, %al	/* TAB */
	jne	2f
	movb	$0x20, -1(%si)	/* change TAB to SPACE */
	jmp	3f
2:
	cmpb	$0x20, %al	/* another non-printable char below SPACE? */
	jb	invalid_option	/* yes, invalid */
3:
	loop	1b
1:
	decw	%si		/* SI points to the ending NULL */
	movb	$0x00, (%si)	/* change CR/LF to NULL */
	

//----------------------------------------------------------------------------
	/* change the leading slash and chars upto "--" to spaces */ 

	cld			/* scan upward */
	movw	$0x0081, %di	/* get command line */
	movw	%si, %cx
	subw	%di, %cx	/* length of command line */
	movb	$0x20, %al	/* the space bar */
	repz scasb		/* skip spaces */
	jz	3f		/* the line contains only spaces */

	/* scas always increment/decrement DI, so DI > 0x81 */

	decw	%di		/* points to the first non-space char */
	incw	%cx

	cmpb	$0x2f, (%di)	/* check if the leading char is a slash */
	je	2f
	cmpb	$0x00, (%di)	/* check if the leading char is NULL */
	je	3f
	cmpw	$0x2d2d, (%di)	/* check if the leading pair is "--" */
	je	1f		/* yes, continue */
	jmp	invalid_option
2:
	/* yes, it is a possible switch inserted by Microsoft for the
	 * SHELL=GRUB.EXE line in CONFIG.SYS, so we wipe it out...
	 */

	stosb			/* change the leading slash to space... */

	/* ... and change all the rest chars to spaces, up to the pair "--" */
2:
	cmpb	$0x20, (%di)	/* check if the next char is printable */
	jb	3f		/* this is NULL, and command line is empty */
	cmpw	$0x2d2d, (%di)	/* check if the next pair is "--" */
	je	1f		/* yes, continue */
	stosb			/* change the char to space bar */
	loop	2b
				/* no "--" is found */
3:
use_default_config_file:

	/* no option specified */

	/* first, try .\menu.lst */

	/* SI points to filename */
	movw	$ABS_PSP(default_config_file_dos1), %si
	call	open_dos_file
	jnc	3f		/* success */

	/* second, try \menu.lst */

	/* SI points to filename */
	movw	$ABS_PSP(default_config_file_dos2), %si
	call	open_dos_file
	jnc	3f		/* success */

	/* last, use default config file */

	movw	$ABS_PSP(default_config_file_dos), %si
	movw	$(default_config_file_dos_end - default_config_file_dos), %cx
	jmp	put_config_file_name
3:
	jmp	raw_commands_embedded
	///* setup saved_entry_no, etc. */
	//jmp	done_options
1:
//----------------------------------------------------------------------------
	/* when we get here, DI points to the leading "--" */

	pushw	%si
	pushw	%di
	pushw	%si
	pushw	%di
	/* find options --bypass, --time-out=T, --hot-key=K, --duce, --chs-no-tune */
4:
	popw	%di
	popw	%si
	pushw	%si
	pushw	%di
	cld
	movw	%si, %cx
	subw	%di, %cx	/* length of command line */
	movb	$0x2d, %al	/* "-" */
1:
	repnz scasb
	testw	%cx, %cx
	jnz	2f
	/* not found */
	movb	ABS_PSP(options_doing), %al
	orb	%al, ABS_PSP(options_done)
	popw	%ax		/* discard old DI */
	popw	%ax		/* discard old SI */
	popw	%di		/* restore original DI */
	popw	%si		/* restore original SI */
	pushw	%si		/* push SI back to stack */
	pushw	%di		/* push DI back to stack */
	pushw	%si		/* push SI again */
	pushw	%di		/* push DI again */
	jmp	3f
2:
	cmpb	$0x2d, (%di)	/* the second "-" */
	jne	1b
	decw	%di
	incw	%cx
	popw	%dx
	pushw	%dx
	cmpw	%dx, %di
	jbe	3f
	incw	%di
	decw	%cx
	incw	%di
	decw	%cx
	cmpb	$0x20, -3(%di)
	jne	1b
	decw	%di
	incw	%cx
	decw	%di
	incw	%cx

	//pushw	%di
3:
	testb	$1, ABS_PSP(options_done)
	jne	5f

	movl	$1, ABS_PSP(options_doing)
	/* compare with "--bypass" */
	cld			/* compare upward */
	movw	$ABS_PSP(option_bypass_dos), %si
	movw	%di, %dx	/* DI is our option string, save to DX */
	movw	$(option_bypass_dos_end - option_bypass_dos), %cx
				/* length of the string */
	repz cmpsb
	jz	2f		/* yes, exactly */

	movw	$ABS_PSP(option_bypass1_dos), %si
	movw	%dx, %di	/* restore DI from DX */
	movw	$(option_bypass1_dos_end - option_bypass1_dos), %cx
				/* length of the string */
	repz cmpsb
	jnz	3f
2:
	/* found "--bypass" */
	cmpb	$0x20, (%di)
	je	2f
	cmpb	$0, (%di)
	jne	3f
	//orb	$1, ABS_PSP(options_done)
2:
	cmpl	$0, ABS_PSP(bypass)
	jne	invalid_option	/* specify --bypass twice */
	movl	$1, ABS_PSP(bypass)
	/* wipe off "--bypass" */
	movw	$(option_bypass_dos_end - option_bypass_dos), %cx
	subw	%cx, %di
	movb	$0x22, %al	/* double-quote */
	stosb
	decw	%cx
	movb	$0x20, %al	/* SPACE */
	repz stosb
3:
	popw	%ax		/* discard old DI */
	pushw	%di		/* push new DI */
	//testb	$1, ABS_PSP(options_done)
	//jz	4b
	jmp	4b

	//popw	%di
	//pushw	%di
5:

	testb	$2, ABS_PSP(options_done)
	jne	5f

	movl	$2, ABS_PSP(options_doing)
	/* compare with "--time-out=" */
	cld			/* compare upward */
	movw	$ABS_PSP(option_time_out_dos), %si
	movw	%di, %dx	/* DI is our option string, save to DX */
	movw	$(option_time_out_dos_end - option_time_out_dos), %cx
				/* length of the string */
	repz cmpsb
	jz	2f		/* yes, exactly */

	movw	$ABS_PSP(option_time_out1_dos), %si
	movw	%dx, %di	/* restore DI from DX */
	movw	$(option_time_out1_dos_end - option_time_out1_dos), %cx
				/* length of the string */
	repz cmpsb
	jnz	3f
2:
	/* found "--time-out=" */
	movl	$0x000000ff, %ebx	/* upper limit of time-out */
	movw	%di, %si
	call	parse_number_dos
	jc	invalid_option		/* invalid time-out value */
	decw	%si
	movw	%si, %cx
	subw	%di, %cx
	movw	%si, %di
	lodsb
	cmpb	$0x20, %al
	je	2f
	cmpb	$0, %al
	jne	invalid_option		/* invalid time-out value */
	//orb	$2, ABS_PSP(options_done)
2:
	cmpl	$0x80000000, ABS_PSP(time_out)
	jne	invalid_option		/* specify time-out twice */
	movl	%ebx, ABS_PSP(time_out)
	/* wipe off "--time-out=T" */
	addw	$(option_time_out_dos_end - option_time_out_dos), %cx
	subw	%cx, %di
	movb	$0x22, %al	/* double-quote */
	stosb
	decw	%cx
	movb	$0x20, %al	/* SPACE */
	repz stosb
3:
	popw	%ax		/* discard old DI */
	pushw	%di		/* push new DI */
	//testb	$2, ABS_PSP(options_done)
	//jz	4b
	jmp	4b

	//popw	%di
	//pushw	%di

5:

	testb	$4, ABS_PSP(options_done)
	jne	5f

	movl	$4, ABS_PSP(options_doing)
	/* compare with "--hot-key=" */
	cld			/* compare upward */
	movw	$ABS_PSP(option_hot_key_dos), %si
	movw	%di, %dx	/* DI is our option string, save to DX */
	movw	$(option_hot_key_dos_end - option_hot_key_dos), %cx
				/* length of the string */
	repz cmpsb
	jz	2f		/* yes, exactly */

	movw	$ABS_PSP(option_hot_key1_dos), %si
	movw	%dx, %di	/* restore DI from DX */
	movw	$(option_hot_key1_dos_end - option_hot_key1_dos), %cx
				/* length of the string */
	repz cmpsb
	jnz	3f
2:
	/* found "--hot-key=" */
	movl	$0x0000ffff, %ebx	/* upper limit of hot-key */
	movw	%di, %si
	call	parse_number_dos
	jc	invalid_option		/* invalid hot-key value */
	decw	%si
	movw	%si, %cx
	subw	%di, %cx
	movw	%si, %di
	lodsb
	cmpb	$0x20, %al
	je	2f
	cmpb	$0, %al
	jne	invalid_option		/* invalid hot-key value */
	//orb	$4, ABS_PSP(options_done)
2:
	cmpl	$0xffff3920, ABS_PSP(hot_key)
	jne	invalid_option		/* specify hot-key twice */
	movl	%ebx, ABS_PSP(hot_key)
	/* wipe off "--hot-key=K" */
	addw	$(option_hot_key_dos_end - option_hot_key_dos), %cx
	subw	%cx, %di
	movb	$0x22, %al	/* double-quote */
	stosb
	decw	%cx
	movb	$0x20, %al	/* SPACE */
	repz stosb
3:
	popw	%ax		/* discard old DI */
	pushw	%di		/* push new DI */
	//testb	$4, ABS_PSP(options_done)
	//jz	4b
	jmp	4b

	//popw	%di
5:

	testb	$8, ABS_PSP(options_done)
	jne	5f

	movl	$8, ABS_PSP(options_doing)
	/* compare with "--duce" */
	cld			/* compare upward */
	movw	$ABS_PSP(option_duce_dos), %si
	movw	%di, %dx	/* DI is our option string, save to DX */
	movw	$(option_duce_dos_end - option_duce_dos), %cx
				/* length of the string */
	repz cmpsb
	jz	2f		/* yes, exactly */

	movw	$ABS_PSP(option_duce1_dos), %si
	movw	%dx, %di	/* restore DI from DX */
	movw	$(option_duce1_dos_end - option_duce1_dos), %cx
				/* length of the string */
	repz cmpsb
	jnz	3f
2:
	/* found "--duce" */
	cmpb	$0x20, (%di)
	je	2f
	cmpb	$0, (%di)
	jne	3f
	//orb	$1, ABS_PSP(options_done)
2:
	cmpl	$0, ABS_PSP(duce)
	jne	invalid_option	/* specify --duce twice */
	movl	$1, ABS_PSP(duce)
	/* wipe off "--duce" */
	movw	$(option_duce_dos_end - option_duce_dos), %cx
	subw	%cx, %di
	movb	$0x22, %al	/* double-quote */
	stosb
	decw	%cx
	movb	$0x20, %al	/* SPACE */
	repz stosb
3:
	popw	%ax		/* discard old DI */
	pushw	%di		/* push new DI */
	//testb	$1, ABS_PSP(options_done)
	//jz	4b
	jmp	4b

	//popw	%di
	//pushw	%di
5:

	testb	$0x10, ABS_PSP(options_done)
	jne	5f

	movl	$0x10, ABS_PSP(options_doing)
	/* compare with "--chs-no-tune" */
	cld			/* compare upward */
	movw	$ABS_PSP(option_chs_no_tune_dos), %si
	movw	%di, %dx	/* DI is our option string, save to DX */
	movw	$(option_chs_no_tune_dos_end - option_chs_no_tune_dos), %cx
				/* length of the string */
	repz cmpsb
	jz	2f		/* yes, exactly */

	movw	$ABS_PSP(option_chs_no_tune1_dos), %si
	movw	%dx, %di	/* restore DI from DX */
	movw	$(option_chs_no_tune1_dos_end - option_chs_no_tune1_dos), %cx
				/* length of the string */
	repz cmpsb
	jnz	3f
2:
	/* found "--chs-no-tune" */
	cmpb	$0x20, (%di)
	je	2f
	cmpb	$0, (%di)
	jne	3f
	//orb	$1, ABS_PSP(options_done)
2:
	cmpl	$0, ABS_PSP(chs_no_tune)
	jne	invalid_option	/* specify --chs-no-tune twice */
	movl	$1, ABS_PSP(chs_no_tune)
	/* wipe off "--chs-no-tune" */
	movw	$(option_chs_no_tune_dos_end - option_chs_no_tune_dos), %cx
	subw	%cx, %di
	movb	$0x22, %al	/* double-quote */
	stosb
	decw	%cx
	movb	$0x20, %al	/* SPACE */
	repz stosb
3:
	popw	%ax		/* discard old DI */
	pushw	%di		/* push new DI */
	//testb	$1, ABS_PSP(options_done)
	//jz	4b
	jmp	4b

	//popw	%di
	//pushw	%di
5:

//	testb	$2, ABS_PSP(options_done)
//	jne	5f
//
//	jmp	4b
//
//1:
	popw	%di
	popw	%si
	popw	%di
	popw	%si

//---------------------------------------------------------------------------
	/* if specified --bypass, then time-out default to 5 */

	movl	ABS_PSP(bypass), %ecx	/* --bypass specified? */
	jecxz	1f			/* no, continue */
	cmpl	$0x80000000, ABS_PSP(time_out)
	jne	1f
	movl	$5, ABS_PSP(time_out)
1:
//---------------------------------------------------------------------------
	/* if time-out is not 0, print message */
	movw	ABS_PSP(time_out), %cx
	jcxz	1f

	movw	$ABS_PSP(press_space_bar_string), %dx
	cmpw	$0x3920, ABS_PSP(hot_key)
	je	2f
	movw	$ABS_PSP(press_hot_key_string), %dx
2:
	movb	$0x09, %ah	/* display a dollar terminated string */
	int	$0x21		/* call DOS */
	movw	$ABS_PSP(press_any_key_string), %dx
	movb	$0x09, %ah	/* display a dollar terminated string */
	int	$0x21		/* call DOS */
1:	
//---------------------------------------------------------------------------
	/* find option "--config-file=" */

	cld
	movw	%di, %si	/* SI points to the leading "--" */
				/* but may be changed to double-quote */
1:
	lodsb
	cmpb	$0x22, %al	/* the double quote char */
	//je	1b
	jne	2f
	movb	$0x20, -1(%si)
	jmp	1b
2:
	cmpb	$0x20, %al	/* SPACE */
	je	1b
	cmpb	$0, %al
	je	use_default_config_file
	decw	%si
	cmpw	$0x2d2d, (%si)	/* "--" */
	jne	invalid_option

	movw	%si, %di	/* DI points to the leading "--" */

	/* compare with "--config-file=" */

	cld			/* compare upward */
	movw	$ABS_PSP(option_config_file_dos), %si
	movw	%si, %bx	/* SI is const string "--config-file=" */
	movw	%di, %dx	/* DI is our option string, save to DX */
	movw	$(option_config_file_dos_end - option_config_file_dos), %cx
				/* length of the string */
	repz cmpsb
	jz	1f		/* yes, exactly */

	/* translate all upper case to lower case, and try again */

	movw	$0x1000, %cx
	movw	%dx, %si	/* about to translate our option string */
	movw	%dx, %di
2:
	lodsb
	cmpb	$0x00, %al
	je	2f
	cmpb	$0x41, %al	/* below 'A'? */
	jb	3f		/* yes, no change. */
	cmpb	$0x5a, %al	/* above 'Z'? */
	ja	3f		/* yes, no change. */
	orb	$0x20, %al	/* change to lower */
3:
	stosb
	loop	2b
2:

	/* compare again */

	cld			/* compare upward */
	movw	$(option_config_file_dos_end - option_config_file_dos), %cx
	movw	%bx, %si	/* SI is const string "--config-file=" */
	movw	%dx, %di	/* DI is our option string, restore from DX */
	repz cmpsb		/* compare for the second time */
	jnz	invalid_option
1:

	/* the option "--config-file=" exists for sure */

	cld			/* scan upward */
	movw	%di, %si	/* points to the config file name */
	movw	$0x1000, %cx
	movb	$0x00, %al	/* find the end of command line */
	repnz scasb
	jnz	invalid_option	/* no ending NULL */

	movw	%di, %cx	/* points to end of config file name */
	subw	%si, %cx
	decw	%cx		/* length of config file name */
	jz	invalid_option	/* FILENAME is empty */

	/* SI points to filename string with length CX */ 

	/* the leading "(" or "/" indicates a normal config filename */
	movb	(%si), %al
	cmpb	$0x28, %al	/* "(" */
	jz	2f
	cmpb	$0x2F, %al	/* "/" */
	jnz	1f
2:
	/* we change the ending space-slash to NULL only for normal config
	 * filename.
	 */

	pushw	%cx		/* save CX(=length) important! */

	/* find the space-slash pair and change the space to NULL */
	cld			/* scan upward */
	xorw	%dx, %dx	/* 0 for outside the double-quotes */
	movw	%si, %di	/* scan the filename */
	//movw	$0x1000, %cx	/* max length of command line */
	movb	$0x20, %al	/* the space bar character */
2:
	repnz scasb		/* find the space char */
	jnz	2f		/* not found, continue */
	cmpb	$0x2f, (%di)	/* is it the " /" pair */
	jnz	2b		/* no, search the rest of the command line */
	decw	%di
	movb	$0x00, %al	/* mark the end of command line */
	stosb			/* change the space to NULL */
2:
	popw	%cx		/* restore CX, which is non-zero. */
	jmp	put_config_file_name
1:
	/* The filename specifies an embedded command-line menu. */

	movw	%cx, %bx
	incw	%cx

	cld
	//movw	$0x1000, %cx
	movw	$0x81, %di
	xorw	%ax, %ax

	/* change semi-colon to LF. change double-quote to 0 if it is followed
	 * by SPACE or NULL, otherwise delete the double-quote char and
	 * continue.
	 */

3:
	lodsb
4:
	cmpb	$0x3B, %al	/* semi-colon */
	jnz	2f
	movb	$0x0A, %al	/* change to LF */
2:
	cmpb	$0x22, %al	/* the double quote */
	jnz	2f
	jcxz	4f
	lodsb
	decw	%cx
	cmpw	%bx, %cx	/* is the double quote leading? */
	jae	4b		/* yes, discard the double quote */
	cmpb	$0x20, %al	/* is the next char a space? */
	jz	4f		/* yes, end */
	cmpb	$0x00, %al	/* is the next char a NULL */
	jnz	4b		/* no, discard the double quote */
4:
	movb	$0x00, %al	/* change to NULL */
2:
	stosb
	cmpb	$0x00, %al
	jz	1f
	jcxz	4b
	loop	3b
1:

	/* DI points to the char after the ending NULL */

	movw	$0x81, %si	/* SI points to filename */
	movw	%di, %cx	/* points to end of filename */
	subw	%si, %cx
	decw	%cx		/* CX=length of the filename */
	jz	invalid_option	/* FILENAME is empty */

	/* the leading "(" or "/" indicates a normal config filename */
	movb	(%si), %al
	cmpb	$0x28, %al	/* "(" */
	jz	put_config_file_name
	cmpb	$0x2F, %al	/* "/" */
	jz	put_config_file_name

	/* invalidate the config file in pre_stage2 */

raw_commands_embedded:

	/* CX=0 means raw commands are embedded. */
	xorw	%cx, %cx	/* copy 0 bytes to config-file field */
	//jmp	6f

put_config_file_name:
	cld

	movl	%esi, %edx	/* save ESI to EDX */

	movl	ABS_PSP(duce), %eax	/* --duce specified? */

	movw	$ABS_PSP(pre_stage2_start+0x12), %di /* version string */

	shlb	$2, %al				/* bit2=DUCE */
	movb	ABS_PSP(chs_no_tune), %ah
	shlb	$3, %ah				/* bit3=chs-no-tune */
	orb	%ah, %al
	orb	$0x01, %al			/* bit0=disable pxe */
	orb	%al, -13(%di)

	xorl	%eax, %eax	/* 0 means the end of the string */

	/* pre_stage2_start+0xA holds the boot partition number. We use
	 * default partition number 0(and default drive number 0x80 in DL)
	 */
	movb	%al, -8(%di)	/* the boot partition number */

	/* pre_stage2_start+0xB holds our temp boot_drive */
	movb	$0x80, -7(%di)	/* temp storage for boot_drive */

	jcxz	6f		/* CX=0 means raw commands are embedded. */

	/* pre_stage2_start+0xC holds the address of preset_menu.
	 * we are using the config-file, and we do not change the default
	 * preset_menu, so let it be 0.  */
	movl	%eax, -6(%di) 

	/* ESI points to the first byte of the filename. if it is not `(',
	 * then don't touch the boot device.
	 */

	cmpb	$0x28, (%si)	/* 0x28 is "(" */
	jne	6f

	xorw	%ax, %ax	/* clear AH */

	lodsb			/* AL="(" */
	lodsb

	/* the drive number in hex or decimal form */

	cmpb	$0x30, %al	/* 0x30 is "0" */
	jb	invalid_option	/* invalid config file */
	cmpb	$0x39, %al	/* 0x39 is "9" */
	jbe	2f		/* BIOS drive number */

	/* the drive number in (fd?) or (hd?) form */

	cmpb	$0x66, %al	/* 0x66 is "f" */
	je	3f
	movb	$0x80, %ah	/* for hard drive */
	cmpb	$0x68, %al	/* 0x68 is "h" */
	je	3f
	lodsb
	cmpb	$0x64, %al	/* 0x64 is "d" */
	je	6f		/* might be cd/nd/md/rd, do nothing */
	jmp	invalid_option	/* invalid config file */
3:
	/* hard drive or floppy */
	lodsb
	cmpb	$0x64, %al	/* 0x64 is "d" */
	jne	invalid_option	/* invalid config file */
	
	lodsb
	cmpb	$0x30, %al	/* 0x30 is "0" */
	jb	invalid_option	/* invalid config file */
	cmpb	$0x39, %al	/* 0x39 is "9" */
	ja	invalid_option	/* invalid config file */
	
2:
	decw	%si		/* SI points to hexa or decimal number */
	movl	$0x7f, %ebx		/* Max drive number */
	call	parse_number_dos	/* parse drive number */
	jc	invalid_option		/* invalid config file */
	cld
	decw	%si		/* SI points to delimiter "," or ")" */
	lodsb
	cmpb	$0x2C, %al	/* "," */
	je	2f
	cmpb	$0x29, %al	/* ")" */
	jne	invalid_option	/* invalid config file */
2:
	xchgl	%eax, %ebx	/* save drive number to EAX */
				/* BH=0 for floppy, and 0x80 for hard drive */
	orb	%bh, %al	/* adjust hard drive number */
	movb	$0xff, %bl	/* partition number for floppy */
	testb	%bh, %bh	/* floppy, skip the partition number parsing */
	jz	2f
	movl	$0x7f, %ebx		/* Max partition number */
	call	parse_number_dos	/* parse partition number */
	jc	invalid_option		/* invalid config file */
2:

	/* BL=boot partition number, AL=boot_drive number */

	movb	%al, %bh	/* BH=boot_drive number */

	decw	%si		/* SI should point to ")" */
	lodsb

	cmpb	$0x29, %al	/* ")" */
	jne	invalid_option	/* invalid config file */

	movw	%bx, -8(%di)	/* setup boot_drive and boot_partition number */

//----------------------------------------------------------------------------
6:
	movl	%edx, %esi	/* restore ESI from EDX */
	xorb	%al, %al
	pushw	%cx		/* CX=0 means raw commands are embedded. */
	movw	$0x0010, %cx	/* set max length of grub version string */
	cld
	repnz scasb		/* DI changed */
	popw	%cx		/* CX=0 means raw commands are embedded. */

	movw	%cx, %ax
	addw	%di, %ax
	cmpw	$ABS_PSP(pre_stage2_start+0x6f), %ax
				/* check for possible buffer overflow */
	jnb	file_name_too_long
	pushw	%cx		/* CX=0 for embedded menu, and ... */
	cld
	repz movsb		/* now it is safe, perform the move */
	popw	%cx		/* ... CX=non-zero for normal file */
	xorb	%al, %al	/* write an end-of-string mark ... */
	movb	%al, (%di)	/* ... to the new config file name */

	testw	%cx, %cx	/* CX=0 means raw commands are embedded. */
	jnz	1f		/* normal grub-file, continue */

	/* CX=0, and SI points to beginning of the string. */

	/* If "#@" is leading, it leads a DOS filename for menu.
	 * Based on John Cobb (Queen Mary, University of London):
	 *	http://sysdocs.stu.qmul.ac.uk/sysdocs/Comment/Code_Snippets/Grub_For_DOS_Extra/paramfile.s
	 */

	cmpw	$0x4023, (%si)	/* "#@" */
	jne	2f		/* normal embedded menu, continue */

	lodsw			/* addw	$2, %si; see cld above */

dos_filename:

	/* SI points to filename */
	call	open_dos_file
	jc	invalid_option		/* failure */
	jmp	1f		/* done, continue. */

2:
	/* check if it is DOS-style */
	cld
	movw	%si, %di
	movw	$0x1000, %cx
	movb	$0x20, %al
	repz scasb
	//jcxz	1f		/* don't check a long menu for dos filename */
	testw	%cx, %cx
	jz	1f		/* don't check a long menu for dos filename */
	decw	%di		/* DI points to the first non-space char */
	movw	%di, %si
	movw	$70, %cx
	xorb	%al, %al
	repnz scasb
	//jcxz	1f		/* don't check a long menu for dos filename */
	testw	%cx, %cx
	jz	1f		/* don't check a long menu for dos filename */
	movw	%di, %bx
	subw	%si, %bx
	decw	%bx		/* length */
	movw	(%si), %ax
	cmpb	$0x3A, %ah	/* : */
	jne	2f
	cmpb	$0x41, %al	/* A */
	jb	2f
	cmpb	$0x7A, %al	/* z */
	ja	2f
	cmpb	$0x5A, %al	/* Z */
	jbe	dos_filename	//invalid_option
	cmpb	$0x61, %al	/* a */
	jae	dos_filename	//invalid_option
2:
	cmpb	$0x5C, %al	/* \ */
	je	dos_filename	//invalid_option
	//cmpb	$0x2F, %al	/* / */
	//je	invalid_option

	/* if there is a LF, this is not of a DOS filename. */

	movw	%si, %di
	//incw	%di
	movw	%bx, %cx
	//decw	%cx
	movb	$0x0A, %al
	repnz scasb
	jz	1f

	/* if there is a back slash, this is of a DOS filename. */

	movw	%si, %di
	//incw	%di
	movw	%bx, %cx
	//decw	%cx
	movb	$0x5C, %al
	repnz scasb
	jz	dos_filename	//invalid_option

	/* now no LFs, no back slahses. So this can only be a filename without
	 * leading dir part. If there is a space in the file name, then it is
	 * not treated as a DOS filename.
	 */

	movw	%si, %di
	//incw	%di
	movw	%bx, %cx
	//decw	%cx
	movb	$0x20, %al
	repnz scasb
	jz	1f

	//movw	%si, %di
	//incw	%di
	//movw	%bx, %cx
	//decw	%cx
	//movb	$0x2F, %al
	//repnz scasb
	//jz	invalid_option

	/* now no spaces. If there is a dot in the file name, then it is
	 * treated as a DOS filename.
	 */

	movw	%si, %di
	movw	%bx, %cx
	movb	$0x2E, %al	/* . */
	repnz scasb
	jz	dos_filename	//invalid_option

	movw	%si, %di
	movw	%bx, %cx
	movb	$0x2D, %al	/* - */
	repnz scasb
	jz	dos_filename	//invalid_option

	//movw	%si, %di
	//movw	%bx, %cx
	//movb	$0x5F, %al	/* _ */
	//repnz scasb
	//jz	invalid_option

	movw	%si, %di
	movw	%bx, %cx
	movb	$0x7E, %al	/* ~ */
	repnz scasb
	jz	dos_filename	//invalid_option

	movw	%si, %di
	movw	%bx, %cx
	movb	$0x21, %al	/* ! */
	repnz scasb
	jz	dos_filename	//invalid_option

	movw	%si, %di
	movw	%bx, %cx
	movb	$0x2A, %al	/* * */
	repnz scasb
	jz	dos_filename	//invalid_option

	movw	%si, %di
	movw	%bx, %cx
	movb	$0x3F, %al	/* ? */
	repnz scasb
	jz	dos_filename	//invalid_option

1:
done_options:

	smsw	%ax		/* the old 286 code, save MSW to AX */
	testb	$0x01, %al	/* is it in protected mode? */
	jnz	protected_mode	/* continue to check vm86 mode */
	jmp	backup_low_memory_and_HMA	/* in real mode, continue */

invalid_option:
	movw	$ABS_PSP(usage_string), %dx
	movb	$0x09, %ah	/* display a dollar terminated string */
	int	$0x21		/* call DOS */
	
	/* hexdump the PSP commandline area */
	movb	$0x0e, %ah	/* display char */
	movw	$7, %bx		/* white */
	movb	$8, %dh		/* 8 sections (1 section = 16 bytes) */
	movw	$0x0080, %si	/* offset in PSP */
4:
	movw	$0x10, %cx	/* display 16 bytes per line */
	/* display leading string like "0080:   " */
	movb	$0x30, %al	/* display "0" */
	int	$0x10
	int	$0x10		/* twice */
	movw	%si, %ax	/* AH modified */
	shrb	$4, %al		/* higher 4 bits of SI */
	cmpb	$9, %al
	jbe	2f
	addb	$7, %al
2:
	addb	$0x30, %al	/* 0x30 is '0' */
	movb	$0x0e, %ah	/* display char */
	int	$0x10
	movb	$0x30, %al	/* display "0" */
	int	$0x10
	movb	$0x3a, %al	/* display ":" */
	int	$0x10
	movb	$0x20, %al	/* display 3 space chars */
	int	$0x10
	int	$0x10
	int	$0x10
	
	/* display hex values */
1:
	lodsb
	movb	%al, %dl	/* save lower 4 bits of AL to DL */
	shrb	$4, %al		/* higher 4 bits */
	cmpb	$9, %al
	jbe	2f
	addb	$7, %al
2:
	addb	$0x30, %al	/* 0x30 is '0' */
	movb	$0x0e, %ah	/* display char */
	//movw	$7, %bx		/* white */
	int	$0x10
	movb	%dl, %al	/* restore AL from DL */
	andb	$0x0f, %al
	cmpb	$9, %al
	jbe	2f
	addb	$7, %al
2:
	addb	$0x30, %al	/* 0x30 is '0' */
	//movb	$0x0e, %ah	/* display char */
	//movw	$7, %bx		/* white */
	int	$0x10
	movb	$0x20, %al	/* display a space char */
	int	$0x10
	loop	1b
	
	int	$0x10		/* display 2 space chars */
	int	$0x10
	
	/* display ascii values */
	
	movw	$0x10, %cx
	subw	%cx, %si
1:
	lodsb
	//cmpb	$0x80, %al	/* is it big char? */
	//jb	2f		/* no, continue */
	cmpb	$7, %al		/* is it BELL char? */
	je	2f		/* no, continue */
	cmpb	$8, %al		/* is it BACKSPACE char? */
	je	2f		/* no, continue */
	cmpb	$0x0a, %al	/* is it LF char? */
	je	2f		/* no, continue */
	cmpb	$0x0d, %al	/* is it CR char? */
	jne	3f		/* no, continue */
2:
	movb	$0x2e, %al	/* display a dot */
3:
	int	$0x10
	loop	1b
	
	movb	$0x0d, %al	/* display CR char */
	int	$0x10
	movb	$0x0a, %al	/* display LF char */
	int	$0x10
	
	decb	%dh
	jnz	4b
	
	jmp	exit_no_message

open_dos_file:

	/* SI points to filename */

	/* skip any possible leading blanks in the filename. */
	movw	%si, %di
	movw	$0x1000, %cx
	movb	$0x20, %al	/* space */
	cld
	repz scasb
	jz	4f		//invalid_option	/* filename cannot be only spaces */
	decw	%di		/* DI points to the first non-space char */

	//AH = 3Dh	//OPEN EXISTING FILE
	//AL = access and sharing modes
	//DS:DX -> ASCIZ filename
	//CL = attribute mask of files to look for (server call only)

	//Return:
	//CF clear if successful
	//AX = file handle
	//CF set on error
	//AX = error code (01h,02h,03h,04h,05h,0Ch,56h)

	movzwl	%di, %edx
	movw	$0x3d00, %ax	/* open file for reading */
	int	$0x21		/* call DOS */
        jnc     3f

	/* open failure */

	pushl	%edx
	movl	$ABS_PSP(failed_open_file_string), %edx
	movb	$0x09, %ah
	int	$0x21
	popl	%edx

	/* locate the end of filename */
	movw	%dx, %di
	movw	$0x1000, %cx
	movb	$0, %al		/* NULL */
	cld
	repnz scasb
	decw	%di		/* DI points to the ending NULL */
	pushw	%di
	movb	$0x24, %al	/* '$' */
	stosb			/* change the NULL to '$' */

	movb	$0x09, %ah	/* display a dollar terminated string */
	int	$0x21		/* call DOS */
	popw	%di
	movb	$0, %al
	stosb			/* change `$' back to NULL */
	jmp	4f		//invalid_option	/* jump if failed to open */
failed_open_file_string:
	.ascii "\r\nUnable to open DOS file: $"
3:

	//READ FROM FILE OR DEVICE

	//AH = 3Fh
	//BX = file handle
	//CX = number of bytes to read
	//DS:DX -> buffer for data

	//Return:
	//CF clear if successful
	//AX = number of bytes actually read (0 if at EOF before call)
       	//CF set on error
	//AX = error code (05h,06h) 

	movw	%ax, %bx
	pushw	%bx
	movb	$0x3f, %ah
	movw	$0x1000, %cx
	movl	$0x81, %edx
	int	$0x21
	popw	%bx
        jnc     3f

	/* read failure */

	movl	$ABS_PSP(failed_read_file_string), %edx
	movb	$0x09, %ah	/* display a dollar terminated string */
	int	$0x21		/* call DOS */
	jmp	4f		//invalid_option	/* jump if failed to read */
failed_read_file_string:
	.ascii "\r\nUnable to read DOS file.$"
3:
	//CLOSE FILE

	//AH = 3Eh
	//BX = file handle
	//
	//Return:
	//CF clear if successful
	//	AX destroyed
	//CF set on error
	//	AX = error code (06h)

	pushw	%ax		//number of bytes actually read (0 if at EOF before call)

	movb	$0x3e, %ah	// close file (BX = file handle)
	int	$0x21

	popw	%bx		//number of bytes actually read (0 if at EOF before call)

	movb	$0, 0x81(%bx)	/* end in NULL */
	clc
	ret
4:
	stc
	ret

message_exit:
	movb	$0x09, %ah	/* display a dollar terminated string */
	int	$0x21		/* call DOS */
exit_no_message:
	movw	$0x4C01, %ax	/* exit EXE with error number 01 */
terminate_program:
	cmpb	$0, %cs:0x80	/* Are we running as EXE or device driver? */
	jne	1f		/* It is EXE. So we call DOS to exit. */

	/* We are running as a device driver. */

	/* Calculate the CS */
	movw	%cs, %bx			/* points to START. */
	subw	$((start -nxtdev) >> 4), %bx
	pushw	%bx			/* points to device driver start */
	movw	$(device_driver_exit - nxtdev), %bx
	pushw	%bx
	lret

1:
	int	$0x21		/* call DOS */

program_hangs: /* should not get here, just in case int21/AH=4Ch would fail */
	jmp	program_hangs

//----------------------------------------------------------------------------
file_name_too_long:

	.code16

	movw	$ABS_PSP(fatal_string), %dx
	jmp	message_exit
	
//----------------------------------------------------------------------------
parse_number_dos:

	.code16

	/* input:	ESI	points to the number
	 *		EBX	upper limit of the number
	 * output:	EBX	the value of the number
	 *		ESI	points to the next byte after the delimiter
	 *		EBP	changed
	 *		CF=1	failure
	 *		CF=0	success
	 */

	pushl	%edx
	pushl	%eax
	pushl	%ebx		/* upper limit */
	cld
	movl	$16, %ebp	/* initialize EBP for hex */
	//movl	%edi, %esi
	movl	$0xffffffff, %edx
	xorl	%ebx, %ebx
	lodsw
	cmpw	$0x5830, %ax	/* 0X */
	je	2f
	cmpw	$0x7830, %ax	/* 0x */
	je	2f

	/* decimal */
	decl	%esi
	decl	%esi
	movl	$10, %ebp
2:
	xorl	%eax, %eax
	lodsb
	cmpb	$0, %al
	je	4f		/* CF=0 */
	cmpb	$0x2C, %al	/* 0x2C= `,' ends the drive number. */
	je	4f		/* CF=0 */
	cmpb	$0x29, %al	/* 0x29= `)' ends partition number. */
	je	4f		/* CF=0 */
	cmpb	$0x20, %al	/* 0x20= ` ' */
	je	4f		/* CF=0 */
	cmpb	$0x30, %al
	jb	3f
	cmpb	$0x39, %al
	jbe	1f
	cmpl	$16, %ebp	/* Is hex? */
	jb	3f		/* no, failure */
	orb	$0x20, %al
	cmpb	$0x61, %al
	jb	3f
	cmpb	$0x66, %al
	ja	3f
	subb	$0x27, %al
1:
	subb	$0x30, %al
	pushl	%eax
	movl	%ebx, %eax
	mull	%ebp
	movl	%eax, %ebx
	popl	%eax
	jc	3f
	addl	%eax, %ebx
	jc	3f
	popl	%eax
	pushl	%eax		/* upper limit */
	cmpl	%eax, %ebx
	ja	3f
	jmp	2b

4:
	testl	%edx, %edx	/* CF=0 */
	jz	1f		/* return success */
3:
	/* return failure */
	stc
1:
	popl	%eax		/* upper limit */
	popl	%eax
	popl	%edx
	ret

protected_mode:
	pushfw
	popw	%ax
	testb	$0x30, %ah	/* IOPL */
	jz	1f

	/* IOPL is not 0 */
	andb	$0xcf, %ah	/* let IOPL = 0 */
	pushw	%ax
	popfw
	pushfw
	popw	%ax
	testb	$0x30, %ah	/* is IOPL still 0? */
	jz	2f		/* CPL is 0 */
	jmp	3f
1:
	/* IOPL is 0 */
	orb	$0x30, %ah	/* let IOPL != 0 */
	pushw	%ax
	popfw
	pushfw
	popw	%ax
	testb	$0x30, %ah	/* is IOPL still 0? */
	jnz	2f		/* CPL is 0 */
	jmp	3f
2:
	/* ring 0 of 16-bit protected mode will get here */
	andb	$0xcf, %ah	/* let IOPL = 0 */
	pushw	%ax
	popfw
	jmp	backup_low_memory_and_HMA	/* CPL = 0, Continue */
3:
	/* vm86 mode(emm386/Windows DOS Box/LINUX DOSEMU) will get here */
	/* CPL != 0 */

#ifndef	BAD_BIOS
	/* before probing int, we initialize umb_array while in VM86 mode. */

	movw	%cs, %ax
	movw	%ax, %es
	cld
	movw	$ABS_START(umb_array), %di
	movw	$8, %cx

	/* find the first umb in the range from C000:0000 to F000:0000 */

	/* the first umb should begin at a 4K boundary */

	movw	$0xBF00, %ax	/* will begin at 0xBF00 + 0x100 = 0xC000 */
	movw	%ax, %ds

1:
	movw	%ds, %ax
	addw	$0x100, %ax
	cmpw	$0xF000, %ax
	jnb	1f
	movw	%ax, %ds

	cmpb	$0x4D, 0	/* 0x4D='M' */
	jne	1b
	cmpl	$0x20424D55, 8	/* 'UMB ' - 'UMB' and a space */
	jne	1b
	cmpl	$0x20202020, 12	/* '    ' - 4 spaces */
	jne	1b

	/* found. DS:0000 points to the first umb. */
4:
	movw	%ds, %ax
	stosw			/* start segment */
	xchgw	%ax, %bx	/* save AX to BX */
	movw	3, %ax
	incw	%ax
	stosw			/* length in paragraphs */
	addw	%ax, %bx	/* the next umb */

	jcxz	1f
	decw	%cx
	jz	1f

	movw	%bx, %ds
	
2:
	jcxz	1f
	cmpb	$0x4D, 0	/* 0x4D='M' */
	je	5f
	cmpb	$0x5A, 0	/* 0x5A='Z' */
	jne	1f
	xorw	%cx, %cx	/* CX=0 indicates 'no more block'. */
5:
	cmpl	$0x20202020, 12	/* '    ' - 4 spaces */
	jne	1f

	cmpl	$0x20424D55, 8	/* 'UMB ' - 'UMB' and a space */
	je	3f

	/* 'SM' or others */

	movw	%ds, %ax
	addw	3, %ax
	incw	%ax
	movw	%ax, %ds
	jmp	2b
3:
	/* UMB */

	movw	%ds, %ax
	cmpw	%ax, %bx
	jne	4b		/* add a new item */

	/* use the old item and increase its length */
	movw	3, %ax
	incw	%ax
	addw	%ax, %es:-2(%di)
	addw	%ax, %bx
	movw	%bx, %ds
	jmp	2b

1:
#endif

	/* Note for people who are tracing/debugging this program:
	 *
	 * PROBE_INT will take over int01, so probably you don't want
	 * to trace into PROBE_INT.
	 */

	call	probe_int

	jc	failed_probe_int

	movw	%cs, %ax
	movw	%ax, %ds
	movw	%ax, %es

	/* Note for people who are tracing/debugging this program:
	 *
	 * The following code will switch from VM86 mode to protected mode,
	 * and then to real mode. Your debugger will hang in a mode switch.
	 * So stop tracing now.
	 */

/* Use VCPI to switch to protected mode, and then switch to real mode
 * and run grub. After returning from grub, switch to protected mode, and
 * finally use VCPI again to switch back to vm86 mode.
 */

/* stolen from http://my.execpc.com/~geezer/os/slfb.asm */
#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
#; Simulated Linear Frame Buffer
#; Christopher Giese <geezer@execpc.com>
#; http://www.execpc.com/~geezer/os/
#;
#; Updated March 6, 2001: can now return to V86 mode when done
#;
#; Some stuff (actually, pmode VESA BIOS bank switching) fixed by
#; Alexei A. Frounze <alexfru@chat.ru>
#; http://alexfru.chat.ru
#;
#; You can do anything with this code but blame us for it.
#;
#; To run this code, you need a PC with a 32-bit processor (386SX or better)
#; and DOS. This code has been tested with the following SVGA video boards:
#;
#;                                               bank-switch function
#;       buss            chipset                 used by this code
#;       ----            -------                 --------------------
#;       16-bit ISA      Cirrus 5422             Cirrus
#;       32-bit PCI      S3 86c765 (Trio 64V+)   S3
#;       32-bit PCI (?)  STB Nitro (?)           S3
#;
#; To assemble this code, you need NASM (http://www.web-sites.co.uk/nasm/)
#;       nasm -f bin -o slfb.com slfb.asm
#;
#; bugs/to do:
#; - test with other systems
#;
#; Here is an interesting link:
#;       http://marc.theaimsgroup.com/?m=88102879813311&w=2
#; Also, look at the "vflat" files in the source code to the
#; SciTech MGL graphics library
#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

	movl	$1, ABS_PSP(emm386_running)

#; save CS value for return to real mode
	movw	%cs, ABS_PSP(real_mode_cs)

#; our pmode code will use the stack DOS gave us, but we have
#; to zero the top 16 bits of the stack pointer (ESP)
	movzwl	%sp, %esp

#; get the virtual-to-physical conversion value. Though we turn on paging,
#; this code runs in memory that is identity-mapped (i.e. no page-based
#; address translation). We do, however, use segment-based address
#; translation, to give things the same addresses in both real and pmode.
	xorl	%ebx, %ebx
	movw	%cs, %bx
	shll	$4, %ebx

#; set base addresses of the 16- and 32-bit code segment descriptors
	movl	%ebx, %eax
	movw	%ax, ABS_PSP(gdt2 + 2)	#; 32-bit code segment
	movw	%ax, ABS_PSP(gdt4 + 2)	#; 16-bit code segment
	shrl	$16, %eax
	movb	%al, ABS_PSP(gdt2 + 4)	#; 32-bit code segment
	movb	%al, ABS_PSP(gdt4 + 4)	#; 16-bit code segment
	movb	%ah, ABS_PSP(gdt2 + 7)	#; 32-bit code segment; AH=0
	#; movb	%ah, ABS_PSP(gdt4 + 7)	#; 16-bit code segment

#; now do the same with the data/stack segment descriptors
	movl	%ebx, %eax
	movw	%ax, ABS_PSP(gdt3 + 2)	#; 32-bit data segment
	movw	%ax, ABS_PSP(gdt5 + 2)	#; 16-bit data segment
	shrl	$16, %eax
	movb	%al, ABS_PSP(gdt3 + 4)	#; 32-bit data segment
	movb	%al, ABS_PSP(gdt5 + 4)	#; 16-bit data segment
	movb	%ah, ABS_PSP(gdt3 + 7)	#; 32-bit data segment; AH=0
	#; movb	%ah, ABS_PSP(gdt5 + 7)	#; 16-bit data segment

#; point the TSS descriptor to the LINEAR/PHYSICAL address of 'tss'
	movl	$ABS_PSP(tss), %eax
	addl	%ebx, %eax
	movw	%ax, ABS_PSP(gdt6 + 2)	#; 32-bit TSS selector
	shrl	$16, %eax
	movb	%al, ABS_PSP(gdt6 + 4)	#; 32-bit TSS selector
	movb	%ah, ABS_PSP(gdt6 + 7)	#; 32-bit TSS selector

# we don't use protected mode idt during the mode switch

#; point 'gdt_ptr' to LINEAR/PHYSICAL address of the GDT;
#; 'idt_ptr' to LINEAR/PHYSICAL addr of the IDT
	addl	%ebx, ABS_PSP(gdt_ptr + 2)
	addl	%ebx, ABS_PSP(idt_ptr + 2)

#; DOS doesn't load .COM or .EXE files on a page (4K) boundary, so
#; we must now find a page boundary for the page directory/tables.
	movw	%es, %ax
	addw	$(HMA_backup), %ax
	movw	%ax, %es

#; page_info immediately follows 64K space at HMA_backup

	xorl	%esi, %esi
#if 1
	movw	%es, %si
	addw	$(HMA_backup+0x1000), %si	#; SI=segment of page_info
	shll	$4, %esi	#; ESI = LINEAR/PHYSICAL addr of page_info
#else	
	movw	$ABS_PSP(page_info), %si	#; SI = offset of page_info
	addl	%ebx, %esi	#; ESI = LINEAR/PHYSICAL addr of page_info
#endif
	addl	$4095, %esi	#; round to 4K boundary

	andl	$0xFFFFF000, %esi #; ESI = LINEAR/PHYSICAL addr of page dir
	movl	%esi, %edi
#if 0
	subl	%ebx, %edi	#; DI = offset of page dir; EDI <= 0xffff
#else
	shrl	$4, %edi	#; DI=segment of page dir
	movw	%di, %es	#; ES:0000 points to page dir
	xorw	%di, %di
#endif

#; save page dir address for later use by VCPI
	movl	%esi, ABS_PSP(vcpi_cr3)

#; EAX = LINEAR/PHYSICAL address of "kernel" page table
#; (4K above the page directory)
	movl	%esi, %eax
	addl	$4096, %eax
#; create entry in page dir for "kernel" page table
	orb	$7, %al		#; Ring 3, writable, present
#if 0
	movl	%eax, (%di)
#else
	movl	%eax, %es:(%di)	#; EDI=0
#endif

#; advance DI from page directory to "kernel" page table
	addl	$4096, %edi	#; EDI=4096

#; using the "kernel" page table, identity-map
#; (virtual == physical) the bottom 4M of RAM
#; With VCPI, we can skip this step, and simply take over EMM386's
#; conventional memory page table using INT 67h AX=DE01h
	cld
	movw	$1024, %cx
	movl	$7, %eax	#; Ring 3, writable, present
1:
	stosl
	addl	$4096, %eax	#; next page
	loop	1b

#; move DI back to "kernel" page table, in case we want to change it
	subl	$4096, %edi	#; EDI=4096

# Windows is running?
	pushl	%ebx
	pushw	%es
	pushl	%edi
	movw	$0x1600, %ax
	int	$0x2F
	popl	%edi
	popw	%es
	popl	%ebx

	//cmpb	$0, %al
	//je	check_vcpi		# not Windows DOS Box
	//cmpb	$0x80, %al
	//je	check_vcpi		# not Windows DOS Box
	shlb	$1, %al
	jz	check_vcpi		# not Windows DOS Box
	
	movl	$1, ABS_PSP(windows_running)

check_dpmi:

	/* print the warning */

	movw	$ABS_PSP(warning_win_msg), %dx
	movb	$0x09, %ah	/* display a dollar terminated string */
	int	$0x21		/* call DOS */

	movw	$ABS_PSP(press_space_bar_string), %dx
	cmpw	$0x3920, ABS_PSP(hot_key)
	je	2f
	movw	$ABS_PSP(press_hot_key_string), %dx
2:
	movb	$0x09, %ah	/* display a dollar terminated string */
	int	$0x21		/* call DOS */
	movw	$ABS_PSP(press_any_key_string), %dx
	movb	$0x09, %ah	/* display a dollar terminated string */
	int	$0x21		/* call DOS */

	movw	$5, ABS_PSP(time_out)	/* non-zero timeout hangs Windows */

	sti				/* for sleep_5_seconds to work. */

	call	sleep_5_seconds
	//xorw	%ax, %ax

	cli				/* the clock is not used any more */

	movw	$ABS_PSP(cancel_msg), %dx
	jne	message_exit		/* not the hot-key, exit to DOS */
					/* hot-key pressed, continue */

	//// movw	$0, ABS_PSP(time_out)	/* clear time_out before we continue to run under Windows. */

	cmpl	$0, ABS_PSP(bypass)	/* default is bypass GRUB? */
	jne	message_exit		/* yes, exit to DOS now. */
					/* no, continue to run grub under windows. */

					/* now bypass is 0. */

#if 0
	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jmp	message_exit		#; Cant_Enter_PMode
#endif
	#; check dpmi
#;
#; Get the entry point address and save it
#;
	movw	$0x1687, %ax		#; DOS Protected-Mode Interface - INSTALLATION CHECK
	int	$0x2F			#; Return:
					#; AX = 0000h if installed BX = flags
					#;
					#; bit 0: 32-bit programs supported
					#; CL = processor type (02h=80286, 03h=80386, 04h=80486)
					#; DH = DPMI major version
					#; DL = two-digit DPMI minor version (binary)
					#; SI = number of paragraphs of DOS extender private data
					#; ES:DI -> DPMI mode-switch entry point.
					#; AX nonzero if not installed


	testw	%ax, %ax
	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jnz	message_exit		#; Cant_Enter_PMode
	movw	%es, ABS_PSP(PMode_Entry_Seg)
	movw	%di, ABS_PSP(PMode_Entry_Off)

#;
#; Allocate memory for use by DOS extender if necessary
#; NOTE:  This code assumes that the program has already
#;        shrunk its memory block so that the DOS
#;        memory allocation call will work
#;
	testw	%si, %si
	jz	Enter_PMode_Now
	movw	%si, %bx
	movb	$0x48, %ah
	int	$0x21
	jc	message_exit		#; Cant_Enter_PMode
	movw	%ax, %es

#;
#; Enter protected mode as a 16-bit program
#;
Enter_PMode_Now:
#; After using Int 2Fh function 1687h, to obtain the protected mode
#; entry point, the DPMI client must call the entry point address as
#; described in this section.

#;To Call

#;     AX = Flags
#;     Bit 0 = 1 if program is a 32-bit application
#;     ES =  Real mode  segment of  DPMI host data area.  This
#;          must be  the size  of the data area returned in SI
#;          from the previous function.  ES will be ignored if
#;          the required data size is zero.
#;     Call the  address returned  in ES:DI  by  the  previous
#;          function

#;Returns

#;     If function was successful:
#;     Carry flag is clear.
#;     Program is now executing in protected mode.
#;     CS =  16-bit selector  with base  of real mode CS and a
#;          64K limit
#;     SS = Selector with base of real mode SS and a 64K limit
#;     DS = Selector with base of real mode DS and a 64K limit
#;     ES = Selector to program's PSP with a 100h byte limit
#;     FS and GS = 0 (if running on an 80386 or 80486)
#;     If the program is a 32-bit application the high word of
#;          ESP will be 0
#;     All other registers are preserved

#;     If function was not successful:
#;     Carry flag is set.
#;     Program is executing in real mode

	xorw	%ax, %ax
	//movw	%ax, %ds		#; DS=0
	lcall	%cs:*ABS_PSP(PMode_Entry_Off)
	jc	message_exit		#; Cant_Enter_PMode

#;
#; The program is running in protected mode now!

ring_check:

#; 5. clear the PE bit
	movl	%cr0, %eax
	andb	$0xFE, %al
	movl	%eax, %cr0

	pushfw
	popw	%ax
	testb	$0x30, %ah	/* IOPL */
	jz	4f

	/* IOPL is not 0 */
	andb	$0xcf, %ah	/* let IOPL = 0 */
	pushw	%ax
	popfw
	pushfw
	popw	%ax
	testb	$0x30, %ah	/* is IOPL still 0? */
	jz	2f		/* CPL is 0 */
	jmp	3f
4:
	/* IOPL is 0 */
	orb	$0x30, %ah	/* let IOPL != 0 */
	pushw	%ax
	popfw
	pushfw
	popw	%ax
	testb	$0x30, %ah	/* is IOPL still 0? */
	jnz	2f		/* CPL is 0 */
	jmp	3f
2:
	/* ring 0 of 16-bit protected mode will get here */
	andb	$0xcf, %ah	/* let IOPL = 0 */
	pushw	%ax
	popfw
	jmp	real2		/* CPL = 0, Continue */
3:
	/* CPL != 0 */

	#; we must switch to ring 0

	#; Allocate Descriptors
	movw	$0x0000, %ax	#; function number
	movw	$1, %cx		#; CX = Number of descriptors to allocate
	int	$0x31		#; call DPMI
				#; return AX = Base selector
	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode

	movw	%ax, ABS_PSP(selector_alloc)

	#; Get Descriptor
	movw	$0x000B, %ax	#; function number
	movw	%ds, %bx	#; selector number
	#; ES:(E)DI = Pointer to an 8 byte buffer to receive copy of descriptor
	movl	$ABS_PSP(descriptor_buf), %edi
	pushw	%es
	pushw	%ds
	popw	%es
	int	$0x31		#; call DPMI
	popw	%es
				#; DS:DI points to buffer

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode

	#; Set Descriptor
	movw	$0x000C, %ax	#; function number
	movw	ABS_PSP(selector_alloc), %bx	#; selector number
	#; ES:(E)DI = Pointer to an 8 byte buffer that contains descriptor.
	#; The type byte (byte 5) follows the same format and restrictions
	#; as the access rights/type parameter (in CL) to Set Descriptor
	#; Access Rights. The extended type byte (byte 6) follows the same
	#; format and restrictions as the extended access rights/type parameter
	#; (in CH) to Set Descriptor Access Rights, except the limit field may
	#; have any value, except the low order 4 bits (marked "reserved") are
	#; used to set the upper 4 bits of the descriptor's limit.
	movl	$ABS_PSP(descriptor_buf), %edi
	pushw	%es
	pushw	%ds
	popw	%es
	int	$0x31		#; call DPMI
	popw	%es
				#; DS:DI points to buffer

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode

	movw	ABS_PSP(selector_alloc), %cx
	incw	%cx
	testw	$7, %cx
	jnz	message_exit

//	. = . - (ABS_PSP(.) - 0x28F3)

	movw	ABS_PSP(selector_alloc), %cx
	movw	%cx, %fs	#; FS is the new selector

	#; get LDTR(it is a selector that points into GDT)

//	pushw	%ds
//	popw	%fs		#; fs base = 0, limit=64K

//	pushw	%ss
//	popw	%ds

	#; Set Segment Base Address of fs to 0
	#; Sets the 32-bit linear base address field in the LDT descriptor
	#; for the specified segment.
	movw	$0x0007, %ax	#; function number
	movw	%fs, %bx	#; selector number
	#; CX:DX = 32-bit linear base address of segment
	xorw	%cx, %cx
	xorw	%dx, %dx
	int	$0x31		#; call DPMI

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode
	
	#; check if fs base == 0
	#; Get Segment Base Address
	movw	$0x0006, %ax	#; function number
	movw	%fs, %bx	#; selector number
	int	$0x31		#; call DPMI
		#; return CX:DX = 32-bit linear base address of segment

	movw	%dx, %ax
	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode

	testw	%ax, %ax
	jnz	message_exit

	testw	%cx, %cx
	jnz	message_exit

	#; adjust fs limit to 4G
	#; AX = 0008h
	#; BX = Selector
	#; CX:DX = 32-bit segment limit
	movw	$0x0008, %ax	#; function number
	movw	%fs, %bx	#; selector number
	movw	$0xffff, %cx
	movw	$0xffff, %dx
	int	$0x31		#; call DPMI

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode
#if 1
	xorl	%ecx, %ecx
	movl	%fs, %ecx
	lsll	%ecx, %eax
	jnz	message_exit

	movw	$ABS_PSP(err_msg), %dx	#; yup, it's 'Doze

	incl	%eax
	jnz	message_exit

	sgdt	ABS_PSP(gdtr)

//	movl	ABS_PSP(gdtr + 2), %ebx	#; GDT linear base address
//
//	fs testl	$0xFFFFFFFF, (%ebx)
//	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
//	jnz	message_exit		#; Cant_Enter_PMode
#endif
#if 0
	#; Get CS Base Address
	movw	$0x0006, %ax	#; function number
	movw	%cs, %bx	#; selector number
	int	$0x31		#; call DPMI
		#; return CX:DX = 32-bit linear base address of segment

	movw	%dx, %ax
	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode

	shll	$16, %ecx
	movw	%ax, %cx	#; ECX=linear base address of CS

	xorl	%edx, %edx
	movw	ABS_PSP(real_mode_cs), %dx
	shll	$4, %edx

	cmpl	%ecx, %edx
	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jnz	message_exit		#; Cant_Enter_PMode
#endif

	#; Set Protected Mode Interrupt Vector
	#;

	movw	$0x0205, %ax	#; function number
	movb	$0x00, %bl	#; Interrupt number

	#; CX:(E)DX = Selector:Offset of exception handler
	xorl	%edx, %edx
	xorl	%ecx, %ecx
#if 0
	movw	ABS_PSP(real_mode_cs), %cx
	movw	$ABS_PSP(int3_handler), %dx
	shll	$4, %ecx
	addl	%ecx, %edx	#; EDX=linear address
	movl	$0x28, %ecx	#; win9x selector with ring 0
#else
	movw	%cs, %cx
	movw	$ABS_PSP(int3_handler), %dx
#endif
	int	$0x31		#; call DPMI

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode
//	jnc	message_exit		#; Cant_Enter_PMode

	movw	%cs, %cx
	incw	%cx
	testw	$7, %cx
	jnz	message_exit

	#; Allocate Descriptors
	movw	$0x0000, %ax	#; function number
	movw	$1, %cx		#; CX = Number of descriptors to allocate
	int	$0x31		#; call DPMI
				#; return AX = Base selector
	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode

	movw	%ax, ABS_PSP(selector_alloc)

	#; Get Descriptor
	movw	$0x000B, %ax	#; function number
	movw	%cs, %bx	#; selector number
	#; ES:(E)DI = Pointer to an 8 byte buffer to receive copy of descriptor
	movl	$ABS_PSP(descriptor_buf), %edi
	pushw	%es
	pushw	%ds
	popw	%es
	int	$0x31		#; call DPMI
	popw	%es
				#; DS:DI points to buffer

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode

//	andb	$0x9F, 5(%di)	#; Let DPL=0

	#; Set Descriptor
	movw	$0x000C, %ax	#; function number
	movw	ABS_PSP(selector_alloc), %bx	#; selector number
	#; ES:(E)DI = Pointer to an 8 byte buffer that contains descriptor.
	#; The type byte (byte 5) follows the same format and restrictions
	#; as the access rights/type parameter (in CL) to Set Descriptor
	#; Access Rights. The extended type byte (byte 6) follows the same
	#; format and restrictions as the extended access rights/type parameter
	#; (in CH) to Set Descriptor Access Rights, except the limit field may
	#; have any value, except the low order 4 bits (marked "reserved") are
	#; used to set the upper 4 bits of the descriptor's limit.
	movl	$ABS_PSP(descriptor_buf), %edi
	pushw	%es
	pushw	%ds
	popw	%es
	int	$0x31		#; call DPMI
	popw	%es
				#; DS:DI points to buffer

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode

	movw	ABS_PSP(selector_alloc), %cx
	incw	%cx
	testw	$7, %cx
	jnz	message_exit

	#; get LDTR(it is a selector that points into GDT)

	sldt	%bx
#if 0
	/* cannot get ldt base in this way because the function works only
	 * for BX=(a selector that points into LDT)
	 */

	#; Get LDT Base Address
	movw	$0x0006, %ax	#; function number
//	movw	%fs, %bx	#; selector number
	int	$0x31		#; call DPMI
		#; return CX:DX = 32-bit linear base address of LDT

//	movw	$ABS_PSP(err_msg), %dx	#; DEBUG DPMI
//	cmpw	$0x8022, %ax
//	jz	message_exit		#; Cant_Enter_PMode
//	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
//	jmp	message_exit

	movw	%dx, %ax
	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit
#else
	movl	ABS_PSP(gdtr + 2), %eax	#; GDT linear base address
	andl	$0xFFF8, %ebx
	addl	%eax, %ebx		#; EBX points to LDT descriptor
	addr32 fs movl	2(%ebx), %eax		#; lower 3 byte of LDT base
	roll	$8, %eax
	andb	$0x1F, %al
	cmpb	$0x02, %al
	jne	message_exit

	addr32 fs movb	7(%ebx), %al		#; higher byte of LDT base
	rorl	$8, %eax		#; EAX=linear address of LDT base
	movl	%eax, ABS_PSP(ldt_base)
#endif
//	movw	%cx, %bx
//	shll	$16, %ebx
//	movw	%ax, %bx	#; EBX=LDT linear base address

	movl	ABS_PSP(ldt_base), %ebx
	xorl	%ecx, %ecx
	movw	ABS_PSP(selector_alloc), %cx
	andw	$0xFFF8, %cx	#; offset in LDT
	addl	%ecx, %ebx	#; points to descriptor
	
	addr32 fs movb	5(%ebx), %al
	xorb	$0x60, %al
	andb	$0x60, %al

	jnz	message_exit

	addr32 fs xorb	$0x60, 5(%ebx)	#; Let DPL=0

//	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
//	jz	message_exit

	#; Set Protected Mode Interrupt Vector
	#;

	movw	$0x0205, %ax	#; function number
	movb	$0x00, %bl	#; Interrupt number

	#; CX:(E)DX = Selector:Offset of exception handler
	xorl	%edx, %edx
	xorl	%ecx, %ecx

	movw	ABS_PSP(selector_alloc), %cx
	andw	$0xFFFC, %cx
	movw	$ABS_PSP(int3_handler), %dx
	int	$0x31		#; call DPMI

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode

	#; Physical Address Mapping
	#;

	#; To Call

	#;	AX = 0800h
	#;	BX:CX = Physical address of memory
	#;	SI:DI = Size of region to map in bytes

	#; Returns

	#;	If function was successful:
	#;	Carry flag is clear.
	#;	BX:CX = Linear address that can be used to access the physical memory

	#;	If function was not successful:
	#;	Carry flag is set.

	movw	$0x0800, %ax
	movw	$0, %bx
	movw	$0, %cx
	movw	$0x000A, %si
	movw	$0, %di

	int	$0x31

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit

	movw	%cx, ABS_PSP(conventional_linear)
	movw	%bx, ABS_PSP(conventional_linear + 2)

	#; Allocate Memory Block
	#; Allocates and commits a block of linear memory.
	#; Call With
	#;	AX = 0501H
	#;	BX:CX = size of block (bytes, must be nonzero)
	#; Returns
	#;	if function successful
	#;		Carry flag = clear
	#;		BX:CX = linear address of allocated memory block
	#;		SI:DI = memory block handle (used to resize and free block)
	#;	if function unsuccessful
	#;		Carry flag = set
	#;		AX = error code 
	#;			8012H  linear memory unavailable
	#;			8013H  physical memory unavailable
	#;			8014H  backing store unavailable
	#;			8016H  handle unavailable
	#;			8021H  invalid value (BX:CX = 0)
	movw	$0x0501, %ax
	movw	$0x000A, %bx
	movw	$0, %cx

	int	$0x31

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit

	movw	%cx, ABS_PSP(conventional_backup)
	movw	%bx, ABS_PSP(conventional_backup + 2)

	#; Allocate Descriptors
	movw	$0x0000, %ax	#; function number
	movw	$1, %cx		#; CX = Number of descriptors to allocate
	int	$0x31		#; call DPMI
				#; return AX = Base selector
	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode

	movw	%ax, ABS_PSP(selector_alloc1)

	#; Get Descriptor
	movw	$0x000B, %ax	#; function number
	movw	%cs, %bx	#; selector number
	#; ES:(E)DI = Pointer to an 8 byte buffer to receive copy of descriptor
	movl	$ABS_PSP(descriptor_buf), %edi
	pushw	%es
	pushw	%ds
	popw	%es
	int	$0x31		#; call DPMI
//	. = . - (ABS_PSP(.) - 0x2AE6)
	popw	%es
				#; DS:DI points to buffer

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode

	#; Set Descriptor
	movw	$0x000C, %ax	#; function number
	movw	ABS_PSP(selector_alloc1), %bx	#; selector number
	#; ES:(E)DI = Pointer to an 8 byte buffer that contains descriptor.
	#; The type byte (byte 5) follows the same format and restrictions
	#; as the access rights/type parameter (in CL) to Set Descriptor
	#; Access Rights. The extended type byte (byte 6) follows the same
	#; format and restrictions as the extended access rights/type parameter
	#; (in CH) to Set Descriptor Access Rights, except the limit field may
	#; have any value, except the low order 4 bits (marked "reserved") are
	#; used to set the upper 4 bits of the descriptor's limit.
	movl	$ABS_PSP(descriptor_buf), %edi
	pushw	%es
	pushw	%ds
	popw	%es
	int	$0x31		#; call DPMI
	popw	%es
				#; DS:DI points to buffer

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode

	movw	ABS_PSP(selector_alloc1), %cx
	incw	%cx
	testw	$7, %cx
	jnz	message_exit

	movw	ABS_PSP(selector_alloc1), %cx
	movw	%cx, %gs	#; GS is the new selector

	#; Set Segment Base Address of gs
	#; Sets the 32-bit linear base address field in the LDT descriptor
	#; for the specified segment.
	movw	$0x0007, %ax	#; function number
	movw	%gs, %bx	#; selector number
	#; CX:DX = 32-bit linear base address of segment
	//movw	ABS_PSP(conventional_linear), %dx
	//movw	ABS_PSP(conventional_linear + 2), %cx
	//xorw	%cx, %cx
	//xorw	%dx, %dx
	xorl	%ecx, %ecx
	xorl	%edx, %edx
	movw	ABS_PSP(real_mode_cs), %cx
	//shll	$4, %ecx
	//movw	%cx, %dx
	//shrl	$16, %ecx
	movw	%cx, %dx
	shrw	$12, %cx
	shlw	$4, %dx
	int	$0x31		#; call DPMI

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode

	#; adjust gs limit to 64K
	#; AX = 0008h
	#; BX = Selector
	#; CX:DX = 32-bit segment limit
	movw	$0x0008, %ax	#; function number
	movw	%gs, %bx	#; selector number
	movw	$0x0000, %cx
	movw	$0xFFFF, %dx
	int	$0x31		#; call DPMI

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode

	xorl	%ecx, %ecx
	movl	%gs, %ecx
	lsll	%ecx, %eax
	jnz	message_exit

	cmpl	$0x0000FFFF, %eax
	jnz	message_exit

	movl	ABS_PSP(ldt_base), %ebx
	xorl	%ecx, %ecx
	movw	ABS_PSP(selector_alloc1), %cx
	andw	$0xFFF8, %cx	#; offset in LDT
	addl	%ecx, %ebx	#; points to descriptor
	
	addr32 fs movb	5(%ebx), %al
	xorb	$0x60, %al
	andb	$0x60, %al

	jnz	message_exit

	addr32 fs xorb	$0x60, 5(%ebx)	#; Let DPL=0

#if 0
	#; Set Protected Mode Interrupt Vector
	#;

	movw	$0x0205, %ax	#; function number
	movb	$0x00, %bl	#; Interrupt number

	#; CX:(E)DX = Selector:Offset of exception handler
	xorl	%edx, %edx
	xorl	%ecx, %ecx

	movw	ABS_PSP(selector_alloc1), %cx
	andw	$0xFFFC, %cx
	movw	ABS_PSP(real_mode_cs), %dx
	shll	$4, %edx
	addl	$ABS_PSP(int3_handler), %edx
	int	$0x31		#; call DPMI

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit		#; Cant_Enter_PMode
#endif


//	movw	%cs, %cx
//	incw	%cx
//	testw	$7, %cx
//	jnz	message_exit

#if 0
	//pushl	%edx
	sidt	ABS_PSP(idtr)
	//popl	%edx		#; EDX=IDT base address

	movl	ABS_PSP(idtr + 2), %edx

	addl	$(0x00 * 8), %edx
	pushw	%ds
	movw	$0x30, %cx
	movw	%cx, %ds
	addr32 orw	$0xE000, 4(%edx)
	popw	%ds
				#; EBX=original offset of int3 service routine

#endif

	/* we can use int00 instead of int03 */

	xorw	%bx, %bx
	xorw	%dx, %dx
	movw	$1, %ax
#if 0
	divw	%bx
#else
	int	$0x00
#endif

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jmp	message_exit		#; Cant_Enter_PMode

/* DPMI DATA */

dpmi_old_cr0:
	.long	0

dpmi_old_cr3:
	.long	0

ldt_base:
	.long	0

conventional_linear:
	.long	0

conventional_backup:
	.long	0

descriptor_buf:
	.long	0
	.long	0

selector_alloc:
	.word	0
selector_alloc1:
	.word	0
gdtr:
	.word	0
	.long	0

idtr:
	.word	0
	.long	0

/* VCPI DATA */

#; Even if you don't use TSS-based task-switching, you need one
#; TSS to hold the user stack pointer.
tss:
	.word	0, 0		#; back link

	.long	0		#; ESP0
	.word	gdt3 - gdt0, 0	#; SS0, reserved

	.long	0		#; ESP1
	.word	0, 0		#; SS1, reserved

	.long	0		#; ESP2
	.word	0, 0		#; SS2, reserved

	.long	0		#; CR3
	.long	0, 0		#; EIP, EFLAGS
	.long	0, 0, 0, 0	#; EAX, ECX, EDX, EBX
	.long	0, 0, 0, 0	#; ESP, EBP, ESI, EDI
	.word	0, 0		#; ES, reserved
	.word	0, 0		#; CS, reserved
	.word	0, 0		#; SS, reserved
	.word	0, 0		#; DS, reserved
	.word	0, 0		#; FS, reserved
	.word	0, 0		#; GS, reserved
	.word	0, 0		#; LDT, reserved
	.word	0, 0		#; debug, IO perm. bitmap

	.align	16
#; null descriptor
gdt0:
	.word	0	#; limit 15:0
	.word	0	#; base 15:0
	.byte	0	#; base 23:16
	.byte	0	#; type
	.byte	0	#; limit 19:16, flags
	.byte	0	#; base 31:24
#; LINEAR_SEL      equ     $-gdt
gdt1:
	.word	0xFFFF
	.word	0
	.byte	0
	.byte	0x92	#; present, ring 0, data, expand-up, writable
	.byte	0xCF	#; page-granular, 32-bit
	.byte	0
#; CODE_SEL	equ	$-gdt
gdt2:
	.word	0xFFFF
	.word	0
	.byte	0
	.byte	0x9A	#; present, ring 0, code, non-conforming, readable
	.byte	0xCF	#; page-granular, 32-bit
	.byte	0
#; DATA_SEL	equ	$-gdt
gdt3:
	.word	0xFFFF
	.word	0
	.byte	0
	.byte	0x92	#; present, ring 0, data, expand-up, writable
	.byte	0xCF	#; page-granular, 32-bit
	.byte	0
#; CODE_SEL16	equ	$-gdt
gdt4:
	.word	0xFFFF
	.word	0
	.byte	0
	.byte	0x9A	#; present, ring 0, code, non-conforming, readable
	.byte	0	#; byte-granular, 16-bit
	.byte	0
#; DATA_SEL16	equ	$-gdt
gdt5:
	.word	0xFFFF
	.word	0
	.byte	0
	.byte	0x92	#; present, ring 0, data, expand-up, writable
	.byte	0	#; byte-granular, 16-bit
	.byte	0
#; TSS_SEL		equ	$-gdt
gdt6:
	.word	103
	.word	0
	.byte	0
	.byte	0x89	#; Ring 0 available 32-bit TSS
	.byte	0
	.byte	0
#; VCPI_SEL	equ	$-gdt
gdt7:
	.long	0, 0	#; dummy descriptors used by VCPI

	.long	0, 0

	.long	0, 0
gdt10_end:

idt:
	.rept	32

	.word	0		#; low 16 bits of ISR address
	.word	gdt2 - gdt0	#; 32-bit code segment selector
	.byte	0		#; word count
	.byte	0x8E		#; access byte: Present, Ring 0, '386 intr gate
	.word	0		#; high 16 bits of ISR

	.endr
idt_end:

gdt_ptr:
	.word	gdt10_end - gdt0 - 1	#; GDT limit
	.long	ABS_PSP(gdt0)			#; linear, physical address of GDT

idt_ptr:
	.word	idt_end - idt - 1	#; IDT limit
	.long	ABS_PSP(idt)			#; linear, physical address of IDT

real_idt_ptr:
	.word	0x3FF			#; limit 1023
	.long	0			#; IDT (IVT, actually) at address 0

#;krnl_page_table:
#;	dw 0

vcpi_entry:
	.long	0
	.word	gdt7 - gdt0	#; dummy descriptors used by VCPI

vcpi_cr0:
	.long	0

vcpi_control_block:
vcpi_cr3:
	.long	0
vcpi_gdtr:
	.long	ABS_PSP(gdt_ptr)
vcpi_idtr:
	.long	ABS_PSP(idt_ptr)
vcpi_ldtr:
	.word	0
vcpi_tr:
	.word	gdt6 - gdt0	#; 32-bit TSS selector
vcpi_eip:
	.long	ABS_PSP(from_vcpi)
vcpi_cs:
	.word	gdt2 - gdt0	#; 32-bit code segment selector

//page_info:
//	.space	4096	#; padding to 4K boundary
//	.space	4096	#; page dir somewhere in here
//	.space	4096	#; "kernel" page table for bottom 4 meg

#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
#; DATA
#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

PMode_Entry_Off:
	.word	0
PMode_Entry_Seg:
	.word	0

windows_running:
	.long	0

emm386_running:
	.long	0

error_message:
	.long	0

err_msg:
	.ascii	"\r\nIt is in VM86 mode but without VCPI. Enable VCPI with EMM386 and try again.\r\n"
	.ascii	"\r\nThis problem will occur when GRUB.EXE runs at the Command Prompt of Windows\r\n"
	.ascii	"NT/2K/XP. If so, restart the computer with a bootable DOS floppy and try again.\r\n$"

win_msg:
	.ascii	"\r\nDue to a DPMI failure, GRUB.EXE cannot run in a Windows DOS box.\r\n"
	.ascii	"\r\nRestart the computer in MS-DOS mode and try again.\r\n$"

warning_win_msg:
	.ascii	"\r\nRunning GRUB.EXE from a Windows DOS box could hang the machine!\r\n"
	.ascii	"\r\nYou should better restart the computer in MS-DOS mode and run GRUB.EXE there.\r\n"
	.ascii	"\r\n        !!Save your work before you choose to continue!!\r\n$"

cancel_msg:
	.ascii	"\r\n\r\nCancelled.\r\n$"

vcpi_err_msg:
	.ascii	"\r\nError getting VCPI server entry point.\r\n$"

int3_handler:

	/* it is our handler, int3 or int0 */

	/* it seems our handler is in 16-bit protected mode */

	.code16

	cli
//	jmp	0f
//
//	#; simply return if we are in real mode
//	incl	%ebx
//	xorw	%dx, %dx
//	xorw	%ax, %ax
//
//	iret
//
//0:

	#;jmp	ring_check

#; 5. clear the PE bit
	movl	%cr0, %eax
	andb	$0xFE, %al
	movl	%eax, %cr0

	pushfw
	popw	%ax
	testb	$0x30, %ah	/* IOPL */
	jz	4f

	/* IOPL is not 0 */
	andb	$0xcf, %ah	/* let IOPL = 0 */
	pushw	%ax
	popfw
	pushfw
	popw	%ax
	testb	$0x30, %ah	/* is IOPL still 0? */
	jz	2f		/* CPL is 0 */
	jmp	3f
4:
	/* IOPL is 0 */
	orb	$0x30, %ah	/* let IOPL != 0 */
	pushw	%ax
	popfw
	pushfw
	popw	%ax
	testb	$0x30, %ah	/* is IOPL still 0? */
	jnz	2f		/* CPL is 0 */
	jmp	3f
3:

//	. = . - (ABS_PSP(.) - 0x2A36)

	/* CPL != 0 */
#if 0
	movw	$1, %bx
	movw	$0, %ax
	movw	$0, %dx
	iret
#endif
	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jmp	message_exit		#; Cant_Enter_PMode
2:
	/* ring 0 of 16-bit protected mode will get here */
	andb	$0xcf, %ah	/* let IOPL = 0 */
	pushw	%ax
	popfw

	/* we are in 16-bit protected mode with CPL=0 */
#if 0
	/* for debug only */
	movl	$ABS_PSP(int3_handler), %eax
	xorl	%ecx, %ecx
	movw	ABS_PSP(real_mode_cs), %cx
	shll	$4, %ecx
	addl	%ecx, %eax

	addr32 fs cmpw	$0xEBFA, (%eax)
	jne	0f
//	jmp	real2		/* CPL = 0, Continue */
	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
0:
	jmp	message_exit		#; Cant_Enter_PMode
#endif

	/* now switch from privileged protected mode to real mode */

	#; save old dpmi cr0 and cr3

	movl	$ABS_PSP(dpmi_old_cr0), %edi
	movl	%cr0, %eax
	movl	%eax, (%di)
	xorl	%esi, %esi
	movw	ABS_PSP(real_mode_cs), %si
	shll	$4, %esi
	addl	%esi, %edi
//	. = . - (ABS_PSP(.) - 0x2BBA)
	addr32 fs movl	%eax, (%edi)

	movl	$ABS_PSP(dpmi_old_cr3), %edi
	movl	%cr3, %eax
	movl	%eax, (%di)
	xorl	%esi, %esi
	movw	ABS_PSP(real_mode_cs), %si
	shll	$4, %esi
	addl	%esi, %edi
	addr32 fs movl	%eax, (%edi)

	#; get physical base address of page dir
	andl	$0xFFFFF000, %eax

	movw	%ax, %cx
	shrl	$16, %eax
	movw	%ax, %bx

	#; Physical Address Mapping
	#;

	#; To Call

	#;	AX = 0800h
	#;	BX:CX = Physical address of memory
	#;	SI:DI = Size of region to map in bytes

	#; Returns

	#;	If function was successful:
	#;	Carry flag is clear.
	#;	BX:CX = Linear address that can be used to access the physical memory

	#;	If function was not successful:
	#;	Carry flag is set.

	movw	$0x0800, %ax
	movw	$0x0000, %si
	movw	$0x1000, %di

	int	$0x31

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit

	movw	%bx, %si
	shll	$16, %esi
	movw	%cx, %si	#; ESI=linear base address of page dir

	#; load the first entry
	cld
//	. = . - (ABS_PSP(.) - 0x2BE8)
	addr32 fs lodsl

	pushl	%eax

	#; copy all page dir entries except the first one
	movw	%es, %ax
	movw	%fs, %bx
	movw	%bx, %es
	movl	$(1024 - 1), %ecx
	movl	ABS_PSP(vcpi_cr3), %edi
	addl	$4, %edi
	cld
	repz addr32 fs movsl
	movw	%ax, %es

	popl	%eax

	#; get physical base address of the first page table
	andl	$0xFFFFF000, %eax
	
	movw	%ax, %cx
	shrl	$16, %eax
	movw	%ax, %bx

	#; Physical Address Mapping
	#;

	#; To Call

	#;	AX = 0800h
	#;	BX:CX = Physical address of memory
	#;	SI:DI = Size of region to map in bytes

	#; Returns

	#;	If function was successful:
	#;	Carry flag is clear.
	#;	BX:CX = Linear address that can be used to access the physical memory

	#;	If function was not successful:
	#;	Carry flag is set.

	movw	$0x0800, %ax
	movw	$0x0000, %si
	movw	$0x1000, %di

	int	$0x31

	movw	$ABS_PSP(win_msg), %dx	#; yup, it's 'Doze
	jc	message_exit

	movw	%bx, %si
	shll	$16, %esi
	movw	%cx, %si	#; ESI=linear base address of the first page table

	#; skip the leading 160 page table entries
	addl	$(160 * 4), %esi	#; 160 = 640K / 4K

	#; copy the rest of the page table entries
	movw	%es, %ax
	movw	%fs, %bx
	movw	%bx, %es
	movl	$(1024 - 160), %ecx
	movl	ABS_PSP(vcpi_cr3), %edi
	addl	$(4096 + (160 * 4)), %edi
	cld
	repz addr32 fs movsl
	movw	%ax, %es

#if 1
	#; move 640K linear conventional memory to physical 0

	cld
	movw	%es, %ax
	movw	%fs, %bx
	movw	%bx, %es
	movl	ABS_PSP(conventional_backup), %edi
	xorl	%esi, %esi
	movl	$(0xA0000 / 4), %ecx
	repz addr32 fs movsl

	movl	ABS_PSP(conventional_linear), %edi
	movl	ABS_PSP(conventional_backup), %esi
	movl	$(0xA0000 / 4), %ecx
	repz addr32 fs movsl
	movw	%ax, %es

#else
	#; move only the grub.exe image from linear to physical

	movw	%es, %ax
	movw	%fs, %bx
	movw	%bx, %es

	movl	$((ABS_PSP(STAGE2_SIZE + pre_stage2_start + 15 + 0x10000 + 0x03000) / 16) * 4), %ecx
					#; 0x10000 = 64KB for HMA_backup
					#; 0x03000 = 12KB for VCPI page_info
	movl	ABS_PSP(conventional_linear), %edi
	xorl	%esi, %esi
	movw	ABS_PSP(real_mode_cs), %si
	shll	$4, %esi
	addl	%esi, %edi

	cld
	repz addr32 fs movsl
	movw	%ax, %es
#endif

	#; load cr3
	movl	ABS_PSP(vcpi_cr3), %eax
	movl	%eax, %cr3

	#; now the low 640K is identity-mapped

#; back-to-real-mode sequence from 14.5 of 386INTEL.TXT
#; 1. TURN OFF PAGING
#; 1a. jump to code memory which is identity-mapped

	/* Load new GDT. All memory references should be limited in
	 * conventional memory, i.e., lower than physical address 640K.
	 */

	lgdt	ABS_PSP(gdt_ptr)
	ljmp	$(gdt4 - gdt0), $ABS_PSP(2f)	#; 16-bit code segment
2:

#; 1b. clear the PG bit
	movl	%cr0, %eax
	andl	$0x7FFFFFFF, %eax
	movl	%eax, %cr0

#; 1c. "Move zeros to CR3 to clear out the paging cache."
	xorl	%eax, %eax
	movl	%eax, %cr3
#; 2. jump to 16-bit code segment
	//ljmp	$(gdt4 - gdt0), $ABS_PSP(real2)
	//		#; (gdt4 - gdt0) is 16-bit code segment selector

	#; we are already in 16-bit code segment
	jmp	real2


	.code16

#; Protected mode initialization code would go here.
#; Mark program's real mode memory as pageable, etc.
#;
#;        .
#;        .
#;        .

#;
#; Quit the program and return to real mode DOS
#;
#;        mov     ax, 4C00h
#;        int     21h

check_vcpi:

#; if it's EMM386, we can use VCPI to switch to protected mode
#; Testing for VCPI like this makes Win95 pop up a dialog suggesting
#; "MS-DOS mode". This may or may not be a good thing.
	movw	$0xDE00, %ax
	pushl	%ebx		#; save EBX; not interested in VCPI version
	pushw	%es
	pushl	%edi
	int	$0x67
	popl	%edi
	popw	%es
	popl	%ebx
	cmpb	$0, %ah
	movw	$ABS_PSP(err_msg), %dx
#if 1
	jne	message_exit	# no VCPI; Windows NT/2K/XP
#else
	jne	check_dpmi	# no VCPI; Windows NT/2K/XP
				# DPMI for NT/2K/XP does not work :-( 
#endif
#; get "kernel" page table and partial GDT from the VCPI server.
#; If we set up our own identity-mapped page table, this step is optional.
#; (we still need to do INT 67h AX=DE01h to get the pmode entry
#; point to the VCPI server -- so we can return to V86 mode later)

	#; ES:DI points to buffer for "kernel" page table
	#; DS:SI points to buffer for 3 entries in GDT 

	movw	$ABS_PSP(gdt7), %si	#; dummy descriptors used by VCPI
	movw	$0xDE01, %ax
	pushl	%ebx
	//pushl	%edi
	int	$0x67
	movl	%ebx, ABS_PSP(vcpi_entry)
	//popl	%edi
	popl	%ebx
	cmpb	$0, %ah
	movw	$ABS_PSP(vcpi_err_msg), %dx
	jne	message_exit

#; set up the VCPI control block for the switch to pmode
	addl	%ebx, ABS_PSP(vcpi_gdtr)
	addl	%ebx, ABS_PSP(vcpi_idtr)

#; disable interrupts
	cli

#; OK, let's do it
	movl	$ABS_PSP(vcpi_control_block), %esi
	addl	%ebx, %esi
	movw	$0xDE0C, %ax
#; if all goes well, the interrupt will return at 'from_vcpi'
	int	$0x67

#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
#; MAIN 32-BIT PMODE CODE, here from VCPI
#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

from_vcpi:

	/* This is in 32-bit protected mode. CS=(gdt2 - gdt0) */

	.code32

//1:	jmp	1b
	movw	$(gdt3 - gdt0), %ax	#; 32-bit data segment
	movw	%ax, %ss
	movw	%ax, %ds
	movw	$(gdt1 - gdt0), %ax	#; 4GB, 32-bit data segment, base 0
	movw	%ax, %es
	movw	%ax, %fs
	movw	%ax, %gs

#;	call draw_lines

#; save pmode registers
	movl	%cr0, %eax
	movl	%eax, ABS_PSP(vcpi_cr0)
	#; movl	%cr3, %eax
	#; movl	%eax, ABS_PSP(pmode_cr3)
#; save GDTR LDTR IDTR
	#; (needn't do)

#; back-to-real-mode sequence from 14.5 of 386INTEL.TXT
#; 1. TURN OFF PAGING
#; 1a. jump to code memory which is identity-mapped
	#; (already done)
#; 1b. clear the PG bit
	movl	%cr0, %eax
	andl	$0x7FFFFFFF, %eax
	movl	%eax, %cr0

#; 1c. "Move zeros to CR3 to clear out the paging cache."
	xorl	%eax, %eax
	movl	%eax, %cr3
#; 2. jump to 16-bit code segment (real2 is above, in the BITS 16 section)
	ljmp	$(gdt4 - gdt0), $ABS_PSP(real2)	#; 16-bit code segment

#; enter real mode
#;	mov eax, cr0
#;	and eax, 7ffffffeh	; turn off paging
#;	mov cr0, eax		; enter real mode
#;	xor eax, eax
#;	mov cr3, eax		; flush the TLB

#; return to protected mode

#; restore pmode registers


#; we jump here (in 16-bit pmode) when returning to real mode
#; Back-to-real-mode sequence from 14.5 of 386INTEL.TXT:
#; 3. load segment registers with values "appropriate to real mode"
real2:

	/* This is in 16-bit protected mode */

	.code16

//	. = . - (ABS_PSP(.) - 0x2A84)

	movw	$(gdt5 - gdt0), %ax	#; 16-bit data segment selector
	movw	%ax, %ss
	movw	%ax, %ds
	movw	%ax, %es
	movw	%ax, %fs
	movw	%ax, %gs
#; 4. disable interrupts
	#; (already done)
#; 5. clear the PE bit
	movl	%cr0, %eax
	andb	$0xFE, %al
	movl	%eax, %cr0

#; 6. far jump to true real mode

#if 0
	#; movw	$ABS_PSP(real3), ABS_PSP(real_mode_ip)
	ljmp	*ABS_PSP(real_mode_ip)
#else
	.byte	0xEA	#; ljmp	$CURR_CS, $ABS_PSP(real3)
#endif
real_mode_ip:
	.word	ABS_PSP(real3)
real_mode_cs:
	.word	0	#; filled earlier with the current CS value

#; 7. load an IDT that is compatible with real-mode IVT
real3:

	/* This is in real mode */

	.code16

	/* Note: DS is still of protected mode but working */

	lidt	ABS_PSP(real_idt_ptr)

#; 9. restore real-mode segment registers
	movw	%cs, %ax
	movw	%ax, %ss
	movw	%ax, %ds
	movw	%ax, %es
	movw	%ax, %fs
	movw	%ax, %gs

#; we are in real mode, run grub as normal :-)
#; remember to restore our stack pointer for quit_address to work well
	movw	$ABS_START(dos_stack), %sp

	#; initialize EFLAGS
	pushl	$0
	popfl

#if 1
	cmpl	$0, ABS_START(windows_running)
	je	1f

	/* this is needed for booting via win98 */

	xorw	%ax, %ax

	/* init DMA, stolen from bochs(rombios.c) */

	#; first reset the DMA controllers
	outb	%al, $0x0D	#; disable DMA-1
	outb	%al, $0xDA	#; disable DMA-2
	movl	$2, %ecx		# delay at least 2 microseconds
	call	iodelay

	#; then initialize the DMA controllers
	movb	$0xC0, %al	#; cascade mode of channel 4 enabled
	outb	%al, $0xD6	#; DMA-2 mode register
	movb	$0x00, %al	#; unmask channel 4
	outb	%al, $0xD4	#; DMA-2 mask register
	movl	$2, %ecx		# delay at least 2 microseconds
	call	iodelay
1:
#endif

	#; initialize PIC here
	#; Note that the code for init_pic is shared. It can be called when
	#; grub.exe is running both from dos and from kexec on linux.
	call	init_pic

#if 0
	#; disable DMA
	movb	$0, %al
	outb	%al, $0x0D	#; disable DMA-1
	outb	%al, $0xDA	#; disable DMA-2
	movl	$2, %ecx		# delay at least 2 microseconds
	call	iodelay

	#; system clock 0 set to mode 3
	movb	$0x16, %al	#; 8-bit command, mode 3, binary data
	outb	%al, $0x43	#; sent to mode control port
	movl	$2, %ecx		# delay at least 2 microseconds
	call	iodelay

	movb	$0, %al		#; data 0 for 18.2Hz
	outb	%al, $0x40	#; save to clock 0 
	movl	$2, %ecx		# delay at least 2 microseconds
	call	iodelay
#endif

#if 1
	cmpl	$0, ABS_START(windows_running)
	je	1f

	/* this is needed for booting via win98 */

	/* EISA 8259-1 */
	/* init system timer 0 (stolen from bochs rombios.c) */
#if 0
	movb	$0x34, %al	# system timer 0, 16-bit binary count, mode 2
#else
	/* system timer 0 should be in mode 3 */
	movb	$0x36, %al	# system timer 0, 16-bit binary count, mode 3
#endif
	movw	$0x43, %dx
	call	outb_and_delay

	movb	$0x00, %al	# maximum count of 0000H = 18.2Hz
	movw	$0x40, %dx
	call	outb_and_delay	# write lo byte 00
	call	outb_and_delay	# write hi byte 00

	/* disable NMI */
	orb	$0x80, %al
	outb	%al, $0x70
	movl	$2, %ecx		# delay at least 2 microseconds
	call	iodelay
1:
#endif

#if 1
	cmpl	$0, ABS_START(windows_running)
	je	1f

	/* this is needed for booting via win98 */

	/* EISA 8259-1 */
	movw	$0x4D0, %dx
	inb	%dx, %al
	movw	$0x21, %dx	# mask off level-triggerred IRQs
	call	outb_and_delay

	/* EISA 8259-2 */
	movw	$0x4D1, %dx
	inb	%dx, %al
	movw	$0xA1, %dx	# mask off level-triggerred IRQs
	call	outb_and_delay
1:
#endif

#if 0
	/* debug check for a working emm386 VCPI */
	jmp	message_exit1
#endif

	cmpl	$0, ABS_START(windows_running)
	jne	restore_BIOS_environment	# no backup 64K DOS memory
	jmp	backup_low_memory_and_HMA


//----------------------------------------------------------------------------
	.align	4
options_doing:
	.long	0
options_done:
	.long	0

	.align	4
option_bypass_dos:
	.ascii	"--bypass"
option_bypass_dos_end:
	.align	4
bypass:
	.long	0
option_bypass1_dos:
	.ascii	"--BYPASS"
option_bypass1_dos_end:
	.align	4
time_out:
	.long	0x80000000
option_time_out_dos:
	.ascii	"--time-out="
option_time_out_dos_end:
	.align	4
option_time_out1_dos:
	.ascii	"--TIME-OUT="
option_time_out1_dos_end:
	.align	4
hot_key:
	.long	0xffff3920
option_hot_key_dos:
	.ascii	"--hot-key="
option_hot_key_dos_end:
	.align	4
option_hot_key1_dos:
	.ascii	"--HOT-KEY="
option_hot_key1_dos_end:
	.align	4
option_duce_dos:
	.ascii	"--duce"
option_duce_dos_end:
	.align	4
duce:
	.long	0
option_duce1_dos:
	.ascii	"--DUCE"
option_duce1_dos_end:
	.align	4
option_chs_no_tune_dos:
	.ascii	"--chs-no-tune"
option_chs_no_tune_dos_end:
	.align	4
chs_no_tune:
	.long	0
option_chs_no_tune1_dos:
	.ascii	"--CHS-NO-TUNE"
option_chs_no_tune1_dos_end:
	.align	4
option_config_file_dos:
	.ascii	"--config-file="
option_config_file_dos_end:
default_config_file_dos:
	.ascii	"/menu.lst"
default_config_file_dos_end:

	.byte	0		/* mark the end of ascii zero string */

	/* bad DOS pathname delimiter! Don't use single back slash by mistake! */

default_config_file_dos2:
	.ascii	"\\menu.lst\0"		/* use double back slashes */

default_config_file_dos1:
	.ascii	".\\menu.lst\0"		/* use double back slashes */

usage_string: /* DOS string terminator is dollar($), not the null char */
	.ascii	"\r\nGRUB: Unrecognized or failed command line parameters. Usage:\r\n"
	.ascii	"\tGRUB [OPTIONS]\r\n"
	.ascii	"OPTIONS: --bypass, --time-out=T, --hot-key=K, --duce, --chs-no-tune,\r\n"
	.ascii	"OPTIONS: --config-file=\"FILE\"\r\n"
	.ascii	"The options are case-sensitive, you must use lower-case letters. Each\r\n"
	.ascii	"option can be specified only once at most.\r\n"
//	.ascii	"option can be specified only once at most. FILE defaults to (hd0,0)/menu.lst:\r\n"
//	.ascii	"\tGRUB --config-file=(hd0,0)/menu.lst\r\n"
	.ascii	"FILE can be specified in GRUB or DOS style. If FILE is led by the pair '#@',\r\n"
	.ascii	"then a DOS filename follows.\r\n"
	.ascii	"FILE can also be some GRUB commands delimited by semi-colon, or the whole\r\n"
	.ascii	"content of a menu file(again semi-colon delimits each line of the menu file).\r\n"
	.ascii	"FILE can be double-quoted(this is recommended, especially for use as embedded\r\n"
	.ascii	"commands or menu).     Hexdump of command-line buffer in PSP:\r\n$"

fatal_string:
	.ascii	"\r\nFatal error: filename too long!\r\n$"

dos_unsupport_string:
#ifdef	BAD_BIOS
	.ascii	"\r\nSorry! Only MS-DOS 7+ and FreeDOS are supported.\r\n\r\nPrograms such as TSRs and device drivers may also change the BIOS interrupt\r\nvector table. Make sure those programs are not running, then try again.\r\n$"
#else
	.ascii	"\r\nFailure restore ROM INT 0xHH vector. Unsupported DOS, device driver, or TSR.\r\n$"
#endif

#if 0
A20_crash_string:
	.ascii	"\r\nGRUB.EXE: About to turn on A20. Report bug if crashing. CR0=0x$"
#endif

//check_bootable_cdrom_string:
//	.ascii	"\r\nAbout to check bootable CDROM disk emulation...\r\n$"
//terminate_cdrom_emulation_string:
//	.ascii	"\r\nAbout to terminate CDROM disk emulation...\r\n$"
//check_bootable_cdrom_done_string:
//	.ascii	"\r\nBootable CDROM check is done\r\n$"

press_space_bar_string:
	.ascii	"\r\nPress space bar$"

press_hot_key_string:
	.ascii	"\r\nPress your hot-key$"

press_any_key_string:
	.ascii	" to start GRUB, any other key to bypass GRUB ...$"

	.align	4

//mapped_int13_vector_BIOS:
//	.word	0	/* hooked int13 segment */
//	.word	0	/* low mem in K before int13 hook */
//	.long	0	/* original BIOS int13 vector if non-zero */
stage2_64K_pages:
	.long (STAGE2_SIZE + 0x1010 + 0x200 + 0xffff) >> 16
//boot_drive:
//	.long	0x80	/* default boot drive is (hd0) */
a20_status:
	.long	0

sleep_5_seconds:

	.code16

	/* sleep 5 seconds */

	/* sleep forever if ABS_PSP(time_out) is 0xff */

	/* calculate the timeout ticks */

	pushw	%es
	pushw	%ds
	pushl	%edx

	pushw	%ds
	popw	%es

	movl	$0xffffffff, %edx
	movzbl	ABS_PSP(time_out), %eax
	cmpb	$0xff, %al
	je	1f
	movl	$18, %edx	/* 18.2 ticks per second. We simply use 18. */
	mulw	%dx		/* EDX=0, EAX=ticks */
	xchgw	%ax, %dx	/* EAX=0, EDX=ticks */
1:
	xorw	%ax, %ax
	movw	%ax, %ds	/* DS=0 */
	movl	0x46c, %eax	/* initial tick */
	movl	%eax, %ecx	/* ECX=initial tick */
	testl	%edx, %edx
	js	1f
	addl	%edx, %eax	/* EAX=timeout tick */
	jmp	3f
1:
	movl	%edx, %eax	/* EAX=0xffffffff */
3:
	movl	0x46c, %ebx	/* EBX=current tick */
	cmpl	%ecx, %ebx
	jnb	2f

	/* current tick is less than initial tick, this means the ticks have
	 * overflowed to the next day, and EBX is rather small. */
	xorl	%ecx, %ecx
	movl	%edx, %eax
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
	cmpl	%eax, %ebx	/* timeout? */
	jbe	3b		/* no, continue to wait */

	/* timeout reached, CF=0, no key pressed. */
	/* `above' for no key */
	popl	%edx
	popw	%ds
	popw	%es
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

	/* DS=0, but ES=old DS on stack */

	xorw	%es:ABS_PSP(hot_key), %ax	/* CF=0 */
	popw	%ax

	je	1f
	xorw	%es:ABS_PSP(hot_key), %ax	/* CF=0 */
	jne	2f		/* not desired, return CF=0 */

	/* remove the desired key from the keyboard buffer. */

	pushfw
	movb	$0, %ah
	int	$0x16	/* discard the key */
	popfw
	jmp	3f

1:
	/* remove the desired key from the keyboard buffer. */

	pushfw
	movb	$0x10, %ah
	int	$0x16	/* discard the key */
	popfw
3:
	stc	/* CF=1, the desired key pressed */
2:
	cmc

	/* `equal' for hot key, `below' for other key */

	popl	%eax
	popl	%edx
	popw	%ds
	popw	%es
	ret

//check_a_range_of_ROM_vectors:
//	cld
//	lodsl
//	cmpl	$0xC0000000, %eax /* ROM vectors assumed to be above C000:0 */
//	jb	1f	/* check failed, with carry */
//	loop	check_a_range_of_ROM_vectors
//	clc		/* check passed, with no carry */
//1:	ret

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
dos_gdt:
	/* this is the default null entry in GDT */
	.word	dos_gdt_end - dos_gdt - 1	# gdt limit
	.long	0				# linear address of dos_gdt
	.word	0				# pad 2 bytes

	.word	0xFFFF				# 4Gb - (0x100000*0x1000 = 4Gb)
	.word	0				# base address = 0
	.word	0x9200				# data read/write
	.word	0x00CF				# granularity = 4096, 386
						#  (+5th nibble of limit)
//	/* real mode data segment base=0x200000 */
//	.word	0xFFFF, 0
//	.byte	0x20, 0x92, 0, 0

	/* real mode data segment base=0 */
	.word	0xFFFF, 0
	.byte	0, 0x92, 0, 0

dos_gdt_end:

quit_address:

	.code16

	cli
	cld
	movw	%cs, %ax
	movw	%ax, %ss
	movw	$(ABS_START(dos_stack) - 36), %sp
	popal
	popw	%es
	popw	%ds

	/* restore High Memory Area */
	pushw	%ds
	pushw	%es
	movw	%ds, %ax
	addw	$(HMA_backup + 1), %ax
	movw	%ax, %ds		/* DS:0 is (CS + HMA_backup):0010 */
	xorw	%si, %si
	movw	$0xFFFF, %di
	movw	%di, %es		/* ES=0xFFFF */
	movw	$0x0010, %di
	movw	$(0x4000-4), %cx	/* move 64KB -16Bytes */
	repz movsl
	popw	%es
	popw	%ds
	
message_exit1:

	.code16

#; if we had escaped from emm386, we should go back to pmode
	cmpl	$0, ABS_PSP(emm386_running)
	jne	1f

	/* No emm386, normal exit to real-mode dos. */

	movw	$0x0003, %ax	/* set display mode: 80*25 color text */
	int	$0x10

	movl	ABS_PSP(error_message), %edx
	testl	%edx, %edx
	jnz	message_exit		/* error */

	movw	$0x4c00, %ax	/* exit with error number 00 */
	//int	$0x21		/* call DOS */
	jmp	terminate_program

1:
	/* emm386 was running and we need to restore its VM86 environment. */

	/* print a debug message */
	movw	$0x0e58, %ax		/* print an 'X' */
	int	$0x10

#; set vital registers: page directory base register(CR3)
	movl	ABS_PSP(vcpi_cr3), %eax
	movl	%eax, %cr3
#; ...GDTR and IDTR
	cli				/* in case interrupt was enabled. */
	lgdt	ABS_PSP(gdt_ptr)
	lidt	ABS_PSP(idt_ptr)
#; ...enable paging and pmode
	movl	ABS_PSP(vcpi_cr0), %eax
	movl	%eax, %cr0
#; far jmp to 32-bit pmode code segment to return to vm86-mode DOS 
	ljmp	$(gdt2 - gdt0), $ABS_PSP(1f)	#; 32-bit code segment

1:
##############################################################################

	/* This is in 32-bit protected mode. CS=(gdt2 - gdt0) */

	/* Will switch to VM86 mode and go back to DOS in VM86 mode */

	.code32

	movw	$(gdt3 - gdt0), %ax	#; 32-bit data segment
	movw	%ax, %ds
	movw	%ax, %ss
	movl	$ABS_START(dos_stack), %esp

	movw	$(gdt1 - gdt0), %ax	#; 4GB, 32-bit data segment, base 0
	movw	%ax, %es
	movw	%ax, %fs
	movw	%ax, %gs

	#; movl	ABS_PSP(vcpi_cr3), %eax
	#; movl	%eax, %cr3
	#; movl	ABS_PSP(vcpi_cr0), %eax
	#; movl	%eax, %cr0

#if 0
	/* FreeDOS has not a working VCPI with EMM386 */
	jmp	1f
#endif

#; return to V86 mode
	movl	$0xDE0C, %eax

#; from E-67DE0C of Ralf Brown's list:
#;	  DS = segment selector mapping entire linear
#;		address space obtained via AX=DE01h
#; I'm not sure what that means, but I peeked inside EMM386.EXE,
#; and it sets DS for me, so I don't have to.

	movzwl	ABS_PSP(real_mode_cs), %ebx
	movl	%esp, %ebp
	pushl	%ebx			#; GS
	pushl	%ebx			#; FS
	pushl	%ebx			#; DS
	pushl	%ebx			#; ES

	pushl	%ebx			#; SS
	pushl	%ebp			#; ESP
	pushl	$0x00023002		#; EFLAGS

	pushl	%ebx			#; CS
	pushl	$ABS_PSP(1f)		#; EIP

	movw	$(gdt7 - gdt0), %bx	#; dummy descriptors used by VCPI
	movw	%bx, %ds

	lcall	%cs:*ABS_PSP(vcpi_entry)

	/* will return to VM86 mode below */

	#; should not reach this

	// in case VCPI returns failure, go to real mode and print a message.
	//jmp	from_vcpi

	/* end of 32-bit code segment of switch to vm86 mode */
##############################################################################

1:
	/* This is in VM86 mode */

	/* Will return to DOS in VM86 mode(terminate normally). */

	.code16

#if 0
#undef debug_putchar
#define debug_putchar(x) movw $(x | ((x << 12) & 0xF000) | (((x << 8) & 0x0F00) ^ 0xC00)), (0x140 + (((x - 0x30) % 80) * 2))

	movw	$0xB800, %ax
	movw	%ax, %ds

	debug_putchar ('2')
	debug_putchar ('3')
	debug_putchar ('4')
	debug_putchar ('5')
#endif
	movw	%cs, %ax
	movw	%ax, %ds
	movw	%ax, %es
	movw	%ax, %fs
	movw	%ax, %gs
	movw	%ax, %ss
	movw	$ABS_START(dos_stack), %sp

	movw	$0x0003, %ax	/* set display mode: 80*25 color text */
	int	$0x10

#if 0
	/* print a debug message */
	movw	$0x0e59, %ax		/* print a 'Y' */
	int	$0x10
#endif

	movl	ABS_PSP(error_message), %edx
	testl	%edx, %edx
	jnz	message_exit		/* error */

	movw	$0x4c00, %ax	/* exit with error number 00 */
	//int	$0x21		/* call DOS */
	jmp	terminate_program

# The mode switch series completed
##############################################################################

#if 0
display_word:

	.code16

	/* routine for display hex value of BP */
	pushaw
	xorw	%bx, %bx
	movw	%bp, %ax
	shrw	$12, %ax
	cmpb	$9, %al
	jbe	1f
	addb	$7, %al
1:
	addb	$0x30, %al
	movb	$0x0e, %ah
	int	$0x10

	movw	%bp, %ax
	shrw	$8, %ax
	andb	$0x0f, %al
	cmpb	$9, %al
	jbe	1f
	addb	$7, %al
1:
	addb	$0x30, %al
	movb	$0x0e, %ah
	int	$0x10

	movw	%bp, %ax
	shrw	$4, %ax
	andb	$0x0f, %al
	cmpb	$9, %al
	jbe	1f
	addb	$7, %al
1:
	addb	$0x30, %al
	movb	$0x0e, %ah
	int	$0x10

	movw	%bp, %ax
	andb	$0x0f, %al
	cmpb	$9, %al
	jbe	1f
	addb	$7, %al
1:
	addb	$0x30, %al
	movb	$0x0e, %ah
	int	$0x10
	popaw
	ret
#endif

backup_low_memory_and_HMA:

	.code16

#if 0
	movw	$ABS_PSP(A20_crash_string), %dx
	movb	$0x09, %ah	/* display a dollar terminated string */
	int	$0x21		/* call DOS */

	movl	%cr0, %eax

	movw	$0x4D1, %dx
	inb	%dx, %al
	movb	%al, %ah
	movw	$0x4D0, %dx
	inb	%dx, %al
	movl	%eax, %ebp

	shrl	$16, %ebp

	call	display_word

	movl	%eax, %ebp

	call	display_word
#endif	

//---------------------------------------------------------------------------
#if 1
	/* if time-out is not 0, sleep */
	movw	ABS_PSP(time_out), %cx
	jcxz	2f

	sti				/* for sleep_5_seconds to work. */

	call	sleep_5_seconds

	//cli	/*2008-08-04*/		/* the clock is not used any more */

	je	1f			/* desired hot-key pressed */
	jb	message_exit1		/* another key pressed */

	/* timeout reached */
2:
	cmpl	$0, ABS_PSP(bypass)	/* default is bypass GRUB? */
	jne	message_exit1		/* yes, exit to DOS */
					/* no, continue to run grub */
1:
#endif	
//---------------------------------------------------------------------------
#if 0
	movl	$0x04000000, %ecx
1:
	addr32 loop	1b
#endif

	/* enable A20! */

	/* oh! it seems we MUST cli, because DOS might enable/disable A20
	 * when entering/leaving DOS interrupt service routine which is
	 * loaded in the High Memory Area.
	 *
	 * We should asure A20 keeps ON when we backup HMA!
	 */


	//cli				/* marked off 2008-08-04 */

	movw	$0x00ff, %cx		# try so many times on failure
	movw	$0x0101, %dx		# with a20 debug on

	/* Note for people who are tracing/debugging this program:
	 *
	 * ENABLE_DISABLE_A20 is not likely what you want to trace into.
	 */

#if 1
	call	enable_disable_a20
	movw	$ABS_PSP(a20_control_fail_string), %dx
	jnz	message_exit		/* enable a20 failed */
	//jz	exit_no_message		/* A20 disabled */
#endif

#if 0	/* marked off 2008-08-04 */
	//pushw	ABS_PSP(time_out)
	movw	$1, ABS_PSP(time_out)	/* sleep 1 second after A20 control */

	sti				/* for sleep_5_seconds to work. */

	call	sleep_5_seconds

	//cli	/*2008-08-04*/		/* the clock is not used any more */
	//popw	ABS_PSP(time_out)
#endif

#if 0
	/* now A20 is on */
	decl	ABS_PSP(a20_status)	# let it be 0xFFFFFFFF
#else
	/* save the current gateA20 status */
	xorl	%eax, %eax
	movl	%eax, ABS_PSP(a20_status)

	/* check A20 status again to confirm */

	call	a20_test	/* ZF=0 for A20 enabled, ZF=1 for disabled */ 
	movw	$ABS_PSP(a20_control_fail_string), %dx
//	jz	1f			/* A20 disabled */
	jz	message_exit		/* enable a20 failed */

	/* now A20 is on */
	decl	%eax		/* EAX=0xFFFFFFFF */
	movl	%eax, ABS_PSP(a20_status)
1:
#endif


	/* backup High Memory Area to HMA_backup */

	pushw	%ds
	pushw	%es
	movw	$0xFFFF, %ax
	movw	%ax, %ds	/* DS=0xFFFF(i.e., HMA segment) */

	/* HMA_backup is the destination address */
	movw	%es, %ax
	addw	$(HMA_backup), %ax
	movw	%ax, %es

	movw	$0x4000, %cx	/* 0x4000 dwords= 64KB */
	xorw	%si, %si
	xorw	%di, %di
	cld
	repz movsl
	popw	%es
	popw	%ds

	/* HMA backup is done, so it is safe now to sti. But this could
	 * cause A20 off, even keyboard off. So we don't sti until DOS
	 * has totally gone.
	 */
	//sti


	/* save 640KB conventional memory(surely, including 64K at HMA_backup)
	 * to physical address 0x200000=2MB, so we could restore our DOS
	 * memory later.
	 */

	/* fill gdt base first thing! */
	xorl	%eax, %eax
	movw	%ds, %ax
	shll	$4, %eax
	addl	$ABS_PSP(dos_gdt), %eax
	movl	%eax, ABS_PSP(dos_gdt) + 2

	/* DS=ES */

	/* Save all registers on stack, which quit_address will use to
	 * restore registers after pre_stage2 calls quit.
	 */

	pushw	%ds
	pushw	%es
	pushal
	//movw	%es, %bx	# save old ES to BX
	movl	ABS_PSP(a20_status), %edx

	cli
	lgdt	ABS_PSP(dos_gdt)

	/* Note for people who are tracing/debugging this program:
	 *
	 * This will switch to protected mode! Don't single step it!
	 *
	 * Set break point at restore_BIOS_environment, and go!
	 */

	movl	%cr0, %eax
	orb	$1, %al
	movl	%eax, %cr0

	/* Here the CPU is in protected mode. The real mode interrupt
	 * vector table won't work now.
	 *
	 * Note that the CS segment is still 16-bit because we have not
	 * reloaded CS with a 32-bit segment selector.
	 */

	jmp	1f
1:
	movw	$8, %si		# 4GB limit
	movw	%si, %es
	movw	%si, %ds

	xorl	%ebp, %ebp
	xorl	%esi, %esi
	movl	$0x200000, %edi
	movl	$(0xA0000 / 4), %ecx	# move 640K

	cld
1:
	addr32 lodsl	(%esi)
	addl	%eax, %ebp
	addr32 stosl	(%edi)
	addr32 loop	1b
	//decl	%ecx
	//jnz	1b
	
	movl	$0x50554B42, %eax	# "BKUP"
	addl	%eax, %ebp
	addr32 stosl	(%edi)
	xchgl	%eax, %edx
	addl	%eax, %ebp
	addr32 stosl	(%edi)
	movw	%cs, %ax
	shll	$16, %eax
	movw	$ABS_START(quit_address), %ax
	addl	%eax, %ebp
	addr32 stosl	(%edi)

	xchgl	%eax, %ebp
	negl	%eax
	addr32 stosl	(%edi)

	movw	$16, %si	# get real mode 64K segment limit
	movw	%si, %es
	movw	%si, %ds

	movl	%cr0, %eax
	andb	$0xfe, %al
	movl	%eax, %cr0

	jmp	1f
1:
	/* Here the CPU turns back to real mode. The real mode interrupt
	 * vector table should work now.
	 *
	 * Note that the CS segment is still 16-bit because we have not
	 * reloaded CS with a 32-bit segment selector.
	 */

	//jmp	1b
	//movw	%bx, %es	# restore ES from BX
	//movw	%bx, %ds	# restore DS from BX
	sti			/* added 2008-08-04 */
	popal
	popw	%es
	popw	%ds


restore_BIOS_environment:

	/* Now we should be safely in real mode. But if emm386_running,
	 * the probe_int should have been called while in VM86 mode,
	 * and we shouldn't call it once more.
	 */

	cmpl	$0, ABS_PSP(emm386_running)
	jne	1f

	/* Note for people who are tracing/debugging this program:
	 *
	 * PROBE_INT will take over int01, so probably you don't want
	 * to trace into PROBE_INT.
	 */

	call	probe_int

	jc	failed_probe_int

1:

	/* Note for people who are tracing/debugging this program:
	 *
	 * restore_BDA_EBDA will destroy the DOS memory structure,
	 * i.e., the MCB (Memory Control Block).
	 * 
	 * If you trace into restore_BDA_EBDA now, DOS could hang
	 * when you quit the debugger.
	 */

	call	restore_BDA_EBDA

	/* Note for people who are tracing/debugging this program:
	 *
	 * Oh! Don't continue. The interrupt vector table will be changed!
	 * The DOS(especially with your debugger!) will disappear!
	 * It will be overwritten by the GRUB code and data of pre_stage2.
	 * After pre_stage2 gains control, the processor will switch to
	 * protected mode.
	 */

	/* overwrite 1 sector of IVT with the new bios_interrupt_vector_table */
	movw	%cs, %ax
	movw	%ax, %ds
	movw	$ABS_START(bios_interrupt_vector_table), %si
	xorw	%di, %di		/* ES:DI=0000:0000 */
	movw	%di, %es
	movw	$0x80, %cx

	cli
	cld
	repz movsl
	sti				/* added 2008-08-04 */

#if 0					/* marked out in 2008-05-07 */
	/* restore int 13 and int 15 for disk emulation */
	movl	ABS_START(tmp_int13_vector), %eax
	cmpl	$0x5A000000, %eax	// cmpl	$0x9A000000, %eax
	jb	1f
	movw	$0x4C, %di
	stosl
	
	movl	ABS_START(tmp_int15_vector), %eax
	cmpl	$0x5A000000, %eax	// cmpl	$0x9A000000, %eax
	jb	1f
	movw	$0x54, %di
	stosl
1:
#endif
	jmp	move_stage2_image

failed_probe_int:
	/* probe failure */
	movw	%cs, %ax
	movw	%ax, %ds
	movw	%ax, %es
#ifndef	BAD_BIOS
	xchgw	%ax, %cx	# move CL to AL
	xorb	%ah, %ah
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
	movw	%ax, ABS_START(dos_unsupport_string) + 28
#endif
	movl	$ABS_START(dos_unsupport_string), ABS_PSP(error_message)
	jmp	message_exit1


probe_int:

#ifdef	BAD_BIOS

	/* copy 1 sector of IVT to bios_interrupt_vector_table */
	movw	%cs, %ax
	movw	%ax, %es		/* ES=CS */
	movw	$ABS_START(bios_interrupt_vector_table), %di
	xorw	%si, %si		/* SI=0 */
	movw	%si, %ds		/* DS=0 */
	movw	$0x80, %cx
2:
	cld
	lodsl
	cmpl	$0, %es:(%di)
	jne	1f
	stosl
	subw	$4, %di
1:
	addw	$4, %di
	loop	2b

	/* OK, now begin to guess dos versions */

	/* check MS-DOS 7.0+ */
	
	xorw	%ax, %ax
	movw	%ax, %ds		/* DS=0 */

	movw	$0x0560, %si /* begins the int 08 vector */
	cld
	lodsl			/* int 08 - IRQ 0 - system timer */
	cmpl	$0xC0000000, %eax
	jb	failed_check_msdos7plus
	lodsl			/* int 09 - IRQ 1 - keyboard data ready */
	cmpl	$0xC0000000, %eax
	jb	failed_check_msdos7plus
	//lodsl			/* int 0A - IRQ 2 - LPT2(PC), vertical retrace interrupt */
	//lodsl			/* int 0B - IRQ 3 - serial communications(COM2) */
	//lodsl			/* int 0C - IRQ 4 - serial communications(COM1) */
	//lodsl			/* int 0D - IRQ 5 - fixed disk(PC,XT), LPT2(AT), reserved(PS/2) */
	//lodsl			/* int 0E - IRQ 6 - diskette controller */
	//lodsl			/* int 0F - IRQ 7 - parallel printer */
#if 0
	/* this area seems to be an internal MSDOS stack, so may be corrupted */
	movw	$0x05dc, %si /* begins the int 70 vector */
	movw	$0x0008, %cx /* 8 vectors to check, from int 70 to 77 */
	call	check_a_range_of_ROM_vectors
	jc	failed_check_msdos7plus
#else
	movw	$0x05DC, %si	/* int 70 - IRQ 8 - CMOS real-time clock */
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	1f
	movw	$0x01C0, %si	/* int 70 - IRQ 8 - CMOS real-time clock */
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	1f
	ldsw	-4(%si), %si	/* DS changed! */
	subw	$4, %si
	lodsl
	cmpl	$0xC0000000, %eax
	jb	failed_check_msdos7plus
	xorw	%ax, %ax
	movw	%ax, %ds	/* DS = 0 */
1:
	movw	$0x05E0, %si	/* int 71 - IRQ 9 - redirected to int 0A by BIOS */
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	1f
	movw	$0x01C4, %si	/* int 71 - IRQ 9 - redirected to int 0A by BIOS */
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jb	failed_check_msdos7plus
1:
//	movw	$0x05E4, %si	/* int 72 - IRQ 10 - reserved */
//	cld
//	lodsl
//	cmpl	$0xC0000000, %eax
//	jnb	1f
//	movw	$0x01C8, %si	/* int 72 - IRQ 10 - reserved */
//	cld
//	lodsl
//	cmpl	$0xC0000000, %eax
//	jnb	1f
//	ldsw	-4(%si), %si	/* DS changed! */
//	lodsw
//	cmpw	$0x10EB, %ax
//	jne	failed_check_msdos7plus
//	lodsl
//	cmpl	$0xC0000000, %eax
//	jb	failed_check_msdos7plus
//	xorw	%ax, %ax
//	movw	%ax, %ds	/* DS = 0 */
1:
//	movw	$0x05e8, %si	/* int 73 - IRQ 11 - reserved */
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jnb	1f
//	movw	$0x01cc, %si
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jnb	1f
//	ldsw	-4(%si), %si   /* DS got changed */
//	lodsw
//	cmpw	$0x10eb, %ax
//	jne	failed_check_msdos7plus
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos7plus
//	xorw	%ax, %ax
//	movw	%ax, %ds	/* let DS = 0 */
1:
//	movw	$0x05ec, %si	/* int 74 - IRQ 12 - pointing device(PS) */
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jnb	1f
//	movw	$0x01d0, %si
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jnb	1f
//	ldsw	-4(%si), %si   /* DS got changed */
//	lodsw
//	cmpw	$0x10eb, %ax
//	jne	failed_check_msdos7plus
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos7plus
//	xorw	%ax, %ax
//	movw	%ax, %ds	/* let DS = 0 */
1:
	movw	$0x05f0, %si	/* int 75 - IRQ 13 - math coprocessor exception(AT+) */
	cld
	lodsl
	cmpl	$0xc0000000, %eax
	jnb	1f
	movw	$0x01d4, %si
	cld
	lodsl
	cmpl	$0xc0000000, %eax
	jb	failed_check_msdos7plus
1:
//	movw	$0x05f4, %si	/* int 76 - IRQ 14 - hard disk controller - operation complete(AT+) */
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jnb	1f
//	movw	$0x01d8, %si
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jnb	1f
//	ldsw	-4(%si), %si   /* DS got changed */
//	lodsw
//	cmpw	$0x10eb, %ax
//	jne	failed_check_msdos7plus
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos7plus
//	xorw	%ax, %ax
//	movw	%ax, %ds	/* let DS = 0 */
1:
//	movw	$0x05f8, %si	/* int 77 - IRQ 15 - reserved(AT, PS) - secondary IDE controller */
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jnb	1f
//	movw	$0x01dc, %si
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jnb	1f
//	ldsw	-4(%si), %si   /* DS got changed */
//	lodsw
//	cmpw	$0x10eb, %ax
//	jne	failed_check_msdos7plus
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos7plus
//	xorw	%ax, %ax
//	movw	%ax, %ds	/* let DS = 0 */
1:
#endif
	cmpl	$0, 0x5A4	/* int 19 vector(?) must be 0 */
	jnz	failed_check_msdos7plus

	cmpl	$0xC0000000, 0x5D4	/* int 4B - Virtual DMA Specification */
	jb	failed_check_msdos7plus

	movw	$0x800, %si	/* another saved int 10 vector */
	cld
	lodsb
	cmpb	$0x10, %al
	jnz	failed_check_msdos7plus
	cld
	lodsl
	cmpl	%eax, 0x580	/* saved int 10 vector */
	jnz	failed_check_msdos7plus

	movw	$0x805, %si	/* another saved int 13 vector */
	cld
	lodsb
	cmpb	$0x13, %al
	jnz	failed_check_msdos7plus
	cld
	lodsl
	cmpl	%eax, 0x58C	/* saved int 13 vector */
	jnz	failed_check_msdos7plus

	movw	$0x80A, %si	/* another saved int 15 vector */
	cld
	lodsb
	cmpb	$0x15, %al
	jnz	failed_check_msdos7plus
	cld
	lodsl
	cmpl	%eax, 0x594	/* saved int 15 vector */
	jnz	failed_check_msdos7plus

	movw	$0x814, %si	/* another saved int 1B vector */
	cld
	lodsb
	cmpb	$0x1B, %al
	jnz	failed_check_msdos7plus
	cld
	lodsl
	cmpl	%eax, 0x5AC	/* saved int 1B vector */
	jnz	failed_check_msdos7plus

	movw	$0x819, %si	/* another saved int 4F vector */
	cld
	lodsb
	cmpb	$0x4F, %al
	jnz	failed_check_msdos7plus
	cld
	lodsl
	cmpl	%eax, 0x5D8	/* saved int 4F vector */
	jnz	failed_check_msdos7plus

	movw	$0x81E, %si	/* another saved int 08 vector */
	cld
	lodsb
	cmpb	$0x08, %al
	jnz	failed_check_msdos7plus
	cld
	lodsl
	cmpl	%eax, 0x560	/* saved int 08 vector */
	jnz	failed_check_msdos7plus

	movw	$0x823, %si	/* another saved int 0F vector */
	cld
	lodsb
	cmpb	$0x0F, %al
	jnz	failed_check_msdos7plus
	cld
	lodsl
	cmpl	%eax, 0x57C	/* saved int 0F vector */
	jnz	failed_check_msdos7plus

	/* yes, it is MS-DOS 7.0+ */
	
	xorw	%ax, %ax
	movw	%ax, %ds		/* DS=0 */
	movw	$0x540, %si		/* int 00 to 1F */
	movw	%cs, %ax
	movw	%ax, %es		/* ES=CS */
	movw	$ABS_START(bios_interrupt_vector_table), %di

	/* Fix int1A remote boot problem. Reported by John Cobb (Queen Mary, University of London). */
	movw	$0x0020, %cx		/* int 00 to 1F */
	cld
1:
	lodsl
	cmpl	$0xC0000000, (%di)	/* Is it already a ROM vector? */
	jnb	2f			/* Yes. Keep it untouched. */
	stosl				/* No. Store the new vector. */
	subw	$4, %di
2:
	addw	$4, %di
	loop	1b

	movw	$0x5C0, %si		/* int 40 to 43 */
	movw	$ABS_START(bios_interrupt_vector_table + 0x100), %di
	movw	$0x0004, %cx		/* int 40 to 43 */
	repz movsl

	lodsl				/* int 46 */
	movw	$ABS_START(bios_interrupt_vector_table + 0x118), %di
	stosl

	lodsl				/* int 4B, maybe changed by emm386 */
	movw	$ABS_START(bios_interrupt_vector_table + 0x12C), %di
	stosl

	lodsl				/* int 4F */
	movw	$ABS_START(bios_interrupt_vector_table + 0x13C), %di
	stosl
#if 0
	/* the area 0x5dc-0x5ff seems to be an internal MSDOS stack, so may be corrupted */
	movw	$0x01c0, %di	/* int 70 to 77 */
	movw	$0x0010, %cx	/* 16 words to move */
	repz movsw
#else
	movw	$0x5DC, %si	/* int 70 */
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	2f
	movw	$0x1C0, %si
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	1f		/* need not change */
	ldsw	-4(%si), %si	/* DS changed! */
	subw	$4, %si
	lodsl
	xorw	%si, %si
	movw	%si, %ds	/* DS = 0 */
	cmpl	$0xC0000000, %eax
	jb	1f
2:
	movw	$ABS_START(bios_interrupt_vector_table + 0x1C0), %di
	stosl			/* save new int 70 */
1:
	movw	$0x5E0, %si	/* int 71 */
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jb	1f
	movw	$ABS_START(bios_interrupt_vector_table + 0x1C4), %di
	stosl			/* save new int 71 */
1:
	movw	$0x5E4, %si	/* int 72 */
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	2f
	movw	$0x1C8, %si
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	1f		/* need not change */
	ldsw	-4(%si), %si	/* DS changed! */
	lodsw
	lodsl
	xorw	%si, %si
	movw	%si, %ds	/* DS = 0 */
	cmpl	$0xC0000000, %eax
	jb	1f
2:
	movw	$ABS_START(bios_interrupt_vector_table + 0x1C8), %di
	stosl			/* save new int 72 */
1:
	movw	$0x5E8, %si	/* int 73 */
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	2f
	movw	$0x1CC, %si
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	1f		/* need not change */
	ldsw	-4(%si), %si	/* DS changed! */
	lodsw
	lodsl
	xorw	%si, %si
	movw	%si, %ds	/* DS = 0 */
	cmpl	$0xC0000000, %eax
	jb	1f
2:
	movw	$ABS_START(bios_interrupt_vector_table + 0x1CC), %di
	stosl			/* save new int 73 */
1:
	movw	$0x5EC, %si	/* int 74 */
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	2f
	movw	$0x1D0, %si
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	1f		/* need not change */
	ldsw	-4(%si), %si	/* DS changed! */
	lodsw
	lodsl
	xorw	%si, %si
	movw	%si, %ds	/* DS = 0 */
	cmpl	$0xC0000000, %eax
	jb	1f
2:
	movw	$ABS_START(bios_interrupt_vector_table + 0x1D0), %di
	stosl			/* save new int 74 */
1:
	movw	$0x5F0, %si	/* int 75 */
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jb	1f
	movw	$ABS_START(bios_interrupt_vector_table + 0x1D4), %di
	stosl			/* save new int 75 */
1:
	movw	$0x5F4, %si	/* int 76 */
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	2f
	movw	$0x1D8, %si
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	1f
	ldsw	-4(%si), %si	/* DS changed! */
	lodsw
	lodsl
	xorw	%si, %si
	movw	%si, %ds	/* DS = 0 */
	cmpl	$0xC0000000, %eax
	jb	1f
2:
	movw	$ABS_START(bios_interrupt_vector_table + 0x1D8), %di
	stosl			/* save new int 76 */
1:
	movw	$0x5F8, %si	/* int 77 */
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	2f
	movw	$0x1DC, %si
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	1f
	ldsw	-4(%si), %si	/* DS changed! */
	lodsw
	lodsl
	xorw	%si, %si
	movw	%si, %ds	/* DS = 0 */
	cmpl	$0xC0000000, %eax
	jb	1f
2:
	movw	$ABS_START(bios_interrupt_vector_table + 0x1DC), %di
	stosl			/* save new int 77 */
1:
#endif
	movw	$0x810, %si	/* another saved int 19 */
	lodsl
	movw	$ABS_START(bios_interrupt_vector_table + 0x0064), %di
	stosl

	movw	$0x170, %si	/* int 5C */
	lodsl
	cmpl	$0xC0000000, %eax
	jnb	1f
	ldsw	-4(%si), %si	/* DS changed! */
	cld
	lodsb
	cmpb	$0xEA, %al	/* 0xEA=opcode for jmp far */
	jne	1f
	lodsl
	movw	$ABS_START(bios_interrupt_vector_table + 0x170), %di
	stosl			/* save new int 5C */
1:
	xorw	%si, %si	/* CF=0 */
	movw	%si, %ds	/* DS = 0 */

	//clc			/* CF already cleared */
	ret

failed_check_msdos7plus:
//	/* check MS-DOS 5.0+ */
//	
//	xorw	%ax, %ax
//	movw	%ax, %ds
//
//	movw	$0x0800, %si
//	cld
//	lodsb
//	cmpb	$0x10, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x13, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0x98000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x15, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x19, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x1b, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//
//	movw	$0x0d41, %si
//	cld
//	lodsb
//	cmpb	$0x02, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x08, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x09, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x0a, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x0b, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x0c, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x0d, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x0e, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x70, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x72, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x73, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x74, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	cld
//	lodsb
//	cmpb	$0x76, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jnb	1f
//	addw	$0x000d, %ax
//	movw	%ax, %si
//	shrl	$0x10, %eax
//	movw	%ax, %ds
//	lodsw
//	movw	%ax, %si
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//	xorw	%ax, %ax
//	movw	%ax, %ds
//	movw	$0x0d82, %si
//1:
//	cld
//	lodsb
//	cmpb	$0x77, %al
//	jnz	failed_check_msdos5plus
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	failed_check_msdos5plus
//
//	call	restore_BDA_EBDA
//	
//	cli
//	xorw	%ax, %ax
//	movw	%ax, %es
//	movw	%ax, %ds
//
//	movw	$0x0800, %si
//	cld
//	lodsb
//	movw	$0x0040, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x004c, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x0054, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x0064, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x006c, %di
//	cld
//	lodsl
//	stosl
//
//	movw	$0x0d41, %si
//	cld
//	lodsb
//	movw	$0x0008, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x0020, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x0024, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x0028, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x002c, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x0030, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x0034, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x0038, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x01c0, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x01c8, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x01cc, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x01d0, %di
//	cld
//	lodsl
//	stosl
//	cld
//	lodsb
//	movw	$0x01d8, %di
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jnb	1f
//	addw	$0x000d, %ax
//	movw	%ax, %si
//	shrl	$0x10, %eax
//	movw	%ax, %ds
//	lodsw
//	movw	%ax, %si
//	lodsl
//1:
//	stosl
//	xorw	%ax, %ax
//	movw	%ax, %ds
//	movw	$0x0d82, %si
//	cld
//	lodsb
//	movw	$0x01dc, %di
//	cld
//	lodsl
//	stosl
//
//	jmp	move_stage2_image
//
//check_msdos4minus:
//	/* check MS-DOS 4.0- */
//	
//	xorw	%ax, %ax
//	movw	%ax, %ds
//
//	movw	%bx, %si	/* int 19 */
//	cld
//	lodsl
//	cmpl	$0xc0000000, %eax
//	jb	1f
//	cld
//	lodsb
//	cmpb	$0x01, %al  /* the byte 01 followed by int 02, ... */
//	jnz	1f
//	
//		/* int 02,08-0e,70,72-74,76-77 */
//	movw	$0x000e, %cx /* 14 vectors to check */
//	call	check_a_range_of_ROM_vectors
//	jc	1f
//
//	pushw	%bx
//	call	restore_BDA_EBDA
//	popw	%bx
//	
//	cli
//	cld
//	xorw	%ax, %ax
//	movw	%ax, %es
//	movw	%ax, %ds
//	movw	%bx, %si	/* int 19 */
//	movw	$0x0064, %di
//	lodsl
//	stosl
//	lodsb			/* the byte "01" */
//	movw	$0x0008, %di	/* int 02 */
//	lodsl
//	stosl
//	movw	$0x0020, %di	/* int 08 to 0f */
//	movw	$0x000e, %cx	/* 14 words to move */
//	repz movsw
//	movw	$0x01c0, %di	/* int 70 */
//	lodsl
//	stosl
//	movw	$0x01c8, %di	/* int 72 */
//	lodsl
//	stosl
//	lodsl			/* int 73 */
//	stosl
//	lodsl			/* int 74 */
//	stosl
//	movw	$0x01d8, %di	/* int 76 */
//	lodsl
//	stosl
//	lodsl			/* int 77 */
//	stosl
//
//	clc
//	ret
//1:
//	stc	/* failed_check_msdos4minus */
//	ret
//
//failed_check_msdos5plus:
//	/* check for MS-DOS 4.01 */
//	
//	movw	$0x240e, %bx
//	call	check_msdos4minus
//	jc	failed_check_msdos4
//
//	jmp	move_stage2_image
//
//failed_check_msdos4:
//	/* check for MS-DOS 3.30 */
//	
//	movw	$0x2172, %bx
//	call	check_msdos4minus
//	jc	failed_check_msdos3
//
//	jmp	move_stage2_image
//
//failed_check_msdos3:

	/* check FreeDOS (build 2029+) */
	
	/*
	 * MS himem.sys takes over int 15, so check for the case.
	 */
	
	xorw	%ax, %ax
	movw	%ax, %es
	movw	%ax, %ds
	movw	$0x0054, %di
	movl	(%di), %eax		/* int 15 vector in table */
	cmpl	$0xC0000000, %eax	/* is it a valid BIOS vector? */
	jnb	1f			/* yes, do nothing */
	movw	$0x3086, %si		/* no, take one from himem */
	movl	(%si), %eax
	cmpl	$0xC0000000, %eax	/* is it a system BIOS vector? */
	jb	failed_check_freedos	/* no, do not continue */
1:					/* yes, continue */
	xorw	%ax, %ax
	movw	%ax, %ds
	movw	$0x0020, %si		/* DS:SI points to int 08 */
	lodsl
	movl	%eax, %ebx
	movl	%eax, %edx
	movw	$7, %cx
1:
	lodsl
	addw	$6, %bx
	jc	failed_check_freedos
	cmpl	%eax, %ebx
	jnz	failed_check_freedos
	loop	1b
	
	movw	$0x1C0, %si		/* DS:SI points to int 70 */
	movw	$8, %cx
1:
	lodsl
	addw	$6, %bx
	jc	failed_check_freedos
	cmpl	%eax, %ebx
	jnz	failed_check_freedos
	loop	1b
	
	movw	%dx, %si
	shrl	$16, %edx
	movw	%dx, %ds	/* DS:SI points to int 08 routine */

	movw	$16, %cx
	xorw	%bx, %bx
	xorw	%dx, %dx
1:
	lodsw
	cmpw	$0xBB53, %ax	/* 0x53="pushw %bx",0xBB="movw $(...), %bx" */
	jnz	failed_check_freedos
	lodsw
	cmpw	%ax, %bx
	jnz	failed_check_freedos
	addw	$4, %bx
	cmpw	$1, %cx
	jz	2f
	lodsb
	cmpb	$0xEB, %al	/* 0xEB="jmp ..." */
	jnz	failed_check_freedos
	lodsb
	orw	%dx, %dx
	jnz	3f
	movw	%si, %dx
	xorb	%ah, %ah
	addw	%ax, %dx
	jc	failed_check_freedos
	jmp	2f
3:
	xorb	%ah, %ah
	addw	%si, %ax
	jc	failed_check_freedos
	cmpw	%ax, %dx
	jnz	failed_check_freedos
2:
	loop	1b

	addw	$0x0025, %si
	lodsb
	cmpb	$0x9C, %al	/* 0x9C="pushfw" */
	jnz	failed_check_freedos
	lodsw
	cmpw	$0x9FFF, %ax	/* 0x9FFF="call far [bx+????]" */
	jnz	failed_check_freedos
	lodsw
	/*xorl	%esi, %esi*/
	movw	%ax, %si	/* DS:SI begins old int 08-0F,70-77 vectors */
	movw	%ds, %ax
	orb	%ah, %ah
	jnz	failed_check_freedos
	shlw	$4, %ax
	addw	%ax, %si	/* 0000:SI begins the above int08-77vectors */
	jc	failed_check_freedos
	
	
	xorw	%ax, %ax
	movw	%ax, %ds
	/*movw	$0x08a4, %si*/	/* int 08-0f,70-77 begins here */
	movw	%si, %di	/* save SI into DI */
	cld
	lodsl			/* int 08 */
	cmpl	$0xC0000000, %eax	/* is it a valid BIOS vector? */
	jb	failed_check_freedos
	lodsl			/* int 09 */
	cmpl	$0xC0000000, %eax	/* is it a valid BIOS vector? */
	jb	failed_check_freedos
	lodsl			/* int 0A */
	lodsl			/* int 0B */
	lodsl			/* int 0C */
	lodsl			/* int 0D */
	lodsl			/* int 0E */
	lodsl			/* int 0F */
	lodsl			/* int 70 */
	cmpl	$0xC0000000, %eax	/* is it a valid BIOS vector? */
	jb	failed_check_freedos
	lodsl			/* int 71 */
	cmpl	$0xC0000000, %eax	/* is it a valid BIOS vector? */
	jb	failed_check_freedos
	lodsl			/* int 72 */
	lodsl			/* int 73 */
	lodsl			/* int 74 */
	lodsl			/* int 75 */
	cmpl	$0xC0000000, %eax	/* is it a valid BIOS vector? */
	jb	failed_check_freedos
	lodsl			/* int 76 */
	lodsl			/* int 77 */

	/* yes, it is FreeMS */

	movw	%di, %si	/* restore SI from DI */
	xorw	%ax, %ax
	movw	%ax, %ds		/* DS=0 */
	/*movw	$0x08a4, %si*/
	movw	%cs, %ax
	movw	%ax, %es		/* ES=CS */
	movw	$ABS_START(bios_interrupt_vector_table + 0x20), %di
	movw	$0x0008, %cx	/* int 08 to 0F */
	cld
	repz movsl
	movw	$ABS_START(bios_interrupt_vector_table + 0x1C0), %di
	movw	$0x0008, %cx	/* int 70 to 77 */
	cld
	repz movsl
	
	/*
	 * MS himem.sys takes over int 15, so try to restore it
	 */
	
	movw	$0x0054, %di
	movl	(%di), %eax		/* int 15 vector in table */
	cmpl	$0xC0000000, %eax	/* is it a valid BIOS vector? */
	jnb	1f			/* yes, do nothing */
	movw	$0x3086, %si		/* no, take one from himem */
	movl	(%si), %eax
	cmpl	$0xC0000000, %eax	/* is it a system BIOS vector? */
	jb	1f			/* no, do nothing */
	addw	$ABS_START(bios_interrupt_vector_table), %di
	stosl				/* yes, write it to the table */
1:
	clc
	ret

failed_check_freedos:

	/* check DOSbox */
	
	xorw	%ax, %ax
	movw	%ax, %ds
	movw	$0x0020, %si	/* int 08-1f */
	movw	$0x0018, %cx /* 24 vectors to check */
	call	check_a_range_of_ROM_vectors
	//jc	failed_check_dosbox

	/* yes, it is DOSbox */
	
	//clc
	ret

check_a_range_of_ROM_vectors:
1:
	cld
	lodsl
	cmpl	$0xC0000000, %eax	/* ROM vectors assumed to be above C000:0 */
	jb	1f			/* check failed, with carry */
	loop	1b
					/* check passed, with no carry */
1:
	ret

//failed_check_dosbox:
//	movw	%cs, %ax
//	movw	%ax, %ds
//	movw	%ax, %es
//	movl	$ABS_START(dos_unsupport_string), ABS_PSP(error_message)
//	jmp	message_exit1

#else	/* ! BAD_BIOS */
	/* Note for people who are tracing/debugging this program:
	 * PROBE_INT will take over int01, so probably you don't want
	 * to trace into PROBE_INT.
	 *
	 * int 00 - 07, 10 will be replaced and restored in RESTORE_VECTOR.
	 */

	/* probe critical interrupt vectors established by ROM BIOS. */

	/* find a dummy default vector that simply do an `iret' */

	/* first, search the Interrupt Vector Table for a dummy vector */
	xorw	%ax, %ax
	movw	%ax, %ds		/* DS=0 */
	movw	%ax, %si
	movw	$256, %cx
1:
	cld
	lodsl
	cmpl	$0xC0000000, %eax
	jb	2f			/* failure, try next vector */

	movw	%ax, %di
	shrl	$16, %eax
	movw	%ax, %es
	cmpb	$0xCF, %es:(%di)	/* 0xCF=IRET */
	je	3f
2:
	loop	1b

	/* not found, try a further probe in ROM segment F000:0000 */

	movw	$0xF000, %ax
	movw	%ax, %es		/* ES=0xF000 */
	movw	$0xFFFF, %cx
	movb	$0xCF, %al		/* 0xCF=IRET */
	movw	$0xFFFF, %di		/* top-down */
	std
	repnz scasb
	cld
	movw	$0xFFFE, %cx
	stc
	jnz	9f
	incw	%di

3:
	/* found, ES:DI points to IRET */
	movw	%di, %cs:ABS_START(dummy_iret_vector)
	movw	%es, %cs:ABS_START(dummy_iret_vector + 2)

	/* copy 1 sector of IVT to bios_interrupt_vector_table */
	movw	%cs, %ax
	movw	%ax, %es		/* ES=CS */
	movw	$ABS_START(bios_interrupt_vector_table), %di
	xorw	%si, %si		/* DS:SI=0000:0000 */
	movw	$0x80, %cx
2:
	cld
	lodsl
	cmpl	$0, %es:(%di)
	jne	1f
	stosl
	subw	$4, %di
1:
	addw	$4, %di
	loop	2b

	/* ES=CS, DS=0 */

	/* save the current int 00 - 1F vectors */
	xorw	%si, %si		/* DS:SI=0000:0000 */
	movw	$ABS_START(orig_int_00_1F_vectors), %di
	movw	$32, %cx
	repz movsl

	movw	%cs, %ax
	movw	%ax, %ds		/* DS=ES=CS */

	/* Print a message before it could hang. */
	movw	$ABS_START(probe_int_hang_string), %si
	call	prtstr

//	/* check the int 13 vector high word */
//	cmpw	$0xC000, ABS_START(bios_interrupt_vector_table) + 0x4E
//	jb	2f
//
//	cmpw	$0xF000, ABS_START(bios_interrupt_vector_table) + 0x4E
//	jna	3f	/* int 13 points to ROM */
//2:
//	/* int 13 service routine was not in ROM */
//	/* clear tmp_int13_vector and tmp_int15_vector */
////	xorl	%eax, %eax		/* marked out in 2008-05-07 */
////	movl	%eax, ABS_START(tmp_int13_vector)
////	movl	%eax, ABS_START(tmp_int15_vector)
//3:
//	/* check the int 15 vector high word */
//	cmpw	$0xC000, ABS_START(bios_interrupt_vector_table) + 0x56
//	jb	2f
//
//	cmpw	$0xF000, ABS_START(bios_interrupt_vector_table) + 0x56
//	jna	3f	/* int 15 points to ROM */
//2:
//	/* int 15 service routine was not in ROM */
//	/* clear tmp_int15_vector */
////	xorl	%eax, %eax		/* marked out in 2008-05-07 */
////	movl	%eax, ABS_START(tmp_int15_vector)
//3:

	movw	$ABS_START(bios_interrupt_vector_table), %si
	movw	%si, %di
	xorw	%cx, %cx
1:	
	//cmpw	$0x15, %cx
	//je	2f
	call	print_cl

	cld
	lodsl
	testl	%eax, %eax		/* zero vector? */
	jz	2f			/* yes. won't touch */
	cmpl	$0xF000FFFF, %eax	/* modified by protected-mode OS? */
	ja	8f			/* yes. */
	cmpl	$0xC0000000, %eax	/* ROM vector? */
	jb	8f			/* no. */

	/* it is in the ROM range. */
	/* if in real mode, then it is ROM vector. */

	pushw	%ax
	smsw	%ax
	testb	$1, %al
	popw	%ax
	jz	2f		/* Real mode, ROM vector, won't touch. */

	/* Now we are in VM86 mode. */

	/* if it points to an ARPL, we suppose it is running in Windows 9x */

	pushw	%ds
	pushw	%si
	ldsw	-4(%si), %si
	cmpb	$0x63, (%si)	/* 0x63=arpl */
	popw	%si
	popw	%ds
	jne	5f

	/* We are running in Windows 9x */

	/* We know MS-DOS will backup int 13 and int 4B in memory areas
	 * starting at 0000:0800 and 0000:0540
	 */

	/* if it is not MS-DOS, let it fail. */
	pushw	%ds
	pushw	%ax
	xorw	%ax, %ax
	movw	%ax, %ds
	movw	0x803, %ax		/* int 10 segment */
	cmpw	$0xC000, %ax
	jb	6f
	movw	0x808, %ax		/* int 13 segment */
	cmpw	$0xC000, %ax
	jb	6f
	movw	0x80D, %ax		/* int 15 segment */
	cmpw	$0xC000, %ax
	jb	6f
	movw	0x812, %ax		/* int 19 segment */
	cmpw	$0xC000, %ax
	jb	6f
	movw	0x817, %ax		/* int 1B segment */
	cmpw	$0xC000, %ax
	jb	6f
	movw	0x81C, %ax		/* int 4F segment */
	cmpw	$0xC000, %ax
	jb	6f
	movw	0x821, %ax		/* int 08 segment */
	cmpw	$0xC000, %ax
	jb	6f
	movw	0x826, %ax		/* int 0F segment */
	cmpw	$0xC000, %ax
	jb	6f
	movw	0x82B, %ax		/* int 16 segment */
	cmpw	$0xC000, %ax
	jb	6f
	movb	0x800, %al		/* should be 0x10 */
	cmpb	$0x10, %al
	jne	6f
	movb	0x805, %al		/* should be 0x13 */
	cmpb	$0x13, %al
	jne	6f
	movb	0x80A, %al		/* should be 0x15 */
	cmpb	$0x15, %al
	jne	6f
	movb	0x80F, %al		/* should be 0x19 */
	cmpb	$0x19, %al
	jne	6f
	movb	0x814, %al		/* should be 0x1B */
	cmpb	$0x1B, %al
	jne	6f
	movb	0x819, %al		/* should be 0x4F */
	cmpb	$0x4F, %al
	jne	6f
	movb	0x81E, %al		/* should be 0x08 */
	cmpb	$0x08, %al
	jne	6f
	movb	0x823, %al		/* should be 0x0F */
	cmpb	$0x0F, %al
	jne	6f
	movb	0x828, %al		/* should be 0x16 */
	cmpb	$0x16, %al
	jne	6f
	movl	0x5D6, %eax		/* int 4B segment */
	cmpw	$0xC000, %ax
	jb	6f
	movl	0x5D8, %eax		/* int 4F */
	cmpl	0x81A, %eax		/* int 4F */
	//jne	6f
6:
	popw	%ax
	popw	%ds
	jne	9f			/* it is not MS-DOS. Failure. */

	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x4C, %di	/* int 13 */
	jne	7f
	movl	0x806, %eax
	jmp	2f
7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x12C, %di	/* int 4B */
	jne	9f		/* failure */
	movl	0x5D4, %eax
	jmp	2f
5:
	/* now in VM86 mode(EMM386). check if the ROM routine is writable. */

	pushl	%eax
	pushw	%ds
	pushw	%si
	movw	%ax, %si
	shrl	$16, %eax
	movw	%ax, %ds
	movw	(%si), %ax	/* save original word at CS:IP to AX. */
	notw	(%si)		/* toggle each bit. */
	cmpw	(%si), %ax	/* is it changed? */
	notw	(%si)		/* toggle back. The NOT won't change flags. */
	popw	%si
	popw	%ds
	popl	%eax
	je	2f		/* equal, so it is in ROM and won't touch. */

8:
	/* if it points to an IRET, set it to dummy iret */
	pushw	%ds
	pushw	%si
	ldsw	-4(%si), %si
	cmpb	$0xCF, (%si)	/* 0xCF=iret */
	popw	%si
	popw	%ds
	je	3f

	/* if it points to beyond the low mem, we accept it. */
	cmpl	$0xC0000000, %eax
	jnb	8f
	cmpl	$0x5A000000, %eax
	jb	8f
	pushw	%ds
	pushw	%bx
	pushw	%cx
	xorw	%bx, %bx
	movw	%bx, %ds	/* DS=0 */
	movw	0x413, %bx	/* low mem size in KB */
	shlw	$6, %bx		/* low mem size in paragraphs */
	pushl	%eax		/* the vector */
	popw	%cx
	popw	%cx		/* segment value of the vector */
	cmpw	%bx, %cx
	popw	%cx
	popw	%bx
	popw	%ds
	jnb	2f
8:
	/* set int 00, 01, 03, 04, 07 to dummy */
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x08, %di
	jb	3f							/* int 00, 01 */
	ja	8f

	/* int 02 External hardware - NON-MASKABLE INTERRUPT */

	/* Desc: Generated by the CPU when the input to the NMI pin is asserted. */

	/* Notes: Return address points to start of interrupted instruction on
	 * 80286+. On the 80286+, further NMIs are disabled until the next IRET
	 * instruction, but one additional NMI is remembered by the hardware
	 * and will be serviced after the IRET instruction reenables NMIs.
	 * Maskable interrupts may interrupt the NMI handler if interrupts are
	 * enabled. Although the Intel documentation states that this interrupt
	 * is typically used for power-failure procedures, it has many other
	 * uses on IBM-compatible machines: Memory parity error, Coprocessor
	 * interrupt, Keyboard interrupt, I/O channel check, Disk-controller
	 * power-on request, System suspend, Real-time clock, System watch-dog
	 * timer time-out interrupt, DMA timer time-out interrupt, Low battery,
	 * Module pulled.
	 */

	#; jmp	4f		/* qemu sets this to dummy. */
	call	restore_vector

	/* if failure, we set it to dummy */
	jc	3f	//jc	9f

	jmp	2f
8:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x0C, %di	/* int 03 */
	je	3f
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x10, %di	/* int 04 */
	je	3f
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x14, %di	/* int 05 */
	jne	8f
//	je	3f

	/* qemu sets this to dummy. */

	call	restore_vector
	jc	3f
	jmp	2f
8:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x18, %di	/* int 06 */
	jne	8f
#if 0
	/* FreeDOS takes over int06, so we couldn't probe it. Set it to dummy. */
	jmp	3f
#else
	#; jmp	6f		/* qemu sets this to dummy. */
	call	restore_vector

	/* if failure, we set it to dummy */
	jc	3f	//jc	9f

	jmp	2f
#endif
8:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x1C, %di	/* int 07 */
	je	3f
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x20, %di	/* int 08-0f hardware IRQs */
	jb	7f
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x40, %di
	jnb	7f
	call	restore_vector
	jnc	2f
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x30, %di	/* int 0C */
	je	3f	
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x34, %di	/* int 0D */
	je	3f	
	jmp	9f
7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x1C0, %di	/* int 70-77 hardware IRQs */
	jb	7f
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x1E0, %di
	jnb	7f
	call	restore_vector
	jc	9f
	jmp	2f
7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x40, %di	/* int 10, VIDEO */
	jne	7f

	/* teletype output a space char */
	movw	$0x0E20, %ax
	xorw	%bx, %bx
	call	restore_vector
	jc	9f
	jmp	2f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x44, %di	/* int 11, GET EQUIPMENT LIST */
	jne	7f
	call	restore_vector
	jc	9f
	jmp	2f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x48, %di	/* int 12, GET MEMORY SIZE */
	jne	7f
	call	restore_vector
	jc	9f
	jmp	2f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x4C, %di	/* int 13, DISK */
	jne	7f

	/* If we track it by reading a sector, we could track into protected
	 * mode or into int15/ah=87h for a RAM disk. So we only check the
	 * status of the drives.
	 */

	/* GET STATUS OF LAST OPERATION */

	movb	$0, %dl		/* try each drive 00 - FF */
8:
	movb	$1, %ah
	call	restore_vector
	jnc	2f

	/* try next floppy */
	incb	%dl		/* INC won't touch CF */
	jnz	8b

	jmp	9f		/* CF=1 */

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x50, %di	/* int 14, SERIAL */
	jne	7f

	/* GET PORT STATUS */
	movw	$0x0300, %ax
	movw	$0, %dx		/* port number */
	call	restore_vector
	jc	9f
	jmp	2f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x54, %di	/* int 15, SYSTEM service */
	jne	7f

	/* later PS/2s - GET A20 GATE STATUS */
	movw	$0x2402, %ax
	call	restore_vector
	jnc	2f
	/* BIOS - JOYSTICK SUPPORT (XT after 1982/11/8, AT, XT286, PS) */
	movw	$0x8400, %ax
	movw	$0x0000, %dx	/* subfunction: read joystick switches */
	call	restore_vector
	jnc	2f
	/* SYSTEM - GET CONFIGURATION (XT >1986/1/10, AT mdl 3x9, CONV, XT286, PS) */
	movw	$0xC000, %ax
	call	restore_vector
	jnc	2f
	jmp	9f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x58, %di	/* int 16, KEYBOARD */
	jne	7f

	/* GET KEYBOARD FUNCTIONALITY */
	movw	$0x0900, %ax
	call	restore_vector
	jnc	2f

	/* GET KEYBOARD ID */
	movw	$0x0A00, %ax
	call	restore_vector
	jnc	2f
	jmp	9f		/* CF=1 */

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x5C, %di	/* int 17, PRINTER */
	jne	7f

	/* GET STATUS */
	movw	$0x0200, %ax
	movw	$0, %dx		/* port number */
	call	restore_vector
	jnc	2f
	jmp	9f		/* CF=1 */

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x60, %di	/* int 18, BOOT FAILURE */
	jne	7f

	/* We should not try to call this interrupt! */
	jmp	3f			/* simply set to dummy */

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x64, %di	/* int 19, SYSTEM - BOOTSTRAP LOADER */
	jne	7f

	/* We should not try to call this interrupt! */
	jmp	3f			/* simply set to dummy */

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x68, %di	/* int 1A, TIME and PCI BIOS */
	jne	7f

	/* Tracking into TIMER could hang the system when accessing CMOS! */

	/* PCI BIOS needs too much stack, so do not call it. */

	/* Call it with unknown function. */
	movw	$0xFFFF, %ax
	call	restore_vector
	jnc	2f
	jmp	9f		/* CF=1 */

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x6C, %di	/* int 1B, KEYBOARD - CONTROL-BREAK HANDLER */
	jne	7f

	/* Tracking into int 1B could break GRUB.EXE and return to DOS! */

	/* BIOS sets this to dummy iret */

	jmp	3f			/* simply set to dummy */

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x70, %di	/* int 1C, TIME - SYSTEM TIMER TICK */
	jne	7f

	/* BIOS sets this to dummy iret */

	jmp	3f			/* simply set to dummy */

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x74, %di	/* int 1D, SYSTEM DATA - VIDEO PARAMETER TABLES */
	jne	7f

	/* Notes: The default parameter table is located at F000h:F0A4h
	 * for 100% compatible BIOSes. Under PhysTechSoft's PTS ROM-DOS
	 * this table is fictitious. ---- Ralf Brown's Interrupt List
	 */

	/* QEMU sets this to dummy iret. It is not proper. */

	/* DOS should not change this vector. */

	pushw	%ax
	smsw	%ax
	testb	$1, %al
	popw	%ax
	jz	8f		/* running in real-mode */

	/* running in VM86 mode */
	cmpl	$0xC0000000, %eax
	jnb	2f

8:
	stc
	jmp	9f		/* CF=1 */

	//movl	$0xF000F0A4, %eax
	//jmp	2f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x78, %di	/* int 1E, SYSTEM DATA - DISKETTE PARAMETERS */
	jne	7f

	/* Notes: The default parameter table is located at F000h:EFC7h
	 * for 100% compatible BIOSes.
	 */

	/* QEMU sets this to F000h:EFDFh. It is not proper. */

	/* We can get this vector by calling int13/ah=8h (GET DRIVE PARAMETERS).
	 */

	/* original floppy parameter table */

	#; Do not call int13 if it has not been restored.

	cmpl	$0xC000, ABS_START(bios_interrupt_vector_table) + 0x4E
	jb	2f

	cmpl	$0xF000, ABS_START(bios_interrupt_vector_table) + 0x4E
	ja	2f

	pushw	%cx
	pushw	%ds
	pushw	%si
	pushw	%es
	pushw	%di
	pushl	%eax

	movb	$8, %ah
	movb	$0, %dl
	stc
	#; int	$0x13
	pushfw
	lcall	*ABS_START(bios_interrupt_vector_table) + 0x4C
	jc	8f
	orw	%bx, %ax
	orw	%cx, %ax
	jz	8f
	movw	%es, %ax
	testw	%ax, %ax
	jz	8f
	popl	%eax
	pushw	%es
	pushw	%di
8:
	popl	%eax
	popw	%di
	popw	%es
	popw	%si
	popw	%ds
	popw	%cx
	jmp	2f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x7C, %di	/* int 1F, SYSTEM DATA - 8 x 8 GRAPHICS FONT */
	jne	7f

	/* This vector points at 1024 bytes of graphics data, 8 bytes for
	 * each character 80h-FFh.
	 */

	/* Notes: Graphics data for characters 00h-7Fh stored at F000h:FA6Eh
	 * in 100% compatible BIOSes. Under PhysTechSoft's PTS ROM-DOS this
	 * table is fictitious.    ---- Ralf Brown's Interrupt List 
	 */

	/* System VGA BIOS sets to 0:0, Video Card usually sets to C000:xxxx */

	/* We can get this vector by calling int10/ax=1130h/bh=04h
	 * (GET FONT INFORMATION).
	 */

	/* get original font */

	#; Do not call int10 if it has not been restored.

	cmpl	$0xC000, ABS_START(bios_interrupt_vector_table) + 0x42
	jb	2f

	cmpl	$0xF000, ABS_START(bios_interrupt_vector_table) + 0x42
	ja	2f

	pushw	%cx
	pushw	%ds
	pushw	%si
	pushw	%es
	pushw	%di
	pushl	%eax

	movw	$0x1130, %ax
	movb	$4, %bh
	#; int	$0x10
	pushfw
	lcall	*ABS_START(bios_interrupt_vector_table) + 0x40
	movw	%es, %ax
	cmpw	$0xC000, %ax
	jb	8f
	popl	%eax
	pushw	%es
	pushw	%bp
8:
	popl	%eax
	popw	%di
	popw	%es
	popw	%si
	popw	%ds
	popw	%cx
	jmp	2f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x100, %di	/* int 40, original ROM BIOS DISKETTE HANDLER */
	jne	7f

	/* This is ROM BIOS diskette handler relocated by hard disk BIOS. */

	/* GET STATUS OF LAST OPERATION */

	movb	$0, %dl
8:
	movb	$1, %ah
	call	restore_vector
	jnc	2f
	incb	%dl
	cmpb	$2, %dl
	jnz	8b
	stc
	jmp	9f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0xC0, %di	/* int 30 */
	jne	7f

	/* It seems BIOS set this interrupt to dummy iret. */
	jmp	3f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x104, %di	/* int 41, SYSTEM DATA - HARD DISK 0 */
	jne	7f

	/* SYSTEM DATA(NOT A VECTOR!) - HARD DISK 0 PARAMETER TABLE ADDRESS */

	/* DOS should not change this vector. */

	/* It is hard to retrieve this vector. Hopefully int13/ah=09h never be called. */
	jmp	2f
7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x118, %di	/* int 46, SYSTEM DATA - HARD DISK 1 */
	jne	7f

	/* SYSTEM DATA(NOT A VECTOR!) - HARD DISK 1 PARAMETER TABLE ADDRESS */

	/* DOS should not change this vector. */

	/* It is hard to retrieve this vector. Hopefully int13/ah=09h never be called. */
	jmp	2f
7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x108, %di	/* int 42, RELOCATED INT 10 VIDEO SERVICES */
	jne	7f

	/* Desc: Contains the address of the original INT 10 handler which
	 * an EGA+ video adapter replaces with its own on-board BIOS code.
	 */

	/* DOS should not change this vector. */

	pushw	%ax
	smsw	%ax
	testb	$1, %al
	popw	%ax
	jz	8f		/* running in real-mode */

	/* running in VM86 mode */
	cmpl	$0xC0000000, %eax
	jnb	2f

8:
	stc
	jmp	9f

	/* The vector is generally not used any longer. */
	//jmp	2f
7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x10C, %di	/* int 43, VIDEO DATA - CHARACTER TABLE */
	jne	7f

	/* VIDEO DATA(NOT A VECTOR!) - Points at graphics data for characters
	 * 00h-7Fh of the current font in 8 x 8 dot modes, graphics data for
	 * all characters in 8 x 14 and 8 x 16 modes.
	 */

	/* We can get this vector by calling int10/ax=1130h/bh=03h
	 * (GET FONT INFORMATION).
	 */

	/* get original font */

	#; Do not call int10 if it has not been restored.

	cmpl	$0xC000, ABS_START(bios_interrupt_vector_table) + 0x42
	jb	2f

	cmpl	$0xF000, ABS_START(bios_interrupt_vector_table) + 0x42
	ja	2f

	pushw	%cx
	pushw	%ds
	pushw	%si
	pushw	%es
	pushw	%di
	pushl	%eax

	movw	$0x1130, %ax
	movb	$3, %bh
	#; int	$0x10
	pushfw
	lcall	*ABS_START(bios_interrupt_vector_table) + 0x40
	movw	%es, %ax
	cmpw	$0xC000, %ax
	jb	8f
	popl	%eax
	pushw	%es
	pushw	%bp
8:
	popl	%eax
	popw	%di
	popw	%es
	popw	%si
	popw	%ds
	popw	%cx
	jmp	2f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x110, %di	/* int 44, undocumented */
	jne	7f

	/* VIDEO DATA - ROM BIOS CHARACTER FONT, CHARACTERS 00h-7Fh (PCjr)
	 * This vector points at graphics data for current character font.
	 * 			   ---- Ralf Brown's Interrupt List
	 */

	/* Ralf Brown's Interrupt List seems wrong for this interrupt.
	 * And it seems BIOS set this interrupt to dummy iret.
	 */

	/* DOS should not change this vector. */

	pushw	%ax
	smsw	%ax
	testb	$1, %al
	popw	%ax
	jz	8f		/* running in real-mode */

	/* running in VM86 mode */
	cmpl	$0xC0000000, %eax
	jnb	2f

8:
	stc
	jmp	9f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x114, %di	/* int 45, undocumented */
	jne	7f

	/* It seems BIOS set this interrupt to dummy iret. */

	/* DOS should not change this vector. */

	pushw	%ax
	smsw	%ax
	testb	$1, %al
	popw	%ax
	jz	8f		/* running in real-mode */

	/* running in VM86 mode */
	cmpl	$0xC0000000, %eax
	jnb	2f

8:
	stc
	jmp	9f

7:

	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x11C, %di	/* int 47, undocumented */
	jne	7f

	/* It seems BIOS set this interrupt to dummy iret. */

	/* DOS should not change this vector. */

	pushw	%ax
	smsw	%ax
	testb	$1, %al
	popw	%ax
	jz	8f		/* running in real-mode */

	/* running in VM86 mode */
	cmpl	$0xC0000000, %eax
	jnb	2f

8:
	stc
	jmp	9f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x120, %di	/* int 48, undocumented keyboard */
	jne	7f

	/* It seems BIOS set this interrupt to dummy iret. */

	/* DOS should not change this vector. */

	pushw	%ax
	smsw	%ax
	testb	$1, %al
	popw	%ax
	jz	8f		/* running in real-mode */

	/* running in VM86 mode */
	cmpl	$0xC0000000, %eax
	jnb	2f

8:
	stc
	jmp	9f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x124, %di	/* int 49, undocumented */
	jne	7f

	/* SYSTEM DATA - NON-KEYBOARD SCAN-CODE TRANSLATION TABLE (PCjr)
	 * 			   ---- Ralf Brown's Interrupt List
	 */

	/* Ralf Brown's Interrupt List seems wrong for this interrupt.
	 * And it seems BIOS set this interrupt to dummy iret.
	 */

	/* DOS should not change this vector. */

	pushw	%ax
	smsw	%ax
	testb	$1, %al
	popw	%ax
	jz	8f		/* running in real-mode */

	/* running in VM86 mode */
	cmpl	$0xC0000000, %eax
	jnb	2f

8:
	stc
	jmp	9f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x128, %di	/* int 4A, SYSTEM - USER ALARM HANDLER */
	jne	7f

	/* Desc: This interrupt is invoked by the BIOS when a real-time
	 * clock alarm occurs. An application may use it to perform an
	 * action at a predetermined time.
	 *
	 * Note: This interrupt is called from within a hardware
	 * interrupt handler, so all usual precautions against
	 * reentering DOS must be taken.
	 * 			   ---- Ralf Brown's Interrupt List
	 */

	/* It seems BIOS set this interrupt to dummy iret. */

	/* DOS should not change this vector. */

	pushw	%ax
	smsw	%ax
	testb	$1, %al
	popw	%ax
	jz	8f		/* running in real-mode */

	/* running in VM86 mode */
	cmpl	$0xC0000000, %eax
	jnb	2f

8:
	stc
	jmp	9f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x12C, %di	/* int 4B, Virtual DMA Specification (VDS) */
	jne	7f

	#;/* It seems BIOS set this interrupt to dummy iret. */
	#;jmp	3f

	/* Virtual DMA Specification (VDS) - GET VERSION */
	/* Int 4B/AX=8102h/DX=0000h */

	//movw	$0x8102, %ax
	movw	$0xFFFF, %ax		/* use an unknown function call */
	movw	$0, %dx
	call	restore_vector
	jc	9f
	jmp	2f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x130, %di	/* int 4C, undocumented */
	jne	7f

	#;/* It seems BIOS set this interrupt to dummy iret. */
	#;jmp	3f

	movw	$0xFFFF, %ax		/* use an unknown function call */
	call	restore_vector
	//jc	9f
	jc	3f			/* set to dummy on failure */
	jmp	2f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x134, %di	/* int 4D, undocumented */
	jne	7f

	#;/* It seems BIOS set this interrupt to dummy iret. */
	#;jmp	3f

	movw	$0xFFFF, %ax		/* use an unknown function call */
	call	restore_vector
	//jc	9f
	jc	3f			/* set to dummy on failure */
	jmp	2f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x138, %di	/* int 4E, undocumented */
	jne	7f

	#;/* It seems BIOS set this interrupt to dummy iret. */
	#;jmp	3f

	movw	$0xFFFF, %ax		/* use an unknown function call */
	call	restore_vector
	//jc	9f
	jc	3f			/* set to dummy on failure */
	jmp	2f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x13C, %di	/* int 4F, undocumented */
	jne	7f

	#;/* It seems BIOS set this interrupt to dummy iret. */
	#;jmp	3f

	movw	$0xFFFF, %ax		/* use an unknown function call */
	call	restore_vector
	//jc	9f
	jc	3f			/* set to dummy on failure */
	jmp	2f

7:
#if 0
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x170, %di	/* int 5C, NetBIOS INTERFACE */
	jne	7f

	/* Windows revectored this interrupt. */

	/* It seems BIOS set this interrupt to dummy iret. */
	jmp	3f

7:
#endif
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x140, %di	/* int 50 - 5F */
	jb	7f
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x180, %di
	jnb	7f

#if 0
	#;/* It seems BIOS set this interrupt to dummy iret. */
	#;jmp	3f

	movw	$0xFFFF, %ax		/* use an unknown function call */
	call	restore_vector
	jc	9f
	jmp	2f
#else
	/* Windows revectored INT 5C(NetBIOS Interface). */
	/* It seems DOS does not change this vector. */

	/* It seems BIOS set this interrupt to dummy iret. */
	/* It hangs on Haier MX510-28 after : ... 55 56! 57! 58 59 
	 * so we simply set it to dummy */
	jmp	3f
#endif

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x180, %di	/* int 60 - 67 */
	jb	7f
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x1A0, %di
	jnb	7f

	/* It seems BIOS set this interrupt to 0:0. */
	xorl	%eax, %eax
	jmp	2f

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x1B4, %di	/* int 6D, VIDEO BIOS ENTRY POINT */
	jne	7f

	/* DOS should not change this vector. */

	pushw	%ax
	smsw	%ax
	testb	$1, %al
	popw	%ax
	jz	8f		/* running in real-mode */

	/* running in VM86 mode */
	cmpl	$0xC0000000, %eax
	jnb	2f

8:
#if 0
	stc
	jmp	9f
#else
	/* Ignore the error and simply set to dummy */
	jmp	3f
#endif

7:
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x1A0, %di	/* int 68 - 6F */
	jb	7f
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x1C0, %di
	jnb	7f

#if 0
	#;/* It seems BIOS set this interrupt to dummy iret. */
	#;jmp	3f

	movw	$0xFFFF, %ax		/* use an unknown function call */
	call	restore_vector
	jc	3f		//jc	9f
	jmp	2f
#else
	/* It seems DOS does not change this vector. */

	/* It seems BIOS set int 6D to C000:xxxx and set others to dummy. */
	/* For safety we simply set it to dummy */
	jmp	3f
#endif

7:

	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x1E0, %di	/* int 78 - 7F */
	jb	7f
	cmpw	$ABS_START(bios_interrupt_vector_table) + 0x200, %di
	jnb	7f

	/* It seems BIOS set this interrupt to 0:0. */
	xorl	%eax, %eax
	jmp	2f

7:
	/* other vectors won't touch */
	jmp	2f

#; 6:
#;	/* int 06, bad code interrupt. */
#;	/* qemu sets this to dummy, so can we. */

#; 5:
#;	/* int 05 */
#;	/* qemu sets this to dummy, so can we. */

#; 4:
#;	/* int 02 */
#;	/* qemu sets this to dummy, so can we. */

3:
	/* dummy iret vector */
	movl	ABS_START(dummy_iret_vector), %eax
2:
	stosl
	jmp	2f
9:
	testb	%ch, %ch		/* save the first failed vector ... */
	jnz	3f
	movb	%cl, %ch		/* ... in CH */
3:
	addw	$4, %di

	/* print an "!" for failure */

	pushw	%ds
	pushw	%es
	pushal

	xorw	%bx, %bx
	movw	$0x0e21, %ax		/* 0x21 = "!" */
	int	$0x10

	popal
	popw	%es
	popw	%ds


2:
	incb	%cl
	cmpb	$0x80, %cl
	jb	1b

	movb	%ch, %cl
	negb	%ch			/* CF=1 if CH is non-zero */

	ret

probe_int_hang_string:
	.ascii	"\r\nProbing ROM INT vectors. If hang, unload a device driver or TSR and try again.\r\n\0"

restore_vector:
	#; input:
	#;		DI	points to vector in bios_interrupt_vector_table
	#; output:
	#;		CF=0	success, EAX=the restored ROM vector
	#;		CF=1	failure, EAX destroyed.

	/* Note for people who are tracing/debugging this program:
	 * This is where int 00 - 07, 10 will be replaced and restored.
	 * Take care!
	 */

	/* replace int1 handler */
	pushw	%ax
	pushw	%es
	pushw	%di
	xorw	%ax, %ax
	movw	%ax, ABS_START(tmp_vector + 2)	/* clear the segment value */
	movw	%ax, %es			/* ES=0 */
	movw	$4, %di				/* ES:DI=0000:0004 */
	movw	$ABS_START(int1_handler), %ax
	cld
	stosw				/* setup new int1 handler offset */
	movw	%cs, %ax
	stosw				/* setup new int1 handler segment */
	popw	%di
	popw	%es
	popw	%ax

	///* clear tmp_vector */
	//movl	$0, ABS_START(tmp_vector)	#; DS=CS
	movw	%di, ABS_START(tmp_vector)	/* offset set to DI */

	#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
	/* setup our fault recovery handler */

	pushw	%es
	pushw	%di
	pushl	%eax

	xorw	%di, %di
	movw	%di, %es		/* ES:DI=0000:0000 */

	/* set EAX=CS:fault_recovery_handler */
	pushw	%cs
	pushw	$ABS_START(fault_recovery_handler)
	popl	%eax

	/* Catch CPU exceptions 0, 2, 3, 4, 5, 6, 7
	 *	0	Divide
	 *	1	Debug - handled by int1_handler
	 *	2	NMI
	 *	3	Break point
	 *	4	Overflow
	 *	5	Bound
	 *	6	Invalid Instruction
	 *	7	no coprocessor
	 */

	cld
	stosl				/* setup int 00 */
	addw	$4, %di			/*  skip int 01 */
	stosl				/* setup int 02 */
	stosl				/* setup int 03 */
	stosl				/* setup int 04 */
	stosl				/* setup int 05 */
	stosl				/* setup int 06 */
	stosl				/* setup int 07 */
	addw	$(4 * 8), %di		/*  skip int 08 - 0F */
	stosl				/* setup int 10 */

	popl	%eax
	popw	%di
	popw	%es

	/* backup old registers. */

	movw	%ds, %cs:ABS_START(original_registers)
	movw	%es, %cs:ABS_START(original_registers) + 4
	movw	%ss, %cs:ABS_START(original_registers) + 8
	movl	%esp, %cs:ABS_START(original_registers) + 12
	movl	%eax, %cs:ABS_START(original_registers) + 16
	movl	%ebx, %cs:ABS_START(original_registers) + 20
	movl	%ecx, %cs:ABS_START(original_registers) + 24
	movl	%edx, %cs:ABS_START(original_registers) + 28
	movl	%esi, %cs:ABS_START(original_registers) + 32
	movl	%edi, %cs:ABS_START(original_registers) + 36
	movl	%ebp, %cs:ABS_START(original_registers) + 40
	#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

	pushw	%ds
	pushw	%es
	pushaw

	/* additional PUSHF/POPF are required because some BIOS INT service
	 * routines will end with `ret 02' instead of `iret'.
	 * The `ret 02' does not clear TF, while `iret' does.
	 * With additional PUSHF/POPF, the TF can be safely cleared.
	 */

	pushfw		/* additional PUSHF */
	cli		/* added 2008-08-04 */
	pushfw		/* PUSHF here together with LCALL below form an INT */

	/* set the TF flag */
	pushw	%ax
	pushfw
	popw	%ax
	orw	$0x100, %ax
	pushw	%ax
	popfw
	popw	%ax

	lcall	*(%di)	/* PUSHF above together with LCALL here form an INT */

	sti		/* added 2008-08-04 */
	popfw		/* additional POPF */

	/* TF is cleared here automatically */

	popaw
	popw	%es
	popw	%ds

restore_int_00_1F:

	cli

	pushl	$0
	popfl			#; CLD, CLI, Clear TF and many more...

	sti		/* added 2008-08-04 */
	/* restore the original int 00 - 1F vectors */
	pushw	%cs
	popw	%ds		/* DS=CS */
	pushw	%cs
	popw	%es		/* ES=CS */

	pushw	%es
	pushw	%di
	pushw	%si
	pushw	%cx
	movw	$ABS_START(orig_int_00_1F_vectors), %si
	xorw	%di, %di
	movw	%di, %es	/* ES:DI=0000:0000 */
	movw	$32, %cx

	cli		/* added 2008-08-04 */
	cld
	repz movsl
	sti		/* added 2008-08-04 */

	popw	%cx
	popw	%si
	popw	%di
	popw	%es

	/* failure? */
	movl	ABS_START(tmp_vector), %eax
	cmpl	$0x5A000000, %eax	// cmpl	$0xC0000000, %eax

	/* CF=1 for failure. EAX below 0xC0000000 is not a ROM vector.
	 * CF=0 for success. EAX is a ROM vector.
	 */

	ret

/*
 * Check if the next instruction is in ROM, and if this is true, store the
 * entry point to tmp_vector and terminate the tracking.
 *
 */
int1_handler:
	cli			/* so that we won't take up too much stack. */
	pushw	%bp
	movw	%sp, %bp
	pushl	%eax

	/* if we have got the vector, we clear TF flag to end the tracking. */
	cmpl	$0x5A000000, %cs:ABS_START(tmp_vector)	// cmpl	$0xC0000000, %cs:ABS_START(tmp_vector)
	jnb	4f

	movl	2(%bp), %eax	/* CS:IP of the next instruction */
	cmpl	$0xC0000000, %eax
	jnb	2f

	/* if it points to beyond the low mem, we accept it. */
	cmpl	$0x5A000000, %eax
//	jb	3f		/* marked out in 2008-05-07 */
	jb	1f
	pushw	%ds
	pushw	%bx
	pushw	%cx
	xorw	%bx, %bx
	movw	%bx, %ds	/* DS=0 */
	movw	0x413, %bx	/* low mem size in KB */
	shlw	$6, %bx		/* low mem size in paragraphs */
	pushl	%eax		/* the vector */
	popw	%cx
	popw	%cx		/* segment value of the vector */
	cmpw	%bx, %cx
	popw	%cx
	popw	%bx
	popw	%ds
	jnb	5f
	jmp	1f
//3:				/* marked out in 2008-05-07 */
//	/* if int 13 or int 15 */
//
//	cmpl	$ABS_START(bios_interrupt_vector_table + 0x4C), %cs:ABS_START(tmp_vector) // int 13
//	jne	3f
//	cmpl	$0, %cs:ABS_START(tmp_int13_vector)	/* check already done? */
//	jne	1f					/* yes, skip */
//
//	cmpl	$0x5A000000, %eax	// cmpl	$0x9A000000, %eax
//	jb	1f
//
//	movl	$1, %cs:ABS_START(tmp_int13_vector)	/* invalidate it if the first ip is not 0x100 */
//	cmpw	$0x100, %ax
//	jne	1f
//	testl	$0x3F0000, %eax
//	jnz	1f
//
//	/* check our int13 signature "$INT13SFGRUB4DOS" */
//	pushw	%ds
//	pushw	%bx
//	pushw	%cx
//	xorw	%cx, %cx
//	pushl	%eax
//	popw	%bx			/* BX=0x100 */
//	popw	%ds			/* int13 handler segment */
//	cmpl	$0x544E4924, 0x3(%bx)	/* $INT */
//	setnz	%cl
//	orb	%cl, %ch
//	cmpl	$0x46533331, 0x7(%bx)	/* 13SF */
//	setnz	%cl
//	orb	%cl, %ch
//	cmpl	$0x42555247, 0xB(%bx)	/* GRUB */
//	setnz	%cl
//	orb	%cl, %ch
//	cmpl	$0x534F4434, 0xF(%bx)	/* 4DOS */
//	setnz	%cl
//	orb	%cl, %ch
//	testw	%cx, %cx
//	popw	%cx
//	popw	%bx
//	popw	%ds
//	jnz	1f
//
//	/* check if the segment value matches low memsize at 40:13 */
//	pushw	%ds
//	pushw	%bx
//	xorw	%ax, %ax
//	movw	%ax, %ds	/* DS=0 */
//	movw	0x413, %ax	/* AX=mem size in KB */
//	shlw	$6, %ax		/* AX=mem size in paragraphs */
//	movw	%ax, %bx	/* BX=mem size in paragraphs */
//	rorl	$16, %eax	/* EAX hi word=mem size in paragraphs */
//	cmpw	%ax, %bx
//	popw	%bx
//	popw	%ds
//	jne	1f
//
//	/* EAX hi word=AX=mem size in paragraphs */
//
//	/* this was a disk emulation made by an old grub4dos. */
//	movw	$0x100, %ax
//	movl	%eax, %cs:ABS_START(tmp_int13_vector)
//	jmp	1f
//3:
//	cmpl	$ABS_START(bios_interrupt_vector_table + 0x54), %cs:ABS_START(tmp_vector) // int 15
//	jne	1f
//
//	cmpl	$0, %cs:ABS_START(tmp_int15_vector)
//	jne	1f
//
//	cmpl	$1, %cs:ABS_START(tmp_int13_vector)
//	jbe	1f
//
//	rorl    $16, %eax
//	cmpw	%ax, %cs:ABS_START(tmp_int13_vector + 2)
//	jne	1f
//
//	rorl    $16, %eax
//	movl	%eax, %cs:ABS_START(tmp_int15_vector)
//
//	jmp	1f
2:
	/* calculate linear address of CS:IP in EAX */

	pushl	%eax
	pushl	%ebx
	movl	%eax, %ebx
	xorw	%bx, %bx
	shrl	$12, %ebx
	movzwl	%ax, %eax
	addl	%eax, %ebx	/* EBX=linear address */
	cmpl	$0x100000, %ebx	/* is it below 1M? */
	popl	%ebx
	popl	%eax
	jnb	1f		/* not below, so it is not in ROM. */

	/* it is in the ROM range. */
	/* if in real mode, then it is ROM vector. */

	pushw	%ax
	smsw	%ax
	testb	$1, %al
	popw	%ax
	jz	5f		/* in real mode, so it is ROM vector. */

	/* now in VM86 mode. check if the ROM routine at CS:IP is writable. */

	pushl	%eax
	pushw	%ds
	pushw	%si
	movw	%ax, %si
	shrl	$16, %eax
	movw	%ax, %ds
	movw	(%si), %ax	/* save original word at CS:IP to AX. */
	notw	(%si)		/* toggle each bit. */
	cmpw	(%si), %ax	/* is it changed? */
	notw	(%si)		/* toggle back. The NOT won't change flags. */
	popw	%si
	popw	%ds
	popl	%eax
	je	5f		/* equal means read-only */

	/* not equal, so it is writable. */
	call	is_in_umb
	jnc	1f		/* yes, in umb. so it is not a ROM vector. */
5:
	/* This is the entry point in ROM */

	/* It could hang when we call int 02 on some machines, so we end it. */
	/* It could hang when we call int 08 on some machines, so we end it. */
	/* It could hang when we call int 76 on some machines, so we end it. */
	/* It could hang when we call int 05 on some machines, so we end it. */

	/* %cs:ABS_START(tmp_vector) stores DI which points to the current vector */ 

	//pushl	%eax
	//movl	%cs:ABS_START(tmp_vector), %eax
	//popl	%cs:ABS_START(tmp_vector)
	xchgl	%eax, %cs:ABS_START(tmp_vector)

	cmpl	$ABS_START(bios_interrupt_vector_table) + 0x08, %eax
	je	fault_recovery_handler	/* it is int 02, stop now */
	cmpl	$ABS_START(bios_interrupt_vector_table) + 0x20, %eax
	je	fault_recovery_handler	/* it is int 08, stop now */
	cmpl	$ABS_START(bios_interrupt_vector_table) + 0x1D8, %eax
	je	fault_recovery_handler	/* it is int 76, stop now */
	cmpl	$ABS_START(bios_interrupt_vector_table) + 0x14, %eax
	je	fault_recovery_handler	/* it is int 05, stop now */

	/* not int 02, 08, 76, 05 continue */

4:

#if 1
	/* clear the TF flag */
	andb	$0xFE, 7(%bp)

//	/* unhook int1 handler */
//
//	movl	%cs:ABS_START(dummy_iret_vector), %eax
//	pushw	%ds
//	pushw	%si
//	xorw	%si, %si
//	movw	%si, %ds	/* DS:SI=0000:0000 */
//	movl	%eax, 4(%si)
//	popw	%si
//	popw	%ds

#else
	/* we can not go directly to fault_recovery_handler. */
	//pushl	$0		/* Clear TF */
	//popfl
	//jmp	fault_recovery_handler

	/* clear the TF flag */
	andb	$0xFE, 7(%bp)

//	/* unhook int1 handler */
//
//	movl	%cs:ABS_START(dummy_iret_vector), %eax
//	pushw	%ds
//	pushw	%si
//	xorw	%si, %si
//	movw	%si, %ds	/* DS:SI=0000:0000 */
//	movl	%eax, 4(%si)
//	popw	%si
//	popw	%ds

	/* set the CF flag to indicate an error for the int call */
	orb	$0x01, 12(%bp)		/* Note: this should not be 6(%bp) */

	/* set the return address to dummy iret */
	movl	%cs:ABS_START(dummy_iret_vector), %eax
	movl	%eax, 2(%bp)

#endif

1:
	/* restore registers */	
	popl	%eax
	popw	%bp

	iret

is_in_umb:

	pushal
	movw	$ABS_START(umb_array), %si
	movl	%eax, %ebx
	movzwl	%ax, %eax
	shrl	$16, %ebx
	shll	$4, %ebx
	addl	%eax, %ebx
	movw	$8, %cx
1:
	cld
	cs lodsl	/* start segment */
	testw	%ax, %ax
	jz	1f
	movl	%eax, %edx
	movzwl	%ax, %eax
	shll	$4, %eax
	cmpl	%eax, %ebx
	jbe	1f
	shrl	$16, %edx
	shll	$4, %edx
	addl	%edx, %eax
	cmpl	%ebx, %eax
	ja	2f		/* found umb, CF=0 */
	loop	1b
1:
	stc
2:
	popal
	ret
	
	.align	4

umb_array:
	.word	0	/* 1, start segment */
	.word	0	/* 1, length in paragraphs */
	.word	0	/* 2, start segment */
	.word	0	/* 2, length in paragraphs */
	.word	0	/* 3, start segment */
	.word	0	/* 3, length in paragraphs */
	.word	0	/* 4, start segment */
	.word	0	/* 4, length in paragraphs */
	.word	0	/* 5, start segment */
	.word	0	/* 5, length in paragraphs */
	.word	0	/* 6, start segment */
	.word	0	/* 6, length in paragraphs */
	.word	0	/* 7, start segment */
	.word	0	/* 7, length in paragraphs */
	.word	0	/* 8, start segment */
	.word	0	/* 8, length in paragraphs */
	.word	0	/* end array with a null */
	.word	0	/* end array with a null */

#if 0					/* marked out in 2008-05-07 */
tmp_int13_vector:
	.word	0
	.word	0

tmp_int15_vector:
	.word	0
	.word	0
#endif

tmp_vector:
	.word	0
	.word	0

dummy_iret_vector:
	.word	0
	.word	0

orig_int_00_1F_vectors:
	.space	128

original_registers:
	.space	48

fault_recovery_handler:

	/* restore old registers. */
	
	/* stack validated first */

	movw	%cs:ABS_START(original_registers) + 8, %ss
	movl	%cs:ABS_START(original_registers) + 12, %esp

	/* stack is available, so we can push and pop. */

	pushl	$0
	popfl			#; CLD, CLI, Clear TF and many more...

	//cli		/* marked off 2008-08-04 */
	sti		/* added 2008-08-04 */
	movw	%cs:ABS_START(original_registers), %ds
	movw	%cs:ABS_START(original_registers) + 4, %es
	//movw	%cs:ABS_START(original_registers) + 8, %ss
	//movl	%cs:ABS_START(original_registers) + 12, %esp
	movl	%cs:ABS_START(original_registers) + 16, %eax
	movl	%cs:ABS_START(original_registers) + 20, %ebx
	movl	%cs:ABS_START(original_registers) + 24, %ecx
	movl	%cs:ABS_START(original_registers) + 28, %edx
	movl	%cs:ABS_START(original_registers) + 32, %esi
	movl	%cs:ABS_START(original_registers) + 36, %edi
	movl	%cs:ABS_START(original_registers) + 40, %ebp

	pushw	$ABS_START(restore_int_00_1F)	/* return address */
	ret

	/* never come here. */

	iret

print_cl:
	pushw	%ds
	pushw	%es
	pushal

	xchgw	%ax, %cx	# move CL to AL
	xorb	%ah, %ah
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

	pushw	%ax
	movw	$0x0e20, %ax
	int	$0x10
	popw	%ax

	movb	$0x0e, %ah
	int	$0x10

	movb	$0x0e, %ah
	movb	%cl, %al
	int	$0x10

	popal
	popw	%es
	popw	%ds
	ret
#endif	/* ! BAD_BIOS */

	.align	4

	/* 1 sector for the first half of IVT */
bios_interrupt_vector_table:
	.space	0x200

restore_BDA_EBDA:

	/* MS-DOS 7+ moved the EBDA segment from higher address to lower
	 * address, so we need to move it back to the top of conventional
	 * memory.
	 */
	cli
	cld
	xorw	%ax, %ax
	movw	%ax, %ds
	movw	$0x040e, %si	/* points to EBDA segment */
	lodsw
	orw	%ax, %ax	/* is EBDA segment? */
#;	jz	invalid_EBDA	/* no EBDA exists */
	jnz	1f
	/* no EBDA, let EBDA be at A000:0000 */
	movw	$0xA000, %ax
1:

	movw	%ax, %cx	/* CX=EBDA segment */
	movw	$0x0413, %si	/* points to conventional memory size in KB */
	lodsw
	cmpw	$0x0280, %ax	/* 0x280 == 640 */
	ja	invalid_EBDA	/* too much conventional memory */

	shlw	$0x06, %ax
	movw	%ax, %dx	/* conventional memory size in paragraphs */

	xorb	%al, %al
	cmpw	$0xA000, %cx
	jz	1f		#; no EBDA exists

	movw	%cx, %ds	/* DOS currently used EBDA segment */
	xorw	%si, %si	/* the first byte of the EBDA ... */
	lodsb			/* 	...is the EBDA size in KB */
	cmpb	$0x80, %al	/* EBDA size greater than 128K ? */
	ja	invalid_EBDA	/* EBDA too large */

	orb	%al, %al	/* EBDA size is 0 ? */
	jz	invalid_EBDA	/* EBDA should not be 0 in length */
1:
	movw	$0x0280, %bx
	subb	%al, %bl	/* BX is the calculated low mem in K */
	shlw	$0x06, %bx	/* BX is the calculated EBDA segment */
	cmpw	%bx, %cx	/* CX is currently used EBDA segment */
	jb	1f		/* MSDOS had moved EBDA to low, jump */

	/* BX should be equal to CX, so EBDA needn't be restored.
	 *
	 * DX holds the segment at low mem end, so DX should be less
	 * than or equal to BX.
	 */

#if 0	 
	/* restore vectors in the range from DX:0 to BX:0 */ 

	movw	%cs, %ax
	movw	%ax, %es
	movw	$ABS_START(mapped_int13_vector_BIOS), %di
	movw	%dx, %ax	/* AX=currently used low mem in paragraghs */
	stosw			/* the possible hooked int13 segment */

	movw	%bx, %ax	/* AX is the calculated EBDA segment */
	shrw	$6, %ax		/* AX=calculated low mem in K */
	stosw			/* the low mem in K before int13 hook */
				#; after int13 is unhooked, the low mem will
				#; end at EBDA. so any int13 service routine
				#; installed by another software(eg, memdisk)
				#; will be forcibly dismissed!!!!!!
	movw	%di, %bp
	movw	%dx, %es	/* currently used low mem in paragraghs */
	xorw	%di, %di

	/* suppose ES:DI is our int13 handler, we check it. */

	/* the original int13 vector must be stored in the first kilo bytes */

	movw	$0x0400, %cx
	movb	$0x9a, %al	/* 0x9a == lcall */
3:
	repnz scasb
	jcxz	2f		/* our int13 code was not found. */
	cmpl	$0x9a006e8b, %es:-4(%di) /* movw (%bp), %bp; lcall */
	jnz	3b

	/* our int13 found. */
	movw	%di, %si
	movw	%bp, %di
	movw	%es, %ax
	movw	%ax, %ds	/* DS=code segment of int13 service routine */
				#; DS:SI points to original BIOS int13 vector
	movw	%cs, %ax
	movw	%ax, %es	#; ES:DI points to the location to save 
	lodsl
	cmpl	$0x80000000, %eax
	jb	2f
	stosl			/* save the original BIOS int13 vector */
	
2:
#endif
	ret
	
1:
	/* MS-DOS 7+ moved 1K EBDA from 9FC0:0000 to lower mem. In this case,
	 * there shouldn't be any int13 routine at the top of conventional
	 * memory. so we simply copy 1K of EBDA back to 9FC0:0000 and
	 * of course, adjust data at 0000:040e and 0000:0413
	 */

	/* Restore vectors in the range from DX:0 to A000:0 
	 * No vectors need to be restored because DX seems always be 0xA000
	 */

	/* AL = EBDA size in KB */
	/* BX = calculated EBDA segment = 0xA000 - EBDA_size_in_paragraphs */
	/* CX = currently used EBDA segment, and CX < BX */
	/* DX = conventional memory size in paragraphs, usually 0xA000 */

	/* if MS-DOS would have changed EBDA, then CX should be small. */
	cmpw	$0x4000, %cx
	jb	1f
	ret
1:
	movw	%bx, %es	/* ES is the calculated EBDA segment */
	shlw	$9, %ax		/* AX *= 512 */
	movw	%ax, %cx	/* EBDA size in words */
	decw	%ax
	shlw	$1, %ax		/* points to the last word in EBDA */
	movw	%ax, %si	/* DS holds the currently used EBDA segment */
	movw	%ax, %di	/* ES holds the calculated EBDA segment */
	std			/* move higher word first */
	repz movsw		/* move to BIOS EBDA */
	cld
	xorw	%ax, %ax
	movw	%ax, %es	/* DI string operations use ES == 0 */
	movw	%bx, %ax
	movw	$0x040e, %di
	stosw			/* restore the BDA pointer of EBDA segment */
	movw	$0x0413, %di
	shrw	$6, %ax
	stosw			/* restore the BDA field of low mem size */
	ret

invalid_EBDA:
	xorw	%ax, %ax	/* AX == 0 means invalid EBDA segment */
	movw	%ax, %es	/* DI string operations use ES == 0 */
	movw	$0x040e, %di	/* let EBDA segment be invalid */
	stosw			/* store 0 to 0000:040e */
	movw	$0x0413, %di	/* let lower memory size at 0x413 ... */
	movw	$0x0280, %ax	/* 	... be 640K (0x280 == 640) */
	stosw			/* store 640 to 0000:0413 */
	ret

move_stage2_image:

#if 1

	/* The Chinese DOS display systems are in graphics mode and cause
	 * display problem after we enter GRUB environment, so we need to
	 * enter text mode.
	 */
	
	movw	$0x0003, %ax	/* set display mode: 80*25 color text */
	int	$0x10

#endif

	movw	%cs, %ax
	movw	%ax, %ds		/* DS=CS */
	xorw	%ax, %ax
	movw	%ax, %es		/* ES=0 */

	/* move command-line menu from CS:0081 to 0000:0800 */
	movw	$0x0081, %si		/* DS=CS */
	movw	$0x0800, %di		/* ES=0 */
	movw	$0x0400, %cx		/* move 4KB */
	cld
	repz movsl
	stosb				/* end in NULL */

	/* the stack 0000:2000 is safe because this is where the dos kernel
	 * code was living, and dos cannot load grub.exe below 0000:2000.
	 */

	cli			/* added 2008-08-04 */
	xorw	%ax, %ax
	movw	%ax, %ss
	movw	$0x2000, %sp
	sti			/* added 2008-08-04 */

	movw	$ABS_START(stage2_64K_pages), %si
	movw	(%si), %cx

	movw	%cs, %ax
	addw	$(ABS_START(pre_stage2_start-0x200)/0x10), %ax
	movw	%ax, %bx	/* save the final stage2 segment to BX */
	cmpw	$0x0800, %ax
	ja	2f		/* move from higher at BX:0000 to lower at 0800:0000 */

	/* move from lower at BX:0000 to higher at 0800:0000 */
1:
	xorw	%ax, %ax
	movb	%cl, %ah
	decb	%ah
	shlb	$0x04, %ah
	movw	%bx, %dx
	addw	%ax, %dx
	movw	%dx, %ds
	addb	$0x08, %ah	/* addw $0x0800, %ax */
	movw	%ax, %es
	movw	$0xfffe, %si
	movw	%si, %di
	movw	%cx, %dx	/* save %cx to %dx */
	movw	$0x8000, %cx	/* 0x8000 words == 64K bytes */

	/* Can safely move the final sector, because this code is just before
	 * the final sector */
#if 0
	cmpw	$0x0001, %dx	#; do not move the sector containing this code,
				#; to ensure no overlap
	ja	3f
	decb	%ch		/* %cx == 0x7f00 */
3:
#endif
	//cli
	std			/* move begins at higher end */
	repz movsw
	movw	%dx, %cx	/* restore %cx from %dx */
	loop	1b

	// launch_stage2_code is in the final sector, so it may be overwritten
	//jmp	launch_stage2_code
	//

	ljmp	$0x800, $ABS_FINAL(launch_stage2_code)
	
	//. = (DOSSTART_SIZE - 0x0200)

	. = . + (0x400 - (. % 0x200)) % 0x200

//////////////////////////////////////////////////////////////////////////////

	/* The final sector begins here! */

2:
	/* move from higher at BX:0000 to lower at 0800:0000.
	 * Note: this could overwrite our code and stack, so we shouldn't
	 * use stack(remember to cli), and we should copy the final sector
	 * to a safe place(because the code will continue to execute after
	 * the moving).
	 */

	/* first, copy the final sector to 07e0:0000. Use 07e0 other than 0800
	 * to ensure no overlap.
	 */

	/* Now we are at the final sector, and we are above 0800:0000.
	 * So it is safe to move ourselves onto the lower sector at 07e0:0000.
	 */

	xorw	%si, %si
	xorw	%di, %di
	movw	$0x07e0, %ax
	movw	%ax, %es
	movw	%bx, %ds
	movw	%cx, %dx	/* save %cx to %dx */
	movw	$0x0100, %cx	/* move the sector containing this code */
	//cli			/* marked off 2008-08-04 */
	cld
	repz movsw
	movw	%dx, %cx	/* restore %cx from %dx */

	/* Now we should long jump to the new safe code that has just moved,
	 * because the further moving could overwrite the code here at the
	 * final sector.
	 */

	ljmp	$0x07e0, $ABS_FINAL(1f)

1:
	/* from here on, code must be in the FINAL sector */
	movw	$0x0800, %ax
	movw	%ax, %es
	movw	%bx, %ds
1:
	xorw	%si, %si
	xorw	%di, %di
	movw	%cx, %dx	/* save %cx to %dx */
	movw	$0x8000, %cx	/* 0x8000 words == 64K bytes */
	cld
	repz movsw
	movw	%dx, %cx	/* restore %cx from %dx */
	addw	$0x1000, %ax	/* move the next 64K-byte page */
	movw	%ax, %es
	addw	$0x1000, %bx
	movw	%bx, %ds
	loop	1b

launch_stage2_code:

	cld
	xorw	%ax, %ax
	movw	%ax, %ds
	movw	%ax, %es
	cli
	movw	%ax, %ss
	movw	$0x2000, %sp
	sti			/* added 2008-08-04 */
	xchgb	%al, 0x820B	# AL=boot_drive, and clear the byte at 0x820B
	xchgw	%ax, %dx	# DL=boot_drive
	xorl	%ebp, %ebp
	xorl	%esi, %esi

	ljmp	$0, $0x8200
	
	. = 2b + 0x200
#-----------------------------------------------------------------------------
#			EXE code ends here
#-----------------------------------------------------------------------------

	// if not aligned 0x200, issue error

	. = . - (. % 0x200)

pre_stage2_start:

	/* Main program of GNU GRUB(i.e., pre_stage2) immediately follows. */


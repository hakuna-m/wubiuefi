/*
 *  GRUB Utilities --  Utilities for GRUB Legacy, GRUB2 and GRUB for DOS
 *  Copyright (C) 2007,2008 Bean (bean123ch@gmail.com)
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

        .file   "header.S"

#include <symbol.h>

#define CODE_ADDR	0x6000
#define BLCK_LENG	0x4000

	.text

        .code16

data_start:
	movw	%cs, %ax
	cmpw	$0x2000, %ax
	jz	1f

	/* We are not loaded by grldr, clear the partition byte.  */
	movb	$0xFF, %dh
1:
	xorl	%ebp, %ebp
	jmp	linux_next

	. = data_start + 0x1F1

setup_sects:
	.byte	0
root_flags:
	.word	0
syssize:
	.word	0
swap_dev:
	.word	0
ram_size:
	.word	0
vid_mode:
	.word	0
root_dev:
	.word	0
boot_flag:
	.word	0xAA55

start:
_start:

	jmp linux_init

	.ascii	"HdrS"			/* Header signature.  */
	.word	0x0203			/* Header version number.  */

realmode_swtch:
	.word	0, 0			/* default_switch, SETUPSEG.  */
start_sys_seg:
	.word	0x1000			/* Obsolete.  */
version_ptr:
	.word	0			/* Version string ptr.  */
type_of_loader:
	.byte	0			/* Filled in by boot loader.  */
loadflags:
	.byte	1			/* Please load high.  */
setup_move_size:
	.word	0			/* Unused.  */
code32_start:
	.long	0x100000		/* 32-bit start address.  */
ramdisk_image:
	.long	0			/* Loaded ramdisk image address.  */
ramdisk_size:
	.long	0			/* Size of loaded ramdisk.  */
bootsect_kludge:
	.word	0, 0
heap_end_ptr:
	.word	0
pad1:
	.word	0
cmd_line_ptr:
	.long	0			/* Command line.  */
ramdisk_max:
	.long	0xffffffff		/* Highest allowed ramdisk address.  */

gdt:
	.long	0, 0, 0, 0		/* Must be zero.  */
	.word	0xffff			/* 64 K segment size.  */
gdt_src1:
	.byte	0, 0 ,0			/* Low 24 bits of source address.  */
	.byte	0x93			/* Access rights.  */
	.byte	0			/* Extended access rights.  */
gdt_src2:
	.byte	0			/* High 8 bits of source address.  */
	.word	0xffff			/* 64 K segment size.  */
gdt_dst1:
	.byte	0, 0, 0			/* Low 24 bits of target address.  */
	.byte	0x93			/* Access rights.  */
	.byte	0			/* Extended access rights.  */
gdt_dst2:
	.byte	0			/* High 8 bits of source address.  */
	.long	0, 0, 0, 0		/* More space for the BIOS.  */

reg_edx:
	.byte	0x80,0xFF,0xFF,0xFF

data_leng:
	.long	0

linux_init:

	movw	%cs:(reg_edx - start), %dx
	movl	%cs:(code32_start - start), %ebp

linux_next:

	call	normalize

normalize:
	popw	%bx
	subw	$(normalize - start), %bx
	shrw	$4, %bx
	movw	%cs, %ax
	addw	%bx, %ax
	pushw	%ax
	pushw	$(real_code - start)

	/* jump to real_code.  */
	lret

real_code:
	subw	$0x20, %ax
	movw	%ax, %ds
	movw	(setup_sects - data_start), %cx
	shlw	$7, %cx

	/* Setup stack.  */
	xorw	%si, %si
	movw	%si, %ss
	movw	$(CODE_ADDR), %sp

	/* Move itself to 0:CODE_ADDR.  */
	cld
	movw	%cs, %ax
	movw	%ax, %ds
	movw	$(CODE_ADDR >> 4), %ax
	movw	%ax, %es
	movw	%si, %di

	rep
	movsl

	ljmp	$(CODE_ADDR >> 4), $(real_code_2  - start)

real_code_2:

/*
	pushw	%dx

	// Read MBR to 0:0x7C00

	movw	$201, %ax
	xorw	%cx, %cx
	movw	%cx, %es
	incw	%cx
	movw	$0x7C00, %bx
	xorb	%dh, %dh

	int	$0x13

	popw	%dx

	pushw	%ds
	popw	%es
*/

	xchgl	%ebp, %esi
	orl	%esi, %esi
	jnz	1f
	movw	%ds, %si
	shll	$4, %esi
	addl	%ebp, %esi
1:

	pushw	%es
	popw	%ds

	movl	(data_leng - start), %ecx
	or	%ecx, %ecx
	jnz	1f

	movl	(ramdisk_image - start), %esi
	movl	(ramdisk_size - start), %ecx
1:

	jmp	EXT_FUNC(main)

/*
 * Parameters:
 *   esi: source address
 *   edi: target address
 *   ecx: number of bytes
 */
DEF_FUNC(move_memory)
	incl	%ecx
	andb	$0xFE, %cl
	cmpl	%esi, %edi
	ja	1f
	jb	2f
	ret
1:
	addl	%ecx, %esi
	addl	%ecx, %edi

2:

	pushw	%dx
1:
	pushl	%ecx
	cmpl	$BLCK_LENG, %ecx
	jbe	2f
	movl	$BLCK_LENG, %ecx
2:
	pushl	%ecx

	cmpl	%esi, %edi
	jb	3f
	subl	%ecx, %esi
	subl	%ecx, %edi
3:
	pushl	%esi
	pushl	%edi

	movl	%esi, %eax
	movw	%si, (gdt_src1 - start)
	shrl	$16, %eax
	movb	%al, (gdt_src1 + 2 - start)
	movb	%ah, (gdt_src2 - start)

	movl	%edi, %eax
	movw	%di, (gdt_dst1 - start)
	shrl	$16, %eax
	movb	%al, (gdt_dst1 + 2 - start)
	movb	%ah, (gdt_dst2 - start)

	movw	$(gdt - start), %si
	movb	$0x87, %ah
	shrw	$1, %cx

	int	$0x15

	popl	%edi
	popl	%esi
	popl	%eax
	popl	%ecx

	jnc	2f
	movw	$(err_int15_msg - start), %si
	jmp	fail

2:

	cmpl	%esi, %edi
	ja	3f
	addl	%eax, %esi
	addl	%eax, %edi
3:
	subl	%eax, %ecx
	jnz	1b

	popw	%dx
	ret

/*
 * Parameters:
 *   si: message
 */
fail:
	movb	$0x0e, %ah
	xorw	%bx, %bx
1:
	lodsb	(%si), %al
	int	$0x10
	cmpb	$0, %al
	jne	1b
1:	jmp	1b

err_int15_msg:
	.ascii	"move memory fails\0"

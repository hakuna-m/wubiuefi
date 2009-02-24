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

#define CODE_ADDR	0x700
#define CODE_LENG	0x200		// 1 sector
#define DATA_ADDR	0x820

#define BLCK_LENG	0x8000

	.file	"g2hdr.S"

	.text

	.code16

	.globl	start, _start

start:
_start:

	// Move itself to CODE_ADDR:0
	// Don't modify dx

	cld
	movw	%cs, %ax
	movw	%ax, %ds
	movw	$CODE_ADDR, %ax
	movw	%ax, %es
	xorw	%si, %si
	movw	%si, %di
	movw	$(CODE_LENG >> 2), %cx

	rep
	movsl

	ljmp	$0, $(jump_start-start+(CODE_ADDR << 4))

jump_start:
	// Move core.img to 0x820:0

	movw	%ds, %ax
	addw	$((CODE_LENG >> 4)+0x20), %ax
	movw	%ax, %ds
	movw	$(DATA_ADDR), %ax
	movw	%ax, %es
	xorl	%eax, %eax
	movb	%dh, %al
	movl	%eax, 0x14		// GRUB_KERNEL_MACHINE_INSTALL_DOS_PART
	movl	0x10, %eax		// GRUB_KERNEL_MACHINE_COMPRESSED_SIZE
	addl	$0x4A0, %eax		// GRUB_KERNEL_MACHINE_RAW_SIZE
	xorl	%ecx, %ecx

1:
	xorw	%si, %si
	movw	%si, %di

	movw	$(BLCK_LENG), %cx
	cmpl	%ecx, %eax
	jae	2f
	movw	%ax, %cx
2:

	pushw	%cx
	addw	$3, %cx
	shrw	$2, %cx

	rep
	movsl

	popw	%cx

	movw	%ds, %si
	addw	$(BLCK_LENG >> 4), %si
	movw	%si, %ds

	movw	%es, %si
	addw	$(BLCK_LENG >> 4), %si
	movw	%si, %es

	subl	%ecx, %eax
	jnz	1b

	movb	$0xFF, %dh

	ljmp	$0, $(DATA_ADDR << 4)

	. = _start + 0x200 - 2

	.word 0xAA55


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

	.file "romboot.S"

#define DATA_ADDR	0x8200

	.text

	.code16

	.globl  start, _start

start:
_start:

	.word	code_end - start	// It's changed to 0xAA55 in grub-mkrom

image_size:
	.byte	0

	jmp	code_start

checksum:
	.byte	0

hotkey:
	.word	0x3920			// SPACE Key

timeout:
	.word	18 * 2			// in ticks (1/18.2 second)

desc_ofs:
	.byte	desc_start - start

desc_len:
	.byte	desc_end - desc_start

reg_edx:
	.long	0


#ifdef PCI

	. = start + 0x18

	.word	PCIHDR - start		// PCI Header
	.word	PNPHDR - start		// PnP Expansion Header

PCIHDR:
	.ascii	"PCIR"			// Signature
	.word	0			// vendor ID
	.word	0			// device ID
	.word	0			// Pointer to vital product data
	.word	24			// PCI data structure length in bytes
	.byte	0			// PCI data structure revision (0=PCI 2.1)
	.byte	2,0,0			// PCI device class code
	.word	0			// ROM size in 512 byte blocks
	.word	0			// Revision level of code
	.byte	0			// Code type (0=x86 PC-AT)
	.byte	0x80			// Last image indicator
	.word	0			// Reserved

PNPHDR:
	.ascii	"$PnP"			// Signature
	.byte	1			// PnP structure revision
	.byte	2			// PnP structure length in 16 byte blocks
	.word	0			// Offset to next header
	.byte	0			// Reserved
	.byte	0x33			// PnP structure checksum
	.long	0			// Device identifier
	.word	0			// Pointer to manufacturer string
	.word	0			// Pointer to productname string
	.byte	2,0,0			// Device class code
	.byte	0x64			// Device indicators
	.word	0			// Boot connection vector
	.word	0			// Disconnect vector
	.word	0			// Bootstrap entry vector
	.word	0			// Reserved
	.word	0			// Static resource info vector

#endif

desc_start:
	.ascii	"Press SPACE to start BOOTROM ..\0"

	. = desc_start + 32

desc_end:

code_start:
	pushfw
	pushw	%ds
	pushaw

	cld

	pushw	$0
	popw	%ds

	movb	$0x0e, %ah
	xorw	%bx, %bx
	movw	$(desc_start - start), %si

1:
	lodsb	%cs:(%si), %al
	int	$0x10
	cmpb	$0, %al
	jne	1b

	movw	%cs:(timeout - start), %si
	addw	(0x46c), %si

1:

	movb	$0x11, %ah
	int	$0x16
	jnz	1f

	cmpw	(0x46c), %si
	jae	1b

	xorw	%ax, %ax

1:

	cmpw	%cs:(hotkey - start), %ax
	jnz	1f

	movw	$(new_int19 - start),(0x19 * 4)
	movw	%cs, (0x19 * 4 +2)
	jmp	2f

1:
	movw	%ds, %cs:(0)		// ds = 0
2:

1:					// Clear keys
	movb	$1, %ah
	int	$0x16
	jz	1f
	movb	$0, %ah
	int	$0x16
	jmp	1b
1:

	popaw
	popw	%ds
	popfw
	lret

new_int19:

#ifndef LZMA
	pushw	%cs
	popw	%ds
	pushw	$(DATA_ADDR >> 4)
	popw	%es

	movzbw	(image_size - start), %cx
	shlw	$9, %cx
	movw	$(code_end - start), %si
	subw	%si, %cx
	xorw	%di, %di

	cld
	rep	movsb

	movl	(reg_edx - start), %edx

	ljmp	$0, $(DATA_ADDR)

#else

#define CR0_PE_ON		0x1

#define REAL_MODE_STACK		0x8000

#define PROT_MODE_CSEG		0x8
#define PROT_MODE_DSEG		0x10
#define REAL_MODE_DSEG		0x18
#define REAL_MODE_CSEG		0x20

	cli

	xorw	%ax, %ax
	xorw	%cx, %cx
	xorl	%ebp, %ebp
	pushl	%ebp
	pushw	$REAL_MODE_STACK
	popl	%esp			// ss:esp = 0:REAL_MODE_STACK
	popw	%ss

	decw	%bp

	movb	$0x9e, %ah		// 16 bit real mode CS
	pushw	%cx			// .word  0xFFFF, 0
	pushw	%ax			// .byte  0, 0x9E, 0, 0
	pushl	%ebp

	movb	$0x92, %ah
	pushw	%cx			// 16 bit real mode DS
	pushw	%ax			// .word  0xFFFF, 0
	pushl	%ebp			// .byte  0, 0x92, 0, 0

	movb	$0xcf, %cl
	pushw	%cx			// prot mode DS
	pushw	%ax			// .word  0xFFFF, 0
	pushl	%ebp			// .byte  0, 0x92, 0xCF, 0

	movb	$0x9a, %ah
	pushw	%cx			// prot mode CS
	pushw	%ax			// .word  0xFFFF, 0
	pushl	%ebp			// .byte  0, 0x9A, 0xCF, 0

	xorw	%bp, %bp		// dummy
	pushl	%ebp			// .word  0, 0
	pushl	%ebp			// .byte  0, 0, 0,0

	pushl	%esp			// .word  0x27
	pushw	$0x27			// .long  gdt

	movw	%sp, %bp

	lgdt	(%bp)

	movw	%cs, %bp
	shll	$4, %ebp
	addw	$(protcseg - start), %bp

	movl	%cr0, %eax
	orl	$CR0_PE_ON, %eax
	movl	%eax, %cr0

	movw	$PROT_MODE_DSEG, %ax
	movw	%ax, %ds
	movw	%ax, %es

	pushw	$PROT_MODE_CSEG
	pushl	%ebp
	DATA32	lret

	.code32
protcseg:

	leal	code_end - protcseg - (code_end - realcseg)(%ebp), %esi
	movl	$(code_end - realcseg), %ecx
	movl	$(DATA_ADDR - (code_end - realcseg)), %edi

	cld
	rep	movsb

	movl	5(%esi), %ecx
	addl	%edi, %ecx
	pushl	%ecx			// Probs
	subl	$12, %esp		// Properties

	movl	%esp, %eax
	pushl	$5			// LZMA_PROPERTIES_SIZE
	pushl	%esi			// properties
	pushl	%eax			// &state.Properties
	call	_LzmaDecodeProperties
	addl	$(4*3), %esp

	movl	%esp, %edx
	movl	%esi, %eax
	movl	5(%esi), %ecx
	addl	$(5+8), %esi

	pushl	%eax			// &outProcessed
	pushl	%ecx			// outSize
	pushl	%edi			// dest
	pushl	%eax			// &inProcessed
	pushl	$0xFFFFFFFF		// inSize
	pushl	%esi			// source
	pushl	%edx			// &state
	call	_LzmaDecode
	//addl	$(4*7+16), %esp

	movl	%ds:reg_edx - protcseg(%ebp), %edx

	ljmp	$REAL_MODE_CSEG, $(DATA_ADDR - (code_end - realcseg))

	.code32

#include "LzmaDecode.s"

	.code16
realcseg:
	movw	$REAL_MODE_DSEG, %ax
	movw	%ax, %ds
	movw	%ax, %es

	movl	%cr0, %eax
	andl 	$(~CR0_PE_ON), %eax
	movl	%eax, %cr0

	ljmp	$0, $DATA_ADDR

#endif

code_end:

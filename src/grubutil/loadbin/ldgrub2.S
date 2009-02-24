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

	.file	"ldgrub2.S"

#include <symbol.h>

#define DATA_ADDR	0x8000

	.text

	.code16

DEF_FUNC(main)
	movl	$DATA_ADDR, %edi

	call	EXT_FUNC(move_memory)

	pushw	%ss
	popw	%ds

	movsbl	%dh, %eax

	/* GRUB_KERNEL_MACHINE_INSTALL_DOS_PART.  */
	movl	%eax, (DATA_ADDR + 0x214)

	movb	$0xFF, %dh

	ljmp	$((DATA_ADDR >> 4) + 0x20), $0

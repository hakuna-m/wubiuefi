/*
 *  badgrubstart.S -- DOS EXE and Linux kernel startup code for GNU GRUB
 *  Copyright (C) 2003-2008  Tinybit(tinybit@tom.com)
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
 * This program is used to generate the badgrub.exe file, which can boot off
 * DOS directly or, in another way, boot off Linux through KEXEC.
 *
 * Use the following shell command to generate the badgrub.exe file:
 *
 * 	cat badgrubstart pre_stage2 > badgrub.exe
 *
 */

#define BAD_BIOS
#include "dosstart.S"


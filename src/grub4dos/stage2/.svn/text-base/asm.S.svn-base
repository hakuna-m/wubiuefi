/*
 *  GRUB  --  GRand Unified Bootloader
 *  Copyright (C) 1999,2000,2001,2002,2004 Free Software Foundation, Inc.
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
 * Note: These functions defined in this file may be called from C.
 *       Be careful of that you must not modify some registers. Quote
 *       from gcc-2.95.2/gcc/config/i386/i386.h:
	
   1 for registers not available across function calls.
   These must include the FIXED_REGISTERS and also any
   registers that can be used without being saved.
   The latter must include the registers where values are returned
   and the register where structure-value addresses are passed.
   Aside from that, you can include as many other registers as you like.

  ax,dx,cx,bx,si,di,bp,sp,st,st1,st2,st3,st4,st5,st6,st7,arg
{  1, 1, 1, 0, 0, 0, 0, 1, 1,  1,  1,  1,  1,  1,  1,  1,  1 }
 */

#define ASM_FILE

#include "shared.h"

#ifdef STAGE1_5
# define	ABS(x)	((x) - EXT_C(main) + 0x2200)
#else
# define	ABS(x)	((x) - EXT_C(main) + 0x8200)
#endif
	
	.file	"asm.S"

	.text

	/* Tell GAS to generate 16-bit instructions so that this code works
	   in real mode. */
	.code16

#ifndef STAGE1_5
	/* 
	 * In stage2, do not link start.S with the rest of the source
	 * files directly, so define the start symbols here just to
	 * force ld quiet. These are not referred anyway.
	 */
	.globl	start, _start
start:
_start:
#endif /* ! STAGE1_5 */
	
ENTRY(main)
	/*
	 *  Guarantee that "main" is loaded at 0x0:0x8200 in stage2 and
	 *  at 0x0:0x2200 in stage1.5.
	 */
	ljmp $0, $ABS(codestart)

	. = EXT_C(main) + 0x5

	/* control byte: pxe, DUCE, tune
	 * bit 0 = 1: disable pxe
	 * bit 1 = 1: disable keyboard intervention in boot process
	 * bit 2 = 1: disable the "unconditional command-line entrance" feature
	 * bit 3 = 1: disable geometry tune
	 */

	.byte	0

	/*
	 *  Compatibility version number
	 *
	 *  These MUST be at byte offset 6 and 7 of the executable
	 *  DO NOT MOVE !!!
	 */
	. = EXT_C(main) + 0x6
	.byte	COMPAT_VERSION_MAJOR, COMPAT_VERSION_MINOR

	/*
	 *  This is a special data area 8 bytes from the beginning.
	 */

	. = EXT_C(main) + 0x8

VARIABLE(install_partition)
	.long	0xFFFFFF
/* This variable is here only because of a historical reason.  */
VARIABLE(saved_entryno)
#if defined(STAGE1_5) /* || ! defined(PRESET_MENU_STRING) */
	.long	0
#else

/* Note: GRUB for DOS uses this for the commandline preset_menu.
 * A preset_menu can be embedded in the commandline of GRUB.EXE.
 * This new preset_menu overrides the built-in preset_menu.
 * If the variable is not touched, and the first byte at config_file is 0,
 * then the new menu at 0x0800 will work.
 * If the variable here is cleared to 0, or the first byte at config_file is
 * not 0, then the built-in preset_menu will work.
 *
 * Do NOT change this variable to other value than 0.
 */
 
	.long	EXT_C(preset_menu)
#endif
VARIABLE(stage2_id)
	.byte	STAGE2_ID
VARIABLE(force_lba)
	.byte	0
VARIABLE(version_string)
	.string VERSION
VARIABLE(config_file)
#ifndef STAGE1_5
	.string "/boot/grub/menu.lst"
#else   /* STAGE1_5 */
	.long	0xffffffff
	.string "/boot/grub/stage2"
#endif  /* STAGE1_5 */

	/*
	 *  Leave some breathing room for the config file name.
	 */

	. = EXT_C(main) + 0x6C  #; bss starting address
#ifndef STAGE1_5
#if defined(HAVE_USCORE_USCORE_BSS_START_SYMBOL)
	//.word	(__bss_start - main) & 0x0F, (__bss_start - main) >> 4
	.long	__bss_start
#elif defined(HAVE_USCORE_EDATA_SYMBOL)
	//.word	(_edata - main) & 0x0F, (_edata - main) >> 4
	.long	_edata
#elif defined(HAVE_EDATA_SYMBOL)
	//.word	(edata - main) & 0x0F, (edata - main) >> 4
	.long	edata
#else
#error no bss starting address
#endif
#endif

	. = EXT_C(main) + 0x70

/* the real mode code continues... */
codestart:
	cli		/* we're not safe here! */
	cld

	/* set up %ds, %ss, and %es */
	xorw	%ax, %ax
	movw	%ax, %ds
	movw	%ax, %es
	movw	%ax, %ss
	movl	$STACKOFF, %esp

	sti		/* added 2008-08-04 */

#ifndef STAGE1_5
	movb	0x0410, %al
	movb	%al, ABS(EXT_C(floppies_orig))
	movb	0x0475, %al
	movb	%al, ABS(EXT_C(harddrives_orig))

	//movb	$((int13_handler_end - int13_handler + 0x3ff) / 0x400), ABS(int13_handler)

	movl	0x54, %eax
	movl	%eax, ABS(EXT_C(ROM_int15))
	movl	0x4C, %eax
	movl	%eax, ABS(ROM_int13)
	movl	%eax, ABS(ROM_int13_dup)
	cmpl	$0xC0000000, %eax
	jnb	1f
	cmpl	$0x5A000000, %eax	// cmpl	$0x9A000000, %eax
	jb	1f
	andl	$0x3FFFFF, %eax
	cmpl	$0x100, %eax
	jnz	1f
	movw	0x413, %ax		/* Memory size in Kb */
	shlw	$6, %ax			/* Memory size in paragragh */
	cmpw	0x4E, %ax		/* 0000:004E=current int 13 segment */
	jne	1f			/* not hooked */

	movw	%ax, %ds		/* DS=current int13 code segment */

	/* check our int13 signature "$INT13SFGRUB4DOS" */
	cmpl	$0x544E4924, 0x103	/* $INT */
	jnz	2f
	cmpl	$0x46533331, 0x107	/* 13SF */
	jnz	2f
	cmpl	$0x42555247, 0x10B	/* GRUB */
	jnz	2f
	cmpl	$0x534F4434, 0x10F	/* 4DOS */
	jnz	2f

	movl	(ROM_int13 - int13_handler), %eax	/* 0x1C=ROM int 13 */
	cmpl	$0x5A000000, %eax	// cmpl	$0x9A000000, %eax
	jb	2f					/* not our handler */

	movl	(EXT_C(ROM_int15) - int13_handler), %eax	/* 0x0C=ROM int 15 */
	cmpl	$0x5A000000, %eax	// cmpl	$0x9A000000, %eax
	jb	2f					/* not our handler */

	/* restore old emu data, except the first byte of handler size. */
	movw	$(0x140 - 1), %cx
	movw	$1, %si			/* DS=current int13 code segment */
	movw	$ABS(int13_handler + 1), %di		/* ES=0 */
	repz movsb

	/* calculate the new max_cdrom_id. */
	movw	$2, %si
	lodsw				/* AL=atapi_dev_count, AH=min_cdrom_id */
	addb	%ah, %al
	decw	%ax			/* AL=max_cdrom_id */
	movb	%al, %cs:ABS(max_cdrom_id)		/* CS=0 */

	/* initialize bios_drive_map with hooked_drive_map */
	movw	$(DRIVE_MAP_SIZE * DRIVE_MAP_SLOT_SIZE / 2), %cx
	movw	$ABS(EXT_C(hooked_drive_map)), %si		/* CS=0 */
	movw	$ABS(EXT_C(bios_drive_map)), %di		/* ES=0 */
	cs repz movsw
	//xorw	%ax, %ax
	//movw	%ax, %ds			/* DS=0 */
	//jmp	3f

2:
	xorw	%ax, %ax
	movw	%ax, %ds			/* DS=0 */
1:
	//movl	ABS(EXT_C(ROM_int15)), %eax
	//cmpl	$0x5A000000, %eax	// cmpl	$0x9A000000, %eax
	//jnb	3f
	//movl	0x0054, %eax
	//movl	%eax, ABS(EXT_C(ROM_int15))
//3:
	/* check the BIOS type (currently only for Bochs) */
	movw	$0xF000, %ax
	movw	%ax, %es			/* ES=0xF000 */
	movw	$0xFF00, %di
	movw	$ABS(bochs_copygrght_string), %si
	movw	$0x22, %cx
	repz cmpsw
	setz	ABS(EXT_C(bios_id))	/* 1 for bochs, 0 for unknown. */
	xorw	%ax, %ax
	movw	%ax, %es			/* ES=0 */

#endif  /* STAGE1_5 */
//#ifndef SUPPORT_DISKLESS
//	/*
//	 * Save the sector number of the second sector (i.e. this sector)
//	 * in INSTALL_SECOND_SECTOR. See also "stage2/start.S".
//	 */
//	ADDR32	movl	%ebp, EXT_C(install_second_sector)
//#endif
	

	/* the active mouse will hang the machine */

#if 0
	cli
	pushal
	pushw	%ds
	pushw	%es
	pushw	%cs
	call	1f
	popw	%es
	popw	%ds
	popal
	jmp	2f
1:
	pushw	$0xADDA
	//ljmp	$0xF000, $0x98E1
	ljmp	$0xF000, $0xA5F2

2:
	ljmp	$0xF000, $0xFFF0
#endif

	pushw	%dx		/* DL=boot drive */

	/* qemu-0.8.0 could hang on mouse init here. */

#if 0
	/* reset mouse */
	movw	$0xC201, %ax
	int	$0x15
#endif

#if 0
	/* disable mouse */
	movw	$0xC200, %ax
	xorw	%bx, %bx	/* BH=0 means disable */
	int	$0x15
#endif

#if 0
	/* set mouse handler address */
	movw	$0xC207, %ax
	xorw	%bx, %bx	/* ES:BX=0000:0000 to cancel the handler */
	int	$0x15
#endif

#if 0
	/* disable monitor clock (Watch-Dog) */
	movw	$0xC300, %ax
	int	$0x15
#endif

#if 0
	/* restart all adaptors */
	movb	$0xFF, %al
	outb	%al, $0x96
	xorw	%cx, %cx
1:	loop	1b
	movb	$0xF0, %al
	outb	%al, $0x96
	xorw	%cx, %cx
1:	loop	1b
	movb	$0x00, %al
	outb	%al, $0x96
	xorw	%cx, %cx
1:	loop	1b

	/* initialize all adaptors */
	movw	$0xC000, %bx
2:
	movw	%bx, %ds
	xorw	%si, %si
	lodsw
	cmpw	$0xAA55, %ax
	jne	1f
	xorw	%ax, %ax
	lodsb			#; ROM size in sectors
	addw	$3, %ax
	andw	$0xFFFC, %ax
	subw	$4, %ax
	shlw	$5, %ax
	pushaw
	pushw	%bx
	pushw	$3
	movw	%sp, %bp
	lcall	*(%bp)
	popw	%bx
	popw	%bx
	popaw
1:
	addw	$0x80, %ax
	addw	%ax, %bx
	cmpw	$0xF000, %bx
	jb	2b
	
#endif

	xorw	%ax, %ax
	movw	%ax, %ds
	movw	%ax, %es

#if 0
	/* cancel alarm clock */
	movb	$0x07, %ah
	int	$0x1A
#endif

#if 0	/* commented out 2008-06-11 */
	/* clear VDS */
	andb	$0xD7, 0x47B
#endif

#ifndef STAGE1_5

	sti

	/* check the DUCE indicator */

	movl	0x5FC, %eax
	movl	%eax, %ecx
	testb	$0x0C, %al
	jz	1f
	orb	$0x0C, %al
	cmpl	$0x4543554C, %eax
	jne	1f
	andb	$0x0C, %cl	/* bit2=DUCE, bit3=chs-no-tune */
	orb	%cl, ABS(EXT_C(main)) + 5 /* at 0x8205 */
1:
	movw	$1, %bx		/* BL=1, BH=0 */

	testb	$0x02, ABS(EXT_C(main)) + 5	/* disable keyboard intervention? */
	jnz	4f			/* yes */

	movl	0x46c, %eax	/* initial tick */
	addl	$5, %eax	/* wait 0.27 seconds */
	pushl	%eax

2:
	/* checkkey 'c' */

	pushw	%bx
	movb	$0x01, %ah	/* checkkey */
	int	$0x16
	popw	%bx

	jz	1f		/* no keypress */

	/* getkey */

	pushw	%bx
	movb	$0x00, %ah	/* getkey */
	int	$0x16
	popw	%bx

	cmpw	$KEY_IC, %ax	/* insert char */
	jne	3f
	movb	$1, %bh		/* DEBUG_KEY pressed */
3:
	orb	$0x20, %al
	cmpb	$0x63, %al	/* is "C"? */
	jne	2b		/* no, get next key */

	/* "C" is pressed. */

	testb	$0x04, ABS(EXT_C(main)) + 5 /* at 0x8205, bit2=DUCE */
	jnz	2b

	/* Bypass all config files */
	movb	$0, %bl
	jmp	2b
1:

	popl	%eax
	pushl	%eax
	movl	0x46c, %ecx	/* current tick */
	cmpl	%eax, %ecx
	jnb	1f
	subl	$5, %eax
	cmpl	%eax, %ecx
	jnb	2b
	cmpl	$5, %ecx
	jb	2b
1:
	popl	%eax
4:
	movb	%bh, EXT_C(debug_boot)
#endif

	popw	%dx		/* DL=boot drive */

	//cli

//	pushw	%bx

#ifndef SUPPORT_DISKLESS
	/* save boot drive reference */
	ADDR32	movb	%dl, EXT_C(boot_drive)

//	testb	%bh, %bh	/* debug_boot? */
//	jz	1f
//	movw	$ABS(reset_disk_string),%si
//	call	print_message	/* will not change DX */
//1:
//	xorw	%ax, %ax
//	/* reset disk system (%ah = 0) */
//#ifdef STAGE1_5
//	int	$0x13
//#else
//	call	safe_int13
//#endif
//	movw	$ABS(reset_disk_failure_string),%si
//	jc	1f
//	movw	$ABS(reset_disk_success_string),%si
//1:
//	popw	%bx
//	pushw	%bx
//	testb	%bh, %bh	/* debug_boot? */
//	jz	1f
//	call	print_message	/* will not change DX */
//1:
#endif

//	popw	%bx

	xorw	%ax, %ax
	movw	%ax, %ds
	movw	%ax, %es

	testb	$0x02, ABS(EXT_C(main)) + 5	/* disable keyboard intervention? */
	jnz	4f			/* yes */

	pushw	%bx

	/* clear keyboard buffer */
2:
	movb	$0x01, %ah	/* checkkey */
	int	$0x16

	jz	1f		/* no keypress */

	movb	$0x00, %ah	/* getkey */
	int	$0x16
	jmp	2b
1:

	popw	%bx

4:

	/* transition to protected mode */
	DATA32	call EXT_C(real_to_prot)

	/* The ".code32" directive takes GAS out of 16-bit mode. */
	.code32

#ifndef STAGE1_5
	testb	%bl, %bl
	jnz	1f
	movl	$0, EXT_C(use_config_file)
1:

	/* before clearing the bss, we move preset_menu to 0x800 */

	movl	EXT_C(preset_menu), %eax

#if defined(HAVE_USCORE_USCORE_BSS_START_SYMBOL)
	cmpl	$__bss_start, %eax
#elif defined(HAVE_USCORE_EDATA_SYMBOL)
	cmpl	$_edata, %eax
#elif defined(HAVE_EDATA_SYMBOL)
	cmpl	$edata, %eax
#else
#error no bss starting address
#endif
	jnz	1f		/* use old bootp for diskless */		

	xorl	%eax, %eax
	cmpb	%al, EXT_C(config_file)	/* AL == 0 */
	jnz	2f
	movl	EXT_C(saved_entryno), %ebx
	testl	%ebx, %ebx
	jnz	3f	/* use menu embedded in commnad-line of grub.exe */
2:
	/* use builtin preset_menu */

	/* set the starting address of the preset_menu */
	
#if defined(HAVE_USCORE_USCORE_BSS_START_SYMBOL)
	movl	$__bss_start, %esi
#elif defined(HAVE_USCORE_EDATA_SYMBOL)
	movl	$_edata, %esi
#elif defined(HAVE_EDATA_SYMBOL)
	movl	$edata, %esi
#else
#error no bss starting address
#endif
	
	cld
	addl	$16, %esi	/* skip 4 bytes of B0 02 1A CE */
				/* skip 4 bytes of reserved */
				/* skip 4 bytes of reserved */
				/* skip 4 bytes of zeroes */

	movl	$0x400, %ecx	/* move 4KB of the menu ... */
	movl	$0x800, %edi	/* ... to 0x800 */
	repz movsl

3:
	movl	$0x0800, EXT_C(preset_menu)	/* use new menu at 0x800 */
1:
#endif /* !STAGE1_5 */

	/* if force_cdrom_as_boot_device==0, we are running by configfile, so we do not clear bss */
	cmpl	$0, EXT_C(force_cdrom_as_boot_device)
	je	1f

	/* clean out the bss */

	/* set %edi to the bss starting address */
#if defined(HAVE_USCORE_USCORE_BSS_START_SYMBOL)
	movl	$__bss_start, %edi
#elif defined(HAVE_USCORE_EDATA_SYMBOL)
	movl	$_edata, %edi
#elif defined(HAVE_EDATA_SYMBOL)
	movl	$edata, %edi
#else
#error no bss starting address
#endif

	/* set %ecx to the bss end */	
#if defined(HAVE_END_SYMBOL)
	movl	$end, %ecx
#elif defined(HAVE_USCORE_END_SYMBOL)
	movl	$_end, %ecx
#else
#error no bss ending address
#endif

	/* compute the bss length */
	subl	%edi, %ecx
	
	/* zero %al */
	xorb	%al, %al

	/* set the direction */
	cld
	
	/* clean out */
	rep
	stosb
	
1:	
	/*
	 *  Call the start of main body of C code, which does some
	 *  of it's own initialization before transferring to "cmain".
	 */
	call EXT_C(init_bios_info)
	call EXT_C(cmain)


/*
 *  This call is special...  it never returns...  in fact it should simply
 *  hang at this point!
 */

ENTRY(stop)
	call	EXT_C(prot_to_real)

	/*
	 * This next part is sort of evil.  It takes advantage of the
	 * byte ordering on the x86 to work in either 16-bit or 32-bit
	 * mode, so think about it before changing it.
	 */

	/* No external program ever calls HARD_STOP. HARD_STOP is only called
	 * by the asm.S itself, and all calls are from real mode. So we
	 * could(and should) use .code16 here clearly.
	 */

	.code16

//ENTRY(hard_stop)
hard_stop:
	sti
	hlt
	//jmp EXT_C(hard_stop)
	jmp hard_stop

#ifndef STAGE1_5

/* If preset_menu == __bss_start, the new menu at end of pre_stage2 will be used. */

VARIABLE(preset_menu)
#if defined(PRESET_MENU_STRING)
#if defined(HAVE_USCORE_USCORE_BSS_START_SYMBOL)
	//.word	(__bss_start - main) & 0x0F, (__bss_start - main) >> 4
	.long	__bss_start
#elif defined(HAVE_USCORE_EDATA_SYMBOL)
	//.word	(_edata - main) & 0x0F, (_edata - main) >> 4
	.long	_edata
#elif defined(HAVE_EDATA_SYMBOL)
	//.word	(edata - main) & 0x0F, (edata - main) >> 4
	.long	edata
#else /* ! HAVE_EDATA_SYMBOL */
#error no bss starting address
#endif /* ! HAVE_EDATA_SYMBOL */
#else  /* ! PRESET_MENU_STRING */
	.long	0
#endif /* PRESET_MENU_STRING */

VARIABLE(debug_boot)
	.long	0
#endif /* ! STAGE1_5 */
	.code16

	/* real mode print string */

/* prints string DS:SI (modifies AX BX SI) */

print_message:
1:
	sti		/* for hardware interrupt or watchdog */
	cld
	lodsb	(%si), %al	/* get token */
	xorw	%bx, %bx	/* video page 0 */
	movb	$0x0e, %ah	/* print it */
	int	$0x10		/* via TTY mode */
	cmpb	$0, %al		/* end of string? */
	jne	1b		/* until done */
	ret

reset_disk_string:
	.ascii	"Reseting the boot drive... \0"
reset_disk_success_string:
	.ascii	"Success.\r\n\0"
reset_disk_failure_string:
	.ascii	"Failure!\r\n\0"

bochs_copygrght_string:
	.ascii	"(c) 2002 MandrakeSoft S.A. Written by Kevin Lawton & the Bochs team.\0"
ENTRY(bios_id)
	.long	0	/* 1 for bochs, 0 for unknown. */

	.code32


#ifndef STAGE1_5

/* unsigned long pxe_scan(void)
 *
 * scan pxe runtime
 */
ENTRY(pxe_scan)
	pushl	%ebx

	call	EXT_C(prot_to_real)
	.code16

	sti		/* for hardware interrupt or watchdog */
	movw	$0x5650, %ax
	int	$0x1A
	cmpw	$0x564E, %ax
	jnz	1f
	cmpl	$0x4E455850, %es:(%bx)		// PXEN(V+)
	jnz	1f
	cmpw	$0x201, %es:6(%bx)		// API version
	jb	1f
	lesw	%es:0x28(%bx), %bx		// !PXE structure
	cmpl	$0x45585021, %es:(%bx)		// !PXE
	jnz	1f
	movw	%es, %cx
	jmp	2f
1:
	xorw	%bx, %bx
	xorw	%cx, %cx
2:

	DATA32  call EXT_C(real_to_prot)
	.code32

	xorl	%eax, %eax
	movw	%cx, %ax
	shll	$4, %eax
	andl	$0xFFFF, %ebx
	addl	%ebx, %eax
	jz	3f

	movl	0x10(%eax), %ebx
	movl	%ebx, EXT_C(pxe_entry)
	xorl	%ecx, %ecx
	movl	0x2A(%eax), %ebx
	cmpl	0x32(%eax), %ebx
	ja	1f
	movl	0x32(%eax), %ebx
	movw	0x36(%eax), %cx
	jmp	2f
1:
	movw	0x2E(%eax), %cx
2:
	addl	%ecx, %ebx
	addl	$1023, %ebx
	shrl	$10, %ebx
	movw	%bx, EXT_C(pxe_freemem)

3:
	popl	%ebx
	ret

/* int pxe_call(int func,void* data)
 *
 * PXE function call
 */
ENTRY(pxe_call)
	pushl	%ebp
	movl	%esp, %ebp
	pushl	%esi
	pushl	%edi
	pushl	%ebx

	movl	8(%ebp), %ecx
	movl	12(%ebp), %edx
	movl	%edx, %eax
	andl	$0xF, %eax
	shrl	$4, %edx
	shll	$16, %edx
	addl	%eax, %edx
	movl	EXT_C(pxe_entry), %ebx

	call	EXT_C(prot_to_real)
	.code16
	
	sti		/* for hardware interrupt or watchdog */
	pushl	%ebx
	pushl	%edx
	pushw	%cx
	movw	%sp, %bx
	lcall	*%ss:6(%bx)
	cld
	addw	$10, %sp
	movw	%ax, %cx

	DATA32  call EXT_C(real_to_prot)
	.code32

	movzwl	%cx, %eax
	
	popl	%ebx
	popl	%edi
	popl	%esi
	popl	%ebp
	ret

#if PXE_FAST_READ

/* int pxe_fast_read(void* data,int num)
 *
 * Read multiple packets
 */
ENTRY(pxe_fast_read)
	pushl	%ebp
	movl	%esp, %ebp
	pushl	%esi
	pushl	%edi
	pushl	%ebx

	movl	8(%ebp), %edx
	movl	12(%ebp), %esi	/* num */
	movl	EXT_C(pxe_blksize), %edi
	movl	%edx, %eax
	andl	$0xF, %eax
	shrl	$4, %edx
	shll	$16, %edx
	addl	%eax, %edx
	movl	EXT_C(pxe_entry), %ebx

	call	EXT_C(prot_to_real)
	.code16

	sti		/* for hardware interrupt or watchdog */
	movw	%si, %cx	/* num */
1:
	pushw	%cx		/* blocks to read */
	pushw	%di		/* block size */
	pushl	%ebx		/* pxe_entry */
	pushl	%edx		/* data pointer */
	pushw	$0x22		// PXENV_TFTP_READ
	movw	%sp, %bp
	lesw	2(%bp), %si	/* ES:SI=data pointer */

	movw	%di, %es:4(%si)	/* block size */
	lcall	*6(%bp)
	movw	%sp, %bp
	lesw	2(%bp), %si	/* ES:SI=data pointer */
	popw	%dx		// PXENV_TFTP_READ
	popl	%edx		/* data pointer */
	popl	%ebx		/* pxe_entry */
	popw	%di		/* block size */
	popw	%cx		/* blocks to read */
	cld
	
	cmpw	$0, %es:(%si)
	jnz	2f
	movw	%es:4(%si), %bp
//	cmpw	$512, %dx
//	jb	2f
//	cmpw	%di, %dx
//	ja	2f
//	je	3f
//	cmpl	EXT_C(filemax), %edx
//	jae	3f
//	movl	%edx, EXT_C(pxe_blksize)
//	movl	%edx, %edi
//3:
	addw	%bp, %es:6(%si)
	cmpw	%di, %bp
	jb	2f
	loop	1b

2:
	//addw	$10, %sp
	movw	%ax, %cx

	DATA32  call EXT_C(real_to_prot)
	.code32

	movzwl	%cx, %eax

	popl	%ebx
	popl	%edi
	popl	%esi
	popl	%ebp
	ret
#endif

/*
 * stop_floppy()
 *
 * Stops the floppy drive from spinning, so that other software is
 * jumped to with a known state.
 */
ENTRY(stop_floppy)
	pushal
	call	EXT_C(prot_to_real)
	.code16
	sti	#; added 2006-11-30
	xorb	%dl, %dl
#if defined(STAGE1_5) || 1
	int	$0x13
#else
	call	safe_int13
#endif
	DATA32  call EXT_C(real_to_prot)
	.code32
	popal
	ret

/*
 * grub_reboot()
 *
 * Reboot the system. At the moment, rely on BIOS.
 */
ENTRY(grub_reboot)
	call	EXT_C(prot_to_real)

	.code16

	/* cold boot */

	//sti		/* needn't enable interrupt here. comment it out */

	movw	$0x0472, %di
	movw	%ax, (%di)
	ljmp	$0xFFFF, $0x0000

	.code32
	
/*
 * grub_halt(int no_apm)
 *
 * Halt the system, using APM if possible. If NO_APM is true, don't use
 * APM even if it is available.
 */
ENTRY(grub_halt)
	/* get the argument */
	movl	4(%esp), %eax
	
	/* see if zero */
	testl	%eax, %eax
	jnz	EXT_C(stop)

	call	EXT_C(prot_to_real)

	.code16
	
	//sti		/* this is not needed here, so comment it out. */
	sti	#; added 2006-11-30

	/* detect APM */
	movw	$0x5300, %ax
	xorw	%bx, %bx
	int	$0x15
	//jc	EXT_C(hard_stop)
	jc	hard_stop
	/* don't check %bx for buggy BIOSes... */

	/* disconnect APM first */
	movw	$0x5304, %ax
	xorw	%bx, %bx
	int	$0x15

	/* connect APM */
	movw	$0x5301, %ax
	xorw	%bx, %bx
	int	$0x15
	//jc	EXT_C(hard_stop)
	jc	hard_stop

	/* set APM protocol level - 1.1 or bust. (this covers APM 1.2 also) */
	movw	$0x530E, %ax
	xorw	%bx, %bx
	movw	$0x0101, %cx
	int	$0x15
	//jc	EXT_C(hard_stop)
	jc	hard_stop
	
	/* set the power state to off */
	movw	$0x5307, %ax
	movw	$1, %bx
	movw	$3, %cx
	int	$0x15

	/* shouldn't reach here */
	//jmp	EXT_C(hard_stop)
	jmp	hard_stop


/*
 * int check_64bit (void)
 *
 * Checks whether 64-bit mode is supported
 *
 * Stolen from a patch originaly intended for syslinux
 * (http://syslinux.zytor.com/archives/2007-January/007832.html)
 *
 * Copyright (C) 2007 Byron Stanoszek <gandalf@winds.org>
 *
 * Adapted to AT&T syntax by Robert Millan <rmh@aybabtu.com>
 */

ENTRY(check_64bit)

	.code32

	pushl	%ebp
	pushl	%ebx
	pushl	%edx

	/* Check if this CPU supports the CPUID command */
	pushfl
	pushfl
	popl	%eax
	movl	%eax, %ebx
	xorl	$(1 << 21), %eax	// CPUID bit
	pushl	%eax
	popfl
	pushfl
	popl	%eax
	popfl				// Restore the original flags
	xorl	%ebx, %eax
	jz	is_32bit

	/* Now check for the 64-bit flag in the CPU features byte ($0000_0001, edx)
	This is bit 30 for Intel CPUs, and bit 29 for AMD CPUs */
	movl	$0x00000000, %eax	// Find last Intel cpuid #
	cpuid
	cmpl	$0x00000000, %eax
	je	test_amd
	movl	$0x00000001, %eax	// Read Intel CPU flags
	cpuid
	btl	$30, %edx		// 64-bit if bit 30 is set
	jc	is_64bit

test_amd:
	movl	$0x80000000, %eax	// Find last AMD cpuid #
	cpuid
	cmpl	$0x80000000, %eax
	jbe	is_32bit
	movl	$0x80000001, %eax	// Read AMD CPU flags
	cpuid
	btl	$29, %edx		// 64-bit if bit 29 is set
	jnc	is_32bit

is_64bit:
	movl	$1, %eax
	popl	%edx
	popl	%ebx
	popl	%ebp
	ret
is_32bit:
	xorl	%eax, %eax
	popl	%edx
	popl	%ebx
	popl	%ebp
	ret


/*
 * int tpm_init (void)
 *      return non-zero for success and zero for failure.
 */
ENTRY(tpm_init)
	pushl	%ebp
	pushl	%ebx
	pushl	%esi
	pushl	%edi
	
	call	EXT_C(prot_to_real)	/* enter real mode */

	.code16

	sti

	movw	$0xBB00, %ax
	int	$0x1A
	testl	%eax, %eax
	jnz	1f			/* failure */
	cmpl	$0x41504354, %ebx	/* "TCPA" */
	jnz	1f			/* failure */
	cmpw	$0x102, %cx		/* TCG BIOS version 1.2 */
	jb	1f			/* failure */
	movw	%ax, %es		/* ES=0 */
	movw	$0xBB07, %ax		/* eax hi word=0 */
	movl	$0x00000200, %ecx	/* buffer size to hash */
	movl	$0x00000008, %edx	/* PCR index for the hashed result */
	xorl	%esi, %esi		/* place 0 into the event field */
	movl	$0x00007C00, %edi	/* ES:DI point to data buffer to hash */
	int	$0x1A
	
	testl	%eax, %eax
1:
	setz	%dl

	DATA32	call	EXT_C(real_to_prot)
	.code32

	movzbl	%dl, %eax

	popl	%edi
	popl	%esi
	popl	%ebx
	popl	%ebp
	ret


/* Catch CPU exceptions 0 - 7
 *	0	Divide
 *	1	Debug
 *	2	NMI
 *	3	Break point
 *	4	Overflow
 *	5	Bound
 *	6	Invalid Instruction
 *	7	no coprocessor
 */

set_fault_recovery_handler:

	.code16

	pushfw
	pushw	%ds
	pushw	%es
	pushaw

	/* backup int 00 - 07 */

	xorw	%ax, %ax
	movw	%ax, %ds
	movw	%ax, %es
	xorw	%si, %si
	movw	$ABS(int_00_07_vectors), %di
	movw	$16, %cx
	cld
	repz movsw

	/* set to new vector */

	xorw	%ax, %ax
	movw	%ax, %ds
	movw	%ax, %es
	xorw	%si, %si
	movw	$ABS(int_00_07_vectors), %di

	pushl	%eax

	xorw	%di, %di
	movl	$ABS(fault_recovery_handler), %eax	/* 0000:fault_recovery_handler */
	movw	$8, %cx
	cld
	repz stosl

	popl	%eax

	popaw
	popw	%es
	popw	%ds
	popfw
	ret

unset_fault_recovery_handler:

	.code16

	pushfw
	pushw	%ds
	pushw	%es
	pushaw

	/* restore int 00 - 07 */

	xorw	%ax, %ax
	movw	%ax, %ds
	movw	%ax, %es
	xorw	%di, %di
	movw	$ABS(int_00_07_vectors), %si
	movw	$16, %cx
	cld
	repz movsw

	popaw
	popw	%es
	popw	%ds
	popfw
	ret

	.align	4

int_00_07_vectors:
	.space	32

original_registers:
	.space	48

safe_int13:

	.code16

	/* setup our fault recovery handler */

	call	set_fault_recovery_handler

	/* backup old registers. Note: CS=0 */

	movw	%ds, %cs:ABS(original_registers)
	movw	%es, %cs:ABS(original_registers) + 4
	movw	%ss, %cs:ABS(original_registers) + 8
	movl	%esp, %cs:ABS(original_registers) + 12
	movl	%eax, %cs:ABS(original_registers) + 16
	movl	%ebx, %cs:ABS(original_registers) + 20
	movl	%ecx, %cs:ABS(original_registers) + 24
	movl	%edx, %cs:ABS(original_registers) + 28
	movl	%esi, %cs:ABS(original_registers) + 32
	movl	%edi, %cs:ABS(original_registers) + 36
	movl	%ebp, %cs:ABS(original_registers) + 40

	pushw	%bp
	pushw	%ax
	movw	%sp, %bp
	movw	4(%bp), %ax
	movw	%ax, %cs:ABS(original_registers) + 44	#; return IP
	popw	%ax
	popw	%bp

	int	$0x13

	call	unset_fault_recovery_handler

	ret

fault_recovery_handler:

	.code16

	/* restore old registers. Note: CS=0 */

	movw	%cs:ABS(original_registers), %ds
	movw	%cs:ABS(original_registers) + 4, %es
	movw	%cs:ABS(original_registers) + 8, %ss
	movl	%cs:ABS(original_registers) + 12, %esp
	movl	%cs:ABS(original_registers) + 16, %eax
	movl	%cs:ABS(original_registers) + 20, %ebx
	movl	%cs:ABS(original_registers) + 24, %ecx
	movl	%cs:ABS(original_registers) + 28, %edx
	movl	%cs:ABS(original_registers) + 32, %esi
	movl	%cs:ABS(original_registers) + 36, %edi
	movl	%cs:ABS(original_registers) + 40, %ebp

	/* stack is available, so we can push and pop. */

	pushw	%bp
	pushw	%ax
	movw	%sp, %bp
	movw	%cs:ABS(original_registers) + 44, %ax	#; return IP
	movw	%ax, 4(%bp)
	popw	%ax
	popw	%bp

	pushl	$1		#; CF=1 indicating error
	popfl			#; CLD, CLI, and many more...

	call	unset_fault_recovery_handler

	ret

	/* never come here. */

	iret

	.code32

/*
 * set_int15_handler(void)
 *
 * Set up int15_handler.
 */
ENTRY(set_int15_handler)

	.code32

	pushl	%edi
	
	/* save the original int15 handler */
	movl	$0x54, %edi
#if 0
	movw	(%edi), %ax
	movw	%ax, ABS(int15_offset)
	movw	2(%edi), %ax
	movw	%ax, ABS(int15_segment)

	/* save the new int15 handler */
	movw	$ABS(int15_handler), %ax
	movw	%ax, (%edi)
	xorw	%ax, %ax
	movw	%ax, 2(%edi)
#else
	movl	(%edi), %eax
	movl	%eax, ABS(int15_offset)

	/* set the new int15 handler */
	movl	$ABS(int15_handler), %eax
	stosl
#endif

	popl	%edi
	ret


/*
 * unset_int15_handler(void)
 *
 * Restore the original int15 handler
 */
ENTRY(unset_int15_handler)

	.code32

	pushl	%edi
	
	/* check if int15_handler is set */
	movl	$0x54, %edi
#if 0
	movw	$ABS(int15_handler), %ax
	cmpw	%ax, (%edi)
	jne	1f
	xorw	%ax, %ax
	cmpw	%ax, 2(%edi)
	jne	1f

	/* restore the original */
	movw	ABS(int15_offset), %ax
	movw	%ax, (%edi)
	movw	ABS(int15_segment), %ax
	movw	%ax, 2(%edi)
#else
	movl	$ABS(int15_handler), %eax
	cmpl	%eax, (%edi)
	jne	1f

	/* restore the original */
	movl	ABS(int15_offset), %eax
	stosl
#endif

1:
	popl	%edi
	ret


/*
 * Translate a key code to another.
 *
 * Note: This implementation cannot handle more than one length
 * scancodes (such as Right Ctrl).
 */
	.code16
int15_handler:
	/* if non-carrier, ignore it */
	jnc	1f
	/* check if AH=4F */
	cmpb	$0x4F, %ah
	jne	1f

	/* E0 and E1 are special */
	cmpb	$0xE1, %al
	je	4f
	cmpb	$0xE0, %al
	/* this flag is actually the machine code (je or jmp) */
int15_skip_flag:	
	je	4f
	
	pushw	%bp
	movw	%sp, %bp
	
	pushw	%bx
	pushw	%dx
	pushw	%ds
	pushw	%si

	/* save bits 0-6 of %al in %dl */
	movw	%ax, %dx
	andb	$0x7f, %dl
	/* save the highest bit in %bl */
	movb	%al, %bl
	xorb	%dl, %bl
	/* set %ds to 0 */
	xorw	%ax, %ax
	movw	%ax, %ds
	/* set %si to the key map */
	movw	$ABS(EXT_C(bios_key_map)), %si

	/* find the key code from the key map */
2:
	lodsw
	/* check if this is the end */
	testw	%ax, %ax
	jz	3f
	/* check if this matches the key code */
	cmpb	%al, %dl
	jne	2b
	/* if so, perform the mapping */
	movb	%ah, %dl
3:
	/* restore %ax */
	movw	%dx, %ax
	orb	%bl, %al
	/* make sure that CF is set */
	orw	$1, 6(%bp)
	/* restore other registers */
	popw	%si
	popw	%ds
	popw	%dx
	popw	%bx
	popw	%bp
	iret
	
4:
	/* tricky: jmp (0x74) <-> je (0xeb) */
	xorb	$(0x74 ^ 0xeb), ABS(int15_skip_flag)
1:
	/* just cascade to the original */
	/* ljmp */
	.byte	0xea
int15_offset:	.word	0
int15_segment:	.word	0

	.code32

	.align	4	
ENTRY(bios_key_map)
	.space	(KEY_MAP_SIZE + 1) * 2
	
	
/*
 * set_int13_handler(map)
 *
 * Copy MAP to the drive map and set up int13_handler.
 */
ENTRY(set_int13_handler)

	.code32

	pushl	%ebp
	movl	%esp, %ebp

	pushl	%edi
	pushl	%esi

	/* copy MAP to the drive map */
	movl	$(DRIVE_MAP_SIZE * DRIVE_MAP_SLOT_SIZE / 4), %ecx
	movl	$ABS(EXT_C(hooked_drive_map)), %edi
	movl	8(%ebp), %esi
	cld
	repz movsl

//	Now initialized early at the beginning of this file
//
//	/* save the original int13 handler */
//	movl	$0x4c, %edi
//	movl	(%edi), %eax
//	movl	%eax, ABS(ROM_int13)
	
	/* decrease the lower memory size and set it to the BIOS memory */
	movl	$0x413, %edi
	movl	%edi, %esi

	lodsw
	/* KBytes that int13 handler occupies */
	subb	ABS(int13_handler), %al
	stosw
	
	/* compute the segment(high word) */
	shll	$(16 + 6), %eax

	/* the offset(low word) should be 0x100 */
	movw	$0x100, %ax

	/* save the new int13 handler */
	movl	$0x4c, %edi
	stosl

	/* EDI points to the destination int13 handler in the reserved area */
	movl	%eax, %edi		/* the int13 vector just saved */
	shrl	$12, %edi		/* get base address of segment */

	/* set ESI to the drive map */
	movl	$ABS(EXT_C(hooked_drive_map)), %esi
	movl	$(DRIVE_MAP_SIZE), %ecx
1:
	cmpb	$0xff, 1(%esi)		/* Is there a mapped memdrive? */
	jne	2f			/* No. Try next slot */
	testb	$0x40, 5(%esi)		/* Is To_DRIVE a CDROM? */
	jz	1f			/* No. Memdrive indeed. Hook int15 */
2:
	/* try next slot */
	addl	$DRIVE_MAP_SLOT_SIZE, %esi
	loop	1b
	jmp	2f			/* no memdrives, don't hook int15 */

1:
	/* save the new int15 handler */
	movw	$(int15_e820_handler - int13_handler), %ax	/* segment still in high word */
	movl	%eax, 0x54

2:
	/* copy int13_handler to the reserved area */
	movl	$ABS(int13_handler), %esi
	movl	$((int13_handler_end - int13_handler) / 4), %ecx
	cld
	repz movsl

	popl	%esi
	popl	%edi
	popl	%ebp
	ret

/* int
 * unset_int13_handler(check_status_only)
 *
 * Restore the original int13 handler
 *
 * Return 0 for success and non-zero for failure.
 */
ENTRY(unset_int13_handler)

	.code32

	pushl	%ebp
	movl	%esp, %ebp

	pushl	%edi
	
	/* check if int13_handler is set */
	movl	$0x413, %edi
	movw	(%edi), %ax
	cmpw	$640, %ax
	jae	1f		#; needn't unset
//	cmpw	$632, %ax
//	jb	1f
	shll	$(16 + 6), %eax

	/* the offset(low word) should be 0x100 */
	movw	$0x100, %ax

	cmpl	%eax, 0x4c
	jne	1f		#; not hooked, unset failure
	movl	%eax, %edi
	shrl	$12, %edi	/* segment base address */

	/* check our int13 signature "$INT13SFGRUB4DOS" */
	cmpl	$0x544E4924, 0x103(%edi)	/* $INT */
	jnz	1f
	cmpl	$0x46533331, 0x107(%edi)	/* 13SF */
	jnz	1f
	cmpl	$0x42555247, 0x10B(%edi)	/* GRUB */
	jnz	1f
	cmpl	$0x534F4434, 0x10F(%edi)	/* 4DOS */
	jnz	1f

	//cmpl	$0x9A000000, 0x1C(%edi)		/* old int 13 */
	cmpl	$0x5A000000, 0x1C(%edi)		/* old int 13 */
	jb	1f

	//cmpl	$0x9A000000, 0x0C(%edi)		/* old int 15 */
	cmpl	$0x5A000000, 0x0C(%edi)		/* old int 15 */
	jb	1f

	movl	ABS(ROM_int13), %eax
	cmpl	0x1C(%edi), %eax
	jnz	1f

	movl	ABS(EXT_C(ROM_int15)), %eax
	cmpl	0x0C(%edi), %eax
	jnz	1f

	xorl	%eax, %eax

	cmpl	%eax, 8(%ebp)
	jnz	1f

	/* increase the lower memory size */

	movzbw	(%edi), %ax
	addw	%ax, 0x413

	/* restore the original int15 handler */
	movl	ABS(EXT_C(ROM_int15)), %eax
	movl	%eax, 0x54

	/* restore the original int13 handler */
	movl	ABS(ROM_int13), %eax
	movl	%eax, 0x4c

	xorl	%eax, %eax			/* success */
1:
	/* return non-zero for failure */
	popl	%edi
	popl	%ebp
	ret


/* 
 * Map a drive to another drive or a disk image file.
 */
	
	.code16
	
	.align	4

ENTRY(bios_drive_map)
	.space	(DRIVE_MAP_SIZE + 1) * DRIVE_MAP_SLOT_SIZE

	/* align it this way so that int13_handler can be used as a segment
	 * base address. The `cdrom' command requires this.
	 */
	.align	16

int13_handler:

	/* memory size in K that int13 handler uses. */

	.byte	((int13_handler_end - int13_handler + 0x3ff) / 0x400)

	/* 1-byte space reserved. */

	. = int13_handler + 0x2

ENTRY(atapi_dev_count)	.byte	0
ENTRY(min_cdrom_id)	.byte	0xE0
	
	. = int13_handler + 0x4

	/* Signature */
	.ascii	"G4DS"		# Please don't use this signature any longer.
				# This field might be used for other purposes.
				# Use signature at offset 0x103 instead.
	
	. = int13_handler + 0x08

	/* Version number */
	.word	1

	. = int13_handler + 0x0A

VARIABLE(floppies_orig)
	.byte	0			/* original value at 0040:0010 */

	. = int13_handler + 0x0B

VARIABLE(harddrives_orig)
	.byte	0			/* original value at 0040:0075 */

	. = int13_handler + 0x0C

VARIABLE(ROM_int15)
	.long	0			/* original int15 vector */

	. = int13_handler + 0x10

	/* 12-byte space reserved. */

	. = int13_handler + 0x1C

ROM_int13:	.long	0		/* original int13 vector */

	. = int13_handler + 0x20	/* drive map table begins at 0x20 */

ENTRY(hooked_drive_map)
	.space	(DRIVE_MAP_SIZE + 1) * DRIVE_MAP_SLOT_SIZE

	/* 8-byte space reserved. */

	. = int13_handler + 0x100	/* real int13 handler entry at 0x100 */

	jmp	1f

	. = int13_handler + 0x103

	/*******************************************************************/
	/* ----------------- SafeMBRHook structure begin ----------------- */

	.ascii	"$INT13SF"		/* Win9x use this! Don't touch! */

	.ascii	"GRUB4DOS"		/* 8-byte Vender ID */

	. = int13_handler + 0x113

ROM_int13_dup:		/* Win9x Safe-MBR-Hook structure requires this! */

	.long	0

	. = int13_handler + 0x117

VARIABLE(safe_mbr_hook)

	.long	0x00000001		/* safe MBR hook flag */

	/* -----------------  SafeMBRHook structure end  ----------------- */
	/*******************************************************************/

	/* But Win9x may expect additional data after SafeMBRHook structure.
	 * This is undocumented, and mysterious. If this area is not what
	 * Win9x expected, Win9x could hang.
	 */

	. = int13_handler + 0x11B

VARIABLE(int13_scheme)

	/* bit 0 controls how we access sectors in protected mode.
	 * bit0=0: use pushf and far call for ROM int13 service.
	 * bit0=1: use the `int $0x13' instruction.
	 */
	.long	0x00000001

	/* space reserved. */

	. = int13_handler + 0x140

#if 0
1:
	/* backup far return address */
	popl	%cs:(int13_old_cs_ip - int13_handler)

	/* build new stack: flags */
	popw	%cs:(int13_handler_end - 2 - int13_handler)

	/* backup old stack */
	movw	%sp, %cs:(int13_old_sp - int13_handler)
	movw	%ss, %cs:(int13_old_ss - int13_handler)

	/* build new stack pointer */
	movw	$(int13_handler_end - 2 - int13_handler), %cs:(int13_new_sp - int13_handler)
	movw	%cs, %cs:(int13_new_ss - int13_handler)

	/* switch to new stack */
	lssw	%cs:(int13_new_sp - int13_handler), %sp

	//pushfw			/* flags already on stack */
	pushw	%cs
	call	1f

	/* restore old stack */
	lssw	%cs:(int13_old_sp - int13_handler), %sp

	/* transfer control to caller */
	ljmp	*%cs:(int13_old_cs_ip - int13_handler)

	//iret				/* never reach here */

	.align	4

int13_old_cs_ip:	.long	0
int13_old_sp:		.word	0
int13_old_ss:		.word	0
int13_new_sp:		.word	0
int13_new_ss:		.word	0
		
#endif

1:

	/* backup far return address */
	popl	%cs:(int13_old_cs_ip - int13_handler)

	/* backup old flags */
	popw	%cs:(int13_old_flags - int13_handler)

#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
		/* original stack layout for reference */
		/* BP+10: old Flags */
		/* BP+ 8: return CS */
		/* BP+ 6: return IP */
		/* BP+ 2: old EAX */
		/* BP+ 0: old BP */
		/* BP- 2: old SI */
		/* BP- 6: FROM, TO, Hmax, Smax */
		/* BP-10: TO_C, TO_H, TO_S */
		/* BP-14: StartLBA_Lo */
		/* BP-18: StartLBA_Hi */
		/* BP-22: S_count_Lo */
		/* BP-26: S_count_Hi */
#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
	cld
	movl	%eax, %cs:(int13_old_eax - int13_handler)
	movl	%ebx, %cs:(int13_old_ebx - int13_handler)
	movl	%ecx, %cs:(int13_old_ecx - int13_handler)
	movl	%edx, %cs:(int13_old_edx - int13_handler)
	movl	%esi, %cs:(int13_old_esi - int13_handler)
	movl	%edi, %cs:(int13_old_edi - int13_handler)
	movl	%esp, %cs:(int13_old_esp - int13_handler)
	movl	%ebp, %cs:(int13_old_ebp - int13_handler)
	movw	%ds, %cs:(int13_old_ds - int13_handler)
	movw	%es, %cs:(int13_old_es - int13_handler)

	cmpb	$0x1a, %ah	/* PS/2 low level format ESDI drive!!!! */
	je	error_01_disable	/* disabled in any case */

	cmpb	$0, %cs:(EXT_C(atapi_dev_count) - int13_handler)
	jz	1f		/* no cdrom */
	cmpb	%cs:(EXT_C(min_cdrom_id) - int13_handler), %dl
	jb	1f		/* not cdrom drive */
	cmpb	%cs:(max_cdrom_id - int13_handler), %dl
	jbe	edd30_for_cdrom
1:

/****************************************************************************/
	/* find the drive number from the drive map */
	movw	$(EXT_C(hooked_drive_map) - int13_handler - DRIVE_MAP_SLOT_SIZE), %bp
1:	
	addw	$DRIVE_MAP_SLOT_SIZE, %bp
	movw	%bp, %cs:(int13_new_bp - int13_handler)
	movl	%cs:(%bp), %eax		/* FROM, TO, Hmax, Smax */

	/* check if this is the end */
	testl	%eax, %eax
	jnz	3f			/* not end, continue */

	movl	%cs:8(%bp), %eax	/* StartLBA_Lo */
	testl	%eax, %eax
	jnz	3f			/* not end, continue */

	movl	%cs:16(%bp), %eax	/* S_count_Lo */
	testl	%eax, %eax
	jz	2f		/* map whole drive to itself signals the end */
3:
	/* Now this is a valid drive map slot */
	cmpb	%cs:(%bp), %dl	/* check if this matches the drive number */
	jne	1b		/* no, continue to check the next map */

	/* yes, found the map corresponding to drive DL */

	movw	%cs:2(%bp), %ax		/* AL=Hmax, AH=Smax */

	/* bit 1-5 already cleared for in-situ */
	//andb	$0xC1, %ah		/* clear bit 5 - bit 1 */

	testb	$0x80, %cs:7(%bp)	/* TO_S */
	jnz	1f			/* in-situ */

	/* non-zero StartLBA signals emulation */

	cmpl	$0, %cs:8(%bp)		/* StartLBA_Lo */
	jnz	drive_emulation

	/* StartLBA_Lo == 0 */

	/* if FROM and TO are both cdrom, this is a whole drive map. */
	testw	$0x4000, %cs:4(%bp)	/* TO_C bit 14=TO has 2048-byte cdrom sector */
	jz	3f			/* not cdrom */
	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jz	3f			/* not cdrom */
	movb	%cs:1(%bp), %dl		/* DL changed(!!) to TO_drive */
	cmpb	$0, %cs:(EXT_C(atapi_dev_count) - int13_handler)
	jz	2f		/* no cdrom by our driver, so it is a bios drive map. */
	cmpb	%cs:(EXT_C(min_cdrom_id) - int13_handler), %dl	/* TO_drive */
	jb	2f		/* not cdrom drive by our driver, so it is a bios drive map. */
	cmpb	%cs:(max_cdrom_id - int13_handler), %dl	/* TO_drive */
	ja	2f		/* not cdrom drive by our driver, so it is a bios drive map. */
	jmp	edd30_for_cdrom
3:

	/* S_count being not 1 signals emulation */

	movl	%cs:16(%bp), %eax	/* S_count_Lo */
	shrl	$1, %eax
	jnz	drive_emulation

	/* now StartLBA=0 and sector count=1(for whole disk) */

	/* if sectors per track > 1, this is force geometry screw. */

	movw	%cs:2(%bp), %ax		/* AL=Hmax, AH=Smax */
	testb	$62, %ah	/* Sectors > 1 means force geom, this -- */
	jnz	drive_emulation	/* -- also leads to drive emulation */

	/* ignore geom and directly map a whole drive */
	
1:
	/* bit 7 of the TO_S is for in-situ primary partition(alter MBR) */

	/* bits of AH:
	 *    7		bit set means readonly/fakewrite
	 *    6		bit set means disable LBA
	 *  5 - 1	bits already cleared(=0)
	 *    0		bit cleared means disable CHS
	 * So, if AH!=1, it is a restricted disk access;
	 * and if AH=1, it is a normal disk access.
	 */
	cmpb	$1, %ah
	je	1f
//	testb	$0x3F, %ah
//	jz	3f
//	testb	$0xC0, %ah
//	jz	1f
//3:
	call	restricted_map
1:
	/* map a whole drive, normal access */

	/* but if --in-situ was used, we should avoid writing the MBR! */
	testb	$0x80, %cs:7(%bp)	/* TO_S */
	jz	1f			/* not in-situ, allow write */
	testb	$0x40, %cs:7(%bp)	/* TO_S. bit 6 here means safe-boot */
	jz	1f			/* unsafe-boot, allow write */
	movw	%cs:(int13_old_eax - int13_handler), %ax
	cmpb	$0x03, %ah		/* is it CHS write? */
	jne	3f

	/* check if it is a write to MBR, i.e., C/H/S=0/0/1 */
	cmpw	$0x0001, %cx		/* C=0, S=1 */
	jne	1f
	cmpb	$0x00, %dh		/* H=0 */
	jne	1f

	/* deny the write and end the int 13 call */
	call	readonly_fakewrite	/* NO RETURN!! */
3:
	cmpb	$0x43, %ah		/* is it LBA write? */
	jne	1f			/* no, continue the normal access */

	/* check if it is a write to MBR, i.e., LBA=0 */

	xorl	%eax, %eax
	orl	12(%si), %eax		/* LBA_hi */
	orl	8(%si), %eax		/* LBA_lo */
	je	readonly_fakewrite	/* deny the write and end */

1:
	movb	%cs:1(%bp), %dl	/* Let DL access TO instead of FROM */
2:
	/* might map to itself, i.e., actually not mapped */
	
	movl	%cs:(int13_old_eax - int13_handler), %eax
	movl	%cs:(int13_old_ebp - int13_handler), %ebp  /* BP changed!! */

	call	backup_int13

	pushw	%cs:(int13_old_flags - int13_handler)
	popfw

	int	$0x13

	/* save the returned CF flag to int13_old_flags */

	jnc	1f
	orb	$1, %cs:(int13_old_flags - int13_handler)
	jmp	2f
1:
	andb	$0xFE, %cs:(int13_old_flags - int13_handler)
2:
	call	restore_int13

	/* restore BP!! */
	movw	%cs:(int13_new_bp - int13_handler), %bp
	xchgw	%ax, %cs:(int13_old_eax - int13_handler)
				/* old AX changed!! */

	/* check int13/AH=4Bh for cdrom */
	testw	$0x4000, %cs:4(%bp)	/* TO_C bit 14=TO has 2048-byte cdrom sector */
	jz	1f			/* not cdrom */
	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jz	1f			/* not cdrom */
	cmpb	$0x4B, %ah
	jne	1f
	cmpb	$0x01, %al
	ja	1f
	/* this is int13 function 0x4B00 or 0x4B01 */
	/* restore DS:SI, just in case they were changed by buggy int13 */
	movw	%cs:(int13_old_esi - int13_handler), %si
	movw	%cs:(int13_old_ds - int13_handler), %ds
	cmpb	$0x13, (%si)		/* packet size */
	jne	1f
	testb	$0x0F, 1(%si)		/* boot type(0=no emu) */
	jne	1f
	movb	%cs:1(%bp), %dl		/* just in case DL was changed by a buggy int13 */
	cmpb	%dl, 2(%si)
	jne	1f
	movb	%cs:(%bp), %dl		/* restore DL back to the FROM drive */
	movb	%dl, 2(%si)
	jmp	3f			/* return */
1:


#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

	pushw	%cs:(int13_old_flags - int13_handler)
	popfw

	/* check if should restore(reversely map) the drive number */
	jc	1f		/* restore DL on error */

	/* alter MBR after read */

	testb	$0x80, %cs:7(%bp)	/* TO_S */
	jz	2f

	cmpb	$0x02, %ah
	je	4f		/* alter MBR */
	cmpb	$0x42, %ah
	je	4f		/* alter MBR */
2:
	cmpb	$0x08, %ah	/* int13 AH=08h, read drive parameters */
	jne	2f

	/* DL==number of drives, should not restore */
	xorw	%ax, %ax
	movw	%ax, %ds
	movb	0x475, %dl	/* DL=number of hard drives */
	testb	$0x80, %cs:(int13_old_edx - int13_handler) /* harddrive? */
	jnz	3f		/* yes, jump */
	//movw	$0x10, %bx	/* for floppy, refer to function 0x48 */
	movb	0x410, %al
	rorb	$1, %al
	cbw
	shlb	$1, %al
	shrb	$6, %al
	incw	%ax
	andb	%ah, %al
	movb	%al, %dl	/* DL=number of floppy drives */
	//lesw	0x0078, %di	/* point to int 1E floppy parameters */
	jmp	3f
2:
	cmpb	$0x15, %ah	/* read drive type */
	jne	2f
	testb	$0x80, %cs:(int13_old_edx - int13_handler) /* harddrive? */
	jnz	3f		/* yes, do not restore DL */
	/* restore DL for floppy int13 AH=15h call */
	jmp	1f
4:
	call	modify_in_situ
	movl	%cs:(int13_old_ebx - int13_handler), %ebx
	movl	%cs:(int13_old_ecx - int13_handler), %ecx
	movl	%cs:(int13_old_edx - int13_handler), %edx
	movl	%cs:(int13_old_edi - int13_handler), %edi
	movw	%cs:(int13_old_es - int13_handler), %es
2:
	movw	%cs:(%bp), %ax	/* get the drive mapping */
	/* try to restore DL if possible */
	cmpb	%al, %ah	/* check if the mapping was performed */
	je	3f		/* not performed, so need not restore DL */
	cmpb	%dl, %ah
	jne	3f		/* DL changed by int13, so do not restore */
1:
	movb	%cs:(int13_old_edx - int13_handler), %dl	/* restore DL back to the FROM drive */
3:
	/* return */

	/* BX, CX, DX, ES, DI are output registers and should not touch. */

	pushw	%cs:(int13_old_flags - int13_handler)
	popfw

	movl	%cs:(int13_old_esi - int13_handler), %esi
	movw	%cs:(int13_old_ds - int13_handler), %ds
	movl	%cs:(int13_old_eax - int13_handler), %eax
	movl	%cs:(int13_old_ebp - int13_handler), %ebp
	movw	%cs:(int13_old_esp - int13_handler), %sp
	ljmp	*%cs:(int13_old_cs_ip - int13_handler)

	.align	4

int13_old_cs_ip:	.long	0
int13_old_eax:		.long	0
int13_old_ebx:		.long	0
int13_old_ecx:		.long	0
int13_old_edx:		.long	0
int13_old_esi:		.long	0
int13_old_edi:		.long	0
int13_old_esp:		.long	0
int13_old_ebp:		.long	0
int13_old_ds:		.word	0
int13_old_es:		.word	0
int13_old_flags:	.word	0
int13_new_bp:		.word	0

/****************************************************************************/
restricted_map:
	movw	%cs:(int13_old_eax - int13_handler), %ax

	/* CHS read functions */
	cmpb	$0x02, %ah	/* read sectors */
	je	2f
	cmpb	$0x04, %ah	/* verify sectors, also a read operation */
	je	2f
	cmpb	$0x0a, %ah	/* read long sectors */
	je	2f
	cmpb	$0x0c, %ah	/* seek to cylinder */
	je	2f
	cmpb	$0x21, %ah	/* PS/1 and newer PS/2 - read multiple disk sectors */
	jne	1f
2:
	movb	%cs:3(%bp), %ah	/* AH=Smax */
	testb	$63, %ah	/* check if Sectors=0, i.e., disable CHS */
	jz	error_01_disable
	ret
1:
	/* CHS write functions */
	cmpb	$0x03, %ah	/* CHS write sectors */
	je	2f
	cmpb	$0x05, %ah	/* PC/XT/AT/EISA format tracks */
	je	2f
	cmpb	$0x06, %ah	/* PC/XT format tracks with bad sectors */
	je	2f
	cmpb	$0x07, %ah	/* PC/XT format multiple cylinders */
	je	2f
	cmpb	$0x0b, %ah	/* PC/XT/AT/EISA write sectors with ECC */
	je	2f
	cmpb	$0x0f, %ah	/* PC/XT/PS/1 write sector buffer */
	je	2f
	cmpb	$0x22, %ah	/* PS/1 and newer PS/2 - write multiple disk sectors */
	jne	1f
2:
	movb	%cs:3(%bp), %ah	/* AH=Smax */
	testb	$63, %ah	/* check if Sectors=0, i.e., disable CHS */
	jz	error_01_disable
	testb	$0x80, %ah	/* readonly access? */
	jnz	readonly_fakewrite
	ret
1:
	/* LBA read functions */
	cmpb	$0x41, %ah	/* Extensions - INSTALLATION CHECK */
	je	2f
	cmpb	$0x42, %ah	/* Extensions - EXTENDED READ */
	je	2f
	cmpb	$0x44, %ah	/* Extensions - verify sectors */
	je	2f
	cmpb	$0x45, %ah	/* Extensions - LOCK/UNLOCK DRIVE */
	je	2f
	cmpb	$0x46, %ah	/* Extensions - EJECT MEDIA */
	je	2f
	cmpb	$0x47, %ah	/* Extensions - EXTENDED SEEK */
	je	2f
	cmpb	$0x48, %ah	/* Extensions - GET DRIVE PARAMETERS */
	je	2f
	cmpb	$0x49, %ah	/* Extensions - detect media change */
	je	2f
	cmpb	$0x4a, %ah	/* Bootable CDROM - INITIATE DISK EMULATION */
	je	2f
	cmpb	$0x4b, %ah	/* Bootable CDROM - TERMINATE DISK EMULATION */
	je	2f
	cmpb	$0x4c, %ah	/* Bootable CDROM - INITIATE DISK EMULATION AND BOOT */
	je	2f
	cmpb	$0x4d, %ah	/* Bootable CDROM - RETURN BOOT CATALOG */
	je	2f
	cmpb	$0x4e, %ah	/* Extensions v2.1 - SET HARDWARE CONFIGURATION */
	jne	1f
2:
	movb	%cs:3(%bp), %ah	/* AH=Smax */
	testb	$64, %ah	/* disable LBA? */
	jnz	error_01_disable
	ret
1:
	/* LBA write functions */
	cmpb	$0x43, %ah	/* Extensions - EXTENDED WRITE */
	jne	1f
2:
	movb	%cs:3(%bp), %ah	/* AH=Smax */
	testb	$64, %ah	/* disable LBA? */
	jnz	error_01_disable
	testb	$0x80, %ah	/* readonly access? */
	jnz	readonly_fakewrite
1:
	/* no restrictions, return and continue */
	ret

error_01_disable:
	/* function not supported, or the input CHS is invalid */
	movl	%cs:(int13_old_eax - int13_handler), %eax
	movb	$0x01, %ah	/* invalid function call */
1:
	pushw	%cs:(int13_old_flags - int13_handler)
	popfw
	stc			/* error */
	jmp	1f

readonly_fakewrite:
	testb	$0x40, %cs:7(%bp)	/* bit 6 of TO_S */
	movl	%cs:(int13_old_eax - int13_handler), %eax
	movb	$0x03, %ah	/* write protection */
	jz	1b		/* read only */
	xorb	%ah, %ah	/* fake write */
	pushw	%cs:(int13_old_flags - int13_handler)
	popfw
	clc			/* write succeeded */
1:
	movl	%cs:(int13_old_esi - int13_handler), %esi
	movw	%cs:(int13_old_ds - int13_handler), %ds
	movl	%cs:(int13_old_ebp - int13_handler), %ebp
	movw	%cs:(int13_old_esp - int13_handler), %sp
	ljmp	*%cs:(int13_old_cs_ip - int13_handler)


/****************************************************************************/
drive_emulation:
	movw	%cs:2(%bp), %ax	/* AL=Hmax, AH=Smax */
	testb	$63, %ah	/* disable CHS? */
	jz	2f		/* yes, call restricted map */
	testb	$0xc0, %ah	/* readonly or disable LBA? */
	jz	1f
2:
	call	restricted_map
1:
	movw	%cs:(int13_old_eax - int13_handler), %ax

	testb	%ah, %ah	/* reset disk system, always succeed */
	jnz	1f
	/*clc*/			/* CF already cleared by TEST */
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x01, %ah	/* get status, always succeed */
	jnz	1f
	xorb	%ah, %ah
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x04, %ah	/* verify sectors, always succeed */
	jnz	1f
	xorb	%ah, %ah
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x09, %ah /* INITIALIZE CONTROLLER WITH DRIVE PARAMETERS */
	jnz	1f
	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jnz	error_01_invalid	/* CDROM */
	xorb	%ah, %ah
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x0c, %ah	/* SEEK TO CYLINDER */
	jnz	1f
	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jnz	error_01_invalid	/* CDROM */
	xorb	%ah, %ah
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x0d, %ah	/* reset hard disks */
	jnz	1f
	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jnz	error_01_invalid	/* CDROM */
	xorb	%ah, %ah
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x10, %ah	/* check if drive ready */
	jnz	1f
	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jnz	error_01_invalid	/* CDROM */
	xorb	%ah, %ah
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x11, %ah	/* recalibrate drive */
	jnz	1f
	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jnz	error_01_invalid	/* CDROM */
	xorb	%ah, %ah
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x14, %ah	/* CONTROLLER INTERNAL DIAGNOSTIC */
	jnz	1f
	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jnz	error_01_invalid	/* CDROM */
	xorb	%ah, %ah
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x05, %ah	/* format track */
	jnz	1f
	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jnz	error_01_invalid	/* CDROM */

	/* CH=cylinder number (bits 8,9 in high bits of CL)
	 * CL=high bits of cylinder number (bits 7,6)
	 * DH=head number
	 * DL=drive number
	 */

	xorb	%ah, %ah	/* do nothing but return success */
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x08, %ah	/* get drive parameters */
	jnz	1f
	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jnz	error_01_invalid	/* CDROM */
	pushw	%ds
	xorw	%ax, %ax
	movw	%ax, %ds
	testb	%dl, %dl	/* hard drive? */
	movb	0x475, %dl	/* DL=number of hard drives */
	js	2f		/* yes, jump */
	movw	$0x10, %bx	/* for floppy, refer to function 0x48 */
	movb	0x410, %al
	rorb	$1, %al
	cbw
	shlb	$1, %al
	shrb	$6, %al
	incw	%ax
	andb	%ah, %al
	xchgw	%ax, %dx	/* DL=number of floppy drives */
	lesw	0x0078, %di	/* point to int1E floppy parameters */
2:
	popw	%ds
	movw	%cs:2(%bp), %ax	/* AL=Hmax, AH=Smax */
	movb	%al, %dh	/* max head number */
	andb	$63, %ah
	movb	%ah, %cl	/* max sector number */

	/* max cylinder number */

	pushl	%edx
	pushl	%ecx
	movzbl	%dh, %eax
	movzbl	%cl, %ecx
	incl	%eax
	mull	%ecx		/* EDX=0, EAX=sectors per cylinder */
	xchgl	%eax, %ecx

	movl	%cs:16(%bp), %eax	/* S_count_Lo */
	cmpl	$4, %eax
	ja	2f
	cmpl	$0, %cs:8(%bp)		/* StartLBA_Lo */
	jnz	2f
	/* map whole drive, use TO_C instead. */
	movw	%cs:4(%bp), %ax		/* TO_C */
	jmp	3f
2:
	decl	%eax
	//xorl	%edx, %edx
	divl	%ecx		/* EAX=max cylinder number */
3:
	popl	%ecx
	popl	%edx

	movb	%al, %ch	/* low 8 bits of cylinder */
	shlb	$6, %ah		/* high 2 bits of cylinder */
	orb	%ah, %cl

	xorw	%ax, %ax
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x15, %ah	/* get disk type */
	jnz	1f
	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jnz	error_01_invalid	/* CDROM */
	testb	%dl, %dl	/* hard drive? */
	js	2f		/* yes, jump */
	movb	$0x02, %ah	/* floppy (or other removable drive) with change-line support */
	clc
	jmp	int13_return
2:
	movb	$0x03, %ah	/* hard disk */

	/* CX:DX=total number of sectors */
	movw	%cs:16(%bp), %dx	/* lo word of S_count_Lo */
	movw	%cs:18(%bp), %cx	/* hi word of S_count_Lo */
	clc
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x16, %ah
	jnz	1f
	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jnz	error_01_invalid	/* CDROM */
	xorb	%ah, %ah	/* AH=0 means disk not changed */
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x17, %ah	/* set floppy type for format */
	jnz	1f
	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jnz	error_01_invalid	/* CDROM */
	movb	$0x03, %al	/* 1.44M drive, 1.44M floppy */
	xorb	%ah, %ah
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x18, %ah	/* set media type for format */
	jnz	1f
	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jnz	error_01_invalid	/* CDROM */
	testb	%dl, %dl	/* hard drive? */
	js	error_01_invalid
	pushw	%ax
	xorw	%ax, %ax
	movw	%ax, %es
	movw	$0x0078, %di
	movl	%es:(%di), %eax
	movw	%ax, %di
	shrl	$0x10, %eax
	movw	%ax, %es
	popw	%ax
	xorb	%ah, %ah
	jmp	int13_return
/****************************************************************************/
1:
	/* Now AH is neither 0 nor 1 */

	testb	$0xfc, %ah	/* CHS read/write sectors */
	jnz	1f

	/* so AH is either 2(for read) or 3(for write) */

	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jnz	error_01_invalid	/* CDROM */

	cmpw	$0x0301, %ax	/* is it write 1 sector? */
	jne	2f
	cmpw	$0x0001, %cx	/* write to cylinder 0, sector 1? */
	jne	2f
	cmpb	$0x01, %dh	/* write to head 0 or 1? */
	ja	2f
	/* cmpw	$0xaa55, %es:0x1fe(%bx)
	je	2f */
	testb	%dl, %dl
	js	3f		/* protect hard disk head 0 and 1 */
	testb	%dh, %dh	/* write to floppy head 0? */
	jne	2f		/* no, write permitted */
3:
	testb	$0x40, %cs:7(%bp)	/* TO_S, bit 6=fake write(safeboot) */
	jnz	readonly_fakewrite	/* fake the write */
2:
	cmpb	$0x7F, %al	/* check if sectors exceed 127 */
	ja	error_01_invalid
	testb	%al, %al	/* read 0 sectors not allowed */
	jz	error_01_invalid
	testb	$63, %cl	/* beginning sector number 0 is invalid */
	jz	error_01_invalid
	movb	%cs:3(%bp), %ah	/* AH=Smax */
	andb	$63, %ah
	pushw	%cx
	andb	$63, %cl
	cmpb	%ah, %cl	/* CL should not > max sector number */
	popw	%cx
	ja	error_01_invalid
	movb	%cs:2(%bp), %ah	/* AH=Hmax */
	cmpb	%ah, %dh	/* DH should not > max head number */
	ja	error_01_invalid

	pushw	%cs
	popw	%ds		/* DS=CS */

	movw	$(EBIOS_disk_address_packet - int13_handler), %si
	movw	$0x0010, (%si)	/* Disk Address Packet length */
	movb	%al, 2(%si)	/* number of sectors to transfer */
	movw	%bx, 4(%si)	/* offset */
	movw	%es, 6(%si)	/* segment */
	xorl	%eax, %eax	/* EAX=0 */
	movb	%ah, 3(%si)	/* sectors_hi_reserved */
	movl	%eax, 12(%si)	/* zero out hi 32 bits */
	movb	%ch, %al	/* cylinder number lo 8 bits */
	movb	%cl, %ah	/* CL holds higher 2 bits */
	shrb	$6, %ah		/* AH lower holds the 2 bits */
				/* EAX=cylinder number, <1024 */
	pushl	%ebx		/* save EBX */

	xorl	%ebx, %ebx	/* EBX=0 */
	movb	%cs:2(%bp), %bl	/* BL=Hmax */
	incw	%bx		/* EBX=total heads, <=256 */

	pushl	%edx
	mull	%ebx		/* EDX=0, EAX=tracks before this cylinder */
	popl	%edx

	xorw	%bx, %bx	/* EBX=0 */
	movb	%dh, %bl	/* EBX=head number */
	addl	%ebx, %eax	/* EAX=tracks before this head */
	movb	%cs:3(%bp), %bl	/* Max sector number */
	andb	$63, %bl	/* EBX=sectors per track */

	pushl	%edx
	mull	%ebx		/* EDX=0, EAX=sectors before this head */
	popl	%edx

	movb	%cl, %bl	/* sector number */
	andb	$63, %bl
	decb	%bl
	addl	%ebx, %eax	/* EAX=lo 32 bits of logical sector number */
	movl	%eax, 8(%si)

	popl	%ebx		/* restore EBX */

disk_address_packet_ready:

	/* DS=CS */

	/* start-sector-number(LBA) in DAP is still for FROM_DRIVE */

/****************************************************************************/
	/* 
	 * check if the request exceeds the boundary of the emulated disk.
	 *
	 * input:	DS:SI
	 * output:	CF=0, success, all sectors transferred
	 *		CF=1, failure, no sectors transferred
	 *		EAX changed
	 *
	 */
	cmpl	$1, %cs:16(%bp)		/* S_count_Lo */
	ja	2f
	cmpl	$0, %cs:8(%bp)		/* StartLBA_Lo */
	je	4f			/* map whole drive, no restrictions */
2:
	cmpl	$0, 12(%si)	/* hi 32-bit of the requested StartLBA */
	jnz	3f		/* non-zero is considered `too big' */
	movl	%cs:16(%bp), %eax	/* S_count_Lo */
	cmpl	%eax, 8(%si)	/* lo 32-bit of the requested StartLBA */
	jnb	3f
	subl	8(%si), %eax
	pushl	%ebx
	movzwl	2(%si), %ebx	/* requested sectors */
	cmpl	%ebx, %eax
	popl	%ebx
//	jnb	4f
//3:
//	stc
4:
/****************************************************************************/

	jc	3f		/* no sectors to transfer, fail */

	/* adjust start-sector-number(LBA) to access TO_DRIVE */
	movl	%cs:8(%bp), %eax	/* StartLBA_Lo */
	addl	%eax, 8(%si)
	adcl	$0, 12(%si)

	/* set drive number(TO_DRIVE) and function number(EBIOS) */
	movb	%cs:1(%bp), %dl		/* DL=TO_DRIVE */
	movb	%cs:(int13_old_eax - int13_handler + 1), %ah
				/* 0x02=read, 0x03=write */
	orb	$0x40, %ah	/* 0x42=EXT_read, 0x43=EXT_write */

	call	real_int13_service

	///* restore original start-sector-number(in the DAP) */
	//pushfw
	//movl	%cs:8(%bp), %eax	/* StartLBA_Lo */
	//subl	%eax, 8(%si)
	//sbbl	$0, 12(%si)
	//popfw

	jc	3f			/* failure */

	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jnz	4f			/* CDROM */
	movw	$(EBIOS_disk_address_packet - int13_handler), %si
	pushw	%cs
	popw	%ds
	call	modify_boot_sectors
4:
	movb	%cs:(int13_old_eax - int13_handler), %al
	xorb	%ah, %ah
	jmp	4f			/* success */

3:
	movw	$0x400, %ax	/* no sectors transferred */
	/* write back sectors transferred to original DAP for LBA access */
	cmpb	$0x40, %cs:(int13_old_eax - int13_handler + 1)
	jb	4f		/* CF=1, function 02 or 03, not an LBA call */

	movw	%cs:(int13_old_esi - int13_handler), %si
	movw	%cs:(int13_old_ds - int13_handler), %ds

	/* DS:SI -> original DAP */
	movb	%al, 2(%si)
	stc				/* failure */
4:
	movl	%cs:(int13_old_edx - int13_handler), %edx
	movl	%cs:(int13_old_ebx - int13_handler), %ebx
	movl	%cs:(int13_old_ecx - int13_handler), %ecx
	movl	%cs:(int13_old_edi - int13_handler), %edi
	movw	%cs:(int13_old_es - int13_handler), %es
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x41, %ah	/* EBIOS installation check */
	jnz	1f
	cmpw	$0x55aa, %bx
	jnz	error_01_invalid
//	testb	%dl, %dl
//	jns	error_01_invalid
	movw	$0xaa55, %bx
	movb	$0x21, %ah	/* major version 2.1(EDD-1.1) */
	movw	$0x01, %cx	/* support functions 42h,43h,44h,47h,48h */
	clc
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x42, %ah	/* EBIOS read sectors */
	jz	2f
	cmpb	$0x43, %ah	/* EBIOS write sectors */
	jnz	1f

	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jz	2f

	/* CDROM */
	movb	$0x03, %ah	/* write protection */
	stc			/* error */
	jmp	int13_return
2:
	/* get old SI, disk address packet */
	movw	%cs:(int13_old_esi - int13_handler), %si
	movl	(%si), %eax	/* packet length, sectors, etc. */
	testb	%ah, %ah
	jnz	error_01_invalid
	testb	$0xf0, %al
	jz	error_01_invalid
	shrl	$16, %eax
	testw	$0xff80, %ax
	jnz	error_01_invalid
	testb	%al, %al
	jz	error_01_invalid

	/* copy disk address packet to EBIOS_disk_address_packet */ 

	pushw	%es
	pushw	%cx
	pushw	%di

	movw	%cs, %ax
	movw	%ax, %es	/* ES=CS */

	movw	$(EBIOS_disk_address_packet - int13_handler), %di
	movw	$8, %cx		/* will copy only 16 bytes! */
	cld
	repz movsw

	popw	%di
	popw	%cx
	popw	%es

	/* set DS:SI */

	movw	%cs, %ax
	movw	%ax, %ds	/* DS=CS */
	movw	$(EBIOS_disk_address_packet - int13_handler), %si

	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jz	2f
	shlb	$2, 2(%si)
	movl	8(%si), %eax
	shldl	$2, %eax, 12(%si)
	shll	$2, 8(%si)
2:
	jmp	disk_address_packet_ready

/****************************************************************************/
1:
	cmpb	$0x44, %ah	/* EBIOS verify sectors */
	jnz	1f
	xorb	%ah, %ah
	clc
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x47, %ah	/* EBIOS seek */
	jnz	1f
	xorb	%ah, %ah
	clc
	jmp	int13_return
/****************************************************************************/
1:
	cmpb	$0x48, %ah	/* EBIOS GET DRIVE PARAMETERS */
	jnz	1f

	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jz	2f			/* normal disks */

	/* CDROM */
	/* get old SI, extended drive parameter table */
	movw	%cs:(int13_old_esi - int13_handler), %si
	cmpw	$26, (%si)
	jb	error_01_invalid

	movw	$26, (%si)	/* buffer length */
	movw	$0x00, 2(%si)		# no flags
	movw	$0x800, 24(%si)		# bytes per sect=2048
	xorl	%eax, %eax
	decw	%ax
	movl	%eax, 4(%si)		# cylinders=0xFFFF
	movb	$0, %ah
	movl	%eax, 8(%si)		# heads=0xFF
	movb	$15, %al
	movl	%eax, 12(%si)		# sectors per track=15
	movl	%eax, 20(%si)		# total sectors hi dword=0
	xorw	%ax, %ax		# CF cleared
	decl	%eax			# EAX=0xFFFFFFFF
	movl	%eax, 16(%si)		# total sectors lo dword
					# CF is cleared

	xorw	%ax, %ax	/* success, CF cleared */
	jmp	int13_return
2:
	/* get old SI, extended drive parameter table */
	movw	%cs:(int13_old_esi - int13_handler), %si
	movw	$26, (%si)	/* buffer length */
	movw	$2, 2(%si)	/* info */
	xorl	%eax, %eax
	movl	%eax, 8(%si)	/* total heads */
	movl	%eax, 12(%si)	/* sectors per track */
	movl	%eax, 16(%si)	/* total sectors */
	movl	%eax, 20(%si)	/* hi 32 bits of total sectors */
	pushl	%ebx
	xorl	%ebx, %ebx
	movw	%cs:2(%bp), %ax	/* AL=Hmax, AH=Smax */
	andb	$63, %ah
	movb	%ah, 12(%si)	/* sectors per track */
	movb	%ah, %bl
	xorb	%ah, %ah
	incw	%ax		/* total heads=Hmax+1 */
	movw	%ax, 8(%si)	/* total heads */
	pushl	%edx
	mulw	%bx		/* DX:AX=product, DX=0 */
	movw	%ax, %bx	/* BX=sectors per cylinder */
	movl	%cs:16(%bp), %eax	/* S_count_Lo */
	#;andb	$0xfe, %al
	movl	%eax, 16(%si)	/* total sectors */
	xorl	%edx, %edx	/* EDX:EAX=64bit total sectors */
	testw	%bx, %bx
	jz	2f
	divl	%ebx		/* EAX=quotient, EDX=residue */
2:
	testl	%edx, %edx
	popl	%edx
	popl	%ebx
	jz	2f
	incl	%eax
2:
	movl	%eax, 4(%si)	/* total cylinders */
	movw	$512, 24(%si)	/* bytes per sector */
	xorb	%ah, %ah
	/*clc*/			/* signal success, CF already cleared by XOR */
	jmp	int13_return

/****************************************************************************/
1:
	cmpw	$0x4B01, %ax	/* CDROM GET DISK EMULATION STATUS */
	jnz	1f

	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jz	error_01_invalid	/* normal disks have no 0x4B01 function */

	/* CDROM */
	pushw	%es
	pushw	%di
	movw	%cs:(int13_old_esi - int13_handler), %di	/* old SI */
	pushw	%ds
	popw	%es
	movw	$0x0013, %ax	/* packet size=13h, boot type=0 (no-emu) */
	cld
	stosw
	movb	%dl, %al	/* drive=DL, controller=0 */
	stosw

	pushl	%cs:EXT_C(lba_cd_boot) - int13_handler
	popw	%ax
	stosw
	popw	%ax
	stosw			/* LBA for no-emu image */

	xorw	%ax, %ax
	stosw			/* device specification */
	stosw			/* user buffer segment */
	stosw			/* load segment */
	movb	$4, %al
	stosw			/* sector count=4 */
				/* CHS makes no sense for no-emu */
	popw	%di
	popw	%es
	xorb	%ah, %ah	/* success, CF cleared */
	jmp	int13_return

/****************************************************************************/
1:
/****************************************************************************/
error_01_invalid:
	movb	$0x01, %ah	/* unsupported function call */
	stc			/* signal error */

int13_return:
	movw	%ax, %cs:(int13_old_eax - int13_handler)	/* status */
	jnc	1f
	orb	$1, %cs:(int13_old_flags - int13_handler)
	jmp	2f
1:
	andb	$0xFE, %cs:(int13_old_flags - int13_handler)
2:
	pushw	%cs:(int13_old_flags - int13_handler)
	popfw

	movl	%cs:(int13_old_eax - int13_handler), %eax
	movl	%cs:(int13_old_esi - int13_handler), %esi
	movw	%cs:(int13_old_ds - int13_handler), %ds
	movl	%cs:(int13_old_ebp - int13_handler), %ebp
	movw	%cs:(int13_old_esp - int13_handler), %sp
	ljmp	*%cs:(int13_old_cs_ip - int13_handler)

/****************************************************************************/
real_int13_service:

	/* AH = 0x42 or 0x43 */

	/* save return address to memory */
	popw	%cs:(int13_ret_IP - int13_handler)
	/* save AX to memory */
	movw	%ax, %cs:(int13_reg_AX - int13_handler)

	cmpb	$0xff, %dl	/* mem drive */
	jne	normal_disk_drive

	testw	$0x4000, %cs:4(%bp)	/* TO_C bit 14=TO has 2048-byte cdrom sector */
	jnz	normal_disk_drive

	/* handle memdrive */

	sti		/* for hardware interrupt or watchdog */
	cmpb	$0x42, %ah
	je	3f
	cmpb	$0x43, %ah
	je	3f
	stc
	jmp	*%cs:(int13_ret_IP - int13_handler)	//ret
	/* DS:SI points to disk address packet 	*/
	/* 	2(%si), byte, sectors(1-127) 	*/
	/* 	4(%si), word, offset 		*/
	/* 	6(%si), word, segment 		*/
	/* 	8(%si), qword, lba		*/
3:
	/* AH = 0x42 or 0x43 */
	sahf	/* Store AH into flags SF ZF xx AF xx PF xx CF */
	pushf
	movzwl	4(%si), %ebx	#;  BX=offset, EBX_high_word=0
	movzwl	6(%si), %eax	#;  AX=segment
	movl	8(%si), %ecx	#; ECX=LBA of MEMDRIVE SECTOR
	shll	$9, %ecx	#; ECX=linear address of SECTOR(above 1M)
	shll	$4, %eax	#; EAX=linear base address of segment
	addl	%ebx, %eax	#; EAX=linear address of BUFFER(below 1M)
	popf
	jc	4f	/* write */
	xchgl	%eax, %ecx
4:
	/* Data transfer: (%eax) -> (%ecx), number of sectors 2(%si) */
	movl	%eax, %cs:(int13_data_addr_from - int13_handler)
	movl	%ecx, %cs:(int13_data_addr_to - int13_handler)

	cmpl	$0, %cs:(EXT_C(memdisk_raw) - int13_handler)
	je	4f		/* do not use raw mode */

	/* raw mode as in memdisk, contributed by Bean */

//	pushw	%ax
	smsw	%bx
	testb	$1, %bl
//	popw	%ax
	jnz	4f		/* protected mode */

	/* switch to protected mode myself */
	/* ebx destroy */
	
	//pushw	%ds
	//pushw	%es
	//pushl	%eax
	//pushl	%ecx

	//cli

	#;xorl	%ebx, %ebx
	movw	%cs, %bx	#; EBX_high_word=0
	shll	$4, %ebx
	addl	$(MyGDT - int13_handler), %ebx
	movl	%ebx, %cs:MyGDT - int13_handler + 2

	movzbl	2(%si), %ebx
	shll	$9, %ebx
	movl	%ebx, %edx
	addl	%eax, %ebx
	decl	%ebx
	orl	%eax, %ebx
	addl	%ecx, %edx
	decl	%edx
	orl	%ecx, %edx
	orl	%ebx, %edx
	testl	$0x100000, %edx	# zero means data inside an even mega
	setz	%dl		# we think of it as if A20 were on
	jz	3f		# no need to enable A20

	pushw	%dx
	movw	$0x00ff, %cx		# try so many times on failure
	movw	$0x0001, %dx		# DL=enable A20, DH=debug off

	cli	/* yes, keep interrupt off when controlling A20 */
	call	enable_disable_a20
	sti

	popw	%dx
	jz	1f		/* success */

	/* A20 control failed. */

	# notify the user
	movzbw	%cs:(%bp), %ax		/* FROM_DRIVE */
	pushw	%ax
	pushw	$a20_failure - int13_handler	# the format string
	call	realmode_printf
	addw	$4, %sp			# adjust the stack pointer

	//popl	%ecx
	//popl	%eax
	//popw	%es
	//popw	%ds

	//jmp	4f		/* try once more with int15/ah=87h */

	stc
	jmp	*%cs:(int13_ret_IP - int13_handler)	//ret

a20_failure:
	.ascii	"\r\ngrub4dos: A20 failure on memdrive=0x%X.\r\n\0"

1:
	/* CF=1 means A20 was originally enabled. */
	setc	%dl
	movb	$0, %dh

3:
	movw	$(EBIOS_disk_address_packet - int13_handler), %si
	pushw	%cs
	popw	%ds
	//popl	%ecx
	//popl	%eax
	movzbl	2(%si), %ecx	#; ECX=number of sectors to transfer
	movl	%cs:(int13_data_addr_to - int13_handler), %edi
	movl	%cs:(int13_data_addr_from - int13_handler), %esi
				#; ESI changed!!

	shll	$7, %ecx	/* 128 dwords per sector */

	cli
	lgdt	%cs:MyGDT - int13_handler
	movl	%cr0, %eax
	andl	$0x0000FFFF, %eax
	orb	$1, %al
	movl	%eax, %cr0	/* Switch to protected mode */

//	jmp	1f
//1:
//	jmp	1f
//1:


	movw	$16, %bx	/* Switch to 4G data segment */
	movw	%bx, %ds
	movw	%bx, %es

//	jmp	1f
//1:
//	jmp	1f
//1:


	cld

	addr32	rep movsl	/* ESI, EDI changed! */

	andb	$0xFE, %al
	movl	%eax, %cr0	/* Back to real mode */
	
//	jmp	1f
//1:
//	jmp	1f
//1:
	sti

	//popw	%es
	//popw	%ds

	cmpl	$0, %cs:(EXT_C(a20_keep_on) - int13_handler)
	jne	1f	/* Keep A20 on. This should hurt nothing. */

	/* Disable A20 if necessary ! */
	andw	%dx, %dx	/* 0=orig A20 off, 1=orig A20 on */
	jnz	1f

	movw	$0x0004, %cx		# try so many times on failure
	//movw	$0x0000, %dx		# DL=disable A20, DH=debug off
	cli	/* yes, keep interrupt off when controlling A20 */
	call	enable_disable_a20
	sti

1:
	clc
	jmp	*%cs:(int13_ret_IP - int13_handler)	//ret
4:
	movb	2(%si), %bl	/* number of sectors to be moved */
	pushw	%cs
	popw	%es
	movw	$(GDT_data - int13_handler), %si /* SI changed!! */
	movw	%ax, %es:0x12(%si)	#; source physical address low 16 bits
	shrl	$16, %eax
	movb	%al, %es:0x14(%si)	#; source physical address bit 16-23
	movb	%ah, %es:0x17(%si)	#; source physical address bit 24-32
	movw	%cx, %es:0x1a(%si)	#; dest physical address low 16 bits
	shrl	$16, %ecx
	movb	%cl, %es:0x1c(%si)	#; dest physical address bit 16-23
	movb	%ch, %es:0x1f(%si)	#; dest physical address bit 24-32

	xorw	%cx, %cx	/* ECX is 0 */
	movl	%ecx, %es:(%si)
	movl	%ecx, %es:0x04(%si)
	movl	%ecx, %es:0x08(%si)
	movl	%ecx, %es:0x0c(%si)
	movl	%ecx, %es:0x20(%si)
	movl	%ecx, %es:0x24(%si)
	movl	%ecx, %es:0x28(%si)
	movl	%ecx, %es:0x2c(%si)
	movb	%bl, %ch	/* CX=number of words to be moved */
	movb	$0x87, %ah	/* access extended memory */

	pushw	%ax
	smsw	%ax
	testb	$1, %al
	popw	%ax
	jnz	4f		/* protected mode */

	/* real mode */
	pushfw
	lcall	%cs:*(EXT_C(ROM_int15) - int13_handler)
	
	jmp	6f
4:
	/* protected mode */
	int	$0x15
6:
	jmp	*%cs:(int13_ret_IP - int13_handler)	//ret

/****************************************************************************/
normal_disk_drive:

	/* handle normal disk drive */

	/* AH = 0x42 or 0x43 */
	pushw	%ax
	smsw	%ax
	testb	$1, %al
	popw	%ax
	jz	3f	// real mode

	/* protected mode(Windows 98, EMM386) */

	pushw	%si		/* save SI */
	pushl	%eax		/* save EAX */
	pushl	%ebx		/* save EBX */

	/* set SI to the drive map */
	movw	$(EXT_C(hooked_drive_map) - int13_handler), %si
	/* find the drive number from the drive map */
	cld
	subw	$DRIVE_MAP_SLOT_SIZE - 4, %si
2:	
	addw	$DRIVE_MAP_SLOT_SIZE - 4, %si
	lodsl	%cs:(%si), %eax
	testl	%eax, %eax	/* end of map table? */
	movl	%eax, %ebx	/* save the map to EBX */
	jz	2f		/* yes, no map found */
	cmpb	%dl, %ah	/* found the map? */
	jne	2b		/* no, check the next slot */

	/* drive is mapped. check if map a whole drive */
	shrl	$16, %eax
	testb	$62, %ah
	jnz	2b			/* no, check the next slot */
	movl	%cs:4(%si), %eax	/* StartLBA_Lo */
	testl	%eax, %eax
	jnz	2b			/* no, check the next slot */
	movl	%cs:12(%si), %eax	/* S_count_Lo */
	shrl	$1, %eax
	jnz	2b		/* no, check the next slot */
2:
	testl	%ebx, %ebx	/* mapped or not mapped ? */
	jz	2f		/* not mapped, do nothing */
	movb	%bl, %dl	/* use the mapped FROM_DRIVE for win 98 */
2:
	movb	%cs:(%bp), %al	/* AL=FROM_DRIVE */
	testb	%al, %al	/* hard drive emulation? */
	jns	2f		/* floppy, jump */
	cmpb	%al, %dl
	jb	2f
	incb	%dl
2:
	popl	%ebx
	popl	%eax
	popw	%si

	/* fall through to real mode... */

3:

	/* in real mode DOS, call original real mode int13 */
	/* DS:SI points to disk address packet 	*/
	/* 	2(%si), byte, sectors(1-127) 	*/
	/* 	4(%si), word, offset 		*/
	/* 	6(%si), word, segment 		*/
	/* 	8(%si), qword, lba		*/

	testw	$0x4000, %cs:4(%bp)	/* TO_C bit 14=TO has 2048-byte cdrom sector */
	jz	1f

	/* LBA supported, CHS not applicable for CDROM */

	movw	%es, %cs:(int13_cdrom_es - int13_handler)
	movw	%cx, %cs:(int13_cdrom_cx - int13_handler)
	movl	%ebx, %cs:(int13_cdrom_ebx - int13_handler)
	movl	%edi, %cs:(int13_cdrom_edi - int13_handler)

	movzbw	2(%si), %cx	/* sectors to transfer */
	movl	8(%si), %edi	/* start sector number(LBA) */
	movl	12(%si), %ebx
3:
	/* read 1 small sector at LBA=EDI to edd30_disk_buffer */

	/* if we have previously read it, we can skip this step now. */
	cmpb	%dl, %cs:last_read_cd_drive - int13_handler
	jne	2f
	cmpl	%ebx, %cs:last_read_sector - int13_handler + 4
	jne	2f
	movl	%edi, %eax
	andb	$0xFC, %al
	cmpl	%eax, %cs:last_read_sector - int13_handler	#; // + 4
	je	4f
2:
	movl	(%si), %eax
	movl	%eax, %cs:(tmp_dap - int13_handler)
	movl	4(%si), %eax
	movl	%eax, %cs:(tmp_dap - int13_handler + 4)
	movl	8(%si), %eax
	movl	%eax, %cs:(tmp_dap - int13_handler + 8)
	movl	12(%si), %eax
	movl	%eax, %cs:(tmp_dap - int13_handler + 12)

	movl	%edi, 8(%si)
	movl	%ebx, 12(%si)
	shrdl	$2, %ebx, 8(%si)	/* turn LBA small to LBA big */
	shrl	$2, 12(%si)

	movb	$1, 2(%si)		/* read 1 big sector */

	//pushw	%es
	movw	%bx, %cs:(int13_cdrom_bx - int13_handler)
	movw	%cs, %ax
	movw	%ax, %es
	movw	%ax, 6(%si)		/* set the buffer segment */
	movw	$edd30_disk_buffer - int13_handler, %bx
	movw	%bx, 4(%si)		/* set the buffer offset */
	movw	%cs:(int13_reg_AX - int13_handler), %ax

	/* check if DL is for anyone of (cd?)'s */
	cmpb	$0, %cs:(EXT_C(atapi_dev_count) - int13_handler)
	jz	2f			/* no cdX'es */
	cmpb	%cs:(EXT_C(min_cdrom_id) - int13_handler), %dl
	jb	2f			/* not cdX */
	cmpb	%cs:(max_cdrom_id - int13_handler), %dl
	ja	2f			/* not cdX */
	/* read 1 cdrom sector using our builtin cdrom driver. */
	movb	$1, %cs:(force_int13 - int13_handler)
2:
	call	int13_with_retry	/* read a big 2048-byte sector */

	movb	$0, %cs:(force_int13 - int13_handler)

	movw	%cs:(int13_cdrom_bx - int13_handler), %bx
	//popw	%es
	jc	3f			/* failed */

	movl	%cs:(tmp_dap - int13_handler), %eax
	movl	%eax, (%si)
	movl	%cs:(tmp_dap - int13_handler + 4), %eax
	movl	%eax, 4(%si)
	movl	%cs:(tmp_dap - int13_handler + 8), %eax
	movl	%eax, 8(%si)
	movl	%cs:(tmp_dap - int13_handler + 12), %eax
	movl	%eax, 12(%si)

	pushw	%di
	andw	$0xFFFC, %di
	movl	%edi, %cs:last_read_sector - int13_handler
	popw	%di
	movl	%ebx, %cs:last_read_sector - int13_handler + 4
	movb	%dl, %cs:last_read_cd_drive - int13_handler
4:
	pushw	%cx
	pushw	%bx
	pushw	%di

	/* calculate the buffer ES:BX */
	//movw	%di, %ax
	subw	8(%si), %di	/* sectors already read */
	shlw	$5, %di		/* paragraghs */
	addw	6(%si), %di	/* segment */
	movw	4(%si), %bx	/* offset */
	movw	%bx, %ax
	shrw	$4, %ax		/* turn to paragraghs */
	andw	$0x000F, %bx
	addw	%di, %ax	/* segment */
	movw	%ax, %es

	movw	%bx, %di
	popw	%ax		/* AX=old DI */
	pushw	%ax

	andb	$3, %al
	shlw	$9, %ax		/* offset in edd30_disk_buffer */

	addw	$edd30_disk_buffer - int13_handler, %ax

	xchgw	%ax, %si

	/* move 512 bytes */
	movw	$0x100, %cx
	cld
	cs repz movsw

	xchgw	%ax, %si

	popw	%di
	popw	%bx

	incl	%edi		/* next sector */
	jnz	2f
	incl	%ebx
2:

	popw	%cx
	decw	%cx
	jnz	3b
//	loop	3b

	movw	%cs:(int13_cdrom_es - int13_handler), %es
	movw	%cs:(int13_cdrom_cx - int13_handler), %cx
	movl	%cs:(int13_cdrom_ebx - int13_handler), %ebx
	movl	%cs:(int13_cdrom_edi - int13_handler), %edi
	clc
	jmp	*%cs:(int13_ret_IP - int13_handler)	//ret
3:
	movw	%cs:(int13_cdrom_es - int13_handler), %es
	movw	%cs:(int13_cdrom_cx - int13_handler), %cx
	movl	%cs:(int13_cdrom_ebx - int13_handler), %ebx
	movl	%cs:(int13_cdrom_edi - int13_handler), %edi
	stc
	jmp	*%cs:(int13_ret_IP - int13_handler)	//ret

/* cache 1 big 2048-byte sector at edd30_disk_buffer */

last_read_cd_drive:
	.byte	0	#; a value < 0x80 normally invalidate the cache

	.align	4
tmp_dap:
	.long	0
	.long	0
	.long	0
	.long	0

last_read_sector: /* set it to 0xFFFFFFFFFFFFFFFF to invalidate the cache */
	.long	0xFFFFFFFF	#; lo dword. for a valid cache, lowest 2 bits=0
	.long	0xFFFFFFFF	#; hi dword

int13_data_addr_from:
	.long	0
int13_data_addr_to:
	.long	0
int13_cdrom_edi:
	.long	0
int13_cdrom_ebx:
	.long	0
int13_cdrom_cx:
	.word	0
int13_cdrom_bx:
	.word	0
int13_cdrom_es:
	.word	0

1:
	#;jmp	1f	/* just check if CHS translation code works */
	testw	$0x8000, %cs:4(%bp)	/* TO_C bit 15=LBA support */
#if 0
	jnz	int13_with_retry	/* LBA mode */
#else
	jz	1f			/* CHS only, so skip the LBA access */
	movw	%es, %cs:(int13_tmp_es_bx - int13_handler + 2)
	movw	%bx, %cs:(int13_tmp_es_bx - int13_handler)
	movw	4(%si), %bx
	shrw	$4, %bx
	addw	%bx, 6(%si)
	andw	$0x000F, 4(%si)
	cmpb	$0x80, 2(%si)
	jb	2f			/* 0x7F sectors or less is ok */
	ja	3f			/* 0x81 sectors or more is bad */

	/* now 0x80 sectors requested. */

	testw	$0x2000, %cs:4(%bp)	/* TO_C bit 13=FROM has 2048-byte cdrom sector */
	jz	3f			/* not CDROM, fail out. */
	/* virtual cdrom function call could request 64K data each time */
	/* transfer 0x80 sectors = twice 0x40 sectors */
	movb	$0x40, 2(%si)		/* transfer the first 32K */
	movw	4(%si), %bx
	movw	6(%si), %es
	call	int13_with_retry
	jc	4f
	movb	$0x40, 2(%si)
	addw	$0x800, 6(%si)		/* step to next 32K of the buffer */
	movw	4(%si), %bx
	movw	6(%si), %es
	pushl	%eax
	xorl	%eax, %eax
	movb	$0x40, %al
	addl	%eax, 8(%si)		/* adjust start_LBA */
	movb	$0, %al
	adcl	%eax, 12(%si)
	popl	%eax
	call	int13_with_retry
	/* we ignore this step and keep start_LBA in a modified state. This is
	 * because only modify_boot_sectors need start_LBA and we are accessing
	 * the virtual cdrom, so we will not call modify_boot_sectors.
	 */
	//pushfw
	//pushl	%eax
	//xorl	%eax, %eax
	//movb	$0x40, %al
	//subl	%eax, 8(%si)		/* adjust start_LBA */
	//movb	$0, %al
	//sbbl	%eax, 12(%si)
	//popl	%eax
	//popfw
4:
	movb	$0x80, 2(%si)		/* restore its original value */
	lesw	%cs:(int13_tmp_es_bx - int13_handler), %bx
	movw	%bx, 4(%si)		/* restore its original value */
	movw	%es, 6(%si)		/* restore its original value */
	jmp	*%cs:(int13_ret_IP - int13_handler)	//ret
	
2:
	movw	4(%si), %bx
	movw	6(%si), %es
	call	int13_with_retry
	lesw	%cs:(int13_tmp_es_bx - int13_handler), %bx
	movw	%bx, 4(%si)		/* restore its original value */
	movw	%es, 6(%si)		/* restore its original value */
	jnc	4f
	testw	$0x1000, %cs:4(%bp)	/* TO_C bit 12=BIFURCATE */
	jz	1f	/* not bifurcate, use CHS access once more. */
	stc		/* bifurcate, error out. */
4:
	jmp	*%cs:(int13_ret_IP - int13_handler)	//ret

3:
	movb	$1, %ah
	stc
	jmp	*%cs:(int13_ret_IP - int13_handler)	//ret

	.align	4
int13_tmp_es_bx:	.long	0

1:
#endif
	/* CHS mode */

	/* byte at SI+2: number of sectors to access */
	/* 8 bytes at SI+8: StartLBA */

	/* CHS mode cannot access large addresses */
	cmpl	$0, 12(%si)
	jnz	1f

	pushl	%edx
	pushl	%ebx
	movw	%cs:4(%bp), %ax	/* TO_C */
	andw	$0x3FF, %ax	/* get lo 10 bits */
	incw	%ax		/* cylinders */
	pushw	%ax
	movzbw	%cs:6(%bp), %ax	/* TO_H */
	incw	%ax		/* heads */
	movzbw	%cs:7(%bp), %bx	/* TO_S */
	andb	$0x3F, %bl
	mulw	%bx		/* DX=0, AX=heads*sectors */
	popw	%bx		/* cylinders */
	mulw	%bx		/* DX:AX=total sectors in drive */
	pushw	%dx
	pushw	%ax
	movzbl	2(%si), %eax	/* number of sectors to access */
	addl	8(%si), %eax	/* last sector number + 1 */
	popl	%edx		/* total sectors in drive */
	cmpl	%edx, %eax
	popl	%ebx
	popl	%edx
	jnb	1f

	/* all requested sectors can be accessed by CHS */

	/* we will access one sector at a time */

	movzbw	2(%si), %cx	/* sectors to transfer */
	movl	8(%si), %edi	/* start sector number(LBA) */
3:
	/* translate LBA to CHS */

	//pushw	%cx
	movw	%cx, %cs:(int13_chs_cx - int13_handler)

	/* get sectors per cylinder */

	//pushw	%dx
	movw	%dx, %cs:(int13_chs_dx - int13_handler)

	pushl	%edi		/* lba */
	movzbw	%cs:6(%bp), %ax	/* TO_H */
	incw	%ax		/* heads */
	movzbw	%cs:7(%bp), %bx	/* TO_S */
	andb	$0x3F, %bl
	mulw	%bx		/* DX=0, AX=sectors per cylinder */
	popw	%cx		/* lba_lo */
	xchgw	%ax, %cx	/* CX=sectors per cylinder, AX=lba_lo */
	popw	%dx		/* DX:AX=lba */

	divw	%cx		/* AX=cylinder number, DX=rem */
	xchgw	%ax, %dx	/* DX=cylinder number, AX=rem */

	movb	%dl, %ch	/* CH=lo 8 bits of cylinder */

	divb	%bl		/* AL=head number, AH=sector number - 1 */
	movb	%ah, %cl
	incw	%cx		/* CL=sector number */
	shlb	$6, %dh		/* hi 2 bits of cylinder */
	orb	%dh, %cl

	movw	%cs:(int13_chs_dx - int13_handler), %dx	/* DL=drive number */
	//popw	%dx		/* DL=drive number */
	//pushw	%dx

	movb	%al, %dh	/* DH=head number */

	//pushl	%edi
	movl	%edi, %cs:(int13_chs_edi - int13_handler)

	//movw	%di, %ax
	subw	8(%si), %di	/* sectors already read */
	shlw	$5, %di		/* paragraghs */
	addw	6(%si), %di	/* segment */
	movw	4(%si), %bx	/* offset */
	movw	%bx, %ax
	shrw	$4, %ax		/* turn to paragraghs */
	andw	$0x000F, %bx
	addw	%di, %ax	/* segment */
	movw	%ax, %es

	movb	%cs:(int13_old_eax - int13_handler + 1), %ah
				/* 0x42/0x02=read, 0x43/0x03=write */
	andb	$0x03, %ah	/* AH=0x02 or 0x03 */
	movb	$0x01, %al	/* number of sectors to read/write */

	call	int13_with_retry

	movl	%cs:(int13_chs_edi - int13_handler), %edi
	movw	%cs:(int13_chs_dx - int13_handler), %dx
	//popl	%edi
	//popw	%dx

	incl	%edi		/* next sector */

	movw	%cs:(int13_chs_cx - int13_handler), %cx
	//popw	%cx
	jc	1f
	loop	3b

	jmp	*%cs:(int13_ret_IP - int13_handler)	//ret
1:
	stc
	jmp	*%cs:(int13_ret_IP - int13_handler)	//ret

	.align	2
int13_ret_IP:
	.word	0
int13_reg_AX:
	.word	0
int13_chs_cx:
	.word	0
int13_chs_dx:
	.word	0

	.align	4
int13_chs_edi:
	.long	0

/****************************************************************************/
int13_with_retry:

	/* save return address to memory */
	popw	%cs:(int13_retry_IP - int13_handler)
//	/* backup the last DWORD in the buffer */
//	pushl	%es:0x1FC(%bx)
//	popl	%cs:(sector_last_dword - int13_handler)

	/* retry count should be an odd number initially */
	movb	$5, %cs:(retry_count - int13_handler)

	cmpb	$0, %cs:(force_int13 - int13_handler)
	jnz	3f	/* we should use current int 13 instead of ROM_int13 */
	call	backup_int13
3:
	movb	%ah, %cs:(int13_retry_ah - int13_handler)
	call	int13_simple

	jnc	3f		/* success */

//	/* if the last dword changed, consider it is success */
//
//	pushl	%eax
//	movl	%es:0x1FC(%bx), %eax
//	cmpl	%eax, %cs:(sector_last_dword - int13_handler)
//	popl	%eax
//
//	jne	3f		/* success */

	decb	%cs:(retry_count - int13_handler)
	jz	2f		/* finally failed */

	/* reset disk and try again */
	movb	$0, %cs:(int13_retry_ah - int13_handler)
	call	int13_simple

//	testb	$1, %cs:(int13_old_eax - int13_handler + 1)
//				/* 0x42/0x02=read, 0x43/0x03=write */
//	jnz	3b		/* it is write */
//
//	/* touch the last dword of the buffer */
//	notl	%es:0x1FC(%bx)
//	notl	%cs:(sector_last_dword - int13_handler)

	jmp	3b		/* try again, ignoring the reset failure */
2:
	stc			/* failure */
	jmp	2f
3:
	clc			/* success */
2:
	pushfw

	cmpb	$0, %cs:(force_int13 - int13_handler)
	jnz	2f	/* we have not touched the int 13 vector */
	call	restore_int13
2:
	popfw
	jmp	*%cs:(int13_retry_IP - int13_handler)	//ret

backup_int13:

	/* backup the current int 13 to tmp_int13, then install ROM_int13 */
	cli
	pushw	%ds
	pushl	%eax
	xorw	%ax, %ax
	movw	%ax, %ds
	movl	0x4C, %eax	/* current int 13 vector */
	movl	%eax, %cs:(tmp_int13 - int13_handler)
	movl	%cs:(ROM_int13 - int13_handler), %eax
	movl	%eax, 0x4C
	popl	%eax
	popw	%ds
	ret

restore_int13:

	/* restore the current int 13 from tmp_int13 */
	cli
	pushw	%ds
	pushl	%eax
	xorw	%ax, %ax
	movw	%ax, %ds
	movl	%cs:(tmp_int13 - int13_handler), %eax
	movl	%eax, 0x4C
	popl	%eax
	popw	%ds
	ret

retry_count:
	.byte	5

int13_retry_ah:
	.byte	0
force_int13:
	.byte	0

	.align	2
int13_retry_IP:
	.word	0
int13_retry_ds:
	.word	0
int13_retry_es:
	.word	0

	.align	4
int13_retry_eax:
	.long	0
int13_retry_ebx:
	.long	0
int13_retry_ecx:
	.long	0
int13_retry_edx:
	.long	0
int13_retry_esi:
	.long	0
int13_retry_edi:
	.long	0
int13_retry_ebp:
	.long	0
tmp_int13:
	.long	0
//sector_last_dword:
//	.long	0

/****************************************************************************/
int13_simple:

	/* input:	CF=0	reset disk	*/

	/* save return address to memory */
	popw	%cs:(int13_simple_IP - int13_handler)

	movl	%eax, %cs:(int13_retry_eax - int13_handler)
	movl	%ebx, %cs:(int13_retry_ebx - int13_handler)
	movl	%ecx, %cs:(int13_retry_ecx - int13_handler)
	movl	%edx, %cs:(int13_retry_edx - int13_handler)
	movl	%esi, %cs:(int13_retry_esi - int13_handler)
	movl	%edi, %cs:(int13_retry_edi - int13_handler)
	movl	%ebp, %cs:(int13_retry_ebp - int13_handler)
	movw	%ds, %cs:(int13_retry_ds - int13_handler)
	movw	%es, %cs:(int13_retry_es - int13_handler)

	//sti

	cmpb	$0, %cs:(force_int13 - int13_handler)
	jz	3f
	/* read 1 cdrom sector using our builtin cdrom driver. */

	/* backup old variables to bak variables */
	movl	%cs:(int13_old_eax - int13_handler), %eax
	movl	%eax, %cs:(int13_bak_eax - int13_handler)
	movl	%cs:(int13_old_ebx - int13_handler), %eax
	movl	%eax, %cs:(int13_bak_ebx - int13_handler)
	movl	%cs:(int13_old_ecx - int13_handler), %eax
	movl	%eax, %cs:(int13_bak_ecx - int13_handler)
	movl	%cs:(int13_old_edx - int13_handler), %eax
	movl	%eax, %cs:(int13_bak_edx - int13_handler)
	movl	%cs:(int13_old_esi - int13_handler), %eax
	movl	%eax, %cs:(int13_bak_esi - int13_handler)
	movl	%cs:(int13_old_edi - int13_handler), %eax
	movl	%eax, %cs:(int13_bak_edi - int13_handler)
	movl	%cs:(int13_old_ebp - int13_handler), %eax
	movl	%eax, %cs:(int13_bak_ebp - int13_handler)
	movw	%cs:(int13_old_ds - int13_handler), %ax
	movw	%ax, %cs:(int13_bak_ds - int13_handler)
	movw	%cs:(int13_old_es - int13_handler), %ax
	movw	%ax, %cs:(int13_bak_es - int13_handler)
	movw	%cs:(int13_old_flags - int13_handler), %ax
	movw	%ax, %cs:(int13_bak_flags - int13_handler)
	movl	%cs:(int13_old_cs_ip - int13_handler), %eax
	movl	%eax, %cs:(int13_bak_cs_ip - int13_handler)

	/* setup old variables for use by edd30_for_cdrom */

	/* edd30_for_cdrom far return address */
	movw	%cs, %cs:(int13_old_cs_ip + 2 - int13_handler)
	movw	$(2f - int13_handler), %cs:(int13_old_cs_ip - int13_handler)
	/* edd30_for_cdrom flags */
	pushfw
	popw	%cs:(int13_old_flags - int13_handler)
	movw	%cs:(int13_retry_es - int13_handler), %ax
	movw	%ax, %cs:(int13_old_es - int13_handler)
	movw	%cs:(int13_retry_ds - int13_handler), %ax
	movw	%ax, %cs:(int13_old_ds - int13_handler)
	movl	%cs:(int13_retry_ebp - int13_handler), %eax
	movl	%eax, %cs:(int13_old_ebp - int13_handler)
	movl	%cs:(int13_retry_edi - int13_handler), %eax
	movl	%eax, %cs:(int13_old_edi - int13_handler)
	movl	%cs:(int13_retry_esi - int13_handler), %eax
	movl	%eax, %cs:(int13_old_esi - int13_handler)
	movl	%cs:(int13_retry_edx - int13_handler), %eax
	movl	%eax, %cs:(int13_old_edx - int13_handler)
	movl	%cs:(int13_retry_ecx - int13_handler), %eax
	movl	%eax, %cs:(int13_old_ecx - int13_handler)
	movl	%cs:(int13_retry_ebx - int13_handler), %eax
	movl	%eax, %cs:(int13_old_ebx - int13_handler)
	movl	%cs:(int13_retry_eax - int13_handler), %eax
	movl	%eax, %cs:(int13_old_eax - int13_handler)

	movb	%cs:(int13_retry_ah - int13_handler), %ah
	jmp	edd30_for_cdrom		/* will return at 2f */
2:
	/* restore old variables from bak variables */
	movl	%cs:(int13_bak_eax - int13_handler), %eax
	movl	%eax, %cs:(int13_old_eax - int13_handler)
	movl	%cs:(int13_bak_ebx - int13_handler), %eax
	movl	%eax, %cs:(int13_old_ebx - int13_handler)
	movl	%cs:(int13_bak_ecx - int13_handler), %eax
	movl	%eax, %cs:(int13_old_ecx - int13_handler)
	movl	%cs:(int13_bak_edx - int13_handler), %eax
	movl	%eax, %cs:(int13_old_edx - int13_handler)
	movl	%cs:(int13_bak_esi - int13_handler), %eax
	movl	%eax, %cs:(int13_old_esi - int13_handler)
	movl	%cs:(int13_bak_edi - int13_handler), %eax
	movl	%eax, %cs:(int13_old_edi - int13_handler)
	movl	%cs:(int13_bak_ebp - int13_handler), %eax
	movl	%eax, %cs:(int13_old_ebp - int13_handler)
	movw	%cs:(int13_bak_ds - int13_handler), %ax
	movw	%ax, %cs:(int13_old_ds - int13_handler)
	movw	%cs:(int13_bak_es - int13_handler), %ax
	movw	%ax, %cs:(int13_old_es - int13_handler)
	movw	%cs:(int13_bak_flags - int13_handler), %ax
	movw	%ax, %cs:(int13_old_flags - int13_handler)
	movl	%cs:(int13_bak_cs_ip - int13_handler), %eax
	movl	%eax, %cs:(int13_old_cs_ip - int13_handler)
	/* eax changed but no problem */

	jmp	2f
3:
	movb	%cs:(int13_retry_ah - int13_handler), %ah
	int	$0x13
2:
	movw	%cs:(int13_retry_ds - int13_handler), %ds
	movw	%cs:(int13_retry_es - int13_handler), %es
	movl	%cs:(int13_retry_eax - int13_handler), %eax
	movl	%cs:(int13_retry_ebx - int13_handler), %ebx
	movl	%cs:(int13_retry_ecx - int13_handler), %ecx
	movl	%cs:(int13_retry_edx - int13_handler), %edx
	movl	%cs:(int13_retry_esi - int13_handler), %esi
	movl	%cs:(int13_retry_edi - int13_handler), %edi
	movl	%cs:(int13_retry_ebp - int13_handler), %ebp

	jmp	*%cs:(int13_simple_IP - int13_handler)	//ret

	.align	2
int13_simple_IP:
	.word	0

	.align	4
int13_bak_cs_ip:	.long	0
int13_bak_eax:		.long	0
int13_bak_ebx:		.long	0
int13_bak_ecx:		.long	0
int13_bak_edx:		.long	0
int13_bak_esi:		.long	0
int13_bak_edi:		.long	0
int13_bak_ebp:		.long	0
int13_bak_ds:		.word	0
int13_bak_es:		.word	0
int13_bak_flags:	.word	0

/****************************************************************************/
modify_boot_sectors:

	movw	%cs:(int13_old_eax - int13_handler), %ax
//	/* check CHS read */
//	cmpb	$0x02, %ah	/* is it read? */
//	jne	3f
//	cmpw	$0x0001, %cx	/* read from cylinder 0, sector 1? */
//	je	5f
//3:
	/* check LBA read */
	//cmpb	$0x42, %ah	/* is it extended read? */
	testb	$0x01, %ah	/* is it extended read? */
	jne	4f		/* no, do nothing. */
	cmpl	$0, 12(%si)	/* read from LBA_high=0? */
	jne	4f		/* no, do nothing. */

	movb	$0, %dh		/* simulate CHS read of head 0 */
	cmpl	$0, 8(%si)	/* read from LBA_low=0? */
	je	3f		/* yes, continue. */

	movzbl	%cs:3(%bp), %eax	/* AL=Smax */
	andb	$63, %al	/* EAX=sectors per track */
	movb	$1, %dh		/* simulate CHS read of head 1 */
	cmpl	%eax, 8(%si)	/* read from LBA_low=sectors per track? */
	jne	4f		/* no, exit. */
3:
	movw	4(%si), %bx	/* simulate CHS read buffer offset */
	movw	6(%si), %es	/* simulate CHS read buffer segment */

5:
	/* CHS mode read from cylinder 0, sector 1 */

#;	testb	%dl, %dl	/* The TO_DRIVE is hard drive? */
#;	jns	4f		/* no, do nothing */
	cmpw	$0xaa55, %es:0x1fe(%bx)	/* is it a valid boot sector? */
	jne	4f			/* no, skip */
	movl	%cs:16(%bp), %eax	/* S_count_Lo */
	shrl	$1, %eax	/* map a whole drive? */
	jz	4f		/* yes, nothing need to change */
	movl	%cs:8(%bp), %eax	/* StartLBA_Lo */
	testl	%eax, %eax	/* geometry translation only? */
	jz	4f		/* yes, needn't change */
	movl	%cs:(%bp), %eax	/* FROM_DRIVE, TO_DRIVE, H, S */

	testb	%al, %al	/* The FROM_DRIVE is hard drive? */
	jns	modify_floppy	/* no, goto floppy boot record modification */

	testb	%dh, %dh	/* read from head 0? */
	jnz	modify_HD_DOS	/* no, goto HD DOS boot record modification */

	/* we have read an MBR, and we need to modify the partition table */

	/* the partition table could be an extended partition table. if so,
	 * we need to turn it to be a primary partition table.
	 */

	/* if all start_sectors are not sectors_per_track, then it is not
	 * an extended partition table.
	 */

	/* first, the MS magic number should be non-zero */
	cmpl	$0, %es:0x1b8(%bx)
	jne	5f
	movb	%al, %es:0x1b8(%bx)	/* let it be the FROM_DRIVE */
5:
	shrl	$16, %eax	/* AL=Hmax, AH=Smax */
	andb	$63, %ah	/* AH=Smax */
//	cmpb	$1, %ah
//	jbe	4f /* do not modify partition table when disable CHS mode */

	/* an extended partition table should have an entry with
	 * StartSector=Smax.
	 */
	movzbl	%ah, %eax
	movw	$0x1c6, %si		/* SI=0x1c6 */
	cmpl	%eax, %es:(%bx, %si)
	jz	5f
	addw	$16, %si		/* SI=0x1d6 */
	cmpl	%eax, %es:(%bx, %si)
	jz	5f
	addw	$16, %si		/* SI=0x1e6 */
	cmpl	%eax, %es:(%bx, %si)
	jz	5f
	addw	$16, %si		/* SI=0x1f6 */
	cmpl	%eax, %es:(%bx, %si)
	jnz	4f	/* not an extended partition table */
5:
	/* check if it is a primary partition table */

	/* now the StartSector=Smax. if it is a primary partition table entry,
	 * it must have C/H/S=0/1/1.
	 */

	movl	%es:-8(%bx, %si), %eax
	shrl	$8, %eax	/* hi word:cylinder/sector, lo word:head */
	cmpl	$0x000101, %eax		/* 0x00=C, 0x01=S, 0x01=H */
	je	4f	/* primary partition table, nothing to do */

	/* now we are sure this is an extended partition table */

	/* compose a master boot record routine */

	cld
#if 1
	movw	%bx, %di
	movb	$0xFA, %al		/* cli */
	stosb
	movl	$0xD08EC033, %eax	/* xor AX,AX; mov SS,AX */
	stosl
	movl	$0xFB7C00BC, %eax	/* mov SP,7C00 ; sti */
	stosl
	movl	$0x07501F50, %eax	/* push AX; pop DS; push AX; pop ES */
	stosl
	movl	$0x7C1CBEFC, %eax	/* cld; mov SI,7C1C */
	stosl
	movl	$0x50061CBF, %eax	/* mov DI,061C ; push AX */
	stosl
	movl	$0x01E4B957, %eax	/* push DI ; mov CX, 01E4 */
	stosl
	movl	$0x1ECBA4F3, %eax	/* repz movsb; retf; push DS */
	stosl
	movl	$0x537C00BB, %eax	/* mov BX,7C00 ; push BX */
	stosl
	movl	$0x520180BA, %eax	/* mov DX,0180 ; push DX */
	stosl
	movl	$0x530201B8, %eax	/* mov AX,0201 ; push BX */
	stosl
	movl	$0x5F13CD41, %eax	/* inc CX; int 13; pop DI */
	stosl
	movl	$0x5607BEBE, %eax	/* mov SI,07BE ; push SI */
	stosl
	movl	$0xCBFA5A5D, %eax	/* pop BP; pop DX; cli; retf */
	stosl
#endif

	/* empty all other entries except this one by 2 steps: */

	/* step 1. move this entry onto the first one (overwrite it) */
	movl	%es:-8(%bx, %si), %eax
	movl	%eax, %es:0x1be(%bx)
	movl	%es:-4(%bx, %si), %eax
	movl	%eax, %es:0x1c2(%bx)
	movl	%es:(%bx, %si), %eax
	movl	%eax, %es:0x1c6(%bx)
	movl	%es:4(%bx, %si), %eax
	movl	%eax, %es:0x1ca(%bx)

#if 1
	/* step 2. empty the last 3 entries */
	xorw	%ax, %ax
	movw	%bx, %di
	addw	$0x1ce, %di
	movw	$24, %cx
	repz stosw		/* DI=BX+0x1fe */
#else
	xorw	%ax, %ax
	movw	%bx, %di
	addw	$0x1d1, %di
	stosw			/* DI=BX+0x1d3 */
	addw	$2, %di		/* DI=BX+0x1d5 */
	stosb			/* DI=BX+0x1d6 */
	addw	$0x28, %di	/* DI=BX+0x1fe */
#endif

	/* modify the start_CHS of the first entry */
	subw	$0x40, %di	/* DI=BX+0x1be */
	movb	$0x80, %al	/* set boot indicator */
	stosb			/* DI=BX+0x1bf */
	movb	$0x01, %al	/* AX=1 */
	stosb			/* DI=BX+0x1c0, H=0x01 */
	stosw			/* DI=BX+0x1c2, S=0x01, C=0x00 */

#if 0
	movb	$0x0B, %al
	stosb			/* DI=BX+0x1c3 */
#else
	/* modify the end_CHS of the first entry */
	incw	%di		/* DI=BX+0x1c3 */
#endif

	/* get total sectors */
	movl	%es:7(%di), %eax	/* DI+7=BX+0x1ca */

	/* calculate the end sector number */
	addl	%es:3(%di), %eax	/* DI+3=BX+0x1c6 */
	//decl	%eax

	pushl	%eax		/* EAX-1=end sector number */
	movzwl	%cs:2(%bp), %eax	/* Hmax, Smax */
	andb	$63, %ah
	movzbl	%ah, %ecx
	mulb	%cl
	addw	%cx, %ax	/* EAX=sectors per cylinder */
	pushl	%eax		/* EAX=sectors per cylinder */
	movw	$1024, %cx
	mull	%ecx		/* EAX=CHS addressible total sectors */
				/* EDX=0 */
	popl	%edx		/* EDX=sectors per cylinder */
	popl	%ecx		/* ECX-1=end sector number */
	cmpl	%eax, %ecx
	jb	5f

	/* assign max end sector number */
	movl	%eax, %ecx
	//subl	$0x3EC1, %ecx	/* XXX: 0x3EC1=255*63 */
5:
	pushl	%ecx		/* ECX-1=end sector number */
	movl	%edx, %ecx	/* ECX=sectors per cylinder */
	xorl	%edx, %edx
	popl	%eax		/* EAX-1=end sector number */
	decl	%eax

	divl	%ecx		/* EAX=cylinder number */
				/* EDX=sector number in the last cylinder */
				/* EAX hi=0, EDX hi=0 */
	xchgw	%ax, %cx	/* CX=cylinder number */
	xchgw	%ax, %dx	/* AX=sector number in the last cylinder */
	movb	%cs:3(%bp), %dl	/* DL=Smax */
	andb	$63, %dl
	divb	%dl		/* AL=head number, AH=sector number - 1 */
	stosb			/* DI=BX+0x1c4 */
	movb	%ah, %al
	incw	%ax		/* AL=sector number */
	movb	%cl, %ah	/* cylinder lo 8 bits */
	shlb	$6, %ch		/* cylinder hi 2 bits */
	orb	%ch, %al
	//movb	$0, %ah		/* XXX: let cylinder lo 8 bits=0 */
	stosw			/* DI=BX+0x1c6 */

4:
	/* end partition table modification */
	/* needn't restore registers */
	ret

/****************************************************************************/
modify_floppy:

	/* AL=FROM_DRIVE is the floppy drive number. */

	cmpb	$0x00, %dh	/* read from head 0? */
	jne	4b

	pushl	%ecx
	pushw	%si

	/* FAT12/FAT16/NTFS drive number is at offset 0x24. */
	movw	$0x24, %si

	xorl	%ecx, %ecx

	/* check if it is FAT32. */

	/* FAT32 should have 0 root_dir_entries and total_sectors_short. */
	cmpl	%ecx, %es:0x11(%bx)
	jne	5f			/* not FAT32 */

	/* FAT32 should have 0 sectors_per_fat. */
	cmpw	%cx, %es:0x16(%bx)
	jne	5f			/* not FAT32 */

	/* FAT32 should have non-zero total_sectors_long. */
	cmpl	%ecx, %es:0x20(%bx)
	je	5f			/* not FAT32 */

	/* FAT32 should have non-zero sectors_per_fat32. */
	cmpl	%ecx, %es:0x24(%bx)
	je	5f			/* not FAT32 */

	/* Now it is FAT32, and the drive number is at offset 0x40. */
	movw	$0x40, %si
5:
	movb	%al, %es:(%bx, %si)	/* modify the boot drive number. */

	movl	%ecx, %es:0x1c(%bx)	/* let number of hidden sectors=0 */
	/*movb	$0xf0, %es:0x15(%bx)*/	/* set floppy media descriptor */

	popw	%si
	popl	%ecx

	jmp	4b

/****************************************************************************/
modify_HD_DOS:

	cmpb	$0x01, %dh		/* read from head 1? */
	jne	4b
	movl	%cs:8(%bp), %eax		/* StartLBA_Lo */
	testl	%eax, %eax
	jz	4b
	cmpl	%eax, %es:0x1c(%bx)	/* Number of hidden sectors */
	jbe	4b
	subl	%eax, %es:0x1c(%bx)
	movzbl	%cs:3(%bp), %eax		/* AL=Smax */
	andb	$63, %al
	cmpl	%eax, %es:0x1c(%bx)	/* Number of hidden sectors */
	jnb	4b
	movl	%eax, %es:0x1c(%bx)
	jmp	4b

/****************************************************************************/
modify_in_situ:

	movb	%al, %cs:(int13_in_situ_sectors - int13_handler)

	cld

	/* if FROM is not harddrive, do nothing. */
	testb	$0x80, %cs:(%bp)	/* FROM drive */
	jz	4f

	cmpb	$0x02, %ah	/* is it CHS read? */
	jne	3f

	/* AL=sectors read */

	/* translate CHS to LBA */

	movw	%dx, %di	/* save DX to DI */
	movw	%cx, %si	/* save CX to SI */

	movb	%cs:7(%bp), %al	/* TO_S */
	andb	$63, %al
	movzbw	%al, %dx
	mulb	%cs:6(%bp)	/* TO_H */
	addw	%dx, %ax	/* AX=sectors_per_cylinder */

	/* get current cylinder number */

	shrb	$6, %cl
	xchgb	%cl, %ch

	mulw	%cx		/* DX:AX=sectors */

	pushw	%dx
	pushw	%ax

	/* restore DX */

	movw	%di, %dx

	/* get current head number */
 
	movb	%cs:7(%bp), %al	/* TO_S */
	andb	$63, %al
	mulb	%dh		/* AX=sectors */

	popl	%edx

	movzwl	%ax, %eax
	addl	%edx, %eax

	movw	%si, %cx	/* restore CX */
	andb	$0x3F, %cl
	decw	%cx
	movzbl	%cl, %ecx
	addl	%ecx, %eax	/* EAX=start sector number */
	movzbl	%cs:(int13_in_situ_sectors - int13_handler), %ecx
	jmp	6f
	
3:
	cmpb	$0x42, %ah	/* is it LBA read? */
	jne	4f
	cmpl	$0, 12(%si)	/* read from LBA_high=0? */
	jne	4f
	movl	8(%si), %eax	/* start sector number */
	movzbl	2(%si), %ecx	/* sectors read */
	movw	4(%si), %bx	/* simulate CHS read buffer offset */
	movw	6(%si), %es	/* simulate CHS read buffer segment */
6:
#;	testb	%dl, %dl	/* The TO_DRIVE is hard drive? */
#;	jns	4f		/* no, do nothing */
	/* ECX=sectors read */
	cmpl	$0, %eax	/* start sector number 0 is for MBR */
	je	5f

	/* if EAX <= startLBA_Lo < EAX + ECX, then the boot sector is read. */

	cmpl	%cs:8(%bp), %eax	/* startLBA_Lo */
	ja	4f		/* boot sector was not read */
	addl	%eax, %ecx
	cmpl	%cs:8(%bp), %ecx
	jbe	4f		/* boot sector was not read */

	movl	%cs:8(%bp), %ecx
	subl	%eax, %ecx	/* sectors between ES:BX and boot record */

	/* modify hidden sectors of the partition boot record */
	cmpb	$0x07, %cs:4(%bp)	/* NTFS */
	je	3f
	cmpb	$0x0C, %cs:4(%bp)	/* FAT32(LBA) */
	je	3f
	cmpb	$0x0E, %cs:4(%bp)	/* FAT12/16 */
	je	3f
	cmpb	$0x83, %cs:4(%bp)	/* EXT2 */
	jne	4f
3:
	movw	%es, %ax
	shlw	$5, %cx		/* 1 sector is 32 paragraphs */
	addw	%cx, %ax
	movw	%ax, %es
	cmpw	$0xaa55, %es:0x1fe(%bx)
	jne	4f
	movl	%cs:8(%bp), %eax	/* startLBA_Lo */
	movl	%eax, %es:0x1c(%bx)

	jmp	4f
5:
	/* Modify partition table. Note that there are 4 partition entries.
	 * The first one is called entry 0, and the last is entry 3. */

	cmpw	$0xaa55, %es:0x1fe(%bx)
	jne	4f

	/* first, the MS magic number should be non-zero */
	cmpl	$0, %es:0x1b8(%bx)
	jne	5f
	movb	%cs:(%bp), %al	/* FROM drive */
	movb	%al, %es:0x1b8(%bx)	/* let it be the FROM_DRIVE */
5:
	leaw	0x1be(%bx), %di	/* DI=BX+0x1be */

	movw	%di, %si

	/* if the first entry is empty, we simply put our new entry on it. */

	cmpb	$0, %es:4(%si)	/* consider partition type 00 as empty */
	jz	5f
	testb	$63, %es:2(%si)	/* invalid start sector number of 0 */ 
	jz	5f
	testb	$63, %es:6(%si)	/* invalid end sector number of 0 */ 
	jz	5f
	cmpl	$0, %es:8(%si)	/* invalid start LBA of 0 */ 
	jz	5f
	cmpl	$0, %es:12(%si)	/* invalid sector count of 0 */ 
	jz	5f

	/* Now that the first entry is not empty, we should find an empty one
	 * in entries 1, 2, 3(the last 3 partition entries). */

7:
	addw	$0x10, %si	/* SI=BX+0x1ce or BX+0x1de or BX+0x1ee */

	cmpb	$0, %es:4(%si)	/* consider partition type 00 as empty */
	jz	7f
	testb	$63, %es:2(%si)	/* invalid start sector number of 0 */ 
	jz	7f
	testb	$63, %es:6(%si)	/* invalid end sector number of 0 */ 
	jz	7f
	cmpl	$0, %es:8(%si)	/* invalid start LBA of 0 */ 
	jz	7f
	cmpl	$0, %es:12(%si)	/* invalid sector count of 0 */ 
	jz	7f

	leaw	0x1ee(%bx), %bx
	cmpw	%bx, %si
	leaw	-0x1ee(%bx), %bx
	jb	7b		/* try next entry */

	/* Now SI=BX+0x1ee points to the last entry */

7:
	/* SI points to empty entry(or the last entry), we move old entry 0
	 * onto this one.
	 */

	movl	%es:(%di), %eax
	movl	%eax, %es:(%si)
	movl	%es:4(%di), %eax
	movl	%eax, %es:4(%si)
	movl	%es:8(%di), %eax
	movl	%eax, %es:8(%si)
	movl	%es:12(%di), %eax
	movl	%eax, %es:12(%si)

5:
	/* build our new entry 0 */

	/* DI=BX+0x1be */

	movl	%cs:8(%bp), %eax	/* startLBA_Lo */

	call	lba_to_chs

	movb	$0x80, %al	/* set boot indicator */
	//movb	$0x00, %al	/* clear boot indicator */
	stosl			/* DI=BX+0x1c2 */

	movl	%cs:16(%bp), %eax
	addl	%cs:8(%bp), %eax
	decl	%eax		/* endLBA */
	
	call	lba_to_chs

	/* if in situ, TO_C holds the partition type:
	 * 	0x07(NTFS), 0x0C(FAT32), 0x0E(FAT12/16), 0x83(EXT2/3)
	 */
	movb	%cs:4(%bp), %al	/* TO_C */
	stosl			/* DI=BX+0x1c6 */

	/* modify start sector and sector count */

	movl	%cs:8(%bp), %eax
	stosl			/* DI=BX+0x1ca */
	movl	%cs:16(%bp), %eax
	stosl			/* DI=BX+0x1ce */

#if 1
	/* clear other boot indicators in the last 3 entries */

	movb	$0, %al		/* DI=BX+0x1ce */
	stosb			/* DI=BX+0x1cf */
	
	leaw	0x1de(%bx), %di	/* DI=BX+0x1de */
	stosb			/* DI=BX+0x1df */
	
	leaw	0x1ee(%bx), %di	/* DI=BX+0x1ee */
	stosb			/* DI=BX+0x1ef */
#endif

//#if 0
//	/* hide entry 3 (test only) */
//	orb	$0x10, %es:0x1f2(%bx)
//#endif
	
#if 0
	/* move extended partition entries to last */

	cmpb	$0x0F, %es:0x1f2(%bx)
	je	4f		/* entry 3 is extended, do nothing */

	cmpb	$0x05, %es:0x1f2(%bx)
	je	4f		/* entry 3 is extended, do nothing */

	cmpb	$0x0F, %es:0x1e2(%bx)
	je	7f		/* entry 2 is extended */

	cmpb	$0x05, %es:0x1e2(%bx)
	je	7f		/* entry 2 is extended */

	/* both entry 2 and entry 3 are not extended */

	cmpb	$0x0F, %es:0x1d2(%bx)
	je	8f		/* entry 1 is extended */

	cmpb	$0x05, %es:0x1d2(%bx)
	jne	4f	/* all entries 1, 2, 3 are not extended, do nothing */
8:
	/* entry 1 is extended, but entry 2 and entry 3 are not extended.
	 * so exchange entry 1 and entry 3. */

	xchgl	%eax, %es:0x1ce(%bx)
	xchgl	%eax, %es:0x1ee(%bx)
	xchgl	%eax, %es:0x1ce(%bx)

	xchgl	%eax, %es:0x1d2(%bx)
	xchgl	%eax, %es:0x1f2(%bx)
	xchgl	%eax, %es:0x1d2(%bx)

	xchgl	%eax, %es:0x1d6(%bx)
	xchgl	%eax, %es:0x1f6(%bx)
	xchgl	%eax, %es:0x1d6(%bx)
	
	xchgl	%eax, %es:0x1da(%bx)
	xchgl	%eax, %es:0x1fa(%bx)
	xchgl	%eax, %es:0x1da(%bx)

	jmp	4f

7:
	/* entry 2 is extended, but entry 3 is not. if entry 1 is extended,
	 * we exchange entry 1 and 3, else, we exchange entry 2 and 3. */
	 */

	cmpb	$0x0F, %es:0x1d2(%bx)
	je	8b		/* entry 1 is extended */

	cmpb	$0x05, %es:0x1d2(%bx)
	je	8b		/* entry 1 is extended */

	/* exchange entry 2 and 3 */
	xchgl	%eax, %es:0x1de(%bx)
	xchgl	%eax, %es:0x1ee(%bx)
	xchgl	%eax, %es:0x1de(%bx)

	xchgl	%eax, %es:0x1e2(%bx)
	xchgl	%eax, %es:0x1f2(%bx)
	xchgl	%eax, %es:0x1e2(%bx)

	xchgl	%eax, %es:0x1e6(%bx)
	xchgl	%eax, %es:0x1f6(%bx)
	xchgl	%eax, %es:0x1e6(%bx)
	
	xchgl	%eax, %es:0x1ea(%bx)
	xchgl	%eax, %es:0x1fa(%bx)
	xchgl	%eax, %es:0x1ea(%bx)
#endif

//	/* empty the last 3 entries */
//	xorw	%ax, %ax
//	movw	%bx, %di
//	addw	$0x1ce, %di
//	movw	$24, %cx
//	repz stosw		/* DI=BX+0x1fe */

4:
	/* end partition table and BPB modification */
	ret

int13_in_situ_sectors:
	.byte	0

/****************************************************************************/

lba_to_chs:

	/* input:
	 *
	 *	EAX:	LBA
	 *
	 * output:
	 *
	 *	EAX:	CHS
	 *
	 *
	 *
	 */

	pushl	%eax		/* EAX=end sector number */
	movzwl	%cs:6(%bp), %eax	/* TO_H, TO_S */
	andb	$63, %ah
	movzbl	%ah, %ecx
	mulb	%cl
	addw	%cx, %ax	/* EAX=sectors per cylinder */
	pushl	%eax		/* EAX=sectors per cylinder */
	movw	$1024, %cx
	mull	%ecx		/* EAX=CHS addressible total sectors */
				/* EDX=0 */
	popl	%edx		/* EDX=sectors per cylinder */
	popl	%ecx		/* ECX=end sector number */
	decl	%eax
	cmpl	%eax, %ecx
	jb	5f

	/* assign max end sector number */
	movl	%eax, %ecx
	//subl	$0x3EC1, %ecx	/* XXX: 0x3EC1=255*63 */
5:
	pushl	%ecx		/* ECX=end sector number */
	movl	%edx, %ecx	/* ECX=sectors per cylinder */
	xorl	%edx, %edx
	popl	%eax		/* EAX=end sector number */

	divl	%ecx		/* EAX=cylinder number */
				/* EDX=sector number in the last cylinder */
				/* EAX hi=0, EDX hi=0 */
	xchgw	%ax, %cx	/* CX=cylinder number */
	xchgw	%ax, %dx	/* AX=sector number in the last cylinder */
	movb	%cs:7(%bp), %dl	/* TO_S */
	andb	$63, %dl
	divb	%dl		/* AL=head number, AH=sector number - 1 */
	//stosb			/* DI=BX+0x1c4 */

	xchgb	%ah, %al	/* AH=head number, AL=sector number - 1 */

	pushw	%ax

	//movb	%ah, %al
	incw	%ax		/* AL=sector number */
	movb	%cl, %ah	/* cylinder lo 8 bits */
	shlb	$6, %ch		/* cylinder hi 2 bits */
	orb	%ch, %al
	//movb	$0, %ah		/* XXX: let cylinder lo 8 bits=0 */
	//stosw			/* DI=BX+0x1c6 */
	shll	$16, %eax

	popw	%ax

	ret

/****************************************************************************/
max_cdrom_id:		.byte	0xE0

	.align	4
ENTRY(memdisk_raw)	.long	1	/* set to 0 if accessing memdrives using int15/AH=87h */
ENTRY(a20_keep_on)	.long	1	/* set to 0 if a20 should be auto-off */
ENTRY(lba_cd_boot)	.long	0	/* LBA of no-emulation boot image, in 2048-byte sectors */

minimum_mem_lo_in_map:
	.long	0	/* min ram drive base below 16M */
minimum_mem_hi_in_map:
	.long	0	/* min ram drive base above 16M */

/****************************************************************************/
int15_e820_handler:

	/* Comments are mostly gotten from Ralf Brown's Interrupt List. */

	cmpw	$0xe820, %ax		//cmpl	$0x0000e820, %eax
	jne	1f

	/* Newer BIOSes - GET SYSTEM MEMORY MAP */

	//AX = E820h
	//EAX = 0000E820h
	//EDX = 534D4150h ('SMAP')
	//EBX = continuation value or 00000000h to start at beginning of map
	//ECX = size of buffer for result, in bytes (should be >= 20 bytes)
	//ES:DI -> buffer for result

	//Return:
	//CF clear if successful
	//EAX = 534D4150h ('SMAP')
	//ES:DI buffer filled
	//EBX = next offset from which to copy or 00000000h if all done
	//ECX = actual length returned in bytes
	//CF set on error
	//AH = error code (86h)

	/* Notes: Originally introduced with the Phoenix BIOS v4.0, this
	 * function is now supported by most newer BIOSes, since various
	 * versions of Windows call it to find out about the system memory.
	 * A maximum of 20 bytes will be transferred at one time, even if ECX
	 * is higher; some BIOSes (e.g. Award Modular BIOS v4.50PG) ignore the
	 * value of ECX on entry, and always copy 20 bytes. Some BIOSes expect
	 * the high word of EAX to be clear on entry, i.e. EAX=0000E820h. If
	 * this function is not supported, an application should fall back to
	 * AX=E802h, AX=E801h, and then AH=88h. The BIOS is permitted to return
	 * a nonzero continuation value in EBX and indicate that the end of the
	 * list has already been reached by returning with CF set on the next
	 * iteration. This function will return base memory and ISA/PCI memory
	 * contiguous with base memory as normal memory ranges; it will
	 * indicate chipset-defined address holes which are not in use and
	 * motherboard memory-mapped devices, and all occurrences of the system
	 * BIOS as reserved; standard PC address ranges will not be reported
	 */

//Format of Phoenix BIOS system memory map address range descriptor:
//
//Offset Size	Description
//------ -----	----------------------
//  00h  QWORD	base address
//  08h  QWORD	length in bytes
//  10h  DWORD	type of address range

//Values for System Memory Map address type:
//01h memory, available to OS
//02h reserved, not available (e.g. system ROM, memory-mapped device)
//03h ACPI Reclaim Memory (usable by OS after reading ACPI tables)
//04h ACPI NVS Memory (OS is required to save this memory between NVS sessions)
//other not defined yet -- treat as Reserved

	cmpl	$0x534D4150, %edx	/* "SMAP" */
	jne	1f
	cmpl	$20, %ecx
	jb	2f

	pushfw
	lcall	%cs:*(EXT_C(ROM_int15) - int13_handler)

	jc	3f
	cmpl	$0x534D4150, %eax	/* "SMAP" */
	jne	2f
	pushal
	movl	%es:4(%di), %eax	/* BaseAddrHigh */
	testl	%eax, %eax
	jnz	4f
	movl	%es:16(%di), %eax	/* Type */
	decl	%eax /* 1=usable memory, available to the operating system */
	jnz	4f
	/* set %si to the drive map */
	movw	$(EXT_C(hooked_drive_map) - int13_handler), %si
	movw	$(DRIVE_MAP_SIZE), %cx
6:
	cmpb	$0xff, %cs:1(%si)
	jne	5f
	testb	$0x40, %cs:5(%si)	/* TO_C bit 14=TO has 2048-byte cdrom sector */
	jnz	5f
	movl	%cs:8(%si), %ebx	/* start_sector */
	shll	$9, %ebx
	movl	%es:4(%di), %eax	/* BaseAddrHigh */
	testl	%eax, %eax
	jnz	5f
	cmpl	%es:(%di), %ebx		/* BaseAddrLow */
	jb	5f
	movl	%es:12(%di), %eax	/* LengthHigh */
	testl	%eax, %eax
	jnz	7f
	movl	%es:8(%di), %eax	/* LengthLow */
	addl	%es:(%di), %eax
	jc	7f
	cmpl	%eax, %ebx
	jnb	5f
7:
	subl	%es:(%di), %ebx		/* new length */
	movl	%ebx, %es:8(%di)	/* LengthLow */
	xorl	%ebx, %ebx
	movl	%ebx, %es:12(%di)	/* LengthHigh */
	//jmp	4f

5:
	/* try next slot */
	addw	$DRIVE_MAP_SLOT_SIZE, %si
	loop	6b
	//memory block length update done
4:
	popal
	clc
	lret	$2

2:
	movb	$0x86, %ah	/* function not supported */
3:
	stc
	lret	$2
#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
1:
	cmpw	$0xe801, %ax	//cmpl	$0x0000e801, %eax
	je	1f
	cmpw	$0xe881, %ax	//cmpl	$0x0000e881, %eax
	je	1f
	cmpw	$0xda88, %ax
	je	1f
	cmpb	$0xc7, %ah
	je	1f
	cmpb	$0x8a, %ah
	je	1f
	cmpb	$0x88, %ah
	je	1f
	ljmp	%cs:*(EXT_C(ROM_int15) - int13_handler)
#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
1:

	pushal

	/* find minimum mem ever used in the drive map slots */

	movl	$-1, %eax	/* 0xffffffff */
	movl	%eax, %cs:(minimum_mem_hi_in_map - int13_handler)
	movl	$0x1000000, %cs:(minimum_mem_lo_in_map - int13_handler)
	/* set %si to the drive map */
	movw	$(EXT_C(hooked_drive_map) - int13_handler), %si
	movw	$(DRIVE_MAP_SIZE), %cx
6:
	cmpb	$0xff, %cs:1(%si)
	jne	5f
	testb	$0x40, %cs:5(%si)	/* TO_C bit 14=TO has 2048-byte cdrom sector */
	jnz	5f
	movl	%cs:8(%si), %ebx	/* StartLBA_Lo */
	shll	$9, %ebx

	cmpl	$0x1000000, %ebx	/* 16M */
	jb	7f
	/* hi mem */
	cmpl	%ebx, %cs:(minimum_mem_hi_in_map - int13_handler)
	jbe	5f
	movl	%ebx, %cs:(minimum_mem_hi_in_map - int13_handler)
	jmp	5f
7:
	/* lo mem */
	cmpl	%ebx, %cs:(minimum_mem_lo_in_map - int13_handler)
	jbe	5f
	movl	%ebx, %cs:(minimum_mem_lo_in_map - int13_handler)
5:
	/* try next slot */
	addw	$DRIVE_MAP_SLOT_SIZE, %si
	loop	6b

	popal

	cmpl	$-1, %cs:(minimum_mem_hi_in_map - int13_handler)
	jne	1f
	cmpl	$0x1000000, %cs:(minimum_mem_lo_in_map - int13_handler)
	jne	1f

	ljmp	%cs:*(EXT_C(ROM_int15) - int13_handler)

#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
1:
	cmpw	$0xe801, %ax	//cmpl	$0x0000e801, %eax
	jne	1f

	/* Phoenix BIOS v4.0 - GET MEMORY SIZE FOR >64M CONFIGURATIONS */

	//AX = E801h

	//Return:
	//CF clear if successful
	//AX = extended memory between 1M and 16M, in K (max 3C00h = 15MB)
	//BX = extended memory above 16M, in 64K blocks
	//CX = configured memory 1M to 16M, in K
	//DX = configured memory above 16M, in 64K blocks
	//CF set on error

	/* Notes: Supported by the A03 level (6/14/94) and later XPS P90
	 * BIOSes, as well as the Compaq Contura, 3/8/93 DESKPRO/i, and
	 * 7/26/93 LTE Lite 386 ROM BIOS. Supported by AMI BIOSes dated
	 * 8/23/94 or later. On some systems, the BIOS returns AX=BX=0000h;
	 * in this case, use CX and DX instead of AX and BX. This interface
	 * is used by Windows NT 3.1, OS/2 v2.11/2.20, and is used as a
	 * fall-back by newer versions if AX=E820h is not supported. This
	 * function is not used by MS-DOS 6.0 HIMEM.SYS when an EISA machine
	 * (for example with parameter /EISA) (see also MEM F000h:FFD9h), or
	 * no Compaq machine was detected, or parameter /NOABOVE16 was given.
	 */ 

	//movw	$0x3c00, %ax	/* 1-16M mem in K (0x3c00KB = 15MB) */
	//movw	$0x0300, %bx	/* mem above 16M in 64K blocks */
4:
	pushfw

	pushfw
	lcall	%cs:*(EXT_C(ROM_int15) - int13_handler)

	jc	3f

	pushl	%eax

	/* between 16M and 4G, we modify BX, DX */

	movl	%cs:(minimum_mem_hi_in_map - int13_handler), %eax
	cmpl	$-1, %eax		/* 4G - 1 */
	je	5f
	subl	$0x1000000, %eax	/* 16M */
	shrl	$16, %eax	/* AX=mem above 16M in 64K blocks */
	movw	%ax, %bx
	movw	%ax, %dx
	popl	%eax
	popfw
	pushfw
	pushl	%eax
	jnc	5f
	movzwl	%bx, %ebx
	movzwl	%dx, %edx
5:
	popl	%eax
	pushl	%eax

	/* between 1M and 16M, we modify AX, CX */

	movl	%cs:(minimum_mem_lo_in_map - int13_handler), %eax
	cmpl	$0x1000000, %eax	/* 16M */
	je	5f
	subl	$0x0100000, %eax	/* 1M */
	shrl	$10, %eax	/* AX=1-16M mem in K */
	movw	%ax, %cx
	popl	%eax
	movw	%cx, %ax
	popfw
	pushfw
	pushl	%eax
	jnc	5f
	popl	%eax
	movzwl	%ax, %eax
	pushl	%eax
	movzwl	%cx, %ecx
5:

	popl	%eax

	popfw
	clc
	lret	$2
3:
	popfw
	stc
	lret	$2

#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
1:
	cmpw	$0xe881, %ax	//cmpl	$0x0000e881, %eax
	jne	1f

	/* Phoenix BIOS v4.0 - GET MEMORY SIZE FOR >64M CONFIGURATIONS (32-bit) */

	//AX = E881h

	//Return:
	//CF clear if successful
	//EAX = extended memory between 1M and 16M, in K (max 3C00h = 15MB)
	//EBX = extended memory above 16M, in 64K blocks
	//ECX = configured memory 1M to 16M, in K
	//EDX = configured memory above 16M, in 64K blocks
	//CF set on error

	/* Notes: Supported by AMI BIOSes dated 8/23/94 or later. This
	 * interface is used by Windows NT 3.1, OS/2 v2.11/2.20, and is used
	 * as a fall-back by newer versions if AX=E820h is not supported
	 */

	//movl	$0x3c00, %eax	/* 1-16M mem in K (0x3c00 = 15MB) */
	//movl	$0x0300, %ebx	/* mem above 16M in 64K blocks */

	stc
	jmp	4b
#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
1:
	cmpw	$0xda88, %ax
	jne	1f

	/* AMI PCI BIOS - GET EXTENDED MEMORY SIZE */

	//AX = DA88h

	//Return:
	//CF clear (successful)
	//AX = 0000h
	//CL:BX = extended memory size in KBytes

	/* 63M = 3f00000 Bytes = 0xfc00 K */
	//movw	$0xfc00, %bx

#;	pushfw
#;	lcall	%cs:*(EXT_C(ROM_int15) - int13_handler)
#;
#;	jc	3f

	pushl	%eax

	movl	%cs:(minimum_mem_lo_in_map - int13_handler), %eax
	cmpl	$0x1000000, %eax	/* 16M */
	jb	5f
	movl	%cs:(minimum_mem_hi_in_map - int13_handler), %eax
5:
	subl	$0x0100000, %eax
	shrl	$10, %eax	/* EAX=extended mem in K */
	xchgw	%ax, %bx
	shrl	$16, %eax
	movb	%al, %cl

	popl	%eax

	xorw	%ax, %ax
	clc
	lret	$2
#;3:
#;	stc
#;	lret	$2

#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
1:
	cmpb	$0xC7, %ah
	jne	1f

	/* SYSTEM - later PS/2s - RETURN MEMORY-MAP INFORMATION */

	//AH = C7h
	//DS:SI -> user supplied memory map table

	//Return:
	//CF set on error
	//CF clear if successful

	/* Notes: Call AH=C0h and examine bit 4 of feature byte 2 to check if
	 * this function is supported. IBM classifies this function as
	 * optional. Windows95 OSR2 reportedly does not support this function
	 * even though INT 15/AH=C0h indicates that it is available (observed
	 * on several different systems)
	 */

//Format of memory-map table structure:
//	
//Offset Size	Description
//------ -----	--------------------------------------------------------------
//  00h  WORD	length of table (excluding this word)
//  02h  DWORD	local memory between 1M and 16M, in 1K blocks
//  06h  DWORD	local memory between 16M and 4G, in 1K blocks
//  0Ah  DWORD	system memory between 1M and 16M, in 1K blocks
//  0Eh  DWORD	system memory between 16M and 4G, in 1K blocks
//  12h  DWORD	cacheable memory between 1M and 16M, in 1K blocks
//  16h  DWORD	cacheable memory between 16M and 4G, in 1K blocks
//  1Ah  DWORD	1K blocks before start of non-system memory between 1M and 16M
//  1Eh  DWORD	1K blocks before start of non-system memory between 16M and 4G
//  22h  WORD	start segment of largest free block from C0000h-DFFFFh
//  24h  WORD	size of largest free block
//  26h  DWORD	reserved

	//movw	$0x0028, (%si)
	pushw	%ds
	pushw	%si

	pushfw
	lcall	%cs:*(EXT_C(ROM_int15) - int13_handler)

	popw	%si
	popw	%ds

	jc	3f

	pushl	%eax

	/* between 16M and 4G */

	movl	%cs:(minimum_mem_hi_in_map - int13_handler), %eax
	cmpl	$-1, %eax		/* 4G - 1 */
	je	5f
	subl	$0x1000000, %eax	/* 16M */
	shrl	$10, %eax	/* AX=mem above 16M in 1K blocks */
	movl	%eax, 0x0e(%si)
	movl	%eax, 0x1e(%si)
5:

	/* between 1M and 16M */

	movl	%cs:(minimum_mem_lo_in_map - int13_handler), %eax
	cmpl	$0x1000000, %eax	/* 16M */
	je	5f
	subl	$0x0100000, %eax	/* 1M */
	shrl	$10, %eax	/* AX=1-16M mem in K */
	movl	%eax, 0x0a(%si)
	movl	%eax, 0x1a(%si)
5:

	popl	%eax

	clc
	lret	$2
3:
	stc
	lret	$2

#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
1:
	cmpb	$0x8a, %ah
	jne	1f

	/* Phoenix BIOS v4.0 - GET BIG MEMORY SIZE */

	//AH = 8Ah

	//Return:
	//DX:AX = extended memory size in K 
	//movw	$0xfc00, %ax

#;	pushfw
#;	lcall	%cs:*(EXT_C(ROM_int15) - int13_handler)
#;
#;	jc	3f

	pushl	%eax

	movl	%cs:(minimum_mem_lo_in_map - int13_handler), %eax
	cmpl	$0x1000000, %eax	/* 16M */
	jb	5f
	movl	%cs:(minimum_mem_hi_in_map - int13_handler), %eax
5:
	subl	$0x0100000, %eax
	shrl	$10, %eax	/* EAX=extended mem in K */
	popw	%dx
	pushw	%ax
	shrl	$16, %eax
	xchgw	%ax, %dx

	popl	%eax

	clc
	lret	$2
#;3:
#;	stc
#;	lret	$2

#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
1:
	cmpb	$0x88, %ah
	jne	1f

	/* SYSTEM - GET EXTENDED MEMORY SIZE (286+) */

	//AH = 88h

	//Return:
	//CF clear on success(Not all BIOSes correctly return the carry flag)
	//AX = number of contiguous KB starting at absolute address 100000h
	//CF set on error
	//AH = status
	//	80h invalid command (PC,PCjr)
	//	86h unsupported function (XT,PS30)
	//movw	$0xfc00, %ax

#;	pushfw
#;	lcall	%cs:*(EXT_C(ROM_int15) - int13_handler)
#;
#;	jc	3f

	pushl	%eax

	movl	%cs:(minimum_mem_lo_in_map - int13_handler), %eax
	cmpl	$0x1000000, %eax	/* 16M */
	jb	5f
	movl	%cs:(minimum_mem_hi_in_map - int13_handler), %eax
5:
	subl	$0x0100000, %eax
	shrl	$10, %eax	/* EAX=extended mem in K */

	cmpl	$0x10000, %eax
	jb	5f
	movw	$0xFFFF, %ax
5:
	addw	$2, %sp
	pushw	%ax
	popl	%eax

	clc
	lret	$2
#;3:
#;	stc
#;	lret	$2

1:
	ljmp	%cs:*(EXT_C(ROM_int15) - int13_handler)

/****************************************************************************/

#include "a20.inc"

/****************************************************************************/

/* EDD30 code imported from edd30.asm of Smart Boot Manager. */

/*
#; asmsyntax=nasm
#;
#; CD-ROM Boot Extension v 1.1 for Smart Boot Manager
#; 
#; Copyright (C) 2000, Christopher Li <chrisl@gnuchina.org>.
#; Copyright (C) 2000, James Su <suzhe@gnuchina.org>
#;
#; This is free software, you can redistribute it and/or modify it
#; under the terms of the GNU General Public License version 2 or above.
#;
#; The ATAPI driver is based on the source code of atadrv written by
#; Hale Landis <hlandis@ibm.net>, Thanks him a lot!
#;
#; Without his great program, we could not implement the CD-ROM Boot feature
#; so quickly.
#;
*/


//#define	EDD_3_0

#define	sane_check
#define	check_extra_fail

//#define CB_DATA	0	//; data reg         in/out pio_base_addr1+0
//#define CB_FR		1	//; feature reg         out pio_base_addr1+1
//#define CB_SC		2	//; sector count     in/out pio_base_addr1+2
//#define CB_SN		3	//; sector number    in/out pio_base_addr1+3
//#define CB_CL		4	//; cylinder low     in/out pio_base_addr1+4
//#define CB_CH		5	//; cylinder high    in/out pio_base_addr1+5
//#define CB_DH		6	//; device head      in/out pio_base_addr1+6
//#define CB_STAT	7	//; primary status   in     pio_base_addr1+7
//#define CB_CMD	7	//; command             out pio_base_addr1+7
//#define CB_DC		8	//; device control      out pio_base_addr2+6
//#define CB_ASTAT	8	//; alternate status in     pio_base_addr2+6
//#define CB_DC_SRST	0x04	//; soft reset
#define	CB_STAT_BSY	0x80	//; busy
#define	CB_STAT_RDY	0x40	//; ready
#define	CB_STAT_SKC	0x10	//; seek complete

#define	CB_STAT_DRQ	0x08	//; data request
#define	CB_STAT_ERR	0x01	//; error

#define	CB_SC_P_TAG	0xf8	//; ATAPI tag (mask)
#define	CB_SC_P_REL	0x04	//; ATAPI release
#define	CB_SC_P_IO	0x02	//; ATAPI I/O
#define	CB_SC_P_CD	0x01	//; ATAPI C/D

#define	FAILBIT8	0x0100	//; SC( CD/IO bits) wrong at end of cmd
#define	FAILBIT6	0x0040	//; byte count wrong at data packet xfer time
#define	FAILBIT5	0x0020	//; SC (IO bit) wrong at data packet xfer time
#define	FAILBIT4	0x0010	//; SC (CD bit) wrong at data packet xfer time
#define	FAILBIT3	0x0008	//; byte count wrong at cmd packet xfer time
#define	FAILBIT2	0x0004	//; SC wrong at cmd packet xfer time
#define	FAILBIT0	0x0001	//; slow setting BSY=1 or DRQ=1 after AO cmd

#define	CB_DC_HD15	0x08	//; bit should always be set to one
#define	CB_DC_NIEN	0x02	//; disable interrupts
#define	cmd_DC	CB_DC_HD15
#define cmd_DC_ni CB_DC_HD15 | CB_DC_NIEN

/****************************************************************************/

__reg_select_dev:
#; ax = dev
#; simple version of the select dev
	addb	$0x0A, %al	#; AL= 0x0A or 0x0B
	shlb	$4, %al		#; AL= 0xA0 or 0xB0
	movw	reg_addr - int13_handler + (6 * 2), %dx	#; CB_DH = drive select
	outb	%al, %dx

	call	delay400ns
	ret


reg_select_dev:
#; input: ax = bx = dev
#; set_timeout first
//	movw	%ax, %bx
	cmpb	$2, (reg_dev_info - int13_handler)(%bx)	# REG_CONFIG_TYPE_ATA
	jb	__reg_select_dev	# not ATA

	/* The device is ATA */

//	pushw	%bx

	call	reg_poll_busy		# change AL, DX

#if 0
	orw	%ax, %ax
	jnz	1f	# return if,{or ax,ax},nz
#else
	ja	1f	# timeout, failure
#endif

	movw	%bx, %ax
	call	__reg_select_dev	# change AL, DX

#ifndef USE_ATA
	call	reg_poll_busy		# change AL, DX
#if 0
	jmp	1f
#else
#if 0
	orw	%ax, %ax
	jz	1f
#else
	jna	1f
#endif
#endif
#else	//; USE_ATA
3:
	movw	reg_addr - int13_handler + (7 * 2), %dx		#; CB_STAT
	inb	%dx, %al

	cmpb	$2, (reg_dev_info - int13_handler)(%bx)	# REG_CONFIG_TYPE_ATA
	jne	4f
	andb	$(CB_STAT_BSY | CB_STAT_RDY | CB_STAT_SKC), %al
	# return if,{cmp al,CB_STAT_RDY|CB_STAT_SKC},e
	cmpb	$(CB_STAT_RDY | CB_STAT_SKC), %al
	je	1f
	jmp	3b
4:
	# return if,{test al,CB_STAT_BSY},z
	testb	$CB_STAT_BSY, %al
	jz	1f
	jmp	3b
#endif	//; USE_ATA


	call	__reg_select_dev
1:
//	popw	%bx
	ret


select_atapi:
	cmpw	%cs:(atapi_cur_dev - int13_handler), %ax	# device serial number
	jne	select_atapi_force
	//clc	#; CF already cleared
	ret


select_atapi_force:
#; input: ax = device serial number
#; return: cf =0 success, cf =1 failed
	pushaw
	pushw	%es

	pushw	%cs
	popw	%es

	cmpb	%cs:(EXT_C(atapi_dev_count) - int13_handler), %al
	cmc
	jb	2f

	movw	%ax, %cs:(atapi_cur_dev - int13_handler)	# device serial number

	movw	$atapi_dev_base - int13_handler, %si	# array of ATAPI reg pointer and dev
	shlw	$2, %ax					# each element of array has 4 bytes
	addw	%ax, %si
	movw	%cs:(%si), %bx				# BX is the reg pointer of the current device

	call	reg_setup_base_addr			# fill the 10-word reg_addr area
							# change no registers

	movw	%cs:2(%si), %bx				# BX is the dev number of the current device
	movw	%bx, %ax

	call	set_timeout				# set timeout for reg_select_dev
							# change no registers

	call	reg_select_dev

	addb	$0x0A, %bl		#; BL= 0x0A or 0x0B
	shlb	$4, %bl			#; BL= 0xA0 or 0xB0
	movb	%bl, %cs:(reg_cur_dev - int13_handler)

	clc
2:
	pop	%es
	popaw
	ret


read_atapi:
#;input: es:di -> buffer, cx = sector count, edx = lba address
#;return: cf =0 success, cx = number of bytes actually read
	pushaw
	orw	%cx, %cx
	jz	3f

1:
	pushw	%cx
	pushl	%edx

	call	clear_atapi_buffer
	movb	$0x28, atapi_cmd_buffer - int13_handler

	bswapl	%edx
	movl	%edx, atapi_cmd_buffer - int13_handler + 2
	movb	$1, atapi_cmd_buffer - int13_handler + 8

	# invoke reg_packet,byte, 0, es, di, REG_ATAPI_MAX_BYTES
	pushw	$0x8000			#;   REG_ATAPI_MAX_BYTES
	pushw	%di
	pushw	%es
	pushw	$0
	call	reg_packet
	addw	$8, %sp

	orw	%ax, %ax
	jnz	2f
	cmpw	$0x800, %cx		#; CDSECTOR_SIZE
	jne	2f
	popl	%edx
	incl	%edx
	addw	%cx, %di
	popw	%cx
	loop	1b

	clc
	jmp	4f

2:
	popl	%edx
	popw	%cx

3:
	stc
4:
	popaw
	ret


read_bios_time:
#;	return EAX as the long time
	pushw	%ds
	xorw	%ax, %ax
	movw	%ax, %ds
	movl	0x46c, %eax
	popw	%ds
	ret


edd30_read_cdrom:
#;return cf=0 success, cf=1 fail, ah = fail code
#;will change all registers, including ES!!

	call	test_atapi_ready
	movb	$0xAA, %ah	# error code if CF=1
	jc	4f

	movw	%ds, %ax	# save DS

	# get DS for the disk address packet
	movw	%cs:(int13_old_ds - int13_handler), %ds
	movw	2(%si), %cx	# struc_int13ext.blk_count
	movw	4(%si), %di	# struc_int13ext.buf_addr_off
	movw	6(%si), %bx	# struc_int13ext.buf_addr_seg
	movl	8(%si), %edx	# struc_int13ext.blk_num_low1
	cmpb	$16, (%si)	# valid packet size is 16

	movw	%ax, %ds	# restore DS

	setne	%ah		# AH=1 for invalid function call
	stc			# error out if ...
	jne	4f		# ... invalid packet size

	movw	%bx, %es	# ES changed!!

	call	read_atapi

	movb	$0x0C, %ah	# error code if CF=1
4:
//	/* debug print AX and FLAGS */
//	pushfw
//	pushw	%ax
//	pushw	$read_cdrom_ah_flags - int13_handler	# the format string
//	call	realmode_printf
//	popw	%ax
//	popw	%ax
//	popfw
	ret

//read_cdrom_ah_flags:
//	.ascii	"edd30_read_cdrom: AX=%X, FLAGS=%X\r\n\0"


reg_reset:
#; call after reg_probe_exist
	pushaw

#;	mov_ax 0
#;	call __reg_select_dev

#if 0
	/* The ATA software reset mechanism, SRST, (bit 2 in the Device Control
	 * Register) cannot be used for ATAPI Device, because resets issued by
	 * the ATAPI driver would also reset any attached hard disk and vice
	 * versa. To solve this, ATAPI defines an ATAPI Soft Reset command
	 * using a reserved ATA opcode which could be decoded by the interface
	 * controller hardware.
	 */

	movb	$cmd_DC, %al
	orb	$0x04, %al	#; CB_DC_SRST = soft reset

	movw	reg_addr - int13_handler + (8 * 2), %dx		#; CB_DC
	outb	%al, %dx

	call	delay400ns
#endif

#if 0
	movb	$0x08, %al		#; ATAPI Soft Reset
	movw	reg_addr - int13_handler + (7 * 2), %dx		#; CB_CMD
	outb	%al, %dx

	call	delay400ns
#endif

#if 1
	/* set features (0xEF to command port) */
	/* set transfer mode (0x03 in feature register) */
	/* mode value in Sector Count register (0 for PIO default mode) */

	movb	$0, %al		#; PIO default transfer mode
	movw	reg_addr - int13_handler + (2 * 2), %dx	#; CB_SC = interrupt reason register
	outb	%al, %dx

	call	delay400ns

	movb	$0x03, %al	#; 0x03 = set transfer mode based on value in sector count register
	movw	reg_addr - int13_handler + (1 * 2), %dx	#; CB_FR = Feature Register
	outb	%al, %dx

	call	delay400ns

	movb	$0xEF, %al		#; Set Features Command
	movw	reg_addr - int13_handler + (7 * 2), %dx		#; CB_CMD
	outb	%al, %dx

	call	delay400ns
#endif

#if 1
	movb	$0x08, %al		#; ATAPI Soft Reset
	movw	reg_addr - int13_handler + (7 * 2), %dx		#; CB_CMD
	outb	%al, %dx

	call	delay400ns
#endif

#; Test only: do a hard reset and see if it works
#if 1
	/* The ATA software reset mechanism, SRST, (bit 2 in the Device Control
	 * Register) cannot be used for ATAPI Device, because resets issued by
	 * the ATAPI driver would also reset any attached hard disk and vice
	 * versa. To solve this, ATAPI defines an ATAPI Soft Reset command
	 * using a reserved ATA opcode which could be decoded by the interface
	 * controller hardware.
	 */

	movb	$cmd_DC, %al
	orb	$0x04, %al	#; CB_DC_SRST = soft reset

	movw	reg_addr - int13_handler + (8 * 2), %dx		#; CB_DC
	outb	%al, %dx

	call	delay400ns
#endif

	movb	$cmd_DC, %al
	movw	reg_addr - int13_handler + (8 * 2), %dx		#; CB_DC
	outb	%al, %dx

	call	delay400ns

	call	set_timeout

	cmpb	$0, reg_dev_info - int13_handler
	je	1f			#; master not exist

	call	sub_atapi_delay

	call	reg_poll_busy

1:
	cmpb	$0, reg_dev_info - int13_handler + 1
	je	1f			#; slave not exist

	call	sub_atapi_delay

	//call	reg_poll_busy		#; added recently for test

	//jmp	1f			#; added recently for test

2:
	movw	$1, %ax

	call	__reg_select_dev

	movw	reg_addr - int13_handler + (2 * 2), %dx	#; CB_SC = interrupt reason register
	inb	%dx, %al
	movb	%al, %ah

	movw	reg_addr - int13_handler + (3 * 2), %dx	#; CB_SN = reserved for SAM TAG byte
	inb	%dx, %al

	cmpw	$0x0101, %ax
	je	1f

	call	check_timeout
	jna	2b 
1:
	popaw
	ret


test_atapi_ready:
#; return: cf =0 ready, cf =1 not ready
	pushaw
	movw	$2, %cx

1:
	pushw	%cx

	call	clear_atapi_buffer

	#; TEST UNIT READY Command
	#;
	#; The TEST UNIT READY command provides a means to check if the Device
	#; is ready. This is not a request for a self-test. If the Device would
	#; accept an appropriate medium-access command without returning CHECK
	#; CONDITION status, this command shall return a GOOD status. If the
	#; Device cannot become operational or is in a state such that a Host
	#; Computer action(e.g. START/STOP UNIT command with LoEj = 0 and Start
	#; = 1) is required to make the unit ready, the ATAPI CD-ROM Drive
	#; shall return CHECK CONDITION status with a sense key of NOT READY.
	#;
	#; Byte
	#;   0			Operation code (00h)
	#;   1			Reserved
	#;   2			Reserved
	#;   3			Reserved
	#;   4			Reserved
	#;   5			Reserved
	#;   6			Reserved
	#;   7			Reserved
	#;   8			Reserved
	#;   9			Reserved
	#;  10			Reserved
	#;  11			Reserved
	#;
	#; Using the TEST UNIT READY Command
	#;
	#; The TEST UNIT READY command is useful in that it allows a Host
	#; Computer to poll a Device until it is ready without the need to
	#; allocate space for returned data. It is especially useful to check
	#; cartridge status. ATAPI CD-ROM Drives are expected to respond
	#; promptly to indicate the current status of the device.

	# invoke reg_packet,byte,0,cs, atapi_tmp_buffer, 128
	pushw	$128
	pushw	$atapi_tmp_buffer - int13_handler
	pushw	%cs
	pushw	$0
	call	reg_packet
	addw	$8, %sp

//	/* debug print AX */
//	pushw	%ax
//	pushw	$test_atapi_ax - int13_handler	# the format string
//	call	realmode_printf
//	popw	%ax
//	popw	%ax

	orw	%ax, %ax
	jnz	2f

	call	get_atapi_sense

//	/* debug print AL, FLAGS */
//	pushfw
//	pushw	%ax
//	pushw	$test_atapi_al_flags - int13_handler	# the format string
//	call	realmode_printf
//	popw	%ax
//	popw	%ax
//	popfw

	jc	2f
	orb	%al, %al
	jnz	2f

	popw	%cx
	clc
	popaw
	ret
2:
	call	start_stop_unit		#; start unit

	popw	%cx
	loop	1b			#; try again

	stc
	popaw
	ret

//test_atapi_ax:
//	.ascii	"test_atapi_ax: AX=%X\r\n\0"

//test_atapi_al_flags:
//	.ascii	"test_atapi_al_flags: AX=%X, FLAGS=%X\r\n\0"


start_stop_unit:
#; return: cf =0 ready, cf =1 not ready
	pushaw
	movw	$1, %cx

1:
	pushw	%cx

	call	clear_atapi_buffer

	#; START/STOP UNIT Command
	#;
	#; The START/STOP UNIT command requests that the ATAPI CD-ROM Drive
	#; enable or disable media access operations.
	#;
	#;      |  bit     bit     bit     bit     bit     bit     bit     bit
	#; Byte |   7       6       5       4       3       2       1       0
	#; -----+--------------------------------------------------------------
	#;   0  |                    Operation code (1Bh)
	#; -----+-------------------------------------------------------+------
	#;   1  |                   Reserved                            | Immed
	#; -----+-------------------------------------------------------+------
	#;   2  |                        Reserved
	#; -----+--------------------------------------------------------------
	#;   3  |                        Reserved
	#; -----+-----------------------------------------------+-------+------
	#;   4  |                Reserved                       | LoEj  | Start
	#; -----+-----------------------------------------------+-------+------
	#;   5  |                        
	#; -----+--------------------------------------------------------------
	#;   6  |                        Reserved
	#; -----+--------------------------------------------------------------
	#;   7  |                        Reserved
	#; -----+--------------------------------------------------------------
	#;   8  |                        Reserved
	#; -----+--------------------------------------------------------------
	#;   9  |                        Reserved
	#; -----+--------------------------------------------------------------
	#;  10  |                        Reserved
	#; -----+--------------------------------------------------------------
	#;  11  |                        Reserved
	#; -----+--------------------------------------------------------------

	movb	$0x1B, atapi_cmd_buffer - int13_handler
	movb	$0x01, atapi_cmd_buffer - int13_handler + 4	#; start unit

	# invoke reg_packet,byte,0,cs, atapi_tmp_buffer, 128
	pushw	$128
	pushw	$atapi_tmp_buffer - int13_handler
	pushw	%cs
	pushw	$0
	call	reg_packet
	addw	$8, %sp

	orw	%ax, %ax
	jnz	2f

//	call	get_atapi_sense
//
//	jc	2f
//	orb	%al, %al
//	jnz	2f

	popw	%cx
	clc
	popaw
	ret
2:
	popw	%cx
	loop	1b

	stc
	popaw
	ret




reg_setup_base_addr:
#; input:  bx = base addr pointer
	pushw	%ax
	pushw	%di
	cld			# store upward
	movw	$reg_addr - int13_handler, %di	# points to 10-word space
	movw	%cs:(%bx), %ax	# get base address
	# store 8 ports(command block registers)

#if 0
	pushw	18(%di)
	pushw	16(%di)
	pushw	14(%di)
	pushw	12(%di)
	pushw	10(%di)
	pushw	8(%di)
	pushw	6(%di)
	pushw	4(%di)
	pushw	2(%di)
	pushw	(%di)
	pushw	2(%bx)
	pushw	%ax
	pushw	$reg_addresses - int13_handler		# the format string
	call	realmode_printf
	addw	$26, %sp			# adjust the stack pointer
#endif

	stosw
	incw	%ax
	stosw
	incw	%ax
	stosw
	incw	%ax
	stosw
	incw	%ax
	stosw
	incw	%ax
	stosw
	incw	%ax
	stosw
	incw	%ax
	stosw

	movw	%cs:2(%bx), %ax		# get base address
	stosw				# store 2 ports(control block registers)
	incw	%ax
	stosw
	popw	%di
	popw	%ax
	ret

#if 0
reg_addresses:
	.ascii	"reg_addresses: Data=%X, Ctrl=%X, di: %X, %X, %X, %X, %X, %X, %X, %X, %X, %X\r\n\0"
#endif

set_timeout:
	pushl	%eax
	call	read_bios_time
	addl	$(5 * 18), %eax	#; 20 seconds
				# not 20 seconds, but 5 seconds
	 			#; FIXME: Midnight overflow
	 			# Midnight overflow is handled in check_timeout
	movl	%eax, %cs:(time_out - int13_handler)
	popl	%eax
	ret


check_timeout:
#; you need to setup the timeout first
	pushl	%eax
	pushl	%ebx
	pushl	%edx
	call	read_bios_time
	movl	time_out - int13_handler, %ebx
	movl	%ebx, %edx
	subl	$(5 * 18), %ebx		# the time when we set_timeout
	cmpl	%ebx, %eax
	jnb	1f
	/* the next day */
	addl	$0x001800B0, %eax	/* 24 hours = 0x1800B0 ticks */
1:
	cmpl	%edx, %eax
	popl	%edx
	popl	%ebx
	popl	%eax
	ret


clear_atapi_buffer:
	pushaw
	pushw	%es
	pushw	%cs
	popw	%es
	cld
	movw	$atapi_tmp_buffer - int13_handler, %di
	movw	$128, %cx	# but note the buffer is 256-byte long!
	xorb	%al, %al
	rep stosb		# added the lost rep prefix
	movw	$atapi_cmd_buffer - int13_handler, %di
	movw	$16, %cx
	rep stosb		# added the lost rep prefix
	popw	%es
	popaw
	ret


reg_packet:	
#;proc	reg_packet,withlocal,dir,packet_seg,packet_off,packet_len
#; input:
#; return ax = 0 noerror, ah = error code al= error bit
#;	 cx = len
	pushaw

	movw	%sp, %bp

	call	set_timeout
	movb	$0, _pre_fail_bit7_  - int13_handler
	
#;	outbytes CB_DC,cmd_DC_ni,CB_FR,0,CB_SC,0,CB_SN,0,
	# outbytes CB_DC,cmd_DC,CB_FR,0,CB_SC,0,CB_SN,0,
	movb	$cmd_DC, %al
	movw	reg_addr - int13_handler + (8 * 2), %dx	#; CB_DC
	outb	%al, %dx

	call	delay400ns	#; added recently

	call	sub_atapi_delay	#; added recently

	movb	$0, %al
	movw	reg_addr - int13_handler + (1 * 2), %dx	#; CB_FR = Feature Register
	outb	%al, %dx

	movb	$0, %al
	movw	reg_addr - int13_handler + (2 * 2), %dx	#; CB_SC = interrupt reason register
	outb	%al, %dx

	movb	$0, %al
	movw	reg_addr - int13_handler + (3 * 2), %dx	#; CB_SN = reserved for SAM TAG byte
	outb	%al, %dx


	# outbytes CB_CL,[.packet_len],CB_CH,[.packet_len+1]
	movb	24(%bp), %al		#; packet_len low byte
	movw	reg_addr - int13_handler + (4 * 2), %dx	#; CB_CL = byte count low
	outb	%al, %dx

	movb	25(%bp), %al		#; packet_len high byte
	movw	reg_addr - int13_handler + (5 * 2), %dx	#; CB_CH = byte count high
	outb	%al, %dx

	# outbyte CB_DH,[reg_cur_dev]
	movb	reg_cur_dev - int13_handler, %al
	movw	reg_addr - int13_handler + (6 * 2), %dx	#; CB_DH = drive select
	outb	%al, %dx

	# outbyte CB_CMD,CMD_PACKET
	movb	$0xA0, %al		#; CMD_PACKET
	movw	reg_addr - int13_handler + (7 * 2), %dx		#; CB_CMD
	outb	%al, %dx

	call	delay400ns

	call	sub_atapi_delay

	subw	%bx, %bx		#; clear error number

	# while {inbyte CB_ASTAT},{test al,CB_STAT_BSY|CB_STAT_ERR|CB_STAT_DRQ},z
3:
	# inbyte CB_ASTAT
	movw	reg_addr - int13_handler + (8 * 2), %dx		#; CB_ASTAT=8, CB_STAT=7
	inb	%dx, %al

	testb	$(CB_STAT_BSY | CB_STAT_DRQ | CB_STAT_ERR), %al
	jnz	3f

	orb	$FAILBIT0, %bl		#; error
	call	check_timeout
	jna	3b
3:
	# endwhile
	
	# while {inbyte CB_ASTAT},{test al, CB_STAT_BSY}, nz
3:
	# inbyte CB_ASTAT
	movw	reg_addr - int13_handler + (8 * 2), %dx		#; CB_ASTAT=8, CB_STAT=7
	inb	%dx, %al

	testb	$CB_STAT_BSY, %al
	jz	3f

	call	check_timeout
	jna	3b
	movw	$-1, 18(%bp)
	movb	$51, %bh		#; error
3:
	# endwhile
	
	cmpb	$0, %bh
	jnz	2f			#; error
	
	# inbyte CB_STAT,[.status]
	movw	reg_addr - int13_handler + (7 * 2), %dx		#; CB_STAT
	inb	%dx, %al
	movb	%al, _status_ - int13_handler

	# inbyte CB_SC, [.reason]
	movw	reg_addr - int13_handler + (2 * 2), %dx	#; CB_SC = interrupt reason register
	inb	%dx, %al
	movb	%al, _reason_ - int13_handler

	# inbyte CB_CL, [.bcnt]
	movw	reg_addr - int13_handler + (4 * 2), %dx	#; CB_CL = byte count low
	inb	%dx, %al
	movb	%al, _bcnt_ - int13_handler

	# inbyte CB_CH, [.bcnt+1]
	movw	reg_addr - int13_handler + (5 * 2), %dx	#; CB_CH = byte count high
	inb	%dx, %al
	movb	%al, _bcnt_ - int13_handler + 1

	movb	_status_ - int13_handler, %al
	andb	$(CB_STAT_BSY | CB_STAT_DRQ), %al
	cmpb	$CB_STAT_DRQ, %al
	jz	3f
	movb	$52, %bh		#; error

	jmp	2f
3:

#ifdef sane_check	
	movb	_reason_ - int13_handler, %al
	testb	$(CB_SC_P_TAG | CB_SC_P_REL | CB_SC_P_IO), %al
	jnz	3f
	testb	$CB_SC_P_CD, %al
	jnz	4f
3:
	orb	$FAILBIT2, %bl		#; error
4:
	movw	_bcnt_ - int13_handler, %ax
	cmpw	24(%bp), %ax
	jz	3f
	orb	$FAILBIT3, %bl		#; error

3:

#endif	//; sane_check

	movw	$atapi_cmd_buffer - int13_handler, %si
#if 0
	movw	$12, %cx		#; cmd_buff_len is 12
	shrw	$1, %cx
#else
	movw	$6, %cx			#; cmd_buff_len is 12
#endif
	movw	reg_addr - int13_handler + (0 * 2), %dx		#; CB_DATA = 16-bit data port
	cld
	repz outsw
	
	call	delay400ns

	subw	%cx, %cx
3:
	# while

	call	sub_atapi_delay
4:	    
	# while {inbyte CB_ASTAT},{test al,CB_STAT_BSY},nz
	# inbyte CB_ASTAT
	movw	reg_addr - int13_handler + (8 * 2), %dx		#; CB_ASTAT=8, CB_STAT=7
	inb	%dx, %al

	testb	$CB_STAT_BSY, %al
	jz	4f
	call	check_timeout
	jna	4b
	movb	$54, %bh		#; error
	jmp	2f
	# endwhile
4:

	#; Data transfer loop
	#; read the primary state register

	# inbyte CB_STAT,[.status]
	movw	reg_addr - int13_handler + (7 * 2), %dx		#; CB_STAT
	inb	%dx, %al
	movb	%al, _status_ - int13_handler

	# inbyte CB_SC, [.reason]
	movw	reg_addr - int13_handler + (2 * 2), %dx	#; CB_SC = interrupt reason register
	inb	%dx, %al
	movb	%al, _reason_ - int13_handler

	# inbyte CB_CL, [.bcnt]
	movw	reg_addr - int13_handler + (4 * 2), %dx	#; CB_CL = byte count low
	inb	%dx, %al
	movb	%al, _bcnt_ - int13_handler

	# inbyte CB_CH, [.bcnt+1]
	movw	reg_addr - int13_handler + (5 * 2), %dx	#; CB_CH = byte count high
	inb	%dx, %al
	movb	%al, _bcnt_ - int13_handler + 1

	testb	$(CB_STAT_BSY | CB_STAT_DRQ), _status_ - int13_handler
	jnz	4f
	orb	$0x80, 18(%bp)		#; NON_DATA
	jmp	2f
4:
	movb	_status_ - int13_handler, %al
	andb	$(CB_STAT_BSY | CB_STAT_DRQ), %al
	cmpb	$CB_STAT_DRQ, %al
	jz	4f
	movb	$55, %bh		#; error
	jmp	2f
4:

#ifdef sane_check
	testb	$(CB_SC_P_TAG | CB_SC_P_REL | CB_SC_P_CD), _reason_ - int13_handler
	jz	4f
	orb	$FAILBIT4, %bl		#; error
4:
	testb	$CB_SC_P_IO, _reason_ - int13_handler
	jz	4f
	cmpb	$0, 18(%bp)
	jz	4f
	orb	$FAILBIT5, %bl		#; error
4:
#endif	//; sane_check

	#; do the slow data transfer

	call	sub_atapi_delay

	movw	_bcnt_ - int13_handler, %ax
	orw	%ax, %ax
	jnz	4f
	movb	$60, %bh		#; error
	orb	$0x80, 18(%bp)		#; NON_DATA
	jmp	2f
4:

#ifdef sane_check 
	cmpw	$0x8000, %ax		#; REG_ATAPI_MAX_BYTES
	jna	4f
	orb	$FAILBIT6, %bl		#; error
4:
#endif	//; sane_check
	movb	_pre_fail_bit7_ - int13_handler, %dl
	orb	%dl, %bl		#; error
	testb	$1, %al
	setnz	_pre_fail_bit7_ - int13_handler

	movw	%cx, %dx 
	addw	%ax, %dx
	cmpw	24(%bp), %dx
	jna	4f 
	movb	$59, %bh		#; error
	orb	$0x80, 18(%bp)		#; NON_DATA
	jmp	2f
4:

	pushw	%dx
	movw	%ax, %cx
	incw	%cx
	shrw	$1, %cx
	movw	reg_addr - int13_handler + (0 * 2), %dx		#; CB_DATA = 16-bit data port
	cld
	cmpb	$0, 18(%bp)
	jz	4f
	pushw	%ds
	movw	20(%bp), %ds		#; packet_seg
	movw	22(%bp), %si		#; packet_off
	repz outsw
	popw	%ds
	jmp	5f
4:
	pushw	%es
	movw	20(%bp), %es		#; packet_seg
	movw	22(%bp), %di		#; packet_off
	repz insw
	popw	%es
5:
	popw	%cx

	addw	%ax, 22(%bp)		#; packet_off
	call	delay400ns
	jmp	3b
	# endwhile	
3:
	testb	$0x80, 18(%bp)		#; NON_DATA
	jnz	3f
	call	sub_atapi_delay

	call	check_timeout		# !!added recently!!
	jna	3f

	movb	$57, %bh		#; error: time is out
	jmp	2f
3:

	# inbyte CB_STAT, #; [.status]
	movw	reg_addr - int13_handler + (7 * 2), %dx		#; CB_STAT
	inb	%dx, %al

	testb	$(CB_STAT_BSY | CB_STAT_DRQ | CB_STAT_ERR), %al
	jz	1f

	movb	$58, %bh		#; error
	jmp	2f
1:
	# inbyte CB_SC, [.reason]
	movw	reg_addr - int13_handler + (2 * 2), %dx	#; CB_SC = interrupt reason register
	inb	%dx, %al
	movb	%al, _reason_ - int13_handler
2:

#ifdef check_extra_fail
	movb	_reason_ - int13_handler, %al
	testb	$(CB_SC_P_TAG | CB_SC_P_REL), %al
	jnz	1f
	testb	$CB_SC_P_IO, %al
	jz	1f
	testb	$CB_SC_P_CD, %al
	jnz	2f
1:
	orw	$FAILBIT8, %bx		#; error
2:
#endif	//; check_extra_fail

#;	outbyte CB_DC,cmd_DC

	movw	%bx, 14(%bp)	# __AX	#; error
	movw	%cx, 12(%bp)	# __CX

	popaw
	ret

#	local status,1,reason,1,bcnt,2,pre_fail_bit7,1
_status_:		.byte	0
_reason_:		.byte	0
_bcnt_:			.byte	0, 0
_pre_fail_bit7_:	.byte	0
# //; end of function reg_packet


delay400ns:

	pushw	%cx
	movw	$0x0040, %cx
1:
	pause
	loop	1b
	popw	%cx
	ret

	# inbyte CB_ASTAT
	movw	reg_addr - int13_handler + (8 * 2), %dx		#; CB_ASTAT=8, CB_STAT=7
	inb	%dx, %al
	inb	%dx, %al
	inb	%dx, %al
	inb	%dx, %al
	ret


sub_atapi_delay:
#; delay a few clicks
	cmpl	$0, EXT_C(slow_atapi_device) - int13_handler
	jz	1f

	# delay 1 millisecond

	pushl	%ecx
	//pushfw

	//sti		#; sti should already be done by the caller

	movl	delay_repeat_num - int13_handler, %ecx	# loops per millisecond
2:
	call	read_bios_time
	cmpw	%ax, %ax	# for more accurate timing
	addr32 loope	2b

	//popfw
	popl	%ecx

1:
	ret


reg_poll_busy:
#; need to setup the timeout first
#;return ax=0	ok
#;	ax = 1	timeout

1:
	movw	reg_addr - int13_handler + (7 * 2), %dx		#; CB_STAT
	inb	%dx, %al

	andb	$0x80, %al	# CB_STAT_BSY
	jz	1f
	call	check_timeout
	jna	1b
	# timeout
1:
	ret


get_atapi_sense:
#; return: cf =0 success, al = sense key, bl = asc, bh = ascq
#;	  cf =1 failed 

	call	clear_atapi_buffer

	#; REQUEST SENSE Command
	#;
	#; The REQUEST SENSE command requests that the ATAPI CD-ROM Drive
	#; transfer sense data to the Host Computer.
	#;
	#; Byte
	#;   0			Operation code (03h)
	#;   1			Reserved
	#;   2			Reserved
	#;   3			Reserved
	#;   4			Allocation Length
	#;   5			Reserved
	#;   6			Reserved
	#;   7			Reserved
	#;   8			Reserved
	#;   9			Reserved
	#;  10			Reserved
	#;  11			Reserved

	movb	$0x03, atapi_cmd_buffer - int13_handler
	movb	$32, atapi_cmd_buffer - int13_handler + 4

	# invoke reg_packet,byte,0,cs, atapi_tmp_buffer, 128
	pushw	$128
	pushw	$atapi_tmp_buffer - int13_handler
	pushw	%cs
	pushw	$0
	call	reg_packet
	addw	$8, %sp

	orw	%ax, %ax
	jnz	1f

	movb	atapi_tmp_buffer - int13_handler, %al
	/* bit 7 is `Valid' bit, and should be 1
	 * bit 0-6 is the error code and can be 70h or 71h
	 */ 
	andb	$0x7f, %al
	cmpb	$0x70, %al
	je	2f
	cmpb	$0x71, %al
	jne	1f
2:
	movb	atapi_tmp_buffer - int13_handler + 2, %al	#; get sense key
	andb	$0x0f, %al	#; low 4 bits are sense key
	xorw	%bx, %bx
	cmpb	$0x06, atapi_tmp_buffer - int13_handler + 7	#; additional sense length
	jb	3f
	movw	atapi_tmp_buffer - int13_handler + 12, %bx
3:
	clc
	ret
1:
	stc
	ret


edd30_for_cdrom:
//	; Stack layout:
//	;   +10 INT flags
//	;   +8  INT CS
//	;   +6  INT IP
//	;   +2  EAX
//	; BP+0 BP
//	;   -2 ax
//	;   -4 cx
//	;   -6 dx
//	;   -8 bx
//	;   -10 sp
//	;   -12 bp
//	;   -14 si
//	;   -16 di
//	;   -18 ds
//	;   -20 es
//	;   -24 edx

	/* will read these variables:
	 *	int13_old_eax
	 *	int13_old_ebx
	 *	int13_old_ecx
	 *	int13_old_edx
	 *	int13_old_esi
	 *	int13_old_edi
	 *	int13_old_ebp
	 *	int13_old_ds
	 *	int13_old_es
	 *	int13_old_flags
	 *	int13_old_cs_ip
	 * will write these variables:
	 *	int13_old_eax
	 *	int13_old_ebx
	 *	int13_old_ecx
	 *	int13_old_flags
	 */

	sti

	cld

	pushw	%cs
	popw	%ds

	movzbw	%dl, %ax
	subb	%cs:(EXT_C(min_cdrom_id) - int13_handler), %al
	call	select_atapi	#; select_atapi_force
	movw	%cs:(int13_old_eax - int13_handler), %ax

	jnc	1f
	movb	$0xAA, %ah
	jmp	2f	//fail_out
1:
	cmpb	$0, %ah
	je	6f	//reset
	cmpb	$1, %ah
	je	7f	//get_last_stat
	cmpb	$0x41, %ah
	je	8f	//install_check
	cmpb	$0x42, %ah
	je	9f	//ext_read
	cmpb	$0x43, %ah
	je	10f	//ext_write
	cmpb	$0x44, %ah		/* verify sectors */
	je	5f	//success_out
	cmpb	$0x47, %ah		/* extended seek */
	je	5f	//success_out
	cmpb	$0x48, %ah
	je	11f	//get_drv_param
	cmpb	$0x4B, %ah
	jne	3f	//invalid_cmd

	//stop_disk_emu:
	cmpb	$1, %al			/* only 0x4B01 supported */
	jne	3f	//invalid_cmd

	movw	%si, %di
	movw	%cs:(int13_old_ds - int13_handler), %es
	movw	$0x0013, %ax	/* packet size=13h, boot type=0 (no-emu) */
	cld
	stosw
	//movb	%dl, %al	/* drive=DL, controller=0 */
	movb	%cs:(int13_old_edx - int13_handler), %al	/* drive=DL, controller=0 */
	stosw
	xorw	%ax, %ax
	stosw
	stosw			/* LBA for no-emu image=0 */
	stosw			/* device specification */
	stosw			/* user buffer segment */
	stosw			/* load segment */
	movb	$4, %al
	stosw			/* sector count=4 */
				/* CHS makes no sense for no-emu */
	jmp	5f	//success_out

11:	//get_drv_param:
	movw	%cs:(int13_old_ds - int13_handler), %ds
	cmpw	$26, (%si)
	jb	3f		//invalid_cmd

	movw	$26, (%si)
//	movw	$0x74, 2(%si)		#; struc_extparam.flags: removable, lock, chg line
	movw	$0x00, 2(%si)		# none, tinybit 2007-11-15
	movw	$0x800, 24(%si)		# bytes per sect=2048
	xorl	%eax, %eax
	decw	%ax
	movl	%eax, 4(%si)		# cylinders=0xFFFF
	movb	$0, %ah
	movl	%eax, 8(%si)		# heads=0xFF
	movb	$15, %al
	movl	%eax, 12(%si)		# sectors per track=15
	movl	%eax, 20(%si)		# total sectors hi dword=0
	xorw	%ax, %ax		# CF cleared
	decl	%eax			# EAX=0xFFFFFFFF
	movl	%eax, 16(%si)		# total sectors lo dword
					# CF is cleared
	jmp	5f	//success_out

10:	//ext_write:
	movb	$0x03, %ah	# error code of write-protection
	jmp	2f	//fail_out

9:	//ext_read:
	call	edd30_read_cdrom
	jnc	5f	//success_out
	jmp	2f	//fail_out

8:	//install_check:
	cmpw	$0x55AA, %bx	# added by tinybit 2007-11-15
	jne	3f	//invalid_cmd

	movw	$0xAA55, %cs:(int13_old_ebx - int13_handler)	#; bx=0xaa55
	movb	$0x21, %ah	# ah=0x21  edd-1.1
	movb	$0x01, %cs:(int13_old_ecx - int13_handler)	# cx=0x01, ext disk access ok -- tinybit 2007-11-15
	jmp	4f	//success_out_no_ah

7:	//get_last_stat:
	movb	%cs:(int13_last_stat - int13_handler), %ah
	jmp	4f	//success_out_no_ah

6:	//reset:
	call	reg_reset
	movw	%cs:(atapi_cur_dev - int13_handler), %ax	# device serial number
	call	select_atapi_force

5:	//success_out:
	xorb	%ah, %ah

4:	//success_out_no_ah:
	andb	$0xFE, %cs:(int13_old_flags - int13_handler)
	jmp	1f

3:	//invalid_cmd:
	movb	$0x01, %ah

2:	//fail_out:
	orb	$1, %cs:(int13_old_flags - int13_handler)	// set CF=1 for ERROR

1:
	/* set error code AH */
	movb	%ah, %cs:(int13_last_stat - int13_handler)
	movb	%ah, %cs:(int13_old_eax + 1 - int13_handler)

	movl	%cs:(int13_old_eax - int13_handler), %eax
	movl	%cs:(int13_old_ebx - int13_handler), %ebx
	movl	%cs:(int13_old_ecx - int13_handler), %ecx
	movl	%cs:(int13_old_edx - int13_handler), %edx
	movl	%cs:(int13_old_esi - int13_handler), %esi
	movl	%cs:(int13_old_edi - int13_handler), %edi
	movl	%cs:(int13_old_ebp - int13_handler), %ebp
	movw	%cs:(int13_old_ds - int13_handler), %ds
	movw	%cs:(int13_old_es - int13_handler), %es

	/* restore old flags */
	pushw	%cs:(int13_old_flags - int13_handler)
	popfw
	/* transfer control to caller */
	ljmp	*%cs:(int13_old_cs_ip - int13_handler)

#;============================================================================

int13_last_stat:	.byte	0			#; the error code in AH

start_of_atapi_data:

atapi_cur_dev:		.word	0	#; device serial number
reg_cur_dev:		.byte	0	#; 0xA0 for master, 0xB0 for slave
time_out:		.long	0
reg_dev_info:		.byte	0, 0


atapi_dev_base:		.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device

atapi_dev_base_bak:	.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device
			.word	0, 0	#; base pointer, device

reg_addr:		.word	0, 0, 0, 0, 0, 0, 0, 0, 0, 0
atapi_cmd_buffer:	.space	16
atapi_tmp_buffer:	.space	256
//atapi_devinfo:	.space	32	# SIZE_OF_ATAPI_DEVINFO
delay_repeat_num:	.long	0	# loops per millisecond

end_of_atapi_data:

			.align	16

edd30_disk_buffer:	.space	0x800

ENTRY(slow_atapi_device)
			.long	0

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
 * 		pushw	$format_string - int13_handler
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

	.align	16

GDT_data:		/* used by int15/ah=87h */

/*00*/	.long	0, 0	/* unused descriptor, must be 0 */
/*08*/	.long	0, 0	/* GDT descriptor, must be 0 */

	/* source descriptor */
/*10*/	.word	0xffff	/* segment limit, 64K */
/*12*/	.byte	0, 0, 0	/* physical address(low 24 bits) */
/*15*/	.byte	0x93	/* access rights, 93h=readable/writable */
/*16*/	.byte	0	/* low 4 bits are high 4 bits of segment limit(here
			   should be 0). high 4 bits are flags, also should
			   be set to 0 for this function call */
/*17*/	.byte	0	/* physical address(high 8 bits) */

	/* destination descriptor */
/*18*/	.word	0xffff	/* segment limit, 64K */
/*1A*/	.byte	0, 0, 0	/* physical address(low 24 bits) */
/*1D*/	.byte	0x93	/* access rights, 93h=readable/writable */
/*1E*/	.byte	0	/* low 4 bits are high 4 bits of segment limit(here
			   should be 0). high 4 bits are flags, also should
			   be set to 0 for this function call */
/*1F*/	.byte	0	/* physical address(high 8 bits) */

/*20*/	.long	0, 0	/* code segment descriptor, must be 0 */
/*28*/	.long	0, 0	/* stack segment descriptor, must be 0 */
/*30*/

	.align	16

MyGDT:	.word	MyGDTEnd - MyGDT - 1
	.long	0		/* Pointer to self */
	.word	0

MyRMDS:	.long	0x0000ffff	/* 64K data segment */
	.long	0x00009200

MyPMDS:	.long	0x0000ffff	/* 4GB data segment */
	.long	0x00cf9200

MyGDTEnd:


	#;*******************************************************************
	#;			ATA Registers Layout
	#;*******************************************************************
	#;
	#; Address		Read			Write
	#; ---------	---------------------	-----------------------------
	#; A N 0 0 0	16-bit data port for both read and write
	#; ------------------------------------------------------------------
	#; A N 0 0 1	ATAPI/ATA Error(Read)	ATAPI/ATA Feature(Write)
	#; ------------------------------------------------------------------
	#; A N 0 1 0	ATAPI Interrupt Reason(Read) / ATA Sector Count
	#; ------------------------------------------------------------------
	#; A N 0 1 1	Reserved for SAM TAG Byte / ATA Sector Number
	#; ------------------------------------------------------------------
	#; A N 1 0 0	ATAPI Byte Count LSB(R/W) / ATA Cylinder Low(R/W)
	#; ------------------------------------------------------------------
	#; A N 1 0 1	ATAPI Byte Count MSB(R/W) / ATA Cylinder High(R/W)
	#; ------------------------------------------------------------------
	#; A N 1 1 0	ATAPI Drive Select(R/W) / ATA Drive/Head Select(R/W)
	#; ------------------------------------------------------------------
	#; A N 1 1 1	ATAPI/ATA Status(Read)	ATA Command(Write) 
	#; ------------------------------------------------------------------
	#; N A 1 1 0	Alternate Status(Read)	Device Control(Write) 
	#; ------------------------------------------------------------------

reg_base_addr:
			.word	0x01f0, 0x03f6
			.word	0x0170, 0x0376
			.word	0x00f0, 0x02f6
			#;.word	0x0070, 0x0276	//port 70 and 71 is for CMOS
			.word	0x0180, 0x0386
			.word	0x6b00, 0x6f00
			.word	0x7300, 0x7700
ENTRY(reg_base_addr_append)
			.word	0, 0, 0, 0

/* EBIOS_disk_address_packet should be at the end of the handler because some
 * buggy BIOSes could destroy the memory that immediately follows.
 */

EBIOS_disk_address_packet:
	.byte	0x10	/* packet size, 16 or more */
	.byte	0	/* reserved, must be 0 */
	.byte	0	/* number of sectors, must be from 1 to 127 */
	.byte	0	/* reserved, must be 0 */
	.word	0	/* displacement of memory address */
	.word	0	/* segment of memory address */
	.long	0	/* 64bit, start logical sector number */
	.long	0

/* Don't insert code or data here! Buggy BIOSes could overwrite this area! */

//	.align	16

//	.space	0x1000	/* 4KB stack */

int13_handler_end:
	
#;============================================================================

#define CDROM_INIT
#ifdef CDROM_INIT

/* unsigned long
 * init_atapi() : return number of atapi cdrom devices.
 */

ENTRY(init_atapi)

	.code32

	pushl	%ebp
	pushl	%ebx

	call	EXT_C(prot_to_real)	/* enter real mode */

	.code16

	sti		/* enable interrupt for ATAPI */

	cld

	/* set CS base to be int13_handler */
#if 0
	ljmp	$((ABS(int13_handler)) >> 4), $(1f - int13_handler)
#else
	.byte	0xEA
	.word	1f - int13_handler
	.word	(ABS(int13_handler)) >> 4
#endif
1:
	pushaw
	pushw	%es
	pushw	%ds

	pushw	%cs
	popw	%ds
	pushw	%cs
	popw	%es
	xorw	%ax, %ax

	# initialize variables

	movw	$(start_of_atapi_data - int13_handler), %di
	movw	$(end_of_atapi_data - start_of_atapi_data), %cx
	repz stosb

	decw	atapi_cur_dev - int13_handler	# device serial number initialized to 0xFFFF

	#; begin init_timer

	call	read_bios_time
	movw	%ax, %bx		#; store initial timer in BX
1:
	call	read_bios_time
	cmpw	%ax, %bx		#; timer just changed?
	je	1b			#; no, continue.

	/* now AX=BX+1 */

	movw	%ax, %bx		#; store initial timer in BX
	xorl	%ecx, %ecx
1:
	call	read_bios_time
	cmpw	%ax, %bx		#; timer changed?
	addr32 loope	1b

	negl	%ecx

	/* ECX loops=a tick=1/18.2second=1000/18.2(=54.9) milliseconds */

	movl	%ecx, %eax
	xorl	%edx, %edx
	xorl	%ecx, %ecx
	movw	$55, %cx		# a tick is about 55 milliseconds
	divl	%ecx

	/* EAX=loops per millisecond */

	movl	%eax, delay_repeat_num - int13_handler

	#; end init_timer

	call	init_atapi_cdroms

	//movw	$-1, atapi_cur_dev - int13_handler	# device serial number initialized to 0xFFFF

	popw	%ds
	popw	%es

	movw	%sp, %bp
	movw	%cx, 8(%bp)	#; 8(%bp) is old BX on stack !
	popaw

	ljmp	$0, $ABS(1f)
1:

	DATA32	call	EXT_C(real_to_prot)
	.code32

	movzwl	%bx, %eax

	popl	%ebx
	popl	%ebp
	ret

#endif	/* CDROM_INIT */


#ifdef CDROM_INIT

init_atapi_cdroms:

	.code16

#; return: CF=0 success, CX=number of cdroms
#;         CF=1 failed, no cdrom found
#;	push cs
#;	pop es

	call	reg_probe	#; return cx = number of atapi devices

	orw	%cx, %cx
	jnz	1f

	call	reg_probe	#; return cx = number of atapi devices

	orw	%cx, %cx
	jnz	1f

	stc
	ret

1:
#if 1
	movw	$atapi_dev_base - int13_handler, %si	#; array of ATAPI reg pointer and dev
	movw	$atapi_dev_base_bak - int13_handler, %di	#; for CDROMs

	cld

	pushw	%si
	pushw	%di

	xorw	%ax, %ax
	xorw	%bx, %bx
1:
	call	select_atapi_force	#;input: ax = device serial number
					#;return: cf=0 success, cf=1 failed


	jc	2f

	call	check_atapi_cdrom	#;return: cf=0 is cdrom, cf=1 not cdrom

	jc	2f

	/* It is CDROM */

	incw	%bx			#;count the cdroms
	movsw				#;store CDROM base pointer
	movsw				#;store CDROM device number
	subw	$4, %si

	# debug print the reg and dev
	pushw	%bx

	movw	(%si), %bx		# BX=reg group pointer

	pushw	2(%si)			# CDROM device number
	pushw	2(%bx)			# base port of control block regs, i.e., device control port
	pushw	(%bx)			# base port of command block regs, i.e., data port
	pushw	$cdrom_reg_dev - int13_handler		# the format string
	call	realmode_printf
	addw	$8, %sp			# adjust the stack pointer

	popw	%bx

2:
	addw	$4, %si
	incw	%ax			#; try next ATAPI device
	loop	1b

	popw	%si			#; points to atapi_dev_base_bak, which is for CDROMs
	popw	%di			#; points to atapi_dev_base, which is for ATAPIs

	movw	$64, %cx		#; overwrite ATAPIs with CDROMs
	repz movsb

	movb	%bl, EXT_C(atapi_dev_count) - int13_handler
	movb	EXT_C(min_cdrom_id) - int13_handler, %cl
	addb	%bl, %cl
	decw	%cx
	movb	%cl, max_cdrom_id - int13_handler
	movw	%bx, %cx
#endif

	clc
	ret

cdrom_reg_dev:
	.ascii	"CDROM device found: Data=%X, Ctrl=%X, dev=%X(Note: 0=master, 1=slave)\r\n\0"

#endif	/* CDROM_INIT */


#ifdef CDROM_INIT

/* Called by init_atapi_cdroms
 * Calls reg_setup_base_addr, reg_reset 
 */
reg_probe:

	.code16

#; return cx = number of atapi devices
	pushw	%ax
	pushw	%bx
	pushw	%si
	pushw	%di
	cld
	movb	$0, EXT_C(atapi_dev_count) - int13_handler		# reset counter
	movw	$reg_base_addr - int13_handler, %bx		# BX points to base address array
	movw	$atapi_dev_base - int13_handler, %di		# will store base pointers and device numbers
1:
	call	reg_setup_base_addr	# setup the base reg addresses(reg_addr) for reg base address BX

	#; begin reg_probe_exist
	movb	$cmd_DC, %al
	movw	reg_addr - int13_handler + (8 * 2), %dx		#; CB_DC
	outb	%al, %dx

	movw	$0, %ax

	call	reg_probe_dev_exist

	movb	%al, reg_dev_info - int13_handler	# master device existence
	movw	$1, %ax

	call	reg_probe_dev_exist

	movb	%al, reg_dev_info - int13_handler + 1	# slave device existence

	#; end reg_probe_exist

	call	reg_reset

	xor	%si, %si		# SI=0 for master
2:
//	movw	%si, %ax
//	call	reg_probe_dev_exist

	cmpb	$0, (reg_dev_info - int13_handler)(%si)		# check existence
//	cmpb	$0, %al						# check existence
	je	3f						# device not exist, so skip

	/* The device exists, so do a further check for device type.  */

	movw	%si, %ax

	#; begin reg_check_dev_type

	#; call after a reset

	call	__reg_select_dev

	movw	reg_addr - int13_handler + (2 * 2), %dx	#; CB_SC = interrupt reason register
	inb	%dx, %al
	movb	%al, %ah

	movw	reg_addr - int13_handler + (3 * 2), %dx	#; CB_SN = reserved for SAM TAG byte
	inb	%dx, %al

	cmpw	$0x0101, %ax		# success?
	movw	$1, %ax			# REG_CONFIG_TYPE_UNKN
	jne	4f			# No. The device type is unknown.

	movw	reg_addr - int13_handler + (4 * 2), %dx	#; CB_CL = byte count low
	inb	%dx, %al
	movb	%al, %ah

	movw	reg_addr - int13_handler + (5 * 2), %dx	#; CB_CH = byte count high
	inb	%dx, %al

	cmpw	$0x14EB, %ax		# Is ATAPI?
	je	5f			# yes.

	testb	%al, %al		# 0 is for ATA
	movw	$1, %ax			# REG_CONFIG_TYPE_UNKN
	jnz	4f
					# AX=1

	movw	reg_addr - int13_handler + (7 * 2), %dx		#; CB_STAT
	inb	%dx, %al
					# AH=0
	//if AL==0, then AX=1=REG_CONFIG_TYPE_UNKN, else AX=2=REG_CONFIG_TYPE_ATA
	testb	%al, %al
	setne	%al
	incw	%ax
	jmp	4f
5:
	movw	$3, %ax			# REG_CONFIG_TYPE_ATAPI
4:
	
	#; end reg_check_dev_type


	movb	%al, (reg_dev_info - int13_handler)(%si)	#; added (%si) recently
	cmpb	$3, %al			# Is ATAPI?
	jne	3f			# no, ignore it.

	#; It is ATAPI, so add it to the list at atapi_dev_base
	incb	EXT_C(atapi_dev_count) - int13_handler	# count it
	movw	%bx, %ax		# store the pointer to the base reg pair
	stosw
	movw	%si, %ax		# store the device number(master/slave)
	stosw

	# debug print the reg and dev
	pushw	%si
	pushw	2(%bx)			# base port of control block regs, i.e., device control port
	pushw	(%bx)			# base port of command block regs, i.e., data port
	pushw	$atapi_reg_dev - int13_handler		# the format string
	call	realmode_printf
	addw	$8, %sp			# adjust the stack pointer
3:
	incw	%si			# SI=1 for slave
	cmpw	$2, %si
	jb	2b

	addw	$4, %bx			# try next group of base reg
	#; incw	%bx			# try next group of base reg
	#; incw	%bx
	cmpw	$0, (%bx)		# end?
	jnz	1b			# no, probe next reg group

	movzbw	EXT_C(atapi_dev_count) - int13_handler, %cx
	movw	%cx, %bx
	decw	%bx
	movb	EXT_C(min_cdrom_id) - int13_handler, %al
	addb	%bl, %al
	movb	%al, max_cdrom_id - int13_handler
	popw	%di
	popw	%si
	popw	%bx
	popw	%ax
	ret

atapi_reg_dev:
	.ascii	"ATAPI device found: Data=%X, Ctrl=%X, dev=%X(Note: 0=master, 1=slave)\r\n\0"

#endif	/* CDROM_INIT */


#ifdef CDROM_INIT

check_atapi_cdrom:

	.code16

#;return: cf =0 is cdrom, cf =1 not cdrom
	pushaw
#;	push es
#;	push cs
#;	pop es
#;	mov di, atapi_devinfo
	call	inquiry_atapi
	jc	1f
	clc

#define	ATATYPE_CDR	0x4	//#; Write-once device
#define	ATATYPE_CD	0x5	//#; CD-ROM device

	cmpb	$ATATYPE_CD, %al
	je	1f
	cmpb	$ATATYPE_CDR, %al
	je	1f
	stc
1:
#;	pop es
	popaw
	ret

#endif	/* CDROM_INIT */


#ifdef CDROM_INIT

inquiry_atapi:

	.code16

#;input: es:di -> atapi_devinfo
#;return: cf =0 success, al = device type, 
#;        cf =1 fail
#;	save si, di, cx
	call	clear_atapi_buffer
	movb	$0x12, atapi_cmd_buffer - int13_handler
	movb	$128, atapi_cmd_buffer - int13_handler + 4

	# invoke reg_packet,byte,0,cs, atapi_tmp_buffer, 128
	pushw	$128
	pushw	$atapi_tmp_buffer - int13_handler
	pushw	%cs
	pushw	$0
	call	reg_packet
	addw	$8, %sp

	orw	%ax, %ax
	jnz	1f

	movb	atapi_tmp_buffer - int13_handler, %al
	testb	$0xe0, %al
	jnz	1f

	andb	$0x1f, %al

#if 0
	mov [es:di + struc_atapi_devinfo.dev_type], al

	mov ah, [atapi_tmp_buffer+7]
	mov [es:di + struc_atapi_devinfo.dev_flags], ah

	add di, struc_atapi_devinfo.vender_id
	mov si, atapi_tmp_buffer + 8
	mov cx, 24
	cld
	rep movsb
#endif
	clc
	ret
1:
	stc
	ret

#endif	/* CDROM_INIT */


#ifdef CDROM_INIT

reg_probe_dev_exist:

	.code16

#; input ax=dev
#; return ax = 1: exist		# <----- "ax=1" should be "al=1"
	call	__reg_select_dev

	# outbytes CB_SC,0x55,CB_SN,0xaa,CB_SC,0xaa,CB_SN,0x55,CB_SC,0x55
	movb	$0x55, %al
	movw	reg_addr - int13_handler + (2 * 2), %dx	#; CB_SC = interrupt reason register
	outb	%al, %dx

	movb	$0xAA, %al
	movw	reg_addr - int13_handler + (3 * 2), %dx	#; CB_SN = reserved for SAM TAG byte
	outb	%al, %dx

	movb	$0xAA, %al
	movw	reg_addr - int13_handler + (2 * 2), %dx	#; CB_SC = interrupt reason register
	outb	%al, %dx

	movb	$0x55, %al
	movw	reg_addr - int13_handler + (3 * 2), %dx	#; CB_SN = reserved for SAM TAG byte
	outb	%al, %dx

	movb	$0x55, %al
	movw	reg_addr - int13_handler + (2 * 2), %dx	#; CB_SC = interrupt reason register
	outb	%al, %dx

	movb	$0xAA, %al
	movw	reg_addr - int13_handler + (3 * 2), %dx	#; CB_SN = reserved for SAM TAG byte
	outb	%al, %dx

	movw	reg_addr - int13_handler + (2 * 2), %dx	#; CB_SC = interrupt reason register
	inb	%dx, %al
	movb	%al, %ah

	movw	reg_addr - int13_handler + (3 * 2), %dx	#; CB_SN = reserved for SAM TAG byte
	inb	%dx, %al

	cmpw	$0x55AA, %ax
	sete	%al
	ret

#endif	/* CDROM_INIT */

	.code32
	
	
/*
 * chain_stage1(segment, offset, part_table_addr)
 *
 *  This starts another stage1 loader, at segment:offset.
 */

ENTRY(chain_stage1)
	/* no need to save anything, just use %esp */

	/* store %ESI, presuming %ES is 0 */
	movl	0xc(%esp), %esi

	/* store new offset */
	movl	0x8(%esp), %eax
	movl	%eax, offset

	/* store new segment */
	movw	0x4(%esp), %ax
	movw	%ax, segment

	/* set up to pass boot drive */
	movb	EXT_C(boot_drive), %dl

	call	EXT_C(prot_to_real)

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

#ifdef ABSOLUTE_WITHOUT_ASTERISK
	DATA32	ADDR32	ljmp	(offset)
#else
	DATA32	ADDR32	ljmp	*(offset)
#endif
	.code32
#endif /* STAGE1_5 */


#ifdef STAGE1_5
/*
 * chain_stage2(segment, offset, second_sector)
 *
 *  This starts another stage2 loader, at segment:offset.  It presumes
 *  that the other one starts with this same "asm.S" file, and passes
 *  parameters by writing the embedded install variables.
 */

ENTRY(chain_stage2)
	/* no need to save anything, just use %esp */

	/* store new offset */
	movl	0x8(%esp), %eax
	movl	%eax, offset
	movl	%eax, %ebx

	/* store new segment */
	movw	0x4(%esp), %ax
	movw	%ax, segment
	shll	$4, %eax

	/* generate linear address */
	addl	%eax, %ebx

	/* set up to pass the partition where stage2 is located in */
	movl	EXT_C(current_partition), %eax
	movl	%eax, (EXT_C(install_partition)-EXT_C(main))(%ebx)

	/* set up to pass the drive where stage2 is located in */
	movb	EXT_C(current_drive), %dl

	/* set up to pass the second sector of stage2 */
	movl	0xc(%esp), %ecx

	call	EXT_C(prot_to_real)

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

	movl	%ecx, %ebp

#ifdef ABSOLUTE_WITHOUT_ASTERISK
	DATA32	ADDR32	ljmp	(offset)
#else
	DATA32	ADDR32	ljmp	*(offset)
#endif

	.code32
#endif /* STAGE1_5 */
	
/*
 *  These next two routines, "real_to_prot" and "prot_to_real" are structured
 *  in a very specific way.  Be very careful when changing them.
 *
 *  NOTE:  Use of either one messes up %eax and %ebp.
 */

ENTRY(real_to_prot)
	.code16

	cli

	/* load the GDT register */
	xorw	%ax, %ax
	movw	%ax, %ds
	DATA32	ADDR32	lgdt	gdtdesc

	/* turn on protected mode */
	movl	%cr0, %eax
	andl	$0x0000FFFF, %eax
	orl	$CR0_PE_ON, %eax
	movl	%eax, %cr0

	/* jump to relocation, flush prefetch queue, and reload %cs */
	DATA32	ljmp	$PROT_MODE_CSEG, $protcseg

	/*
	 *  The ".code32" directive only works in GAS, the GNU assembler!
	 *  This gets out of "16-bit" mode.
	 */
	.code32

protcseg:
	/* reload other segment registers */
	movw	$PROT_MODE_DSEG, %ax
	movw	%ax, %ds
	movw	%ax, %es
	movw	%ax, %fs
	movw	%ax, %gs
	movw	%ax, %ss

#;	/* put the return address in a known safe location */
#;	movl	(%esp), %eax
#;	movl	%eax, STACKOFF

#;	/* get protected mode stack */
#;	movl	protstack, %eax
#;	movl	%eax, %esp
#;	movl	%eax, %ebp

#;	/* get return address onto the right stack */
#;	movl	STACKOFF, %eax
#;	movl	%eax, (%esp)

	/* zero %eax */
	xorl	%eax, %eax

	/* return on the old (or initialized) stack! */
	ret


ENTRY(prot_to_real)
	/* just in case, set GDT */
	lgdt	gdtdesc

#;	/* save the protected mode stack */
#;	movl	%esp, %eax
#;	movl	%eax, protstack

#;	/* get the return address */
#;	movl	(%esp), %eax
#;	movl	%eax, STACKOFF

#;	/* set up new stack */
#;	movl	$STACKOFF, %eax
#;	movl	%eax, %esp
#;	movl	%eax, %ebp

	/* set up segment limits */
	movw	$PSEUDO_RM_DSEG, %ax
	movw	%ax, %ds
	movw	%ax, %es
	movw	%ax, %fs
	movw	%ax, %gs
	movw	%ax, %ss

	/* this might be an extra step */
	ljmp	$PSEUDO_RM_CSEG, $tmpcseg	/* jump to a 16 bit segment */

tmpcseg:
	.code16

	/* clear the PE bit of CR0 */
	movl	%cr0, %eax
	//andl 	$CR0_PE_OFF, %eax
	andl 	$0x0000FFFE, %eax
	movl	%eax, %cr0

	/* flush prefetch queue, reload %cs */
	DATA32	ljmp	$0, $realcseg

realcseg:
	/* we are in real mode now
	 * set up the real mode segment registers : DS, SS, ES
	 */
	/* zero %eax */
	xorl	%eax, %eax

	movw	%ax, %ds
	movw	%ax, %es
	movw	%ax, %fs
	movw	%ax, %gs
	movw	%ax, %ss

	/* restore interrupts */
	/* oh, don't enable interrupt when we are controlling gateA20 */
	//sti

	/* return on new stack! */
	DATA32	ret

	.code32


/*
 *   int biosdisk_int13_extensions (int ax, int drive, void *dap)
 *
 *   Call IBM/MS INT13 Extensions (int 13 %ax=AX) for DRIVE. DAP
 *   is passed for disk address packet. If an error occurs, return
 *   non-zero, otherwise zero.
 */

ENTRY(biosdisk_int13_extensions)
	pushl	%ebp
	movl	%esp, %ebp

	#; +16	dap
	#; +12	drive
	#;  +8	 ax
	#;  +4	EIP
	#; ebp	EBP
	#;  -4	ESI
	#;  -8	EBX

	pushl	%esi
	pushl	%ebx
	pushl	%ecx
	pushl	%edx

	/* compute the address of disk_address_packet */
	movl	0x10(%ebp), %eax	#; linear address of dap

	/* if DS can be 0x40, we can avoid AWARD BIOS bug of int13/AX=4B01 */
	subl	$0x400, %eax

	shll	$1, %eax
	movw	%ax, %si
	shrw	$1, %si			#; low 15-bit for offset

	xorw	%ax, %ax
	shrl	$5, %eax		#; segment value in AX
	addw	$0x40, %ax
	movw	%ax, %cx	/* save the segment to cx */

	/* drive */
	movb	0xc(%ebp), %dl
	/* ax */
	movw	0x8(%ebp), %bx
	/* enter real mode */
	call	EXT_C(prot_to_real)
	
	.code16

	sti	#; cli should also work for biosdisk_int13_extensions

	movw	%bx, %ax
	movw	%cx, %ds

	/* set additional registers to serve buggy BIOSes. */
	pushw	%di
	pushw	%bx
	movw	%cx, %es
	movw	%si, %di
	movw	%si, %bx

#if defined(STAGE1_5) || 1
	int	$0x13
#else
	call	safe_int13
#endif
	popw	%bx
	popw	%di

#if 1
	/* some buggy USB BIOSes fail to clear AH on success */
	setc	%dl
#else
	movb	$1, %dl		/* set error */
	jc	1f
	movb	%ah, %dl	/* save return value */
1:
#endif

	/* clear the data segment */
	xorw	%ax, %ax
	movw	%ax, %ds
	movw	%ax, %es
#ifndef STAGE1_5

	/* if it is not read/write operation, we can skip the A20 code. */

	andb	$0xFE, %bh
	cmpb	$0x42, %bh
	jne	1f

	/* ensure A20 is on when we come back to protected mode. */

	pushal

	movw	$0x00ff, %cx		# try so many times on failure
	movw	$0x0001, %dx		# DL=enable A20, DH=debug off

	cli	/* yes, keep interrupt off when controlling A20 */
	call	enable_disable_a20
	sti

	//sete	%dl			# DL=1 means success

	popal
1:
#endif /* ! STAGE1_5 */
	/* back to protected mode */
	DATA32	call	EXT_C(real_to_prot)
	.code32

	movzbl	%dl, %eax	/* return value in %eax */

	popl	%edx
	popl	%ecx
	popl	%ebx
	popl	%esi
	popl	%ebp

	ret
	
/*
 *   int biosdisk_standard (int ah, int drive, int coff, int hoff, int soff,
 *                          int nsec, int segment)
 *
 *   Call standard and old INT13 (int 13 %ah=AH) for DRIVE. Read/write
 *   NSEC sectors from COFF/HOFF/SOFF into SEGMENT. If an error occurs,
 *   return non-zero, otherwise zero.
 */

ENTRY(biosdisk_standard)
	pushl	%ebp
	movl	%esp, %ebp

	pushl	%ebx
	pushl	%edi
	pushl	%esi

	/* set up CHS information */
	movl	0x10(%ebp), %eax
	movb	%al, %ch
	movb	0x18(%ebp), %al
	shlb	$2, %al
	shrw	$2, %ax
	movb	%al, %cl
	movb	0x14(%ebp), %dh
	/* drive */
	movb	0xc(%ebp), %dl
	/* segment */
	movw	0x20(%ebp), %bx
	/* save nsec and ah to %di */
	movb	0x8(%ebp), %ah
	movb	0x1c(%ebp), %al
	movw	%ax, %di
	/* enter real mode */
	call	EXT_C(prot_to_real)

	.code16

	//sti	#; biosdisk_standard won't require sti
	sti	#; added 2006-11-30

	movw	%bx, %es
	movw	$5, %si		/* attempt at least 5 times */

1:	
	pushw	%si
	pushw	%di
	pushw	%cx
	pushw	%dx
	xorw	%bx, %bx
	movw	%di, %ax
#if defined(STAGE1_5) || 1
	int	$0x13
#else
	call	safe_int13
#endif
	popw	%dx
	popw	%cx
	popw	%di
	popw	%si

#if 1
	/* some buggy USB BIOSes fail to clear AH on success */
	setc	%bl
	jnc	2f
#else
	movb	%ah, %bl	/* save return value */
	jc	3f		/* check if successful */

	testb	%ah, %ah
	jz	2f
3:
#endif

	movw	%di, %ax	/* get function number */
	cmpb	$0x04, %ah	/* verify sectors? */
	je	4f		/* yes, do not retry */
	/* if fail, reset the disk system */
	pushw	%si
	pushw	%di
	pushw	%cx
	pushw	%dx
	xorw	%ax, %ax
#if defined(STAGE1_5) || 1
	int	$0x13
#else
	call	safe_int13
#endif
	popw	%dx
	popw	%cx
	popw	%di
	popw	%si
	
	decw	%si
	jnz	1b		/* retry */
4:
	movb	$1, %bl		/* set error */
2:	
#ifndef STAGE1_5
	/* ensure A20 is on when we come back to protected mode. */

	pushal

	movw	$0x00ff, %cx		# try so many times on failure
	movw	$0x0001, %dx		# DL=enable A20, DH=debug off

	cli	/* yes, keep interrupt off when controlling A20 */
	call	enable_disable_a20
	sti

	//sete	%dl			# DL=1 means success

	popal
#endif /* ! STAGE1_5 */
	/* back to protected mode */
	DATA32	call	EXT_C(real_to_prot)
	.code32

	movzbl	%bl, %eax	/* return value in %eax */
	
	popl	%esi
	popl	%edi
	popl	%ebx
	popl	%ebp

	ret


/*
 *   int check_int13_extensions (int drive)
 *
 *   Check if LBA is supported for DRIVE. If it is supported, then return
 *   the major version and API support bits of extensions, otherwise zero.
 */

ENTRY(check_int13_extensions)
	pushl	%ebp
	movl	%esp, %ebp

	pushl	%ebx

	/* drive */
	movb	0x8(%ebp), %dl
	/* enter real mode */
	call	EXT_C(prot_to_real)

	.code16

	//sti	#; check_int13_extensions won't require sti
	sti	#; added 2006-11-30

	pushw	%cx
	pushw	%dx

	movb	$0x41, %ah
	movw	$0x55aa, %bx
#if defined(STAGE1_5) || 1
	int	$0x13
#else
	call	safe_int13
#endif
	
	/* check the result */
	jc	1f
	cmpw	$0xaa55, %bx
	jne	1f

	movb	%ah, %bl	/* save the major version into %bl */

	/* check if AH=0x42 is supported if FORCE_LBA is zero */
	movb	EXT_C(force_lba), %al
	testb	%al, %al
#if 0
	jnz	2f
	andw	$1, %cx
	jnz	2f
#else
	setnz	%al
	orb	%al, %cl
	jmp	2f
#endif
	
1:
	xorw	%bx, %bx
	xorw	%cx, %cx
2:
	roll	$16, %ebx	#; version number in high word
	movw	%cx, %bx	#; API subset support bitmap in low word

	popw	%dx
	popw	%cx

	/* back to protected mode */
	DATA32	call	EXT_C(real_to_prot)
	.code32

	xchgl	%eax, %ebx	/* return value in %eax */

	popl	%ebx
	popl	%ebp

	ret

	.code32

/*
 *   int get_diskinfo_standard (int drive, unsigned long *cylinders, 
 *                              unsigned long *heads, unsigned long *sectors)
 *
 *   if bit 8-15 of drive(dh) != 0 on call, then geometry_tune will be used.
 *
 *   Return the geometry of DRIVE in CYLINDERS, HEADS and SECTORS. If an
 *   error occurs, then return non-zero, otherwise zero.
 */

ENTRY(get_diskinfo_standard)
	pushl	%ebp
	movl	%esp, %ebp

	pushl	%ebx
	pushl	%edi

	/* Heads */
	movl	0x10(%ebp), %edi
	movl	(%edi), %edi
	movl	%edi, ABS(Heads_passed_in)

	/* Sectors */
	movl	0x14(%ebp), %edi
	movl	(%edi), %edi
	movl	%edi, ABS(Sectors_passed_in)

	/* drive */
	movl	0x8(%ebp), %edx

	/* enter real mode */
	call	EXT_C(prot_to_real)

	.code16

	sti

	testb	%dh, %dh
	jz	2f

	call	geometry_tune

	movb	$1, %bh		/* geometry_tune indicator */
	jmp	1f
2:
	xorw	%cx, %cx
	movb	$0x8, %ah
#if defined(STAGE1_5) || 1
	int	$0x13
#else
	call	safe_int13
#endif
	movb	$0, %bh		/* geometry_tune indicator */
	jc	2f

	/* check if successful */
	testb	%ah, %ah
	jnz	1f		/* Error number in AH */

	/* bogus BIOSes may not return an error number */
	testb	$0x3f, %cl	/* 0 sectors means no disk */
	jnz	1f		/* if non-zero, then succeed */
2:
	/* failure */
	/* XXX 0x60 is one of the unused error numbers */
	movb	$0x60, %ah
1:
	movb	%ah, %bl	/* save return value in %bl */
	/* back to protected mode */
	DATA32	call	EXT_C(real_to_prot)

	.code32

	testb	%bl, %bl	/* check failure */
	jnz	1f		/* failure */

	/* restore %ebp */
	leal	0x8(%esp), %ebp
	
	/* heads */
	xorl	%eax, %eax
	movb	%dh, %al
	incl	%eax		/* number of heads is counted from zero */
	movl	0x10(%ebp), %edi
	//movl	%eax, (%edi)
	stosl

	/* sectors */
	xorl	%eax, %eax
	movb	%cl, %al
	andb	$0x3f, %al
	movl	0x14(%ebp), %edi
	//movl	%eax, (%edi)
	stosl

	/* cylinders */

	testb	%bh, %bh
	jnz	1f		/* geometry_tune won't touch cylinders */

	xorl	%eax, %eax
	shrb	$6, %cl
	movb	%cl, %ah
	movb	%ch, %al
	incl	%eax		/* number of cylinders is counted from zero */
	movl	0x0C(%ebp), %edi
	//movl	%eax, (%edi)
	stosl
1:
	movzbl	%bl, %eax	/* return value in %eax */

	popl	%edi
	popl	%ebx
	popl	%ebp

	ret

	.code16

geometry_tune:

	/* on call:
	 *		CS	0
	 *
	 * on return:
	 *		AH=0	success, otherwise failure
	 *		CL	max sector number
	 *		DH	max head number
	 *		DS	changed
	 *		ES	changed
	 *		AX	changed
	 *		BX	changed
	 *		CX	changed
	 */

	movw	$63, %cx	/* cylinder=0, sector=Max possible */
1:
	movw	$0x57E0, %ax	/* Don't use SCRATCHSEG */
	movw	%ax, %es
	movw	%ax, %ds
	xorw	%bx, %bx
	movw	$0x201, %ax	/* read 1 sector */
	movb	$0, %dh		/* head=0 */
	pushaw
	movw	%bx, %si
	movw	%bx, %di
#if defined(STAGE1_5) || 1
	int	$0x13
#else
	call	safe_int13
#endif
	popaw
	jnc	1f		/* found Max sector */
	loop	1b
2:
	movb	$1, %ah		/* failure */
	ret
1:

	/* CX=Max Sector */
	movw	%cx, %cs:ABS(Smax_tuned)

//////////////////////////////////////////////////////////////////////////////

	/* check if we can read sectors across the track boundary */

	movb	$0, %cs:ABS(cross_track)

	movw	$1, %cx		/* sector 1, cylinder 0 */
	movb	$0, %dh		/* head 0 */
	movb	%cs:ABS(Smax_tuned), %al	/* sectors to read */
	incw	%ax		/* read 1 more sector */
	movb	$2, %ah		/* READ */
	movw	$0x5000, %bx
	movw	%bx, %es
	movw	%bx, %ds
	xorw	%bx, %bx
	pushaw
	movw	%bx, %si
	movw	%bx, %di
#if defined(STAGE1_5) || 1
	int	$0x13
#else
	call	safe_int13
#endif
	popaw
	jc	1f		/* cross-track read is not supported */

	/* read again normally */

	movb	%cs:ABS(Smax_tuned), %al	/* sectors to read */
	movb	$2, %ah		/* READ */
	movw	$0x5800, %bx
	movw	%bx, %es
	movw	%bx, %ds
	xorw	%bx, %bx
	pushaw
	movw	%bx, %si
	movw	%bx, %di
#if defined(STAGE1_5) || 1
	int	$0x13
#else
	call	safe_int13
#endif
	popaw
	jc	2b		/* failure */

	/* compare the two tracks */

	pushw	%cx
	pushw	%si
	pushw	%di
	movw	%cs:ABS(Smax_tuned), %cx	/* sectors */
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
	movb	$1, %cs:ABS(cross_track)
1:

//////////////////////////////////////////////////////////////////////////////

	movb	$0xFF, %dh	/* head=Max possible */
1:
	movw	$0x57E0, %ax	/* Don't use SCRATCHSEG */
	movw	%ax, %es
	movw	%ax, %ds
	xorw	%bx, %bx
	movw	$0x201, %ax	/* read 1 sector */
	movw	$1, %cx		/* cylinder=0, sector=1 */
	pushaw
	movw	%bx, %si
	movw	%bx, %di
#if defined(STAGE1_5) || 1
	int	$0x13
#else
	call	safe_int13
#endif
	popaw
	jnc	1f		/* found Max head */
	decb	%dh
	cmpb	$0xFF, %dh
	jne	1b
	movb	$1, %ah		/* failure */
	ret
1:

	/* DH=Max head */
	movb	%dh, %cs:ABS(Hmax_tuned)

//////////////////////////////////////////////////////////////////////////////

	/* tune Hmax */

	/* First, try the passed-in value */
	movb	%cs:ABS(Heads_passed_in), %dh
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

	cmpb	%cs:ABS(Hmax_tuned), %dh
	ja	2f		/* this should not happen */
	je	5f

	incb	%dh		/* Next Hmax */
	jnz	1b

	/* Hmax=0xFF */
4:
	/* got Hmax=DH-1 */

	decb	%dh
	movb	%dh, %cs:ABS(Hmax_tuned)
5:
	/* Hmax is tuned ok. */

//////////////////////////////////////////////////////////////////////////////

	/* tune Smax */

	/* First, try the passed-in value */
	movb	%cs:ABS(Sectors_passed_in), %cl
	cmpb	$0, %cs:ABS(cross_track)
	jnz	4f
	cmpb	%cs:ABS(Smax_tuned), %cl
	jnb	1f
	cmpb	$8, %cl
	jb	1f
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
	cmpb	%cs:ABS(Smax_tuned), %cl
	jb	1b

4:
	/* got Smax=CL */

	movb	%cl, %cs:ABS(Smax_tuned)

	/* Smax is tuned ok. */

//////////////////////////////////////////////////////////////////////////////

	movw	%cs:ABS(Smax_tuned), %cx
	movb	%cs:ABS(Hmax_tuned), %dh
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
	movb	%cs:ABS(Smax_tuned), %al	/* sectors to read */
	movw	$0x5000, %bx
	movw	%bx, %es
	movw	%bx, %ds
	xorw	%bx, %bx
	pushaw
	movw	%bx, %si
	movw	%bx, %di
#if defined(STAGE1_5) || 1
	int	$0x13
#else
	call	safe_int13
#endif
	popaw
	jc	2f		/* failure */

	/* read beginning track of the next cylinder */

	incb	%ch		/* next cylinder */

	pushw	%dx		/* save DH */

	movb	$0, %dh

	movb	$1, %cl		/* sector 1=the leading sector */
	movb	$2, %ah		/* READ */
	movb	%cs:ABS(Smax_tuned), %al	/* sectors to read */
	movw	$0x5800, %bx
	movw	%bx, %es
	movw	%bx, %ds
	xorw	%bx, %bx
	pushaw
	movw	%bx, %si
	movw	%bx, %di
#if defined(STAGE1_5) || 1
	int	$0x13
#else
	call	safe_int13
#endif
	popaw
	popw	%dx		/* restore DH */
	jc	2f		/* failure */

	/* compare the two tracks */

	pushw	%cx
	pushw	%si
	pushw	%di
	movw	%cs:ABS(Smax_tuned), %cx	/* sectors */
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

	movw	$10, %cs:ABS(Smax_count)

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
#if defined(STAGE1_5) || 1
	int	$0x13
#else
	call	safe_int13
#endif
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
#if defined(STAGE1_5) || 1
	int	$0x13
#else
	call	safe_int13
#endif
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

	decw	%cs:ABS(Smax_count)
	jz	6f

	cmpb	%cs:ABS(Hmax_tuned), %dh
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

//////////////////////////////////////////////////////////////////////////////

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

	.code32


#ifndef STAGE1_5
/* get_code_end() :  return the address of the end of the code
 * This is here so that it can be replaced by asmstub.c.
 */
ENTRY(get_code_end)
	/* will be the end of the bss */
# if defined(HAVE_END_SYMBOL)
	movl	$end, %eax
# elif defined(HAVE_USCORE_END_SYMBOL)
	movl	$_end, %eax
# endif
	shrl	$2, %eax		/* Round up to the next word. */
	incl	%eax
	shll	$2, %eax
	ret
#endif /* ! STAGE1_5 */

/*
 *
 * get_memsize(i) :  return the memory size in KB. i == 0 for conventional
 *		memory, i == 1 for extended memory
 *	BIOS call "INT 12H" to get conventional memory size
 *	BIOS call "INT 15H, AH=88H" to get extended memory size
 *		Both have the return value in AX.
 *
 */

ENTRY(get_memsize)
	pushl	%ebp
	pushl	%ebx

	movl	0xc(%esp), %ebx

	call	EXT_C(prot_to_real)	/* enter real mode */

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

	cmpb	$0x1, %bl
	//DATA32	je	xext
	je	1f

	int	$0x12
	//DATA32	jmp	xdone
	jmp	2f

//xext:
1:
	movb	$0x88, %ah
#ifdef STAGE1_5
	int	$0x15
#else
	pushfw
	lcall	*ABS(EXT_C(ROM_int15))
#endif

//xdone:
2:
	movw	%ax, %bx

	DATA32	call	EXT_C(real_to_prot)
	.code32

	movw	%bx, %ax
	popl	%ebx
	popl	%ebp
	ret


#ifndef STAGE1_5

/*
 *
 * get_eisamemsize() :  return packed EISA memory map, lower 16 bits is
 *		memory between 1M and 16M in 1K parts, upper 16 bits is
 *		memory above 16M in 64K parts.  If error, return -1.
 *	BIOS call "INT 15H, AH=E801H" to get EISA memory map,
 *		AX = memory between 1M and 16M in 1K parts.
 *		BX = memory above 16M in 64K parts.
 *
 */

ENTRY(get_eisamemsize)
	pushl	%ebp
	pushl	%ebx
	pushl	%ecx
	pushl	%edx

	call	EXT_C(prot_to_real)	/* enter real mode */

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

	movw	$0xe801, %ax
	//int	$0x15
	pushfw
	lcall	*ABS(EXT_C(ROM_int15))
	jc	1f
	testb	$0x80, %ah
	jnz	1f

	shll	$16, %ebx
	movw	%ax, %bx
	testl	%ebx, %ebx
	jnz	3f
	movw	%cx, %ax
	movw	%dx, %bx
	shll	$16, %ebx
	movw	%ax, %bx
3:
	jmp	2f
1:
	movl	$0xFFFFFFFF, %ebx
2:
	xorw	%ax, %ax
	movw	%ax, %ds
	movw	%ax, %es

	DATA32	call	EXT_C(real_to_prot)
	.code32

	movl	%ebx, %eax

	popl	%edx
	popl	%ecx
	popl	%ebx
	popl	%ebp
	ret

/*
 *
 * get_mmap_entry(addr, cont) :  address and old continuation value (zero to
 *		start), for the Query System Address Map BIOS call.
 *
 *  Sets the first 4-byte int value of "addr" to the size returned by
 *  the call.  If the call fails, sets it to zero.
 *
 *	Returns:  new (non-zero) continuation value, 0 if done.
 *
 * NOTE: Currently hard-coded for a maximum buffer length of 1024.
 */

ENTRY(get_mmap_entry)
	pushl	%ebp
	pushl	%ebx
	pushl	%edi
	pushl	%esi

	/* place address (+4) in ES:DI */
	movl	0x14(%esp), %eax
	addl	$4, %eax
	movl	%eax, %edi
	andl	$0xf, %edi
	shrl	$4, %eax
	movl	%eax, %esi

	/* set continuation value */
	movl	0x18(%esp), %ebx

	pushl	%ecx		/* save ECX */

	/* set default maximum buffer size */
	movl	$0x14, %ecx

	/* set EDX to 'SMAP' */
	movl	$0x534d4150, %edx

	call	EXT_C(prot_to_real)	/* enter real mode */

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

	movw	%si, %es

	/* set additional registers to serve buggy BIOSes. */
	movw	%si, %ds
	movw	%di, %si

	movl	$0xe820, %eax
	//int	$0x15
	pushfw
	lcall	%cs:*ABS(EXT_C(ROM_int15))

	//DATA32	jc	xnosmap
	jnc	1f
	movl	$0, %ebx	/* set end indicator */
1:
	cmpl	$0x534d4150, %eax
	//DATA32	jne	xnosmap
	jne	1f

	/* 20-byte length is currently standard. So others are considered
	 * invalid.
	 */

	cmpl	$0x14, %ecx
	//DATA32	jb	xnosmap
	//
	//cmpl	$0x400, %ecx
	//DATA32	jg	xnosmap
	//DATA32	jmp	xsmap
	je	2f

//xnosmap:
1:
	movl	$0, %ecx
//xsmap:
2:

	xorw	%ax, %ax
	movw	%ax, %ds
	movw	%ax, %es

	DATA32	call	EXT_C(real_to_prot)
	.code32

	popl	%eax		/* OLD ECX */

	/* write length of buffer (zero if error) into "addr" */
	movl	0x14(%esp), %edi
	xchgl	%eax, %ecx
	stosl

	/* set return value to continuation */
	movl	%ebx, %eax

	popl	%esi
	popl	%edi
	popl	%ebx
	popl	%ebp
	ret

/*
 * get_rom_config_table()
 *
 * Get the linear address of a ROM configuration table. Return zero,
 * if fails.
 */
	
ENTRY(get_rom_config_table)
	pushl	%ebp
	pushl	%ebx
	pushl	%edx

	/* zero %ebx for simplicity */
	xorl	%ebx, %ebx
	
	call	EXT_C(prot_to_real)

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

	movb	$0xc0, %ah
	int	$0x15

	jc	no_rom_table
	testb	%ah, %ah
	jnz	no_rom_table
	
	movw	%es, %dx
	jmp	found_rom_table
	
no_rom_table:
	xorw	%dx, %dx
	xorw	%bx, %bx
	
found_rom_table:

	xorw	%ax, %ax
	movw	%ax, %ds
	movw	%ax, %es

	DATA32	call	EXT_C(real_to_prot)
	.code32

	/* compute the linear address */
	xorl	%eax, %eax
	movw	%dx, %ax
	shll	$4, %eax
	addl	%ebx, %eax

	popl	%edx
	popl	%ebx
	popl	%ebp
	ret


/*
 * int get_vbe_controller_info (struct vbe_controller *controller_ptr)
 *
 * Get VBE controller information.
 */

ENTRY(get_vbe_controller_info)
	pushl	%ebp
	movl	%esp, %ebp
	
	pushl	%edi
	pushl	%ebx
	pushl	%esi

	/* Convert the linear address to segment:offset */
	movl	8(%ebp), %eax
	movl	%eax, %edi
	andl	$0x0000000f, %edi
	shrl	$4, %eax
	movl	%eax, %ebx

	call	EXT_C(prot_to_real)

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

	movw	%bx, %es

	/* set additional registers to serve buggy BIOSes. */
	movw	%bx, %ds
	movw	%di, %si

	movw	$0x4F00, %ax
	int	$0x10

	movw	%ax, %bx

	xorw	%ax, %ax
	movw	%ax, %ds
	movw	%ax, %es

	DATA32	call	EXT_C(real_to_prot)
	.code32

	movzwl	%bx, %eax

	popl	%esi
	popl	%ebx
	popl	%edi
	popl	%ebp
	ret

	
/*
 * int get_vbe_mode_info (int mode_number, struct vbe_mode *mode_ptr)
 *
 * Get VBE mode information.
 */

ENTRY(get_vbe_mode_info)
	pushl	%ebp
	movl	%esp, %ebp
	
	pushl	%edi
	pushl	%ebx

	/* Convert the linear address to segment:offset */
	movl	0xc(%ebp), %eax
	movl	%eax, %edi
	andl	$0x0000000f, %edi
	shrl	$4, %eax
	movl	%eax, %ebx

	/* Save the mode number in %cx */
	movl	0x8(%ebp), %ecx
	
	call	EXT_C(prot_to_real)

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

	movw	%bx, %es
	movw	$0x4F01, %ax
	int	$0x10

	movw	%ax, %bx
	DATA32	call	EXT_C(real_to_prot)
	.code32

	movzwl	%bx, %eax

	popl	%ebx
	popl	%edi
	popl	%ebp
	ret

	
/*
 * int set_vbe_mode (int mode_number)
 *
 * Set VBE mode. Don't support user-specified CRTC information.
 */

ENTRY(set_vbe_mode)
	pushl	%ebp
	movl	%esp, %ebp
	
	pushl	%ebx

	/* Save the mode number in %bx */
	movl	0x8(%ebp), %ebx
	/* Clear bit D11 */
	andl	$0xF7FF, %ebx
	
	call	EXT_C(prot_to_real)

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

	movw	$0x4F02, %ax
	int	$0x10

	movw	%ax, %bx
	DATA32	call	EXT_C(real_to_prot)
	.code32

	movzwl	%bx, %eax

	popl	%ebx
	popl	%ebp
	ret

		
/*
 * grub2_gate_a20(int on)
 *
 * Gate address-line 20 for high memory.
 *
 * This routine is probably overconservative in what it does, but so what?
 *
 * It also eats any keystrokes in the keyboard buffer.  :-(
 */

ENTRY(grub2_gate_a20)

	.code32

	//movl	%eax, %edx
	movl	4(%esp), %edx		/* the value of `on' */

gate_a20_test_current_state:	
	/* first of all, test if already in a good state */
	call	gate_a20_check_state
	cmpb	%al, %dl
	jnz	gate_a20_try_bios
	ret

gate_a20_try_bios:
	/* second, try a BIOS call */
	pushl	%ebp
	call	EXT_C(prot_to_real)

	.code16
	sti		/* for hardware interrupt or watchdog */
	movw	$0x2400, %ax
	testb	%dl, %dl
	jz	1f
	incw	%ax
1:	int	$0x15

	DATA32	call	EXT_C(real_to_prot)
	.code32

	popl	%ebp
	call	gate_a20_check_state
	cmpb	%al, %dl
	jnz	gate_a20_try_keyboard_controller
	ret
	
gate_a20_flush_keyboard_buffer:
	inb	$0x64
	andb	$0x02, %al
	jnz	gate_a20_flush_keyboard_buffer
2:	
	inb	$0x64
	andb	$0x01, %al
	jz	3f
	inb	$0x60
	jmp	2b
3:
	ret
	
gate_a20_try_keyboard_controller:	
	/* third, try the keyboard controller */
	call    gate_a20_flush_keyboard_buffer

	movb	$0xd1, %al
	outb	$0x64
4:	
	inb	$0x64
	andb	$0x02, %al
	jnz	4b

	movb	$0xdd, %al
	testb	%dl, %dl
	jz	5f
	orb	$0x02, %al
5:	outb	$0x60
	call    gate_a20_flush_keyboard_buffer

	/* output a dummy command (USB keyboard hack) */
	movb	$0xff, %al
	outb	$0x64
	call    gate_a20_flush_keyboard_buffer

	call	gate_a20_check_state
	cmpb	%al, %dl
	jnz	gate_a20_try_system_control_port_a
	ret

gate_a20_try_system_control_port_a:
	/* fourth, try the system control port A */
	inb	$0x92
	andb	$(~0x03), %al
	testb	%dl, %dl
	jz	6f
	orb	$0x02, %al
6:	outb	$0x92

	/* When turning off Gate A20, do not check the state strictly,
	   because a failure is not fatal usually, and Gate A20 is always
	   on some modern machines.  */
	testb	%dl, %dl
	jz	7f	
	call	gate_a20_check_state
	cmpb	%al, %dl
	/* everything failed, so restart from the beginning */
	jnz	gate_a20_try_bios
7:	ret
	
gate_a20_check_state:
	/* iterate the checking for a while */
	movl	$100, %ecx
1:	
	call	3f
	cmpb	%al, %dl
	jz	2f
	loop	1b
2:
	ret
3:	
	pushl	%ebx
	pushl	%ecx
	xorl	%eax, %eax
	/* compare the byte at 0x8000 with that at 0x108000 */
	movl	$0x8000/*GRUB_BOOT_MACHINE_KERNEL_ADDR*/, %ebx
	pushl	%ebx				# EBX=0x8000
	/* save the original byte in CL */
	movb	(%ebx), %cl			# CL=byte at 0x8000
	/* store the value at 0x108000 in AL */
	addl	$0x100000, %ebx			# EBX=0x108000
	movb	(%ebx), %al			# AL=byte at 0x108000
	/* try to set one less value at 0x8000 */
	popl	%ebx				# EBX=0x8000
	movb	%al, %ch			# CH=AL
	decb	%ch				# CH=AL-1
	movb	%ch, (%ebx)			# byte at 0x8000=CH
	/* serialize */
	outb	%al, $0x80
	outb	%al, $0x80
	/* obtain the value at 0x108000 in CH */
	pushl	%ebx				# EBX=0x8000
	addl	$0x100000, %ebx			# EBX=0x108000
	movb	(%ebx), %ch			# CH=byte at 0x108000
	/* this result is 1 if A20 is on or 0 if it is off */
	subb	%ch, %al			# AL-=CH
	xorb	$1, %al
	/* restore the original */
	popl	%ebx				# EBX=0x8000
	movb	%cl, (%ebx)			# restore it
	popl	%ecx
	popl	%ebx
	ret

/*
 * int gateA20(int linear)
 *
 * Gate address-line 20 for high memory.
 *
 * This routine is probably overconservative in what it does, but so what?
 *
 * It also eats any keystrokes in the keyboard buffer.  :-(
 *
 *	on call:	linear=0 for a20 off and 1 for on
 *
 *	return value:	0 for failure and 1 for success	
 *
 */

ENTRY(gateA20)

	.code32

	pushl	%ebp
	movl	8(%esp), %edx		/* the value of `linear' */

#if 1
	/* first, check if A20 status is already what we desired. */

	/* disable CPU cache for the test to work reliably. */
	movl	%cr0, %eax
	pushl	%eax			/* save old cr0 */
//	andl	$0x00000011, %eax
	orl	$0x60000000, %eax	/* set CD and NW */
	movl	%eax, %cr0
	movl	%cr0, %eax
	testl	$0x60000000, %eax	/* check if we can use wbinvd. */
	jz	1f			/* CPU has no wbinvd instruction. */
	wbinvd
	andl	$0xDFFFFFFF, %eax	/* clear NW */
	movl	%eax, %cr0
1:
	movl	0x00000000, %eax
	pushl	%eax			/* save old int0 vector */

	cmpl	0x00100000, %eax
	jne	1f			/* A20 is on */

	notl	0x00000000
	movl	0x00000000, %eax
	cmpl	0x00100000, %eax
	notl	0x00000000		/* logical `NOT' won't touch flags */
1:
	/* ZF=0(means not equal) for A20 on, ZF=1(means equal) for A20 off. */
	sete	%al			/* save ZF to AL */
	testl	%edx, %edx
	sete	%ah			/* save ZF to AH */
	cmpb	%al, %ah

	/* ZF=1(means equal) for desired and we needn't do anything. */
	
	popl	%eax			/* restore int0 vector */
	movl	%eax, 0x00000000
	popl	%eax			/* restore cr0 */
	movl	%eax, %cr0
	movl	$1, %eax		/* return value 1 means success */

	jz	1f			/* success */

#endif

	/* failure, then call a real-mode function enable_disable_a20 */

	call	EXT_C(prot_to_real)
	
	.code16

	sti		/* for hardware interrupt or watchdog */

	movw	$0x00ff, %cx		# try so many times on failure
	movb	$0x01, %dh		# with a20 debug on

	cli	/* yes, keep interrupt off when controlling A20 */
	call	enable_disable_a20
	sti		/* for hardware interrupt or watchdog */

	sete	%dl			# DL=1 means success

#if 0	/* comment out to avoid hanging ONDA C51G board. */
	pushal

#if 0
	# qemu arrow keys will not work if we turn on NumLock in this way.

	/* Turn on Number Lock */
	orb	$0x20, 0x417
#endif

	/* reset mouse */
	movw	$0xC201, %ax
	int	$0x15

	/* disable mouse */
	movw	$0xC200, %ax
	xorw	%bx, %bx	/* BH=0 means disable */
	int	$0x15

	popal
#endif

	DATA32	call	EXT_C(real_to_prot)

	.code32

	movzbl	%dl, %eax

1:
	popl	%ebp
	ret

	.code32

/*
 * linux_boot()
 *
 * Does some funky things (including on the stack!), then jumps to the
 * entry point of the Linux setup code.
 */

VARIABLE(linux_text_len)
	.long	0
	
VARIABLE(linux_data_tmp_addr)
	.long	0
	
VARIABLE(linux_data_real_addr)
	.long	0
	
ENTRY(linux_boot)
	/* don't worry about saving anything, we're committed at this point */
	cld	/* forward copying */

	/* copy kernel */
	movl	EXT_C(linux_text_len), %ecx
	addl	$3, %ecx
	shrl	$2, %ecx
	movl	$LINUX_BZIMAGE_ADDR, %esi	# 0x100000
	movl	$LINUX_ZIMAGE_ADDR, %edi	# 0x10000

	rep movsl

ENTRY(big_linux_boot)
	movl	EXT_C(linux_data_real_addr), %ebx
	
	/* copy the real mode part */
	movl	EXT_C(linux_data_tmp_addr), %esi
	movl	%ebx, %edi
	movl	$LINUX_SETUP_MOVE_SIZE, %ecx	# 0x9100
	cld
	rep movsb

	/* change %ebx to the segment address */
	shrl	$4, %ebx	#; CS of LINUX SETUP, high word = 0
	movl	%ebx, %eax
	addl	$0x20, %eax	#; one sector
	movw	%ax, 1f		// linux_setup_seg
			
#;	/* XXX new stack pointer in safe area for calling functions */
#;	movl	$0x4000, %esp
#;	call	EXT_C(stop_floppy)

	/* final setup for linux boot */

	call	EXT_C(prot_to_real)

	.code16

	/* final setup for linux boot */
	cli
	movw	%bx, %ss
	movw	$LINUX_SETUP_STACK, %sp		# 0x9000
	
	movw	%bx, %ds
	movw	%bx, %es
	movw	%bx, %fs
	movw	%bx, %gs

#;	/* Reset floppy. Not required. */
#;	xorw	%ax, %ax
#;	xorb	%dl, %dl
#;	int	$0x13

	/* jump to start */
	/* ljmp */
	.byte	0xea
	.word	0
1:				//linux_setup_seg:	
	.word	0


	.code32


/*
 * multi_boot(int start, int mb_info)
 *
 *  This starts a kernel in the manner expected of the multiboot standard.
 */

ENTRY(multi_boot)
	/* no need to save anything */
	call	EXT_C(stop_floppy)

	movl	$0x2BADB002, %eax
	movl	0x8(%esp), %ebx

	/* boot kernel here (absolute address call) */
	call	*0x4(%esp)

	/* error */
	call	EXT_C(stop)

#endif /* ! STAGE1_5 */
	
/*
 * void console_putchar (int c)
 *
 * Put the character C on the console. Because GRUB wants to write a
 * character with an attribute, this implementation is a bit tricky.
 * If C is a control character (CR, LF, BEL, BS), use INT 10, AH = 0Eh
 * (TELETYPE OUTPUT). Otherwise, save the original position, put a space,
 * save the current position, restore the original position, write the
 * character and the attribute, and restore the current position.
 *
 * The reason why this is so complicated is that there is no easy way to
 * get the height of the screen, and the TELETYPE OUPUT BIOS call doesn't
 * support setting a background attribute.
 */
ENTRY(console_putchar)
	movl	0x4(%esp), %edx
	pusha
#ifdef STAGE1_5
	movb	$0x07, %bl
#else
	movl	EXT_C(console_current_color), %ebx
#endif
	
	call	EXT_C(prot_to_real)
	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

	movb	%dl, %al
	xorb	%bh, %bh

#ifndef STAGE1_5
	/* use teletype output if control character */
	cmpb	$0x7, %al
	je	1f
	cmpb	$0x8, %al
	je	1f
	cmpb	$0xa, %al
	je	1f
	cmpb	$0xd, %al
	je	1f

	/* save the character and the attribute on the stack */
	pushw	%ax
	pushw	%bx
	
	/* get the current position */
	movb	$0x3, %ah
	int	$0x10

	/* check the column with the width */
	cmpb	$79, %dl
	jl	2f
	
	/* print CR and LF, if next write will exceed the width */	
	movw	$0x0e0d, %ax
	int	$0x10
	movb	$0x0a, %al
	int	$0x10
	
	/* get the current position */
	movb	$0x3, %ah
	int	$0x10

2:	
	/* restore the character and the attribute */
	popw	%bx
	popw	%ax
	
	/* write the character with the attribute */
	movb	$0x9, %ah
	movw	$1, %cx
	int	$0x10

	/* move the cursor forward */
	incb	%dl
	movb	$0x2, %ah
	int	$0x10

	jmp	3f
#endif /* ! STAGE1_5 */
	
1:	movb	$0xe, %ah
	int	$0x10
	
3:	DATA32	call	EXT_C(real_to_prot)
	.code32
	
	popa
	ret


#ifndef STAGE1_5

#if 0
/* this table is used in translate_keycode below */
translation_table:
	.word	KEY_LEFT, 2
	.word	KEY_RIGHT, 6
	.word	KEY_UP, 16
	.word	KEY_DOWN, 14
	.word	KEY_HOME, 1
	.word	KEY_END, 5
	.word	KEY_DC, 4
	.word	KEY_BACKSPACE, 8
	.word	KEY_PPAGE, 7
	.word	KEY_NPAGE, 3
	.word	0
	
/*
 * translate_keycode translates the key code %dx to an ascii code.
 */
	.code16

translate_keycode:
	pushw	%bx
	pushw	%si
	
	movw	$ABS(translation_table), %si
	
1:	lodsw
	/* check if this is the end */
	testw	%ax, %ax
	jz	2f
	/* load the ascii code into %ax */
	movw	%ax, %bx
	lodsw
	/* check if this matches the key code */
	cmpw	%bx, %dx
	jne	1b
	/* translate %dx, if successful */
	movw	%ax, %dx

2:	popw	%si
	popw	%bx
	ret
#endif

	.code32
	

/*
 * remap_ascii_char remaps the ascii code %dl to another if the code is
 * contained in ASCII_KEY_MAP.
 */
	.code16
	
remap_ascii_char:
	pushw	%si
	
	movw	$ABS(EXT_C(ascii_key_map)), %si
1:
	lodsw
	/* check if this is the end */
	testw	%ax, %ax
	jz	2f
	/* check if this matches the ascii code */
	cmpb	%al, %dl
	jne	1b
	/* if so, perform the mapping */
	movb	%ah, %dl
2:
	/* restore %si */
	popw	%si

	ret

	.code32

	.align	4
ENTRY(ascii_key_map)
	.space	(KEY_MAP_SIZE + 1) * 2
	

/*
 * int console_getkey (void)
 * BIOS call "INT 16H Function 00H" to read character from keyboard
 *	Call with	%ah = 0x0
 *	Return:		%ah = keyboard scan code
 *			%al = ASCII character
 */

ENTRY(console_getkey)
	push	%ebp

	call	EXT_C(prot_to_real)

	.code16

	sti		/* getkey needs interrupt on */

	#; work around for Apple BIOS getkey bug
	#; check the keyboard buffer, until there is a keypress.
1:
	movb	$0x01, %ah		#; check key
	int	$0x16
	jz	1b			#; no keypress

	xorw	%ax, %ax
	int	$0x16

	movw	%ax, %dx		/* real_to_prot uses %eax */
	//call	translate_keycode
	call	remap_ascii_char
	
	DATA32	call	EXT_C(real_to_prot)
	.code32

	movw	%dx, %ax

	pop	%ebp
	ret


/*
 * int console_checkkey (void)
 *	if there is a character pending, return it; otherwise return -1
 * BIOS call "INT 16H Function 01H" to check whether a character is pending
 *	Call with	%ah = 0x1
 *	Return:
 *		If key waiting to be input:
 *			%ah = keyboard scan code
 *			%al = ASCII character
 *			Zero flag = clear
 *		else
 *			Zero flag = set
 */
ENTRY(console_checkkey)
	push	%ebp
	xorl	%edx, %edx
	
	call	EXT_C(prot_to_real)	/* enter real mode */

	.code16

	sti		/* checkkey needs interrupt on */

	movb	$0x1, %ah
	int	$0x16

	DATA32	jz	notpending
	
	movw	%ax, %dx
	//call	translate_keycode
	call	remap_ascii_char
	DATA32	jmp	pending

notpending:
	movl	$0xFFFFFFFF, %edx

pending:
	DATA32	call	EXT_C(real_to_prot)
	.code32

	mov	%edx, %eax

	pop	%ebp
	ret

	
/*
 * int console_getxy (void)
 * BIOS call "INT 10H Function 03h" to get cursor position
 *	Call with	%ah = 0x03
 *			%bh = page
 *      Returns         %ch = starting scan line
 *                      %cl = ending scan line
 *                      %dh = row (0 is top)
 *                      %dl = column (0 is left)
 */


ENTRY(console_getxy)
	push	%ebp
	push	%ebx                    /* save EBX */

	call	EXT_C(prot_to_real)

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

        xorb	%bh, %bh                /* set page to 0 */
	movb	$0x3, %ah
	int	$0x10			/* get cursor position */

	DATA32	call	EXT_C(real_to_prot)
	.code32

	movb	%dl, %ah
	movb	%dh, %al

	pop	%ebx
	pop	%ebp
	ret


/*
 * void console_gotoxy(int x, int y)
 * BIOS call "INT 10H Function 02h" to set cursor position
 *	Call with	%ah = 0x02
 *			%bh = page
 *                      %dh = row (0 is top)
 *                      %dl = column (0 is left)
 */


ENTRY(console_gotoxy)
	push	%ebp
	push	%ebx                    /* save EBX */

	movb	0xc(%esp), %dl           /* %dl = x */
	movb	0x10(%esp), %dh          /* %dh = y */

	call	EXT_C(prot_to_real)

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

        xorb	%bh, %bh                /* set page to 0 */
	movb	$0x2, %ah
	int	$0x10			/* set cursor position */

	DATA32	call	EXT_C(real_to_prot)
	.code32

	pop	%ebx
	pop	%ebp
	ret

	
/*
 * void console_cls (void)
 * BIOS call "INT 10H Function 09h" to write character and attribute
 *	Call with	%ah = 0x09
 *                      %al = (character)
 *                      %bh = (page number)
 *                      %bl = (attribute)
 *                      %cx = (number of times)
 */


ENTRY(console_cls)
	push	%ebp
	push	%ebx                    /* save EBX */

	call	EXT_C(prot_to_real)

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

	/* move the cursor to the beginning */
	movb	$0x02, %ah
	xorb	%bh, %bh
	xorw	%dx, %dx
	int	$0x10

	/* write spaces to the entire screen */
	movw	$0x0920, %ax
	movw	$0x07, %bx
	movw	$(80 * 25), %cx
        int	$0x10

	/* move back the cursor */
	movb	$0x02, %ah
	int	$0x10

	DATA32	call	EXT_C(real_to_prot)
	.code32

	pop	%ebx
	pop	%ebp
	ret

	
/*
 * int console_setcursor (int on)
 * BIOS call "INT 10H Function 01h" to set cursor type
 *      Call with       %ah = 0x01
 *                      %ch = cursor starting scanline
 *                      %cl = cursor ending scanline
 */

console_cursor_state:
	.byte	1
console_cursor_shape:
	.word	0
	
ENTRY(console_setcursor)
	push	%ebp
	push	%ebx

	/* check if the standard cursor shape has already been saved */
	movw	console_cursor_shape, %ax
	testw	%ax, %ax
	jne	1f

	call	EXT_C(prot_to_real)

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

	movb	$0x03, %ah
	xorb	%bh, %bh
	int	$0x10

	DATA32	call	EXT_C(real_to_prot)
	.code32

	movw	%cx, console_cursor_shape
1:
	/* set %cx to the designated cursor shape */
	movw	$0x2000, %cx
	movl	0xc(%esp), %ebx
	testl	%ebx, %ebx
	jz	2f
	movw	console_cursor_shape, %cx
2:	
	call	EXT_C(prot_to_real)

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

	movb    $0x1, %ah
	int     $0x10 

	DATA32	call	EXT_C(real_to_prot)
	.code32

	movzbl	console_cursor_state, %eax
	movb	%bl, console_cursor_state
	
	pop	%ebx
	pop	%ebp
	ret

/* graphics mode functions */
#ifdef SUPPORT_GRAPHICS
VARIABLE(cursorX)
	.word	0
VARIABLE(cursorY)
	.word	0
VARIABLE(cursorCount)
	.word	0
VARIABLE(cursorBuf)
	.byte	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

	
/*
 * int set_videomode(mode)
 * BIOS call "INT 10H Function 0h" to set video mode
 *	Call with	%ah = 0x0
 *			%al = video mode
 *      Returns old videomode.
 */
ENTRY(set_videomode)
	push	%ebp
	push	%ebx
	push	%ecx

	movb	0x10(%esp), %cl

	call	EXT_C(prot_to_real)

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

	xorw	%bx, %bx
	movb	$0xf, %ah
	int	$0x10			/* Get Current Video mode */
	movb	%al, %ch
	xorb	%ah, %ah
	movb	%cl, %al
	int	$0x10			/* Set Video mode */

	DATA32	call	EXT_C(real_to_prot)
	.code32

	xorb	%ah, %ah
	movb	%ch, %al

	pop	%ecx
	pop	%ebx
	pop	%ebp
	ret


/*
 * unsigned char * graphics_get_font()
 * BIOS call "INT 10H Function 11h" to set font
 *      Call with       %ah = 0x11
 */
ENTRY(graphics_get_font)
	push	%ebp
	push	%ebx
	push	%ecx
	push	%edx

	call	EXT_C(prot_to_real)

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

	movw	$0x1130, %ax
	movb	$6, %bh		/* font 8x16 */
	int	$0x10
	movw	%bp, %dx
	movw	%es, %cx

	DATA32	call	EXT_C(real_to_prot)
	.code32

	xorl	%eax, %eax
	movw	%cx, %ax
	shll	$4, %eax
	movw	%dx, %ax

	pop	%edx
	pop	%ecx
	pop	%ebx
	pop	%ebp
	ret
	

	
/*
 * graphics_set_palette(index, red, green, blue)
 * BIOS call "INT 10H Function 10h" to set individual dac register
 *	Call with	%ah = 0x10
 *			%bx = register number
 *			%ch = new value for green (0-63)
 *			%cl = new value for blue (0-63)
 *			%dh = new value for red (0-63)
 */

ENTRY(graphics_set_palette)
	push	%ebp
	push	%eax
	push	%ebx
	push	%ecx
	push	%edx

	movw	$0x3c8, %bx		/* address write mode register */

	/* wait vertical retrace */

	movw	$0x3da, %dx
l1b:	inb	%dx, %al	/* wait vertical active display */
	test	$8, %al
	jnz	l1b

l2b:	inb	%dx, %al	/* wait vertical retrace */
	test	$8, %al
	jnz	l2b

	mov	%bx, %dx
	movb	0x18(%esp), %al		/* index */
	outb	%al, %dx
	inc	%dx

	movb	0x1c(%esp), %al		/* red */
	outb	%al, %dx

	movb	0x20(%esp), %al		/* green */
	outb	%al, %dx

	movb	0x24(%esp), %al		/* blue */
	outb	%al, %dx

	movw	0x18(%esp), %bx

	call	EXT_C(prot_to_real)

	.code16

	//sti		/* it is not bad keeping interrupt off */
	sti		/* for hardware interrupt or watchdog */

	movb	%bl, %bh
	movw	$0x1000, %ax
	int	$0x10

	DATA32	call	EXT_C(real_to_prot)
	.code32	

	pop	%edx
	pop	%ecx
	pop	%ebx
	pop	%eax
	pop	%ebp
	ret

#endif /* SUPPORT_GRAPHICS */
		
/*
 * getrtsecs()
 *	if a seconds value can be read, read it and return it (BCD),
 *      otherwise return 0xFF
 * BIOS call "INT 1AH Function 02H" to check whether a character is pending
 *	Call with	%ah = 0x2
 *	Return:
 *		If RT Clock can give correct values
 *			%ch = hour (BCD)
 *			%cl = minutes (BCD)
 *                      %dh = seconds (BCD)
 *                      %dl = daylight savings time (00h std, 01h daylight)
 *			Carry flag = clear
 *		else
 *			Carry flag = set
 *                         (this indicates that the clock is updating, or
 *                          that it isn't running)
 */
ENTRY(getrtsecs)
	push	%ebp

	call	EXT_C(prot_to_real)	/* enter real mode */

	.code16

	#;sti		/* getrtsecs needs interrupt on */
	sti	#; added 2006-11-30

#if 0
	movb	$0x2, %ah

	/* Ralf Brown's Interrupt List says:
	 *
	 * BUG: Some BIOSes leave CF unchanged if successful,
	 * so CF should be cleared before calling this function
	 */

	clc
	int	$0x1a

	DATA32	jnc	gottime
	movb	$0xff, %dh

gottime:
#else
	/* The call int1A/ah=02 could fail all the time.
	 * So we should avoid using it. Instead, we use ticks at 0040:006C.
	 *					- Tinybit 2007-04-21
	 */
	pushl	%ecx
	movl	0x46C, %eax
	movl	$5, %ecx	/* 5 seconds */
	mull	%ecx
	xorl	%edx, %edx
	movl	$91, %ecx	/* 91 ticks = 5 seconds */
	divl	%ecx
	xorl	%edx, %edx
	movl	$60, %ecx
	divl	%ecx		/* EDX=seconds (0 .. 59) */
	movb	%dl, %dh
	popl	%ecx
	
#endif
	DATA32	call	EXT_C(real_to_prot)
	.code32

	movb	%dh, %al

	pop	%ebp
	ret

	
/*
 *  void get_datetime(unsigned long *date, unsigned long *time);
 */
ENTRY(get_datetime)
	pushl	%ebp
	call	EXT_C(prot_to_real)

	.code16

	sti		/* for hardware interrupt or watchdog */
	movb	$2, %ah
	clc
	int	$0x1a
	jc	2f

	pushw	%cx
	pushw	%dx

	movb	$4, %ah
	clc
	int	$0x1a
	jc	3f

	pushw	%cx
	pushw	%dx
	popl	%edx
	popl	%ecx
	jmp	1f

3:
	popl	%eax

2:
	xorl	%ecx, %ecx
	xorl	%edx, %edx

1:
	DATA32	call	EXT_C(real_to_prot)
	.code32

	movl	%esp, %ebp
	movl	8(%ebp), %eax
	movl	%edx, (%eax)
	movl	12(%ebp), %eax
	movl	%ecx, (%eax)

	popl	%ebp
	ret

#if 0
	/* This BIOS call should NOT be called since it will clear the byte at 0040:0070. */

/*
 * currticks()
 *	return the real time in ticks, of which there are about
 *	18-20 per second
 */
ENTRY(currticks)
	pushl	%ebp

	call	EXT_C(prot_to_real)	/* enter real mode */

	.code16

	#;sti		/* currticks needs interrupt on */
	sti	#; added 2006-11-30

	/* %ax is already zero */
        int	$0x1a

	DATA32	call	EXT_C(real_to_prot)
	.code32

	movl	%ecx, %eax
	shll	$16, %eax
	movw	%dx, %ax

	popl	%ebp
	ret
#endif

#endif /* STAGE1_5 */

/*
 *  This is the area for all of the special variables.
 */

	.align	4

#;protstack:
#;	.long	PROTSTACKINIT

VARIABLE(boot_drive)
#ifdef SUPPORT_DISKLESS
	.long	NETWORK_DRIVE
#else
	.long	0
#endif

//VARIABLE(install_second_sector)
//	.long	0
	
	/* an address can only be long-jumped to if it is in memory, this
	   is used by multiple routines */
offset:
	.long	0x8000
segment:
	.word	0

#if 0
VARIABLE(apm_bios_info)
	.word	0	/* version */
	.word	0	/* cseg */
	.long	0	/* offset */
	.word	0	/* cseg_16 */
	.word	0	/* dseg_16 */
	.word	0	/* cseg_len */
	.word	0	/* cseg_16_len */
	.word	0	/* dseg_16_len */
#endif
	
/*
 * This is the Global Descriptor Table
 *
 *  An entry, a "Segment Descriptor", looks like this:
 *
 * 31          24         19   16                 7           0
 * ------------------------------------------------------------
 * |             | |B| |A|       | |   |1|0|E|W|A|            |
 * | BASE 31..24 |G|/|0|V| LIMIT |P|DPL|  TYPE   | BASE 23:16 |
 * |             | |D| |L| 19..16| |   |1|1|C|R|A|            |
 * ------------------------------------------------------------
 * |                             |                            |
 * |        BASE 15..0           |       LIMIT 15..0          |
 * |                             |                            |
 * ------------------------------------------------------------
 *
 *  Note the ordering of the data items is reversed from the above
 *  description.
 */

	.align	16
gdt:
	.word	0, 0
	.byte	0, 0, 0, 0

	/* code segment */
	.word	0xFFFF, 0
	.byte	0, 0x9A, 0xCF, 0

	/* data segment */
	.word	0xFFFF, 0
	.byte	0, 0x92, 0xCF, 0

	/* 16 bit real mode CS */
	.word	0xFFFF, 0
	.byte	0, 0x9E, 0, 0

	/* 16 bit real mode DS */
	.word	0xFFFF, 0
	.byte	0, 0x92, 0, 0


/* this is the GDT descriptor */
gdtdesc:
	.word	0x27			/* limit */
	.long	gdt			/* addr */



	.code32

/* this code will be moved to and get executed at HMA_ADDR=0x2B0000 */

/* our gdt starts at HMA_ADDR=0x2B0000 */

ENTRY(HMA_start)

	/* the first entry of GDT, i.e., the default null entry,
	 * can be any value. it never get used. So we use these
	 * 8 bytes for our jmp and GDT descriptor.
	 */

	. = EXT_C(HMA_start) + 0	/* GDT entry: default null */

	jmp	1f		/* two-byte short jmp */

	. = EXT_C(HMA_start) + 2

	/* 6-byte GDT descriptor */
gdtdescHMA:
	.word	0x27		/* limit */
	.long	HMA_ADDR	/* linear base address */

	. = EXT_C(HMA_start) + 8	/* GDT entry: unused */

	/* code segment, although it is no use here for now */
	.word	0xFFFF, 0
	.byte	0, 0x9A, 0xCF, 0

	. = EXT_C(HMA_start) + 0x10	/* GDT entry: unused */

	/* data segment, although it is no use here for now */
	.word	0xFFFF, 0
	.byte	0, 0x92, 0xCF, 0

	. = EXT_C(HMA_start) + 0x18	/* GDT entry: 16-bit code */

	/* 16-bit code segment base=0x2B0000 */
	.word	0xFFFF, 0x0000
	.byte	0x2B, 0x9E, 0, 0

	. = EXT_C(HMA_start) + 0x20	/* GDT entry: 16-bit data */

	/* real mode data segment base=0x200 */
	.word	0xFFFF, 0x0200
	.byte	0x00, 0x92, 0, 0

1:
	/* set up to pass boot drive */
	movb	EXT_C(boot_drive), %dl

	/* check if the --ebx option is given. */
	movl	(EXT_C(chain_ebx_set) - EXT_C(HMA_start) + HMA_ADDR), %eax
	testl	%eax, %eax
	jz	1f
	movl	(EXT_C(chain_ebx) - EXT_C(HMA_start) + HMA_ADDR), %ebx
1:

	/* check if the --edx option is given. */
	movl	(EXT_C(chain_edx_set) - EXT_C(HMA_start) + HMA_ADDR), %eax
	testl	%eax, %eax
	jz	1f
	movl	(EXT_C(chain_edx) - EXT_C(HMA_start) + HMA_ADDR), %edx
1:

	/* move new loader from extended memory to conventional memory.
	 * this will overwrite our GRUB code, data and stack, so we should not
	 * use instuctions like push/pop/call/ret, and we should not use
	 * functions like gateA20().
	 */

	/* the new loader is currently at 0x200000 */
	movl	$0x00200000, %esi
	xorl	%eax, %eax
	xorl	%edi, %edi
	movw	(EXT_C(chain_load_segment) - EXT_C(HMA_start) + HMA_ADDR), %di
	shll	$4, %edi
	movw	(EXT_C(chain_load_offset) - EXT_C(HMA_start) + HMA_ADDR), %ax
	addl	%eax, %edi
	//movl	$0x00007c00, %edi
	movl	(EXT_C(chain_load_length) - EXT_C(HMA_start) + HMA_ADDR), %ecx
	cld
	repz movsb

	/* switch to real mode */

	/* set new GDT */
	lgdt	(gdtdescHMA - EXT_C(HMA_start) + HMA_ADDR)

	/* set up segment limits */
	movw	$PSEUDO_RM_DSEG, %ax
	movw	%ax, %ds
	movw	%ax, %es
	movw	%ax, %fs
	movw	%ax, %gs
	movw	%ax, %ss

	movl	$0x200, %esp	/* points to end of interrupt vector table */
				/* SS base=0x200, so SS:SP=physical 0x400 */

	/* jump to a 16 bit segment, this might be an extra step:
	 * set up CS limit, also clear high word of EIP
	 */
	ljmp	$PSEUDO_RM_CSEG, $(1f - EXT_C(HMA_start))
1:
	.code16

	/* clear the PE bit of CR0 */
	movl	%cr0, %eax
	//andl	$CR0_PE_OFF, %eax
	andl 	$0x0000FFFE, %eax
	movl	%eax, %cr0

	/* setup DS, ES, SS, FS and GS before loading CS */
	xorl	%eax, %eax
	movw	%ax, %ds
	movw	%ax, %es
	movw	%ax, %ss
	movl	$0x400, %esp
	movw	%ax, %fs
	movw	%ax, %gs

	/* flush prefetch queue, reload %cs */

	.byte	0xEA		/* ljmp 0000:7c00 */
VARIABLE(chain_boot_IP)
	.word	0x7c00		/* offset */
VARIABLE(chain_boot_CS)
	.word	0x0000		/* segment */

VARIABLE(chain_load_offset)
	.word	0x7c00
VARIABLE(chain_load_segment)
	.word	0x0000
VARIABLE(chain_load_length)
	.long	0x200
VARIABLE(chain_ebx)
	.long	0
VARIABLE(chain_ebx_set)
	.long	0
VARIABLE(chain_edx)
	.long	0
VARIABLE(chain_edx_set)
	.long	0
VARIABLE(chain_enable_gateA20)
	.long	0

	/* max length of code is 1 sector */
	. = . - (. - EXT_C(HMA_start))/0x201

	/* ensure this resides in the first 64KB */
	. = . - (ABS(.) / 0x10001)

	.code32



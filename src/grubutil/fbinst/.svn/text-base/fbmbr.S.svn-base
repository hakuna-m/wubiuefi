/*
 *  GRUB Utilities --  Utilities for GRUB Legacy, GRUB2 and GRUB for DOS
 *  Copyright (C) 2009  Bean (bean123ch@gmail.com)
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

	.text

#include "version.h"
#include "fbinst.h"

#define ABS(a)		(a - start + CODE_START)

#define VARIABLE(a)	. = start + OFS_ ## a ; a:

#define KEY_ESCAPE	0x11b

#define DATA_BUF_SEG	0x8000
#define CODE_START	0x2000

#define DOT_SIZE	1024		/* 512k  */

#define	orig_es		-2(%bp)
#define	orig_di		-4(%bp)
#define	text_color	-6(%bp)
#define	file_name	-8(%bp)
#define	gdt_table	-56(%bp)
#define	gdt_src_len	-40(%bp)
#define	gdt_src_low	-38(%bp)
#define	gdt_src_hi1	-36(%bp)
#define	gdt_src_acc	-35(%bp)
#define	gdt_src_hi2	-33(%bp)
#define	gdt_dst_len	-32(%bp)
#define	gdt_dst_low	-30(%bp)
#define	gdt_dst_hi1	-28(%bp)
#define	gdt_dst_acc	-27(%bp)
#define	gdt_dst_hi2	-25(%bp)
#define	block_size	-58(%bp)
#define	dot_max		-60(%bp)
#define	dot_cur		-62(%bp)

//#define DEBUG
//#define DEBUG_INT13

#ifdef DEBUG

#define DBG_PRINT(s)	jmp 101f ; 100: .ascii s "\0" ; 101: pushaw ; movw $ABS(100b), %si ; call print_string; popaw
#define DUMP_VAR(v)	pushw v ; call dump_hex

#else

#define DBG_PRINT(s)
#define DUMP_VAR(s)

#endif

	.code16

start:
	jmp	start_7c00

	. = start + 0x10
	.byte	2

	. = start + 0x18
	.word	0x3f
	.word	0xff

	. = start + 0x24
	.byte	0x80

#ifdef DEBUG
	. = start + 0x28
#else
	. = start + 0x60
#endif

start_7c00:
	xorw	%bx, %bx
	movw	%bx, %ds
	movw	%bx, %bp

	movw	%bx, %ss
	movw	$0x7c00, %sp

	pushw	%es
	pushw	%di

#if CODE_START == 0x2000
	movw	$0x200, %ax
	movw	%ax, %es
	incw	%ax
#else
	pushw	$(CODE_START >> 4)
	popw	%es
	movw	$0x201, %ax
#endif

	movw	$0x1, %cx
	xorb	%dh, %dh
	call	safe_int13		/* 0, 0, 1  */
	call	check_mbr
	movw	ABS(lba), %di		/* sector 0 offset  */

	pushw	$((CODE_START + 0x200) >> 4)
	popw	%es

	/* detect lba mode  */
	pushaw

	movb	$0x41, %ah
	movw	$0x55aa, %bx
	int	$0x13
	jc	1f			/* No EBIOS */
	cmpw	$0xaa55, %bx
	jne	1f			/* No EBIOS */
	testb	$1, %cl
	jz	1f			/* No EBIOS */
	popaw
	decb	%dh
	jmp	2f
1:

	popaw

	incb	%dh
	call	safe_int13		/* 0, 1, 1  */
	pushw	%ax
	call	calc_lba
	movb	%al, ABS(spt)
	popw	%ax

	xchg	%ch, %dh		/* 1, 0, 1  */
	call	safe_int13
	call	calc_lba
	divb	ABS(spt)
	movb	%al, ABS(heads)

2:

	movw	ABS(boot_base), %ax
	incw	%ax
	movw	ABS(boot_size), %si
	call	read_sectors
	ljmp	$0, $ABS(start_2000)

calc_lba:
	movw	(CODE_START + 0x200 + 0x1fe), %ax
	cmpw	$0xaa55, %ax
	jnz	1f
	call	check_mbr
	movw	(CODE_START + 0x200 + OFS_lba), %ax
1:
	subw	%di, %ax
	ret

check_mbr:
	cmpw	$FB_MAGIC_WORD, %es: (OFS_fb_magic)
	jnz	1f
	ret
1:
	movb	$'m', %al
	jmp	early_fail

test_int13:

	pushaw
	stc
	int	$0x13
	sti
	popaw

#ifdef DEBUG_INT13
	pushfw
	pushaw

	pushaw
	pushfw
	pushw	%es

	shlw	$9, %ax
	addw	%ax, %bx
	movw	$5, %cx

1:
	decw	%bx
	decw	%bx
	pushw	%es: (%bx)
	loop	1b

	pushw	%es: (OFS_lba)

	movb	$16, %cl
1:
	call	dump_hex
	loop	1b

	popaw
	popfw
#endif

	ret

safe_int13:
	call	test_int13
	jc	err_int13
	ret

err_int13:
	movb	$'i', %al

early_fail:
	movb	$0xe, %ah
	xorw	%bx, %bx
	int	$0x10

halt:
	hlt
	jmp	halt

#ifdef DEBUG

/*
 * input:
 *   18(%bp) - word
 */
dump_hex:
	pushaw
	movw	%sp, %bp

	movb	$0xe, %ah
	xorw	%bx, %bx
	movw	$4, %cx
	movw	18(%bp), %dx
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
	ret	$2

#endif

/*
 * input:
 *   %es:%bx - target address
 *   %bp,%ax - start sector
 *   %si - sector count
 *   %di - sector offset
 * output:
 *   %si - remain sectors
 */
read_sectors:
	subw	%di, %ax
	sbbw	$0, %bp

	cmpb	$0xff, %dh
	jnz	chs_mode

lba_mode:
	/* cx = sector,  ax = current count, si = total count  */

	movw	%ax, %cx

lba_mode_cont:

	pushw	%si

	xorw	%ax, %ax
	pushw	%ax
	pushw	%ax

	pushw	%bp
	pushw	%cx

	pushw	%es
	pushw	%bx

	movb	ABS(max_sec), %al
	cmpw	%si, %ax
	jbe	1f
	movw	%si, %ax
1:
	pushw	%ax
	pushw	$0x10

	movw	%sp, %si
	movb	$0x42, %ah
	call	read_int13
	addw	$16, %sp

	popw	%si
	ret

chs_mode:
	/* ch = cylinder, cl = sector, dh = head, dl = drive  */
	/* ax = current count, si = total count  */

	pushw	%dx
	movw	%bp, %dx

	movw	%ax, %cx
	movb	ABS(spt), %al
	mulb	ABS(heads)
	xchgw	%ax, %cx
	divw	%cx

	movw	%ax, %cx	/* cx = cylinder  */

	movw	%dx, %ax
	divb	ABS(spt)

	popw	%dx		/* dl = drive  */
	movb	%al, %dh	/* dh = heads  */

	shlb	$6, %ch
	orb	%ah, %ch
	xchgb	%cl, %ch	/* cl = sector, ch = cylinder  */

chs_mode_cont:
	movzbw	ABS(spt), %ax
	subb	%cl, %al
	andb	$0x3f, %al
	cmpb	ABS(max_sec), %al
	jbe	1f
	movb	ABS(max_sec), %al
1:

	cmpw	%si, %ax
	jbe	1f
	movw	%si, %ax
1:

	movb	$2, %ah
	incb	%cl

read_int13:
	call	test_int13
	jc	1f
	xorb	%ah, %ah
	ret

1:
	cmpb	$7, %al
	jbe	1f
	movb	$7, %al
	jmp	2f

1:
	cmpb	$1, %al
	jbe	err_int13
	movb	$1, %al

2:

	cmpb	$0xff, %dh
	jnz	2f
	movb	%al, 2(%si)
2:

	movb	%al, ABS(max_sec)
	pushaw
	xorw	%ax, %ax
	int	$0x13
	popaw
	jmp	read_int13

VARIABLE(max_sec)
	.byte	63

VARIABLE(lba)
	.byte	0

VARIABLE(bootdrv)
	.byte	0

VARIABLE(spt)
	.byte	63

VARIABLE(heads)
	.byte	255

VARIABLE(boot_base)
	.word	0

VARIABLE(boot_size)
	.word	0

VARIABLE(fb_magic)
	.ascii	FB_MAGIC

	. = start + 0x200 - 2

	.word	0xaa55

VARIABLE(menu_ofs)
	.word	start_menu - start - 0x200

VARIABLE(flags)
	.word	0

VARIABLE(ver_major)
	.byte	VER_MAJOR

VARIABLE(ver_minor)
	.byte	VER_MINOR

VARIABLE(pri_size)
	.long	0

VARIABLE(ext_size)
	.long	0

read_sectors_cont_1:
	pushw	%ax

	shlw	$5, %ax
	pushw	%bx
	movw	%es, %bx
	addw	%ax, %bx
	movw	%bx, %es
	popw	%bx

	popw	%ax

read_sectors_cont_2:
	subw	%ax, %si
	jnz	1f
	ret

1:
	cmpb	$0xff, %dh
	jnz	1f
	addw	%ax, %cx
	adcw	$0, %bp
	jmp	lba_mode_cont

1:
	decb	%cl
	addb	%cl, %al
	andb	$0x3f, %al
	andb	$0xc0, %cl
	cmpb	ABS(spt), %al
	jz	1f
	orb	%al, %cl
	jmp	chs_mode_cont
1:
	incb	%dh
	cmpb	ABS(heads), %dh
	jnz	chs_mode_cont
	xorb	%dh, %dh
	incb	%ch
	jnz	chs_mode_cont
	addb	$0x40, %cl
	jmp	chs_mode_cont

/*
 * input:
 *   %si: string pointer
 */
fail:
	call	print_string
	jmp	halt

/*
 * input:
 *   %si - string pointer
 */
print_string:
	cld
	pushaw
	movw	$1, %cx
	movw	text_color, %bx

1:
	lodsb	(%si), %al
	orb	%al, %al
	jz	1f
	cmpb	$10, %al
	jz	2f
	cmpb	$13, %al
	jz	2f
	movb	$0x9, %ah
	int	$0x10
2:
	movb	$0xe, %ah
	int	$0x10
	jmp	1b

1:
	popaw
	ret

/*
 * input:
 *   src, dst - gdt table
 *   %ax - number of sectors
 *   block_size (512/510)
 */
copy_sectors:
	pushw	%es
	pushw	%ds

	pushw	%ds
	popw	%es
	leaw	gdt_table, %si
	movw	block_size, %cx
	cmpb	$2, %ch
	jnz	1f
	shlw	$9, %ax
	movw	%ax, %cx
	movb	$1, %al

1:
	movb	$0x87, %ah

1:
	pushaw
	shrw	$1, %cx
	int	$0x15
	popaw

	jnc	2f
	movw	$ABS(err_int15), %si
	jmp	fail

2:
	addw	$512, gdt_src_low
	addw	%cx, gdt_dst_low
	jnc	2f
	incb	gdt_dst_hi1
	jnz	2f
	incb	gdt_dst_hi2
2:
	decb	%al
	jnz	1b

	popw	gdt_src_low
	popw	%es
	ret

/*
 * input:
 *   %cl - type
 * output:
 *   cf clear if found
 *   %si - current item
 */

find_first_item:
	movw	%bp, %si
	jmp	find_item_start

find_next_item:
	movb	-2(%si), %al
1:
	xorb	%ah, %ah
	addw	%ax, %si

find_item_start:
	cld
	lodsw
	cmpb	%ah, %cl
	jz	1f
	orb	%al, %al
	jnz	1b
	stc
1:
	ret

/*
 * input:
 *   %si - file name
 * output:
 *   %si - current item
 *   %ax - number of sectors
 *   block_size (512/510)
 */
find_file:
	movw	%si, file_name
	movw	$ABS(start_menu), %si
	movb	$FBM_TYPE_FILE, %cl
	call	find_item_start

1:
	jnc	2f
	movw	$ABS(err_no_file), %si
	jmp	fail

2:

	pushw	%si
	addw	$13, %si
	movw	file_name, %bx

2:
	lodsb
	cmpb	(%bx), %al
	jnz	2f
	incw	%bx
	orb	%al, %al
	jnz	2b

	movw	%bx, file_name

2:
	popw	%si
	jz	1f
	call	find_next_item
	jmp	1b

1:

	movw	2(%si), %ax
	cmpw	ABS(pri_size + 2), %ax
	jnz	1f
	movw	(%si), %ax
	cmpw	ABS(pri_size), %ax
1:

	movw	$512, %cx
	jae	1f
	decw	%cx
	decw	%cx
1:

	pushw	%dx

	movw	4(%si), %ax
	movw	6(%si), %dx
	divw	%cx
	orw	%dx, %dx
	jz	1f
	incw	%ax
1:

	popw	%dx
	movw	%cx, block_size

	movw	dot_max, %bx
	orw	%bx, %bx
	jz	1f
	movw	%bx, dot_cur
	movw	%si, %bx
	movw	$ABS(loading_message), %si
	call	print_string
	leaw	13(%bx), %si
	call	print_string
	movw	%bx, %si

1:
	ret

/*
 * input:
 *   gdt_dst - target address
 *   %si - name
 */

load_file:
	call	find_file

/*
 * input:
 *   gdt_dst - target address
 *   %si - current item
 *   %ax - number of sectors
 *   block_size (512/510)
 */
load_data:
	pushw	%bp

	xorw	%bx, %bx
	pushw	$DATA_BUF_SEG
	popw	%es

	pushw	%ax
	movw	(%si), %ax
	movw	2(%si), %bp
	popw	%si

	call	read_sectors

1:
	movw	%bp, %bx
	popw	%bp

	cmpw	$0, dot_max
	jz	2f
	subw	%ax, dot_cur
	jnc	2f
	pushw	%si
	movw	$ABS(dot_message), %si
	call	print_string
	movw	dot_max, %si
	addw	%si, dot_cur
	popw	%si
2:

	pushaw
	call	copy_sectors
	popaw

	pushw	%bp
	movw	%bx, %bp
	xorw	%bx, %bx
	call	read_sectors_cont_2
	orw	%si, %si
	jnz	1b

	popw	%bp
	ret

start_2000:
	pushw	%si

1:
	call	read_sectors_cont_1
	orw	%si, %si
	jnz	1b

	popw	%ax				/* ax = boot_size  */
	pushw	%ax

	shlw	$9, %ax
	addw	$(CODE_START + 0x200 + 64), %ax

	movw	%ax, %bp
	movw	$COLOR_NORMAL, text_color
	movw	%si, dot_max			/* si = 0  */

	xorw	%ax, %ax
	movw	%ax, %es
	movw	$24, %cx
	pushw	%di
	leaw	gdt_table, %di
	cld
	rep	stosw
	popw	%di

	decw	%ax
	movw	%ax, gdt_src_len
	movw	%ax, gdt_dst_len
	movb	$0x93, %al
	movb	%al, gdt_src_acc
	movb	%al, gdt_dst_acc

	movw	ABS(menu_ofs), %cx
	shrw	$9, %cx
	incw	%cx
	popw	%ax				/*  ax = boot_size  */
	subw	%cx, %ax
	jz	1f
	shlw	$9, %cx
	addw	$(CODE_START + 0x200), %cx
	movw	%cx, gdt_src_low
	decw	%cx
	decw	%cx
	movw	%cx, gdt_dst_low
	movw	$510, block_size
	call	copy_sectors
1:

	popw	orig_di
	popw	orig_es

	movb	$(DATA_BUF_SEG >> 12), gdt_src_hi1
	movw	$ABS(menu_file), %si
	movw	%bp, gdt_dst_low
	call	load_file

	jmp	parse_menu

	. = start + 0x400 - 2
	.word	0

/*
 * output:
 *   %ax - keycode
 */
check_key:
	movb	$0x1, %ah
	pushw	%ax
	int	$0x16
	popw	%ax
	jnz	1f

	movb	$0x11, %ah
	pushw	%ax
	int	$0x16
	popw	%ax
	jnz	1f
	xorw	%ax, %ax
	ret

1:
	decb	%ah
	int	$0x16
	ret

/*
 * output:
 *   cf clear if menu found
 *   si - current item
 */
check_menu:
	call	check_key
	orw	%ax, %ax
	jz	2f

	pushaw
	movw	%ax, %bx
	movb	$FBM_TYPE_MENU, %cl
	call	find_first_item

1:
	jc	1f
	cmpw	(%si), %bx
	jz	3f
	call	find_next_item
	jmp	1b
1:

	popaw

2:
	stc
	ret

3:
	addw	$16, %sp
	ret

/*
 * input:
 *   %bl - timeout
 * output:
 *   cf clear if menu found
 *   si - current item
 */
check_timeout:
	pushw	%dx

	cmpb	$0xff, %bl
	jnz	2f

1:
	call	check_menu
	jnc	3f
	hlt
	jmp	1b

2:
	xorw	%ax, %ax
	int	$0x1a

	/* cx,dx = current tick  */
	/* si,bx = next tick  */
	movb	$18, %al
	mulb	%bl
	addw	%ax, %dx
	adcw	$0, %cx
	movw	%dx, %bx
	movw	%cx, %si

1:
	call	check_menu
	jnc	3f

	xorw	%ax, %ax
	int	$0x1a

	orb	%al, %al
	jz	2f
	subw	$0xb0, %bx
	sbbw	$0x18, %si
2:
	cmpw	%cx, %si
	jnz	2f
	cmpw	%dx, %bx
2:
	jb	3f

	hlt
	jmp	1b

3:

	popw	%dx
	ret

parse_menu:
	/* bl = timeout  */
	movb	$FBM_TYPE_TIMEOUT, %cl
	call	find_first_item
	movb	$0, %bl
	jc	1f
	movb	(%si), %bl
1:

	call	check_menu
	jnc	boot_item
	cmpw	$KEY_ESCAPE, %ax
	jnz	1f
	movb	$0xff, %bl
1:

	orb	%bl, %bl
	jz	no_timeout

	cld
	movw	%bp, %si

1:
	lodsw
	orb	%al, %al
	jz	3f
	cmpb	$FBM_TYPE_COLOR, %ah
	jnz	2f
	movb	(%si), %bh
	movb	%bh, text_color
2:
	cmpb	$FBM_TYPE_TEXT, %ah
	jnz	2f
	call	print_string
2:
	xorb	%ah, %ah
	addw	%ax, %si
	jmp	1b

3:
	movb	$COLOR_NORMAL, text_color
	call	check_timeout
	jnc	boot_item

no_timeout:
	movb	$FBM_TYPE_DEFAULT, %cl
	call	find_first_item
	movb	$0, %bl
	jc	1f
	movb	(%si), %bl
1:

	movb	$FBM_TYPE_MENU, %cl
	call	find_first_item

1:
	jc	1f
	subb	$1, %bl
	jc	boot_item
	call	find_next_item
	jmp	1b

1:
	movw	$ABS(err_no_menu), %si
	jmp	fail

boot_item:
	call	clear_dest

	movb	2(%si), %al
	addw	$3, %si
	cmpb	$FBS_TYPE_GRLDR, %al
	jnz	1f

boot_grldr:
	movb	$2, gdt_dst_hi1
	call	load_file
	call	setup_mbr
	ljmp	$0x2000, $0

1:
	cmpb	$FBS_TYPE_SYSLINUX, %al
	jnz	10f

boot_syslinux:
	movw	$0x7c00, gdt_dst_low
	call	load_file
	call	copy_bs
	movb	ABS(max_sec), %al
	movb	%al, (0x7dfc)		/* MaxTransfer  */
	call	setup_mbr
	ljmp	$0, $0x7c00

10:
	cmpb	$FBS_TYPE_LINUX, %al
	jnz	10f

boot_linux:
	movw	$DOT_SIZE, dot_max
	call	find_file
	pushw	%ax
	movb	$9, gdt_dst_hi1
	movw	$1, %ax
	call	load_data_inc
	movw	$0x9000, %bx
	movw	%bx, %es
	movb	%es: (0x1f1), %al
	incw	%ax
	shlw	$9, %ax
	movw	%ax, %cx
	addw	block_size, %ax
	decw	%ax
	pushw	%dx
	xorw	%dx, %dx
	divw	block_size
	popw	%dx

	pushw	%ax
	decw	%ax
	call	load_data_inc
	incw	%ax

	pushw	%dx
	mulw	block_size
	popw	%dx
	subw	%cx, %ax

	movb	$0x10, gdt_dst_hi1
	movw	$0, %cx
	xchgw	%cx, gdt_dst_low	/* assume load address 0x100000 */

	jz	1f
	pushw	block_size
	movw	%ax, block_size
	subw	%ax, %cx
	movw	%cx, gdt_src_low
	incb	gdt_src_hi1		/* 8000 -> 9000  */
	movw	$1, %ax
	pushw	%si
	call	copy_sectors
	popw	%si
	decb	gdt_src_hi1		/* 9000 -> 8000  */
	popw	block_size
1:

	popw	%cx
	popw	%ax

	subw	%cx, %ax
	jz	1f
	call	load_data_inc
1:

	call	print_newline

	movw	%bx, %es
	movw	file_name, %si
	cmpb	$0, (%si)
	jz	1f
	call	clear_dest
	incb	gdt_dst_hi2			/* initrd at 16m  */
	pushw	%bx
	call	find_file

	incb	%es: (0x218 + 3)		/* ramdisk_image  */
	movw	4(%si), %cx
	movw	%cx, %es: (0x21c)		/* ramdisk_size  */
	movw	6(%si), %cx
	movw	%cx, %es: (0x21c + 2)		/* ramdisk_size  */

	call	load_data
	call	print_newline

	popw	%bx
	movw	%bx, %es

	movw	file_name, %si
	decw	%si
1:
	incw	%si

	movw	%bx, %es: (0x228)		/* cmd_line_ptr  */
	cld

1:
	lodsb
	movb	%al, %es: (%bx)
	incw	%bx
	orb	%al, %al
	jnz	1b

	movb	$7, %es: (0x210)		/* type of loader (GRUB) */
	movw	$(0x9000 - 0x200), %es: (0x224)	/* heap end  */
	orb	$0x80, %es: (0x211)		/* loadflags  */
	movb	$9, %es: (0x228 + 2)		/* cmd_line_ptr  */

	cli
	movw	%es, %bx

	movw	%bx, %ss
	movw	%bx, %sp

	movw	%bx, %ds
	movw	%bx, %fs
	movw	%bx, %gs

	ljmp	$0x9020, $0

	. = start + 0x600 - 2
	.word	0

print_newline:
	movw	$ABS(newline), %si
	call	print_string
	ret

clear_dest:
	xorw	%ax, %ax
	movw	%ax, gdt_dst_low
	movb	%al, gdt_dst_hi1
	movb	%al, gdt_dst_hi2
	ret

load_data_inc:
	pushaw
	call	load_data
	popaw
	addw	%ax, (%si)
	adcw	$0, 2(%si)
	ret

10:
	cmpb	$FBS_TYPE_MSDOS, %al
	jnz	10f

	call	find_file
	movw	$(DATA_BUF_SEG >> 5), %bx
	subw	%ax, %bx
	pushw	%ax
	pushw	%ax
	movw	%bx, %ax
	shlw	$9, %ax
	movw	%ax, gdt_dst_low
	movw	%bx, %ax
	shrw	$7, %ax
	movb	%al, gdt_dst_hi1
	popw	%ax
	pushw	%bx
	call	load_data
	call	copy_bs

	popw	%bx
	popw	%ax

	movw	$ABS(iosys_trampoline_start), %si
	movw	$(iosys_trampoline_end - iosys_trampoline_start), %cx
	movw	$0x200, %di
	rep	movsb

	ljmp	$DATA_BUF_SEG, $0x200

10:
	movw	$ABS(err_no_type), %si
	jmp	fail

#define IOSYS_CM_MAGIC		0x4d43

iosys_trampoline_start:
	movw	%es, %cx
	movw	%cx, %ss
	xorw	%sp, %sp

	addw	$4, %bx
	subw	$4, %ax
	shlw	$5, %bx

	movw	%bx, %ds
	pushw	$0x70
	popw	%es

	movw	%ax, %bx

	xorw	%si, %si
	xorw	%di, %di

	pushw	%dx

	cmpw	$IOSYS_CM_MAGIC,(%si)
	jz	iosys_expand

1:
	movw	$256, %cx
	rep	movsw

	call	normalize_address

	decw	%bx
	jnz	1b

iosys_boot:
	popw	%dx
	xorw	%ax, %ax
	xorw	%bx, %bx
	xorw	%bp, %bp
	xorw	%di, %di

	pushw	%cs
	popw	%ds

	movb	$0xf8, %dh
	ljmp	$0x70, $0

iosys_expand:
	pushw	%ds
	lodsw
	pushw	%si

	xorb	%bh, %bh

1:
	lodsb
	movb	%al, %bl
	lodsw
	orw	%ax, %ax
	jz	1f
	addw	%bx, %ax		/* skip the source len field  */
	addw	%bx, %ax
	addw	%ax, %si
	call	normalize_address
	jmp	1b

1:

	orw	%si, %si
	jz	1f
	movw	%ds, %ax
	incw	%ax
	movw	%ax, %ds
1:

	xorw	%si, %si
	lodsw
	cmpw	$IOSYS_CM_MAGIC, %ax
	jnz	iosys_expand_error
	lodsw
	movw	%ax, %cs: (iosys_expand_func - iosys_trampoline_start + 0x200)
	movw	%ds, %cs: (iosys_expand_func - iosys_trampoline_start + 0x200 + 2)

	popw	%si
	popw	%ds

1:
	call	normalize_address
	lodsb
	movb	%al, %bl
	lodsw
	orw	%ax, %ax
	jz	iosys_boot
	orb	%bl, %bl
	jnz	2f

	movw	%ax, %cx		/* uncompressed block  */
	rep	movsb
	jmp	1b

2:
	lodsw				/* dest length  */
	movw	%ax, %cx		/* convert to sector  */
	shrw	$9, %ax
	andw	$0x1ff, %cx
	jz	2f
	incw	%ax
2:

	movw	%ax, %cx
	lodsw				/* 0x5344  */
	lodsw
	lodsw
	xorw	%dx, %dx

	.byte	0x9a			/* lcall  */
iosys_expand_func:
	.word	0, 0
	jc	iosys_expand_error

	decw	%si
	jmp	1b

iosys_expand_error:
	hlt
	jmp	iosys_expand_error

normalize_address:
	movw	%si, %ax
	andw	$0xf, %si
	shrw	$4, %ax
	movw	%ds, %cx
	addw	%cx, %ax
	movw	%ax, %ds

	movw	%di, %ax
	andw	$0xf, %di
	shrw	$4, %ax
	movw	%es, %cx
	addw	%cx, %ax
	movw	%ax, %es
	ret

iosys_trampoline_end:

setup_mbr:
	pushw	%ds
	popw	%es
	movw	$8, %cx
	movw	$(CODE_START + 0x1be), %si
	movw	$(0x800 - 18), %di
	pushw	%di
	rep	movsw
	popw	%si

	movw	orig_es, %es
	movw	orig_di, %di

	xorb	%dh, %dh
	movb	%dl, ABS(bootdrv)
	ret

copy_bs:
	pushaw

	xorw	%di, %di
	movw	$DATA_BUF_SEG, %ax
	movw	%ax, %es
	xorw	%bx, %bx
	movw	$1, %si

	movw	(CODE_START + 0x1c6), %ax
	movw	(CODE_START + 0x1c8), %bp

	pushw	%bp
	pushw	%ax

	call	read_sectors

	movb	(0x7c01), %cl
	xorb	%ch, %ch

	movw	ABS(spt), %ax

	pushw	%ds
	pushw	%es

	popw	%ds
	popw	%es

	popw	(0x1c)		/* Hidden sectors  */
	popw	(0x1e)

	movb	%al, (0x18)
	movb	%ah, (0x1a)

	movw	$2, %si
	movw	$0x7c02, %di

	cld
	rep	movsb

	pushw	%ds
	pushw	%es

	popw	%ds
	popw	%es

	popaw
	ret

#if 0

dump_reg:
	pushw	%cx
	pushaw
	movw	$8, %cx
1:
	call	dump_hex
	loop	1b
	popw	%cx
	ret

/*
 * input:
 *   22(%bp) - len
 *   20(%bp) - seg
 *   18(%bp) - ofs
 */
dump_mem:
	pushaw
	movw	%sp, %bp
	pushw	%ds

	ldsw	18(%bp), %si
1:
	pushw	(%si)
	addw	$2, %si
	call	dump_hex
	decw	22(%bp)
	jnz	1b

	popw	%ds
	popaw
	ret	$6

#endif

menu_file:
	.ascii	FB_MENU_FILE "\0"

err_int15:
	.ascii	"int15\0"

err_no_file:
	.ascii	"no file\0"

err_no_menu:
	.ascii	"no menu\0"

err_no_type:
	.ascii	"no type\0"

loading_message:
	.ascii	"Loading \0"

dot_message:
	.ascii	".\0"

newline:
	.ascii	"\r\n\0"

start_menu:

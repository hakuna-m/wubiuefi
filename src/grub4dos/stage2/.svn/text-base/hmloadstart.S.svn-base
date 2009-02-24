/*
 *  hmloadstart.S -- A DOS utility for loading a file into high memory.
 *  Copyright (C) 2006,2007  Tinybit(tinybit@tom.com)
 *  Copyright (C) 2006,2007  John Cobb (Queen Mary, University of London)
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
   The original source code was written by John Cobb and can be found at:
   http://sysdocs.stu.qmul.ac.uk/sysdocs/Comment/GrubForDOS/code/xmsel.asm

   Transformed to AT&T syntax by Tinybit <tinybit@tom.com>.

   The original copyright notice can be found at:
   http://sysdocs.stu.qmul.ac.uk/sysdocs/Comment/GrubForDOS/code/warranty

and here is an exact copy of the "warranty" file in August 16, 2007:
 
The material is available under the usual free software rules.
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
 *  Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
*/


/*
 * This program is used to generate the hmload.com file.
 *
 * Use the following shell command to generate the file:
 *
 * 	cp hmloadstart hmload.com
 *
 */

/* John Cobb's Note:
 *	It takes two parameters -f filename -a address
 *	Address is in megabytes. It assumes that himem.sys 
 *	or equivalent XMS provider is running.
 */

/* Use the following command to compile and build:
 *
 *	gcc -o hmloadstart.exec -nostdlib -I. -I.. -I../stage1 -Wl,-N -Wl,-s hmloadstart.S
 *
 */

#define ABS(x) (x - _start + 0x100)

#define xmsh	(bss_begin_address + 0)
#define xmsa	(bss_begin_address + 256)
#define xmsl	(bss_begin_address + 256 + 512)
#define buffer	(bss_begin_address + 256 + 512 + 128)
#define thestack	(bss_begin_address + 256 + 512 + 128 + 4096)
#define lastword	(bss_begin_address + 256 + 512 + 128 + 4096 + 4096)
#define xmsh	(bss_begin_address + 0)
#define xmsh	(bss_begin_address + 0)
#define xmsh	(bss_begin_address + 0)

	.text
	.globl	_start
        
_start:

	/* this is real mode dos code */

	.code16

# this code loads a file at a given address using the 32 bit XMS extensions.
# it makes a pretty wild assumption which is that if it
# asks for the biggest XMS memory block that block will contain the
# the address required. (on all machines I tried I got back two
# blocks, one small one and one large one.
# Obviously more sophisticated code could work round  the possibility
# that you space you need straddles more than one block.
# The other assumption is that the data once loaded will stay at the
# same address, which of course it need not. A solution to that might be
# to exit terminate and stay loaded so as to hold onto the resources

//org 100h
//section .text
//start:

	# first cut program size down to that desired
	# (.com prgrams get all of memory to start)

	movw	%cs, %ax
	movw	%ax, %es		# set ES to CS
	movw	$ABS(lastword), %bx	# desired end of program
	movw	%bx, %sp		# set stack pointer
	addw	$15, %bx  # round to nearest page (ok so long as not too big!)
	shrw	$4, %bx			# pages
	movb	$0x4A, %ah
	int	$0x21			# cut program down to size

	xorw	%ax, %ax
	movw	%ax, ABS(hand)		# not ensure handle zero
	movw	%ax, ABS(file)
	movw	%ax, ABS(addr)
	movw	$1, ABS(xmsa20init)
	movw	$ABS(hallo), %dx
	call	chars		# initial part of message about parameters

	xorw	%cx, %cx
	cld
	movb	0x80, %cl
	movw	$0x81, %si
	movw	$ABS(buffer), %di
	repz movsb	# copy the parameter block to a convenient place
	movb	$'$', (%di)
	movw	$ABS(buffer), %dx
	call	msg	# echo the parameters
	movb	0x80, %al
	movw	$ABS(errparam), %dx
	testb	%al, %al
	jnz	startparams
paramerr:
	call	msg
	movw	$ABS(use), %dx
	call	msg
	movw	$ABS(func), %dx
	call	msg
	jmp	exiterr
nohyphen:
	movw	$ABS(needhyphen), %dx
	jmp	paramerr
noparamletter:
	movw	$ABS(misparam), %dx
notparam:
	movb	%ah, ABS(notknown)
	movw	$ABS(notknown), %dx
	jmp	paramerr
novalue:
	movb	%ah, ABS(misvalue+11)
	movw	$ABS(misvalue), %dx
	jmp	paramerr
nofile:
	movw	$ABS(misfile), %dx
	jmp	paramerr
noaddr:
	movw	$ABS(misaddr), %dx
	jmp	paramerr
startparams:
	xorw	%cx, %cx         
	movb	0x80, %cl	# count in cx
	movw	$0x81, %di	# point to start of buffer
	cld
parameters:
	movb	$' ', %al
	repe scasb	    # skip spaces nb pointer and count are left after
	jcxz	endparams   # the character that causes the termination!
	movb	-1(%di), %ah	# pick up the character that caused termination
	cmpb	$'-', %ah
	jne	nohyphen
	jcxz	noparamletter
	movb	(%di), %ah	# the parameter identifier
	incw	%di
	decw	%cx
	jcxz	novalue
	movb	$' ', %al	# skip spaces after the identifier
	repe scasb
	incw	%cx
	decw	%di
	orb	$0x20, %ah	# case insensitive
	cmpb	$'f', %ah
	je	.isfile
	cmpb	$'a', %ah
	je	.isaddr
	jmp	notparam
.isfile:
	movw	%di, ABS(file)
	jmp	.nextp
.isaddr:
	movw	%di, ABS(addr)
.nextp:
	movb	$' ', %al	# look for space
	repne scasb
	cmpb	$' ', -1(%di)	# did we actually find a space?
	jne	.lastp	# if not must have been last and terminated by count
	movb	$0, -1(%di)
	jcxz	endparams
	jmp	parameters
.lastp:
	movb	$0, (%di)
#	check we got everything
endparams:
	movw	ABS(addr), %cx
	jcxz	noaddr
	movw	ABS(file), %cx
	jcxz	nofile
	xorl	%eax, %eax
	movl	$10, %ecx
	movw	ABS(addr), %si	# address of addressvalue
	xorl	%ebx, %ebx
.dec1:
	movb	(%si), %bl
	subb	$'0', %bl
	jl	.dec2
	cmpb	$10, %bl
	jge	.dec2
	mull	%ecx
	addl	%ebx, %eax
	incw	%si
	jmp	.dec1
.dec2:
	shll	$20, %eax	#; shift to megabytes
	movl	%eax, ABS(address)
	movw	ABS(file), %dx
	xorw	%cx, %cx
	movw	$0x3d00, %ax	#; open the file
	int	$0x21
	jnc	opened
	movw	$ABS(erropen), %dx
	movw	ABS(file), %si
	jmp	errstr
opened:
	movw	%ax, ABS(hand)
	movw	$ABS(act1), %dx
	call	chars
	movw	ABS(file), %di
	movb	$0, %al
	movw	$256, %cx
	repne scasb
	movb	$'$', (%di)
	movw	ABS(file), %dx
	call	chars
	movw	$ABS(act2), %dx
	call	chars
	movw	$ABS(address+3), %si
	call	hexl
	call	eol
#		see if we have xms available
	movw	$0, ABS(xmsfull)
	movw	$0x4300, %ax
	int	$0x2F
	cmpb	$0x80, %al
	je	.xmsok
	movw	$ABS(noxmsmsg), %dx
	call	msg
	jmp	exiterr
.xmsok:
	movw	$0x4310, %ax
	pushw	%es
	pushw	%ds
	int	$0x2F
	popw	%ds
	movw	%es, ABS(xmsptr+2)
	movw	%bx, ABS(xmsptr)
	popw	%es
	movw	$ABS(xmsProc), %dx
	call	chars
	movw	$ABS(xmsptr+3), %si
	call	hexl
	call	eol
#		xms version etc
	movb	$0, %ah
	call	xms
	movw	%ax, ABS(num)
	movw	%bx, ABS(num+2)
	pushw	%dx
	movw	$ABS(xmsver), %dx
	call	chars
	movw	$ABS(num+1), %si
	call	hexw
	movw	$ABS(xmsrev), %dx
	call	chars
	movw	$ABS(num+3), %si
	call	hexw
	popw	%cx	# value that was in dx after the xms call
	movw	$ABS(xmsHMAno), %dx
	jcxz	.next
	movw	$ABS(xmsHMAyes), %dx
.next:
	call	msg
	call	checka20	# check status of the a20 line
	jnc	.ok
	jmp	exiterr
.ok:
	movw	%ax, ABS(xmsa20init)	# save initial status of line
#		a20 not needed in this version
#	call	xmsenable	# locally enable a20
#	jnc	.gota20
#	jmp	xmserr
#.gota20:
#
#	aquire xms memory blocks 
# i am going to assume that most of xms is available as one large block
# and that will encompass the desired adress obviously I should do a sanity
# check but for now lets just stick straws in the hair
# extended xms spec found at
# http://freedos.sourceforge.net/freedos/news/press/1991-xms30.html
#	aquire all full sized xms memory blocks available
	movw	$0, ABS(nxmsh)	# zero count
.getxms:
	movb	$0x88, %ah
	call	xms		# query largest xms block size
	testb	%bl, %bl
	jz	.gotms		# success if BL zero
	movw	$ABS(xmsnomem), %dx
	call	msg
	jmp	.donemem
.gotms:
	movl	%eax, ABS(num)	# save block size
	movw	$ABS(xmslargest), %dx
	call	chars
	movw	$ABS(num+3), %si
	call	hexl
	movw	$ABS(inkbmsg), %dx
	call	chars
#	movw	ABS(num), %dx
#	xorw	ABS(fullxmsblock), %dx
#	jnz	.donemem
	movl	ABS(num), %edx
	movb	$0x89, %ah
	call	xms			# grab the block
	testw	%ax, %ax
	jz	.donemem
	movw	ABS(nxmsh), %si		# current handle index
	movb	$0, ABS(xmsl)(%si)	# zero the lock indicator
	shlw	$1, %si
	movw	%dx, ABS(xmsh)(%si)	# store handle
	pushw	%dx
	movw	$ABS(xmsgotblock), %dx
	call	chars
	popw	%dx
	movb	$0x0C, %ah
	call	xms
	testw	%ax, %ax
	jz	.incind
	movw	ABS(nxmsh), %si		# current handle index
	movb	$1, ABS(xmsl)(%si)	# set the lock indicator
	shlw	$2, %si
	movw	%bx, ABS(xmsa)(%si)
	movw	%dx, ABS(xmsa+2)(%si)
	pushw	%si
	movw	$ABS(xmslockedblock), %dx
	call	chars
	popw	%si
	addw	$ABS(xmsa+3), %si
	call	hexl
#	movw	$4, %cx
#	call	hexstr
.incind:
	call	eol
	movw	ABS(nxmsh), %si		# current handle index
	incw	%si
	movw	%si, ABS(nxmsh)
	jmp	.getxms
.donemem:
	call	eol
	movw	$ABS(xmsblocksgot), %dx
	call	chars
	movw	$ABS(nxmsh+1), %si
	call	hexw
	call	eol

#	start the load
	movl	ABS(address), %eax
	subl	ABS(xmsa), %eax	# make relative to the first xms segment
copyin:
	pushl	%eax
	movb	$0x3f, %ah	#; read file
	movw	ABS(hand), %bx
	movw	$4096, %cx
	movw	$ABS(buffer), %dx
	int	$0x21
	jc	eof
	testw	%ax, %ax
	jz	eof
	movw	$ABS(buffer), %bx

#	setup the xms move structure
	movzwl	%ax, %eax
	movl	%eax, ABS(xmsmvlen)
	movw	$0, ABS(xmsmvshand)
	movw	%bx, ABS(xmsmvsoff)
	movw	%ds, ABS(xmsmvsseg)
	popl	%eax
	movl	%eax, ABS(xmsmvdoff)
	addl	ABS(xmsmvlen), %eax
	movw	ABS(xmsh), %dx
	movw	%dx, ABS(xmsmvdhand)
	movw	$ABS(xmsmove), %si
	pushl	%eax
	movb	$0x0B, %ah
	call	xms
	popl	%eax
	jmp	copyin
eof:
	popl	%eax
	movw	$ABS(done), %dx
	call	msg
#	for now release the xms again
#	nb this is questionable as we don't want it to move but...
.relxms:
	movw	ABS(nxmsh), %si		# index of last handle
	testw	%si, %si
	jz	.xmsfreed
	decw	%si
	movw	%si, ABS(nxmsh)		# decrement for next time
	movb	ABS(xmsl)(%si), %ah	# check lock status
	testb	%ah, %ah
	jz	.nolock
	shlw	$1, %si
	movw	ABS(xmsh)(%si), %dx
	movb	$0x0D, %ah
	call	xms			# unlock block
.nolock:
	movw	ABS(nxmsh), %si		# index of last handle
	shlw	$1, %si
	movw	ABS(xmsh)(%si), %dx
	movb	$0x0A, %ah
	call	xms			# free block
	jmp	.relxms
.xmsfreed:
	movw	ABS(xmsa20init), %ax
	testw	%ax, %ax
	jnz	.wason
#	call	xmsdisable		# locally disable xms
#	jnc	.losta20
#	jmp	exiterr
#.losta20:
.wason:		# or possibly we never got it in the first place
	movw	ABS(hand), %bx
	movb	$0x3E, %ah		# close file
	int	$0x21
	movw	$0x4C00, %ax		# return success
	int	$0x21
exit:
	movw	$0x4C00, %ax		# exit with 0 result code
	int	$0x21
errstr:
	pushw	%si
	call	chars
	popw	%si
	movw	$256, %cx
	movw	$ABS(buffer), %di
	cld
.str1:
	lodsb
	testb	%al, %al
	jz	.str2
	stosb
	loop	.str1
.str2:
	movb	$'$', (%di)
	movw	$ABS(buffer), %dx
err:
	call	msg
exiterr:
	movw	ABS(hand), %bx
	testw	%bx, %bx
	jz	.nofile
	movb	$0x3e, %ah	# close file
	int	$0x21
.nofile:
	movw	$0x4c01, %ax	# return failure
	int	$0x21
msg:
	movb	$0x09, %ah
	int	$0x21
eol:
	movw	$ABS(eolmsg), %dx
	movb	$0x09, %ah
	int	$0x21
	ret
chars:
	movb	$0x09, %ah
	int	$0x21
	ret
hexstr:
	cld
	jmp	hexout
hexl:
	movw	$4, %cx
	jmp	hexnum
hexw:
	movw	$2, %cx
	jmp	hexnum
hexb:
	movw	$1, %cx
hexnum:
	std
hexout:
	# expect si pointing at string or at most sig byte of num
	movw	$ABS(hex), %bx
	lodsb
	movb	%al, %ah
	shrb	$4, %al
	# andb	$0x0F, %al
	xlat
	movb	%al, ABS(tbuff+1)
	pushw	%cx
	pushw	%si
	movw	$ABS(tbuff), %dx
	movb	$0x09, %ah
	int	$0x21
	popw	%si
	popw	%cx
	loop	hexout
	ret

checka20:
	# check status of a20 line
	movb	$7, %ah
	call	xms
	testb	%bl, %bl
	jnz	.noa20
	movw	$ABS(xmsa20off), %dx
	pushw	%ax
	testw	%ax, %ax
	jz	.next1
	movw	$ABS(xmsa20on), %dx
.next1:
	call	msg
	movb	$0, %bl
	popw	%ax
	clc
	ret
.noa20:
	pushw	%bx
	movw	$ABS(xmsnoa20), %dx
	call	chars
	popw	%bx
	pushw	%bx
	call	xmserr
	popw	%bx
	stc
	ret

xmserr:
	movb	%bl, ABS(num)
	movw	$ABS(xmserrcode), %dx
	call	chars
	movw	$ABS(num), %si
	call	hexb
	call	eol
	ret
xms:
	pushw	%ds
	lcall	*ABS(xmsptr)
	popw	%ds
	ret

xmsenable:
	movb	$5, %ah
	call	xms
	testw	%ax, %ax
	jnz	.gota
	movw	$ABS(xmslocenfai), %dx
	pushw	%bx
	call	chars
	popw	%bx
	call	xmserr
	stc
	ret
.gota:
	movw	$ABS(xmslocenable), %dx
	call	msg
	call	checka20
	clc
	ret

xmsdisable:
	movb	$6, %ah
	call	xms
	testw	%ax, %ax
	jnz	.losta
	movw	$ABS(xmslocdisfai), %dx
	pushw	%bx
	call	chars
	popw	%bx
	call	xmserr
	stc
	ret
.losta:
	movw	$ABS(xmslocdisable), %dx
	call	msg
	clc
	ret

//section .data

hallo:
	.ascii	"Parameters: $"
//; file: db 'C:\temp\mdump',0
erropen:
	.ascii	"Could not open file: $"
errparam:
	.ascii	"No Parameters!$"
use:
	.ascii	" Use: -f filename -a address (in megabytes)$"
func:
	.ascii	"Loads file to address$"
needhyphen:
	.ascii	" parameters must start with -$"
notknown:
	.ascii	"x is not a recognised parameter$"
misparam:
	.ascii	"Parameter type missing after -$"
misvalue:
	.ascii	"Parameter -x has no value!$"
misfile:
	.ascii	"-f (filename) parameter missing$"
misaddr:
	.ascii	"Address parameter missing$"
act1:
	.ascii	"Loading file: $"
act2:
	.ascii	" to 0x$"
done:
	.ascii	"file loaded$"

	.align	2
file:
	.word	0
addr:
	.word	0
hand:
	.word	0
eolmsg:
	.ascii	"\r\n$"
inkbmsg:
	.ascii	" KB,$"
xmsnomem:
	.ascii	"No free XMS memory$"
xmslargest:
	.ascii	"Largest XMS block 0x$"
xmsgotblock:
	.ascii	" aquired,$"
xmslockedblock:
	.ascii	" locked at 0x$"
xmsblocksgot:
	.ascii	"number of full sized XMS blocks 0x$"
noxmsmsg:
	.ascii	"XMS interface not available$"
xmsnohmsg:
	.ascii	"XMS get handle failed$"
xmsfree:
	.ascii	"Free XMS$"
xmslarge:
	.ascii	"largest XMS$"
xmsstat:
	.ascii	"XMS Status$"
xmsnoa20:
	.ascii	"couldn't read a20 state$"
xmserrcode:
	.ascii	" err=0x$"
xmsa20off:
	.ascii	"A20 line off$"
xmsa20on:
	.ascii	"A20 line on$"
xmsver:
	.ascii	"XMS Version 0x$"
xmsrev:
	.ascii	" XMS Revision 0x$"
xmsHMAyes:
	.ascii	" HMA Exists$"
xmsHMAno:
	.ascii	" No HMA$"
xmsProc:
	.ascii	"XMS procedure address 0x$"
hex:
	.ascii	"0123456789ABCDEF"      # String of hex numbers
tbuff:
	.ascii	"xx$"

	.align	2
xmsa20init:
	.word	0
xmslocenfai:
	.ascii	"Failed local enable of A20$"
xmslocdisfai:
	.ascii	"Failed local disable of A20$"
xmslocenable:
	.ascii	"A 20 locally enabled$"
xmslocdisable:
	.ascii	"A 20 locally disabled$"
dump:
	.byte	0,1,2,3


//section .bss

	.align	4
num:
	.byte	0,0,0,0
xmsptr:
	.word	0,0
xmsnext:
	.word	0
xmsfull:
	.word	0
address:
	.long	0

xmsmove:	# structure
xmsmvlen:
	.long	0
xmsmvshand:
	.word	0
xmsmvsoff:	# note if shand non zero then 32 bit ofsset and no seg
	.word	0
xmsmvsseg:
	.word	0
xmsmvdhand:
	.word	0
xmsmvdoff:
	.word	0
xmsmvdseg:
	.word	0
# end of xms move structure

nxmsh:
	.word	0


	.align	16
bss_begin_address:

/*
xmsh:
	.space	256
xmsa:
	.space	512
xmsl:
	.space	128
buffer:
	.space	4096
thestack:
	.space	4096
lastword:
	.word	0
*/


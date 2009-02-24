;
;  GRUB Utilities --  Utilities for GRUB Legacy, GRUB2 and GRUB for DOS
;  Copyright (C) 2007 Bean (bean123ch@gmail.com)
;
;  This program is free software: you can redistribute it and/or modify
;  it under the terms of the GNU Affero General Public License as
;  published by the Free Software Foundation, either version 3 of the
;  License, or (at your option) any later version.
;
;  This program is distributed in the hope that it will be useful,
;  but WITHOUT ANY WARRANTY; without even the implied warranty of
;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;  GNU Affero General Public License for more details.
;
;  You should have received a copy of the GNU Affero General Public License
;  along with this program.  If not, see <http://www.gnu.org/licenses/>.
;

.386
locals

xd_t struc
	flg	dw 0
	num	dw 0
	ofs	dd 0
	prm	dw 0
xd_t ends

global _xd16_init:near
global _xd16_read:near
global _xd16_write:near

_TEXT segment byte use16 public 'CODE'
assume cs:_TEXT

; void xd16_init(xd_t*);
_xd16_init proc near
	push	bp
	mov	bp, sp
	mov	bx, [bp+4]
	mov	dl, byte ptr [bx].num
	mov	ah, 41h
	mov	bx, 55aah
	int	13h
	jc	short @@chs
	cmp	bx, 0aa55h
	jnz	short @@chs
	test	cx, 1
	jz	short @@chs
@@lba:
	mov	[bx].prm, 0
@@quit:
	pop	bp
	ret
@@chs:
	mov	ah, 8
	mov	bx, [bp+4]
	mov	dl, byte ptr [bx].num
	push	es
	push	di
	push	si
	push	bx
	int	13h
	pop	bx
	pop	si
	pop	di
	pop	es
	jc	@@lba
	mov	al, cl
	and	al, 3Fh
	mov	byte ptr [bx].prm, al
	inc	dh
	mov	byte ptr [bx+1].prm, dh
	jmp	@@quit
_xd16_init endp

; xd16_read(xd_t*,char*,int);
_xd16_read proc near
	mov	dh,0
	jmp	short _xd16_rdwr
_xd16_read endp

_xd16_write proc near
	mov	dh,1
_xd16_write endp

_xd16_rdwr proc near
	push	bp
	mov	bp, sp
	push	si
	mov	bx, [bp+4]
	mov	dl, byte ptr [bx].num
	cmp	[bx].prm, 0
	jnz	short @@chs
	xor	eax, eax
	push	eax
	push	[bx].ofs
	push	ds
	push	word ptr [bp+6]
	push	word ptr [bp+8]
	push	10h
	mov	si, sp
	mov	ah, dh
	add	ah, 42h
	int	13h
	jc	short @@fail
	mov	ax, [si+2]
	cmp	[bp+8], ax
	jnz	short @@fail
@@done:
	add	word ptr [bx].ofs, ax
	adc	word ptr [bx+2].ofs, 0
	xor	ax, ax
@@quit:
	mov	si, [bp-2]
	leave
	ret
@@fail:
	mov	ax, 1
	jmp	@@quit
@@chs:
	mov	cx, [bp+8]

@@back:
	push	cx
	push	dx

	push	dx
	mov	ax, [bx].prm
	mul	ah
	mov	cx, ax
	mov	ax, word ptr [bx].ofs
	mov	dx, word ptr [bx+2].ofs
	div	cx
	cmp	ax, 1024
	jae	@@fail
	xchg	dx, ax
	div	byte ptr [bx].prm
	inc	ah
	mov	ch, dl
	mov	cl, dh
	shl	cl, 6
	or	cl, ah
	pop	dx
	mov	ah, dh
	add	ah, 2
	mov	dh, al
	mov	al, 1
	mov	bx, [bp+6]
	push	es
	push	ds
	pop	es
	int	13h
	pop	es
	jc	short @@fail

	add	word ptr [bp+6], 200h
	mov	bx, [bp+4]
	add	word ptr [bx].ofs, 1
	adc	word ptr [bx+2].ofs, 0

	pop	dx
	pop	cx
	loop	@@back

	xor	ax, ax
	jmp	@@quit
_xd16_rdwr endp

_TEXT ends

end

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

#ifndef __XDIO_H
#define __XDIO_H

#if defined(__cplusplus) || defined(c_plusplus)
extern "C" {
#endif

#ifdef DOS
#include <io.h>
#endif

#define MAX_DISKS		20
#define MAX_PARTS		30

#define XDF_FILE		1
#define XDF_DISK		2

#define XD_INVALID_SIZE		0xffffffff

#if (! defined(WIN32)) && (! defined(DOS))

#define O_BINARY		0

#endif

typedef struct {
  int flg;
  int num;
  unsigned long ofs;
#ifdef DOS
  unsigned short prm;
#endif
} xd_t;

typedef struct {
  unsigned char	cur;		// Current partition number
  unsigned char	nxt;		// Next partition number
  unsigned char	dfs;		// File system flag
  unsigned char	pad;		// Padding
  unsigned long	bse;		// Partition start address
  unsigned long len;		// Partition length
  unsigned long ebs;		// Base address for the extended partition
} xde_t;

#define valueat(buf,ofs,type)	*((type *) (((char*) &buf) + ofs))

#ifdef DOS
void xd16_init (xd_t*);
int xd16_read (xd_t*, char*, int);
int xd16_write (xd_t*, char*, int);
#endif

xd_t* xd_open (char*, int);
int xd_seek (xd_t*, unsigned long);
int xd_enum (xd_t*, xde_t*);
int xd_read (xd_t*, char*, int);
int xd_write (xd_t*, char*, int);
void xd_close (xd_t*);
unsigned long xd_size (xd_t* xd);

#if defined(__cplusplus) || defined(c_plusplus)
}
#endif
#endif /* __XDIO_H */

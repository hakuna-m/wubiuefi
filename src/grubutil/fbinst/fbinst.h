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

#ifndef __FBINST_H
#define __FBINST_H

#define FB_MAGIC		"FBBF"
#define FB_MAGIC_LONG		0x46424246
#define FB_MAGIC_WORD		(FB_MAGIC_LONG & 0xffff)


#define FB_AR_MAGIC		"FBAR"
#define FB_AR_MAGIC_LONG	0x52414246
#define FB_AR_MAGIC_WORD	(FB_AR_MAGIC_LONG & 0xffff)
#define FB_AR_MAX_SIZE		0x7fffffff

#define FB_MENU_FILE		"fb.cfg"

#define FBM_TYPE_FILE		1
#define FBM_TYPE_MENU		2
#define FBM_TYPE_TEXT		3
#define FBM_TYPE_TIMEOUT	4
#define FBM_TYPE_DEFAULT	5
#define FBM_TYPE_COLOR		6

#define FBS_TYPE_MENU		1
#define FBS_TYPE_GRLDR		2
#define FBS_TYPE_SYSLINUX	3
#define FBS_TYPE_LINUX		4
#define FBS_TYPE_MSDOS		5

#define FBF_FLAG_EXTENDED	1
#define FBF_FLAG_SYSLINUX	2

#define OFS_max_sec		0x1ab
#define OFS_lba			0x1ac
#define OFS_bootdrv		0x1ad
#define OFS_spt			0x1ae
#define OFS_heads		0x1af
#define OFS_boot_base		0x1b0
#define OFS_boot_size		0x1b2
#define OFS_fb_magic		0x1b4
#define OFS_mbr_table		0x1b8

#define OFS_menu_ofs		0x200
#define OFS_flags		0x202
#define OFS_ver_major		0x204
#define OFS_ver_minor		0x205
#define OFS_pri_size		0x206
#define OFS_ext_size		0x20a

#define COLOR_NORMAL		7

#endif /* __FBINST_H */

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

#ifndef __UTILS_H
#define __UTILS_H

#if defined(__cplusplus) || defined(c_plusplus)
extern "C" {
#endif

#define FST_OTHER		0
#define FST_MBR			1
#define FST_MBR2		2
#define FST_FAT16		3
#define FST_FAT32		4
#define FST_NTFS		5
#define FST_EXT2		6

extern int mbr_nhd, mbr_spt;
int get_fstype (unsigned char*);
char* fst2str (int);
char* dfs2str (int);

#if defined(__cplusplus) || defined(c_plusplus)
}
#endif
#endif /* __UTILS_H */

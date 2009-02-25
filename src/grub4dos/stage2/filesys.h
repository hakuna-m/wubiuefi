/* filesys.h - abstract filesystem interface */
/*
 *  GRUB  --  GRand Unified Bootloader
 *  Copyright (C) 1999,2000,2001,2004  Free Software Foundation, Inc.
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

#include "pc_slice.h"

#ifdef FSYS_FFS
#define FSYS_FFS_NUM 1
int ffs_mount (void);
unsigned long ffs_read (char *buf, unsigned long len);
int ffs_dir (char *dirname);
unsigned long ffs_embed (unsigned long *start_sector, unsigned long needed_sectors);
#else
#define FSYS_FFS_NUM 0
#endif

#ifdef FSYS_UFS2
#define FSYS_UFS2_NUM 1
int ufs2_mount (void);
unsigned long ufs2_read (char *buf, unsigned long len);
int ufs2_dir (char *dirname);
unsigned long ufs2_embed (unsigned long *start_sector, unsigned long needed_sectors);
#else
#define FSYS_UFS2_NUM 0
#endif

#ifdef FSYS_FAT
#define FSYS_FAT_NUM 1
int fat_mount (void);
unsigned long fat_read (char *buf, unsigned long len);
int fat_dir (char *dirname);
#else
#define FSYS_FAT_NUM 0
#endif

#ifdef FSYS_NTFS
#define FSYS_NTFS_NUM 1
int ntfs_mount (void);
unsigned long ntfs_read (char *buf, unsigned long len);
int ntfs_dir (char *dirname);
#else
#define FSYS_NTFS_NUM 0
#endif

#ifdef FSYS_EXT2FS
#define FSYS_EXT2FS_NUM 1
int ext2fs_mount (void);
unsigned long ext2fs_read (char *buf, unsigned long len);
int ext2fs_dir (char *dirname);
#else
#define FSYS_EXT2FS_NUM 0
#endif

#ifdef FSYS_MINIX
#define FSYS_MINIX_NUM 1
int minix_mount (void);
unsigned long minix_read (char *buf, unsigned long len);
int minix_dir (char *dirname);
#else
#define FSYS_MINIX_NUM 0
#endif

#ifdef FSYS_REISERFS
#define FSYS_REISERFS_NUM 1
int reiserfs_mount (void);
unsigned long reiserfs_read (char *buf, unsigned long len);
int reiserfs_dir (char *dirname);
unsigned long reiserfs_embed (unsigned long *start_sector, unsigned long needed_sectors);
#else
#define FSYS_REISERFS_NUM 0
#endif

#ifdef FSYS_VSTAFS
#define FSYS_VSTAFS_NUM 1
int vstafs_mount (void);
unsigned long vstafs_read (char *buf, unsigned long len);
int vstafs_dir (char *dirname);
#else
#define FSYS_VSTAFS_NUM 0
#endif

#ifdef FSYS_JFS
#define FSYS_JFS_NUM 1
int jfs_mount (void);
unsigned long jfs_read (char *buf, unsigned long len);
int jfs_dir (char *dirname);
unsigned long jfs_embed (unsigned long *start_sector, unsigned long needed_sectors);
#else
#define FSYS_JFS_NUM 0
#endif

#ifdef FSYS_XFS
#define FSYS_XFS_NUM 1
int xfs_mount (void);
unsigned long xfs_read (char *buf, unsigned long len);
int xfs_dir (char *dirname);
#else
#define FSYS_XFS_NUM 0
#endif

#ifdef FSYS_TFTP
#define FSYS_TFTP_NUM 1
int tftp_mount (void);
unsigned long tftp_read (char *buf, unsigned long len);
int tftp_dir (char *dirname);
void tftp_close (void);
#else
#define FSYS_TFTP_NUM 0
#endif

#ifdef FSYS_ISO9660
#define FSYS_ISO9660_NUM 1
int iso9660_mount (void);
unsigned long iso9660_read (char *buf, unsigned long len);
int iso9660_dir (char *dirname);
#else
#define FSYS_ISO9660_NUM 0
#endif

#ifdef FSYS_PXE
#define FSYS_PXE_NUM 1
int pxe_mount (void);
unsigned long pxe_read (char *buf, unsigned long len);
int pxe_dir (char *dirname);
void pxe_close (void);
#else
#define FSYS_PXE_NUM 0
#endif

#ifndef NUM_FSYS
#define NUM_FSYS	\
  (FSYS_FFS_NUM + FSYS_FAT_NUM + FSYS_NTFS_NUM + FSYS_EXT2FS_NUM + FSYS_MINIX_NUM	\
   + FSYS_REISERFS_NUM + FSYS_VSTAFS_NUM + FSYS_JFS_NUM + FSYS_XFS_NUM	\
   + FSYS_TFTP_NUM + FSYS_ISO9660_NUM + FSYS_UFS2_NUM + FSYS_PXE_NUM)
#endif

/* defines for the block filesystem info area */
#ifndef NO_BLOCK_FILES
#define BLK_CUR_FILEPOS      (*((unsigned long*)FSYS_BUF))
#define BLK_CUR_BLKLIST      (*((unsigned long*)(FSYS_BUF+4)))
#define BLK_CUR_BLKNUM       (*((unsigned long*)(FSYS_BUF+8)))
#define BLK_MAX_ADDR         (FSYS_BUF+0x77F9)
#define BLK_BLKSTART(l)      (*((unsigned long*)l))
#define BLK_BLKLENGTH(l)     (*((unsigned long*)(l+4)))
#define BLK_BLKLIST_START    (FSYS_BUF+12)
#define BLK_BLKLIST_INC_VAL  8
#endif /* NO_BLOCK_FILES */

/* this next part is pretty ugly, but it keeps it in one place! */

struct fsys_entry
{
  char *name;
  int (*mount_func) (void);
  unsigned long (*read_func) (char *buf, unsigned long len);
  int (*dir_func) (char *dirname);
  void (*close_func) (void);
  unsigned long (*embed_func) (unsigned long *start_sector, unsigned long needed_sectors);
};

#ifdef STAGE1_5
# define print_possibilities 0
#else
extern int print_possibilities;
#endif

extern unsigned long fsmax;
extern struct fsys_entry fsys_table[NUM_FSYS + 1];

/* disk_io.c - implement abstract BIOS disk input and output */
/*
 *  GRUB  --  GRand Unified Bootloader
 *  Copyright (C) 1999,2000,2001,2002,2003,2004  Free Software Foundation, Inc.
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


#include <shared.h>
#include <filesys.h>
#include <iso9660.h>

#ifdef SUPPORT_NETBOOT
# define GRUB	1
# include <etherboot.h>
#endif

#ifdef GRUB_UTIL
# include <device.h>
#endif

/* instrumentation variables */
void (*disk_read_hook) (unsigned long, unsigned long, unsigned long) = NULL;
void (*disk_read_func) (unsigned long, unsigned long, unsigned long) = NULL;

/* Forward declarations.  */
static int next_bsd_partition (void);
static int next_pc_slice (void);
static char open_filename[512];
static unsigned long relative_path;

#ifndef STAGE1_5
int print_possibilities;

static int unique;
static char *unique_string;
static unsigned long cur_part_offset;
static unsigned long cur_part_addr;
static int do_completion;

int dir (char *dirname);
static int sane_partition (void);

/* XX used for device completion in 'set_device' and 'print_completions' */
static int incomplete, disk_choice;
static enum
{
  PART_UNSPECIFIED = 0,
  PART_DISK,
  PART_CHOSEN,
}
part_choice;
#endif /* ! STAGE1_5 */


unsigned long i;

#if !defined(STAGE1_5) && !defined(GRUB_UTIL)
/* The first sector of stage2 can be reused as a tmp buffer.
 * Do NOT write more than 512 bytes to this buffer!
 * The stage2-body, i.e., the pre_stage2, starts at 0x8200!
 * Do NOT overwrite the pre_stage2 code at 0x8200!
 */
char *mbr = (char *)0x8000; /* 512-byte buffer for any use. */
#else
char mbr[SECTOR_SIZE];
#endif

unsigned long next_partition_drive;
unsigned long next_partition_dest;
unsigned long *next_partition_partition;
unsigned long *next_partition_type;
unsigned long *next_partition_start;
unsigned long *next_partition_len;
unsigned long *next_partition_offset;
unsigned long *next_partition_entry;
unsigned long *next_partition_ext_offset;
char *next_partition_buf;

static unsigned long dest_partition;
static unsigned long part_offset;
static unsigned long entry;
static unsigned long ext_offset;

static unsigned long bsd_part_no;
static unsigned long pc_slice_no;

unsigned long fsmax;
struct fsys_entry fsys_table[NUM_FSYS + 1] =
{
  /* TFTP should come first because others don't handle net device.  */
# ifdef FSYS_PXE
  {"pxe", pxe_mount, pxe_read, pxe_dir, pxe_close, 0},
# endif
# ifdef FSYS_TFTP
  {"tftp", tftp_mount, tftp_read, tftp_dir, tftp_close, 0},
# endif
# ifdef FSYS_EXT2FS
  {"ext2fs", ext2fs_mount, ext2fs_read, ext2fs_dir, 0, 0},
# endif
# ifdef FSYS_FAT
  {"fat", fat_mount, fat_read, fat_dir, 0, 0},
# endif
# ifdef FSYS_NTFS
  {"ntfs", ntfs_mount, ntfs_read, ntfs_dir, 0, 0},
# endif
# ifdef FSYS_MINIX
  {"minix", minix_mount, minix_read, minix_dir, 0, 0},
# endif
# ifdef FSYS_REISERFS
  {"reiserfs", reiserfs_mount, reiserfs_read, reiserfs_dir, 0, reiserfs_embed},
# endif
# ifdef FSYS_VSTAFS
  {"vstafs", vstafs_mount, vstafs_read, vstafs_dir, 0, 0},
# endif
# ifdef FSYS_JFS
  {"jfs", jfs_mount, jfs_read, jfs_dir, 0, jfs_embed},
# endif
# ifdef FSYS_XFS
  {"xfs", xfs_mount, xfs_read, xfs_dir, 0, 0},
# endif
# ifdef FSYS_UFS2
  {"ufs2", ufs2_mount, ufs2_read, ufs2_dir, 0, ufs2_embed},
# endif
# ifdef FSYS_ISO9660
  {"iso9660", iso9660_mount, iso9660_read, iso9660_dir, 0, 0},
# endif
  /* XX FFS should come last as it's superblock is commonly crossing tracks
     on floppies from track 1 to 2, while others only use 1.  */
# ifdef FSYS_FFS
  {"ffs", ffs_mount, ffs_read, ffs_dir, 0, ffs_embed},
# endif
  {0, 0, 0, 0, 0, 0}
};


/* These have the same format as "boot_drive" and "install_partition", but
   are meant to be working values. */
unsigned long current_drive = GRUB_INVALID_DRIVE;
unsigned long current_partition;

#ifndef STAGE1_5
/* The register ESI should contain the address of the partition to be
   used for loading a chain-loader when chain-loading the loader.  */
unsigned long boot_part_addr = 0;
#endif

/*
 *  Global variables describing details of the filesystem
 */

/* FIXME: BSD evil hack */
#include "freebsd.h"
int bsd_evil_hack;

/* filesystem type */
int fsys_type = NUM_FSYS;

/* these are the translated numbers for the open partition */
unsigned long part_start;
unsigned long part_length;

unsigned long current_slice;

/* disk buffer parameters */

int buf_drive = -1;
int buf_track = -1;

struct geometry buf_geom;
struct geometry tmp_geom;	/* tmp variable used in many functions. */
struct geometry fd_geom[4];
struct geometry hd_geom[4];

int rawread_ignore_memmove_overflow = 0;/* blocklist_func() set this to 1 */

/* filesystem common variables */
unsigned long filepos;
unsigned long filemax;

unsigned long emu_iso_sector_size_2048 = 0;

inline unsigned long
log2_tmp (unsigned long word)
{
  asm volatile ("bsfl %1,%0"
		: "=r" (word)
		: "r" (word));
  return word;
}

/* Convert unicode filename to UTF-8 filename. N is the max characters to be
 * converted. The caller should asure there is enough room in the UTF8 buffer.
 *
 */
void
unicode_to_utf8 (unsigned short *filename, unsigned char *utf8, unsigned long n)
{
	unsigned short uni;
	unsigned long j, k;

	for (j = 0, k = 0; j < n && (uni = filename[j]); j++)
	{
		if (uni <= 0x007F)
		{
			if (uni != ' ')
				utf8[k++] = uni;
			else
			{
				/* quote the SPACE with a backslash */
				utf8[k++] = '\\';
				utf8[k++] = uni;
			}
		}
		else if (uni <= 0x07FF)
		{
			utf8[k++] = 0xC0 | (uni >> 6);
			utf8[k++] = 0x80 | (uni & 0x003F);
		}
		else
		{
			utf8[k++] = 0xE0 | (uni >> 12);
			utf8[k++] = 0x80 | ((uni >> 6) & 0x003F);
			utf8[k++] = 0x80 | (uni & 0x003F);
		}
	}
	utf8[k] = 0;
}

/* Read bytes from DRIVE to BUF.
 *
 * The bytes start at BYTE_OFFSET in absolute sector number SECTOR and with
 * BYTE_LEN bytes long.
 *
 */
int
rawread (unsigned long drive, unsigned long sector, unsigned long byte_offset, unsigned long byte_len, char *buf)
{
  unsigned long slen, sectors_per_vtrack;
  unsigned long sector_size_bits = log2_tmp (buf_geom.sector_size);

//  if (byte_len == 0)
//    return 1;

  errnum = 0;

  while (byte_len > 0)
    {
      unsigned long soff, num_sect, track, size = byte_len;
      char *bufaddr;

      /*
       *  Check track buffer.  If it isn't valid or it is from the
       *  wrong disk, then reset the disk geometry.
       */
      if (buf_drive != drive)
	{
	  if (get_diskinfo (drive, &buf_geom))
	    {
	      errnum = ERR_NO_DISK;
	      return 0;
	    }
	  buf_drive = drive;
	  buf_track = -1;
	  sector_size_bits = log2_tmp (buf_geom.sector_size);
	}

#if 0
      /* Make sure that SECTOR is valid.  */
      if (/* sector < 0 || */ sector >= buf_geom.total_sectors)
	{
	  errnum = ERR_GEOM;	/* Selected cylinder exceeds maximum supported by BIOS. This message is not proper. */
	  return 0;
	}
#endif

      /* Sectors that need to read */
      slen = ((byte_offset + byte_len + buf_geom.sector_size - 1) >> sector_size_bits);

      /* Eliminate a buffer overflow.  */
      if ((buf_geom.sectors << sector_size_bits) > BUFFERLEN)
	sectors_per_vtrack = (BUFFERLEN >> sector_size_bits);
      else
	sectors_per_vtrack = buf_geom.sectors;

      /* Get the first sector number in the track.  */
      soff = sector % sectors_per_vtrack;

      /* Get the starting sector number of the track. */
      track = sector - soff;

      /* max number of sectors to read in the track. */
      num_sect = sectors_per_vtrack - soff;

      /* Read data into the track buffer; Not all sectors in the track would be filled in. */
      bufaddr = ((char *) BUFFERADDR + (soff << sector_size_bits) + byte_offset);

      if (track != buf_track)
	{
	  unsigned long bios_err;
	  unsigned long read_start = track;
	  unsigned long read_len = sectors_per_vtrack;

	  buf_track = track;

	  /*
	   *  If there's more than one read in this entire loop, then
	   *  only make the earlier reads for the portion needed.  This
	   *  saves filling the buffer with data that won't be used!
	   */
	  if (slen > num_sect)
	    {
	      buf_track = -1;	/* invalidate the buffer */
	      read_start = sector;
	      read_len = num_sect;
	      bufaddr = (char *) BUFFERADDR + byte_offset;
	    }

	  bios_err = biosdisk (BIOSDISK_READ, drive, &buf_geom, read_start, read_len, BUFFERSEG);
	  if (bios_err)
	    {
	      buf_track = -1;	/* invalidate the buffer */

//	      if (bios_err == BIOSDISK_ERROR_GEOMETRY)
//	      {
//		errnum = ERR_GEOM;
//		return 0;
//	      }
//	      else
		{
		  /* Do not try again to read sectors near a bad track.
		   * Reading these sectors may slow down the system.
		   * This can also remind us potential problems with the disk.
		   */
#if 1
		  /*
		   *  If there was an error, try to load only the
		   *  required sector(s) rather than failing completely.
		   */
		  if (slen > num_sect
		      || biosdisk (BIOSDISK_READ, drive, &buf_geom,
				   sector, slen, BUFFERSEG))
#endif
		  {
		    errnum = ERR_READ;
		    return 0;
		  }

		  bufaddr = (char *) BUFFERADDR + byte_offset;
		}
	    }
	} /* if (track != buf_track) */

      if (size > (num_sect << sector_size_bits) - byte_offset)
	  size = (num_sect << sector_size_bits) - byte_offset;

      /*
       *  Instrumentation to tell which sectors were read and used.
       */
      if (disk_read_func)
	{
	  unsigned long sector_num = sector;
	  unsigned long length = buf_geom.sector_size - byte_offset;
	  if (length > size)
	    length = size;
	  (*disk_read_func) (sector_num++, byte_offset, length);
	  length = size - length;
	  if (length > 0)
	    {
	      while (length > buf_geom.sector_size)
		{
		  (*disk_read_func) (sector_num++, 0, buf_geom.sector_size);
		  length -= buf_geom.sector_size;
		}
	      (*disk_read_func) (sector_num, 0, length);
	    }
	}

      grub_memmove (buf, bufaddr, size);

      if (errnum == ERR_WONT_FIT)
        {
	  if (! rawread_ignore_memmove_overflow)
	      return 0;

	  errnum = 0;
	  buf = NULL; /* so that further memcheck() always fail */
        }
      else
        buf += size;
      byte_len -= size;		/* byte_len always >= size */
      sector += num_sect;
      byte_offset = 0;
    } /* while (byte_len > 0 && !errnum) */

  return 1;//(!errnum);
}


int
devread (unsigned long sector, unsigned long byte_offset, unsigned long byte_len, char *buf)
{
  unsigned long sector_size_bits = log2_tmp(buf_geom.sector_size);

  if (emu_iso_sector_size_2048)
    {
      emu_iso_sector_size_2048 = 0;
      asm volatile ("shl%L0 %1,%0"
		: "=r"(sector)
		: "Ic"((int8_t)(ISO_SECTOR_BITS - sector_size_bits)),
		"0"(sector));
    }

  /*
   *  Check partition boundaries
   */
//grub_printf ("sector=%x, byte_offset=%x, byte_len=%x, buf=%x, part_length=%x\n", sector, byte_offset, byte_len, buf, part_length);
  if (((unsigned long)(sector + ((byte_offset + byte_len - 1) >> sector_size_bits)) >= part_length) && part_start)
    {
      errnum = ERR_OUTSIDE_PART;
      return 0;
    }

//  if (byte_len <= 0)
//    return 1;

  /*
   *  Get the read to the beginning of a partition.
   */
  sector += byte_offset >> sector_size_bits;
  byte_offset &= buf_geom.sector_size - 1;

#if !defined(STAGE1_5)
  if (disk_read_hook && (((unsigned long)debug) >= 0x7FFFFFFF))
    printf ("<%d, %d, %d>", sector, byte_offset, byte_len);
#endif /* !STAGE1_5 */

  /*
   *  Call RAWREAD, which is very similar, but:
   *
   *    --  It takes an extra parameter, the drive number.
   *    --  It requires that "sector" is relative to the beginning
   *            of the disk.
   *    --  It doesn't handle offsets across the sector boundary.
   */
  return rawread (current_drive, part_start + sector, byte_offset, byte_len, buf);
}


#ifndef STAGE1_5
/* Write 1 sector at BUF onto sector number SECTOR on drive DRIVE.
 * Only a 512-byte sector should be written with this function.
 * Return:
 *		1	success
 *		0	failure
 */
int
rawwrite (unsigned long drive, unsigned long sector, char *buf)
{
  /* skip the write if possible. */
  if (biosdisk (BIOSDISK_READ, drive, &buf_geom, sector, 1, SCRATCHSEG))
    {
      errnum = ERR_READ;
      return 0;
    }

  if (! memcmp ((char *) SCRATCHADDR, buf, SECTOR_SIZE))
	return 1;

  memmove ((char *) SCRATCHADDR, buf, SECTOR_SIZE);
  if (biosdisk (BIOSDISK_WRITE, drive, &buf_geom, sector, 1, SCRATCHSEG))
    {
      errnum = ERR_WRITE;
      return 0;
    }

#if 1
  if (buf_drive == drive && sector - sector % buf_geom.sectors == buf_track)
    {
	/* Update the cache. */
	memmove ((char *) BUFFERADDR + ((sector - buf_track) << SECTOR_BITS), buf, SECTOR_SIZE);
    }
#else
  if (sector - sector % buf_geom.sectors == buf_track)
    /* Clear the cache.  */
    buf_track = -1;
#endif

  return 1;
}
#endif /* ! STAGE1_5 */

#ifndef STAGE1_5
int
devwrite (unsigned long sector, unsigned long sector_count, char *buf)
{
#if defined(GRUB_UTIL) && defined(__linux__)
  if (current_partition != 0xFFFFFF
      && is_disk_device (device_map, current_drive))
    {
      /* If the grub shell is running under Linux and the user wants to
	 embed a Stage 1.5 into a partition instead of a MBR, use system
	 calls directly instead of biosdisk, because of the bug in
	 Linux. *sigh*  */
      return write_to_partition (device_map, current_drive, current_partition, sector, sector_count, buf);
    }
  else
#endif /* GRUB_UTIL && __linux__ */
    {
      //unsigned long i;

      for (i = 0; i < sector_count; i++)
	{
	  if (! rawwrite (current_drive, part_start + sector + i, buf + (i << SECTOR_BITS)))
	      return 0;
	}
      return 1;
    }
}
#endif /* ! STAGE1_5 */


#ifndef STAGE1_5
int
set_bootdev (int hdbias)
{
  int j;

  if (kernel_type != KERNEL_TYPE_FREEBSD && kernel_type != KERNEL_TYPE_NETBSD)
	return 0;
  /* Copy the boot partition information to 0x7be-0x7fd for chain-loading.  */
  if ((saved_drive & 0x80) && cur_part_addr)
    {
      if (rawread (saved_drive, cur_part_offset, 0, SECTOR_SIZE, (char *) SCRATCHADDR))
	{
	  char *dst, *src;

	  /* Need only the partition table.
	     XXX: We cannot use grub_memmove because BOOT_PART_TABLE
	     (0x07be) is less than 0x1000.  */
	  dst = (char *) BOOT_PART_TABLE;
	  src = (char *) SCRATCHADDR + BOOTSEC_PART_OFFSET;
	  while (dst < (char *) BOOT_PART_TABLE + BOOTSEC_PART_LENGTH)
	    *dst++ = *src++;

	  /* Clear the active flag of all partitions.  */
	  for (i = 0; i < 4; i++)
	    PC_SLICE_FLAG (BOOT_PART_TABLE - BOOTSEC_PART_OFFSET, i) = 0;

	  /* Set the active flag of the booted partition.  */
	  *((unsigned char *) cur_part_addr) = PC_SLICE_FLAG_BOOTABLE;
	  boot_part_addr = cur_part_addr;
	}
      else
      {
	return 0;
      }
    }

  /*
   *  Set BSD boot device.
   */
  i = (saved_partition >> 16) + 2;
  if (saved_partition == 0xFFFFFF)
    i = 1;
  else if ((saved_partition >> 16) == 0xFF)
    i = 0;

  /* FIXME: extremely evil hack!!! */
  j = 2;
  if (saved_drive & 0x80)
    j = bsd_evil_hack;

  return MAKEBOOTDEV (j, (i >> 4), (i & 0xF), ((saved_drive - hdbias) & 0x7F), ((saved_partition >> 8) & 0xFF));
}
#endif /* STAGE1_5 */


#ifndef STAGE1_5
/*
 *  This prints the filesystem type or gives relevant information.
 */

void
print_fsys_type (void)
{
  if (! do_completion)
    {
      printf (" Filesystem type ");

      if (fsys_type != NUM_FSYS)
	printf ("is %s, ", fsys_table[fsys_type].name);
      else
	printf ("unknown, ");

      if (current_partition == 0xFFFFFF)
	printf ("using whole disk\n");
      else
	printf ("partition type 0x%02X\n", current_slice & 0xFF);
    }
}
#endif /* ! STAGE1_5 */


  /* Get next BSD partition in current PC slice.  */
static int
next_bsd_partition (/*unsigned long drive, unsigned long *partition, int *type, unsigned long *start, unsigned long *len, char *buf*/void)
{
//    int i;
      bsd_part_no = (*next_partition_partition & 0xFF00) >> 8;

#ifndef STAGE1_5
//if (debug == -2) grub_printf ("next_bsd_partition: 001\n");
#endif
      /* If this is the first time...  */
      if (bsd_part_no == 0xFF)
	{
	  /* Check if the BSD label is within current PC slice.  */
	  if (*next_partition_len < BSD_LABEL_SECTOR + 1)
	    {
	      errnum = ERR_BAD_PART_TABLE;
	      return 0;
	    }

#ifndef STAGE1_5
//if (debug == -2) grub_printf ("next_bsd_partition: 002\n");
#endif
	  /* Read the BSD label.  */
	  if (! rawread (next_partition_drive, *next_partition_start + BSD_LABEL_SECTOR,
			 0, SECTOR_SIZE, next_partition_buf))
	    return 0;

#ifndef STAGE1_5
//if (debug == -2) grub_printf ("next_bsd_partition: 003\n");
#endif
	  /* Check if it is valid.  */
	  if (! BSD_LABEL_CHECK_MAG (next_partition_buf))
	    {
	      errnum = ERR_BAD_PART_TABLE;
	      return 0;
	    }

	  bsd_part_no = -1;
	}

#ifndef STAGE1_5
//if (debug == -2) grub_printf ("next_bsd_partition: 004\n");
#endif
      /* Search next valid BSD partition.  */
      if (BSD_LABEL_NPARTS (next_partition_buf) <= BSD_LABEL_NPARTS_MAX)
      for (i = bsd_part_no + 1; i < BSD_LABEL_NPARTS (next_partition_buf); i++)
	{
	  if (BSD_PART_TYPE (next_partition_buf, i))
	    {
	      /* Note that *TYPE and *PARTITION were set
		 for current PC slice.  */
	      *next_partition_type = (BSD_PART_TYPE (next_partition_buf, i) << 8) | (*next_partition_type & 0xFF);
	      *next_partition_start = BSD_PART_START (next_partition_buf, i);
	      *next_partition_len = BSD_PART_LENGTH (next_partition_buf, i);
	      *next_partition_partition = (*next_partition_partition & 0xFF00FF) | (i << 8);

#ifndef STAGE1_5
	      /* XXX */
	      if ((next_partition_drive & 0x80) && BSD_LABEL_DTYPE (next_partition_buf) == DTYPE_SCSI)
		bsd_evil_hack = 4;
#endif /* ! STAGE1_5 */

	      return 1;
	    }
	}

#ifndef STAGE1_5
//if (debug == -2) grub_printf ("next_bsd_partition: 005\n");
#endif
      errnum = ERR_NO_PART;
      return 0;
}

  /* Get next PC slice. Be careful of that this function may return
     an empty PC slice (i.e. a partition whose type is zero) as well.  */
static int
next_pc_slice (void)
{
redo:
#ifndef STAGE1_5
//if (debug == -2) grub_printf ("next_pc_slice: 001\n");
#endif
      pc_slice_no = (*next_partition_partition & 0xFF0000) >> 16;

      /* If this is the first time...  */
      if (pc_slice_no == 0xFF)
	{
	  *next_partition_offset = 0;
	  *next_partition_ext_offset = 0;
	  *next_partition_entry = -1;
	  pc_slice_no = -1;
	}

#ifndef STAGE1_5
//if (debug == -2) grub_printf ("next_pc_slice: 002\n");
#endif
      /* Read the MBR or the boot sector of the extended partition.  */
      if (! rawread (next_partition_drive, *next_partition_offset, 0, SECTOR_SIZE, next_partition_buf))
	return 0;

      /* Check if it is valid.  */
      if (! PC_MBR_CHECK_SIG (next_partition_buf))
	{
	  errnum = ERR_BAD_PART_TABLE;
	  return 0;
	}

next_entry:
#ifndef STAGE1_5
//if (debug == -2) grub_printf ("next_pc_slice: 003\n");
#endif
      /* Increase the entry number.  */
      (*next_partition_entry)++;

      /* If this is out of current partition table...  */
      if (*next_partition_entry == PC_SLICE_MAX)
	{
//	  int i;

	  /* Search the first extended partition in current table.  */
	  for (i = 0; i < PC_SLICE_MAX; i++)
	    {
	      if (IS_PC_SLICE_TYPE_EXTENDED (PC_SLICE_TYPE (next_partition_buf, i)))
		{
		  /* Found. Set the new offset and the entry number,
		     and restart this function.  */
		  *next_partition_offset = *next_partition_ext_offset + PC_SLICE_START (next_partition_buf, i);
		  if (! *next_partition_ext_offset)
		    *next_partition_ext_offset = *next_partition_offset;
		  *next_partition_entry = -1;
#ifndef STAGE1_5
//if (debug == -2) grub_printf ("next_pc_slice: recursive call\n");
#endif

#if 0
		  return next_pc_slice ();	/* FIXME: Recursive!!!! */
#else
		  goto redo;
#endif
		}
	    }

#ifndef STAGE1_5
//if (debug == -2) grub_printf ("next_pc_slice: return error\n");
#endif
	  errnum = ERR_NO_PART;
	  return 0;
	}

      *next_partition_type = PC_SLICE_TYPE (next_partition_buf, *next_partition_entry);
      *next_partition_start = *next_partition_offset + PC_SLICE_START (next_partition_buf, *next_partition_entry);
      *next_partition_len = PC_SLICE_LENGTH (next_partition_buf, *next_partition_entry);

      /* The calculation of a PC slice number is complicated, because of
	 the rather odd definition of extended partitions. Even worse,
	 there is no guarantee that this is consistent with every
	 operating systems. Uggh.  */
      if (((int)pc_slice_no) >= PC_SLICE_MAX - 1	/* if it is a logical partition */
	  && (PC_SLICE_ENTRY_IS_EMPTY (next_partition_buf, *next_partition_entry))) /* ignore the garbage entry(typically all bytes are 0xF6). */
	goto next_entry;
#if 1
      /* disable partition id 00. */
      if (((int)pc_slice_no) >= PC_SLICE_MAX - 1	/* if it is a logical partition */
	  && *next_partition_type == PC_SLICE_TYPE_NONE)	/* ignore the partition with id=00. */
	goto next_entry;
#else
      /* enable partition id 00. */
#endif

      if (((int)pc_slice_no) < PC_SLICE_MAX - 1
	  || ! IS_PC_SLICE_TYPE_EXTENDED (*next_partition_type))
	pc_slice_no++;

#ifndef STAGE1_5
//if (debug == -2) grub_printf ("next_pc_slice: return success\n");
#endif
      *next_partition_partition = (pc_slice_no << 16) | 0xFFFF;
      return 1;
}


/* Get the information on next partition on the drive DRIVE.
   The caller must not modify the contents of the arguments when
   iterating this function. The partition representation in GRUB will
   be stored in *PARTITION. Likewise, the partition type in *TYPE, the
   start sector in *START, the length in *LEN, the offset of the
   partition table in *OFFSET, the entry number in the table in *ENTRY,
   the offset of the extended partition in *EXT_OFFSET.
   BUF is used to store a MBR, the boot sector of a partition, or
   a BSD label sector, and it must be at least 512 bytes length.
   When calling this function first, *PARTITION must be initialized to
   0xFFFFFF. The return value is zero if fails, otherwise non-zero.  */
int
next_partition (/*unsigned long drive, unsigned long dest,
		unsigned long *partition, int *type,
		unsigned long *start, unsigned long *len,
		unsigned long *offset, int *entry,
		unsigned long *ext_offset, char *buf*/void)
{
  /* Start the body of this function.  */

#ifndef STAGE1_5
  if ((current_drive == NETWORK_DRIVE) || (current_drive == PXE_DRIVE))
    return 0;
#endif

  /* If previous partition is a BSD partition or a PC slice which
     contains BSD partitions...  */
  if ((*next_partition_partition != 0xFFFFFF && IS_PC_SLICE_TYPE_BSD (*next_partition_type & 0xff))
      || ! (next_partition_drive & 0x80))
    {
#ifndef STAGE1_5
//if (debug == -2) grub_printf ("next_partition: bsd check begin\n");
#endif
      if (*next_partition_type == PC_SLICE_TYPE_NONE)
	*next_partition_type = PC_SLICE_TYPE_FREEBSD;

      /* Get next BSD partition, if any.  */
      if (next_bsd_partition (/*next_partition_drive, next_partition_partition, next_partition_type, next_partition_start, next_partition_len, next_partition_buf*/))
	return 1;

      /* If the destination partition is a BSD partition and current
	 BSD partition has any error, abort the operation.  */
      if ((next_partition_dest & 0xFF00) != 0xFF00
	  && ((next_partition_dest & 0xFF0000) == 0xFF0000
	      || (next_partition_dest & 0xFF0000) == (*next_partition_partition & 0xFF0000)))
	return 0;

      /* Ignore the error.  */
      errnum = ERR_NONE;
    }

#ifndef STAGE1_5
//if (debug == -2) grub_printf ("next_partition: next_pc_slice begin\n");
#endif
  return next_pc_slice ();
}

static void
attempt_mount (void)
{
#ifndef STAGE1_5
  for (fsys_type = 0; fsys_type < NUM_FSYS; fsys_type++)
  {
//    if (fsys_type >= 4) continue;
    if (errnum = 0, ((fsys_table[fsys_type].mount_func) ()))
      break;
  }

  if (fsys_type == NUM_FSYS && errnum == ERR_NONE)
    errnum = ERR_FSYS_MOUNT;
#else
  fsys_type = 0;
  if ((*(fsys_table[fsys_type].mount_func)) () != 1)
    {
      fsys_type = NUM_FSYS;
      errnum = ERR_FSYS_MOUNT;
    }
#endif
}


/*
 *  This performs a "mount" on the current device, both drive and partition
 *  number.
 */

int
open_device (void)
{
  if (open_partition ())
    attempt_mount ();

  if (errnum != ERR_NONE)
    return 0;

  return 1;
}


  /* For simplicity.  */
static unsigned long next_part (void);
static unsigned long
next_part (void)
{
	next_partition_drive		= current_drive;
	next_partition_dest		= dest_partition;
	next_partition_partition	= &current_partition;
	next_partition_type		= &current_slice;
	next_partition_start		= &part_start;
	next_partition_len		= &part_length;
	next_partition_offset		= &part_offset;
	next_partition_entry		= &entry;
	next_partition_ext_offset	= &ext_offset;
	next_partition_buf		= mbr;
	i = next_partition ();
	bsd_part_no = (current_partition >> 8) & 0xFF;
	pc_slice_no = current_partition >> 16;
	return i;
}


#ifndef STAGE1_5
static void
check_and_print_mount (void)
{
  attempt_mount ();
  if (errnum == ERR_FSYS_MOUNT)
    errnum = ERR_NONE;
  if (!errnum)
    print_fsys_type ();
  print_error ();
}
#endif /* ! STAGE1_5 */


/* Open a partition.  */
int
real_open_partition (int flags)
{
#if defined(STAGE1_5) || defined(GRUB_UTIL)
//  char mbr[SECTOR_SIZE];
#endif
//  int bsd_part, pc_slice;

  dest_partition = current_partition;

#ifndef STAGE1_5
  /* network drive */
  if ((current_drive == NETWORK_DRIVE) || (current_drive==PXE_DRIVE))
    return 1;

  if (! sane_partition ())
    return 0;
#endif

  bsd_evil_hack = 0;
  current_slice = 0;
  part_start = 0;

  /* Make sure that buf_geom is valid. */
  if (buf_drive != current_drive)
    {
      if (get_diskinfo (current_drive, &buf_geom))
	{
	  errnum = ERR_NO_DISK;
	  return 0;
	}
      buf_drive = current_drive;
      buf_track = -1;
    }
  part_length = buf_geom.total_sectors;

  /* If this is the whole disk, return here.  */
  if (! flags && current_partition == 0xFFFFFF)
    return 1;

  if (flags)
    dest_partition = 0xFFFFFF;

  /* Initialize CURRENT_PARTITION for next_partition.  */
  current_partition = 0xFFFFFF;

  while (next_part ())
    {
#ifndef STAGE1_5
    loop_start:

      cur_part_offset = part_offset;
      cur_part_addr = BOOT_PART_TABLE + (entry << 4);
//if (debug == -2) grub_printf ("real_open_partition: outer loop: 001\n");
#endif /* ! STAGE1_5 */

      /* If this is a valid partition...  */
      if (current_slice)
	{
#ifndef STAGE1_5
	  /* Display partition information.  */
	  if (flags && ! IS_PC_SLICE_TYPE_EXTENDED (current_slice))
	    {
	      if (! do_completion)
		{
		  if (current_drive & 0x80)
		    {
			int active = (PC_SLICE_FLAG (mbr, entry) == PC_SLICE_FLAG_BOOTABLE);
			grub_printf ("   Partition num: %d%s, ",
				 (current_partition >> 16), (active ? ", active": ""));
		    }

//if (debug == -2) grub_printf ("real_open_partition: outer loop: 002\n");
		  if (! IS_PC_SLICE_TYPE_BSD (current_slice))
		    check_and_print_mount ();
		  else
		    {
		      int got_part = 0;
		      int saved_slice = current_slice;

//if (debug == -2) grub_printf ("real_open_partition: outer loop: 003\n");
		      while (next_part ())
			{
//if (debug == -2) grub_printf ("real_open_partition: inner loop: 004\n");
			  if (bsd_part_no == 0xFF)
			    break;

			  if (! got_part)
			    {
			      grub_printf ("[BSD sub-partitions immediately follow]\n");
			      got_part = 1;
			    }

			  grub_printf ("     BSD Partition num: \'%c\', ",
				       bsd_part_no + 'a');
			  check_and_print_mount ();
			}

		      if (! got_part)
			grub_printf (" No BSD sub-partition found, partition type 0x%x\n",
				     saved_slice);

		      if (errnum)
			{
			  errnum = ERR_NONE;
			  break;
			}

		      goto loop_start;
		    }
		}
	      else
		{
//if (debug == -2) grub_printf ("real_open_partition: outer loop: 005\n");
		  if (bsd_part_no != 0xFF)
		    {
		      char str[16];

		      if (! (current_drive & 0x80)
			  || (dest_partition >> 16) == pc_slice_no)
			grub_sprintf (str, "%c)", bsd_part_no + 'a');
		      else
			grub_sprintf (str, "%d,%c)",
				      pc_slice_no, bsd_part_no + 'a');
		      print_a_completion (str);
		    }
		  else if (! IS_PC_SLICE_TYPE_BSD (current_slice))
		    {
		      char str[8];

//if (debug == -2) grub_printf ("real_open_partition: outer loop: 006\n");
		      grub_sprintf (str, "%d)", pc_slice_no);
		      print_a_completion (str);
		    }
		}
	    }

//if (debug == -2) grub_printf ("real_open_partition: outer loop: 007\n");
	  errnum = ERR_NONE;
#endif /* ! STAGE1_5 */

	  /* Check if this is the destination partition.  */
	  if (! flags
	      && (dest_partition == current_partition
		  || ((dest_partition >> 16) == 0xFF
		      && ((dest_partition >> 8) & 0xFF) == bsd_part_no)))
	    return 1;
#ifndef STAGE1_5
//if (debug == -2) grub_printf ("real_open_partition: outer loop: 008\n");
#endif /* ! STAGE1_5 */
	}
#ifndef STAGE1_5
//if (debug == -2) grub_printf ("real_open_partition: outer loop: 009\n");
#endif /* ! STAGE1_5 */
    }
#ifndef STAGE1_5
//if (debug == -2) grub_printf ("real_open_partition: outer loop: 010\n");
#endif /* ! STAGE1_5 */

#ifndef STAGE1_5
  if (flags)
    {
      if (! (current_drive & 0x80))
	{
	  current_partition = 0xFFFFFF;
	  check_and_print_mount ();
	}
//if (debug == -2) grub_printf ("real_open_partition: outer loop: 011\n");

      errnum = ERR_NONE;
      return 1;
    }
#endif /* ! STAGE1_5 */

#ifndef STAGE1_5
//if (debug == -2) grub_printf ("real_open_partition: outer loop: 012\n");
#endif /* ! STAGE1_5 */
  return 0;
}


int
open_partition (void)
{
  return real_open_partition (0);
}


#ifndef STAGE1_5
static int
sane_partition (void)
{
//  /* network drive */
//  if (current_drive == NETWORK_DRIVE)
//    return 1;
//
//  /* ram drive */
//  if (current_drive == ram_drive)
//    return 1;

  if (!(current_partition & 0xFF000000uL)	/* the drive field must be 0 */
//      && ((current_drive & 0xFFFFFF7F) < 8	/* and the drive must be < 8 ... */
//	  || current_drive == cdrom_drive)	/* ... or it is cdrom */
      && (current_partition & 0xFF) == 0xFF	/* the low byte is not used and must be 0xFF */
      && ((current_partition & 0xFF00) == 0xFF00 /* the higher byte must be 0xFF for normal ... */
	  || (current_partition & 0xFF00) < 0x800) /* ... or < 8 for BSD partitions */
      && ((current_partition >> 16) == 0xFF	/* the partition field must be whole-drive for floppy */
	  || (current_drive & 0x80)))		/* ... or it is hard drive */
    return 1;

  errnum = ERR_DEV_VALUES;
  return 0;
}
#endif /* ! STAGE1_5 */


/* Parse a device string and initialize the global parameters. */
char *
set_device (char *device)
{
#ifdef STAGE1_5
    /* In Stage 1.5, the first 4 bytes of FILENAME has a device number.  */
  unsigned long dev = *((unsigned long *) device);
  unsigned long drive = (dev >> 24) & 0xFF;
  unsigned long partition = dev & 0xFFFFFF;

  /* If DRIVE is disabled, use SAVED_DRIVE instead.  */
  if (drive == 0xFF/*GRUB_INVALID_DRIVE*/)
    current_drive = saved_drive;
  else
    current_drive = drive;

  /* The `partition' part must always have a valid number.  */
  current_partition = partition;

  errnum = 0;
  return device + sizeof (unsigned long);

#else /* ! STAGE1_5 */

  int result = 0;

  errnum = 0;
  incomplete = 0;
  disk_choice = 1;
  part_choice = PART_UNSPECIFIED;
  current_drive = saved_drive;
  current_partition = 0xFFFFFF;

  if (*device == '(' && !*(device + 1))
    /* user has given '(' only, let disk_choice handle what disks we have */
    return device + 1;

  if (*device == '(' && *(++device))
    {
      if (*device == ')')	/* the device "()" is for the current root */
	{
	  current_partition = saved_partition;
	  return device + 1;
	}
      if (*device != ',' /* && *device != ')' */ )
	{
	  char ch = *device;
	  if (*device == 'f' || *device == 'h' || *device == 'm' || *device == 'r'
#ifdef SUPPORT_NETBOOT
	      || (*device == 'n' && network_ready)
#endif /* SUPPORT_NETBOOT */
#ifdef FSYS_PXE
	      || (*device == 'p' && pxe_entry)
#endif /* FSYS_PXE */
#ifndef GRUB_UTIL
	      || (*device == 'c' && (cdrom_drive != GRUB_INVALID_DRIVE || atapi_dev_count)))
#else
	      || (*device == 'c' && cdrom_drive != GRUB_INVALID_DRIVE))
#endif
	    {
	      /* user has given '([fhn]', check for resp. add 'd' and
		 let disk_choice handle what disks we have */
	      if (!*(device + 1))
		{
		  device++;
		  *device++ = 'd';
		  *device = '\0';
		  return device;
		}
	      else if (*(device + 1) == 'd' && !*(device + 2))
		return device + 2;
	    }

	  if ((*device == 'f'
	      || *device == 'h'
	      || *device == 'm'
	      || *device == 'r'
#ifdef SUPPORT_NETBOOT
	      || (*device == 'n' && network_ready)
#endif
#ifdef FSYS_PXE
	      || (*device == 'p' && pxe_entry)
#endif
#ifndef GRUB_UTIL
	      || (*device == 'c' && (cdrom_drive != GRUB_INVALID_DRIVE || atapi_dev_count)))
#else
	      || (*device == 'c' && cdrom_drive != GRUB_INVALID_DRIVE))
#endif
	      && *(++device, device++) != 'd')
	    errnum = ERR_NUMBER_PARSING;

#ifdef SUPPORT_NETBOOT
	  if (ch == 'n' && network_ready)
	    current_drive = NETWORK_DRIVE;
	  else
#endif /* SUPPORT_NETBOOT */
#ifdef FSYS_PXE
	  if (ch == 'p' && pxe_entry)
	    current_drive = PXE_DRIVE;
	  else
#endif /* FSYS_PXE */
	    {
	      if (ch == 'c' && cdrom_drive != GRUB_INVALID_DRIVE && *device == ')')
		current_drive = cdrom_drive;
	      else if (ch == 'm')
		current_drive = 0xffff;
	      else if (ch == 'r')
		current_drive = ram_drive;
	      else
		{
		  safe_parse_maxint (&device, (int *)(void *) &current_drive);

		  disk_choice = 0;
		  if (ch == 'h')
		    current_drive |= 0x80;
#ifndef GRUB_UTIL
		  //else if (ch == 'c' && cdrom_drive != GRUB_INVALID_DRIVE && current_drive < 8)
		  //{
		  //  if (cdrom_drives[current_drive] != GRUB_INVALID_DRIVE)
		  //	    current_drive = cdrom_drives[current_drive];
		  //}
		  else if (ch == 'c' && atapi_dev_count && current_drive < (unsigned long)atapi_dev_count)
		  {
		    current_drive += min_cdrom_id;
		  }
#endif
		}
	    }
	}

      if (errnum)
	return 0;

      if (*device == ')')
	{
	  part_choice = PART_CHOSEN;
	  result = 1;
	}
      else if (*device == ',')
	{
	  /* Either an absolute PC or BSD partition. */
	  disk_choice = 0;
	  part_choice ++;
	  device++;

	  if (*device >= '0' && *device <= '9')
	    {
	      part_choice ++;
	      current_partition = 0;

	      if (!(current_drive & 0x80)
		  || !safe_parse_maxint (&device, (int *)(void *) &current_partition)
		  || current_partition > 254)
		{
		  errnum = ERR_DEV_FORMAT;
		  return 0;
		}

	      current_partition = (current_partition << 16) + 0xFFFF;

	      if (*device == ',')
		device++;

	      if (*device >= 'a' && *device <= 'h')
		{
		  current_partition = (((*(device++) - 'a') << 8)
				       | (current_partition & 0xFF00FF));
		}
	    }
	  else if (*device >= 'a' && *device <= 'h')
	    {
	      part_choice ++;
	      current_partition = ((*(device++) - 'a') << 8) | 0xFF00FF;
	    }

	  if (*device == ')')
	    {
	      if (part_choice == PART_DISK)
		{
		  current_partition = saved_partition;
		  part_choice ++;
		}

	      result = 1;
	    }
	}
    }

  if (! sane_partition ())
    return 0;

  if (result)
    return device + 1;
  else
    {
      if (!*device)
	incomplete = 1;
      errnum = ERR_DEV_FORMAT;
    }

  return 0;

#endif /* ! STAGE1_5 */
}

static char *
setup_part (char *filename)
{
  relative_path = 1;
#ifdef STAGE1_5

  if (! (filename = set_device (filename)))
    {
      current_drive = GRUB_INVALID_DRIVE;
      return 0;
    }

# ifndef NO_BLOCK_FILES
  if (*filename != '/')
    open_partition ();
  else
# endif /* ! NO_BLOCK_FILES */
    open_device ();

#else /* ! STAGE1_5 */

  if (*filename == '(')
    {
      relative_path = 0;
      if ((filename = set_device (filename)) == 0)
	{
	  current_drive = GRUB_INVALID_DRIVE;
	  return 0;
	}
# ifndef NO_BLOCK_FILES
      if (*filename != '/')
	open_partition ();
      else
# endif /* ! NO_BLOCK_FILES */
	open_device ();
    }
  else if (saved_drive != current_drive
	   || saved_partition != current_partition
	   || (*filename == '/' && fsys_type == NUM_FSYS)
	   || buf_drive == -1)
    {
      current_drive = saved_drive;
      current_partition = saved_partition;
      /* allow for the error case of "no filesystem" after the partition
         is found.  This makes block files work fine on no filesystem */
# ifndef NO_BLOCK_FILES
      if (*filename != '/')
	open_partition ();
      else
# endif /* ! NO_BLOCK_FILES */
	open_device ();
    }

#endif /* ! STAGE1_5 */

  if (errnum && (*filename == '/' || errnum != ERR_FSYS_MOUNT))
    return 0;
  else
    errnum = 0;

#ifndef STAGE1_5
  if (!sane_partition ())
    return 0;
#endif

  return filename;
}


#ifndef STAGE1_5
///* Reposition a file offset.  */
//unsigned long
//grub_seek (unsigned long offset)
//{
//  if (offset > filemax /*|| offset < 0*/)
//    return -1;
//
//  filepos = offset;
//  return offset;
//}

int
dir (char *dirname)
{
#ifndef NO_DECOMPRESSION
  compressed_file = 0;
#endif /* NO_DECOMPRESSION */

  if (!(dirname = setup_part (dirname)))
    return 0;

  if (*dirname != '/')
    errnum = ERR_BAD_FILENAME;

  if (fsys_type == NUM_FSYS)
    errnum = ERR_FSYS_MOUNT;

  if (relative_path)
    if (grub_strlen(saved_dir) + grub_strlen(dirname) >= sizeof(open_filename))
      errnum = ERR_WONT_FIT;

  if (errnum)
    return 0;

  /* set "dir" function to list completions */
  print_possibilities = 1;

  if (relative_path)
    grub_sprintf (open_filename, "%s%s", saved_dir, dirname);
  return (*(fsys_table[fsys_type].dir_func)) (relative_path ? open_filename : dirname);
}
#endif /* STAGE1_5 */


#ifndef STAGE1_5
/* If DO_COMPLETION is true, just print NAME. Otherwise save the unique
   part into UNIQUE_STRING.  */
void
print_a_completion (char *name)
{
  /* If NAME is "." or "..", do not count it.  */
  if (grub_strcmp (name, ".") == 0 || grub_strcmp (name, "..") == 0)
    return;

  if (do_completion)
    {
      char *buf = unique_string;

      if (! unique)
	while ((*buf++ = *name++))
	  ;
      else
	{
	  while (*buf && (*buf == *name))
	    {
	      buf++;
	      name++;
	    }
	  /* mismatch, strip it.  */
	  *buf = '\0';
	}
    }
  else
    grub_printf (" %s", name);

  unique++;
}

/*
 *  This lists the possible completions of a device string, filename, or
 *  any sane combination of the two.
 */

int
print_completions (int is_filename, int is_completion)
{
  char *buf = (char *) COMPLETION_BUF;
  char *ptr = buf;

  unique_string = (char *) UNIQUE_BUF;
  *unique_string = 0;
  unique = 0;
  do_completion = is_completion;

  if (! is_filename)
    {
      /* Print the completions of builtin commands.  */
      struct builtin **builtin;

      if (! is_completion)
	grub_printf (" Possible commands are:");

      for (builtin = builtin_table; (*builtin); builtin++)
	{
	  /* If *BUILTIN cannot be run in the command-line, skip it.  */
	  if (! ((*builtin)->flags & BUILTIN_CMDLINE))
	    continue;

	  if (substring (buf, (*builtin)->name, 0) <= 0)
	    print_a_completion ((*builtin)->name);
	}

      if (is_completion && *unique_string)
	{
	  if (unique == 1)
	    {
	      char *u = unique_string + grub_strlen (unique_string);

	      *u++ = ' ';
	      *u = 0;
	    }

	  grub_strcpy (buf, unique_string);
	}

      if (! is_completion)
	grub_putchar ('\n');

      print_error ();
      do_completion = 0;
      if (errnum)
	return -1;
      else
	return unique - 1;
    }

  if (*buf == '/' || (ptr = set_device (buf)) || incomplete)
    {
      errnum = 0;

      if (*buf == '(' && (incomplete || ! *ptr))
	{
	  if (! part_choice)
	    {
	      /* disk completions */
	      int j;
//	      struct geometry tmp_geom;

	      if (! is_completion)
		grub_printf (" Possible disks are: ");

	      if (!ptr
		  || *(ptr-1) != 'd' || (
#ifdef SUPPORT_NETBOOT
		  *(ptr-2) != 'n' &&
#endif /* SUPPORT_NETBOOT */
		  *(ptr-2) != 'c' &&
		  *(ptr-2) != 'm' &&
		  *(ptr-2) != 'r'))
		{
		  int k;
		  for (k = (ptr && (*(ptr-1) == 'd' && *(ptr-2) == 'h') ? 1:0);
		       k < (ptr && (*(ptr-1) == 'd' && *(ptr-2) == 'f') ? 1:2);
		       k++)
		    {
#define HARD_DRIVES (*((char *)0x475))
#define FLOPPY_DRIVES ((*(char*)0x410 & 1)?(*(char*)0x410 >> 6) + 1 : 0)
#ifdef GRUB_UTIL
		      for (j = 0; j < 8; j++)
#else
		      for (j = 0; j < (k ? HARD_DRIVES : FLOPPY_DRIVES); j++)
#endif
#undef HARD_DRIVES
#undef FLOPPY_DRIVES
			{
			  i = (k * 0x80) + j;
			  if ((disk_choice || i == current_drive)
			      && ! get_diskinfo (i, &tmp_geom))
			    {
			      char dev_name[8];

			      grub_sprintf (dev_name, "%cd%d", k ? 'h':'f', j);
			      print_a_completion (dev_name);
			    }
			}
		    }
		}

	      if (rd_base != 0xffffffff
		  && (disk_choice || ram_drive == current_drive)
		  && (!ptr
		      || *(ptr-1) == '('
		      || (*(ptr-1) == 'd' && *(ptr-2) == 'r')))
		print_a_completion ("rd");

	      if (cdrom_drive != GRUB_INVALID_DRIVE
		  && (disk_choice || cdrom_drive == current_drive)
		  && (!ptr
		      || *(ptr-1) == '('
		      || (*(ptr-1) == 'd' && *(ptr-2) == 'c')))
		print_a_completion ("cd");

#ifndef GRUB_UTIL
	      if (atapi_dev_count  && (!ptr || *(ptr-1) == '(' || (*(ptr-1) == 'd' && *(ptr-2) == 'c')))
	      {
		for (j = 0; j < (unsigned long)atapi_dev_count; j++)
		  if (disk_choice || min_cdrom_id + j == current_drive)
		    {
			char dev_name[8];

			grub_sprintf (dev_name, "cd%d", j);
			print_a_completion (dev_name);
		    }
	      }
#endif

# ifdef SUPPORT_NETBOOT
	      if (network_ready
		  && (disk_choice || NETWORK_DRIVE == current_drive)
		  && (!ptr
		      || *(ptr-1) == '('
		      || (*(ptr-1) == 'd' && *(ptr-2) == 'n')))
		print_a_completion ("nd");
# endif /* SUPPORT_NETBOOT */

# ifdef FSYS_PXE
	      if (pxe_entry
		  && (disk_choice || PXE_DRIVE == current_drive)
		  && (!ptr
		      || *(ptr-1) == '('
		      || (*(ptr-1) == 'd' && *(ptr-2) == 'p')))
		print_a_completion ("pd");
# endif /* FSYS_PXE */

	      if (is_completion && *unique_string)
		{
		  ptr = buf;
		  while (*ptr != '(')
		    ptr--;
		  ptr++;
		  grub_strcpy (ptr, unique_string);
		  if (unique == 1)
		    {
		      ptr += grub_strlen (ptr);
		      if (*unique_string == 'h')
			{
			  *ptr++ = ',';
			  *ptr = 0;
			}
		      else
			{
			  *ptr++ = ')';
			  *ptr = 0;
			}
		    }
		}

	      if (! is_completion)
		grub_putchar ('\n');
	    }
	  else
	    {
	      /* partition completions */
	      if (part_choice == PART_CHOSEN
		  && open_partition ()
		  && ! IS_PC_SLICE_TYPE_BSD (current_slice))
		{
		  unique = 1;
		  ptr = buf + grub_strlen (buf);
		  if (*(ptr - 1) != ')')
		    {
		      *ptr++ = ')';
		      *ptr = 0;
		    }
		}
	      else
		{
		  if (! is_completion)
		    grub_printf (" Possible partitions are:\n");
		  real_open_partition (1);

		  if (is_completion && *unique_string)
		    {
		      ptr = buf;
		      while (*ptr++ != ',')
			;
		      grub_strcpy (ptr, unique_string);
		    }
		}
	    }
	}
      else if (ptr && *ptr == '/')
	{
	  /* filename completions */
	  if (! is_completion)
	    grub_printf (" Possible files are:");

	  dir (buf);

	  if (is_completion && *unique_string)
	    {
	      ptr += grub_strlen (ptr);
	      while (*ptr != '/')
		ptr--;
	      ptr++;

	      grub_strcpy (ptr, unique_string);

	      if (unique == 1)
		{
		  ptr += grub_strlen (unique_string);

		  /* Check if the file UNIQUE_STRING is a directory.  */
		  *ptr = '/';
		  *(ptr + 1) = 0;

		  dir (buf);

		  /* Restore the original unique value.  */
		  unique = 1;

		  if (errnum)
		    {
		      /* Regular file */
		      errnum = 0;
		      *ptr = ' ';
		      *(ptr + 1) = 0;
		    }
		}
	    }

	  if (! is_completion)
	    grub_putchar ('\n');
	}
      else
	errnum = ERR_BAD_FILENAME;
    }

  print_error ();
  do_completion = 0;
  if (errnum)
    return -1;
  else
    return unique - 1;
}
#endif /* ! STAGE1_5 */


#ifndef NO_BLOCK_FILES
static int block_file = 0;
#endif /* NO_BLOCK_FILES */

/*
 *  This is the generic file open function.
 */

int
grub_open (char *filename)
{
#ifndef NO_DECOMPRESSION
  compressed_file = 0;
#endif /* NO_DECOMPRESSION */

  /* if any "dir" function uses/sets filepos, it must
     set it to zero before returning if opening a file! */
  filepos = 0;

  if (!(filename = setup_part (filename)))
    return 0;

#ifndef NO_BLOCK_FILES
  block_file = 0;
#endif /* NO_BLOCK_FILES */

  /* This accounts for partial filesystem implementations. */
  fsmax = MAXINT;

  if (*filename != '/')
    {
#ifdef NO_BLOCK_FILES
      return !(errnum = ERR_BAD_FILENAME);
#else
      char *ptr = filename;
      unsigned long tmp, list_addr = FSYS_BUF + 12;  /* BLK_BLKLIST_START */
      filemax = 0;

      while (list_addr < FSYS_BUF + 0x77F9)	/* BLK_MAX_ADDR */
	{
	  tmp = 0;
	  safe_parse_maxint (&ptr, (int *)(void *)&tmp);
	  errnum = 0;

	  if (*ptr != '+')
	    {
	      /* Set FILEMAX in bytes, Undocumented!! */

	      /* The FILEMAX must not exceed the one calculated from
	       * all the blocks in the list.
	       */

	      if ((*ptr && *ptr != '/' && !isspace (*ptr))
		  || tmp == 0 || tmp > filemax)
		break;		/* failure */

	      filemax = tmp;
	      goto block_file;		/* success */
	    }

	  /* since we use the same filesystem buffer, mark it to
	     be remounted */
	  fsys_type = NUM_FSYS;

	  *((unsigned long*)list_addr) = tmp;	/* BLK_BLKSTART */
	  ptr++;		/* skip the plus sign */

	  safe_parse_maxint (&ptr, (int *)(void *)&tmp);

	  if (errnum)
		return 0;

	  if (!tmp || (*ptr && *ptr != ',' && *ptr != '/' && !isspace (*ptr)))
		break;		/* failure */

	  *((unsigned long*)(list_addr+4)) = tmp;	/* BLK_BLKLENGTH */

	  tmp *= buf_geom.sector_size;
	  filemax += tmp;
	  list_addr += 8;			/* BLK_BLKLIST_INC_VAL */

	  if (*ptr != ',')
		goto block_file;		/* success */

	  ptr++;		/* skip the comma sign */
	} /* while (list_addr < FSYS_BUF + 0x77F9) */

      return !(errnum = ERR_BAD_FILENAME);

//      if (list_addr < FSYS_BUF + 0x77F9 && ptr != filename)
//	{
block_file:
	  block_file = 1;
	  (*((unsigned long*)FSYS_BUF))= 0;	/* BLK_CUR_FILEPOS */
	  (*((unsigned long*)(FSYS_BUF+4))) = FSYS_BUF + 12;	/* let BLK_CUR_BLKLIST = BLK_BLKLIST_START */
	  (*((unsigned long*)(FSYS_BUF+8))) = 0;	/* BLK_CUR_BLKNUM */

	  if (current_drive == ram_drive && filemax == 512 &&  filemax < rd_size && (*(long *)(FSYS_BUF + 12)) == 0)
	  {
		filemax = rd_size;
		*(long *)(FSYS_BUF + 16) = (filemax + 0x1FF) >> 9;
	  }
#ifdef NO_DECOMPRESSION
	  return 1;
#else
	  return gunzip_test_header ();
#endif
//	}
#endif /* block files */
    } /* if (*filename != '/') */

  if (!errnum && fsys_type == NUM_FSYS)
    errnum = ERR_FSYS_MOUNT;

#ifndef STAGE1_5
  /* set "dir" function to open a file */
  print_possibilities = 0;
#endif

  if (relative_path)
  {
    if (grub_strlen(saved_dir) + grub_strlen(filename) >= sizeof(open_filename))
    {
      errnum = ERR_WONT_FIT;
      return 0;
    }

    grub_sprintf (open_filename, "%s%s", saved_dir, filename);
  }
  if (!errnum && (*(fsys_table[fsys_type].dir_func)) (relative_path ? open_filename : filename))
    {
#ifdef NO_DECOMPRESSION
      return 1;
#else
      return gunzip_test_header ();
#endif
    }

  return 0;
}


unsigned long
grub_read (char *buf, unsigned long len)
{
  /* Make sure "filepos" is a sane value */
  if (/*filepos < 0 || */filepos > filemax)
    filepos = filemax;

  /* Make sure "len" is a sane value */
  if (/*len < 0 || */len > filemax - filepos)
    len = filemax - filepos;

  /* if target file position is past the end of
     the supported/configured filesize, then
     there is an error */
  if (filepos + len > fsmax)
    {
      errnum = ERR_FILELENGTH;
      return 0;
    }

#ifndef NO_DECOMPRESSION
  if (compressed_file)
    return gunzip_read (buf, len);
#endif /* NO_DECOMPRESSION */

#ifndef NO_BLOCK_FILES
  if (block_file)
    {
      unsigned long size, off, ret = 0;

      while (len && !errnum)
	{
	  /* we may need to look for the right block in the list(s) */
	  if (filepos < (*((unsigned long*)FSYS_BUF)) /* BLK_CUR_FILEPOS */)
	    {
	      (*((unsigned long*)FSYS_BUF)) = 0;
	      (*((unsigned long*)(FSYS_BUF+4))) = FSYS_BUF + 12;	/* let BLK_CUR_BLKLIST = BLK_BLKLIST_START */
	      (*((unsigned long*)(FSYS_BUF+8))) = 0;	/* BLK_CUR_BLKNUM */
	    }

	  /* run BLK_CUR_FILEPOS up to filepos */
	  while (filepos > (*((unsigned long*)FSYS_BUF)))
	    {
	      if ((filepos - ((*((unsigned long*)FSYS_BUF)) & ~(buf_geom.sector_size - 1)))
		  >= buf_geom.sector_size)
		{
		  (*((unsigned long*)FSYS_BUF)) += buf_geom.sector_size;
		  (*((unsigned long*)(FSYS_BUF+8)))++;

		  if ((*((unsigned long*)(FSYS_BUF+8))) >= *((unsigned long*) ((*((unsigned long*)(FSYS_BUF+4))) + 4)) )
		    {
		      (*((unsigned long*)(FSYS_BUF+4))) += 8;	/* BLK_CUR_BLKLIST */
		      (*((unsigned long*)(FSYS_BUF+8))) = 0;	/* BLK_CUR_BLKNUM */
		    }
		}
	      else
		(*((unsigned long*)FSYS_BUF)) = filepos;
	    }

	  off = filepos & (buf_geom.sector_size - 1);
	  size = ((*((unsigned long*)((*((unsigned long*)(FSYS_BUF+4))) + 4)) - (*((unsigned long*)(FSYS_BUF+8))))
		  * buf_geom.sector_size) - off;
	  if (size > len)
	    size = len;

	  disk_read_func = disk_read_hook;

	  /* read current block and put it in the right place in memory */
	  devread ((*((unsigned long*)(*((unsigned long*)(FSYS_BUF+4))))) + (*((unsigned long*)(FSYS_BUF+8))),
		   off, size, buf);

//printf("devread ok\n");
	  disk_read_func = NULL;

	  len -= size;
	  filepos += size;
	  ret += size;
	  buf += size;
	}

      if (errnum)
	ret = 0;

      return ret;
    }
#endif /* NO_BLOCK_FILES */

  if (fsys_type == NUM_FSYS)
    {
      errnum = ERR_FSYS_MOUNT;
      return 0;
    }

  return (*(fsys_table[fsys_type].read_func)) (buf, len);
}

void
grub_close (void)
{
#ifndef NO_BLOCK_FILES
  if (block_file)
    return;
#endif /* NO_BLOCK_FILES */

  if (fsys_table[fsys_type].close_func != 0)
    (*(fsys_table[fsys_type].close_func)) ();
}

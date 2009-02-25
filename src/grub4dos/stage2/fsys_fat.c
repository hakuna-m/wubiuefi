/*
 *  GRUB  --  GRand Unified Bootloader
 *  Copyright (C) 2000,2001,2005   Free Software Foundation, Inc.
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

#ifdef FSYS_FAT

#include "shared.h"
#include "filesys.h"
#include "fat.h"

struct fat_superblock 
{
  int fat_offset;
  int fat_length;
  int fat_size;
  int root_offset;
  int root_max;
  int data_offset;
  
  int num_sectors;
  int num_clust;
  int clust_eof_marker;
  int sects_per_clust;
  int sectsize_bits;
  int clustsize_bits;
  int root_cluster;
  
  int cached_fat;
  int file_cluster;
  unsigned long current_cluster_num;
  int current_cluster;
};

/* pointer(s) into filesystem info buffer for DOS stuff */
#define FAT_SUPER ((struct fat_superblock *)(FSYS_BUF + 32256))/* 512 bytes long */
#define FAT_BUF   (FSYS_BUF + 30208)	/* 4 sector FAT buffer(2048 bytes) */
#define NAME_BUF  (FSYS_BUF + 28160)	/* unicode name buffer(833*2 bytes)*/
#define UTF8_BUF  (FSYS_BUF + 25600)	/* UTF8 name buffer (833*3 bytes)*/

#define FAT_CACHE_SIZE 2048

//static __inline__ unsigned long
//log2_tmp (unsigned long word)
//{
//  __asm__ ("bsfl %1,%0"
//	   : "=r" (word)
//	   : "r" (word));
//  return word;
//}

int
fat_mount (void)
{
  struct fat_bpb bpb;
  __u32 magic, first_fat;
  
  /* Check partition type for harddisk */
//  if (((current_drive & 0x80) || (current_slice != 0))
//      && ! IS_PC_SLICE_TYPE_FAT (current_slice)
//      && (! IS_PC_SLICE_TYPE_BSD_WITH_FS (current_slice, FS_MSDOS)))
//    return 0;
  
  /* Read bpb */
  if (! devread (0, 0, sizeof (bpb), (char *) &bpb))
    return 0;

  /* Check if the number of sectors per cluster is zero here, to avoid
     zero division.  */
  if (bpb.sects_per_clust == 0)
    return 0;
  
  /*  Sectors per cluster. Valid values are 1, 2, 4, 8, 16, 32, 64 and 128.
   *  But a cluster size larger than 32K should not occur.
   */
  if (128 % bpb.sects_per_clust)
    return 0;

  FAT_SUPER->sectsize_bits = log2_tmp (FAT_CVT_U16 (bpb.bytes_per_sect));

  /* sector size must be 512 */
  if (FAT_SUPER->sectsize_bits != 9)
    return 0;

  FAT_SUPER->clustsize_bits
    = FAT_SUPER->sectsize_bits + log2_tmp (bpb.sects_per_clust);
  
#ifndef STAGE1_5
  /* cluster size must be <= 32768 */
  if (FAT_SUPER->clustsize_bits > 15)
  {
    if (debug > 0)
	grub_printf ("Warning! FAT cluster size(=%d) larger than 32K!\n", 1 << (FAT_SUPER->clustsize_bits));
    //return 0;
  }
#endif /* STAGE1_5 */

  /* reserved sectors should not be 0 for fat_fs */
  if (FAT_CVT_U16 (bpb.reserved_sects) == 0)
    return 0;

  /* Number of FATs(nearly always 2).  */
  if ((unsigned char)(bpb.num_fats - 1) > 1)
    return 0;
  
  /* sectors per track(between 1 and 63).  */
  if ((unsigned short)(bpb.secs_track - 1) > 62)
    return 0;
  
  /* number of heads(between 1 and 256).  */
  if ((unsigned short)(bpb.heads - 1) > 255)
    return 0;
  
  /* Fill in info about super block */
  FAT_SUPER->num_sectors = FAT_CVT_U16 (bpb.short_sectors) 
    ? FAT_CVT_U16 (bpb.short_sectors) : bpb.long_sectors;
  
  /* FAT offset and length */
  FAT_SUPER->fat_offset = FAT_CVT_U16 (bpb.reserved_sects);
  FAT_SUPER->fat_length = 
    bpb.fat_length ? bpb.fat_length : bpb.fat32_length;
  
  /* Rootdir offset and length for FAT12/16 */
  FAT_SUPER->root_offset = 
    FAT_SUPER->fat_offset + bpb.num_fats * FAT_SUPER->fat_length;
  FAT_SUPER->root_max = FAT_DIRENTRY_LENGTH * FAT_CVT_U16(bpb.dir_entries);
  
  /* Data offset and number of clusters */
  FAT_SUPER->data_offset = 
    FAT_SUPER->root_offset
    + ((FAT_SUPER->root_max + SECTOR_SIZE - 1) >> FAT_SUPER->sectsize_bits);
  FAT_SUPER->num_clust = 
    2 + ((FAT_SUPER->num_sectors - FAT_SUPER->data_offset) 
	 / bpb.sects_per_clust);
  FAT_SUPER->sects_per_clust = bpb.sects_per_clust;
  
  if (!bpb.fat_length)
    {
      /* This is a FAT32 */
      if (FAT_CVT_U16(bpb.dir_entries))
 	return 0;
      
      if (bpb.flags & 0x0080)
	{
	  /* FAT mirroring is disabled, get active FAT */
	  int active_fat = bpb.flags & 0x000f;
	  if (active_fat >= bpb.num_fats)
	    return 0;
	  FAT_SUPER->fat_offset += active_fat * FAT_SUPER->fat_length;
	}
      
      FAT_SUPER->fat_size = 8;
      FAT_SUPER->root_cluster = bpb.root_cluster;

      /* Yes the following is correct.  FAT32 should be called FAT28 :) */
      FAT_SUPER->clust_eof_marker = 0xffffff8;
    } 
  else 
    {
      if (!FAT_SUPER->root_max)
 	return 0;
      
      FAT_SUPER->root_cluster = -1;
      if (FAT_SUPER->num_clust > FAT_MAX_12BIT_CLUST) 
	{
	  FAT_SUPER->fat_size = 4;
	  FAT_SUPER->clust_eof_marker = 0xfff8;
	} 
      else
	{
	  FAT_SUPER->fat_size = 3;
	  FAT_SUPER->clust_eof_marker = 0xff8;
	}
    }

  /* Now do some sanity checks */
  
  if (FAT_CVT_U16(bpb.bytes_per_sect) != (1 << FAT_SUPER->sectsize_bits)
      || FAT_CVT_U16(bpb.bytes_per_sect) != SECTOR_SIZE
      || bpb.sects_per_clust != (1 << (FAT_SUPER->clustsize_bits
 				       - FAT_SUPER->sectsize_bits))
      || FAT_SUPER->num_clust <= 2
      || (FAT_SUPER->fat_size * FAT_SUPER->num_clust / (2 * SECTOR_SIZE)
 	  > FAT_SUPER->fat_length))
    return 0;
  
  /* kbs: Media check on first FAT entry [ported from PUPA] */

  if (!devread(FAT_SUPER->fat_offset, 0,
               sizeof(first_fat), (char *)&first_fat))
    return 0;

  if (FAT_SUPER->fat_size == 8)
    {
      first_fat &= 0x0fffffff;
      magic = 0x0fffff00;
    }
  else if (FAT_SUPER->fat_size == 4)
    {
      first_fat &= 0x0000ffff;
      magic = 0xff00;
    }
  else
    {
      first_fat &= 0x00000fff;
      magic = 0x0f00;
    }

  /* Ignore the 3rd bit, because some BIOSes assigns 0xF0 to the media
     descriptor, even if it is a so-called superfloppy (e.g. an USB key).
     The check may be too strict for this kind of stupid BIOSes, as
     they overwrite the media descriptor.  */
#ifndef STAGE1_5
//  if ((first_fat | 0x8) != (magic | bpb.media | 0x8))
//  if ((first_fat | 0x8) != (magic | 0xF8))
  if ((first_fat | 0xF) != (magic | 0xFF))
  {
    if (debug > 0)
	grub_printf ("Warning! Invalid first FAT entry(=0x%X)!\n", first_fat);
    //return 0;
  }
#endif /* STAGE1_5 */

  FAT_SUPER->cached_fat = - 2 * FAT_CACHE_SIZE;
  return 1;
}

unsigned long
fat_read (char *buf, unsigned long len)
{
  unsigned long logical_clust;
  unsigned long offset;
  unsigned long ret = 0;
  unsigned long size;
  
  if (FAT_SUPER->file_cluster < 0)
    {
      /* root directory for fat16 */
      size = FAT_SUPER->root_max - filepos;
      if (size > len)
 	size = len;
      if (!devread(FAT_SUPER->root_offset, filepos, size, buf))
 	return 0;
      filepos += size;
      return size;
    }
  
  logical_clust = filepos >> FAT_SUPER->clustsize_bits;
  offset = (filepos & ((1 << FAT_SUPER->clustsize_bits) - 1));
  if (logical_clust < FAT_SUPER->current_cluster_num)
    {
      FAT_SUPER->current_cluster_num = 0;
      FAT_SUPER->current_cluster = FAT_SUPER->file_cluster;
    }
  
  while (len > 0)
    {
      unsigned long sector;
      while (logical_clust > FAT_SUPER->current_cluster_num)
	{
	  /* calculate next cluster */
	  unsigned long fat_entry = 
	    FAT_SUPER->current_cluster * FAT_SUPER->fat_size;
	  unsigned long next_cluster;
	  unsigned long cached_pos = (fat_entry - FAT_SUPER->cached_fat);
	  
	  if (cached_pos < 0 || 
	      (cached_pos + FAT_SUPER->fat_size) > 2*FAT_CACHE_SIZE)
	    {
	      FAT_SUPER->cached_fat = (fat_entry & ~(2*SECTOR_SIZE - 1));
	      cached_pos = (fat_entry - FAT_SUPER->cached_fat);
	      sector = FAT_SUPER->fat_offset
		+ FAT_SUPER->cached_fat / (2*SECTOR_SIZE);
	      if (!devread (sector, 0, FAT_CACHE_SIZE, (char*) FAT_BUF))
		return 0;
	    }
	  next_cluster = * (unsigned long *) (FAT_BUF + (cached_pos >> 1));
	  if (FAT_SUPER->fat_size == 3)
	    {
	      if (cached_pos & 1)
		next_cluster >>= 4;
	      next_cluster &= 0xFFF;
	    }
	  else if (FAT_SUPER->fat_size == 4)
	    next_cluster &= 0xFFFF;
	  
	  if (next_cluster >= FAT_SUPER->clust_eof_marker)
	    return ret;
	  if (next_cluster < 2 || next_cluster >= FAT_SUPER->num_clust)
	    {
	      errnum = ERR_FSYS_CORRUPT;
	      return 0;
	    }
	  
	  FAT_SUPER->current_cluster = next_cluster;
	  FAT_SUPER->current_cluster_num++;
	}
      
      sector = FAT_SUPER->data_offset + ((FAT_SUPER->current_cluster - 2)
		<< (FAT_SUPER->clustsize_bits - FAT_SUPER->sectsize_bits));
      
      size = (1 << FAT_SUPER->clustsize_bits) - offset;
      
      if (size > len)
	  size = len;
      
      disk_read_func = disk_read_hook;
      
      devread(sector, offset, size, buf);
      
      disk_read_func = NULL;
      
      len -= size;	/* len always >= 0 */
      buf += size;
      ret += size;
      filepos += size;
      logical_clust++;
      offset = 0;
    }
  return errnum ? 0 : ret;
}

int
fat_dir (char *dirname)
{
  char *rest, ch, dir_buf[FAT_DIRENTRY_LENGTH];
  unsigned short *filename = (unsigned short *) NAME_BUF; /* unicode */
  unsigned char *utf8 = (unsigned char *) UTF8_BUF; /* utf8 filename */
  int attrib = FAT_ATTRIB_DIR;
//#ifndef STAGE1_5
//  int do_possibilities = 0;
//#endif
  
  /* XXX I18N:
   * the positions 2,4,6 etc are high bytes of a 16 bit unicode char 
   */
  static unsigned char longdir_pos[] = 
  { 1, 3, 5, 7, 9, 14, 16, 18, 20, 22, 24, 28, 30 };
  int slot = -2;
  int alias_checksum = -1;
  
  FAT_SUPER->file_cluster = FAT_SUPER->root_cluster;
  
  /* main loop to find desired directory entry */
 loop:
  filepos = 0;
  FAT_SUPER->current_cluster_num = MAXINT;
  
  /* if we have a real file (and we're not just printing possibilities),
     then this is where we want to exit */
  
  if (!*dirname || isspace (*dirname))
    {
      if (attrib & FAT_ATTRIB_DIR)
	{
	  errnum = ERR_BAD_FILETYPE;
	  return 0;
	}
      
      return 1;
    }
  
  /* continue with the file/directory name interpretation */
  
  /* skip over slashes */
  while (*dirname == '/')
    dirname++;
  
  if (!(attrib & FAT_ATTRIB_DIR))
    {
      errnum = ERR_BAD_FILETYPE;
      return 0;
    }
  /* Directories don't have a file size */
  filemax = MAXINT;
  
  /* check if the dirname ends in a slash(saved in CH) and end it in a NULL */
  //for (rest = dirname; (ch = *rest) && !isspace (ch) && ch != '/'; rest++);
  for (rest = dirname; (ch = *rest) && !isspace (ch) && ch != '/'; rest++)
  {
	if (ch == '\\')
	{
		rest++;
		if (! (ch = *rest))
			break;
	}
  }
  
  *rest = 0;
  
//# ifndef STAGE1_5
//  if (print_possibilities && ch != '/')
//    do_possibilities = 1;
//# endif
  
  while (1)
    {
      /* read the dir entry */
      if (fat_read (dir_buf, FAT_DIRENTRY_LENGTH) != FAT_DIRENTRY_LENGTH
		/* read failure */
	  || dir_buf[0] == 0 /* end of dir entry */)
	{
	  if (errnum == 0)
	    {
# ifndef STAGE1_5
	      if (print_possibilities < 0)
		{
		  /* previously succeeded, so return success */
#if 0
		  putchar ('\n');
#endif
		  *rest = ch;	/* XXX: Should restore the byte? */
		  return 1;
		}
# endif /* STAGE1_5 */
	      
	      errnum = ERR_FILE_NOT_FOUND;
	    }
	  
	  *rest = ch;
	  return 0;
	}
      
      if (FAT_DIRENTRY_ATTRIB (dir_buf) == FAT_ATTRIB_LONGNAME)
	{
	  /* This is a long filename.  The filename is build from back
	   * to front and may span multiple entries.  To bind these
	   * entries together they all contain the same checksum over
	   * the short alias.
	   *
	   * The id field tells if this is the first entry (the last
	   * part) of the long filename, and also at which offset this
	   * belongs.
	   *
	   * We just write the part of the long filename this entry
	   * describes and continue with the next dir entry.
	   */
	  int i, offset;
	  unsigned char id = FAT_LONGDIR_ID(dir_buf);
	  
	  if ((id & 0x40)) 
	    {
	      id &= 0x3f;
	      slot = id;
	      filename[slot * 13] = 0;
	      alias_checksum = FAT_LONGDIR_ALIASCHECKSUM(dir_buf);
	    } 
	  
	  if (id != slot || slot == 0
	      || alias_checksum != FAT_LONGDIR_ALIASCHECKSUM(dir_buf))
	    {
	      alias_checksum = -1;
	      continue;
	    }
	  
	  slot--;
	  offset = slot * 13;
	  
	  for (i=0; i < 13; i++)
	    filename[offset+i] = *(unsigned short *)(dir_buf+longdir_pos[i]);
	  continue;
	}
      
      if (!FAT_DIRENTRY_VALID (dir_buf))
	continue;
      
      if (alias_checksum != -1 && slot == 0)
	{
	  int i;
	  unsigned char sum;
	  
	  slot = -2;
	  for (sum = 0, i = 0; i< 11; i++)
	    sum = ((sum >> 1) | (sum << 7)) + dir_buf[i];
	  
	  if (sum == alias_checksum)
	    {
	      goto valid_filename;
//# ifndef STAGE1_5
//	      if (do_possibilities)
//		goto print_filename;
//# endif /* STAGE1_5 */
//	      
//	      if (substring (dirname, filename, 1) == 0)
//		break;
	    }
	}
      
      /* XXX convert to 8.3 filename format here */
      {
	int i, j, c;
	
	for (i = 0; i < 8 && (c = filename[i] = tolower (dir_buf[i]))
	       && /*!isspace (c)*/ c != ' '; i++);
	
	filename[i++] = '.';
	
	for (j = 0; j < 3 && (c = filename[i + j] = tolower (dir_buf[8 + j]))
	       && /*!isspace (c)*/ c != ' '; j++);
	
	if (j == 0)
	  i--;
	
	filename[i + j] = 0;
      }
      
valid_filename:
      unicode_to_utf8 (filename, utf8, 832);
# ifndef STAGE1_5
      if (print_possibilities && ch != '/')
	{
//	print_filename:
	  if (substring (dirname, (char *)utf8, 1) <= 0)
	    {
	      if (print_possibilities > 0)
		print_possibilities = -print_possibilities;
	      print_a_completion ((char *)utf8);
	    }
	  continue;
	}
# endif /* STAGE1_5 */
      
      if (substring (dirname, (char *)utf8, 1) == 0)
	break;
    }
  
  *(dirname = rest) = ch;
  
  attrib = FAT_DIRENTRY_ATTRIB (dir_buf);
  filemax = FAT_DIRENTRY_FILELENGTH (dir_buf);
  FAT_SUPER->file_cluster = FAT_DIRENTRY_FIRST_CLUSTER (dir_buf);
  
  /* go back to main loop at top of function */
  goto loop;
}

#endif /* FSYS_FAT */

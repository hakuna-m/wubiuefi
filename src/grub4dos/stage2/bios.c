/* bios.c - implement C part of low-level BIOS disk input and output */
/*
 *  GRUB  --  GRand Unified Bootloader
 *  Copyright (C) 1999,2000,2003,2004  Free Software Foundation, Inc.
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

#include "shared.h"
#include "iso9660.h"

/* These are defined in asm.S, and never be used elsewhere, so declare the
   prototypes here.  */
extern int biosdisk_standard (int ah, int drive,
			      int coff, int hoff, int soff,
			      int nsec, int segment);
extern int get_diskinfo_standard (int drive,
				  unsigned long *cylinders,
				  unsigned long *heads,
				  unsigned long *sectors);

extern struct drive_map_slot hooked_drive_map[DRIVE_MAP_SIZE + 1];
extern int drive_map_slot_empty (struct drive_map_slot item);

/* Read/write NSEC sectors starting from SECTOR in DRIVE disk with GEOMETRY
   from/into SEGMENT segment. If READ is BIOSDISK_READ, then read it,
   else if READ is BIOSDISK_WRITE, then write it. If an geometry error
   occurs, return BIOSDISK_ERROR_GEOMETRY, and if other error occurs, then
   return the error number. Otherwise, return 0.  */
int
biosdisk (int read, int drive, struct geometry *geometry,
	  int sector, int nsec, int segment)
{
  int err;
  
  /* first, use EBIOS if possible */
  if ((geometry->flags & BIOSDISK_FLAG_LBA_EXTENSION) && (! (geometry->flags & BIOSDISK_FLAG_BIFURCATE) || (drive & 0xFFFFFF00) == 0x100))
    {
      struct disk_address_packet
      {
	unsigned char length;
	unsigned char reserved;
	unsigned short blocks;
	unsigned long buffer;
	unsigned long long block;
	
	/* This structure is passed in the stack. A buggy BIOS could write
	 * garbage data to the tail of the struct and hang the machine. So
	 * we need this protection. - Tinybit
	 */
	unsigned char dummy[16];
      } __attribute__ ((packed)) *dap;

      /* Even the above protection is not enough to avoid stupid actions by
       * buggy BIOSes. So we do it in the 0040:0000 segment. - Tinybit
       */
      dap = (struct disk_address_packet *)0x580;

      if (drive == 0xffff || (drive == ram_drive && rd_base != 0xffffffff))
      {
	char *disk_sector;
	char *buf_address;
	
	if (nsec <=0 || nsec >= 0x80)
		return 1;	/* failure */
	
	disk_sector = (char *)((sector<<9) + ((drive==0xffff) ? 0 : rd_base));
	buf_address = (char *)(segment<<4);

	if (read)	/* read == 1 really means write to DISK */
		grub_memmove (disk_sector, buf_address, nsec << 9);
	else		/* read == 0 really means read from DISK */
		grub_memmove (buf_address, disk_sector, nsec << 9);
		
	return 0;	/* success */
      }

      dap->length = 0x10;
      dap->block = sector;
      dap->blocks = nsec;
      dap->reserved = 0;
      dap->buffer = segment << 16;
      
      err = biosdisk_int13_extensions ((read + 0x42) << 8, (unsigned char)drive, dap);

      if (!err)
	return 0;	/* success */

      /* bootable CD-ROM specification has no standard CHS-mode call */
      if (geometry->flags & BIOSDISK_FLAG_CDROM)
      {
#ifndef STAGE1_5
	if (debug > 1)
	  grub_printf ("biosdisk_int13_extensions read=%d, drive=0x%x, dap=%x, err=0x%x\n", read, drive, dap, err);
#endif
	return err;
      }

      if (geometry->flags & BIOSDISK_FLAG_BIFURCATE)
	return err;

    } /* if (geometry->flags & BIOSDISK_FLAG_LBA_EXTENSION) */

   /* try the standard CHS mode */
  
    {
      int cylinder_offset, head_offset, sector_offset;
      int head;

      /* SECTOR_OFFSET is counted from one, while HEAD_OFFSET and
	 CYLINDER_OFFSET are counted from zero.  */
      sector_offset = sector % geometry->sectors + 1;
      head = sector / geometry->sectors;
      head_offset = head % geometry->heads;
      cylinder_offset = head / geometry->heads;
      
      err = biosdisk_standard (read + 0x02, drive,
			       cylinder_offset, head_offset, sector_offset,
			       nsec, segment);
    }

  return err;
}

/* Check bootable CD-ROM emulation status. Return 0 on failure. */
int
get_cdinfo (int drive, struct geometry *geometry)
{
  int err;
  struct iso_spec_packet
  {
    unsigned char size;
    unsigned char media_type;
    unsigned char drive_no;
    unsigned char controller_no;
    unsigned long image_lba;
    unsigned short device_spec;
    unsigned short cache_seg;
    unsigned short load_seg;
    unsigned short length_sec512;
    unsigned char cylinders;
    unsigned char sectors;
    unsigned char heads;
    
    unsigned char dummy[16];
  } __attribute__ ((packed));
  
  struct iso_spec_packet *cdrp;
  
  cdrp = (struct iso_spec_packet *)0x580;
  grub_memset (cdrp, 0, sizeof (struct iso_spec_packet));
  cdrp->size = sizeof (struct iso_spec_packet) - 16;

#ifndef STAGE1_5
  if (debug > 1)
	grub_printf (" int13/4B01(%X),", drive);
#endif
  err = biosdisk_int13_extensions (0x4B01, drive, cdrp);
#ifndef STAGE1_5
  if (debug > 1)
	grub_printf ("err=%X,drive=%X, ", err, drive);
#endif

  if (drive == 0x7F && drive < (unsigned long)(cdrp->drive_no))
	drive = cdrp->drive_no;

  if (! err && cdrp->drive_no == drive && !(cdrp->media_type & 0x0F))
    {
	/* No-emulation mode bootable CD-ROM */
	geometry->flags = BIOSDISK_FLAG_LBA_EXTENSION | BIOSDISK_FLAG_CDROM;
	geometry->cylinders = 65536;
	geometry->heads = 255;
	geometry->sectors = 15;
	geometry->sector_size = 2048;
	geometry->total_sectors = 65536 * 255 * 15;
	return drive;
    }
  return 0;	/* failure */
}

static unsigned long flags;
static unsigned long cylinders;
static unsigned long heads;
static unsigned long sectors;


/* Return the geometry of DRIVE in GEOMETRY. If an error occurs, return
   non-zero, otherwise zero.  */
int
get_diskinfo (int drive, struct geometry *geometry)
{
  int err;
  int version;
  unsigned long long total_sectors = 0, tmp = 0;

  if (drive == 0xffff)	/* memory disk */
    {
      unsigned long long total_mem_bytes;

      total_mem_bytes = 0;

      if (mbi.flags & MB_INFO_MEM_MAP)
        {
          struct AddrRangeDesc *map = (struct AddrRangeDesc *) saved_mmap_addr;
          unsigned long end_addr = saved_mmap_addr + saved_mmap_length;

          for (; end_addr > (unsigned long) map; map = (struct AddrRangeDesc *) (((int) map) + 4 + map->size))
	    {
	      unsigned long long top_end;

	      if (map->Type != MB_ARD_MEMORY)
		  continue;
	      top_end =  map->BaseAddr + map->Length;
	      if (top_end > 0x100000000ULL)
		  top_end = 0x100000000ULL;
	      if (total_mem_bytes < top_end)
		  total_mem_bytes = top_end;

	    }
        }
      else
	  grub_printf ("Address Map BIOS Interface is not activated.\n");

      if (total_mem_bytes)
      {
	geometry->flags = BIOSDISK_FLAG_LBA_EXTENSION;
	geometry->sector_size = SECTOR_SIZE;
	geometry->total_sectors = (total_mem_bytes /*+ SECTOR_SIZE - 1*/) >> SECTOR_BITS;
	geometry->heads = 255;
	geometry->sectors = 63;
	geometry->cylinders = (geometry->total_sectors + 255 * 63 -1) / (255 * 63);
	return 0;
      }
      
    } else if (drive == ram_drive)	/* ram disk device */
    {
      if (rd_base != 0xffffffff)
      {
	geometry->flags = BIOSDISK_FLAG_LBA_EXTENSION;
	geometry->sector_size = SECTOR_SIZE;
	geometry->total_sectors = (rd_size ? ((rd_size + SECTOR_SIZE - 1)>> SECTOR_BITS) : 0x800000);
	geometry->heads = 255;
	geometry->sectors = 63;
	geometry->cylinders = (geometry->total_sectors + 255 * 63 -1) / (255 * 63);
	return 0;
      }
    }

#if defined(GRUB_UTIL) || defined(STAGE1_5)
  if (drive == cdrom_drive)
#else
  if (drive == cdrom_drive || (drive >= (unsigned char)min_cdrom_id && drive < (unsigned char)(min_cdrom_id + atapi_dev_count)))
#endif
  {
	/* No-emulation mode bootable CD-ROM */
	geometry->flags = BIOSDISK_FLAG_LBA_EXTENSION | BIOSDISK_FLAG_CDROM;
	geometry->cylinders = 65536;
	geometry->heads = 255;
	geometry->sectors = 15;
	geometry->sector_size = 2048;
	geometry->total_sectors = 65536 * 255 * 15;
	return 0;
  }

  /* Clear the flags.  */
  flags = 0;

#ifdef GRUB_UTIL
#define FIND_DRIVES 8
#else
#define FIND_DRIVES (*((char *)0x475))
#endif
      if (((unsigned char)drive) >= 0x80 + FIND_DRIVES /* || (version && (drive & 0x80)) */ )
	{
	  /* Possible CD-ROM - check the status.  */
	  if (get_cdinfo ((unsigned char)drive, geometry))
	    return 0;
	}
      
#if (! defined(GRUB_UTIL)) && (! defined(STAGE1_5))
    {
	unsigned long j;
	unsigned long d;

	/* check if the drive is virtual. */
	d = (unsigned char)drive;
	j = DRIVE_MAP_SIZE;		/* real drive */
	if (! unset_int13_handler (1))
	    for (j = 0; j < DRIVE_MAP_SIZE; j++)
	    {
		if (drive_map_slot_empty (hooked_drive_map[j]))
		{
			j = DRIVE_MAP_SIZE;	/* real drive */
			break;
		}

		if (((unsigned char)drive) != hooked_drive_map[j].from_drive)
			continue;
		if ((hooked_drive_map[j].max_sector & 0x3E) == 0 && hooked_drive_map[j].start_sector == 0 && hooked_drive_map[j].sector_count <= 1)
		{
			/* this is a map for the whole drive. */
			d = hooked_drive_map[j].to_drive;
			j = DRIVE_MAP_SIZE;	/* real drive */
		}
		break;
	    }

	if (j == DRIVE_MAP_SIZE)	/* real drive */
	{
	    if (d >= 0x80 && d < 0x84)
	    {
		d -= 0x80;
		if (hd_geom[d].sector_size == 512 && hd_geom[d].sectors > 0 && hd_geom[d].sectors <= 63 && hd_geom[d].heads <= 256)
		{
			geometry->flags = hd_geom[d].flags;
			if ((geometry->flags & BIOSDISK_FLAG_BIFURCATE) && (drive & 0xFFFFFF00) == 0x100)
			{
				if (geometry->flags & BIOSDISK_FLAG_CDROM)
				{
					geometry->cylinders = 65536;
					geometry->heads = 255;
					geometry->sectors = 15;
					geometry->sector_size = 2048;
					geometry->total_sectors = 65536 * 255 * 15;
					return 0;
				}
			}
			geometry->sector_size = hd_geom[d].sector_size;
			geometry->total_sectors = hd_geom[d].total_sectors;
			geometry->heads = hd_geom[d].heads;
			geometry->sectors = hd_geom[d].sectors;
			geometry->cylinders = hd_geom[d].cylinders;
			return 0;
		}
	    } else if (d < 4) {
		if (fd_geom[d].sector_size == 512 && fd_geom[d].sectors > 0 && fd_geom[d].sectors <= 63 && fd_geom[d].heads <= 256)
		{
			geometry->flags = fd_geom[d].flags;
			if ((geometry->flags & BIOSDISK_FLAG_BIFURCATE) && (drive & 0xFFFFFF00) == 0x100)
			{
				if (geometry->flags & BIOSDISK_FLAG_CDROM)
				{
					geometry->cylinders = 65536;
					geometry->heads = 255;
					geometry->sectors = 15;
					geometry->sector_size = 2048;
					geometry->total_sectors = 65536 * 255 * 15;
					return 0;
				}
			}
			geometry->sector_size = fd_geom[d].sector_size;
			geometry->total_sectors = fd_geom[d].total_sectors;
			geometry->heads = fd_geom[d].heads;
			geometry->sectors = fd_geom[d].sectors;
			geometry->cylinders = fd_geom[d].cylinders;
			return 0;
		}
	    }
	}
    }
#endif

#ifndef STAGE1_5
	if (debug > 1)      
		grub_printf (" int13/41(%X),", drive);
#endif
	version = check_int13_extensions ((unsigned char)drive);
#ifndef STAGE1_5
	if (debug > 1)      
		grub_printf ("version=%X, ", version);
#endif

	/* Set the LBA flag.  */
	if (version & 1) /* support functions 42h-44h, 47h-48h */
	{
		flags = BIOSDISK_FLAG_LBA_EXTENSION;
	}
	total_sectors = 0;

#ifndef STAGE1_5
	if (debug > 1)
		grub_printf (" int13/08(%X),", drive);
#endif

	version = get_diskinfo_standard ((unsigned char)drive, &cylinders, &heads, &sectors);

#ifndef STAGE1_5
	if (debug > 1)
		grub_printf ("version=%X, C/H/S=%d/%d/%d, ", version, cylinders, heads, sectors);
#endif

#ifndef STAGE1_5
	if (debug > 1)
		grub_printf (" int13/02(%X),", drive);
#endif

	/* read the boot sector: int 13, AX=0x201, CX=1, DH=0 */
	err = biosdisk_standard (0x02, (unsigned char)drive, 0, 0, 1, 1, 0x5F00/*SCRATCHSEG*/);

#ifndef STAGE1_5
	if (debug > 1)
		grub_printf ("err=%X, ", err);
#endif

	//version = 0;

	/* try again using LBA */
	if (flags & BIOSDISK_FLAG_LBA_EXTENSION || ((unsigned char)drive) >= 0x80 + FIND_DRIVES)
	{
		struct disk_address_packet
		{
			unsigned char length;
			unsigned char reserved;
			unsigned short blocks;
			unsigned long buffer;
			unsigned long long block;

			unsigned char dummy[16];
		} __attribute__ ((packed)) *dap;

		dap = (struct disk_address_packet *)0x580;

		dap->length = 0x10;
		dap->reserved = 0;
		dap->blocks = 1;
		dap->buffer = 0x5F80/*SCRATCHSEG*/ << 16;
		dap->block = 0;

		/* set a known value */
		grub_memset ((char *)0x5F800, 0xEC, 0x800);
		version = biosdisk_int13_extensions (0x4200, (unsigned char)drive, dap);
		/* see if it is a big sector */
		{
			char *p;
			for (p = (char *)0x5FA00; p < (char *)0x60000; p++)
			{
				if ((*p) != (char)0xEC)
				{
					flags |= BIOSDISK_FLAG_CDROM | BIOSDISK_FLAG_LBA_EXTENSION;
					if (! err)
						flags |= BIOSDISK_FLAG_BIFURCATE;
					break;
				}
			}
		}
		if ((! version) && (! err))
		{
			if (grub_memcmp ((char *)0x5F000, (char *)0x5F800, 0x200))
			{
				flags |= BIOSDISK_FLAG_BIFURCATE;
			}
		}
		if (err && ! (flags & BIOSDISK_FLAG_BIFURCATE) && !(flags & BIOSDISK_FLAG_CDROM))
		{
			grub_memmove ((char *)0x5F000, (char *)0x5F800, 0x200);
		}

	} /* if (geometry->flags & BIOSDISK_FLAG_LBA_EXTENSION) */

	if (err && version)
		return err; /* When we return with ERROR, we should not change the geometry!! */

	geometry->flags = flags;

	if (err && (flags & BIOSDISK_FLAG_CDROM))
	{
		geometry->cylinders = 65536;
		geometry->heads = 255;
		geometry->sectors = 15;
		geometry->sector_size = 2048;
		geometry->total_sectors = 65536 * 255 * 15;
		return 0;
	}

	geometry->cylinders = cylinders;
	geometry->heads = heads;
	geometry->sectors = sectors;
	geometry->sector_size = SECTOR_SIZE;
	if (geometry->heads > 256)
	    geometry->heads = 256;
	if (geometry->sectors * geometry->sector_size > 63 * 512)
	    geometry->sectors = 63 * 512 / geometry->sector_size;
	tmp = (unsigned long long)(geometry->cylinders) *
	      (unsigned long long)(geometry->heads) *
	      (unsigned long long)(geometry->sectors);
	if (total_sectors < tmp)
	    total_sectors = tmp;
	geometry->total_sectors = total_sectors;

	/* successfully read boot sector */

#ifndef STAGE1_5
	if (drive & 0x80)
	{
		/* hard disk */
		if ((err = probe_mbr((struct master_and_dos_boot_sector *)0x5F000/*SCRATCHADDR*/, 0, total_sectors, 0)))
		{
			if (debug > 1)
				grub_printf ("\nWarning: Unrecognized partition table for drive %X. Please rebuild it using\na Microsoft-compatible FDISK tool(err=%d). Current C/H/S=%d/%d/%d\n", drive, err, geometry->cylinders, geometry->heads, geometry->sectors);
			goto failure_probe_boot_sector;
		}
		err = (int)"MBR";
	}else{
		/* floppy */
		if (probe_bpb((struct master_and_dos_boot_sector *)0x5F000/*SCRATCHADDR*/))
		{
			goto failure_probe_boot_sector;
		}

		err = (int)"BPB";
	}

	if (drive & 0x80)
	if (probed_cylinders != geometry->cylinders)
	    if (debug > 1)
		grub_printf ("\nWarning: %s cylinders(%d) is not equal to the BIOS one(%d).\n", (char *)err, probed_cylinders, geometry->cylinders);

	geometry->cylinders = probed_cylinders;

	if (probed_heads != geometry->heads)
	    if (debug > 1)
		grub_printf ("\nWarning: %s heads(%d) is not equal to the BIOS one(%d).\n", (char *)err, probed_heads, geometry->heads);

	geometry->heads	= probed_heads;

	if (probed_sectors_per_track != geometry->sectors)
	    if (debug > 1)
		grub_printf ("\nWarning: %s sectors per track(%d) is not equal to the BIOS one(%d).\n", (char *)err, probed_sectors_per_track, geometry->sectors);

	geometry->sectors = probed_sectors_per_track;

	if (probed_total_sectors > total_sectors)
	{
	    if (drive & 0x80)
	    if (debug > 1)
		grub_printf ("\nWarning: %s total sectors(%d) is greater than the BIOS one(%d).\nSome buggy BIOSes could hang when you access sectors exceeding the BIOS limit.\n", (char *)err, probed_total_sectors, total_sectors);
	    geometry->total_sectors	= probed_total_sectors;
	}

	if (drive & 0x80)
	if (probed_total_sectors < total_sectors)
	    if (debug > 1)
		grub_printf ("\nWarning: %s total sectors(%d) is less than the BIOS one(%d).\n", (char *)err, probed_total_sectors, total_sectors);

failure_probe_boot_sector:
	
#ifndef GRUB_UTIL
#if 1
	if (!(geometry->flags & BIOSDISK_FLAG_LBA_EXTENSION) && ! ((*(char *)0x8205) & 0x08))
	{
		err = geometry->heads;
		version = geometry->sectors;

		/* DH non-zero for geometry_tune */
		get_diskinfo_standard (drive | 0x0100, &geometry->cylinders, &geometry->heads, &geometry->sectors);

		if (debug > 0)
		{
		    if (err != geometry->heads)
			grub_printf ("\nNotice: number of heads for drive %X tuned from %d to %d.\n", drive, err, geometry->heads);
		    if (version != geometry->sectors)
			grub_printf ("\nNotice: sectors-per-track for drive %X tuned from %d to %d.\n", drive, version, geometry->sectors);
		}
	}
#endif
#endif

	/* if C/H/S=0/0/0, use a safe default one. */
	if (geometry->sectors == 0)
	{
		if (drive & 0x80)
		{
			/* hard disk */
			geometry->sectors = 63;
		}else{
			/* floppy */
			if (geometry->total_sectors > 5760)
				geometry->sectors = 63;
			else if (geometry->total_sectors > 2880)
				geometry->sectors = 36;
			else
				geometry->sectors = 18;
		}
	}
	if (geometry->heads == 0)
	{
		if (drive & 0x80)
		{
			/* hard disk */
			geometry->heads = 255;
		}else{
			/* floppy */
			if (geometry->total_sectors > 5760)
				geometry->heads = 255;
			else
				geometry->heads = 2;
		}
	}
	if (geometry->cylinders == 0)
	{
		geometry->cylinders = (geometry->total_sectors / geometry->heads / geometry->sectors);
	}

	if (geometry->cylinders == 0)
		geometry->cylinders = 1;
#endif	/* ! STAGE1_5 */

  /* backup the geometry into array hd_geom or fd_geom. */

#if (! defined(GRUB_UTIL)) && (! defined(STAGE1_5))
    {
	unsigned long j;
	unsigned long d;

	/* check if the drive is virtual. */
	d = (unsigned char)drive;
	j = DRIVE_MAP_SIZE;		/* real drive */
	if (! unset_int13_handler (1))
	    for (j = 0; j < DRIVE_MAP_SIZE; j++)
	    {
		if (drive_map_slot_empty (hooked_drive_map[j]))
		{
			j = DRIVE_MAP_SIZE;	/* real drive */
			break;
		}

		if (((unsigned char)drive) != hooked_drive_map[j].from_drive)
			continue;
		if ((hooked_drive_map[j].max_sector & 0x3E) == 0 && hooked_drive_map[j].start_sector == 0 && hooked_drive_map[j].sector_count <= 1)
		{
			/* this is a map for the whole drive. */
			d = hooked_drive_map[j].to_drive;
			j = DRIVE_MAP_SIZE;	/* real drive */
		}
		break;
	    }

	if (j == DRIVE_MAP_SIZE)	/* real drive */
	{
	    if (d >= 0x80 && d < 0x84)
	    {
		d -= 0x80;
		if (hd_geom[d].sector_size != 512 || hd_geom[d].sectors <= 0 || hd_geom[d].sectors > 63 || hd_geom[d].heads > 256)
		{
			hd_geom[d].flags		= geometry->flags;
			hd_geom[d].sector_size		= geometry->sector_size;
			hd_geom[d].total_sectors	= geometry->total_sectors;
			hd_geom[d].heads		= geometry->heads;
			hd_geom[d].sectors		= geometry->sectors;
			hd_geom[d].cylinders		= geometry->cylinders;
		}
	    } else if (d < 4) {
		if (fd_geom[d].sector_size != 512 || fd_geom[d].sectors <= 0 || fd_geom[d].sectors > 63 || fd_geom[d].heads > 256)
		{
			fd_geom[d].flags		= geometry->flags;
			fd_geom[d].sector_size		= geometry->sector_size;
			fd_geom[d].total_sectors	= geometry->total_sectors;
			fd_geom[d].heads		= geometry->heads;
			fd_geom[d].sectors		= geometry->sectors;
			fd_geom[d].cylinders		= geometry->cylinders;
		}
	    }
	}
    }
	if ((geometry->flags & BIOSDISK_FLAG_BIFURCATE) && (drive & 0xFFFFFF00) == 0x100)
	{
		if (geometry->flags & BIOSDISK_FLAG_CDROM)
		{
			geometry->cylinders = 65536;
			geometry->heads = 255;
			geometry->sectors = 15;
			geometry->sector_size = 2048;
			geometry->total_sectors = 65536 * 255 * 15;
		}
	}
#endif

  return 0;
}

#undef FIND_DRIVES


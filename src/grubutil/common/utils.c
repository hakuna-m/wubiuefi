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

#include <string.h>
#include "utils.h"

#define valueat(buf,ofs,type)	*((type*)(((char*)&buf)+ofs))

#define EXT2_SUPER_MAGIC      0xEF53

int mbr_nhd, mbr_spt;

#ifdef DOS

void
split_chs (unsigned char *chs, unsigned long *c, unsigned long *h,
	   unsigned long *s)
{
  *h = chs[0];
  *s = (chs[1] & 0x3F) - 1;
  *c = ((unsigned long) (chs[1] >> 6)) * 256 + chs[2];
}

int
chk_chs (unsigned long nhd, unsigned long spt, unsigned long lba,
	 unsigned char *chs)
{
  unsigned long c1, h1, s1, c2, h2, s2;

  split_chs (chs, &c1, &h1, &s1);
  c2 = lba / (nhd * spt);
  lba = lba % (nhd * spt);
  h2 = lba / spt;
  s2 = lba % spt;
  if (c2 > 0x3FF)
    c2 = 0x3FF;
  return ((c1 == c2) && (h1 == h2) && (s1 == s2));
}

int
chk_mbr (unsigned char *buf)
{
  unsigned long nhd, spt, a1, a2, c2, h2, s2;
  int i;

  i = 0x1BE;
  while ((i < 0x1FE) && (buf[i + 4] == 0))
    i += 16;
  if (i >= 0x1FE)
    return 0;
  a1 = valueat (buf[i], 8, unsigned long);
  a2 = a1 + valueat (buf[i], 12, unsigned long) - 1;
  if (a1 >= a2)
    return 0;
  split_chs (buf + i + 5, &c2, &h2, &s2);
  if (c2 == 0x3FF)
    {
      nhd = h2 + 1;
      spt = s2 + 1;
      if (!chk_chs (nhd, spt, a1, buf + i + 1))
	return 0;
    }
  else
    {
      unsigned long c1, h1, s1;
      long n1, n2;

      split_chs (buf + i + 1, &c1, &h1, &s1);
      if ((c1 == 0x3FF) || (c1 > c2))
	return 0;
      n1 =
	(long) (c1 * a2) - (long) (c2 * a1) - (long) (c1 * s2) +
	(long) (c2 * s1);
      n2 = (long) (c1 * h2) - (long) (c2 * h1);
      if (n2 < 0)
	{
	  n2 = -n2;
	  n1 = -n1;
	}
      if ((n2 == 0) || (n1 <= 0) || (n1 % n2))
	return 0;
      spt = (unsigned long) (n1 / n2);
      if (c2)
	{
	  n1 = (long) a2 - (long) s2 - (long) (h2 * spt);
	  n2 = (long) (c2 * spt);
	  if ((n2 == 0) || (n1 <= 0) || (n1 % n2))
	    return 0;
	  nhd = (unsigned long) (n1 / n2);
	}
      else
	nhd = h2 + 1;
    }
  if ((nhd == 0) || (nhd > 255) || (spt == 0) || (spt > 63))
    return 0;
  i += 16;
  while (i < 0x1FE)
    {
      if (buf[i + 4])
	{
	  if ((!chk_chs
	       (nhd, spt, valueat (buf[i], 8, unsigned long), buf + i + 1))
	      ||
	      (!chk_chs
	       (nhd, spt,
		valueat (buf[i], 8, unsigned long) + valueat (buf[i], 12,
							      unsigned long) -
		1, buf + i + 5)))
	      return 0;
	}
      i += 16;
    }
  mbr_nhd = (int) nhd;
  mbr_spt = (int) spt;
  return 1;
}

#else

#ifdef __GNUC__
#define PACKED	__attribute__ ((packed))
#else
#define PACKED
#endif

struct master_and_dos_boot_sector
{
  /* 00 */ char dummy1[0x0b];
  /* at offset 0, normally there is a short JMP instuction(opcode is 0xEB) */
  /* 0B */ unsigned short bytes_per_sector;
  /* seems always to be 512, so we just use 512 */
  /* 0D */ unsigned char sectors_per_cluster;
  /* non-zero, the power of 2, i.e., 2^n */
  /* 0E */ unsigned short reserved_sectors;
  /* FAT=non-zero, NTFS=0? */
  /* 10 */ unsigned char number_of_fats;
  /* NTFS=0; FAT=1 or 2  */
  /* 11 */ unsigned short root_dir_entries;
  /* FAT32=0, NTFS=0, FAT12/16=non-zero */
  /* 13 */ unsigned short total_sectors_short;
  /* FAT32=0, NTFS=0, FAT12/16=any */
  /* 15 */ unsigned char media_descriptor;
  /* range from 0xf0 to 0xff */
  /* 16 */ unsigned short sectors_per_fat;
  /* FAT32=0, NTFS=0, FAT12/16=non-zero */
  /* 18 */ unsigned short sectors_per_track;
  /* range from 1 to 63 */
  /* 1A */ unsigned short total_heads;
  /* range from 1 to 256 */
  /* 1C */ unsigned long hidden_sectors;
  /* any value */
  /* 20 */ unsigned long total_sectors_long;
  /* FAT32=non-zero, NTFS=0, FAT12/16=any */
  /* 24 */ unsigned long sectors_per_fat32;
  /* FAT32=non-zero, NTFS=any, FAT12/16=any */
  /* 28 */ unsigned long total_sectors_long_1;
  /* NTFS=non-zero, FAT12/16/32=any */
  /* 28 */ unsigned long total_sectors_long_2;
  /* NTFS=non-zero, FAT12/16/32=any */
  /* 30 */ char dummy2[0x18e];

  /* Partition Table, starting at offset 0x1BE */
  /* 1BE */ struct
  {
    /* +00 */ unsigned char boot_indicator;
    /* +01 */ unsigned char start_head;
    /* +02 */ unsigned short start_sector_cylinder;
    /* +04 */ unsigned char system_indicator;
    /* +05 */ unsigned char end_head;
    /* +06 */ unsigned short end_sector_cylinder;
    /* +08 */ unsigned long start_lba;
    /* +0C */ unsigned long total_sectors;
    /* +10 */
  } P[4];
  /* 1FE */ unsigned short boot_signature;
  /* 0xAA55 */
#if 0
  /* This starts at offset 0x200 */
  /* 200 */ unsigned long probed_total_sectors;
  /* 204 */ unsigned long probed_heads;
  /* 208 */ unsigned long probed_sectors_per_track;
  /* 20C */ unsigned long probed_cylinders;
  /* 210 */ unsigned long sectors_per_cylinder;
  /* 214 */ char dummy3[0x0c];

  /* matrix of coefficients of linear equations
   *
   *   C[n] * (H_count * S_count) + H[n] * S_count = LBA[n] - S[n] + 1
   *
   * where n = 1, 2, 3, 4, 5, 6, 7, 8
   */
  /* This starts at offset 0x130 */
  /* 220 */ long long L[9];
  /* L[n] == LBA[n] - S[n] + 1 */
  /* 268 */ long H[9];
  /* 28C */ short C[9];
  /* 29E */ short X;
  /* 2A0 */ short Y;
  /* 2A2 */ short Cmax;
  /* 2A4 */ long Hmax;
  /* 2A8 */ unsigned long Z;
  /* 2AC */ short Smax;
  /* 2AE */
#endif
} PACKED;


int
probe_mbr (struct master_and_dos_boot_sector *BS, unsigned long start_sector1,
	   unsigned long sector_count1, unsigned long part_start1)
{
  unsigned long j, i;
  unsigned long probed_total_sectors;
  unsigned long probed_heads;
  unsigned long probed_sectors_per_track;
  unsigned long probed_cylinders;
  unsigned long sectors_per_cylinder;

  /* matrix of coefficients of linear equations
   *
   *   C[n] * (H_count * S_count) + H[n] * S_count = LBA[n] - S[n] + 1
   *
   * where n = 1, 2, 3, 4, 5, 6, 7, 8
   */
  /* This starts at offset 0x130 */
  long long L[9];		/* L[n] == LBA[n] - S[n] + 1 */
  long H[9];
  short C[9];
  short X;
  short Y;
  short Cmax;
  long Hmax;
  short Smax;
  unsigned long Z;

  /* probe the partition table */

  Cmax = 0;
  Hmax = 0;
  Smax = 0;
  for (i = 0; i < 4; i++)
    {
      /* the boot indicator must be 0x80 (for bootable) or 0 (for non-bootable) */
      if ((unsigned char) (BS->P[i].boot_indicator << 1))	/* if neither 0x80 nor 0 */
	return 1;
      /* check if the entry is empty, i.e., all the 16 bytes are 0 */
      if (*(long long *) (void *) &(BS->P[i].boot_indicator)
	  || *(long long *) (void *) &(BS->P[i].start_lba))
	{
	  /* valid partitions never start at 0, because this is where the MBR
	   * lives; and more, the number of total sectors should be non-zero.
	   */
	  if (!BS->P[i].start_lba || !BS->P[i].total_sectors)
	    return 2;
	  /* the partitions should not overlap each other */
	  for (j = 0; j < i; j++)
	    {
	      if ((BS->P[j].start_lba <= BS->P[i].start_lba)
		  && (BS->P[j].start_lba + BS->P[j].total_sectors >=
		      BS->P[i].start_lba + BS->P[i].total_sectors))
		continue;
	      if ((BS->P[j].start_lba >= BS->P[i].start_lba)
		  && (BS->P[j].start_lba + BS->P[j].total_sectors <=
		      BS->P[i].start_lba + BS->P[i].total_sectors))
		continue;
	      if ((BS->P[j].start_lba < BS->P[i].start_lba) ?
		  (BS->P[i].start_lba - BS->P[j].start_lba <
		   BS->P[j].total_sectors) : (BS->P[j].start_lba -
					      BS->P[i].start_lba <
					      BS->P[i].total_sectors))
		return 3;
	    }
	  /* the cylinder number */
	  C[i] =
	    (BS->P[i].
	     start_sector_cylinder >> 8) | ((BS->P[i].
					     start_sector_cylinder & 0xc0) <<
					    2);
	  if (Cmax < C[i])
	    Cmax = C[i];
	  H[i] = BS->P[i].start_head;
	  if (Hmax < H[i])
	    Hmax = H[i];
	  X = BS->P[i].start_sector_cylinder & 0x3f;	/* the sector number */
	  if (Smax < X)
	    Smax = X;
	  /* the sector number should not be 0. */
	  /* partitions should not start at the first track, the MBR-track */
	  if (!X || BS->P[i].start_lba < Smax /* X - 1 */ )
	    return 4;
	  L[i] = BS->P[i].start_lba - X + 1;
	  if (start_sector1 == part_start1)	/* extended partition is pretending to be a whole drive */
	    L[i] += (unsigned long) part_start1;

	  C[i + 4] =
	    (BS->P[i].
	     end_sector_cylinder >> 8) | ((BS->P[i].
					   end_sector_cylinder & 0xc0) << 2);
	  if (Cmax < C[i + 4])
	    Cmax = C[i + 4];
	  H[i + 4] = BS->P[i].end_head;
	  if (Hmax < H[i + 4])
	    Hmax = H[i + 4];
	  Y = BS->P[i].end_sector_cylinder & 0x3f;
	  if (Smax < Y)
	    Smax = Y;
	  if (!Y)
	    return 5;
	  L[i + 4] = BS->P[i].start_lba + BS->P[i].total_sectors;
	  if (L[i + 4] < Y)
	    return 6;
	  L[i + 4] -= Y;
	  if (start_sector1 == part_start1)	/* extended partition is pretending to be a whole drive */
	    L[i + 4] += (unsigned long) part_start1;

	  /* C[n] * (H_count * S_count) + H[n] * S_count = LBA[n] - S[n] + 1 = L[n] */

	  /* C[n] * (H * S) + H[n] * S = L[n] */

	  /* Check the large disk partition -- Win98 */
	  if (Y == 63 && H[i + 4] == Hmax && C[i + 4] == Cmax
	      && (Hmax >= 254 || Cmax >= 1022)
	      /* && C[i+4] == 1023 */
	      && (Cmax + 1) * (Hmax + 1) * 63 < L[i + 4] + Y
	      /* && C[i] * (Hmax + 1) * 63 + H[i] * 63 + X - 1 == BS->P[i].start_lba */
	    )
	    {
	      //grub_printf ("LargeDiskWin98_001 i=%d, C[i]=%d, Hmax=%d, H[i]=%d, L[i]=%d\n", i, C[i], Hmax, H[i], L[i]);
	      if (C[i] * (Hmax + 1) * 63 + H[i] * 63 > L[i])
		return 7;
	      //grub_printf ("LargeDiskWin98_002 i=%d\n", i);
	      if (C[i] * (Hmax + 1) * 63 + H[i] * 63 < L[i])
		{
		  /* calculate CHS numbers from start LBA */
		  if (X != ((unsigned long) L[i] % 63) + 1 && X != 63)
		    return 8;
		  if (H[i] != ((unsigned long) L[i] / 63) % (Hmax + 1)
		      && H[i] != Hmax)
		    return 9;
		  if (C[i] !=
		      (((unsigned long) L[i] / 63 / (Hmax + 1)) & 0x3ff)
		      && C[i] != Cmax)
		    return 10;
		}
	      //grub_printf ("LargeDiskWin98_003 i=%d\n", i);
	      C[i] = 0;
	      H[i] = 1;
	      L[i] = 63;
	      C[i + 4] = 1;
	      H[i + 4] = 0;
	      L[i + 4] = (Hmax + 1) * 63;
	    }

	  /* Check the large disk partition -- Win2K */
	  else if (Y == 63 && H[i + 4] == Hmax	/* && C[i+4] == Cmax */
		   && (C[i + 4] + 1) * (Hmax + 1) * 63 < L[i + 4] + Y
		   && !(((unsigned long) L[i + 4] + Y) % ((Hmax + 1) * 63))
		   &&
		   ((((unsigned long) L[i + 4] + Y) / ((Hmax + 1) * 63) -
		     1) & 0x3ff) == C[i + 4])
	    {
	      //grub_printf ("LargeDiskWin2K_001 i=%d\n", i);
	      if (C[i] * (Hmax + 1) * 63 + H[i] * 63 > L[i])
		return 11;
	      //grub_printf ("LargeDiskWin2K_002 i=%d\n", i);
	      if (C[i] * (Hmax + 1) * 63 + H[i] * 63 < L[i])
		{
		  if (((unsigned long) L[i] - H[i] * 63) % ((Hmax + 1) * 63))
		    return 12;
		  //grub_printf ("LargeDiskWin2K_003 i=%d\n", i);
		  if (((((unsigned long) L[i] -
			 H[i] * 63) / ((Hmax + 1) * 63)) & 0x3ff) != C[i])
		    return 13;
		}
	      //grub_printf ("LargeDiskWin2K_004 i=%d\n", i);
	      C[i] = 0;
	      H[i] = 1;
	      L[i] = 63;
	      C[i + 4] = 1;
	      H[i + 4] = 0;
	      L[i + 4] = (Hmax + 1) * 63;
	    }

	  /* Maximum of C[n] * (H * S) + H[n] * S = 1023 * 255 * 63 + 254 * 63 = 0xFB03C1 */

	  else if (L[i + 4] > 0xFB03C1)	/* Large disk */
	    {
	      /* set H/S to max */
	      if (Hmax < 254)
		Hmax = 254;
	      Smax = 63;
	      if ((unsigned long) L[i + 4] % Smax)
		return 114;
	      if (H[i + 4] != ((unsigned long) L[i + 4] / 63) % (Hmax + 1)
		  && H[i + 4] != Hmax)
		return 115;
	      if (C[i + 4] !=
		  (((unsigned long) L[i + 4] / 63 / (Hmax + 1)) & 0x3ff)
		  && C[i + 4] != Cmax)
		return 116;

	      if (C[i] * (Hmax + 1) * 63 + H[i] * 63 > L[i])
		return 117;
	      if (C[i] * (Hmax + 1) * 63 + H[i] * 63 < L[i])
		{
		  /* calculate CHS numbers from start LBA */
		  if (X != ((unsigned long) L[i] % 63) + 1 && X != 63)
		    return 118;
		  if (H[i] != ((unsigned long) L[i] / 63) % (Hmax + 1)
		      && H[i] != Hmax)
		    return 119;
		  if (C[i] !=
		      (((unsigned long) L[i] / 63 / (Hmax + 1)) & 0x3ff)
		      && C[i] != Cmax)
		    return 120;
		}
	      C[i] = 0;
	      H[i] = 1;
	      L[i] = 63;
	      C[i + 4] = 1;
	      H[i + 4] = 0;
	      L[i + 4] = (Hmax + 1) * 63;
	    }
	}
      else
	{
	  /* empty entry, zero all the coefficients */
	  C[i] = 0;
	  H[i] = 0;
	  L[i] = 0;
	  C[i + 4] = 0;
	  H[i + 4] = 0;
	  L[i + 4] = 0;
	}
    }

  //  for (i = 0; i < 4; i++)
  //    {
  //grub_printf ("%d   \t%d   \t%d\n%d   \t%d   \t%d\n", C[i], H[i],(int)(L[i]), C[i+4], H[i+4],(int)(L[i+4]));
  //    }
  for (i = 0; i < 8; i++)
    {
      if (C[i])
	break;
    }
  if (i == 8)			/* all C[i] == 0 */
    {
      for (i = 0; i < 8; i++)
	{
	  if (H[i])
	    break;
	}
      if (i == 8)		/* all H[i] == 0 */
	return 14;
      for (j = 0; j < i; j++)
	if (L[j])
	  return 15;
      if (!L[i])
	return 16;
      //if (*(long *)((char *)&(L[i]) + 4))
      if (L[i] > 0x7fffffff)
	return 17;
      if ((long) L[i] % H[i])
	return 18;
      probed_sectors_per_track = (long) L[i] / H[i];
      if (probed_sectors_per_track > 63 || probed_sectors_per_track < Smax)
	return 19;
      Smax = probed_sectors_per_track;
      for (j = i + 1; j < 8; j++)
	{
	  if (H[j])
	    {
	      if (probed_sectors_per_track * H[j] != L[j])
		return 20;
	    }
	  else if (L[j])
	    return 21;
	}
      probed_heads = Hmax + 1;
#if 0
      if (sector_count1 == 1)
	probed_cylinders = 1;
      else
#endif
	{
	  L[8] = sector_count1;	/* just set to a number big enough */
	  Z = sector_count1 / probed_sectors_per_track;
	  for (j = probed_heads; j <= 256; j++)
	    {
	      H[8] = Z % j;	/* the remainder */
	      if (L[8] > H[8])
		{
		  L[8] = H[8];	/* the least residue */
		  probed_heads = j;	/* we got the optimum value */
		}
	    }
	  probed_cylinders = Z / probed_heads;
	  if (!probed_cylinders)
	    probed_cylinders = 1;
	}
      sectors_per_cylinder = probed_heads * probed_sectors_per_track;
      probed_total_sectors = sectors_per_cylinder * probed_cylinders;
    }
  else
    {
      if (i > 0)
	{
	  C[8] = C[i];
	  H[8] = H[i];
	  L[8] = L[i];
	  C[i] = C[0];
	  H[i] = H[0];
	  L[i] = L[0];
	  C[0] = C[8];
	  H[0] = H[8];
	  L[0] = L[8];
	}
      H[8] = 0;			/* will store sectors per track */
      for (i = 1; i < 8; i++)
	{
	  H[i] = C[0] * H[i] - C[i] * H[0];
	  L[i] = C[0] * L[i] - C[i] * L[0];
	  if (H[i])
	    {
	      if (H[i] < 0)
		{
		  H[i] = -H[i];	/* H[i] < 0x080000 */
		  L[i] = -L[i];
		}
	      /* Note: the max value of H[i] is 1024 * 256 * 2 = 0x00080000,
	       * so L[i] should be less than 0x00080000 * 64 = 0x02000000 */
	      if (L[i] <= 0 || L[i] > 0x7fffffff)
		return 22;
	      L[8] = ((long) L[i]) / H[i];	/* sectors per track */
	      if (L[8] * H[i] != L[i])
		return 23;
	      if (L[8] > 63 || L[8] < Smax)
		return 24;
	      Smax = L[8];
	      if (H[8])
		{
		  /* H[8] is the old L[8] */
		  if (L[8] != H[8])
		    return 25;
		}
	      else		/* H[8] is empty, so store L[8] for the first time */
		H[8] = L[8];
	    }
	  else if (L[i])
	    return 26;
	}
      if (H[8])
	{
	  /* H[8] is sectors per track */
	  L[0] -= H[0] * H[8];
	  /* Note: the max value of H[8] is 63, the max value of C[0] is 1023,
	   * so L[0] should be less than 64 * 1024 * 256 = 0x01000000    */
	  if (L[0] <= 0 || L[0] > 0x7fffffff)
	    return 27;

	  /* L[8] is number of heads */
	  L[8] = ((long) L[0]) / H[8] / C[0];
	  if (L[8] * H[8] * C[0] != L[0])
	    return 28;
	  if (L[8] > 256 || L[8] <= Hmax)
	    return 29;
	  probed_sectors_per_track = H[8];
	}
      else			/* fail to set L[8], this means all H[i]==0, i=1,2,3,4,5,6,7 */
	{
	  /* Now the only equation is: C[0] * H * S + H[0] * S = L[0] */
	  for (i = 63; i >= Smax; i--)
	    {
	      L[8] = L[0] - H[0] * i;
	      if (L[8] <= 0 || L[8] > 0x7fffffff)
		continue;
	      Z = L[8];
	      if (Z % (C[0] * i))
		continue;
	      L[8] = Z / (C[0] * i);
	      if (L[8] <= 256 && L[8] > Hmax)
		break;		/* we have got the PROBED_HEADS */
	    }
	  if (i < Smax)
	    return 30;
	  probed_sectors_per_track = i;
	}
      probed_heads = L[8];
      sectors_per_cylinder = probed_heads * probed_sectors_per_track;
      probed_cylinders =
	(sector_count1 + sectors_per_cylinder - 1) / sectors_per_cylinder;
      if (probed_cylinders < Cmax + 1)
	probed_cylinders = Cmax + 1;
      probed_total_sectors = sectors_per_cylinder * probed_cylinders;
    }

  mbr_nhd = probed_heads;
  mbr_spt = probed_sectors_per_track;

  /* partition table probe success */
  return 0;
}

int
chk_mbr (unsigned char *buf)
{
  return (probe_mbr ((struct master_and_dos_boot_sector *) buf, 0, 1, 0) ==
	  0);
}

#endif

int
chk_mbr2 (char *buf)
{
  unsigned long pt[4][2];
  int i, pn, bp;

  pn = bp = 0;
  for (i = 0x1BE; i < 0x1FE; i += 16)
    {
      if ((unsigned char) buf[i] == 0x80)
	{
	  if (bp)
	    return 0;
	  else
	    bp = 1;
	}
      else if (buf[i])
	return 0;

      if (buf[i + 4])
	{
	  int j;

	  pt[pn][0] = valueat (buf[i], 8, unsigned long);
	  pt[pn][1] = pt[pn][0] + valueat (buf[i], 12, unsigned long);
	  if ((pt[pn][0] == 0) || (pt[pn][0] >= pt[pn][1]))
	    return 0;

	  for (j = 0; j < pn; j++)
	    if ((pt[pn][0] > pt[j][0]) ? (pt[pn][0] < pt[j][1]) : (pt[pn][1] >
								   pt[j][0]))
	      return 0;

	  pn++;
	}
      else
	{
	  int j;

	  for (j = 0; j < 16; j++)
	    if (buf[i + j])
	      return 0;
	}
    }

  return pn;
}

int
get_fstype (unsigned char *buf)
{
  if (chk_mbr (buf))
    return FST_MBR;

  if (chk_mbr2 (buf))
    return FST_MBR2;

  // The first sector of EXT2 might not contain the 0xAA55 signature
  if (valueat (buf[1024], 56, unsigned short) == EXT2_SUPER_MAGIC)
    return FST_EXT2;
  if (valueat (buf[0], 0x1FE, unsigned short) != 0xAA55)
      return FST_OTHER;
  if (!strncmp (&buf[0x36], "FAT", 3))
    return ((buf[0x26] == 0x28)
	    || (buf[0x26] == 0x29)) ? FST_FAT16 : FST_OTHER;
  if (!strncmp (&buf[0x52], "FAT32", 5))
    return ((buf[0x42] == 0x28)
	    || (buf[0x42] == 0x29)) ? FST_FAT32 : FST_OTHER;
  if (!strncmp (&buf[0x3], "NTFS", 4))
    return ((buf[0] == 0xEB) && (buf[1] == 0x52)) ? FST_NTFS : FST_OTHER;
  return FST_OTHER;
}

char *
fst2str (int fs)
{
  switch (fs)
    {
    case FST_OTHER:
      return "Other";
    case FST_MBR:
      return "MBR";
    case FST_MBR2:
      return "MBR2";
    case FST_FAT16:
      return "FAT12/FAT16";
    case FST_FAT32:
      return "FAT32";
    case FST_NTFS:
      return "NTFS";
    case FST_EXT2:
      return "EXT2/EXT3";
    default:
      return "Unknown";
    }
}

typedef struct
{
  int id;
  char *str;
} fstab_t;

static fstab_t fstab[] = {
  {0x1, "FAT12"},
  {0x4, "FAT16"},
  {0x5, "Extended"},
  {0x6, "FAT16B"},
  {0x7, "NTFS"},
  {0xB, "FAT32"},
  {0xC, "FAT32X"},
  {0xE, "FAT16X"},
  {0xF, "ExtendedX"},
  {0x11, "(H)FAT12"},
  {0x14, "(H)FAT16"},
  {0x16, "(H)FAT16B"},
  {0x17, "(H)NTFS"},
  {0x1B, "(H)FAT32"},
  {0x1C, "(H)FAT32X"},
  {0x1E, "(H)FAT16X"},
  {0x82, "Swap"},
  {0x83, "Ext2"},
  {0xA5, "FBSD"},
  {0, "Other"}
};

char *
dfs2str (int fs)
{
  int i;

  for (i = 0; fstab[i].id; i++)
    if (fs == fstab[i].id)
      return fstab[i].str;
  return fstab[i].str;
}

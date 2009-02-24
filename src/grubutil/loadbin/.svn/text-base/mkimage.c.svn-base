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

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <getopt.h>
#include <errno.h>

#define BUF_SIZE	16384

#define OFS_HLEN	0x1F1
#define OFS_REDX	0x260
#define OFS_DLEN	0x264

#define APP_NAME	"mkimage"

#define valueat(buf,ofs,type)	*((type*)(((char*)&buf)+ofs))

void usage(int status)
{
  fprintf(stderr,
          "Usage:\n"
          "  mkimage [OPTIONS] header [image] output\n\n"
          "Options:\n"
          "  -d\t\tdrive[,part]\tSet default drive and partition\n");
  exit(status);
}

void quit(int syserr,char *fmt, ...)
{
  va_list argptr;

  va_start(argptr, fmt);

  fprintf(stderr, APP_NAME ": ");
  vfprintf(stderr, fmt, argptr);
  if (syserr)
    fprintf(stderr,": %s\n", strerror(errno));
  else
    fprintf(stderr,"\n");

  va_end(argptr);

  exit(1);
}

unsigned char buf[BUF_SIZE];

int main(int argc, char **argv)
{
  char ch,*pout;
  FILE *fin,*fout;
  long ofs,len,i;
  unsigned long edx;

  edx=0xFFFFFFFF;
  while ((ch=getopt(argc,argv, "hd:"))!= -1)
    switch (ch) {
    case 'd':
      {
        unsigned long drive,part;
        char *pp;

        drive=(strtoul(optarg,&pp,0) & 0xFF);
        if (*pp==',')
          part=(strtoul(pp+1,NULL,0) & 0xFF);
        else
          part=0xFF;
        edx=drive + (part << 16) + 0xFFFF0000;
        break;
      }
    case 'h':
    default:
      usage(0);
    }

  if ((optind + 2 != argc) && (optind + 3 !=argc))
    usage(1);

  fin=fopen(argv[optind], "rb");
  if (fin == NULL)
    quit(1, "Unable to open %s", argv[optind]);

  fseek(fin,0,SEEK_END);
  len = ftell(fin);
  if (len >= BUF_SIZE)
    {
      fclose(fin);
      quit(0, "%s too long", argv[optind]);
    }

  fseek(fin, 0, SEEK_SET);
  if (fread(buf, len, 1, fin)!=1)
    {
      fclose(fin);
      quit(0, "%s read error", argv[optind]);
    }

  fclose(fin);
  fin = NULL;

  len = (len + 511) & (~0x1FF);
  buf[OFS_HLEN] = (len >> 9) - 1;
  if (edx != 0xFFFFFFFF)
    valueat(buf, OFS_REDX, unsigned long) = edx;

  if (optind + 2 == argc)
    pout=argv[optind + 1];
  else
    {
      long len1;

      fin=fopen(argv[optind+1], "rb");
      if (fin == NULL)
        quit(1, "Unable to open %s", argv[optind+1]);

      fseek(fin,0,SEEK_END);
      len1 = ftell(fin);

      if (len1 <= 0)
        {
          fclose(fin);
          quit(0, "%s invalid length", argv[optind+1]);
        }

      fseek(fin, 0, SEEK_SET);

      valueat(buf, OFS_DLEN, unsigned long) = len1;
      pout = argv[optind + 2];
    }

  fout=fopen(pout, "wb");
  if (fout == NULL)
    quit(1, "Unable to open %s", pout);

  if (fwrite(buf, len, 1, fout)!=1)
    {
      fclose(fout);
      quit(0, "%s read error", pout);
    }

  if (fin)
    {
      while (1)
        {
          len = fread(buf, 1, BUF_SIZE, fin);
          if (len < 0)
            {
              fclose(fin);
              fclose(fout);
              quit(1, "%s read error", argv[optind+1]);
            }
          if (len == 0)
            break;
          if (fwrite(buf, len, 1, fout)!=1)
            {
              fclose(fin);
              fclose(fout);
              quit(1, "%s write error", pout);
            }
        }
      fclose(fin);
    }
  fclose(fout);

  return 0;
}

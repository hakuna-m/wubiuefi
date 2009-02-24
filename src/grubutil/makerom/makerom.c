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

#include "keytab.h"

#define BUF_SIZE	65536

#define OFS_LEN1	2
#define OFS_LEN2	0x2C
#define OFS_CSUM	5
#define OFS_HKEY	6
#define OFS_TIME	8
#define OFS_MOFS	0xA
#define OFS_MLEN	0xB
#define OFS_REDX	0xC

#define FLG_VERB	1
#define FLG_PCIR	2
#define FLG_LZMA	4

#define MAX_MLEN	32

#define APP_NAME	"makerom"

#define DEF_SKIP	512

#ifdef WIN32

#define BIN_MODE	"b"
#define CMD_LZMA	"lzma e -si -so "

#else

#define BIN_MODE
#define CMD_LZMA	"lzma_alone e -si -so "

#endif

#define valueat(buf,ofs,type)	*((type*)(((char*)&buf)+ofs))

void usage(int status)
{
  fprintf(stderr,
          "Usage:\n"
          "  makerom [OPTIONS] romboot.img core.img output\n\n"
          "Options:\n"
          "  -v\t\t\tShow verbose information\n"
          "  -m message\t\tBoot message\n"
          "  -t timeout\t\tTimeout in seconds\n"
          "  -k key\t\tHotkey\n"
          "  -d edx\t\tValue of edx\n"
          "  -s skip\t\tNumber of bytes to skip (default 512)\n"
          "  -z\t\t\tUse lzma to compress input file\n"
          "  -p parm\t\tExtra parameter for lzma\n");

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
  char ch;
  FILE *ff;
  long ofs,len,rlen,i;
  int flg;
  unsigned char csum;
  char msg[MAX_MLEN];
  int timeout,hotkey;
  char *lzma_parm;
  long edx,skip=DEF_SKIP;

  flg=0;
  lzma_parm=NULL;
  msg[0]=0;
  timeout=-1;
  hotkey=-1;
  edx=-1;
  while ((ch=getopt(argc,argv, "hm:k:t:d:s:zp:v"))!= -1)
    switch (ch) {
    case 'm':
      {
        if (strlen(optarg)>=MAX_MLEN)
          quit(0, "Message too long");
        strcpy(msg, optarg);
        break;
      }
    case 't':
      {
        timeout=strtoul(optarg,NULL,0) * 18;
        break;
      }
    case 'k':
      {
        int key;

        key=get_keycode(optarg);
        if (key)
          hotkey=key;
        break;
      }
    case 'd':
      {
        edx=strtoul(optarg,NULL,0);
        break;
      }
    case 's':
      {
        skip=strtoul(optarg,NULL,0);
        break;
      }
    case 'z':
      {
        flg|=FLG_LZMA;
        break;
      }
    case 'p':
      {
        lzma_parm=optarg;
        break;
      }
    case 'v':
      {
        flg|=FLG_VERB;
        break;
      }
    case 'h':
    default:
      usage(0);
    }

  if (optind + 3 > argc)
    usage(1);

  ff=fopen(argv[optind], "r" BIN_MODE);
  if (ff == NULL)
    quit(1, "Unable to open %s", argv[optind]);

  fseek(ff,0,SEEK_END);
  len = ftell(ff);
  if (len >= BUF_SIZE)
    {
      fclose(ff);
      quit(0, "%s too long", argv[optind]);
    }

  fseek(ff, 0, SEEK_SET);
  if (fread(buf, len, 1, ff)!=1)
    {
      fclose(ff);
      quit(0, "%s read error", argv[optind]);
    }

  fclose(ff);

  if (len < *((unsigned short*)&buf[0]))
    quit(0, "%s too short", argv[optind]);

  ofs = valueat(buf,0,unsigned short);
  valueat(buf,0,unsigned short) = 0xAA55;
  if (memcmp(&buf[0x1C],"PCIR",4)==0)
    flg|=FLG_PCIR;

  if (msg[0])
    strcpy(&buf[buf[OFS_MOFS]],msg);

  if (timeout!=-1)
    valueat(buf, OFS_TIME, unsigned short) = timeout;

  if (hotkey!=-1)
    valueat(buf, OFS_HKEY, unsigned short) = hotkey;

  if (edx!=-1)
    valueat(buf, OFS_REDX, unsigned long) = edx;

  if (flg & FLG_LZMA)
    ff=freopen(argv[optind+1], "r" BIN_MODE, stdin);
  else
    ff=fopen(argv[optind+1], "r" BIN_MODE);

  if (ff == NULL)
    quit(1, "Unable to open %s", argv[optind+1]);

  if (fseek(ff, 0, SEEK_END))
    quit(1, "fseek fails");

  rlen=ftell(ff);
  if (rlen<0)
    quit(1,"ftell fails");

  if (rlen<=skip)
    quit(0,"%s too small", argv[optind + 1]);

  if (fseek(ff, skip, SEEK_SET))
    quit(1, "fseek fails");

  rlen-=skip;

  fflush(ff);

  if (flg & FLG_LZMA)
    {
      char cmd[512];

      strcpy(cmd,CMD_LZMA);
      if (lzma_parm)
        {
          if (strlen(cmd)+strlen(lzma_parm)>=sizeof(cmd))
            quit(0, "extra options too long");

          strcat(cmd,lzma_parm);
        }

      ff=popen(cmd, "r" BIN_MODE);
      if (ff==NULL)
        quit(1, "lzma fails");
    }

  len=fread(&buf[ofs], 1, BUF_SIZE - ofs, ff);
  if (len<0)
    quit(1, "%s read error",argv[optind+1]);

  if (ofs + len==BUF_SIZE)
    {
      long nn;
      nn=fread(buf,1, BUF_SIZE, ff);
      if (nn>0)
        quit(0, "%s %d bytes too long", argv[optind+1], nn);
    }

  fclose(ff);

  if (flg & FLG_VERB)
    printf("Header: %d\nImage: %d\nTotal: %d\n", ofs, len, ofs+len);

  if (flg & FLG_LZMA)
    {
      fclose(stdin);

      valueat(buf,ofs+5,unsigned long)=rlen;
      valueat(buf,ofs+5+4,unsigned long)=0;

      if (flg & FLG_VERB)
        printf("Original: %d\n", rlen);
    }

  len = (len + ofs + 511) & (~0x1FF);

  buf[OFS_LEN1] = len >> 9;
  if (flg & FLG_PCIR)
    buf[OFS_LEN2] = buf[OFS_LEN1];

  csum = 0;
  for (i=0;i<len;i++)
    csum += buf[i];

  buf[OFS_CSUM] = (unsigned char)(0x100 - (int) csum);

  ff=fopen(argv[optind+2], "w" BIN_MODE);
  if (ff == NULL)
    quit(1, "Unable to open %s", argv[optind+2]);

  if (fwrite(buf, len, 1, ff)!=1)
    {
      fclose(ff);
      quit(0, "%s read error", argv[optind+2]);
    }

  fclose(ff);

  return 0;
}

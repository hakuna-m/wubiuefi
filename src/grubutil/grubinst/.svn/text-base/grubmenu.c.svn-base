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
#include <string.h>
#include <fcntl.h>
#include <sys/stat.h>

#ifndef WIN32

#define O_BINARY		0

#endif

#define OP_INFO			1
#define OP_PRINT		2
#define OP_EXPORT		3
#define OP_IMPORT		4

#define FG_RAW			1
#define FG_KEEP			2

#define BUF_SIZE		16
#define TST_COUNT		4

#define MAX_MENU		4096

#define APP_NAME		"grubmenu: "

#define print_apperr(a)		fprintf(stderr,APP_NAME "%s\n",a)
#define print_apperr_1(a,b)	fprintf(stderr,APP_NAME a "\n",b)
#define print_apperr_2(a,b,c)	fprintf(stderr,APP_NAME a "\n",b,c)
#define print_syserr(a)		perror(APP_NAME a)

#define phy2ofs(a)		a-0x8200+data_ofs

#define valueat(buf,ofs,type)	*((type*)(((char*)&buf)+ofs))

void help(void)
{
  fputs("Usage:\n"
        "\tgrubmenu info grldr\n"
        "\tgrubmenu print grldr\n"
        "\tgrubmenu [-r] export grldr menu.lst\n"
        "\tgrubmenu [-r] [-k] import grldr menu.lst\n",stderr);
}

char *grldr,*menu,buf[512*BUF_SIZE];
int old_style,data_ofs;

int main(int argc,char** argv)
{
  int idx,op,hd,i,j,nr,len,fg;
  unsigned long ppmenu,pmenu,pbss;
  char *pb;

  fg=0;
  if (argc<3)
    {
      help();
      return 1;
    }

  idx=1;
  while (idx<argc)
    {
      if (argv[idx][0]=='-')
        {
          if (argv[idx][1]=='k')
            fg|=FG_KEEP;
          else if (argv[idx][1]=='r')
            fg|=FG_RAW;
          else
            {
              print_apperr("Invalid option");
              return 1;
            }
        }
      else
        break;
      idx++;
    }
  if (idx>=argc)
    {
      print_apperr("No command");
      return 1;
    }
  if (! strcmp(argv[idx],"info"))
    op=OP_INFO;
  else if (! strcmp(argv[idx],"print"))
    op=OP_PRINT;
  else if (! strcmp(argv[idx],"export"))
    op=OP_EXPORT;
  else if (! strcmp(argv[idx],"import"))
    op=OP_IMPORT;
  else
    help();
  idx++;
  grldr=argv[idx++];
  if ((op==OP_EXPORT) || (op==OP_IMPORT))
    {
      if (idx>=argc)
        {
          print_apperr("Not enough parameter");
          return 1;
        }
      menu=argv[idx];
    }
  else
    menu=NULL;

  hd=open(grldr,((op==OP_IMPORT)?O_RDWR:O_RDONLY) | O_BINARY,S_IREAD);
  if (hd<0)
    {
      print_syserr("open (grldr)");
      return 1;
    }

  pb=NULL;
  // scan the first 4*16 sectors for the signature
  for (i=0;i<TST_COUNT;i++)
    {
      nr=read(hd,buf,sizeof(buf));
      if (nr<0)
        {
          print_syserr("read (grldr)");
          return 1;
        }
      if (nr!=sizeof(buf))
        {
          print_apperr("file too small");
          return 1;
        }
      for (j=0;j<BUF_SIZE;j++)
        {
          if (valueat(buf,j*512,unsigned long)==0x8270EA)
            {
              pb=&buf[j*512];
              data_ofs+=j*512;
              break;
            }
        }
      if (pb)
        break;
      data_ofs+=BUF_SIZE*512;
    }
  if (! pb)
    {
      print_apperr("signature not found");
      return 1;
    }
  ppmenu=phy2ofs(valueat(pb[0],0xC,unsigned long));
  pbss=phy2ofs(valueat(pb[0],0x6C,unsigned long));

  if (ppmenu==0)
    {
      print_apperr("no preset menu");
      return 1;
    }
  if (lseek(hd,ppmenu,SEEK_SET)!=ppmenu)
    {
      print_apperr("lseek fails (ppmenu)");
      return 1;
    }
  if (read(hd,&pmenu,4)!=4)
    {
      print_apperr("read fails (pmenu)");
      return 1;
    }
  pmenu=phy2ofs(pmenu);
  if (pmenu==0)
    {
      print_apperr("no preset menu");
      return 1;
    }
  if (pmenu!=pbss)
    old_style=1;
  else
    pmenu=pbss+16;

  if (lseek(hd,pmenu,SEEK_SET)!=pmenu)
    {
      print_apperr("lseek fails (pmenu)");
      return 1;
    }
  nr=read(hd,buf,sizeof(buf)-1);
  if (nr<=0)
    {
      print_syserr("read (menu)");
      return 1;
    }
  buf[nr]=0;
  len=strlen(buf)+1;
  if (op==OP_INFO)
    {
      printf("%s style binary\n",(old_style)?"Old":"New");
      printf("Data offset: 0x%X\n",data_ofs);
      printf("Menu offset: 0x%X\n",pmenu);
      printf("Menu length: %u\n",len);
      printf("Bss  offset: 0x%X\n",pbss);
    }
  else if (op==OP_PRINT)
    printf("%s",buf);
  else if (op==OP_EXPORT)
    {
      FILE* ff;

      ff=fopen(menu,((O_BINARY!=0) && (fg & FG_RAW))?"wb":"w");
      if (ff==NULL)
        {
          print_syserr("open (menu.lst)");
          return 1;
        }
      fputs(buf,ff);
      fclose(ff);
    }
  else if (op==OP_IMPORT)
    {
      FILE* ff;
      int sz,nb;
      char* pb;

      ff=fopen(menu,((O_BINARY!=0) && (fg & FG_RAW))?"rb":"r");
      if (ff==NULL)
        {
          print_syserr("open (menu.lst)");
          return 1;
        }

      pb=buf;
      nb=sizeof(buf)-1;
      if ((fg & FG_RAW)==0)
        {
          while ((nb>1) && (fgets(pb,nb,ff)))
            {
              char *pp;

              // skip comments
              if ((pb[0]==0) || (pb[0]=='#'))
                continue;
              pp=pb+strlen(pb)-1;
              while ((pp>=pb) &&
                     ((*pp==' ') || (*pp=='\t') || (*pp=='\r') || (*pp=='\n')))
                pp--;
              // skip blank line
              if (pp<pb)
                continue;
              *(++pp)='\n';
              pp++;
              nb-=pp-pb;
              pb=pp;
            }
        }
      else
        {
          nb=fread(pb,1,nb,ff);
          if (nb==0)
            {
              print_syserr("read (menu.lst)");
              return 1;
            }
          pb+=nb;
        }
      *(pb++)=0;
      fclose(ff);
      sz=pb-buf;
      if ((old_style) && (sz>len))
        {
          print_apperr_2("menu %d bytes overflow (old size %d)",sz-len,len);
          return 1;
        }
      else if ((! old_style) && (sz>MAX_MENU))
        {
          print_apperr_2("menu %d bytes overflow (max size %d)",sz-MAX_MENU,MAX_MENU);
          return 1;
        }
      if ((old_style) && (sz<len))
        {
          int j;

          memset(&buf[sz-1],' ',len-sz);
          for (j=len-2;j>sz;j-=80)
            buf[j]=0xA;
          sz=len;
        }
      lseek(hd,pmenu,SEEK_SET);
      if (write(hd,buf,sz)!=sz)
        {
          print_apperr("write menu fails");
          return 1;
        }
      if ((! old_style) && ((fg & FG_KEEP)==0))
        {
          unsigned short sig;

          lseek(hd,0,SEEK_SET);
          if (read(hd,&sig,2)!=2)
            {
              print_apperr("read menu fails");
              return 1;
            }
          if (sig==0x5A4D)
            {
              unsigned short val;

              val=(pmenu+sz) & 0x1FF;
              write(hd,&val,2);
              val=(pmenu+sz+511) >> 9;
              write(hd,&val,2);
            }
          ftruncate(hd,pmenu+sz);
        }
    }
  close(hd);
  return 0;
}

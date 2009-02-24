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

#include <windows.h>
#include <string.h>
#include <winioctl.h>
#include <stdio.h>
#include <fcntl.h>

#include "resource.h"
#include "version.h"
#include "utils.h"
#include "xdio.h"

HINSTANCE hInst;
PCHAR lng_ext;
char* str_tab[IDS_COUNT];

void ChangeText(HWND hWnd)
{
  char LocaleName[4],buf[MAX_PATH],*pc;
  FILE *in;

  if (! lng_ext)
    {
      GetLocaleInfo(GetUserDefaultLCID(), LOCALE_SABBREVLANGNAME, LocaleName, sizeof(LocaleName));
      lng_ext=LocaleName;
    }
  GetModuleFileName(hInst,buf,sizeof(buf));
  pc=strrchr(buf,'.');
  if (pc)
    strcpy(pc+1,lng_ext);
  in=fopen(buf,"rt");
  if (in==NULL)
    return;
  while (fgets(buf,sizeof(buf),in))
    {
      char *pb;
      int nn;

      if (buf[0]=='#')
        continue;
      pb=&buf[strlen(buf)];
      while ((pb!=buf) && ((*(pb-1)=='\r') || (*(pb-1)=='\n')))
        pb--;
      if (pb==buf)
        continue;
      *pb=0;
      pb=strchr(buf,'=');
      if (pb==NULL)
        continue;
      *(pb++)=0;
      nn=atoi(buf);
      if ((nn>=IDS_BEGIN) && (nn<=IDS_END))
        {
          nn-=IDS_BEGIN;
          if (str_tab[nn])
            free(str_tab[nn]);
          str_tab[nn]=malloc(strlen(pb)+1);
          if (str_tab[nn])
            strcpy(str_tab[nn],pb);
        }
      else
        SetDlgItemText(hWnd,nn,pb);
    }
  fclose(in);
}

char* LoadText(int id)
{
  static char buf[80];

  if ((id>=IDS_BEGIN) && (id<=IDS_END) && (str_tab[id-IDS_BEGIN]))
    return str_tab[id-IDS_BEGIN];

  LoadString(hInst,id,buf,sizeof(buf));
  return buf;
}

void PrintError(HWND hWnd,DWORD msg)
{
  MessageBox(hWnd,LoadText(msg),NULL,MB_OK | MB_ICONERROR);
}

void RefreshDisk(HWND hWnd)
{
  char dn[24],nn[20];
  int i;

  SendDlgItemMessage(hWnd,IDC_DISKS,CB_RESETCONTENT,0,0);
  strcpy(dn,"\\\\.\\PhysicalDrive0");
  for (i=0;i<MAX_DISKS;i++)
    {
      HANDLE hd;
      DISK_GEOMETRY ge;
      DWORD rs;

      dn[17]='0'+i;
      hd=CreateFile (dn,GENERIC_READ | GENERIC_WRITE,FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,OPEN_EXISTING, 0, NULL);
      if (hd==INVALID_HANDLE_VALUE)
        continue;

      if (DeviceIoControl(hd,IOCTL_DISK_GET_DRIVE_GEOMETRY,NULL,0,&ge,sizeof(ge),&rs,NULL))
        {
          DWORD dd,mm;

          dd=ge.TracksPerCylinder*ge.SectorsPerTrack*ge.BytesPerSector;
          mm=dd % 0xFFFFF;
          dd>>=20;
          dd*=ge.Cylinders.LowPart;
          mm*=ge.Cylinders.LowPart;
          dd+=(mm >> 20);
          sprintf(nn,"(hd%d) [%uM]",i,dd);
        }
      else
        sprintf(nn,"(hd%d)",i);
      SendDlgItemMessage(hWnd,IDC_DISKS,CB_ADDSTRING,0,(LPARAM)&nn);
      CloseHandle(hd);
    }
  if (GetDriveType("A:\\")==DRIVE_REMOVABLE)
    SendDlgItemMessage(hWnd,IDC_DISKS,CB_ADDSTRING,0,(LPARAM)"(fd0)");
  if (GetDriveType("B:\\")==DRIVE_REMOVABLE)
    SendDlgItemMessage(hWnd,IDC_DISKS,CB_ADDSTRING,0,(LPARAM)"(fd1)");
}

int GetFileName(HWND hWnd,char* fn,int len)
{
  if (IsDlgButtonChecked(hWnd,IDC_ISDISK)==BST_CHECKED)
    {
      char* pc;

      if (GetDlgItemText(hWnd,IDC_DISKS,fn,len)==0)
        {
          PrintError(hWnd,IDS_NO_DISKNAME);
          return 1;
        }
      pc=strchr(fn,' ');
      if (pc)
        *pc=0;
    }
  else if (IsDlgButtonChecked(hWnd,IDC_ISFILE)==BST_CHECKED)
    {
      if (GetDlgItemText(hWnd,IDC_FILENAME,fn,len)==0)
        {
          PrintError(hWnd,IDS_NO_FILENAME);
          return 1;
        }
    }
  else
    {
      PrintError(hWnd,IDS_NO_DEVICETYPE);
      return 1;
    }
  return 0;
}

void RefreshPart(HWND hWnd)
{
  char fn[MAX_PATH];
  char buf[512*4];
  int fs,len;
  xd_t *xd;

  SendDlgItemMessage(hWnd,IDC_PARTS,CB_RESETCONTENT,0,0);

  if (GetFileName(hWnd,fn,sizeof(fn)))
    return;

  xd=xd_open(fn,0);
  if (xd==NULL)
    {
      PrintError(hWnd,IDS_INVALID_FILE);
      return;
    }
  if (xd_read(xd,buf,sizeof(buf)>>9))
    {
      PrintError(hWnd,IDS_INVALID_FILE);
      xd_close(xd);
      return;
    }
  fs=get_fstype(buf);

  if (fs==FST_MBR2)
    {
      PrintError(hWnd, IDS_INVALID_MBR);
      fs=FST_MBR;
    }

  CheckDlgButton(hWnd,IDC_IS_FLOPPY,(fs!=FST_MBR));

  strcpy(buf,LoadText(IDS_WHOLE_DISK));
  len=strlen(buf);
  sprintf(&buf[len]," (%s)",fst2str(fs));
  SendDlgItemMessage(hWnd,IDC_PARTS,CB_ADDSTRING,0,(LPARAM)buf);

  if (fs==FST_MBR)
    {
      xde_t xe;

      xe.cur=xe.nxt=0xFF;
      while (! xd_enum(xd,&xe))
        {
          sprintf(buf,"%d: %02X(%s) [%uM]",xe.cur,xe.dfs,dfs2str(xe.dfs),xe.len>>11);
          SendDlgItemMessage(hWnd,IDC_PARTS,CB_ADDSTRING,0,(LPARAM)buf);
        }
    }
  xd_close(xd);
}

void Install(HWND hWnd,BOOLEAN test)
{
  char fn[512],*pb;
  char temp[16];
  int len;

  GetModuleFileName(hInst,fn,sizeof(fn));
  pb=strrchr(fn,'\\');
  if (! pb)
    pb=fn;
  else
    pb++;
  strcpy(pb,"grubinst.exe --pause ");
  len=strlen(fn);


  if (IsDlgButtonChecked(hWnd,IDC_OUTPUT)==BST_CHECKED)
    {
      if (IsDlgButtonChecked(hWnd,IDC_ISFILE)!=BST_CHECKED)
        {
          PrintError(hWnd,IDS_NO_DEVICE);
          return;
        }
      strcpy(&fn[len],"--output ");
      len+=strlen(&fn[len]);
    }
  if (IsDlgButtonChecked(hWnd,IDC_READ_ONLY)==BST_CHECKED)
    {
      strcpy(&fn[len],"--read-only ");
      len+=strlen(&fn[len]);
    }
  if (IsDlgButtonChecked(hWnd,IDC_VERBOSE)==BST_CHECKED)
    {
      strcpy(&fn[len],"--verbose ");
      len+=strlen(&fn[len]);
    }
  if (IsDlgButtonChecked(hWnd,IDC_NO_BACKUP_MBR)==BST_CHECKED)
    {
      strcpy(&fn[len],"--no-backup-mbr ");
      len+=strlen(&fn[len]);
    }
  if (IsDlgButtonChecked(hWnd,IDC_DISABLE_FLOPPY)==BST_CHECKED)
    {
      strcpy(&fn[len],"--mbr-disable-floppy ");
      len+=strlen(&fn[len]);
    }
  if (IsDlgButtonChecked(hWnd,IDC_DISABLE_OSBR)==BST_CHECKED)
    {
      strcpy(&fn[len],"--mbr-disable-osbr ");
      len+=strlen(&fn[len]);
    }
  if (IsDlgButtonChecked(hWnd,IDC_PREVMBR_FIRST)==BST_CHECKED)
    {
      strcpy(&fn[len],"--boot-prevmbr-first ");
      len+=strlen(&fn[len]);
    }
  if (IsDlgButtonChecked(hWnd,IDC_GRUB2)==BST_CHECKED)
    {
      strcpy(&fn[len],"--grub2 ");
      len+=strlen(&fn[len]);
    }
  if (IsDlgButtonChecked(hWnd,IDC_IS_FLOPPY)==BST_CHECKED)
    {
      strcpy(&fn[len],"--floppy ");
      len+=strlen(&fn[len]);
    }
  if (GetDlgItemText(hWnd,IDC_TIMEOUT,temp,sizeof(temp))!=0)
    {
      sprintf(&fn[len],"--time-out=%s ",temp);
      len+=strlen(&fn[len]);
    }
  if (GetDlgItemText(hWnd,IDC_HOTKEY,temp,sizeof(temp))!=0)
    {
      sprintf(&fn[len],"--hot-key=%s ",temp);
      len+=strlen(&fn[len]);
    }
  if (GetDlgItemText(hWnd,IDC_LOADSEG,temp,sizeof(temp))!=0)
    {
      sprintf(&fn[len],"--load-seg=%s ",temp);
      len+=strlen(&fn[len]);
    }
  if (GetDlgItemText(hWnd,IDC_BOOTFILE,temp,sizeof(temp))!=0)
    {
      sprintf(&fn[len],"--boot-file=%s ",temp);
      len+=strlen(&fn[len]);
    }
  if (IsDlgButtonChecked(hWnd,IDC_RESTORE_SAVE)==BST_CHECKED)
    {
      strcpy(&fn[len],"--restore=");
      len+=strlen(&fn[len]);
      if (GetDlgItemText(hWnd,IDC_SAVEFILE,&fn[len],sizeof(fn)-len)==0)
        {
          PrintError(hWnd,IDS_NO_SAVEFILE);
          return;
        }
      len+=strlen(&fn[len]);
      fn[len++]=' ';
      fn[len]=0;
    }
  else if (IsDlgButtonChecked(hWnd,IDC_RESTORE_PREVMBR)==BST_CHECKED)
    {
      strcpy(&fn[len],"--restore-prevmbr ");
      len+=strlen(&fn[len]);
    }
  else
    {
      int slen;

      strcpy(&fn[len],"--save=");
      slen=strlen(&fn[len]);
      if (GetDlgItemText(hWnd,IDC_SAVEFILE,&fn[len+slen],sizeof(fn)-len-slen)!=0)
        {
          len+=strlen(&fn[len]);
          fn[len++]=' ';
          fn[len]=0;
        }
      else
        fn[len]=0;
    }
  if (GetDlgItemText(hWnd,IDC_PARTS,temp,sizeof(temp))!=0)
    if ((temp[0]>='0') && (temp[0]<='9'))
      {
        int n;

        n=atoi(temp);
        sprintf(&fn[len],"--install-partition=%d ",n);
        len+=strlen(&fn[len]);
      }
  if (GetDlgItemText(hWnd,IDC_EXTRA,&fn[len],sizeof(fn)-len)!=0)
    {
      len+=strlen(&fn[len]);
      fn[len++]=' ';
      fn[len]=0;
    }
  if (GetFileName(hWnd,&fn[len],sizeof(fn)-len))
    return;
  if (test)
    MessageBox(hWnd,fn,"",MB_OK);
  else if (WinExec(fn,SW_SHOW)<=31)
    {
      PrintError(hWnd,IDS_EXEC_ERROR);
      return;
    }
}

BOOL CALLBACK DialogProc(HWND hWnd,UINT wMsg,WPARAM wParam,LPARAM lParam)
{

  switch (wMsg) {
  case WM_CLOSE:
    EndDialog(hWnd,0);
    break;
  case WM_INITDIALOG:
    {
      HICON hIcon;
      char title[30];

      ChangeText(hWnd);
      sprintf(title,"%s " VERSION,LoadText(IDS_MAIN));
      SendMessage(hWnd,WM_SETTEXT,0,(LPARAM)title);
      hIcon=LoadIcon(hInst,MAKEINTRESOURCE(ICO_MAIN));
      SendMessage(hWnd,WM_SETICON,ICON_BIG,(LPARAM)hIcon);
      RefreshDisk(hWnd);
      break;
    }
  case WM_COMMAND:
    {
      switch (wParam & 0xFFFF) {
      case IDC_TEST:
        Install(hWnd,TRUE);
        break;
      case IDC_INSTALL:
        Install(hWnd,FALSE);
        break;
      case IDC_QUIT:
        EndDialog(hWnd,0);
        break;
      case IDC_REFRESH_DISK:
        RefreshDisk(hWnd);
        break;
      case IDC_REFRESH_PART:
        RefreshPart(hWnd);
        break;
      case IDC_BROWSE:
        {
          OPENFILENAME ofn;
          char fn[MAX_PATH];

          memset(&ofn,0,sizeof(ofn));
          GetDlgItemText(hWnd,IDC_FILENAME,fn,sizeof(fn));
          ofn.lStructSize=sizeof(ofn);
          ofn.hwndOwner=hWnd;
          ofn.hInstance=hInst;
          ofn.lpstrFile=fn;
          ofn.nMaxFile=sizeof(fn);
          if (IsDlgButtonChecked(hWnd,IDC_OUTPUT)==BST_CHECKED)
            {
              ofn.Flags=0;
              strcpy(fn,"grldr.mbr");
            }
          else
            ofn.Flags=OFN_PATHMUSTEXIST | OFN_FILEMUSTEXIST;
          if (GetOpenFileName(&ofn))
            SetDlgItemText(hWnd,IDC_FILENAME,fn);
          break;
        }
      case IDC_DISKS:
        {
          if (wParam>>16==CBN_SELENDOK)
            {
              CheckRadioButton(hWnd,IDC_ISDISK,IDC_ISFILE,IDC_ISDISK);
              SendDlgItemMessage(hWnd,IDC_PARTS,CB_RESETCONTENT,0,0);
            }
          break;
        }
      case IDC_RESTORE_SAVE:
        {
          if (wParam>>16==BN_CLICKED)
            {
              if (IsDlgButtonChecked(hWnd,IDC_RESTORE_SAVE)==BST_CHECKED)
                CheckDlgButton(hWnd,IDC_RESTORE_PREVMBR,BST_UNCHECKED);
            }
          break;
        }
      case IDC_RESTORE_PREVMBR:
        {
          if (wParam>>16==BN_CLICKED)
            {
              if (IsDlgButtonChecked(hWnd,IDC_RESTORE_PREVMBR)==BST_CHECKED)
                CheckDlgButton(hWnd,IDC_RESTORE_SAVE,BST_UNCHECKED);
            }
          break;
        }
      case IDC_FILENAME:
        {
          if (wParam>>16==EN_CHANGE)
            {
              CheckRadioButton(hWnd,IDC_ISDISK,IDC_ISFILE,IDC_ISFILE);
              SendDlgItemMessage(hWnd,IDC_PARTS,CB_RESETCONTENT,0,0);
            }
          break;
        }
      case IDC_BROWSE_SAVE:
        {
          OPENFILENAME ofn;
          char fn[512];

          memset(&ofn,0,sizeof(ofn));
          GetDlgItemText(hWnd,IDC_SAVEFILE,fn,sizeof(fn));
          ofn.lStructSize=sizeof(ofn);
          ofn.hwndOwner=hWnd;
          ofn.hInstance=hInst;
          ofn.lpstrFile=fn;
          ofn.nMaxFile=sizeof(fn);
          if (GetOpenFileName(&ofn))
            SetDlgItemText(hWnd,IDC_SAVEFILE,fn);
          break;
        }
      }
      break;
    }
  default:
    return FALSE;
  }
  return TRUE;
}

int WINAPI WinMain(HINSTANCE hInstance,HINSTANCE hPrevInstance,LPSTR lpCmdLine,int nCmdShow)
{
  char buf[30];

  hInst=hInstance;
  if (! strncmp(lpCmdLine,"--lang=",7))
    lng_ext=&lpCmdLine[7];

  DialogBoxParam(hInst,MAKEINTRESOURCE(DLG_MAIN),NULL,DialogProc,0);
  return 0;
}

/*
 *  GRUB Utilities --  Utilities for GRUB Legacy, GRUB2 and GRUB for DOS
 *  Copyright (C) 2007 Bean (bean123@126.com)
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

#define DLG_MAIN	1

#define ICO_MAIN	10

#define IDC_GROUPBOX1	100
#define IDC_ISDISK	101
#define IDC_DISKS	102
#define IDC_REFRESH_DISK	103
#define IDC_ISFILE	104
#define IDC_FILENAME	105
#define IDC_BROWSE	106
#define IDC_LPART	107
#define IDC_PARTS	108
#define IDC_REFRESH_PART	109
#define IDC_OUTPUT	110

#define IDC_GROUPBOX2	120
#define IDC_READ_ONLY	121
#define IDC_VERBOSE	122
#define IDC_NO_BACKUP_MBR	123
#define IDC_DISABLE_FLOPPY	124
#define IDC_DISABLE_OSBR	125
#define IDC_PREVMBR_FIRST	126
#define IDC_GRUB2	127
#define IDC_IS_FLOPPY	128
#define IDC_LTIMEOUT	129
#define IDC_TIMEOUT	130
#define IDC_LHOTKEY	131
#define IDC_HOTKEY	132
#define IDC_LLOADSEG	133
#define IDC_LOADSEG	134
#define IDC_LBOOTFILE	135
#define IDC_BOOTFILE	136
#define IDC_LEXTRA	137
#define IDC_EXTRA	138

#define IDC_GROUPBOX3	140
#define IDC_LSAVEFILE	141
#define IDC_SAVEFILE	142
#define IDC_BROWSE_SAVE	143
#define IDC_RESTORE_SAVE	144
#define IDC_RESTORE_PREVMBR	145

#define IDC_TEST	160
#define IDC_INSTALL	161
#define IDC_QUIT	162

#define IDS_BEGIN	500

#define IDS_MAIN	500
#define IDS_NO_SAVEFILE	501
#define IDS_NO_DISKNAME 502
#define IDS_NO_FILENAME 503
#define IDS_NO_DEVICETYPE 504
#define IDS_EXEC_ERROR 505
#define IDS_INVALID_FILE 506
#define IDS_WHOLE_DISK 507
#define IDS_NO_DEVICE 508
#define IDS_INVALID_MBR 509

#define IDS_END		509
#define IDS_COUNT	(IDS_END-IDS_BEGIN+1)

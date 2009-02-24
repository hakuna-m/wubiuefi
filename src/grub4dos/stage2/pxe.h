/*
 *  PXE file system for GRUB
 *
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

#ifndef __PXE_H
#define __PXE_H

#define PXENV_TFTP_OPEN			0x0020
#define PXENV_TFTP_CLOSE		0x0021
#define PXENV_TFTP_READ			0x0022
#define PXENV_TFTP_READ_FILE		0x0023
#define PXENV_TFTP_READ_FILE_PMODE	0x0024
#define PXENV_TFTP_GET_FSIZE		0x0025

#define PXENV_UDP_OPEN			0x0030
#define PXENV_UDP_CLOSE			0x0031
#define PXENV_UDP_READ			0x0032
#define PXENV_UDP_WRITE			0x0033

#define PXENV_START_UNDI		0x0000
#define PXENV_UNDI_STARTUP		0x0001
#define PXENV_UNDI_CLEANUP		0x0002
#define PXENV_UNDI_INITIALIZE		0x0003
#define PXENV_UNDI_RESET_NIC		0x0004
#define PXENV_UNDI_SHUTDOWN		0x0005
#define PXENV_UNDI_OPEN			0x0006
#define PXENV_UNDI_CLOSE		0x0007
#define PXENV_UNDI_TRANSMIT		0x0008
#define PXENV_UNDI_SET_MCAST_ADDR	0x0009
#define PXENV_UNDI_SET_STATION_ADDR	0x000A
#define PXENV_UNDI_SET_PACKET_FILTER	0x000B
#define PXENV_UNDI_GET_INFORMATION	0x000C
#define PXENV_UNDI_GET_STATISTICS	0x000D
#define PXENV_UNDI_CLEAR_STATISTICS	0x000E
#define PXENV_UNDI_INITIATE_DIAGS	0x000F
#define PXENV_UNDI_FORCE_INTERRUPT	0x0010
#define PXENV_UNDI_GET_MCAST_ADDR	0x0011
#define PXENV_UNDI_GET_NIC_TYPE		0x0012
#define PXENV_UNDI_GET_IFACE_INFO	0x0013
#define PXENV_UNDI_ISR			0x0014
#define	PXENV_STOP_UNDI			0x0015	// Overlap...?
#define PXENV_UNDI_GET_STATE		0x0015	// Overlap...?

#define PXENV_UNLOAD_STACK		0x0070
#define PXENV_GET_CACHED_INFO		0x0071
#define PXENV_RESTART_DHCP		0x0072
#define PXENV_RESTART_TFTP		0x0073
#define PXENV_MODE_SWITCH		0x0074
#define PXENV_START_BASE		0x0075
#define PXENV_STOP_BASE			0x0076

#define PXENV_EXIT_SUCCESS 0x0000
#define PXENV_EXIT_FAILURE 0x0001

#define PXENV_STATUS_SUCCESS 0x00
#define PXENV_STATUS_FAILURE 0x01
#define PXENV_STATUS_BAD_FUNC 0x02
#define PXENV_STATUS_UNSUPPORTED 0x03
#define PXENV_STATUS_KEEP_UNDI 0x04
#define PXENV_STATUS_KEEP_ALL 0x05
#define PXENV_STATUS_OUT_OF_RESOURCES 0x06
#define PXENV_STATUS_ARP_TIMEOUT 0x11
#define PXENV_STATUS_UDP_CLOSED 0x18
#define PXENV_STATUS_UDP_OPEN 0x19
#define PXENV_STATUS_TFTP_CLOSED 0x1A
#define PXENV_STATUS_TFTP_OPEN 0x1B
#define PXENV_STATUS_MCOPY_PROBLEM 0x20
#define PXENV_STATUS_BIS_INTEGRITY_FAILURE 0x21
#define PXENV_STATUS_BIS_VALIDATE_FAILURE 0x22
#define PXENV_STATUS_BIS_INIT_FAILURE 0x23
#define PXENV_STATUS_BIS_SHUTDOWN_FAILURE 0x24
#define PXENV_STATUS_BIS_GBOA_FAILURE 0x25
#define PXENV_STATUS_BIS_FREE_FAILURE 0x26
#define PXENV_STATUS_BIS_GSI_FAILURE 0x27
#define PXENV_STATUS_BIS_BAD_CKSUM 0x28
#define PXENV_STATUS_TFTP_CANNOT_ARP_ADDRESS 0x30
#define PXENV_STATUS_TFTP_OPEN_TIMEOUT	0x32

#define PXENV_STATUS_TFTP_UNKNOWN_OPCODE 0x33
#define PXENV_STATUS_TFTP_READ_TIMEOUT 0x35
#define PXENV_STATUS_TFTP_ERROR_OPCODE 0x36
#define PXENV_STATUS_TFTP_CANNOT_OPEN_CONNECTION 0x38
#define PXENV_STATUS_TFTP_CANNOT_READ_FROM_CONNECTION 0x39
#define PXENV_STATUS_TFTP_TOO_MANY_PACKAGES 0x3A
#define PXENV_STATUS_TFTP_FILE_NOT_FOUND 0x3B
#define PXENV_STATUS_TFTP_ACCESS_VIOLATION 0x3C
#define PXENV_STATUS_TFTP_NO_MCAST_ADDRESS 0x3D
#define PXENV_STATUS_TFTP_NO_FILESIZE 0x3E
#define PXENV_STATUS_TFTP_INVALID_PACKET_SIZE 0x3F
#define PXENV_STATUS_DHCP_TIMEOUT 0x51
#define PXENV_STATUS_DHCP_NO_IP_ADDRESS 0x52
#define PXENV_STATUS_DHCP_NO_BOOTFILE_NAME 0x53
#define PXENV_STATUS_DHCP_BAD_IP_ADDRESS 0x54
#define PXENV_STATUS_UNDI_INVALID_FUNCTION 0x60
#define PXENV_STATUS_UNDI_MEDIATEST_FAILED 0x61
#define PXENV_STATUS_UNDI_CANNOT_INIT_NIC_FOR_MCAST 0x62
#define PXENV_STATUS_UNDI_CANNOT_INITIALIZE_NIC 0x63
#define PXENV_STATUS_UNDI_CANNOT_INITIALIZE_PHY 0x64
#define PXENV_STATUS_UNDI_CANNOT_READ_CONFIG_DATA 0x65
#define PXENV_STATUS_UNDI_CANNOT_READ_INIT_DATA 0x66
#define PXENV_STATUS_UNDI_BAD_MAC_ADDRESS 0x67
#define PXENV_STATUS_UNDI_BAD_EEPROM_CHECKSUM 0x68
#define PXENV_STATUS_UNDI_ERROR_SETTING_ISR 0x69
#define PXENV_STATUS_UNDI_INVALID_STATE 0x6A
#define PXENV_STATUS_UNDI_TRANSMIT_ERROR 0x6B
#define PXENV_STATUS_UNDI_INVALID_PARAMETER 0x6C
#define PXENV_STATUS_BSTRAP_PROMPT_MENU 0x74
#define PXENV_STATUS_BSTRAP_MCAST_ADDR 0x76
#define PXENV_STATUS_BSTRAP_MISSING_LIST 0x77
#define PXENV_STATUS_BSTRAP_NO_RESPONSE 0x78
#define PXENV_STATUS_BSTRAP_FILE_TOO_BIG 0x79
#define PXENV_STATUS_BINL_CANCELED_BY_KEYSTROKE 0xA0
#define PXENV_STATUS_BINL_NO_PXE_SERVER 0xA1
#define PXENV_STATUS_NOT_AVAILABLE_IN_PMODE 0xA2
#define PXENV_STATUS_NOT_AVAILABLE_IN_RMODE 0xA3
#define PXENV_STATUS_BUSD_DEVICE_NOT_SUPPORTED 0xB0
#define PXENV_STATUS_LOADER_NO_FREE_BASE_MEMORY 0xC0
#define PXENV_STATUS_LOADER_NO_BC_ROMID 0xC1
#define PXENV_STATUS_LOADER_BAD_BC_ROMID 0xC2
#define PXENV_STATUS_LOADER_BAD_BC_RUNTIME_IMAGE 0xC3
#define PXENV_STATUS_LOADER_NO_UNDI_ROMID 0xC4
#define PXENV_STATUS_LOADER_BAD_UNDI_ROMID 0xC5
#define PXENV_STATUS_LOADER_BAD_UNDI_DRIVER_IMAGE 0xC6
#define PXENV_STATUS_LOADER_NO_PXE_STRUCT 0xC8
#define PXENV_STATUS_LOADER_NO_PXENV_STRUCT 0xC9
#define PXENV_STATUS_LOADER_UNDI_START 0xCA
#define PXENV_STATUS_LOADER_BC_START 0xCB

#define PACKED		__attribute__ ((packed))

#define SEGMENT(x)	((x) >> 4)
#define OFFSET(x)	((x) & 0xF)
#define SEGOFS(x)	((SEGMENT(x)<<16)+OFFSET(x))
#define LINEAR(x)	(void*)(((x >> 16) <<4)+(x & 0xFFFF))

#define PXE_ERR_LEN	0xFFFFFFFF

typedef unsigned long	UINT32;
typedef unsigned short	UINT16;
typedef unsigned char	UINT8;

typedef UINT16		PXENV_STATUS;
typedef UINT32		SEGOFS16;
typedef UINT32		IP4;
typedef UINT16		UDP_PORT;

#define MAC_ADDR_LEN	16
typedef UINT8		MAC_ADDR[MAC_ADDR_LEN];

#define PXENV_PACKET_TYPE_DHCP_DISCOVER	1
#define PXENV_PACKET_TYPE_DHCP_ACK	2
#define PXENV_PACKET_TYPE_CACHED_REPLY	3

typedef struct {
  PXENV_STATUS	Status;
  UINT16	PacketType;
  UINT16	BufferSize;
  SEGOFS16	Buffer;
  UINT16	BufferLimit;
} PACKED PXENV_GET_CACHED_INFO_t;

#define BOOTP_REQ	1
#define BOOTP_REP	2

#define BOOTP_BCAST	0x8000

#if 1
#define BOOTP_DHCPVEND  1024    /* DHCP extended vendor field size */
#else
#define BOOTP_DHCPVEND  312	/* DHCP standard vendor field size */
#endif

#ifndef	VM_RFC1048
#define	VM_RFC1048	0x63825363L
#endif

typedef struct {
  UINT8		opcode;
  UINT8		Hardware;	/* hardware type */
  UINT8		Hardlen;	/* hardware addr len */
  UINT8		Gatehops;	/* zero it */
  UINT32	ident;		/* random number chosen by client */
  UINT16	seconds;	/* seconds since did initial bootstrap */
  UINT16	Flags;		/* seconds since did initial bootstrap */
  IP4		cip;		/* Client IP */
  IP4		yip;		/* Your IP */
  IP4		sip;		/* IP to use for next boot stage */
  IP4		gip;		/* Relay IP ? */
  MAC_ADDR	CAddr;		/* Client hardware address */
  UINT8		Sname[64];	/* Server's hostname (Optional) */
  UINT8		bootfile[128];	/* boot filename */
  union {
    UINT8	d[BOOTP_DHCPVEND];	/* raw array of vendor/dhcp options */
    struct {
      UINT8	magic[4];	/* DHCP magic cookie */
      UINT32	flags;		/* bootp flags/opcodes */
      UINT8	pad[56];
    } v;
  } vendor;
} PACKED BOOTPLAYER;

typedef struct {
  PXENV_STATUS	Status;
  IP4		ServerIPAddress;
  IP4		GatewayIPAddress;
  UINT8		FileName[128];
  UDP_PORT	TFTPPort;
  UINT16	PacketSize;
} PACKED PXENV_TFTP_OPEN_t;

typedef struct {
  PXENV_STATUS	Status;
} PACKED PXENV_TFTP_CLOSE_t;

typedef struct {
  PXENV_STATUS	Status;
  UINT16	PacketNumber;
  UINT16	BufferSize;
  SEGOFS16	Buffer;
} PACKED PXENV_TFTP_READ_t;

typedef struct {
  PXENV_STATUS	Status;
  IP4		ServerIPAddress;
  IP4		GatewayIPAddress;
  UINT8		FileName[128];
  UINT32	FileSize;
} PACKED PXENV_TFTP_GET_FSIZE_t;

typedef struct {
  PXENV_STATUS	Status;
  IP4		src_ip;
} PACKED PXENV_UDP_OPEN_t;

typedef struct {
  PXENV_STATUS	Status;
} PACKED PXENV_UDP_CLOSE_t;

typedef struct {
  PXENV_STATUS	Status;
  IP4		ip;
  IP4		gw;
  UDP_PORT	src_port;
  UDP_PORT	dst_port;
  UINT16	buffer_size;
  SEGOFS16	buffer;
} PACKED PXENV_UDP_WRITE_t;

typedef struct {
  PXENV_STATUS	Status;
  IP4		src_ip;
  IP4		dst_ip;
  UDP_PORT	src_port;
  UDP_PORT	dst_port;
  UINT16	buffer_size;
  SEGOFS16	buffer;
} PACKED PXENV_UDP_READ_t;

typedef struct {
  PXENV_STATUS	Status;
  UINT8		reserved[10];
} PACKED PXENV_UNLOAD_STACK_t;

#undef PACKED

#endif /* __PXE_H */

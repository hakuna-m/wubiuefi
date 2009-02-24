/*
 *  GRUB  --  GRand Unified Bootloader
 *  Copyright (C) 2000,2001,2002  Free Software Foundation, Inc.
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

/* RULE: You must define the macro ``GRUB'' when including this header
   file in GRUB code.  */

/* Based on "src/etherboot.h" in etherboot-5.0.5.  */

/**************************************************************************
ETHERBOOT -  BOOTP/TFTP Bootstrap Program

Author: Martin Renters
  Date: Dec/93

**************************************************************************/

/* Include GRUB-specific macros and prototypes here.  */
#include <shared.h>

/* FIXME: For now, enable the DHCP support. Perhaps I should segregate
   the DHCP support from the BOOTP support, and permit both to
   co-exist.  */
#undef NO_DHCP_SUPPORT

/* In GRUB, the relocated address in Etherboot doesn't have any sense.
   Just define it as a bogus value.  */
#define RELOC	0

/* FIXME: Should be an option.  */
#define BACKOFF_LIMIT	7

#include <osdep.h>

#define CTRL_C		3

#ifndef	MAX_TFTP_RETRIES
# define MAX_TFTP_RETRIES	20
#endif

#ifndef	MAX_BOOTP_RETRIES
# define MAX_BOOTP_RETRIES	20
#endif

#define MAX_BOOTP_EXTLEN	(ETH_FRAME_LEN - ETH_HLEN - \
				 sizeof (struct bootp_t))

#ifndef	MAX_ARP_RETRIES
# define MAX_ARP_RETRIES	20
#endif

#ifndef	MAX_RPC_RETRIES
# define MAX_RPC_RETRIES	20
#endif

#define	TICKS_PER_SEC		18

/* Inter-packet retry in ticks */
#define TIMEOUT			(10 * TICKS_PER_SEC)

/* These settings have sense only if compiled with -DCONGESTED */
/* total retransmission timeout in ticks */
#define TFTP_TIMEOUT		(30 * TICKS_PER_SEC)
/* packet retransmission timeout in ticks */
#define TFTP_REXMT		(3 * TICKS_PER_SEC)

#ifndef	NULL
# define NULL			((void *) 0)
#endif

/*
   I'm moving towards the defined names in linux/if_ether.h for clarity.
   The confusion between 60/64 and 1514/1518 arose because the NS8390
   counts the 4 byte frame checksum in the incoming packet, but not
   in the outgoing packet. 60/1514 are the correct numbers for most
   if not all of the other NIC controllers. I will be retiring the
   64/1518 defines in the lead-up to 5.0.
*/

#define ETH_ALEN		6	/* Size of Ethernet address */
#define ETH_HLEN		14	/* Size of ethernet header */
#define	ETH_ZLEN		60	/* Minimum packet */
/*#define ETH_MIN_PACKET		64*/
#define	ETH_FRAME_LEN		1514	/* Maximum packet */
/*#define ETH_MAX_PACKET		1518*/
/* Because some DHCP/BOOTP servers don't treat the maximum length the same
   as Etherboot, subtract the size of an IP header and that of an UDP
   header.  */
#define	ETH_MAX_MTU		(ETH_FRAME_LEN - ETH_HLEN \
				- sizeof (struct iphdr) \
				- sizeof (struct udphdr))

#define ARP_CLIENT	0
#define ARP_SERVER	1
#define ARP_GATEWAY	2
#define ARP_ROOTSERVER	3
#define ARP_SWAPSERVER	4
#define MAX_ARP		ARP_SWAPSERVER+1

#define	RARP_REQUEST	3
#define	RARP_REPLY	4

#define IP		0x0800
#define ARP		0x0806
#define	RARP		0x8035

#define BOOTP_SERVER	67
#define BOOTP_CLIENT	68
#define TFTP_PORT	69
#define SUNRPC_PORT	111

#define IP_UDP		17
/* Same after going through htonl */
#define IP_BROADCAST	0xFFFFFFFF

#define ARP_REQUEST	1
#define ARP_REPLY	2

#define BOOTP_REQUEST	1
#define BOOTP_REPLY	2

#define TAG_LEN(p)		(*((p) + 1))
#define RFC1533_COOKIE		99, 130, 83, 99
#define RFC1533_PAD		0
#define RFC1533_NETMASK		1
#define RFC1533_TIMEOFFSET	2
#define RFC1533_GATEWAY		3
#define RFC1533_TIMESERVER	4
#define RFC1533_IEN116NS	5
#define RFC1533_DNS		6
#define RFC1533_LOGSERVER	7
#define RFC1533_COOKIESERVER	8
#define RFC1533_LPRSERVER	9
#define RFC1533_IMPRESSSERVER	10
#define RFC1533_RESOURCESERVER	11
#define RFC1533_HOSTNAME	12
#define RFC1533_BOOTFILESIZE	13
#define RFC1533_MERITDUMPFILE	14
#define RFC1533_DOMAINNAME	15
#define RFC1533_SWAPSERVER	16
#define RFC1533_ROOTPATH	17
#define RFC1533_EXTENSIONPATH	18
#define RFC1533_IPFORWARDING	19
#define RFC1533_IPSOURCEROUTING	20
#define RFC1533_IPPOLICYFILTER	21
#define RFC1533_IPMAXREASSEMBLY	22
#define RFC1533_IPTTL		23
#define RFC1533_IPMTU		24
#define RFC1533_IPMTUPLATEAU	25
#define RFC1533_INTMTU		26
#define RFC1533_INTLOCALSUBNETS	27
#define RFC1533_INTBROADCAST	28
#define RFC1533_INTICMPDISCOVER	29
#define RFC1533_INTICMPRESPOND	30
#define RFC1533_INTROUTEDISCOVER 31
#define RFC1533_INTROUTESOLICIT	32
#define RFC1533_INTSTATICROUTES	33
#define RFC1533_LLTRAILERENCAP	34
#define RFC1533_LLARPCACHETMO	35
#define RFC1533_LLETHERNETENCAP	36
#define RFC1533_TCPTTL		37
#define RFC1533_TCPKEEPALIVETMO	38
#define RFC1533_TCPKEEPALIVEGB	39
#define RFC1533_NISDOMAIN	40
#define RFC1533_NISSERVER	41
#define RFC1533_NTPSERVER	42
#define RFC1533_VENDOR		43
#define RFC1533_NBNS		44
#define RFC1533_NBDD		45
#define RFC1533_NBNT		46
#define RFC1533_NBSCOPE		47
#define RFC1533_XFS		48
#define RFC1533_XDM		49
#ifndef	NO_DHCP_SUPPORT
#define RFC2132_REQ_ADDR	50
#define RFC2132_MSG_TYPE	53
#define RFC2132_SRV_ID		54
#define RFC2132_PARAM_LIST	55
#define RFC2132_MAX_SIZE	57
#define RFC2132_VENDOR_CLASS_ID	60

#define DHCPDISCOVER		1
#define DHCPOFFER		2
#define DHCPREQUEST		3
#define DHCPACK			5
#endif	/* NO_DHCP_SUPPORT */

#define RFC1533_VENDOR_MAJOR	0
#define RFC1533_VENDOR_MINOR	0

#define RFC1533_VENDOR_MAGIC	128
#define RFC1533_VENDOR_ADDPARM	129
#define RFC1533_VENDOR_MNUOPTS	160
#define RFC1533_VENDOR_SELECTION 176
#define RFC1533_VENDOR_MOTD	184
#define RFC1533_VENDOR_NUMOFMOTD 8
#define RFC1533_VENDOR_IMG	192
#define RFC1533_VENDOR_NUMOFIMG	16

#define RFC1533_VENDOR_CONFIGFILE	150

#define RFC1533_END		255

#define BOOTP_VENDOR_LEN	64
#ifndef	NO_DHCP_SUPPORT
#define DHCP_OPT_LEN		312
#endif	/* NO_DHCP_SUPPORT */

#define	TFTP_DEFAULTSIZE_PACKET	512
#define	TFTP_MAX_PACKET		1432 /* 512 */

#define TFTP_RRQ	1
#define TFTP_WRQ	2
#define TFTP_DATA	3
#define TFTP_ACK	4
#define TFTP_ERROR	5
#define TFTP_OACK	6

#define TFTP_CODE_EOF	1
#define TFTP_CODE_MORE	2
#define TFTP_CODE_ERROR	3
#define TFTP_CODE_BOOT	4
#define TFTP_CODE_CFG	5

#define AWAIT_ARP	0
#define AWAIT_BOOTP	1
#define AWAIT_TFTP	2
#define AWAIT_RARP	3
#define AWAIT_RPC	4
#define AWAIT_QDRAIN	5	/* drain queue, process ARP requests */

typedef struct
{
  unsigned long	s_addr;
}
in_addr;

struct arptable_t
{
  in_addr ipaddr;
  unsigned char node[6];
};

/*
 * A pity sipaddr and tipaddr are not longword aligned or we could use
 * in_addr. No, I don't want to use #pragma packed.
 */
struct arprequest
{
  unsigned short hwtype;
  unsigned short protocol;
  char hwlen;
  char protolen;
  unsigned short opcode;
  char shwaddr[6];
  char sipaddr[4];
  char thwaddr[6];
  char tipaddr[4];
};

struct iphdr
{
  char verhdrlen;
  char service;
  unsigned short len;
  unsigned short ident;
  unsigned short frags;
  char ttl;
  char protocol;
  unsigned short chksum;
  in_addr src;
  in_addr dest;
};

struct udphdr
{
  unsigned short src;
  unsigned short dest;
  unsigned short len;
  unsigned short chksum;
};

/* Format of a bootp packet.  */
struct bootp_t
{
  char bp_op;
  char bp_htype;
  char bp_hlen;
  char bp_hops;
  unsigned long bp_xid;
  unsigned short bp_secs;
  unsigned short unused;
  in_addr bp_ciaddr;
  in_addr bp_yiaddr;
  in_addr bp_siaddr;
  in_addr bp_giaddr;
  char bp_hwaddr[16];
  char bp_sname[64];
  char bp_file[128];
#ifdef	NO_DHCP_SUPPORT
  char bp_vend[BOOTP_VENDOR_LEN];
#else
  char bp_vend[DHCP_OPT_LEN];
#endif	/* NO_DHCP_SUPPORT */
};

/* Format of a bootp IP packet.  */
struct bootpip_t
{
  struct iphdr ip;
  struct udphdr udp;
  struct bootp_t bp;
};

/* Format of bootp packet with extensions.  */
struct bootpd_t
{
  struct bootp_t bootp_reply;
  unsigned char  bootp_extension[MAX_BOOTP_EXTLEN];
};

struct tftp_t
{
  struct iphdr ip;
  struct udphdr udp;
  unsigned short opcode;
  union
  {
    char rrq[TFTP_DEFAULTSIZE_PACKET];
    
    struct
    {
      unsigned short block;
      char download[TFTP_MAX_PACKET];
    }
    data;
    
    struct
    {
      unsigned short block;
    }
    ack;
    
    struct
    {
      unsigned short errcode;
      char errmsg[TFTP_DEFAULTSIZE_PACKET];
    }
    err;
    
    struct
    {
      char data[TFTP_DEFAULTSIZE_PACKET+2];
    }
    oack;
  }
  u;
};

/* Define a smaller tftp packet solely for making requests to conserve stack
   512 bytes should be enough.  */
struct tftpreq_t
{
  struct iphdr ip;
  struct udphdr udp;
  unsigned short opcode;
  union
  {
    char rrq[512];
    
    struct
    {
      unsigned short block;
    }
    ack;
    
    struct
    {
      unsigned short errcode;
      char errmsg[512-2];
    }
    err;
  }
  u;
};

#define TFTP_MIN_PACKET	(sizeof(struct iphdr) + sizeof(struct udphdr) + 4)

struct rpc_t
{
  struct iphdr ip;
  struct udphdr udp;
  union
  {
    char data[300];		/* longest RPC call must fit!!!! */
    
    struct
    {
      long id;
      long type;
      long rpcvers;
      long prog;
      long vers;
      long proc;
      long data[1];
    }
    call;
    
    struct
    {
      long id;
      long type;
      long rstatus;
      long verifier;
      long v2;
      long astatus;
      long data[1];
    }
    reply;
  }
  u;
};

#define PROG_PORTMAP	100000
#define PROG_NFS	100003
#define PROG_MOUNT	100005

#define MSG_CALL	0
#define MSG_REPLY	1

#define PORTMAP_GETPORT	3

#define MOUNT_ADDENTRY	1
#define MOUNT_UMOUNTALL	4

#define NFS_LOOKUP	4
#define NFS_READ	6

#define NFS_FHSIZE	32

#define NFSERR_PERM	1
#define NFSERR_NOENT	2
#define NFSERR_ACCES	13

/* Block size used for NFS read accesses.  A RPC reply packet (including  all
 * headers) must fit within a single Ethernet frame to avoid fragmentation.
 * Chosen to be a power of two, as most NFS servers are optimized for this.  */
#define NFS_READ_SIZE	1024

#define	FLOPPY_BOOT_LOCATION	0x7c00
/* Must match offsets in loader.S */
#define ROM_SEGMENT		0x1fa
#define ROM_LENGTH		0x1fc

#define	ROM_INFO_LOCATION	(FLOPPY_BOOT_LOCATION + ROM_SEGMENT)
/* at end of floppy boot block */

struct rom_info
{
  unsigned short	rom_segment;
  unsigned short	rom_length;
};

static inline int
rom_address_ok (struct rom_info *rom, int assigned_rom_segment)
{
  return (assigned_rom_segment < 0xC000
	  || assigned_rom_segment == rom->rom_segment);
}

/* Define a type for passing info to a loaded program.  */
struct ebinfo
{
  unsigned char	major, minor;	/* Version */
  unsigned short	flags;		/* Bit flags */
};

/***************************************************************************
External prototypes
***************************************************************************/
/* main.c */
extern void print_network_configuration (void);
extern int ifconfig (char *ip, char *sm, char *gw, char *svr);
extern int udp_transmit (unsigned long destip, unsigned int srcsock,
			 unsigned int destsock, int len, const void *buf);
extern int await_reply (int type, int ival, void *ptr, int timeout);
extern int decode_rfc1533 (unsigned char *, int, int, int);
extern long rfc2131_sleep_interval (int base, int exp);
extern void cleanup (void);
extern int rarp (void);
extern int bootp (void);
extern void cleanup_net (void);

/* config.c */
extern void print_config (void);
extern void eth_reset (void);
extern int eth_probe (void);
extern int eth_poll (void);
extern void eth_transmit (const char *d, unsigned int t,
			  unsigned int s, const void *p);
extern void eth_disable (void);

/* misc.c */
extern void twiddle (void);
extern void sleep (int secs);
extern int getdec (char **s);
extern void etherboot_printf (const char *, ...);
extern int etherboot_sprintf (char *, const char *, ...);
extern int inet_aton (char *p, in_addr *i);

/***************************************************************************
External variables
***************************************************************************/
/* main.c */
extern int ip_abort;
extern int network_ready;
extern struct rom_info rom;
extern struct arptable_t arptable[MAX_ARP];
extern struct bootpd_t bootp_data;
#define	BOOTP_DATA_ADDR	(&bootp_data)
extern unsigned char *end_of_rfc1533;

/* config.c */
extern struct nic nic;

/* Local hack - define some macros to use etherboot source files "as is".  */
#ifndef GRUB
# undef printf
# define printf	etherboot_printf
# undef sprintf
# define sprintf etherboot_sprintf
#endif /* GRUB */

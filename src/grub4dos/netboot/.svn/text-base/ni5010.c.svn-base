/**************************************************************************
Etherboot -  BOOTP/TFTP Bootstrap Program
Driver for NI5010.
Code freely taken from Jan-Pascal van Best and Andreas Mohr's
Linux NI5010 driver.
***************************************************************************/

/*
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2, or (at
 * your option) any later version.
 */

/* to get some global routines like printf */
#include "etherboot.h"
/* to get the interface to the body of the program */
#include "nic.h"
/* to get our own prototype */
#include "cards.h"

/* ni5010.h file included verbatim */
/*
 * Racal-Interlan ni5010 Ethernet definitions
 *
 * This is an extension to the Linux operating system, and is covered by the
 * same Gnu Public License that covers that work.
 *
 * copyrights (c) 1996 by Jan-Pascal van Best (jvbest@wi.leidenuniv.nl)
 *
 * I have done a look in the following sources:
 *   crynwr-packet-driver by Russ Nelson
 */

#define NI5010_BUFSIZE	2048	/* number of bytes in a buffer */

#define NI5010_MAGICVAL0 0x00  /* magic-values for ni5010 card */
#define NI5010_MAGICVAL1 0x55
#define NI5010_MAGICVAL2 0xAA

#define SA_ADDR0 0x02
#define SA_ADDR1 0x07
#define SA_ADDR2 0x01

/* The number of low I/O ports used by the ni5010 ethercard. */
#define NI5010_IO_EXTENT       32

#define PRINTK(x) if (NI5010_DEBUG) printk x
#define PRINTK2(x) if (NI5010_DEBUG>=2) printk x
#define PRINTK3(x) if (NI5010_DEBUG>=3) printk x

/* The various IE command registers */
#define EDLC_XSTAT	(ioaddr + 0x00)	/* EDLC transmit csr */
#define EDLC_XCLR	(ioaddr + 0x00)	/* EDLC transmit "Clear IRQ" */
#define EDLC_XMASK	(ioaddr + 0x01)	/* EDLC transmit "IRQ Masks" */
#define EDLC_RSTAT	(ioaddr + 0x02)	/* EDLC receive csr */
#define EDLC_RCLR	(ioaddr + 0x02)	/* EDLC receive "Clear IRQ" */
#define EDLC_RMASK	(ioaddr + 0x03)	/* EDLC receive "IRQ Masks" */
#define EDLC_XMODE	(ioaddr + 0x04)	/* EDLC transmit Mode */
#define EDLC_RMODE	(ioaddr + 0x05)	/* EDLC receive Mode */
#define EDLC_RESET	(ioaddr + 0x06)	/* EDLC RESET register */
#define EDLC_TDR1	(ioaddr + 0x07)	/* "Time Domain Reflectometry" reg1 */
#define EDLC_ADDR	(ioaddr + 0x08)	/* EDLC station address, 6 bytes */
	 			/* 0x0E doesn't exist for r/w */
#define EDLC_TDR2	(ioaddr + 0x0f)	/* "Time Domain Reflectometry" reg2 */
#define IE_GP		(ioaddr + 0x10)	/* GP pointer (word register) */
				/* 0x11 is 2nd byte of GP Pointer */
#define IE_RCNT		(ioaddr + 0x10)	/* Count of bytes in rcv'd packet */
 				/* 0x11 is 2nd byte of "Byte Count" */
#define IE_MMODE	(ioaddr + 0x12)	/* Memory Mode register */
#define IE_DMA_RST	(ioaddr + 0x13)	/* IE DMA Reset.  write only */
#define IE_ISTAT	(ioaddr + 0x13)	/* IE Interrupt Status.  read only */
#define IE_RBUF		(ioaddr + 0x14)	/* IE Receive Buffer port */
#define IE_XBUF		(ioaddr + 0x15)	/* IE Transmit Buffer port */
#define IE_SAPROM	(ioaddr + 0x16)	/* window on station addr prom */
#define IE_RESET	(ioaddr + 0x17)	/* any write causes Board Reset */

/* bits in EDLC_XSTAT, interrupt clear on write, status when read */
#define XS_TPOK		0x80	/* transmit packet successful */
#define XS_CS		0x40	/* carrier sense */
#define XS_RCVD		0x20	/* transmitted packet received */
#define XS_SHORT	0x10	/* transmission media is shorted */
#define XS_UFLW		0x08	/* underflow.  iff failed board */
#define XS_COLL		0x04	/* collision occurred */
#define XS_16COLL	0x02	/* 16th collision occurred */
#define XS_PERR		0x01	/* parity error */

#define XS_CLR_UFLW	0x08	/* clear underflow */
#define XS_CLR_COLL	0x04	/* clear collision */
#define XS_CLR_16COLL	0x02	/* clear 16th collision */
#define XS_CLR_PERR	0x01	/* clear parity error */

/* bits in EDLC_XMASK, mask/enable transmit interrupts.  register is r/w */
#define XM_TPOK		0x80	/* =1 to enable Xmt Pkt OK interrupts */
#define XM_RCVD		0x20	/* =1 to enable Xmt Pkt Rcvd ints */
#define XM_UFLW		0x08	/* =1 to enable Xmt Underflow ints */
#define XM_COLL		0x04	/* =1 to enable Xmt Collision ints */
#define XM_COLL16	0x02	/* =1 to enable Xmt 16th Coll ints */
#define XM_PERR		0x01	/* =1 to enable Xmt Parity Error ints */
 				/* note: always clear this bit */
#define XM_ALL		(XM_TPOK | XM_RCVD | XM_UFLW | XM_COLL | XM_COLL16)

/* bits in EDLC_RSTAT, interrupt clear on write, status when read */
#define RS_PKT_OK	0x80	/* received good packet */
#define RS_RST_PKT	0x10	/* RESET packet received */
#define RS_RUNT		0x08	/* Runt Pkt rcvd.  Len < 64 Bytes */
#define RS_ALIGN	0x04	/* Alignment error. not 8 bit aligned */
#define RS_CRC_ERR	0x02	/* Bad CRC on rcvd pkt */
#define RS_OFLW		0x01	/* overflow for rcv FIFO */
#define RS_VALID_BITS	( RS_PKT_OK | RS_RST_PKT | RS_RUNT | RS_ALIGN | RS_CRC_ERR | RS_OFLW )
 				/* all valid RSTAT bits */

#define RS_CLR_PKT_OK	0x80	/* clear rcvd packet interrupt */
#define RS_CLR_RST_PKT	0x10	/* clear RESET packet received */
#define RS_CLR_RUNT	0x08	/* clear Runt Pckt received */
#define RS_CLR_ALIGN	0x04	/* clear Alignment error */
#define RS_CLR_CRC_ERR	0x02	/* clear CRC error */
#define RS_CLR_OFLW	0x01	/* clear rcv FIFO Overflow */

/* bits in EDLC_RMASK, mask/enable receive interrupts.  register is r/w */
#define RM_PKT_OK	0x80	/* =1 to enable rcvd good packet ints */
#define RM_RST_PKT	0x10	/* =1 to enable RESET packet ints */
#define RM_RUNT		0x08	/* =1 to enable Runt Pkt rcvd ints */
#define RM_ALIGN	0x04	/* =1 to enable Alignment error ints */
#define RM_CRC_ERR	0x02	/* =1 to enable Bad CRC error ints */
#define RM_OFLW		0x01	/* =1 to enable overflow error ints */

/* bits in EDLC_RMODE, set Receive Packet mode.  register is r/w */
#define RMD_TEST	0x80	/* =1 for Chip testing.  normally 0 */
#define RMD_ADD_SIZ	0x10	/* =1 5-byte addr match.  normally 0 */
#define RMD_EN_RUNT	0x08	/* =1 enable runt rcv.  normally 0 */
#define RMD_EN_RST	0x04	/* =1 to rcv RESET pkt.  normally 0 */

#define RMD_PROMISC	0x03	/* receive *all* packets.  unusual */
#define RMD_MULTICAST	0x02	/* receive multicasts too.  unusual */
#define RMD_BROADCAST	0x01	/* receive broadcasts & normal. usual */
#define RMD_NO_PACKETS	0x00	/* don't receive any packets. unusual */

/* bits in EDLC_XMODE, set Transmit Packet mode.  register is r/w */
#define XMD_COLL_CNT	0xf0	/* coll's since success.  read-only */
#define XMD_IG_PAR	0x08	/* =1 to ignore parity.  ALWAYS set */
#define XMD_T_MODE	0x04	/* =1 to power xcvr. ALWAYS set this */
#define XMD_LBC		0x02	/* =1 for loopback.  normally set */
#define XMD_DIS_C	0x01	/* =1 disables contention. normally 0 */

/* bits in EDLC_RESET, write only */
#define RS_RESET	0x80	/* =1 to hold EDLC in reset state */

/* bits in IE_MMODE, write only */
#define MM_EN_DMA	0x80	/* =1 begin DMA xfer, Cplt clrs it */
#define MM_EN_RCV	0x40	/* =1 allows Pkt rcv.  clr'd by rcv */
#define MM_EN_XMT	0x20	/* =1 begin Xmt pkt.  Cplt clrs it */
#define MM_BUS_PAGE	0x18	/* =00 ALWAYS.  Used when MUX=1 */
#define MM_NET_PAGE	0x06	/* =00 ALWAYS.  Used when MUX=0 */
#define MM_MUX		0x01	/* =1 means Rcv Buff on system bus */
				/* =0 means Xmt Buff on system bus */

/* bits in IE_ISTAT, read only */
#define IS_TDIAG	0x80	/* =1 if Diagnostic problem */
#define IS_EN_RCV	0x20	/* =1 until frame is rcv'd cplt */
#define IS_EN_XMT	0x10	/* =1 until frame is xmt'd cplt */
#define IS_EN_DMA	0x08	/* =1 until DMA is cplt or aborted */
#define IS_DMA_INT	0x04	/* =0 iff DMA done interrupt. */
#define IS_R_INT	0x02	/* =0 iff unmasked Rcv interrupt */
#define IS_X_INT	0x01	/* =0 iff unmasked Xmt interrupt */

/* NIC specific static variables go here */

static unsigned short		ioaddr = 0;
static unsigned int		bufsize_rcv = 0;

#if	0
static void show_registers(void)
{
	printf("XSTAT %hhX ", inb(EDLC_XSTAT));
	printf("XMASK %hhX ", inb(EDLC_XMASK));
	printf("RSTAT %hhX ", inb(EDLC_RSTAT));
	printf("RMASK %hhX ", inb(EDLC_RMASK));
	printf("RMODE %hhX ", inb(EDLC_RMODE));
	printf("XMODE %hhX ", inb(EDLC_XMODE));
	printf("ISTAT %hhX\n", inb(IE_ISTAT));
}
#endif

static void reset_receiver(void)
{
	outw(0, IE_GP);		/* Receive packet at start of buffer */
	outb(RS_VALID_BITS, EDLC_RCLR);	/* Clear all pending Rcv interrupts */
	outb(MM_EN_RCV, IE_MMODE); /* Enable rcv */
}

/**************************************************************************
RESET - Reset adapter
***************************************************************************/
static void ni5010_reset(struct nic *nic)
{
	int		i;

	/* Reset the hardware here.  Don't forget to set the station address. */
	outb(RS_RESET, EDLC_RESET);	/* Hold up EDLC_RESET while configing board */
	outb(0, IE_RESET);	/* Hardware reset of ni5010 board */
	outb(0, EDLC_XMASK);	/* Disable all Xmt interrupts */
	outb(0, EDLC_RMASK);	/* Disable all Rcv interrupt */
	outb(0xFF, EDLC_XCLR);	/* Clear all pending Xmt interrupts */
	outb(0xFF, EDLC_RCLR);	/* Clear all pending Rcv interrupts */
	outb(XMD_LBC, EDLC_XMODE);	/* Only loopback xmits */
	/* Set the station address */
	for(i = 0; i < ETH_ALEN; i++)
		outb(nic->node_addr[i], EDLC_ADDR + i);
	outb(XMD_IG_PAR | XMD_T_MODE | XMD_LBC, EDLC_XMODE); 
				/* Normal packet xmit mode */
	outb(RMD_BROADCAST, EDLC_RMODE);
				/* Receive broadcast and normal packets */
	reset_receiver();
	outb(0x00, EDLC_RESET);	/* Un-reset the ni5010 */
}

/**************************************************************************
POLL - Wait for a frame
***************************************************************************/
static int ni5010_poll(struct nic *nic)
{
	int		rcv_stat;

	if (((rcv_stat = inb(EDLC_RSTAT)) & RS_VALID_BITS) != RS_PKT_OK) {
		outb(rcv_stat, EDLC_RSTAT);	/* Clear the status */
		return (0);
	}
        outb(rcv_stat, EDLC_RCLR);	/* Clear the status */
	nic->packetlen = inw(IE_RCNT);
	/* Read packet into buffer */
        outb(MM_MUX, IE_MMODE);	/* Rcv buffer to system bus */
	outw(0, IE_GP);		/* Seek to beginning of packet */
	insb(IE_RBUF, nic->packet, nic->packetlen); 
	return (1);
}

/**************************************************************************
TRANSMIT - Transmit a frame
***************************************************************************/
static void ni5010_transmit(struct nic *nic,
	const char *d,	/* Destination */
	unsigned int t,	/* Type */
	unsigned int s,	/* size */
	const char *p)	/* Packet */
{
	unsigned int	len;
	int		buf_offs, xmt_stat;
	unsigned long	time;

	len = s + ETH_HLEN;
	if (len < ETH_ZLEN)
		len = ETH_ZLEN;
	buf_offs = NI5010_BUFSIZE - len;
	outb(0, EDLC_RMASK);	/* Mask all receive interrupts */
	outb(0, IE_MMODE);	/* Put Xmit buffer on system bus */
	outb(0xFF, EDLC_RCLR);	/* Clear out pending rcv interrupts */
	outw(buf_offs, IE_GP);	/* Point GP at start of packet */
	outsb(IE_XBUF, d, ETH_ALEN);	/* Put dst in buffer */
	outsb(IE_XBUF, nic->node_addr, ETH_ALEN);/* Put src in buffer */
	outb(t >> 8, IE_XBUF);
	outb(t, IE_XBUF);
	outsb(IE_XBUF, p, s);	/* Put data in buffer */
	while (s++ < ETH_ZLEN - ETH_HLEN)	/* Pad to min size */
		outb(0, IE_XBUF);
	outw(buf_offs, IE_GP);	/* Rewrite where packet starts */
	/* should work without that outb() (Crynwr used it) */
	/*outb(MM_MUX, IE_MMODE);*/
	/* Xmt buffer to EDLC bus */
	outb(MM_EN_XMT | MM_MUX, IE_MMODE);	/* Begin transmission */
	/* wait for transmit complete */
	while (((xmt_stat = inb(IE_ISTAT)) & IS_EN_XMT) != 0)
		;
	reset_receiver();	/* Immediately switch to receive */
}

/**************************************************************************
DISABLE - Turn off ethernet interface
***************************************************************************/
static void ni5010_disable(struct nic *nic)
{
	outb(0, IE_MMODE);
	outb(RS_RESET, EDLC_RESET);
}

static inline int rd_port(void)
{
	inb(IE_RBUF);
	return inb(IE_SAPROM);
}

static int ni5010_probe1(struct nic *nic)
{
	int		i, boguscount = 40, data;

	/* The tests are from the Linux NI5010 driver
	   I don't understand it all, but if it works for them...  */
	if (inb(ioaddr) == 0xFF)
		return (0);
	while ((rd_port() & rd_port() & rd_port()
		& rd_port() & rd_port() & rd_port()) != 0xFF)
	{
		if (boguscount-- <= 0)
			return (0);
	}
	for (i = 0; i < 32; i++)
		if ((data = rd_port()) != 0xFF)
			break;
	if (data == 0xFF)
		return (0);
	if (data == SA_ADDR0 && rd_port() == SA_ADDR1 && rd_port() == SA_ADDR2) {
		for (i = 0; i < 4; i++)
			rd_port();
		if (rd_port() != NI5010_MAGICVAL1 || rd_port() != NI5010_MAGICVAL2)
			return (0);
	} else
		return (0);
	for (i = 0; i < ETH_ALEN; i++) {
		outw(i, IE_GP);
		nic->node_addr[i] = inb(IE_SAPROM);
	}
	printf("\nNI5010 ioaddr %#hX, addr %!\n", ioaddr, nic->node_addr);
/* get the size of the onboard receive buffer
 * higher addresses than bufsize are wrapped into real buffer
 * i.e. data for offs. 0x801 is written to 0x1 with a 2K onboard buffer
 */
	if (bufsize_rcv == 0) {
        	outb(1, IE_MMODE);      /* Put Rcv buffer on system bus */
        	outw(0, IE_GP);		/* Point GP at start of packet */
        	outb(0, IE_RBUF);	/* set buffer byte 0 to 0 */
        	for (i = 1; i < 0xFF; i++) {
                	outw(i << 8, IE_GP); /* Point GP at packet size to be tested */
                	outb(i, IE_RBUF);
                	outw(0x0, IE_GP); /* Point GP at start of packet */
                	data = inb(IE_RBUF);
                	if (data == i) break;
        	}
		bufsize_rcv = i << 8;
        	outw(0, IE_GP);		/* Point GP at start of packet */
        	outb(0, IE_RBUF);	/* set buffer byte 0 to 0 again */
	}
	printf("Bufsize rcv/xmt=%d/%d\n", bufsize_rcv, NI5010_BUFSIZE);
	return (1);
}

/**************************************************************************
PROBE - Look for an adapter, this routine's visible to the outside
***************************************************************************/
struct nic *ni5010_probe(struct nic *nic, unsigned short *probe_addrs)
{
	static unsigned short	io_addrs[] = {
		0x300, 0x320, 0x340, 0x360, 0x380, 0x3a0, 0 };
	unsigned short		*p;

	/* if probe_addrs is 0, then use list above */
	if (probe_addrs == 0 || *probe_addrs == 0)
		probe_addrs = io_addrs;
	for (p = probe_addrs; (ioaddr = *p) != 0; p++) {
		if (ni5010_probe1(nic))
			break;
	}
	if (ioaddr == 0)
		return (0);
	ni5010_reset(nic);
	/* point to NIC specific routines */
	nic->reset = ni5010_reset;
	nic->poll = ni5010_poll;
	nic->transmit = ni5010_transmit;
	nic->disable = ni5010_disable;
	return (nic);
}

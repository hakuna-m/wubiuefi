/**************************************************************************
Etherboot -  BOOTP/TFTP Bootstrap Program
LANCE NIC driver for Etherboot
Large portions borrowed from the Linux LANCE driver by Donald Becker
Ken Yap, July 1997
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
#ifdef	INCLUDE_LANCE
#include "pci.h"
#endif
#include "cards.h"

/* Offsets from base I/O address */
#if	defined(INCLUDE_NE2100) || defined(INCLUDE_LANCE)
#define	LANCE_ETH_ADDR	0x0
#define	LANCE_DATA	0x10
#define	LANCE_ADDR	0x12
#define	LANCE_RESET	0x14
#define	LANCE_BUS_IF	0x16
#define	LANCE_TOTAL_SIZE	0x18
#endif
#ifdef	INCLUDE_NI6510
#define	LANCE_ETH_ADDR	0x8
#define	LANCE_DATA	0x0
#define	LANCE_ADDR	0x2
#define	LANCE_RESET	0x4
#define	LANCE_BUS_IF	0x6
#define	LANCE_TOTAL_SIZE	0x10
#endif

/* lance_poll() now can use multiple Rx buffers to prevent packet loss. Set
 * Set LANCE_LOG_RX_BUFFERS to 0..7 for 1, 2, 4, 8, 16, 32, 64 or 128 Rx
 * buffers. Usually 4 (=16 Rx buffers) is a good value. (Andreas Neuhaus)
 * Decreased to 2 (=4 Rx buffers) (Ken Yap, 20010305) */

#define LANCE_LOG_RX_BUFFERS	2		/* Use 2^2=4 Rx buffers */

#define RX_RING_SIZE		(1 << (LANCE_LOG_RX_BUFFERS))
#define RX_RING_MOD_MASK	(RX_RING_SIZE - 1)
#define RX_RING_LEN_BITS	((LANCE_LOG_RX_BUFFERS) << 29)

struct lance_init_block
{
	unsigned short	mode;
	unsigned char	phys_addr[ETH_ALEN];
	unsigned long	filter[2];
	Address		rx_ring;
	Address		tx_ring;
};

struct lance_rx_head
{
	union {
		Address		base;
		unsigned char	addr[4];
	} u;
	short		buf_length;	/* 2s complement */
	short		msg_length;
};

struct lance_tx_head
{
	union {
		Address		base;
		unsigned char	addr[4];
	} u;
	short		buf_length;	/* 2s complement */
	short		misc;
};

struct lance_interface
{
	struct lance_init_block	init_block;
	struct lance_rx_head	rx_ring[RX_RING_SIZE];
	struct lance_tx_head	tx_ring;
	unsigned char		rbuf[RX_RING_SIZE][ETH_FRAME_LEN+4];
	unsigned char		tbuf[ETH_FRAME_LEN];
	/*
	 * Do not alter the order of the struct members above;
	 * the hardware depends on the correct alignment.
	 */
	int			rx_idx;
};

#define	LANCE_MUST_PAD		0x00000001
#define	LANCE_ENABLE_AUTOSELECT	0x00000002
#define	LANCE_SELECT_PHONELINE	0x00000004
#define	LANCE_MUST_UNRESET	0x00000008

/* A mapping from the chip ID number to the part number and features.
   These are from the datasheets -- in real life the '970 version
   reportedly has the same ID as the '965. */
static const struct lance_chip_type
{
	int	id_number;
	const char	*name;
	int	flags;
} chip_table[] = {
	{0x0000, "LANCE 7990",			/* Ancient lance chip.  */
		LANCE_MUST_PAD + LANCE_MUST_UNRESET},
	{0x0003, "PCnet/ISA 79C960",		/* 79C960 PCnet/ISA.  */
		LANCE_ENABLE_AUTOSELECT},
	{0x2260, "PCnet/ISA+ 79C961",		/* 79C961 PCnet/ISA+, Plug-n-Play.  */
		LANCE_ENABLE_AUTOSELECT},
	{0x2420, "PCnet/PCI 79C970",		/* 79C970 or 79C974 PCnet-SCSI, PCI. */
		LANCE_ENABLE_AUTOSELECT},
	/* Bug: the PCnet/PCI actually uses the PCnet/VLB ID number, so just call
		it the PCnet32. */
	{0x2430, "PCnet32",			/* 79C965 PCnet for VL bus. */
		LANCE_ENABLE_AUTOSELECT},
        {0x2621, "PCnet/PCI-II 79C970A",        /* 79C970A PCInetPCI II. */
                LANCE_ENABLE_AUTOSELECT},
	{0x2625, "PCnet-FAST III 79C973",	/* 79C973 PCInet-FAST III. */
		LANCE_ENABLE_AUTOSELECT},
        {0x2626, "PCnet/HomePNA 79C978",        
                LANCE_ENABLE_AUTOSELECT|LANCE_SELECT_PHONELINE},
	{0x0, "PCnet (unknown)",
		LANCE_ENABLE_AUTOSELECT},
};

/* Define a macro for converting program addresses to real addresses */
#undef	virt_to_bus
#define	virt_to_bus(x)		((unsigned long)x)

static int			chip_version;
static int			lance_version;
static unsigned short		ioaddr;
#ifndef	INCLUDE_LANCE
static int			dma;
#endif
static struct lance_interface	*lp;

/* additional 8 bytes for 8-byte alignment space */
#ifdef	USE_LOWMEM_BUFFER
#define lance ((char *)0x10000 - (sizeof(struct lance_interface)+8))
#else
static char			lance[sizeof(struct lance_interface)+8];
#endif

#ifndef	INCLUDE_LANCE
/* DMA defines and helper routines */

/* DMA controller registers */
#define DMA1_CMD_REG		0x08	/* command register (w) */
#define DMA1_STAT_REG		0x08	/* status register (r) */
#define DMA1_REQ_REG            0x09    /* request register (w) */
#define DMA1_MASK_REG		0x0A	/* single-channel mask (w) */
#define DMA1_MODE_REG		0x0B	/* mode register (w) */
#define DMA1_CLEAR_FF_REG	0x0C	/* clear pointer flip-flop (w) */
#define DMA1_TEMP_REG           0x0D    /* Temporary Register (r) */
#define DMA1_RESET_REG		0x0D	/* Master Clear (w) */
#define DMA1_CLR_MASK_REG       0x0E    /* Clear Mask */
#define DMA1_MASK_ALL_REG       0x0F    /* all-channels mask (w) */

#define DMA2_CMD_REG		0xD0	/* command register (w) */
#define DMA2_STAT_REG		0xD0	/* status register (r) */
#define DMA2_REQ_REG            0xD2    /* request register (w) */
#define DMA2_MASK_REG		0xD4	/* single-channel mask (w) */
#define DMA2_MODE_REG		0xD6	/* mode register (w) */
#define DMA2_CLEAR_FF_REG	0xD8	/* clear pointer flip-flop (w) */
#define DMA2_TEMP_REG           0xDA    /* Temporary Register (r) */
#define DMA2_RESET_REG		0xDA	/* Master Clear (w) */
#define DMA2_CLR_MASK_REG       0xDC    /* Clear Mask */
#define DMA2_MASK_ALL_REG       0xDE    /* all-channels mask (w) */


#define DMA_MODE_READ	0x44	/* I/O to memory, no autoinit, increment, single mode */
#define DMA_MODE_WRITE	0x48	/* memory to I/O, no autoinit, increment, single mode */
#define DMA_MODE_CASCADE 0xC0   /* pass thru DREQ->HRQ, DACK<-HLDA only */

/* enable/disable a specific DMA channel */
static void enable_dma(unsigned int dmanr)
{
	if (dmanr <= 3)
		outb_p(dmanr, DMA1_MASK_REG);
	else
		outb_p(dmanr & 3, DMA2_MASK_REG);
}

static void disable_dma(unsigned int dmanr)
{
	if (dmanr <= 3)
		outb_p(dmanr | 4, DMA1_MASK_REG);
	else
		outb_p((dmanr & 3) | 4, DMA2_MASK_REG);
}

/* set mode (above) for a specific DMA channel */
static void set_dma_mode(unsigned int dmanr, char mode)
{
	if (dmanr <= 3)
		outb_p(mode | dmanr, DMA1_MODE_REG);
	else
		outb_p(mode | (dmanr&3), DMA2_MODE_REG);
}
#endif	/* !INCLUDE_LANCE */

/**************************************************************************
RESET - Reset adapter
***************************************************************************/
static void lance_reset(struct nic *nic)
{
	int		i;
	Address		l;

	/* Reset the LANCE */
	(void)inw(ioaddr+LANCE_RESET);
	/* Un-Reset the LANCE, needed only for the NE2100 */
	if (chip_table[lance_version].flags & LANCE_MUST_UNRESET)
		outw(0, ioaddr+LANCE_RESET);
	if (chip_table[lance_version].flags & LANCE_ENABLE_AUTOSELECT)
	{
		/* This is 79C960 specific; Turn on auto-select of media
		   (AUI, BNC). */
		outw(0x2, ioaddr+LANCE_ADDR);
		/* Don't touch 10base2 power bit. */
		outw(inw(ioaddr+LANCE_BUS_IF) | 0x2, ioaddr+LANCE_BUS_IF);
	}
	/* HomePNA cards need to explicitly pick the phoneline interface.
	 * Some of these cards have ethernet interfaces as well, this
	 * code might require some modification for those.
  	 */
        if (chip_table[lance_version].flags & LANCE_SELECT_PHONELINE) {
                short media, check ;
                /* this is specific to HomePNA cards... */
                outw(49, ioaddr+0x12) ;
                media = inw(ioaddr+0x16) ;
#ifdef DEBUG
                printf("media was %d\n", media) ;
#endif
                media &= ~3 ;
                media |= 1 ;
#ifdef DEBUG
                printf("media changed to %d\n", media) ;
#endif
                media &= ~3 ;
                media |= 1 ;
                outw(49, ioaddr+0x12) ;
                outw(media, ioaddr+0x16) ;
                outw(49, ioaddr+0x12) ;
                check = inw(ioaddr+0x16) ;
#ifdef DEBUG
                printf("check %s, media was set properly\n", 
			check ==  media ? "passed" : "FAILED" ) ; 
#endif
	}
 
	/* Re-initialise the LANCE, and start it when done. */
	/* Set station address */
	for (i = 0; i < ETH_ALEN; ++i)
		lp->init_block.phys_addr[i] = nic->node_addr[i];
	/* Preset the receive ring headers */
	for (i=0; i<RX_RING_SIZE; i++) {
		lp->rx_ring[i].buf_length = -ETH_FRAME_LEN-4;
		/* OWN */
		lp->rx_ring[i].u.base = virt_to_bus(lp->rbuf[i]) & 0xffffff;
		/* we set the top byte as the very last thing */
		lp->rx_ring[i].u.addr[3] = 0x80;
	}
	lp->rx_idx = 0;
	lp->init_block.mode = 0x0;	/* enable Rx and Tx */
	l = (Address)virt_to_bus(&lp->init_block);
	outw(0x1, ioaddr+LANCE_ADDR);
	(void)inw(ioaddr+LANCE_ADDR);
	outw((short)l, ioaddr+LANCE_DATA);
	outw(0x2, ioaddr+LANCE_ADDR);
	(void)inw(ioaddr+LANCE_ADDR);
	outw((short)(l >> 16), ioaddr+LANCE_DATA);
	outw(0x4, ioaddr+LANCE_ADDR);
	(void)inw(ioaddr+LANCE_ADDR);
	outw(0x915, ioaddr+LANCE_DATA);
	outw(0x0, ioaddr+LANCE_ADDR);
	(void)inw(ioaddr+LANCE_ADDR);
	outw(0x4, ioaddr+LANCE_DATA);		/* stop */
	outw(0x1, ioaddr+LANCE_DATA);		/* init */
	for (i = 10000; i > 0; --i)
		if (inw(ioaddr+LANCE_DATA) & 0x100)
			break;
#ifdef	DEBUG
	if (i <= 0)
		printf("Init timed out\n");
#endif
	/* Apparently clearing the InitDone bit here triggers a bug
	   in the '974. (Mark Stockton) */
	outw(0x2, ioaddr+LANCE_DATA);		/* start */
}

/**************************************************************************
POLL - Wait for a frame
***************************************************************************/
static int lance_poll(struct nic *nic)
{
	int		status;

	status = lp->rx_ring[lp->rx_idx].u.base >> 24;
	if (status & 0x80)
		return (0);
#ifdef	DEBUG
	printf("LANCE packet received rx_ring.u.base %X mcnt %hX csr0 %hX\n",
		lp->rx_ring[lp->rx_idx].u.base, lp->rx_ring[lp->rx_idx].msg_length,
		inw(ioaddr+LANCE_DATA));
#endif
	if (status == 0x3)
		memcpy(nic->packet, lp->rbuf[lp->rx_idx], nic->packetlen = lp->rx_ring[lp->rx_idx].msg_length);
	/* Andrew Boyd of QNX reports that some revs of the 79C765
	   clear the buffer length */
	lp->rx_ring[lp->rx_idx].buf_length = -ETH_FRAME_LEN-4;
	lp->rx_ring[lp->rx_idx].u.addr[3] |= 0x80;	/* prime for next receive */

	/* I'm not sure if the following is still ok with multiple Rx buffers, but it works */
	outw(0x0, ioaddr+LANCE_ADDR);
	(void)inw(ioaddr+LANCE_ADDR);
	outw(0x500, ioaddr+LANCE_DATA);		/* clear receive + InitDone */

	/* Switch to the next Rx ring buffer */
	lp->rx_idx = (lp->rx_idx + 1) & RX_RING_MOD_MASK;

	return (status == 0x3);
}

/**************************************************************************
TRANSMIT - Transmit a frame
***************************************************************************/
static void lance_transmit(
	struct nic *nic,
	const char *d,			/* Destination */
	unsigned int t,			/* Type */
	unsigned int s,			/* size */
	const char *p)			/* Packet */
{
	unsigned long		time;

	/* copy the packet to ring buffer */
	memcpy(lp->tbuf, d, ETH_ALEN);	/* dst */
	memcpy(&lp->tbuf[ETH_ALEN], nic->node_addr, ETH_ALEN); /* src */
	lp->tbuf[ETH_ALEN+ETH_ALEN] = t >> 8;	/* type */
	lp->tbuf[ETH_ALEN+ETH_ALEN+1] = t;	/* type */
	memcpy(&lp->tbuf[ETH_HLEN], p, s);
	s += ETH_HLEN;
	if (chip_table[chip_version].flags & LANCE_MUST_PAD)
		while (s < ETH_ZLEN)	/* pad to min length */
			lp->tbuf[s++] = 0;
	lp->tx_ring.buf_length = -s;
	lp->tx_ring.misc = 0x0;
	/* OWN, STP, ENP */
	lp->tx_ring.u.base = virt_to_bus(lp->tbuf) & 0xffffff;
	/* we set the top byte as the very last thing */
	lp->tx_ring.u.addr[3] = 0x83;
	/* Trigger an immediate send poll */
	outw(0x0, ioaddr+LANCE_ADDR);
	(void)inw(ioaddr+LANCE_ADDR);	/* as in the datasheets... */
	/* Klaus Espenlaub: the value below was 0x48, but that enabled the
	 * interrupt line, causing a hang if for some reasone the interrupt
	 * controller had the LANCE interrupt enabled.  I have no idea why
	 * nobody ran into this before...  */
	outw(0x08, ioaddr+LANCE_DATA);
	/* wait for transmit complete */
	time = currticks() + TICKS_PER_SEC;		/* wait one second */
	while (currticks() < time && (lp->tx_ring.u.base & 0x80000000) != 0)
		;
	if ((lp->tx_ring.u.base & 0x80000000) != 0)
		printf("LANCE timed out on transmit\n");
	(void)inw(ioaddr+LANCE_ADDR);
	outw(0x200, ioaddr+LANCE_DATA);		/* clear transmit + InitDone */
#ifdef	DEBUG
	printf("tx_ring.u.base %X tx_ring.buf_length %hX tx_ring.misc %hX csr0 %hX\n",
		lp->tx_ring.u.base, lp->tx_ring.buf_length, lp->tx_ring.misc,
		inw(ioaddr+LANCE_DATA));
#endif
}

static void lance_disable(struct nic *nic)
{
	(void)inw(ioaddr+LANCE_RESET);
	if (chip_table[lance_version].flags & LANCE_MUST_UNRESET)
		outw(0, ioaddr+LANCE_RESET);

	outw(0, ioaddr+LANCE_ADDR);
	outw(0x0004, ioaddr+LANCE_DATA);	/* stop the LANCE */

#ifndef	INCLUDE_LANCE
	disable_dma(dma);
#endif
}

#ifdef	INCLUDE_LANCE
static int lance_probe1(struct nic *nic, struct pci_device *pci)
#else
static int lance_probe1(struct nic *nic)
#endif
{
	int			reset_val ;
	unsigned int		i;
	Address			l;
	short			dma_channels;
#ifndef	INCLUDE_LANCE
	static const char	dmas[] = { 5, 6, 7, 3 };
#endif

	reset_val = inw(ioaddr+LANCE_RESET);
	outw(reset_val, ioaddr+LANCE_RESET);
#if	1  /* Klaus Espenlaub -- was #ifdef	INCLUDE_NE2100*/
	outw(0x0, ioaddr+LANCE_ADDR);	/* Switch to window 0 */
	if (inw(ioaddr+LANCE_DATA) != 0x4)
		return (-1);
#endif
	outw(88, ioaddr+LANCE_ADDR);	/* Get the version of the chip */
	if (inw(ioaddr+LANCE_ADDR) != 88)
		lance_version = 0;
	else
	{
		chip_version = inw(ioaddr+LANCE_DATA);
		outw(89, ioaddr+LANCE_ADDR);
		chip_version |= inw(ioaddr+LANCE_DATA) << 16;
		if ((chip_version & 0xfff) != 0x3)
			return (-1);
		chip_version = (chip_version >> 12) & 0xffff;
		for (lance_version = 1; chip_table[lance_version].id_number != 0; ++lance_version)
			if (chip_table[lance_version].id_number == chip_version)
				break;
	}
	/* make sure data structure is 8-byte aligned */
	l = ((Address)lance + 7) & ~7;
	lp = (struct lance_interface *)l;
	lp->init_block.mode = 0x3;	/* disable Rx and Tx */
	lp->init_block.filter[0] = lp->init_block.filter[1] = 0x0;
	/* using multiple Rx buffer and a single Tx buffer */
	lp->init_block.rx_ring = (virt_to_bus(&lp->rx_ring) & 0xffffff) | RX_RING_LEN_BITS;
	lp->init_block.tx_ring = virt_to_bus(&lp->tx_ring) & 0xffffff;
	l = virt_to_bus(&lp->init_block);
	outw(0x1, ioaddr+LANCE_ADDR);
	(void)inw(ioaddr+LANCE_ADDR);
	outw((unsigned short)l, ioaddr+LANCE_DATA);
	outw(0x2, ioaddr+LANCE_ADDR);
	(void)inw(ioaddr+LANCE_ADDR);
	outw((unsigned short)(l >> 16), ioaddr+LANCE_DATA);
	outw(0x4, ioaddr+LANCE_ADDR);
	(void)inw(ioaddr+LANCE_ADDR);
	outw(0x915, ioaddr+LANCE_DATA);
	outw(0x0, ioaddr+LANCE_ADDR);
	(void)inw(ioaddr+LANCE_ADDR);
	/* Get station address */
	for (i = 0; i < ETH_ALEN; ++i) {
		nic->node_addr[i] = inb(ioaddr+LANCE_ETH_ADDR+i);
	}
#ifndef	INCLUDE_LANCE
	/* now probe for DMA channel */
	dma_channels = ((inb(DMA1_STAT_REG) >> 4) & 0xf) |
		(inb(DMA2_STAT_REG) & 0xf0);
	/* need to fix when PCI provides DMA info */
	for (i = 0; i < (sizeof(dmas)/sizeof(dmas[0])); ++i)
	{
		int		j;

		dma = dmas[i];
		/* Don't enable a permanently busy DMA channel,
		   or the machine will hang */
		if (dma_channels & (1 << dma))
			continue;
		outw(0x7f04, ioaddr+LANCE_DATA);	/* clear memory error bits */
		set_dma_mode(dma, DMA_MODE_CASCADE);
		enable_dma(dma);
		outw(0x1, ioaddr+LANCE_DATA);		/* init */
		for (j = 100; j > 0; --j)
			if (inw(ioaddr+LANCE_DATA) & 0x900)
				break;
		if (inw(ioaddr+LANCE_DATA) & 0x100)
			break;
		else
			disable_dma(dma);
	}
	if (i >= (sizeof(dmas)/sizeof(dmas[0])))
		dma = 0;
	printf("\n%s base %#X, DMA %d, addr %!\n",
		chip_table[lance_version].name, ioaddr, dma, nic->node_addr);
#else
	printf(" %s base %#hX, addr %!\n", chip_table[lance_version].name, ioaddr, nic->node_addr);
#endif
	if (chip_table[chip_version].flags & LANCE_ENABLE_AUTOSELECT) {
		/* Turn on auto-select of media (10baseT or BNC) so that the
		 * user watch the LEDs. */
		outw(0x0002, ioaddr+LANCE_ADDR);
		/* Don't touch 10base2 power bit. */
		outw(inw(ioaddr+LANCE_BUS_IF) | 0x0002, ioaddr+LANCE_BUS_IF);
	}
	return (lance_version);
}

/**************************************************************************
PROBE - Look for an adapter, this routine's visible to the outside
***************************************************************************/

#ifdef	INCLUDE_LANCE
struct nic *lancepci_probe(struct nic *nic, unsigned short *probe_addrs, struct pci_device *pci)
#endif
#ifdef	INCLUDE_NE2100
struct nic *ne2100_probe(struct nic *nic, unsigned short *probe_addrs)
#endif
#ifdef	INCLUDE_NI6510
struct nic *ni6510_probe(struct nic *nic, unsigned short *probe_addrs)
#endif
{
	unsigned short		*p;
#ifndef	INCLUDE_LANCE
	static unsigned short	io_addrs[] = { 0x300, 0x320, 0x340, 0x360, 0 };
#endif

	/* if probe_addrs is 0, then routine can use a hardwired default */
	if (probe_addrs == 0) {
#ifdef	INCLUDE_LANCE
		return 0;
#else
		probe_addrs = io_addrs;
#endif
	}
	for (p = probe_addrs; (ioaddr = *p) != 0; ++p)
	{
		char	offset15, offset14 = inb(ioaddr + 14);
		unsigned short	pci_cmd;

#ifdef	INCLUDE_NE2100
		if ((offset14 == 0x52 || offset14 == 0x57) &&
		 ((offset15 = inb(ioaddr + 15)) == 0x57 || offset15 == 0x44))
			if (lance_probe1(nic) >= 0)
				break;
#endif
#ifdef	INCLUDE_NI6510
		if ((offset14 == 0x00 || offset14 == 0x52) &&
		 ((offset15 = inb(ioaddr + 15)) == 0x55 || offset15 == 0x44))
			if (lance_probe1(nic) >= 0)
				break;
#endif
#ifdef	INCLUDE_LANCE
		adjust_pci_device(pci);
		if (lance_probe1(nic, pci) >= 0)
			break;
#endif
	}
	/* if board found */
	if (ioaddr != 0)
	{
		/* point to NIC specific routines */
		lance_reset(nic);
		nic->reset = lance_reset;
		nic->poll = lance_poll;
		nic->transmit = lance_transmit;
		nic->disable = lance_disable;
		return nic;
	}

	/* no board found */
	return 0;
}

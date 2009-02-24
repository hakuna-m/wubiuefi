/* epic100.c: A SMC 83c170 EPIC/100 fast ethernet driver for Etherboot */

#define LINUX_OUT_MACROS

#include "etherboot.h"
#include "nic.h"
#include "cards.h"
#include "timer.h"
#include "epic100.h"

#undef	virt_to_bus
#define	virt_to_bus(x)	((unsigned long)x)

#define TX_RING_SIZE	2	/* use at least 2 buffers for TX */
#define RX_RING_SIZE	2

#define PKT_BUF_SZ	1536	/* Size of each temporary Tx/Rx buffer.*/

/*
#define DEBUG_RX
#define DEBUG_TX
#define DEBUG_EEPROM
*/

#define EPIC_DEBUG 0	/* debug level */

/* The EPIC100 Rx and Tx buffer descriptors. */
struct epic_rx_desc {
    unsigned short status;
    unsigned short rxlength;
    unsigned long  bufaddr;
    unsigned short buflength;
    unsigned short control;
    unsigned long  next;
};

/* description of the tx descriptors control bits commonly used */
#define TD_STDFLAGS	TD_LASTDESC

struct epic_tx_desc {
    unsigned short status;
    unsigned short txlength;
    unsigned long  bufaddr;
    unsigned short buflength;
    unsigned short control;
    unsigned long  next;
};

#define delay(nanosec)   do { int _i = 3; while (--_i > 0) \
                                     { __SLOW_DOWN_IO; }} while (0)

static void	epic100_open(void);
static void	epic100_init_ring(void);
static void	epic100_disable(struct nic *nic);
static int	epic100_poll(struct nic *nic);
static void	epic100_transmit(struct nic *nic, const char *destaddr,
				 unsigned int type, unsigned int len, const char *data);
static int	read_eeprom(int location);
static int	mii_read(int phy_id, int location);

static int	ioaddr;

static int	command;
static int	intstat;
static int	intmask;
static int	genctl ;
static int	eectl  ;
static int	test   ;
static int	mmctl  ;
static int	mmdata ;
static int	lan0   ;
static int	rxcon  ;
static int	txcon  ;
static int	prcdar ;
static int	ptcdar ;
static int	eththr ;

static unsigned int	cur_rx, cur_tx;		/* The next free ring entry */
#ifdef	DEBUG_EEPROM
static unsigned short	eeprom[64];
#endif
static signed char	phys[4];		/* MII device addresses. */
static struct epic_rx_desc	rx_ring[RX_RING_SIZE];
static struct epic_tx_desc	tx_ring[TX_RING_SIZE];
#ifdef	USE_LOWMEM_BUFFER
#define rx_packet ((char *)0x10000 - PKT_BUF_SZ * RX_RING_SIZE)
#define tx_packet ((char *)0x10000 - PKT_BUF_SZ * RX_RING_SIZE - PKT_BUF_SZ * TX_RING_SIZE)
#else
static char		rx_packet[PKT_BUF_SZ * RX_RING_SIZE];
static char		tx_packet[PKT_BUF_SZ * TX_RING_SIZE];
#endif

/***********************************************************************/
/*                    Externally visible functions                     */
/***********************************************************************/

    static void
epic100_reset(struct nic *nic)
{
    /* Soft reset the chip. */
    outl(GC_SOFT_RESET, genctl);
}

    struct nic*
epic100_probe(struct nic *nic, unsigned short *probeaddrs)
{
    unsigned short sum = 0;
    unsigned short value;
    int i;
    unsigned short* ap;
    unsigned int phy, phy_idx;

    if (probeaddrs == 0 || probeaddrs[0] == 0)
	return 0;

    /* Ideally we would detect all network cards in slot order.  That would
       be best done a central PCI probe dispatch, which wouldn't work
       well with the current structure.  So instead we detect just the
       Epic cards in slot order. */

    ioaddr = probeaddrs[0] & ~3; /* Mask the bit that says "this is an io addr" */

    /* compute all used static epic100 registers address */
    command = ioaddr + COMMAND;		/* Control Register */
    intstat = ioaddr + INTSTAT;		/* Interrupt Status */
    intmask = ioaddr + INTMASK;		/* Interrupt Mask */
    genctl  = ioaddr + GENCTL;		/* General Control */
    eectl   = ioaddr + EECTL;		/* EEPROM Control  */
    test    = ioaddr + TEST;		/* Test register (clocks) */
    mmctl   = ioaddr + MMCTL;		/* MII Management Interface Control */
    mmdata  = ioaddr + MMDATA;		/* MII Management Interface Data */
    lan0    = ioaddr + LAN0;		/* MAC address. (0x40-0x48) */
    rxcon   = ioaddr + RXCON;		/* Receive Control */
    txcon   = ioaddr + TXCON;		/* Transmit Control */
    prcdar  = ioaddr + PRCDAR;		/* PCI Receive Current Descr Address */
    ptcdar  = ioaddr + PTCDAR;		/* PCI Transmit Current Descr Address */
    eththr  = ioaddr + ETHTHR;		/* Early Transmit Threshold */

    /* Reset the chip & bring it out of low-power mode. */
    outl(GC_SOFT_RESET, genctl);

    /* Disable ALL interrupts by setting the interrupt mask. */
    outl(INTR_DISABLE, intmask);

    /*
     * set the internal clocks:
     * Application Note 7.15 says:
     *    In order to set the CLOCK TEST bit in the TEST register,
     *	  perform the following:
     *
     *        Write 0x0008 to the test register at least sixteen
     *        consecutive times.
     *
     * The CLOCK TEST bit is Write-Only. Writing it several times
     * consecutively insures a successful write to the bit...
     */

    for (i = 0; i < 16; i++) {
	outl(0x00000008, test);
    }

#ifdef	DEBUG_EEPROM
    for (i = 0; i < 64; i++) {
	value = read_eeprom(i);
	eeprom[i] = value;
	sum += value;
    }

#if	(EPIC_DEBUG > 1)
    printf("EEPROM contents\n");
    for (i = 0; i < 64; i++) {
	printf(" %hhX%s", eeprom[i], i % 16 == 15 ? "\n" : "");
    }
#endif
#endif

    /* This could also be read from the EEPROM. */
    ap = (unsigned short*)nic->node_addr;
    for (i = 0; i < 3; i++)
	*ap++ = inw(lan0 + i*4);

    printf(" I/O %#hX %! ", ioaddr, nic->node_addr);

    /* Find the connected MII xcvrs. */
    for (phy = 0, phy_idx = 0; phy < 32 && phy_idx < sizeof(phys); phy++) {
	int mii_status = mii_read(phy, 0);

	if (mii_status != 0xffff  && mii_status != 0x0000) {
	    phys[phy_idx++] = phy;
#if	(EPIC_DEBUG > 1)
	    printf("MII transceiver found at address %d.\n", phy);
#endif
	}
    }
    if (phy_idx == 0) {
#if	(EPIC_DEBUG > 1)
	printf("***WARNING***: No MII transceiver found!\n");
#endif
	/* Use the known PHY address of the EPII. */
	phys[0] = 3;
    }

    epic100_open();

    nic->reset    = epic100_reset;
    nic->poll     = epic100_poll;
    nic->transmit = epic100_transmit;
    nic->disable  = epic100_disable;

    return nic;
}

    static void
epic100_open(void)
{
    int mii_reg5;
    int full_duplex = 0;
    unsigned long tmp;

    epic100_init_ring();

    /* Pull the chip out of low-power mode, and set for PCI read multiple. */
    outl(GC_RX_FIFO_THR_64 | GC_MRC_READ_MULT | GC_ONE_COPY, genctl);

    outl(TX_FIFO_THRESH, eththr);

    tmp = TC_EARLY_TX_ENABLE | TX_SLOT_TIME;

    mii_reg5 = mii_read(phys[0], 5);
    if (mii_reg5 != 0xffff && (mii_reg5 & 0x0100)) {
	full_duplex = 1;
	printf(" full-duplex mode");
	tmp |= TC_LM_FULL_DPX;
    } else
	tmp |= TC_LM_NORMAL;

    outl(tmp, txcon);

    /* Give adress of RX and TX ring to the chip */
    outl(virt_to_bus(&rx_ring), prcdar);
    outl(virt_to_bus(&tx_ring), ptcdar);

    /* Start the chip's Rx process: receive unicast and broadcast */
    outl(0x04, rxcon);
    outl(CR_START_RX | CR_QUEUE_RX, command);

    putchar('\n');
}

/* Initialize the Rx and Tx rings. */
    static void
epic100_init_ring(void)
{
    int i;
    char* p;

    cur_rx = cur_tx = 0;

    p = &rx_packet[0];
    for (i = 0; i < RX_RING_SIZE; i++) {
	rx_ring[i].status    = RRING_OWN;	/* Owned by Epic chip */
	rx_ring[i].buflength = PKT_BUF_SZ;
	rx_ring[i].bufaddr   = virt_to_bus(p + (PKT_BUF_SZ * i));
	rx_ring[i].control   = 0;
	rx_ring[i].next      = virt_to_bus(&(rx_ring[i + 1]) );
    }
    /* Mark the last entry as wrapping the ring. */
    rx_ring[i-1].next = virt_to_bus(&rx_ring[0]);

    /*
     *The Tx buffer descriptor is filled in as needed,
     * but we do need to clear the ownership bit.
     */
    p = &tx_packet[0];

    for (i = 0; i < TX_RING_SIZE; i++) {
	tx_ring[i].status  = 0;			/* Owned by CPU */
	tx_ring[i].bufaddr = virt_to_bus(p + (PKT_BUF_SZ * i));
	tx_ring[i].control = TD_STDFLAGS;
	tx_ring[i].next    = virt_to_bus(&(tx_ring[i + 1]) );
    }
    tx_ring[i-1].next = virt_to_bus(&tx_ring[0]);
}

/* function: epic100_transmit
 * This transmits a packet.
 *
 * Arguments: char d[6]:          destination ethernet address.
 *            unsigned short t:   ethernet protocol type.
 *            unsigned short s:   size of the data-part of the packet.
 *            char *p:            the data for the packet.
 * returns:   void.
 */
    static void
epic100_transmit(struct nic *nic, const char *destaddr, unsigned int type,
		 unsigned int len, const char *data)
{
    unsigned short nstype;
    char* txp;
    int entry;

    /* Calculate the next Tx descriptor entry. */
    entry = cur_tx % TX_RING_SIZE;

    if ((tx_ring[entry].status & TRING_OWN) == TRING_OWN) {
	printf("eth_transmit: Unable to transmit. status=%hX. Resetting...\n",
	       tx_ring[entry].status);

	epic100_open();
	return;
    }

    txp = (char*)tx_ring[entry].bufaddr;

    memcpy(txp, destaddr, ETH_ALEN);
    memcpy(txp + ETH_ALEN, nic->node_addr, ETH_ALEN);
    nstype = htons(type);
    memcpy(txp + 12, (char*)&nstype, 2);
    memcpy(txp + ETH_HLEN, data, len);

    len += ETH_HLEN;

    /*
     * Caution: the write order is important here,
     * set the base address with the "ownership"
     * bits last.
     */
    tx_ring[entry].txlength  = (len >= 60 ? len : 60);
    tx_ring[entry].buflength = len;
    tx_ring[entry].status    = TRING_OWN;	/* Pass ownership to the chip. */

    cur_tx++;

    /* Trigger an immediate transmit demand. */
    outl(CR_QUEUE_TX, command);

    load_timer2(10*TICKS_PER_MS);         /* timeout 10 ms for transmit */
    while ((tx_ring[entry].status & TRING_OWN) && timer2_running())
	/* Wait */;

    if ((tx_ring[entry].status & TRING_OWN) != 0)
	printf("Oops, transmitter timeout, status=%hX\n",
	    tx_ring[entry].status);
}

/* function: epic100_poll / eth_poll
 * This receives a packet from the network.
 *
 * Arguments: none
 *
 * returns:   1 if a packet was received.
 *            0 if no pacet was received.
 * side effects:
 *            returns the packet in the array nic->packet.
 *            returns the length of the packet in nic->packetlen.
 */

    static int
epic100_poll(struct nic *nic)
{
    int entry;
    int status;
    int retcode;

    entry = cur_rx % RX_RING_SIZE;

    if ((status = rx_ring[entry].status & RRING_OWN) == RRING_OWN)
	return (0);

    /* We own the next entry, it's a new packet. Send it up. */

#if	(EPIC_DEBUG > 4)
    printf("epic_poll: entry %d status %hX\n", entry, status);
#endif

    cur_rx++;
    if (status & 0x2000) {
	printf("epic_poll: Giant packet\n");
	retcode = 0;
    } else if (status & 0x0006) {
	/* Rx Frame errors are counted in hardware. */
	printf("epic_poll: Frame received with errors\n");
	retcode = 0;
    } else {
	/* Omit the four octet CRC from the length. */
	nic->packetlen = rx_ring[entry].rxlength - 4;
	memcpy(nic->packet, (char*)rx_ring[entry].bufaddr, nic->packetlen);
	retcode = 1;
    }

    /* Clear all error sources. */
    outl(status & INTR_CLEARERRS, intstat);

    /* Give the descriptor back to the chip */
    rx_ring[entry].status = RRING_OWN;

    /* Restart Receiver */
    outl(CR_START_RX | CR_QUEUE_RX, command);

    return retcode;
}


    static void
epic100_disable(struct nic *nic)
{
}


#ifdef	DEBUG_EEPROM
/* Serial EEPROM section. */

/*  EEPROM_Ctrl bits. */
#define EE_SHIFT_CLK	0x04	/* EEPROM shift clock. */
#define EE_CS		0x02	/* EEPROM chip select. */
#define EE_DATA_WRITE	0x08	/* EEPROM chip data in. */
#define EE_WRITE_0	0x01
#define EE_WRITE_1	0x09
#define EE_DATA_READ	0x10	/* EEPROM chip data out. */
#define EE_ENB		(0x0001 | EE_CS)

/* The EEPROM commands include the alway-set leading bit. */
#define EE_WRITE_CMD	(5 << 6)
#define EE_READ_CMD	(6 << 6)
#define EE_ERASE_CMD	(7 << 6)

#define eeprom_delay(n)	delay(n)

    static int
read_eeprom(int location)
{
    int i;
    int retval = 0;
    int read_cmd = location | EE_READ_CMD;

    outl(EE_ENB & ~EE_CS, eectl);
    outl(EE_ENB, eectl);

    /* Shift the read command bits out. */
    for (i = 10; i >= 0; i--) {
	short dataval = (read_cmd & (1 << i)) ? EE_DATA_WRITE : 0;
	outl(EE_ENB | dataval, eectl);
	eeprom_delay(100);
	outl(EE_ENB | dataval | EE_SHIFT_CLK, eectl);
	eeprom_delay(150);
	outl(EE_ENB | dataval, eectl);	/* Finish EEPROM a clock tick. */
	eeprom_delay(250);
    }
    outl(EE_ENB, eectl);

    for (i = 16; i > 0; i--) {
	outl(EE_ENB | EE_SHIFT_CLK, eectl);
	eeprom_delay(100);
	retval = (retval << 1) | ((inl(eectl) & EE_DATA_READ) ? 1 : 0);
	outl(EE_ENB, eectl);
	eeprom_delay(100);
    }

    /* Terminate the EEPROM access. */
    outl(EE_ENB & ~EE_CS, eectl);
    return retval;
}
#endif


#define MII_READOP	1
#define MII_WRITEOP	2

    static int
mii_read(int phy_id, int location)
{
    int i;

    outl((phy_id << 9) | (location << 4) | MII_READOP, mmctl);
    /* Typical operation takes < 50 ticks. */

    for (i = 4000; i > 0; i--)
	if ((inl(mmctl) & MII_READOP) == 0)
	    break;
    return inw(mmdata);
}

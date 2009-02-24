/*
        Driver for the National Semiconductor DP83810 Ethernet controller.
        
        Portions Copyright (C) 2001 Inprimis Technologies, Inc.
        http://www.inprimis.com/
        
        This driver is based (heavily) on the Linux driver for this chip 
        which is copyright 1999-2001 by Donald Becker.

        This software has no warranties expressed or implied for any
        purpose.

        This software may be used and distributed according to the terms of
        the GNU General Public License (GPL), incorporated herein by reference.
        Drivers based on or derived from this code fall under the GPL and must
        retain the authorship, copyright and license notice.  This file is not
        a complete program and may only be used when the entire operating
        system is licensed under the GPL.  License for under other terms may be
        available.  Contact the original author for details.

        The original author may be reached as becker@scyld.com, or at
        Scyld Computing Corporation
        410 Severn Ave., Suite 210
        Annapolis MD 21403
*/


typedef unsigned char  u8;
typedef   signed char  s8;
typedef unsigned short u16;
typedef   signed short s16;
typedef unsigned int   u32;
typedef   signed int   s32;

#include "etherboot.h"
#include "nic.h"
#include "pci.h"

#undef	virt_to_bus
#define	virt_to_bus(x)          ((unsigned long)x)
#define cpu_to_le32(val)        (val)
#define le32_to_cpu(val)        (val)
#define virt_to_le32desc(addr)  cpu_to_le32(virt_to_bus(addr))
#define le32desc_to_virt(addr)  bus_to_virt(le32_to_cpu(addr))

#define TX_RING_SIZE 1
#define RX_RING_SIZE 4
#define TIME_OUT     1000000
#define PKT_BUF_SZ   1536

/* Offsets to the device registers. */
enum register_offsets {
    ChipCmd=0x00, ChipConfig=0x04, EECtrl=0x08, PCIBusCfg=0x0C,
    IntrStatus=0x10, IntrMask=0x14, IntrEnable=0x18,
    TxRingPtr=0x20, TxConfig=0x24,
    RxRingPtr=0x30, RxConfig=0x34,
    WOLCmd=0x40, PauseCmd=0x44, RxFilterAddr=0x48, RxFilterData=0x4C,
    BootRomAddr=0x50, BootRomData=0x54, StatsCtrl=0x5C, StatsData=0x60,
    RxPktErrs=0x60, RxMissed=0x68, RxCRCErrs=0x64,
};

/* Bit in ChipCmd. */
enum ChipCmdBits {
    ChipReset=0x100, RxReset=0x20, TxReset=0x10, RxOff=0x08, RxOn=0x04,
    TxOff=0x02, TxOn=0x01,
};

/* Bits in the interrupt status/mask registers. */
enum intr_status_bits {
    IntrRxDone=0x0001, IntrRxIntr=0x0002, IntrRxErr=0x0004, IntrRxEarly=0x0008,
    IntrRxIdle=0x0010, IntrRxOverrun=0x0020,
    IntrTxDone=0x0040, IntrTxIntr=0x0080, IntrTxErr=0x0100,
    IntrTxIdle=0x0200, IntrTxUnderrun=0x0400,
    StatsMax=0x0800, LinkChange=0x4000,	WOLPkt=0x2000,
    RxResetDone=0x1000000, TxResetDone=0x2000000,
    IntrPCIErr=0x00f00000, IntrNormalSummary=0x0251, IntrAbnormalSummary=0xED20,
};

/* Bits in the RxMode register. */
enum rx_mode_bits {
    AcceptErr=0x20, AcceptRunt=0x10, AcceptBroadcast=0xC0000000,
    AcceptMulticast=0x00200000, AcceptAllMulticast=0x20000000,
    AcceptAllPhys=0x10000000, AcceptMyPhys=0x08000000,
};

/* Bits in network_desc.status */
enum desc_status_bits {
    DescOwn=0x80000000, DescMore=0x40000000, DescIntr=0x20000000,
    DescNoCRC=0x10000000,
    DescPktOK=0x08000000, RxTooLong=0x00400000,
};

/* The Rx and Tx buffer descriptors. */
struct netdev_desc {
    u32 next_desc;
    s32 cmd_status;
    u32 addr;
};

static struct FA311_DEV {
    unsigned int    ioaddr;
    unsigned short  vendor;
    unsigned short  device;
    unsigned int    cur_rx;
    unsigned int    cur_tx;
    unsigned int    rx_buf_sz;
    volatile struct netdev_desc *rx_head_desc;
    volatile struct netdev_desc rx_ring[RX_RING_SIZE] __attribute__ ((aligned (4)));
    volatile struct netdev_desc tx_ring[TX_RING_SIZE] __attribute__ ((aligned (4)));
} fa311_dev;

static int  eeprom_read(long ioaddr, int location);
static void init_ring(struct FA311_DEV *dev);
static void fa311_reset(struct nic *nic);
static int  fa311_poll(struct nic *nic);
static void fa311_transmit(struct nic *nic, const char *d, unsigned int t, unsigned int s, const char *p);
static void fa311_disable(struct nic *nic);

static char rx_packet[PKT_BUF_SZ * RX_RING_SIZE] __attribute__ ((aligned (4)));
static char tx_packet[PKT_BUF_SZ * TX_RING_SIZE] __attribute__ ((aligned (4)));

struct nic * fa311_probe(struct nic *nic, unsigned short *io_addrs, struct pci_device *pci)
{
int            prev_eedata;
int            i;
int            duplex;
int            tx_config;
int            rx_config;
unsigned char  macaddr[6];
unsigned char  mactest;
unsigned char  pci_bus = 0;
struct FA311_DEV* dev = &fa311_dev;
	
    if (io_addrs == 0 || *io_addrs == 0)
        return (0);
    memset(dev, 0, sizeof(*dev));
    dev->vendor = pci->vendor;
    dev->device = pci->dev_id;
    dev->ioaddr = pci->membase;

    /* Work around the dropped serial bit. */
    prev_eedata = eeprom_read(dev->ioaddr, 6);
    for (i = 0; i < 3; i++) {
        int eedata = eeprom_read(dev->ioaddr, i + 7);
        macaddr[i*2] = (eedata << 1) + (prev_eedata >> 15);
        macaddr[i*2+1] = eedata >> 7;
        prev_eedata = eedata;
    }
    mactest = 0;
    for (i = 0; i < 6; i++)
        mactest |= macaddr[i];
    if (mactest == 0)
        return (0);
    for (i = 0; i < 6; i++)
        nic->node_addr[i] = macaddr[i];
    printf("%! ", nic->node_addr);

    adjust_pci_device(pci);

    fa311_reset(nic);

    nic->reset = fa311_reset;
    nic->disable = fa311_disable;
    nic->poll = fa311_poll;
    nic->transmit = fa311_transmit;

    init_ring(dev);

    writel(virt_to_bus(dev->rx_ring), dev->ioaddr + RxRingPtr);
    writel(virt_to_bus(dev->tx_ring), dev->ioaddr + TxRingPtr);

    for (i = 0; i < 6; i += 2)
    {
        writel(i, dev->ioaddr + RxFilterAddr);
        writew(macaddr[i] + (macaddr[i+1] << 8),
               dev->ioaddr + RxFilterData);
    }

    /* Initialize other registers. */
    /* Configure for standard, in-spec Ethernet. */
    if (readl(dev->ioaddr + ChipConfig) & 0x20000000)
    {    /* Full duplex */
        tx_config = 0xD0801002;
        rx_config = 0x10000020;
    }
    else
    {
        tx_config = 0x10801002;
        rx_config = 0x0020;
    }
    writel(tx_config, dev->ioaddr + TxConfig);
    writel(rx_config, dev->ioaddr + RxConfig);

    duplex = readl(dev->ioaddr + ChipConfig) & 0x20000000 ? 1 : 0;
    if (duplex) {
        rx_config |= 0x10000000;
        tx_config |= 0xC0000000;
    } else {
        rx_config &= ~0x10000000;
        tx_config &= ~0xC0000000;
    }
    writew(tx_config, dev->ioaddr + TxConfig);
    writew(rx_config, dev->ioaddr + RxConfig);

    writel(AcceptBroadcast | AcceptAllMulticast | AcceptMyPhys, 
           dev->ioaddr + RxFilterAddr);

    writel(RxOn | TxOn, dev->ioaddr + ChipCmd);
    writel(4, dev->ioaddr + StatsCtrl);              /* Clear Stats */
    return nic;	

}

static void fa311_reset(struct nic *nic)
{
u32 chip_config;
struct FA311_DEV* dev = &fa311_dev;

    /* Reset the chip to erase previous misconfiguration. */
    outl(ChipReset, dev->ioaddr + ChipCmd);

    if ((readl(dev->ioaddr + ChipConfig) & 0xe000) != 0xe000)
    {
        chip_config = readl(dev->ioaddr + ChipConfig);
    }
}

static int fa311_poll(struct nic *nic)
{
s32 desc_status;
int to;
int entry;
int retcode;
struct FA311_DEV* dev = &fa311_dev;

    retcode = 0;
    entry = dev->cur_rx;
    to = TIME_OUT;
    while (to != 0)
    {
        desc_status = dev->rx_ring[entry].cmd_status;
        if ((desc_status & DescOwn) != 0)
            break;
        else
            --to;
    }
    if (to != 0)
    {
        readl(dev->ioaddr + IntrStatus);         /* clear interrrupt bits */
        /* driver owns the next entry it's a new packet. Send it up. */
        if ((desc_status & (DescMore|DescPktOK|RxTooLong)) == DescPktOK)
        {
            nic->packetlen = (desc_status & 0x0fff) - 4;    /* Omit CRC size. */
            memcpy(nic->packet, (char*)(dev->rx_ring[entry].addr), nic->packetlen);
            retcode = 1;
        }
        /* Give the descriptor back to the chip */
        dev->rx_ring[entry].cmd_status = cpu_to_le32(dev->rx_buf_sz);
        dev->cur_rx++;
        if (dev->cur_rx >= RX_RING_SIZE)
            dev->cur_rx = 0;
        dev->rx_head_desc = &dev->rx_ring[dev->cur_rx];
    }
    /* Restart Rx engine if stopped. */
    writel(RxOn, dev->ioaddr + ChipCmd);
    return retcode;
}

static void fa311_transmit(struct nic *nic, const char *destaddr, unsigned int type, unsigned int len, const char *data)
{
unsigned short nstype;
s32            desc_status;
int            to;
int            entry;
char*          txp;
unsigned char* s;
struct FA311_DEV* dev = &fa311_dev;

    /* Calculate the next Tx descriptor entry. */
    entry = dev->cur_tx;
    txp = (char*)(dev->tx_ring[entry].addr);

    memcpy(txp, destaddr, ETH_ALEN);
    memcpy(txp + ETH_ALEN, nic->node_addr, ETH_ALEN);
    nstype = htons(type);
    memcpy(txp + 12, (char*)&nstype, 2);
    memcpy(txp + ETH_HLEN, data, len);
    len += ETH_HLEN;
    /* pad frame */
    if (len <  ETH_ZLEN)
    {
        s = (unsigned char*)(txp+len);
        while (s < (unsigned char*)(txp+ETH_ZLEN))
            *s++ = 0;
        len = ETH_ZLEN;
    }
    dev->tx_ring[entry].cmd_status = cpu_to_le32(DescOwn | len);
    dev->cur_tx++;
    if (dev->cur_tx >= TX_RING_SIZE)
        dev->cur_tx = 0;

    /* Wake the potentially-idle transmit channel. */
    writel(TxOn, dev->ioaddr + ChipCmd);

    /* wait for tranmission to complete */
    to = TIME_OUT;
    while (to != 0)
    {
        desc_status = dev->tx_ring[entry].cmd_status;
        if ((desc_status & DescOwn) == 0)
            break;
        else
            --to;
    }

    readl(dev->ioaddr + IntrStatus);         /* clear interrrupt bits */
    return;
}

static void fa311_disable(struct nic *nic)
{
struct FA311_DEV* dev = &fa311_dev;

    /* Stop the chip's Tx and Rx processes. */
    writel(RxOff | TxOff, dev->ioaddr + ChipCmd);
}


/* Read the EEPROM and MII Management Data I/O (MDIO) interfaces.
   The EEPROM code is for the common 93c06/46 EEPROMs with 6 bit addresses. */

/* Delay between EEPROM clock transitions.
   No extra delay is needed with 33Mhz PCI, but future 66Mhz access may need
   a delay.  Note that pre-2.0.34 kernels had a cache-alignment bug that
   made udelay() unreliable.
   The old method of using an ISA access as a delay, __SLOW_DOWN_IO__, is
   depricated.
*/
#define eeprom_delay(ee_addr)	inl(ee_addr)

enum EEPROM_Ctrl_Bits {
	EE_ShiftClk=0x04, EE_DataIn=0x01, EE_ChipSelect=0x08, EE_DataOut=0x02,
};
#define EE_Write0 (EE_ChipSelect)
#define EE_Write1 (EE_ChipSelect | EE_DataIn)

/* The EEPROM commands include the alway-set leading bit. */
enum EEPROM_Cmds {
	EE_WriteCmd=(5 << 6), EE_ReadCmd=(6 << 6), EE_EraseCmd=(7 << 6),
};


static int eeprom_read(long addr, int location)
{
	int i;
	int retval = 0;
	int ee_addr = addr + EECtrl;
	int read_cmd = location | EE_ReadCmd;
	writel(EE_Write0, ee_addr);

	/* Shift the read command bits out. */
	for (i = 10; i >= 0; i--) {
		short dataval = (read_cmd & (1 << i)) ? EE_Write1 : EE_Write0;
		writel(dataval, ee_addr);
		eeprom_delay(ee_addr);
		writel(dataval | EE_ShiftClk, ee_addr);
		eeprom_delay(ee_addr);
	}
	writel(EE_ChipSelect, ee_addr);
	eeprom_delay(ee_addr);

	for (i = 0; i < 16; i++) {
		writel(EE_ChipSelect | EE_ShiftClk, ee_addr);
		eeprom_delay(ee_addr);
		retval |= (readl(ee_addr) & EE_DataOut) ? 1 << i : 0;
		writel(EE_ChipSelect, ee_addr);
		eeprom_delay(ee_addr);
	}

	/* Terminate the EEPROM access. */
	writel(EE_Write0, ee_addr);
	writel(0, ee_addr);
	return retval;
}

/* Initialize the Rx and Tx rings, along with various 'dev' bits. */
static void init_ring(struct FA311_DEV *dev)
{
	int i;

	dev->cur_rx = 0;
    dev->cur_tx = 0;

	dev->rx_buf_sz = PKT_BUF_SZ;
	dev->rx_head_desc = &dev->rx_ring[0];

	/* Initialize all Rx descriptors. */
	for (i = 0; i < RX_RING_SIZE; i++) {
		dev->rx_ring[i].next_desc = virt_to_le32desc(&dev->rx_ring[i+1]);
		dev->rx_ring[i].cmd_status = DescOwn;
	}
	/* Mark the last entry as wrapping the ring. */
	dev->rx_ring[i-1].next_desc = virt_to_le32desc(&dev->rx_ring[0]);

	/* Fill in the Rx buffers.  Handle allocation failure gracefully. */
	for (i = 0; i < RX_RING_SIZE; i++) {
		dev->rx_ring[i].addr = (u32)(&rx_packet[PKT_BUF_SZ * i]);
	    dev->rx_ring[i].cmd_status = cpu_to_le32(dev->rx_buf_sz);
	}

	for (i = 0; i < TX_RING_SIZE; i++) {
		dev->tx_ring[i].next_desc = virt_to_le32desc(&dev->tx_ring[i+1]);
		dev->tx_ring[i].cmd_status = 0;
	}
	dev->tx_ring[i-1].next_desc = virt_to_le32desc(&dev->tx_ring[0]);

	for (i = 0; i < TX_RING_SIZE; i++)
		dev->tx_ring[i].addr = (u32)(&tx_packet[PKT_BUF_SZ * i]);
	return;
}


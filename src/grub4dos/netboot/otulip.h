/* mostly stolen from FreeBSD if_de.c, if_devar.h */

#define TULIP_CSR_READ(csr)		(membase[csr*2])
#define CSR_READ(csr)			(membase[csr*2])
#define TULIP_CSR_WRITE(csr, val)	(membase[csr*2] = val)
#define CSR_WRITE(csr, val)		(membase[csr*2] = val)

#define csr_0			0
#define csr_1			1
#define csr_2			2
#define csr_3			3
#define csr_4			4
#define csr_5			5
#define csr_6			6
#define csr_7			7
#define csr_8			8
#define csr_9			9
#define csr_10			10
#define csr_11			11
#define csr_12			12
#define csr_13			13
#define csr_14			14
#define csr_15			15

#define csr_busmode		csr_0
#define csr_txpoll		csr_1
#define csr_rxpoll		csr_2
#define csr_rxlist		csr_3
#define csr_txlist		csr_4
#define csr_status		csr_5
#define csr_command		csr_6
#define csr_intr		csr_7
#define csr_missed_frames	csr_8
#define csr_enetrom		csr_9		/* 21040 */
#define csr_reserved		csr_10		/* 21040 */
#define csr_full_duplex		csr_11		/* 21040 */
#define csr_bootrom		csr_10		/* 21041/21140A/?? */
#define csr_gp			csr_12		/* 21140* */
#define csr_watchdog		csr_15		/* 21140* */
#define csr_gp_timer		csr_11		/* 21041/21140* */
#define csr_srom_mii		csr_9		/* 21041/21140* */
#define csr_sia_status		csr_12		/* 2104x */
#define csr_sia_connectivity	csr_13		/* 2104x */
#define csr_sia_tx_rx		csr_14		/* 2104x */
#define csr_sia_general		csr_15		/* 2104x */

#define SROMSEL		0x0800
#define SROMCS		0x0001
#define SROMCLKON	0x0002
#define SROMCLKOFF	0x0002
#define SROMRD		0x4000
#define SROMWR		0x2000
#define SROM_BITWIDTH	6
#define SROMCMD_RD	6
#define SROMCSON	0x0001
#define SROMDOUT	0x0004
#define SROMDIN		0x0008


struct txdesc {
	unsigned long	status;		/* owner, status */
	unsigned long	buf1sz:11,	/* size of buffer 1 */
			buf2sz:11,	/* size of buffer 2 */
			control:10;	/* control bits */
	const unsigned char *buf1addr;	/* buffer 1 address */
	const unsigned char *buf2addr;	/* buffer 2 address */
};

struct rxdesc {
	unsigned long	status;		/* owner, status */
	unsigned long	buf1sz:11,	/* size of buffer 1 */
			buf2sz:11,	/* size of buffer 2 */
			control:10;	/* control bits */
	unsigned char	*buf1addr;	/* buffer 1 address */
	unsigned char	*buf2addr;	/* buffer 2 address */
};

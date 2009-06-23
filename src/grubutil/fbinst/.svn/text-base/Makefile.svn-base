#
#  GRUB Utilities --  Utilities for GRUB Legacy, GRUB2 and GRUB for DOS
#  Copyright (C) 2007 Bean (bean123ch@gmail.com)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

ifeq ($(SRCDIR),)
SRCDIR := $(dir $(firstword $(MAKEFILE_LIST)))
endif

PACKAGE = fbinst

extra_SRCS = Makefile version fbmbr.S fbinst.h

all_DIST =

cmn_SRCS = common.mk ldscript keytab.c keytab.h bin2h.c bin2h.pl ver2h.c ver2h.pl utils.c utils.h xdio.c xdio.h xd16.asm

all_SRCS := fbinst.c $(extra_SRCS)
all_OBJS = fbinst.o
all_EXES = fbinst$(EXEEXT)

extra_CLEAN = fb.mbr version.h fb_mbr.h

-include common.mk $(SRCDIR)../common/common.mk

fbinst$(EXEEXT): fbinst.o xdio.o keytab.o
	$(CC) $(CFLAGS) -o$@ $^

fbinst.o: version.h fbinst.h fb_mbr_rel.h fb_mbr_dbg.h

fb_rel.mbr: fbmbr.S version.h fbinst.h
	$(CC) -nostdlib -I. -I$(SRCDIR) -Wl,-N -Wl,-T -Wl,$(CMNDIR)ldscript -o fb$(EXEEXT) $<
	$(OC) -O binary fb$(EXEEXT) $@
	rm fb$(EXEEXT)

fb_mbr_rel.h: fb_rel.mbr $(BIN2H_DEPS)
	$(BIN2H_EXEC) $< $@ fb_mbr_rel

fb_dbg.mbr: fbmbr.S version.h fbinst.h
	$(CC) -nostdlib -I. -I$(SRCDIR) -DDEBUG -DDEBUG_INT13 -Wl,-N -Wl,-T -Wl,$(CMNDIR)ldscript -o fb$(EXEEXT) $<
	$(OC) -O binary fb$(EXEEXT) $@
	rm fb$(EXEEXT)

fb_mbr_dbg.h: fb_dbg.mbr $(BIN2H_DEPS)
	$(BIN2H_EXEC) $< $@ fb_mbr_dbg

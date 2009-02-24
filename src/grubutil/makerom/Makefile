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

PACKAGE = makerom

makerom_ASRC = rom.S
makerom_CSRC = makerom.c
makerom_SRCS = $(makerom_ASRC) $(makerom_CSRC)
makerom_EXES = $(subst .c,$(EXEEXT),$(makerom_CSRC))
makerom_BINS = rom_isa.bin rom_pci.bin rom_zisa.bin rom_zpci.bin

extra_SRCS = Makefile version LzmaDecode.c LzmaDecode.s LzmaDecode.h LzmaTypes.h

all_SRCS = $(makerom_SRCS) $(extra_SRCS)
all_EXES = $(makerom_EXES)
all_BINS = $(makerom_BINS)
all_OBJS = keytab.o

cmn_SRCS = common.mk ldscript keytab.c keytab.h

extra_CLEAN = *.pre

-include common.mk $(SRCDIR)../common/common.mk

#LzmaDecode.s: LzmaDecode.c LzmaDecode.h LzmaTypes.h
#	gcc -Os -S -o $@ $<

rom_isa.pre: rom.S
	$(CC) -nostdlib -MMD -Wl,-T -Wl,$(CMNDIR)ldscript -o $@ $<

rom_pci.pre: rom.S
	$(CC) -nostdlib -MMD -DPCI -Wl,-T -Wl,$(CMNDIR)ldscript -o $@ $<

rom_zisa.pre: rom.S
	$(CC) -nostdlib -MMD -DLZMA -Wl,-T -Wl,$(CMNDIR)ldscript -o $@ $<

rom_zpci.pre: rom.S
	$(CC) -nostdlib -MMD -DPCI -DLZMA -Wl,-T -Wl,$(CMNDIR)ldscript -o $@ $<

makerom$(EXEEXT): makerom.o keytab.o
	$(CC) $(CFLAGS) -o $@ $^

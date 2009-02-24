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

PACKAGE = loadbin

loadbin_ASRC = ldgrub2.S ldgrub.S ldntldr.S
loadbin_AEXT = header.S
loadbin_CSRC = mkimage.c
loadbin_SRCS = $(loadbin_ASRC) $(loadbin_AEXT) $(loadbin_CSRC)
loadbin_EXES = $(subst .c,$(EXEEXT),$(loadbin_CSRC))
loadbin_BINS = $(subst .S,.bin,$(loadbin_ASRC))

extra_SRCS = Makefile version

all_SRCS = $(loadbin_SRCS) $(extra_SRCS)
all_EXES = $(loadbin_EXES)
all_BINS = $(loadbin_BINS)

cmn_DIST = COPYING
cmn_SRCS = common.mk ldscript

extra_CLEAN = *.pre

-include common.mk $(SRCDIR)../common/common.mk

.PRECIOUS: %.o

%.bin: %.pre
	$(OC) $(OCFLAGS) -O binary $< $@
	./mkimage$(EXEEXT) $@ $@

$(subst .S,.bin,$(loadbin_ASRC)): mkimage$(EXEEXT)

ldgrub2.pre: ldscript header.o ldgrub2.o
	$(LD) $(LDFLAGS) -T $^ -o $@

ldgrub.pre: ldscript header.o ldgrub.o
	$(LD) $(LDFLAGS) -T $^ -o $@

ldntldr.pre: ldscript header.o ldntldr.o
	$(LD) $(LDFLAGS) -T $^ -o $@

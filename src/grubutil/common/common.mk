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

ifeq ($(_COMMON_),)

_COMMON_ = 1

CMNDIR   := $(dir $(lastword $(MAKEFILE_LIST)))

OSTYPE   = $(shell uname -s)
#REV	 = $(shell sh $(SRCDIR)genrev.sh $(SRCDIR) ${rev})
REV      = $(shell date --utc --iso-8601)
_NONE    :=
_SPACE   := $(_NONE) $(_NONE)
VERSION  = $(subst $(_SPACE),-,$(shell cat $(SRCDIR)version))

CC       = gcc
OC	 = objcopy
LD	 = ld

CFLAGS   += -I$(CMNDIR) -I. -Wall
AFLAGS   += -I$(CMNDIR) -I. -Wall

SYSSTR   = lnx

ifneq ($(findstring MINGW,$(OSTYPE)),)
IS_WIN32 = 1
CFLAGS   += -DWIN32
AFLAGS   += -DWIN32
EXEEXT   = .exe
SYSSTR   = w32
endif

ifneq ($(findstring CYGWIN,$(OSTYPE)),)
IS_WIN32 = 1
CFLAGS   += -DWIN32 -mno-cygwin
AFLAGS   += -DWIN32 -mno-cygwin
EXEEXT   = .exe
SYSSTR   = w32
endif

USE_ZIP  ?= y

ifeq ($(USE_ZIP),y)
HAVE_ZIP = $(shell which zip)
endif

USE_PERL ?= y

ifeq ($(USE_PERL),y)
HAVE_PERL= $(shell which perl)
endif

VPATH = $(SRCDIR) $(CMNDIR)

.PHONY: all clean pkg_src pkg_bin

all_EXES += $(all_EXES_$(SYSSTR))
all_OBJS += $(all_OBJS_$(SYSSTR))
all_DIST += $(all_DIST_$(SYSSTR))

all: $(CURDIR)/Makefile $(all_EXES) $(all_BINS)

pkg_bin: all
ifneq ($(HAVE_ZIP),)
	zip -j -q -r $(PACKAGE)-$(VERSION)-bin-$(SYSSTR)-$(REV).zip $(all_EXES) $(all_BINS) $(addprefix $(SRCDIR),$(all_DIST)) $(CMNDIR)COPYING
else
	tar czf $(PACKAGE)-$(VERSION)-bin-$(SYSSTR)-$(REV).tar.gz $(all_EXES) $(all_BINS) $(addprefix $(SRCDIR),$(all_DIST)) $(CMNDIR)COPYING
endif

pkg_src:
ifneq ($(HAVE_ZIP),)
	zip -j -q -r $(PACKAGE)-$(VERSION)-src-$(REV).zip $(addprefix $(SRCDIR),$(all_SRCS) $(all_DIST)) $(addprefix $(CMNDIR),$(cmn_SRCS) COPYING)
else
	tar czf $(PACKAGE)-$(VERSION)-src-$(REV).tar.gz $(addprefix $(SRCDIR),$(all_SRCS) $(all_DIST)) $(addprefix $(CMNDIR),$(cmn_SRCS) COPYING)
endif

clean:
	rm -f $(all_EXES) $(all_BINS) $(extra_CLEAN) *.o *.d  # Cleanup

$(CURDIR)/Makefile:
	echo -e "SRCDIR:=$(SRCDIR)\ninclude $(SRCDIR)$(notdir $(firstword $(MAKEFILE_LIST)))" > $@ # Create Makefile

%$(EXEEXT): %.c
	$(CC) $(CFLAGS) -MMD -o $@ $<

%.o: %.c
	$(CC) $(CFLAGS) -c -MMD -o $@ $<

%.o: %.S
	$(CC) $(AFLAGS) -c -MMD -o $@ $<

%.bin: %.pre
	$(OC) $(OCFLAGS) -O binary $< $@

%.pre: %.S
	$(CC) $(AFLAGS) -nostdlib -MMD -Wl,-T -Wl,$(CMNDIR)ldscript -o $@ $<

ifneq ($(HAVE_PERL),)

version.h: version ver2h.pl
	perl $(CMNDIR)ver2h.pl $< $@

BIN2H_EXEC = perl $(CMNDIR)bin2h.pl
BIN2H_DEPS = bin2h.pl

else

version.h: version ver2h$(EXEEXT)
	./ver2h$(EXEEXT) $< $@

BIN2H_EXEC = bin2h$(EXEEXT)
BIN2H_DEPS = bin2h$(EXEEXT)

extra_CLEAN += ver2h$(EXEEXT) bin2h$(EXEEXT)
endif

ifeq ($(EXEEXT),)
all_DEPS := $(addsuffix .d, $(all_EXES))
else
all_DEPS := $(subst $(EXEEXT),.d,$(all_EXES))
endif

all_DEPS += $(subst .bin,.d,$(all_BINS))
all_DEPS += $(subst .o,.d,$(all_OBJS))

-include $(all_DEPS)

endif
export SHELL = sh
PROGRAM = pylauncher
LDFLAGS = -shared -dll
CC = i586-mingw32msvc-gcc
STRIP = i586-mingw32msvc-strip

all: cpuid.dll

cpuid.dll: cpuid.c
	$(CC) -o $@ $(LDFLAGS) $^
	$(STRIP) $@

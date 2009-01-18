export SHELL = sh
PROGRAM = pylauncher
LDFLAGS = -shared -dll
CC = i586-mingw32msvc-gcc

all: cpuid.dll

cpuid.dll: cpuid.c
	$(CC) -o $@ $(LDFLAGS) $^

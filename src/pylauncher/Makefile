export SHELL = sh
#DEBUG = yes
PACKAGE = winlauncher
CC = i586-mingw32msvc-gcc
LD = i586-mingw32msvc-gcc
LDFLAGS = -shared -dll
DLL = i586-mingw32msvc-dlltool
ifdef DEBUG
	CFLAGS = -g -Wl,--file-alignment,512 -MD -Wall -Os -m32 -march=i386
	STRIP=@echo
else
	CFLAGS = -Wl,--file-alignment,512 -MD -Wall  -Os -m32 -march=i386
	STRIP = i586-mingw32msvc-strip
endif
# CFLAGS= -W3 -O1 -GF -Gs -Gr -nologo -DWINDOWS -MD
# -W3 max warnings
# -O1 minimize size
# -GF read-only string constants
# -Gs disable stack checking calls
# -Gr fastcall calling convention
# -MD link against MSVCRT.DLL (also required by Python)

all: build

build: pylauncher.exe

pylauncher.exe: pylauncher.c
	$(CC) $(CFLAGS) $^ -o $@
#user32.lib gdi32.lib shell32.lib

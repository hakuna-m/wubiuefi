export SHELL = sh
PROGRAM = pylauncher
#LDFLAGS = -shared -dll
#LIB = -lm -static
#LIBS = user32.lib gdi32.lib shell32.lib
CC = i586-mingw32msvc-gcc
WINDRES = i586-mingw32msvc-windres
CFLAGS = \
	-c \
	-Os \
	-Wall \
	-m32 \
	-march=i386 \
	-D_SZ_FILE_SIZE_32

# -D_SZ_FILE_SIZE_32  - define it if you need only support for files smaller than 4 GB
# -D_LZMA_IN_CB -if defined it does not read the full archive to memory
# -D USE_WINDOWS_FUNCTIONS use windows functions instead of libc in unpack.c
# -DWINDOWS
# -c do not link
# -Os optimize for size
# -GF read-only string constants
# -Gs disable stack checking calls
# -Gr fastcall calling convention
# -MD link against MSVCRT.DLL (also required by Python)
# -W3 max warnings
# -Wl,--file-alignment,512  pass option --file-alignement 512 to the linker
#	-m32
# -march=i386

ifdef DEBUG
	DEBUGFLAG = -g
	STRIP = @echo
else
	DEBUGFLAG =
	LDFLAGS = -mwindows
	STRIP = i586-mingw32msvc-strip
endif

7Z_OBJS = \
	7zAlloc.o \
	7zBuffer.o \
	7zCrc.o \
	7zDecode.o \
	7zExtract.o \
	7zHeader.o \
	7zIn.o \
	7zItem.o \
	7zMethodID.o \
	LzmaDecode.o \
	BranchX86.o \
	BranchX86_2.o

7Z_DIR = ../7z/C

7Z_OBJS_SRC = \
	$(7Z_DIR)/Archive/7z/*.c  \
	$(7Z_DIR)/Compress/Branch/BranchX86.c \
	$(7Z_DIR)/Compress/Branch/BranchX86_2.c \
	$(7Z_DIR)/Compress/Lzma/LzmaDecode.c \
	$(7Z_DIR)/7zCrc.c

all: pylauncher.exe header.exe pyrun.exe

header.exe:$(7Z_OBJS) unpack.o deletedir.o header.o str.o resources.o
	$(CC) -o $@ $(LDFLAGS) $(LIBS) $^
	$(STRIP) $@

pyrun.exe: deletedir.o pyrun.o str.o resources.o
	$(CC) -o $@ $(LDFLAGS) $(LIBS) $^
	$(STRIP) $@

pylauncher.exe: deletedir.o pylauncher.o str.o resources.o
	$(CC) -o $@ $(LDFLAGS) $(LIBS) $^
	$(STRIP) $@

$(7Z_OBJS): $(7Z_OBJS_SRC)
	$(CC) $(DEBUGFLAG) $(CFLAGS) $^

resources.o: resources.rc
	$(WINDRES) -o $@ $^

pylauncher.o: pylauncher.c
	$(CC) $(DEBUGFLAG) $(CFLAGS) $^

pyrun.o: pyrun.c
	$(CC) $(DEBUGFLAG) $(CFLAGS) $^

header.o: header.c
	$(CC) $(DEBUGFLAG) $(CFLAGS) $^

deletedir.o: deletedir.c
	$(CC) $(DEBUGFLAG) $(CFLAGS) $^

unpack.o: unpack.c
	$(CC) $(DEBUGFLAG) $(CFLAGS) $^

str.o: str.c
	$(CC) $(DEBUGFLAG) $(CFLAGS) $^

clean:
	rm -f unpack.exe header.exe pylauncher.exe $(7Z_OBJS) *.d *.o

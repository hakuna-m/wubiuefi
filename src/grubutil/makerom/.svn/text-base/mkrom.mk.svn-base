EXEEXT=.exe

all: rom_isa.img rom_pci.img rom_isa_lzma.img rom_pci_lzma.img makerom$(EXEEXT)

rom_isa.img: romboot.S
	gcc -nostdlib -Wl,-T -Wl,ldscript -o rom_isa$(EXEEXT) $<
	objcopy -O binary rom_isa$(EXEEXT) $@
	rm rom_isa$(EXEEXT)

rom_pci.img: romboot.S
	gcc -nostdlib -Wl,-T -DPCI -Wl,ldscript -o rom_pci$(EXEEXT) $<
	objcopy -O binary rom_pci$(EXEEXT) $@
	rm rom_pci$(EXEEXT)

rom_isa_lzma.img: romboot.S
	gcc -nostdlib -Wl,-T -DLZMA -Wl,ldscript -o rom_isa_lzma$(EXEEXT) $<
	objcopy -O binary rom_isa_lzma$(EXEEXT) $@
	rm rom_isa_lzma$(EXEEXT)

rom_pci_lzma.img: romboot.S
	gcc -nostdlib -Wl,-T -DLZMA -DPCI -Wl,ldscript -o rom_pci_lzma$(EXEEXT) $<
	objcopy -O binary rom_pci_lzma$(EXEEXT) $@
	rm rom_pci_lzma$(EXEEXT)

makerom$(EXEEXT): makerom.c
	gcc -mno-cygwin -o $@ $<
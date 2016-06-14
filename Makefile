export SHELL = sh
PACKAGE = wubi
ICON = data/images/Wubi.ico
VERSION = $(shell head -n 1 debian/changelog | sed -e "s/^$(PACKAGE) (\(.*\)).*/\1/g" | cut -d r -f 1)
REVISION = $(shell head -n 1 debian/changelog | sed -e "s/^$(PACKAGE) (\(.*\)).*/\1/g" | cut -d r -f 2)
COPYRIGHTYEAR = 2009
AUTHOR = Agostino Russo
EMAIL = agostino.russo@gmail.com

all: build check

build: wubi

wubi: wubi-pre-build
	PYTHONPATH=src tools/pywine -OO src/pypack/pypack --verbose --bytecompile --outputdir=build/wubi src/main.py data build/bin build/version.py build/winboot build/translations
	PYTHONPATH=src tools/pywine -OO build/pylauncher/pack.py build/wubi
	mv build/application.exe build/wubi.exe

wubizip: wubi-pre-build
	PYTHONPATH=src tools/pywine src/pypack/pypack --verbose --outputdir=build/wubi src/main.py data build/bin build/version.py build/winboot build/translations
	cp wine/drive_c/Python27/python.exe build/wubi #TBD
	cd build; zip -r wubi.zip wubi

wubi-pre-build: check_wine check_winboot pylauncher winboot2 src/main.py src/wubi/*.py cpuid version.py translations
	rm -rf build/wubi
	rm -rf build/bin
	cp -a blobs build/bin
	cp wine/drive_c/Python27/python27.dll build/pylauncher #TBD
	cp build/cpuid/cpuid.dll build/bin

pot:
	xgettext --default-domain="$(PACKAGE)" --output="po/$(PACKAGE).pot" $(shell find src/wubi -name "*.py" | sort)
	sed -i 's/SOME DESCRIPTIVE TITLE/Translation template for $(PACKAGE)/' po/$(PACKAGE).pot
	sed -i "s/YEAR THE PACKAGE'S COPYRIGHT HOLDER/$(COPYRIGHTYEAR)/" po/$(PACKAGE).pot
	sed -i 's/FIRST AUTHOR <EMAIL@ADDRESS>, YEAR/$(AUTHOR) <$(EMAIL)>, $(COPYRIGHTYEAR)/' po/$(PACKAGE).pot
	sed -i 's/Report-Msgid-Bugs-To: /Report-Msgid-Bugs-To: $(EMAIL)/' po/$(PACKAGE).pot
	sed -i 's/CHARSET/UTF-8/' po/$(PACKAGE).pot
	sed -i 's/PACKAGE VERSION/$(VERSION)-r$(REVISION)/' po/$(PACKAGE).pot
	sed -i 's/PACKAGE/$(PACKAGE)/' po/$(PACKAGE).pot

update-po: pot
	for i in po/*.po ;\
	do \
	mv $$i $${i}.old ; \
	(msgmerge $${i}.old po/wubi.pot | msgattrib --no-obsolete > $$i) ; \
	rm $${i}.old ; \
	done

translations: po/*.po
	mkdir -p build/translations/
	@for po in $^; do \
		language=`basename $$po`; \
		language=$${language%%.po}; \
		target="build/translations/$$language/LC_MESSAGES"; \
		mkdir -p $$target; \
		msgfmt --output=$$target/$(PACKAGE).mo $$po; \
	done

version.py:
	$(shell echo 'version = "$(VERSION)"' > build/version.py)
	$(shell echo 'revision = $(REVISION)' >> build/version.py)
	$(shell echo 'application_name = "$(PACKAGE)"' >> build/version.py)

pylauncher: 7z src/pylauncher/*
	cp -rf src/pylauncher build
	cp "$(ICON)" build/pylauncher/application.ico
	sed -i 's/application_name/$(PACKAGE)/' build/pylauncher/pylauncher.exe.manifest
	cd build/pylauncher; make

cpuid: src/cpuid/cpuid.c
	cp -rf src/cpuid build
	cd build/cpuid; make

winboot2:
	mkdir -p build/winboot
	cp -f data/wubildr.cfg data/wubildr-bootstrap.cfg build/winboot/
	/usr/lib/grub/i386-pc/grub-ntldr-img --grub2 --boot-file=wubild2 -o build/winboot/wubild2.mbr
	cd build/winboot && tar cf wubildr.tar wubildr.cfg
	mkdir -p build/grubutil
	grub-mkimage -O i386-pc -c build/winboot/wubildr-bootstrap.cfg -m build/winboot/wubildr.tar -o build/grubutil/core.img \
		loadenv biosdisk part_msdos part_gpt fat ntfs ext2 ntfscomp iso9660 loopback search linux boot minicmd cat cpuid chain halt help ls reboot \
		echo test configfile gzio normal sleep memdisk tar font gfxterm gettext true vbe vga video_bochs video_cirrus probe
	cat /usr/lib/grub/i386-pc/lnxboot.img build/grubutil/core.img > build/winboot/wubild2
	mkdir -p build/winboot/EFI
	grub-mkimage -O x86_64-efi -c build/winboot/wubildr-bootstrap.cfg -m build/winboot/wubildr.tar -o build/winboot/EFI/grubx64.efi \
		loadenv part_msdos part_gpt fat ntfs ext2 ntfscomp iso9660 loopback search linux linuxefi boot minicmd cat cpuid chain halt help ls reboot \
		echo test configfile gzio normal sleep memdisk tar font gfxterm gettext true efi_gop efi_uga video_bochs video_cirrus probe efifwsetup \
		all_video gfxterm_background png gfxmenu
	cp /usr/lib/shim/shim.efi.signed build/winboot/EFI/shimx64.efi
	cp /usr/lib/shim/MokManager.efi.signed build/winboot/EFI/MokManager.efi
	sbsign --key .key/*.key --cert .key/*.crt --output build/winboot/EFI/grubx64.efi build/winboot/EFI/grubx64.efi
	grub-mkimage -O i386-efi -c build/winboot/wubildr-bootstrap.cfg -m build/winboot/wubildr.tar -o build/winboot/EFI/grubia32.efi \
		loadenv part_msdos part_gpt fat ntfs ext2 ntfscomp iso9660 loopback search linux linuxefi boot minicmd cat cpuid chain halt help ls reboot \
		echo test configfile gzio normal sleep memdisk tar font gfxterm gettext true efi_gop efi_uga video_bochs video_cirrus probe efifwsetup \
		all_video gfxterm_background png gfxmenu
	sbsign --key .key/*.key --cert .key/*.crt --output build/winboot/EFI/grubia32.efi build/winboot/EFI/grubia32.efi
	cp .key/*.cer build/winboot/EFI/.

winboot: grub4dos grubutil
	mkdir -p build/winboot
	cp -f data/menu.winboot build/winboot/menu.lst
	cp -f build/grub4dos/stage2/grldr build/winboot/wubild2
	cp -f build/grub4dos/stage2/grub.exe build/winboot/wubild2.exe
	dd if=build/winboot/wubild2 of=build/winboot/wubild2.mbr bs=1 count=8192
	cd build/winboot; ../grubutil/grubinst/grubinst -o -b=wubild2 wubild2.mbr

grub4dos: src/grub4dos/*
	cp -rf src/grub4dos build
	cd build/grub4dos;./configure --enable-preset-menu=../../data/menu.winboot
	cd build/grub4dos; make

grubutil: src/grubutil/grubinst/*
	cp -rf src/grubutil build
	cd build/grubutil/grubinst; make

# not compiling 7z at the moment, but source is used by pylauncher
7z: src/7z/C/*.c
	mkdir -p build/7z
	cp -rf src/7z build

runbin: wubi
	rm -rf build/test
	mkdir build/test
	cd build/test; ../../tools/wine ../wubi.exe --test

check_wine: tools/check_wine
	tools/check_wine

check_winboot: tools/check_winboot
	tools/check_winboot

unittest:
	tools/pywine tools/test

check: wubi
	tests/run

runpy:
	PYTHONPATH=src tools/pywine src/main.py --test

clean:
	rm -rf dist/*
	rm -rf build/*

.PHONY: all build test wubi wubizip wubi-pre-build pot runpy runbin check_wine check_winboot unittest
	7z translations version.py pylauncher winboot grubutil grub4dos

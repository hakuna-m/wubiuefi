application_name = "Wubi"
version = "8.10"
subversion = 0
revision  = 0
release = "beta"
default_distro = "Ubuntu"
change_icon_on_distro_change = True
change_artwork_on_distro_change = True
compulsory_metalink_signature = True
cd_info_file = ".disk\info"
home_page_url =  "http://www.ubuntu.com"
!define SupportPageURL "http://www.ubuntu.com/support"
!define Publisher "Ubuntu"
!define BackupFolderName ubuntu-backup
!define DefaultInstallationDir "ubuntu"
!define MinMemoryMB 256 #min memory size for installation puroposes
!define MinSizeMB 5000 #min disk size for installation puroposes
!define ReallyMinSizeMB 1000 #min size if booting from ISO
!define cdBootOnly false

!ifdef ${AppSuffix}
    !define AppFullVersion "${AppVersion}-${AppSuffix}"
!else
    !define AppFullVersion "${AppVersion}"
!endif

!if ${cdBootOnly} == true
    !define AppFullName "${AppName}-cdboot-${AppFullVersion}"
!else
    !define AppFullName "${AppName}-${AppFullVersion}"
!endif

!define OutFile "${AppFullName}-rev${AppRevision}.exe"

VIAddVersionKey "ProductName" "${AppName}"
VIAddVersionKey "Comments" "Licenced under GPL version 2 or later"
VIAddVersionKey "LegalTrademarks" "Ubuntu is a trademark of Canonical Ltd."
VIAddVersionKey "LegalCopyright" " Agostino Russo et al., and Canonical Ltd."
VIAddVersionKey "FileDescription" "Windows based UBuntu Installer"
VIAddVersionKey "FileVersion" "${AppFullVersion}"
VIProductVersion "${AppVersion}.${AppSubVersion}.${AppRevision}"

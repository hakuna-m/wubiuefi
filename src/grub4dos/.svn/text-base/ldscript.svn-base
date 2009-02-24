/* Linker script to create grub .img files on Cygwin.  */

SECTIONS
{
  .text :
  {
    start = . ;
    *(.text)
    etext = . ;
  }
  .data :
  {
    __data_start__ = . ;
    *(.data)
    __data_end__ = . ;
  }
  .rdata :
  {
    __rdata_start__ = . ;
    *(.rdata)
    __rdata_end__ = . ;
  }
  .pdata :
  {
    *(.pdata)
    edata = . ;
  }
  .bss :
  {
    __bss_start__ = . ;
    *(.bss)
    __common_start__ = . ;
    *(COMMON)
    __bss_end__ = . ;
  }
  .edata :
  {
    *(.edata)
    end = . ;
  }
  .stab :
  {
    *(.stab)
  }
  .stabstr :
  {
    *(.stabstr)
  }
}

ASSERT("__rdata_end__"=="edata", ".pdata not empty")
ASSERT("__bss_end__"  =="end"  , ".edata not empty")


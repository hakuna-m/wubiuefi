/*
 *  cpuid.c - test for long mode using cpuid instruction
 *  Copyright (C) 2007  Robert Millan <rmh@aybabtu.com>
 *  Based on gcc/gcc/config/i386/driver-i386.c
 *  Copyright (C) 2006, 2007  Free Software Foundation, Inc.
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#define cpuid(num,a,b,c,d) \
  asm volatile ("xchgl %%ebx, %1; cpuid; xchgl %%ebx, %1" \
		: "=a" (a), "=r" (b), "=c" (c), "=d" (d)  \
		: "0" (num))

#define bit_LM (1 << 29)

int
check_64bit ()
{
  unsigned int eax, ebx, ecx, edx;
  unsigned int max_level;
  unsigned int ext_level;
  unsigned char has_longmode = 0;

  /* See if we can use cpuid.  */
  asm volatile ("pushfl; pushfl; popl %0; movl %0,%1; xorl %2,%0;"
		"pushl %0; popfl; pushfl; popl %0; popfl"
		: "=&r" (eax), "=&r" (ebx)
		: "i" (0x00200000));
  if (((eax ^ ebx) & 0x00200000) == 0)
    goto done;

  /* Check the highest input value for eax.  */
  cpuid (0, eax, ebx, ecx, edx);
  /* We only look at the first four characters.  */
  max_level = eax;
  if (max_level == 0)
    goto done;

  cpuid (0x80000000, eax, ebx, ecx, edx);
  ext_level = eax;
  if (ext_level < 0x80000000)
    goto done;

  cpuid (0x80000001, eax, ebx, ecx, edx);
  has_longmode = !!(edx & bit_LM);

done:
  return has_longmode;
}

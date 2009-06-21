/*
 *  GRUB Utilities --  Utilities for GRUB Legacy, GRUB2 and GRUB for DOS
 *  Copyright (C) 2007 Bean (bean123ch@gmail.com)
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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int
main (int argc, char *argv[])
{
  FILE *in, *out;
  int major, minor, len;
  char ver[40];

  if (argc != 3)
    {
      fprintf (stderr, "Usage: ver2h version version.h\n");
      return 1;
    }

  in = fopen (argv[1], "rt");

  if (!in)
    {
      fprintf (stderr, "ver2h: open %s fail\n", argv[1]);
      return 1;
    }

  ver[0] = 0;
  fgets (ver, sizeof (ver), in);
  len = strlen (ver) - 1;
  while ((len >= 0) && ((ver[len] == '\r') || (ver[len] == '\n')))
    len--;
  ver[len + 1] = 0;
  sscanf (ver, "%d.%d", &major, &minor);

  fclose (in);

  out = fopen (argv[2], "wt");

  if (!out)
    {
      fclose (in);
      fprintf (stderr, "ver2h: open %s fail\n", argv[2]);
      return 1;
    }

  fprintf (out, "#define VERSION \"%s\"\n", ver);
  fprintf (out, "#define VER_MAJOR %d\n", major);
  fprintf (out, "#define VER_MINOR %d\n", minor);
  fclose (out);

  return 0;
}

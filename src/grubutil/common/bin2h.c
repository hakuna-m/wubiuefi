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

int
main (int argc, char *argv[])
{
  FILE *in, *out;
  unsigned char *data;
  int length, i;

  if (argc != 4)
    {
      fprintf (stderr, "Usage: bin2h file.dat outfile.h token_name\n");
      return 1;
    }

  in = fopen (argv[1], "rb");

  if (!in)
    {
      fprintf (stderr, "bin2h: open %s fail\n", argv[1]);
      return 1;
    }

  fseek (in, 0, SEEK_END);
  length = ftell (in);
  fseek (in, 0, SEEK_SET);

  if (length == 0)
    {
      fprintf (stderr, "bin2h: %s is empty\n", argv[1]);
      return 1;
    }

  if ((data = malloc (length)) == NULL)
    {
      fclose (in);
      fprintf (stderr, "bin2h: can\'t allocate memory\n");
      return 1;
    }

  if ((fread (data, 1, length, in)) != length)
    {
      fclose (in);
      fprintf (stderr, "bin2h: read %s fail\n", argv[1]);
      return 1;
    }

  fclose (in);

  out = fopen (argv[2], "wt");

  if (!out)
    {
      fclose (in);
      fprintf (stderr, "bin2h: open %s fail\n", argv[2]);
      return 1;
    }

  fprintf (out, "unsigned char %s[%d] = {", argv[3], length);

  for (i = 0; i < length; i++)
    {
      if (i % 20 == 0)
	{
	  fprintf (out, "\n  ");
	}
      fprintf (out, "%d", data[i]);
      if (i != length - 1)
	fprintf (out, ",");
    }

  fprintf (out, "};\n");
  fclose (out);
  free (data);
  return 0;
}

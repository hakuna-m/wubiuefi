/*
 *  mbrstart.S -- Master boot record code for loading GRLDR
 *  Copyright (C) 2005  Tinybit(tinybit@163.net)
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

/*
 * This program is used to generate the GRLDR.MBR file.
 *
 * Use the following shell command to generate the GRLDR.MBR file:
 *
 * 	cat mbrstart > grldr.mbr
 *
 */

#define GRLDR_MBR
#include "grldrstart.S"


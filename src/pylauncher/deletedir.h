/*
 * Copyright (c) 2007, 2008 Agostino Russo
 * Using http://www.codeguru.com/forum/showthread.php?t=239271
 *
 *  Written by Agostino Russo <agostino.russo@gmail.com>
 *  Heavily inspired by exemaker from Fredrik Lundh
 *
 *  pylauncher is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as
 *  published by the Free Software Foundation; either version 2 of
 *  the License, or (at your option) any later version.
 *
 *  pylauncher is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * DESCRIPTION:
 * Recursively deletes a directory
 */

#include <windows.h>
#include <conio.h>

int delete_directory(char* root_directory);

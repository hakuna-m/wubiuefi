#! /bin/sh

#
#  GRUB Utilities --  Utilities for GRUB Legacy, GRUB2 and GRUB for DOS
#  Copyright (C) 2007 Bean (bean123ch@gmail.com)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

cd $1

if [ -n "$2" ]; then
	if [ "a$2" != "adate" ]; then
		echo $2
		exit
	fi
else
	if [ -d .svn ]; then
		svn info | sed -n "s/Revision:\ //p"
		exit
	fi
fi

date --utc --iso-8601

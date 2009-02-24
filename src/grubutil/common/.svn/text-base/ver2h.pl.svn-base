#!/usr/bin/perl -w

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

#
# Read the "version" file and produce some macro declarations
#

use Fcntl;

($vfile, $vout) = @ARGV;
sysopen(VERSION, $vfile, O_RDONLY) or die "$0: Cannot open $vfile\n";
$version = <VERSION>;
chomp $version;
close(VERSION);

unless ( $version =~ /^([0-9]+)\.([0-9]+) *([A-Za-z0-9 ]*)$/ ) {
    die "$0: Cannot parse version format\n";
}
$vma = $1+0; $vmi = $2+0;

sysopen(VI, $vout, O_WRONLY|O_CREAT|O_TRUNC)
    or die "$0: Cannot create $vout: $!\n";
print VI "#define VERSION \"$version\"\n";
print VI "#define VER_MAJOR $vma\n";
print VI "#define VER_MINOR $vmi\n";
close(VI);

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

$delim = $/;
undef $/;       # undef input record separator - read file as a whole

$ifile = shift;
$ofile = shift;
$token = shift;

if (! $token) {
    die "Usage: bin2h file.dat outfile.h token_name\n";
}

# open ifile
open(INFILE,$ifile) || die "bin2h: open $ifile fail\n";
binmode(INFILE);

# check file size
@st = stat($ifile);
if (1 && $st[7] <= 0) {
    die "bin2h: $ifile is empty\n";
}

# read whole file
$data = <INFILE>;
close(INFILE);

$n = length($data);
die "bin2h: read $ifile fail" if ($n != $st[7]);

# open ofile
open(OUTFILE,">$ofile") || die "bin2h: open $ofile fail\n";
binmode(OUTFILE);
select(OUTFILE);

$if = $ifile;
$if =~ s/.*[\/\\]//;
$of = $ofile;
$of =~ s/.*[\/\\]//;

printf("unsigned char %s[%d] = {",$token,$n);
for ($i = 0; $i < $n; $i++) {
    if ($i % 20 == 0) {
        printf("\n  ");
    }
    printf("%d", ord(substr($data, $i, 1)));
    print "," if ($i != $n - 1);
}

print "};\n";

close(OUTFILE);
select(STDOUT);

undef $delim;
exit(0);

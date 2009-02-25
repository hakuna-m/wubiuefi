# Copyright (c) 2008 Agostino Russo
#
# Written by Agostino Russo <agostino.russo@gmail.com>
#
# This file is part of Wubi the Win32 Ubuntu Installer.
#
# Wubi is free software; you can redistribute it and/or modify
# it under 5the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.
#
# Wubi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

'''
win32 mappings
'''

hkl2variant = {
    0x00010409 : "dvorak",
    0x00020409 : "intl",
    0x00010C0C : "fr-legacy",
    0x00001009 : "multix",
    0x0000100C : "fr",
    0x00000807 : "de_nodeadkeys",
    0x0001041F : "f",
    0x0000041F : "alt",
}

icountry2country = {
    376 : "AD",
    971 : "AE",
    93 : "AF",
    1268 : "AG",
    1264 : "AI",
    355 : "AL",
    374 : "AM",
    599 : "AN",
    244 : "AO",
    54 : "AR",
    1684 : "AS",
    43 : "AT",
    61 : "AU",
    297 : "AW",
    994 : "AZ",
    387 : "BA",
    1246 : "BB",
    880 : "BD",
    32 : "BE",
    226 : "BF",
    359 : "BG",
    973 : "BH",
    257 : "BI",
    229 : "BJ",
    1441 : "BM",
    673 : "BN",
    591 : "BO",
    55 : "BR",
    1242 : "BS",
    975 : "BT",
    267 : "BW",
    375 : "BY",
    501 : "BZ",
    2 : "CA",
    236 : "CF",
    242 : "CG",
    243 : "CG",
    41 : "CH",
    225 : "CI",
    682 : "CK",
    56 : "CL",
    237 : "CM",
    86 : "CN",
    57 : "CO",
    506 : "CR",
    53 : "CU",
    238 : "CV",
    357 : "CY",
    420 : "CZ",
    49 : "DE",
    253 : "DJ",
    45 : "DK",
    1767 : "DM",
    1809 : "DO",
    1829 : "DO",
    213 : "DZ",
    593 : "EC",
    372 : "EE",
    20 : "EG",
    291 : "ER",
    34 : "ES",
    251 : "ET",
    358 : "FI",
    679 : "FJ",
    500 : "FK",
    691 : "FM",
    298 : "FO",
    33 : "FR",
    241 : "GA",
    44 : "GB",
    1473 : "GD",
    995 : "GE",
    594 : "GF",
    233 : "GH",
    350 : "GI",
    299 : "GL",
    220 : "GM",
    224 : "GN",
    590 : "GP",
    240 : "GQ",
    30 : "GR",
    502 : "GT",
    1671 : "GU",
    245 : "GW",
    592 : "GY",
    852 : "HK",
    504 : "HN",
    385 : "HR",
    509 : "HT",
    36 : "HU",
    62 : "ID",
    353 : "IE",
    972 : "IL",
    91 : "IN",
    964 : "IQ",
    98 : "IR",
    354 : "IS",
    39 : "IT",
    1876 : "JM",
    962 : "JO",
    81 : "JP",
    254 : "KE",
    996 : "KG",
    855 : "KH",
    686 : "KI",
    269 : "KM",
    1869 : "KN",
    850 : "KP",
    82 : "KR",
    965 : "KW",
    1345 : "KY",
    961 : "LB",
    1758 : "LC",
    423 : "LI",
    94 : "LK",
    231 : "LR",
    266 : "LS",
    370 : "LT",
    352 : "LU",
    371 : "LV",
    218 : "LY",
    212 : "MA",
    377 : "MC",
    373 : "MD",
    382 : "ME",
    261 : "MG",
    692 : "MH",
    389 : "MK",
    223 : "ML",
    95 : "MM",
    976 : "MN",
    853 : "MO",
    1670 : "MP",
    596 : "MQ",
    222 : "MR",
    1664 : "MS",
    356 : "MT",
    230 : "MU",
    960 : "MV",
    265 : "MW",
    52 : "MX",
    60 : "MY",
    258 : "MZ",
    264 : "NA",
    687 : "NC",
    227 : "NE",
    672 : "NF",
    234 : "NG",
    505 : "NI",
    31 : "NL",
    47 : "NO",
    977 : "NP",
    674 : "NR",
    683 : "NU",
    64 : "NZ",
    968 : "OM",
    507 : "PA",
    51 : "PE",
    689 : "PF",
    675 : "PG",
    63 : "PH",
    92 : "PK",
    48 : "PL",
    508 : "PM",
    1787 : "PR",
    1939 : "PR",
    970 : "PS",
    351 : "PT",
    680 : "PW",
    595 : "PY",
    974 : "QA",
    40 : "RO",
    381 : "RS",
    7 : "RU",
    250 : "RW",
    966 : "SA",
    677 : "SB",
    248 : "SC",
    249 : "SD",
    46 : "SE",
    65 : "SG",
    290 : "SH",
    386 : "SI",
    421 : "SK",
    232 : "SL",
    378 : "SM",
    221 : "SN",
    252 : "SO",
    597 : "SR",
    239 : "ST",
    503 : "SV",
    963 : "SY",
    268 : "SZ",
    1649 : "TC",
    235 : "TD",
    228 : "TG",
    66 : "TH",
    992 : "TJ",
    690 : "TK",
    670 : "TL",
    993 : "TM",
    216 : "TN",
    676 : "TO",
    90 : "TR",
    1868 : "TT",
    688 : "TV",
    886 : "TW",
    255 : "TZ",
    380 : "UA",
    256 : "UG",
    1 : "US",
    598 : "UY",
    998 : "UZ",
    379 : "VA",
    1784 : "VC",
    58 : "VE",
    1284 : "VG",
    1340 : "VI",
    84 : "VN",
    678 : "VU",
    681 : "WF",
    685 : "WS",
    967 : "YE",
    262 : "YT",
    27 : "ZA",
    260 : "ZM",
    263 : "ZW",
}

keymaps = {
    0x0423 : "by", # Belarussian
    0x0402 : "bg", # Bulgarian
    0x0405 : "cz", # Czech
    0x0807 : "ch", # Swiss German
    0x0c07 : "de", # Austrian German
    0x0407 : "de", # German
    0x1407 : "de", # Liechtenstein German
    0x1007 : "de", # Luxembourg German
    0x0406 : "dk", # Danish
    0x0c09 : "us", # Australia
    0x2809 : "us", # Belize
    0x1009 : "us", # Canada
    0x2409 : "us", # Caribbean
    0x4009 : "us", # India
    0x2009 : "us", # Jamaica
    0x4409 : "us", # Malaysia
    0x1409 : "us", # New Zealand
    0x3409 : "us", # Philippines (Tagalog)
    0x4809 : "us", # Singapore
    0x1c09 : "us", # South Africa
    0x2c09 : "us", # Trinidad and Tobago
    0x0409 : "us", # United States
    0x3009 : "us", # Zimbabwe
    0x0c04 : "us", # Chinese / Hong Kong
    0x1404 : "us", # Chinese / Macao
    0x1004 : "us", # Chinese / Singapore
    0x0804 : "us", # Chinese / Simplified
    0x0404 : "us", # Chinese / Traditional
    0x0412 : "us", # Korean
    0x0413 : "us", # Dutch
    0x1401 : "ara", # Arabic / Algeria
    0x3c01 : "ara", # Arabic / Bahrain
    0x0c01 : "ara", # Arabic / Egypt
    0x0801 : "ara", # Arabic / Iraq
    0x2c01 : "ara", # Arabic / Jordan
    0x3401 : "ara", # Arabic / Kuwait
    0x3001 : "ara", # Arabic / Lebanon
    0x1001 : "ara", # Arabic / Libya
    0x1801 : "ara", # Arabic / Morocco
    0x2001 : "ara", # Arabic / Oman
    0x4001 : "ara", # Arabic / Qatar
    0x0401 : "ara", # Arabic / Saudi Arabia
    0x2801 : "ara", # Arabic / Syria
    0x1c01 : "ara", # Arabic / Tunisia
    0x3801 : "ara", # Arabic / U.A.E.
    0x2401 : "ara", # Arabic / Yemen
    0x0429 : "ir", # Persian", #0x0439 : "in_deva #TBD add variant to variants.ini
    0x0439 : "in", # Hindi
    0x0421 : "us", # Indonesian
    0x041c : "al", # Albanian
    0x042a : "vn", # Vietnamese
    0x0434 : "us", # Xhosa
    0x0809 : "gb", # United Kingdom
    0x1809 : "gb", # Ireland
    0x083c : "ie", # Irish / Gaelic
    0x0452 : "gb", # Welsh
    0x0425 : "ee", # Estonian
    0x0c0a : "es", # Spanish / Castillian
    0x0403 : "es", # Catalan
    0x042d : "es", # Basque
    0x0456 : "es", # Galician
    0x2c0a : "latam", # Spanish / Argentina
    0x400a : "latam", # Spanish / Bolivia
    0x340a : "latam", # Spanish / Chile
    0x240a : "latam", # Spanish / Colombia
    0x140a : "latam", # Spanish / Costa Rica
    0x1c0a : "latam", # Spanish / Dominican Republic
    0x300a : "latam", # Spanish / Ecuador
    0x440a : "latam", # Spanish / El Salvador
    0x100a : "latam", # Spanish / Guatemala
    0x480a : "latam", # Spanish / Honduras
    0x080a : "latam", # Spanish / Mexico
    0x4c0a : "latam", # Spanish / Nicaragua
    0x180a : "latam", # Spanish / Panama
    0x3c0a : "latam", # Spanish / Paraguay
    0x280a : "latam", # Spanish / Peru
    0x500a : "latam", # Spanish / Puerto Rico
    0x380a : "latam", # Spanish / Uruguay
    0x200a : "latam", # Spanish / Venezuela
    0x040b : "fi", # Finnish
    0x040c : "fr", # French / France
    0x140c : "fr", # French / Luxembourg
    0x180c : "fr", # French / Monaco
    0x047e : "fr", # Breton
    0x0482 : "fr", # Occitan
    0x080c : "be", # French / Belgium
    0x0813 : "be", # Dutch / Belgium
    0x0c0c : "ca", # French / Quebec", #0x100c : "ch_fr #TBD add variant to variants.ini
    0x100c : "ch", # French / Switzerland
    0x0408 : "gr", # Greek
    0x040d : "il", # Hebrew
    0x040e : "hu", # Hungarian
    0x040f : "is", # Icelandic
    0x0410 : "it", # Italian
    0x0810 : "ch", # Italian / Switzerland
    0x0427 : "lt", # Lithuanian
    0x0426 : "lv", # Latvian
    0x0411 : "jp", # Japanese (106 Key)
    0x042f : "mk", # Macedonian
    0x0414 : "no", # Norwegian / Bokmal
    0x0814 : "no", # Norwegian / Nynorsk", #0x0c3b : "fi_smi #TBD add variant to variants.ini
    0x0c3b : "fi", # Northern Sami / Finland", #0x043b : "no_smi #TBD add variant to variants.ini
    0x043b : "no", # Northern Sami / Norway", #0x083b : "se_smi #TBD add variant to variants.ini
    0x083b : "se", # Northern Sami / Sweden
    0x0415 : "pl", # Polish
    0x0416 : "br", # Portuguese / Brazil
    0x0816 : "pt", # Portuguese
    0x0418 : "ro", # Romanian
    0x0419 : "ru", # Russian
    0x041b : "sk", # Slovakian
    0x0424 : "si", # Slovenian
    0x041a : "hr", # Serbo-Croatian / Croatia / Latin
    0x101a : "ba", # Serbo-Croatian / Bosnia and Herzegovina / Latin
    0x7c1a : "ba", # Serbo-Croatian / Bosnia and Herzegovina / Cyrillic
    0x181a : "cs", # Serbo-Croatian / Serbia and Montenegro / Latin
    0x0c1a : "cs", # Serbo-Croatian / Serbia and Montenegro / Cyrillic
    0x081d : "se", # Swedish / Finland
    0x041d : "se", # Swedish / Sweden
    0x041e : "th", # Thai
    0x041f : "tr", # Turkish (F layout)
    0x0422 : "ua", # Ukrainian
}

n2language = {
    1052 : "sq", # Albanian
    1025 : "ar", # Arabic
    1069 : "eu", # Basque
    1059 : "be", # Belarusian
    5146 : "bs", # Bosnian
    1026 : "bg", # Bulgarian
    1027 : "ca", # Catalan
    2052 : "zh", # Chinese (Simplified)
    1028 : "zh", # Chinese (Traditional)
    1050 : "hr", # Croatian
    1029 : "cs", # Czech
    1030 : "da", # Danish
    1043 : "nl", # Dutch
    1033 : "en", # English
    1061 : "et", # Estonian
    1035 : "fi", # Finnish
    1036 : "fr", # French
    1031 : "de", # German
    1032 : "el", # Greek
    1037 : "he", # Hebrew
    1038 : "hu", # Hungarian
    1057 : "id", # Indonesian
    1040 : "it", # Italian
    1041 : "ja", # Japanese
    1042 : "ko", # Korean
    9999 : "ku", # Kurdish
    1062 : "lv", # Latvian
    1063 : "lt", # Lithuanian
    1071 : "mk", # Macedonian
    1044 : "nb", # Norwegian
    2068 : "nn", # NorwegianNynorsk
    1045 : "pl", # Polish
    1046 : "pt", # PortugueseBR
    2070 : "pt", # Portuguese
    1048 : "ro", # Romanian
    1049 : "ru", # Russian
    1051 : "sk", # Slovak
    1060 : "sl", # Slovenian
    1034 : "es", # Spanish
    1053 : "sv", # Swedish
    1054 : "th", # Thai
    1055 : "tr", # Turkish
    1058 : "uk", # Ukrainian
}

language2n = dict([(v,k) for k,v in n2language.items()])

n2fulllanguage = {
    1052 : "Albanian",
    1025 : "Arabic",
    1069 : "Basque",
    1059 : "Belarusian",
    5146 : "Bosnian",
    1026 : "Bulgarian",
    1027 : "Catalan",
    2052 : "Chinese (Simplified)",
    1028 : "Chinese (Traditional)",
    1050 : "Croatian",
    1029 : "Czech",
    1030 : "Danish",
    1043 : "Dutch",
    1033 : "English",
    1061 : "Estonian",
    1035 : "Finnish",
    1036 : "French",
    1031 : "German",
    1032 : "Greek",
    1037 : "Hebrew",
    1038 : "Hungarian",
    1057 : "Indonesian",
    1040 : "Italian",
    1041 : "Japanese",
    1042 : "Korean",
    9999 : "Kurdish",
    1062 : "Latvian",
    1063 : "Lithuanian",
    1071 : "Macedonian",
    1044 : "Norwegian",
    2068 : "NorwegianNynorsk",
    1045 : "Polish",
    1046 : "PortugueseBR",
    2070 : "Portuguese",
    1048 : "Romanian",
    1049 : "Russian",
    1051 : "Slovak",
    1060 : "Slovenian",
    1034 : "Spanish",
    1053 : "Swedish",
    1054 : "Thai",
    1055 : "Turkish",
    1058 : "Ukrainian",
}


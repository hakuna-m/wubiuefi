/*
 * Copyright (c) 2007, 2008 Agostino Russo
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
 * Pylauncher extracts a lzma archive that can be appended to this
 * executable and containing:
 *
 * ./main.pyo           # main script to run
 * ./data                  # data
 * ./lib                     # python modules, ./lib is added to PYTHONPATH
 * ./python.dll         # python dll
 *
 * then it loads python.dll and runs main.py within that. A python
 * script can be packed in the appropriate format using pack.py
 *
 * Note that the current implementation assumes that the python modules
 * are bytecompiled and  optimized (*.pyo)
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include "windows.h"
#include "deletedir.h"
#include "str.h"

#define true 1
#define false 0

int __cdecl
main(int ac, char **av)
{
    //~ printf("pylauncher: starting\n");
    DWORD i;
    char *cmd;
    char message[MAX_PATH + 1000];
    char targetdir[MAX_PATH];
    char exefile[MAX_PATH];
    strcpy(targetdir, av[1]);
    strcpy(exefile, av[2]);

    //Run script in python script via pyrun
    cmd = (char *)malloc((strlen(targetdir)*2 + +strlen(exefile) + 19) * sizeof(char));
    sprintf(cmd, "\"%s\\pyrun.exe\" \"%s\" \"%s\"", targetdir, targetdir, exefile);
    for (i = 3; i < (DWORD) ac; i++){
        cmd = concat(cmd, " ", true);
        cmd = concat(cmd, av[i], true);
    }
    STARTUPINFO si;
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    PROCESS_INFORMATION pi;
    //~ printf("pylauncher running cmd: %s\n", cmd);
    if(!CreateProcess(NULL, cmd, NULL, NULL, TRUE, 0, NULL, NULL, &si, &pi)){
        strcpy(message, "Failed to run pyrun\n");
        free(cmd);
        goto error;
    } else {
        WaitForSingleObject(pi.hProcess, INFINITE);
    }
    free(cmd);

    //Delete directory
    //~ printf("pylauncher: deleting temp directory %s\n", targetdir);
    delete_directory(targetdir);

    //~ printf("pylauncher: Finished\n");
    return 0;

error:
    MessageBox(NULL, message, "Internal error", MB_ICONERROR | MB_OK);
    //TBD We should delete the targetdir but might be risky
    return 1;
}

int WINAPI
WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance,
        LPSTR lpCmdLine, int nCmdShow)
{
    return main(__argc, __argv);
}

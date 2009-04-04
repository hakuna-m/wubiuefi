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
#include "unpack.h"
#include "deletedir.h"
#include "str.h"

#define true 1
#define false 0

int __cdecl
main(int ac, char **av)
{
    //~ printf("header: starting\n");
    char *cmd;
    char message[MAX_PATH + 1000];
    char pylauncher[MAX_PATH];
    char currentdir[MAX_PATH];
    char exefile[MAX_PATH];
    char tmpdir[MAX_PATH];
    char targetdir[MAX_PATH];

    GetModuleFileName(NULL, exefile, sizeof(exefile));

    //Create targetdir
    GetTempPath(MAX_PATH, tmpdir);
    GetTempFileName(tmpdir, "pyl", 0, targetdir);
    DeleteFile(targetdir);
    getcwd(currentdir, MAX_PATH);
    CreateDirectory(targetdir, NULL);
    chdir(targetdir);

    //Extract LZMA bundled archive
    if (unpack(exefile)) {
        sprintf(message, "Cannot unpack %s\n", exefile);
        goto error;
    }

    //Copy pylauncher.exe
    sprintf(pylauncher, "%s.exe", targetdir);
    if (!CopyFile("pylauncher.exe", pylauncher, FALSE)){
        sprintf(message, "Cannot copy %s\n", pylauncher);
        goto error;
    }

    HANDLE exe_handle = OpenProcess(SYNCHRONIZE, TRUE, GetCurrentProcessId());
    HANDLE pylauncher_handle = CreateFile(pylauncher, 0, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_FLAG_DELETE_ON_CLOSE, NULL);

    cmd = (char *)malloc((strlen(pylauncher) + strlen(targetdir) + strlen(exefile) + 9) * sizeof(char));
    sprintf(cmd, "\"%s\" \"%s\" \"%s\"", pylauncher, targetdir, exefile);
    DWORD i;
    for (i = 1; i < (DWORD) ac; i++){
        cmd = concat(cmd, " ", true);
        cmd = concat(cmd, av[i], true);
    }
    STARTUPINFO si;
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    PROCESS_INFORMATION pi;
    //~ printf("header running cmd: %s\n", cmd);
    if(!CreateProcess(NULL, cmd, NULL, NULL, TRUE, 0, NULL, NULL, &si, &pi)){
        strcpy(message, "Failed to run pylauncher\n");
        free(cmd);
        goto error;
    }
    free(cmd);

    Sleep(1000); // Give time to the new process to start
    //~ printf("header: finishing\n");
    CloseHandle(exe_handle);
    CloseHandle(pylauncher_handle);
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

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
 * ./main.py            # main script to run
 * ./data                  # data
 * ./lib                     # python modules, ./lib is added to PYTHONPATH
 * ./python.dll         # python dll
 *
 * then it loads python.dll and runs main.py within that. A python
 * script can be packed in the appropriate format using pack.py
 */

#include <stdio.h>
#include <stdlib.h>
#include "windows.h"
#include "unpack.h"

int __cdecl
main(int ac, char **av)
{
    HINSTANCE dll;
    char* argv[100];
    int (__cdecl * Py_Main)(int argc, char *argv[]);
    void (__cdecl * Py_SetPythonHome)(char* home);
    char exefile[256];
    char exefilearg[256];
    DWORD i;
    char dllfile[256] = "python23.dll"; //TBD be a bit more flexible on the dll used
    char pythonpath[256] = "lib";
    char pythonhome[256] = ".";
    char scriptfile[256] = "main.pyc";
    char message[512];
    char debug[3] = "Off";
    char verbose[2] = "0";
    char tmpdir[MAX_PATH];

    //Get path of this executable
    GetModuleFileName(NULL, exefile, sizeof(exefile));

    //Create tmpdir
    GetTempPath(MAX_PATH, &tmpdir);
    GetTempFileName(&tmpdir, "pyl", 0, &tmpdir);
    DeleteFile(tmpdir);
    //~ mkdtemp(tmpdir);
    CreateDirectory(tmpdir, NULL);
    chdir(tmpdir);

    //Extract LZMA bundled archive
    if (unpack(exefile)) {
        strcpy(message, "Cannot unpack "); strcat(message, exefile);
        goto error;
    }

    //Load python dll file
    dll = LoadLibraryEx(dllfile, NULL, LOAD_WITH_ALTERED_SEARCH_PATH);
    if (!dll) {
        strcpy(message, "Cannot find "); strcat(message, dllfile);
        goto error;
    }
    GetModuleFileName(dll, dllfile, sizeof(dllfile));

    //Get entry point for Py_main
    Py_Main = (void*) GetProcAddress(dll, "Py_Main");
    if (!Py_Main)
        ExitProcess(1);

    //Set python path
    Py_SetPythonHome = (void*) GetProcAddress(dll, "Py_SetPythonHome");
    if (Py_SetPythonHome) {
        Py_SetPythonHome(pythonhome); // SetPythonHome keeps a reference!
    }

    //Set environment variables
    SetEnvironmentVariable("PYTHONHOME", pythonhome);
    SetEnvironmentVariable("PYTHONOPTIMIZE", NULL);
    SetEnvironmentVariable("PYTHONPATH", pythonpath);
    SetEnvironmentVariable("PYTHONVERBOSE", verbose);
    SetEnvironmentVariable("PYTHONDEBUG", debug);

    //Run script in python
    argv[0] = exefile;
    argv[1] = "-S";
    argv[2] = scriptfile;
    strcpy(exefilearg, "--exefile=");
    strcat(exefilearg, exefile);
    argv[3] = exefilearg;
    for (i = 1; i < (DWORD) ac; i++)
        argv[3+i] = av[i];
    return Py_Main(3+i, argv);

    //TBD delete tempdir

error:
    MessageBox(NULL, message, "Internal error", MB_ICONERROR | MB_OK);
    return 1;
}

int WINAPI
WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance,
        LPSTR lpCmdLine, int nCmdShow)
{
    return main(__argc, __argv);
}

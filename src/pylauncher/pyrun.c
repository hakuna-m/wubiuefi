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
    //~ printf("pyrun: starting\n");
    int result;
    DWORD i;
    char* argv[100];
    char message[MAX_PATH + 1000];
    char exefile[MAX_PATH];
    char originalexefile[MAX_PATH + 100];
    char targetdir[MAX_PATH];
    const char dllfile[MAX_PATH] = "python23.dll";
    const char pythonpath[MAX_PATH] = "lib";
    const char pythonhome[MAX_PATH] = ".";
    const char scriptfile[MAX_PATH] = "main.pyo";
    const char debug[4] = "Off";
    const char verbose[2] = "0";

    HINSTANCE dll;
    int (__cdecl * Py_Main)(int argc, char *argv[]);
    void (__cdecl * Py_SetPythonHome)(char* home);

    //Get path of this executable
    GetModuleFileName(NULL, exefile, sizeof(exefile));

    //Find targetdir (dir containing exefile)
    strcpy(targetdir, av[1]);
    sprintf(originalexefile, "--exefile=\"%s\"", av[2]);
    //~ printf("pyrun targetdir=%s\n", targetdir);
    chdir(targetdir);

    //Load python dll file
    dll = LoadLibraryEx(dllfile, NULL, LOAD_WITH_ALTERED_SEARCH_PATH);
    if (!dll) {
        sprintf(message, "Cannot find %s\n", dllfile);
        goto error;
    }
    GetModuleFileName(dll, dllfile, sizeof(dllfile));

    //Get entry point for Py_main
    Py_Main = (int (*)(int, char**)) GetProcAddress(dll, "Py_Main");
    if (!Py_Main){
        ExitProcess(1);
    }

    //Set python path
    Py_SetPythonHome = (void (*)(char*)) GetProcAddress(dll, "Py_SetPythonHome");
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
    argv[2] = "-OO";
    argv[3] = scriptfile;
    argv[4] = originalexefile;
    int nargs = 5;
    for (i = 3; i < (DWORD) ac; i++){
        argv[nargs] = av[i];
        nargs++;
    }
    //~ printf("pyrun running python with following arguments:\n");
    //~ for (i = 0; i < nargs; i++){
        //~ printf("arg %i = %s\n", i, argv[i]);
    //~ }
    result = Py_Main(nargs, argv);

    //~ printf("pyrun: Finished\n");
    return result;

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

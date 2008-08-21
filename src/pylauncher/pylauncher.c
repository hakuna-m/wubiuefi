/*
 * pylauncher
 *
 * extracts an ELF LZMA archive that can be appended to this executable
 * and containing:
 *
 * ./run.config         # runtime configuration file
 *./bin/python24.dll  # python dll
 *./script.py            # main script to run
 *./data                  # data
 *./lib                     # pure python modules
 *
 * the actual directory content can be changed in run.config
 * run.config can set other python.dll options such as
 * debug, python.dll path, pythopath, pythonhome, verbose...
 *
 * Copyright (c) 2008-2009 by Agostino Russo
 * Heavily inspired by exemaker from Fredrik Lundh
 * from which most of code have been ripped
*/

#include <stdio.h>
#include <stdlib.h>
#include "windows.h"

int __cdecl
main(int ac, char **av)
{
    HINSTANCE dll;
    HANDLE file;
    DWORD n;
    char* argv[100];
    int (__cdecl * Py_Main)(int argc, char *argv[]);
    void (__cdecl * Py_SetPythonHome)(char* home);
    char configfile[256] = "run.config";
    char exefile[256];
    DWORD i;
    //TBD the following should be extracted from run.config
    char dllfile[256] = "python23.dll";
    char pythonpath[256] = ".";
    char pythonhome[256] = ".";
    char scriptfile[256] = "wubi.py";
    char message[512];
    char debug[3] = "Off";
    char verbose[2] = "0";

    GetModuleFileName(NULL, exefile, sizeof(exefile));

    //TBD extract LZMA archive from ELF executable

    //TBD read inputs from configfile
    /*
    file = CreateFile(configfile, GENERIC_READ, FILE_SHARE_READ, NULL,
                      OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
     if (file == (HANDLE) -1) {
        strcpy(message, "Cannot open "); strcat(message, configfile);
        goto error;
    }
    ReadFile(file, dllfile, sizeof(dllfile)-1, &n, NULL);
    CloseHandle(file);
    */

    //Load dll file
    dll = LoadLibraryEx(dllfile, NULL, LOAD_WITH_ALTERED_SEARCH_PATH);
    if (!dll) {
        strcpy(message, "Cannot find "); strcat(message, dllfile+2);
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

    //TBD: set environment variables, does not seem to work !!!
    SetEnvironmentVariable("PYTHONHOME", pythonhome); //do we need it?
    SetEnvironmentVariable("PYTHONOPTIMIZE", NULL);
    SetEnvironmentVariable("PYTHONPATH", pythonpath);
    SetEnvironmentVariable("PYTHONVERBOSE", verbose);
    SetEnvironmentVariable("PYTHONDEBUG", debug);

    argv[0] = exefile;
    argv[1] = "-S";
    argv[2] = scriptfile;
    for (i = 1; i < (DWORD) ac; i++)
        argv[2+i] = av[i];
    return Py_Main(2+i, argv);

error:
    MessageBox(NULL, message, "Internal error", MB_ICONERROR | MB_OK);
    return 1;
}

#if 0
int WINAPI
WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance,
        LPSTR lpCmdLine, int nCmdShow)
{
    return main(__argc, __argv);
}
#endif

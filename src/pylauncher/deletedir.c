/*
 * Copyright (c) 2007, 2008 Agostino Russo
 *
 *  Written by Agostino Russo <agostino.russo@gmail.com>
 *  Following example at http://www.codeguru.com/forum/showthread.php?t=239271
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

#include "deletedir.h"
#include "str.h"
#include "windows.h"

#define true 1
#define false 0

int _delete_directory(char* root_directory);

int delete_directory(char* target_directory)
{
    char abs_path[MAX_PATH];
    int result;
    if (GetFullPathName(target_directory, MAX_PATH, abs_path, NULL)!=0){
        chdir("\\");
        result = _delete_directory(abs_path);
        return result;
    }
    return 1;
}

int _delete_directory(char* root_directory)
{
    int result;
    HANDLE file_handle;
    char* file_path = 0;
    char* pattern;
    WIN32_FIND_DATA file_info;

    pattern = concat(root_directory, "\\*.*", false);
    if(!pattern) return ERROR_NOT_ENOUGH_MEMORY;
    file_handle = FindFirstFile(pattern, &file_info);

    if(file_handle != INVALID_HANDLE_VALUE){
        do{
            if(file_info.cFileName[0] != '.'){
                file_path = concat(root_directory, "\\", false);
                file_path = concat(file_path, file_info.cFileName, true);
                if(!file_path) {
                    FindClose(file_handle);
                    free(pattern);
                    return ERROR_NOT_ENOUGH_MEMORY;
                }
                result = 0;
                if(file_info.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY){
                    // Delete subdirectory
                    result = _delete_directory(file_path);
                } else {
                    // Set file attributes
                    if(SetFileAttributes(file_path, FILE_ATTRIBUTE_NORMAL) == FALSE){
                        result = GetLastError();
                    }
                    // Delete file
                    if(DeleteFile(file_path) == FALSE){
                        result = GetLastError();
                    }
                }
                if(result){
                    freestr(&file_path);
                    FindClose(file_handle);
                    free(pattern);
                    return result;
                }
            }
        } while(FindNextFile(file_handle, &file_info) == TRUE);
        freestr(&file_path);
        FindClose(file_handle);
        free(pattern);

        DWORD dwError = GetLastError();
        if(dwError != ERROR_NO_MORE_FILES){
            return dwError;
        } else {
            // Set directory attributes
            if(SetFileAttributes(root_directory, FILE_ATTRIBUTE_NORMAL) == FALSE){
                return GetLastError();
            }
            // Delete directory
            if(RemoveDirectory(root_directory) == FALSE){
                return GetLastError();
            }
        }
    }
    return 0;
}

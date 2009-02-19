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
 * Unpacks an lzma archive
 */

#include "unpack.h"
#include "str.h"
#include <string.h>

#define true 1
#define false 0

#ifdef USE_WINDOWS_FUNCTIONS
typedef HANDLE MY_FILE_HANDLE;
#else
typedef FILE *MY_FILE_HANDLE;
#endif

//TBD using a global here is ugly as hell, but will do for now
size_t g_offset = 0;

#ifdef USE_WINDOWS_FUNCTIONS
/*
   ReadFile and WriteFile functions in Windows have BUG:
   If you Read or Write 64MB or more (probably min_failure_size = 64MB - 32KB + 1)
   from/to Network file, it returns ERROR_NO_SYSTEM_RESOURCES
   (Insufficient system resources exist to complete the requested service).
*/
#define kChunkSizeMax (1 << 24)
#endif

size_t read_file(MY_FILE_HANDLE file, void *data, size_t size)
{
    if (size == 0)
        return 0;
    #ifdef USE_WINDOWS_FUNCTIONS
    {
        size_t processed_size = 0;
        do
        {
            DWORD cur_size = (size > kChunkSizeMax) ? kChunkSizeMax : (DWORD)size;
            DWORD processed_loc = 0;
            BOOL res = ReadFile(file, data, cur_size, &processed_loc, NULL);
            data = (void *)((unsigned char *)data + processed_loc);
            size -= processed_loc;
            processed_size += processed_loc;
            if (!res || processed_loc == 0)
                break;
        }
        while (size > 0);
        return processed_size;
    }
    #else
    return fread(data, 1, size, file);
    #endif
}

size_t write_file(MY_FILE_HANDLE file, void *data, size_t size)
{
    if (size == 0)
        return 0;
    #ifdef USE_WINDOWS_FUNCTIONS
    {
        size_t processed_size = 0;
        do
        {
            DWORD cur_size = (size > kChunkSizeMax) ? kChunkSizeMax : (DWORD)size;
            DWORD processed_loc = 0;
            BOOL res = WriteFile(file, data, cur_size, &processed_loc, NULL);
            data = (void *)((unsigned char *)data + processed_loc);
            size -= processed_loc;
            processed_size += processed_loc;
            if (!res)
                break;
        }
        while (size > 0);
        return processed_size;
    }
    #else
    return fwrite(data, 1, size, file);
    #endif
}

int close_file(MY_FILE_HANDLE file)
{
    #ifdef USE_WINDOWS_FUNCTIONS
    return (CloseHandle(file) != FALSE) ? 0 : 1;
    #else
    return fclose(file);
    #endif
}

typedef struct _CFileInStream
{
    ISzInStream InStream;
    MY_FILE_HANDLE File;
} CFileInStream;

#ifdef _LZMA_IN_CB

#define kBufferSize (1 << 12)
Byte g_Buffer[kBufferSize];

SZ_RESULT read_file_imp(void *object, void **buffer, size_t max_required_size, size_t *processed_size)
{
    CFileInStream *s = (CFileInStream *)object;
    size_t processedSizeLoc;
    if (max_required_size > kBufferSize)
        max_required_size = kBufferSize;
    processedSizeLoc = read_file(s->File, g_Buffer, max_required_size);
    *buffer = g_Buffer;
    if (processed_size != 0)
        *processed_size = processedSizeLoc;
    return SZ_OK;
}

#else

SZ_RESULT read_file_imp(void *object, void *buffer, size_t size, size_t *processed_size)
{
    CFileInStream *s = (CFileInStream *)object;
    size_t processedSizeLoc = read_file(s->File, buffer, size);
    if (processed_size != 0)
        *processed_size = processedSizeLoc;
    return SZ_OK;
}

#endif

SZ_RESULT seek_file_imp(void *object, CFileSize pos)
{
    CFileInStream *s = (CFileInStream *)object;
    pos += g_offset;
    #ifdef USE_WINDOWS_FUNCTIONS
    {
        LARGE_INTEGER value;
        value.LowPart = (DWORD)pos;
        value.HighPart = (LONG)((UInt64)pos >> 32);
        #ifdef _SZ_FILE_SIZE_32
        /* VC 6.0 has bug with >> 32 shifts. */
        value.HighPart = 0;
        #endif
        value.LowPart = SetFilePointer(s->File, value.LowPart, &value.HighPart, FILE_BEGIN);
        if (value.LowPart == 0xFFFFFFFF)
            if(GetLastError() != NO_ERROR)
                return SZE_FAIL;
        return SZ_OK;
    }
    #else
    int res = fseek(s->File, (long)pos, SEEK_SET);
    if (res == 0)
        return SZ_OK;
    return SZE_FAIL;
    #endif
}

MY_FILE_HANDLE open_file_r(char *file_name)
{
    MY_FILE_HANDLE output_handle;
    output_handle =
    #ifdef USE_WINDOWS_FUNCTIONS
    CreateFile(file_name, GENERIC_READ, FILE_SHARE_READ,
      NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (output_handle == INVALID_HANDLE_VALUE)
        return 0;
    #else
    fopen(file_name, "rb");
    #endif
    return output_handle;
}

MY_FILE_HANDLE open_file_w(char *file_name)
{
    MY_FILE_HANDLE output_handle;
    output_handle =
    #ifdef USE_WINDOWS_FUNCTIONS
    CreateFile(file_name, GENERIC_WRITE, FILE_SHARE_READ,
        NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (output_handle == INVALID_HANDLE_VALUE)
        return 0;
    #else
    fopen(file_name, "wb+");
    #endif
    return output_handle;
}

int create_directory(char *directory_name)
{
    int result;
    #ifdef USE_WINDOWS_FUNCTIONS
    CreateDirectory(directory_name,NULL);
    #else
    result = mkdir(directory_name); //, S_IRUSR | S_IWUSR); //second argument not supported by mingw version
    #endif
    return result;
}

void print_error(char *message)
{
    #ifdef DEBUG
    printf("\nERROR: %s\n", message);
    #ifdef USE_WINDOWS_FUNCTIONS
    MessageBox(NULL, message, "Unpack Error", MB_ICONERROR | MB_OK);
    #endif
    #endif
}

CFileSize seek_beginning_of_archive(CFileInStream *archive_stream)
{
    UInt32 i;
    int is_found;
    char* pylauncher = "@@@pylauncher@@@";
    char* signature = concatn(pylauncher, (char*)k7zSignature, k7zSignatureSize, false);
    if(!signature) return 1;
    int signature_size = strlen(signature);
    int result;
    size_t archive_size = 0;
    #ifdef DEBUG
    printf("signature: '%s'\n", signature);
    #endif
    #ifdef USE_WINDOWS_FUNCTIONS
        archive_size = 1000000 //TBD
    #else
        struct stat filestat;
        fstat(fileno(archive_stream->File), &filestat);
        archive_size = filestat.st_size;
    #endif
    is_found = false;
    Byte b[signature_size];
    #ifdef DEBUG
    printf("archive_size=%d", archive_size);
    #endif
    for (i=0; i < archive_size; i++){
        result = seek_file_imp(archive_stream, i);
        result = read_file(archive_stream->File, &b, signature_size);
        if (result == 0){
            break;
        }
        if(memcmp(signature, b, signature_size) == 0) {
            is_found = true;
            break;
        }
    }
    #ifdef DEBUG
    printf("signature=%s, offset=%d, found=%i\n", b, i, is_found);
    #endif
    if (! is_found){
        print_error("Could not find the beginning of the archive");
    }
    free(signature);
    return (CFileSize)(i + strlen(pylauncher));
}

int unpack(char archive[512])
{
    UInt32 i;
    CFileInStream archive_stream;
    CArchiveDatabaseEx db;
    SZ_RESULT res;
    ISzAlloc alloc_imp;
    ISzAlloc alloc_temp_imp;
    #ifdef DEBUG
    printf("extracting %s...\n", archive);
    #endif
    archive_stream.File = open_file_r(archive);
    if (archive_stream.File == 0)
    {
        print_error("can not open input file");
        return 1;
    }
    archive_stream.InStream.Read = read_file_imp;
    archive_stream.InStream.Seek = seek_file_imp;
    alloc_imp.Alloc = SzAlloc;
    alloc_imp.Free = SzFree;
    alloc_temp_imp.Alloc = SzAllocTemp;
    alloc_temp_imp.Free = SzFreeTemp;
    CrcGenerateTable();

    //SEEK OFFSET
    size_t offset;
    offset = seek_beginning_of_archive(&archive_stream);

    //INIT DB
    SzArDbExInit(&db);

    //SET THE OFFSET
    g_offset = offset;
    seek_file_imp(&archive_stream.InStream, 0); //seek to beginning of file including offset

    res = SzArchiveOpen(&archive_stream.InStream, &db, &alloc_imp, &alloc_temp_imp);
    #ifdef DEBUG
    printf("res = %i\n",res);
    #endif
    if (res == SZ_OK)
    {
        /*
        if you need cache, use these 3 variables.
        if you use external function, you can make these variable as static.
        */
        UInt32 block_index = 0xFFFFFFFF; /* it can have any value before first call (if out_buffer = 0) */
        Byte *out_buffer = 0; /* it must be 0 before first call for each new archive. */
        size_t out_buffer_size = 0;    /* it can have any value before first call (if out_buffer = 0) */

        //~ for (i = db.Database.NumFolders-1; i >0; i--)
        //~ {
            //~ CFileItem *f = db.Database.Folders + i;
            //~ if (!f->IsDirectory){
            //~ } else {
            //~ }
        //~ }

        for (i = db.Database.NumFiles-1; i >0; i--)
        {
            CFileItem *f = db.Database.Files + i;
            if (!f->IsDirectory){
                continue;
            }
            #ifdef DEBUG
            printf("Creating directory %s", f->Name);
            #endif
            if (create_directory(f->Name) != 0)
            {
                print_error("can not create directory");
            }
            #ifdef DEBUG
            printf("\n");
            #endif
        }

        for (i = 0; i < db.Database.NumFiles; i++)
        {
            CFileItem *f = db.Database.Files + i;
            #ifdef DEBUG
            printf("Extracting %s\n %d %s", f->Name, i, f->IsDirectory);
            #endif
            if (f->IsDirectory){
                continue;
            }
            size_t out_size_processed;
            #ifdef DEBUG
            printf("Extracting %s\n", f->Name);
            #endif
            res = SzExtract(&archive_stream.InStream, &db, i,
                    &block_index, &out_buffer, &out_buffer_size,
                    &offset, &out_size_processed,
                    &alloc_imp, &alloc_temp_imp);

            if (res != SZ_OK)
                break;

            MY_FILE_HANDLE output_handle = open_file_w(f->Name);
            if (output_handle == 0)
            {
                print_error("can not open output file");
                res = SZE_FAIL;
                break;
            }

            size_t processed_size;
            processed_size = write_file(output_handle, out_buffer + offset, out_size_processed);
            if (processed_size != out_size_processed)
            {
                print_error("can not write output file");
                res = SZE_FAIL;
                break;
            }
            if (close_file(output_handle))
            {
                print_error("can not close output file");
                res = SZE_FAIL;
                break;
            }
            #ifdef DEBUG
            printf("\n");
            #endif
        }
        alloc_imp.Free(out_buffer);
    }
    SzArDbExFree(&db, alloc_imp.Free);

    close_file(archive_stream.File);
    if (res == SZ_OK)
    {
        #ifdef DEBUG
        printf("\nEverything is Ok\n");
        #endif
        return 0;
    }
    if (res == (SZ_RESULT)SZE_NOTIMPL)
        print_error("decoder doesn't support this archive");
    else if (res == (SZ_RESULT)SZE_OUTOFMEMORY)
        print_error("can not allocate memory");
    else if (res == (SZ_RESULT)SZE_CRC_ERROR)
        print_error("CRC error");
    else
        print_error("Unknown error"); //TBD print res
    return 1;
}

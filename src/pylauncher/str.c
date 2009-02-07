#include <stdlib.h>
#include <string.h>

char* concat(char* str1, char* str2, int free_old)
{
    if(!str1 || !str2) return NULL;
    size_t len1 = strlen(str1);
    size_t len2 = strlen(str2);
    char* result = (char*) malloc(len1+len2+1);
    if(!result) return NULL;
    strcpy(result, str1);
    strcpy(result+len1, str2);
    if(free_old) free(str1);
    return result;
}

char* concatn(char* str1, char* str2, size_t len2, int free_old)
{
    if(!str1 || !str2) return NULL;
    size_t len1 = strlen(str1);
    char* result = (char*) malloc(len1+len2+1);
    if(!result) return NULL;
    strcpy(result, str1);
    strncpy(result+len1, str2, len2);
    result[len1+len2] = '\0';
    if(free_old) free(str1);
    return result;
}

void freestr(char** ptr) {
    if(*ptr) free(*ptr);
    *ptr = 0;
}


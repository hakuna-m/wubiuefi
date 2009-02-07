#ifndef _STR_H_
#define _STR_H_

char* concat(char* str1, char* str2, int free_old);
char* concatn(char* str1, char* str2, size_t len2, int free_old);
void freestr(char** ptr);

#endif


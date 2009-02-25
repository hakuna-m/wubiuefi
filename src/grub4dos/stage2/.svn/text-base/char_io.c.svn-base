/* char_io.c - basic console input and output */
/*
 *  GRUB  --  GRand Unified Bootloader
 *  Copyright (C) 1999,2000,2001,2002,2004  Free Software Foundation, Inc.
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

#include <shared.h>
#include <term.h>

#ifdef SUPPORT_HERCULES
# include <hercules.h>
#endif

#ifdef SUPPORT_SERIAL
# include <serial.h>
#endif

#ifndef STAGE1_5
struct term_entry term_table[] =
  {
    {
      "console",
      0,
      24,
      console_putchar,
      console_checkkey,
      console_getkey,
      console_getxy,
      console_gotoxy,
      console_cls,
      console_setcolorstate,
      console_setcolor,
      console_setcursor,
      0,
      0
    },
#ifdef SUPPORT_SERIAL
    {
      "serial",
      /* A serial device must be initialized.  */
      TERM_NEED_INIT,
      24,
      serial_putchar,
      serial_checkkey,
      serial_getkey,
      serial_getxy,
      serial_gotoxy,
      serial_cls,
      serial_setcolorstate,
      0,
      0,
      0,
      0
    },
#endif /* SUPPORT_SERIAL */
#ifdef SUPPORT_HERCULES
    {
      "hercules",
      0,
      24,
      hercules_putchar,
      console_checkkey,
      console_getkey,
      hercules_getxy,
      hercules_gotoxy,
      hercules_cls,
      hercules_setcolorstate,
      hercules_setcolor,
      hercules_setcursor,
      0,
      0
    },      
#endif /* SUPPORT_HERCULES */
#ifdef SUPPORT_GRAPHICS
    { "graphics",
      TERM_NEED_INIT, /* flags */
      30, /* number of lines */
      graphics_putchar, /* putchar */
      console_checkkey, /* checkkey */
      console_getkey, /* getkey */
      graphics_getxy, /* getxy */
      graphics_gotoxy, /* gotoxy */
      graphics_cls, /* cls */
      graphics_setcolorstate, /* setcolorstate */
      graphics_setcolor, /* setcolor */
      graphics_setcursor, /* nocursor */
      graphics_init, /* initialize */
      graphics_end /* shutdown */
    },
#endif /* SUPPORT_GRAPHICS */
    /* This must be the last entry.  */
    { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 }
  };

/* This must be console.  */
struct term_entry *current_term = term_table;

int max_lines = 24;
int count_lines = -1;
int use_pager = 1;
#endif

int quit_print = 0;

void
print_error (void)
{
  if (errnum > ERR_NONE && errnum < MAX_ERR_NUM)
#ifndef STAGE1_5
    /* printf("\7\n %s\n", err_list[errnum]); */
    printf ("\nError %u: %s\n", errnum, err_list[errnum]);
#else /* STAGE1_5 */
    printf ("Error %u\n", errnum);
#endif /* STAGE1_5 */
}

char *
convert_to_ascii (char *buf, int c,...)
{
  unsigned long num = *((&c) + 1), mult = 10;
  char *ptr = buf;

#ifndef STAGE1_5
  if (c == 'x' || c == 'X')
    mult = 16;

  if ((num & 0x80000000uL) && c == 'd')
    {
      num = (~num) + 1;
      *(ptr++) = '-';
      buf++;
    }
#endif

  do
    {
      int dig = num % mult;
      *(ptr++) = ((dig > 9) ? dig + c - 33 : '0' + dig);
    }
  while (num /= mult);

  /* reorder to correct direction!! */
  {
    char *ptr1 = ptr - 1;
    char *ptr2 = buf;
    while (ptr1 > ptr2)
      {
	int tmp = *ptr1;
	*ptr1 = *ptr2;
	*ptr2 = tmp;
	ptr1--;
	ptr2++;
      }
  }

  return ptr;
}

void
grub_putstr (const char *str)
{
  while (*str)
    grub_putchar (*str++);
}

#if 1
void
grub_printf (const char *format,...)
{
  int *dataptr = (int *)(void *) &format;
  char c, str[16];
  char pad;
  int width;
  
  dataptr++;

  while ((c = *(format++)) != 0)
    {
      if (c != '%')
	grub_putchar (c);
      else
      {
	pad = ' ';
	width = 0;
	c = *(format++);

#ifndef STAGE1_5
find_specifier:
#endif
	switch (c)
	  {
#ifndef STAGE1_5
	  case 'd':
	  case 'x':
	  case 'X':
#endif
	  case 'u':
	    *convert_to_ascii (str, c, *((unsigned long *) dataptr++)) = 0;
	    width -= grub_strlen (str);
	    if (width > 0)
		while(width--)
		    grub_putchar (pad);
	    grub_putstr (str);
	    break;

#ifndef STAGE1_5
	  case 'c':
	    if (width > 0)
		while(--width)
		    grub_putchar (pad);
	    grub_putchar ((*(dataptr++)) & 0xff);
	    break;

	  case 's':
	    width -= grub_strlen ((char *) *(dataptr));
	    if (width > 0)
		while(width--)
		    grub_putchar (pad);
	    grub_putstr ((char *) *(dataptr++));
	    break;
	  case '0':
	    pad = '0';
	  case '1' ... '9':
	    width = c - '0';
	    while ((c = *(format++)) >= '0' && c <= '9')
	    {
		width = width * 10 + c - '0';
	    }

	    /* format is now pointing to the non-numerical char */
#if 1
	    goto find_specifier;
#else
	    switch (c)
	    {
		case 'd':
		case 'x':
		case 'X':
		case 'u':
		    *convert_to_ascii (str, c, *((unsigned long *) dataptr++)) = 0;
		    width -= grub_strlen (str);
		    if (width > 0)
			while(--width)
			    grub_putchar (pad);
		    grub_putstr (str);
		    break;
		case 'c':
		    if (width > 0)
			while(--width)
			    grub_putchar (pad);
		    grub_putchar ((*(dataptr++)) & 0xff);
		    break;

		case 's':
		    width -= grub_strlen ((char *) *(dataptr++));
		    if (width > 0)
			while(--width)
			    grub_putchar (pad);
		    grub_putstr ((char *) *(dataptr++));
		    break;

	    }
#endif
#endif
	  }
      }
    }
}
#else
int
grub_printf (const char *format,...)
{
	/* sorry! this does not work :-( */
	return grub_sprintf (NULL, format,...);
}
#endif

int
grub_sprintf (char *buffer, const char *format, ...)
{

  /* Call with buffer==NULL, and it will just printf().  */

  /* XXX hohmuth
     ugly hack -- should unify with printf() */
  int *dataptr = (int *)(void *) &format;
  char c, *ptr, str[16];
  char *bp = buffer;

  dataptr++;

  while ((c = *(format++)) != 0)
    {
      if (c != '%')
      {
	if (buffer)
	  *bp++ = c; /* putchar(c); */
	else
	{
	  grub_putchar (c);
	  bp++;
	}
      }
      else
	switch (c = *(format++))
	  {
	  case 'd': case 'x':	case 'X':  case 'u':
	    *convert_to_ascii (str, c, *((unsigned long *) dataptr++)) = 0;

	    ptr = str;
	    if (buffer)
	    {
		while (*ptr)
			*bp++ = *(ptr++); /* putchar(*(ptr++)); */
	    } else {
		while (*ptr)
		{
			grub_putchar (*(ptr++));
			bp++;
		}
	    }
	    break;

	  case 'c':
	    if (buffer)
	    {
		*bp++ = (*(dataptr++)) & 0xff;
	    } else {
		grub_putchar ((*(dataptr++)) & 0xff);
		bp++;
	    }
	    break;

	  case 's':
	    ptr = (char *) (*(dataptr++));

	    if (buffer)
	    {
		while ((c = *(ptr++)) != 0)
			*bp++ = c; /* putchar(c); */
	    } else {
		while ((c = *(ptr++)) != 0)
		{
			grub_putchar (c);
			bp++;
		}
	    }
	    break;
	  }
    }

  if (buffer)
	*bp = 0;
  return bp - buffer;
}


#ifndef STAGE1_5
#include "grub4dos_version.h"

#ifdef GRUB4DOS_VERSION

void
init_page (void)
{
  cls ();

  grub_printf ("GRUB4DOS " GRUB4DOS_VERSION /* ", GNU GRUB %s" */ ", Memory: %dK / %dM, MenuEnd: 0x%X\n",
	  /* version_string, */ saved_mem_lower, saved_mem_upper / 1024, ((char *) init_free_mem_start) + 256 * sizeof (char *) + config_len/*get_code_end()*/);
}

#else

void
init_page (void)
{
  cls ();

  grub_printf ("GNU GRUB  version %s  (%dK lower / %dK upper memory)\n",
	  version_string, saved_mem_lower, saved_mem_upper);
}

#endif

/* The number of the history entries.  */
static int num_history = 0;

/* Get the NOth history. If NO is less than zero or greater than or
   equal to NUM_HISTORY, return NULL. Otherwise return a valid string.  */
static char *
get_history (int no)
{
  if (no < 0 || no >= num_history)
    return 0;

  return (char *) HISTORY_BUF + MAX_CMDLINE * no;
}

/* Add CMDLINE to the history buffer.  */
static void
add_history (const char *cmdline, int no)
{
  grub_memmove ((char *) HISTORY_BUF + MAX_CMDLINE * (no + 1),
		(char *) HISTORY_BUF + MAX_CMDLINE * no,
		MAX_CMDLINE * (num_history - no));
  grub_strcpy ((char *) HISTORY_BUF + MAX_CMDLINE * no, cmdline);
  if (num_history < HISTORY_SIZE)
    num_history++;
}

/* XXX: These should be defined in shared.h, but I leave these here,
	until this code is freezed.  */
#define CMDLINE_WIDTH	78
#define CMDLINE_MARGIN	10
  
char *prompt;
int maxlen;
int echo_char;
int readline;

static int xpos, lpos, section;

/* The length of PROMPT.  */
static int plen;
/* The length of the command-line.  */
static int llen;
/* The working buffer for the command-line.  */
static char *buf;

static void cl_refresh (int full, int len);
static void cl_backward (int count);
static void cl_forward (int count);
static void cl_insert (const char *str);
static void cl_delete (int count);
static void cl_init (void);
  
/* Move the cursor backward.  */
static void cl_backward (int count)
{
      lpos -= count;
      
      /* If the cursor is in the first section, display the first section
	 instead of the second.  */
      if (section == 1 && plen + lpos < CMDLINE_WIDTH)
	cl_refresh (1, 0);
      else if (xpos - count < 1)
	cl_refresh (1, 0);
      else
	{
	  xpos -= count;

	  if (current_term->flags & TERM_DUMB)
	    {
	      int i;
	      
	      for (i = 0; i < count; i++)
		grub_putchar ('\b');
	    }
	  else
	    gotoxy (xpos, getxy () & 0xFF);
	}
}

/* Move the cursor forward.  */
static void cl_forward (int count)
{
      lpos += count;

      /* If the cursor goes outside, scroll the screen to the right.  */
      if (xpos + count >= CMDLINE_WIDTH)
	cl_refresh (1, 0);
      else
	{
	  xpos += count;

	  if (current_term->flags & TERM_DUMB)
	    {
	      int i;
	      
	      for (i = lpos - count; i < lpos; i++)
		{
		  if (! echo_char)
		    grub_putchar (buf[i]);
		  else
		    grub_putchar (echo_char);
		}
	    }
	  else
	    gotoxy (xpos, getxy () & 0xFF);
	}
}

/* Refresh the screen. If FULL is true, redraw the full line, otherwise,
   only LEN characters from LPOS.  */
static void cl_refresh (int full, int len)
{
      int i;
      int start;
      int pos = xpos;
      
      if (full)
	{
	  /* Recompute the section number.  */
	  if (lpos + plen < CMDLINE_WIDTH)
	    section = 0;
	  else
	    section = ((lpos + plen - CMDLINE_WIDTH)
		       / (CMDLINE_WIDTH - 1 - CMDLINE_MARGIN) + 1);

	  /* From the start to the end.  */
	  len = CMDLINE_WIDTH;
	  pos = 0;
	  //grub_putchar ('\r');
	  gotoxy (0, (unsigned char) (getxy ()));

	  /* If SECTION is the first section, print the prompt, otherwise,
	     print `<'.  */
	  if (section == 0)
	    {
	      grub_printf ("%s", prompt);
	      len -= plen;
	      pos += plen;
	    }
	  else
	    {
	      grub_putchar ('<');
	      len--;
	      pos++;
	    }
	}

      /* Compute the index to start writing BUF and the resulting position
	 on the screen.  */
      if (section == 0)
	{
	  int offset = 0;
	  
	  if (! full)
	    offset = xpos - plen;
	  
	  start = 0;
	  xpos = lpos + plen;
	  start += offset;
	}
      else
	{
	  int offset = 0;
	  
	  if (! full)
	    offset = xpos - 1;
	  
	  start = ((section - 1) * (CMDLINE_WIDTH - 1 - CMDLINE_MARGIN)
		   + CMDLINE_WIDTH - plen - CMDLINE_MARGIN);
	  xpos = lpos + 1 - start;
	  start += offset;
	}

      /* Print BUF. If ECHO_CHAR is not zero, put it instead.  */
      for (i = start; i < start + len && i < llen; i++)
	{
	  if (! echo_char)
	    grub_putchar (buf[i]);
	  else
	    grub_putchar (echo_char);

	  pos++;
	}
      
      /* Fill up the rest of the line with spaces.  */
      for (; i < start + len; i++)
	{
	  grub_putchar (' ');
	  pos++;
	}
      
      /* If the cursor is at the last position, put `>' or a space,
	 depending on if there are more characters in BUF.  */
      if (pos == CMDLINE_WIDTH)
	{
	  if (start + len < llen)
	    grub_putchar ('>');
	  else
	    grub_putchar (' ');
	  
	  pos++;
	}
      
      /* Back to XPOS.  */
      if (current_term->flags & TERM_DUMB)
	{
	  for (i = 0; i < pos - xpos; i++)
	    grub_putchar ('\b');
	}
      else
	gotoxy (xpos, getxy () & 0xFF);
}

/* Initialize the command-line.  */
static void cl_init (void)
{
      /* Distinguish us from other lines and error messages!  */
      grub_putchar ('\n');

      /* Print full line and set position here.  */
      cl_refresh (1, 0);
}

/* Insert STR to BUF.  */
static void cl_insert (const char *str)
{
      int l = grub_strlen (str);

      if (llen + l < maxlen)
	{
	  if (lpos == llen)
	    grub_memmove (buf + lpos, str, l + 1);
	  else
	    {
	      grub_memmove (buf + lpos + l, buf + lpos, llen - lpos + 1);
	      grub_memmove (buf + lpos, str, l);
	    }
	  
	  llen += l;
	  lpos += l;
	  if (xpos + l >= CMDLINE_WIDTH)
	    cl_refresh (1, 0);
	  else if (xpos + l + llen - lpos > CMDLINE_WIDTH)
	    cl_refresh (0, CMDLINE_WIDTH - xpos);
	  else
	    cl_refresh (0, l + llen - lpos);
	}
}

/* Delete COUNT characters in BUF.  */
static void cl_delete (int count)
{
      grub_memmove (buf + lpos, buf + lpos + count, llen - count + 1);
      llen -= count;
      
      if (xpos + llen + count - lpos > CMDLINE_WIDTH)
	cl_refresh (0, CMDLINE_WIDTH - xpos);
      else
	cl_refresh (0, llen + count - lpos);
}

static int
real_get_cmdline (char *cmdline)
{
  /* This is a rather complicated function. So explain the concept.
     
     A command-line consists of ``section''s. A section is a part of the
     line which may be displayed on the screen, but a section is never
     displayed with another section simultaneously.

     Each section is basically 77 or less characters, but the exception
     is the first section, which is 78 or less characters, because the
     starting point is special. See below.

     The first section contains a prompt and a command-line (or the
     first part of a command-line when it is too long to be fit in the
     screen). So, in the first section, the number of command-line
     characters displayed is 78 minus the length of the prompt (or
     less). If the command-line has more characters, `>' is put at the
     position 78 (zero-origin), to inform the user of the hidden
     characters.

     Other sections always have `<' at the first position, since there
     is absolutely a section before each section. If there is a section
     after another section, this section consists of 77 characters and
     `>' at the last position. The last section has 77 or less
     characters and doesn't have `>'.

     Each section other than the last shares some characters with the
     previous section. This region is called ``margin''. If the cursor
     is put at the magin which is shared by the first section and the
     second, the first section is displayed. Otherwise, a displayed
     section is switched to another section, only if the cursor is put
     outside that section.  */

  int c;
  /* The index for the history.  */
  int history = -1;
  
  buf = (char *) CMDLINE_BUF;
  plen = grub_strlen (prompt);
  llen = grub_strlen (cmdline);

  if (maxlen > MAX_CMDLINE)
    {
      maxlen = MAX_CMDLINE;
      if (llen >= MAX_CMDLINE)
	{
	  llen = MAX_CMDLINE - 1;
	  cmdline[MAX_CMDLINE] = 0;
	}
    }
  lpos = llen;
  grub_strcpy (buf, cmdline);

  cl_init ();

  while ((char)(c = /*ASCII_CHAR*/ (getkey ())) != '\n' && (char)c != '\r')
    {
      /* If READLINE is non-zero, handle readline-like key bindings.  */
      if (readline)
	{
	  if ((char)c == 9)	/* TAB lists completions */
	      {
		int i;
		/* POS points to the first space after a command.  */
		int pos = 0;
		int ret;
		char *completion_buffer = (char *) COMPLETION_BUF;
		int equal_pos = -1;
		int is_filename;

		/* Find the first word.  */
		while (buf[pos] == ' ')
		  pos++;
		while (buf[pos] && buf[pos] != '=' && buf[pos] != ' ')
		  pos++;

		is_filename = (lpos > pos);

		/* Find the position of the equal character after a
		   command, and replace it with a space.  */
		for (i = pos; buf[i] && buf[i] != ' '; i++)
		  if (buf[i] == '=')
		    {
		      equal_pos = i;
		      buf[i] = ' ';
		      break;
		    }

		/* Find the position of the first character in this word.  */
		for (i = lpos; i > 0; i--)
		{
		    if (buf[i - 1] == ' ')
		    {
			/* find backslashes immediately before the space */
			for (ret = i - 2; ret >= 0; ret--)
			{
			    if (buf[ret] != '\\')
				break;
			}

			if (! ((i - ret) & 1)) /* the space not backslashed */
				break;
		    }
		}

		/* Invalidate the cache, because the user may exchange
		   removable disks.  */
		buf_drive = -1;

		/* Copy this word to COMPLETION_BUFFER and do the
		   completion.  */
		grub_memmove (completion_buffer, buf + i, lpos - i);
		completion_buffer[lpos - i] = 0;
		ret = print_completions (is_filename, 1);
		errnum = ERR_NONE;

		if (ret >= 0)
		  {
		    /* Found, so insert COMPLETION_BUFFER.  */
		    cl_insert (completion_buffer + lpos - i);

		    if (ret > 0)
		      {
			/* There are more than one candidates, so print
			   the list.  */
			grub_putchar ('\n');
			print_completions (is_filename, 0);
			errnum = ERR_NONE;
		      }
		  }

		/* Restore the command-line.  */
		if (equal_pos >= 0)
		  buf[equal_pos] = '=';

		if (ret)
		  cl_init ();
	      }
	  else if (c == KEY_HOME/* || (char)c == 1*/)	/* C-a beginning */
		/* Home= 0x4700 for BIOS, 0x0106 for Linux */
	      cl_backward (lpos);
	  else if (c == KEY_END/* || (char)c == 5*/)	/* C-e end */
		/* End= 0x4F00 for BIOS, 0x0168 for Linux */
	      cl_forward (llen - lpos);
	  else if (c == KEY_RIGHT/* || (char)c == 6*/)	/* C-f forward */
		/* Right= 0x4D00 for BIOS, 0x0105 for Linux */
	      {
		if (lpos < llen)
		  cl_forward (1);
	      }
	  else if (c == KEY_LEFT/* || (char)c == 2*/)	/* C-b backward */
		/* Left= 0x4B00 for BIOS, 0x0104 for Linux */
	      {
		if (lpos > 0)
		  cl_backward (1);
	      }
	  else if (c == KEY_UP/* || (char)c == 16*/)	/* C-p previous */
		/* Up= 0x4800 for BIOS, 0x0153 for Linux */
	      {
		char *p;

		if (history < 0)
		  /* Save the working buffer.  */
		  grub_strcpy (cmdline, buf);
		else if (grub_strcmp (get_history (history), buf) != 0)
		  /* If BUF is modified, add it into the history list.  */
		  add_history (buf, history);

		history++;
		p = get_history (history);
		if (! p)
		  {
		    history--;
		  }
		else
		  {

		    grub_strcpy (buf, p);
		    llen = grub_strlen (buf);
		    lpos = llen;
		    cl_refresh (1, 0);
		  }
	      }
	  else if (c == KEY_DOWN/* || (char)c == 14*/)	/* C-n next command */
		/* Down= 0x5000 for BIOS, 0x0152 for Linux */
	      {
		char *p;

		if (history >= 0)
		  {
		    if (grub_strcmp (get_history (history), buf) != 0)
		      /* If BUF is modified, add it into the history list.  */
		      add_history (buf, history);

		    history--;
		    p = get_history (history);
		    if (! p)
		      p = cmdline;

		    grub_strcpy (buf, p);
		    llen = grub_strlen (buf);
		    lpos = llen;
		    cl_refresh (1, 0);
		  }
	      }
	}

      /* ESC, C-d and C-h are always handled. Actually C-d is not
	 functional if READLINE is zero, as the cursor cannot go
	 backward, but that's ok.  */

		/* Ins= 0x5200 for BIOS, 0x014B for Linux */
		/* PgUp= 0x4900 for BIOS, 0x0153 for Linux */
		/* PgDn= 0x5100 for BIOS, 0x0152 for Linux */

	if ((char)c == 27)	/* ESC immediately return 1 */
	  return 1;
	else if (c == KEY_DC/* || (char)c == 4*/)	/* C-d delete */
		/* Del= 0x5300 for BIOS, 0x014A for Linux */
	  {
	    if (lpos != llen)
	      cl_delete (1);
	  }
	else if (c == KEY_BACKSPACE || (char)c == 8)	/* C-h backspace */
		/* Backspace= 0x0E08 for BIOS, 0x0107 for Linux */
	  {
	    if (lpos > 0)
	    {
	      cl_backward (1);
	      cl_delete (1);
	    }
	  }
	else		/* insert printable character into line */
	  {
#ifdef GRUB_UTIL
	    if (c >= ' ' && c <= '~')
	    {
	      char str[2];

	      *(short *)str = (short)c;
	      cl_insert (str);
	    }
#else
	    if ((char)c >= ' ' && (char)c <= '~')
	    {
	      char str[2];

	      str[0] = (char)c;
	      str[1] = 0;
	      cl_insert (str);
	    }
#endif
	  }
    }

  grub_putchar ('\n');

  /* If ECHO_CHAR is NUL, remove the leading spaces.  */
  lpos = 0;
  if (! echo_char)
    while (buf[lpos] == ' ')
      lpos++;

  /* Copy the working buffer to CMDLINE.  */
  grub_memmove (cmdline, buf + lpos, llen - lpos + 1);

  /* If the readline-like feature is turned on and CMDLINE is not
     empty, add it into the history list.  */
  if (readline && lpos < llen)
    add_history (cmdline, 0);

  return 0;
}

/* Don't use this with a MAXLEN greater than 1600 or so!  The problem
   is that GET_CMDLINE depends on the everything fitting on the screen
   at once.  So, the whole screen is about 2000 characters, minus the
   PROMPT, and space for error and status lines, etc.  MAXLEN must be
   at least 1, and PROMPT and CMDLINE must be valid strings (not NULL
   or zero-length).

   If ECHO_CHAR is nonzero, echo it instead of the typed character. */
int
get_cmdline (char *cmdline)
{
  int old_cursor;
  int ret;

  old_cursor = setcursor (1);
  
  /* Because it is hard to deal with different conditions simultaneously,
     less functional cases are handled here. Assume that TERM_NO_ECHO
     implies TERM_NO_EDIT.  */
  if (current_term->flags & (TERM_NO_ECHO | TERM_NO_EDIT))
    {
      char *p = cmdline;
      int c;
      
      /* Make sure that MAXLEN is not too large.  */
      if (maxlen > MAX_CMDLINE)
	maxlen = MAX_CMDLINE;

      /* Print only the prompt. The contents of CMDLINE is simply discarded,
	 even if it is not empty.  */
      grub_printf ("%s", prompt);

      /* Gather characters until a newline is gotten.  */
      while ((c = ASCII_CHAR (getkey ())) != '\n' && c != '\r')
	{
	  /* Return immediately if ESC is pressed.  */
	  if (c == 27)
	    {
	      setcursor (old_cursor);
	      return 1;
	    }

	  /* Printable characters are added into CMDLINE.  */
	  if (c >= ' ' && c <= '~')
	    {
	      if (! (current_term->flags & TERM_NO_ECHO))
		grub_putchar (c);

	      /* Preceding space characters must be ignored.  */
	      if (c != ' ' || p != cmdline)
		*p++ = c;
	    }
	}

      *p = 0;

      if (! (current_term->flags & TERM_NO_ECHO))
	grub_putchar ('\n');

      setcursor (old_cursor);
      return 0;
    }

  /* Complicated features are left to real_get_cmdline.  */
  ret = real_get_cmdline (cmdline);
  setcursor (old_cursor);
  return ret;
}

int
safe_parse_maxint (char **str_ptr, int *myint_ptr)
{
  char *ptr = *str_ptr;
  int myint = 0;
  int mult = 10, found = 0;
  int negative = 0;

  /*
   *  The decimal numbers can be positive or negative, ranging from
   *  0x80000000(the minimal int) to 0x7fffffff(the maximal int).
   *  The hex numbers are not checked.
   */

  if (*ptr == '-') /* check whether or not the negative sign exists */
    {
      ptr++;
      negative = 1;
    }

  /*
   *  Is this a hex number?
   */
  if (*ptr == '0' && tolower (*(ptr + 1)) == 'x')
    {
      ptr += 2;
      mult = 16;
    }

  while (1)
    {
      /* A bit tricky. This below makes use of the equivalence:
	 (A >= B && A <= C) <=> ((A - B) <= (C - B))
	 when C > B and A is unsigned.  */
      unsigned int digit;

      digit = tolower (*ptr) - '0';
      if (digit > 9)
	{
	  digit -= 'a' - '0';
	  if (mult == 10 || digit > 5)
	    break;
	  digit += 10;
	}

      found = 1;
      /* we do not check for hex or negative */
      if (mult == 10 && ! negative)
	if ((unsigned)myint > (((unsigned)(MAXINT - digit)) / (unsigned)mult))
	  {
	    errnum = ERR_NUMBER_OVERFLOW;
	    return 0;
	  }
      myint = ((unsigned)myint * (unsigned)mult) + digit;
      ptr++;
    }

  if (!found)
    {
      errnum = ERR_NUMBER_PARSING;
      return 0;
    }

  *str_ptr = ptr;
  *myint_ptr = negative ? -myint : myint;

  return 1;
}
#endif /* STAGE1_5 */

//#if !defined(STAGE1_5) || defined(FSYS_FAT) || defined(FSYS_NTFS)
int
grub_tolower (int c)
{
  if (c >= 'A' && c <= 'Z')
    return (c + ('a' - 'A'));

  return c;
}
//#endif /* ! STAGE1_5 || FSYS_FAT || FSYS_NTFS */

int
grub_isspace (int c)
{
  switch (c)
    {
    case ' ':
    case '\t':
    case '\r':
    case '\n':
      return 1;
    default:
      break;
    }

  return 0;
}

//#if !defined(STAGE1_5) || defined(FSYS_ISO9660)
int
grub_memcmp (const char *s1, const char *s2, int n)
{
  while (n)
    {
      if (*s1 < *s2)
	return -1;
      else if (*s1 > *s2)
	return 1;
      s1++;
      s2++;
      n--;
    }

  return 0;
}
//#endif /* ! STAGE1_5 || FSYS_ISO9660 */

#ifndef STAGE1_5
int
grub_strncat (char *s1, const char *s2, int n)
{
  int i = -1;

  while (++i < n && s1[i] != 0);

  while (i < n && (s1[i++] = *(s2++)) != 0);

  s1[n - 1] = 0;

  if (i >= n)
    return 0;

  s1[i] = 0;

  return 1;
}
#endif /* ! STAGE1_5 */

/* XXX: This below is an evil hack. Certainly, we should change the
   strategy to determine what should be defined and what shouldn't be
   defined for each image. For example, it would be better to create
   a static library supporting minimal standard C functions and link
   each image with the library. Complicated things should be left to
   computer, definitely. -okuji  */
#if !defined(STAGE1_5) || defined(FSYS_VSTAFS)
int
grub_strcmp (const char *s1, const char *s2)
{
  while (*s1 || *s2)
    {
      if (*s1 < *s2)
	return -1;
      else if (*s1 > *s2)
	return 1;
      s1 ++;
      s2 ++;
    }

  return 0;
}
#endif /* ! STAGE1_5 || FSYS_VSTAFS */

#ifndef STAGE1_5
/* Wait for a keypress and return its code.  */
int
getkey (void)
{
  return current_term->getkey ();
}

/* Check if a key code is available.  */
int
checkkey (void)
{
  return current_term->checkkey ();
}
#endif /* ! STAGE1_5 */

/* Display an ASCII character.  */
void
grub_putchar (int c)
{
  /* if it is a Line Feed, we insert a Carriage Return. */

#ifdef STAGE1_5

  /* In Stage 1.5, only the normal console is supported.  */
  
  if (c == '\n')
    //grub_putchar ('\r');	/* recursive, bad!! */
    console_putchar ('\r');
  console_putchar (c);
  
#else /* ! STAGE1_5 */
  
  if (c == '\t' && current_term->getxy)
    {
      c = 8 - ((current_term->getxy () >> 8) & 3);
      while (c--)
	//grub_putchar (' ');	/* recursive, bad!! */
	current_term->putchar (' ');
      return;
    }

  if (c == '\n')
    {
      current_term->putchar ('\r');
      
      /* Internal `more'-like feature.  */
      if (count_lines >= 0)
	{
	  count_lines++;
	  if (count_lines >= max_lines - 2)
	    {
	      /* It's important to disable the feature temporarily, because
		 the following grub_printf call will print newlines.  */
	      count_lines = -1;

	      //grub_printf("\n");	/* recursive, bad!! */
	      current_term->putchar ('\n');
	      
	      if (! (current_term->flags & TERM_DUMB))
	      {
		if (current_term->setcolorstate)
		  current_term->setcolorstate (COLOR_STATE_HIGHLIGHT);
	      
		//grub_printf ("[Hit return to continue]");	/* recursive, bad!! */
		c = (int)"[Hit Q to quit, any other key to continue]";
		while (*(char *)c)
		  current_term->putchar (*(char *)c++);

		if ((getkey () & 0xDF) == 0x51)	/* 0x51 == 'Q' */
			quit_print = 1;
//		do
//		{
//		  tmp = ASCII_CHAR (getkey ());
//		  if ((tmp & 0xdf) == 0x51)	/* Q */
//		  {
//			quit_print = 1;
//			break;
//		  }
//		}
//		while (tmp != '\n' && tmp != '\r');

		//grub_printf ("\r                                          \r");	/* recursive, bad!! */
		c = (int)"\r                                          \r";
		while (*(char *)c)
		  current_term->putchar (*(char *)c++);
	      
		if (current_term->setcolorstate)
		  current_term->setcolorstate (COLOR_STATE_NORMAL);
	      }
	      
	      /* Restart to count lines.  */
	      count_lines = 0;
	      return;
	    }
	}
    }

//  if (! (current_term->flags & TERM_DUMB))
//  while (checkkey () != -1)
//  {
//	if ((getkey () & 0xdf) == 'Q')
//	{
//		quit_print = 1;
//		break;
//	}
//  }
  
  current_term->putchar (c);
  
#endif /* ! STAGE1_5 */
}

#ifndef STAGE1_5
void
gotoxy (int x, int y)
{
  current_term->gotoxy (x, y);
}

int
getxy (void)
{
  return current_term->getxy ();
}

void
cls (void)
{
  /* If the terminal is dumb, there is no way to clean the terminal.  */
  if (current_term->flags & TERM_DUMB)
    grub_putchar ('\n');
  else
    current_term->cls ();
}

int
setcursor (int on)
{
  if (current_term->setcursor)
    return current_term->setcursor (on);

  return 1;
}
#endif /* ! STAGE1_5 */

int
substring (const char *s1, const char *s2, int case_insensitive)
{
  char ch1, ch2;
  
  for (;;)
    {
      ch1 = *(s1++);
      ch2 = *(s2++);
      
      if (case_insensitive)
      {
	ch1 = tolower(ch1);
	ch2 = tolower(ch2);
      }

      if (! ch1)	/* S1 is a substring of S2, or they match exactly */
	return ch2 ? -1 : 0;
      
      if (ch1 != ch2)
	return 1;	/* S1 isn't a substring of S2 */
    }
}

#ifndef STAGE1_5
/* Terminate the string STR with NUL.  */
int
nul_terminate (char *str)
{
  int ch;
  
//  while (*str && ! grub_isspace (*str))
//    str++;

  while ((ch = *str) && ! grub_isspace (ch))
  {
	if (ch == '\\')
	{
		str++;
		if (! (ch = *str))
			break;
	}
	str++;
  }

//  ch = *str;
  *str = 0;
  return ch;
}

char *
grub_strstr (const char *s1, const char *s2)
{
  while (*s1)
    {
      const char *ptr, *tmp;

      ptr = s1;
      tmp = s2;

      while (*tmp && *ptr == *tmp)
	ptr++, tmp++;
      
      if (tmp > s2 && ! *tmp)
	return (char *) s1;

      s1++;
    }

  return 0;
}
#endif /* ! STAGE1_5 */

//#if !defined(STAGE1_5) || defined(FSYS_NTFS)
int
grub_strlen (const char *str)
{
  int len = 0;

  while (*str++)
    len++;

  return len;
}
//#endif /* ! STAGE1_5 || FSYS_NTFS */

int
memcheck (unsigned long addr, unsigned long len)
{
#ifdef GRUB_UTIL
#if 0
  auto unsigned long start_addr (void);
  auto unsigned long end_addr (void);
  
  auto unsigned long start_addr (void)
    {
      unsigned long ret;
# if defined(HAVE_START_SYMBOL)
      asm volatile ("movl	$start, %0" : "=a" (ret));
# elif defined(HAVE_USCORE_START_SYMBOL)
      asm volatile ("movl	$_start, %0" : "=a" (ret));
# endif
      return ret;
    }

  auto unsigned long end_addr (void)
    {
      unsigned long ret;
# if defined(HAVE_END_SYMBOL)
      asm volatile ("movl	$end, %0" : "=a" (ret));
# elif defined(HAVE_USCORE_END_SYMBOL)
      asm volatile ("movl	$_end, %0" : "=a" (ret));
# endif
      return ret;
    }

  errnum = 0;
//  if (/*! addr ||*/ (start_addr () <= addr && end_addr () > addr + len))
//  if (! addr || (start_addr () <= addr && addr < end_addr ()) || (start_addr () < addr + len && addr + len <= end_addr ()))
//    errnum = ERR_WONT_FIT;

//  return ! errnum;
  if (! addr)
  {
	errnum = ERR_WONT_FIT;
	return ! errnum;
  }
  if ((start_addr () <= addr && addr < end_addr ()) || (start_addr () < addr + len && addr + len <= end_addr ()))
	return ! errnum;

#endif
#endif /* GRUB_UTIL */

  errnum = 0;
  if (! addr /* (addr < (unsigned long)(RAW_ADDR (0x1000))) */
      /* || (addr < (unsigned long)(RAW_ADDR (0x100000))
	  && (unsigned long)(RAW_ADDR (saved_mem_lower * 1024)) < (addr + len)) */
      || (addr >= (unsigned long)(RAW_ADDR (0x100000))
	  && (unsigned long)(RAW_ADDR (saved_mem_upper * 1024)) < ((addr - 0x100000) + len)))
    errnum = ERR_WONT_FIT;

  return ! errnum;
}

#if 0
void
grub_memcpy(void *dest, const void *src, int len)
{
  int i;
  register char *d = (char*)dest, *s = (char*)src;

  for (i = 0; i < len; i++)
    d[i] = s[i];
}
#endif

/* struct copy needs the memcpy function */
/* #undef memcpy */
#if 1
void * grub_memcpy(void * to, const void * from, unsigned int n)
{
       /* This assembly code is stolen from
	* linux-2.4.22/include/asm-i386/string.h
	* It assumes ds=es=data space, this should be normal.
	*/
	int d0, d1, d2;
	__asm__ __volatile__(
		"rep ; movsl\n\t"
		"testb $2,%b4\n\t"
		"je 1f\n\t"
		"movsw\n"
		"1:\ttestb $1,%b4\n\t"
		"je 2f\n\t"
		"movsb\n"
		"2:"
		: "=&c" (d0), "=&D" (d1), "=&S" (d2)
		:"0" (n/4), "q" (n),"1" ((long) to),"2" ((long) from)
		: "memory");
	return to;
}
#else
/* just in case the assembly version of grub_memcpy does not work. */
void * grub_memcpy(void * to, const void * from, unsigned int n)
{
	char *d = (char *)to, *s = (char *)from;

	while (n--)
		*d++ = *s++;

	return to;
}
#endif

void *
grub_memmove (void *to, const void *from, int len)
{
   if (memcheck ((int) to, len))
     {
       /* This assembly code is stolen from
	  linux-2.2.2/include/asm-i386/string.h. This is not very fast
	  but compact.  */
       int d0, d1, d2;

       if (to < from)
	 {
	   asm volatile ("cld\n\t"
			 "rep\n\t"
			 "movsb"
			 : "=&c" (d0), "=&S" (d1), "=&D" (d2)
			 : "0" (len),"1" (from),"2" (to)
			 : "memory");
	 }
       else
	 {
	   asm volatile ("std\n\t"
			 "rep\n\t"
			 "movsb\n\t"
			 "cld"
			 : "=&c" (d0), "=&S" (d1), "=&D" (d2)
			 : "0" (len),
			 "1" (len - 1 + (const char *) from),
			 "2" (len - 1 + (char *) to)
			 : "memory");
	 }
     }

   return errnum ? NULL : to;
}

void *
grub_memset (void *start, int c, int len)
{
  char *p = start;

  if (memcheck ((int) start, len))
    {
      while (len -- > 0)
	*p ++ = c;
    }

  return errnum ? NULL : start;
}

#ifndef STAGE1_5
char *
grub_strcpy (char *dest, const char *src)
{
  grub_memmove (dest, src, grub_strlen (src) + 1);
  return dest;
}
#endif /* ! STAGE1_5 */

#ifndef GRUB_UTIL
# undef memcpy
/* GCC emits references to memcpy() for struct copies etc.  */
void *memcpy (void *dest, const void *src, int n)  __attribute__ ((alias ("grub_memmove")));
#endif

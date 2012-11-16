OBJEXT=.obj
EXEEXT=.exe

TARGDIR=.
OBJDIR=.
TESTDIR=.

LIBPATH=\lib
INCDIR=\include
RM=del /Q

#CC=gcc
LIBS=ws2_32.lib $(LIBPATH)\pthreadVC.lib sqlite.lib
COFLAGS=/Od /Ge /GZ
CWFLAGS=
CIFLAGS=-I. -I$(INCDIR)
CMFLAGS=
DBGFLAG=
#DBGFLAG=-DDEBUG
LFLAGS=/MT
CFLAGS= $(CWFLAGS) $(COFLAGS) $(CIFLAGS) $(CMFLAGS) -D__WIN32__ $(DBGFLAG) -DWIN32 $(LFLAGS)

OBJS=$(OBJDIR)\exp1$(OBJEXT) $(OBJDIR)\sqext$(OBJEXT)

all: $(TARGDIR)\exp1$(EXEEXT)

clean:
	$(RM) $(OBJS) $(TARGDIR)\exp1$(EXEEXT)
.c.obj:
	$(CC) $(CFLAGS) -c /Fo$@ $(*B).c

$(TARGDIR)/exp1$(EXEEXT): $(OBJS)
      $(CC) $(CFLAGS) -o $(TARGDIR)\exp1 $(OBJS) $(LIBS)



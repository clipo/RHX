
The MSL application uses a C interpreter originally known as CEL (C
Extension Language).  CEL is not ANSI standard C, and it is not C++.

The other Msl*.txt files in the samples directory enumerate the
available built in functions for serial and file I/O, use of timers,
user interface tools and C runtime library functions.

See the file MSLEXT.TXT in the bin directory for instructions on how
to add your own DLL functions to MSL.

Before adding your own script based functions to a WinPREP test, you
should review the following.  In spite of CEL's limitations, it is possible
to do substantial work from a script.


Avoid These
Keywords!       Comments
------------------------------------------------------------------------------
enum            Not supported.

extern          Not supported.

float           Use double instead.

do...while()    Not working (use while() instead)

void            Not working (functions should return int instead of void)

static          Not supported.

any #...        Not supported (i.e. #include, #define, #if, etc.) See note
                7 below.


Misc Keyword
Notes           Comments
------------------------------------------------------------------------------
for             Cannot use comma operator e.g. for (a = 0 , i = 0;...);
                a "forever" loop cannot be constructed using 
                for (;;) - conditional part of "for" assumed
                to be present although flagging isn't done if it isn't

goto            Generally ok but unreliable within loop statements
                (e.g. may exit loop prematurely or cause additional iteration)

unsigned        unsigned short , unsigned -ok
                unsigned char behaves as if it is an unsigned int;
                unsigned long acts like unsigned short also in incremental
                expressions not for direct assignments.

+=              Works fine when both sides have same data type
-=              Works fine when both sides have same data type
*=              Works fine when both sides have same data type
/=              Works fine when both sides have same data type
%=              Works fine when both sides have same data type
>>=             Works fine when both sides have same data type
<<=             Works fine when both sides have same data type
&=              Works fine when both sides have same data type
|=              Works fine when both sides have same data type
^=              Works fine when both sides have same data type

&               Ok - pointers to pointers not handled completely
                     e.g double *dptr;
                         double **dpptr;
                         dpptr = &dptr;
                     gives "Pointer type mismatch for assignment 
                     operator." even though it is reasonable

constants       Hex (0x) and octal(prefacing 0) constant notation ok.
                Character constants in octal and hex DO NOT work
                (e.g. '\0101'). Note character constant initialization
                ( e.g. char a = '*';) works ok

conditional ?:  Ok.  But the condition expression needs to be put into a
                pair of parentheses.



Additional Notes
------------------------------------------------------------------------------

1) Does NOT handle bracket notation "[]" as an alias of "*"
     e.g. "char arr_a[]" is NOT supported,  but "char *arr_a" is

2) A maximum of 144 bytes of information may be passed to a script function.
   This means 18 doubles, 36 pointer,longs,floats, or 72 integers,characters.
   Of course you can mix variable types as long as the total number of
   bytes that are passed to a function are less than 144.

3) Does not handle '\0' as a character (assumes its octal)--use 0 instead.
   For example:
        x[3]='\0';  // does not work
        x[3]=0;     // this is OK

4) Does not always handle typedef w/in another typedef.


5) Do not include script based typedefs in the argument list of a script
   function.  Instead, pass structure pointers as char*, then load the
   char* into a structure pointer.  e.g.

   int Uf_MyProc(     // 0=Normal; 3=Abort
       char*  pPCX )  // Address of procedure context information
   {
        int nRet = 0;                       // Load return value into nRet
        MP2_PROC_CONTEXT_DEF* pPC = pPCX;   // Cast pPCX into local procedure context ptr

        ...

        return nRet;
   }

   This is not a limitation for built in MSL functions or DLL functions.

  
6) The return value of a script function should be int or double.  Do not
   attempt to return a pointer as the value of a function.
   However, built in MSL functions and DLL functions may return pointers.

7) Multiple script files may be combined into a single script by using a
   project file (.PRO).  When the WinPREP application constructs a script,
   it places the names of all the individual script files in a project
   file and passes that project file to MSL.

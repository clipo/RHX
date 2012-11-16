/******************************************************************************
*
*   MultiPROBE II WinPREP Standard Include Script
*   ---------------------------------------------
*
*   Contains the structure definitions and utility functions
*   that are required by WinPREP generated scripts.
*
*   MultiPROBE and WinPREP are trademarks of Packard Instrument Company.
*
******************************************************************************/


/******************************************************************************
*
*   Structure definitions
*
******************************************************************************/

//----------------------------------------------------------
//  Runtime File Datatype
//----------------------------------------------------------

typedef struct _MP2_RTFILE_DEF {
	
	char  szPath[260];    // Path to file
	char* pszRtVar;       // Address of script variable (if any) from which
	//  the path should be copied.
	char  szRtFunct[64];// Name of the script function (if any) to calculate
	//  the value of the script variable.
	
	int    nType;         // File type (0=Column, 1=Keyword)
	int    nDelimiter;    // Column delimiter character
	int    nOffset;       // Records to skip from top of file
	
	int    nRecords;      // Records in file (column based only).
	int    nFields;       // Max fields in file (column based only).
	
} MP2_RTFILE_DEF;


//----------------------------------------------------------
//  Well Map Definitions
//----------------------------------------------------------

//#define MP2_MAX_REF_MAPS    16
//#define EOM_ACTION_STOP         0
//#define EOM_ACTION_WRAP         1
//#define EOM_ACTION_ASSEMCHANGE  2

typedef struct _MP2_WELLMAP_DEF {
	
	int nType;                // 0=Master, 1=Match to
	//    Type 1 does not have its own file
	int nDtType;      // Disposable tip type
	//    0=Non Dt Map; 1=GetTip Map; 2=DropTip Map
	
	MP2_RTFILE_DEF* pFile;  // File containing well map (if any)
	MP2_RTFILE_DEF* pVector;// File containing a vector table (i.e. to lookup the well map record)
	int     nColVector;       // Column number of the vector value
	int     bVectorOneBased;  // Non-Zero if the vector value is 1 based (not zero based)
	
	int     nRefMaps;         // Number of referenced maps
	int     nRefIndx;         // Reference list index
	char *pRefMaps[16];       // List of referenced maps
	int     nRefRecs[16];     // List of records where the match
	//    to map left off in each reference map
	int     nRefPass[16];     // Counts number of passes through each
	//    reference map
	
	int nColRack;     // Column number of rack name (zero based)
	int nColPos;      // Column number of well position in rack (zero based)
	int nRecords;     // Number of records in file.
	int nPasses;      // Number of passes through map
	int nCurRec;      // Current record number
	int nMaxRec;      // Max record number reached so far
	int nOffset;      // Start record offset
	int nIncrement;           // Map record increment
	int nActionAtEnd;         // Action to take when the end of the map
	//    has file has been reached.
	//    (0=EndTest; 1=WrapAround; 2=AssemblyChange)
	int nUseCount;            // Map use count (reset by call to MSL_IncNextMapPos()).
	int bAssemChngReq;        // Non-Zero if an assemble change should be performed
	
	char *pAltMap;            // Alternate (optimized) well map pointer
	//    NULL by default; created by MSL_CreateOptimizedWellMap()
	char *pFunct;     // Ptr to function used to create the alternate map
	char *pPC;                // Procedure that created the alternate map
	int    nTargets;          // Number of targets used to create the alternate map
	int    nDspPerAsp;        // Dispenses/Aspirate used to create the alternate map
	
	char *pAssocMap;          // Associated well map.  Set (for example) in get tip well maps
	// to point to the corresponding drop tip map.
	// NULL by default
	int bOverlapsAssocMap;  // Flag to indicate if there is any overlap between this
	//    map and the associated map.
	
	char *fp;                 // File pointer (NULL unless referencing a disposable tip file)
	
} MP2_WELLMAP_DEF;


//----------------------------------------------------------
//  Struct Definitions Normally Provided By time.h
//----------------------------------------------------------

struct tm
{
	int tm_sec;       // seconds after the minute - [0,59]
	int tm_min;       // minutes after the hour - [0,59]
	int tm_hour;    // hours since midnight - [0,23]
	int tm_mday;    // day of the month - [1,31]
	int tm_mon;       // months since January - [0,11]
	int tm_year;    // years since 1900
	int tm_wday;    // days since Sunday - [0,6]
	int tm_yday;    // days since January 1 - [0,365]
	int tm_isdst;   // daylight savings time flag
};


//----------------------------------------------------------
//  Types Normally Provided By Types.h
//----------------------------------------------------------

typedef long time_t;
typedef long BOOL;
typedef long _dev_t;                    /* device code */
typedef unsigned long _ino_t;           /* i-node number (not used on DOS) */
typedef long _off_t;                    /* file offset value */


//----------------------------------------------------------
//  Struct Definitions Normally Provided By Stat.h
//----------------------------------------------------------

struct _stat {
	_dev_t st_dev;
	_ino_t st_ino;
	unsigned short st_mode;
	short st_nlink;
	short st_uid;
	short st_gid;
	_dev_t st_rdev;
	_off_t st_size;
	time_t st_atime;
	time_t st_mtime;
	time_t st_ctime;
};


//----------------------------------------------------------
//  Date/Time Struct Definitions
//----------------------------------------------------------

typedef struct _MP2_DATE {
	
	int nYear;        // Year
	int nMonth;       // Month of year (1-12)
	int nDay;         // Day of month (1-31)
	
} MP2_DATE;


typedef struct _MP2_TIME {
	
	BOOL bPeriod;   // TRUE if time period rather than time
	//    of day.
	int nDays;        // Days in period
	int nHours;       // Hour in period
	int nMinutes;   // Minutes in period
	int nSeconds;   // Seconds in period
	
	int nHour;        // Hour of day (0-23)
	int nMinute;    // Minute of hour (0-59)
	int nSecond;    // Second of minute (0-59)
	
} MP2_TIME;



//----------------------------------------------------------
//  Wellmap reference (used by the procedure context)
//----------------------------------------------------------

//#define MAPFLG_INC_PER_SAMPLE       1
//#define MAPFLG_RESET_AT_STARTOFPROC 2

typedef struct _MP2_WELLMAP_REF {
	
	MP2_WELLMAP_DEF* pMap;  // Well-map structure pointer
	int iOperation;           // EGS operation associated with this reference.
	int iMapFlags;            // Map modification flags (see MAPFLG_...)
	
} MP2_WELLMAP_REF;


//----------------------------------------------------------
//  Procedure Context Definitions
//----------------------------------------------------------

typedef struct _MP2_PROC_CONTEXT_DEF {
	
	//-----------------------------------------------------------
	// The following elements are reserved for the procedure.
	// Although they may be modified by a user function, it is
	// generally not recommended.
	// The term dilutor is used below to refer to the combination
	// of Syringe Pump + Tubing + TipAdapter.
	//-----------------------------------------------------------
	char szName[64];          // Name of procedure
	char *pParentPC;          // Address of parent procedure context
	//    data.  NULL if this is not a child
	//    procedure.
	int    nProcId;           // Database record id
	int    nProcIndex;        // Procedure index in test tree
	
	int    nSampOffset;       // Start sample offset
	int    nDestOffset;       // Start destination offset
	int    nSamples;          // Number of samples to process
	int    nProcLoop;         // Procedure main loop counter
	int    nProcLimit;        // Procedure main loop limit
	int    nProcRepl;         // Outer replicate loop counter (if any)
	
	int    nSeqCnt;           // Dilutor sequence counter
	char szDilInUse[32];    // Use list of all dilutors
	//    (i.e. if 4 available: "Y-Y-Y-Y" )
	int    nDilInUse;         // Number of dilutors in use
	int    hDilutor;          // Current dilutor in use
	
	int    hPrfFile;          // Handle to procedure's performance file
	//    for use with the PrfFile...() functions
	
	// List of well-maps used in this procedure
	int    nMapsAlloc;        // Total list space available
	int    nMapsInUse;        // Number of maps in use
	int    nSampleMap;        // Index to the sample source map
	MP2_WELLMAP_REF* pMapRefs;    // NULL if no maps assoc with the procedure.
	
	//-----------------------------------------------------------
	// The following elements are reserved for user function
	// modification.
	//-----------------------------------------------------------
	int    nUserInt;         // Available int
	char *pUserPtr;          // Available pointer
	
} MP2_PROC_CONTEXT_DEF;


//----------------------------------------------------------
//  Time Marker Definition
//----------------------------------------------------------

typedef struct _MP2_TIME_MARKER {
	
	char* pPrvMarker;         // Ptr to previous marker (NULL if first marker)
	char* pNxtMarker;         // Ptr to next marker (NULL if last marker)
	
	char szName[256];         // Name of time marker
	
	// Absolute time members (i.e. lMrkTime, lExpTime) are in
	// units of seconds passed 00:00:00 January 1, 1970.
	long lMrkTime;            // Absolute time the marker was created or
	//    last updated.
	
	// The following members will be zero if a wait is not
	// in progress,
	long   lExpTime;          // Absolute time the wait period will expire.
	double dExpTime;          // Full wait period in seconds (static; calculated
	//    once and then used to compute % complete)
	double dRemTime;          // Remaining seconds in the wait period.
	
	// User modifiable member
	long   lParam;
	
} MP2_TIME_MARKER;




//----------------------------------------------------------
//  Liquid Operation Definition
//----------------------------------------------------------

//#define EGS_PRECALLBACK             1
//#define EGS_POSTCALLBACK            2
//#define EGS_ONLIQUIDERRORCALLBACK   3
//#define EGS_ONCLOTERRORCALLBACK     4

// Possible iEGS_DumpTable modes
//#define EGS_DUMP_NONE       0
//#define EGS_DUMP_TABLE      1
//#define EGS_DUMP_RUNLIST    2
//#define EGS_DUMP_ALL        3

//#define EGS_NOOP            '\0'    // A no operation step which may run in
//  parallel with other steps.
//#define EGS_NEWSEQ          'N'     // The start of a new sequence of steps
//#define EGS_ASP             'A'     // Aspirate liquid
//#define EGS_ASPAIR          'B'     // Aspirate air
//#define EGS_ASPSYSTEMLIQ    'S'     // Aspirate system liquid
//#define EGS_DSP             'D'     // Dispense liquid (with or without air)
//#define EGS_MIX             'M'     // Aspirate/Dispense liquid
//#define EGS_GETTIP          'G'     // Get a disposable tip
//#define EGS_DROPTIP         'R'     // Drop a disposable tip
//#define EGS_WASH            'W'     // Empty and wash dilutor
//#define EGS_WASTE           'E'     // Empty dilutor
//#define EGS_PERIWASH        'P'     // Empty dilutor and wash with the peri pump.
//#define EGS_FINDLIQUID      'L'     // Detect "Liquid" Level
//#define EGS_MOVETO          'V'     // Move to target
//#define EGS_TALON_GET       'H'     // Talon get plate
//#define EGS_TALON_PUT       'I'     // Talon put plate
//#define EGS_NLASP           'X'     // nL Aspirate liquid
//#define EGS_NLDSP           'Y'     // nL Dispense liquid
//#define EGS_NLWASH          'Z'     // nL Wash (peri + syringe)

//Move To Target Final Tip Height Options
//#define MOVETO_SAFE_TRAVEL                  0
//#define MOVETO_SEARCH_HEIGHT                1
//#define MOVETO_TOP_OF_WELL                  2
//#define MOVETO_DISPENSE_HEIGHT              3
//#define MOVETO_ASPIRATE_HEIGHT              4
//#define MOVETO_BOTTOM_OF_WELL               5

// Talon Move Types
//#define TALON_MOVE_POSITION                 1   // by static position
//#define TALON_MOVE_NAMED                    2   // mapped from drag-n-drop 
//#define TALON_MOVE_LABWARE                  3   // by labware offsets ("virtual labware" not on the deck GUI) 
//#define TALON_MOVE_MANIFOLD                 4   // by manifold component


typedef struct liquid_operation {           // standard liquid handling operation
	int       iDone;                  // set means do NOT process 
	
	int       iOption;
	char    szRackname[64];
	int       iPosition;
	int       hDilutor;               // dilutor handle
	char    *pPos;                    // Rack position (loaded just before step execution)
	
	double  dVolume;                  // requested volume
	double  dVolumeFound;     // volume found by liquid sensor
	double  dHeightFound;     // Height at which liquid found by sensor
	//    (relative to the bottom of the well).
	double  dPreAirVolume;
	double  dPostAirVolume;
	
	double  dPrewetVolume;
	double  dPrewetBlowoutVolume;
	double  dSpitVolume;
	double  dWasteVolume;
	int       iBlowoutDelay;          // blowout delay in ms
	
	int       iAspOption;    
	double  dAspHeight;                   
	double  dAspSpeed;                // aspirate (pump) speed in ul/sec
	double  dAspAirSpeed;     // aspirate air (pump) speed in ul/sec
	double  dAspSubmergeDepth;        // submerge depth below liquid in mm
	double  dAspRamp;                   // (negative depth = above liquid)
	double  dAspAirRamp;
	double  dAspZMoveSpeed;           // default Z speed when aspirating
	double  dAspZMoveRamp;
	int       iAspPreDelay;           // pre-aspirate delay in ms
	int       iAspPostDelay;          // post-aspirate delay in ms
	int       iAspType;               // aspirate type:  ASP_TYPE_LIQUID,
	// ASP_TYPE_AIR, ASP_TYPE_SYSTEM_LIQUID
	double  dAspTrackingRate;         // tracking rate (% of pump speed)
	
	int       iDspOption;
	double  dDspHeight;
	double  dDspSpeed;                // dispense (pump) speed in ul/sec
	double  dDspSubmergeDepth;        // submerge depth below liquid in mm
	double  dDspRamp;                   // (negative depth = above liquid)
	double  dDspZMoveSpeed;           // default Z speed when dispensing
	double  dDspZMoveRamp;
	int       iDspPreDelay;           // pre-dispense delay in ms
	int       iDspPostDelay;          // post-dispense delay in ms
	int       iDspMode;               // total, liquid, liquid+blowout, blowout
	double  dDspTrackingRate;         // tracking rate (% of pump speed)
	
	double  dZTravelSpeed;            // speed from or to travel height
	double  dZTravelRamp;
	double  dScanInSpeed;     // speed from Z start to liquid
	double  dScanInRamp;
	double  dSubmergeSpeed;           // speed from liquid to submerge
	double  dSubmergeRamp;
	double  dRetractSpeed;            // speed from liquid to retract
	double  dRetractRamp;
	double  dScanOutSpeed;            // speed going to Z start, before post-air
	double  dScanOutRamp;
	double  dAttachSpeed;     // speed on DT pickup
	double  dAttachRamp;
	double  dDetachSpeed;     // speed on DT drop ("eject" speed)
	double  dDetachRamp;
	
	int       iDetectClot;            // YES or NO
	double  dRetractHeight;           // relative retract height above liquid:
	// - reset clot detect here
	// - can prewet & mix dsp here after asp
	double  dClotDetectHeight;        // relative clot detect check height
	double  dClotDspVolFactor;        // 0.0 - 1.0 factor to determine amount of
	//    aspirate to dispense.
	
	int       iClotErrorAction;       // Default action when a clot is detected
	int       iLiquidErrorAction;     // Default action when insufficient liquid
	//    is detected.
	
	int       iCycles;                // for mix or wash
	
	int       iGetSampleIdFromPosition;
	char    szSampleId[64];
	char    szLiquidType[64];
	int       iPipetteRule;
	int       iLLSSensitivity;        // Liq. Level Sense Sensitivity (LSBs 0-4095)
	//    or -1 if not in use
	
	char    szTipName[64];            // DT name
	double  dZTipOffset;      // DT Z offset from default tip
	
	double  dMotorCurrentMult;        // fraction of default motor current for
	// attaching and detaching DTs
	
	char    PreExecuteCallBack[64];
	char    PostExecuteCallBack[64];
	char    OnLiquidErrorCallBack[64];
	char    OnClotErrorCallBack[64];
	
	// Timer Parameters
	char    szSetTimeMarker[32];    // Name of timer to set after operation completes
	char    szWaitTimeMarker[32];   // Name of timer to wait for before operation starts
	int       iWaitSeconds;   // Time to wait (seconds) if a wait time marker was specified.
	
	// Move to target (EGS_MOVETO) operation options
	int       iMoveToFinalHeight; // Final Tip Height option (see MOVETO_...)
	int       iMoveToInitPump;    // TRUE if syringe pump should be initialized
	
	// Optional WinPREP step index, well map and procedure context information
	int iNodeIndex;                   // Index of this step in the outline
	int iIsReplicate;                 // 1 if replicate of another op in same sequence
	MP2_WELLMAP_DEF *pWellMap;
	MP2_PROC_CONTEXT_DEF *pPC;
	
	// Assembly change information.
	int iAssemblyChangeThisStep;    // Non-zero if an assembly change should be performed
	//    on this step's well map before the step is executed
	int iAssemblyChangeMapAlloc;    // Number of assembly change wellmap entries allocated.
	int iAssemblyChangeMapInUse;    // Number of assembly change wellmap entries in use.
	MP2_WELLMAP_DEF **ppMapList;    // List of well maps from other steps (if any)
	
	// Handle to associated performance file (-1 if not open)
	int hPrfFile;
	
	// The database id of any error that may have occurred while
	// executing this step
	int iErrorId;
	
	// general EGS flags
	int       iMask;
	
	// Minimum number of steps that must have been executed before
	// a step that was marked as EGS_EXEC_MODE_ONSKIPSAMPLE can be
	// executed.
	int       nMinStepsForExecModeOnSkip;
	char   *pMinStepAddress;
	
	// nL parameters
	int       iMaskNL;            // nl aspirate/dispense/wash mask
	double  dPressureNL;  // aspirate retract/dispense pressure value
	double  dDeltaPressureNL;     // change in pressure following a piezo dispense
	double  dPeriWashTimeNL;      // peripump wash time (sec)
	
	// Talon Move parameters          
	int       nMoveType;          // TALON_MOVE_x
	char    szDeckPosition[16]; // A3, B6, Off-Deck, etc
	char    szRotation[8];        // None, 90, 180, 270
	char    szRow[4];             // A-G
	char    szCol[4];             // 1-14
	char    szCategory[64];       // labware category or support
	char    szComponent[64];      // labware component or item
	char    szSpeed[64];  // speed profile for Put
	
} LIQUID_OPERATION;


//----------------------------------------------------------
//  Error Context Definition
//----------------------------------------------------------

// Possible error return codes

//#define ONERR_DEFAULT           0
//#define ONERR_OK                1
//#define ONERR_CANCEL            2
//#define ONERR_ABORT             3
//#define ONERR_RETRY             4
//#define ONERR_IGNORE            5
//#define ONERR_YES               6
//#define ONERR_NO                7
//#define ONERR_SKIPSAMPLE        8
//#define ONERR_GOTOZMAX          9
//#define ONERR_NEWTIPPOS         10
//#define ONERR_CONTINUE          11
//#define ONERR_STOPPROC          12
//#define ONERR_SKIPSTEP          13


typedef struct _MP2_ERR_CONTEXT {
	
	// The error code and text descrition
	int    nCode;
	char szText[256];
	
	// The number of possible return codes for this error and
	// a list of those codes (see the ONERR_... values defined above).
	int nReturnCodes;
	int nCodeList[10];
	
	// The number of dilutors (tips) affected by the error.
	// May be 0 to the number of dilutors available.
	int nDilutorsAffected;
	
	// The list of affected dilutors. If 2 dilutors are
	// affected, hDilutor[0] and hDilutor[1] will contain
	// the handles of the those affected dilutors.
	int hDilutorList[8];
	
	// The ID of error in the DB Error Table filled by MSL_Error
	int iErrorId;
	
} MP2_ERR_CONTEXT;


//----------------------------------------------------------
//  EGS Context Definition
//----------------------------------------------------------

typedef struct _MP2_EGS_CONTEXT {
	
	// The number of parallel EGS steps being executed.
	// May be 0 to the number of dilutors available.
	int nParallelSteps;
	
	// The operation being performed by each step (i.e. 'A' : aspirate,
	// 'D' : dispense, ' ' : NoOp. etc. )
	// An EGS step with a given operation may be executed only with
	// other steps that have the same operation.  The exception is
	// the NoOp.  A NoOp step may be executed in parallel with any
	// other step.  However, nOperation would not be NoOp unless all
	// the parallel steps were NoOps.
	int nOperation;
	
	// Array containing the pointer to each EGS step being executed
	// in parallel.
	LIQUID_OPERATION* pLiqOp[8];
	
} MP2_EGS_CONTEXT;



//----------------------------------------------------------
//  MSL External Function Argument Structure
//----------------------------------------------------------

//#define MSLEXT_MAX_ARGTYPES     4
//#define MSLEXT_ARGTYPE_INT      0
//#define MSLEXT_ARGTYPE_LONG     0
//#define MSLEXT_ARGTYPE_DOUBLE   1
//#define MSLEXT_ARGTYPE_TEXT     2
//#define MSLEXT_ARGTYPE_BOOL     3

typedef struct _MSLEXT_ARG_DEF {
	
	int    nSize;         // Size of this structure
	
	char szName[64];      // Argument Name
	char szDesc[256];     // Argument Description
	int    nType;         // Argument Type
	
	char szValue[256];    // Argument Value represented as a string.
	//  (use sprintf/sscanf etc. for int or doubles)
	
	double dMin;  // For numeric types, the value's lower limit
	double dMax;  // For numeric types, the value's upper limit
	
} MSLEXT_ARG_DEF;



/****************************************************************************
*                               COORD
****************************************************************************/
struct coordinate    
{
	double x;                 // X location in mm
	double y;                 // Y location in mm
	
};
typedef struct coordinate COORDINATE;    

/****************************************************************************
*                               MP_POSITION
****************************************************************************/
//#define POS_TYPE_LIQUID         1
//#define POS_TYPE_FLUSH          2
//#define POS_TYPE_WASH           4
//#define POS_TYPE_TIP            8
//#define POS_TYPE_TIPDROPONLY    16
//#define POS_TYPE_LABWARE        32
//#define POS_TYPE_ANY            -1

//#define POS_ATTR_CIRCULAR       1
//#define POS_ATTR_ROUNDBTM       2
//#define POS_ATTR_IDFRMBCR       4

struct position
{
	COORDINATE    Center;             // X-Y position in mm
	long  iType;              // position type mask (POS_TYPE_...)
	long  iAttr;              // position attribute mask (POS_ATTR_...)
	
	double        dLength;            // well length in mm
	double        dWidth;             // well width in mm
	double        dDiameter;          // well inside diameter in mm
	double        dTopOfWell;         // top of well in mm (MTK 5-19-97)
	
	double        dZStart;            // liquid scan in start height in mm
	
	double        dZDispenseHeight;   // Default dispense height also used as ZEnd for striper
	double        dZAspirateHeight;   // Default Aspirate height, also used as starting
	// point to track liquid (after asp, dsp operations)
	
	double        dCurrentAspirateHeight; /* The "liquid level" now, dropped or raised from
										  dZStartLiquidVolume(after asp, dsp operations).
	Do not put it in GUI */ 
	
	double        dZMax;              // Max Z location in mm
	
	int           iNumofTipsinWell;   // Used by trough rack added 3/29/96
	double        dVariSpan;
	
	char  szPositionLabel[16];// ie. A1,A2... used only for output to log file
	char  szSampleId[64];     // Sample id associated with the position
	
	int           iLocationId;        // location id in database (-1 = not logged)
	
};
typedef struct position MP_POSITION;


/****************************************************************************
*                               RACKUNIT
****************************************************************************/
struct rackunit
{
	int       RackUnitID;         // Unique ID used for generating rack info file
	int       RackUnitType;       // same as RACK iFunctionType
	
	char    szGridRowLabel[64]; // rack position on grid
	char    szGridColLabel[64]; // rack position on grid
	
	int       nGridRow;           // Grid row location 'A'=0
	int       nGridColumn;        // Grid column location '1'=0
	
	double  dXmin;                // rack frame dimension in mm
	double  dXmax;                // rack frame dimension in mm
	double  dYmin;                // rack frame dimension in mm
	double  dYmax;                // rack frame dimension in mm
	
	char    szTipName[64];        // used for tip attach detach only
	char    szSupportName[64];    // For plate only
	int       iSupportPosition;   // For plate only
	COORDINATE    stepptl[3];     // 3 positions in mm (used internally by GUI
	// to define rack)
	
	double  dZSafeTravel; // height for movements over rack in mm
	
	int       iNoOfRows;          // # of rows for all rackpositions
	int       iNoOfCols;          // # of columns for all rackpositions
	int       iNoOfPositions;     // total # number of positions in unit
	double  dDiameter;            // well inside diameter in mm
	double  dRotation;            // The rack rotation (in degrees)
	int       iPosTypes;          // OR of all position types (see POS_TYPE_...)
	
	int       iOpenCount;         // Number of times this rack was opened (assembly changed)
	BOOL    bReqRackId;           // Flag to request the rack id
	BOOL    bBarcodeProvidesId; // Flag to indicate whether barcode provides id
	int       iLabwareId;         // labware ID from database
	char    szRackId[64]; // rack identifier (eg, barcode label)
	char    szBarcodePosition[10]; // position of barcode on rack
	int       nResForReset;       // This entry used by the reset tip racks dialog.
};
typedef struct rackunit RACKUNIT;


/****************************************************************************
*                               RACK
****************************************************************************/
struct rack     /*multi-unit rack or "super rack" in general*/
{
	char    szRackComment[256];
	int       iFunctionType;          // rack type:
	// "Pipette rack-Rectangular"
	// "Pipette rack-Circular"
	// "Pipette rack-Custom"
	// "Plate-Landscape"
	// "Plate-Portrait"
	// "Plate Support-Landscape"
	// "Plate Support-Portrait"
	// "Tip Disposal"
	// "Tip Rack"
	// "Trough"
	
	int       iNoOfUnits;             // total # of units in rack (always 1 now)
	int       iTotalPositions;        // total # of positions in rack
	
	int       iPackardSupplied;       // 1 means Packard file, not to be modified
	
	char    filler[32];
	
};
typedef struct rack  RACK;



/****************************************************************************
*                            Barcode Reader
****************************************************************************/

//----------------------------------------------------------
//  Supported Barcode Symbology Masks
//----------------------------------------------------------

//#define BCR_SYM_CODE_39     0x00000001
//#define BCR_SYM_CODABAR     0x00000002
//#define BCR_SYM_I_2_OF_5    0x00000004
//#define BCR_SYM_UPC_EAN     0x00000008
//#define BCR_SYM_CODE_128    0x00000010
//#define BCR_SYM_ALL         0x0000001F
//#define BCR_SYM_OTHER       0x00001000


//----------------------------------------------------------
//  Barcode Reader Cassette Position Structure Definition
//----------------------------------------------------------

//#define BCR_POS_SCAN_REQUIRED   0x00000001
//#define BCR_POS_SCAN_NOW        0x00000002
//#define BCR_POS_SCAN_FAILED     0x00000004
//#define BCR_POS_SCAN_DUPLICATE  0x00000008
//#define BCR_POS_IN_SAMPLELIST   0x00000010
//#define BCR_POS_USER_SKIPPED    0x00000020

typedef struct _BCR_POS_DEF {
	
	int     nIndex;           // Index of this position in the cassette structure
	void *pCass;      // Pointer to cassette structure of which this position
	//    is a part.
	
	int     nScanCount;       // The number if times this position has been scanned.
	long  nScanFlags;         // Scan flags for this position. See BCR_POS_SCAN...
	
	int    nScanLen;          // Number of characters scanned.
	MP_POSITION *pRackPos;  // Pointer to the cassette rack position structure.
	//    The scanned text is stored in its 'szSampleId'
	//    member.
	
	// Note that "nDupCnt" and "pDupPos" are mutually exclusive.
	int    nDupCnt;           // The number of other positions which have a sample id
	//    that matches this position's sample id.  Those other
	//    positions are considered duplicates of this position.
	
	void *pDupPos;            // If this position is a duplicate of some previous position
	//    (that is, it has the same sample id) "pDupPos" is
	//    a pointer to that original position.
	
	int    nSampleListRefs;   // Number of sample lists that reference this position
	
	// When genenerating a scan order sample list...
	int    nRecOfCurSampleList;   // The record number (of the current sample list file)
	// that corresponds to this position.
	
} BCR_POS_DEF;



//----------------------------------------------------------
//  Barcode Reader Cassette Structure Definition
//----------------------------------------------------------

//#define MAX_CASSETTE_POSITIONS  16

typedef struct _BCR_CASSETTE_DEF {
	
	int     nIndex;           // Index of this cassette in the link list of
	// cassettes that were and/or will be scanned.
	char *pBCR;               // Pointer to the barcode scan context structure
	
	char *pPrevCass;          // Pointer to previous cassette in list (if any)
	char *pNextCass;          // Pointer to next cassette in list (if any)
	
	char *pRackNode;          // Pointer to the cassette rack node
	int     nLane;            // Lane number of this cassette
	
	int     nTotalPositions;  // Number of physical positions available in this cassette
	int     nScanPositions;   // Number of positions to actually scan
	
	// PosArray contains one entry for each physical tube position.  Each position
	// may be queried to see if it must be scanned.
	BCR_POS_DEF PosArray[16];
	
} BCR_CASSETTE_DEF;



//----------------------------------------------------------
//  Sample List Structure Definition
//----------------------------------------------------------

//#define BCR_PROCESS_ORDER_LIST  0
//#define BCR_PROCESS_ORDER_SCAN  1

typedef struct _BCR_SAMPLELIST_DEF {
	
	MP2_RTFILE_DEF *pOrgFile;     // Original Sample list runtime file definition
	
	int nSampleIdCol;             // Column of sample id in original sample list file
	int nProcessOrder;            // Indicates the order samples will be processed
	//  See BCR_PROCESS_ORDER_...
	
	// When this sample list is processed the following elements will
	// be initialized.
	int nTotalSamples;            // Number of samples (records) in sample list
	int nMissingSamples;  // Number samples w/o a corresponding tube.
	BCR_POS_DEF **ppPosArray;     // Array of position pointers (one for each sample
	//  list record). If the pointer for a given record
	//  is NULL, it indicates that a corresponding
	//  cassette position was not found (i.e. a Missing Tube).
	
	// Once all cassette positions corresponding to sample records have been
	// established, a wellmap based on the requested sample order will be
	// generated.  This wellmap file will contain an extra column that will
	// (for each record in the wellmap) indicate the corresponding record number
	// of the sample in the original sample list file.
	int nMapRecords;              // Number of records in the wellmap file
	MP2_RTFILE_DEF  MapFile;      // Wellmap file information
	
} BCR_SAMPLELIST_DEF;



//----------------------------------------------------------
// Generic Summary Structure Defintion
//
// All ..._SUMMARY_DEF structures MUST conform to the
// generic summary structure defined below.
//----------------------------------------------------------

typedef struct _BCR_ANY_SUMMARY_DEF {
	
	int nArraySize;
	void **ppPtrArray;
	
} BCR_ANY_SUMMARY_DEF;


//----------------------------------------------------------
//  Barcode Reader Position Summary Structure Definition
//
//  Used to deliver an array of locations where there was
//  a read error, a duplicate id, or where a sample id
//  was read which was not part of a sample list.
//----------------------------------------------------------

typedef struct _BCR_POS_SUMMARY_DEF {
	
	int nPositions;       // Number of questionable cassette positions
	
	// ppPosArray contains the address of an array of cassette
	// position structure pointers.  The length of the array
	// is specified in nPositions.
	BCR_POS_DEF **ppPosArray;
	
} BCR_POS_SUMMARY_DEF;



//----------------------------------------------------------
//  Barcode Reader Sample List Summary Structure Defintion
//
//  Used to deliver an array of sample lists that have
//  1 or more sample ids (records) with no matching cassette
//  position.
//----------------------------------------------------------

typedef struct _BCR_SAMPLELIST_SUMMARY_DEF {
	
	int nSampleLists;     // Number of sample lists
	
	// ppSmpArray contains the address of an array of
	// sample list structure pointers.    The length of the
	// array is specified in nSampleLists.
	BCR_SAMPLELIST_DEF **ppSmpArray;
	
} BCR_SAMPLELIST_SUMMARY_DEF;



//----------------------------------------------------------
//  Barcode Reader Error Structure Defintion
//----------------------------------------------------------

//#define BCR_MAX_ERRORS          4
//#define BCR_ERR_SCANFAILED      0
//#define BCR_ERR_DUPLICATEID     1
//#define BCR_ERR_MISSINGTUBES    2
//#define BCR_ERR_EXCESSTUBES     3

//#define BCR_ONERR_REPORT        0
//#define BCR_ONERR_IGNORE        1
//#define BCR_ONERR_ABORT         2
//#define BCR_ONERR_CALLBACK      3

typedef struct _BCR_ONERROR_DEF {
	
	int    nAction;                       // On error action
	char szCB[64];                        // User defined callback (if any)
	
	BCR_ANY_SUMMARY_DEF Summary;  // Summary if items associated with the error
	
} BCR_ONERROR_DEF;



//----------------------------------------------------------
//  Barcode Reader Context Structure Definition
//----------------------------------------------------------

typedef struct _BCR_CONTEXT_DEF {
	
	int hBCR;                             // Handle of this barcode context.
	
	MP2_PROC_CONTEXT_DEF* pPC;            // The context of the procedure that allocated
	//  this barcode reader context (if any)
	MP2_WELLMAP_DEF* pMap;                // The wellmap indicating which tubes are to
	//  be scanned.
	
	int    nMaximumTubes;                 // Maximum number of tubes to scan.  If zero,
	//  keep scanning until stop code or end of
	//  map is reached.
	int    nScannedTubes;                 // Number of tubes scanned so far.
	
	long nSymMask;                        // Bit mask of which symbologies to scan for.
	char szStopCode[64];          // The scan stop code (if any)
	BCR_POS_DEF *pPosOfStopCode;  // Points to the position where the stop
	//  code was encountered (NULL otherwise).
	
	int nCassettes;                       // Number of cassettes that have been scanned.
	BCR_CASSETTE_DEF *pCassList;  // Pointer to start of cassette link list
	BCR_CASSETTE_DEF *pLastCass;  // Pointer to last cassette in the list.
	int bAllCassettesLoaded;              // There are no more cassettes in the wellmap that
	//  have not yet been added to the barcode context.
	
	int bScanInProgress;          // TRUE if the scan thread is busy
	BCR_CASSETTE_DEF *pScanCass;  // The cassette that is being or has just been
	///   scanned (NULL otherwise)
	
	MP2_RTFILE_DEF *pScanFile;            // Scan file to generate when all scanning
	// is complete.
	
	int nSampleListsAllocated;            // Number of sample list pointers allocated.
	int nSampleListsInUse;                // Number of sample lists to process.  Zero if
	//  none to process.
	BCR_SAMPLELIST_DEF **ppSmpArray;      // Array of sample list pointers
	
	// Pre/Post Scan Cassette Callbacks...
	char szPreScanCB[64];
	char szPostScanCB[64];
	
	// Summary of cassette positions that were scanned.    Loaded by BCR_ProcessResults
	BCR_POS_SUMMARY_DEF ScanSummary;
	
	// Error handling...
	BCR_ONERROR_DEF OnErr[4];
	
	
} BCR_CONTEXT_DEF;






/******************************************************************************
*
*   SignalByFile
*
*   Demonstration function to signal some other program by creating
*   a signal file and waiting for a reply file.
*
******************************************************************************/

int SignalByFile(           // Returns length of reply text, -1 if failed.
				 
				 char* pszSignalFile,    // Name of signal file
				 char* pszSignalData,    // Text to be written to the signal file
				 char* pszReplyFile,        // Name of file to contain the reply.
				 char* pszReplyData,        // Contents of the first record of the reply
				 int      nMaxReplyLen,     // Max length of reply buffer
				 int      nReplyTimeout )   // Reply timeout (seconds). Set to 0 to wait
				 // indefinately.
{
	int i;                    // Retry counter
	int nLen = 0;     // Length of the reply text
	char* fpSignal;           // Signal file pointer
	char* fpReply;            // Reply file pointer
	char* NULL = 0;
	
	
	// If the reply file already exists, delete it!
	fpReply = fopen( pszReplyFile, "r" );
	if( fpReply != NULL )
	{
		fclose( fpReply );
		DeleteFile( pszReplyFile );
	}
	
	// Attempt to open the signal file and write the data.
	fpSignal = fopen( pszSignalFile, "w" );
	if( fpSignal == NULL ) return -1;
	fputs( pszSignalData, fpSignal );
	fclose( fpSignal );
	
	// Check for a reply once every half second
	for( i = 0; 1; i++ )
	{
		// Does the file exist?
		fpReply = fopen( pszReplyFile, "r" );
		if( fpReply != NULL )
		{
			// If so, read that first record.
			if( nMaxReplyLen > 0 )
			{
				fgets( pszReplyData, nMaxReplyLen, fpReply );
				
				// Make sure the reply is zero terminated
				pszReplyData[ nMaxReplyLen-1 ] = 0;
				nLen = strlen( pszReplyData );
			}
			fclose( fpReply );
			
			// Return the length of the reply
			return nLen;
		}
		
		// Otherwise, check for a timeout
		if( (nReplyTimeout > 0) && ((i/2) >= nReplyTimeout ) )
			break;
		
		// No timeout yet, sleep for a half second.
		Sleep( 500 );
	}
	
	// Timeout while waiting for the reply.
	return -1;
}



/******************************************************************************
*
*   IniLabwareDef()
*
*   Opens each rack/plate found in the caller specified file.  The file
*   MUST be comma delimited and have the following columns for each
*   record...
*
*   Column      Description
*   ------      -----------------------------------------------------------
*   1           The name of the rack/plate.  Must be unique for all
*               racks/plates to be on the deck.
*
*   2           The file containing the rack/plate definition
*
*   3           The Y grid location (zero based: 0 to  6; or -1 if a plate)
*
*   4           The X grid location (zero based: 0 to 23; or -1 if a plate)
*
*   5           The rack/plate rotation (i.e. 0, 90, 180 or 270)
*
*   6           The rack/plate id required flag.  If non-zero, an assembly
*               change will be triggered when the rack/plate is opened so
*               that the initial rack/plate id may be requested.
*
*   7           If a plate, The rack name of the support upon which the
*               plate is to be placed.
*
******************************************************************************/

int IniLabwareDef(
				  
				  char *pszFile )       // File containing labware list
				  
{
	double dRot;
	char szRack[256];
	char szPath[256];
	char szBarcodeDirection[256];
	char szTmp[256];
	char *pszTmp; 
	char szSupport[256];
	int    nGridX;
	int    nGridY;
	int    bReqRackId;
	int    bBarcodeProvidesId;    
	int    bOutsideRange;
	int    nLen;
	int    i;
	char *NULL = 0;
	MP2_RTFILE_DEF *pFile;
	
	// Allocate a runtime file definition
	pFile = calloc( 1, sizeof(MP2_RTFILE_DEF) );
	if( pFile == NULL ) return 0;
	MSL_IniRtFileDef( pFile, pszFile, 0, NULL, 0, ',', 1, sizeof(MP2_RTFILE_DEF) );
	
	// Keep looping until EOF reached.
	for( i = 0; 1; i++ )
	{
		// Get rack name and path
		strcpy( szRack, MSL_GetRtFileColData( pFile, i, 0, &nLen, &bOutsideRange ) );
		if( (nLen == 0) || bOutsideRange ) break;
		strcpy( szPath, MSL_GetRtFileColData( pFile, i, 1, &nLen, &bOutsideRange ) );
		if( (nLen == 0) || bOutsideRange ) break;
		
		// Get grid location
		nGridY = MSL_GetRtFileColInt( pFile, i, 2, -10 );
		if( nGridY == -10 ) break;
		nGridX = MSL_GetRtFileColInt( pFile, i, 3, -10 );
		if( nGridX == -10 ) break;
		
		// Get the rotation
		dRot = MSL_GetRtFileColDouble( pFile, i, 4, 0 );
		
		// Get the prompt for rack id flag
		bReqRackId = MSL_GetRtFileColInt( pFile, i, 5, 0 );
		
		// If the rack is already open, close it.
		if( MSL_RackCheckOpen( szRack ) == 0 )
			MSL_RackClose( szRack );
		
		// If the grid is non-negative, assume a free standing rack
		if( nGridX >= 0 )
		{
			// Get the barcode provides id flag and direction, if present in file
			pszTmp = MSL_GetRtFileColData(pFile, i, 6, &nLen, &bOutsideRange); 
			if(bOutsideRange || nLen == 0) 
			{
				bBarcodeProvidesId = 0;
				strcpy(szBarcodeDirection, "none");
			}
			else
			{
				if(*pszTmp == '1')
					bBarcodeProvidesId = 1;
				else
					bBarcodeProvidesId = 0;
				// Get the barcode direction
				strcpy( szBarcodeDirection, MSL_GetRtFileColData( pFile, i, 7, &nLen, &bOutsideRange ) );      
			}
			// Open the rack file
			if(bBarcodeProvidesId)
			{
				MSL_RackOpenEx( szRack, szPath, nGridY, nGridX, dRot, "unknown", bReqRackId );
				MSL_RackLoadIdOptions(szRack, bReqRackId, bBarcodeProvidesId, szBarcodeDirection);           
			}
			else
			{
				MSL_RackOpenEx( szRack, szPath, nGridY, nGridX, dRot, "", bReqRackId );
				MSL_RackLoadIdOptions(szRack, bReqRackId, bBarcodeProvidesId, szBarcodeDirection);
			}
		}
		
		// Otherwise, assume this is a plate...
		else
		{
			// Get the support.
			strcpy( szSupport, MSL_GetRtFileColData( pFile, i, 6, &nLen, NULL ) );
			if( nLen == 0 ) break;
			
			// Get the barcode provides id flag and direction, if present in file
			pszTmp = MSL_GetRtFileColData(pFile, i, 8, &nLen, &bOutsideRange); 
			if(bOutsideRange || nLen == 0) 
			{
				bBarcodeProvidesId = 0;
				strcpy(szBarcodeDirection, "none");
			}
			else
			{
				if(*pszTmp == '1')
					bBarcodeProvidesId = 1;
				else
					bBarcodeProvidesId = 0;
				// Get the barcode direction
				strcpy( szBarcodeDirection, MSL_GetRtFileColData( pFile, i, 9, &nLen, &bOutsideRange ) );      
			}
			// Open the rack file
			if(bBarcodeProvidesId)
			{
				// Load "unknown" identifier for all labware using secondary barcode reader.
				// This will force a read in MSL_RackSecondaryBarcodeReadAll().
				MSL_PlateOpenEx(szRack, szPath, szSupport, 0, dRot, "unknown", bReqRackId );
				MSL_RackLoadIdOptions(szRack, bReqRackId, bBarcodeProvidesId, szBarcodeDirection);           
			}
			else
			{
				MSL_PlateOpenEx(szRack, szPath, szSupport, 0, dRot, "", bReqRackId );
				MSL_RackLoadIdOptions(szRack, bReqRackId, bBarcodeProvidesId, szBarcodeDirection);           
			}
		}
	}
	
	// Free the runtime file definition
	free( pFile );
	
	return 0;
}
// End of WinPREP.S

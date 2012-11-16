/*****************************************************************
*                                                                *
*        MoveId.s   MSL Functions for Moving Id of a Moved       *
*                   Rack to the New Location                     *
*                                                                *
*****************************************************************/
  
int MOVEID_DEBUG  = 0;   // set to 1 to display communication strings
int MAX_RACK      = 32;  // max number of racks that can be put on deck
char *NULL        = 0;   // global null pointer
int nRecords      = 0;   // number of racks on rack layout
int TableBuilt    = 0;   // global flag of whether there is a table or not

// structure of records for the table which is used to record the 
// test's record information.

typedef struct _Record {
	char szRackName[128];
	char szRackFile[128];
	char szRackId[128];
	int nYLocation;
	int nXLocation;
	double dRotation;
} Record;

Record Table[32];

// Structure of imagined offdeck locations which represent options
// that can be used with multiprobe. Labwares can be moved between
// multiprobe and those options.

typedef struct _OffdeckLocation {
	char szLocationName[128];
	char szRackId[128];
} OffdeckLocation;

OffdeckLocation OdLTable[200];

// Structure of ondeck locations.

typedef struct _Location {
	int nYGrid;
	int nXGrid;
} Location; 

/*********************************************************************
*                                                                    *
*   Function:  MSL_ShowErrorDialog (char*, char*)                    *
*                                                                    *
*    Purpose:  To display a error message and wait for the user      *
*              to respond. There are two buttons, ignore and         *
*              abort.                                                *
*                                                                    *
*    Returns:  12 if user click ignore, 3 if user click abort        *
*                                                                    *
*********************************************************************/

int MSL_ShowErrorDialog (          // Abort or Ignore
		char* pszTitle,            // title for the dialogbox
		char* pszLabel)            // error message
{
	int iDialog;
	int iIgnoreBtn;
	int iAbortBtn;
	int iBtnList[2];
	int iBtn;

	iDialog = MSL_GetAvailableDialogId();

	MSL_CreateDialog( 0, iDialog, -1, -1, -1, -1, pszTitle, 0 );
	iIgnoreBtn = MSL_GetAvailableControlId(iDialog);
	iAbortBtn = MSL_GetAvailableControlId(iDialog)+1;
	iBtnList[0] = iIgnoreBtn;
	iBtnList[1] = iAbortBtn;

	MSL_CreatePushBtn( iDialog, iIgnoreBtn, 4, 6, 10, 1, "Ignore", "Ignore error and continue test", 0, 0, 0 );
	MSL_CreatePushBtn( iDialog, iAbortBtn, 18, 6, 10, 1, "Abort", "Abort test", 0, 0, 0 );
	MSL_CreateLabel( iDialog, 603, 1, 1, 30, 4, pszLabel, 0 );
	MSL_Beep( 500, 0.1 );
	MSL_ShowDialog( iDialog, 1, 0 );
	while( 1 )
	{
		MSL_SetControlFocus( iDialog, iIgnoreBtn );
		iBtn = MSL_WaitControlList( iDialog, iBtnList, 2, -1.0, 0 );
		
		if (iBtn == iIgnoreBtn)
		{
			MSL_DeleteDialog(iDialog, 0); 
			return 12;
		}
		else if (iBtn == iAbortBtn)
		{
			MSL_DeleteDialog(iDialog, 0); 
			return 3;
		}

	}
}

/****************************************************************************
*                                                                           *
*   Function:  MSL_ConvertDeckLocation( char*, Location* )                  *
*                                                                           *
*    Purpose:  Convert deck location from the format which user supply      *
*              (i.e., D5, C10) to the format which function can use         *
*                                                                           *
*    Returns:  0 if success                                                 *
*              3 if user gave an incorrect value and selected abort in      *
*              error dialog                                                 *
*              12 if user gave an incorrect value and selected ignore       *
*              in error dialog                                              *
*                                                                           *
****************************************************************************/

int MSL_ConvertDeckLocation (          // SUCCESS, Abort or Ignore
		char* ps,                  // deck location with user format
		Location* pLocation)       // deck location with program format
{
	int i;
	char tempYCoordinate;
	char tempXCoordinate[5];

	tempYCoordinate = ps[0]; 

	switch (tempYCoordinate) {
		case 'A': 
		case 'a':
			pLocation->nYGrid = 0;
			break;
		case 'B':
		case 'b':
			pLocation->nYGrid = 1;
			break;
		case 'C':
		case 'c':
			pLocation->nYGrid = 2;
			break;
		case 'D':
		case 'd':
			pLocation->nYGrid = 3;
			break;
		case 'E':
		case 'e':
			pLocation->nYGrid = 4;
			break;
		case 'F':
		case 'f':
			pLocation->nYGrid = 5;
			break;
		case 'G':
		case 'g':
			pLocation->nYGrid = 6;
			break;
		default:
			return MSL_ShowErrorDialog("Error", "Incorrect Y Grid Value or Format!");
	}

	for (i = 0; i<5; i++)
		tempXCoordinate[i] = ps[i+1];
	pLocation->nXGrid = atoi(tempXCoordinate) - 1;

	if (pLocation->nXGrid > 32 || pLocation < 0)
		return MSL_ShowErrorDialog("Error", "Incorrect X Grid Value or Format!");

	return 0;
}
		
/******************************************************************
*                                                                 *
*   Function:  MSL_BuildTable()                                   *
*                                                                 *
*    Purpose:  Build the table of test's layout information       *
*              using the dump file got from MSL_RackDumpLayout()  *
*                                                                 *
*    Returns:  0 if the table is built successfully, otherwise    *
*              return 3.                                          *
*                                                                 *
******************************************************************/

int MSL_BuildTable()          // SUCCESS or FAIL
{
	char     szFileNameofTable[128];
	RACKUNIT Unit; 
	int      i = 0;
	int      j = 0;
	char*    pFile;
	int      FoundSameLocation = 0;
	int      nLines = 0;
	int      nPlates;
	int      yCoordinate;
	int      xCoordinate;

	// Looking for a file name which does not exsit. This file
	// is a temporary file which will hold the layout infomation
	// of the test.

	sprintf(szFileNameofTable, "TempFile%03d.txt", i);
	pFile = fopen(szFileNameofTable, "r");

	while(pFile && i < 1000)
	{ 
		fclose(pFile);
		i++;
		sprintf(szFileNameofTable, "TempFile%03d.txt", i);
		pFile = fopen(szFileNameofTable, "r");
	}

	if ( i == 1000)
	{
		fclose(pFile);
		MSL_MessageDialog(0, "Build Table Error", "Too many TempFiles, please delete TempFile*.txt", 0, 1, 1, 0);
		return 3;
	}

	// Write the layout infomation to the temporary file.

	MSL_RackDumpLayout(szFileNameofTable);
	nLines = MSL_GetFileLines(szFileNameofTable, NULL) - 1;

	// Get name, id, Y location, X location of each rack location from 
	// the temporary file, and put them into the table.

	for(i = 0; i < nLines; i++) 
		if (strcmp("", MSL_GetFileString(szFileNameofTable, i+1, 6)))
		{
			strcpy(Table[j].szRackName, MSL_GetFileString(szFileNameofTable, i+1, 0));
			strcpy(Table[j].szRackFile, MSL_GetFileString(szFileNameofTable, i+1, 1));
			Table[j].nYLocation = MSL_GetFileLong(szFileNameofTable, i+1, 2);
			Table[j].nXLocation = MSL_GetFileLong(szFileNameofTable, i+1, 3);
			Table[j].dRotation = MSL_GetFileDouble(szFileNameofTable, i+1, 4);
			MSL_RackGetUnit(Table[j].szRackName, 1, &Unit, sizeof(Unit));
			strcpy(Table[j].szRackId, Unit.szRackId);
			j ++;
		}
	nPlates = j;
	nRecords = nPlates;
	
	for(i = 0; i < nLines; i ++)
	{
		j = -1;
		FoundSameLocation = 0;
		if ( !strcmp("", MSL_GetFileString(szFileNameofTable, i+1, 6)))
		{
			yCoordinate = MSL_GetFileLong(szFileNameofTable, i+1, 2);
			xCoordinate = MSL_GetFileLong(szFileNameofTable, i+1, 3);
			while ((++j) < nPlates && FoundSameLocation == 0)
			{
				if((yCoordinate == Table[j].nYLocation)
					&& (xCoordinate == Table[j].nXLocation))
					FoundSameLocation = 1;
			}
			if (FoundSameLocation == 0)
			{
				strcpy(Table[nRecords].szRackName, MSL_GetFileString(szFileNameofTable, i+1, 0));
				strcpy(Table[nRecords].szRackFile, MSL_GetFileString(szFileNameofTable, i+1, 1));
				Table[nRecords].nYLocation = MSL_GetFileLong(szFileNameofTable, i+1, 2);
				Table[nRecords].nXLocation = MSL_GetFileLong(szFileNameofTable, i+1, 3);
				Table[nRecords].dRotation = MSL_GetFileDouble(szFileNameofTable, i+1, 4);
				MSL_RackGetUnit(Table[nRecords].szRackName, 1, &Unit, sizeof(Unit));
				strcpy(Table[nRecords].szRackId, Unit.szRackId);
				nRecords ++;
			}
		}
	}
				
	if (MOVEID_DEBUG)
	{
		printf("\nThe layout table at the beginning of the test is:\n\n");
		printf("szRackname         szRackId          nYLocation    nXLocation\n");
		for(i=0; i < nRecords; i++) 
		{
			printf("   %s  ", Table[i].szRackName);
			MSL_RackGetUnit(Table[i].szRackName, 1, &Unit, sizeof(Unit));
			printf("   %s   ", Unit.szRackId);
			printf(" %d  %d  \n", Table[i].nYLocation, Table[i].nXLocation);
		}			
	}

	TableBuilt = 1;
	
	MSL_GetFileClose();		
	DeleteFile(szFileNameofTable);

	for (i=0; i< 100; i++)
	{
		strcpy(OdLTable[i].szLocationName, "");
		strcpy(OdLTable[i].szRackId, "");
	}

	return 0;
}

/******************************************************************
*                                                                 *
*   Function:  MSL_UpdateTable(char* SourceName, char* DestName)  *
*                                                                 *
*    Purpose:  Update the layout table after each rack movement   *
*                                                                 *
*    Returns:  0 if update successfully, 3 otherwise              *
*                                                                 *
******************************************************************/

int MSL_UpdateTable(         // FAIL or SUCCESS
		char * SourceName,   // rackname of old location
		char * DestName)     // rackname of new location
{
	char     MovedId[128];
	char     MovedRackFile[128];
	double   MovedRotation;
	int      i = -1;
	int      FoundSource = 0;
	int      FoundDest = 0;
	RACKUNIT Unit;

	// If there is no source name, the source is not on deck,
	// the source id has been set to RACKUNIT, so just get 
	// the id from it.

	if (strcmp(SourceName, "")) 
	{
		while(i < MAX_RACK && FoundSource == 0) 
		{
			i ++;
			if (!strcmp(SourceName, Table[i].szRackName)) 
			{
				strcpy(MovedId, Table[i].szRackId);
				strcpy(Table[i].szRackId, "");
				strcpy(MovedRackFile, Table[i].szRackFile);
				strcpy(Table[i].szRackFile, "");
				MovedRotation = Table[i].dRotation;
				Table[i].dRotation = 360;
				FoundSource = 1;
			}
		}
		if (i == MAX_RACK)
		{
			MSL_MessageDialog(0, "Update Table Error", "No rack on the get location", 0, 1, 1, 0);
			return 3;
		}
	}
	else 
	{
		MSL_RackGetUnit(DestName, 1, &Unit, sizeof(Unit));
		strcpy(MovedId, Unit.szRackId);
		i = -1;
		while(i < MAX_RACK && FoundDest == 0) 
		{
			i ++;
			if (Unit.nGridRow == Table[i].nYLocation && Unit.nGridColumn == Table[i].nXLocation)
				FoundDest = 1;
		}
		strcpy(MovedRackFile, Table[i].szRackFile);
		MovedRotation = Table[i].dRotation;
	}

	FoundDest = 0;
	i = -1;
	while(i < MAX_RACK && FoundDest == 0)
	{
		i ++;
		if (!strcmp(DestName, Table[i].szRackName))
		{
			strcpy(Table[i].szRackId, MovedId);
			strcpy(Table[i].szRackFile, MovedRackFile);
			Table[i].dRotation = MovedRotation;
			FoundDest = 1;
		}
	}
	if ( i == MAX_RACK )
	{
		MSL_MessageDialog(0, "Update Table Error", "No rack on the put location", 0, 1, 1, 0);
		return 3;
	}

	if (MOVEID_DEBUG)
	{
		printf("\nThe layout table after this labware movement is:\n\n");
		printf("szRackname      szRackId      nYLocation    nXLocation\n");
		for(i=0; i < nRecords; i++) 
		{
			printf("   %s  ", Table[i].szRackName);
			MSL_RackGetUnit(Table[i].szRackName, 1, &Unit, sizeof(Unit));
			printf("   %s   ", Unit.szRackId);
			printf(" %d  %d  \n", Table[i].nYLocation, Table[i].nXLocation);
		}
	}
	return 0;
}

/*****************************************************************
*                                                                *
*  Function:  MSL_UpdateMovedIdDest(char*, char*)                *
*                                                                *
*   Purpose:  Add the rack id of a new rack to its location on   *
*             layout, the location is defined by deck's Y, X     *
*             grid location, and also update the layout table    *
*                                                                *
*   Returns:  0 if success, 3 otherwise                          *
*                                                                *
*****************************************************************/

int MSL_UpdateMovedIdDest(      // FAIL or SUCCESS
		char* DLocation,        // destination's grid location
		char* szRackId)         // rackid of added rack
{
	int FoundDest = 0;
	int i = -1;
	int iDConversion;
	RACKUNIT Unit;
	Location Destination;

	iDConversion = MSL_ConvertDeckLocation(DLocation, &Destination);

	if (iDConversion != 0)
		return iDConversion;

	if (TableBuilt == 0) 
		MSL_BuildTable();

	while(!FoundDest && i < MAX_RACK) 
	{
		i++;
		if (Table[i].nYLocation == Destination.nYGrid && Table[i].nXLocation == Destination.nXGrid)
			FoundDest = 1;
	}

	if ( i == MAX_RACK )
		return MSL_ShowErrorDialog("Move Id Error", "Couldn't find the destination");

	if (MOVEID_DEBUG) 
	{
		MSL_RackGetUnit(Table[i].szRackName, 1, &Unit, sizeof(Unit));
		printf("\nThe rack id before moving is %s\n", Unit.szRackId);
	}

	MSL_RackLoadId(Table[i].szRackName, szRackId);

	MSL_UpdateTable("", Table[i].szRackName);

	// Reopen the rack in order to store the new id etc in the database

	MSL_RackOpenEx(Table[i].szRackName, Table[i].szRackFile, Table[i].nYLocation,
	Table[i].nXLocation, Table[i].dRotation, Table[i].szRackId, 0);

	if (MOVEID_DEBUG) 
	{
		MSL_RackGetUnit(Table[i].szRackName, 1, &Unit, sizeof(Unit));
		printf("\nThe rack id after moving is %s\n", Unit.szRackId);
	}

	return 0;
}

/*****************************************************************
*                                                                *
*  Function:  MSL_UpdateMovedIdLoc(char* , char* )               *
*                                                                *
*   Purpose:  Move the rack id of moved rack to the new location,*
*             the locations are defined by deck's Y, X grid      *
*             locations, and also update the layout table        *
*                                                                *
*   Returns:  0 if success, 3 otherwise                          *
*                                                                *
*****************************************************************/

int MSL_UpdateMovedIdLoc(      // FAIL or SUCCESS
		char* SLocation,       // old ondeck location 
		char* DLocation)       // new ondeck location
{
	int FoundSource = 0;
	int FoundDest = 0;
	int i = -1;
	int j = -1;
	int iSConversion;
	int iDConversion;
	RACKUNIT Unit;
	Location Source;
	Location Destination;

	iSConversion = MSL_ConvertDeckLocation(SLocation, &Source);
	iDConversion = MSL_ConvertDeckLocation(DLocation, &Destination);

	if ((iSConversion == 3) || (iDConversion == 3))
		return 3;
	else if ((iSConversion == 0) && (iDConversion == 0))
		;
	else
		return 12;

	if (TableBuilt == 0)
		MSL_BuildTable();

	while(!FoundSource && i < MAX_RACK)
	{
		i ++;
		if (Table[i].nYLocation == Source.nYGrid && Table[i].nXLocation == Source.nXGrid && strcmp(Table[i].szRackId, ""))
			FoundSource = 1;
	}

	if ( i == MAX_RACK )
		return MSL_ShowErrorDialog("Move Id Error", "No rack on get location");

	while (!FoundDest && j < MAX_RACK)
	{
		j ++;
		if (Table[j].nYLocation == Destination.nYGrid && Table[j].nXLocation == Destination.nXGrid)
			FoundDest = 1;
	}

	if ( j == MAX_RACK )
		return MSL_ShowErrorDialog("Move Id Error", "No rack on put location");

	if (MOVEID_DEBUG) 
	{
		MSL_RackGetUnit(Table[i].szRackName, 1, &Unit, sizeof(Unit));
		printf("\nThe source rack id before moving is %s\n", Unit.szRackId);
		MSL_RackGetUnit(Table[j].szRackName, 1, &Unit, sizeof(Unit));
		printf("\nThe destinate rack id before moving is %s\n", Unit.szRackId);
	}

	MSL_RackLoadId(Table[j].szRackName, Table[i].szRackId);
	MSL_RackLoadId(Table[i].szRackName, "");

	if (MOVEID_DEBUG) 
	{
		MSL_RackGetUnit(Table[i].szRackName, 1, &Unit, sizeof(Unit));
		printf("\nThe source rack id after moving is %s\n", Unit.szRackId);
		MSL_RackGetUnit(Table[j].szRackName, 1, &Unit, sizeof(Unit));
		printf("\nThe destinate rack id after moving is %s\n", Unit.szRackId);

	}

	MSL_UpdateTable(Table[i].szRackName, Table[j].szRackName);

	// Reopen the rack in order to store the new id etc in the database

	MSL_RackOpenEx(Table[j].szRackName, Table[j].szRackFile, Table[j].nYLocation,
	Table[j].nXLocation, Table[j].dRotation, Table[j].szRackId, 0);

	return 0;
}

/*****************************************************************************
*                                                                            *
*  Function: MSL_UpdateMovedIdOffDeck(char* fromLocation, char* toLocation)  *
*                                                                            *
*   Purpose: Move the rack id of rack which was moved to some offdeck        *
*            locations, i.e., incubator etc, from some ondeck locations      *
*            and will be moved back later.                                   *
*                                                                            *
*   Returns: 0 for success, 3 otherwise                                      *
*                                                                            *
*****************************************************************************/

int MSL_UpdateMovedIdOffDeck(        // SUCCESS or FAIL
		char* fromLocation,          // old ondeck location
		char* toLocation)            // new offdeck location
{
	int i = -1;
	int j = 0;
	int LocationFound = 0;
	int OptionFound = 0;
	Location SourceCoordinate;

	if (MSL_ConvertDeckLocation(fromLocation, &SourceCoordinate) == 3)
		return 3;

	if (TableBuilt == 0)
		MSL_BuildTable();

	while((!LocationFound) && i<MAX_RACK)
	{
		i ++;
		if ((SourceCoordinate.nYGrid == Table[i].nYLocation) && 
		(SourceCoordinate.nXGrid == Table[i].nXLocation)&& strcmp(Table[i].szRackId, ""))
			LocationFound = 1;
	}

	if (i == MAX_RACK)
		return MSL_ShowErrorDialog("Move Id Error", "No rack on the get location");

	while((!OptionFound) && strcmp(OdLTable[j].szLocationName, "") != 0)
	{
		if (strcmp(OdLTable[j].szLocationName, toLocation) == 0)
		{
			OptionFound = 1;
			j --;
		}
		j ++;
	}

	if (j == 200)
		return MSL_MessageDialog(0, "Error", "No neough space for offdeck locations", 0, 1, 1, 0);

	strcpy(OdLTable[j].szLocationName, toLocation);
	strcpy(OdLTable[j].szRackId, Table[i].szRackId);

	MSL_RackLoadId(Table[i].szRackName, "");
	strcpy(Table[i].szRackId, "");

	MSL_RackOpenEx(Table[i].szRackName, Table[i].szRackFile, Table[i].nYLocation,
	Table[i].nXLocation, Table[i].dRotation, Table[i].szRackId, 0);

	if (MOVEID_DEBUG)
	{
		i = 0;
		while (strcmp(OdLTable[i].szLocationName, "") != 0)
		{
			printf("\nAlready used offdeck locations are:\n");
			printf("   LocationName      RackId  \n");
			printf("   %s         %s", OdLTable[i].szLocationName, OdLTable[i].szRackId);
			i++;
		}
	}

	return 0;
}

/*****************************************************************************
*                                                                            *
*  Function: MSL_UpdateMovedIdOnDeck(char* fromLocation, char* toLocation)   *
*                                                                            *
*   Purpose: Move the rack which was on an ondeck location back to ondeck    *
*            location from some offdeck location, i.e., incubator etc.       *
*                                                                            *
*   Returns: 0 for success, 3 otherwise                                      *
*                                                                            *
*****************************************************************************/

int MSL_UpdateMovedIdOnDeck(       // SUCCESS or FAIL
		char* fromLocation,        // offdeck location
		char* toLocation)          // ondeck location
{
	int i = -1;
	int j = 0;
	int LocationFound = 0;
	int OptionFound = 0;
	Location SourceCoordinate;

	if (MSL_ConvertDeckLocation(toLocation, &SourceCoordinate) == 3)
		return 3;

	if (TableBuilt == 0)
		MSL_BuildTable();

	while((!OptionFound) && strcmp(OdLTable[j].szLocationName, "") != 0)
	{
		if (strcmp(OdLTable[j].szLocationName, fromLocation) == 0)
		{
			OptionFound = 1;
			j --;
		}
		j ++;
	}

	if (j == 200)
		return MSL_MessageDialog(0, "Error", "No labware on the given get location", 0, 1, 1, 0);

	while((!LocationFound) && i<MAX_RACK)
	{
		i ++;
		if ((SourceCoordinate.nYGrid == Table[i].nYLocation) && (SourceCoordinate.nXGrid == Table[i].nXLocation))
			LocationFound = 1;
	}

	if (i == MAX_RACK)
		return MSL_ShowErrorDialog("Move Id Error", "No rack on the put location");

	MSL_RackLoadId(Table[i].szRackName, OdLTable[j].szRackId);
	strcpy(Table[i].szRackId, OdLTable[j].szRackId);

	strcpy(OdLTable[j].szRackId, "");

	MSL_RackOpenEx(Table[i].szRackName, Table[i].szRackFile, Table[i].nYLocation,
	Table[i].nXLocation, Table[i].dRotation, Table[i].szRackId, 0);

	return 0;
}	

/*****************************************************************
*                                                                *
*  Function:  MSL_MoveIdOffdecktoOffdeck(char* , char* )         *
*                                                                *
*   Purpose:  Move the rack id of moved rack from a offdeck      *
*             location to the new offdeck location               *
*                                                                *
*   Returns:  0 if success, 3 otherwise                          *
*                                                                *
*****************************************************************/

int MSL_MoveIdOffdecktoOffdeck(           // SUCCESS or FAIL
		char* getLocation,            // old offdeck location
		char* putLocation)            // new offdeck location
{
	int i = 0;
	int j = 0;
	int sourceFound = 0;
	int destFound = 0;

	if (TableBuilt == 0)
		MSL_BuildTable();

	while((!sourceFound) && strcmp(OdLTable[i].szLocationName, "") != 0)
	{
		if (strcmp(OdLTable[i].szLocationName, getLocation) == 0)
		{
			sourceFound = 1;
			i --;
		}
		i ++;
	}

	if (i == 200)
		return MSL_MessageDialog(0, "Error", "No labware on the given get location", 0, 1, 1, 0);

	while((!destFound) && strcmp(OdLTable[j].szLocationName, "") != 0)
	{
		if (strcmp(OdLTable[j].szLocationName, putLocation) == 0)
		{
			destFound = 1;
			j --;
		}
		j ++;
	}

	if (j == 200)
		return MSL_MessageDialog(0, "Error", "No labware on the given put location", 0, 1, 1, 0);

	strcpy(OdLTable[j].szRackId, OdLTable[i].szRackId);
	strcpy(OdLTable[i].szRackId, "");

	return 0;
}
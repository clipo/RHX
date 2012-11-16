/*******************************************************************************
* MSLGUI2.S
*
*	Module to demonstrate various GUI capabilities
*
*******************************************************************************/


char *NULL = 0;

int iDlgMain        = 1;

int iCmbCatag       = 1000;
int iCmbControls    = 1001;

int iGrpButtons     = 2000;
int iGrpComboBoxes  = 2100;
int iGrpEditBoxes   = 2200;
int iGrpGroupBoxes  = 2300;
int iGrpLabels      = 2400;
int iGrpScrollBars  = 2500;

int iGrpFileSelect  = 3000;
int iGrpFileContent;

int iGrpInProgInfo  = 4000;

int iGrpListLink    = 5000;

int iGrpListRecords = 6000;

int iGrpPosition    = 7000;

int iGrpMessages    = 8000;
int iGrpMsgIcons;
int iGrpMsgBtns;

int iBtnDone    = 20000;
int iBtnExample = 20001;
int iBtnFile    = 20002;
int iBtnInProg  = 20003;
int iBtnMsg     = 20004;
int iBtnBegPos  = 20005;
int iBtnEndPos  = 20006;

int iOn  = 1;
int iOff = 0;

double dPosX, dPosY, dPosW, dPosH;

//char *pszCatagories = "Controls,File Selection,In Progress Information,List Linking,List Records,Reposition,Messages/Queries";
char *pszCatagories = "Controls,File Selection,In Progress Information,List Linking,Reposition,Messages/Queries";
char *pszControls   = "Buttons,Combo/List Boxes,Edit Boxes,Group Boxes/Labels,Scroll Bars";

char szFileDlgTitle[82];
char szFileFilterDsc[82];
char szFileFilterVal[82];
char szFileDefaultDir[82];
char szFilePath[128];
char szFileName[64];
char szMsgText[82];
char szMsgTitle[82];


/*******************************************************************************
*  BuildControls()
*
*
*******************************************************************************/

int BuildControls()
{
  int i;
  int n;
  int iColList[48];

// Create the specific controls catagory.  Slave it to the demo catagories

    MSL_CreateComboBox (iDlgMain, iCmbControls, 45, 1, 16, 7,
			"Specific Controls:",
			"Use the arrow keys or mouse to select which controls to demo.",
			NULL, 0, 0);
    MSL_ListLoadValues (iDlgMain, iCmbControls, pszControls, ',', 0);
    MSL_ListSetSelIndex  (iDlgMain, iCmbControls, 0, 1);
    MSL_SetControlMaster (iDlgMain, iCmbControls, iCmbCatag, "Controls", 0.0, 3, 0);


//--------------------------------------
// Create the button controls...
//--------------------------------------

    n = 0;
    MSL_CreateGroupBox  (iDlgMain, iGrpButtons,    1, 3, 60, 20,
			 "Button Controls", 0);
    iColList[n] = iGrpButtons+n; n++;


// Radio Buttons

    MSL_CreateGroupBox  (iDlgMain, iGrpButtons+n,  2, 5, 18, 8,
			 "Labware (Radio Btns)", 0);
    iColList[n] = iGrpButtons+n; n++;

    MSL_CreateRadioBtn  (iDlgMain,  iGrpButtons+n, 3, 7, 12,  1,
			 "384 Well Plate",
			 "If selected, a rare hamburger will be served",
			 NULL, 1, 0);
    iColList[n] = iGrpButtons+n; n++;

    MSL_CreateRadioBtn  (iDlgMain,  iGrpButtons+n, 3,  -1, 12,  1,
			 "96 Well Plate",
			 "If selected, a medium rare hamburger will be served",
			 NULL, 1, 0);
    iColList[n] = iGrpButtons+n; n++;

    MSL_CreateRadioBtn  (iDlgMain,  iGrpButtons+n, 3,  -1, 12,  1,
			 "Big Well Plate",
			 "If selected, a medium hamburger will be served",
			 NULL, 1, 0);
    iColList[n] = iGrpButtons+n; n++;

    MSL_CreateRadioBtn  (iDlgMain,  iGrpButtons+n, 3,  -1, 12,  1,
			 "Disposable Tips",
			 "If selected, a well done hamburger will be served",
			 NULL, 1, 0);
    iColList[n] = iGrpButtons+n; n++;


// Toggle Buttons

    MSL_CreateGroupBox  (iDlgMain, iGrpButtons+n,  2, 14, 18, 7,
			 "Options (Toggle Btns)", 0);
    iColList[n] = iGrpButtons+n; n++;

    MSL_CreateToggleBtn (iDlgMain,  iGrpButtons+n, 3,  16,  12,  1,
			 "Short Support",
			 "If check set, ketchup will be added to your burger", NULL, 0);
    iColList[n] = iGrpButtons+n; n++;

    MSL_CreateToggleBtn (iDlgMain,  iGrpButtons+n, 3, -1,  12,  1,
			 "Tall Support",
			 "If check set, mustard will be added to your burger", NULL, 0);
    iColList[n] = iGrpButtons+n; n++;

    MSL_CreateToggleBtn (iDlgMain,  iGrpButtons+n, 3, -1,  12,  1,
			 "Rotate Plate",
			 "If check set, onions will be added to your burger", NULL, 0);
    iColList[n] = iGrpButtons+n; n++;


// Push Buttons

    MSL_CreateGroupBox  (iDlgMain, iGrpButtons+n,  22,  5, 38, 16,
			 "Actions (Push Btns)", 0);
    iColList[n] = iGrpButtons+n; n++;

    MSL_CreatePushBtn   (iDlgMain,  iGrpButtons+n, 23,  7,  12,  1,
			 "&Start", "Click here to place your lunch order",
			 0, 0, 0);
    iColList[n] = iGrpButtons+n; n++;

    MSL_CreatePushBtn   (iDlgMain,  iGrpButtons+n, 23,  -1,  12,  1,
			 "S&top Order", "Click here to cancel your lunch order",
			 0, 0, 0);
    iColList[n] = iGrpButtons+n; n++;

    MSL_CreatePushBtn   (iDlgMain,  iGrpButtons+n, 23,  -1,  12,  1,
			 "&Pause", "Click here to receive the bill",
			 0, 0, 0);
    iColList[n] = iGrpButtons+n; n++;

    MSL_CreatePushBtn   (iDlgMain,  iGrpButtons+n, 23,  -1,  36,  7,
			 "&Emergency Stop", "Click here to summon the waitress",
			 0, 0, 0);
    iColList[n] = iGrpButtons+n; n++;


// ...Finally, make a collection from all the button controls and slave that collection
// to the controls combo box

    MSL_CreateCollection (iDlgMain, iGrpButtons+99, iColList, n, 0);
    MSL_SetControlMaster (iDlgMain, iGrpButtons+99, iCmbControls,    "Buttons", 0.0, 3, 0);


//--------------------------------------
// Create the combo/list box controls...
//--------------------------------------

    n = 0;
    MSL_CreateGroupBox (iDlgMain, iGrpComboBoxes, 1, 3, 60, 20,
                        "Combo/List Box Controls", 0);
    iColList[n] = iGrpComboBoxes+n; n++;

// Combo Boxes

    MSL_CreateComboBox (iDlgMain, iGrpComboBoxes+n, 3, 6, 25, 16,
			"Combo with label on Top",
			"This combo contains an  auto sorted list of items",
			NULL, 0, 0x404);
    MSL_ListLoadValues  (iDlgMain, iGrpComboBoxes+n,
			 "Vials,Support,Test Fixture,Test Tube,96 Deep Well Plate,Big Well Plate,96 Well Plate,Flush/Wash,Disposable Tips,384 Well Plate,Microfuge,TipChute,Reagent,Test Tube",
			 ',', 0);
    MSL_ListSetSelIndex (iDlgMain, iGrpComboBoxes+n, 0, 1);
    iColList[n] = iGrpComboBoxes+n; n++;

    MSL_CreateComboBox (iDlgMain, iGrpComboBoxes+n, 12, 9, 16, 16,
			"And on Side:",
			"This combo contains an unsorted list of items",
			NULL, 0, 0);
    MSL_ListLoadValues  (iDlgMain, iGrpComboBoxes+n,
			 "Vials,Support,Test Fixture,Test Tube,96 Deep Well Plate,Big Well Plate,96 Well Plate,Flush/Wash,Disposable Tips,384 Well Plate,Microfuge,TipChute,Reagent,Test Tube",
			 ',', 0);
    MSL_ListSetSelIndex (iDlgMain, iGrpComboBoxes+n, 0, 1);
    iColList[n] = iGrpComboBoxes+n; n++;


// List Boxes

    MSL_CreateListBox (iDlgMain, iGrpComboBoxes+n, 30, 6, 28, 6,
		       "Sorted List with single selection",
                       "This control is using a monospaced font",
		       NULL, 0, 0, 0, 0x401);
    MSL_ListLoadValues  (iDlgMain, iGrpComboBoxes+n,
			 "Vials,Support,Test Fixture,Test Tube,96 Deep Well Plate,Big Well Plate,96 Well Plate,Flush/Wash,Disposable Tips,384 Well Plate,Microfuge,TipChute,Reagent,Test Tube",
			 ',', 0);
    MSL_ListSetSelIndex (iDlgMain, iGrpComboBoxes+n, 0, 1);
    iColList[n] = iGrpComboBoxes+n; n++;

    MSL_CreateListBox (iDlgMain, iGrpComboBoxes+n, 30, 14, 28, 6,
		       "Unsorted List with multiple selections",
		       "This control is using a proportional font",
		       NULL, 0, 0, 0, 0x010);
    MSL_ListLoadValues  (iDlgMain, iGrpComboBoxes+n,
			 "Vials,Support,Test Fixture,Test Tube,96 Deep Well Plate,Big Well Plate,96 Well Plate,Flush/Wash,Disposable Tips,384 Well Plate,Microfuge,TipChute,Reagent,Test Tube",
			 ',', 0);
    MSL_ListSetSelIndex (iDlgMain, iGrpComboBoxes+n, 0, 1);
    MSL_ListSetSelIndex (iDlgMain, iGrpComboBoxes+n, 4, 0);
    iColList[n] = iGrpComboBoxes+n; n++;


// ...Finally, make a collection from all the combo/list controls and slave that collection
// to the controls combo box

    MSL_CreateCollection (iDlgMain, iGrpComboBoxes+99, iColList, n, 0);
    MSL_SetControlMaster (iDlgMain, iGrpComboBoxes+99, iCmbControls,
                          "Combo/List Boxes", 0.0, 3, 0);


//--------------------------------------
// Create the edit box controls...
//--------------------------------------

    n = 0;
    MSL_CreateGroupBox (iDlgMain, iGrpEditBoxes,  1, 3, 60, 20,
                        "Edit Box Controls", 0);
    iColList[n] = iGrpEditBoxes+n; n++;

    MSL_CreateEditBox (iDlgMain, iGrpEditBoxes+n,  12, 5,  6,  1,
                       "Integer Editor:",  "Value must be 1 to 10",
                       NULL, "INT",
                       1.0, 10.0, 0.0, 0, 0x70);
    iColList[n] = iGrpEditBoxes+n; n++;

    MSL_CreateEditBox (iDlgMain, iGrpEditBoxes+n,  12, -1,  6,  1,
                       "Double Editor:",  "Value must be 1.0 to 10.0",
                       NULL, "DOUBLE",
                       1.0, 10.0, 0.1, 0, 0x60);
    iColList[n] = iGrpEditBoxes+n; n++;

    MSL_CreateEditBox (iDlgMain, iGrpEditBoxes+n,  12, -1,  10,  1,
                       "Text Editor:",  "Value can be anything",
                       NULL, "TEXT",
                       0.0, 0.0, 0.1, 0, 0x10);
    iColList[n] = iGrpEditBoxes+n; n++;

    MSL_CreateEditBox (iDlgMain, iGrpEditBoxes+n,  3, 12,  56,  9,
                       "Multiline Text Editor",  "Value can be anything",
                       NULL, "TEXT",
                       0.0, 0.0, 0.0, 0, 0x84);
    iColList[n] = iGrpEditBoxes+n; n++;


// ...Finally, make a collection from all the combo/list controls and slave that collection
// to the controls combo box

    MSL_CreateCollection (iDlgMain, iGrpEditBoxes+99, iColList, n, 0);
    MSL_SetControlMaster (iDlgMain, iGrpEditBoxes+99, iCmbControls, "Edit Boxes", 0.0, 3, 0);


//--------------------------------------
// Create group box and label controls...
//--------------------------------------

    n = 0;
    MSL_CreateGroupBox   (iDlgMain, iGrpGroupBoxes, 1, 3, 60, 20,
                          "Group Box and Label Controls", 0);
    iColList[n] = iGrpGroupBoxes+n; n++;

    MSL_CreateGroupBox   (iDlgMain, iGrpGroupBoxes+n, 3, 5, 27, 17,
                          "Text Label", 0);
    iColList[n] = iGrpGroupBoxes+n; n++;

    MSL_CreateLabel (iDlgMain, iGrpGroupBoxes+n, 5, 6, 23, 3,
		     "^ Group Box with label text", 0);
    iColList[n] = iGrpGroupBoxes+n; n++;

    MSL_CreateLabel (iDlgMain, iGrpGroupBoxes+n, 5, 10, 23, 2,
		     "Multiline monospaced label\nwith a border", 0x1001);
    iColList[n] = iGrpGroupBoxes+n; n++;

    MSL_CreateGroupBox   (iDlgMain, iGrpGroupBoxes+n, 32, 5, 27, 17,
                          "", 0);
    iColList[n] = iGrpGroupBoxes+n; n++;

    MSL_CreateLabel (iDlgMain, iGrpGroupBoxes+n, 33, 6, 23, 3,
		     "^ Group Box without label text", 0);
    iColList[n] = iGrpGroupBoxes+n; n++;

    MSL_CreateLabel (iDlgMain, iGrpGroupBoxes+n, 34, 10, 22, 1,
		     "Single line proportional label", 0);
    iColList[n] = iGrpGroupBoxes+n; n++;


// ...Finally, make a collection from all the combo/list controls and slave that collection
// to the controls combo box

    MSL_CreateCollection (iDlgMain, iGrpGroupBoxes+99, iColList, n, 0);
    MSL_SetControlMaster (iDlgMain, iGrpGroupBoxes+99, iCmbControls,
			  "Group Boxes/Labels", 0.0, 3, 0);


//--------------------------------------
// Create the scroll bar controls...
//--------------------------------------

    n = 0;
    MSL_CreateGroupBox (iDlgMain, iGrpScrollBars, 1, 3, 60, 20, "Scroll Bar Controls", 0);
    iColList[n] = iGrpScrollBars+n; n++;


// Voltage

    MSL_CreateEditBox (iDlgMain, iGrpScrollBars+n,  3,  6,  14,  1,
                       "Volume Liquid Level (in microliters)",
                       "Adjusts the liquid level volume (edit box linked to scrollbar)",
                       NULL, "DOUBLE",
                       0.0, 0.0, 0.1, 0, 0x04);
    iColList[n] = iGrpScrollBars+n; n++;

    MSL_CreateScrollBar (iDlgMain, iGrpScrollBars+n, 3, -1, 14,
			 "Adjusts the liquid level volume (scrollbar linked to edit box)",
                         NULL, 0.0, 6000.0, 1.0, 100.0,
                         iColList[n-1], 0);
    iColList[n] = iGrpScrollBars+n; n++;


// Amplifier Gain

    MSL_CreateEditBox (iDlgMain, iGrpScrollBars+n,  3, 12,  14,  1,
                       "Gain (1.0x - 10.0x)", 
                       "You may type a gain value or use the scroll bar",
                       NULL, "DOUBLE",
                       0.0, 0.0, 0.1, 0, 0x04);
    iColList[n] = iGrpScrollBars+n; n++;

    MSL_CreateScrollBar (iDlgMain, iGrpScrollBars+n, 3, -1, 14,
			 "Adjusts the amplifier gain value (scrollbar linked to edit box)",
                         NULL, 1.0, 10.0, 0.01, 0.1,
                         iColList[n-1], 0);
    iColList[n] = iGrpScrollBars+n; n++;

// Base

    MSL_CreateLabel (iDlgMain, iGrpScrollBars+n, 29, 5, 4, 1,
		     "", 0x1100);
    iColList[n] = iGrpScrollBars+n; n++;

    MSL_CreateScrollBar (iDlgMain, iGrpScrollBars+n, 30, -1, 14,
			 "Adjusts the base value (scrollbar linked to bordered label)",
			 NULL, 0.0, 100.0, 0.1, 10.0,
                         iColList[n-1], 0x30);
    iColList[n] = iGrpScrollBars+n; n++;

    MSL_CreateLabel (iDlgMain, iGrpScrollBars+n, 29, -1, 6, 1,
		     "Base", 0);
    iColList[n] = iGrpScrollBars+n; n++;

// Treble

    MSL_CreateLabel (iDlgMain, iGrpScrollBars+n, 39, 5, 4, 1,
		     "", 0x1100);
    iColList[n] = iGrpScrollBars+n; n++;

    MSL_CreateScrollBar (iDlgMain, iGrpScrollBars+n, 40, -1, 14,
			 "Adjusts the treble value (scrollbar linked to bordered label)",
                         NULL, 0.0, 100.0, 0.1, 10.0,
                         iColList[n-1], 0x30);
    iColList[n] = iGrpScrollBars+n; n++;

    MSL_CreateLabel (iDlgMain, iGrpScrollBars+n, 39, -1, 6, 1,
		     "Treble", 0);
    iColList[n] = iGrpScrollBars+n; n++;


// ...Finally, make a collection from all the scroll bar controls and slave
// that collection to the controls combo box

    MSL_CreateCollection (iDlgMain, iGrpScrollBars+99, iColList, n, 0);
    MSL_SetControlMaster (iDlgMain, iGrpScrollBars+99, iCmbControls,
			  "Scroll Bars", 0.0, 3, 0);
}


/*******************************************************************************
*  BuildFileSelect()
*
*
*******************************************************************************/

int BuildFileSelect()
{
  int i;
  int n;
  int iColList[48];


// Create the file selection controls...

    n = 0;
    MSL_CreateGroupBox (iDlgMain, iGrpFileSelect,  1, 3, 60, 20,
                        "File Selection Demo", 0);
    iColList[n] = iGrpFileSelect+n; n++;

    strcpy (szFileDlgTitle, "Open");
    MSL_CreateEditBox (iDlgMain, iGrpFileSelect+n,  15, 5, 30,  1,
                       "Dialog Title:",  "Title to appear in file selection dialog banner",
                       szFileDlgTitle, "TEXT",
                       0.0, 80.0, 0.0, 0, 0);
    iColList[n] = iGrpFileSelect+n; n++;

    strcpy (szFileFilterDsc, "Text Files (*.t)|*.txt|All Files (*.*)|*.*||");
    MSL_CreateEditBox (iDlgMain, iGrpFileSelect+n,  15, -1, 30,  1,
                       "File Filter Desc:",  "Description of file filter",
                       szFileFilterDsc, "TEXT",
                       0.0, 80.0, 0.0, 0, 0);
    iColList[n] = iGrpFileSelect+n; n++;

    strcpy (szFileDefaultDir, "");
    MSL_CreateEditBox (iDlgMain, iGrpFileSelect+n,  15, -1, 30,  1,
                       "Default Directory:",  "Initial directory to appear in the file selection dialog",
                       szFileDefaultDir, "TEXT",
                       0.0, 80.0, 0.0, 0, 0);
    iColList[n] = iGrpFileSelect+n; n++;

    MSL_CreateEditBox (iDlgMain, iGrpFileSelect+n,  3, 12, 56,  9,
                       "File Contents",  "Text read in from the selected file",
                       NULL, "TEXT",
                       0.0, 0.0, 0.0, 0, 0xCD);
    iColList[n] = iGrpFileSelect+n; n++;
    iGrpFileContent = iColList[n-1];

    MSL_CreatePushBtn (iDlgMain, iBtnFile,  47, 5,  12,  2,
                       "&File Select...",
		       "Click here to invoke the file selection dialog box",
			0, 0, 0);
    iColList[n] = iBtnFile; n++;


// ...Finally, make a collection from all the file selection controls and slave
// that collection to the controls combo box

    MSL_CreateCollection (iDlgMain, iGrpFileSelect+99, iColList, n, 0);
    MSL_SetControlMaster (iDlgMain, iGrpFileSelect+99, iCmbCatag,
			  "File Selection", 0.0, 3, 0);
}


/*******************************************************************************
*  BuildInProgInfo()
*
*
*******************************************************************************/

int BuildInProgInfo()
{
  int i;
  int n;
  int iColList[48];


// Create the In Progress Info controls...

    n = 0;
    MSL_CreateGroupBox (iDlgMain, iGrpInProgInfo,  1, 3, 60, 20,
                        "In Progress Demo", 0);
    iColList[n] = iGrpInProgInfo+n; n++;


    MSL_CreatePushBtn (iDlgMain, iBtnInProg,  22, 12,  18,  2,
                       "&Show  'In Progress'",
		       "Click here to show how the 'In Progress' information bar looks",
			0, 0, 0);
    iColList[n] = iBtnInProg; n++;


// ...Finally, make a collection from all the in progress controls and slave
// that collection to the controls combo box

    MSL_CreateCollection (iDlgMain, iGrpInProgInfo+99, iColList, n, 0);
    MSL_SetControlMaster (iDlgMain, iGrpInProgInfo+99, iCmbCatag,
			  "In Progress Information", 0.0, 3, 0);

}


/*******************************************************************************
*  BuildListLink()
*
*
*******************************************************************************/

int BuildListLink()
{
  int i;
  int n;
  int iColList[48];


// Create the List Link controls...

    n = 0;
    MSL_CreateGroupBox (iDlgMain, iGrpListLink,  1, 3, 60, 20,
                        "Listbox Linking Demo", 0);
    iColList[n] = iGrpListLink+n; n++;


// Create list boxes that copy one to another

    MSL_CreateListBox (iDlgMain, iGrpListLink+n, 3, 6, 12, 5,
		       "Available Animals",
                       "Contains all available animals (Double click entries to select)",
		       NULL, 0, 0, 0, 0x401);
    MSL_ListLoadValues  (iDlgMain, iGrpListLink+n,
			 "Lion,Bear,Tiger,Elephant,Snake,Bird,Insect,Fish",
			 ',', 0);
    iColList[n] = iGrpListLink+n; n++;

    MSL_CreateListBox (iDlgMain, iGrpListLink+n, 16, 6, 12, 5,
		       "Selected Animals",
                       "Contains all selected animals (Double click entries to remove)",
		       NULL, 0, 0, 0, 0x401);
    iColList[n] = iGrpListLink+n; n++;
    MSL_ListLink (iDlgMain, iColList[n-2], iColList[n-1], 0, 2);

    MSL_CreateLabel (iDlgMain, iGrpListLink+n, 3, -1, 30, 1,
		     "You may copy as many as are available", 0);
    iColList[n] = iGrpListLink+n; n++;


// Create a fixed and copy too list

    MSL_CreateListBox (iDlgMain, iGrpListLink+n, 30, 15, 12, 5,
		       "Available Animals",
                       "Contains all available animals (single click entries to select)",
		       NULL, 0, 0, 0, 0x401);
    MSL_ListLoadValues  (iDlgMain, iGrpListLink+n,
			 "Lion,Bear,Tiger,Elephant,Snake,Bird,Insect,Fish",
			 ',', 0);
    iColList[n] = iGrpListLink+n; n++;

    MSL_CreateListBox (iDlgMain, iGrpListLink+n, 43, 15, 12, 5,
		       "Selected Animals",
                       "Contains all selected animals (single click entries to remove)",
		       NULL, 0, 0, 0, 0x401);
    iColList[n] = iGrpListLink+n; n++;
    MSL_ListLink (iDlgMain, iColList[n-2], iColList[n-1], iColList[n-2], 1);

    MSL_CreateLabel (iDlgMain, iGrpListLink+n, 30, -1, 30, 1,
		     "You may copy as many as you wish!", 0);
    iColList[n] = iGrpListLink+n; n++;


// ...Finally, make a collection from all the listbox linking controls and slave
// that collection to the controls combo box

    MSL_CreateCollection (iDlgMain, iGrpListLink+99, iColList, n, 0);
    MSL_SetControlMaster (iDlgMain, iGrpListLink+99, iCmbCatag,
			  "List Linking", 0.0, 3, 0);
}


/*******************************************************************************
*  BuildListRecords()
*
*
*******************************************************************************/

int BuildListRecords()
{
  int i;
  int n;
  int iColList[48];


// Create the List Record controls...

    n = 0;
    MSL_CreateGroupBox (iDlgMain, iGrpListRecords,  1, 3, 60, 20,
                        "Listbox Record Selection Demo", 0);
    iColList[n] = iGrpListRecords+n; n++;

// ...Finally, make a collection from all the listbox records controls and slave
// that collection to the controls combo box

    MSL_CreateCollection (iDlgMain, iGrpListRecords+99, iColList, n, 0);
    MSL_SetControlMaster (iDlgMain, iGrpListRecords+99, iCmbCatag,
			  "List Records", 0.0, 3, 0);
}


/*******************************************************************************
*  BuildPosition()
*
*
*******************************************************************************/

int BuildPosition ()
{
  int i;
  int n;
  int iColList[48];


// Create the List Record controls...

    n = 0;
    MSL_CreateGroupBox (iDlgMain, iGrpPosition,  1, 3, 60, 20,
                        "MSL_SetWindowPos  Demo", 0);
    iColList[n] = iGrpPosition+n; n++;


    MSL_CreatePushBtn (iDlgMain, iBtnBegPos,  3, 5,  8,  1,
                       "&Begin",
		       "Click here to start the position demonstration",
			0, 0, 0x800);
    iColList[n] = iBtnBegPos; n++;

    MSL_CreatePushBtn (iDlgMain, iBtnEndPos, -1,  5,  8, 1,
                       "E&nd",
		       "Click here to stop the position demonstration",
			0, 0, 0);
    iColList[n] = iBtnEndPos; n++;
    MSL_EnableControl (iDlgMain, iBtnEndPos, 0);


    dPosY = 8.0; dPosW = 50.0;
    MSL_CreateLabel (iDlgMain, iGrpPosition+n, 5, 8, 50, 1, "", 0x1000);
    iColList[n] = iGrpPosition+n; n++;

    MSL_CreateScrollBar (iDlgMain, iGrpPosition+n, 3, 8, 12,
			 "Adjusts the bar Y position",
                         &dPosY, 8.0, 19.0, 1.0, 2.0, 0, 0x10); 
    iColList[n] = iGrpPosition+n; n++;
    MSL_EnableControl (iDlgMain, iColList[n-1], 0);

    MSL_CreateScrollBar (iDlgMain, iGrpPosition+n, 5, 20, 50,
			 "Adjusts the bar width position",
                         &dPosW, 0.0, 50.0, 1.0, 5.0, 0, 0); 
    iColList[n] = iGrpPosition+n; n++;
    MSL_EnableControl (iDlgMain, iColList[n-1], 0);



// ...Finally, make a collection from all the listbox records controls and slave
// that collection to the controls combo box

    MSL_CreateCollection (iDlgMain, iGrpPosition+99, iColList, n, 0);
    MSL_SetControlMaster (iDlgMain, iGrpPosition+99, iCmbCatag,
			  "Reposition", 0.0, 3, 0);
}


/*******************************************************************************
*  BuildMessages()
*
*
*******************************************************************************/

int BuildMessages()
{
  int i;
  int n;
  int iColList[48];


// Create the List Record controls...

    n = 0;
    MSL_CreateGroupBox (iDlgMain, iGrpMessages,  1, 3, 60, 20,
                        "Message/Query Box Demo", 0);
    iColList[n] = iGrpMessages+n; n++;

// Create available icon selection

    MSL_CreateComboBox (iDlgMain, iGrpMessages+n, 3, 6, 15, 7,
			"Desired Icon",
			"List of available message/query dialog icons",
			NULL, 0, 4);
    MSL_ListLoadValues  (iDlgMain, iGrpMessages+n,
			 "None,Information,Exclamation,Question,Stop", ',', 0);
    MSL_ListSetSelIndex (iDlgMain, iGrpMessages+n, 1, 1);
    iColList[n] = iGrpMessages+n; n++;
    iGrpMsgIcons = iColList[n-1];


// Create available buttons selection

    MSL_CreateComboBox (iDlgMain, iGrpMessages+n, 3, 10, 15, 9,
			"Desired Buttons",
			"List of available message/query dialog push buttons",
			NULL, 0, 4);
    MSL_ListLoadValues  (iDlgMain, iGrpMessages+n,
			 "OK,OK/Cancel,Retry/Cancel,Abort/Retry/Ignore,Yes/No,Yes/No/Cancel",
			 ',', 0);
    MSL_ListSetSelIndex (iDlgMain, iGrpMessages+n, 0, 1);
    iColList[n] = iGrpMessages+n; n++;
    iGrpMsgBtns = iColList[n-1];


// Create text box where message title may be specified

    strcpy (szMsgTitle, "Hey you!");
    MSL_CreateEditBox (iDlgMain, iGrpMessages+n,  3, 14, 40,  1,
                       "Message Title",  "Text to appear in banner of the message box",
                       szMsgTitle, "TEXT",
                       0.0, 80.0, 0.0, 0, 4);
    iColList[n] = iGrpMessages+n; n++;


// Create text box where message may be specified

    strcpy (szMsgText, "Here's a Sample Message");
    MSL_CreateEditBox (iDlgMain, iGrpMessages+n,  3, 18, 40,  1,
                       "Message Contents",  "Text to appear in the message box",
                       szMsgText, "TEXT",
                       0.0, 80.0, 0.0, 0, 4);
    iColList[n] = iGrpMessages+n; n++;


// Create a button to invoke the message dialog box

    MSL_CreatePushBtn (iDlgMain, iBtnMsg,  28, 6,  15,  2,
                       "&Display Message...",
		       "Click here to invoke the message/query dialog box",
			0, 0, 0);
    iColList[n] = iBtnMsg; n++;


// ...Finally, make a collection from all the message box demo controls and slave
// that collection to the controls combo box

    MSL_CreateCollection (iDlgMain, iGrpMessages+99, iColList, n, 0);
    MSL_SetControlMaster (iDlgMain, iGrpMessages+99, iCmbCatag,
			  "Messages/Queries", 0.0, 3, 0);
}


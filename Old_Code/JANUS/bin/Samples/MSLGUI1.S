/*******************************************************************************
* MSLGUI1.S
*
*   Module to demonstrate various GUI capabilities
*
*******************************************************************************/



/*******************************************************************************
*  BuildDialog()
*
*
*******************************************************************************/

int BuildDialog()
{
  int i;
  int n;


// Create the main dialog box.

    MSL_CreateDialog (0, 1, -1, -1, -1, -1, "MSL GUI Demonstration", 0);


// Create combo box to contain demo catagories.  Then load the list

    MSL_CreateComboBox  (iDlgMain, iCmbCatag, 9, 1, 18, 8,
             "Catagories:",
             "Use the arrow keys or mouse to select a demo catagory.",
             NULL, 0, 0);
    MSL_ListLoadValues  (iDlgMain, iCmbCatag, pszCatagories, ',', 0);
    MSL_ListSetSelIndex (iDlgMain, iCmbCatag, 0, 1);


// Build the various catagories

    BuildControls();
    BuildFileSelect();
    BuildInProgInfo();
    BuildListLink();
//    BuildListRecords();
    BuildPosition();
    BuildMessages();

// Create the push buttons

    MSL_CreatePushBtn   (iDlgMain, iBtnDone,     1, 24,   8,  1,
                         "&Done",
             "Click here to exit the program",
             0, 0, 0x870);

//    MSL_CreatePushBtn   (iDlgMain, iBtnExample, 10, 24,  12,  1,
//                         "&Example...",
//           "Click here to display corresponding C code.",
//           0, 0, 0x800);


// Finally show the dialog & wait for a user selection.

    MSL_ShowDialog (iDlgMain, iOn, 0);
}



/*******************************************************************************
*  Main()
*
*
*******************************************************************************/

int main()

{
    int i;
    int iBtnList[8];
    int iBtn;
    int iRC;
    int iMsgIcon,iMsgBtn;
    double dOldPosY, dOldPosW;
    int iPosX, iPosY, iPosW, iPosH;


    // Build the dialog
    BuildDialog ();

    // Make a list of btns to wait for
    iBtnList[0] = iBtnDone;
    iBtnList[1] = iBtnExample;
    iBtnList[2] = iBtnFile;
    iBtnList[3] = iBtnInProg;
    iBtnList[4] = iBtnMsg;
    iBtnList[5] = iBtnBegPos;

    // Loop until done selected
    while (1)
    {
        // Wait for button selection
        MSL_SetControlFocus (iDlgMain, iBtnDone);
        iBtn = MSL_WaitControlList (iDlgMain, iBtnList, 6, -1.0, 0);
        if (iBtn == iBtnDone) break;

        // Handle file selection
        if (iBtn == iBtnFile)
        {
            strcpy (szFilePath, "");
            iRC = MSL_SelectFileDialog (iDlgMain, szFileDlgTitle,
                                        szFileFilterDsc,// szFileFilterVal,
                                        NULL, szFileDefaultDir,
                                        szFilePath, 128, szFileName, 16, NULL, 0);
            if (!iRC)
            {
                MSL_SetControlLabel (iDlgMain, iGrpFileContent, szFilePath);
                MSL_EditReadFile (iDlgMain, iGrpFileContent, szFilePath, 0);
            }
        }

        // Handle in progress demo
        if (iBtn == iBtnInProg)
        {
            for (i = 0; i <= 100; i += 5)
            {
                MSL_WaitControl (iDlgMain, iBtnInProg, 0.1);
                MSL_InfoShowProg (iDlgMain, "Working:", i, "");
            }

            MSL_InfoShowProg (iDlgMain, "Working:", i, "Completed");
            MSL_WaitControl  (iDlgMain, iBtnInProg, 2.0);
            MSL_InfoShowHelp (iDlgMain);
        }

        // Handle message box demo
        if (iBtn == iBtnMsg)
        {
            MSL_ListGetSelIndex (iDlgMain, iGrpMsgIcons, &iMsgIcon, 1);
            MSL_ListGetSelIndex (iDlgMain, iGrpMsgBtns,  &iMsgBtn,  1);
            iMsgBtn++;
            MSL_MessageDialog (iDlgMain, szMsgTitle, szMsgText,
                               iMsgIcon, iMsgBtn, 0, 0);
        }

        // Handle message box demo
        if (iBtn == iBtnBegPos)
        {
            MSL_EnableControl (iDlgMain, iBtnEndPos, 1);
            MSL_EnableControl (iDlgMain, iGrpPosition+4, 1);
            MSL_EnableControl (iDlgMain, iGrpPosition+5, 1);
            dOldPosY = dPosY;
            dOldPosW = dPosW;
            while (1)
            {
                if (MSL_WaitControl  (iDlgMain, iBtnEndPos, 0.0)) break;
                if ((dOldPosY != dPosY) || (dOldPosW != dPosW))
                {
                    iPosY = dPosY;
                    iPosW = dPosW;
                    MSL_SetControlPos (iDlgMain, iGrpPosition+3,
                                        5, iPosY, iPosW, 1, 0, 3);
                    dOldPosY = dPosY;
                    dOldPosW = dPosW;
                }
            }
            MSL_EnableControl (iDlgMain, iBtnEndPos, 0);
            MSL_EnableControl (iDlgMain, iGrpPosition+4, 0);
            MSL_EnableControl (iDlgMain, iGrpPosition+5, 0);
            MSL_SetControlFocus (iDlgMain, iCmbCatag);
        }
    }
}


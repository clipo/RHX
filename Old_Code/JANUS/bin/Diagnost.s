/********************************************************************
 Script  : Diagnost.s 
 Purpose : Contains all functions needed used by the Diagnostics
              tests in WinPrep.
           Sets up global variables to be used by these functions.
 Culprit : kwb
********************************************************************/


int iNumDilutors, hDilutor[8], bActive[8], iValue[8], iError[8];
int iMoveModes[8];
int iTip, iPos;
int iReturn, iFlag, i;

double  dSpeed[8], dRamp[8];
double dZSpeedsUp=0.0, dZRampsUp=0.0, dZLocations;
char strRackname[80];

// purge volumes for priming manifold
double g_dPurgeVol1;    // purge volume for first valve (steps)
double g_dPurgeVol2;    // purge volume for remaining valves (steps)
double g_dPurgeVol3;    // post-purge volume (steps)

// peripiump preferences for priming manifold
double g_dPeriFlowrate; // ul/sec
double g_dPeriSpeed;    // step/sec to deliver flow rate
double g_dPeriRamp;     // step/sec/sec to deleiver flow rate
int    g_iPeriCurrent;  // motor current (0=don't change)

MP_POSITION RackPosition;

/********************************************************************
 Function : SetupDilutors()
 Purpose  : Set up general dilutor variables
********************************************************************/
int SetupDilutors()
{
    //get number of dilutors on instrument
    iNumDilutors = MSL_NumberOfDilutors();

    //initialize dilutor variables
    for(i=0; i<iNumDilutors ; i++) {
        hDilutor[i] = i+1;
        bActive[i] = 1;
        iValue[i] = 270;	// Syringe to system liquid bottle
        dSpeed[i] = 0;
        dRamp[i] = 0;
        iError[i] = 0;
    }
}


/********************************************************************
 Function : SyringeEmpty()
 Purpose  : Move dilutor plungers all the way up to empty syringe,
               home position
********************************************************************/
int SyringeEmpty()
{
    //if just evaluating test, do not attempt to move syringes
    if(!MSL_IsInstrumentOpen())
        return 0;
    
    //move dilutor pumps to home position
    iReturn = MSL_DilutorsHomePumps(iNumDilutors,hDilutor,bActive,iValue,dSpeed,dRamp,iError);
    if( iReturn != 0 ) iReturn = 3; // Abort test

    return iReturn;

}


/********************************************************************
 Function : SyringeFill()
 Purpose  : Move dilutor plungers all the way down to fill syringe
********************************************************************/
int SyringeFill()
{
    //if just evaluating test, do not attempt to move syringes
    if(!MSL_IsInstrumentOpen())
        return 0;
    
    //move dilutor pump to fill position
    iReturn = MSL_DilutorsFillPumps(iNumDilutors,hDilutor,bActive,iValue,dSpeed,dRamp,iError);
    if( iReturn != 0 ) iReturn = 3; // Abort test

    return iReturn;

}


/********************************************************************
 Function : MoveToHeight(strRackname,iPos)
 Purpose  : Move tips to specified height
********************************************************************/
//int MoveToHeight(strRackname,iPos)
//{
    //iMoveModes[0]=Z_MOVE_MODE_NORMAL;

    //find dispense height of align tip rack
    //iReturn = MSL_RackGetPosition(strRackname,iPos);
    //dZLocations[0] = RackPosition.dZDispenseHeight;

    // move tip to dispense height position
    //iReturn = MSL_DilutorsMoveToLocation(iNumDilutors, hDilutors, bActive,
                         //dZSpeedsUp, dZRampsUp, dZLocations,
                         //iMoveModes, iError);
//}


/*******************************************************************************
*
*    SetValvePositions()
*
*******************************************************************************/

int SetValvePositions(
    int nTipMask,       // Enabled tips
    int nValvePos )     // Valve position
                        //   0 => Syringe to tip
                        //  90 => peri to tip
                        // 180 => peri to system liquid
                        // 270 => Syringe to system liquid

{
    int i;
    int nRet;
    int nTip = 1;
    int nDilutors = 0;
    int hDilutors[8];
    int bActive[8];
    int nValves[8];
    int nErrors[8];
    int nMaxTips = MSL_NumberOfDilutors();

    //-----------------------------------------------------
    // Initialize arrays
    //-----------------------------------------------------
    for( i = 0; i < nMaxTips; i++ )
    {
        // Move this tip?
        if( (nTip & nTipMask) != 0 )
        {
            hDilutors[nDilutors] = i + 1;
            bActive[nDilutors]   = 1;
            nValves[nDilutors]   = nValvePos;
            nErrors[nDilutors]   = 0;
            nDilutors++;
        }

        // Advance to next tip
        nTip *= 2;
    }


    //-----------------------------------------------------
    // If the instrument is not open, don't bother
    //-----------------------------------------------------
    if( (MSL_IsInstrumentOpen()   == 0) ||
        (EGS_GetEvaluationLevel() != 0) ) return 0;


    //-----------------------------------------------------
    // Turn the valves
    //-----------------------------------------------------
    nRet = MSL_DilutorsTurnValves(
            nDilutors,
            hDilutors,
            bActive,
            nValves,
            nErrors );

    return nRet;
}


/*******************************************************************************
*
*    ValvesPeriToSysLiq()
*
*******************************************************************************/

int ValvesPeriToSysLiq()
{
    int i, nRet, nTips, nMask;

    //-----------------------------------------------------
    // If the instrument is not open, don't bother
    //-----------------------------------------------------
    if( (MSL_IsInstrumentOpen()   == 0) ||
        (EGS_GetEvaluationLevel() != 0) ) return 0;

    //-----------------------------------------------------
    // Position all valves Peri to System Liquid
    //-----------------------------------------------------
    nTips = MSL_NumberOfDilutors();
    nMask = 0;
    for( i = 0; i<nTips; i++ )
        nMask = (nMask << 1) | 1;
    nRet = SetValvePositions( nMask, 180 );

    return nRet;
}


/*******************************************************************************
*
*    PrimeManifoldPreferences
*
*******************************************************************************/

int PrimeManifoldPreferences(
    double dPurgeVol1;      // purge volume for first valve (steps)
    double dPurgeVol2;      // purge volume for remaining valves (steps)
    double dPurgeVol3;      // post-purge volume (steps)
    double dPeriFlowrate,   // ul/sec
    double dPeriSpeed,      // step/sec to deliver flow rate
    double dPeriRamp,       // step/sec/sec to deleiver flow rate
    int iPeriCurrent)       // motor current (0=don't change)
{
    g_dPurgeVol1 = dPurgeVol1;
    g_dPurgeVol2 = dPurgeVol2;
    g_dPurgeVol3 = dPurgeVol3;
    g_dPeriFlowrate = dPeriFlowrate;
    g_dPeriSpeed = dPeriSpeed;
    g_dPeriRamp = dPeriRamp;
    g_iPeriCurrent = iPeriCurrent;
}


/*******************************************************************************
*
*    PrimeManifoldPurge
*
*******************************************************************************/

int PrimeManifoldPurge()
{
    int i, nRet, nTips, nStartMask, nMask;
    double dVol_Steps, dVol_ul;

    //-----------------------------------------------------
    // If the instrument is not open, don't bother
    //-----------------------------------------------------
    if( (MSL_IsInstrumentOpen()   == 0) ||
        (EGS_GetEvaluationLevel() != 0) ) return 0;

    nTips = MSL_NumberOfDilutors();
    nStartMask = 1 << nTips - 1;

    // Position all valves SyringeToTip
    nMask = 0;
    for( i = 0; i<nTips; i++ )
        nMask = (nMask << 1) | 1;
    nRet = SetValvePositions( nMask, 0 );
//    MSL_WriteFile( "PrimeManifoldDump.txt",
//        "\r\nSpeed=%f, Flowrate=%f, Ramp=%f, Current=%d\r\n",
//        g_dPeriSpeed,g_dPeriFlowrate,g_dPeriRamp,g_iPeriCurrent);
//    MSL_WriteFile( "PrimeManifoldDump.txt",
//        "Initial valve mask=%x\r\n", nMask);

    nStartMask = 1 << nTips - 1;
    nMask = nStartMask;
    for( i = 0; i<nTips; i++ )
    {
        // Set the next syringe valve to PeriToSysLiq
        nRet = SetValvePositions( nStartMask, 180 );

        // Get volume based on first time or not
        if(i==0)
            dVol_Steps = g_dPurgeVol1;
        else
            dVol_Steps = g_dPurgeVol2;

        // Convert volume from steps to ul
        dVol_ul = dVol_Steps * g_dPeriFlowrate / g_dPeriSpeed;

        // Run the peripump
//        MSL_WriteFile( "PrimeManifoldDump.txt",
//            "Mask=%x, Volume(steps)=%f, Volume(uL)=%f\r\n",
//            nMask, dVol_Steps, dVol_ul);
        nRet = MSL_RunPeriPump(
            dVol_ul,        // volume (ul)
            g_dPeriSpeed,   // speed (step/sec to deliver flow rate)
            g_dPeriFlowrate,// flow rate (ul/sec)
            g_dPeriRamp,    // ramp (step/sec/sec to deliver flow rate)
            g_iPeriCurrent, // motor current (0=don't change)
            0);             // post-move delay (ms)

        // select next valve
        nMask = (nMask >> 1) | nStartMask;
    }

    // Final purge with all valves still at PeriToSysLiq
    dVol_ul = g_dPurgeVol3 * g_dPeriFlowrate / g_dPeriSpeed;
    nRet = MSL_RunPeriPump(
        dVol_ul,        // volume (ul)
        g_dPeriSpeed,   // speed (step/sec to deliver flow rate)
        g_dPeriFlowrate,// flow rate (ul/sec)
        g_dPeriRamp,    // ramp (step/sec/sec to deliver flow rate)
        g_iPeriCurrent, // motor current (0=don't change)
        0);             // post-move delay (ms)
//    MSL_WriteFile( "PrimeManifoldDump.txt",
//        "Final purge: Volume(steps)=%f, Volume(uL)=%f\r\n",
//        g_dPurgeVol3, dVol_ul);
}


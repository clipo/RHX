/******************************************************************************
*
*   P03_MoveToXYZ()
*
*   <Reserved for text entered into the procedure's comment page.>
*
******************************************************************************/

int P03_MoveToXYZ()
{
    MP2_PROC_CONTEXT_DEF *pPC = &P03_MoveToXYZ();
    int  nRet;              // Funct. return value
    int  nFileIndex = 0;    // Current File Index
    int  nLoopCount = 0;    // Number of unskipped procedure loops
    int  bDone;             // Last procedure loop flag


    // Set the current procedure context.
    MSL_SetCurrentProcContext( pPC, 0, 0 );

    // Toplevel procedures start with dilutor number 1.
    EGS_SetNextDilutor( 1 );

        // first -- get the crucible...
        
        
        nRet = Uf_moveToXYZ( pPC,100,100,100 );
        if( nRet ==  3 ) return -1;    // Check for abort
        if( nRet == 12 ) return  0;    // Check for done

        // Release any auto allocated strings.
        MSL_SetRtFileStringAutoAlloc( 0 );

    return 0;

} //<End >

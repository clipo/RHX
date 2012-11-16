// The name and path of this test.
char *pszTestName = "moveToXY";
char *pszTestPath = "c:\\packard\\janus\\bin";





 

/******************************************************************************
*
*   main()
*
******************************************************************************/

int main(int argc, char **argv)
{
    int nErr;

    // Set the EGS dump table and single step modes as well as
    // the evaluation level.
    EGS_SetDumpMode( 0 );
    EGS_SetSingleStep( 0 );
    EGS_SetEvaluationLevel( 0 );

    // Load Instrument Data
    nErr = MSL_CreateMachine(argv[0]);
    if( nErr ) return;

    // Initialize Instrument
    nErr = MSL_InitializeMachine( 0 );
    if( nErr ) return;
 
    nErr = P03_MoveToXYZ();
    if( nErr ) return;



}



// End of Script
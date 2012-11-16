/******************************************************************************
*
*   Runtime Variable Definitions
*
******************************************************************************/

int		Balance_X = 400;

int		Balance_Y = 400;

int 	Balance_Y_pre = 395;

int		Balance_Z_raised = 250;

int 	Balance_Z_lowered = 255;

int		Balance_Theta = 90;

int		Samples_X = 5;
int 	Samples_Y = 5;

int		Number_of_Samples = 25;


int		Balance_Z_Lift = 390;


int    Rt_nNbrOfErrorsX = 0;
int    Rt_nNbrOfErrorsY = 0;
int    Rt_nNbrOfErrorsZ = 0;
int    Rt_nNbrOfErrorsG = 0;
int    Rt_nNbrOfErrorsT = 0;
char   Rt_szMoveTextX[260];
char   Rt_szMoveTextY[260];
char   Rt_szMoveTextZ[260];
char   Rt_szMoveTextG[260];
char   Rt_szMoveTextT[260];
int    Rt_nNbrOfMovesMade   = 0;
double Rt_dXSpeed   = 420;
double Rt_dXRamp    = 550;
double Rt_dYSpeed   = 470;
double Rt_dYRamp    = 470;
double Rt_dZSpeed   = 100;
double Rt_dZRamp    = 1000;
double Rt_dTSpeed   = 100;
double Rt_dTRamp    = 100;
double Rt_dGSpeed   = 60;
double Rt_dGRamp    = 60;
//------------------------------------------------
// Uf_moveToXYZ()
//------------------------------------------------

int Uf_moveToXYZ(    // 0=Normal; 3=Abort; 12=Stop Procedure
    char*  pPCX,  // Address of procedure context information
    int gotoX,		// X location, etc.
	int gotoY,
	int gotoZ)
{
    int nRet = 0;                       // Load return value into nRet
    MP2_PROC_CONTEXT_DEF* pPC = pPCX;   // Cast pPCX into local procedure context ptr

    int i, nMotorMask;
    int WAIT=1, NOWAIT=0;
    int SIGNAL=1, NOSIGNAL=0;
    int bFaulted, bAnyFaulted, iButton;
    int zmotors;

    // motor IDs
    int nXMotor = 0x01;
    int nYMotor = 0x02;
    int nZMotor = 0x04;
    int nTMotor = 0x08;
    int nGMotor = 0x10;
    int nAllMotors = nXMotor | nYMotor | nZMotor | nTMotor | nGMotor;

    // motor targets
    double dXTarget, dYTarget, dZTarget, dTTarget, dGTarget;

    // motor min & max positions
    double dXMin = 0.0,    dXMax = 1000.0;
    double dYMin = 0.0,    dYMax = 325.0;
    double dZMin = 0.0,    dZMax = 245.0;
    double dTMin = -160.0, dTMax = 180.0;
    double dGMin = 0.0,    dGMax = 35.0;
    
    //------------------------------------------------------------
    // Move gripper motors
    //------------------------------------------------------------
    
    if( MSL_IsInstrumentOpen() )
    {
				// set targets.
                dXTarget = gotoX;
                dYTarget = gotoY;
                dZTarget = gotoZ;
                dTTarget = 90;       

        while(1)
        {
            bAnyFaulted = 0;
        
            printf( "\nX min,max,target = %f,%f,%f", dXMin, dXMax, dXTarget );
            printf( "\nY min,max,target = %f,%f,%f", dYMin, dYMax, dYTarget );
            printf( "\nZ min,max,target = %f,%f,%f", dZMin, dZMax, dZTarget );
           
         	//now move to XYZ
       	
            GRIP_MoveAbsolute(dXTarget, dYTarget, dZTarget, dTTarget, 0, nMotorMask, WAIT, NOSIGNAL);

            GRIP_GetIsXFaulted(&bFaulted);
            if(bFaulted)
            {
                Rt_nNbrOfErrorsX ++;
                bAnyFaulted = 1;
            }

            GRIP_GetIsYFaulted(&bFaulted);
            if(bFaulted)
            {
                Rt_nNbrOfErrorsY ++;
                bAnyFaulted = 1;
            }

            GRIP_GetIsZFaulted(&bFaulted);
            if(bFaulted)
            {
                Rt_nNbrOfErrorsZ ++;
                bAnyFaulted = 1;
            }

            GRIP_GetIsTFaulted(&bFaulted);
            if(bFaulted)
            {
                Rt_nNbrOfErrorsT ++;
                bAnyFaulted = 1;
            }

            GRIP_GetIsGFaulted(&bFaulted);
            if(bFaulted)
            {
                Rt_nNbrOfErrorsG ++;
                bAnyFaulted = 1;
            }

            if(bAnyFaulted)
            {
                iButton=MSL_MessageDialog(0,"Motor Faulted","A gripper motor has faulted!",2,4,2,0);
                GRIP_ClearAllFaults();
                if(iButton == 3)
                    // retry
                    continue;
                if(iButton == 5)
                    // ignore
                    break;
                if(iButton == 4)
                    // abort
                    return 3;
            }
            else
                break;
   		}
    }
}
 
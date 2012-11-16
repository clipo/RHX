/////////////////////////////////////////////////////////////////////
//
//	File:	HeaterControlletOption.s
//	Version:	12
//	Date:	March 26, 2004
//
//	Author:	Timothy Olaska
//			Jie Liang
//
//	Description:
//	This file contains functions that interface to the CAL control's  
//	model 3300 temperature controller.  The following functions are 
//	supported:
//		Check to see if unit responds to commands
//		Set the desired temperature
//		Read current temperature
//		Read the Set temperature.
//		Check temperature limits
//
//	History:
//		Version 3 added selection of communication port.
//		Version 4 adds capability to set & wait for temperature.
//		Version 5 adds checks for temperature renges.
//		Version 6 adds checks for disconnected plate.
//		Version 7 fixes problems with set point locking.
//		Version 8 adds front panel parameter locking
//		Version 9 moves all functionality to this file.
//		Version 10 standardizes all of the fatal error messages.
//		Version 11 implements safety shut down
//		Version 12 implements backward compatability with Version 10 or earlier
//
//////////////////////////////////////////////////////////////////////////

// "Defined" global constants -- MSL does not allow #define
int TRUE             = 1;
int FALSE            = 0;
int ON               = 1;
int OFF              = 0;
int YES              = 1;
int NO               = 0;
int PASS             = 1;
int FAIL             = 0;

// Communication Constants
int Parity = 0;       	// 0 -> None, 1 -> odd, 2 -> even, 3 -> mark, 4 -> space
int BaudRate = 9600;
int DataBits = 8;
int StopBits = 0;     	// 0 -> 1 stop bit, 1 -> 1.5, 2 -> 2

// Temperature controller constants: defined by the equipment spec
//    for the CAL3300.
unsigned char REG_WRITE = 0x06;	// Write a register command byte
unsigned char BIT_WRITE = 0x05;	// Write a bit to a register 
unsigned char RAMP_OFF = 0x00;
unsigned char RAMP_ON = 0x01;

int PURGE_NONE   = 0;
int PURGE_BEFORE = 1;
int PURGE_AFTER  = 2;

//
// CRCadder:  This function calculates a Ciclic Redundancy Code for use in
//    the communications protocol set by the Cal controller.

int CRCadder (int Length, unsigned char *Mssg)
{
    // NOTE: The math behind the CRC calculation requires that the 
    //    Mssg[] array be of type: unsigned char because it is
    //    promoted to type "int" VIA "thisbyte" variable.

    int crc, i, shift, thisbyte, lastbit;
    crc = 0xffff;

    // Go through the loop for each char in the Mssg, Length.
    for (i = 0; i < Length; i++)
    {
        thisbyte = Mssg[i];
        crc = crc ^ thisbyte;

        // Go through eight bits of the byte
        for (shift = 1; shift <= 8; shift++)
        {
            lastbit = crc & 0x0001;
            crc = (crc >> 1) & 0x7fff;
            if (lastbit == 1)
            {
                crc = crc ^ 0xa001;
            }
        }
    }
    Mssg[Length + 1] = (char) ((crc >> 8) & 0xff);
    Mssg[Length] = (char) (crc & 0xff);

    return 0;
}


//////////////////////////////////////////////////////////////////////////////
//
// TemperatureSet:  This function receives the request for a temp setting
//	and sends specified value to the selected controller according to the 
//	Cal 3300 protocol.  In particular note that there are five commands to
//	send.  The first two lock out the front panel buttons.  The third actually
//	transmits the temperature setting to the appropriate register.  The last two
//	reenable the front panel. 

int TemperatureSet (int Unit, double Temp, int CommPort)
{
    // This function 
    // Variables
    int T, crc, CommHandle;
    int i, shift, thisbyte, lastbit, NumRead;
    unsigned char Cmmd[10];
    int MssgSize = 8;


    // Clear all communication ports
    // MSL_RemoteClearDevices ();

    // Open Communication channel
    CommHandle = MSL_RemoteOpenCOMM ( CommPort, "\r\n\t" ); 
    MSL_RemoteSetCOMMOptions (CommHandle, BaudRate, Parity, DataBits, StopBits );

    // Message load-up 1: This message is to precede a security locking message
    Cmmd[0] = Unit;  // Addresses the specific controller
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x03;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x05;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;    // This last byte should never be transmitted, but its '\r', carriage
                       //    return, value will halt RemoteSend if encountered by MSL.

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);

    // Gives the controller some time to process the command.
    Sleep (300);       

    // Message load-up 2: This is the security frontpanel lockout message.
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x15;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x00;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // This is the command that transmits the temperature.
    // Convert Temp into a form usable by the controller
    // The resolution of the controller is in tenths of a degree.
    // Thes temperature is multiplied by ten to be in tenths.
    T = (int)(Temp * 10);

    // Message load-up 3: This message sets the temperature by writing to the appropriate register.
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x00;    // High byte of register address
    Cmmd[3] = 0x7f;    // Low byte of register address

    // Temperature type conversion into two bytes for serial transmission
    Cmmd[4] = (unsigned char) ((T >> 8) & 0xff); // MSB
    Cmmd[5] = (unsigned char) (T & 0xff);        // LSB

    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 4
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x03;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x06;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 5
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x16;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x00;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);

    Sleep (300);

    // Close Commnication channel
    MSL_RemoteCloseDevice ( CommHandle );

    return 0;
}


// ---------------------------------------------------------------------------
//

int RampSoak (int Unit, double Temp, int CommPort, int SafetyTimeout, unsigned char RampOn)
{
    // This function 
    // Variables
    int T, crc, CommHandle, SoakTime, RampRate = 600;
    int i, shift, thisbyte, lastbit, NumRead;
    unsigned char Cmmd[10];
    int MssgSize = 8;
	char Title[100];


    // Clear all communication ports
    // MSL_RemoteClearDevices ();

    // Open Communication channel
    CommHandle = MSL_RemoteOpenCOMM ( CommPort, "\r\n\t" ); 
    MSL_RemoteSetCOMMOptions (CommHandle, BaudRate, Parity, DataBits, StopBits );

    // Message load-up 1: This message is to precede a security locking message
    Cmmd[0] = Unit;  // Addresses the specific controller
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x03;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x05;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;    // This last byte should never be transmitted, but its '\r', carriage
                       //    return, value will halt RemoteSend if encountered by MSL.

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);

    // Gives the controller some time to process the command.
    Sleep (300);       

    // Message load-up 2: This is the security frontpanel lockout message.
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x15;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x00;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // This is the command that transmits the temperature.
    // Convert Temp into a form usable by the controller
    // The resolution of the controller is in tenths of a degree.
    // Thes temperature is multiplied by ten to be in tenths.
    T = (int)(Temp * 10);

    // Message load-up 3.1: This message sets the temperature by writing to the appropriate register.
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x00;    // High byte of register address
    Cmmd[3] = 0x7f;    // Low byte of register address

    // Temperature type conversion into two bytes for serial transmission
    Cmmd[4] = (unsigned char) ((T >> 8) & 0xff); // MSB
    Cmmd[5] = (unsigned char) (T & 0xff);        // LSB

    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 3.2: This message sets the ramp rate.
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x02;    // High byte of register address
    Cmmd[3] = 0xd0;    // Low byte of register address

    // Ramp rate type conversion into two bytes for serial transmission
    Cmmd[4] = (unsigned char) ((RampRate >> 8) & 0xff); // MSB
    Cmmd[5] = (unsigned char) (RampRate & 0xff);        // LSB

    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 3.3: This message sets the soak time.
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x02;    // High byte of register address
    Cmmd[3] = 0xd2;    // Low byte of register address

	// Add extra 15 minutes to the soak time to make sure the heater
	// won't be automatically shut down too early.
    SoakTime = (SafetyTimeout + 15) * 10;
    // Soak time type conversion into two bytes for serial transmission
    Cmmd[4] = (unsigned char) ((SoakTime >> 8) & 0xff); // MSB
    Cmmd[5] = (unsigned char) (SoakTime & 0xff);        // LSB

    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 3.4: This message sets ramp on/off/hold.
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x03;    // High byte of register address
    Cmmd[3] = 0xd4;    // Low byte of register address

    // Soak time type conversion into two bytes for serial transmission
    Cmmd[4] = 0x00;
    Cmmd[5] = RampOn;

    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 4
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x03;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x06;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 5
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x16;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x00;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);

    Sleep (300);

    // Close Commnication channel
    MSL_RemoteCloseDevice ( CommHandle );

    return 0;
}


// ---------------------------------------------------------------------------
//
double GetCurrentTemp (int Unit, int CommPort)
{
    // Constants
    int Parity = 0;       // 0 -> None, 1 -> odd, 2 -> even, 3 -> mark, 4 -> space
    int BaudRate = 9600;
    int DataBits = 8;
    int StopBits = 0;     // 0 -> 1 stop bit, 1 -> 1.5, 2 -> 2
    int PURGE_NONE   = 0;
    int PURGE_BEFORE = 1;
    int PURGE_AFTER  = 2;
    int REG_READ = 0x03;    // Read register function code for CAL3300

    // Variables
    double TempSetting = 0;
    int crc, CommHandle;
    int i, shift, thisbyte, lastbit, NumRead;
    char mssgA[10];
    unsigned char RtnMssg[25], *pBuffer;
    int highbyte, lowbyte;
    int MssgSize = 8;
    int ReceiveMssgSize = 10;

    pBuffer = &RtnMssg[0];

    // Open Communication channel
    CommHandle = MSL_RemoteOpenCOMM ( CommPort, "\r\n\t" ); 
    MSL_RemoteSetCOMMOptions (CommHandle, BaudRate, Parity, DataBits, StopBits );


    // Load up Return message buffer, terminate with a null.
    for (i = 0;  i < 15; i++)
        RtnMssg[i] = (0x41 + i);
   RtnMssg[15] = 0;

    // Message load-up
    mssgA[0] = Unit;
    mssgA[1] = REG_READ;
    mssgA[2] = 0x00;    // Current temperature Register high addr.
    mssgA[3] = 0x1c;    // Current temperature Register low addr.
    mssgA[4] = 0x00;
    mssgA[5] = 0x01;
    mssgA[6] = 0x00;
    mssgA[7] = 0x00;
    mssgA[8] = 0x0d;

    crc = 0xffff;
    for (i = 0; i < 6; i++)
    {
        thisbyte = mssgA[i];
        crc = crc ^ thisbyte;
        for (shift = 1; shift <= 8; shift++)
        {
            lastbit = crc & 0x0001;
            crc = (crc >> 1) & 0x7fff;
            if (lastbit == 1)
            {
                crc = crc ^ 0xa001;
            }
        }
    }
    mssgA[7] = (crc >> 8) & 0xff;
    mssgA[6] = crc & 0xff;

    // Now, send the five fixed messages
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", mssgA[0], mssgA[1], mssgA[2], mssgA[3], mssgA[4], mssgA[5], mssgA[6], mssgA[7]);

    Sleep (500);

    // Get the temperature
    MSL_RemoteGetString( CommHandle, PURGE_AFTER, 8, 1, &NumRead, pBuffer);
    TempSetting = (((RtnMssg[3] << 8) + RtnMssg[4])/10.0);


    // Close Commnication channel
    MSL_RemoteCloseDevice ( CommHandle );

    return TempSetting;
}

// ------------------------------------------------------------------------------------

double GetTempSetting (int Unit, int CommPort)
{
    // Constants
    int Parity = 0;       // 0 -> None, 1 -> odd, 2 -> even, 3 -> mark, 4 -> space
    int BaudRate = 9600;
    int DataBits = 8;
    int StopBits = 0;     // 0 -> 1 stop bit, 1 -> 1.5, 2 -> 2
    int PURGE_NONE   = 0;
    int PURGE_BEFORE = 1;
    int PURGE_AFTER  = 2;
    int REG_READ = 0x03;    // Read register function code for CAL3300

    // Variables
    double TempSetting = 0;
    int crc, CommHandle;
    int i, shift, thisbyte, lastbit, NumRead;
    char mssgA[10];
    unsigned char RtnMssg[25], *pBuffer;
    int highbyte, lowbyte;
    int MssgSize = 8;
    int ReceiveMssgSize = 10;

    pBuffer = &RtnMssg[0];

    // Open Communication channel
    CommHandle = MSL_RemoteOpenCOMM ( CommPort, "\r\n\t" ); 
    MSL_RemoteSetCOMMOptions (CommHandle, BaudRate, Parity, DataBits, StopBits );


    // Load up Return message buffer, terminate with a null.
    for (i = 0;  i < 15; i++)
        RtnMssg[i] = (0x41 + i);
   RtnMssg[15] = 0;

    // Message load-up
    mssgA[0] = Unit;
    mssgA[1] = REG_READ;
    mssgA[2] = 0x00;    // Temperature Setting Register high addr.
    mssgA[3] = 0x7f;    // Temperature Setting Register low addr.
    mssgA[4] = 0x00;
    mssgA[5] = 0x01;
    mssgA[6] = 0x00;
    mssgA[7] = 0x00;
    mssgA[8] = 0x0d;

    crc = 0xffff;
    for (i = 0; i < 6; i++)
    {
        thisbyte = mssgA[i];
        crc = crc ^ thisbyte;
        for (shift = 1; shift <= 8; shift++)
        {
            lastbit = crc & 0x0001;
            crc = (crc >> 1) & 0x7fff;
            if (lastbit == 1)
            {
                crc = crc ^ 0xa001;
            }
        }
    }
    mssgA[7] = (crc >> 8) & 0xff;
    mssgA[6] = crc & 0xff;

    // Now, send the five fixed messages
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", mssgA[0], mssgA[1], mssgA[2], mssgA[3], mssgA[4], mssgA[5], mssgA[6], mssgA[7]);

    Sleep (500);

    // Get the temperature
    MSL_RemoteGetString( CommHandle, PURGE_AFTER, 8, 1, &NumRead, pBuffer);
    TempSetting = (((RtnMssg[3] << 8) + RtnMssg[4])/10.0);


    // Close Commnication channel
    MSL_RemoteCloseDevice ( CommHandle );

    return TempSetting;
}


// -------------------------------------------------------------------------------
//    This function will establish whether a given unit is "on-line"  by trying
//       to change its setting and then back again.  Return value is non-zero
//       if the test passes, i.e. selected controller is readable and writable.

int ControllerCheck (int Unit, int CommPort)
{
    int Check = 0;   // Default is not present
    double CurrentTempSetting = 0.0;
    double CurrentTempReading = 0.0;
    double AlteredTemp = 0.0;

    // Read in current Temperature setting, save value
    CurrentTempReading = GetCurrentTemp ( Unit, CommPort );
    CurrentTempSetting = GetTempSetting ( Unit, CommPort );

    // Change Temp setting to some other value for a brief time
    if ( CurrentTempSetting < 2.0)
    {
        AlteredTemp = 3.0;
        TemperatureSet (Unit, AlteredTemp, CommPort);
    }

    else
    {
        AlteredTemp = 1.0;
        TemperatureSet (Unit, AlteredTemp, CommPort);
    }

    // Read in new temperature setting, check against setting
    if (AlteredTemp != GetTempSetting ( Unit, CommPort ))
    {
        // Unit not returning correct response, return error code
        return 0;
    }

    // Otherwise, The unit is responding, reset Temp and leave
    TemperatureSet (Unit, CurrentTempSetting, CommPort);
    return 1;

}

// --------------------------------------------------------------

int CheckTempLimits (double Temp)
{
    double MAXTEMP = 70.0;
    double MINTEMP = 0.0;

    if ((Temp < MAXTEMP) && (Temp > MINTEMP))
        return 1;

    else
        return 0;

}

// ------------------------------------------------------------------------------------

int ShutDownAllTiles (int CommPort)
{
    // Set the temperature of all tiles to Room Temperature.
    //    20 degrees insurtes that the temperature is below Room temp
    RampSoak (1, 20.0, CommPort, 0, RAMP_OFF);
    RampSoak (2, 20.0, CommPort, 0, RAMP_OFF);
    RampSoak (3, 20.0, CommPort, 0, RAMP_OFF);
    RampSoak (4, 20.0, CommPort, 0, RAMP_OFF);

    return 0;
}

//
// ---------------------------------------------------------------------------
//
int GetDisplayByte (int Unit, int CommPort)
{
    // Constants
    int Parity = 0;       // 0 -> None, 1 -> odd, 2 -> even, 3 -> mark, 4 -> space
    int BaudRate = 9600;
    int DataBits = 8;
    int StopBits = 0;     // 0 -> 1 stop bit, 1 -> 1.5, 2 -> 2
    int PURGE_NONE   = 0;
    int PURGE_BEFORE = 1;
    int PURGE_AFTER  = 2;
    int REG_READ = 0x03;    // Read register function code for CAL3300

    // Variables
    double TempSetting = 0;
    int crc, CommHandle, Num = 0, Result = 0;
    int i, shift, thisbyte, lastbit, NumRead;
    char mssgA[10];
    unsigned char RtnMssg[25], *pBuffer;
    int highbyte, lowbyte;
    int MssgSize = 8;
    int ReceiveMssgSize = 10;

    pBuffer = &RtnMssg[0];

    // Open Communication channel
    CommHandle = MSL_RemoteOpenCOMM ( CommPort, "\r\n\t" ); 
    MSL_RemoteSetCOMMOptions (CommHandle, BaudRate, Parity, DataBits, StopBits );


    // Load up Return message buffer, terminate with a null.
    for (i = 0;  i < 15; i++)
        RtnMssg[i] = (0x41 + i);
   RtnMssg[15] = 0;

    // Message load-up
    mssgA[0] = Unit;
    mssgA[1] = REG_READ;
    mssgA[2] = 0x03;    // Display Register high addr.
    mssgA[3] = 0x06;    // Display Register low addr.
    mssgA[4] = 0x00;
    mssgA[5] = 0x01;
    mssgA[6] = 0x00;
    mssgA[7] = 0x00;
    mssgA[8] = 0x0d;

    CRCadder (6, mssgA);

    // Now, send  message
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", mssgA[0], mssgA[1], mssgA[2], mssgA[3], mssgA[4], mssgA[5], mssgA[6], mssgA[7]);

    Sleep (500);

    // Get the response
    MSL_RemoteGetString( CommHandle, PURGE_AFTER, 8, 1, &NumRead, pBuffer);

    // Interpret return data
    Num = RtnMssg[4]; 

    // Check bit 5 for error signal from heater controller.
    if (Num & 0x20) 
        if((Num & 0x3f) == 0x26)
            Result = -1;

    // Close Commnication channel
    MSL_RemoteCloseDevice ( CommHandle );

    return Result;
}

//
// ---------------------------------------------------------------------------------------------
//

int TemperatureLock (int Unit, int CommPort)
{
    // This function 
    // Variables
    int T, crc, CommHandle;
    int i, shift, thisbyte, lastbit, NumRead;
    unsigned char Cmmd[10];
    int MssgSize = 8;


    // Clear all communication ports
    // MSL_RemoteClearDevices ();

    // Open Communication channel
    CommHandle = MSL_RemoteOpenCOMM ( CommPort, "\r\n\t" ); 
    MSL_RemoteSetCOMMOptions (CommHandle, BaudRate, Parity, DataBits, StopBits );

    // Message load-up 1: This message is to precede a security locking message
    Cmmd[0] = Unit;  // Addresses the specific controller
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x03;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x05;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;    // This last byte should never be transmitted, but its '\r', carriage
                       //    return, value will halt RemoteSend if encountered by MSL.

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);

    // Gives the controller some time to process the command.
    Sleep (300);       

    // Message load-up 2: This is the security frontpanel lockout message.
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;;
    Cmmd[2] = 0x15;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x00;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 3: 
    Cmmd[0] = Unit;
    Cmmd[1] = BIT_WRITE;;
    Cmmd[2] = 0x00;    // High byte of register address lock/unlock
    Cmmd[3] = 0x28;    // Low byte of register address

    // Temperature type conversion into two bytes for serial transmission
    Cmmd[4] = 0xff; // MSB
    Cmmd[5] = 0xff;        // LSB

    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 4
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x03;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x06;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 5
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x16;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x00;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);

    Sleep (300);

    // Close Commnication channel
    MSL_RemoteCloseDevice ( CommHandle );

    return 0;
}

//
// ---------------------------------------------------------------------------------------------
//

int AllLock (int Unit, int CommPort)
{
    // This function 
    // Variables
    int T, crc, CommHandle;
    int i, shift, thisbyte, lastbit, NumRead;
    unsigned char Cmmd[10];
    int MssgSize = 8;


    // Clear all communication ports
    // MSL_RemoteClearDevices ();

    // Open Communication channel
    CommHandle = MSL_RemoteOpenCOMM ( CommPort, "\r\n\t" ); 
    MSL_RemoteSetCOMMOptions (CommHandle, BaudRate, Parity, DataBits, StopBits );

    // Message load-up 1: This message is to precede a security locking message
    Cmmd[0] = Unit;  // Addresses the specific controller
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x03;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x05;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;    // This last byte should never be transmitted, but its '\r', carriage
                       //    return, value will halt RemoteSend if encountered by MSL.

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);

    // Gives the controller some time to process the command.
    Sleep (300);       

    // Message load-up 2: This is the security frontpanel lockout message.
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;;
    Cmmd[2] = 0x15;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x00;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 3: 
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;;
    Cmmd[2] = 0x01;    // High byte of register address lock/unlock
    Cmmd[3] = 0x9c;    // Low byte of register address

    // Temperature type conversion into two bytes for serial transmission
    Cmmd[4] = 0x03;     // MSB
    Cmmd[5] = 0x03;     // LSB

    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 4
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x03;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x06;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 5
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x16;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x00;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);

    Sleep (300);

    // Close Commnication channel
    MSL_RemoteCloseDevice ( CommHandle );

    return 0;
}


int ParameterUnLock (int Unit, int CommPort)
{
    // This function 
    // Variables
    int T, crc, CommHandle;
    int i, shift, thisbyte, lastbit, NumRead;
    unsigned char Cmmd[10];
    int MssgSize = 8;


    // Clear all communication ports
    // MSL_RemoteClearDevices ();

    // Open Communication channel
    CommHandle = MSL_RemoteOpenCOMM ( CommPort, "\r\n\t" ); 
    MSL_RemoteSetCOMMOptions (CommHandle, BaudRate, Parity, DataBits, StopBits );

    // Message load-up 1: This message is to precede a security locking message
    Cmmd[0] = Unit;  // Addresses the specific controller
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x03;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x05;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;    // This last byte should never be transmitted, but its '\r', carriage
                       //    return, value will halt RemoteSend if encountered by MSL.

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);

    // Gives the controller some time to process the command.
    Sleep (300);       

    // Message load-up 2: This is the security frontpanel lockout message.
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;;
    Cmmd[2] = 0x15;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x00;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 3: 
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;;
    Cmmd[2] = 0x01;    // High byte of register address lock/unlock
    Cmmd[3] = 0x9c;    // Low byte of register address

    // Temperature type conversion into two bytes for serial transmission
    Cmmd[4] = 0x00;     // MSB
    Cmmd[5] = 0x00;     // LSB

    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 4
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x03;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x06;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 5
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x16;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x00;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);

    Sleep (300);

    // Close Commnication channel
    MSL_RemoteCloseDevice ( CommHandle );

    return 0;
}



//
// ---------------------------------------------------------------------------------------------
//

int TemperatureUnLock (int Unit, int CommPort)
{
    // This function 
    // Variables
    int T, crc, CommHandle;
    int i, shift, thisbyte, lastbit, NumRead;
    unsigned char Cmmd[10];
    int MssgSize = 8;


    // Clear all communication ports
    // MSL_RemoteClearDevices ();

    // Open Communication channel
    CommHandle = MSL_RemoteOpenCOMM ( CommPort, "\r\n\t" ); 
    MSL_RemoteSetCOMMOptions (CommHandle, BaudRate, Parity, DataBits, StopBits );

    // Message load-up 1: This message is to precede a security locking message
    Cmmd[0] = Unit;  // Addresses the specific controller
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x03;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x05;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;    // This last byte should never be transmitted, but its '\r', carriage
                       //    return, value will halt RemoteSend if encountered by MSL.

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);

    // Gives the controller some time to process the command.
    Sleep (300);       

    // Message load-up 2: This is the security frontpanel lockout message.
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;;
    Cmmd[2] = 0x15;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x00;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);


    // Message load-up 3: 
    Cmmd[0] = Unit;
    Cmmd[1] = BIT_WRITE;;
    Cmmd[2] = 0x00;    // High byte of register address for lock/unlock
    Cmmd[3] = 0x28;    // Low byte of register address

    // Temperature type conversion into two bytes for serial transmission
    Cmmd[4] = 0x00;        // MSB
    Cmmd[5] = 0x00;        // LSB

    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 4
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x03;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x06;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);
    Sleep (300);

    // Message load-up 5
    Cmmd[0] = Unit;
    Cmmd[1] = REG_WRITE;
    Cmmd[2] = 0x16;    // High byte of register address
    Cmmd[3] = 0x00;    // Low byte of register address
    Cmmd[4] = 0x00;
    Cmmd[5] = 0x00;
    Cmmd[6] = 0x00;
    Cmmd[7] = 0x00;
    Cmmd[8] = 0x0d;

    CRCadder (6, Cmmd);
    MSL_RemoteSendString ( CommHandle, 0, 5, &MssgSize, "%c%c%c%c%c%c%c%c", 
		Cmmd[0], Cmmd[1], Cmmd[2], Cmmd[3], Cmmd[4], Cmmd[5], Cmmd[6], Cmmd[7]);

    Sleep (300);

    // Close Commnication channel
    MSL_RemoteCloseDevice ( CommHandle );

    return 0;
}


//
// --------------------------------------------------------------------------------------------
//

int UnLockAllTiles (int CommPort)
{
    TemperatureUnLock (1, CommPort);
    TemperatureUnLock (2, CommPort);
    TemperatureUnLock (3, CommPort);
    TemperatureUnLock (4, CommPort);

    // Front panel parameters remain 
    //permenantly locked unless you enable the following four lines.
    //ParameterUnlock (1, CommPort);
    //ParameterUnlock (2, CommPort);
    //ParameterUnlock (3, CommPort);
    //ParameterUnlock (4, CommPort);

    return 0;
}

//
// ---------------------------------------------------------------------------------------------
//

int TempReader (int CommPort, int Heater_Tile)
{
    // Variables
    int i,  
        TSwitch = 0, 
        AllDone = 0, 
        DelayCount = 0, 
        DELAYSECONDS = 40,  // Estimated to equal 120 seconds
        Num = 0;

    double Temp = 0.0;

    char Title[100], 
         LogLine[80], 
         TempText[10], 
         TimeStr[80],
         ChkMssg[100],
         LogFileName [40];

    time_t ltime;  // Time data structure

    // Assign the name of the data logging file
    sprintf (LogFileName, "HeaterTileLogFile.txt");

    // Communication port Range checking
    if ((CommPort > 10) || (CommPort < 1))
    {
        // Report comport range error to user and return abort code.
        MSL_MessageDialog 
        (
            0,
            "Error",
            "Communication port number is out of range \nPlease enter a number between 1 and 10.\nFATAL ERROR.",
            4, // 1 = STOP
            1,
            1,
            0
        );
        return 3;
    }

    // Heater Tile Range checking: There are at most four tiles, numbered 1 through four.
    if ((Heater_Tile > 4) || (Heater_Tile < 1))
    {
        // Report heater tile number range error to user and return abort code.
        sprintf (Title, "Heater tile number is out of range.\nPlease enter a number between 1 and 4.\nFATAL ERROR.");
        MSL_MessageDialog 
        (
            0,
            "Error",
            Title,
            4, // 1 = STOP
            1,
            1,
            0
        );
        return 3;
    }

    // Check serial communication
    if (ControllerCheck (Heater_Tile, CommPort) == 0)
    {
        // Report error to user and return abort code.
        sprintf (Title, "Communication not established. Please check\nRS-232 connections and/or selected port number.\nFATAL ERROR.");
        MSL_MessageDialog 
        (
            0,
            "Error",
            Title,
            4, // 1 = STOP
            1,
            1,
            0
        );
        return 3;
    }


    // Check to see that the controller has a heater plate connected.
    Num = GetDisplayByte (Heater_Tile, CommPort);
    if (Num == -1)
    {
        sprintf (ChkMssg, "Heater tile is not connected to the controller\nCheck connections of its cable.\nFATAL ERROR");
        MSL_MessageDialog 
        (
            0,
            "Fatal Error",
            ChkMssg,
            4, // 1 = STOP
            1,
            1,
            0
        );
        return 3;  // Abort, fatal error.
    }
 
    Temp = GetCurrentTemp(Heater_Tile, CommPort);

    // As soon as we use these functions, the front panel locks
    TemperatureLock (Heater_Tile, CommPort);
    AllLock (Heater_Tile, CommPort);

    // Setup read temperature dispaly screen
    sprintf (Title, "Read Temperature");
    sprintf (TempText," %4.1f C", Temp);
    MSL_CreateDialog (0, 1, -1, -1, 26, 11, &Title[0], 1);
    MSL_ShowDialog ( 1, 1, 0);
    MSL_CreateEditBox (1, 2, 15, 1, 7, 1, "Current Temperature","" , TempText, "TEXT", 0, 500, 0, 0, 0); 
    MSL_CreateEditBox (1, 4, 15, 3, 2, 1, "Heater Tile Number  ","" , &Heater_Tile, "INT", 0, 500, 0, 0, 0); 
    MSL_CreatePushBtn ( 1, 3, 10, 6, 7, 2, "OK","", 0, 0, 0); 
    MSL_SetControlFocus (1, 3);

    // Cycle for 120 seconds or until the "OK" button is activated.
    while (!AllDone)
    {
        if (DelayCount++ >= DELAYSECONDS)
            AllDone = 1;

		// On one heater controller, GetCurrentTemp() alone does not work.
		// Adding GetTempSetting() fixes the problem.
		GetTempSetting (Heater_Tile, CommPort);
        Temp = GetCurrentTemp(Heater_Tile, CommPort);
        sprintf (TempText," %4.1f C", Temp);
        MSL_EditSetValue (1, 2, TempText, 0);

        TSwitch = MSL_WaitControl (1, 3, 1.0 );
        if ( TSwitch != 0)
            AllDone = 1;
    }

    // Log the action taken into a data file
    time (&ltime);
    sprintf (TimeStr, "%s", ctime(&ltime));
    TimeStr[strlen (TimeStr) - 1] = 0;

    sprintf (LogLine, "%s\r\n  Read Temperature Tile Number:%d %4.1f C\r\n", TimeStr, Heater_Tile, Temp);
    MSL_WriteFile (LogFileName, "%s", LogLine);

    MSL_DeleteDialog (1,0); // Close out dialog box, free resources.

    return 0;

}

//
// ------------------------------------------------------------------------------------------
//

int TempSetter (int CommPort, double Temperature, int Heater_Tile)
{
    int AllDone = 0, 
        TSwitch = 0, 
        Num = 0;

    char Title[100], 
         LogLine[80], 
         ChkMssg[80], 
         TimeStr[80];    

    time_t ltime;  // Time data structure

    double StartingTemp = 0;

    // Temperature Range checking: the user is only allowed to ask for a temperature between 
    //    room temperature (>= 20 C) and 70 degrees Celsius
    if ((Temperature > 70.0) || (Temperature < 20.0))
    {
        sprintf (Title, "Temperature is out of range. Temperature entered\nshould be between room temperature and 70 Celsius.\nFATAL ERROR.");
        MSL_MessageDialog 
        (
            0,
            "Error",
            Title,
            4, // 4 = STOP icon
            1, // 1 = OK button
            1, 
            0
        );            
        return 3;
    }

    // Communication Port Range checking
    if ((CommPort < 1) || (CommPort > 10))
    {
        sprintf (Title, "Communication port number is out of range.\n Please enter a number between 1 and 10.\nFATAL ERROR.");
         MSL_MessageDialog 
        (
            0,
            "Error",
            Title,
            4, // 4 = STOP icon
            1, // 1 = OK button
            1, 
            0
        );            
        return 3;
    }

    // Heater Tile Range checking
    if ((Heater_Tile < 1) || (Heater_Tile > 4))
    {
        sprintf (Title, "Heater Tile number is out of range.\nPlease use a number between 1 and 4.\nFATAL ERROR.");
        MSL_MessageDialog 
        (
            0,
            "Error",
            Title,
            4, // 4 = STOP icon
            1, // 1 = OK button
            1, 
            0
        );            
        return 3;
    }

    // Check to see that the controller has a heater plate connected.
    Num = GetDisplayByte (Heater_Tile, CommPort);
    if (Num == -1)
    {
        sprintf (Title, "Heater tile is not connected to the controller.\nCheck connections of its cable.\nFATAL ERROR.", Num);
        MSL_MessageDialog 
        (
            0,
            "Fatal Error",
            Title,
            4, // 1 = STOP
            1,
            1,
            0
        );
        return 3;  // Abort, fatal error.
    }

    // Check communication
    if (ControllerCheck (Heater_Tile, CommPort) == 0)
    {
        sprintf (Title, "Communication not established. Please check\nRS-232 connections and/or selected port number.\nFATAL ERROR.");
        MSL_MessageDialog 
        (
            0,
            "Error",
            Title,
            4, // 4 = STOP icon
            1, // 1 = OK button
            1, 
            0
        );            
        return 3;
    }

    // Check current temp.  Do not allow the temperature to be lowered more than 3 degrees.
    //    Three degrees difference is chosen because it is about the maximum overshoot for the controller.
    //    Should the heater be a little higher than its setting, it could not be reset to the same
    //    temperature otherwise.
    //    Note that we do not use temperature setting here because the plate could be hot from a 
    //    previous test but was shut down to room temperature setting.
    StartingTemp = GetCurrentTemp(Heater_Tile, CommPort);
    if (StartingTemp > Temperature + 3.0)
    {
        sprintf (Title, "Temperature selected is lower than\nthe current temperature of the tile.\nFATAL ERROR.");
        MSL_MessageDialog 
        (
            0,
            "Error",
            Title,
            4, // 4 = STOP icon
            1, // 1 = OK button
            1, 
            0
        );            
        return 3;
    }

    // Set the temperature and lokc out the front panel from changing it.
    TemperatureSet (Heater_Tile, Temperature, CommPort);
    TemperatureLock (Heater_Tile, CommPort);

    // Write out to the log file the action taken.
    time (&ltime);
    sprintf (TimeStr, "%s", ctime(&ltime));
    TimeStr[strlen (TimeStr) - 1] = 0;

    sprintf (LogLine, "%s\r\n  Set Temperature  Tile Number:%d  %4.1f C\r\n", TimeStr, Heater_Tile, Temperature);
    MSL_WriteFile ("HeaterTileLogFile.txt", "%s", LogLine);

    return 0;
  }

//
// ------------------------------------------------------------------------------------------
//

int TempSetterEx (int CommPort, double Temperature, int Heater_Tile, int SafetyTimeout)
{
    int AllDone = 0, 
        TSwitch = 0, 
        Num = 0;

    char Title[100], 
         LogLine[80], 
         ChkMssg[80], 
         TimeStr[80];    

    time_t ltime;  // Time data structure

    double StartingTemp = 0;

    // Temperature Range checking: the user is only allowed to ask for a temperature between 
    //    room temperature (>= 20 C) and 70 degrees Celsius
    if (Heater_Tile == 1)
    {
		if ((Temperature > 70.0) || (Temperature < 20.0))
		{
			sprintf (Title, "Temperature is out of range. Temperature entered\nshould be between room temperature and 70 Celsius.\nFATAL ERROR.");
			MSL_MessageDialog 
			(
				0,
				"Error",
				Title,
				4, // 4 = STOP icon
				1, // 1 = OK button
				1, 
				0
			);            
			return 3;
		}
	}
	else
	{
		if ((Temperature > 70.0) || (Temperature < 20.0))
		{
			sprintf (Title, "Temperature is out of range. Temperature entered\nshould be between room temperature and 70 Celsius.\nFATAL ERROR.");
			MSL_MessageDialog 
			(
				0,
				"Error",
				Title,
				4, // 4 = STOP icon
				1, // 1 = OK button
				1, 
				0
			);            
			return 3;
		}
	}

    // Communication Port Range checking
    if ((CommPort < 1) || (CommPort > 10))
    {
        sprintf (Title, "Communication port number is out of range.\n Please enter a number between 1 and 10.\nFATAL ERROR.");
         MSL_MessageDialog 
        (
            0,
            "Error",
            Title,
            4, // 4 = STOP icon
            1, // 1 = OK button
            1, 
            0
        );            
        return 3;
    }

    // Heater Tile Range checking
    if ((Heater_Tile < 1) || (Heater_Tile > 4))
    {
        sprintf (Title, "Heater Tile number is out of range.\nPlease use a number between 1 and 4.\nFATAL ERROR.");
        MSL_MessageDialog 
        (
            0,
            "Error",
            Title,
            4, // 4 = STOP icon
            1, // 1 = OK button
            1, 
            0
        );            
        return 3;
    }

    // Check to see that the controller has a heater plate connected.
    Num = GetDisplayByte (Heater_Tile, CommPort);
    if (Num == -1)
    {
        sprintf (Title, "Heater tile is not connected to the controller.\nCheck connections of its cable.\nFATAL ERROR.", Num);
        MSL_MessageDialog 
        (
            0,
            "Fatal Error",
            Title,
            4, // 1 = STOP
            1,
            1,
            0
        );
        return 3;  // Abort, fatal error.
    }

    // Check communication
    if (ControllerCheck (Heater_Tile, CommPort) == 0)
    {
        sprintf (Title, "Communication not established. Please check\nRS-232 connections and/or selected port number.\nFATAL ERROR.");
        MSL_MessageDialog 
        (
            0,
            "Error",
            Title,
            4, // 4 = STOP icon
            1, // 1 = OK button
            1, 
            0
        );            
        return 3;
    }


    // Check current temp.  Do not allow the temperature to be lowered more than 3 degrees.
    //    Three degrees difference is chosen because it is about the maximum overshoot for the controller.
    //    Should the heater be a little higher than its setting, it could not be reset to the same
    //    temperature otherwise.
    //    Note that we do not use temperature setting here because the plate could be hot from a 
    //    previous test but was shut down to room temperature setting.
    StartingTemp = GetCurrentTemp(Heater_Tile, CommPort);
    if (StartingTemp > Temperature + 3.0)
    {
        sprintf (Title, "Temperature selected is lower than\nthe current temperature of the tile.\nFATAL ERROR.");
        MSL_MessageDialog 
        (
            0,
            "Error",
            Title,
            4, // 4 = STOP icon
            1, // 1 = OK button
            1, 
            0
        );            
        return 3;
    }

    // Set the temperature and lock out the front panel from changing it.
    RampSoak (Heater_Tile, Temperature, CommPort, SafetyTimeout, RAMP_ON);
    TemperatureLock (Heater_Tile, CommPort);

    // Write out to the log file the action taken.
    time (&ltime);
    sprintf (TimeStr, "%s", ctime(&ltime));
    TimeStr[strlen (TimeStr) - 1] = 0;

    sprintf (LogLine, "%s\r\n  Set Temperature  Tile Number:%d  %4.1f C\r\n", TimeStr, Heater_Tile, Temperature);
    MSL_WriteFile ("HeaterTileLogFile.txt", "%s", LogLine);

    return 0;
  }

//
// ---------------------------------------------------------------------------------------------
//

int TempWaiter (int CommPort, int Heater_Tile)
{
    int TRUE = 1, 
        FALSE = 0, 
        AllDone = 0, 
        TSwitch = 0, 
        Num = 0, 
        TempOk = 0, 
        SettlingCounter = 0; 

    int TWOMINUTES = 40;	// Estimated number for 2 minutes

    double Tolerance = 1.0,
           CurrentTemp = 0.0, 
           Temperature = 0.0, 
           TempDelta = 0.0;

    char TempTitle[100], 
         LogLine[80], 
         ChkMssg[80], 
         TempText[10], 
         TimeStr[80];

    time_t ltime;  // Time data structure

    // Communication Port Range checking
    if ((CommPort < 1) || (CommPort > 10))
    {
        sprintf (TempTitle, "Communication port number is out of range.\nPlease enter a number between 1 and 10.\nFATAL ERROR.");
        MSL_MessageDialog 
        (
            0,
            "Error",
            TempTitle,
            4, // 4 = STOP icon
            1, // 1 = OK button
            1, 
            0
        );            
        return 3;
    }
 
   // Heater Tile Range checking
    if ((Heater_Tile < 1) || (Heater_Tile > 4))
    {
        sprintf (TempTitle, "Heater Tile number is out of range.\n Please enter a number between 1 and 4.\nFATAL ERROR");
        MSL_MessageDialog 
        (
            0,
            "Error",
            TempTitle,
            4, // 4 = STOP icon
            1, // 1 = OK button
            1, 
            0
        );            
        return 3;
    }
    // Check communication
    if (ControllerCheck (Heater_Tile, CommPort) == 0)
    {
        sprintf (TempTitle, "Communication not established. Please check\nRS-232 connections and/or entered port number.\nFATAL ERROR.");
        MSL_MessageDialog 
        (
            0,
            "Error",
            TempTitle,
            4, // 4 = STOP icon
            1, // 1 = OK button
            1, 
            0
        );            
        return 3;
    }

    // Check to see that the controller has a heater plate connected.
    Num = GetDisplayByte (Heater_Tile, CommPort);
    if (Num == -1)
    {
        sprintf (TempTitle, "Heater tile is not connected to the controller.\nCheck connections of its cable.\nFATAL ERROR.");
        MSL_MessageDialog 
        (
            0,
            "Fatal Error",
            TempTitle,
            4, // 1 = STOP
            1,
            1,
            0
        );
        return 3;  // Abort, fatal error.
    }

    // Get current setting 
    Temperature = GetTempSetting (Heater_Tile, CommPort);

    // Check to see that this unit has a proper setting
    if (Temperature < 1.0)
    {
        sprintf (TempTitle, "Heater tile has no temperature set");
        MSL_MessageDialog 
        (
            0,
            "Error",
            TempTitle,
            4, // 4 = STOP icon
            1, // 1 = OK button
            1, 
            0
        );            
        return 3;
    }
    if (Heater_Tile == 1)
    {
		if ((Temperature < 20.0) || (Temperature > 70.0))
		{
			sprintf (TempTitle, "Temperature is out of range. Temperature entered\nShould be between room temperature and 70 Celsius.\nFATAL ERROR.");
			MSL_MessageDialog 
			(
				0,
				"Error",
				TempTitle,
				4, // 4 = STOP icon
				1, // 1 = OK button
				1, 
				0
			);            
			return 3;
		}
	}
    else
    {
		if ((Temperature < 20.0) || (Temperature > 70.0))
		{
			sprintf (TempTitle, "Temperature is out of range. Temperature entered\nShould be between room temperature and 70 Celsius.\nFATAL ERROR.");
			MSL_MessageDialog 
			(
				0,
				"Error",
				TempTitle,
				4, // 4 = STOP icon
				1, // 1 = OK button
				1, 
				0
			);            
			return 3;
		}
	}


    // Make a dialog box to display while waiting for the temperature to be reached.
    MSL_CreateDialog (0, 1, -1, -1, 30, 14, "Waiting for Temperature", 1);
    MSL_ShowDialog ( 1, 1, 0);
    sprintf (TempText," %4.1f C", Temperature);
    MSL_CreateEditBox (1, 4, 17, 1, 7, 1, "Target Temperature  ","" , TempText, "TEXT", 0, 500, 0, 0, 0); 

    // Setup the temperature display window
    CurrentTemp = GetCurrentTemp (Heater_Tile,  CommPort);
    sprintf (TempText," %4.1f C", CurrentTemp);

    MSL_CreateEditBox (1, 2, 17, 3, 7, 1, "Current Temperature","" , TempText, "TEXT", 0, 500, 0, 0, 0); 
    MSL_CreateEditBox (1, 5, 17, 5, 2, 1, "Heater Tile Number  ","" , &Heater_Tile, "INT", 0, 500, 0, 0, 0); 
    MSL_CreateEditBox (1, 6, 29, 8, 0, 0, "Pressing CONTINUE Button","" , &Heater_Tile, "INT", 0, 500, 0, 0, 0); 
    MSL_CreateEditBox (1, 7, 29, 9, 0, 0, "resumes the test before        ","" , &Heater_Tile, "INT", 0, 500, 0, 0, 0); 
    MSL_CreateEditBox (1, 8, 29, 10, 0, 0, "target Temp is reached.       ","" , &Heater_Tile, "INT", 0, 500, 0, 0, 0); 
    MSL_CreatePushBtn ( 1, 3, 2, 8, 7, 2, "Continue","", 0, 0, 0); 
    MSL_SetControlFocus (1, 3);

    // Pause for a second
    Sleep (1000);

    // Wait until the temperature is within tolerance of the setting, 
    //    or the cancel button is hit
    while ( !AllDone )
    {
        // Delay 500ms each time through the loop to make 1 second per loop.

		// On one heater controller, GetCurrentTemp() alone does not work.
		// Adding GetTempSetting() fixes the problem.
		GetTempSetting (Heater_Tile, CommPort);
        CurrentTemp = GetCurrentTemp (Heater_Tile,  CommPort);
        sprintf (TempText," %4.1f C", CurrentTemp);
        MSL_EditSetValue (1, 2, TempText, 0);

        // If the temperature is equal to or greater than set value, count the time in seconds
        if (CurrentTemp >= Temperature)
            TempOk = 1;

        if (TempOk == 1)
            SettlingCounter++;

        // Check if two minutes has past.
        if (SettlingCounter >= TWOMINUTES)
            AllDone = 1;

        // Check for push button
        TSwitch = MSL_WaitControl (1, 3, 1.0 );
        if ( TSwitch != 0)
            AllDone = 1;

    }

    // As soon as we talk to the controller, the display will be locked until we shut them all down.
    TemperatureLock (Heater_Tile, CommPort);

    // Log the action and the results.
    time (&ltime);
    sprintf (TimeStr, "%s", ctime(&ltime));
    TimeStr[strlen (TimeStr) - 1] = 0;

    sprintf (LogLine, "%s\r\n  Wait for Temperature  Tile Number:%d  %4.1f C\r\n", TimeStr, Heater_Tile, Temperature);
    MSL_WriteFile ("HeaterTileLogFile.txt", "%s", LogLine);

    MSL_DeleteDialog (1,0);  // Close out dialog box.

    return 0;
}

//
// --------------------------------------------------------------------------------------------
//

int ShutDowner (int CommPort)
{
    int AllDone = 0,  
        TSwitch = 0;

    char TempTitle[100], 
         LogLine[80], 
         TimeStr[80];

    time_t ltime; // Time data structure

    // Communication Port Range checking.  Note that there is no other error checking.  This function
    //    forces the units to be shut off and ignores any error messages.  Thus if any or all of the
    //    controllers fail to communicate, or are not present, the software will carry on to the next 
    //    device in numerical order.
    if ((CommPort < 1) || (CommPort > 10))
    {
        // if in error, notify user with dialog box and return abort code.
        sprintf (TempTitle, "Communication port number is out of range.\nPlease enter a number between 1 and 10.\nFATAL ERROR");
        MSL_MessageDialog 
        (
            0,
            "Error",
            TempTitle,
            4, // 4 = STOP icon
            1, // 1 = OK button
            1, 
            0
        );            
        return 3;
    }

    // Check to see that we can communicate to at least one heater controller
    if ((ControllerCheck (1, CommPort) == 0) &&
        (ControllerCheck (2, CommPort) == 0) &&
        (ControllerCheck (3, CommPort) == 0) &&
        (ControllerCheck (4, CommPort) == 0))
    {
        // if in error, notify user with dialog box and return abort code.
        sprintf (TempTitle, "Communication not established. Please check\nRS-232 connections and/or selected port number.\nFATALERROR");
        MSL_MessageDialog 
        (
            0,
            "Error",
            TempTitle,
            4, // 4 = STOP icon
            1, // 1 = OK button
            1, 
            0
        );            
        return 3;
    }

  

    // This forces the temperature of all tiles to be set below room Temp: i.e. to 20 deg. C
    //    This effectively shuts the tiles off.  Note they only heat, they do not cool.
    ShutDownAllTiles (CommPort);

    // This enables the front panel for manual control.
    UnLockAllTiles (CommPort);

    // Save the results of what is done to the log file.
    time (&ltime);
    sprintf (TimeStr, "%s", ctime(&ltime));
    TimeStr[strlen (TimeStr) - 1] = 0;

    sprintf (LogLine, "%s\r\n  Heater Shut Down\r\n", TimeStr);
    MSL_WriteFile ("HeaterTileLogFile.txt", "%s", LogLine);

    return 0;
}
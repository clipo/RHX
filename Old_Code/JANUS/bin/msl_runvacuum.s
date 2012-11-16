/******************************************************************************
 **                                                                          **
 **     (c) Packard Instrument Company 2000-01                               **
 **                                                                          **
 **                                                                          **
 **     Project: SPE/DNA Workstation                                         **
 **                                                                          **
 **     File: MSL_RUNVACUUM.S                                                **
 **     Version: 1.0                                                         **
 **     Creation Date: 11/08/2000                                            **
 **     Last Modification: 01/19/2001                                        **
 **     Created by: Bruce Tyley (BDT)                                        **
 **     Modified by:                                                         **
 **                                                                          **
 **                                                                          **
 **--------------------------------------------------------------------------**
 **                             Revision History                             **
 **-------+----------+--------+----------------------------------------------**
 **  Rev  |          | Change |                                              **
 **  Nbr  |   Date   |   by   |                 Description                  **
 **-------+----------+--------+----------------------------------------------**
 **  1.01 |          |        |Revision release                              **
 **       +----------+--------+----------------------------------------------**
 **       |          |        |                                              **
 **-------+----------+--------+----------------------------------------------**
 **  1.0  | 01/19/01 |        |Initial release                               **
 **-------+----------+--------+----------------------------------------------**
 **                                                                          **
 **                                                                          **
 **     Description:                                                         **
 **                                                                          **
 **                                                                          **
 ******************************************************************************/


int VC_VacuumStep (char *pPCX)
{
    int status;
    MP2_PROC_CONTEXT_DEF *pPC = pPCX;
    MP2_PROC_CONTEXT_DEF *pParent = pPC->pParentPC;

    status = -1;
    while ((status != 0) && (status != 3) && (status != 12)) {
        status = VC_RunVacuumStep(pParent->szName);
    }

    return(status);
}


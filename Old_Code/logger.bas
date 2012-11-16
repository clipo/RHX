#include "vbcompat.bi"
#include "math.bi"
#include "fbgfx.bi"
#include "datetime.bi"

Dim as WString * 16 balanceRead
Dim adresult As String
Dim weight As Single
Dim elapsed As Double
Dim elapsedquarter As Double
Dim elaspedhour As Double
Dim elaspedmin As Double
Dim elaspedhourquarter As Double
Dim elaspedminquarter As Double
Dim  b1 As Double
Dim  a1 As Double
Dim filename as String
Dim intervalsec as Integer
Dim starttime As String, startdate As String, d1 As Double, d2 As Double
Dim timeSinceStartSec As Double, timeSinceStartMin As Double
Dim startingweight as Double
Dim NumTotalPoints as Integer
Dim NumCurrentPoints as Integer
Dim sampleNum as Integer
Dim setName as String
Dim stopCode as Integer
Dim keyEntry as String
Dim As Long MaxCount 
Dim As String s() , text , Delimiter 
Dim tempHumidityString as String


Public Sub Split(Text As String, Delim As String = " ", Count As Long = -1, Ret() As String)

        Dim As Long x, p
        If Count < 1 Then
                Do 
                        x = InStr(x + 1, Text, Delim)
                        p += 1
                Loop Until x = 0
                Count = p - 1
        ElseIf Count = 1 Then
                ReDim Ret(Count)
                Ret(0) = Text
        Else
                Count -= 1
        End If
        Dim RetVal(Count) As Long
        x = 0
        p = 0
        Do Until p = Count
                x = InStr(x + 1,Text,Delim)
                RetVal(p) = x
                p += 1
        Loop
        ReDim Ret(Count)
        Ret(0) = Left(Text, RetVal(0) - 1 )
        p = 1
        Do Until p = Count
                Ret(p) = Mid(Text, RetVal(p - 1) + 1, RetVal(p) - RetVal(p - 1) )
                p += 1
        Loop
        Ret(Count) = Mid(Text, RetVal(Count - 1) + 1)
        
End Sub





' Number of points
Dim NumPoints as Integer

' Fitted parameters and variance-covariance matrix
DIM AS DOUBLE B(0 TO 1), V(0 TO 1, 0 TO 1)

' Statistical tests
DIM AS TRegTest Test

' Significance level
CONST Alpha = 0.05

' Student's t and Snedecor's F
DIM AS DOUBLE T, F

' Loop variable
DIM AS INTEGER I
' Open Connection to Balance
Open Com "com5:9600,n,8,1,cs0,cd0,ds0,rs" As #1
If Err <> 0 Then
    Print "Error opening COM5:"
    Sleep
    End
end If

' Open Connection to Temp Humidity
Open Com "com6:9600,n,8,1,cs0,cd0,ds0,rs" As #10
If Err <> 0 Then
    Print "Error opening COM6:"
    Sleep
    End
end If


Dim AS Integer SlopeNum
a1 = Now
Print "The current time/date is: "
Print Format(a1, "mm-dd-yyyy hh:mm:ss")
Print

Print "Enter name for output file (e.g., output.csv):  ";
input filename 

Print "Enter date at which the firing finished "
Print "Format: mm-dd-yyyy --> ";
input startdate

Print "Enter time at which the firing finished "
Print "Format (24 hours): hh:mm:ss -->";
input starttime

    d1 = DateValue( startdate ) + TimeValue( starttime )
    d2 = Now()
    timeSinceStartSec = DateDiff("s",d1,d2)
    timeSinceStartMin = int(timeSinceStartSec/60)
Print "Date entered:  ",Format(d1, "mm-dd-yyyy hh:mm:ss")
Print "Seconds elapsed since firing ", timeSinceStartSec
Print "Minutes elapsed since firing ", timeSinceStartMin

Print "Enter sampling interval (in seconds, e.g., 5,10,15,30,120): ";
input intervalsec 

Print "Enter approx. starting weight (g): ";
input startingweight

Print "How many points for slope calculation (e.g., 100) ";
input SlopeNum
if (SlopeNum < 1) then
    SlopeNum = 100
End If

Print "Enter set name (e.g., Mississippian ): ";
input setName
if (setName ="" ) then
    setName="Sherd-"
End If

Print "Enter first sample number (e.g., 1):  ";

' Data
DIM AS DOUBLE X(0 to SlopeNum) 
DIM AS DOUBLE Y(0 to SlopeNum)
DIM AS Double LastNValues(1 to SlopeNum)
DIM AS DOUBLE PreviousNValues(1 to SlopeNum)
Dim as double LastTValues(1 to SlopeNum)
Dim as double PreviousTValues(1 to SlopeNum)
Dim as double slope
Dim as double SB
Dim as double meanWeight
Dim as double stdevWeight
Dim as double elapsedminquarter

' Computed Y values
DIM AS DOUBLE Ycalc(0 to SlopeNum)

intervalsec = intervalsec  * 1000

Open filename for Append As #2
Print "press q to quit"
Print "PointNumber - Sample - Date - ElapsedMin - Weight - Slope - Slope SD - ElapsedMin^1/4 - ElapsedHour^0.25 - AverageWeight"
close #2

Open filename for Append As #3
Print #3, "PointNumber,Sample,Date,ElaspedMin,Weight,Slope,SlopeSD,ElapsedMin^0.25,ElaspedHour^0.25"
Close #3

Do
    Input #1,adResult 'get result
    'Print "result: "; adResult
    Close #1
    
    Open Com "com5:9600,n,8,1,cs0,cd0,ds0,rs" As #1
    If Err <> 0 Then
        Print "Error opening COM5:"
        Sleep
        End
    end If  
    'set slope back to 0 so that the first n values are okay
    slope =0

	Input #10,tempHumidityString 'get temphumidity
    'Print "result: "; tempHumidityString
    Close #10
    
    Open Com "com6:9600,n,8,1,cs0,cd0,ds0,rs" As #10
    If Err <> 0 Then
        Print "Error opening COM6:"
        Sleep
        End
    end If  


MaxCount = 6 
Delimiter = "," 

split tempHumidityString, Delimiter, MaxCount, s() 

Dim as String humidityValue
humidityValue = rtrim(s(0),"#")

Dim as INTEGER istep
Dim as Double elaspedminquarter
'print "Balance:  "; adResult

balanceRead = mid(adResult,5)

'Print "Balance-mid: "; balanceRead

balanceRead = rtrim(balanceRead," g")
'Print "Balance-trim: "; balanceRead

weight = val(balanceRead)

'Print "Weight: "; weight
Sleep intervalsec,0 'reading every n seconds
If weight > 0 Then
    
    'print "Weight - "; weight
    If weight < startingweight-.1 or weight > startingweight+.1 Then
        'do nothing
    Else
        'Print weight
        NumTotalPoints=NumTotalPoints+1
        NumCurrentPoints = NumCurrentPoints+1
        b1 = Now
        elapsed = DateDiff("s",a1,b1)+timeSinceStartSec
        elapsed = elapsed/60
        elapsedquarter = elapsed^(0.25)
        elaspedhour = elapsed/60
        elaspedhourquarter = elaspedhour^(0.25)
        
        LastNValues(NumCurrentPoints)=weight
        LastTValues(NumCurrentPoints)=elapsedminquarter

        ' print "LastNValues:  ",NumCurrentPoints,LastNValues(NumCurrentPoints)
        
        if (NumTotalPoints > SlopeNum-1) Then
        
            LinFit LastTValues(), LastNValues(), B(), V()
            slope=B(1)
            meanWeight=Mean(LastNValues())
            'stdevWeight=StDevP(LastNValues(),meanWeight)
            'FOR I = 0 TO 1
            '    PRINT USING "B(#)"; I;
             '   PRINT USING "########.########"; B(I); 
            'NEXT I
            SB = SQR(V(1,1))
            
            for istep = 1 to SlopeNum-1 Step 1
               LastNValues(istep) = LastNValues(istep+1)
               LastTValues(istep) = LastNValues(istep+1)
            Next istep
             
            ' do slope calc
            ' now drop the first value  and shift array
            NumCurrentPoints = SlopeNum-1
        End If

        Open filename for Append As #2
        Print #2, NumTotalPoints;",",setName;"-";sampleNum;",";Format(b1, "mm/dd/yyyy hh:mm:ss");",";elapsed;",";weight;",";Format(slope,"#####.#######0");Format(SB,"#####.######0");",";Format(elapsedquarter, "######.########0");",";Format(elaspedhour, "######.########0");",";Format(elaspedhourquarter, "######.########0");",";humidityValue;",";s(1);",";s(2);",";s(3);",";s(4);",";s(5)
        Close #2
        Print NumTotalPoints;" - ";setName;"-";sampleNum;" - ";weight;" - ";Format(slope,"#####.#######0");" - ";Format(SB,"#####.######0");" - ";Format(elapsed, "######.###0");" - ";Format(elapsedquarter, "####.#####0"); " - "; Format(meanWeight,"####.#####0"); " - "; Format(stdevWeight,"####.####0");" - ";humidityValue;" - ";s(1);" - ";s(2);" - ";s(3);",";s(4);",";s(5)

        
        
    end If
end If

keyEntry = Inkey$

Select Case keyEntry

        Case "q": stopCode = 1
        
        Case Chr$(32)
        	Print "Enter next sample number: ";
			input sampleNum
			NumTotalPoints =1
End Select			
       
Loop Until stopCode = 1

Sleep


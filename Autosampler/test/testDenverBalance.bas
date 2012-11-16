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
Open Com "com12:9600,n,8,1,cs0,cd0,ds0,rs" As #1
If Err <> 0 Then
    Print "Error opening COM5:"
    Sleep
    End
end If


a1 = Now
Print "The current time/date is: "
Print Format(a1, "mm-dd-yyyy hh:mm:ss")
Print

Print "Enter sampling interval (in seconds, e.g., 5,10,15,30,120): ";
input intervalsec 

' Data

Dim as double slope
Dim as double SB
Dim as double meanWeight
Dim as double stdevWeight
Dim as double elapsedminquarter
dim as double weightValue

' Computed Y value
intervalsec = intervalsec  * 1000



Do
    Input #1,adResult 'get result
    'Print "result: "; adResult
    Close #1
    
    Open Com "com12:9600,n,8,1,cs0,cd0,ds0,rs" As #1
    If Err <> 0 Then
        Print "Error opening COM12:"
        Sleep
        End
    end If  
    'set slope back to 0 so that the first n values are okay
    slope =0




MaxCount = 4 
Delimiter = "," 



balanceRead = mid(adResult,5)

'Print "Balance-mid: "; balanceRead

balanceRead = rtrim(balanceRead," g")
'Print "Balance-trim: "; balanceRead

weightValue = val(balanceRead)

'Print "Weight: "; weight
Sleep intervalsec,0 'reading every n seconds


    
Print sampleNum;" - ";Format(weight,"#####.#######0");" weight: ";weight

        

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


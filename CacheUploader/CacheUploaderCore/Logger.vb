Public Class Logger

    Public Enum Severity As Byte
        Information
        Warning
        [Error]
    End Enum

    Public Event LoggingOccured(ByVal sender As Object, ByVal e As LoggingEventArgs)


    Public Sub LogError(ByVal message As String)
        Log(message, Severity.Error)
    End Sub

    Public Sub LogInfo(ByVal message As String)
        Log(message, Severity.Information)
    End Sub

    Public Sub LogWarning(ByVal message As String)
        Log(message, Severity.Warning)
    End Sub


    Public Sub Log(ByVal message As String, ByVal severity As Severity)
        Dim le As New LoggingEvent With {.Message = message, .Severity = severity, .Time = DateTime.Now}
        Dim lea As New LoggingEventArgs With {.LoggingEvent = le}
        RaiseEvent LoggingOccured(Me, lea)
    End Sub
End Class

Public Class LoggingEvent

    Public Property Message As String
    Public Property Severity As Logger.Severity
    Public Property Time As DateTime

    Public Overrides Function ToString() As String
        Return String.Format("{0:HH:mm:ss} [{1}]: {2}", Time, Severity.ToString.ToUpper, Message)
    End Function

    Public Function ToShortString() As String
        Return String.Format("{0:HH:mm:ss} {1}", Time, Message)
    End Function


End Class

Public Class LoggingEventArgs
    Inherits EventArgs

    Public Property LoggingEvent As LoggingEvent



End Class

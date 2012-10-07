Imports System.Xml.Serialization
Imports System.IO

<Serializable()>
Public Class EveInstallation

    Public Sub New(ByVal evepath As String, ByVal cachePath As String)
        Me.EvePath = evepath
        Me.CachePath = cachePath
    End Sub

    Public Sub New()

    End Sub

    Public Property EvePath As String
    Public Property CachePath As String

    Public Overrides Function ToString() As String
        Return EvePath.ToUpperInvariant & " ( CachePath: " & CachePath & ")"
    End Function

    Public Overloads Shared Operator =(ByVal x As EveInstallation, ByVal y As EveInstallation) As Boolean
        If x.EvePath.ToLowerInvariant = y.EvePath.ToLowerInvariant AndAlso x.CachePath.ToLowerInvariant = y.CachePath.ToLowerInvariant Then
            Return True
        Else
            Return False
        End If
    End Operator

    Public Overloads Shared Operator <>(ByVal x As EveInstallation, ByVal y As EveInstallation) As Boolean
        Return Not x = y
    End Operator
End Class

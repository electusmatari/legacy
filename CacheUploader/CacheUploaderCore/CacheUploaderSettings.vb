Imports System.Xml.Serialization
Imports System.IO

<Serializable()>
Public Class CacheUploaderSettings
    Public Property InstallationsToMonitor As HashSet(Of EveInstallation)
    Public Property EMAuthToken As String
    Public Property InstallationsToStart As HashSet(Of EveInstallation)
    Public Property DeleteCacheFilesAfterUpload As Boolean
    Public Property OpAnnouncementsEnabled As Boolean
    Public Property CheckForOpsEveryMinute As Integer
    Public Property ShowOpAnnouncementBallonForMinutes As Integer
    Public Property ReshowOpsNotOlderThanMinutes As Integer
    Public Property ReshowOpsNotMoreThanTimes As Integer

    Public Sub New()
        InstallationsToMonitor = New HashSet(Of EveInstallation)
    End Sub

    Public Sub addInstallationToMonitor(ByVal i As EveInstallation)
        If Not InstallationsToMonitor.Any(Function(x) x = i) Then
            InstallationsToMonitor.Add(i)
        End If
    End Sub

    Public Sub addInstallationToStart(ByVal i As EveInstallation)
        If Not InstallationsToStart.Any(Function(x) x = i) Then
            InstallationsToStart.Add(i)
        End If

    End Sub

    Public Sub XMLSerialize(ByVal path As String)
        Dim mySerializer As New XmlSerializer(GetType(CacheUploaderSettings))
        Using myWriter As New StreamWriter(path, False)
            mySerializer.Serialize(myWriter, Me)
        End Using
    End Sub


    Public Shared Function XMLDeserialize(ByVal path As String) As CacheUploaderSettings
        Dim mySerializer As New XmlSerializer(GetType(CacheUploaderSettings))
        Using myFileStream As New FileStream(path, FileMode.Open)
            Return DirectCast(mySerializer.Deserialize(myFileStream), CacheUploaderSettings)
        End Using
    End Function
End Class

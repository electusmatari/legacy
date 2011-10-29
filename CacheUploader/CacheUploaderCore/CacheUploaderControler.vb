Imports System.IO
Imports System.Threading.Tasks

Public Class CacheUploaderControler
    Implements IDisposable


#Region "Fields"
    Private WithEvents m_finder As CacheFinder
    Private m_cacheFileChecker As CacheFileChecker
    Private m_fileSystemWatcher As HashSet(Of FileSystemWatcher)
    Private m_settings As CacheUploaderSettings
    Private m_fileUploadCount As Integer = 0
    Private WithEvents m_logger As Logger
    Private WithEvents m_opNotifier As OpNotifier
    Private m_consumerQueue As ConsumerQueue(Of String)
#End Region

#Region "Events"
    Public Event EveInstallationsFound(ByVal sender As Object, ByVal e As EveInstallationsFoundEventArgs)
    Public Event SettingsLoaded(ByVal sender As Object, ByVal e As SettingsLoadedEventArgs)
    Public Event fileUploaded(ByVal sender As Object, ByVal e As FileUploadedEventArgs)
    Public Event LoggingOccured(ByVal sender As Object, ByVal e As LoggingEventArgs)
    Public Event OpNotification(ByVal sender As Object, ByVal e As OperationEventArgs)
#End Region

#Region "Init"

    Public Sub Init()
        'Get Settings
        initSettings()
        'find all Installations on this computer
        findEveInstallations()
        'we need the settings here allready
        m_opNotifier = New OpNotifier(m_settings, m_logger)
        AddHandler m_opNotifier.opsFound, AddressOf onOpNotification
        m_opNotifier.checkForOps()
    End Sub

    Private Sub initFileWatchers()
        For Each watcher In m_fileSystemWatcher
            RemoveHandler watcher.Created, AddressOf onCacheFileCreated
        Next
        m_fileSystemWatcher.Clear()
        For Each item As EveInstallation In m_settings.InstallationsToMonitor
            Dim watcher As New FileSystemWatcher(item.CachePath) With {.EnableRaisingEvents = True}
            m_fileSystemWatcher.Add(watcher)
            AddHandler watcher.Created, AddressOf onCacheFileCreated
        Next
    End Sub

    Private Sub initSettings()
        Try
            'try to get saved settings.
            m_settings = Nothing
            m_settings = CacheUploaderSettings.XMLDeserialize(m_finder.getSerializationPath)
            'make sure we look at the most recent version of the cache path
            Dim mostRecentVersions As New HashSet(Of EveInstallation)
            For Each installation As EveInstallation In m_settings.InstallationsToMonitor
                Dim newVersion As EveInstallation = m_finder.checkForNewVersionOfCachePath(installation)
                If newVersion IsNot Nothing Then
                    mostRecentVersions.Add(newVersion)
                End If
            Next
            m_settings.InstallationsToMonitor = mostRecentVersions
            SaveSettings()
        Catch ex As IO.FileNotFoundException
            m_logger.LogWarning("No Settings found, creating new settings")
            m_settings = New CacheUploaderSettings
        End Try
        initFileWatchers()
        RaiseEvent SettingsLoaded(Me, New SettingsLoadedEventArgs With {.Settings = m_settings})
    End Sub

    Public Sub New()
        m_logger = New Logger
        AddHandler m_logger.LoggingOccured, AddressOf OnLoggingOccured
        m_finder = New CacheFinder
        m_cacheFileChecker = New CacheFileChecker
        m_fileSystemWatcher = New HashSet(Of FileSystemWatcher)
        m_consumerQueue = New ConsumerQueue(Of String)(2, AddressOf uploadFile)
    End Sub
#End Region

    Private Sub findEveInstallations()
        m_finder.searchForCachePaths()
        RaiseEvent EveInstallationsFound(Me, New EveInstallationsFoundEventArgs With {.EveInstallations = m_finder.EveInstallations})
    End Sub

    Private Sub OnLoggingOccured(ByVal sender As Object, ByVal e As LoggingEventArgs)
        RaiseEvent LoggingOccured(sender, e)
    End Sub

    Private Sub onOpNotification(ByVal sender As Object, ByVal e As OperationEventArgs)
        RaiseEvent OpNotification(sender, e)
    End Sub

    Private Sub onExitApplication()
        SaveSettings()
    End Sub

#Region "Settings safe and delete"
    Public Sub deleteSettings()
        File.Delete(m_finder.getSerializationPath)
        Init()
    End Sub

    Private Sub SaveSettings()
        'save new settings
        m_settings.XMLSerialize(m_finder.getSerializationPath)
    End Sub
#End Region

#Region "Properties"

    Public Property InstallationsToMonitor As HashSet(Of EveInstallation)
        Get
            Return m_settings.InstallationsToMonitor
        End Get
        Set(ByVal value As HashSet(Of EveInstallation))
            m_settings.InstallationsToMonitor = value
            SaveSettings()
            initFileWatchers()

        End Set
    End Property

    Public Property AuthToken As String
        Get
            Return m_settings.EMAuthToken
        End Get
        Set(ByVal value As String)
            m_settings.EMAuthToken = value
            SaveSettings()
        End Set
    End Property

    Public Property DeleteFilesAfterUpload As Boolean
        Get
            Return m_settings.DeleteCacheFilesAfterUpload
        End Get
        Set(ByVal value As Boolean)
            m_settings.DeleteCacheFilesAfterUpload = value
            SaveSettings()
        End Set
    End Property

    Public ReadOnly Property Settings As CacheUploaderSettings
        Get
            Return m_settings
        End Get
    End Property
#End Region

#Region "FileUpload"

    Private Sub onCacheFileCreated(ByVal sender As Object, ByVal e As FileSystemEventArgs)
        m_consumerQueue.Add(e.FullPath)
    End Sub

    Public Sub uploadAllFiles()
        For Each installation As EveInstallation In InstallationsToMonitor
            Dim cachepath As New DirectoryInfo(installation.CachePath)

            For Each cacheFile In cachepath.GetFiles("*.cache")
                If m_cacheFileChecker.isMarketCacheFile(cacheFile.FullName) Then
                    m_consumerQueue.Add(cacheFile.FullName)
                End If

            Next
        Next
    End Sub

    Private Sub uploadFile(ByVal path As String)
        Using cf As New CacheFileUtils(m_logger)
            AddHandler cf.FileUploaded, AddressOf onFileUploaded
            Try
                cf.uploadFile(path, AuthToken, DeleteFilesAfterUpload)
            Finally
                RemoveHandler cf.FileUploaded, AddressOf onFileUploaded
            End Try
        End Using
    End Sub


    Private Sub onFileUploaded(ByVal sender As Object, ByVal e As EventArgs)
        m_fileUploadCount += 1
        RaiseEvent fileUploaded(Me, New FileUploadedEventArgs() With {.UploadedFileCount = m_fileUploadCount})
    End Sub
#End Region

#Region "IDisposable Support"
    Private disposedValue As Boolean ' To detect redundant calls

    ' IDisposable
    Protected Overridable Sub Dispose(ByVal disposing As Boolean)
        If Not Me.disposedValue Then
            If disposing Then
                ' TODO: dispose managed state (managed objects).
            End If

            ' TODO: free unmanaged resources (unmanaged objects) and override Finalize() below.
            ' TODO: set large fields to null.
            onExitApplication()
            RemoveHandler m_logger.LoggingOccured, AddressOf OnLoggingOccured
            m_logger = Nothing
            m_finder = Nothing
            For Each watcher As FileSystemWatcher In m_fileSystemWatcher
                RemoveHandler watcher.Created, AddressOf onCacheFileCreated
                watcher.Dispose()
            Next
            m_fileSystemWatcher = Nothing
            m_settings = Nothing
            m_consumerQueue.dispose()
        End If
        Me.disposedValue = True
    End Sub

    ' TODO: override Finalize() only if Dispose(ByVal disposing As Boolean) above has code to free unmanaged resources.
    'Protected Overrides Sub Finalize()
    '    ' Do not change this code.  Put cleanup code in Dispose(ByVal disposing As Boolean) above.
    '    Dispose(False)
    '    MyBase.Finalize()
    'End Sub

    ' This code added by Visual Basic to correctly implement the disposable pattern.
    Public Sub Dispose() Implements IDisposable.Dispose
        ' Do not change this code.  Put cleanup code in Dispose(ByVal disposing As Boolean) above.
        Dispose(True)
        GC.SuppressFinalize(Me)
    End Sub
#End Region

End Class



Public Class EveInstallationsFoundEventArgs
    Inherits EventArgs

    Public Property EveInstallations As IEnumerable(Of EveInstallation)
End Class

Public Class CurrentInstallationsChanged
    Inherits EventArgs

    Public Property Installation As HashSet(Of EveInstallation)
End Class

Public Class FileUploadedEventArgs
    Inherits EventArgs

    Public Property UploadedFileCount As Integer
End Class

Public Class SettingsLoadedEventArgs
    Inherits EventArgs

    Public Property Settings As CacheUploaderSettings
End Class
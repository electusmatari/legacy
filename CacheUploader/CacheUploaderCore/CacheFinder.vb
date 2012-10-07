Imports System.IO
Imports System.Windows.Forms


Public Class CacheFinder

    Private Enum OSVersion As Byte
        Windows_95
        Windows_98
        Windows_98SE
        Windows_ME
        Windows_NT_3_51
        Windows_NT_4_00
        Windows_2000
        Windows_XP
        Windows_Vista
        Windows_7
    End Enum

#Region "Properties and Fields"
    Public Property EveInstallations As HashSet(Of EveInstallation)
#End Region

    Public Sub New()
        EveInstallations = New HashSet(Of EveInstallation)
    End Sub




    Public Function getSerializationPath() As String
        Return Path.Combine(Application.StartupPath, "Settings.xml")
    End Function


    Public Sub searchForCachePaths()
        EveInstallations.Clear()
        Dim osVersion As OSVersion = getOSVersion()
        Dim basePath As String = ""

        If osVersion = CacheFinder.OSVersion.Windows_Vista OrElse osVersion = CacheFinder.OSVersion.Windows_7 Then
            'Vista and Windows 7
            basePath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData)

        Else
            'Windows XP (and older, though I am not sure if it works on 95, 98 etc. But it should...)
            basePath = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile)
            basePath = findCCPPathXP(basePath)
        End If

        'if basepath is empty here, we are running on an unknown OS. 
        Dim eveCachepath As String
        Dim evePath As String = ""
        If basePath <> "" Then
            eveCachepath = Path.Combine(basePath, "CCP", "EVE")
            Dim di As New DirectoryInfo(eveCachepath)
            Dim subdirs As DirectoryInfo() = di.GetDirectories

            'Search for tranquility-folder. While we are doing this, we discover the path where eve is installed
            For Each dir As DirectoryInfo In subdirs
                If dir.FullName.ToLowerInvariant.EndsWith("tranquility") Then
                    evePath = getEvePath(dir)
                    basePath = Path.Combine(dir.FullName, "Cache", "MachoNet", "87.237.38.200")
                    eveCachepath = getCurrentCacheFolderFromBaseFolder(basePath)
                    EveInstallations.Add(New EveInstallation(evePath, eveCachepath))
                End If
            Next


        End If

    End Sub

    Private Function getEvePath(ByVal dir As DirectoryInfo) As String
        'split at underscore
        Dim parts As String() = dir.FullName.Split("_"c)

        'Get EvePath
        Dim driveLetter As String = parts(0).Split(Path.DirectorySeparatorChar).Last & ":" & Path.DirectorySeparatorChar
        Dim evePathParts As New List(Of String)
        evePathParts.Add(driveLetter)
        evePathParts.AddRange(parts.Skip(1).Take(parts.Length - 2))
        'evePath is everything except the last "tranquility"
        Return Path.Combine(evePathParts.ToArray)
    End Function

    Private Function getBasePathFromCachePath(ByVal CachePath As String) As String
        Dim explodedPath As String() = CachePath.Split(Path.DirectorySeparatorChar)
        Dim baseParts As String() = explodedPath.Take(explodedPath.Length - 2).ToArray
        baseParts(0) = baseParts(0) & Path.DirectorySeparatorChar
        Return Path.Combine(baseParts.ToArray)
    End Function

    Private Function getCurrentCacheFolderFromBaseFolder(ByVal basePath As String) As String
        Dim di = New DirectoryInfo(basePath)
        If di.Exists Then
            Dim subdirs = di.GetDirectories
            Dim versionNumbers As New List(Of Integer)
            For Each dir As DirectoryInfo In subdirs
                Try
                    versionNumbers.Add(CInt(dir.FullName.Split(Path.DirectorySeparatorChar).Last()))
                Catch ex As InvalidCastException
                    'If we can't cast it, it is not the folder we are looking for, so do nothing
                End Try
            Next

            Dim fullpath As String = Path.Combine(basePath, versionNumbers.Max.ToString, "CachedMethodCalls")
            Return fullpath
        Else
            Return Nothing
        End If
    End Function

    Private Function getOSVersion() As OSVersion
        'Get Operating system information.
        Dim os As OperatingSystem = Environment.OSVersion
        'Get version information about the os.
        Dim vs As Version = os.Version

        Dim operatingSystem As OSVersion

        If os.Platform = PlatformID.Win32Windows Then
            'This is a pre-NT version of Windows
            Select Case vs.Minor
                Case 0
                    operatingSystem = OSVersion.Windows_95
                    Exit Select
                Case 10
                    If vs.Revision.ToString() = "2222A" Then
                        operatingSystem = OSVersion.Windows_98SE
                    Else
                        operatingSystem = OSVersion.Windows_98
                    End If
                    Exit Select
                Case 90
                    operatingSystem = OSVersion.Windows_ME
                    Exit Select
                Case Else
                    Exit Select
            End Select
        ElseIf os.Platform = PlatformID.Win32NT Then
            Select Case vs.Major
                Case 3
                    operatingSystem = OSVersion.Windows_NT_3_51
                    Exit Select
                Case 4
                    operatingSystem = OSVersion.Windows_NT_4_00
                    Exit Select
                Case 5
                    If vs.Minor = 0 Then
                        operatingSystem = OSVersion.Windows_2000
                    Else
                        operatingSystem = OSVersion.Windows_XP
                    End If
                    Exit Select
                Case 6
                    If vs.Minor = 0 Then
                        operatingSystem = OSVersion.Windows_Vista
                    Else
                        operatingSystem = OSVersion.Windows_7
                    End If
                    Exit Select
                Case Else
                    Exit Select
            End Select
        End If

        Return operatingSystem
    End Function

    Private Function findCCPPathXP(ByVal basePath As String) As String
        Dim di As New DirectoryInfo(basePath)
        Dim result As String = ""
        Dim found As Boolean = False

        'On XP we look for a like <basepath>\Local Settings\Application Data\CCP\EVE\
        'Unfortunatly, "Local Settings" and "Application Data" are localized, so for a german client we are  looking for <basepath>\Lokale Einstellungen\Anwendungsdaten\CCP\EVE\
        'so we look for a folder that starts with basepath, has two subfolders and in the inner subfolder the folders CCP\EVE.
        'Or in other words: <basepath>\.*\.*\CCP\EVE\ (yes, regex slightly off, but you get the idea)
        For Each outerDir As DirectoryInfo In di.GetDirectories
            For Each innerDir As DirectoryInfo In outerDir.GetDirectories
                If innerDir.GetDirectories.Where(Function(d) d.Name.ToLowerInvariant = "CCP".ToLowerInvariant).Count = 1 Then
                    Dim outerAndInner As String = Path.Combine(outerDir.FullName, innerDir.Name)
                    Dim pathSoFar As String = Path.Combine(basePath, outerDir.Name, innerDir.Name, "CCP")
                    If Directory.Exists(Path.Combine(pathSoFar, "EVE")) Then
                        found = True
                        result = outerAndInner
                        Exit For
                    End If
                End If
            Next
            If found Then
                Exit For
            End If
        Next
        Return result

    End Function

    Public Function checkForNewVersionOfCachePath(ByVal cachePath As EveInstallation) As EveInstallation
        Dim basepath As String = getBasePathFromCachePath(cachePath.CachePath)
        Dim cachePathMostRecentVersion As String = getCurrentCacheFolderFromBaseFolder(basepath)
        If cachePathMostRecentVersion Is Nothing Then
            Return Nothing
        Else
            Return New EveInstallation(cachePath.EvePath, cachePathMostRecentVersion)
        End If
    End Function


End Class

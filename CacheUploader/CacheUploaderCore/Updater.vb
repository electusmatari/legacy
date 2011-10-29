Imports System.Windows.Forms
Imports System.IO
Imports System.Net
Imports System.Text
Imports System.Security.Cryptography

Public Class Updater

    Public Sub New()
        If File.Exists(Path.Combine(Application.StartupPath, "update.bat")) Then
            File.Delete(Path.Combine(Application.StartupPath, "update.bat"))
        End If
    End Sub


    Public Function checkForUpdates() As Boolean

#If DEBUG Then
#Else
     'download hash File from Server
        downloadHashes()
        downloadSignature()
#End If


        'check for new files on server
        Dim fh As New FileHasher

        Dim hashesOk As Boolean = fh.VerifySignature

        If hashesOk Then
            Dim files As IEnumerable(Of String) = fh.getFilesToUpdate(Path.Combine(Application.StartupPath, "hashes.txt"))

            If files.Count > 0 Then
#If DEBUG Then
#Else
                If MessageBox.Show("There is a new Version of EveCacheUploader. Download it?", "New version found", MessageBoxButtons.OKCancel, MessageBoxIcon.Question) = DialogResult.OK Then
                    'download files from server
                    downloadNewFiles(files)

                    'create update.bat
                    'the bat overwrites the files with the new ones and starts the program again
                    createUpdateBat(files)

                    Dim p As New ProcessStartInfo(Path.Combine(Application.StartupPath, "update.bat"))

                    Process.Start(p)


                    Return True
                Else
                    Return False
                End If
#End If
            End If
        Else
            MessageBox.Show("Updating of the Gradient Market Index Uploader failed! The signature of the update files is not ok. Please tell us so in the EM-Forums (http://www.electusmatari.com/forums)", "Update failed: Signature invalid", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End If

        Return False
    End Function

    Private Sub createUpdateBat(ByVal newFiles As IEnumerable(Of String))
        Dim sb As New StringBuilder
        sb.Append("@echo off")
        sb.AppendLine()
        sb.Append("echo Updating EveCachUploader...")
        sb.AppendLine()
        'this one is dirty... since we have no sleep/wait command, lets ping localhost 2 times and continue afterwards
        sb.Append("ping localhost -n 2 > nul")
        sb.AppendLine()
        'create move statements
        For Each filename As String In newFiles
            sb.Append("echo Deleting ")
            sb.Append(filename)
            sb.AppendLine()
            sb.Append("del ")
            sb.Append("""" & Path.Combine(Application.StartupPath, filename) & """")
            sb.AppendLine()
            sb.Append("if ""%errorlevel%""==""0"" Echo Success.")
            sb.AppendLine()
            sb.AppendLine()
            sb.Append("echo Renaming ")
            sb.Append(filename & "_new" & " to " & filename)
            sb.AppendLine()
            sb.Append("ren ")
            sb.Append("""" & Path.Combine(Application.StartupPath, filename & "_new") & """ ")
            sb.Append(filename)
            sb.AppendLine()
            sb.Append("if ""%errorlevel%""==""0"" Echo Success.")
            sb.AppendLine()
        Next
        sb.Append("echo EveCachUploader update ready! Starting again...")
        sb.AppendLine()
        sb.Append("""" & Path.Combine(Application.StartupPath, "CacheUploader.exe") & """")
        sb.AppendLine()
        sb.Append("set /p xxx=Press enter to close")
        sb.AppendLine()
        sb.Append("exit")

        Dim bat As String = sb.ToString
        Using sw As New StreamWriter(Path.Combine(Application.StartupPath, "update.bat"))
            sw.Write(bat)
            sw.Flush()
        End Using
    End Sub

    Private Sub downloadHashes()
        Dim webPath As String = "http://www.electusmatari.com/gmi/uploader/files/hashes.txt"
        Dim filename As String = Path.Combine(Application.StartupPath, "hashes.txt")
        Try
            Dim fileReader As New WebClient()
            fileReader.DownloadFile(webPath, filename)

        Catch ex As HttpListenerException
            Console.WriteLine("Error accessing " + webPath + " - " + ex.Message)
        Catch ex As Exception
            Console.WriteLine("Error accessing " + webPath + " - " + ex.Message)
        End Try
    End Sub

    Private Sub downloadSignature()
        Dim webPath As String = "http://www.electusmatari.com/gmi/uploader/files/signature.txt"
        Dim filename As String = Path.Combine(Application.StartupPath, "signature.txt")
        Try
            Dim fileReader As New WebClient()
            fileReader.DownloadFile(webPath, filename)

        Catch ex As HttpListenerException
            Console.WriteLine("Error accessing " + webPath + " - " + ex.Message)
        Catch ex As Exception
            Console.WriteLine("Error accessing " + webPath + " - " + ex.Message)
        End Try
    End Sub

    Private Sub downloadNewFiles(ByVal files As IEnumerable(Of String))
        Dim webPath As String = "http://www.electusmatari.com/gmi/uploader/files/"

        Try
            Dim fileReader As New WebClient()
            For Each fileName As String In files
                fileReader.DownloadFile(webPath & fileName, Path.Combine(Application.StartupPath, fileName & "_new"))
            Next
        Catch ex As HttpListenerException
            Console.WriteLine("Error accessing " + webPath + " - " + ex.Message)
        Catch ex As Exception
            Console.WriteLine("Error accessing " + webPath + " - " + ex.Message)
        End Try
    End Sub

   

End Class

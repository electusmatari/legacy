Imports System.Security.Cryptography
Imports System.Text
Imports System.IO
Imports System.Reflection


Public Class FileHasher

    Public Function SHA1StringHash(ByVal filePath As String) As String
        Dim SHA1 As System.Security.Cryptography.SHA1CryptoServiceProvider = New System.Security.Cryptography.SHA1CryptoServiceProvider()
        Dim Hash As Byte()
        Dim result As String = String.Empty
        Dim Tmp As String = String.Empty

        Using FN As New FileStream(filePath, FileMode.Open, FileAccess.Read, FileShare.Read, 8192)
            SHA1.ComputeHash(FN)
        End Using

        Hash = SHA1.Hash
        For i As Integer = 0 To Hash.Length - 1
            Tmp = Convert.ToString(Hash(i), 16)
            If Tmp.Length = 1 Then
                Tmp = "0" + Tmp
                result &= Tmp
            End If
        Next

        Return result
    End Function


    Public Sub createHashFile()
        Dim myPath As String = Path.GetDirectoryName([Assembly].GetEntryAssembly().Location)
        Dim exeHash As String
        Dim dllHash As String


        If File.Exists(Path.Combine(myPath, "CacheUploader.exe")) Then
            exeHash = SHA1StringHash(Path.Combine(myPath, "CacheUploader.exe"))
        End If

        If File.Exists(Path.Combine(myPath, "CacheUploaderCore.dll")) Then
            dllHash = SHA1StringHash(Path.Combine(myPath, "CacheUploaderCore.dll"))
        End If

        Dim sb As New StringBuilder
        sb.Append("CacheUploader.exe:")
        sb.Append(exeHash)
        sb.AppendLine()
        sb.Append("CacheUploaderCore.dll:")
        sb.Append(dllHash)



        Dim file As String = 
    End Sub
End Class

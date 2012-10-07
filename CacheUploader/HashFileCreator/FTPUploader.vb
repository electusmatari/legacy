Public Class FTPUploader

    Public Sub upload(ByVal filename As String)
        Dim f As New IO.FileInfo(filename)
        Dim host As String = "ftp://istinn.electusmatari.com"

        ' set up request...
        Dim clsRequest As System.Net.FtpWebRequest = _
            DirectCast(System.Net.WebRequest.Create(host & "/" & f.Name), System.Net.FtpWebRequest)
        clsRequest.Credentials = New System.Net.NetworkCredential("emuploader", "nuki4ooW")
        clsRequest.Method = System.Net.WebRequestMethods.Ftp.UploadFile

        ' read in file...
        Dim bFile() As Byte = System.IO.File.ReadAllBytes(f.FullName)

        ' upload file...
        Using clsStream As System.IO.Stream = clsRequest.GetRequestStream()
            clsStream.Write(bFile, 0, bFile.Length)
        End Using
    End Sub


End Class

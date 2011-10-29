Imports System.IO

Public Class CacheFileChecker
#Region "Check for MarketCacheFile"


    Public Function isMarketCacheFile(ByVal filename As String) As Boolean
        Dim result As Boolean = False

        If File.Exists(filename) Then
            Using fs As New FileStream(filename, FileMode.Open)
                Return isMarketCacheFile(fs)
            End Using
        End If

        Return result
    End Function

    Public Function isMarketCacheFile(ByVal fs As FileStream) As Boolean
        Dim bytesTocheck(17) As Byte
        fs.Position = 12
        For i As Integer = 0 To 17
            bytesTocheck(i) = CByte(fs.ReadByte)
        Next

        Dim enc As New System.Text.UTF8Encoding
        Dim text As String = enc.GetString(bytesTocheck)
        fs.Position = 0
        If text.ToLowerInvariant = "GetOldPriceHistory".ToLowerInvariant Then
            Return True
        Else
            Return False
        End If
    End Function
#End Region
End Class

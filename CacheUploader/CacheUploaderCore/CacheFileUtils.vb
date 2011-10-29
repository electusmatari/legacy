Imports System.IO
Imports System.Runtime.InteropServices
Imports System.Threading
Imports System.Text
Imports System.Net

Public Class CacheFileUtils
    Implements IDisposable


#Region "Fields"
    Private m_cacheFileChecker As New CacheFileChecker
    Private m_logger As Logger
#End Region


#Region "init"
    Public Sub New(ByVal logger As Logger)
        m_logger = logger
    End Sub
#End Region

#Region "events"
    Public Event FileUploaded(ByVal sender As Object, ByVal e As EventArgs)
#End Region

#Region "handle locked files"
    Public Function TryOpenFile(ByVal path As String, ByVal access As FileAccess, ByVal share As FileShare) As FileStream
        Try
            If Not File.Exists(path) Then
                Return Nothing
            End If
            Return File.Open(path, FileMode.Open, access, share)
        Catch e As IOException
            Return Nothing
        Catch e As UnauthorizedAccessException
            Return Nothing
        End Try
    End Function

    Public Function WaitAndOpenFile(ByVal path As String, ByVal access As FileAccess, ByVal share As FileShare, ByVal timeout As TimeSpan) As FileStream
        Dim dt As DateTime = DateTime.UtcNow
        Dim fs As FileStream = Nothing
        While fs Is Nothing AndAlso (DateTime.UtcNow - dt) < timeout
            fs = TryOpenFile(path, access, share)
            ' who knows better way and wants a free cookie? ;)
            Thread.Sleep(250)
        End While
        Return fs
    End Function
#End Region

#Region "upload file"

    Public Sub uploadFile(ByVal path As String, ByVal token As String, ByVal deleteFileAfterUpload As Boolean)
        If token <> "" Then
            Dim isMarketCacheFile As Boolean = False
            Using cacheFile As FileStream = WaitAndOpenFile(path, FileAccess.Read, FileShare.Read, New TimeSpan(0, 0, 10))
                If cacheFile IsNot Nothing Then
                    isMarketCacheFile = m_cacheFileChecker.isMarketCacheFile(cacheFile)
                    If isMarketCacheFile Then
                        postFile(cacheFile, token)
                        RaiseEvent FileUploaded(Me, EventArgs.Empty)
                        m_logger.LogInfo(String.Format("File uploaded: {0}", path))

                    End If
                End If
            End Using
            If isMarketCacheFile AndAlso deleteFileAfterUpload Then
                File.Delete(path)
                m_logger.LogInfo(String.Format("File deleted: {0}", path))
            End If
        End If
    End Sub

    Private Sub postFile(ByVal fs As FileStream, ByVal authToken As String)
        Dim webPath As String = "http://www.electusmatari.com/gmi2/submit/" & authToken & "/"


        ' Create a request using a URL that can receive a post. 
        Dim request As HttpWebRequest = DirectCast(WebRequest.Create(webPath), HttpWebRequest)
        ' Set the Method property of the request to POST.
        request.Method = "POST"
        request.ContentType = "application/octet-stream"

        Dim toWrite(CInt(fs.Length - 1)) As Byte
        ' Create POST data and convert it to a byte array.
        fs.Read(toWrite, 0, CInt(fs.Length - 1))
        ' Set the ContentLength property of the WebRequest.
        request.ContentLength = toWrite.Length
        ' Get the request stream.
        Dim dataStream As Stream = request.GetRequestStream()
        ' Write the data to the request stream.

        m_logger.LogInfo("Posting to server")
        dataStream.Write(toWrite, 0, toWrite.Length)
        ' Close the Stream object.
        dataStream.Close()
        ' Get the response.
        Try
            Using response As WebResponse = request.GetResponse()
                ' Display the status.
                Dim status As String = CType(response, HttpWebResponse).StatusDescription
                ' Get the stream containing content returned by the server.
                dataStream = response.GetResponseStream()
                ' Open the stream using a StreamReader for easy access.
                Using reader As New StreamReader(dataStream)
                    ' Read the content.
                    Dim responseFromServer As String = reader.ReadToEnd()
                    ' Display the content.
                    m_logger.LogInfo(String.Format("Server answered:  {0}", responseFromServer))
                End Using
            End Using

        Catch ex As WebException
            m_logger.LogError("Posting to server failed: " & ex.Message)
        Finally
            dataStream.Close()
        End Try
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
            m_cacheFileChecker = Nothing
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

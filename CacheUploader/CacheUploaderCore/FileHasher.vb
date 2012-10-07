Imports System.Security.Cryptography
Imports System.Text
Imports System.IO
Imports System.Reflection
Imports System.Windows.Forms


Public Class FileHasher

    Dim m_files As HashSet(Of String)

    Public Sub New()
        'Create a set of files we want to check for updates
        m_files = New HashSet(Of String)
        m_files.Add("CacheUploader.exe")
        m_files.Add("CacheUploaderCore.dll")
    End Sub

    ''' <summary>
    ''' Calculate Hash for a file
    ''' </summary>
    ''' <param name="filePath"></param>
    ''' <returns></returns>
    ''' <remarks></remarks>
    Public Function SHA1StringHash(ByVal filePath As String) As String
        Dim SHA1 As System.Security.Cryptography.SHA1CryptoServiceProvider = New System.Security.Cryptography.SHA1CryptoServiceProvider()

        Using FN As New FileStream(filePath, FileMode.Open, FileAccess.Read, FileShare.Read, 8192)
            SHA1.ComputeHash(FN)
        End Using

        Return Convert.ToBase64String(SHA1.Hash)
    End Function

    ''' <summary>
    ''' Checks the signature of the hashes
    ''' </summary>
    ''' <returns></returns>
    ''' <remarks></remarks>
    Public Function VerifySignature() As Boolean
        Dim publicKey As String = "<RSAKeyValue><Modulus>ybG6Qc8W9Axky0bxd65whAQKInfTohGlyKXjrYmR/4Hj4pvm8FM+0T01d7UOU1mno/YNS9UEs6LrOcRs06T+fxxeP2VlKgj3w2lvimCQnijdVKzpGbXed605cWizURSHpeZuMtT+gEl26opidmx0HgkTG7DZwyNtDPK7FKEqtnc=</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>"
        Dim downloadedHashes As String = ""
        Dim downloadedSignature As String = ""

        Using sr As New StreamReader(Path.Combine(Application.StartupPath, "hashes.txt"))
            downloadedHashes = sr.ReadToEnd
        End Using

        Using sr As New StreamReader(Path.Combine(Application.StartupPath, "signature.txt"))
            downloadedSignature = sr.ReadToEnd
        End Using

        ' init providers
        Dim rsaCryptoServiceProvider As New RSACryptoServiceProvider
        Dim rsaFormatter As New RSAPKCS1SignatureDeformatter(rsaCryptoServiceProvider)
        Dim RSA As System.Security.Cryptography.RSA = RSA.Create()
        Dim Encoding As New ASCIIEncoding
        Dim SHA1 As New SHA1Managed

        ' Setting Hashalgorithm and private Key
        rsaFormatter.SetHashAlgorithm("SHA1")
        RSA.FromXmlString(publicKey)
        rsaFormatter.SetKey(RSA)

        'Convert String to Byte() and sign
        Dim clearText As Byte() = Encoding.GetBytes(downloadedHashes)
        Dim signature As Byte() = Convert.FromBase64String(downloadedSignature)

        'validate signatur
        Return rsaFormatter.VerifySignature(SHA1.ComputeHash(clearText), signature)
    End Function

    ''' <summary>
    ''' Calculates the signature of a text
    ''' </summary>
    ''' <param name="textToSign"></param>
    ''' <param name="privateKey"></param>
    ''' <returns></returns>
    ''' <remarks></remarks>
    Public Function Sign(ByVal textToSign As String, ByVal privateKey As String) As String
        ' Init of providers
        Dim rsaCryptoServiceProvider As New RSACryptoServiceProvider
        Dim rsaFormatter As New RSAPKCS1SignatureFormatter(rsaCryptoServiceProvider)
        Dim RSA As RSA = RSA.Create()
        Dim Encoding As New ASCIIEncoding
        Dim SHA1 As New SHA1Managed

        ' Setting Hashalgorithm and private Key
        rsaFormatter.SetHashAlgorithm("SHA1")
        RSA.FromXmlString(privateKey)
        rsaFormatter.SetKey(RSA)

        'Convert String to Byte() and sign
        Dim valueToHash As Byte() = Encoding.GetBytes(textToSign)
        Dim signedValue As Byte() = rsaFormatter.CreateSignature(SHA1.ComputeHash(valueToHash))
        'Convert Byte() to String
        Return Convert.ToBase64String(signedValue)
    End Function

    ''' <summary>
    ''' Calculates the hashes for all monitored Files (m_file => Constructor) and writes them into a file
    ''' </summary>
    ''' <param name="filesPath"></param>
    ''' <param name="privateKey"></param>
    ''' <remarks></remarks>
    Public Sub createHashFile(ByVal filesPath As String, ByVal privateKey As String)
        Dim sb As New StringBuilder
        For Each f As String In m_files

            If File.Exists(Path.Combine(filesPath, f)) Then
                sb.Append(f)
                sb.Append(":")
                sb.Append(SHA1StringHash(Path.Combine(filesPath, f)))
                sb.AppendLine()
            End If
        Next

        Dim fileContent As String = sb.ToString

        'Sign the hashesfile
        Dim signature As String = Sign(fileContent, privateKey)

        'Writing hashes
        Using tw As New StreamWriter(Path.Combine(filesPath, "hashes.txt"), False, Encoding.ASCII)
            tw.Write(fileContent)
            tw.Flush()
        End Using

        Using tw As New StreamWriter(Path.Combine(filesPath, "signature.txt"), False, Encoding.ASCII)
            tw.Write(signature)
            tw.Flush()
        End Using

    End Sub

    ''' <summary>
    ''' Checks for all monitored files if the hashes changed and collects those with new hashes
    ''' </summary>
    ''' <param name="hashFilePath"></param>
    ''' <returns></returns>
    ''' <remarks></remarks>
    Public Function getFilesToUpdate(ByVal hashFilePath As String) As IEnumerable(Of String)
        Dim filesToUpdate As New HashSet(Of String)
        Dim filesPath As String = Application.StartupPath

        If File.Exists(hashFilePath) Then
            'Get the most recent hashes from the file that was downloaded
            Using sr As New StreamReader(hashFilePath)
                While Not sr.EndOfStream
                    Dim line = sr.ReadLine()

                    Dim filenameAndHash As String() = line.Split(":"c)
                    'if the hash contains a colon, copy every part in an index > 0 into ex(1)
                    If filenameAndHash.Count > 2 Then
                        For i As Integer = 2 To filenameAndHash.Count - 1
                            filenameAndHash(1) &= ":" & filenameAndHash(i)
                        Next
                    End If

                    Dim filename As String = filenameAndHash(0)
                    Dim hashFromServer As String = filenameAndHash(1)
                    Dim hashLocal As String = ""
                    'getHashes from local files

                    If File.Exists(Path.Combine(filesPath, filename)) Then
                        hashLocal = SHA1StringHash(Path.Combine(filesPath, filename))
                    End If

                    If hashFromServer <> hashLocal Then
                        filesToUpdate.Add(filename)
                    End If
                End While
            End Using
#If DEBUG Then
#Else
    File.Delete(hashFilePath)
#End If

        End If
        Return filesToUpdate
    End Function

End Class

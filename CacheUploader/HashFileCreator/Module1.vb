Imports System.IO
Imports System.Reflection


Module Module1

    Sub Main(ByVal args As String())
        If args.Length = 0 Then
            ReDim args(1)
            args(0) = "."
        End If
        Console.WriteLine()


        Console.WriteLine("Creating HashFile")
        Try
            Dim fh As New CacheUploaderCore.FileHasher
            fh.createHashFile(args(0), "<RSAKeyValue><Modulus>ybG6Qc8W9Axky0bxd65whAQKInfTohGlyKXjrYmR/4Hj4pvm8FM+0T01d7UOU1mno/YNS9UEs6LrOcRs06T+fxxeP2VlKgj3w2lvimCQnijdVKzpGbXed605cWizURSHpeZuMtT+gEl26opidmx0HgkTG7DZwyNtDPK7FKEqtnc=</Modulus><Exponent>AQAB</Exponent><P>5W+xwu5yhZ/UahfAAhjLaRiQBEUuGmkeV9P572glsrIsDMNAVjtPBXtjwQ6YuZ0c1z126jREupLnLcZkZ6mqYw==</P><Q>4QvH+NcSbJ0hbggRCIYyXyFs3WoTHKkAIuh+DzEr4xo1eEP6baIp4bsleTe+gTibFQn/vAngHAix4OqfuY2V3Q==</Q><DP>lshG7LLENKkLcgXVvAsLczAfRY8pc1XuCQ5YTUwGql+Jr4GKAKHNlu62aiPrnuBwGcxdICHloS/2GhEt3yqTvQ==</DP><DQ>TC/73C+bqi+sAJ80fQlJhlE/lNnzbHF+fVLuUmBYNkNKNNP2tSUAPs5nyljn4sFyJzZCYLuLJpJ+/eEQf/YB9Q==</DQ><InverseQ>EaSwzDB/F353hm5iCKWfcLfKC9cveLlvrbLjcHsJFL9DVnsC5KnQ1jKjkmmvCfU362aapvJJJsQCwBQNEqkg+w==</InverseQ><D>AsqV5FFEZQ5C2tlZgCmG3xzbMwzrfeO2oqdBFmbAAYQ/riQwNwU/6k9pjQWRdC/adRdzqagCD6ZikQMZ6nfvGbb1k3y8e+Frpmqraso4tNqBiDaEz2050MY1GpKQV4vedZzPewFprpt6fp5INVpPceRWISubab5wa6UtSnsq2Gk=</D></RSAKeyValue>")
            Console.WriteLine("Hashfile successfully created")
        Catch ex As Exception
            Console.WriteLine("Problem creating hashfile: " & ex.Message)
        End Try

        Dim debug As Boolean = False
        Dim mode As String = "Ready to upload a new version. Continue? (y/n)"
#If DEBUG Then
        mode = "I'm in DEBUG mode and won't upload anything."
        debug = True
#End If

        Console.WriteLine(mode)

        If Not debug Then
            Dim keyInfo As ConsoleKeyInfo = Console.ReadKey
            If keyInfo.Key = ConsoleKey.Y AndAlso Not debug Then
                Console.WriteLine("Uploading Files...")
                Dim ftp As New FTPUploader

                Dim files As New HashSet(Of String)
                files.Add("CacheUploaderCore.dll")
                files.Add("CacheUploader.exe")
                files.Add("hashes.txt")
                files.Add("signature.txt")

                For Each File As String In files
                    Try
                        ftp.upload(Path.Combine(args(0), File))
                        Console.WriteLine("SUCCESS: " & File & " uploaded")
                    Catch ex As Exception
                        Console.WriteLine("FAILED " & File & " uploaded")
                    End Try
                Next
            End If
        End If
        Console.WriteLine("Press any key to exit...")
        Console.ReadKey()
    End Sub

End Module

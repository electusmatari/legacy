Module Module1

    Sub Main(ByVal args As String())
        If args.Count > 0 Then
            If args(0) = "-hash" Then

            ElseIf args(0) = "-update" Then

            End If
        Else
            Console.WriteLine("Usage: -update: updates the CacheUploaderProgram; -hash creates a file containing the hashes for the program")
        End If

    End Sub

End Module

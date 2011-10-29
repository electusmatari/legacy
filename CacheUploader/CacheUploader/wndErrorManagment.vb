Imports System.Windows.Forms

Public Class wndErrorManagment

    Public Sub New(ByVal e As Exception)
        InitializeComponent()
        txtErrorText.Text = e.Message & vbCrLf & vbCrLf & "=======================================" & vbCrLf & vbCrLf & e.StackTrace
    End Sub

    Private Sub OK_Button_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles OK_Button.Click
        Me.DialogResult = System.Windows.Forms.DialogResult.OK
        Me.Close()
    End Sub

End Class

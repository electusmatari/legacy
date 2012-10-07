Imports CacheUploaderCore
Imports System.IO
Imports System.Threading.Tasks
Imports Microsoft.Win32
Imports System.Text

Public Class wndCacheUploader


#Region "Member fields"
    Private WithEvents m_controler As CacheUploaderCore.CacheUploaderControler
    Private m_loggingQueue As ConsumerQueue(Of LoggingEvent)
#End Region


#Region "delegates"
    Private Delegate Sub integerDelegate(ByVal i As Integer)
    Private Delegate Sub LoggingEventDelegate(ByVal s As LoggingEvent)
#End Region

#Region "Constructor"
    Public Sub New()
        ' This call is required by the designer.
        InitializeComponent()

        m_loggingQueue = New ConsumerQueue(Of LoggingEvent)(1, AddressOf AddNewLogToListbox, 100)

        m_controler = New CacheUploaderControler()
        AddHandler m_controler.LoggingOccured, AddressOf onLoggingOccured
        AddHandler m_controler.OpNotification, AddressOf onOpNotification
        m_controler.Init()

        initOpNotifierControlValues()



        Dim oReg As RegistryKey = Registry.CurrentUser
        Dim oKey As RegistryKey = oReg.OpenSubKey("Software\Microsoft\Windows\CurrentVersion\Run", True)
        chkStartWithWindows.Checked = oKey.GetValue("EveCacheUploader") IsNot Nothing
    End Sub

    Private Sub initOpNotifierControlValues()
        chkEnableAnnouncementNotifier.Checked = m_controler.Settings.OpAnnouncementsEnabled
        nudCheckEveryXMinutes.Value = m_controler.Settings.CheckForOpsEveryMinute
        nudShowPopupXSeconds.Value = m_controler.Settings.ShowOpAnnouncementBallonForMinutes
        nudReshowMax.Value = m_controler.Settings.ReshowOpsNotMoreThanTimes
        nudReshowOpsNotOlderThenMinutes.Value = m_controler.Settings.ReshowOpsNotOlderThanMinutes
    End Sub
#End Region

#Region "Controler EventHandlers"
    Private Sub onSettingsLoaded(ByVal sender As Object, ByVal e As CacheUploaderCore.SettingsLoadedEventArgs) Handles m_controler.SettingsLoaded
        TextBox1.Text = m_controler.AuthToken
        If m_controler.AuthToken = "" Then
            Me.WindowState = FormWindowState.Normal
            Me.Visible = True
            MessageBox.Show("You need to provide an authentication token in order to upload cache files. Click on the link to get one!", "Authentication token needed", MessageBoxButtons.OK, MessageBoxIcon.Information)
        End If
        chkDeleteFileAfterUpload.Checked = m_controler.DeleteFilesAfterUpload
    End Sub

    Private Sub onLoggingOccured(ByVal sender As Object, ByVal e As LoggingEventArgs)
        AddNewLogToListbox(e.LoggingEvent)
    End Sub

    Private Sub onOpNotification(ByVal sender As Object, ByVal e As OperationEventArgs)
        Dim title As New StringBuilder
        Dim fc As New StringBuilder

        Dim ops As IEnumerable(Of Operation) = e.Operations.OrderBy(Function(op) op.AnnouncedSinceMinutes)

        For i As Integer = 0 To ops.Count - 1
            Dim op As Operation = ops(i)

            title.Append(String.Format("{0} ({1} mins ago)", op.Title, op.AnnouncedSinceMinutes))
            fc.Append(op.FC)

            If ops.Count > 1 AndAlso i < ops.Count - 1 Then
                title.Append("; ")
                fc.Append("; ")
            End If
        Next

        NotifyIcon1.ShowBalloonTip(m_controler.Settings.ShowOpAnnouncementBallonForMinutes * 1000, title.ToString, fc.ToString, ToolTipIcon.None)

    End Sub

    Private Sub onEveInstallationsFound(ByVal sender As Object, ByVal e As EveInstallationsFoundEventArgs) Handles m_controler.EveInstallationsFound
        clbInstallations.Items.Clear()

        'Fill list box with entrys
        For Each item As EveInstallation In e.EveInstallations
            clbInstallations.Items.Add(item)
        Next

        'check all installations that are monitored

        For Each ei As EveInstallation In m_controler.InstallationsToMonitor
            Dim found As Boolean = False
            For i As Integer = 0 To clbInstallations.Items.Count - 1
                If CType(clbInstallations.Items(i), EveInstallation) = ei Then
                    clbInstallations.SetItemChecked(i, True)
                    found = True
                    Exit For
                End If
            Next

            'if we do not have the installation in our list, put it there (can happen when we don't find it automatically but it's added manually)
            If Not found Then
                clbInstallations.Items.Add(ei, True)
            End If
        Next

        'If we have no installations to monitor- check all. We suppose we have new settings then
        If m_controler.InstallationsToMonitor.Count = 0 Then
            For i As Integer = 0 To clbInstallations.Items.Count - 1
                clbInstallations.SetItemChecked(i, True)
            Next
            updateInstallationsToMonitor()
        End If
    End Sub

    Private Sub onFileUploaded(ByVal sender As Object, ByVal e As CacheUploaderCore.FileUploadedEventArgs) Handles m_controler.fileUploaded
        updateLabelCountText(e.UploadedFileCount)
    End Sub
#End Region

    Private Sub AddNewLogToListbox(ByVal le As LoggingEvent)
        If ListBoxLogging.InvokeRequired Then
            BeginInvoke(New LoggingEventDelegate(AddressOf AddNewLogToListbox), le)
        Else
            Dim message = le.ToShortString
            If le.Severity = Logger.Severity.Error Then
                message = le.ToString
            End If
            Dim index As Integer = ListBoxLogging.Items.Add(message)
            ListBoxLogging.SelectedIndex = index
        End If
    End Sub



    Private Sub updateLabelCountText(ByVal number As Integer)
        If lblCountUploaded.InvokeRequired Then
            BeginInvoke(New integerDelegate(AddressOf updateLabelCountText), number)
        Else
            lblCountUploaded.Text = "Uploaded: " & number
        End If
    End Sub


    Private Sub updateInstallationsToMonitor()
        If clbInstallations.CheckedItems.Count <> m_controler.InstallationsToMonitor.Count Then
            Dim newToMonitor As New HashSet(Of EveInstallation)
            For Each item As Object In clbInstallations.CheckedItems
                Dim itemCast As EveInstallation = CType(item, EveInstallation)
                newToMonitor.Add(itemCast)
            Next
            m_controler.InstallationsToMonitor = newToMonitor
        End If
    End Sub

#Region "GUI Events"
    Private Sub NotifyIcon1_MouseClick(ByVal sender As System.Object, ByVal e As System.Windows.Forms.MouseEventArgs) Handles NotifyIcon1.MouseClick
        If e.Button = MouseButtons.Left Then
            Me.Visible = True
            Me.WindowState = FormWindowState.Normal
        End If
    End Sub

    Private Sub LinkLabel1_LinkClicked(ByVal sender As System.Object, ByVal e As System.Windows.Forms.LinkLabelLinkClickedEventArgs) Handles LinkLabel1.LinkClicked
        Try
            System.Diagnostics.Process.Start("http://www.electusmatari.com/auth/token/")
        Catch ex As Exception
            MessageBox.Show("I tried to open the site where you can get your authentikation token. Something went wrong, sadly. Please visit the adress http://www.electusmatari.com/auth/token/ to get your token.", "Error Opening Browser", MessageBoxButtons.OK, MessageBoxIcon.Information)
        End Try

    End Sub

    Private Sub cmdDeleteSettings_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles cmdDeleteSettings.Click
        m_controler.deleteSettings()
    End Sub



    Private Sub clbInstallations_MouseUp(ByVal sender As System.Object, ByVal e As System.Windows.Forms.MouseEventArgs) Handles clbInstallations.MouseUp
        updateInstallationsToMonitor()
    End Sub

    Private Sub clbInstallations_KeyUp(ByVal sender As System.Object, ByVal e As System.Windows.Forms.KeyEventArgs) Handles clbInstallations.KeyUp
        updateInstallationsToMonitor()
    End Sub

    Private Sub cmdAddInstallation_Click(ByVal sender As System.Object, ByVal e As System.EventArgs)

    End Sub

    Private Sub TextBox1_TextChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles TextBox1.TextChanged
        If TextBox1.Text.Count > 0 Then
            m_controler.AuthToken = TextBox1.Text
            TextBox1.BackColor = Color.Green
            cmdTokenAdded.Enabled = True
        Else
            cmdTokenAdded.Enabled = False
            TextBox1.BackColor = Color.DarkRed
        End If

    End Sub

    Private Sub chkDeleteFileAfterUpload_CheckedChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles chkDeleteFileAfterUpload.CheckedChanged
        m_controler.DeleteFilesAfterUpload = chkDeleteFileAfterUpload.Checked
    End Sub

    Private Sub cmdUploadAll_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles cmdUploadAll.Click
        m_controler.uploadAllFiles()
    End Sub

    Private Sub ExitToolStripMenuItem_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ExitToolStripMenuItem.Click
        Me.Close()
    End Sub

    'Private Sub CacheUploader_FormClosing(ByVal sender As Object, ByVal e As FormClosingEventArgs) Handles Me.FormClosing
    '    ExitApplication()
    'End Sub

    Private Sub CacheUploader_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
        Dim args As String() = Environment.GetCommandLineArgs
        If args.Count > 1 AndAlso args(1) = "startMinimized" Then
            Me.WindowState = FormWindowState.Minimized
            Me.Visible = False
        End If
    End Sub

    Private Sub cmdTokenAdded_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles cmdTokenAdded.Click
        'this does nothing at the moment... Someone requested an "OK" Button here, so here it is. It works without it, but psychology is important :)
    End Sub

    Private Sub chkStartWithWindows_CheckedChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles chkStartWithWindows.CheckedChanged
        Dim oReg As RegistryKey = Registry.CurrentUser
        Dim oKey As RegistryKey = oReg.OpenSubKey("Software\Microsoft\Windows\CurrentVersion\Run", True)
        If oKey.GetValue("EveCacheUploader") Is Nothing Then
            If chkStartWithWindows.Checked Then
                Dim assemblyName As String = System.Reflection.Assembly.GetExecutingAssembly.GetName.Name()
                oKey.SetValue("EveCacheUploader", """" & Path.Combine(Application.StartupPath, assemblyName & ".exe") & """ startMinimized")
            End If
        Else
            If chkStartWithWindows.Checked = False Then
                oKey.DeleteValue("EveCacheUploader")
            End If
        End If
    End Sub
#End Region




    Private Sub chkEnableAnnouncementNotifier_CheckedChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles chkEnableAnnouncementNotifier.CheckedChanged
        If m_controler IsNot Nothing Then
            pnlAnnouncementNotifier.Enabled = chkEnableAnnouncementNotifier.Checked
            m_controler.Settings.OpAnnouncementsEnabled = chkEnableAnnouncementNotifier.Checked
        End If
    End Sub



    Private Sub cmdClearLog_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles cmdClearLog.Click
        ListBoxLogging.Items.Clear()
    End Sub


    Private Sub nudCheckEveryXSeconds_ValueChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles nudCheckEveryXMinutes.ValueChanged
        If m_controler IsNot Nothing Then
            m_controler.Settings.CheckForOpsEveryMinute = CInt(nudCheckEveryXMinutes.Value)
        End If
    End Sub

    Private Sub nudShowPopupXSeconds_ValueChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles nudShowPopupXSeconds.ValueChanged
        If m_controler IsNot Nothing Then
            m_controler.Settings.ShowOpAnnouncementBallonForMinutes = CInt(nudShowPopupXSeconds.Value)
        End If

    End Sub

    Private Sub nudReshowOpsNotOlderThenMinutes_ValueChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles nudReshowOpsNotOlderThenMinutes.ValueChanged
        If m_controler IsNot Nothing Then
            m_controler.Settings.ReshowOpsNotOlderThanMinutes = CInt(nudReshowOpsNotOlderThenMinutes.Value)
        End If
    End Sub

    Private Sub nudReshowMax_ValueChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles nudReshowMax.ValueChanged
        If m_controler IsNot Nothing Then
            m_controler.Settings.ReshowOpsNotMoreThanTimes = CInt(nudReshowMax.Value)
        End If

    End Sub

    'Private Sub ExitApplication()
    '    m_controler.Dispose()
    'End Sub

    Private Sub wndCacheUploader_Resize(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Resize
        'MyBase.OnResize(e)

        If WindowState = FormWindowState.Normal AndAlso Me.Visible = False Then
            Me.Visible = True
        ElseIf WindowState = FormWindowState.Minimized AndAlso Visible Then
            Me.Visible = False
        End If



           

    End Sub
End Class

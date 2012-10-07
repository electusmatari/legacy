<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class wndCacheUploader
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.  
    'Do not modify it using the code editor.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Me.components = New System.ComponentModel.Container()
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(wndCacheUploader))
        Me.NotifyIcon1 = New System.Windows.Forms.NotifyIcon(Me.components)
        Me.ContextMenuStrip1 = New System.Windows.Forms.ContextMenuStrip(Me.components)
        Me.ExitToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem()
        Me.ImageList1 = New System.Windows.Forms.ImageList(Me.components)
        Me.TabPageNotifier = New System.Windows.Forms.TabPage()
        Me.pnlAnnouncementNotifier = New System.Windows.Forms.Panel()
        Me.grpPopup = New System.Windows.Forms.GroupBox()
        Me.nudReshowMax = New System.Windows.Forms.NumericUpDown()
        Me.nudReshowOpsNotOlderThenMinutes = New System.Windows.Forms.NumericUpDown()
        Me.lblShowPopupXSecondsPost = New System.Windows.Forms.Label()
        Me.nudShowPopupXSeconds = New System.Windows.Forms.NumericUpDown()
        Me.lblReshowMaxPre = New System.Windows.Forms.Label()
        Me.lblShowPopupXSecondsPre = New System.Windows.Forms.Label()
        Me.lblReshowMaxPost = New System.Windows.Forms.Label()
        Me.lblReshowOpsPre = New System.Windows.Forms.Label()
        Me.lblReshowOpsPost = New System.Windows.Forms.Label()
        Me.lblCheckEveryXMinutesPost = New System.Windows.Forms.Label()
        Me.lblCheckEveryXMinutesPre = New System.Windows.Forms.Label()
        Me.nudCheckEveryXMinutes = New System.Windows.Forms.NumericUpDown()
        Me.chkEnableAnnouncementNotifier = New System.Windows.Forms.CheckBox()
        Me.TabPageReset = New System.Windows.Forms.TabPage()
        Me.grpDeleteSettings = New System.Windows.Forms.GroupBox()
        Me.lblDeleteText = New System.Windows.Forms.Label()
        Me.cmdDeleteSettings = New System.Windows.Forms.Button()
        Me.TabPageLog = New System.Windows.Forms.TabPage()
        Me.cmdClearLog = New System.Windows.Forms.Button()
        Me.ListBoxLogging = New System.Windows.Forms.ListBox()
        Me.TabPageBasic = New System.Windows.Forms.TabPage()
        Me.chkStartWithWindows = New System.Windows.Forms.CheckBox()
        Me.grpToken = New System.Windows.Forms.GroupBox()
        Me.LinkLabel1 = New System.Windows.Forms.LinkLabel()
        Me.cmdTokenAdded = New System.Windows.Forms.Button()
        Me.TextBox1 = New System.Windows.Forms.TextBox()
        Me.lblCountUploaded = New System.Windows.Forms.Label()
        Me.cmdUploadAll = New System.Windows.Forms.Button()
        Me.clbInstallations = New System.Windows.Forms.CheckedListBox()
        Me.chkDeleteFileAfterUpload = New System.Windows.Forms.CheckBox()
        Me.TabControl1 = New System.Windows.Forms.TabControl()
        Me.ContextMenuStrip1.SuspendLayout()
        Me.TabPageNotifier.SuspendLayout()
        Me.pnlAnnouncementNotifier.SuspendLayout()
        Me.grpPopup.SuspendLayout()
        CType(Me.nudReshowMax, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.nudReshowOpsNotOlderThenMinutes, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.nudShowPopupXSeconds, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.nudCheckEveryXMinutes, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.TabPageReset.SuspendLayout()
        Me.grpDeleteSettings.SuspendLayout()
        Me.TabPageLog.SuspendLayout()
        Me.TabPageBasic.SuspendLayout()
        Me.grpToken.SuspendLayout()
        Me.TabControl1.SuspendLayout()
        Me.SuspendLayout()
        '
        'NotifyIcon1
        '
        Me.NotifyIcon1.BalloonTipIcon = System.Windows.Forms.ToolTipIcon.Info
        Me.NotifyIcon1.BalloonTipTitle = "New op "
        Me.NotifyIcon1.ContextMenuStrip = Me.ContextMenuStrip1
        Me.NotifyIcon1.Icon = CType(resources.GetObject("NotifyIcon1.Icon"), System.Drawing.Icon)
        Me.NotifyIcon1.Text = "Eve Cache Uploader"
        Me.NotifyIcon1.Visible = True
        '
        'ContextMenuStrip1
        '
        Me.ContextMenuStrip1.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.ExitToolStripMenuItem})
        Me.ContextMenuStrip1.Name = "ContextMenuStrip1"
        Me.ContextMenuStrip1.Size = New System.Drawing.Size(93, 26)
        '
        'ExitToolStripMenuItem
        '
        Me.ExitToolStripMenuItem.Name = "ExitToolStripMenuItem"
        Me.ExitToolStripMenuItem.Size = New System.Drawing.Size(92, 22)
        Me.ExitToolStripMenuItem.Text = "Exit"
        '
        'ImageList1
        '
        Me.ImageList1.ImageStream = CType(resources.GetObject("ImageList1.ImageStream"), System.Windows.Forms.ImageListStreamer)
        Me.ImageList1.TransparentColor = System.Drawing.Color.Transparent
        Me.ImageList1.Images.SetKeyName(0, "medal1.png")
        Me.ImageList1.Images.SetKeyName(1, "medal2.png")
        '
        'TabPageNotifier
        '
        Me.TabPageNotifier.Controls.Add(Me.pnlAnnouncementNotifier)
        Me.TabPageNotifier.Controls.Add(Me.chkEnableAnnouncementNotifier)
        Me.TabPageNotifier.Location = New System.Drawing.Point(4, 22)
        Me.TabPageNotifier.Name = "TabPageNotifier"
        Me.TabPageNotifier.Padding = New System.Windows.Forms.Padding(3)
        Me.TabPageNotifier.Size = New System.Drawing.Size(434, 267)
        Me.TabPageNotifier.TabIndex = 4
        Me.TabPageNotifier.Text = "Op announcements"
        Me.TabPageNotifier.UseVisualStyleBackColor = True
        '
        'pnlAnnouncementNotifier
        '
        Me.pnlAnnouncementNotifier.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
                    Or System.Windows.Forms.AnchorStyles.Left) _
                    Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.pnlAnnouncementNotifier.Controls.Add(Me.grpPopup)
        Me.pnlAnnouncementNotifier.Controls.Add(Me.lblCheckEveryXMinutesPost)
        Me.pnlAnnouncementNotifier.Controls.Add(Me.lblCheckEveryXMinutesPre)
        Me.pnlAnnouncementNotifier.Controls.Add(Me.nudCheckEveryXMinutes)
        Me.pnlAnnouncementNotifier.Location = New System.Drawing.Point(6, 30)
        Me.pnlAnnouncementNotifier.Name = "pnlAnnouncementNotifier"
        Me.pnlAnnouncementNotifier.Size = New System.Drawing.Size(422, 231)
        Me.pnlAnnouncementNotifier.TabIndex = 1
        '
        'grpPopup
        '
        Me.grpPopup.Controls.Add(Me.nudReshowMax)
        Me.grpPopup.Controls.Add(Me.nudReshowOpsNotOlderThenMinutes)
        Me.grpPopup.Controls.Add(Me.lblShowPopupXSecondsPost)
        Me.grpPopup.Controls.Add(Me.nudShowPopupXSeconds)
        Me.grpPopup.Controls.Add(Me.lblReshowMaxPre)
        Me.grpPopup.Controls.Add(Me.lblShowPopupXSecondsPre)
        Me.grpPopup.Controls.Add(Me.lblReshowMaxPost)
        Me.grpPopup.Controls.Add(Me.lblReshowOpsPre)
        Me.grpPopup.Controls.Add(Me.lblReshowOpsPost)
        Me.grpPopup.Location = New System.Drawing.Point(7, 33)
        Me.grpPopup.Name = "grpPopup"
        Me.grpPopup.Size = New System.Drawing.Size(330, 95)
        Me.grpPopup.TabIndex = 3
        Me.grpPopup.TabStop = False
        Me.grpPopup.Text = "Popup"
        '
        'nudReshowMax
        '
        Me.nudReshowMax.Location = New System.Drawing.Point(154, 68)
        Me.nudReshowMax.Maximum = New Decimal(New Integer() {1000, 0, 0, 0})
        Me.nudReshowMax.Name = "nudReshowMax"
        Me.nudReshowMax.Size = New System.Drawing.Size(74, 20)
        Me.nudReshowMax.TabIndex = 0
        Me.nudReshowMax.Value = New Decimal(New Integer() {30, 0, 0, 0})
        '
        'nudReshowOpsNotOlderThenMinutes
        '
        Me.nudReshowOpsNotOlderThenMinutes.Location = New System.Drawing.Point(154, 43)
        Me.nudReshowOpsNotOlderThenMinutes.Maximum = New Decimal(New Integer() {240, 0, 0, 0})
        Me.nudReshowOpsNotOlderThenMinutes.Minimum = New Decimal(New Integer() {1, 0, 0, 0})
        Me.nudReshowOpsNotOlderThenMinutes.Name = "nudReshowOpsNotOlderThenMinutes"
        Me.nudReshowOpsNotOlderThenMinutes.Size = New System.Drawing.Size(74, 20)
        Me.nudReshowOpsNotOlderThenMinutes.TabIndex = 0
        Me.nudReshowOpsNotOlderThenMinutes.Value = New Decimal(New Integer() {30, 0, 0, 0})
        '
        'lblShowPopupXSecondsPost
        '
        Me.lblShowPopupXSecondsPost.AutoSize = True
        Me.lblShowPopupXSecondsPost.Location = New System.Drawing.Point(234, 20)
        Me.lblShowPopupXSecondsPost.Name = "lblShowPopupXSecondsPost"
        Me.lblShowPopupXSecondsPost.Size = New System.Drawing.Size(50, 13)
        Me.lblShowPopupXSecondsPost.TabIndex = 1
        Me.lblShowPopupXSecondsPost.Text = "seconds "
        '
        'nudShowPopupXSeconds
        '
        Me.nudShowPopupXSeconds.Location = New System.Drawing.Point(154, 18)
        Me.nudShowPopupXSeconds.Maximum = New Decimal(New Integer() {1800, 0, 0, 0})
        Me.nudShowPopupXSeconds.Minimum = New Decimal(New Integer() {5, 0, 0, 0})
        Me.nudShowPopupXSeconds.Name = "nudShowPopupXSeconds"
        Me.nudShowPopupXSeconds.Size = New System.Drawing.Size(74, 20)
        Me.nudShowPopupXSeconds.TabIndex = 0
        Me.nudShowPopupXSeconds.Value = New Decimal(New Integer() {20, 0, 0, 0})
        '
        'lblReshowMaxPre
        '
        Me.lblReshowMaxPre.AutoSize = True
        Me.lblReshowMaxPre.Location = New System.Drawing.Point(6, 71)
        Me.lblReshowMaxPre.Name = "lblReshowMaxPre"
        Me.lblReshowMaxPre.Size = New System.Drawing.Size(86, 13)
        Me.lblReshowMaxPre.TabIndex = 1
        Me.lblReshowMaxPre.Text = "Reshow maximal"
        '
        'lblShowPopupXSecondsPre
        '
        Me.lblShowPopupXSecondsPre.AutoSize = True
        Me.lblShowPopupXSecondsPre.Location = New System.Drawing.Point(7, 20)
        Me.lblShowPopupXSecondsPre.Name = "lblShowPopupXSecondsPre"
        Me.lblShowPopupXSecondsPre.Size = New System.Drawing.Size(49, 13)
        Me.lblShowPopupXSecondsPre.TabIndex = 1
        Me.lblShowPopupXSecondsPre.Text = "Show for"
        '
        'lblReshowMaxPost
        '
        Me.lblReshowMaxPost.AutoSize = True
        Me.lblReshowMaxPost.Location = New System.Drawing.Point(234, 71)
        Me.lblReshowMaxPost.Name = "lblReshowMaxPost"
        Me.lblReshowMaxPost.Size = New System.Drawing.Size(31, 13)
        Me.lblReshowMaxPost.TabIndex = 1
        Me.lblReshowMaxPost.Text = "times"
        '
        'lblReshowOpsPre
        '
        Me.lblReshowOpsPre.AutoSize = True
        Me.lblReshowOpsPre.Location = New System.Drawing.Point(6, 45)
        Me.lblReshowOpsPre.Name = "lblReshowOpsPre"
        Me.lblReshowOpsPre.Size = New System.Drawing.Size(141, 13)
        Me.lblReshowOpsPre.TabIndex = 1
        Me.lblReshowOpsPre.Text = "Reshow while not older than"
        '
        'lblReshowOpsPost
        '
        Me.lblReshowOpsPost.AutoSize = True
        Me.lblReshowOpsPost.Location = New System.Drawing.Point(234, 45)
        Me.lblReshowOpsPost.Name = "lblReshowOpsPost"
        Me.lblReshowOpsPost.Size = New System.Drawing.Size(43, 13)
        Me.lblReshowOpsPost.TabIndex = 1
        Me.lblReshowOpsPost.Text = "minutes"
        '
        'lblCheckEveryXMinutesPost
        '
        Me.lblCheckEveryXMinutesPost.AutoSize = True
        Me.lblCheckEveryXMinutesPost.Location = New System.Drawing.Point(173, 11)
        Me.lblCheckEveryXMinutesPost.Name = "lblCheckEveryXMinutesPost"
        Me.lblCheckEveryXMinutesPost.Size = New System.Drawing.Size(160, 13)
        Me.lblCheckEveryXMinutesPost.TabIndex = 1
        Me.lblCheckEveryXMinutesPost.Text = "minutes for new announcements"
        '
        'lblCheckEveryXMinutesPre
        '
        Me.lblCheckEveryXMinutesPre.AutoSize = True
        Me.lblCheckEveryXMinutesPre.Location = New System.Drawing.Point(4, 9)
        Me.lblCheckEveryXMinutesPre.Name = "lblCheckEveryXMinutesPre"
        Me.lblCheckEveryXMinutesPre.Size = New System.Drawing.Size(70, 13)
        Me.lblCheckEveryXMinutesPre.TabIndex = 1
        Me.lblCheckEveryXMinutesPre.Text = "Check every "
        '
        'nudCheckEveryXMinutes
        '
        Me.nudCheckEveryXMinutes.Location = New System.Drawing.Point(93, 9)
        Me.nudCheckEveryXMinutes.Maximum = New Decimal(New Integer() {120, 0, 0, 0})
        Me.nudCheckEveryXMinutes.Minimum = New Decimal(New Integer() {1, 0, 0, 0})
        Me.nudCheckEveryXMinutes.Name = "nudCheckEveryXMinutes"
        Me.nudCheckEveryXMinutes.Size = New System.Drawing.Size(74, 20)
        Me.nudCheckEveryXMinutes.TabIndex = 0
        Me.nudCheckEveryXMinutes.Value = New Decimal(New Integer() {1, 0, 0, 0})
        '
        'chkEnableAnnouncementNotifier
        '
        Me.chkEnableAnnouncementNotifier.AutoSize = True
        Me.chkEnableAnnouncementNotifier.Checked = True
        Me.chkEnableAnnouncementNotifier.CheckState = System.Windows.Forms.CheckState.Checked
        Me.chkEnableAnnouncementNotifier.Location = New System.Drawing.Point(6, 6)
        Me.chkEnableAnnouncementNotifier.Name = "chkEnableAnnouncementNotifier"
        Me.chkEnableAnnouncementNotifier.Size = New System.Drawing.Size(139, 17)
        Me.chkEnableAnnouncementNotifier.TabIndex = 0
        Me.chkEnableAnnouncementNotifier.Text = "Announcement enabled"
        Me.chkEnableAnnouncementNotifier.UseVisualStyleBackColor = True
        '
        'TabPageReset
        '
        Me.TabPageReset.Controls.Add(Me.grpDeleteSettings)
        Me.TabPageReset.Location = New System.Drawing.Point(4, 22)
        Me.TabPageReset.Name = "TabPageReset"
        Me.TabPageReset.Size = New System.Drawing.Size(434, 267)
        Me.TabPageReset.TabIndex = 2
        Me.TabPageReset.Text = "Reset Settings"
        Me.TabPageReset.UseVisualStyleBackColor = True
        '
        'grpDeleteSettings
        '
        Me.grpDeleteSettings.Controls.Add(Me.lblDeleteText)
        Me.grpDeleteSettings.Controls.Add(Me.cmdDeleteSettings)
        Me.grpDeleteSettings.Location = New System.Drawing.Point(8, 3)
        Me.grpDeleteSettings.Name = "grpDeleteSettings"
        Me.grpDeleteSettings.Size = New System.Drawing.Size(195, 210)
        Me.grpDeleteSettings.TabIndex = 5
        Me.grpDeleteSettings.TabStop = False
        Me.grpDeleteSettings.Text = "DeleteSettings"
        '
        'lblDeleteText
        '
        Me.lblDeleteText.Location = New System.Drawing.Point(7, 20)
        Me.lblDeleteText.Name = "lblDeleteText"
        Me.lblDeleteText.Size = New System.Drawing.Size(182, 75)
        Me.lblDeleteText.TabIndex = 5
        Me.lblDeleteText.Text = "This will delete all safed settings. You can look at the safed settings in the Se" & _
            "ttings.xml file in the program directory to see what's in there and what will be" & _
            " deleted."
        '
        'cmdDeleteSettings
        '
        Me.cmdDeleteSettings.Anchor = CType((System.Windows.Forms.AnchorStyles.Bottom Or System.Windows.Forms.AnchorStyles.Left), System.Windows.Forms.AnchorStyles)
        Me.cmdDeleteSettings.Location = New System.Drawing.Point(10, 98)
        Me.cmdDeleteSettings.Name = "cmdDeleteSettings"
        Me.cmdDeleteSettings.Size = New System.Drawing.Size(95, 23)
        Me.cmdDeleteSettings.TabIndex = 4
        Me.cmdDeleteSettings.Text = "Delete Settings"
        Me.cmdDeleteSettings.UseVisualStyleBackColor = True
        '
        'TabPageLog
        '
        Me.TabPageLog.Controls.Add(Me.cmdClearLog)
        Me.TabPageLog.Controls.Add(Me.ListBoxLogging)
        Me.TabPageLog.Location = New System.Drawing.Point(4, 22)
        Me.TabPageLog.Name = "TabPageLog"
        Me.TabPageLog.Size = New System.Drawing.Size(434, 267)
        Me.TabPageLog.TabIndex = 3
        Me.TabPageLog.Text = "Log"
        Me.TabPageLog.UseVisualStyleBackColor = True
        '
        'cmdClearLog
        '
        Me.cmdClearLog.Anchor = CType((System.Windows.Forms.AnchorStyles.Bottom Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.cmdClearLog.Location = New System.Drawing.Point(351, 241)
        Me.cmdClearLog.Name = "cmdClearLog"
        Me.cmdClearLog.Size = New System.Drawing.Size(75, 23)
        Me.cmdClearLog.TabIndex = 1
        Me.cmdClearLog.Text = "Clear"
        Me.cmdClearLog.UseVisualStyleBackColor = True
        '
        'ListBoxLogging
        '
        Me.ListBoxLogging.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
                    Or System.Windows.Forms.AnchorStyles.Left) _
                    Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.ListBoxLogging.FormattingEnabled = True
        Me.ListBoxLogging.HorizontalScrollbar = True
        Me.ListBoxLogging.Location = New System.Drawing.Point(0, 0)
        Me.ListBoxLogging.Name = "ListBoxLogging"
        Me.ListBoxLogging.Size = New System.Drawing.Size(434, 238)
        Me.ListBoxLogging.TabIndex = 0
        '
        'TabPageBasic
        '
        Me.TabPageBasic.Controls.Add(Me.chkStartWithWindows)
        Me.TabPageBasic.Controls.Add(Me.grpToken)
        Me.TabPageBasic.Controls.Add(Me.lblCountUploaded)
        Me.TabPageBasic.Controls.Add(Me.cmdUploadAll)
        Me.TabPageBasic.Controls.Add(Me.clbInstallations)
        Me.TabPageBasic.Controls.Add(Me.chkDeleteFileAfterUpload)
        Me.TabPageBasic.Location = New System.Drawing.Point(4, 22)
        Me.TabPageBasic.Name = "TabPageBasic"
        Me.TabPageBasic.Padding = New System.Windows.Forms.Padding(3)
        Me.TabPageBasic.Size = New System.Drawing.Size(434, 267)
        Me.TabPageBasic.TabIndex = 1
        Me.TabPageBasic.Text = "Basic Settings"
        Me.TabPageBasic.UseVisualStyleBackColor = True
        '
        'chkStartWithWindows
        '
        Me.chkStartWithWindows.AutoSize = True
        Me.chkStartWithWindows.Location = New System.Drawing.Point(8, 7)
        Me.chkStartWithWindows.Name = "chkStartWithWindows"
        Me.chkStartWithWindows.Size = New System.Drawing.Size(194, 17)
        Me.chkStartWithWindows.TabIndex = 11
        Me.chkStartWithWindows.Text = "Start CacheUploader with Windows"
        Me.chkStartWithWindows.UseVisualStyleBackColor = True
        '
        'grpToken
        '
        Me.grpToken.Anchor = CType(((System.Windows.Forms.AnchorStyles.Bottom Or System.Windows.Forms.AnchorStyles.Left) _
                    Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.grpToken.Controls.Add(Me.LinkLabel1)
        Me.grpToken.Controls.Add(Me.cmdTokenAdded)
        Me.grpToken.Controls.Add(Me.TextBox1)
        Me.grpToken.Location = New System.Drawing.Point(6, 198)
        Me.grpToken.Name = "grpToken"
        Me.grpToken.Size = New System.Drawing.Size(418, 38)
        Me.grpToken.TabIndex = 10
        Me.grpToken.TabStop = False
        Me.grpToken.Text = "Authentication Token"
        '
        'LinkLabel1
        '
        Me.LinkLabel1.AutoSize = True
        Me.LinkLabel1.LinkBehavior = System.Windows.Forms.LinkBehavior.HoverUnderline
        Me.LinkLabel1.Location = New System.Drawing.Point(6, 14)
        Me.LinkLabel1.Name = "LinkLabel1"
        Me.LinkLabel1.Size = New System.Drawing.Size(131, 13)
        Me.LinkLabel1.TabIndex = 6
        Me.LinkLabel1.TabStop = True
        Me.LinkLabel1.Text = "EM Authentication Token:"
        '
        'cmdTokenAdded
        '
        Me.cmdTokenAdded.Anchor = CType((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.cmdTokenAdded.Location = New System.Drawing.Point(364, 10)
        Me.cmdTokenAdded.Name = "cmdTokenAdded"
        Me.cmdTokenAdded.Size = New System.Drawing.Size(48, 20)
        Me.cmdTokenAdded.TabIndex = 9
        Me.cmdTokenAdded.Text = "OK"
        Me.cmdTokenAdded.UseVisualStyleBackColor = True
        '
        'TextBox1
        '
        Me.TextBox1.Anchor = CType(((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Left) _
                    Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.TextBox1.BackColor = System.Drawing.Color.Maroon
        Me.TextBox1.Location = New System.Drawing.Point(143, 11)
        Me.TextBox1.Name = "TextBox1"
        Me.TextBox1.Size = New System.Drawing.Size(215, 20)
        Me.TextBox1.TabIndex = 5
        '
        'lblCountUploaded
        '
        Me.lblCountUploaded.Anchor = CType((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.lblCountUploaded.AutoSize = True
        Me.lblCountUploaded.Location = New System.Drawing.Point(299, 7)
        Me.lblCountUploaded.Name = "lblCountUploaded"
        Me.lblCountUploaded.Size = New System.Drawing.Size(65, 13)
        Me.lblCountUploaded.TabIndex = 8
        Me.lblCountUploaded.Text = "Uploaded: 0"
        '
        'cmdUploadAll
        '
        Me.cmdUploadAll.Anchor = CType((System.Windows.Forms.AnchorStyles.Bottom Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.cmdUploadAll.Location = New System.Drawing.Point(269, 238)
        Me.cmdUploadAll.Name = "cmdUploadAll"
        Me.cmdUploadAll.Size = New System.Drawing.Size(157, 23)
        Me.cmdUploadAll.TabIndex = 7
        Me.cmdUploadAll.Text = "Upload all existing cache files"
        Me.cmdUploadAll.UseVisualStyleBackColor = True
        '
        'clbInstallations
        '
        Me.clbInstallations.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
                    Or System.Windows.Forms.AnchorStyles.Left) _
                    Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.clbInstallations.CheckOnClick = True
        Me.clbInstallations.FormattingEnabled = True
        Me.clbInstallations.HorizontalScrollbar = True
        Me.clbInstallations.Location = New System.Drawing.Point(6, 24)
        Me.clbInstallations.Name = "clbInstallations"
        Me.clbInstallations.Size = New System.Drawing.Size(420, 169)
        Me.clbInstallations.TabIndex = 3
        '
        'chkDeleteFileAfterUpload
        '
        Me.chkDeleteFileAfterUpload.Anchor = CType((System.Windows.Forms.AnchorStyles.Bottom Or System.Windows.Forms.AnchorStyles.Left), System.Windows.Forms.AnchorStyles)
        Me.chkDeleteFileAfterUpload.AutoSize = True
        Me.chkDeleteFileAfterUpload.Location = New System.Drawing.Point(8, 242)
        Me.chkDeleteFileAfterUpload.Name = "chkDeleteFileAfterUpload"
        Me.chkDeleteFileAfterUpload.Size = New System.Drawing.Size(170, 17)
        Me.chkDeleteFileAfterUpload.TabIndex = 2
        Me.chkDeleteFileAfterUpload.Text = "Delete cache files after upload"
        Me.chkDeleteFileAfterUpload.UseVisualStyleBackColor = True
        '
        'TabControl1
        '
        Me.TabControl1.Controls.Add(Me.TabPageBasic)
        Me.TabControl1.Controls.Add(Me.TabPageLog)
        Me.TabControl1.Controls.Add(Me.TabPageReset)
        Me.TabControl1.Controls.Add(Me.TabPageNotifier)
        Me.TabControl1.Dock = System.Windows.Forms.DockStyle.Fill
        Me.TabControl1.Location = New System.Drawing.Point(0, 0)
        Me.TabControl1.Name = "TabControl1"
        Me.TabControl1.SelectedIndex = 0
        Me.TabControl1.Size = New System.Drawing.Size(442, 293)
        Me.TabControl1.TabIndex = 7
        '
        'wndCacheUploader
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.ClientSize = New System.Drawing.Size(442, 293)
        Me.Controls.Add(Me.TabControl1)
        Me.Icon = CType(resources.GetObject("$this.Icon"), System.Drawing.Icon)
        Me.MaximizeBox = False
        Me.MinimumSize = New System.Drawing.Size(458, 331)
        Me.Name = "wndCacheUploader"
        Me.ShowInTaskbar = False
        Me.Text = "EVE Cache Uploader"
        Me.ContextMenuStrip1.ResumeLayout(False)
        Me.TabPageNotifier.ResumeLayout(False)
        Me.TabPageNotifier.PerformLayout()
        Me.pnlAnnouncementNotifier.ResumeLayout(False)
        Me.pnlAnnouncementNotifier.PerformLayout()
        Me.grpPopup.ResumeLayout(False)
        Me.grpPopup.PerformLayout()
        CType(Me.nudReshowMax, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.nudReshowOpsNotOlderThenMinutes, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.nudShowPopupXSeconds, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.nudCheckEveryXMinutes, System.ComponentModel.ISupportInitialize).EndInit()
        Me.TabPageReset.ResumeLayout(False)
        Me.grpDeleteSettings.ResumeLayout(False)
        Me.TabPageLog.ResumeLayout(False)
        Me.TabPageBasic.ResumeLayout(False)
        Me.TabPageBasic.PerformLayout()
        Me.grpToken.ResumeLayout(False)
        Me.grpToken.PerformLayout()
        Me.TabControl1.ResumeLayout(False)
        Me.ResumeLayout(False)

    End Sub
    Friend WithEvents NotifyIcon1 As System.Windows.Forms.NotifyIcon
    Friend WithEvents ContextMenuStrip1 As System.Windows.Forms.ContextMenuStrip
    Friend WithEvents ExitToolStripMenuItem As System.Windows.Forms.ToolStripMenuItem
    Friend WithEvents ImageList1 As System.Windows.Forms.ImageList
    Friend WithEvents TabPageNotifier As System.Windows.Forms.TabPage
    Friend WithEvents pnlAnnouncementNotifier As System.Windows.Forms.Panel
    Friend WithEvents grpPopup As System.Windows.Forms.GroupBox
    Friend WithEvents lblShowPopupXSecondsPost As System.Windows.Forms.Label
    Friend WithEvents nudShowPopupXSeconds As System.Windows.Forms.NumericUpDown
    Friend WithEvents lblShowPopupXSecondsPre As System.Windows.Forms.Label
    Friend WithEvents lblCheckEveryXMinutesPost As System.Windows.Forms.Label
    Friend WithEvents lblCheckEveryXMinutesPre As System.Windows.Forms.Label
    Friend WithEvents nudCheckEveryXMinutes As System.Windows.Forms.NumericUpDown
    Friend WithEvents chkEnableAnnouncementNotifier As System.Windows.Forms.CheckBox
    Friend WithEvents TabPageReset As System.Windows.Forms.TabPage
    Friend WithEvents grpDeleteSettings As System.Windows.Forms.GroupBox
    Friend WithEvents lblDeleteText As System.Windows.Forms.Label
    Friend WithEvents cmdDeleteSettings As System.Windows.Forms.Button
    Friend WithEvents TabPageLog As System.Windows.Forms.TabPage
    Friend WithEvents ListBoxLogging As System.Windows.Forms.ListBox
    Friend WithEvents TabPageBasic As System.Windows.Forms.TabPage
    Friend WithEvents chkStartWithWindows As System.Windows.Forms.CheckBox
    Friend WithEvents grpToken As System.Windows.Forms.GroupBox
    Friend WithEvents LinkLabel1 As System.Windows.Forms.LinkLabel
    Friend WithEvents cmdTokenAdded As System.Windows.Forms.Button
    Friend WithEvents TextBox1 As System.Windows.Forms.TextBox
    Friend WithEvents lblCountUploaded As System.Windows.Forms.Label
    Friend WithEvents cmdUploadAll As System.Windows.Forms.Button
    Friend WithEvents clbInstallations As System.Windows.Forms.CheckedListBox
    Friend WithEvents chkDeleteFileAfterUpload As System.Windows.Forms.CheckBox
    Friend WithEvents TabControl1 As System.Windows.Forms.TabControl
    Friend WithEvents cmdClearLog As System.Windows.Forms.Button
    Friend WithEvents nudReshowMax As System.Windows.Forms.NumericUpDown
    Friend WithEvents nudReshowOpsNotOlderThenMinutes As System.Windows.Forms.NumericUpDown
    Friend WithEvents lblReshowMaxPre As System.Windows.Forms.Label
    Friend WithEvents lblReshowMaxPost As System.Windows.Forms.Label
    Friend WithEvents lblReshowOpsPre As System.Windows.Forms.Label
    Friend WithEvents lblReshowOpsPost As System.Windows.Forms.Label

End Class

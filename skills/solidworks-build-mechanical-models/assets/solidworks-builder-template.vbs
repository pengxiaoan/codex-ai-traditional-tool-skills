Option Explicit

' Copy this file into a project and replace BuildSamplePart with task geometry.
' SolidWorks API length values are metres.

Const swDocPART = 1
Const swSaveAsCurrentVersion = 0
Const swSaveAsOptionsSilent = 1

Dim fso, scriptDir, outputDir, logFile, swApp, partTemplate
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
outputDir = fso.BuildPath(scriptDir, "output")
If Not fso.FolderExists(outputDir) Then fso.CreateFolder outputDir
Set logFile = fso.CreateTextFile(fso.BuildPath(outputDir, "build_log.txt"), True, True)

On Error Resume Next
Set swApp = GetObject(, "SldWorks.Application")
If swApp Is Nothing Then Set swApp = CreateObject("SldWorks.Application")
On Error GoTo 0
If swApp Is Nothing Then Fail "Unable to start SOLIDWORKS."

swApp.Visible = True
partTemplate = swApp.GetUserPreferenceStringValue(8)
If Len(partTemplate) = 0 Or Left(partTemplate, 1) = "~" Or Not fso.FileExists(partTemplate) Then
  partTemplate = "C:\ProgramData\SolidWorks\SOLIDWORKS 2025\templates\gb_part.prtdot"
End If
If Not fso.FileExists(partTemplate) Then Fail "Configure a valid part template path."

BuildSamplePart
LogLine "BUILD_COMPLETE"
logFile.Close
WScript.Quit 0

Sub BuildSamplePart()
  Dim doc, feature, outputPath
  Set doc = swApp.NewDocument(partTemplate, swDocPART, 0, 0)
  If doc Is Nothing Then Fail "Unable to create part."
  WScript.Sleep 800

  BeginSketchOnFirstReferencePlane doc
  doc.SketchManager.CreateCircleByRadius 0, 0, 0, 0.025
  doc.SketchManager.InsertSketch True

  Set feature = doc.FeatureManager.FeatureExtrusion2(True, False, False, 0, 0, _
    0.010, 0.010, False, False, False, False, 0, 0, False, False, _
    False, False, True, True, True, 0, 0, False)
  If feature Is Nothing Then Fail "Sample extrusion failed."

  doc.ForceRebuild3 False
  doc.ShowNamedView2 "*Isometric", 7
  doc.ViewZoomtofit2

  outputPath = fso.BuildPath(outputDir, "sample_part.SLDPRT")
  SaveAndVerify doc, outputPath
  swApp.CloseDoc doc.GetTitle
End Sub

Sub BeginSketchOnFirstReferencePlane(doc)
  Dim feature, selected, attempt, typeName
  selected = False
  For attempt = 1 To 5
    On Error Resume Next
    Err.Clear
    doc.ClearSelection2 True
    Set feature = doc.FirstFeature
    Do While Not (feature Is Nothing)
      typeName = ""
      Err.Clear
      typeName = feature.GetTypeName2
      If Err.Number = 0 And typeName = "RefPlane" Then
        selected = feature.Select2(False, 0)
        Exit Do
      End If
      Err.Clear
      Set feature = feature.GetNextFeature
      If Err.Number <> 0 Then Exit Do
    Loop
    On Error GoTo 0
    If selected Then Exit For
    WScript.Sleep 500
  Next
  If selected = False Then Fail "Unable to select a reference plane."
  doc.SketchManager.InsertSketch True
End Sub

Sub SaveAndVerify(doc, path)
  Dim result
  result = doc.SaveAs3(path, swSaveAsCurrentVersion, swSaveAsOptionsSilent)
  If Not fso.FileExists(path) Then Fail "Save failed: " & path
  LogLine "Saved: " & path
End Sub

Sub LogLine(message)
  logFile.WriteLine Now & "  " & message
End Sub

Sub Fail(message)
  On Error Resume Next
  LogLine "ERROR: " & message & " | VB error " & Err.Number & ": " & Err.Description
  logFile.Close
  WScript.Quit 1
End Sub

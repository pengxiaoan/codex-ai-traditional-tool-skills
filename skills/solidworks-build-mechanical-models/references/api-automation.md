# SolidWorks API automation

Read this before editing VBScript/COM automation. Examples use VBScript because it is available on standard Windows installations.

## Connect and preflight

```vbscript
On Error Resume Next
Set swApp = GetObject(, "SldWorks.Application")
If swApp Is Nothing Then Set swApp = CreateObject("SldWorks.Application")
On Error GoTo 0
If swApp Is Nothing Then Fail "Unable to start SOLIDWORKS."
swApp.Visible = True
```

Retrieve default templates with preferences `8` (part) and `9` (assembly). A value beginning with `~`, an empty value, or a missing file is invalid. Fall back only to an existing version-specific template and log the chosen path.

## Avoid localized plane names

Do not select `Front Plane` or its translated label by name. Select a reference plane by feature type:

```vbscript
Set feat = doc.FirstFeature
Do While Not feat Is Nothing
  If feat.GetTypeName2 = "RefPlane" Then
    ok = feat.Select2(False, 0)
    Exit Do
  End If
  Set feat = feat.GetNextFeature
Loop
```

For production automation, identify the intended plane by verified orientation/reference geometry rather than assuming the first reference plane is always suitable.

## Sketch and extrusion pattern

SolidWorks API lengths are metres.

```vbscript
doc.SketchManager.InsertSketch True
doc.SketchManager.CreateCircleByRadius 0, 0, 0, 0.025
doc.SketchManager.InsertSketch True
Set feature = doc.FeatureManager.FeatureExtrusion2( _
  True, False, False, 0, 0, 0.010, 0.010, _
  False, False, False, False, 0, 0, False, False, _
  False, False, True, True, True, 0, 0, False)
If feature Is Nothing Then Fail "Extrusion failed."
```

Validate every generated profile for closure and self-intersection. For lobed/freeform profiles, choose a deterministic sample count and repeat the first point at the end.

## Save behavior

`SaveAs3` return behavior can be exposed differently across COM/version boundaries. Do not use bitwise `Not` on its result. Save, then verify the filesystem:

```vbscript
result = doc.SaveAs3(path, 0, 1)
If Not fso.FileExists(path) Then Fail "Save failed: " & path
```

Use deterministic ASCII filenames for automation when cross-tool encoding is uncertain. User-facing names may be localized after verification.

## Assembly insertion

`AddComponent5` positions a component origin in metres:

```vbscript
Set comp = assy.AddComponent5(path, 0, "", False, "", x, y, z)
If comp Is Nothing Then Fail "Component insertion failed: " & path
```

Absolute insertion is a layout technique, not a mate. Add concentric, coincident, distance, angle, gear, or limit mates when kinematic behavior is an acceptance requirement.

For repeated components, calculate positions deterministically:

```vbscript
For i = 0 To count - 1
  angle = 6.28318530717959 * i / count + phase
  x = radius * Cos(angle)
  y = radius * Sin(angle)
  ' Insert or pattern the component at x, y.
Next
```

## Rebuild and review

After each major part and at final assembly:

```vbscript
doc.ForceRebuild3 False
doc.ShowNamedView2 "*Isometric", 7
doc.ViewZoomtofit2
```

Standard named views beginning with `*` are more stable than localized labels. Export a final bitmap if supported:

```vbscript
doc.SaveBMP previewPath, 1600, 900
```

## Error handling

- Use `On Error Resume Next` only around a known optional/version-dependent call.
- Restore `On Error GoTo 0` immediately.
- Log templates, saves, fatal errors, counts, and `BUILD_COMPLETE`.
- Exit nonzero on failure.
- Verify that the workflow owns a document before closing it.
- Keep the final assembly open when user inspection is part of the request.

Use [../assets/solidworks-builder-template.vbs](../assets/solidworks-builder-template.vbs) for a tested starting structure.

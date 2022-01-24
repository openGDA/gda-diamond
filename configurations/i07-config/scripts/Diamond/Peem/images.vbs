call SingleShot

Dim UView

Sub SingleShot
	Set UView=CreateObject("UviewInt")
	imageFolder="C:\temp\testing\"
	imageNumber=1
	
	'To select/open a new image window
	UView.SelectImage imageNumber,"Image Testing"

	t0 = Timer()
	UView.CameraExpTime=1000
	t1 = Timer()
	Wscript.echo("CameraExpTime: " & FormatNumber(t1-t0, 3))

	imageName=imageFolder+"testing.tif"

	t0 = Timer()
	UView.AcquisitionInProgress=False
	UView.AcquireSingleImage 1       'start image acquisition
	t1 = Timer()
	Wscript.echo("AcquireSingleImage: " & FormatNumber(t1-t0, 3))

	t1 = Timer()
	t00=Timer()
	while UView.AcquisitionInProgress
		t2 = Timer()
		Wscript.echo("---> " & FormatNumber(t2-t1, 3))
		t1=t2
		WScript.Sleep(100)	       ' sleep 100 msec 		
	wend

	t3 = Timer()

	't0 = Timer()
	'UView.ExportImage imageName,5,0
	't1 = Timer()
	'Wscript.echo("ExportImage: " & FormatNumber(t1-t0, 3))

	Wscript.echo("Waiting after triggering: " & FormatNumber(t3-t00, 3))
	Wscript.echo("Total: " & FormatNumber(t3-t0, 3))
		
End Sub

#archive
$compress = @{
	Path = "C:\ProgramData\SaltProject\Salt\var\log", "C:\Lenovo_Support\Salt"
	CompressionLevel = "Fastest"
	DestinationPath = "C:\ProgramData\SaltProject\Salt\var\log\Lenovo_Support/logs.zip"
}

#archives logs
function packUp
{
	<# if (Test-Path  "C:\ProgramData\SaltProject\Salt\var\log\temp" -PathType Container)
	{
		Write-Output "temp already exists!" "rewriting temp..."
		rmdir "C:\ProgramData\SaltProject\Salt\var\log\temp" -Force -Recurse
	}
		Write-Output "creating temp..."
		mkdir C:\ProgramData\SaltProject\Salt\var\log\temp
	cd C:\ProgramData\SaltProject\Salt\var\log\temp
	foreach ($path in $PathToLogFiles)
	{
		Write-Output $path -Recurse
		cp $path ./
	}
	Compress-Archive -Path ./* -DestinationPath ./logs.zip -Recurse 
	if ($? -eq $true)
	{
		Write-Output "Success!"
	}
	else
	{
		Write-Output "Fail"
		Exit
	}
	cp logs.zip C:\ProgramData\SaltProject\Salt\var\log\Lenovo_Support
	rm C:\ProgramData\SaltProject\Salt\var\log\temp -Force -Recurse 
	Write-Output "deleting temp..." #>
	if (Test-Path "C:\ProgramData\SaltProject\Salt\var\log\Lenovo_Support")
	{
		Write-Output "Lenovo_Support already exists"
	}
	else
	{
		mkdir "C:\ProgramData\SaltProject\Salt\var\log\Lenovo_Support"
	}
	Compress-Archive @compress
	if ($? -eq $true)
	{
		Write-Output "Success!"
	}
	else
	{
		Write-Output "Fail"
		Exit
	}
}

function main
{
	if (Test-Path C:\ProgramData\SaltProject\Salt\var\log\logs.zip -PathType Leaf)
	{
		Write-Output "cleaning up..."
		rm -Force C:\ProgramData\SaltProject\Salt\var\log\logs.zip
	}
	Write-Output "archiving..."
	packUp
}

main
#Example Json:
# diskDrives": 
# [
            # {
              # "model": "MTFDDAV240TDS-1AW1ZA", +
              # "healthState": "OK", +
              # "numberOfBlocks": 0, 
              # "interfaceType": "SATA", +
              # "serialNumber": "262395C5", +
              # "blockSize": 0,
              # "mediaType": "SSD", +
              # "diskState": "OK", 
              # "bay": 1, +
              # "description": "240GB M.2 SATA SSD", +
              # "manufacturer": "LEN", +
              # "name": "Drive.M.2_Bay1", +
              # "uuid": "500A0751-2623-95C5-", +
              # "partNumber": "SSS7A23276", + 
              # "largestAvailableSize": 0,  
              # "capacity": 240000000000, +
              # "m2Location": "", 
              # "firmware": [
                # {
                  # "name": "MTFDDAV240TDS-1AW1ZA", +
                  # "date": "", 
                  # "type": "Firmware", 
                  # "build": "0",
                  # "version": "MP33", +
                  # "role": "", 
                  # "status": "Active", +
                  # "classifications": [
                    # 10 
                  # ],
                  # "revision": "0",
                  # "softwareID": "MTFDDAV240TDS-1AW1ZA" 
                # }
              # ]
     
			# }
# ]


$Json = @{"diskDrives" = [System.Collections.ArrayList]@()}

function diskCount
{
	return (get-disk).Number.count
}

#creates a hashtable in order for values to be able to be added 
function diskHashBuild
{
	Write-Output "$(diskCount) disk(s) found"
	Get-WmiObject Win32_DiskDrive | ForEach-Object {
		$Json["diskDrives"].Add(@{})
	}
}

#adds needed info to the hashtable
function fillThatHashUp
{
	$i = 0
 	Get-WmiObject Win32_DiskDrive | ForEach-Object { 
		$disk = $_
		$WmiInfoNeeded = 
		@{

			manufacturer = $($disk.Caption).Substring(0,$($disk.Caption).IndexOf(" "))
			serialNumber = $disk.SerialNumber
			description = $disk.Caption
			capacity = '{0:N2} GB' -f ($disk.Size / 1GB)
		}
		foreach ($key in $WmiInfoNeeded.Keys) {
			$Json["diskDrives"][$i].add($key,$($WmiInfoNeeded[$key]))
		}
		$i++
	}
	$i = 0
	Get-PhysicalDisk | ForEach-Object{
		$disk = $_
		$PhyInfoNeeded = 
		@{
			model = $disk.Model
			healthState = $(if ($disk.HealthStatus -eq "Healthy"){"OK"}else{"NG"})
			interfaceType = $disk.BusType
			mediaType = $disk.MediaType
			name = $disk.FriendlyName
			uuid = $disk.UniqueId
		}
		$firm = Get-PhysicalDisk | Get-StorageFirmwareInformation
		$FirmInfoNeeded = 
		@{
			type = "Firmware"
			version = $disk.FirmwareVersion
			#status = $firm.AsJob
		}
		foreach ($key in $PhyInfoNeeded.Keys) {
			$Json["diskDrives"][$i].add($key,$($PhyInfoNeeded[$key]))
		}
		$Json["diskDrives"][$i].add("firmware", @(@{}))
		foreach ($key in $FirmInfoNeeded.Keys) {
			$Json["diskDrives"][$i]["firmware"][0].add($key,$($FirmInfoNeeded[$key]))
		}

		
		$i++
	}

}

#converts hashtable into Json format 
function hashToJson
{
	Param
	(
		[hashtable[]]$hash
	)
	$jasonHash = $hash | ConvertTo-Json -Depth 4
	Set-Content $jasonHash -Path ".\diskInfo.json"
}

function main
{
	diskHashBuild
	fillThatHashUp
	hashToJson $Json
}

main











# -----------------------tests--------------------------
# $testJsonObject = @{
# asd = "safa"
# asds = @("sdsdg", "dfsdf,")
# asfaf = @{
# asaf = "dfsdf"
# }
# }

# $testJasonObject | ConvertTo-Json | Set-Content -Path "C:\Users\avalov\OneDrive - Lenovo\Desktop\test.json"

# $MyJson = $testJsonObject | ConvertTo-Json

# $err = $null 
# $JsonObj = [Microsoft.PowerShell.Commands.JsonObject]::ConvertFromJson($MyJson, [ref]$err)
# Write-Output $JsonObj $MyJson
# Set-Content $JsonObj -Path "C:\Users\avalov\OneDrive - Lenovo\Desktop\test.json"
# Add-Content $MyJson -Path "C:\Users\avalov\OneDrive - Lenovo\Desktop\test.json"

# $partitions = "ASSOCIATORS OF " + "{Win32_DiskDrive.DeviceID='$($disk.DeviceID)'} " + "WHERE AssocClass = Win32_DiskDriveToDiskPartition"
		# Get_WmiObject -Query $partitions | ForEach-Object
		# {
			# $partition = $_
			# $drives = "ASSOCIATORS OF " + "{Win32_DiskPartition.DeviceID='$($partition.DeviceID)'} " + "WHERE AssocClass = Win32_LogicalDiskToPartition"
			# Get-WmiObject -Query $drives | ForEach-Object
			# {
				
			# }
        # }
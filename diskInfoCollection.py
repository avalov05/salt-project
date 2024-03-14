#!/home/uedm/.local/lib/python3.11
import platform
import subprocess, sys
import yaml
import json
import os

#--------------------------------------------------



infoNeeded = {
    "windows": 
    {
        "diskDrives": [],
        "memoryModules": [],
        "processors": []
    },                                   #OUTLINES WHAT INFO IS NEEDED
    "linux": {
        "diskDrives": [],
        "memoryModules": [],
        "processors": []
    }
}




#--------------------------------------------------

#this will write the windows script into a text file in order to collect the system information in proper format 
def windowsScript(scriptName):

    script = """
    Set-Content -Value "#DiskDrive:" -Path ".\diskInfo.txt"                                                #----------disk----------

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
			Add-Content -Value "d$i$key`:$($WmiInfoNeeded[$key] | ConvertTo-Json)" -Path ".\diskInfo.txt" 
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
		}
		foreach ($key in $PhyInfoNeeded.Keys) {
			Add-Content -Value "d$i$key`:$($PhyInfoNeeded[$key] | ConvertTo-Json)" -Path ".\diskInfo.txt" 
		}
		foreach ($key in $FirmInfoNeeded.Keys) {
			Add-Content -Value "df$i$key`:$($FirmInfoNeeded[$key] | ConvertTo-Json)" -Path ".\diskInfo.txt" 
		}
		$i++
	}
    
    Add-Content -Value "#Memory:" -Path ".\diskInfo.txt"                                               #----------memory----------
    
    $i = 0
 	Get-WmiObject Win32_PhysicalMemory | ForEach-Object { 
		$memory = $_
		$WmiInfoNeeded = 
		@{
			manufacturer = $memory.Manufacturer
			model = $memory.Model
			speed = $memory.Speed
			capacity = '{0:N2} GB' -f ($memory.Capacity / 1GB)
            serialNumber = $memory.SerialNumber
            displayName = $memory.Tag
            slot = $memory.BankLabel
            partNumber = $memory.PartNumber
            healthState = $memory.Status
		}
		foreach ($key in $WmiInfoNeeded.Keys) {
			Add-Content -Value "m$i$key`:$($WmiInfoNeeded[$key] | ConvertTo-Json)" -Path ".\diskInfo.txt" 
		}
        $i++
	}
    
    Add-Content -Value "#Processors:" -Path ".\diskInfo.txt"                                          #----------processors----------
    
    $i = 0
 	Get-WmiObject -Class Win32_Processor -ComputerName. | Select-Object -Property [a-z]* | ForEach-Object { 
		$cpu = $_
		$WmiInfoNeeded = 
		@{
			speed = $cpu.MaxClockSpeed
            manufacturer = $cpu.Manufacturer
            family = $cpu.Family
            displayName = $cpu.Name
            cores = $cpu.NumbeOfCores
            serialNumber = $cpu.SerialNumber
            partNumber = $cpu.PartNumber
            healthState = $cpu.Status
		}
		foreach ($key in $WmiInfoNeeded.Keys) {
			Add-Content -Value "p$i$key`:$($WmiInfoNeeded[$key] | ConvertTo-Json)" -Path ".\diskInfo.txt" 
		}
        $i++
	}
    """
    
    with open(scriptName, "w") as file:
        file.write(script)                                   #//CHANGE TO HAVING A KEY IN FRONT OF IT WHICH MIGHT MAKE THE PREVIOUS COMMENT UNIMPORTANT(resolved)
        file.close()
    return "./" + scriptName                                 #//When retrieving an empty info, set as N/A

def linuxScript(scriptName):

    script = """#!/bin/bash

echo "#DiskDrives:" > diskInfo.txt

dlist=()
while read -r line 
do
	dlist+=("$(echo "$line" | sed 's/ .*//')")
done <<< "$(lsblk | grep 'disk')"/
declare -A dInfoNeeded=( 
	["serialNumber:"]="Serial number:" 
	["model:"]="Product:" 
	["manufacturer:"]="Vendor:" 
	["capacity:"]="User Capacity:")
j=0
for disk in "${dlist[@]}"
do
	
	for key in "${!dInfoNeeded[@]}"; do
		i=0
		while read -r line
		do
			if [ "$key" == "capacity:" ] ; then 
				echo "d$i$key\"$(echo "$line" | sed -E 's/.*\[([^]]+)\].*/\1/')\"" >> diskInfo.txt
			else
				echo "d$i$key\"${line##*  }\"" >> diskInfo.txt 
			fi
			let "i++"
		done <<< "$(sudo smartctl -i /dev/${disk} | grep "${dInfoNeeded[$key]}")"
	done
	let "j++"
done



echo "#Memory:" >> diskInfo.txt

declare -A mInfoNeeded=( 
	["serialNumber:"]="Serial Number:" 
	["capacity:"]="Size:" 
	["manufacturer:"]="Manufacturer:" 
	["partNumber:"]="Part Number:" 
	["slot:"]="Bank Locator:" 
	["model:"]="Type:" 
	["speed:"]="Speed:")

i=0
mlist=()
while read -r line 
do
	if [ "${line##* }" != "Specified" ]; then
		mlist+=("YES")
	else
		mlist+=("NO")
	fi
	let "i++"
done <<< "$(dmidecode --type 17 | grep 'Serial Number:')"
for key in "${!mInfoNeeded[@]}"; do
	i=0
	j=0
	while read -r line
	do
		if [ "${mlist[$j]}" == "YES" ] ; then
			if [ "$(echo "$line" | sed 's/:.*//')" != "Configured Memory Speed" ] ; then
				echo "m$i$key\"${line##*: }\"" >> diskInfo.txt 
				let "i++"
			fi
		fi
		if [ "$(echo "$line" | sed 's/:.*//')" != "Configured Memory Speed" ] ; then
			let "j++"
		fi	
	done <<< "$(dmidecode --type 17 | grep "${mInfoNeeded[$key]}")"
done



echo "#Processor:" >> diskInfo.txt

declare -A pInfoNeeded=( 
	["speed:"]="Current Speed:" 
	["family:"]="Family:" 
	["manufacturer:"]="Manufacturer:" 
	["displayName:"]="Version:" 
	["socket:"]="Socket Designation:" 
	["productVerison:"]="Version:" 
	["cores:"]="Core Count:"
	["maxSpeedMHZ:"]="Max Speed:"
	["serialNumber:"]="Serial Number:"
	["partNumber:"]="Part Number:")

i=0
plist=()
while read -r line 
do
	if [ "$line" != "Voltage: 0.0 V" ]; then
		plist+=("YES")
	else
		plist+=("NO")
	fi
	let "i++"
done <<< "$(dmidecode -t processor | grep 'Voltage:')"
for key in "${!pInfoNeeded[@]}"; do
	i=0
	j=0
	while read -r line
	do
		if [ "${plist[$j]}" == "YES" ] ; then
			echo "p$i$key\"${line##*: }\"" >> diskInfo.txt 
			let "i++"
		fi
		let "j++"
	done <<< "$(dmidecode --t processor | grep "${pInfoNeeded[$key]}")"
done
"""
    with open(scriptName, "w") as file:
        file.write(script)                                   #//CHANGE TO HAVING A KEY IN FRONT OF IT WHICH MIGHT MAKE THE PREVIOUS COMMENT UNIMPORTANT(resolved)
        file.close()
    return "./" + scriptName    


#converts an array to yaml format
def arrToYam(arr):
    out = yaml.dump(arr, explicit_start = True, default_flow_style = False)
    return out

#will format the information file into a infoNeeded array 
def fileDataExtraction(input, platform):
    global dnum, dfnum, mnum, pnum
    file = open(input, "r")
    for line in file:
        if (line[:1] != "#"):
            
            if (line[:2] == "df"):
                findKV(line)
                arrayWrite(4, platform, "diskDrives", "firmware", key, value, num)
            
            elif (line[:1] == "d"):
                findKV(line)
                arrayWrite(3, platform, "diskDrives", "N/A", key, value, num)
                
            elif (line[:1] == "m"):
                findKV(line)
                arrayWrite(3, platform, "memoryModules", "N/A", key, value, num)
                
            elif (line[:1] == "p"):
                findKV(line)
                arrayWrite(3, platform, "processors", "N/A", key, value, num)
    file.close()
    
#finds the number of each piece of hardware
def numberOfHardware(input):
    global dnum, dfnum, mnum, pnum
    file = open(input, "r")
    for line in file:
        if (line[:1] != "#"):
            if (line[:1] == "d"):
                findKV(line)
                dnum = num
            if (line[:2] == "df"):
                findKV(line)
                dfnum = num
            if (line[:1] == "m"):
                findKV(line)
                mnum = num
            if (line[:1] == "p"):
                findKV(line)
                pnum = num
    file.close()
    
#simple usefull utilities

#gets the type of os
def OS():
    return os.name()

#gets key and value from a string
def findKV(line):
    
    global key, value, num
    i = 1
    for ch in line:
        if ch.isdigit():
            ind1 = i
            num = int(ch)
        if ch == ":":
            ind2 = i-1
            break
        i+=1
    key = line[ind1:ind2]
    value = line[ind2+2:len(line)-2]

#puts key value pair into a dictionary
def arrayWrite(depth, platform, type, type2, key, value, num):
    if (depth == 3):
        infoNeeded[platform][type][num][key] = value
    elif (depth == 4):
        infoNeeded[platform][type][num][type2][key] = value


#runs the ps1 script that was written by this script which puts system information into a file
def runScript(script, platform):
    if (platform == "windows"):
        subprocess.call(["powershell",script], shell = True, stderr = subprocess.STDOUT)
    elif (platform == "linux"):
        subprocess.call(["/bin/bash",script], shell=True, stderr=subprocess.STDOUT)
    
#creates a blank data structure for later data storage
def arrayAssembly(platform):
    for i in range(dnum + 1):
        infoNeeded[platform]["diskDrives"].append({})
    for i in range(dfnum + 1):
        infoNeeded[platform]["diskDrives"][dnum]["firmware"] = {}
    for i in range(mnum + 1):
        infoNeeded[platform]["memoryModules"].append({})
    for i in range(pnum + 1):
        infoNeeded[platform]["processors"].append({})

def arrToFile(arr):
    file = open("grains.txt", "w")
    file.write(arrToYam(arr))
    
def cleanup(fileName):
    
    print("cleaning up...")
    os.remove(fileName)
    #os.remove("diskInfo.txt")
    
#linux system disk information collection 
class linuxC:

    #collects disk information
    def getInfo(self):
        global diskCount
        platform = "linux"
        scriptName = "tmp.sh"
        
        print(r"""
         _     _                  
        | |   (_)                 
        | |    _ _ __  _   ___  __
        | |   | | '_ \| | | \ \/ /
        | |___| | | | | |_| |>  < 
        \_____/_|_| |_|\__,_/_/\_\
                            
                            
        """)
        print("collecting system info...")
        runScript(linuxScript(scriptName), platform)
        print("done!")
        print("packing into a file...")
        numberOfHardware("diskInfo.txt")
        arrayAssembly(platform)
        fileDataExtraction("diskInfo.txt", platform)
        arrToFile(infoNeeded[platform])
        print("done!")
        cleanup(scriptName)    
        
#windows system information collection
class windowsC:
    
    #collects disk information
    def getInfo(self):
        global diskCount
        platform = "windows"
        scriptName = "tmp.ps1"
        
        print(r"""
         _    _ _           _                   
        | |  | (_)         | |                  
        | |  | |_ _ __   __| | _____      _____ 
        | |/\| | | '_ \ / _` |/ _ \ \ /\ / / __|
        \  /\  / | | | | (_| | (_) \ V  V /\__ \
         \/  \/|_|_| |_|\__,_|\___/ \_/\_/ |___/
                                            
                                            
        """)
        print("collecting system info...")
        runScript(windowsScript(scriptName), platform)
        print("done!")
        print("packing into a file...")
        numberOfHardware("diskInfo.txt")
        arrayAssembly(platform)
        fileDataExtraction("diskInfo.txt", platform)
        arrToFile(infoNeeded[platform])
        print("done!")
        cleanup(scriptName)
        
def main():

    
    if (os.name == "posix"):
        linux = linuxC()
        linux.getInfo()
    elif (os.name == "nt"):
        windows = windowsC()
        windows.getInfo()
    else:
        print("system not supported...\naborting...")
        
main()
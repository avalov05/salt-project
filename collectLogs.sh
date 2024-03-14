#!/bin/bash 

#constants
PathToLogFiles=(
	'/var/log/Lenovo_Support'
	'/var/log/salt'
)

#archives logs
packUp(){
	if [ ! -d /var/log/temp ]; then
		#echo "creating temp..."
		sudo mkdir /var/log/temp
	fi
	cd /var/log/temp 
	for file in "${PathToLogFiles[@]}"; do
		cp -a $file ./
	done
	tar czf logs.tar.gz *
	if [ $? -eq 0 ]; then
		echo "Success!"
	else
		echo "Fail"
		exit 1
	fi
	cp logs.tar.gz /var/log/Lenovo_Support
	sudo rm -rf /var/log/temp
	#echo "deleting temp..."
}

main()
{
	if [ -f "var/log/Lenovo_Support/logs.tar.gz" ]; then
		echo "cleaning up..."
		sudo rm var/log/Lenovo_Support/logs.tar.gz
	fi
	echo "archiving..."
	packUp
}

main
# BlueCat Datarake Analyzer

## Purpose

This goal of this program is to be an all in one tool for extracting, analyzing, and evaluating datarake files.
The goal is to cut down on time and tedious tasks related to datarake file analysis.



## Installation

#### Option 1 (.exe)
Download the wizard_main.exe file and run it


#### Option 2 (python)

0 - Install python 3 and pip (if you don't have it already)
On windows: https://www.python.org/downloads/windows/

1 - Download the .zip at https://gitlab.bluecatlabs.net/kwirt/datarake-wizard/-/archive/main/datarake-wizard-main.zip file or clone it if you have GIT installed:
```
git clone https://gitlab.bluecatlabs.net/kwirt/datarake-wizard
```
2 - Go to the project folder and install the pre-requisites:

3 - Install package requirements
```
pip install -r requirements.txt 
```

4 - Run the script

cd to the folder and run the script
```
python wizard_main.py 
```

## Usage Options
### Default
<strong>All options: </strong> (All optional options except full extract) <br>
<strong>Decompress .gz files: </strong>(decompresses the leftover .gz files after extraction) <br>
<strong>AO: </strong>Auto open output folder after jobs are completed

### Optional
<strong>Full Extract: </strong>(extract all datarake files, ignores options)  <br> 
<strong>Datarake logs: </strong>(extract /tmp/datarake directory)   <br>
<strong>Var logs: </strong>(extracts the full /var/log director) <br>
<strong>Server log: </strong>(extract commandServer.log files from /var/log) <br>
<strong>Syslog: </strong> (extract syslog files from /var/log)  <br>
<strong>DHCP: </strong>(extract DHCP related files such as dhcpd.leases) <strong>Syslog: </strong> (extract syslog files from /var/log)  <br>
<strong>DNS : </strong>(extract files in \replicated\jail\named\etc) <strong>Syslog: </strong> (extract syslog files from /var/log)  <br>

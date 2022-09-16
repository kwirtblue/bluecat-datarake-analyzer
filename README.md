# BlueCat Datarake Wizard

## Update Notes
#### v1.0.2
- Window now remembers last position when you re-open it
- Added SFTP Tab
- Moved tabs to their own file tabs.py


#### v1.0.1
- Added API extraction option for BAM files
- Added detection for BAM vs BDDS datarake files, window changes to DNS/DHCP or API options depending on which file is detected
- Cleaned up extraction code into a function
- Cleaned up logger logic and added event for errors found
#### v1.0.0 
- First version of the program.
- Program is able to extract datarake files with the option to decompress .gz files after completing.
- When running the program, all options and decompress .gz files are selected by default. All options should cover all the commonly used files and folders.
- If you don't want to use all options, you can select the specific folders you want to extract.
- I added a full extract option that will extract all files with no filter.        


## Purpose

This goal of this program is to be an all in one tool for extracting, analyzing, and evaluating datarake files.
The goal is to cut down on time and tedious tasks related to datarake file analysis.

<ins>Currently a GUI program for Windows only. I plan to add command line in the future.</ins>

## Installation

#### Option 1 (.exe)
<a href="https://gitlab.bluecatlabs.net/kwirt/datarake-wizard/-/raw/main/wizard_main.exe?inline=false">Download the wizard_main.exe</a> file and run it

#### Option 2 (python)

0 - Install python 3 and pip (if you don't have it already)
On windows: https://www.python.org/downloads/windows/

1 - <a href="https://gitlab.bluecatlabs.net/kwirt/datarake-wizard/-/archive/main/datarake-wizard-main.zip">Download the .zip file</a> OR clone it if you have GIT installed:
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
<strong>DHCP: </strong>(extract DHCP related files such as dhcpd.leases)   <br>
<strong>DNS : </strong>(extract files in \replicated\jail\named\etc)  <br>

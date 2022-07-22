'''
Written By:

88      a8P
88    ,88'
88  ,88"
88,d88'       ,adPPYYba,  888888888
8888"88,      ""     `Y8       a8P"
88P   Y8b     ,adPPPPP88    ,d8P'
88     "88,   88,    ,88  ,d8"
88       Y8b  `"8bbdP"Y8  888888888
Kyle Wirt
'''
import PySimpleGUI as sg
import tarfile, os, re, sys, gzip, shutil
from threading import Thread
from tkinter import ttk
import netmiko as nm
import tabs

version = '1.0.2'

sg.theme('DarkTeal12')
sg.UserSettings(filename='wizard_main.py')
sys.path.insert(0, '/images')

#Function to extract files depending on which options are selected
def extract_tar(output_path, dfile, options, fname):
    # re searches
    allfile_search = re.compile('/boot|/etc|/home|/replicated|/root|/tmp|/usr|/var')
    syslog_search = re.compile('/var/log/syslog')
    serverlog_search = re.compile('\/var\/log\/.*Server\.log', re.IGNORECASE)
    dlog_search = re.compile('/tmp/datarake')
    dns_search = re.compile("replicated/jail/named/etc/(?!active)")
    dhcp_search = re.compile('/replicated/etc|/replicated/var/state/dhcp')
    varlog_search = re.compile('/var/log')
    api_search = re.compile('/opt/server/proteus')
    all_searches = [dlog_search, dns_search, dhcp_search, varlog_search, api_search]
   #function to extract each file in members
    def extract_members(members):
        print('Extracting ' + str(len(members)) + ' files...')
        error_list = []
        for member in members:
            try:
                datarake.extract(member, path=output_path, numeric_owner=True)
            except Exception as e:
                error_list.append(e.__str__())
        if len(error_list) > 0:
            window.write_event_value('-EXTRACTION_ERRORS_FOUND-', 'Extraction errors occurred!')
            try:
                with open(os.path.join(output_path, fname, "extractor_errorlog.txt"), mode='w') as log_file:
                    log_file.write('\n'.join(error_list))
            except Exception as e:
                print(e)
        print('Extraction complete!')
    # create list of files to extract
    members = []
    failed = False
    try:
        print('Opening file...')
        with tarfile.open(dfile, mode='r:gz') as datarake:
            if 'full_extract' in options:
                members = datarake.getmembers()
                extract_members(members)
            elif 'all_options' in options:
                for compressed_file in datarake.getmembers():
                    for search in all_searches:
                        if search.search(compressed_file.name):
                            members.append(compressed_file)
                            print(compressed_file.name + " has been added to extract list...")
                extract_members(members)
            else:
                for compressed_file in datarake.getmembers():
                    if 'syslog' in options:
                        if syslog_search.search(compressed_file.name):
                            members.append(compressed_file)
                            print(compressed_file.name + " has been added to extract list...")
                    if 'serverlog' in options:
                        if serverlog_search.search(compressed_file.name):
                            members.append(compressed_file)
                            print(compressed_file.name + " has been added to extract list...")
                    if 'dlog' in options:
                        if dlog_search.search(compressed_file.name):
                            members.append(compressed_file)
                            print(compressed_file.name + " has been added to extract list...")
                    if 'DNS' in options:
                        if dns_search.search(compressed_file.name):
                            members.append(compressed_file)
                            print(compressed_file.name + " has been added to extract list...")
                    if 'DHCP' in options:
                        if dhcp_search.search(compressed_file.name):
                            members.append(compressed_file)
                            print(compressed_file.name + " has been added to extract list...")
                    if 'varlog' in options:
                        if varlog_search.search(compressed_file.name):
                            members.append(compressed_file)
                            print(compressed_file.name + " has been added to extract list...")
                    if 'apilog' in options:
                        if api_search.search(compressed_file.name):
                            members.append(compressed_file)
                            print(compressed_file.name + " has been added to extract list...")
                extract_members(members)
    except Exception as e:
        print('Extraction failed: ' + str(e))
        failed=True
    #decompress .gz files after extraction if option is selected
    if 'decompress' in options and failed == False:
        dir = os.path.join(output_path + '/' + fname + '/var/log/')
        #check if var/log directory exists
        try:
            dir_files = os.listdir(dir)
        except WindowsError:
            pass
            #print("Error: Cannot decompress files, /var/log directory doesn't exist!")
        except Exception as e:
            print(e)
        if 'dir_files' in locals():
            # create list of files remaining with .gz extension
            gz_list = []
            for log in dir_files:
                if log.endswith('.gz'):
                    gz_list.append(log)
            #open each file, decompress and save, then delete the .gz file
            for gz_file in gz_list:
                try:
                    with gzip.open(os.path.join(dir, gz_file), mode='rb') as f_in:
                        print('Decompressing: ' + str(gz_file))
                        with open(os.path.join(dir, gz_file.split('.gz')[0]), mode='wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    os.remove(os.path.join(dir, gz_file))
                except Exception as e:
                    print(e)
            print('File decompression completed!')
    if failed == False:
        window.write_event_value('-EXTRACT_SUCCESS-', 'Extraction process has finished successfully!')
    else:
        window.write_event_value('-EXTRACT_FAILED-', 'Extraction process has failed!')

# Define the window's contents
#Create tab layouts
#sftp_server = 'bluecatsftp.bluecatnetworks.com'
sftp_server = '127.0.0.1'

#sg.Tab('Analyzer',analyzer_tab, key='analyzer')

#create layout
layout= [
    [sg.TabGroup([[sg.Tab('SFTP', tabs.sftp_tab, key='-SFTP_TAB-'),sg.Tab('Extractor', tabs.extractor_tab, key='Extractor')]],key='-TABS-', expand_x=True, expand_y=True)]
]

# Create the window
window = sg.Window('BlueCat Log Extractor',
                   layout,
                   icon='images/cat_icon.ico',
                   finalize=True,
                   resizable=True,
                   use_default_focus=False,
                   enable_close_attempted_event=True,
                   location=sg.user_settings_get_entry('-location-',default=(None,None))
                   )

#Remove the dotted focus border that appears when you click on tabs
s = ttk.Style()
layout = s.layout('Tab')
s.layout("Tab",
    [('Notebook.tab',
      {'children':
        [('Notebook.padding',
          {'children':
            [('Notebook.label',
              {'side':'top','sticky': '',})],
          'sticky': 'nswe',})],
      'sticky': 'nswe',})])

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event in (sg.WINDOW_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT):
        # The line of code to save the position before exiting
        sg.user_settings_set_entry('-location-', window.current_location())
        break

    ###START OF SFTP TAB EVENTS
    if event == '-sftp_login-':
        if values['-sftp_username-'] and values['-sftp_password-']:
            if len(values['-sftp_username-']) > 0 and len(values['-sftp_password-']) >0:
                bcat_sftp_server = {
                    "device_type": "linux",
                    "host": sftp_server,
                    "username": values['-sftp_username-'],
                    "password": values['-sftp_password-'],
                }
                try:
                    with nm.ConnectHandler(**bcat_sftp_server) as server:
                        if server.find_prompt()[-1] == '$':
                            window['-sftp_login_frame-'].update(visible=False)
                            window['-sftp_browser_frame-'].update(visible=True)
                except Exception as e:
                    pos_x,pos_y = window.current_location()
                    sg.PopupScrolled(e, location=(pos_x,pos_y), size=(32,12))

    ###END OF SFTP TAB EVENTS
    ####START OF EXTRACTOR TAB EVENTS
    if event == '-DATARAKE_FILE-':
        adonis_check = re.compile('ADONIS')
        proteus_check = re.compile('PROTEUS')
        if proteus_check.search(values['-DATARAKE_FILE-']):
            window['-BAM_FRAME-'].update(visible=True)
            window['-BDDS_FRAME-'].update(visible=False)
            window['-DHCP-'].update(value=False)
            window['-DNS-'].update(value=False)
            print('BAM datarake detected')

        elif adonis_check.search(values['-DATARAKE_FILE-']):
            window['-BDDS_FRAME-'].update(visible=True)
            window['-BAM_FRAME-'].update(visible=False)
            window['-api_log-'].update(value=False)
            print('BDDS datarake detected')

    if event == '-FULL_EXTRACT-':
        if values['-FULL_EXTRACT-'] == True:
            window['-all_options-'].update(disabled=True)
            window['-dlog-'].update(disabled=True)
            window['-serverlog-'].update(disabled=True)
            window['-syslog-'].update(disabled=True)
            window['-DNS-'].update(disabled=True)
            window['-DHCP-'].update(disabled=True)
            window['-varlog-'].update(disabled=True)
            window['-api_log-'].update(disabled=True)
        else:
            window['-all_options-'].update(disabled=False)
            if values['-all_options-'] == False:
                window['-dlog-'].update(disabled=False)
                window['-syslog-'].update(disabled=False)
                window['-serverlog-'].update(disabled=False)
                window['-DNS-'].update(disabled=False)
                window['-DHCP-'].update(disabled=False)
                window['-varlog-'].update(disabled=False)
                window['-api_log-'].update(disabled=False)

    if event == '-all_options-':
        if values['-all_options-'] == True:
            window['-dlog-'].update(disabled=True, value=False)
            window['-serverlog-'].update(disabled=True,value=False)
            window['-syslog-'].update(disabled=True, value=False)
            window['-DNS-'].update(disabled=True, value=False)
            window['-DHCP-'].update(disabled=True, value=False)
            window['-varlog-'].update(disabled=True, value=False)
            window['-api_log-'].update(disabled=True, value=False)
        else:
            window['-dlog-'].update(disabled=False)
            window['-syslog-'].update(disabled=False)
            window['-serverlog-'].update(disabled=False)
            window['-DNS-'].update(disabled=False)
            window['-DHCP-'].update(disabled=False)
            window['-varlog-'].update(disabled=False)
            window['-api_log-'].update(disabled=False)

    #Handle event when extract logs button is clicked
    if event == 'Extract Logs':
        #disable the extract logs button
        window['Extract Logs'].update(disabled=True)
        #create list of the selected options
        options = []
        if values['-FULL_EXTRACT-']:
            options.append('full_extract')
        elif values['-all_options-']:
            options.append('all_options')
        else:
            if values['-syslog-'] is True:
                options.append('syslog')
            if values['-serverlog-'] is True:
                options.append('serverlog')
            if values['-dlog-'] is True:
                options.append('dlog')
            if values['-auto_open-'] is True:
                options.append('auto_open')
            if values['-varlog-'] is True:
                options.append('varlog')
            if values['-DNS-'] is True:
                options.append('DNS')
            if values['-DHCP-'] is True:
                options.append('DHCP')
            if values['-api_log-'] is True:
                options.append('apilog')
        if values['-decompress-']:
            options.append('decompress')
        #check that at least one main option is selected
        main_options = ['full_extract','all_options','syslog', 'serverlog', 'dlog', 'DNS', 'DHCP', 'varlog','apilog']
        option_count = 0
        for option in options:
            if option in main_options:
                option_count += 1
        if option_count > 0:
            #file location and output directory
            dfile = values['-DATARAKE_FILE-']
            output_path = values['-OUTPUT_FOLDER-']
            fname = values['-DATARAKE_FILE-'].split('/')[-1].split('.tgz')[0]
            #create thread to run the extraction using the extract_tar() function
            try:
                thread = Thread(target=extract_tar, args=(output_path, dfile, options, fname)).start()
            except Exception as e:
                print(e)
        else:
            window['Extract Logs'].update(disabled=False)
            print('Please select at least one extraction option!')
    #re-enable the extraction button after extraction fails or succeeds
    if event == '-EXTRACT_SUCCESS-':
        window['Extract Logs'].update(disabled=False)
        print('Files have been extracted to: "' + str(output_path + fname))
        #auto open browser to the output if option is checked
        if values['-auto_open-'] == True:
            os.startfile(output_path)
    if event == '-EXTRACT_FAILED-':
        window['Extract Logs'].update(disabled=False)
    if event == '-EXTRACTION_ERRORS_FOUND-':
        print('Errors found, logfile has been placed in the output folder')
    ###END OF EXTRACTOR TAB EVENTS


# Finish up by removing from the screen
window.close()
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

version = '1.0.1'

sg.theme('DarkTeal12')
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
extractor_tab = [
    [sg.Frame('Log Extractor',size=(900,260), layout=
        [
            [sg.Text('Select datarake file: '),sg.Input(key='-DATARAKE_FILE-', expand_x=True, enable_events=True), sg.FileBrowse(target='-DATARAKE_FILE-', file_types=(('Datarake Files', '*.tgz'),('All File Types', '*')))],
            [sg.Text('Output Folder: '), sg.Checkbox('AO?',tooltip='Auto open output folder upon finishing extraction', key='-auto_open-', default=True), sg.Input(key='-OUTPUT_FOLDER-', expand_x=True, enable_events=True), sg.FolderBrowse(target='-OUTPUT_FOLDER-')],
            #logs frame
            [sg.Push(),sg.Frame('Logs', layout=[
                [sg.Checkbox('Datarake Logs', key='-dlog-', enable_events=True, disabled=True),
                 sg.Checkbox('Var Logs', key='-varlog-', enable_events=True, disabled=True),
                 sg.Checkbox('Server Log', key='-serverlog-', disabled=True, enable_events=True),
                 sg.Checkbox('Syslog', key='-syslog-', enable_events=True, disabled=True)]])],
            #service frame
            [sg.Push(),
             sg.Frame('BAM Service Files', layout=[
                [sg.Checkbox('API Logs', key='-api_log-', enable_events=True, disabled=True, default=False)]], key='-BAM_FRAME-', visible=False),
             sg.Frame('BDDS Service Files', layout=[
                [sg.Checkbox('DHCP', key='-DHCP-', enable_events=True, disabled=True, default=False),
                 sg.Checkbox('DNS', key='-DNS-', enable_events=True, disabled=True, default=False)]], key='-BDDS_FRAME-', visible=False)
             ],
            [sg.Push(),sg.Checkbox('Decompress .gz files?', key='-decompress-',enable_events=True, default=True),sg.Checkbox('All Options', key='-all_options-', enable_events=True, default=True)],
            [sg.Push(),sg.Checkbox('Full Extract (ignores options)',key='-FULL_EXTRACT-', enable_events=True),sg.Button('Extract Logs')]
        ])
    ],
    [sg.Frame('Output',size=(900, 300), layout=
        [
            [sg.Multiline(key='-OUTPUT-',size=(90,10),disabled=True, auto_refresh=True,expand_x=True, expand_y=True, reroute_stdout=True, write_only=True, autoscroll=True)] #,reroute_stderr=True
        ])
    ]
]
analyzer_tab = [
    [sg.Frame('Log Analyzer', size=(662,300), layout=
    [
    ]
    )]
]


#sg.Tab('Analyzer',analyzer_tab, key='analyzer')

#create layout
layout= [
    [sg.TabGroup([[sg.Tab('Extractor', extractor_tab, key='Extractor'),]],key='-TABS-', expand_x=True, expand_y=True)]
]

# Create the window
window = sg.Window('BlueCat Log Extractor', layout, icon='images/cat_icon.ico', finalize=True, resizable=True, use_default_focus=False)

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
    if event == sg.WINDOW_CLOSED or event == 'Quit':
        break
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
            if values['-syslog-'] == True:
                options.append('syslog')
            if values['-serverlog-'] == True:
                options.append('serverlog')
            if values['-dlog-'] == True:
                options.append('dlog')
            if values['-auto_open-'] == True:
                options.append('auto_open')
            if values['-varlog-'] == True:
                options.append('varlog')
            if values['-DNS-'] == True:
                options.append('DNS')
            if values['-DHCP-'] == True:
                options.append('DHCP')
            if values['-api_log-'] == True:
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
# Finish up by removing from the screen
window.close()
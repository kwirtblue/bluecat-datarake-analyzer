import re, os, tarfile,gzip, shutil
from wizard_main import sg

# file checks
adonis_check = re.compile('ADONIS')
proteus_check = re.compile('PROTEUS')

def extract_tar(output_path, dfile, options, fname, window):
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
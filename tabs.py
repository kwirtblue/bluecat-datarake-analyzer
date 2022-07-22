import PySimpleGUI as sg

sg.theme('DarkTeal12')
sftp_server = '127.0.0.1'
sftp_tab = [
    [sg.Frame('', layout=[
        [sg.VPush()],
        [sg.Push(),sg.Text('SFTP Server: ', pad=((0,0),(0,5)), font='bold'),sg.Text(sftp_server),sg.Push()],
        [sg.Push(),sg.Text('Username: ', pad=((10,0),(0,0)), font='bold'),sg.InputText(key='-sftp_username-',size=25),sg.Push()],
        [sg.Push(),sg.Text('Password: ', pad=((10,0),(0,0)), font='bold'), sg.InputText(key='-sftp_password-',password_char="*", size=25),sg.Push()],
        [sg.Push(),sg.OK(button_text='Log in',key='-sftp_login-' ,size=10, pad=((75,0),(10,0))),sg.Push()],
        [sg.VPush()]
    ],
        key='-sftp_login_frame-',
        expand_x=True,
        expand_y=True,
        pad=200,
        visible=False,
        element_justification='left')],
    [sg.Frame('', layout=[
        [sg.Push(),sg.OK('End Session')],
        [sg.VPush()],
        [sg.Button('Back')],
        [sg.Multiline(size=(80,20)),sg.Multiline(size=(20,20))]
    ],
        expand_x=True,
        expand_y=True,
        size=(900,570),
        key='-sftp_browser_frame-',
        visible=True),
    ]
]

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
    [sg.Frame('Log Analyzer', size=(662,300), layout=[
    ]
    )]
]
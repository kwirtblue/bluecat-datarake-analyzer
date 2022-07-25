import PySimpleGUI as sg
import stat
from time import strftime
from datetime import datetime

sg.theme('DarkTeal12')

def render_table(window,convert_time, file_list = []):
    sftp_file_list = []
    for file_data in file_list:
        filename = file_data.filename
        modified_datetime = datetime.fromtimestamp(file_data.st_mtime)
        m_converted_time = modified_datetime.strftime("%I:%M %p")
        modified_split = str(modified_datetime).split()
        if convert_time == True:
            last_modified = f'{modified_split[0]} at {m_converted_time}'
        elif convert_time == False:
            last_modified = f'{modified_split[0]} at {modified_split[1]}'
        permissions = stat.filemode(file_data.st_mode)
        file_size = file_data.st_size
        sftp_file_list.append([filename,last_modified,permissions,file_size])
    table_output = []
    for file in sftp_file_list:
        table_output.append(str(file).split())
    window['-sftp_browser-'].update(values=sftp_file_list)
    return sftp_file_list


sftp_server = '127.0.0.1'
sftp_tab = [
    [sg.pin(sg.Frame('', layout=[
        [sg.VPush()],
        [sg.Push(),sg.Text('SFTP Server: ', pad=((0,0),(0,5)), font='bold'),sg.Text(sftp_server),sg.Push()],
        [sg.Push(),sg.Text('Username: ', pad=((10,0),(0,0)), font='bold'),sg.InputText(default_text='kyle', key='-sftp_username-',size=25, focus=True),sg.Push()],
        [sg.Push(),sg.Text('Password: ', pad=((10,0),(0,0)), font='bold'), sg.InputText(default_text='test', key='-sftp_password-',password_char="*", size=25),sg.Push()],
        [sg.Push(),sg.OK(button_text='Log in',key='-sftp_login-',bind_return_key=True ,size=10, pad=((75,0),(10,0))),sg.Push()],
        [sg.VPush()]
    ],
        key='-sftp_login_frame-',
        expand_x=True,
        expand_y=True,
        pad=200,
        visible=True,
        element_justification='left'))],
    [sg.pin(sg.Frame('', layout=[
        [sg.Checkbox('24h/12h', key='-convert_time-',enable_events=True),sg.Push(),sg.OK('End Session',key='-sftp_end_session-')],
        [sg.Button('Back', key='-sftp_back_button-')],
        [sg.InputText(key='-current_path_box-', size=(50,1),expand_x=True)],
        [sg.Table(values=[], headings=['Name','Last modified','Access','Size'],
                  key='-sftp_browser-',
                  col_widths=[15,16,8,6,6,6,6,6,6],
                  num_rows=15,
                  bind_return_key=True,
                  background_color='white',
                  text_color='black',
                  justification="left",
                  expand_x=True,
                  select_mode='browse',
                  auto_size_columns=False,
                  right_click_menu=['Test',['Name','Last modified','Access']])],
        [sg.Multiline(size=(30,20)),
         sg.Frame('',layout=[
            [sg.InputText(),sg.FolderBrowse()]
            ],
                  vertical_alignment='top',
                  border_width=0)
         ]],
            expand_x=True,
            expand_y=True,
            size=(900,570),
            key='-sftp_browser_frame-',
            visible=False,
            border_width=0
            ))],
]


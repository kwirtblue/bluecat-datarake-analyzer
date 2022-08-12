import PySimpleGUI as sg
import stat
import os
import paramiko as pm
from time import strftime
from datetime import datetime

sg.theme('DarkTeal12')

#LAYOUT STARTS HERE!!!!!
sftp_server = '192.168.1.154'
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
    [sg.pin(sg.Frame('', layout=
    [
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
                  expand_y=True,
                  select_mode='browse',
                  auto_size_columns=False)],
        [sg.Table(num_rows=13,
                  col_widths=[30],
                  select_mode='browse',
                  key='-download_list-',
                  headings=['Download List'],
                  background_color='white',
                  text_color='black',
                  justification='left',
                  bind_return_key=True,
                  expand_y=True,
                  expand_x=True,
                  auto_size_columns=False,
                  vertical_scroll_only=False,
                  values=[]),
        sg.Column(
            [
                [sg.Frame('Output',
                          border_width=0,
                          expand_x=True,
                          expand_y=True,
                          layout=[
                    [sg.Multiline(key='-sftp_output-',
                              expand_x=True,
                              expand_y=True,
                              size=(10,5),
                              disabled=True)
                    ]
                ])],
                [sg.Frame('Download Progress', layout=
                [
                    [sg.Text('',key='-bytes_downloaded-')],
                    [sg.Text('',key='-num_files-')],
                    [sg.VPush()],
                    [sg.ProgressBar(max_value=100,
                                    key='-download_progress-',
                                    orientation='horizontal',
                                    pad=(10,5),
                                    bar_color=('green','white'),
                                    expand_x=True,
                                    size=(45,15))
                    ],
                    [sg.Push(),sg.Text('',key='-download_percentage-', pad = 0),sg.Push()],
                ],
                          key = '-download_frame-',
                          visible = False,
                          expand_x=True,
                          expand_y=True)],
                [sg.Text('Output Folder'),sg.Input(key='-SFTP_OUTPUT_FOLDER-', enable_events=True, expand_x=True),sg.FolderBrowse()],
                [sg.Button('Download Only', key=('-sftp_download-','-download_only-')),
                 sg.Button('Download and Extract', key=('-sftp_download-','-download_extract-')),
                 sg.Button('Download and Analyze', key=('-sftp_download-','-download_analyze-'))]
            ],
            element_justification='right',
            expand_x=True,
            expand_y=True,
            pad=0,
        ),
        ]
    ],
                     expand_x=True,
                     expand_y=True,
                     key='-sftp_browser_frame-',
                     visible=False,
                     border_width=0
    ),
            expand_x=True,
            expand_y=True,
            )]
]

#REGULAR FUNCTIONS START HERE!!!!
def render_table(window,convert_time, file_list = []):
    rendered_table = []
    sftp_item_list = []
    class Item():
        def __init__(self):
            self.filename = file_data.filename
            self.modified_datetime = datetime.fromtimestamp(file_data.st_mtime)
            self.m_converted_time = self.modified_datetime.strftime("%I:%M %p")
            self.modified_split = str(self.modified_datetime).split()
            self.permissions = stat.filemode(file_data.st_mode)
            self.file_size = file_data.st_size
    for file_data in file_list:
        item = Item()
        if convert_time == True:
            item.last_modified = f'{item.modified_split[0]} at {item.m_converted_time}'
        elif convert_time == False:
            item.last_modified = f'{item.modified_split[0]} at {item.modified_split[1]}'
        rendered_table.append([item.filename,item.last_modified, item.permissions, item.file_size])
        sftp_item_list.append(item)
    window['-sftp_browser-'].update(values=rendered_table)
    return rendered_table, sftp_item_list


#EVENT FUNCTIONS START HERE!!!
def login(window, username, password, time):
    if username and password:
        if len(username) > 0 and len(password) > 0:
            bcat_sftp_server = pm.SSHClient()
            bcat_sftp_server.set_missing_host_key_policy(pm.AutoAddPolicy())
            # bcat_sftp_server.load_system_host_keys()
            try:
                bcat_sftp_server.connect(
                    sftp_server,
                    username=username,
                    password=password,
                    port=22
                )
                # create sftp object
                sftp_con = bcat_sftp_server.open_sftp()
                sftp_con.chdir(path='')
                current_file_list = sftp_con.listdir_attr()
                rendered_table, sftp_item_list = render_table(window, file_list=current_file_list,
                                                       convert_time=time)
                # remove login frame and show browser frame
                window['-sftp_login_frame-'].update(visible=False)
                window['-sftp_browser_frame-'].update(visible=True)
                window['-current_path_box-'].update(value='/')
                return sftp_con, bcat_sftp_server,current_file_list, rendered_table, sftp_item_list
            except Exception as e:
                pos_x, pos_y = window.current_location()
                sg.PopupScrolled(e, location=(pos_x, pos_y), size=(32, 12))
                return 'None','None','None','None','None'
def path_box(path, dir, old_dir, table, sftp_con, sftp_server, window, time):
    input_path = path
    # if input didn't start with /, add / at the start to make path correct
    if not str(input_path).startswith('/'):
        input_path = f'/{input_path}'
    # if input didn't end with /, add / at the end to make path correct
    if not str(input_path).endswith('/'):
        input_path = f'{input_path}/'
    try:
        sftp_con.chdir(input_path)
    except OSError as o:
        if o.args[0] == 'Socket is closed':
            sftp_server.close()
            sg.Popup('Connection error! Returning to login screen...', location=window.current_location())
            window['-sftp_browser_frame-'].update(visible=False)
            window['-sftp_login_frame-'].update(visible=True)
        else:
            sg.Popup('Invalid directory', location=window.current_location())
    except Exception as o:
        sg.Popup(o, location=window.current_location())
    else:
        current_file_list = sftp_con.listdir_attr()
        current_dir = input_path
        # update previous directory for the back button
        suffix = current_dir.split('/')[-2] + "/"
        previous_dir = current_dir.removesuffix(suffix)
        window['-current_path_box-'].update(value=current_dir)
        rendered_table, sftp_item_list = render_table(window, file_list=current_file_list,
                                               convert_time=time)
        return current_dir, previous_dir, rendered_table, sftp_item_list
    return dir, old_dir, table
def sftp_browser(row,
                 table,
                 dir,
                 old_dir,
                 sftp_con,
                 sftp_server,
                 window,
                 time,
                 item_list,
                 download_list,
                 download_item_list):
    selected_row = item_list[row]
    # check if selected row is a directory
    if selected_row.permissions[0] == 'd':
        dir_path = f'{dir}{table[row][0]}/'
        try:
            sftp_con.chdir(dir_path)
            current_file_list = sftp_con.listdir_attr()
        # catch exception if reading directory fails due to connection, return to login screen
        except OSError as o:
            if o.args[0] == 'Socket is closed':
                sftp_server.close()
                sg.Popup('Connection error! Returning to login screen...', location=window.current_location())
                window['-sftp_browser_frame-'].update(visible=False)
                window['-sftp_login_frame-'].update(visible=True)
            else:
                sg.Popup(o, location=window.current_location())
        except Exception as e:
            sg.Popup(e, location=window.current_location())
        else:
            previous_dir = dir
            rendered_table, sftp_item_list= render_table(window, file_list=current_file_list,
                                                   convert_time=time)
            window['-current_path_box-'].update(value=dir_path)
            return dir_path, previous_dir, rendered_table, sftp_item_list, download_item_list
    #check if it was a file that was double-clicked
    if selected_row.permissions[0] == '?':
        list=download_list
        new_download_item_list = download_item_list
        if len(download_list) == 0:
            list.append(selected_row.filename)
            window['-download_list-'].update(values=[list])
        elif len(download_list) > 0:
            list.append([selected_row.filename])
            window['-download_list-'].update(values=list)
        selected_row.path = f'{dir}{selected_row.filename}'
        new_download_item_list.append(selected_row)
        return dir, old_dir, table, item_list, new_download_item_list
    return dir, old_dir, table, item_list, download_item_list
def back_button(dir, old_dir, table, sftp_con, window, time, item_list):
    if dir != '/':
        # change directory to previous directory
        sftp_con.chdir(old_dir)
        # update current directory
        current_dir = old_dir
        # update the previous dir
        suffix = old_dir.split('/')[-2] + "/"
        previous_dir = old_dir.removesuffix(suffix)
        # update file list
        current_file_list = sftp_con.listdir_attr()
        # re-render the table
        rendered_table, sftp_item_list = render_table(window,
                                      file_list=current_file_list,
                                      convert_time=time)
        # update the path display box
        window['-current_path_box-'].update(value=current_dir)
        return current_dir, previous_dir, rendered_table, sftp_item_list
    else:
        return dir, old_dir, table, item_list
def download_window(window,selection, download_item_list):
    download_list = window['-download_list-'].get()
    if len(download_list) == 0:
        return download_item_list
    elif len(download_list) > 0:
        download_list.pop(selection)
        window['-download_list-'].update(values=download_list)
        new_download_item_list = download_item_list
        new_download_item_list.pop(selection)
        return new_download_item_list
def sftp_download_thread(window, workflow_option, item_list, sftp_connection, output_path):
    window['-download_frame-'].update(visible=True)
    file_count = len(item_list)
    file_number = 0
    download_list = window['-download_list-'].get()
    def download_progress(transferred_bytes, total_bytes):
        current_percentage = int(transferred_bytes / total_bytes * 100)
        window['-download_percentage-'].update(value = f'{current_percentage}%')
        window['-bytes_downloaded-'].update(value=f'Bytes Downloaded: {transferred_bytes} of {total_bytes}')
        window['-download_progress-'].update(current_count = current_percentage)
    for file in item_list:
        file_number += 1
        num_files = f'Downloading file {file_number} of {file_count}...'
        window['-num_files-'].update(value=num_files)
        local_path = f'{output_path}/{file.filename}'
        window['-sftp_output-'].print(f'Downloading: {file.filename}')
        try:
            sftp_connection.get(file.path,
                                local_path,
                                callback = download_progress,
                                prefetch = False
                                )
        except Exception as e:
            if e.args[0] == 'Socket is closed':
                window['-sftp_browser_frame-'].update(visible=False)
                window['-sftp_login_frame-'].update(visible=True)
            if e.args[0] == (13, 'Permission denied'):
                window['-sftp_output-'].print(f'{e.args}, connection may have timed out...')
            window['-sftp_output-'].print(f'File download error: {e.args}')
        else:
            window['-sftp_output-'].print('File download finished!')
            window.write_event_value(key=('-DOWNLOAD_THREAD-','-FILE_DOWNLOADED-'),
                                     value=file)
            download_list.remove([file.filename])
            window['-download_list-'].update(values = download_list)
def end_session(sftp_server, window):
    sftp_server.close()
    window['-sftp_browser_frame-'].update(visible=False)
    window['-sftp_login_frame-'].update(visible=True)
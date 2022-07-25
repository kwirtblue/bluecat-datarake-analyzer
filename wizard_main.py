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
import sys, os
from threading import Thread
from tkinter import ttk
import paramiko as pm
import sftp_tab,extract_tab
from datetime import datetime, timezone

version = '1.0.2'

sg.theme('DarkTeal12')
sg.UserSettings(filename='wizard_main.py')
sys.path.insert(0, '/images')

#Function to extract files depending on which options are selected


# Define the window's contents
#Create tab layouts
#sftp_server = 'bluecatsftp.bluecatnetworks.com'
sftp_server = '192.168.1.154'

#sg.Tab('Analyzer',analyzer_tab, key='analyzer')


def main():
    # Display and interact with the Window using an Event Loop
    # create layout
    layout = [
        [sg.TabGroup([[sg.Tab('SFTP', sftp_tab.sftp_tab, key='-SFTP_TAB-'),
                       sg.Tab('Extractor', extract_tab.extractor_tab, key='Extractor')]], key='-TABS-', expand_x=True,
                     expand_y=True)]
    ]

    # Create the window
    window = sg.Window('BlueCat Log Extractor',
                       layout,
                       icon='images/cat_icon.ico',
                       finalize=True,
                       resizable=True,
                       use_default_focus=False,
                       enable_close_attempted_event=True,
                       location=sg.user_settings_get_entry('-location-', default=(None, None))
                       )

    # Remove the dotted focus border that appears when you click on tabs
    s = ttk.Style()
    layout = s.layout('Tab')
    s.layout("Tab",
             [('Notebook.tab',
               {'children':
                    [('Notebook.padding',
                      {'children':
                           [('Notebook.label',
                             {'side': 'top', 'sticky': '', })],
                       'sticky': 'nswe', })],
                'sticky': 'nswe', })])
    window['-current_path_box-'].bind("<Return>", "_Enter")
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
                    bcat_sftp_server = pm.SSHClient()
                    bcat_sftp_server.set_missing_host_key_policy(pm.AutoAddPolicy())
                    #bcat_sftp_server.load_system_host_keys()
                    try:
                        bcat_sftp_server.connect(
                            sftp_server,
                            username=values['-sftp_username-'],
                            password=values['-sftp_password-'],
                            port=22
                        )
                        #create sftp object
                        sftp_con = bcat_sftp_server.open_sftp()
                        sftp_con.chdir(path='')
                        current_dir = '/'
                        current_file_list = sftp_con.listdir_attr()
                        rendered_table = sftp_tab.render_table(window,file_list=current_file_list, convert_time=values['-convert_time-'])
                        #remove login frame and show browser frame
                        window['-sftp_login_frame-'].update(visible=False)
                        window['-sftp_browser_frame-'].update(visible=True)
                        window['-current_path_box-'].update(value='/')

                    except Exception as e:
                        pos_x,pos_y = window.current_location()
                        sg.PopupScrolled(e, location=(pos_x,pos_y), size=(32,12))
        if event == '-convert_time-':
            sftp_tab.render_table(window,file_list=current_file_list, convert_time=values['-convert_time-'])
        if event == '-sftp_browser-':
            #get row that was double clicked and return the first/only item in the list as an int, prevent erros from
            # clicking outside of the box and popup any other errors
            try:
                row_selected = values['-sftp_browser-'][0]
            except IndexError:
                pass
            except Exception as e:
                sg.Popup(e.args, location=window.current_location())
            else:
                selected_row = rendered_table[row_selected]
                dir_path = f'{current_dir}{selected_row[0]}/'
                #check if selected row is a directory or a file
                if selected_row[2][0] == 'd':
                    try:
                        sftp_con.chdir(dir_path)
                        current_file_list = sftp_con.listdir_attr()
                    # catch exception if reading directory fails due to connection, return to login screen
                    except OSError as o:
                        if o.args[0] == 'Socket is closed':
                            bcat_sftp_server.close()
                            sg.Popup('Connection error! Returning to login screen...', locaiton=window.current_location())
                            window['-sftp_browser_frame-'].update(visible=False)
                            window['-sftp_login_frame-'].update(visible=True)
                        else:
                            sg.Popup(o, location=window.current_location())
                    except Exception as e:
                        sg.Popup(e, location=window.current_location())
                    else:
                        previous_dir = current_dir
                        current_dir = dir_path
                        rendered_table = sftp_tab.render_table(window, file_list=current_file_list,
                                                               convert_time=values['-convert_time-'])
                        window['-current_path_box-'].update(value=current_dir)
                else:
                    sg.Popup("Can't double click files yet", location=window.current_location())
        if event == '-current_path_box-' + '_Enter':
            input_path = values['-current_path_box-']
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
                    bcat_sftp_server.close()
                    sg.Popup('Connection error! Returning to login screen...', location=window.current_location())
                    window['-sftp_browser_frame-'].update(visible=False)
                    window['-sftp_login_frame-'].update(visible=True)
                else:
                    sg.Popup('Invalid directory', location=window.current_location())
            except Exception:
                sg.Popup(o, location=window.current_location())
            else:
                current_file_list = sftp_con.listdir_attr()
                current_dir = input_path
                #update previous directory for the back button
                suffix = current_dir.split('/')[-2] + "/"
                previous_dir = current_dir.removesuffix(suffix)
                window['-current_path_box-'].update(value=current_dir)
                rendered_table = sftp_tab.render_table(window, file_list=current_file_list,
                                                       convert_time=values['-convert_time-'])


        if event == '-sftp_back_button-':
            if current_dir != '/':
                #change directory to previous directory
                sftp_con.chdir(previous_dir)
                #update current directory
                current_dir = previous_dir
                #update the previous dir
                suffix = previous_dir.split('/')[-2] + "/"
                previous_dir = previous_dir.removesuffix(suffix)
                #update file list
                current_file_list = sftp_con.listdir_attr()
                #re-render the table
                rendered_table = sftp_tab.render_table(window, file_list=current_file_list,convert_time=values['-convert_time-'])
                #update the path display box
                window['-current_path_box-'].update(value=current_dir)
        if event == '-sftp_end_session-':
            bcat_sftp_server.close()
            window['-sftp_browser_frame-'].update(visible=False)
            window['-sftp_login_frame-'].update(visible=True)


        ###END OF SFTP TAB EVENTS
        ####START OF EXTRACTOR TAB EVENTS
        if event == '-DATARAKE_FILE-':
            if extract_tab.proteus_check.search(values['-DATARAKE_FILE-']):
                window['-BAM_FRAME-'].update(visible=True)
                window['-BDDS_FRAME-'].update(visible=False)
                window['-DHCP-'].update(value=False)
                window['-DNS-'].update(value=False)
                print('BAM datarake detected')

            elif extract_tab.adonis_check.search(values['-DATARAKE_FILE-']):
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
                    thread = Thread(target=extract_tab.extract_tar, args=(output_path, dfile, options, fname, window)).start()
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

if __name__ == '__main__':
    main()
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
import sftp_tab,extract_tab
from datetime import datetime, timezone

version = '1.0.2'

sg.theme('DarkTeal12')
sg.UserSettings(filename='wizard_main.py')
sys.path.insert(0, '/images')

#sftp_server = 'bluecatsftp.bluecatnetworks.com'
sftp_server = '192.168.1.154'
def main():
    # create layout
    layout = [
        [sg.TabGroup([[sg.Tab('SFTP', sftp_tab.sftp_tab, key='-SFTP_TAB-'),
                       sg.Tab('Extractor', extract_tab.extractor_tab, key='Extractor')]], key='-TABS-', expand_x=True,
                     expand_y=True)]
    ]
    # sg.Tab('Analyzer',analyzer_tab, key='analyzer')
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
    #enter button binding for the sftp path both
    window['-current_path_box-'].bind("<Return>", "_Enter")

    ### MAIN PROGRAM LOOP!!!
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
            sftp_con, bcat_sftp_server, current_file_list, rendered_table, sftp_item_list = sftp_tab.login(
                username=values['-sftp_username-'],
                password=values['-sftp_password-'],
                time=values['-convert_time-'],
                window=window)
            current_dir = '/'
            previous_dir = '/'
        if event == '-convert_time-':
            try:
                current_file_list=sftp_con.listdir_attr()
                rendered_table, sftp_item_list =sftp_tab.render_table(window,file_list=current_file_list, convert_time=values['-convert_time-'])
            except Exception as o:
                if o.args[0] == 'Socket is closed':
                    sg.Popup('Connection error! Returning to login screen...', location=window.current_location())
                    window['-sftp_browser_frame-'].update(visible=False)
                    window['-sftp_login_frame-'].update(visible=True)
        if event == '-sftp_browser-':
            # Get row that was double-clicked and return the first/only item in the list as an int, prevent errors from
            # clicking outside the box and popup any other errors, if no errors then run browser function
            try:
                row = values['-sftp_browser-'][0]
            except IndexError:
                pass
            except Exception as e:
                sg.Popup(e.args, location=window.current_location())
            else:
                if 'download_item_list' not in locals():
                    download_item_list = []
                current_dir,previous_dir,rendered_table,sftp_item_list,download_item_list = sftp_tab.sftp_browser(
                    row = row,
                    table=rendered_table,
                    dir=current_dir,
                    old_dir=previous_dir,
                    sftp_con=sftp_con,
                    sftp_server=bcat_sftp_server,
                    window=window,
                    time=values['-convert_time-'],
                    item_list=sftp_item_list,
                    download_list= window['-download_list-'].get(),
                    download_item_list=download_item_list)
        if event == '-current_path_box-' + '_Enter':
            current_dir, previous_dir, rendered_table, sftp_item_list =sftp_tab.path_box(
                path=values['-current_path_box-'],
                dir=current_dir,
                old_dir=previous_dir,
                table=rendered_table,
                sftp_con=sftp_con,
                sftp_server=bcat_sftp_server,
                window=window,
                time=values['-convert_time-'])
        if event == '-sftp_back_button-':
            try:
                current_dir, previous_dir, rendered_table, sftp_item_list = sftp_tab.back_button(
                    dir=current_dir,
                    old_dir=previous_dir,
                    table=rendered_table,
                    sftp_con=sftp_con,
                    window=window,
                    time=values['-convert_time-'],
                    item_list=sftp_item_list
                )
            except Exception as o:
                if o.args[0] == 'Socket is closed':
                    sg.Popup('Connection error! Returning to login screen...', location=window.current_location())
                    window['-sftp_browser_frame-'].update(visible=False)
                    window['-sftp_login_frame-'].update(visible=True)
        if event == '-download_list-':
            try:
                selection = values['-download_list-'][0]
            except:
                pass
            else:
                download_item_list = sftp_tab.download_window(window, selection, download_item_list=download_item_list)
        if event == '-SFTP_OUTPUT_FOLDER-':
            window['-OUTPUT_FOLDER-'].update(value=values['-SFTP_OUTPUT_FOLDER-'])
        if event == '-download_only-':
            download_file_list = window['-download_list-'].get()
            window['-download_only-'].update(disabled=True)
            window['-download_extract-'].update(disabled=True)
            window['-download_analyze-'].update(disabled=True)
            window.start_thread(lambda : sftp_tab.sftp_download_thread(window,
                                                                       workflow_option='download_only',
                                                                       item_list= download_item_list,
                                                                       output_path= values['-OUTPUT_FOLDER-'],
                                                                       sftp_connection= sftp_con
                                                                       ),
                                end_key=('-DOWNLOAD_THREAD-','-DOWNLOADS_FINISHED-'))
        if event == '-download_extract-':
            sg.Popup(window['-download_list-'].get())
            #sftp_tab.sftp_workflow(workflow_option='download_extract', output_path= values['-OUTPUT_FOLDER-'])
        if event == '-download_analyze-':
            pass
            #sftp_tab.sftp_workflow(workflow_option='download_analyze', output_path= values['-OUTPUT_FOLDER-'])
        if event[0] == '-DOWNLOAD_THREAD-':
            if event[1] == '-DOWNLOADS_FINISHED-':
                sg.Popup('Sweet success!', location=window.current_location())
                window['-download_only-'].update(disabled=False)
                window['-download_extract-'].update(disabled=False)
                window['-download_analyze-'].update(disabled=False)
        if event == '-sftp_end_session-':
            sftp_tab.end_session(
                sftp_server=bcat_sftp_server,
                window=window
            )
        ###END OF SFTP TAB EVENTS

        ####START OF EXTRACTOR TAB EVENTS
        if event == '-DATARAKE_FILE-':
            extract_tab.detect_file(window,values['-DATARAKE_FILE-'])
        if event == '-FULL_EXTRACT-':
            extract_tab.full_extract_toggle(window,
                                            extract_checkbox=values['-FULL_EXTRACT-'],
                                            all_options_checkbox=values['-all_options-'])
        if event == '-all_options-':
            extract_tab.all_options_toggle(window, all_options_checkbox=values['-all_options-'])
        #Handle event when extract logs button is clicked
        if event == 'Extract Logs':
            extraction_thread, fname, output_path = extract_tab.extract_logs(window,values)
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
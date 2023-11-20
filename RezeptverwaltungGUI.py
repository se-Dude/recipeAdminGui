import json
import sys
import os
import PySimpleGUI as sg
import pymysql.cursors
from datetime import datetime
from PyPDF2 import PdfReader
from PIL import Image as img  
import pytesseract as PT  
from pdf2image import convert_from_path as CFP

currentPath = os. getcwd()
icon = currentPath + r'\ico.ico'
print(icon)
#Build exe: pyinstaller --onefile -i ico.ico -w RezeptverwaltungGUI.py

def ErrorWindw(errorMsg: str):

    layout = [

        [sg.Text(errorMsg)],
        [sg.Quit()]
    ]

    windowError = sg.Window('Fehler', layout, icon=icon)

    while True:
        event, values = windowError.read()
        if event in (sg.WINDOW_CLOSED, "Quit"):
            windowError.close()
            break
        if event == sg.WIN_CLOSED:
            break

 

def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def defaultsettings():
    #read settings
    try :
        with open('settings.json', 'r') as openfile:
    
            
            settings = json.load(openfile)
            return settings

    except :

        defaultSettings = {
            
            "HostnameDB": '',
            "UsernameDB": 'GUI',
            "PasswordDB": '',
            "DeletePDFafterDBInsert": True,
            "pathToTesseract": r"C:\Users\dthur\Documents\Privat\rezeptverwaltung\OCR_Lib\tesseract.exe",
            
        }
    
        settings = defaultSettings

        defaultSettings = json.dumps(defaultSettings, indent=4)
    

        with open("settings.json", "w") as outfile:
            outfile.write(defaultSettings)

        return settings

def setSettings():
        
    global settings
    
    layout=[


       
        [sg.Text('HostnameDB:', size=(21, 1)), sg.InputText(key='Hostname',default_text= settings["HostnameDB"])],
        [sg.Text('UsernameDB:', size=(21, 1)), sg.InputText(key='Username',default_text= settings["UsernameDB"])],
        [sg.Text('PasswortDB:', size=(21, 1)), sg.InputText(key='Password')],
        [sg.Text('Pfad zu Tesseract:', size=(21, 1)), sg.InputText(key='pathToTesseract',default_text= settings["pathToTesseract"])],
        [sg.Checkbox('PDF nach dem lesen löschen',key='delPdf', default=settings["DeletePDFafterDBInsert"])],
        [sg.Button('OK',key='ok')]
    
      
    ]

    windowSettings= sg.Window('Grundeinstellungen', layout, finalize=True, icon=icon)

    while True:
         event, values = windowSettings.read()

         if event == sg.WIN_CLOSED:
            break

         if event == 'ok':
            
            settings["HostnameDB"] = values['Hostname']
            settings["UsernameDB"] = values['Username']
            settings["PasswordDB"] = values['Password']
            settings["DeletePDFafterDBInsert"] = values['delPdf']
            settings["pathToTesseract"] = values['pathToTesseract']

            newSettings = json.dumps(settings, indent=4)

            with open("settings.json", "w") as outfile:
                outfile.write(newSettings)

            windowSettings.close()
            mainWindow()

def connectDB():

    global settings
    try :
        connection = pymysql.connect(host=settings['HostnameDB'],
                                        user=settings['UsernameDB'],
                                        password=settings['PasswordDB'],
                                        database='rezeptdb',
                                        charset='utf8mb4',
                                        cursorclass=pymysql.cursors.DictCursor)
        return connection

    except Exception as error:

        layout=[


       
        [sg.Text('Ein Fehler ist aufgetreten!', size=(18, 1))],
        [sg.Text('Details:', size=(18, 1)), sg.Text(text=error, size=(18,1))],
        [sg.Quit()]
    
      
    ]

    window= sg.Window('Fehler', layout, finalize=True, icon=icon)

    while True:
         event, values = window.read()
         if event in (sg.WINDOW_CLOSED, "Quit"):
            window.close()
            break

def getLabels():
    global connection

    sql = "SELECT label FROM labels ORDER BY labels.id desc"

    with connection.cursor() as cursor:
        cursor.execute(sql)
        labels = cursor.fetchall()

    return labels

def addLabel():
    layout = [     
                    [sg.Text('Label:'),sg.InputText(key='newLabel')],
                    [sg.Button(f'Speichern')],
                    [sg.Quit()]
                    ]
    window = sg.Window('Rezeptverwaltung',icon=icon).layout(layout)
    
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Quit"):
             window.close()
             mainWindow()
             break
             
        if event == "Speichern" and not values['newLabel'] == '':

            sql = 'SELECT `label` FROM `labels` WHERE label = (%s)'

            with connection.cursor() as cursor:

                cursor.execute(sql,(values['newLabel']))
                result = cursor.fetchone()

            if not result:

                sql = 'INSERT INTO `labels` (`label`) VALUES (%s)'
                with connection.cursor() as cursor:

                    cursor.execute(sql,(values['newLabel']))
                    connection.commit()
                window.close()
                mainWindow()
                break

            else:
                ErrorWindw(errorMsg='Das Angegebene Label ist ungültig oder bereits vorhanden!')

def add():
    global connection
    global settings
    layout = [     
                        
                    [sg.Text('Pfad zum PDF:',size=(50,1)),sg.FilesBrowse('Browse',key='path')],
                    [sg.Checkbox('PDF nach dem lesen löschen',key='delPdf', default=settings["DeletePDFafterDBInsert"])],
                    [sg.Button(f'Rezept aufnehmen')],
                    [sg.Text('Fortschritt:',size=(50,1))],
                    [sg.ProgressBar(100,orientation='h',size=(20,20), key='prog')],
                    [sg.Quit()]
                    ]
    window = sg.Window('Rezeptverwaltung', icon=icon).layout(layout)


    
    
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Quit"):
             window.close()
             mainWindow()
             break
        if event == "Rezept aufnehmen" and not values['path'] == '':
            window['Rezept aufnehmen'].update(disabled=True)
            prog = 10
            window['prog'].update(prog)

            pathToPDF = values['path']
            delPdf = values['delPdf']
            reader = PdfReader(pathToPDF)

            rec = False
            defaultName = ""
            pathToPDFBack = pathToPDF[::-1]


            for element in pathToPDFBack:
                if rec == True and element == "/":
                    rec = False
                    break

                if rec == True:
                    defaultName = defaultName + element

                if rec == False and element == ".":
                    rec = True
                
                

                
                
                
            defaultName = defaultName[::-1]
            
            

            for i in range(0,len(reader.pages)):
                        page = reader.pages[i]
                        text = ''
                        text = text + page.extract_text()
                        prog = prog + round(50/len(reader.pages),0)
                        window['prog'].update(prog)

               
            pages_1 = CFP(pathToPDF)  

            image_counter1 = 1  
            
            for page in pages_1:  
                prog = (prog + round(20/len(reader.pages),0))
                window['prog'].update(prog)
                filename1 = "Page_no_" + str(image_counter1) + " .jpg"  
                    
                page.save(filename1, 'JPEG')  
                
                image_counter1 = image_counter1 + 1  
                
            filelimit1 = image_counter1 - 1


            
            for K in range(1, filelimit1 + 1):  
                prog = prog + round(10/len(reader.pages),0)
                window['prog'].update(prog)
                filename1 = "Page_no_" + str(K) + " .jpg"  

                PT.pytesseract.tesseract_cmd = settings['pathToTesseract']                        
                custom_config = r'-l deu --psm 6'
                text = str(((PT.image_to_string (img.open (filename1), config=custom_config))))
                text = text.replace('-\n', '')     

            
            for K in range(1, filelimit1 + 1): 
                filename1 = "Page_no_" + str(K) + " .jpg" 
                os.remove(filename1)

                
            sql = 'SELECT `id` FROM `rezepte` WHERE rezept = (%s)'

            with connection.cursor() as cursor:

                cursor.execute(sql,(text))
                result = cursor.fetchone()
            


            if not result:
                prog = 100
                window['prog'].update(prog)
                window.close()

                labels = getLabels()
                

                layout = [     
                    [sg.Text('Rezepttitel:'),sg.InputText(key='title',default_text=defaultName)],
                    [sg.Button(f'OK')],
                    [sg.Quit()]                    
                    ]
                for item in labels:
                    layout.insert(3,[sg.Checkbox(item['label'],key=item['label'])])

                window = sg.Window('Rezept aufnehmen', icon=icon).layout([[sg.Column(layout, size=(300,300), scrollable=True)]])
                    
                while True:
                    event, values = window.read()
                    if event in (sg.WINDOW_CLOSED, "Quit"):
                        window.close()
                        break

                
                

                    if event == 'OK':
                        title = values['title']

                        sql = 'SELECT `id` FROM `rezepte` WHERE titel = (%s)'

                        with connection.cursor() as cursor:

                            cursor.execute(sql,(title))
                            result = cursor.fetchone()

                        if not result:
                            window.close()

                            file = convertToBinaryData(pathToPDF)

                            listlabels = ''

                            for item in labels:
                                
                                if values[item['label']]:
                                    listlabels = listlabels + item['label'] + ','



                            

                            now = datetime.utcnow()

                            sql = 'INSERT INTO `rezepte` (`titel`,`timestamp`,`rezept`,`label`,`pdf`) VALUES ( %s, %s, %s, %s, %s)'
                                
                            with connection.cursor() as cursor:

                                cursor.execute(sql,(title,now,text,listlabels,file))
                                connection.commit()

                            if delPdf:

                                os.remove(pathToPDF)

                            mainWindow()
                            break

                        else:
                           ErrorWindw(errorMsg='Das Rezept mit folgender ID hat den identischen Titel:' + str(result['id'])) 
            else:
                ErrorWindw(errorMsg='Das Rezept mit folgender ID hat den identischen Inhalt:' + str(result['id']))


        

def search():
     
    global connection
    listColumns = []
    
    sql = 'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = (%s) ORDER BY ORDINAL_POSITION ASC'
                
    with connection.cursor() as cursor:
        cursor.execute(sql,'rezepte')
        columns = cursor.fetchall()
        lenght = len(listColumns)
        for item in columns:
            listColumns.insert((lenght),item['COLUMN_NAME'])
            lenght = len(listColumns)

    labels = getLabels()
                

    layout = [
        [sg.Text('Suche nach:'),sg.Combo(listColumns,key='searchColumn')],     
        [sg.Text('Suchbegriff:'),sg.InputText(key='keyword')],
        [sg.Combo(['und','oder'],key='logic')],
        [sg.Button(f'OK')],
        [sg.Quit()],
        [sg.Text('Verknüpfungslogik Labels'),sg.Combo(['und','oder'],key='logic_label',default_value='oder')]
        ]
    
    for item in labels:
        layout.insert(6,[sg.Checkbox(item['label'],key=item['label'])])

    window = sg.Window('Rezept suchen', icon=icon).layout([[sg.Column(layout, size=(300,300), scrollable=True)]])

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Quit"):
             window.close()
             mainWindow()
             break
        if event == 'OK':
            listlabels = []

            if values['logic_label'] == 'und':
                logic_label='AND '
            elif values['logic_label'] == 'oder':
                logic_label='OR '
            
            for item in labels:
                if values[item['label']]:
                    
                    listlabels.insert(0, (item['label']))

            if values['logic'] == 'und':
                logic = 'AND '
                noLogic = False

            elif values['logic'] == 'oder':
                logic = 'OR '
                noLogic = False

            elif values['logic'] == '':
                noLogic = True
                logic = ''


            else:
                logic = ''
                ErrorWindw(errorMsg='Ungültige logische Verknüpfung')

            if logic == 'AND ' or logic == 'OR ' or logic == '':

                counter = 1
                sqlLabel = ''
                sqlVar = 'rezepte.' + values['searchColumn'] + " LIKE '%" + values['keyword'] + "%' "

                for item in listlabels:
                    sqlLabel = sqlLabel + "rezepte.label LIKE '%" + item + "%' "
                    if counter < len(listlabels):
                        sqlLabel = sqlLabel + logic_label

                    counter = counter + 1

                if values['keyword'] == '' or values['searchColumn'] == '':
                    sqlVar = ''
                    logic = ''

                elif noLogic:
                    sqlLabel = ''



                sql = "SELECT id, timestamp, titel, rezept, label, pdf FROM rezepte WHERE " + sqlVar + logic + sqlLabel + "ORDER BY rezepte.timestamp DESC LIMIT 10000"

                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    result = cursor.fetchall()

                if len(result) < 1:
                    ErrorWindw('Keine übereinstimmungen gefunden!')
                    window.close()
                    mainWindow()

                if result:


                    lenght = len(listColumns)
                    

                    listResult = [[]]
                    
                    counter0 = 0
                    

                    for item in result:
                        
                        while True:
                            counter = 0
                            lenghtResult =len(listResult)
                            for object in listColumns:
                                
                                listResult[counter0].insert((lenghtResult + 1),item[object])
                                lenghtResult =len(listResult[counter0])
                                counter = counter + 1
                                if counter >= lenght and not (len(listResult) == len(result)):
                                    actualLenght = len(listResult)
                                    dummyList = []
                                    listResult.insert(actualLenght,dummyList)
                                    break
                            if counter >= lenght:
                                counter0 = counter0 + 1
                                break
                if len(listResult) == len(result):
                        window.close()
                        showResultList(resultList=listResult,Toprow=listColumns)

def showResultList(resultList,Toprow):
    global connection
    layout = [
         
         [sg.Text('Ergebnisse:')],
         [sg.Table(values=resultList,display_row_numbers=False,headings=Toprow,key='Table', enable_events=True,auto_size_columns=True,visible_column_map=[True,False,True,False,True,False],alternating_row_color='RoyalBlue4')],
         [sg.Button('zurück', key='back')]
     ]

    windowResults = sg.Window('Suche', icon=icon).layout(layout)

    while True:

        event, values = windowResults.read()

        if event == 'Table':
            data_selected = [resultList[row] for row in values[event]]
            
            showEdit(data=data_selected)

        if event == 'back':
             windowResults.close()
             mainWindow()
             break
        
        if event == sg.WIN_CLOSED:
           break


def showEdit(data):

    layout = [     
                       
                 [sg.Button(f'Öffnen', size=(11,3)), sg.Button(f'Bearbeiten', size=(11,3))],
                 [sg.Quit()]
                 ]

    windowShowEdit = sg.Window('Suche', icon=icon).layout(layout)

    while True:
        event, values = windowShowEdit.read()


        if event in (sg.WINDOW_CLOSED, "Quit"):
             windowShowEdit.close()
             break
        
        if event == 'Öffnen':
            windowShowEdit.close()
            showPdf(data[0][5],filename=('Rezept.pdf'))

        if event == 'Bearbeiten':
            windowShowEdit.close()
            edit(data)



def edit(data):

    global connection

    labels = getLabels()

    layout = [
        [sg.Text('Titel:'),sg.InputText(key='title', default_text = data[0][2])],     
        [sg.Button('zurück', key='Quit'), sg.Button('Rezept Löschen', key='delete'), sg.Button('Ok', key='ok')],
        [sg.Text('Labels:')]
        ]
        
    for item in labels:
        
        if str(data[0][4]).find(item['label']) != -1:
            default = True

        else:
            default = False
         

        layout.insert(3,[sg.Checkbox(item['label'],key=item['label'],default=default)])

    windowEdit = sg.Window('Bearbeiten', icon=icon).layout([[sg.Column(layout, size=(300,300), scrollable=True)]])

    while True:
        event, values = windowEdit.read()


        if event in (sg.WINDOW_CLOSED, "Quit"):
             windowEdit.close()
             break
        
        if event == 'delete':

            sql = 'DELETE FROM rezepte WHERE id = %s;'

            try:
                with connection.cursor() as cursor:

                    cursor.execute(sql,(data[0][0]))
                    connection.commit()
            except Exception as error:

                ErrorWindw(error)

        if event == 'ok':

            listlabels = ''

            for item in labels:
                                
                if values[item['label']]:
                    listlabels = listlabels + item['label'] + ','

            now = datetime.utcnow()


            sql = 'UPDATE `rezepte` SET `titel` = %s,`timestamp` = %s,`label` = %s WHERE `id` = %s'
           
            try:
                with connection.cursor() as cursor:

                    cursor.execute(sql,(values['title'],now,listlabels,data[0][0]))
                    connection.commit()
                windowEdit.close()
                
            except Exception as error:

                ErrorWindw(error)
        

def showPdf(data, filename):
    with open(filename, 'wb') as f:
        f.write(data)

    os.startfile(filename)

def mainWindow():
    
    layout = [     
                       
                 [sg.Button(f'Rezept aufnehmen', size=(11,3)), sg.Button(f'Rezept suchen', size=(11,3))],
                 [sg.Button(f'Label  hinzufügen', size=(11,3))],
                 [sg.Button(f'Einstellungen')],
                 [sg.Quit()]
                 ]

    window = sg.Window('Rezeptverwaltung', icon=icon).layout(layout)


    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Quit"):
             window.close()
             sys.exit(0)
        elif event == "Rezept aufnehmen":
            window.close()
            add()
            break
        elif event == 'Label  hinzufügen':
            window.close()
            addLabel()
            break
        elif event == 'Rezept suchen':
            window.close()
            search()
            break
        elif event == 'Einstellungen':
            window.close()
            setSettings()
            break


settings = defaultsettings()
connection = connectDB()
mainWindow()

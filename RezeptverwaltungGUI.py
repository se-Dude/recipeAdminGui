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



def ErrorWindw(errorMsg: str):

    layout = [

        [sg.Text(errorMsg)],
        [sg.Quit()]
    ]

    windowError = sg.Window('Fehler', layout)

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
            
            "HostnameDB": 'localhost',
            "PasswordDB": '',
            "DeletePDFafterDBInsert": 'true',
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
        [sg.Text('PasswortDB:', size=(21, 1)), sg.InputText(key='Password')],
        [sg.Text('Pfad zu Tesseract:', size=(21, 1)), sg.InputText(key='pathToTesseract',default_text= settings["pathToTesseract"])],
        [sg.Text('Pdf Löschen nach Upload', size=(21,1)), sg.InputText(key='delPdf',default_text= settings["DeletePDFafterDBInsert"])],
        [sg.Button('OK',key='ok')]
    
      
    ]

    windowSettings= sg.Window('Grundeinstellungen', layout, finalize=True)

    while True:
         event, values = windowSettings.read()

         if event == sg.WIN_CLOSED:
            break

         if event == 'ok':
            
            settings["HostnameDB"] = values['Hostname']
            settings["PasswordDB"] = values['Password']
            settings["DeletePDFafterDBInsert"] = values['delPdf']
            settings["pathToTesseract"] = values['pathToTesseract']

            settings = json.dumps(settings, indent=4)

            with open("settings.json", "w") as outfile:
                outfile.write(settings)

            windowSettings.close()
            mainWindow()

def connectDB():

    global settings
    try :
        connection = pymysql.connect(host='localhost',
                                        user='test',
                                        password='test',
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

    window= sg.Window('Fehler', layout, finalize=True)

    while True:
         event, values = window.read()
         if event in (sg.WINDOW_CLOSED, "Quit"):
            window.close()
            break

def addLabel():
    layout = [     
                    [sg.Text('Label:'),sg.InputText(key='newLabel')],
                    [sg.Button(f'Speichern')],
                    [sg.Quit()]
                    ]
    window = sg.Window('Rezeptverwaltung').layout(layout)
    
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
                    [sg.Checkbox('PDF nach dem lesen löschen',key='delPdf')],
                    [sg.Button(f'Rezept aufnehmen')],
                    [sg.Text('Fortschritt:',size=(50,1))],
                    [sg.ProgressBar(100,orientation='h',size=(20,20), key='prog')],
                    [sg.Quit()]
                    ]
    window = sg.Window('Rezeptverwaltung').layout(layout)


    
    
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

                sql = "SELECT label FROM labels"
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    labels = cursor.fetchall()
                

                layout = [     
                    [sg.Text('Rezepttitel:'),sg.InputText(key='title')],
                    [sg.Button(f'OK')],
                    [sg.Quit()]                    
                    ]
                for item in labels:
                    layout.insert(1,[sg.Checkbox(item['label'],key=item['label'])])

                window = sg.Window('Rezept aufnehmen').layout(layout)
                    
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


    sql = "SELECT label FROM labels"

    with connection.cursor() as cursor:
        cursor.execute(sql)
        labels = cursor.fetchall()
                

    layout = [
        [sg.Text('Suche nach:'),sg.Combo(listColumns,key='searchColumn')],     
        [sg.Text('Suchbegriff:'),sg.InputText(key='keyword')],
        [sg.Combo(['und','oder'],key='logic')],
        [sg.Button(f'OK')],
        [sg.Quit()]                    
        ]
    
    for item in labels:
        layout.insert(3,[sg.Checkbox(item['label'],key=item['label'])])

    window = sg.Window('Rezept suchen').layout(layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Quit"):
             window.close()
             mainWindow()
             break
        if event == 'OK':
            listlabels = []
            
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
                ErrorWindw(errorMsg='Ungültige logische Verjnüpfung')

            if logic == 'AND ' or logic == 'OR ' or logic == '':

                counter = 1
                sqlLabel = ''
                sqlVar = 'rezepte.' + values['searchColumn'] + " LIKE '%" + values['keyword'] + "%' "

                for item in listlabels:
                    sqlLabel = sqlLabel + "rezepte.label LIKE '%" + item + "%' "
                    if counter < len(listlabels):
                        sqlLabel = sqlLabel + 'AND '

                    counter = counter + 1

                if values['keyword'] == '' or values['searchColumn'] == '':
                    sqlVar = ''
                    logic = ''

                elif noLogic:
                    sqlLabel = ''



                sql = "SELECT id, timestamp, titel, rezept, label, pdf FROM rezepte WHERE " + sqlVar + logic + sqlLabel + "ORDER BY rezepte.timestamp DESC LIMIT 100"

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
         [sg.Table(values=resultList,display_row_numbers=False,headings=Toprow,key='Table', enable_events=True,auto_size_columns=True)],
         [sg.Button('zurück', key='back')]
     ]

    windowResults = sg.Window('Suche').layout(layout)

    while True:

        event, values = windowResults.read()

        if event == 'Table':
            data_selected = [resultList[row] for row in values[event]]
            
            showPdf(data=data_selected[0][5],filename=('Rezept.pdf'))

        if event == 'back':
             windowResults.close()
             mainWindow()
             break
        
        if event == sg.WIN_CLOSED:
           break


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

    window = sg.Window('Rezeptverwaltung').layout(layout)


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

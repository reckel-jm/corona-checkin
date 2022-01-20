#!/usr/bin/python

import cv2
import numpy as np
from pyzbar.pyzbar import decode
import os
import subprocess
import json
import sys
from datetime import date, datetime
from PyQt5 import QtWidgets, uic

#CAMERADEVICENUM = 2


def returnCameraIndexes():
    # checks the first 10 indexes.
    index = 0
    arr = []
    i = 10
    while i > 0:
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            arr.append(str(index))
            cap.release()
        index += 1
        i -= 1
    return arr

class App():
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = uic.loadUi("qt.ui")
        self.window.noqrcodebutton.clicked.connect(self.guiNoQR)
        self.window.scanqrcodebutton.clicked.connect(self.guiScanQR)
        self.window.buttonOkay.clicked.connect(self.finish)
        #window.tabWidget.setTabEnabled(1, False)
        today = date.today()
        self.filename = today.strftime('%Y-%m-%d.json')
        self.registrationinfo = {'persons' : []}
        self.__reset()
        self.openFileifExists()
        cameras = returnCameraIndexes()
        self.window.cameraCombo.addItems(cameras)

    def start(self):
        self.window.show()
        self.app.exec()

    def guiScanQR(self):
        res = self.startDecoderLoop()
        if self.curQRValid == True:
            self.guiGoToCheckin()
            self.curUserForename = self.registrationinfo['persons'][-1]['Forename']
            self.curUserSurname = self.registrationinfo['persons'][-1]['Surname']
            self.window.editName.setText(self.curUserSurname)
            self.window.editFirstName.setText(self.curUserForename)

    def guiNoQR(self):
        alert = QtWidgets.QMessageBox()
        alert.setText("Bitte überprüfe die Gültigkeit manuell. Ist das Zertifikat gültig?")
        alert.setInformativeText("Ein Genesenenzertifikat darf nur drei Monate alt sein, der Impfausweis muss min. zwei Wochen alt sein.")
        alert.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        ret = alert.exec_()
        if ret == QtWidgets.QMessageBox.Yes:
            self.registrationinfo['persons'].append({})
            self.guiGoToCheckin()

    def guiGoToCheckin(self):
        self.window.tabWidget.setTabEnabled(1, True)
        self.window.tabWidget.setCurrentIndex(1)
        self.window.tabWidget.setTabEnabled(0, False)
        if self.curVaccineJson != None:
            self.window.vacDataResult.show()
            string = self.getImportantVaccineInfoAsString()
            self.window.vacDataResult.setPlainText(string)
        else:
            self.window.vacDataResult.hide()

    def decoder(self,image):
        gray_img = cv2.cvtColor(image,0)
        barcode = decode(gray_img)

        for obj in barcode:
            points = obj.polygon
            (x,y,w,h) = obj.rect
            pts = np.array(points, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(image, [pts], True, (0, 255, 0), 3)

            barcodeData = obj.data.decode("utf-8")
            barcodeType = obj.type
            string = "Data " + str(barcodeData) + " | Type " + str(barcodeType)

            cv2.putText(image, string, (x,y), cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,0,0), 2)
            shellexcape = barcodeData.replace("$", "\\$")
            shellexcape.replace("\\", "\\\\")
            output = subprocess.getstatusoutput('python vacdec/vacdec --raw-string "' + shellexcape + '" --certificates-directory vacdec/certs --certificate-db-json-file vacdec/certs/roots/Digital_Green_Certificate_Signing_Keys.json')
            output = output[1]
            if output.find("Signature verified ok") != -1:
                print('QR-Code is valid')
                self.curQRValid = True
                return output
            else:
                print("No Validation possible.")
                self.curQRValid = False
            return output
        return False

    def parseOutput(self,output):
        if output.find("Signature verified ok") != -1:
            print('QR-Code is valid')
        else:
            self.showErrorQRNotValid()
            print("No Validation possible. Print whole Output:")
            print(output)
            return
        pos = output.find("JSON: ")
        if pos != -1:
            #print('Versuche das Parsen')
            json_string = output[pos+len("JSON: "):output.rfind('}')+1]
            vacdata = json.loads(json_string)
            self.curVaccineJson = vacdata
            self.registrationinfo['persons'].append((vacdata['Health certificate']["1"]["Name"]))
            #print(self.registrationinfo)

    def startDecoderLoop(self):
        cap = cv2.VideoCapture(int(str(self.window.cameraCombo.currentText())))
        qrdetected = False
        while qrdetected == False:
            ret, frame = cap.read()
            qrdetected = self.decoder(frame)
            cv2.putText(frame, 'Bitte Covid-Pass zeigen', (100, 100), cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,0,0), 2)
            imageshow = cv2.imshow('Impfausweis scannen', frame)
            code = cv2.waitKey(10)
            if code == ord('q') or qrdetected != False:
                cv2.destroyAllWindows()
                if qrdetected != False:
                    self.parseOutput(qrdetected)
                return False
        return qrdetected

    def showErrorQRNotValid(self):
        error = QtWidgets.QMessageBox()
        error.setWindowTitle("Fehler")
        error.setText("Der QR-Code ist nicht gültig! Bitte manuell überprüfen!")
        error.exec_()
        return

    def finish(self):
        now = datetime.now()
        now_string = dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        if self.window.editName.text() == '' or self.window.editName.text() == '' or (self.curQRValid == False and self.window.editPhone.text() == ''):
            error = QtWidgets.QMessageBox()
            error.setWindowTitle("Fehler")
            error.setText("Bitte vollständig ausfüllen!")
            error.exec_()
            return
        self.registrationinfo['persons'][-1]['checkin-timestamp'] = now_string
        self.registrationinfo['persons'][-1]['Surename'] = self.window.editName.text()
        self.registrationinfo['persons'][-1]['Forename'] = self.window.editFirstName.text()

        if self.window.editPhone.text() == '':
            self.registrationinfo['persons'][-1]['checkin-method'] = 'corona-warn-app'
        else:
            self.registrationinfo['persons'][-1]['phone'] = self.window.editPhone.text()
            self.registrationinfo['persons'][-1]['checkin-method'] = 'phone-number'
        with open(self.filename, 'w') as f:
            json.dump(self.registrationinfo, f, ensure_ascii=False)
        self.__reset()

    def __reset(self):
        self.window.tabWidget.setTabEnabled(1, False)
        self.window.tabWidget.setCurrentIndex(0)
        self.window.tabWidget.setTabEnabled(0, True)
        self.curQRValid = False
        self.curUserSurname = ""
        self.curUserForename = ""
        self.window.editFirstName.setText("")
        self.window.editName.setText("")
        self.window.editPhone.setText("")
        self.curVaccineJson = None
        self.window.vacDataResult.setPlainText("")
        self.window.vacDataResult.hide()

    def openFileifExists(self):
        if os.path.exists(self.filename):
            with open(self.filename) as json_file:
                try:
                    self.registrationinfo = json.load(json_file)
                except:
                    return

    def getImportantVaccineInfoAsString(self):
        infos = self.curVaccineJson['Health certificate']['1']['Vaccination'][0]
        infos['Birthday of Vaccinated Person'] = self.curVaccineJson['Health certificate']['1']['Date of birth']
        string = "Details of Vaccination:"
        print(infos)
        for k, v in infos.items():
            string = string + str(k) + ' : ' + str(v) + "\n"
        return string
        
def main():
    #print(returnCameraIndexes())
    app = App()
    app.start()

if __name__ == "__main__":
    main()

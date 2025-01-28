import sys
from croblink import *
from math import *
import xml.etree.ElementTree as ET
from heuristicSPT import *

CELLROWS=7
CELLCOLS=14
#out_file = "mappingC3.map"
#out_file2 = "mappa.map"
out_file = "mappingC3.map"
out_file2 = "mappa.map"

class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)

    # In this map the center of cell (i,j), (i in 0..6, j in 0..13) is mapped to labMap[i*2][j*2].
    # to know if there is a wall on top of cell(i,j) (i in 0..5), check if the value of labMap[i*2+1][j*2] is space or not
    def setMap(self, labMap):
        self.labMap = labMap

    def printMap(self):
        for l in reversed(self.labMap):
            print(''.join([str(l) for l in l]))
            
    def updateXYTeta(self, outR, outL, last_X, last_Y, last_Teta):
        x = 0
        y = 0
        lin = 0
        teta = 0
        rot = 0
        
        lin = (outL + outR)/2
        
        x = last_X + (lin*cos(last_Teta))
        y = last_Y + (lin*sin(last_Teta))
        rot = outR-outL
        #teta = last_Teta + rot
        teta = (self.measures.compass / 180) * pi
        
        global lastX, lastY, lastTeta
        lastX = x
        lastY = y
        lastTeta = teta
        
        return x, y, teta
        
    def updateDriveMotors(self, last_outLeft, inL, last_outRight, inR):
        outLeft = 0
        outRight = 0
        
        outLeft = (inL + last_outLeft) / 2
        outRight = (inR + last_outRight) / 2
        
        global last_outL, last_outR
        last_outL = outLeft
        last_outR = outRight
        
        return outLeft, outRight
        
    def correctXOnxPar(self, x, bussola, xpar): #Corrigir o valor do x nas interseçoes 
        correctX = 0
        #xSensor = x + 0.438
        interval = [xpar-0.1, xpar+0.1]
        if bussola >= -15 and bussola <= 15:    #Ir da esquerda para a direita
            xSensor = x + 0.438
            if xSensor < interval[0] or xSensor > interval[1]:
                xSensor = interval[0]
                correctX = xSensor - 0.438
                print("CORRIGIU X!!!")
            elif xSensor >= interval[0] and xSensor <= interval[1]:
                correctX = x
                print("X FICA IGUAL!!!")
        elif bussola <=-165 or bussola >= 165:  #Ir da direita para a esquerda
            xSensor = x - 0.438
            if xSensor > interval[1] or xSensor < interval[0]:   #0 
                xSensor = interval[1]   #0
                correctX = xSensor + 0.438
                print("CORRIGIU X!!!")
            elif xSensor <= interval[1] and xSensor >= interval[0]:    #0
                correctX = x
                print("X FICA IGUAL!!!")

        else:
            correctX = x
        
        print("CORRECT_X", correctX)
        
        return correctX
        
    def correctYOnyPar(self, y, bussola, ypar): #Corrigir o valor no y nas interseções
        correctY = 0
        interval = [ypar-0.1, ypar+0.1] 
        if bussola >= 75 and bussola <= 105:    #Ir para cima
            ySensor = y + 0.438
            if ySensor < interval[0] or ySensor > interval[1]:
                ySensor = interval[0]
                correctY = ySensor - 0.438
                print("CORRIGIU Y!!!")
            elif ySensor >= interval[0] and ySensor <= interval[1]:
                correctY = y
                print("Y FICA IGUAL!!!")
        elif bussola <= -75 and bussola >= -105: #Ir para baixo
            ySensor = y - 0.438
            if ySensor > interval[1] or ySensor < interval[0]:   #0
                ySensor = interval[1]   #0
                correctY = ySensor + 0.438
                print("CORRIGIU Y!!!")
            elif ySensor <= interval[1] and ySensor >= interval[0]:    #0
                correctY = y
                print("Y FICA IGUAL!!!")

        else:
            correctY = y
                
        print("CORRECT_Y", correctY)
                
        return correctY
    
    def calculateClosestPair(self, x, y, bussola): #Calcular o par mais proximo
        closestPairX = 0
        closestPairY = 0
        closestPairXaux = -1
        closestPairYaux = -1
        sensorX = 0
        sensorY = 0
        if bussola >= -35 and bussola <= 35: #horizontal da esquerda para a direita
            sensorX = x + 0.438
            closestPairXaux = round(sensorX,0)
        elif bussola <= -155 or bussola >= 155: #horizontal da direita para a esquerda
            sensorX = x - 0.438
            closestPairXaux = round(sensorX,0)
        elif bussola >= 65 and bussola <= 115:  #vertical de baixo para cima
            sensorY = y + 0.438
            closestPairYaux = round(sensorY,0)
        elif bussola >= -115 and bussola <= -65:    #vertical de cima para baixo
            sensorY = y - 0.438
            closestPairYaux = round(sensorY,0)
            
        
        if closestPairXaux % 2 == 0:
            closestPairX = closestPairXaux
            return closestPairX
        elif closestPairXaux % 2 != 0 and bussola >= -35 and bussola <= 35:
            closestPairX = closestPairXaux + 1
            return closestPairX
        elif closestPairXaux % 2 != 0 and bussola <= -155 or bussola >= 155:
            closestPairX = closestPairXaux - 1
            return closestPairX
        elif closestPairYaux % 2 == 0:
            closestPairY = closestPairYaux
            return closestPairY
        elif closestPairYaux % 2 != 0 and bussola >= 65 and bussola <= 115:
            closestPairY = closestPairYaux + 1
            return closestPairY
        elif closestPairYaux % 2 != 0 and bussola >= -115 and bussola <= -65:
            closestPairY = closestPairYaux - 1
            return closestPairY
        
        #Testar e secalhar tb fazer como o prof fez onde metiamos um vetor e o resultado do msm são, (valorX, valorY), os valores q vamos somar/subtrai no x e no y respetivamente
        return -1
    
    def normalizeCompass(self, teta):
        tetaResult = 0
        interval = [-180, 180]
        
        if teta > interval[1]:
            tetaResult = teta - 360
        elif teta > interval[0] and teta < interval[1]:
            tetaResult = teta
        elif teta < interval[0]:
            tetaResult =  teta + 360
            
        return tetaResult
    
    def correctCompass(self):
        if -15 < self.measures.compass < 15:
            return 0
        elif 75 < self.measures.compass< 105:
            return 90
        elif -105 < self.measures.compass <-75:
            return -90
        elif self.measures.compass <= -170 or self.measures.compass >= 170:
            return 180 * self.measures.compass / abs(self.measures.compass)
        
    def correctTeta(self):
        global teta
        
        print("RESULT_correctCOMPASS----->", self.correctCompass())
        
        if self.correctCompass() == 0:
            teta = 0
        elif self.correctCompass() == 90:
            teta = 90
        elif self.correctCompass() == 180:
            teta = 180
        elif self.correctCompass() == -90:
            teta = -90
    
    def removeElement(self, lista, x, y):
        # for element in lista:
        #     if x == element[0] and y == element[1]:
        #         lista.remove([x, y, element[2], element[3]])
        #SECALHAR alterar para remover as que vao para o msm sitio
        auxList = []
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            if subX >= 0 and subX <= 0.8 and subY >= 0 and subY <= 0.8:     #subX <= 0.2
                auxList.append([element[0], element[1], element[2], element[3]])
        for element in auxList:
            lista.remove([element[0], element[1], element[2], element[3]])
            
    def samePosition(self, lista, x, y, compass):
        #Guarda dos cruzamentos/entrocamentos as posiçoes para assim, por exemplo, no primeiro entrocanmento, qnd ele vem de baixo, nao guardar uma dir à esquerda
        #Pq na primeira volta ele ja veio daí
        same = False
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            if subX >= 0 and subX <= 0.8 and subY >= 0 and subY <= 0.8:     #x <= 0.5; y <= 0.6
                #Robo ia para cima, guardou as posiçoes das interseçoes, e ele agr vem para a direita ou para a esquerda
                if element[2] >= 70 and element[2] <= 110 and ((compass >= -30 and compass <= 30) or (compass <= -155 or compass >= 155)) and (x <= element[0] or x >= element[0]):#and y >= element[1]
                    same = True
                #Robo ia para baixo, guardou as posiçoes das interseçoes, e ele agr vem para a esquerda ou para a direita
                elif element[2] >= -110 and element[2] <= -70 and ((compass <= -160 or compass >= 160) or (compass >= -23 and compass <= 23)) and (x >= element[0] or x <= element[0]):#and y <= element[1]
                    same = True
                #Robo ia para a direita, guardou as posiçoes das interseçoes, e ele agr vem para a cima ou para baixo
                elif element[2] >= -30 and element[2] <= 30 and ((compass >= 70 and compass <= 123) or (compass >= -115 and compass <= -70)) and (y <= element[1] or y >= element[1]):
                    same = True
                #Robo ia para a esquerda, guardou as posiçoes das interseçoes, e ele agr vem para a baixo ou para cima
                elif (element[2] <= -155 or element[2] >= 155) and ((compass <= -70 and compass >= -115) or (compass >= 70 and compass <= 115)) and (y >= element[1] or y <= element[1]):
                    same = True	
        return same
    
                
    def checkDifference(self, lista, xvar, yvar, bussola, lastX, lastY, lastDirection, lastCompass):
        #Secalhar vamos tirar o diffOK
        diffOK = False
        direction = ""
        x = 1000
        y = 1000
        compass = 0
        for element in lista:
            subtractionx = abs(round(element[0] - xvar,1))
            subtractiony = abs(round(element[1] - yvar,1))
			# or (subtractionx == 0.2 and subtractiony == 0) or (subtractionx == 0.2 and subtractiony == 0.1)
			# subtractionx <= 0.1 and subtractionx >= 0 and subtractiony <= 0.1 and subtractiony >= 0
			#(bussola >= 65 and bussola <= 125)
            if bussola >= -125 and bussola <= -60:	#vertical para baixo
                subtractionBussola = bussola - element[3]      
                if subtractionx >= 0 and subtractionx<= 0.7 and subtractiony >=0 and subtractiony<= 0.7 and subtractionBussola <= 12 and subtractionBussola >= -25: #Estava a 2; 3 eventualmente aumentar mais, tipo 5
                    diffOK = True
                    direction = element[2]
                    x = element[0]
                    y = element[1]
                    compass = element[3]
            elif bussola >= 65 and bussola <= 125:	#vertical para cima
                subtractionBussola = bussola - element[3]      
                if subtractionx >= 0 and subtractionx<= 0.7 and subtractiony >=0 and subtractiony<= 0.7 and subtractionBussola <= 25 and subtractionBussola >= -12: #Estava a -2; -3
                    diffOK = True
                    direction = element[2]
                    x = element[0]
                    y = element[1]
                    compass = element[3]
            elif bussola >= -30 and bussola <= 30 and element[3] >= -30 and element[3] <= 30:   #horizontal da esquerda para a direita
                if (subtractionx >= 0 and subtractionx<= 0.7 and subtractiony >=0 and subtractiony<= 0.7):
                    diffOK = True
                    direction = element[2]
                    x = element[0]
                    y = element[1]
                    compass = element[3]
            #(bussola <= -160 or bussola >= 160) and (element[3] <= -155 or element[3] >= 155)
            elif (bussola <= -160 or bussola >= 160) and (element[3] <= -150 or element[3] >= 150):   #horizontal da direita para a esquerda, so estava else
                if (subtractionx >= 0 and subtractionx<= 0.7 and subtractiony >=0 and subtractiony<= 0.7):
                    diffOK = True
                    direction = element[2]
                    x = element[0]
                    y = element[1]
                    compass = element[3]
                    
            if lastX != 0 and lastY != 0 and lastDirection != "" and lastCompass != 0 and x == 0 and y == 0 and direction == "" and compass == 0:
                x = lastX
                y = lastY
                direction = lastDirection
                compass = lastCompass
            
        return diffOK, direction, x, y, compass
    
    # def changeRoutCompass(self, thislist, x, y, compass):  #Turn Right following the direction of compass, ALTERAR esta funçao e adicionar a bussola do robo. Testar
    #     sameLine = False
    #     xrem = 0
    #     yrem = 0
    #     for element in thislist:
    #         subtractX = abs(round(element[0] - x,1))
    #         subtractY = abs(round(element[1] - y,1))
    #         if subtractX <= 0.7 and subtractX >= 0.0 and subtractY <= 0.7 and subtractY >= 0.0 and element[2] == 'direita' and element[3] >= -118.0 and element[3] <= -105.0 and compass >= -40 and compass <= 20:
    #             sameLine = True
    #             xrem = element[0]
    #             yrem = element[1]
    #     return sameLine, xrem, yrem
    
    def doneDirection(self, removeList, x, y):
        directionDone = False
        for element in removeList:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            if subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7: #eventualmente pode-se aumentar para 0.8, antes o y estava 0.1
                directionDone = True
        return directionDone
    
    def checkCoordinatesInList(self, lista, x, y):    #verifica se as coordenadas (aproximadas, nao iguais) x,y da interseçao ja se encontram na lista das direçoes
        alreadyIn = False
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            if subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7:
                alreadyIn = True
        return alreadyIn 
    
    
    def sameCoordinateInList(self, lista, x, y):
        #Ver se a diferença entre o x,y das coordenadas do robo e da direçao da lista é superior
        #a 0.2 para se puder adicionar outra 
        same = False
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            if subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7:
                same = True
        return same
    
    def checkIfDirectionDone(self, lista, x, y, compass):   #Verifica se uma direçao ja foi feita "por outro lado", entroncamento
        done = False
        xToRemove = 0
        yToRemove = 0
        directionToRemove = ""
        compassToRemove = 0
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            print("SUBX_DIRECTION DONE->", subX)
            print("SUBY_DIRECTION DONE->", subY)
            print("ELEMENT[3]->", element[3])
            print("ELEMENT[1]->", element[1])
            print("y->", y)
            print("compass->", compass)
            #Alguma direçao na horizontal da esq para a direita e proximo do x,y da direçao
            if element[3] >= -32 and element[3] <= 32 and subX >= 0 and subX <= 0.8 and subY >= 0 and subY <= 0.8:	#Antes estava a -25 e 0.6
                if compass >= 75 and compass <= 105 and element[2] == 'direita' and y < element[1]:	#Robo a ir de baixo para cima, and y < element[1]
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True
                elif compass >= -105 and compass <= -75 and element[2] == 'esquerda' and y > element[1]:# Robo a ir de cima para baixo, and y > element[1]
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True
                elif compass >= -105 and compass <= -75 and element[2] == 'direita' and y < element[1]:# Robo a ir de cima para baixo e segue em frente, fazendo a direita
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True
                elif compass >= 75 and compass <= 105 and element[2] == 'esquerda' and y > element[1]:	#Robo a ir de baixo para cima, and y > element[1]
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True
            #Alguma direçao na vertical para baixo                
            elif element[3] >= -120 and element[3] <= -60 and subX >= 0 and subX <= 0.8 and subY >= 0 and subY <= 0.8:
                if compass >= -25 and compass <= 25 and element[2] == 'direita' and x < element[0]:	#Robo a vir da esquerda
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True	
                elif (compass <= -160 or compass >= 160) and element[2] == 'esquerda' and x > element[0]:	#Robo a vir da direita	
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True
                elif (compass <= -160 or compass >= 160) and element[2] == 'direita' and x < element[0]:    #Robo a ir para a esquerda, segue em frente, fazendo a direita
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True
                elif compass >= -25 and compass <= 25 and element[2] == 'esquerda' and x > element[0]:	#Robo a vir da esquerda
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True	
            #Alguma direçao na vertical para cima
            elif element[3] >= 60 and element[3] <= 120 and subX >= 0 and subX <= 0.8 and subY >= 0 and subY <= 0.8:
                if (compass <= -165 or compass >= 160) and element[2] == 'direita' and x > element[0]: #Robo vem da direita
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True
                elif compass >= -24 and compass <= 24 and element[2] == 'esquerda' and x < element[0]: #Robo vem da esquerda
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True
                elif compass >= -24 and compass <= 24 and element[2] == 'direita' and x > element[0]: #Robo vem da esquerda, segue em frente, fazendo a direita
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True
                elif (compass <= -165 or compass >= 160) and element[2] == 'esquerda' and x < element[0]: #Robo vem da direita
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True
            #Alguma direcao na horizontal da direita para a esquerda                
            elif (element[3] <= -152 or element[3] >= 152) and subX >= 0 and subX <= 0.8 and subY >= 0 and subY <= 0.8:
                if compass >= 75 and compass <= 105 and element[2] == 'esquerda' and y < element[1]:	#robo a ir para cima
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True
                elif compass >= -105 and compass <= -75 and element[2] == 'direita' and y > element[1]: #robo a ir para baixo
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True
                elif compass >= 75 and compass <= 105 and element[2] == 'direita' and y > element[1]:# Robo a ir para cima e segue em frente, fazendo a direita
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True
                elif compass >= -105 and compass <= -75 and element[2] == 'esquerda' and y < element[1]: #robo a ir para baixo
                    xToRemove = element[0]
                    yToRemove = element[1]
                    directionToRemove = element[2]
                    compassToRemove = element[3]
                    done = True
        return done, xToRemove, yToRemove, directionToRemove, compassToRemove
    
    def coordinatesDoneInCross(self, lista, x, y, compass, itsACross):
        #Verifica se o robo a ir numa determinada direçao (valor bussola), num cruzamento, faz um caminho em frente e remove a determinada direçao
        done = False
        xRemove = 0
        yRemove = 0
        directionRemove = ""
        compassRemove = 0
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            #Encontrou uma direçao muito proxima e é um cruzamento
            if subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and itsACross == True:   #Estava a 0.6
                #Se a direcao tiver sido encontrada qnd o robo ia para cima e ele agr esta a ir da esq para a dir
                if element[2] == 'direita' and element[3] >= 75 and element[3] <= 120 and compass >= -20 and compass <= 20 and x <= element[0]:
                    xRemove = element[0]
                    yRemove = element[1]
                    directionRemove = element[2]
                    compassRemove = element[3]
                    done = True
                #Se a direcao tiver sido encontrada qnd o robo ia para baixo e ele agr esta a ir da dir para a esq
                elif element[2] == 'direita' and element[3] >= -115 and element[3] <= -65 and (compass <= -160 or compass >= 160) and x >= element[0]:
                    xRemove = element[0]
                    yRemove = element[1]
                    directionRemove = element[2]
                    compassRemove = element[3]
                    done = True
                #Se a direcao tiver sido encontrada qnd o robo ia para a direita e ele agr esta a ir para baixo
                elif element[2] == 'direita' and element[3] >= -20 and element[3] <= 20 and compass >= -115 and compass <= -65 and y >= element[1]:
                    xRemove = element[0]
                    yRemove = element[1]
                    directionRemove = element[2]
                    compassRemove = element[3]
                    done = True
                #Se a direcao tiver sido encontrada qnd o robo ia para a esquerda e ele agr esta a ir para cima
                elif element[2] == 'direita' and (element[3] <= -160 or element[3] >= 160) and compass >= 75 and compass <= 120 and y < element[1]:
                    xRemove = element[0]
                    yRemove = element[1]
                    directionRemove = element[2]
                    compassRemove = element[3]
                    done = True
        return done, xRemove, yRemove, directionRemove, compassRemove
    
    def pathOnLeftAlreadyDoneEntroncamentos(self, lista, x, y, compass):
        #Ve se qnd chega a um entroncamento, e o caminho da esquerda ja foi feito, entao retorna true e vira a direita
        notDoneTurnRight = False
        dontAddRighDirection = False
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            if subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7:     #subX >= 0 and subX <= 0.5 and subY >= 0 and subY <= 0.6
                if element[3] >= -120 and element[3] <= -60:	#Direçao captada qnd estava a ir para baixo
                    if compass >= -24 and compass <= 24 and element[2] == 'direita' and x < element[0]: #robo vem da esquerda
                        notDoneTurnRight = True
                        dontAddRighDirection = True
                    elif (compass <= -160 or compass >= 160) and element[2] == 'esquerda' and x > element[0]: #robo vem da direita
                        notDoneTurnRight = False
                        dontAddRighDirection = True
                elif element[3] >= 60 and element[3] <= 120:	#Direçao captada qnd estava a ir para cima
                    if compass >= -24 and compass <= 24 and element[2] == 'esquerda' and x < element[0]: #robo vem da esquerda
                        notDoneTurnRight = False
                        dontAddRighDirection = True
                    elif (compass <= -160 or compass >= 160) and element[2] == 'direita' and x > element[0]: #robo vem da direita
                        notDoneTurnRight = True
                        dontAddRighDirection = True
                elif element[3] >= -30 and element[3] <= 30:	#Direçao captada qnd ia para a direita
                    if compass >= 65 and compass <= 115 and element[2] == 'direita' and y < element[1]: #robo esta a ir para cima
                        notDoneTurnRight = True
                        dontAddRighDirection = True
                    elif compass >= -120 and compass <= -60 and element[2] == 'esquerda' and y > element[1]: #robo esta a ir para baixo
                        notDoneTurnRight = False
                        dontAddRighDirection = True
                elif (element[3] <= -160 or element[3] >= 160):	#Direçao captada qnd ia para a esquerda
                    if compass >= 65 and compass <= 115 and element[2] == 'esquerda' and y < element[1]: #robo esta a ir para cima
                        notDoneTurnRight = False
                        dontAddRighDirection = True
                    elif compass >= -120 and compass <= -60 and element[2] == 'direita' and y > element[1]: #robo esta a ir para baixo
                        notDoneTurnRight = True
                        dontAddRighDirection = True
        return notDoneTurnRight, dontAddRighDirection
    
    def avoidCyclesBol(self, lista, x, y, compass, direction):
        turnLeftToAvoidCycle = False
        turnRightToAvoidCycle = False
        xCycle = 0
        yCycle = 0
        compassCycle = 0
        exist = False
        global add_Repeated_CoordinatesDone
        
        if direction == "Esquerda":
            for element in lista:
                subX = abs(round(element[0] - x,1))
                subY = abs(round(element[1] - y,1))
                #Robo passou numa direçao na horizontal da esquerda para a direita
                if subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and compass >= -30 and compass <= 30 and element[2] >= -30 and element[2] <= 30 and add_Repeated_CoordinatesDone == False:
                    #avoidCyclesComeFromLeft = avoidCyclesComeFromLeft + 1
                    #element[3] = avoidCyclesComeFromLeft    #MUDAR! para element[3] = element[3] + 1 em tds os elifs
                    element[3] = element[3] + 1
                    exist = True
                    add_Repeated_CoordinatesDone = True
                    break
                #Robo passou numa direçao na horizontal da direita para a esquerda
                elif subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and (compass <= -160 or compass >= 160) and (element[2] <= -160 or element[2] >= 160) and add_Repeated_CoordinatesDone == False:
                    #avoidCyclesComeFromRight = avoidCyclesComeFromRight + 1
                    #element[3] = avoidCyclesComeFromRight
                    #print("OLAAA")
                    element[3] = element[3] + 1
                    exist = True
                    add_Repeated_CoordinatesDone = True
                    break
                #Robo passou numa direçao na vertical de cima para baixo
                elif subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and compass >= -120 and compass <= -60 and element[2] >= -120 and element[2] <= -60 and add_Repeated_CoordinatesDone == False:
                    #avoidCyclesDown = avoidCyclesDown + 1
                    #element[3] = avoidCyclesDown
                    element[3] = element[3] + 1
                    exist = True
                    add_Repeated_CoordinatesDone = True
                    break
                #Robo passou numa direçao na vertical de baixo para cima
                elif subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and compass >= 60 and compass <= 120 and element[2] >= 60 and element[2] <= 120 and add_Repeated_CoordinatesDone == False:
                    #avoidCyclesUp = avoidCyclesUp + 1
                    #element[3] = avoidCyclesUp
                    element[3] = element[3] + 1
                    exist = True
                    add_Repeated_CoordinatesDone = True
                    break
                
                elif subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and compass >= -30 and compass <= 30 and element[2] >= 30 and element[2] <= 30 and add_Repeated_CoordinatesDone == True:
                    exist = True
                    break
                #Robo passou numa direçao na horizontal da direita para a esquerda
                elif subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and (compass <= -160 or compass >= 160) and (element[2] <= -160 or element[2] >= 160) and add_Repeated_CoordinatesDone == True:
                    exist = True
                    break
                #Robo passou numa direçao na vertical de cima para baixo
                elif subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and compass >= -120 and compass <= -60 and element[2] >= -120 and element[2] <= -60 and add_Repeated_CoordinatesDone == True:
                    exist = True
                    break
                #Robo passou numa direçao na vertical de baixo para cima
                elif subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and compass >= 60 and compass <= 120 and element[2] >= 60 and element[2] <= 120 and add_Repeated_CoordinatesDone == True:
                    exist = True
                    break
                
                elif (subX > 0.7 and subY >= 0 and subY <= 0.7) or (subY > 0.7 and subX >= 0 and subX <= 0.7) or (subX > 0.7 and subY > 0.7): #Não encontrou nenhuma coor nos intervalos anteriores
                    exist = False
                
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
			#print(element)
            #Ja passou 3 vezes por esse x e y, e atualmente o robo esta nesse x e y, entao vira direita
            if element[3] == 4 and subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and compass >= -30 and compass <= 30 and element[2] >= -30 and element[2] <= 30 and element[4] == "learningLeft" and element[5] == True: #esq para direita
                turnRightToAvoidCycle = True
                xCycle = element[0]
                yCycle = element[1]
                compassCycle = element[2]
                lista.remove([element[0], element[1], element[2], element[3], element[4], element[5]])
                
            elif element[3] == 5 and subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and compass >= -30 and compass <= 30 and element[2] >= -30 and element[2] <= 30 and element[4] == "turningRight" and element[5] == True: #esq para direita
                turnLeftToAvoidCycle = True
                xCycle = element[0]
                yCycle = element[1]
                compassCycle = element[2]
                lista.remove([element[0], element[1], element[2], element[3], element[4], element[5]])    
            
            elif element[3] == 5 and subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and (compass <= -160 or compass >= 160) and (element[2] <= -160 or element[2] >= 160) and element[4] == "learningLeft" and element[5] == True: #direita para esq
                turnRightToAvoidCycle = True
                xCycle = element[0]
                yCycle = element[1]
                compassCycle = element[2]
                lista.remove([element[0], element[1], element[2], element[3], element[4], element[5]])
                
            elif element[3] == 5 and subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and (compass <= -160 or compass >= 160) and (element[2] <= -160 or element[2] >= 160) and element[4] == "turningRight" and element[5] == True: #direita para esq
                turnLeftToAvoidCycle = True
                xCycle = element[0]
                yCycle = element[1]
                compassCycle = element[2]
                lista.remove([element[0], element[1], element[2], element[3], element[4], element[5]])
            
            elif element[3] == 5 and subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and compass >= -120 and compass <= -60 and element[2] >= -120 and element[2] <= -60 and element[4] == "learningLeft" and element[5] == True: #baixo
                turnRightToAvoidCycle = True
                xCycle = element[0]
                yCycle = element[1]
                compassCycle = element[2]
                lista.remove([element[0], element[1], element[2], element[3], element[4], element[5]])
                
            elif element[3] == 5 and subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and compass >= -120 and compass <= -60 and element[2] >= -120 and element[2] <= -60 and element[4] == "turningRight" and element[5] == True: #baixo
                turnLeftToAvoidCycle = True
                xCycle = element[0]
                yCycle = element[1]
                compassCycle = element[2]
                lista.remove([element[0], element[1], element[2], element[3], element[4], element[5]])
                
            elif element[3] == 5 and subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and compass >= 60 and compass <= 120 and element[2] >= 60 and element[2] <= 120 and element[4] == "learningLeft" and element[5] == True: #cima
                turnRightToAvoidCycle = True
                xCycle = element[0]
                yCycle = element[1]
                compassCycle = element[2]
                lista.remove([element[0], element[1], element[2], element[3], element[4], element[5]])
                
            elif element[3] == 5 and subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and compass >= 60 and compass <= 120 and element[2] >= 60 and element[2] <= 120 and element[4] == "turningRight" and element[5] == True: #cima
                turnLeftToAvoidCycle = True
                xCycle = element[0]
                yCycle = element[1]
                compassCycle = element[2]
                lista.remove([element[0], element[1], element[2], element[3], element[4], element[5]])
                
        return turnLeftToAvoidCycle, turnRightToAvoidCycle, xCycle, yCycle, compassCycle, exist
    
    def findCorrespondingCoor_For_ChangingTo_TurnRight(self, x, y, compass):
        already_in_the_list = False
        global coordinatesDone
        
        for element in coordinatesDone:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            if subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and compass >= -30 and compass <= 30 and element[2] >= -30 and element[2] <= 30 and (element[4] == 'learningLeft' or element[4] == 'turningRight') and element[5] == True:
                already_in_the_list = True
                element[3] = element[3] + 1
                element[4] = "turningRight"
                element[5] = True
                break
                
            elif subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and (compass <= -160 or compass >= 160) and (element[2] <= -160 or element[2] >= 160) and (element[4] == 'learningLeft' or element[4] == 'turningRight') and element[5] == True:
                already_in_the_list = True
                element[3] = element[3] + 1
                element[4] = "turningRight"
                element[5] = True
                break
                
            elif subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and compass >= -120 and compass <= -60 and element[2] >= -120 and element[2] <= -60 and (element[4] == 'learningLeft' or element[4] == 'turningRight') and element[5] == True:
                already_in_the_list = True
                element[3] = element[3] + 1
                element[4] = "turningRight"
                element[5] = True
                break
                
            elif subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7 and compass >= 60 and compass <= 120 and element[2] >= 60 and element[2] <= 120 and (element[4] == 'learningLeft' or element[4] == 'turningRight') and element[5] == True:
                already_in_the_list = True
                element[3] = element[3] + 1
                element[4] = "turningRight"
                element[5] = True
                break
            
            else:
                already_in_the_list = False

        return already_in_the_list
    
    def oppositeCompassButSameDirection(self, lista, x, y, compass, lastX, lastY, lastDirection, lastCompass, lastOppTurnRight, lastOppTurnLeft):
        oppositeCompassTurnRight = False
        opossiteCompassTurnLeft = False
        xRem = 1000
        yRem = 1000
        directionRem = ""
        compassRem = 0
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            if subX >= 0 and subX <= 0.8 and subY >= 0 and subY <= 0.8:	#Para umas dadas coordenadas encontrou uma direçao proxima
                #Direçao captada da esquerda para a direita, é uma "direita" e o robo vem no sentido contrário
                if element[3] >= -30 and element[3] <= 30 and element[2] == "direita" and (compass <= -152 or compass >= 150) and x >= element[0]:
                    opossiteCompassTurnLeft = True
                    oppositeCompassTurnRight = False
                    xRem = element[0]
                    yRem = element[1]
                    directionRem = element[2]
                    compassRem = element[3]
                #Direçao captada da esquerda para a direita, é uma "esquerda" e o robo vem no sentido contrário
                elif element[3] >= -30 and element[3] <= 30 and element[2] == "esquerda" and (compass <= -152 or compass >= 150) and x >= element[0]:
                    opossiteCompassTurnLeft = False
                    oppositeCompassTurnRight = True
                    xRem = element[0]
                    yRem = element[1]
                    directionRem = element[2]
                    compassRem = element[3]
                #Direçao captada da direita para a esquerda, é uma "esquerda" e o robo vem no sentido contrário
                elif (element[3] <= -150 or element[3] >= 152) and element[2] == "esquerda" and compass >= -30 and compass <= 30 and x <= element[0]:
                    opossiteCompassTurnLeft = False
                    oppositeCompassTurnRight = True
                    xRem = element[0]
                    yRem = element[1]
                    directionRem = element[2]
                    compassRem = element[3]
                #Direçao captada da direita para a esquerda, é uma "direita" e o robo vem no sentido contrário
                elif (element[3] <= -150 or element[3] >= 152) and element[2] == "direita" and compass >= -30 and compass <= 30 and x <= element[0]:
                    opossiteCompassTurnLeft = True
                    oppositeCompassTurnRight = False
                    xRem = element[0]
                    yRem = element[1]
                    directionRem = element[2]
                    compassRem = element[3]
                #Direçao captada de baixo para cima, é uma "direita" e o robo vem no sentido contrário
                elif element[3] >= 60 and element[3] <= 120 and element[2] == "direita" and compass >= -115 and compass <= -65 and y >= element[1]:
                    opossiteCompassTurnLeft = True
                    oppositeCompassTurnRight = False
                    xRem = element[0]
                    yRem = element[1]
                    directionRem = element[2]
                    compassRem = element[3]
                #Direçao captada de baixo para cima, é uma "esquerda" e o robo vem no sentido contrário
                elif element[3] >= 60 and element[3] <= 120 and element[2] == "esquerda" and compass >= -115 and compass <= -65 and y >= element[1]:
                    opossiteCompassTurnLeft = False
                    oppositeCompassTurnRight = True
                    xRem = element[0]
                    yRem = element[1]
                    directionRem = element[2]
                    compassRem = element[3]
                #Direçao captada de cima para baixo, é uma "esquerda" e o robo vem no sentido contrário
                elif element[3] >= -120 and element[3] <= -60 and element[2] == "esquerda" and compass >= 65 and compass <= 115 and y <= element[1]:
                    opossiteCompassTurnLeft = False
                    oppositeCompassTurnRight = True
                    xRem = element[0]
                    yRem = element[1]
                    directionRem = element[2]
                    compassRem = element[3]
                #Direçao captada de cima para baixo, é uma "direita" e o robo vem no sentido contrário
                elif element[3] >= -120 and element[3] <= -60 and element[2] == "direita" and compass >= 65 and compass <= 115 and y <= element[1]:
                    opossiteCompassTurnLeft = True
                    oppositeCompassTurnRight = False
                    xRem = element[0]
                    yRem = element[1]
                    directionRem = element[2]
                    compassRem = element[3]

                if lastX != 0 and lastY != 0 and lastDirection != "" and lastCompass != 0 and ((lastOppTurnRight == True and lastOppTurnLeft == False) or (lastOppTurnRight == False and lastOppTurnLeft == True)) and xRem == 0 and yRem == 0 and directionRem == "" and compassRem == 0 and opossiteCompassTurnLeft == False and oppositeCompassTurnRight == False:
                    xRem = lastX
                    yRem = lastY
                    directionRem = lastDirection
                    compassRem = lastCompass
                    opossiteCompassTurnLeft = lastOppTurnLeft
                    oppositeCompassTurnRight = lastOppTurnRight
        
        return opossiteCompassTurnLeft, oppositeCompassTurnRight, xRem, yRem, directionRem, compassRem
    
    def actualCoordinatesAreACycle(self, lista, x, y, compass):
        theyAreACycle_Left = False
        theyAreACycle_Right = False
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            #if x == element[0] and y == element[1] and compass >= -20 and compass <= 20 and element[2] >= -20 and element[2] <= 20     #ANTES
            if subX >= 0 and subX <= 0.5 and subY >= 0 and subY <= 0.5 and compass >= -20 and compass <= 20 and element[2] >= -20 and element[2] <= 20 and element[3] == "Left": #esq para direita
               theyAreACycle_Left = True
               
            elif subX >= 0 and subX <= 0.5 and subY >= 0 and subY <= 0.5 and compass >= -20 and compass <= 20 and element[2] >= -20 and element[2] <= 20 and element[3] == "Right": #esq para direita
               theyAreACycle_Right = True
               
            elif subX >= 0 and subX <= 0.5 and subY >= 0 and subY <= 0.5 and compass >= 70 and compass <= 110 and element[2] >= 70 and element[2] <= 110 and element[3] == "Left": #baixo para cima
                theyAreACycle_Left = True
                
            elif subX >= 0 and subX <= 0.5 and subY >= 0 and subY <= 0.5 and compass >= 70 and compass <= 110 and element[2] >= 70 and element[2] <= 110 and element[3] == "Right": #baixo para cima
                theyAreACycle_Right = True
            
            elif subX >= 0 and subX <= 0.5 and subY >= 0 and subY <= 0.5 and compass >= -110 and compass <= -70 and element[2] >= -110 and element[2] <= -70 and element[3] == "Left": #cima para baixo
                theyAreACycle_Left = True
            
            elif subX >= 0 and subX <= 0.5 and subY >= 0 and subY <= 0.5 and compass >= -110 and compass <= -70 and element[2] >= -110 and element[2] <= -70 and element[3] == "Right": #cima para baixo
                theyAreACycle_Right = True    
            
            elif subX >= 0 and subX <= 0.5 and subY >= 0 and subY <= 0.5 and (compass <= -160 or compass >= 160) and (element[2] <= -160 or element[2] >= 160) and element[3] == "Left":   #direita para esq
                theyAreACycle_Left = True
                
            elif subX >= 0 and subX <= 0.5 and subY >= 0 and subY <= 0.5 and (compass <= -160 or compass >= 160) and (element[2] <= -160 or element[2] >= 160) and element[3] == "Right":   #direita para esq
                theyAreACycle_Right = True
                
        return theyAreACycle_Left, theyAreACycle_Right
    
    def dijsktra(self, graph, initial, end):
        # shortest paths is a dict of nodes
        # whose value is a tuple of (previous node, weight)
        shortest_paths = {initial: (None, 0)}
        current_node = initial
        visited = set()
        
        while current_node != end:
            visited.add(current_node)
            destinations = graph.edges[current_node]
            weight_to_current_node = shortest_paths[current_node][1]

            for next_node in destinations:
                weight = graph.weights[(current_node, next_node)] + weight_to_current_node
                if next_node not in shortest_paths:
                    shortest_paths[next_node] = (current_node, weight)
                else:
                    current_shortest_weight = shortest_paths[next_node][1]
                    if current_shortest_weight > weight:
                        shortest_paths[next_node] = (current_node, weight)
            
            next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
            if not next_destinations:
                return "Route Not Possible"
            # next node is the destination with the lowest weight
            current_node = min(next_destinations, key=lambda k: next_destinations[k][1])
        
        # Work back through destinations in shortest path
        path = []
        while current_node is not None:
            path.append(current_node)
            next_node = shortest_paths[current_node][0]
            current_node = next_node
        # Reverse path
        path = path[::-1]
        return path
    
    def checkIfNodeAlreadyInList(self, nodes, node):
        isAlreadyIn = False
        for element in nodes:
            pathAoContrarioDoNoDaLista = element[2][::-1]	#Inverter o path q esta na lista dos nós para ver se o path do nó q vamos inserir é o inverso, se for significa q é o msm caminho, apesar de ser inverso
            if (node[1] == element[1] and node[0] == element[0] and node [2] == element[2] and node[5] == element[5]) or (node[1] == element[0] and node[0] == element[1] and node[2] == pathAoContrarioDoNoDaLista):
                isAlreadyIn = True
        return isAlreadyIn
    
    def findCell(self, list_Nodes,vertex):
        cell = ()
        for node in list_Nodes:
            current_vertex = node[0]
            if current_vertex == vertex:
                cell = node[5]
                break
        return cell
    
    def findVertex(self, list_nodes, cell):
        vertex = ''
        for node in list_nodes:
            current_cell = node[5]
            if current_cell == cell:
                vertex = node[0]
                break
        return vertex
    
    def findCells_of_path2IVertex(self, path_To_IVertex, list_Nodes):
        cells = []
        for vertex in path_To_IVertex:
            cell = self.findCell(list_Nodes, vertex)
            cells.append([vertex, cell])
        return cells
    
    def find_if_Cell_Belong_toPath_toInitial(self, cells, actual_cell):
        belong = False
        for element in cells:
            if actual_cell == element[1]:
                belong = True
                break
        return belong
    
    def find_if_cell_isNode(self, listNodes, actual_cell):
        isANode = False
        for element in listNodes:
            if actual_cell == element[5]:
                isANode = True
        print("IS A NODE->", isANode)
        return isANode
        
    #Para chamar esta função temos de ter 1's
    def Choose_Direction_To_Start(self, path2_InitialVertex, matrizX, matrizY, bussola, lineSensor, sensorLeft, sensorRight):
        #Escolher a direção de acordo com o path para o vértice inicial
        rotate = False
        turnL = False
        turnR = False
        go_foward = False
        global find_cell, exact_cell, adjacent_cell, done_decisionDir_For_That_vertex, number_times_throw_nodes_toStart
        #print("INSIDE FUN BEFORE exact_cell->", exact_cell)
        #print("INSIDE FUN BEFORE adjacent_cell", adjacent_cell)
        
        #print("find_cell BEFORE:", find_cell)
        
        #FIND CELL NAO ESTÁ A FICAR A FALSE!!!
        
        #if find_cell == False:
        for i in range(len(path2_InitialVertex)-1, -1, -1):		
            if path2_InitialVertex[i][1] == (matrizX,matrizY):
                #exact_cell_bool = True
                exact_cell = path2_InitialVertex[i][1]
                adjacent_cell = path2_InitialVertex[i-1][1]
                find_cell = True
                break
                
        #print("find_cell AFTER:", find_cell)
        
        #Vamos ver qual a direção q o robo tem de tomar nesta célula, de acordo com o adjacente a esta célula, para chegar ao inicio
        if adjacent_cell[1] > exact_cell[1] and 60 <= bussola <= 120 and number_times_throw_nodes_toStart == 0:	#Ir para cima	
            rotate = True
            number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
            #done_decisionDir_For_That_vertex = True
            
        elif adjacent_cell[1] > exact_cell[1] and 60 <= bussola <= 120 and number_times_throw_nodes_toStart >= 1: #Está a ir para cima e a celula adjacente é para baixo mas não é o primeiro nó visitiado
            #Vamos ver o X
            if adjacent_cell[0] < exact_cell[0] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorLeft == ['1','1']):   
                turnL = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            elif adjacent_cell[0] > exact_cell[0] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorRight == ['1','1']):
                turnR = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            #Se não for nenhuma destas duas é pq o x é igual então não vira e continua a seguir em frente
            else:
                go_foward = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            
        elif adjacent_cell[1] <= exact_cell[1] and 60 <= bussola <= 120: #Ir para cima
            #Vamos ver o X
            if adjacent_cell[0] < exact_cell[0] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorLeft == ['1','1']):   
                turnL = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            elif adjacent_cell[0] > exact_cell[0] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorRight == ['1','1']):
                turnR = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            #Se não for nenhuma destas duas é pq o x é igual então não vira e continua a seguir em frente
            else:
                go_foward = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            
        elif adjacent_cell[1] < exact_cell[1] and -120 <= bussola <= -60 and number_times_throw_nodes_toStart == 0: #Ir para baixo
            rotate = True
            number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
            #done_decisionDir_For_That_vertex = True
            
        elif adjacent_cell[1] < exact_cell[1] and -120 <= bussola <= -60 and number_times_throw_nodes_toStart >= 1: #Está a ir para baixo e a celula adjacente é para cima mas não é o primeiro nó visitiado
            if adjacent_cell[0] < exact_cell[0] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorRight == ['1','1']):   
                turnR = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            elif adjacent_cell[0] > exact_cell[0] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorLeft == ['1','1']):
                turnL = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            #Se não for nenhuma destas duas é pq o x é igual então não vira e continua a seguir em frente
            else:
                go_foward = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            
        elif adjacent_cell[1] > exact_cell[1] and -120 <= bussola <= -60: #Ir para baixo
            if adjacent_cell[0] < exact_cell[0] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorRight == ['1','1']):   
                turnR = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            elif adjacent_cell[0] > exact_cell[0] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorLeft == ['1','1']):
                turnL = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            #Se não for nenhuma destas duas é pq o x é igual então não vira e continua a seguir em frente
            else:
                go_foward = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            
        elif adjacent_cell[0] < exact_cell[0] and -40 <= bussola <= 40 and number_times_throw_nodes_toStart == 0: #ir para a direita
            rotate = True
            number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
            #done_decisionDir_For_That_vertex = True
            
        elif adjacent_cell[0] < exact_cell[0] and -40 <= bussola <= 40 and number_times_throw_nodes_toStart >= 1: #Ir para a direita e o adjacente está atrás dele mas não o primeiro nó visitado
            if adjacent_cell[1] > exact_cell[1] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorRight == ['1','1']):   
                turnR = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            elif adjacent_cell[1] < exact_cell[1] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorLeft == ['1','1']):
                turnL = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            #Se não for nenhuma destas duas é pq o x é igual então não vira e continua a seguir em frente
            else:
                go_foward = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            
        elif adjacent_cell[0] > exact_cell[0] and -40 <= bussola <= 40: #ir para a direita
            if adjacent_cell[1] > exact_cell[1] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorRight == ['1','1']):   
                turnR = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            elif adjacent_cell[1] < exact_cell[1] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorLeft == ['1','1']):
                turnL = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            #Se não for nenhuma destas duas é pq o x é igual então não vira e continua a seguir em frente
            else:
                go_foward = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            
        elif adjacent_cell[0] > exact_cell[0] and (bussola >= 140 or bussola <= -140) and number_times_throw_nodes_toStart == 0: #ir para a esquerda
            rotate = True
            number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
            #done_decisionDir_For_That_vertex = True
            
        elif adjacent_cell[0] > exact_cell[0] and (bussola >= 140 or bussola <= -140) and number_times_throw_nodes_toStart >= 1: #Ir para a esquerda e o adjacente está atrás dele mas não o primeiro nó visitado
            if adjacent_cell[1] > exact_cell[1] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorLeft == ['1','1']):   
                turnL = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            elif adjacent_cell[1] < exact_cell[1] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorRight == ['1','1']):
                turnR = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            #Se não for nenhuma destas duas é pq o x é igual então não vira e continua a seguir em frente
            else:
                go_foward = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            
        elif adjacent_cell[0] < exact_cell[0] and (bussola >= 140 or bussola <= -140): #ir para a esquerda
            if adjacent_cell[1] > exact_cell[1] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorLeft == ['1','1']):   
                turnL = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            elif adjacent_cell[1] < exact_cell[1] and (lineSensor == ['1','1','1','1','1','1','1'] or sensorRight == ['1','1']):
                turnR = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
            #Se não for nenhuma destas duas é pq o x é igual então não vira e continua a seguir em frente
            else:
                go_foward = True
                number_times_throw_nodes_toStart = number_times_throw_nodes_toStart + 1
                #done_decisionDir_For_That_vertex = True
                            
        return rotate, turnL, turnR, go_foward
    
    def check_if_turned_toMuch(self, compass):
        turned_To_Much = False
        global first_time_compass_value, counter_valueCompass
        
        if counter_valueCompass == 0:   #Entra aqui uma vez, ou seja, para saber a bussola no instante imediatamente antes qnd o robo começou a virar
            first_time_compass_value = compass
            counter_valueCompass = counter_valueCompass + 1
        
        compassDifference = 0 #Inicializar
        if (-10 < first_time_compass_value < 10) or (80 < first_time_compass_value < 100) or (-100 < first_time_compass_value < -80): #Não está a ir para a esquerda
            compassDifference = abs(round(first_time_compass_value - compass,1))
        else:
            if first_time_compass_value > 0 and compass > 0:	#Está para a direita, e compass é um número positivo
                compassDifference = abs(round(first_time_compass_value - compass,1))
            elif first_time_compass_value > 0 and compass < 0: ##Está para a direita, e compass é um número negativo
                compassDifference = round(first_time_compass_value + compass,1)
            elif first_time_compass_value < 0 and compass < 0: #Está para a esquerda, e compass é um número negativo
                compassDifference = abs(round(first_time_compass_value - compass,1))
            elif  first_time_compass_value < 0 and compass > 0: #Está para a esquerda, e compass é um número positivo
                compassDifference = abs(round(first_time_compass_value + compass,1))   
        
        if compassDifference >= 57:
            turned_To_Much = True    
        
        return turned_To_Much
    
    def calculate_adjacent(self, pathToNode):
        adjacent = -1
        for i in range(0,len(nodes)):
            caminhoNoVertice = nodes[i][5]

            if pathToNode != []:
                firstCellPathToNodeColx = pathToNode[0][0] #30
                firstCellPathToNodeColy = pathToNode[0][1] #9
                actualPosCell = pathToNode[-1]
            
            possibleCell1 = (firstCellPathToNodeColx + 1, firstCellPathToNodeColy) #31,9, andar um para a direita	
            possibleCell2 = (firstCellPathToNodeColx, firstCellPathToNodeColy + 1) #30, 10 andar 1 para baixo
            possibleCell3 = (firstCellPathToNodeColx - 1, firstCellPathToNodeColy) #29,9 andar um para a esquerda
            possibleCell4 = (firstCellPathToNodeColx, firstCellPathToNodeColy - 1) #30,8 andar um para cima
                            
            if caminhoNoVertice == possibleCell1 and possibleCell1 != actualPosCell:
                adjacent = nodes[i][0]
                break
            elif caminhoNoVertice == possibleCell2 and possibleCell2 != actualPosCell:
                adjacent = nodes[i][0]
                break
            elif caminhoNoVertice == possibleCell3 and possibleCell3 != actualPosCell:
                adjacent = nodes[i][0]
                break
            elif caminhoNoVertice == possibleCell4 and possibleCell4 != actualPosCell:
                adjacent = nodes[i][0]
                break
            
        return adjacent
    
    def findCostFor2Vertex(self, STPpathVertex, nodes):
        custo = 0
        custosForThisVertex = []
        finalPathAux = []
        
        for i in range(0,len(STPpathVertex)):
            if i < (len(STPpathVertex)-1):
                for node in nodes:	#buscar os custos do beacon inicial aos outros beacons
                    if STPpathVertex[i+1] == node[0] and STPpathVertex[i] == node[1]:
                        custosForThisVertex.append(node[2])
                    elif STPpathVertex[i] == node[0] and STPpathVertex[i+1] == node[1]:
                        custosForThisVertex.append(node[2][::-1])
                
                if len(custosForThisVertex) == 1:
                    finalPathAux.append(custosForThisVertex[0])
                elif len(custosForThisVertex) > 1:
                    finalPathAux.append(min(custosForThisVertex, key=lambda coll: len(coll)))
                    
                for element in finalPathAux:
                    custo = custo + len(element)
                    
                custosForThisVertex = []
                finalPathAux = []
        return custo
    
    def calculateMinPathVertex(self, beaconsLeft, initialBeacon, beaconMinPathToIB, listaAuxiliarPath, graph, nodes):
        #Funçao q calcula o melhor caminho, consoante os vertices, para os restantes beacons, sem ser o inicial e o beacon com melhor caminho até ao inicial
        #beaconsLeftAux = beaconsLeft    #lista dos beacons
        beaconsLeftAux = []
        custosForThisVertexANDInicialVertex = []
        nextBeacon = -1
       
        for element in beaconsLeft:
            if element[0] != initialBeacon and element[0] != beaconMinPathToIB:
                beaconsLeftAux.append(element)
                   
        if len(beaconsLeftAux) == 1:    #No caso de haver 3 beacons
            listaAuxiliarPath = listaAuxiliarPath + self.dijsktra(graph, beaconMinPathToIB, beaconsLeftAux[0][0]) #por exemplo 11 para o 10
            listaAuxiliarPath = listaAuxiliarPath + self.dijsktra(graph, beaconsLeftAux[0][0], initialBeacon)   #e dps do 10 para o inicial (1)
            
        else:   #Caso haja mais do que 3 beacons
            print("ESTOU NO ELSE")
            while len(beaconsLeftAux) > 1:
            #Percorre tds os beacons exceto o inicial e o outro mais perto do inicial, ou seja, q tem caminho minimo
                for element in beaconsLeftAux:  #[('8', '7', 2),///// ('10', '9', 26),(//////////////'12', '23', 6)]
                    custo = 0
                    pathVertexForThisCombination = []
                    pathVertexForThisCombination = self.dijsktra(graph, beaconMinPathToIB, element[0])
                    custo = self.findCostFor2Vertex(pathVertexForThisCombination, nodes)
                    custosForThisVertexANDInicialVertex.append([beaconMinPathToIB, element[0], custo])
                
                custos = []    
                for element in custosForThisVertexANDInicialVertex: #[('11', '8', 7), ('11', '10', 4), ///////('11', '12', 10)]
                    custos.append(element[2])
                min_value = min(custos)
                min_index = custos.index(min_value)
                nextBeacon = custosForThisVertexANDInicialVertex[min_index][1]
                listaAuxiliarPath = listaAuxiliarPath + self.dijsktra(graph, custosForThisVertexANDInicialVertex[min_index][0], custosForThisVertexANDInicialVertex[min_index][1]) #11, 10

                for element in beaconsLeftAux:
                    if element[0] == nextBeacon:
                        beaconsLeftAux.remove(element)  #Remover o beacon com o caminho minimo já calculado
                        
                custosForThisVertexANDInicialVertex = [] #clear à lista
            
            listaAuxiliarPath = listaAuxiliarPath + self.dijsktra(graph, nextBeacon, beaconsLeftAux[0][0]) #caminho do beacon do next beacon para o beacon q sobra na lista
            listaAuxiliarPath = listaAuxiliarPath + self.dijsktra(graph, beaconsLeftAux[0][0], initialBeacon) #e caminho desse beacon para o beacon inicial
            
               
        return listaAuxiliarPath

    def run(self):
        global knowing, learningLeft, turningLeft,turningRight, possibleDirections, checkCompassRem, direction, itsACross, frente, directionRemCross, compassRemCross, waitABit, addTolist, checkXrem, checkYrem, waitAddToList, startCounting, removedDirections, coordinatesDone, doneCross, xRemCross, yRemCross,matrixxinicial,matrixyinicial,aux,aux2,prev_dir,prev_char,dir,xinicial,yinicial,alreadysubtracted,alreadyground,contadorteste,matrixxinicial2,matrixyinicial2, alreadyUpdatedAdjacenInicialvertex, contadorteste2
        global notDoneLetsTurnR_PD, dontAddRightDir_PD, notDoneLetsTurnR_RD, dontAddRightDir_RD, maybeDeadEnd, contador, haveONEs, checkDiff, checkDirection
        global oppositeCompassTurnLeft, oppositeCompassTurnRight, oppositeCompassX, oppositeCompassY, oppositeCompassDirection, oppositeCompassCompass
        global isACycle, isACycle_Right, xVarCycle, yVarCycle, compassVarCycle
        global coordinatesCycle
        global DirectionsAndTargets
        global directionsAndTargetsMatrix, numberNodes, nodes, pathToNode, cost, alreadyInListDirecitonsAndTargets, clearListPath, lastElementBeforeClear, edges, zero, resetPathToNode, beacons
        global inicialCols, inicialLines
        global finalPathAux, finalPath, bestPathVertex, sptHasBeenCalculated, finalPathFile, custosForThisVertexANDInicialVertex
        global time, turnAround, already_in_turnAround_Condition, bussola_turnAround
        global last_outL, last_outR, outL, outR, lastX, lastY, lastTeta, x, y, teta, closestPairXandY, auxXInicial, auxYInicial
        global alreadyCorrect, add_Repeated_CoordinatesDone, already_addCoordinatesDone, already_SeeIfNeed_To_ChangeTo_TurnRight
        global intersection
        global find_cell, exact_cell, adjacent_cell, done_decisionDir_For_That_vertex, rotate_mapEnded, turnL_mapEnded, turnR_mapEnded, go_foward_mapEnded, mapEnded
        global inicialCell, graph_has_been_calculated, graph, cells_To_Start_hasBeen_Calculated, cells, number_times_throw_nodes_toStart, going_foward, stopTurning_LeftOrRight
        global first_time_compass_value, counter_valueCompass, rotate_slowly_going_foward, direction_Right, direction_Left, dontDoNothing_goFoward, checkDiff_and_oppositeCompassSameDir_HasBeenCalculated
        global already_in_the_list
        #Combater o Ruido
        global valueCompass_First_Time_turningRight, valueCompass_First_Time_turningLeft, first_time_Compass_alreadyHaveValue
        already_SeeIfNeed_To_ChangeTo_TurnRight = False
        already_in_the_list = False
        stopTurning_LeftOrRight = False
        first_time_Compass_alreadyHaveValue = 0
        valueCompass_First_Time_turningRight = 0
        valueCompass_First_Time_turningLeft = 0
        checkDiff_and_oppositeCompassSameDir_HasBeenCalculated = False
        dontDoNothing_goFoward = False
        direction_Right = False
        direction_Left = False
        rotate_slowly_going_foward = False
        first_time_compass_value = 0
        counter_valueCompass = 0
        going_foward = False
        number_times_throw_nodes_toStart = 0
        cells = []
        cells_To_Start_hasBeen_Calculated = False
        graph = Graph()
        graph_has_been_calculated = False
        inicialCell = ()
        mapEnded = False
        rotate_mapEnded = False
        turnL_mapEnded = False
        turnR_mapEnded = False
        go_foward_mapEnded = False
        done_decisionDir_For_That_vertex = False
        find_cell = False
        exact_cell = []
        adjacent_cell = []
        intersection = False
        add_Repeated_CoordinatesDone = False
        already_addCoordinatesDone = False
        alreadyCorrect = False
        auxXInicial = 0
        auxYInicial = 0
        last_outL = 0
        last_outR = 0
        outL = 0
        outR = 0
        lastX = 0
        lastY = 0
        lastTeta = 0
        x = 0
        y = 0
        teta = 0
        closestPairXandY = 0
        bussola_turnAround = 0
        already_in_turnAround_Condition = False
        turnAround = False
        time = -1
        custosForThisVertexANDInicialVertex = []
        finalPathFile = []
        sptHasBeenCalculated = False
        bestPathVertex = []
        finalPathAux = []
        finalPath = []
        resetPathToNode = False
        zero = 0
        edges = []
        beacons = []
        inicialCols = 0
        inicialLines = 0
        lastElementBeforeClear = 0
        clearListPath = False
        alreadyInListDirecitonsAndTargets = False
        cost = 0
        pathToNode = []
        numberNodes = 1
        nodes = []
        DirectionsAndTargets = []
        directionsAndTargetsMatrix = []     
        oppositeCompassTurnLeft = False
        oppositeCompassTurnRight = False
        oppositeCompassX = 0
        oppositeCompassY = 0
        oppositeCompassDirection = 0
        oppositeCompassCompass = 0
        knowing = False 
        learningLeft = False
        turningLeft = False
        turningRight = False
        possibleDirections = []
        removedDirections = []
        coordinatesCycle = []
        checkCompassRem = 0    #era o xinicial
        #era o findValue
        direction = ""
        itsACross = False
        frente = False
        directionRemCross = ""  #era o xRemove
        compassRemCross = 0     #era o yRemove
        waitABit = 0
        addTolist = False
        checkXrem = 1000
        checkYrem = 1000
        checkDiff = False       #Podera eliminar-se
        checkDirection = ""
        waitAddToList = 0
        startCounting = False
        coordinatesDone = [] #sinaliza as coordenadas pelas quais ja passou nos cruzamentos/entroncamentos
        doneCross = False
        xRemCross = 0
        yRemCross = 0
        notDoneLetsTurnR_PD = False
        dontAddRightDir_PD = False
        notDoneLetsTurnR_RD = False
        dontAddRightDir_RD = False
        maybeDeadEnd = False   ##
        contador = 0
        haveONEs = False
        isACycle = False
        isACycle_Right = False
        xVarCycle = 0
        yVarCycle = 0
        compassVarCycle = 0

        self.matrix = [[' ' for x in range(49)] for y in range(21)] #matriz
        matrixxinicial2 = 10
        matrixyinicial2 = 24
        matrixxinicial = 0
        matrixyinicial = 0
        self.readSensors()
        prev_char = " "
        prev_dir = " "

        if self.measures.time == 0:     #Coordenadas da posição inicial
            xinicial = round(x,1)
            yinicial = round(y,1)

        aux = round(xinicial,1)
        aux2= round(yinicial,1)
        dir = "R"
        contadorteste = 0
        contadorteste2= 0
        alreadysubtracted = False
        alreadyground = False
        alreadyUpdatedAdjacenInicialvertex = False
        
        if self.status != 0:
            print("Connection refused or error")
            quit()

        state = 'stop'
        stopped_state = 'run'

        

        while True:
            self.readSensors()

            if self.measures.endLed:
                print(self.rob_name + " exiting")
                quit()

            if state == 'stop' and self.measures.start:
                state = stopped_state

            if state != 'stop' and self.measures.stop:
                stopped_state = state
                state = 'stop'

            if state == 'run':
                if self.measures.visitingLed==True:
                    state='wait'
                if self.measures.ground==0:
                    self.setVisitingLed(True)
                self.wander()
            elif state=='wait':
                self.setReturningLed(True)
                if self.measures.visitingLed==True:
                    self.setVisitingLed(False)
                if self.measures.returningLed==True:
                    state='return'
                self.driveMotors(0.0,0.0)
            elif state=='return':
                if self.measures.visitingLed==True:
                    self.setVisitingLed(False)
                if self.measures.returningLed==True:
                    self.setReturningLed(False)
                self.wander()        

    def wander(self):
        #Variaveis globais
        global knowing, checkCompassRem, direction, itsACross, waitABit, checkXrem, checkYrem, waitAddToList, doneCross, xRemCross, yRemCross, notDoneLetsTurnR_PD, dontAddRightDir_PD, notDoneLetsTurnR_RD, dontAddRightDir_RD, xVarCycle, yVarCycle, coordinatesCycle,matrixxinicial,matrixyinicial,aux,aux2,prev_dir,prev_char,dir,xinicial,yinicial,alreadysubtracted,alreadyground,contadorteste,matrixxinicial2,matrixyinicial2, alreadyUpdatedAdjacenInicialvertex,contadorteste2
        global possibleDirections,removedDirections,coordinatesDone   #Possiveis direçoes para cada posição do entroncamento/ direçoes eliminadas apos terem sido feitas/ coordenadas feitas
        global learningLeft, turningLeft, turningRight, frente, directionRemCross, compassRemCross, addTolist, startCounting, maybeDeadEnd, contador, haveONEs, checkDiff, checkDirection, isACycle, isACycle_Right, compassVarCycle
        global oppositeCompassTurnLeft, oppositeCompassTurnRight, oppositeCompassX, oppositeCompassY, oppositeCompassDirection, oppositeCompassCompass
        global DirectionsAndTargets, directionsAndTargetsMatrix, numberNodes, nodes, pathToNode, cost, alreadyInListDirecitonsAndTargets, clearListPath,lastElementBeforeClear, edges, resetPathToNode, beacons
        global inicialCols, inicialLines, zero
        global finalPathAux, finalPath, bestPathVertex, sptHasBeenCalculated, finalPathFile, custosForThisVertexANDInicialVertex
        global time, turnAround, already_in_turnAround_Condition, bussola_turnAround, add_Repeated_CoordinatesDone, already_addCoordinatesDone, already_SeeIfNeed_To_ChangeTo_TurnRight
        global last_outL, last_outR, outL, outR, lastX, lastY, lastTeta, x, y, teta, closestPairXandY, auxXInicial, auxYInicial, alreadyCorrect, intersection
        global find_cell, exact_cell, adjacent_cell, done_decisionDir_For_That_vertex, rotate_mapEnded, turnL_mapEnded, turnR_mapEnded, go_foward_mapEnded, mapEnded
        global inicialCell, graph_has_been_calculated, graph, cells_To_Start_hasBeen_Calculated, cells, number_times_throw_nodes_toStart, going_foward, stopTurning_LeftOrRight
        global first_time_compass_value, counter_valueCompass, rotate_slowly_going_foward, direction_Right, direction_Left, dontDoNothing_goFoward, checkDiff_and_oppositeCompassSameDir_HasBeenCalculated
        global already_in_the_list
        #Combater o Ruido
        global valueCompass_First_Time_turningRight, valueCompass_First_Time_turningLeft, first_time_Compass_alreadyHaveValue
        
        pathAndAdjacenciasForThisVertix = []
        #pathAdjacencias = []
        #pathForThisVertex = []
        actualPosCell = []
        firstCellPathToNodeColx = 0
        firstCellPathToNodeColy = 0
        adjacente = 0
        posNodeInList = -1    #Variavel q serve para verificar se um nó tem mais do que um caminho, ou seja, adiciona à lista de nos o id desse nó e não outro id
        done = False
        xDone = 0
        yDone = 0
        directionDone = ""
        compassDone = 0
        alreadyExist = False
        coordinateIsACycle_turnLeft = False
        coordinateIsACycle_turnRight = False
        
        center_id = 0
        left_id = 1
        right_id = 2
        back_id = 3
        if    self.measures.irSensor[center_id] > 5.0\
           or self.measures.irSensor[left_id]   > 5.0\
           or self.measures.irSensor[right_id]  > 5.0\
           or self.measures.irSensor[back_id]   > 5.0:
            print('Rotate left')
            self.driveMotors(-0.1,+0.1)
        elif self.measures.irSensor[left_id]> 2.7:
            print('Rotate slowly right')
            self.driveMotors(0.1,0.0)
        elif self.measures.irSensor[right_id]> 2.7:
            print('Rotate slowly left')
            self.driveMotors(0.0,0.1)
        else:
            print('Go')
            self.driveMotors(0.1,0.1)
        
        lineThrowRobot = self.measures.lineSensor[2:5]
        pathLeft = self.measures.lineSensor[:1]
        pathRight = self.measures.lineSensor[6:]
        sensorLeft = self.measures.lineSensor[:2]
        sensorRight = self.measures.lineSensor[5:]  
        print(self.measures.lineSensor)
        
        #Testar a correçao do valor de x e y
        print("Bussola->",self.measures.compass)
        print("self_measures_X", self.measures.x)
        print("self_measures_Y", self.measures.y)
        if self.measures.time == 0:
            auxXInicial = round(x,1)
            auxYInicial = round(y,1)
        print("X_measures->", self.measures.x - auxXInicial)
        print("Y_measures->", self.measures.y - auxYInicial)
        
        print("X->", x)
        print("Y->", y)

        contadorteste = -y
        matrixxinicial = matrixxinicial2 + int(round(contadorteste,0))
        matrixyinicial = matrixyinicial2 + + int(round(x,0))
        
        #Centrar o robo
        if ((lineThrowRobot == ['0','1','1'] or lineThrowRobot == ['0','0','1'])  and pathLeft != ['1'] and pathRight != ['1']) and go_foward_mapEnded == False:
            print('Rotate slowly right')
            self.driveMotors(0.08,0.03) #0.15, 0.06
            
            outL, outR = self.updateDriveMotors(last_outL, 0.08, last_outR, 0.03)
            print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
            
        elif ((lineThrowRobot == ['1','1','0'] or lineThrowRobot == ['1','0','0']) and pathRight != ['1'] and pathLeft != ['1']) and go_foward_mapEnded == False:
            print('Rotate slowly left')
            self.driveMotors(0.03,0.8) #0.06, 0.15
            
            outL, outR = self.updateDriveMotors(last_outL, 0.03, last_outR, 0.15)
            print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
            
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
            
        #Fazer tb qnd os lineThrowRobot == ['1','1','1']
        elif (lineThrowRobot == ['1','1','1'] and pathRight != ['1'] and pathLeft != ['1']) or go_foward_mapEnded == True:
            self.driveMotors(0.1,0.1)
            
            outL, outR = self.updateDriveMotors(last_outL, 0.1, last_outR, 0.1)
            print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
            
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
              
              
        if pathLeft == ['1'] or pathRight == ['1']: #Encontrou 1's
            #maybeDeadEnd = False 
            haveONEs = True 
        
        if sensorLeft == ['1', '1'] or sensorRight == ['1','1']:
            intersection = True
            
        print("INTERSECTION-->", intersection)
            
        if self.measures.lineSensor == ['0','0','1','1','1','0','0'] or self.measures.lineSensor == ['0','0','1','1','0','0','0'] or self.measures.lineSensor == ['0','0','0','1','1','0','0'] or self.measures.lineSensor == ['0','1','1','1','0','0','0'] or self.measures.lineSensor == ['0','0','0','1','1','1','0']:
            maybeDeadEnd = False
        
        
        if self.measures.lineSensor == ['0','0','0','0','0','0','0'] and haveONEs == True and mapEnded == False: #and haveONEs == True
            #Marcha atrás
            print("MARCHA-ATRASS")
            self.driveMotors(-0.1,-0.1) # (-0.1)eventualmente diminuir menos
            
            #Se isso faz marcha-atras bue vezes o X vai sempre diminuindo
            
            # outL, outR = self.updateDriveMotors(last_outL, -0.1, last_outR, -0.1)
            # print("(", outL, ", ", outR ,")")
            # x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
            
            # print("(", x,", ", y, ", ", (teta*180)/pi,")")
            
            startCounting = False
            waitAddToList = 0
            addTolist = False   #Caso ele esteja a true volta a False, pq se nao fizermos isto ele vai ficar a true pq o waitAddTolist so conta se o startCounting for verdadeiro
            dontDoNothing_goFoward = False
            #maybeDeadEnd = False
                
        elif self.measures.lineSensor == ['0','0','0','0','0','0','0'] and haveONEs == False and mapEnded == False:
            #self.driveMotors(-0.1,-0.1)
            maybeDeadEnd = True

        elif self.measures.lineSensor == ['0','0','0','0','0','0','0'] and haveONEs == True and mapEnded == True:

            print("MARCHA-ATRASS")
            self.driveMotors(-0.1,-0.1)

            rotate_mapEnded = rotate_mapEnded
            turnL_mapEnded = turnL_mapEnded
            turnR_mapEnded = turnR_mapEnded
            go_foward_mapEnded = go_foward_mapEnded

        
        #print("haveOnes->", haveONEs)
        #print("maybeDeadEnd->", maybeDeadEnd) 
        #print("contador->", contador) 
        if maybeDeadEnd == True or rotate_mapEnded == True:
            contador = contador + 1 
            if contador < 20: #horizontal na direita
                self.driveMotors(-0.15,+1)  #Virar À esquerda
                
                outL, outR = self.updateDriveMotors(last_outL, -0.15, last_outR, 0.15)
                #print("(", outL, ", ", outR ,")")
                x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
                
                print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
                 
                #Virar até ficar ao contrario
                print("ITS A DEAD-END, TURN LEFT")
            elif contador == 20:
                contador = 0
                self.driveMotors(0.1,0.1)
                
                outL, outR = self.updateDriveMotors(last_outL, 0.1, last_outR, 0.1)
                #print("(", outL, ", ", outR ,")")
                x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
                
                print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
            
        
        #PODERA ELIMINAR-SE ESTE IF
        if self.measures.time == 0 and self.measures.time == 1:    
            self.driveMotors(0.15, 0.15) #Acelarar no inicio para evitar q o proximo ciclo continue na posição inicial
            
            outL, outR = self.updateDriveMotors(last_outL, 0.15, last_outR, 0.15)
            #print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
                
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
        
            
        doneCross, xRemCross, yRemCross, directionRemCross, compassRemCross = self.coordinatesDoneInCross(possibleDirections, round(x,1), round(y,1), self.measures.compass, itsACross)
        if doneCross == True and addTolist == False:
            self.removeElement(possibleDirections, xRemCross, yRemCross)
            removedDirections.append([xRemCross, yRemCross, directionRemCross, compassRemCross])
        
        
        print("checkDiff_and_oppositeCompassSameDir_HasBeenCalculated-->", checkDiff_and_oppositeCompassSameDir_HasBeenCalculated)  
        if addTolist == False and (sensorLeft == ['1','1'] or sensorRight == ['1','1']) and checkDiff_and_oppositeCompassSameDir_HasBeenCalculated == False:  
            checkDiff, checkDirection, checkXrem, checkYrem, checkCompassRem = self.checkDifference(possibleDirections, round(x,1), round(y,1), self.measures.compass, checkXrem, checkYrem, checkDirection, checkCompassRem)
            oppositeCompassTurnLeft, oppositeCompassTurnRight, oppositeCompassX, oppositeCompassY, oppositeCompassDirection, oppositeCompassCompass = self.oppositeCompassButSameDirection(possibleDirections, round(x,1), round(y,1), self.measures.compass, oppositeCompassX, oppositeCompassY, oppositeCompassDirection, oppositeCompassCompass, oppositeCompassTurnRight, oppositeCompassTurnLeft)
            if (checkXrem != 1000 and checkYrem != 1000 and checkDirection != "") or (oppositeCompassX != 1000 and oppositeCompassY != 1000 and oppositeCompassDirection != ""):
                checkDiff_and_oppositeCompassSameDir_HasBeenCalculated = True
        
        print("checkxrem,",checkXrem)
        print("checkyrem,",checkYrem)
        
        if intersection == True:    
            done, xDone, yDone, directionDone, compassDone = self.checkIfDirectionDone(possibleDirections, round(x,1), round(y,1), self.measures.compass)
        print("done", done)
        print("xDone", xDone)
        print("yDone", yDone)

        if done == True: #and addTolist == False 
            self.removeElement(possibleDirections, xDone, yDone)
            removedDirections.append([xDone, yDone, directionDone, compassDone])
            
        if startCounting == True:
            waitAddToList = waitAddToList + 1


        
        if pathToNode == []:

                # last_cellOnPath = next(reversed(pathToNode))
                # print("last_cellonpath",last_cellOnPath)
                # print("CELULAS_X",last_cellOnPath[0] % 2)
                # print("CELULAS_y",last_cellOnPath[1] % 2)

                # if ((last_cellOnPath[0] % 2) == 0) and ((last_cellOnPath[1] % 2) == 0 ) :  
            
            if (possibleDirections == [] and self.measures.time >= 500):

                
                print("OLAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                mapEnded = True
                
                if graph_has_been_calculated == False:
                    for element in nodes:
                        edges.append(tuple([element[0], element[1], element[3]])) 
                        if element[4] == 'B':
                            beacons.append(tuple([element[0], element[1], element[3]]))
                    #print("EDGES->", edges)
                    #graph = Graph() #Graph passou a ser uma variavel global
                    for edge in edges:  #Criar o grafo atraves das edges
                        graph.add_edge(*edge)
                    
                    graph_has_been_calculated = True
                    #print("beacons:>", beacons)
                    #listaAuxiliarPath = []
                #print("graph_has_been_calculated:", graph_has_been_calculated)
                
                #Reset às variáveis globais
                if self.measures.time != 5000: #Se o tempo não terminou, o robo vai até ao ponto inicial
                    #self.measures.lineSensor == ['0','0','1','1','1','0','0'] or self.measures.lineSensor == ['0','0','1','1','0','0','0'] or self.measures.lineSensor == ['0','0','0','1','1','0','0']
                    if self.measures.lineSensor == ['0','0','1','1','1','0','0'] or self.measures.lineSensor == ['0','0','1','1','0','0','0'] or self.measures.lineSensor == ['0','0','0','1','1','0','0']:
                        find_cell == False
                        rotate_mapEnded  = 0
                        turnL_mapEnded = 0
                        turnR_mapEnded  = 0
                        go_foward_mapEnded  = 0
                        done_decisionDir_For_That_vertex = False
                    
                    if cells_To_Start_hasBeen_Calculated == False:        
                        end_map_vertex = self.findVertex(nodes, (matrixyinicial,matrixxinicial)) #Fazer com que (matrixyinicial,matrixxinicial) tenha sempre o valor do robo no instante em q terminou o mapa
                        #print("END MAP VERTEX->", end_map_vertex)
                        list_path_to_iVertex = self.dijsktra(graph, '1', end_map_vertex)
                        print("PATH_TO_INICIAL->", list_path_to_iVertex)
                        #custo_caminho = self.findCostFor2Vertex(list_path_to_iVertex, nodes)
                        #print("CUSTO->", custo_caminho)
                        cells = self.findCells_of_path2IVertex(list_path_to_iVertex, nodes)
                        print("CELLS->", cells)
                        cells_To_Start_hasBeen_Calculated = True
                    #print("CELLS TO START", cells_To_Start_hasBeen_Calculated)
                    
                    #print("DECISION DONE FOR VERTEX BEFORE:", done_decisionDir_For_That_vertex)
                    
                    #TODO: CASO ELE SE PERDA AO CHEGAR A UM VERTICE, OU SEJA, O VERTICE NAO PERTENCE AO CAMINHO MINIMO ATÉ AO INICIO, VOLTA A CALCULAR O CAMINHO MINIMO NESSE VERTICE, TESTAR! -- FAZER OFF aulas
                    if self.find_if_cell_isNode(nodes, (matrixyinicial,matrixxinicial)) == True and done_decisionDir_For_That_vertex == False and intersection == True and self.find_if_Cell_Belong_toPath_toInitial(cells, (matrixyinicial,matrixxinicial)) == True:
                        #print("find_cell_OUTSIDE FUN,", find_cell) 
                        rotate_mapEnded, turnL_mapEnded, turnR_mapEnded, go_foward_mapEnded = self.Choose_Direction_To_Start(cells, matrixyinicial, matrixxinicial, self.measures.compass, self.measures.lineSensor, sensorLeft, sensorRight)
                        done_decisionDir_For_That_vertex = True
                        
                    elif self.find_if_cell_isNode(nodes, (matrixyinicial,matrixxinicial)) == True and done_decisionDir_For_That_vertex == False and intersection == True and self.find_if_Cell_Belong_toPath_toInitial(cells, (matrixyinicial,matrixxinicial)) == False: #Está no nó errado do caminho ao início, por isso volta a calcular
                        end_map_vertex_newVertex = self.findVertex(nodes, (matrixyinicial,matrixxinicial)) 
                        #print("END MAP VERTEX->", end_map_vertex)
                        list_path_to_iVertex = self.dijsktra(graph, '1', end_map_vertex_newVertex)
                        print("PATH_TO_INICIAL->", list_path_to_iVertex)
                        cells = self.findCells_of_path2IVertex(list_path_to_iVertex, nodes)
                        print("NEW LIST CELLS->", cells)
                        
                    print("DECISION DONE FOR VERTEX AFTER:", done_decisionDir_For_That_vertex)
            #contadorteste2 = contadorteste2 +1

        print("valor do contador testetetetetetetet:",contadorteste2)
                        
        if self.measures.time == 5000:
            if graph_has_been_calculated == False:
                for element in nodes:
                    edges.append(tuple([element[0], element[1], element[3]])) 
                    if element[4] == 'B':
                        beacons.append(tuple([element[0], element[1], element[3]]))
                #graph = Graph() #Graph passou a ser uma variavel global
                for edge in edges:  #Criar o grafo atraves das edges
                    graph.add_edge(*edge)
                
                graph_has_been_calculated = True
                #print("beacons:>", beacons)
                
        
        #As vezes pode bugar pq nao encontra [1,1,1,1,1,1,1], logo um dos turning fica a true
        if pathRight == ['1'] and pathLeft == ['1'] and turningLeft == False and turningRight == False:  #and turnRight == False 
            notDoneLetsTurnR_PD, dontAddRightDir_PD = self.pathOnLeftAlreadyDoneEntroncamentos(possibleDirections, round(x,1), round(y,1), self.measures.compass)
            notDoneLetsTurnR_RD, dontAddRightDir_RD = self.pathOnLeftAlreadyDoneEntroncamentos(removedDirections,round(x,1), round(y,1), self.measures.compass)
            
        #TODO: TESTAR!
        #Combater o facto de às vezes qnd está a virar à direita meter 0's à direita por causa do ruido msm havendo caminho para a direita
        print("first_time_Compass_alreadyHaveValue:", first_time_Compass_alreadyHaveValue)
        print("valueCompass_First_Time_turningRight:", valueCompass_First_Time_turningRight)
        if first_time_Compass_alreadyHaveValue == True:
            #Estava a ir para cima e já virou pelo menos uma vez para a direita, então significa q é msm uma direita e continua a virar até centrar
            if 85 <= valueCompass_First_Time_turningRight <= 95 and turningRight == True and self.measures.compass >= 82 and self.measures.compass <= 75 and (pathRight == ['0'] or sensorRight == ['1','0'] or sensorRight == ['0','0']): 
                turningRight = True
                print("ESTOU AQUI PQ HOUVE RUIDO!!!!!!!!")
            
            #Estava a ir para a direita e já virou pelo menos uma vez para a direita, então significa q é msm uma direita e continua a virar até centrar    
            elif -5 <= valueCompass_First_Time_turningRight <= 5 and turningRight == True and self.measures.compass <= -7 and self.measures.compass >= -15  and (pathRight == ['0'] or sensorRight == ['1','0'] or sensorRight == ['0','0']):
                turningRight = True
                print("ESTOU AQUI PQ HOUVE RUIDO!!!!!!!!")
                
            #Estava a ir para baixo e já virou pelo menos uma vez para a direita, então significa q é msm uma direita e continua a virar até centrar    
            elif -95 <= valueCompass_First_Time_turningRight <= -85 and turningRight == True and self.measures.compass <= -97 and self.measures.compass >= -105 and (pathRight == ['0'] or sensorRight == ['1','0'] or sensorRight == ['0','0']):
                turningRight = True
                print("ESTOU AQUI PQ HOUVE RUIDO!!!!!!!!")
             
            #Estava a ir para a esquerda e já virou pelo menos uma vez para a direita, então significa q é msm uma direita e continua a virar até centrar    
            elif (valueCompass_First_Time_turningRight <= -175 or valueCompass_First_Time_turningRight >= 175) and turningRight == True and self.measures.compass <= 172 and self.measures.compass >= 165 and (pathRight == ['0'] or sensorRight == ['1','0'] or sensorRight == ['0','0']):
                turningRight = True
                print("ESTOU AQUI PQ HOUVE RUIDO!!!!!!!!")
            
            #Esquerda
                
            #Estava a ir para cima e já virou pelo menos uma vez para a esquerda, então significa q é msm uma esquerda e continua a virar até centrar
            elif 85 <= valueCompass_First_Time_turningLeft <= 95 and turningLeft == True and self.measures.compass >= 97 and self.measures.compass <= 105 and (pathLeft == ['0'] or sensorLeft == ['1','0'] or sensorLeft == ['0','0']):
                turningLeft = True
                print("ESTOU AQUI PQ HOUVE RUIDO!!!!!!!!")
                    
            #Estava a ir para a direita e já virou pelo menos uma vez para a esquerda, então significa q é msm uma esquerda e continua a virar até centrar
            elif -5 <= valueCompass_First_Time_turningLeft <= 5 and turningLeft == True and self.measures.compass >= 7 and self.measures.compass <= 15 and (pathLeft == ['0'] or sensorLeft == ['1','0'] or sensorLeft == ['0','0']):
                turningLeft = True
                print("ESTOU AQUI PQ HOUVE RUIDO!!!!!!!!")
                
            #Estava a ir para baixo e já virou pelo menos uma vez para a esquerda, então significa q é msm uma esquerda e continua a virar até centrar    
            elif -95 <= valueCompass_First_Time_turningLeft <= -85 and turningLeft == True and self.measures.compass >= -82 and self.measures.compass <= -75 and (pathLeft == ['0'] or sensorLeft == ['1','0'] or sensorLeft == ['0','0']):
                turningLeft = True
                print("ESTOU AQUI PQ HOUVE RUIDO!!!!!!!!")
                
            #Estava a ir para a esquerda e já virou pelo menos uma vez para a esquerda, então significa q é msm uma esquerda e continua a virar até centrar    
            elif (valueCompass_First_Time_turningLeft <= -175 or valueCompass_First_Time_turningLeft >= 175) and turningLeft == True and self.measures.compass >= -172 and self.measures.compass <= -165 and (pathLeft == ['0'] or sensorLeft == ['1','0'] or sensorLeft == ['0','0']):
                turningLeft = True
                print("ESTOU AQUI PQ HOUVE RUIDO!!!!!!!!")
         
        #Verifica se a coordenada onde se encontra está na lista de coordenadas q são um ciclo      
        coordinateIsACycle_turnLeft, coordinateIsACycle_turnRight = self.actualCoordinatesAreACycle(coordinatesCycle, round(x,1), round(y,1), self.measures.compass)
        print("coordinateIsACycle_turnLeft->", coordinateIsACycle_turnLeft)
        print("coordinateIsACycle_turnRight->", coordinateIsACycle_turnRight)
                
        if  (notDoneLetsTurnR_PD == True or notDoneLetsTurnR_RD == True) and addTolist == False and isACycle == False and isACycle_Right == False and coordinateIsACycle_turnLeft == False and coordinateIsACycle_turnRight == False and intersection == True and mapEnded == False:    #isCycle = False
            #virar à direita
            self.driveMotors(+0.1,-0.07)    #self.driveMotors(+0.1,-0.08), alterei este valor
            
            outL, outR = self.updateDriveMotors(last_outL, 0.1, last_outR, -0.07)
            #print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
                
            print("ANTES DE ENTRAR NA FUNC(", x,", ", y, ")")
            
            #Calcular closestPair
            closestPairXandY = self.calculateClosestPair(x, y, self.measures.compass)
            print("closestPairXandY->", closestPairXandY)
             
            # Corrigir o X e o Y
            if ((self.measures.compass >= -35 and self.measures.compass <= 35) or (self.measures.compass <= -160 or self.measures.compass >= 160)) and alreadyCorrect == False: #Horizontal, corrigir o X
                #self.correctTeta()  #Corrigir o teta
                x = self.correctXOnxPar(x, self.measures.compass, closestPairXandY)
                lastX = x
                alreadyCorrect = True
            elif ((self.measures.compass >= 65 and self.measures.compass <= 115) or (self.measures.compass >= -115 and self.measures.compass <= -65)) and alreadyCorrect == False: #Vertical, corrigir o Y
                #self.correctTeta()  #Corrigir o teta
                y = self.correctYOnyPar(y, self.measures.compass, closestPairXandY)
                lastY = y
                alreadyCorrect = True
            
    
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
            
            turningRight = True
            
            
            if already_SeeIfNeed_To_ChangeTo_TurnRight == False:
                #Se já estiver na lista, vai mudar o left para right e adiciona 1 e already_in_the_list retorna True
                already_in_the_list = self.findCorrespondingCoor_For_ChangingTo_TurnRight(round(x,1), round(y,1), self.measures.compass) 
                already_SeeIfNeed_To_ChangeTo_TurnRight = True
                
                
            if already_in_the_list == False and already_addCoordinatesDone == False:
                coordinatesDone.append([round(x,1), round(y,1), self.measures.compass, 1, "turningRight", turningRight])
                already_addCoordinatesDone = True
               
            exist = False #Só usamos isto no leats learn left 
            #Como está a virar à "Direita" a avoidCyclesBol apenas vai ver se há algum valor igual a 3 para adicionar como sendo um ciclo
            isACycle, isACycle_Right, xVarCycle, yVarCycle, compassVarCycle, exist = self.avoidCyclesBol(coordinatesDone, round(x,1), round(y,1), self.measures.compass, "Direita")
            if xVarCycle != 0 and yVarCycle != 0 and isACycle == True and ([xVarCycle,yVarCycle,compassVarCycle] not in coordinatesCycle):
                coordinatesCycle.append([xVarCycle,yVarCycle, compassVarCycle, "Left"])
            elif xVarCycle != 0 and yVarCycle != 0 and isACycle_Right == True and ([xVarCycle,yVarCycle,compassVarCycle] not in coordinatesCycle):
                coordinatesCycle.append([xVarCycle,yVarCycle, compassVarCycle, "Right"])



            if pathToNode != []:
                
                last_cellOnPath = next(reversed(pathToNode))
                print("last_cell",last_cellOnPath)
                print("CELULAS_X",last_cellOnPath[0] % 2)
                print("CELULAS_y",last_cellOnPath[1] % 2)

                if ((last_cellOnPath[0] % 2) == 0) and ((last_cellOnPath[1] % 2) == 0):

                    for i in range(0,len(nodes)):
                        caminhoNoVertice = nodes[i][5]
                        if pathToNode != []:
                            firstCellPathToNodeColx = pathToNode[0][0] #30
                            firstCellPathToNodeColy = pathToNode[0][1] #9
                            actualPosCell = pathToNode[-1]
                        possibleCell1 = (firstCellPathToNodeColx + 1, firstCellPathToNodeColy) #31,9, andar um para a direita	
                        possibleCell2 = (firstCellPathToNodeColx, firstCellPathToNodeColy + 1) #30, 10 andar 1 para baixo
                        possibleCell3 = (firstCellPathToNodeColx - 1, firstCellPathToNodeColy) #29,9 andar um para a esquerda
                        possibleCell4 = (firstCellPathToNodeColx, firstCellPathToNodeColy - 1) #30,8 andar um para cima
                        
                        if caminhoNoVertice == possibleCell1 and possibleCell1 != actualPosCell:
                            adjacente = nodes[i][0]
                        elif caminhoNoVertice == possibleCell2 and possibleCell2 != actualPosCell:
                            adjacente = nodes[i][0]
                        elif caminhoNoVertice == possibleCell3 and possibleCell3 != actualPosCell:
                            adjacente = nodes[i][0]
                        elif caminhoNoVertice == possibleCell4 and possibleCell4 != actualPosCell:
                            adjacente = nodes[i][0]
                        
                        nodePos = nodes[i][5] #(24,10),(26,10),(28,10),(30,8)
                        if (tuple([matrixyinicial,matrixxinicial]) == nodePos and nodes[i][1] == adjacente):
                            posNodeInList = i
                            break
                        elif (tuple([matrixyinicial, matrixxinicial]) == nodePos):
                            posNodeInList = i
                            #break
                    
                    #posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0 and ([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]] not in nodes)
                    if posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0 and self.checkIfNodeAlreadyInList(nodes,[nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]]) == False: #nodes[posNodeInList][6]
                        nodes.append([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]]) #nodes[posNodeInList][6]
                        
                    clearListPath = True    #verifica as duas condiçoes de cima e caso encontre igual mas o caminho tb é igual
                    resetPathToNode = True


            
            
            print("Robot came from the left side, LETS TURN RIGHT!")
            
        print("going_foward->", going_foward)    
        #EM PRINCIPIO PODE SE TIRAR ESTAS DUAS CONDIÇOES
        if going_foward == True and (self.measures.lineSensor == ['1','0','0','0','0','0','0'] or self.measures.lineSensor == ['1','1','0','0','0','0','0']):
            print("Foward-> rotate slowly right")
            rotate_slowly_going_foward = True
            self.driveMotors(+0.1,-0.07)
            
            outL, outR = self.updateDriveMotors(last_outL, 0.1, last_outR, -0.07)
            #print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
        
        elif going_foward == True and (self.measures.lineSensor == ['0','0','0','0','0','0','1'] or self.measures.lineSensor == ['0','0','0','0','0','1','1']):
            print("Foward-> rotate slowly left")
            rotate_slowly_going_foward = True
            self.driveMotors(-0.07,+0.1)
            
            outL, outR = self.updateDriveMotors(last_outL, -0.07, last_outR, 0.1)
            #print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
            
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
            
        
        
        # if frente == True and isACycle == False and self.actualCoordinatesAreACycle(coordinatesCycle, self.measures.x, self.measures.y, self.measures.compass) == False and mapEnded == False:
        #     self.driveMotors(0.08,0.03) #Rotate slowly right 0.15, 0.06
            
        #     outL, outR = self.updateDriveMotors(last_outL, 0.08, last_outR, 0.03)
        #     print("(", outL, ", ", outR ,")")
        #     x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
                
        #     print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
            
        #     going_foward = True
        #     #self.driveMotors(0.1, 0.1)
        #     print("Foward")
            
        #Evitar q qnd o lineSensor fica td a 0 meta esta variavel a False   
        if self.measures.lineSensor == ['0','0','1','1','1','0','0'] or self.measures.lineSensor == ['0','0','0','1','1','0','0'] or self.measures.lineSensor == ['0','0','1','1','0','0','0']:
            going_foward = False
            addTolist = False
            rotate_slowly_going_foward = False
        
        # print("checkXRem-", checkXrem)
        # print("checkYrem-", checkYrem)
        # print("checkDirection-", checkDirection)
        # print("addTolist-", addTolist)
        # #print("notDoneLetsTurnR_PD->", notDoneLetsTurnR_PD)
        # #print("dontAddRightDir_PD->", dontAddRightDir_PD)
        # #print("isACycle->", isACycle)
        
        # print("Virou demasiado->", self.check_if_turned_toMuch(self.measures.compass))
        # print("turningLeft->", turningLeft)
        # print("turningRight->", turningRight)
        # print("First time compass value:", first_time_compass_value)
        # print("Counter_value Compass->", counter_valueCompass)
        print("possibleDirections->", possibleDirections)
        print("RemovedDirections->", removedDirections)
        
        if mapEnded == False:   #Se o mapa não terminou verifica isto, se terminou não verifica pq o robô pode ter de se virar para trás para chegar ao inicio
            if direction_Left == True and turningLeft == True:
                if self.check_if_turned_toMuch(self.measures.compass) == True: #Está a virar à esquerda e já virou demasiado por causa do ruido
                    turningLeft = False #Para de virare     #Para de virar
                    stopTurning_LeftOrRight = True
            elif direction_Right == True and turningRight == True:
                if self.check_if_turned_toMuch(self.measures.compass) == True: #Está a virar à direita e já virou demasiado por causa do ruido
                    turningRight = False    #Para de virar 
                    stopTurning_LeftOrRight = True
            print("stopTurning_LeftOrRight:", stopTurning_LeftOrRight)
        
        #Secalhar meter pathRight == ['1'] and pathLeft == ['1'] para evitar o ruido do ['1'1'1'1'1'1'1'] 
        #TEMOS de adicionar and checkXRem == 0 and CheckYRem == 0, antes estava sem estes ands
       
        
        if (self.measures.lineSensor == ['1','1','1','1','1','1','1'] or self.measures.lineSensor == ['1','1','1','1','1','1','0']) and turningRight == False and turningLeft == False and itsACross == False and frente == False and (notDoneLetsTurnR_PD == False and notDoneLetsTurnR_RD == False) and oppositeCompassTurnLeft == False and oppositeCompassTurnRight == False and isACycle == False and isACycle_Right == False and coordinateIsACycle_turnLeft == False and coordinateIsACycle_turnRight == False and checkXrem == 1000 and checkYrem == 1000 and mapEnded == False and dontDoNothing_goFoward == False:
            print("Lets learn left side")   #exprimentar a rodar um pouco menos
            self.driveMotors(-0.09,+0.1) #-0.1 estava a fazer bem
            
            outL, outR = self.updateDriveMotors(last_outL, -0.09, last_outR, 0.1)
            #print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
                
            print("ANTES DE ENTRAR NA FUNC(", x,", ", y, ")")
            
            #Calcular closestPair
            closestPairXandY = self.calculateClosestPair(x, y, self.measures.compass)
            print("closestPairXandY->", closestPairXandY) 
            
            # Corrigir o X e o Y
            if ((self.measures.compass >= -35 and self.measures.compass <= 35) or (self.measures.compass <= -160 or self.measures.compass >= 160)) and alreadyCorrect == False: #Horizontal, corrigir o X
                #self.correctTeta()  #Corrigir o teta
                x = self.correctXOnxPar(x, self.measures.compass, closestPairXandY)
                lastX = x
                alreadyCorrect = True
            elif ((self.measures.compass >= 65 and self.measures.compass <= 115) or (self.measures.compass >= -115 and self.measures.compass <= -65)) and alreadyCorrect == False: #Vertical, corrigir o Y
                #self.correctTeta()  #Corrigir o teta
                y = self.correctYOnyPar(y, self.measures.compass, closestPairXandY)
                lastY = y
                alreadyCorrect = True
                
            
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
            
            #Viramos a esquerda e se encontrarmos um zero metemos true
            learningLeft = True
            
            if already_in_turnAround_Condition == False:
                time = self.measures.time
                bussola_turnAround = self.measures.compass
                already_in_turnAround_Condition = True
            
            exist = False
            print("already_addCoordinatesDone->", already_addCoordinatesDone)
            isACycle, isACycle_Right, xVarCycle, yVarCycle, compassVarCycle, exist = self.avoidCyclesBol(coordinatesDone, round(x,1), round(y,1), self.measures.compass, "Esquerda")
            if xVarCycle != 0 and yVarCycle != 0 and isACycle == True and ([xVarCycle,yVarCycle,compassVarCycle] not in coordinatesCycle):
                coordinatesCycle.append([xVarCycle,yVarCycle, compassVarCycle, "Left"])
            elif xVarCycle != 0 and yVarCycle != 0 and isACycle_Right == True and ([xVarCycle,yVarCycle,compassVarCycle] not in coordinatesCycle):
                coordinatesCycle.append([xVarCycle,yVarCycle, compassVarCycle, "Right"])
            
            print("exist->", exist)    
            if exist == True:
                alreadyExist = True
            else:
                alreadyExist == False
                                   
            if alreadyExist == False and already_addCoordinatesDone == False: #
                coordinatesDone.append([round(x,1), round(y,1), self.measures.compass, 1, "learningLeft", learningLeft])
                already_addCoordinatesDone = True
                add_Repeated_CoordinatesDone = True


            if pathToNode != []:

                last_cellOnPath = next(reversed(pathToNode))
                print("last_cellonpath",last_cellOnPath)
                print("CELULAS_X",last_cellOnPath[0] % 2)
                print("CELULAS_y",last_cellOnPath[1] % 2)

                if ((last_cellOnPath[0] % 2) == 0) and ((last_cellOnPath[1] % 2) == 0 ) :    
                
                    #Verificar se ao passar no msm nó, o caminho é diferente, se for então adiciona
                    for i in range(0,len(nodes)):
                        caminhoNoVertice = nodes[i][5]
                        if pathToNode != []:
                            firstCellPathToNodeColx = pathToNode[0][0] #30
                            firstCellPathToNodeColy = pathToNode[0][1] #9
                            actualPosCell = pathToNode[-1]
                        possibleCell1 = (firstCellPathToNodeColx + 1, firstCellPathToNodeColy) #31,9, andar um para a direita	
                        possibleCell2 = (firstCellPathToNodeColx, firstCellPathToNodeColy + 1) #30, 10 andar 1 para baixo
                        possibleCell3 = (firstCellPathToNodeColx - 1, firstCellPathToNodeColy) #29,9 andar um para a esquerda
                        possibleCell4 = (firstCellPathToNodeColx, firstCellPathToNodeColy - 1) #30,8 andar um para cima
                        
                        if caminhoNoVertice == possibleCell1 and possibleCell1 != actualPosCell:
                            adjacente = nodes[i][0]
                        elif caminhoNoVertice == possibleCell2 and possibleCell2 != actualPosCell:
                            adjacente = nodes[i][0]
                        elif caminhoNoVertice == possibleCell3 and possibleCell3 != actualPosCell:
                            adjacente = nodes[i][0]
                        elif caminhoNoVertice == possibleCell4 and possibleCell4 != actualPosCell:
                            adjacente = nodes[i][0]
                        
                        nodePos = nodes[i][5] #(24,10),(26,10),(28,10),(30,8)
                        if (tuple([matrixyinicial,matrixxinicial]) == nodePos and nodes[i][1] == adjacente) or (tuple([matrixyinicial, matrixxinicial]) == nodePos):
                            posNodeInList = i
                            #break
                    # if posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False:
                    #     print("ESTOU AQUI NO TURN RIGHT!!!!!")
                    #     nodes.append([nodes[posNodeInList][0], nodes[posNodeInList][1], pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]])
                    
                    #posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0 and ([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]] not in nodes)
                    if posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0 and self.checkIfNodeAlreadyInList(nodes,[nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]]) == False: #nodes[posNodeInList][6]
                        nodes.append([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]]) #nodes[posNodeInList][6]
                        
                    #elif posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente == 0:
                        #nodes.append([nodes[posNodeInList][0], nodes[posNodeInList][1], pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]])
                        
                    clearListPath = True    #verifica as duas condiçoes de cima e caso encontre igual mas o caminho tb é igual
                    resetPathToNode = True   

                
                    
                    #Sempre que passa no msm sitio contar
                    if self.sameCoordinateInList(possibleDirections, round(x,1), round(y,1)) == False and self.sameCoordinateInList(removedDirections, round(x,1), round(y,1)) == False and self.samePosition(coordinatesDone, round(x,1), round(y,1), self.measures.compass) == False and dontAddRightDir_PD == False and dontAddRightDir_RD == False:
                        possibleDirections.append([round(x,1), round(y,1), "direita", self.measures.compass])
                        DirectionsAndTargets.append([round(x,1), round(y,1)])
                        directionsAndTargetsMatrix.append([matrixyinicial,matrixxinicial])
                        for i in range(0, len(nodes)):
                            caminhoNoVertice = nodes[i][5]
                            if pathToNode != []:
                                firstCellPathToNodeColx = pathToNode[0][0] #30
                                firstCellPathToNodeColy = pathToNode[0][1] #9
                                actualPosCell = pathToNode[-1]
                            possibleCell1 = (firstCellPathToNodeColx + 1, firstCellPathToNodeColy) #31,9, andar um para a direita	
                            possibleCell2 = (firstCellPathToNodeColx, firstCellPathToNodeColy + 1) #30, 10 andar 1 para baixo
                            possibleCell3 = (firstCellPathToNodeColx - 1, firstCellPathToNodeColy) #29,9 andar um para a esquerda
                            possibleCell4 = (firstCellPathToNodeColx, firstCellPathToNodeColy - 1) #30,8 andar um para cima
                            
                            if caminhoNoVertice == possibleCell1 and possibleCell1 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell2 and possibleCell2 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell3 and possibleCell3 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell4 and possibleCell4 != actualPosCell:
                                adjacente = nodes[i][0] 
                            
                            nodePos = nodes[i][5]
                            if tuple([matrixyinicial, matrixxinicial]) == nodePos:
                                posNodeInList = i
                        # if posNodeInList != -1:
                        #     nodes.append([nodes[posNodeInList][0], nodes[posNodeInList][1], pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                        # else:
                        #     numberNodesAux = numberNodes
                        #     adjacente = numberNodesAux - 1
                        #     nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                        #     numberNodes = numberNodes + 1
                        if posNodeInList != -1 and adjacente != 0:
                            nodes.append([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                        elif posNodeInList == -1 and adjacente != 0:
                            nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                            numberNodes = numberNodes + 1
                        elif posNodeInList == -1 and adjacente == 0:
                            #numberNodesAux = numberNodes
                            adjacente = self.calculate_adjacent(pathToNode)
                            nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                            numberNodes = numberNodes + 1

                        #pathToNode.clear()
                        clearListPath = True
                        addTolist = True
                        startCounting = True 

                    
                
        #checkDiff == True and otherDirectionsLoop == True   and followCompass == False (findValue == True and direction == "direita" and frente == False and addTolist == False) or
        #and isACycle == False
        #EXPERIMENTAR tirar o frente == False e no debaixo tb, and frente == False
        elif (((checkXrem != 1000 and checkYrem != 1000 and checkDirection == "direita" and addTolist == False) or (oppositeCompassTurnRight == True and addTolist == False) or isACycle_Right == True or coordinateIsACycle_turnRight == True) and (isACycle == False and coordinateIsACycle_turnLeft == False and intersection == True and stopTurning_LeftOrRight == False)) or turnR_mapEnded == True:  #SO ENTRA NOS OUTROS ELIF'S SE O findValue FOR False, o otherDirectionsLoop for false
            direction_Right = True
            #Secalhar adicionamos aqui a condição para só executar as linhas de baixo se o mapa não tiver terminado
            if mapEnded == False:
                
                if pathToNode != []:
                    last_cellOnPath = next(reversed(pathToNode))
                    print("last_cellonpath",last_cellOnPath)

                    if ((last_cellOnPath[0] % 2) == 0) and ((last_cellOnPath[1] % 2) == 0 ) :
                        #Verificar se ao passar no msm nó, o caminho é diferente, se for então adiciona
                        for i in range(0,len(nodes)):
                            caminhoNoVertice = nodes[i][5]
                            if pathToNode != []:
                                firstCellPathToNodeColx = pathToNode[0][0] #30
                                firstCellPathToNodeColy = pathToNode[0][1] #9
                                actualPosCell = pathToNode[-1]
                            possibleCell1 = (firstCellPathToNodeColx + 1, firstCellPathToNodeColy) #31,9, andar um para a direita	
                            possibleCell2 = (firstCellPathToNodeColx, firstCellPathToNodeColy + 1) #30, 10 andar 1 para baixo
                            possibleCell3 = (firstCellPathToNodeColx - 1, firstCellPathToNodeColy) #29,9 andar um para a esquerda
                            possibleCell4 = (firstCellPathToNodeColx, firstCellPathToNodeColy - 1) #30,8 andar um para cima
                            
                            if caminhoNoVertice == possibleCell1 and possibleCell1 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell2 and possibleCell2 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell3 and possibleCell3 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell4 and possibleCell4 != actualPosCell:
                                adjacente = nodes[i][0]
                            
                            nodePos = nodes[i][5] #(24,10),(26,10),(28,10),(30,8)
                            if tuple([matrixyinicial,matrixxinicial]) == nodePos and nodes[i][1] == adjacente:
                                posNodeInList = i
                        if posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0:
                            print("ESTOU AQUI NO TURN RIGHT!!!!!")
                            nodes.append([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]]) #,nodes[posNodeInList][6]
                            #clearListPath = True
                        
                        clearListPath = True    #verifica as duas condiçoes de cima e caso encontre igual mas o caminho tb é igual
                        resetPathToNode = True

                   
            
            self.driveMotors(+0.1,-0.07)
            
            outL, outR = self.updateDriveMotors(last_outL, 0.1, last_outR, -0.07)
            #print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
                
            print("ANTES DE ENTRAR NA FUNC(", x,", ", y, ")")
            
            #Calcular closestPair
            closestPairXandY = self.calculateClosestPair(x, y, self.measures.compass)
            print("closestPairXandY->", closestPairXandY) 
            
            # Corrigir o X e o Y
            if ((self.measures.compass >= -35 and self.measures.compass <= 35) or (self.measures.compass <= -160 or self.measures.compass >= 160)) and alreadyCorrect == False: #Horizontal, corrigir o X
                #self.correctTeta()  #Corrigir o teta
                x = self.correctXOnxPar(x, self.measures.compass, closestPairXandY)
                lastX = x
                alreadyCorrect = True
            elif ((self.measures.compass >= 65 and self.measures.compass <= 115) or (self.measures.compass >= -115 and self.measures.compass <= -65)) and alreadyCorrect == False: #Vertical, corrigir o Y
                #self.correctTeta()  #Corrigir o teta
                y = self.correctYOnyPar(y, self.measures.compass, closestPairXandY)
                lastY = y
                alreadyCorrect = True
                
            
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
            
            turningRight = True
            print("Lets turn RIGHT (OTHER DIRECTION)")
            
            if already_in_turnAround_Condition == False:
                time = self.measures.time
                bussola_turnAround = self.measures.compass
                already_in_turnAround_Condition = True
        #checkDiff == True and otherDirectionsLoop == True    and followCompass == False (findValue == True and direction == "esquerda"  and frente == False and addTolist == False) or
        # or isACycle == True, and frente == False
        elif ((((checkXrem != 1000 and checkYrem != 1000 and checkDirection == "esquerda" and addTolist == False) or (oppositeCompassTurnLeft == True and addTolist == False)) or (isACycle == True or coordinateIsACycle_turnLeft == True)) and intersection == True and stopTurning_LeftOrRight == False and isACycle_Right == False and coordinateIsACycle_turnRight == False) or turnL_mapEnded == True:  #SO ENTRA NOS OUTROS ELIF'S SE O findValue FOR False, o otherDirectionsLoop for false
            direction_Left = True
            #Secalhar adicionamos aqui a condição para só executar as linhas de baixo se o mapa não tiver terminado
            if mapEnded == False:


                
                if pathToNode != []:
                    last_cellOnPath = next(reversed(pathToNode))
                    print("last_cellonpath", last_cellOnPath)
                    print("CELULAS_X",last_cellOnPath[0] % 2)
                    print("CELULAS_y",last_cellOnPath[1] % 2)

                    if ((last_cellOnPath[0] % 2) == 0) and ((last_cellOnPath[1] % 2) == 0 ) :
                        #Verificar se ao passar no msm nó, o caminho é diferente, se for então adiciona
                        for i in range(0,len(nodes)):
                            caminhoNoVertice = nodes[i][5]
                            if pathToNode != []:
                                firstCellPathToNodeColx = pathToNode[0][0] #30
                                firstCellPathToNodeColy = pathToNode[0][1] #9
                                actualPosCell = pathToNode[-1]
                            possibleCell1 = (firstCellPathToNodeColx + 1, firstCellPathToNodeColy) #31,9, andar um para a direita	
                            possibleCell2 = (firstCellPathToNodeColx, firstCellPathToNodeColy + 1) #30, 10 andar 1 para baixo
                            possibleCell3 = (firstCellPathToNodeColx - 1, firstCellPathToNodeColy) #29,9 andar um para a esquerda
                            possibleCell4 = (firstCellPathToNodeColx, firstCellPathToNodeColy - 1) #30,8 andar um para cima
                            
                            if caminhoNoVertice == possibleCell1 and possibleCell1 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell2 and possibleCell2 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell3 and possibleCell3 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell4 and possibleCell4 != actualPosCell:
                                adjacente = nodes[i][0]
                            
                            nodePos = nodes[i][5] #(24,10),(26,10),(28,10),(30,8)
                            if tuple([matrixyinicial,matrixxinicial]) == nodePos and nodes[i][1] == adjacente:
                                posNodeInList = i
                        if posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0:
                            print("ESTOU AQUI NO TURN LEFT!!!!!")
                            nodes.append([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]]) #,nodes[posNodeInList][6]
                            
                        clearListPath = True
                        resetPathToNode = True

                   
            
            self.driveMotors(-0.07,+0.1)
            
            outL, outR = self.updateDriveMotors(last_outL, -0.07, last_outR, 0.1)
            print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
                
            print("ANTES DE ENTRAR NA FUNC(", x,", ", y, ")")
            
            #Calcular closestPair
            closestPairXandY = self.calculateClosestPair(x, y, self.measures.compass)
            print("closestPairXandY->", closestPairXandY) 
            
            
            # Corrigir o X e o Y
            if ((self.measures.compass >= -35 and self.measures.compass <= 35) or (self.measures.compass <= -160 or self.measures.compass >= 160)) and alreadyCorrect == False: #Horizontal, corrigir o X
                #self.correctTeta()  #Corrigir o teta
                x = self.correctXOnxPar(x, self.measures.compass, closestPairXandY)
                lastX = x
                alreadyCorrect = True
            elif ((self.measures.compass >= 65 and self.measures.compass <= 115) or (self.measures.compass >= -115 and self.measures.compass <= -65)) and alreadyCorrect == False: #Vertical, corrigir o Y
                #self.correctTeta()  #Corrigir o teta
                y = self.correctYOnyPar(y, self.measures.compass, closestPairXandY)
                lastY = y
                alreadyCorrect = True
                
            
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
            
            turningLeft = True
            print("Lets turn LEFT (OTHER DIRECTION)")
            if already_in_turnAround_Condition == False:
                time = self.measures.time
                bussola_turnAround = self.measures.compass
                already_in_turnAround_Condition = True
        
        #Momento em que descobriu q tem caminho em frente, poderá surgir mais casos de ruido
        #MUDEI PARA sensorRight == ['1','1'] por causa do RUIDO!
        #self.measures.lineSensor != ['1','1','1','1','1','1','1'] and self.measures.lineSensor != ['1','1','1','0','1','1','1'] and self.measures.lineSensor != ['1','1','0','1','1','1','1'] and self.measures.lineSensor != ['1','1','0','0','1','1','1'] and self.measures.lineSensor != ['1','1','0','0','0','1','1'] and self.measures.lineSensor != ['1','1','0','0','0','0','1']
        #ANTES estava pathRigh = ['1','1']
        elif sensorRight == ['1','1'] and pathLeft != ['1'] and turningLeft == False and itsACross == False and frente == False and learningLeft == False and rotate_mapEnded == False and go_foward_mapEnded == False and dontDoNothing_goFoward == False:####
            print('Rotate/Knowing Right')
            turningRight = True
            self.driveMotors(+0.1,-0.03)    #-0.04
            
            outL, outR = self.updateDriveMotors(last_outL, 0.1, last_outR, -0.03)
            print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
                
            print("ANTES DE ENTRAR NA FUNC(", x,", ", y, ")")
            
            #Calcular closestPair
            closestPairXandY = self.calculateClosestPair(x, y, self.measures.compass)
            print("closestPairXandY->", closestPairXandY) 
            
            # Corrigir o X e o Y
            if ((self.measures.compass >= -35 and self.measures.compass <= 35) or (self.measures.compass <= -160 or self.measures.compass >= 160)) and alreadyCorrect == False: #Horizontal, corrigir o X
                #self.correctTeta()  #Corrigir o teta
                x = self.correctXOnxPar(x, self.measures.compass, closestPairXandY)
                lastX = x
                alreadyCorrect = True
            elif ((self.measures.compass >= 65 and self.measures.compass <= 115) or (self.measures.compass >= -115 and self.measures.compass <= -65)) and alreadyCorrect == False: #Vertical, corrigir o Y
                #self.correctTeta()  #Corrigir o teta
                y = self.correctYOnyPar(y, self.measures.compass, closestPairXandY)
                lastY = y
                alreadyCorrect = True
            
            if first_time_Compass_alreadyHaveValue == False:
                valueCompass_First_Time_turningRight = self.measures.compass
                first_time_Compass_alreadyHaveValue = True
                
            
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
            
        #and followCompass == False and checkDiff == False
        #pathLeft == ['1']
        elif sensorLeft == ['1','1'] and turningRight == True and knowing == False and itsACross == False and frente == False and checkXrem == 1000 and checkYrem == 1000 and (notDoneLetsTurnR_PD == False and notDoneLetsTurnR_RD == False) and checkXrem == 1000 and checkYrem == 1000 and oppositeCompassTurnLeft == False and oppositeCompassTurnRight == False and mapEnded == False and dontDoNothing_goFoward == False: 
            #self.driveMotors('0','0')   #stop
            print("WE KNOW THAT WE CAN GO FRONT (LS)")
            self.driveMotors(-0.15,+0.1)
            
            outL, outR = self.updateDriveMotors(last_outL, -0.15, last_outR, 0.1)
            print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
                
            print("ANTES DE ENTRAR NA FUNC(", x,", ", y, ")")
            
            #Calcular closestPair
            closestPairXandY = self.calculateClosestPair(x, y, self.measures.compass)
            print("closestPairXandY->", closestPairXandY) 
            
            # Corrigir o X e o Y
            if ((self.measures.compass >= -35 and self.measures.compass <= 35) or (self.measures.compass <= -160 or self.measures.compass >= 160)) and alreadyCorrect == False: #Horizontal, corrigir o X
                #self.correctTeta()  #Corrigir o teta
                x = self.correctXOnxPar(x, self.measures.compass, closestPairXandY)
                lastX = x
                alreadyCorrect = True
            elif ((self.measures.compass >= 65 and self.measures.compass <= 115) or (self.measures.compass >= -115 and self.measures.compass <= -65)) and alreadyCorrect == False: #Vertical, corrigir o Y
                #self.correctTeta()  #Corrigir o teta
                y = self.correctYOnyPar(y, self.measures.compass, closestPairXandY)
                lastY = y
                alreadyCorrect = True
                
            
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")

            if pathToNode != []:

                last_cellOnPath = next(reversed(pathToNode))
                print("last_cellonpath",last_cellOnPath)
                print("CELULAS_x",last_cellOnPath[0] % 2)
                print("CELULAS_y",last_cellOnPath[1] % 2)


                if ((last_cellOnPath[0] % 2) == 0) and ((last_cellOnPath[1] % 2) == 0 ) : 
            
                    for i in range(0, len(nodes)):
                        caminhoNoVertice = nodes[i][5]
                        if pathToNode != []:
                            firstCellPathToNodeColx = pathToNode[0][0] #30
                            firstCellPathToNodeColy = pathToNode[0][1] #9
                            actualPosCell = pathToNode[-1]
                        possibleCell1 = (firstCellPathToNodeColx + 1, firstCellPathToNodeColy) #31,9, andar um para a direita	
                        possibleCell2 = (firstCellPathToNodeColx, firstCellPathToNodeColy + 1) #30, 10 andar 1 para baixo
                        possibleCell3 = (firstCellPathToNodeColx - 1, firstCellPathToNodeColy) #29,9 andar um para a esquerda
                        possibleCell4 = (firstCellPathToNodeColx, firstCellPathToNodeColy - 1) #30,8 andar um para cima
                        
                        if caminhoNoVertice == possibleCell1 and possibleCell1 != actualPosCell:
                            adjacente = nodes[i][0]
                        elif caminhoNoVertice == possibleCell2 and possibleCell2 != actualPosCell:
                            adjacente = nodes[i][0]
                        elif caminhoNoVertice == possibleCell3 and possibleCell3 != actualPosCell:
                            adjacente = nodes[i][0]
                        elif caminhoNoVertice == possibleCell4 and possibleCell4 != actualPosCell:
                            adjacente = nodes[i][0]
                            
                        nodePos = nodes[i][5]
                        if (tuple([matrixyinicial, matrixxinicial]) == nodePos and nodes[i][1] == adjacente):
                            posNodeInList = i
                            break
                        elif (tuple([matrixyinicial, matrixxinicial]) == nodePos):
                            posNodeInList = i
                            #break
                            
                    #posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0 and ([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)] not in nodes)
                    if posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0 and self.checkIfNodeAlreadyInList(nodes,[nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)]) == False:
                        print("ESTOU AQUI NA PARTE DO LS")
                        nodes.append([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                        clearListPath = True
                        resetPathToNode = True
                    
                    # if posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False:
                    #     print("ESTOU AQUI NA PARTE DO LS")
                    #     nodes.append([nodes[posNodeInList][0], nodes[posNodeInList][1], pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                    #     clearListPath = True
                    #     resetPathToNode = True
                    elif posNodeInList != -1 and pathToNode == nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0:
                        clearListPath = True
                        resetPathToNode = True
                        
                    #clearListPath = True
                    #resetPathToNode = True
                    
                    
                    #or ([round(self.measures.x), self.measures.y] not in possibleDirections) and self.samePosition(coordinatesDone, self.measures.x, self.measures.y) == False and self.checkIfSameHorizontalPos(possibleDirections, self.measures.x, self.measures.y, self.measures.compass) == False self.checkIfSameVerticalPos(possibleDirections, self.measures.x, self.measures.compass) == False
                    #(([self.measures.x, self.measures.y] not in possibleDirections) and self.checkCoordinatesInList(possibleDirections,self.measures.x,self.measures.y) == False)
                    if self.checkCoordinatesInList(possibleDirections,round(x,1),round(y,1)) == False and self.doneDirection(removedDirections, round(x,1), round(y,1)) == False and self.samePosition(coordinatesDone, round(x,1), round(y,1), self.measures.compass) == False and done == False:
                        #Adicionar esta posiçao ao possibleDirections
                        possibleDirections.append([round(x,1), round(y,1), "direita", self.measures.compass])    ####### Adicionar outra direçao a lista
                        DirectionsAndTargets.append([round(x,1), round(y,1)])
                        directionsAndTargetsMatrix.append([matrixyinicial,matrixxinicial])
                        for i in range(0, len(nodes)):  
                            caminhoNoVertice = nodes[i][5]
                            if pathToNode != []:
                                firstCellPathToNodeColx = pathToNode[0][0] #30
                                firstCellPathToNodeColy = pathToNode[0][1] #9
                                actualPosCell = pathToNode[-1]
                            possibleCell1 = (firstCellPathToNodeColx + 1, firstCellPathToNodeColy) #31,9, andar um para a direita	
                            possibleCell2 = (firstCellPathToNodeColx, firstCellPathToNodeColy + 1) #30, 10 andar 1 para baixo
                            possibleCell3 = (firstCellPathToNodeColx - 1, firstCellPathToNodeColy) #29,9 andar um para a esquerda
                            possibleCell4 = (firstCellPathToNodeColx, firstCellPathToNodeColy - 1) #30,8 andar um para cima
                            
                            if caminhoNoVertice == possibleCell1 and possibleCell1 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell2 and possibleCell2 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell3 and possibleCell3 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell4 and possibleCell4 != actualPosCell:
                                adjacente = nodes[i][0]
                            
                            nodePos = nodes[i][5]
                            if tuple([matrixyinicial, matrixxinicial]) == nodePos:
                                posNodeInList = i
                        # if posNodeInList != -1:
                        #     nodes.append([nodes[posNodeInList][0], nodes[posNodeInList][1],pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                        # else:
                        #     numberNodesAux = numberNodes
                        #     adjacente = numberNodesAux - 1
                        #     nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                        #     numberNodes = numberNodes + 1
                        #     print("ESTOU AQUI")
                        if posNodeInList != -1 and adjacente != 0:
                            nodes.append([nodes[posNodeInList][0], adjacente.__str__(),pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                        elif posNodeInList == -1 and adjacente != 0:
                            nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                            numberNodes = numberNodes + 1
                            #print("ESTOU AQUI")
                        elif posNodeInList == -1 and adjacente == 0:
                            #numberNodesAux = numberNodes
                            adjacente = self.calculate_adjacent(pathToNode)
                            nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                            numberNodes = numberNodes + 1
                        
                        clearListPath = True
                        #print("NODES-->", nodes)
                        #print("ESTOU AQUI!!!!!!!!")
                        addTolist = True
                        startCounting = True    
                    turningRight = False
                    turningLeft = True
                    knowing = True
                    print("Virar à esquerda")
             
        # pathLeft == ['1'] and self.measures.lineSensor != ['1','1','1','1','1','1','1'] and turningRight == False
        #Momento em que descobriu q tem caminho em frente
        #MUDEI para sensorLeft == ['1','1'] por causa do RUIDO!
        elif sensorLeft == ['1','1'] and pathRight != ['1'] and turningRight == False and itsACross == False and frente == False and maybeDeadEnd == False and rotate_mapEnded == False and go_foward_mapEnded == False and dontDoNothing_goFoward == False:
            print("Rotate/Knowing left side")
            self.driveMotors(-0.03,+0.1)    #-0.04
            
            outL, outR = self.updateDriveMotors(last_outL, -0.03, last_outR, 0.1)
            print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
            
            print("ANTES DE ENTRAR NA FUNC(", x,", ", y, ")")
            
            #Calcular closestPair
            closestPairXandY = self.calculateClosestPair(x, y, self.measures.compass)
            print("closestPairXandY->", closestPairXandY)
             
            # Corrigir o X e o Y
            if ((self.measures.compass >= -35 and self.measures.compass <= 35) or (self.measures.compass <= -160 or self.measures.compass >= 160)) and alreadyCorrect == False: #Horizontal, corrigir o X
                #self.correctTeta()  #Corrigir o teta
                x = self.correctXOnxPar(x, self.measures.compass, closestPairXandY)
                lastX = x
                alreadyCorrect = True
            elif ((self.measures.compass >= 65 and self.measures.compass <= 115) or (self.measures.compass >= -115 and self.measures.compass <= -65)) and alreadyCorrect == False: #Vertical, corrigir o Y
                #self.correctTeta()  #Corrigir o teta
                y = self.correctYOnyPar(y, self.measures.compass, closestPairXandY)
                lastY = y
                alreadyCorrect = True
                
            if first_time_Compass_alreadyHaveValue == False:
                valueCompass_First_Time_turningLeft = self.measures.compass
                first_time_Compass_alreadyHaveValue = True
                
            
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
            
            turningLeft = True
            
        #and followCompass == False and checkDiff == False
        #pathRight == ['1']
        elif sensorRight == ['1','1'] and turningLeft == True and knowing == False and itsACross == False and frente == False and checkXrem == 1000 and checkYrem == 1000 and (notDoneLetsTurnR_PD == False and notDoneLetsTurnR_RD == False) and checkXrem == 1000 and checkYrem == 1000 and oppositeCompassTurnLeft == False and oppositeCompassTurnRight == False and learningLeft == False and mapEnded == False and dontDoNothing_goFoward == False:   #ADICIONEI learningLeft (6/12/2022)
            #self.driveMotors(0,0)   #STOP
            print("WE KNOW THAT WE CAN GO FRONT (RS)")
            self.driveMotors(+0.1,-0.15)
            
            outL, outR = self.updateDriveMotors(last_outL, 0.1, last_outR, -0.15)
            print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
                
            print("ANTES DE ENTRAR NA FUNC(", x,", ", y, ")")
            
            #Calcular closestPair
            closestPairXandY = self.calculateClosestPair(x, y, self.measures.compass)
            print("closestPairXandY->", closestPairXandY)
             
            # Corrigir o X e o Y
            if ((self.measures.compass >= -35 and self.measures.compass <= 35) or (self.measures.compass <= -160 or self.measures.compass >= 160)) and alreadyCorrect == False: #Horizontal, corrigir o X
                #self.correctTeta()  #Corrigir o teta
                x = self.correctXOnxPar(x, self.measures.compass, closestPairXandY)
                lastX = x
                alreadyCorrect = True
            elif ((self.measures.compass >= 65 and self.measures.compass <= 115) or (self.measures.compass >= -115 and self.measures.compass <= -65)) and alreadyCorrect == False: #Vertical, corrigir o Y
                #self.correctTeta()  #Corrigir o teta
                y = self.correctYOnyPar(y, self.measures.compass, closestPairXandY)
                lastY = y
                alreadyCorrect = True
            
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")

            if pathToNode != []:

                last_cellOnPath = next(reversed(pathToNode))
                print("last_cellonpath",last_cellOnPath)
                print("CELULAS_x",last_cellOnPath[0] % 2)
                print("CELULAS_y",last_cellOnPath[1] % 2)


                if ((last_cellOnPath[0] % 2) == 0) and ((last_cellOnPath[1] % 2) == 0 ) : 
            
                    for i in range(0, len(nodes)):
                        caminhoNoVertice = nodes[i][5]
                        if pathToNode != []:
                            firstCellPathToNodeColx = pathToNode[0][0] #30
                            firstCellPathToNodeColy = pathToNode[0][1] #9
                            actualPosCell = pathToNode[-1]
                        possibleCell1 = (firstCellPathToNodeColx + 1, firstCellPathToNodeColy) #31,9, andar um para a direita	
                        possibleCell2 = (firstCellPathToNodeColx, firstCellPathToNodeColy + 1) #30, 10 andar 1 para baixo
                        possibleCell3 = (firstCellPathToNodeColx - 1, firstCellPathToNodeColy) #29,9 andar um para a esquerda
                        possibleCell4 = (firstCellPathToNodeColx, firstCellPathToNodeColy - 1) #30,8 andar um para cima
                        
                        if caminhoNoVertice == possibleCell1 and possibleCell1 != actualPosCell:
                            adjacente = nodes[i][0]
                        elif caminhoNoVertice == possibleCell2 and possibleCell2 != actualPosCell:
                            adjacente = nodes[i][0]
                        elif caminhoNoVertice == possibleCell3 and possibleCell3 != actualPosCell:
                            adjacente = nodes[i][0]
                        elif caminhoNoVertice == possibleCell4 and possibleCell4 != actualPosCell:
                            adjacente = nodes[i][0]
                        
                        nodePos = nodes[i][5]
                        #Sempre q encontrar uma posiçao do no igual a posiçao atual e com o msm adjacente ou se para o caso onde há mais do q uma interseçao no msm no, onde o adjacente é diferente
                        if (tuple([matrixyinicial, matrixxinicial]) == nodePos and nodes[i][1] == adjacente):
                            posNodeInList = i
                            break
                        elif (tuple([matrixyinicial, matrixxinicial]) == nodePos):
                            posNodeInList = i
                            #break
                    
                    #posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0 and ([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)] not in nodes)
                    if posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0 and self.checkIfNodeAlreadyInList(nodes,[nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)]) == False:
                        print("ESTOU AQUI NA PARTE DO RS")
                        nodes.append([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                        clearListPath = True
                        resetPathToNode = True
                    
                    # if posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False:
                    #     print("ESTOU AQUI NA PARTE DO RS")
                    #     nodes.append([nodes[posNodeInList][0], nodes[posNodeInList][1], pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                    #     clearListPath = True
                    #     resetPathToNode = True
                    elif posNodeInList != -1 and pathToNode == nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0:
                        clearListPath = True
                        resetPathToNode = True
                        
                    #SECALHAR É MELHOR CRIAR OUTRO ELIF COM A CONDIÇAO posNodeInList == -1
                    
                    #Verificar se o x,y nao esta na lista
                    #or ([round(self.measures.x), self.measures.y] not in possibleDirections) and self.samePosition(coordinatesDone, self.measures.x, self.measures.y) == False and self.checkIfSameHorizontalPos(possibleDirections, self.measures.x, self.measures.y, self.measures.compass) == False and self.checkIfSameVerticalPos(possibleDirections, self.measures.x, self.measures.compass) == False
                    #(([self.measures.x, self.measures.y] not in possibleDirections) and self.checkCoordinatesInList(possibleDirections,self.measures.x,self.measures.y) == False)
                    if self.checkCoordinatesInList(possibleDirections,round(x,1),round(y,1)) == False and self.doneDirection(removedDirections, round(x,1), round(y,1)) == False and self.samePosition(coordinatesDone, round(x,1), round(y,1), self.measures.compass) == False and done == False:
                        possibleDirections.append([round(x,1), round(y,1), "esquerda", self.measures.compass])   ###### Adicionar outra direcao na lista
                        DirectionsAndTargets.append([round(x,1), round(y,1)])
                        directionsAndTargetsMatrix.append([matrixyinicial,matrixxinicial])
                        for i in range(0, len(nodes)):  
                            caminhoNoVertice = nodes[i][5]
                            if pathToNode != []:
                                firstCellPathToNodeColx = pathToNode[0][0] #30
                                firstCellPathToNodeColy = pathToNode[0][1] #9
                                actualPosCell = pathToNode[-1]
                            possibleCell1 = (firstCellPathToNodeColx + 1, firstCellPathToNodeColy) #31,9, andar um para a direita	
                            possibleCell2 = (firstCellPathToNodeColx, firstCellPathToNodeColy + 1) #30, 10 andar 1 para baixo
                            possibleCell3 = (firstCellPathToNodeColx - 1, firstCellPathToNodeColy) #29,9 andar um para a esquerda
                            possibleCell4 = (firstCellPathToNodeColx, firstCellPathToNodeColy - 1) #30,8 andar um para cima
                            
                            if caminhoNoVertice == possibleCell1 and possibleCell1 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell2 and possibleCell2 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell3 and possibleCell3 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell4 and possibleCell4 != actualPosCell:
                                adjacente = nodes[i][0]
                            
                            nodePos = nodes[i][5]
                            if tuple([matrixyinicial, matrixxinicial]) == nodePos:
                                posNodeInList = i
                        # if posNodeInList != -1:
                        #     nodes.append([nodes[posNodeInList][0], nodes[posNodeInList][1], pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                        # else:
                        #     numberNodesAux = numberNodes
                        #     adjacente = numberNodesAux - 1
                        #     nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                        #     numberNodes = numberNodes + 1
                        if posNodeInList != -1 and adjacente != 0:
                            nodes.append([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                        elif posNodeInList == -1 and adjacente != 0:
                            nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                            numberNodes = numberNodes + 1
                        elif posNodeInList == -1 and adjacente == 0:
                            #numberNodesAux = numberNodes
                            adjacente = self.calculate_adjacent(pathToNode)
                            nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                            numberNodes = numberNodes + 1
                        clearListPath = True
                        addTolist = True
                        startCounting = True
                    turningLeft = False
                    turningRight = True
                    knowing = True
                    print("Virar a direita")
            
        elif (pathLeft == ['1'] and (turningLeft == True) and go_foward_mapEnded == False and turnR_mapEnded == False and rotate_mapEnded == False) or (self.measures.lineSensor == ['1', '0', '0', '0', '0', '0', '0'] and go_foward_mapEnded == True and turnL_mapEnded == False and rotate_mapEnded == False and turnR_mapEnded == False): #Continua a virar à esquerda, adiciona o caso de qnd está a seguir em frente e encontra aquele line sensor, vira para a esquerda até centrar
            print("Still rotating left")
            self.driveMotors(-0.03,+0.1)    #-0.04
            
            outL, outR = self.updateDriveMotors(last_outL, -0.03, last_outR, 0.1)
            print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
            
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
            
        elif (pathRight == ['1'] and turningRight == True and go_foward_mapEnded == False and turnL_mapEnded == False and rotate_mapEnded == False) or (self.measures.lineSensor == ['0', '0', '0', '0', '0', '0', '1'] and go_foward_mapEnded == True and turnL_mapEnded == False and rotate_mapEnded == False and turnR_mapEnded == False): #Continua a virar à direita, adiciona o caso de qnd está a seguir em frente e encontra aquele line sensor, vira para a direita até centrar
            print("Still rotating right")
            self.driveMotors(+0.1,-0.03)    #-0.04
            
            outL, outR = self.updateDriveMotors(last_outL, 0.1, last_outR, -0.03)
            print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
                
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
            
        
        #Adicionei -> and checkXrem == 0 and checkYrem == 0 and oppositeCompassTurnRight == False and oppositeCompassTurnLeft == False
        #and pathLeft == ['0'] and self.measures.lineSensor != ['1','1','1','1','1','1','1']
        print("SEGUIR EM FRENTE---->", dontDoNothing_goFoward)
        if itsACross == True and isACycle == False and isACycle_Right == False and coordinateIsACycle_turnLeft == False and coordinateIsACycle_turnRight == False and checkXrem == 1000 and checkYrem == 1000 and oppositeCompassTurnRight == False and oppositeCompassTurnLeft == False and mapEnded == False and rotate_slowly_going_foward == False and dontDoNothing_goFoward == False:   #Secalhar vamos ter de fazer esperar um ciclo para ver se é certo
            self.driveMotors(+0.1,-0.1)
            going_foward = True  # Ver se se pode tirar
            turningLeft = False
            turningRight = True
            
            outL, outR = self.updateDriveMotors(last_outL, 0.1, last_outR, -0.1)
            print("(", outL, ", ", outR ,")")
            x, y, teta = self.updateXYTeta(outR, outL, lastX, lastY, lastTeta)
                
            print("(", x,", ", y, ", ", self.normalizeCompass((teta*180)/pi),")")
            
            if (self.measures.compass >= 82 and self.measures.compass <= 98) or (self.measures.compass >= -8 and self.measures.compass <= 8) or (self.measures.compass >= -98 and self.measures.compass <= -82) or (self.measures.compass <= -172 or self.measures.compass >= 172):
                dontDoNothing_goFoward = True
                turningLeft = False
                turningRight = False
            
            #itsACross = False   ####
            

            
            if pathToNode != []:

                last_cellOnPath = next(reversed(pathToNode))
                print("last_cellonpath",last_cellOnPath)
                print("CELULAS_x",last_cellOnPath[0] % 2)
                print("CELULAS_y",last_cellOnPath[1] % 2)


                if ((last_cellOnPath[0] % 2) == 0) and ((last_cellOnPath[1] % 2) == 0 ) :    
                
                    #Verificar se ao passar no msm nó, o caminho é diferente, se for então adiciona
                    for i in range(0,len(nodes)):
                        caminhoNoVertice = nodes[i][5]
                        if pathToNode != []:
                            firstCellPathToNodeColx = pathToNode[0][0] #30
                            firstCellPathToNodeColy = pathToNode[0][1] #9
                            actualPosCell = pathToNode[-1]
                        possibleCell1 = (firstCellPathToNodeColx + 1, firstCellPathToNodeColy) #31,9, andar um para a direita	
                        possibleCell2 = (firstCellPathToNodeColx, firstCellPathToNodeColy + 1) #30, 10 andar 1 para baixo
                        possibleCell3 = (firstCellPathToNodeColx - 1, firstCellPathToNodeColy) #29,9 andar um para a esquerda
                        possibleCell4 = (firstCellPathToNodeColx, firstCellPathToNodeColy - 1) #30,8 andar um para cima
                        
                        if caminhoNoVertice == possibleCell1 and possibleCell1 != actualPosCell:
                            adjacente = nodes[i][0]
                        elif caminhoNoVertice == possibleCell2 and possibleCell2 != actualPosCell:
                            adjacente = nodes[i][0]
                        elif caminhoNoVertice == possibleCell3 and possibleCell3 != actualPosCell:
                            adjacente = nodes[i][0]
                        elif caminhoNoVertice == possibleCell4 and possibleCell4 != actualPosCell:
                            adjacente = nodes[i][0]
                        
                        nodePos = nodes[i][5] #(24,10),(26,10),(28,10),(30,8)
                        if (tuple([matrixyinicial,matrixxinicial]) == nodePos and nodes[i][1] == adjacente) or (tuple([matrixyinicial, matrixxinicial]) == nodePos):
                            posNodeInList = i
                            #break
                    # if posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False:
                    #     print("ESTOU AQUI NO TURN RIGHT!!!!!")
                    #     nodes.append([nodes[posNodeInList][0], nodes[posNodeInList][1], pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]])
                    
                    #posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0 and ([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]] not in nodes)
                    if posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0 and self.checkIfNodeAlreadyInList(nodes,[nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]]) == False: #nodes[posNodeInList][6]
                        nodes.append([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]]) #nodes[posNodeInList][6]
                        
                    #elif posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente == 0:
                        #nodes.append([nodes[posNodeInList][0], nodes[posNodeInList][1], pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]])
                        
                    clearListPath = True    #verifica as duas condiçoes de cima e caso encontre igual mas o caminho tb é igual
                    resetPathToNode = True       
                        
                    #Sempre que passa no msm sitio contar
                    if self.sameCoordinateInList(possibleDirections, round(x,1), round(y,1)) == False and self.sameCoordinateInList(removedDirections, round(x,1), round(y,1)) == False and self.samePosition(coordinatesDone, round(x,1), round(y,1), self.measures.compass) == False and dontAddRightDir_PD == False and dontAddRightDir_RD == False:
                        possibleDirections.append([round(x,1), round(y,1), "direita", self.measures.compass])
                        DirectionsAndTargets.append([round(x,1), round(y,1)])
                        directionsAndTargetsMatrix.append([matrixyinicial,matrixxinicial])
                        for i in range(0, len(nodes)):
                            caminhoNoVertice = nodes[i][5]
                            if pathToNode != []:
                                firstCellPathToNodeColx = pathToNode[0][0] #30
                                firstCellPathToNodeColy = pathToNode[0][1] #9
                                actualPosCell = pathToNode[-1]
                            possibleCell1 = (firstCellPathToNodeColx + 1, firstCellPathToNodeColy) #31,9, andar um para a direita	
                            possibleCell2 = (firstCellPathToNodeColx, firstCellPathToNodeColy + 1) #30, 10 andar 1 para baixo
                            possibleCell3 = (firstCellPathToNodeColx - 1, firstCellPathToNodeColy) #29,9 andar um para a esquerda
                            possibleCell4 = (firstCellPathToNodeColx, firstCellPathToNodeColy - 1) #30,8 andar um para cima
                            
                            if caminhoNoVertice == possibleCell1 and possibleCell1 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell2 and possibleCell2 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell3 and possibleCell3 != actualPosCell:
                                adjacente = nodes[i][0]
                            elif caminhoNoVertice == possibleCell4 and possibleCell4 != actualPosCell:
                                adjacente = nodes[i][0] 
                            
                            nodePos = nodes[i][5]
                            if tuple([matrixyinicial, matrixxinicial]) == nodePos:
                                posNodeInList = i
                        # if posNodeInList != -1:
                        #     nodes.append([nodes[posNodeInList][0], nodes[posNodeInList][1], pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                        # else:
                        #     numberNodesAux = numberNodes
                        #     adjacente = numberNodesAux - 1
                        #     nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                        #     numberNodes = numberNodes + 1
                        if posNodeInList != -1 and adjacente != 0:
                            nodes.append([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                        elif posNodeInList == -1 and adjacente != 0:
                            nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                            numberNodes = numberNodes + 1
                        elif posNodeInList == -1 and adjacente == 0:
                            #numberNodesAux = numberNodes
                            adjacente = self.calculate_adjacent(pathToNode)
                            nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                            numberNodes = numberNodes + 1

                        #pathToNode.clear()
                        clearListPath = True
                        addTolist = True
                        startCounting = True 

                        
                

            print("GO FOWARD, turn a litle bit right")

            
        
        print("waitAbit-->", waitABit)
        #and followCompass == False
        if (waitABit <= 2 and waitABit > 0) and pathRight == ['0']:
            itsACross = False
            turningRight = False
            turningLeft = True
            waitABit = 0
        #and followCompass == False
        elif waitABit >= 3: #and pathRight == ['1']     #Esta parte pode ser melhorada
            itsACross = True
            frente = True  
            #learningLeft = False
            waitABit = 0
            
        
        if self.measures.lineSensor == ['1','1','1','1','1','1','1'] and learningLeft == True:  #SECALHAR, adicionar or self.measures.lineSensor == ['1','1','1','1','1','0','0']
            waitABit = waitABit + 1
        #     frente = True
        #     itsACross = False   #### 
        
        if self.measures.lineSensor == ['0','0','1','1','1','0','0'] or self.measures.lineSensor == ['0','0','0','1','1','0','0'] or self.measures.lineSensor == ['0','0','1','1','0','0','0']:
            haveONEs = False
            turningLeft = False
            turningRight = False
            dontDoNothing_goFoward = False
            first_time_Compass_alreadyHaveValue = False
            stopTurning_LeftOrRight = False
            counter_valueCompass = 0
            already_SeeIfNeed_To_ChangeTo_TurnRight = False
            alreadyCorrect = False
            
        #TODO: SECALHAR ADICIONAR AQUI A BUSSOLA PARA CERTIFICAR-SE Q APENAS ELIMINA NAS HORIZONTAIS E VERTICAIS
        if pathLeft == ['0'] and pathRight == ['0']:    #Exprimentar isto no final dos if's. Secalhar meter este if = [0,0,1,1,1,0,0]
            # turningLeft = False
            # turningRight = False
            knowing = False
            intersection = False
            # global first_time_compass_value, counter_valueCompass
            first_time_compass_value = 0
            already_in_the_list = False
            #counter_valueCompass = 0
            #going_foward = False
            #Remove tb se passar nas msm coordenadas (FAZER) otherDirectionsLoop == True and 
            if addTolist == False:  #secalhar adicionar outra condiçao para remover só dps de ter realizado a direção
                if checkXrem != 1000 and checkYrem != 1000 and checkDirection != "" and checkCompassRem != 0:
                    self.removeElement(possibleDirections, checkXrem, checkYrem)
                    removedDirections.append([checkXrem,checkYrem, checkDirection, checkCompassRem])
                    direction_Left = False
                    direction_Right = False
                    #checkDiff_and_oppositeCompassSameDir_HasBeenCalculated = False
                    #print("Estou pronto para remover valor APROXIMADO")
                elif oppositeCompassX != 0 and oppositeCompassY != 0 and oppositeCompassDirection != "" and oppositeCompassCompass != 0:
                    self.removeElement(possibleDirections,oppositeCompassX, oppositeCompassY)
                    removedDirections.append([oppositeCompassX, oppositeCompassY, oppositeCompassDirection, oppositeCompassCompass])
                    #checkDiff_and_oppositeCompassSameDir_HasBeenCalculated = False
                    
            checkDiff_and_oppositeCompassSameDir_HasBeenCalculated = False
                
            if already_in_turnAround_Condition == True and turnAround == False:
                if self.measures.time > time and self.measures.time < time + 32:    #Se measures.time estiver dentro deste intervalo -> passou pouco tempo, ou seja, virou-se
                    if bussola_turnAround >= -20 and bussola_turnAround <= 20:  #horizontal
                        if self.measures.compass <= -165 or self.measures.compass >= 165:   #Virou-se ao contrario
                            turnAround = True

                    elif bussola_turnAround <= -165 or bussola_turnAround >= 165: #horizontal
                        if self.measures.compass >= -20 and self.measures.compass <= 20:    #Virou-se ao contrario
                            turnAround = True

                    elif bussola_turnAround >= 70 and bussola_turnAround <= 110:    #vertical
                        if self.measures.compass <= -70 and self.measures.compass >= -110:  #Virou-se ao contrario
                            turnAround = True

                    elif bussola_turnAround <= -70 and bussola_turnAround >= -110:  #vertical
                        if self.measures.compass >= 70 and self.measures.compass <= 110:    #Virou-se ao contrario
                            turnAround = True

            if self.measures.time >= time + 34 and turnAround == True:
                already_in_turnAround_Condition = False
                time = -1
                turnAround = False
                bussola_turnAround = 0
            elif turnAround == False and self.measures.time >= time + 34:
                already_in_turnAround_Condition = False
                time = -1
                bussola_turnAround = 0
                
            #alreadyCorrect = False
            add_Repeated_CoordinatesDone = False 
            already_addCoordinatesDone = False    
            itsACross = False
            learningLeft = False
            checkCompassRem = 0
            checkXrem = 1000
            checkYrem = 1000
            checkDiff = False
            checkDirection = ""
            frente = False
            doneCross = False
            xRemCross = 0
            yRemCross = 0
            directionRemCross = ""
            compassRemCross = 0
            notDoneLetsTurnR_PD = False 
            dontAddRightDir_PD = False
            notDoneLetsTurnR_RD = False
            dontAddRightDir_RD = False
            isACycle = False
            isACycle_Right = False
            xVarCycle = 0
            yVarCycle = 0
            compassVarCycle = 0
            alreadyInListDirecitonsAndTargets = False
            #Falta meter os outros do cycle a 0
            
            if waitAddToList == 13:     #antes estava a 8
                addTolist = False
                startCounting = False
                waitAddToList = 0
            
            oppositeCompassTurnLeft = False 
            oppositeCompassTurnRight = False
            oppositeCompassX = 0
            oppositeCompassY = 0
            oppositeCompassDirection = 0
            oppositeCompassCompass = 0


        
        
        #print("Current_cell_map:", (matrixyinicial,matrixxinicial))
        
        if self.measures.time == 0:
            inicialCell = (matrixyinicial2, matrixxinicial2)

        self.matrix[10][24] = '0'

        

        if (self.measures.compass <10 and self.measures.compass > -10) or (self.measures.compass >170 or self.measures.compass < -170):
            self.matrix[matrixxinicial2 + int(round(contadorteste,0))][matrixyinicial2 +  int(round(x,0))] = '-'
            if (matrixyinicial2 +  int(round(x,0))) % 2 == 0:
                self.matrix[matrixxinicial2 + int(round(contadorteste,0))][matrixyinicial2 +  int(round(x,0))] = ' '
                if self.measures.ground !=-1 :
                    self.matrix[matrixxinicial2 + int(round(contadorteste,0))][matrixyinicial2 +  int(round(x,0))] = str(self.measures.ground)
                    #alreadyground = False


            


        if (self.measures.compass <100 and self.measures.compass > 80) or (self.measures.compass >-100 and self.measures.compass<-80):
            self.matrix[matrixxinicial2 + int(round(contadorteste,0))][matrixyinicial2+ int(round(x,0))] = '|'
            if (matrixxinicial2 + int(round(contadorteste,0))) % 2 == 0:
                self.matrix[matrixxinicial2 + int(round(contadorteste,0))][matrixyinicial2 +  int(round(x,0))] = ' '
                if self.measures.ground !=-1 :
                    self.matrix[matrixxinicial2 + int(round(contadorteste,0))][matrixyinicial2 +  int(round(x,0))] = str(self.measures.ground)
                    #alreadyground = False

      
        
        with open(out_file2, 'w') as out:
            for i in self.matrix:
                out.write(''.join(i))
                out.write('\n')

                               
        if self.measures.time == 0:     #Evitar que se adicione a primeira posição da matriz ao caminho
            inicialCols = matrixyinicial2
            inicialLines = matrixxinicial2
        
        #Maneira de no inicio nao adicionar a primeira posição e dps puder adicionar tds as posiçoes incluindo as primeiras
        if self.measures.time <= 50:
            if (tuple([matrixyinicial,matrixxinicial]) not in pathToNode) and clearListPath == False and tuple([matrixyinicial,matrixxinicial]) != (inicialCols,inicialLines):
                pathToNode.append(tuple([matrixyinicial,matrixxinicial]))
        else:
            if (tuple([matrixyinicial,matrixxinicial]) not in pathToNode) and clearListPath == False:
                pathToNode.append(tuple([matrixyinicial,matrixxinicial]))  
        
        
        
        
        if self.measures.time >= 40 and tuple([matrixyinicial,matrixxinicial]) == (inicialCols,inicialLines) and resetPathToNode == False and mapEnded == False and alreadyUpdatedAdjacenInicialvertex == False:   #Atualizar a adjacencia da posicaçao inicial
            #SÓ PODE ENTRAR UMA VEZ
            #numberNodesAux = numberNodes
            #adjacente = numberNodesAux - 1
            adjacentCell_To_initialNode = ()
            if pathToNode != []:
                firstCellPathToNodeColx = pathToNode[0][0] #30
                firstCellPathToNodeColy = pathToNode[0][1] #9
            possibleCell1 = (firstCellPathToNodeColx + 1, firstCellPathToNodeColy) #31,9, andar um para a direita	
            possibleCell2 = (firstCellPathToNodeColx, firstCellPathToNodeColy + 1) #30, 10 andar 1 para baixo
            possibleCell3 = (firstCellPathToNodeColx - 1, firstCellPathToNodeColy) #29,9 andar um para a esquerda
            possibleCell4 = (firstCellPathToNodeColx, firstCellPathToNodeColy - 1) #30,8 andar um para cima

            for element in nodes:
                if element[5] == possibleCell1:
                    adjacentCell_To_initialNode = possibleCell1
                    break
                elif element[5] == possibleCell2:
                    adjacentCell_To_initialNode = possibleCell2
                    break
                elif element[5] == possibleCell3:
                    adjacentCell_To_initialNode = possibleCell3
                    break
                elif element[5] == possibleCell4:
                    adjacentCell_To_initialNode = possibleCell4
                    break

            adjacente = ""
            if adjacentCell_To_initialNode != ():
                for element in nodes:
                    if element[5] == adjacentCell_To_initialNode:
                        adjacente = element[0]

            nodes[0] = [nodes[0][0], adjacente.__str__(), pathToNode, len(pathToNode), nodes[0][4], nodes[0][5]]
            #print("ALTEREI O VERTICE INICIAL")
            clearListPath = True
            resetPathToNode = True  
            alreadyUpdatedAdjacenInicialvertex == True

        print("clearlist",clearListPath)
        print("resetpath",resetPathToNode)
        
        
        if clearListPath == True:
            if pathToNode != []:
                for i in range(0, len(pathToNode)):   #percorre a lista e retira o ultimo elemento
                    if i == (len(pathToNode)-1):
                        lastElementBeforeClear = pathToNode[i]
                #pathToNode.clear()  #mete a lista vazia uma vez quando o clearLIstPath é true e a lista elementos la dentro
                pathToNode = []
                            
        if (matrixyinicial, matrixxinicial) != lastElementBeforeClear:  #se o ultimo elemento da lista for diferente da posiçao da celula atual, metemos false
            clearListPath = False
            resetPathToNode = False
            
        #Adicionar os beacons à lista com as direçoes
        if self.measures.ground != -1:
            if DirectionsAndTargets == [] and directionsAndTargetsMatrix == []:  #Adicionar o primeiro valor do beacon inicial
                DirectionsAndTargets.append([round(x,1), round(y,1)])
                directionsAndTargetsMatrix.append([matrixyinicial,matrixxinicial])
                nodes.append([numberNodes.__str__(), zero.__str__(), [(matrixyinicial,matrixxinicial)], 0, "B", (matrixyinicial, matrixxinicial)])
                numberNodes = numberNodes + 1
            elif DirectionsAndTargets != [] and directionsAndTargetsMatrix != []:
                for i in range(0, len(DirectionsAndTargets)):
                    beaconInicial = False   #para evitar ele voltar a adicionar o beacon inicial qnd passa pelo inicio
                    diffX = abs(round(DirectionsAndTargets[i][0] - round(x,1),1))
                    diffY = abs(round(DirectionsAndTargets[i][1] - round(y,1),1))
                    xBeaconInicialDiff = abs(round(DirectionsAndTargets[0][0] - round(x,1),1))
                    yBeaconInicialDiff = abs(round(DirectionsAndTargets[0][1] - round(y,1),1))
                    if xBeaconInicialDiff >= 0 and xBeaconInicialDiff <= 0.6 and yBeaconInicialDiff >= 0 and yBeaconInicialDiff <= 0.6:
                        beaconInicial = True
                    if diffX >= 0 and diffX <= 1 and diffY >= 0 and diffY <= 1: #antes estava 0.9
                        alreadyInListDirecitonsAndTargets = True    #Encontrou um elemento na lista aproximado às coordenadas do x e y atual do robo
                    if i == (len(DirectionsAndTargets)-1):	#ultimo elemento
                        #print(i)
                        subX = abs(round(DirectionsAndTargets[i][0] - round(x,1),1))   #diferença entre o ultimo elemento e o x a adicionar
                        #print(subX)
                        subY = abs(round(DirectionsAndTargets[i][1] - round(y,1),1))   #diferença entre o ultimo elemento e o y a adicionar
                        #print(subY)
                        #print("\n")
                        #(subX >= 1 and subY >= 0 and subY <= 0.1) or (subY >= 1 and subX >= 0 and subX <= 0.1)
                        if (subX >= 1 or subY >= 1) and diffX >= 0.2 and diffY >= 0.2 and beaconInicial == False and alreadyInListDirecitonsAndTargets == False:  #horizontal/vertical                
                            DirectionsAndTargets.append([round(x,1), round(y,1)])
                            directionsAndTargetsMatrix.append([matrixyinicial,matrixxinicial])
                            for i in range(0, len(nodes)):
                                nodePos = nodes[i][5]
                                if tuple([matrixyinicial, matrixxinicial]) == nodePos:
                                    posNodeInList = i
                            if posNodeInList != -1:
                                nodes.append([nodes[posNodeInList][0], nodes[posNodeInList][1],pathToNode, len(pathToNode), "B", (matrixyinicial, matrixxinicial)])
                            else:
                                #numberNodesAux = numberNodes
                                adjacente = self.calculate_adjacent(pathToNode) 
                                nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "B", (matrixyinicial, matrixxinicial)])
                                numberNodes = numberNodes + 1
                            clearListPath = True
                        #clearListPath = True
                        #resetPathToNode = True
            for element in nodes:   #Dar clear à lista se voltar a passar pela msm posição do beacon
                if element[5] == (matrixyinicial, matrixxinicial) and element[4] == 'B':
                    clearListPath = True
                    resetPathToNode = True
        
        print("NODES->", nodes)
        
        #(possibleDirections == [] and self.measures.time >= 500 and sptHasBeenCalculated == False) or (self.measures.time == 5000 and sptHasBeenCalculated == False)
        if (mapEnded == True) or (self.measures.time == 5000):  #Ja conheceu o mapa, entao vai calcular o caminho minimo
                        
            if ((matrixyinicial, matrixxinicial) == inicialCell and sptHasBeenCalculated == False) or (self.measures.time == 5000 and sptHasBeenCalculated == False):
                
                listaAuxiliarPath = []    
                print("EDGES->", edges)
                print("beacons->", beacons)        
                ##########Detetar o caminho minimo do beacon inicial aos restantes beacons#################
                inicialBeacon = beacons[0]
                for i in range(1, len(beacons)):    #Por exemplo, beacons = [('1', '13', 4), ('8', '7', 2), ('10', '9', 26), ('11', '10', 6), ('12', '23', 6)]
                    custo = 0
                    pathVertexForThisCombination = []
                    pathVertexForThisCombination = self.dijsktra(graph, inicialBeacon[0], beacons[i][0])
                    custo = self.findCostFor2Vertex(pathVertexForThisCombination, nodes)
                    custosForThisVertexANDInicialVertex.append([inicialBeacon[0], beacons[i][0], custo]) #[('1', '8', 26), ('1', '10', 5), ('1', '11', 3)]
                
                custos = []
                if  len(custosForThisVertexANDInicialVertex) == 1:  #2 BEACONS
                    listaAuxiliarPath = self.dijsktra(graph, custosForThisVertexANDInicialVertex[0][0], custosForThisVertexANDInicialVertex[0][1])  #inicial to beacon
                    listaAuxiliarPath = listaAuxiliarPath + self.dijsktra(graph, custosForThisVertexANDInicialVertex[0][1], custosForThisVertexANDInicialVertex[0][0]) #beacon to inicial
                else:
                    #print("ESTOU NO ELSE FORA DA FUNÇAO") 
                    for element in custosForThisVertexANDInicialVertex:
                        custos.append(element[2])
                    min_value = min(custos)
                    min_index = custos.index(min_value)
                    #Adicionar os vertice de custo minimo, ao beacon inicial, à lista listaAuxiliarPath
                    listaAuxiliarPath = self.dijsktra(graph, custosForThisVertexANDInicialVertex[min_index][0], custosForThisVertexANDInicialVertex[min_index][1]) #por exemplo 1,11
                    listaAuxiliarPath = self.calculateMinPathVertex(beacons, custosForThisVertexANDInicialVertex[min_index][0], custosForThisVertexANDInicialVertex[min_index][1], listaAuxiliarPath, graph, nodes)

                
                print("listaAuxiliarPath", listaAuxiliarPath)
                #[bestPathVertex.append(x) for x in listaAuxiliarPath if x not in bestPathVertex or x == '1'] #evitar elementos duplicados exceto o primeiro
                for i in range(0,len(listaAuxiliarPath)):
                    if i < (len(listaAuxiliarPath)-1):
                        if listaAuxiliarPath[i] != listaAuxiliarPath[i+1]:
                            bestPathVertex.append(listaAuxiliarPath[i])
                    elif i == (len(listaAuxiliarPath)-1):
                        bestPathVertex.append(listaAuxiliarPath[i])
                        
                print("BEST_PATH_VERTEX->", bestPathVertex)
                #Buscar o path completo com base nos vertices do shortest path
                for i in range(0,len(bestPathVertex)):
                    if i == 0 and bestPathVertex[i] == '1':
                        finalPath.append(tuple([24,10]))
                    if i < (len(bestPathVertex)-1):
                        pathAndAdjacenciasForThisVertix = []
                        pathAoContrario = []
                        adjacenteAoNodeAtual = 0
                        listToBeAdd = []
                        for node in nodes:
                            #print(node)
                            if bestPathVertex[i+1] == node[0] and bestPathVertex[i] == node[1]:
                                #print("OLA")
                                pathAndAdjacenciasForThisVertix.append(node[2])
                            elif bestPathVertex[i] == node[0] and bestPathVertex[i+1] == node[1]: #trocar, robo veio na direção oposta
                                #print("OLA TROCAR")
                                #print("ELEMENT:", element)
                                #print("node2", node[2][::-1])
                                pathAoContrario.append(node[2][::-1])
                                adjacenteAoNodeAtual = node[1]
                                for elementNode in nodes:
                                    if elementNode[0] == adjacenteAoNodeAtual:
                                        addElement = [elementNode[5]]
                                        #print("addElement->", addElement)
                                        #pathAoContrario = pathAoContrario + addElement
                                        pathAoContrario.append(addElement) #= pathAoContrario + elementNode[5]
                                        break
                                #print("pathAoContrario->", pathAoContrario)
                                for elements in pathAoContrario:	#Meter no formato correto
                                    for element in elements:
                                        listToBeAdd.append(element)
                                pathAndAdjacenciasForThisVertix.append(listToBeAdd)
                                        
                        #print("pathAndAdjacenciasForThisVertix:", pathAndAdjacenciasForThisVertix)
                        if len(pathAndAdjacenciasForThisVertix) == 1:
                            finalPathAux.append(tuple(pathAndAdjacenciasForThisVertix[0]))
                        elif len(pathAndAdjacenciasForThisVertix) > 1:
                            #for element in pathAndAdjacenciasForThisVertix:
                            #print("DENTRO:",pathAndAdjacenciasForThisVertix)
                            #print(tuple(min(pathAndAdjacenciasForThisVertix, key=lambda coll: len(coll))))
                            finalPathAux.append(tuple(min(pathAndAdjacenciasForThisVertix, key=lambda coll: len(coll))))
                            
                print("finalPathAux->", finalPathAux)    
                for elementsTuple in finalPathAux:
                    for element in elementsTuple:
                        finalPath.append(element)
                        
                sptHasBeenCalculated = True
                        
            print("finalPath->", finalPath)
            finalPathFileAux = []
            for element in finalPath:   #ADicionar o final path ao path, q vai ser passado ao ficheiro, e fazer as devidas alterações
                if (element[0] % 2 == 0) and (element[1] % 2 == 0):
                    xcol = element[0] -24
                    yline = (element[1] - 10)*(-1)
                    addElement = (xcol,yline)
                    finalPathFileAux.append(addElement)
            #print(xcol, yline)
    
        
    
            for i in range(0,len(finalPathFileAux)):    #Nao adicionar os repetidos
                if i <= (len(finalPathFileAux)-2): #percorre a lista até à penultima posiçao
                    if finalPathFileAux[i] != finalPathFileAux[i+1]:
                        finalPathFile.append(finalPathFileAux[i])
                elif i ==  (len(finalPathFileAux)-1):   #Ultima posiçao         
                    finalPathFile.append(finalPathFileAux[i])
                
            #print("finalPathFile->", finalPathFile)
                
            # if possibleDirections == [] and self.measures.time >= 500: #Dar tempo até ele encontrar uma direção, 100ms
            #     for i in range(1, len(DirectionsAndTargets)):
            #         print("")
            if (possibleDirections == [] and self.measures.time >= 500 and sptHasBeenCalculated == True) or (self.measures.time == 5000 and sptHasBeenCalculated == True):       
                with open(out_file, 'w') as out:
                    for i in finalPathFile:
                        out.write(str(i[0]) + ' ' + str(i[1]))
                        out.write('\n')
                    self.finish()
            
            
class Map():
    def __init__(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        
        self.labMap = [[' '] * (CELLCOLS*2-1) for i in range(CELLROWS*2-1) ]
        i=1
        for child in root.iter('Row'):
           line=child.attrib['Pattern']
           row =int(child.attrib['Pos'])
           if row % 2 == 0:  # this line defines vertical lines
               for c in range(len(line)):
                   if (c+1) % 3 == 0:
                       if line[c] == '|':
                           self.labMap[row][(c+1)//3*2-1]='|'
                       else:
                           None
           else:  # this line defines horizontal lines
               for c in range(len(line)):
                   if c % 3 == 0:
                       if line[c] == '-':
                           self.labMap[row][c//3*2]='-'
                       else:
                           None
               
           i=i+1


rob_name = "pClient1"
host = "localhost"
pos = 1
mapc = None

for i in range(1, len(sys.argv),2):
    if (sys.argv[i] == "--host" or sys.argv[i] == "-h") and i != len(sys.argv) - 1:
        host = sys.argv[i + 1]
    elif (sys.argv[i] == "--pos" or sys.argv[i] == "-p") and i != len(sys.argv) - 1:
        pos = int(sys.argv[i + 1])
    elif (sys.argv[i] == "--robname" or sys.argv[i] == "-r") and i != len(sys.argv) - 1:
        rob_name = sys.argv[i + 1]
    elif (sys.argv[i] == "--map" or sys.argv[i] == "-m") and i != len(sys.argv) - 1:
        mapc = Map(sys.argv[i + 1])
    else:
        print("Unkown argument", sys.argv[i])
        quit()

if __name__ == '__main__':
    rob=MyRob(rob_name,pos,[0.0,60.0,-60.0,180.0],host)
    if mapc != None:
        rob.setMap(mapc.labMap)
        rob.printMap()
    
    rob.run()
import sys
from croblink import *
from math import *
import xml.etree.ElementTree as ET

CELLROWS=7
CELLCOLS=14
out_file = "mappingC2.map"

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
    
    def removeElement(self, lista, x, y):
        # for element in lista:
        #     if x == element[0] and y == element[1]:
        #         lista.remove([x, y, element[2], element[3]])
        #SECALHAR alterar para remover as que vao para o msm sitio
        auxList = []
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            if subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.7:     #subX <= 0.2
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
            if subX >= 0 and subX <= 0.6 and subY >= 0 and subY <= 0.7:     #x <= 0.5; y <= 0.6
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
        x = 0
        y = 0
        compass = 0
        for element in lista:
            subtractionx = abs(round(element[0] - xvar,1))
            subtractiony = abs(round(element[1] - yvar,1))
			# or (subtractionx == 0.2 and subtractiony == 0) or (subtractionx == 0.2 and subtractiony == 0.1)
			# subtractionx <= 0.1 and subtractionx >= 0 and subtractiony <= 0.1 and subtractiony >= 0
			#(bussola >= 65 and bussola <= 125)
            if bussola >= -125 and bussola <= -60:	#vertical para baixo
                subtractionBussola = bussola - element[3]      
                if ((subtractionx == 0 and subtractiony == 0) or (subtractionx == 0.1 and subtractiony == 0) or (subtractionx == 0 and subtractiony == 0.1) or (subtractionx == 0.1 and subtractiony == 0.1)) and subtractionBussola <= 12 and subtractionBussola >= -25: #Estava a 2; 3 eventualmente aumentar mais, tipo 5
                    diffOK = True
                    direction = element[2]
                    x = element[0]
                    y = element[1]
                    compass = element[3]
            elif bussola >= 65 and bussola <= 125:	#vertical para cima
                subtractionBussola = bussola - element[3]      
                if ((subtractionx == 0 and subtractiony == 0) or (subtractionx == 0.1 and subtractiony == 0) or (subtractionx == 0 and subtractiony == 0.1) or (subtractionx == 0.1 and subtractiony == 0.1)) and subtractionBussola <= 25 and subtractionBussola >= -12: #Estava a -2; -3
                    diffOK = True
                    direction = element[2]
                    x = element[0]
                    y = element[1]
                    compass = element[3]
            elif bussola >= -25 and bussola <= 25 and element[3] >= -30 and element[3] <= 30:   #horizontal da esquerda para a direita, estava a 20
                if ((subtractionx == 0 and subtractiony == 0) or (subtractionx == 0.1 and subtractiony == 0) or (subtractionx == 0 and subtractiony == 0.1) or (subtractionx == 0.1 and subtractiony == 0.1)):
                    diffOK = True
                    direction = element[2]
                    x = element[0]
                    y = element[1]
                    compass = element[3]
            #(bussola <= -160 or bussola >= 160) and (element[3] <= -155 or element[3] >= 155)
            elif (bussola <= -160 or bussola >= 160) and (element[3] <= -150 or element[3] >= 150):   #horizontal da direita para a esquerda, so estava else
                if ((subtractionx == 0 and subtractiony == 0) or (subtractionx == 0.1 and subtractiony == 0) or (subtractionx == 0 and subtractiony == 0.1) or (subtractionx == 0.1 and subtractiony == 0.1)):
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
    
    def changeRoutCompass(self, thislist, x, y, compass):  #Turn Right following the direction of compass, ALTERAR esta funçao e adicionar a bussola do robo. Testar
        sameLine = False
        xrem = 0
        yrem = 0
        for element in thislist:
            subtractX = abs(round(element[0] - x,1))
            subtractY = abs(round(element[1] - y,1))
            if subtractX <= 0.7 and subtractX >= 0.0 and subtractY <= 0.7 and subtractY >= 0.0 and element[2] == 'direita' and element[3] >= -118.0 and element[3] <= -105.0 and compass >= -40 and compass <= 20:
                sameLine = True
                xrem = element[0]
                yrem = element[1]
        return sameLine, xrem, yrem
    
    def doneDirection(self, removeList, x, y):
        #ALTERAR, a removedList vai ter tb  a direçao e o compass, NAO É PRECISO
        directionDone = False
        for element in removeList:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            if subX >= 0 and subX <= 0.7 and subY >= 0 and subY <= 0.5: #eventualmente pode-se aumentar para 0.8, antes o y estava 0.1
                directionDone = True
        return directionDone
    
    def checkCoordinatesInList(self, lista, x, y):    #verifica se as coordenadas (aproximadas, nao iguais) x,y da interseçao ja se encontram na lista das direçoes
        alreadyIn = False
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            if subX >= 0 and subX <= 0.2 and subY >= 0 and subY <= 0.2:
                alreadyIn = True
        return alreadyIn 
        
    def sameCoordinateInList(self, lista, x, y):
        #Ver se a diferença entre o x,y das coordenadas do robo e da direçao da lista é superior
        #a 0.2 para se puder adicionar outra 
        same = False
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            if subX >= 0 and subX <= 0.2 and subY >= 0 and subY <= 0.2:
                same = True
        return same
    
    def checkIfDirectionDone(self, lista, x, y, compass):   #Verifica se uma direçao ja foi feita "por outro lado", entroncamento
        #ADICIONAR A POSSIBILIDADE DE NOS CRUZAMENTOS ELE NAO CRIAR UMA DIREÇAO "direita", E CRIAR UMA "esquerda", pq por exemplo, o sensor inicialmente deteta 0's à esquerda, FEITO!!
        done = False
        xToRemove = 0
        yToRemove = 0
        directionToRemove = ""
        compassToRemove = 0
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            #Alguma direçao na horizontal da esq para a direita e proximo do x,y da direçao
            if element[3] >= -30 and element[3] <= 30 and subX >= 0 and subX <= 0.6 and subY >= 0 and subY <= 0.6:	#antes estava -25
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
            elif element[3] >= -118 and element[3] <= -65 and subX >= 0 and subX <= 0.6 and subY >= 0 and subY <= 0.6:
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
            elif element[3] >= 65 and element[3] <= 115 and subX >= 0 and subX <= 0.6 and subY >= 0 and subY <= 0.6:
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
            elif (element[3] <= -160 or element[3] >= 160) and subX >= 0 and subX <= 0.6 and subY >= 0 and subY <= 0.6:
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
        return done, xToRemove, yToRemove, directionToRemove, compassToRemove
    
    def coordinatesDoneInCross(self, lista, x, y, compass, itsACross):
        #Verifica se o robo a ir numa determinada direçao (valor bussola), num cruzamento, faz um caminho em frente e remove a direçao a determinada direçao
        done = False
        xRemove = 0
        yRemove = 0
        directionRemove = ""
        compassRemove = 0
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            #Encontrou uma direçao muito proxima e é um cruzamento
            if subX >= 0 and subX <= 0.6 and subY >= 0 and subY <= 0.6 and itsACross == True:
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
            if subX >= 0 and subX <= 0.5 and subY >= 0 and subY <= 0.5:     #subX >= 0 and subX <= 0.5 and subY >= 0 and subY <= 0.6
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
    
    def avoidCyclesBol(self, lista, x, y, compass):
        turnLeftToAvoidCycle = False
        #global avoidCyclesUp, avoidCyclesDown, avoidCyclesComeFromLeft, avoidCyclesComeFromRight
        xCycle = 0
        yCycle = 0
        compassCycle = 0
        
        for element in lista:
            #Robo passou numa direçao na horizontal da esquerda para a direita
            if x == element[0] and y == element[1] and compass >= -20 and compass <= 20 and element[2] >= -20 and element[2] <= 20:
                #avoidCyclesComeFromLeft = avoidCyclesComeFromLeft + 1
                #element[3] = avoidCyclesComeFromLeft    #MUDAR! para element[3] = element[3] + 1 em tds os elifs
                element[3] = element[3] + 1
            #Robo passou numa direçao na horizontal da direita para a esquerda
            elif x == element[0] and y == element[1] and (compass <= -165 or compass >= 165) and (element[2] <= -165 or element[2] >= 165):
                #avoidCyclesComeFromRight = avoidCyclesComeFromRight + 1
                #element[3] = avoidCyclesComeFromRight
                element[3] = element[3] + 1
            #Robo passou numa direçao na vertical de cima para baixo
            elif x == element[0] and y == element[1] and compass >= -110 and compass <= -70 and element[2] >= -110 and element[2] <= -70:
                #avoidCyclesDown = avoidCyclesDown + 1
                #element[3] = avoidCyclesDown
                element[3] = element[3] + 1
            #Robo passou numa direçao na vertical de baixo para cima
            elif x == element[0] and y == element[1] and compass >= 70 and compass <= 110 and element[2] >= 70 and element[2] <= 110:
                #avoidCyclesUp = avoidCyclesUp + 1
                #element[3] = avoidCyclesUp
                element[3] = element[3] + 1
                
        for element in lista:
            #Ja passou 4 vezes por esse x e y, e atualmente o robo esta nesse x e y, entao vira direita
            #subX = abs(round(element[0] - x,1))
            #subY = abs(round(element[1] - y,1))
            #element[3] == 4 and x == element[0] and y == element[1]
            if element[3] == 6 and x == element[0] and y == element[1] and compass >= -20 and compass <= 20 and element[2] >= -20 and element[2] <= 20: #esq para direita
                turnLeftToAvoidCycle = True
                element[3] == 0
                print("CONTADOR DAS COORDENADAS REPETIDAS A 0")
                xCycle = element[0]
                yCycle = element[1]
                compassCycle = element[2]
            elif element[3] == 6 and x == element[0] and y == element[1] and (compass <= -165 or compass >= 165) and (element[2] <= -165 or element[2] >= 165): #direita para esq
                turnLeftToAvoidCycle = True
                element[3] == 0
                print("CONTADOR DAS COORDENADAS REPETIDAS A 0")
                xCycle = element[0]
                yCycle = element[1]
                compassCycle = element[2]
            elif element[3] == 6 and x == element[0] and y == element[1] and compass >= -110 and compass <= -70 and element[2] >= -110 and element[2] <= -70: #baixo
                turnLeftToAvoidCycle = True
                element[3] == 0
                print("CONTADOR DAS COORDENADAS REPETIDAS A 0")
                xCycle = element[0]
                yCycle = element[1]
                compassCycle = element[2]
            elif element[3] == 6 and x == element[0] and y == element[1] and compass >= 70 and compass <= 110 and element[2] >= 70 and element[2] <= 110: #cima
                turnLeftToAvoidCycle = True
                element[3] == 0
                print("CONTADOR DAS COORDENADAS REPETIDAS A 0")
                xCycle = element[0]
                yCycle = element[1]
                compassCycle = element[2]
                
        return turnLeftToAvoidCycle, xCycle, yCycle, compassCycle
    
    def oppositeCompassButSameDirection(self, lista, x, y, compass, lastX, lastY, lastDirection, lastCompass, lastOppTurnRight, lastOppTurnLeft):
        oppositeCompassTurnRight = False
        opossiteCompassTurnLeft = False
        xRem = 0
        yRem = 0
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
        theyAreACycle = False
        for element in lista:
            subX = abs(round(element[0] - x,1))
            subY = abs(round(element[1] - y,1))
            #if x == element[0] and y == element[1] and compass >= -20 and compass <= 20 and element[2] >= -20 and element[2] <= 20     #ANTES
            if subX >= 0 and subX <= 0.2 and subY >= 0 and subY <= 0.2 and compass >= -20 and compass <= 20 and element[2] >= -20 and element[2] <= 20: #esq para direita
               theyAreACycle = True
            elif subX >= 0 and subX <= 0.2 and subY >= 0 and subY <= 0.2 and compass >= 70 and compass <= 110 and element[2] >= 70 and element[2] <= 110: #baixo para cima
                theyAreACycle = True
            elif subX >= 0 and subX <= 0.2 and subY >= 0 and subY <= 0.2 and compass >= -110 and compass <= -70 and element[2] >= -110 and element[2] <= -70: #cima para baixo
                theyAreACycle = True
            elif subX >= 0 and subX <= 0.2 and subY >= 0 and subY <= 0.2 and (compass <= -160 or compass >= 160) and (element[2] <= -160 or element[2] >= 160):   #direita para esq
                theyAreACycle = True
        return theyAreACycle

    def run(self):
        global knowing, learningLeft, turningLeft,turningRight, possibleDirections, checkCompassRem, direction, itsACross, frente, directionRemCross, compassRemCross, waitABit, addTolist, bussula, checkXrem, checkYrem, xByCompass, yByCompass, followCompass, waitAddToList, startCounting, removedDirections, coordinatesDone, doneCross, xRemCross, yRemCross,matrixxinicial,matrixyinicial,aux,aux2,prev_dir,prev_char,dir,xinicial,yinicial,alreadysubtracted
        global notDoneLetsTurnR_PD, dontAddRightDir_PD, notDoneLetsTurnR_RD, dontAddRightDir_RD, maybeDeadEnd, contador, haveONEs, checkDiff, checkDirection
        global oppositeCompassTurnLeft, oppositeCompassTurnRight, oppositeCompassX, oppositeCompassY, oppositeCompassDirection, oppositeCompassCompass
        global isACycle, xVarCycle, yVarCycle, compassVarCycle
        global coordinatesCycle
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
        bussula = 0             #pode ser removido
        checkXrem = 0
        checkYrem = 0
        checkDiff = False       #Podera eliminar-se
        checkDirection = ""
        xByCompass = 0
        yByCompass = 0
        followCompass = False
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
        xVarCycle = 0
        yVarCycle = 0
        compassVarCycle = 0

        self.matrix = [[' ' for x in range(49)] for y in range(21)] #matriz
        matrixxinicial = 10
        matrixyinicial = 24
        self.readSensors()
        prev_char = " "
        prev_dir = " "
        alreadysubtracted = False
        

        if self.measures.time == 0:     #Coordenadas da posição inicial
            xinicial = self.measures.x
            yinicial = self.measures.y

        aux = round(xinicial,1)
        aux2= round(yinicial,1)
        dir = "R"
        
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
        global knowing, checkCompassRem, direction, itsACross, waitABit, checkXrem, checkYrem, waitAddToList, doneCross, xRemCross, yRemCross, notDoneLetsTurnR_PD, dontAddRightDir_PD, notDoneLetsTurnR_RD, dontAddRightDir_RD, xVarCycle, yVarCycle, coordinatesCycle,matrixxinicial,matrixyinicial,aux,aux2,prev_dir,prev_char,dir,xinicial,yinicial,alreadysubtracted
        global possibleDirections,removedDirections,coordinatesDone   #Possiveis direçoes para cada posição do entroncamento/ direçoes eliminadas apos terem sido feitas/ coordenadas feitas
        global learningLeft, turningLeft, turningRight, frente, directionRemCross, compassRemCross, addTolist,bussula,xByCompass,yByCompass,followCompass, startCounting, maybeDeadEnd, contador, haveONEs, checkDiff, checkDirection, isACycle, compassVarCycle
        global oppositeCompassTurnLeft, oppositeCompassTurnRight, oppositeCompassX, oppositeCompassY, oppositeCompassDirection, oppositeCompassCompass
        done = False
        xDone = 0
        yDone = 0
        directionDone = ""
        compassDone = 0
        alreadyExist = False
        
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
        
        #Centrar o robo
        if (lineThrowRobot == ['0','1','1'] or lineThrowRobot == ['0','0','1'])  and pathLeft != ['1'] and pathRight != ['1']:
            print('Rotate slowly right')
            self.driveMotors(0.08,0.03) #0.15, 0.06
        elif (lineThrowRobot == ['1','1','0'] or lineThrowRobot == ['1','0','0']) and pathRight != ['1'] and pathLeft != ['1']:
            print('Rotate slowly left')
            self.driveMotors(0.03,0.08) #0.06, 0.15
              
        
        print("lasthaveONEs-->", haveONEs)
              
        if pathLeft == ['1'] or pathRight == ['1']: #Encontrou 1's
            maybeDeadEnd = False 
            haveONEs = True 
        
        
        if self.measures.lineSensor == ['0','0','0','0','0','0','0'] and haveONEs == True: #and haveONEs == True
            #Marcha atrás
            print("MARCHA-ATRASS")
            self.driveMotors(-0.1,-0.1) # (-0.1)eventualmente diminuir menos
            startCounting = False
            waitAddToList = 0
            addTolist = False   #Caso ele esteja a true volta a False, pq se nao fizermos isto ele vai ficar a true pq o waitAddTolist so conta se o startCounting for verdadeiro
            #maybeDeadEnd = False
                
        elif self.measures.lineSensor == ['0','0','0','0','0','0','0'] and haveONEs == False:
            #self.driveMotors(-0.1,-0.1)
            maybeDeadEnd = True
            
        if maybeDeadEnd == True:
            contador = contador + 1 
            if contador < 20: #horizontal na direita
                self.driveMotors(-0.15,+1)  #Virar À esquerda 
                #Virar até ficar ao contrario
                print("ITS A DEAD-END, TURN LEFT")
            elif contador == 20:
                contador = 0
                self.driveMotors(0.1,0.1)
            
        
        
       
      
        
        
        if possibleDirections == [] and self.measures.time >= 500: #Dar tempo até ele encontrar uma direção, 100ms
            self.finish()
        
        
        
        #PODERA ELIMINAR-SE ESTE IF
        if self.measures.time == 0 and self.measures.time == 1:    
            self.driveMotors(0.15, 0.15) #Acelarar no inicio para evitar q o proximo ciclo continue na posição inicial
        
            
        doneCross, xRemCross, yRemCross, directionRemCross, compassRemCross = self.coordinatesDoneInCross(possibleDirections, self.measures.x, self.measures.y, self.measures.compass, itsACross)
        if doneCross == True and addTolist == False:
            self.removeElement(possibleDirections, xRemCross, yRemCross)
            removedDirections.append([xRemCross, yRemCross, directionRemCross, compassRemCross])
        
        #otherDirectionsLoop == True
        #SECALHAR, adicionar uma condiçao se houver 1's, pq pode haver situaçoes, como da ultima print, onde ainda tem 0's e tenta virar para a dir correspondente    
        if addTolist == False:
            # findValue, direction, xremove, yremove, bussula = self.fun1(possibleDirections, self.measures.x, self.measures.y)
            checkDiff, checkDirection, checkXrem, checkYrem, checkCompassRem = self.checkDifference(possibleDirections, self.measures.x, self.measures.y, self.measures.compass, checkXrem, checkYrem, checkDirection, checkCompassRem)
            oppositeCompassTurnLeft, oppositeCompassTurnRight, oppositeCompassX, oppositeCompassY, oppositeCompassDirection, oppositeCompassCompass = self.oppositeCompassButSameDirection(possibleDirections, self.measures.x, self.measures.y, self.measures.compass, oppositeCompassX, oppositeCompassY, oppositeCompassDirection, oppositeCompassCompass, oppositeCompassTurnRight, oppositeCompassTurnLeft)
            #followCompass, xByCompass, yByCompass = self.changeRoutCompass(possibleDirections, self.measures.x, self.measures.y, self.measures.compass)
            
        done, xDone, yDone, directionDone, compassDone = self.checkIfDirectionDone(possibleDirections, self.measures.x, self.measures.y, self.measures.compass)
        if done == True and addTolist == False:  #and followCompass == False é auxiliar, vai ser alterado
            self.removeElement(possibleDirections, xDone, yDone)
            removedDirections.append([xDone, yDone, directionDone, compassDone])
            
            
        print("startCounting------>", startCounting)
        
        if startCounting == True:
            waitAddToList = waitAddToList + 1
            
        print("waitAddToList------->", waitAddToList)
        
      
        
        
        #As vezes pode bugar pq nao encontra [1,1,1,1,1,1,1], logo um dos turning fica a true
        if pathRight == ['1'] and pathLeft == ['1'] and turningLeft == False and turningRight == False:  #and turnRight == False 
            notDoneLetsTurnR_PD, dontAddRightDir_PD = self.pathOnLeftAlreadyDoneEntroncamentos(possibleDirections, self.measures.x, self.measures.y, self.measures.compass)
            notDoneLetsTurnR_RD, dontAddRightDir_RD = self.pathOnLeftAlreadyDoneEntroncamentos(removedDirections, self.measures.x, self.measures.y, self.measures.compass)
            
        
        
        if isACycle == False and xVarCycle == 0 and yVarCycle == 0:
            isACycle, xVarCycle, yVarCycle, compassVarCycle = self.avoidCyclesBol(coordinatesDone, self.measures.x, self.measures.y, self.measures.compass)
            if xVarCycle != 0 and yVarCycle != 0 and ([xVarCycle,yVarCycle,compassVarCycle] not in coordinatesCycle):
                coordinatesCycle.append([xVarCycle,yVarCycle, compassVarCycle])
       
        
        if  (notDoneLetsTurnR_PD == True or notDoneLetsTurnR_RD == True) and addTolist == False and isACycle == False and self.actualCoordinatesAreACycle(coordinatesCycle, self.measures.x, self.measures.y, self.measures.compass) == False:    #isCycle = False
            #virar à direita
            self.driveMotors(+0.1,-0.07)    #self.driveMotors(+0.1,-0.08), alterei este valor
            turningRight = True
            print("Robot came from the left side, LETS TURN RIGHT!")
            
        
        if frente == True and isACycle == False and self.actualCoordinatesAreACycle(coordinatesCycle, self.measures.x, self.measures.y, self.measures.compass) == False:
            self.driveMotors(0.08,0.03) #Rotate slowly right 0.15, 0.06
            #self.driveMotors(0.1, 0.1)
            print("Foward")
        
        #Secalhar meter pathRight == ['1'] and pathLeft == ['1'] para evitar o ruido do ['1'1'1'1'1'1'1'] 
        #and followCompass == False
        #and isACycle == False
        #TEMOS de adicionar and checkXRem == 0 and CheckYRem == 0, antes estava sem estes ands
        if (self.measures.lineSensor == ['1','1','1','1','1','1','1'] or self.measures.lineSensor == ['1','1','1','1','1','1','0']) and turningRight == False and turningLeft == False and itsACross == False and frente == False and (notDoneLetsTurnR_PD == False and notDoneLetsTurnR_RD == False) and oppositeCompassTurnLeft == False and oppositeCompassTurnRight == False and isACycle == False and self.actualCoordinatesAreACycle(coordinatesCycle, self.measures.x, self.measures.y, self.measures.compass) == False and checkXrem == 0 and checkYrem == 0:
            print("Lets learn left side")   #exprimentar a rodar um pouco menos
            self.driveMotors(-0.09,+0.1) #-0.1 estava a fazer bem
            #Viramos a esquerda e se encontrarmos um zero metemos true
            learningLeft = True
            # if [self.measures.x, self.measures.y] not in coordinatesDone:   #Alterar esta parte para adicionar as direçoes a direita
            #         coordinatesDone.append([self.measures.x, self.measures.y, self.measures.compass, 0])
            for element in coordinatesDone:
                if self.measures.x == element[0] and self.measures.y == element[1]:
                    alreadyExist = True
                    break
                else:
                    alreadyExist = False
            if alreadyExist == False:
                coordinatesDone.append([self.measures.x, self.measures.y, self.measures.compass, 0])
            #Sempre que passa no msm sitio contar
            if self.sameCoordinateInList(possibleDirections, self.measures.x, self.measures.y) == False and self.sameCoordinateInList(removedDirections, self.measures.x, self.measures.y) == False and self.samePosition(coordinatesDone, self.measures.x, self.measures.y, self.measures.compass) == False and dontAddRightDir_PD == False and dontAddRightDir_RD == False:
                possibleDirections.append([self.measures.x, self.measures.y, "direita", self.measures.compass])
                addTolist = True
                startCounting = True 
                
        #checkDiff == True and otherDirectionsLoop == True   and followCompass == False (findValue == True and direction == "direita" and frente == False and addTolist == False) or
        #and isACycle == False
        
        #EXPERIMENTAR VIRAR À DIREITA EM CICLOS EM VEZ DE SER À ESQUERDA
        elif (checkXrem != 0 and checkYrem != 0 and checkDirection == "direita" and addTolist == False) or (oppositeCompassTurnRight == True and addTolist == False) and isACycle == False and self.actualCoordinatesAreACycle(coordinatesCycle, self.measures.x, self.measures.y, self.measures.compass) == False:  #SO ENTRA NOS OUTROS ELIF'S SE O findValue FOR False, o otherDirectionsLoop for false
            # if pathLeft == ['1'] and sensorRight == ['0','0']:       #self.measures.lineSensor == ['1','1','1','1','1','0','0']
            #     frente = True
            #     turningRight = False
            #     print("Go front R")
            self.driveMotors(+0.1,-0.07)
            turningRight = True
            print("Lets turn RIGHT (OTHER DIRECTION)")
        #checkDiff == True and otherDirectionsLoop == True    and followCompass == False (findValue == True and direction == "esquerda"  and frente == False and addTolist == False) or
        # or isACycle == True, and frente == False                              #                                                           #
        elif (checkXrem != 0 and checkYrem != 0 and checkDirection == "esquerda" and addTolist == False) or (oppositeCompassTurnLeft == True and addTolist == False) or isACycle == True or self.actualCoordinatesAreACycle(coordinatesCycle, self.measures.x, self.measures.y, self.measures.compass) == True:  #SO ENTRA NOS OUTROS ELIF'S SE O findValue FOR False, o otherDirectionsLoop for false
            # if pathRight == ['1'] and sensorLeft == ['0','0']:    #TIREI ISTO
            #     frente = True
            #     turningLeft = False
            #     print("Go front L")
            self.driveMotors(-0.07,+0.1)
            turningLeft = True
            print("Lets turn LEFT (OTHER DIRECTION)")
                         
        
        elif pathRight == ['1'] and self.measures.lineSensor != ['1','1','1','1','1','1','1'] and self.measures.lineSensor != ['1','1','1','0','1','1','1'] and self.measures.lineSensor != ['1','1','0','1','1','1','1'] and self.measures.lineSensor != ['1','1','0','0','1','1','1'] and self.measures.lineSensor != ['1','1','0','0','0','1','1'] and self.measures.lineSensor != ['1','1','0','0','0','0','1'] and turningLeft == False and itsACross == False and frente == False and learningLeft == False:####
            print('Rotate/Knowing Right')
            turningRight = True
            self.driveMotors(+0.1,-0.03)    #-0.04
           
        #and followCompass == False and checkDiff == False
        elif pathLeft == ['1'] and turningRight == True and knowing == False and itsACross == False and frente == False and checkXrem == 0 and checkYrem == 0 and (notDoneLetsTurnR_PD == False and notDoneLetsTurnR_RD == False) and checkXrem == 0 and checkYrem == 0 and oppositeCompassTurnLeft == False and oppositeCompassTurnRight == False: 
            #self.driveMotors('0','0')   #stop
            print("WE KNOW THAT WE CAN GO FRONT (LS)")
            self.driveMotors(-0.15,+0.1)
            #Caso exista, não adiciona (SECALHAR NAO VAIS SER NECESSARIO)
            #or ([round(self.measures.x), self.measures.y] not in possibleDirections) and self.samePosition(coordinatesDone, self.measures.x, self.measures.y) == False and self.checkIfSameHorizontalPos(possibleDirections, self.measures.x, self.measures.y, self.measures.compass) == False self.checkIfSameVerticalPos(possibleDirections, self.measures.x, self.measures.compass) == False
            #(([self.measures.x, self.measures.y] not in possibleDirections) and self.checkCoordinatesInList(possibleDirections,self.measures.x,self.measures.y) == False)
            if self.checkCoordinatesInList(possibleDirections,self.measures.x,self.measures.y) == False and self.doneDirection(removedDirections, self.measures.x, self.measures.y) == False and self.samePosition(coordinatesDone, self.measures.x, self.measures.y, self.measures.compass) == False and done == False:
                #Adicionar esta posiçao ao possibleDirections
                possibleDirections.append([self.measures.x, self.measures.y, "direita", self.measures.compass])    ####### Adicionar outra direçao a lista
                addTolist = True
                startCounting = True    
            turningRight = False
            turningLeft = True
            knowing = True
            print("Virar à esquerda")
             
        # pathLeft == ['1'] and self.measures.lineSensor != ['1','1','1','1','1','1','1'] and turningRight == False
        #Momento em que descobriu q tem caminho em frente 
        #and followCompass == False    
        elif pathLeft == ['1'] and pathRight != ['1'] and turningRight == False and itsACross == False and frente == False:
            print("Rotate/Knowing left side")
            self.driveMotors(-0.03,+0.1)    #-0.04
            turningLeft = True
            # if pathRight == ['1']:
            #     #entroncamento1 = True
            #     print("WE KNOW THAT WE CAN GO FRONT (RS), marcha-atras")
            #     self.driveMotors(-0.15,-0.15)
            #     frenteE = True
            #     #knowing = False
        #and followCompass == False and checkDiff == False
        elif pathRight == ['1'] and turningLeft == True and knowing == False and itsACross == False and frente == False and checkXrem == 0 and checkYrem == 0 and (notDoneLetsTurnR_PD == False and notDoneLetsTurnR_RD == False) and checkXrem == 0 and checkYrem == 0 and oppositeCompassTurnLeft == False and oppositeCompassTurnRight == False:   #and possibleCross === False
            #self.driveMotors(0,0)   #STOP
            print("WE KNOW THAT WE CAN GO FRONT (RS)")
            self.driveMotors(+0.1,-0.15)
            #Verificar se o x,y nao esta na lista
            #or ([round(self.measures.x), self.measures.y] not in possibleDirections) and self.samePosition(coordinatesDone, self.measures.x, self.measures.y) == False and self.checkIfSameHorizontalPos(possibleDirections, self.measures.x, self.measures.y, self.measures.compass) == False and self.checkIfSameVerticalPos(possibleDirections, self.measures.x, self.measures.compass) == False
            #(([self.measures.x, self.measures.y] not in possibleDirections) and self.checkCoordinatesInList(possibleDirections,self.measures.x,self.measures.y) == False)
            if self.checkCoordinatesInList(possibleDirections,self.measures.x,self.measures.y) == False and self.doneDirection(removedDirections, self.measures.x, self.measures.y) == False and self.samePosition(coordinatesDone, self.measures.x, self.measures.y, self.measures.compass) == False and done == False:
                possibleDirections.append([self.measures.x, self.measures.y, "esquerda", self.measures.compass])   ###### Adicionar outra direcao na lista
                addTolist = True
                startCounting = True
            turningLeft = False
            turningRight = True
            knowing = True
            print("Virar a direita")
        
        #Adicionei -> and checkXrem == 0 and checkYrem == 0 and oppositeCompassTurnRight == False and oppositeCompassTurnLeft == False
        if itsACross == True and pathLeft == ['0'] and self.measures.lineSensor != ['1','1','1','1','1','1','1'] and isACycle == False and self.actualCoordinatesAreACycle(coordinatesCycle, self.measures.x, self.measures.y, self.measures.compass) == False and checkXrem == 0 and checkYrem == 0 and oppositeCompassTurnRight == False and oppositeCompassTurnLeft == False:   #Secalhar vamos ter de fazer esperar um ciclo para ver se é certo
            self.driveMotors(+0.1,-0.1)
            #itsACross = False   ####
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

        #pathLeft == ['0'] and pathRight == ['0']
        if pathLeft == ['0'] and pathRight == ['0']:    #Exprimentar isto no final dos if's. Secalhar meter este if = [0,0,1,1,1,0,0]
            turningLeft = False
            turningRight = False
            knowing = False
            #possibleCross = False   ####
            #findValue = False       ####
            #direction = ""          ####
            #Remove tb se passar nas msm coordenadas (FAZER) otherDirectionsLoop == True and 
            if addTolist == False:  #secalhar adicionar outra condiçao para remover só dps de ter realizado a direção
                # if findValue == True:
                #     self.removeElement(possibleDirections, xremove, yremove)
                #     removedDirections.append([xremove,yremove])
                #     print("Estou pronto para remover valor CERTO!")
                
                #if checkDiff == True:   #Secalhar podemos tirar esta condiçao
                if checkXrem != 0 and checkYrem != 0 and checkDirection != "" and checkCompassRem != 0:
                    self.removeElement(possibleDirections, checkXrem, checkYrem)
                    removedDirections.append([checkXrem,checkYrem, checkDirection, checkCompassRem])
                    print("Estou pronto para remover valor APROXIMADO")
                elif oppositeCompassX != 0 and oppositeCompassY != 0 and oppositeCompassDirection != "" and oppositeCompassCompass != 0:
                    self.removeElement(possibleDirections,oppositeCompassX, oppositeCompassY)
                    removedDirections.append([oppositeCompassX, oppositeCompassY, oppositeCompassDirection, oppositeCompassCompass])
                # elif followCompass == True:
                #     print("Estou pronto para remover valor proveniente da DIREÇAO DA BUSSULA")
                #     self.removeElement(possibleDirections, xByCompass, yByCompass)
                #     removedDirections.append([xByCompass,yByCompass])
                    
            itsACross = False
            learningLeft = False
            #xremove = 0
            checkCompassRem = 0
            #yremove = 0
            checkXrem = 0
            checkYrem = 0
            checkDiff = False
            checkDirection = ""
            bussula = 0     #pode ser removido
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
            xVarCycle = 0
            yVarCycle = 0
            compassVarCycle = 0
            #Falta meter os outros do cycle a 0
            
            if waitAddToList == 13:     #antes estava a 8
                addTolist = False
                startCounting = False
                waitAddToList = 0
                
            #followCompass = False
            xByCompass = 0
            yByCompass = 0
            oppositeCompassTurnLeft = False 
            oppositeCompassTurnRight = False
            oppositeCompassX = 0
            oppositeCompassY = 0
            oppositeCompassDirection = 0
            oppositeCompassCompass = 0


     



        prev_dir = dir
        prev_char = self.matrix[matrixxinicial][matrixyinicial]
       

        self.matrix[10][24] = 'I'

        if maybeDeadEnd == True and alreadysubtracted == False:             #caso haja deadend
           
            if self.measures.compass < 40 and self.measures.compass > -40:      #direita
                alreadysubtracted = True
                matrixyinicial = matrixyinicial -2
                dir = "L"

            if self.measures.compass > 140 or self.measures.compass < -140:         #esquerda
                alreadysubtracted = True
                matrixyinicial = matrixyinicial +2
                dir = "R"

            if self.measures.compass < 120 and self.measures.compass > 60:          #cima
                alreadysubtracted = True
                matrixxinicial = matrixxinicial +2
                dir = "D"

            if self.measures.compass > -120 and self.measures.compass < -60:        #baixo
                alreadysubtracted = True
                matrixxinicial = matrixxinicial -2
                dir ="U"

        if maybeDeadEnd == False:
            alreadysubtracted = False
            

                    
        if prev_char == 'I':
            if self.measures.compass < 40 and self.measures.compass > -40:      #direita
                matrixyinicial = matrixyinicial +1
                self.matrix[matrixxinicial][matrixyinicial] = '-'
                aux2 = yinicial
                aux = xinicial

            if self.measures.compass > 140 or self.measures.compass < -140:     #esquerda
                matrixyinicial = matrixyinicial -1
                self.matrix[matrixxinicial][matrixyinicial] = '-'
                aux2 = yinicial
                aux = xinicial


        if round(aux - self.measures.x,1) == -1 :                                                   #direita
            if self.measures.compass < 30 and self.measures.compass > -30:
                print("R")
                dir = "R"

                if prev_char == '-':
                    if dir == 'R':
                        matrixyinicial = matrixyinicial + 1
                        self.matrix[matrixxinicial][matrixyinicial] = ' '
                        aux = self.measures.x
                                                                                                
                if prev_char == ' ':
                    if dir == 'R':
                        matrixyinicial = matrixyinicial + 1
                        self.matrix[matrixxinicial][matrixyinicial] = '-'
                        aux = self.measures.x


            if self.measures.compass < 140 and self.measures.compass > 40:
                print("U")
                dir = "U"
                if prev_char == ' ':
                    if dir == 'U' and prev_dir =='R':
                        matrixxinicial = matrixxinicial -1 
                        self.matrix[matrixxinicial][matrixyinicial] = '|'
                        aux = self.measures.x

            if self.measures.compass > -140 and self.measures.compass < -40:
                print("D")
                dir = "D"
                if prev_char == ' ':
                    if dir == 'D' and prev_dir =='R':
                        matrixxinicial = matrixxinicial + 1 
                        self.matrix[matrixxinicial][matrixyinicial] = '|'
                        aux = self.measures.x




        if round(aux - self.measures.x,1) == 1 :                                    #esquerda
            if self.measures.compass > 140 or self.measures.compass < -140: 
                print("L")
                dir = "L"
                if prev_char == '-':
                    if dir == 'L' :
                        matrixyinicial = matrixyinicial - 1
                        self.matrix[matrixxinicial][matrixyinicial] = ' '
                        aux = self.measures.x

                if prev_char == ' ':
                    if dir == 'L' :
                        matrixyinicial = matrixyinicial - 1
                        self.matrix[matrixxinicial][matrixyinicial] = '-'
                        aux = self.measures.x

            if self.measures.compass < 140 and self.measures.compass > 40:
                print("U")
                dir = "U"
                if prev_char == ' ':
                    if dir == 'U' and prev_dir =='L':
                        matrixxinicial = matrixxinicial -1 
                        self.matrix[matrixxinicial][matrixyinicial] = '|'
                        aux = self.measures.x

            if self.measures.compass > -140 and self.measures.compass < -40:
                print("D")
                dir = "D"
                if prev_char == ' ':
                    if dir == 'D' and prev_dir =='L':
                        matrixxinicial = matrixxinicial + 1 
                        self.matrix[matrixxinicial][matrixyinicial] = '|'
                        aux = self.measures.x


        if round(aux2 - self.measures.y,1) == -1 :                                                      #Cima
            if self.measures.compass < 130 and self.measures.compass > 50:
                print("U")
                dir = "U"
                if prev_char =='|':
                    if dir == 'U' :
                            matrixxinicial = matrixxinicial -1 
                            self.matrix[matrixxinicial][matrixyinicial] = ' '
                            aux2 = self.measures.y

                if prev_char == ' ':
                    if dir == 'U' :
                        matrixxinicial = matrixxinicial -1 
                        self.matrix[matrixxinicial][matrixyinicial] = '|'
                        aux2 = self.measures.y

            if self.measures.compass < 40 and self.measures.compass > -40: 
                print("R")
                dir = "R"
                if prev_char == ' ':
                    if dir == 'R' and prev_dir =='U':
                        matrixyinicial = matrixyinicial + 1
                        self.matrix[matrixxinicial][matrixyinicial] = '-'
                        aux2 = self.measures.y

            if self.measures.compass > 140 or self.measures.compass < -140: 
                print("L")
                dir = "L"
                if prev_char == ' ':
                    if dir == 'L' and prev_dir =='U':
                        matrixyinicial = matrixyinicial -1
                        self.matrix[matrixxinicial][matrixyinicial] = '-'
                        aux2 = self.measures.y


        if round(aux2 - self.measures.y,1) == 1 :                          #baixo
            if self.measures.compass > -130 and self.measures.compass < -50:
                print("D")
                dir = "D"
                if prev_char =='|':
                     if dir == 'D' :
                        matrixxinicial = matrixxinicial + 1 
                        self.matrix[matrixxinicial][matrixyinicial] = ' '
                        aux2 = self.measures.y

                if prev_char == ' ':
                    if dir == 'D':
                        matrixxinicial = matrixxinicial + 1 
                        self.matrix[matrixxinicial][matrixyinicial] = '|'
                        aux2 = self.measures.y

            if self.measures.compass < 40 and self.measures.compass > -40: 
                print("R")
                dir = "R"
                if prev_char == ' ':
                    if dir == 'R' and prev_dir =='D':
                        matrixyinicial = matrixyinicial + 1
                        self.matrix[matrixxinicial][matrixyinicial] = '-'
                        aux2 = self.measures.y

            if self.measures.compass > 140 or self.measures.compass < -140: 
                print("L")
                dir = "L"
                if prev_char == ' ':
                    if dir == 'L' and prev_dir =='D':
                        matrixyinicial = matrixyinicial - 1
                        self.matrix[matrixxinicial][matrixyinicial] = '-'
                        aux2 = self.measures.y


        with open(out_file, 'w') as out:
            for i in self.matrix:
                out.write(''.join(i))
                out.write('\n')

            
            
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
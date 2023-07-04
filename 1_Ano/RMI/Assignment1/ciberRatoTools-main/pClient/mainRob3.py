import sys
from croblink import *
from math import *
import xml.etree.ElementTree as ET
from heuristicSPT import *

CELLROWS=7
CELLCOLS=14
out_file = "mappingC3.map"

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
                if ((subtractionx == 0 and subtractiony == 0) or (subtractionx == 0.1 and subtractiony == 0) or (subtractionx == 0 and subtractiony == 0.1) or (subtractionx == 0.1 and subtractiony == 0.1)) and subtractionBussola <= 10 and subtractionBussola >= -25: #Estava a 2; 3 eventualmente aumentar mais, tipo 5
                    diffOK = True
                    direction = element[2]
                    x = element[0]
                    y = element[1]
                    compass = element[3]
            elif bussola >= 65 and bussola <= 125:	#vertical para cima
                subtractionBussola = bussola - element[3]      
                if ((subtractionx == 0 and subtractiony == 0) or (subtractionx == 0.1 and subtractiony == 0) or (subtractionx == 0 and subtractiony == 0.1) or (subtractionx == 0.1 and subtractiony == 0.1)) and subtractionBussola <= 25 and subtractionBussola >= -10: #Estava a -2; -3
                    diffOK = True
                    direction = element[2]
                    x = element[0]
                    y = element[1]
                    compass = element[3]
            elif bussola >= -20 and bussola <= 20 and element[3] >= -30 and element[3] <= 30:   #horizontal da esquerda para a direita
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
            if element[3] >= -30 and element[3] <= 30 and subX >= 0 and subX <= 0.5 and subY >= 0 and subY <= 0.5:	#Antes estava a -25 e 0.6
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
            if subX >= 0 and subX <= 0.6 and subY >= 0 and subY <= 0.6 and itsACross == True:   #Estava a 0.6
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
                #print("CONTADOR DAS COORDENADAS REPETIDAS A 0")
                xCycle = element[0]
                yCycle = element[1]
                compassCycle = element[2]
            elif element[3] == 6 and x == element[0] and y == element[1] and (compass <= -165 or compass >= 165) and (element[2] <= -165 or element[2] >= 165): #direita para esq
                turnLeftToAvoidCycle = True
                element[3] == 0
                #print("CONTADOR DAS COORDENADAS REPETIDAS A 0")
                xCycle = element[0]
                yCycle = element[1]
                compassCycle = element[2]
            elif element[3] == 6 and x == element[0] and y == element[1] and compass >= -110 and compass <= -70 and element[2] >= -110 and element[2] <= -70: #baixo
                turnLeftToAvoidCycle = True
                element[3] == 0
                #print("CONTADOR DAS COORDENADAS REPETIDAS A 0")
                xCycle = element[0]
                yCycle = element[1]
                compassCycle = element[2]
            elif element[3] == 6 and x == element[0] and y == element[1] and compass >= 70 and compass <= 110 and element[2] >= 70 and element[2] <= 110: #cima
                turnLeftToAvoidCycle = True
                element[3] == 0
                #print("CONTADOR DAS COORDENADAS REPETIDAS A 0")
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
        # for element in beaconsLeftAux: #elimina os beacons onde já foi calculado o caminho minimo
        #     if element[0] == initialBeacon:
        #         beaconsLeftAux.remove(element)
        #     elif element[0] == beaconMinPathToIB: 
        #         beaconsLeftAux.remove(element)
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
                listaAuxiliarPath = self.dijsktra(graph, custosForThisVertexANDInicialVertex[min_index][0], custosForThisVertexANDInicialVertex[min_index][1]) #11, 10

                for element in beaconsLeftAux:
                    if element[0] == nextBeacon:
                        beaconsLeftAux.remove(element)  #Remover o beacon com o caminho minimo já calculado
                        
                custosForThisVertexANDInicialVertex = [] #clear à lista
            
            listaAuxiliarPath = listaAuxiliarPath + self.dijsktra(graph, nextBeacon, beaconsLeftAux[0][0]) #caminho do beacon do next beacon para o beacon q sobra na lista
            listaAuxiliarPath = listaAuxiliarPath + self.dijsktra(graph, beaconsLeftAux[0][0], initialBeacon) #e caminho desse beacon para o beacon inicial
            
        print("listaAuxiliarPath_RETURN->", listaAuxiliarPath)         
        return listaAuxiliarPath

    def run(self):
        global knowing, learningLeft, turningLeft,turningRight, possibleDirections, checkCompassRem, direction, itsACross, frente, directionRemCross, compassRemCross, waitABit, addTolist, bussula, checkXrem, checkYrem, xByCompass, yByCompass, followCompass, waitAddToList, startCounting, removedDirections, coordinatesDone, doneCross, xRemCross, yRemCross,matrixxinicial,matrixyinicial,aux,aux2,prev_dir,prev_char,dir,xinicial,yinicial
        global notDoneLetsTurnR_PD, dontAddRightDir_PD, notDoneLetsTurnR_RD, dontAddRightDir_RD, maybeDeadEnd, contador, haveONEs, checkDiff, checkDirection
        global oppositeCompassTurnLeft, oppositeCompassTurnRight, oppositeCompassX, oppositeCompassY, oppositeCompassDirection, oppositeCompassCompass
        global isACycle, xVarCycle, yVarCycle, compassVarCycle
        global coordinatesCycle
        global DirectionsAndTargets
        global directionsAndTargetsMatrix, numberNodes, nodes, pathToNode, cost, alreadyInListDirecitonsAndTargets, clearListPath, lastElementBeforeClear, edges, zero, resetPathToNode, beacons
        global inicialCols, inicialLines
        global finalPathAux, finalPath, bestPathVertex, sptHasBeenCalculated, finalPathFile, custosForThisVertexANDInicialVertex
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
        directionsAndTargetsMatrix = []     #vamos puder eliminar
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
        global knowing, checkCompassRem, direction, itsACross, waitABit, checkXrem, checkYrem, waitAddToList, doneCross, xRemCross, yRemCross, notDoneLetsTurnR_PD, dontAddRightDir_PD, notDoneLetsTurnR_RD, dontAddRightDir_RD, xVarCycle, yVarCycle, coordinatesCycle,matrixxinicial,matrixyinicial,aux,aux2,prev_dir,prev_char,dir,xinicial,yinicial
        global possibleDirections,removedDirections,coordinatesDone   #Possiveis direçoes para cada posição do entroncamento/ direçoes eliminadas apos terem sido feitas/ coordenadas feitas
        global learningLeft, turningLeft, turningRight, frente, directionRemCross, compassRemCross, addTolist,bussula,xByCompass,yByCompass,followCompass, startCounting, maybeDeadEnd, contador, haveONEs, checkDiff, checkDirection, isACycle, compassVarCycle
        global oppositeCompassTurnLeft, oppositeCompassTurnRight, oppositeCompassX, oppositeCompassY, oppositeCompassDirection, oppositeCompassCompass
        global DirectionsAndTargets, directionsAndTargetsMatrix, numberNodes, nodes, pathToNode, cost, alreadyInListDirecitonsAndTargets, clearListPath,lastElementBeforeClear, edges, resetPathToNode, beacons
        global inicialCols, inicialLines, zero
        global finalPathAux, finalPath, bestPathVertex, sptHasBeenCalculated, finalPathFile, custosForThisVertexANDInicialVertex
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
        #sensorLeft = self.measures.lineSensor[:2]
        #sensorRight = self.measures.lineSensor[5:]
        print(self.measures.lineSensor)
        
        #Centrar o robo
        if (lineThrowRobot == ['0','1','1'] or lineThrowRobot == ['0','0','1'])  and pathLeft != ['1'] and pathRight != ['1']:
            print('Rotate slowly right')
            self.driveMotors(0.08,0.03) #0.15, 0.06
        elif (lineThrowRobot == ['1','1','0'] or lineThrowRobot == ['1','0','0']) and pathRight != ['1'] and pathLeft != ['1']:
            print('Rotate slowly left')
            self.driveMotors(0.03,0.8) #0.06, 0.15
              
        
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
            
        print("x", self.measures.x)
        print("y", self.measures.y)
        #print("time", self.measures.time)
        print("Compass", self.measures.compass)
        print("")
        
       
        #TODO: Ir testanto para ver a parte dos ciclos, e ir vendo se é melhor usar o frente == False na parte de virar nas direçoes
        #TODO: TESTAR o C2a para ver a parte em q tirei do LETS TURN LEFT/RIGHT e tb para ver alguns valores da bussola q altere
        #BUG: Ver o pq de estar a somar +2 no least learn left side dps do beacon de cima!!!
        
        # if possibleDirections == [] and self.measures.time >= 500: #Dar tempo até ele encontrar uma direção, 100ms
        #     self.finish()
        
        # if self.measures.x == xinicial and (yfirstCellPathToNodeColxinicial - self.measures.y <= 0.6): #and self.measure.time > 20, esperar um pouco and abs(yinicial-self.measures.y<=0.6) e >= 0
        #     otherDirectionsLoop = True  #Terminou a primeira volta e agr executa as outras direçoes tds
        
        #Secalhar pode ter de se aproximar o x tb, por exemplo, 0.1
        # if self.measures.x == xinicial and (abs(yinicial- self.measures.y <= 0.6)) and self.measures.time > 50:
        #     otherDirectionsLoop = True
        #PODERA ELIMINAR-SE ESTE IF
        # if self.measures.time == 0:     #Coordenadas da posição inicial
        #     xinicial = self.measures.x
        #     yinicial = self.measures.y
        
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
        
        # #print("turningLeft-", turningLeft)
        # #print("turningRight-", turningRight)
        print("possibleDirections-> ", possibleDirections)
        print("removeDirections->", removedDirections)
        # print("coordinatesDone-->", coordinatesDone)
        # #print("findValue-", findValue)
        # print("doneCrossposNode->", doneCross)
        # print("xRemCross->", xRemCross)
        # #print("direction-", direction)
        # #print("otherDirectionsLoop", otherDirectionsLoop)
        # print("itsACross", itsACross) 
        # print("learningLeft", learningLeft)
        # #print("Knowing->", knowing)
        # #print("diffOK-->", checkDiff)
        # print("checkXrem--------->", checkXrem)
        # print("checkYrem--------->", checkYrem)
        # print("checkDirection-->", checkDirection)
        # #print("frente", frente)
        # #print("xByCompass---->", xByCompass)
        # #print("yByCompass---->", yByCompass)
        # #print("followCompass---->", followCompass)
        # #print("done-->", done)
        # print("xDone-->", xDone)
        # print("yDone-->", yDone)
        # #print("maybeDeadEnd--------->", maybeDeadEnd)
        # #print("contador------------->", contador)
        # print("oppositeCompassTurnLeft:",oppositeCompassTurnLeft)
        # print("oppositeCompassTurnRight:",oppositeCompassTurnRight)
        # print("oppositeCompassX:", oppositeCompassX)
        # print("oppositeCompassY:", oppositeCompassY)
        
        #As vezes pode bugar pq nao encontra [1,1,1,1,1,1,1], logo um dos turning fica a true
        if pathRight == ['1'] and pathLeft == ['1'] and turningLeft == False and turningRight == False:  #and turnRight == False 
            notDoneLetsTurnR_PD, dontAddRightDir_PD = self.pathOnLeftAlreadyDoneEntroncamentos(possibleDirections, self.measures.x, self.measures.y, self.measures.compass)
            notDoneLetsTurnR_RD, dontAddRightDir_RD = self.pathOnLeftAlreadyDoneEntroncamentos(removedDirections, self.measures.x, self.measures.y, self.measures.compass)
            
        #print("notDoneLetsTurnR_PD---->", notDoneLetsTurnR_PD)
        #print("dontAddRightDir_PD---->", dontAddRightDir_PD)
        #print("notDoneLetsTurnR_RD---->", notDoneLetsTurnR_RD)
        #print("dontAddRightDir_RD---->", dontAddRightDir_RD)
        print("addTolist---->", addTolist)
        if isACycle == False and xVarCycle == 0 and yVarCycle == 0:
            isACycle, xVarCycle, yVarCycle, compassVarCycle = self.avoidCyclesBol(coordinatesDone, self.measures.x, self.measures.y, self.measures.compass)
            if xVarCycle != 0 and yVarCycle != 0 and ([xVarCycle,yVarCycle,compassVarCycle] not in coordinatesCycle):
                coordinatesCycle.append([xVarCycle,yVarCycle, compassVarCycle])
        #print("isACycle--------------->", isACycle)
        print("xVarCycle----------->", xVarCycle)
        print("yVarCycle----------->", yVarCycle)
        print("coordinatesCycle", coordinatesCycle)
        
        if  (notDoneLetsTurnR_PD == True or notDoneLetsTurnR_RD == True) and addTolist == False and isACycle == False and self.actualCoordinatesAreACycle(coordinatesCycle, self.measures.x, self.measures.y, self.measures.compass) == False:    #isCycle = False
            #virar à direita
            self.driveMotors(+0.1,-0.07)    #self.driveMotors(+0.1,-0.08), alterei este valor
            turningRight = True
            
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
            if posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0 and self.checkIfNodeAlreadyInList(nodes,[nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]]) == False:
                nodes.append([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]])
                
            clearListPath = True    #verifica as duas condiçoes de cima e caso encontre igual mas o caminho tb é igual
            resetPathToNode = True
            
            print("Robot came from the left side, LETS TURN RIGHT!")
            
        
        if frente == True:
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
            if posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente != 0 and self.checkIfNodeAlreadyInList(nodes,[nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]]) == False:
                nodes.append([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]])
                   
            #elif posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False and adjacente == 0:
                #nodes.append([nodes[posNodeInList][0], nodes[posNodeInList][1], pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]])
                
            clearListPath = True    #verifica as duas condiçoes de cima e caso encontre igual mas o caminho tb é igual
            resetPathToNode = True       
                
            #Sempre que passa no msm sitio contar
            if self.sameCoordinateInList(possibleDirections, self.measures.x, self.measures.y) == False and self.sameCoordinateInList(removedDirections, self.measures.x, self.measures.y) == False and self.samePosition(coordinatesDone, self.measures.x, self.measures.y, self.measures.compass) == False and dontAddRightDir_PD == False and dontAddRightDir_RD == False:
                possibleDirections.append([self.measures.x, self.measures.y, "direita", self.measures.compass])
                DirectionsAndTargets.append([self.measures.x, self.measures.y])
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
                    numberNodesAux = numberNodes
                    adjacente = numberNodesAux - 1
                    nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                    numberNodes = numberNodes + 1

                #pathToNode.clear()
                clearListPath = True
                addTolist = True
                startCounting = True 
                
        #checkDiff == True and otherDirectionsLoop == True   and followCompass == False (findValue == True and direction == "direita" and frente == False and addTolist == False) or
        #and isACycle == False
        #EXPERIMENTAR tirar o frente == False e no debaixo tb, and frente == False
        elif (checkXrem != 0 and checkYrem != 0 and checkDirection == "direita" and addTolist == False) or (oppositeCompassTurnRight == True and addTolist == False) and isACycle == False and self.actualCoordinatesAreACycle(coordinatesCycle, self.measures.x, self.measures.y, self.measures.compass) == False:  #SO ENTRA NOS OUTROS ELIF'S SE O findValue FOR False, o otherDirectionsLoop for false
            # if pathLeft == ['1'] and sensorRight == ['0','0']:       #self.measures.lineSensor == ['1','1','1','1','1','0','0']
            #     frente = True
            #     turningRight = False
            #     print("Go front R")
            
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
                nodes.append([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]])
                #clearListPath = True
                
            # if posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False:
            #     print("ESTOU AQUI NO TURN RIGHT!!!!!")
            #     nodes.append([nodes[posNodeInList][0], nodes[posNodeInList][1], pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]])
            #     #clearListPath = True
                
            # elif posNodeInList == -1: #comentar
            #     numberNodesAux = numberNodes
            #     adjacente = numberNodesAux - 1
            #     nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
            #     numberNodes = numberNodes + 1
            #     #clearListPath = True
            
            clearListPath = True    #verifica as duas condiçoes de cima e caso encontre igual mas o caminho tb é igual
            resetPathToNode = True
            
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
                nodes.append([nodes[posNodeInList][0], adjacente.__str__(), pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]])
            # if posNodeInList != -1 and pathToNode != nodes[posNodeInList][2] and resetPathToNode == False:
            #     print("ESTOU AQUI NO TURN LEFT!!!!!")
            #     nodes.append([nodes[posNodeInList][0], nodes[posNodeInList][1], pathToNode, len(pathToNode), "D", nodes[posNodeInList][5]])
            #     #clearListPath = True
                
            # elif posNodeInList == -1:
            #     numberNodesAux = numberNodes
            #     adjacente = numberNodesAux - 1
            #     nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
            #     numberNodes = numberNodes + 1
            #     clearListPath = True
                
            clearListPath = True
            resetPathToNode = True
            self.driveMotors(-0.07,+0.1)
            turningLeft = True
            print("Lets turn LEFT (OTHER DIRECTION)")
                         
        #pathRight == ['1'] and self.measures.lineSensor != ['1','1','1','1','1','1','1'] and turningLeft == False
        #Momento em que descobriu q tem caminho em frente, poderá surgir mais casos de ruido
        #Podia secalhar meter pathRight != ['1'] para evitar meter tds as opçoes onde ha ruido
        #and followCompass == False
        elif pathRight == ['1'] and self.measures.lineSensor != ['1','1','1','1','1','1','1'] and self.measures.lineSensor != ['1','1','1','0','1','1','1'] and self.measures.lineSensor != ['1','1','0','1','1','1','1'] and self.measures.lineSensor != ['1','1','0','0','1','1','1'] and self.measures.lineSensor != ['1','1','0','0','0','1','1'] and self.measures.lineSensor != ['1','1','0','0','0','0','1'] and turningLeft == False and itsACross == False and frente == False and learningLeft == False:####
            print('Rotate/Knowing Right')
            turningRight = True
            self.driveMotors(+0.1,-0.03)    #-0.04
            # if pathLeft == ['1']:    #Encontrou caminho em frente
            #     #entroncamento1 = True
            #     #coordenadas.append([self.measures.x, self.measures.y])
            #     self.driveMotors(0,0)   #STOP
            #     print("WE KNOW THAT WE CAN GO FRONT (LS), marcha-atras")
            #     self.driveMotors(-0.15,-0.15)
            #     #frenteD = True
            #     #knowing = False 
        #and followCompass == False and checkDiff == False
        elif pathLeft == ['1'] and turningRight == True and knowing == False and itsACross == False and frente == False and checkXrem == 0 and checkYrem == 0 and (notDoneLetsTurnR_PD == False and notDoneLetsTurnR_RD == False) and checkXrem == 0 and checkYrem == 0 and oppositeCompassTurnLeft == False and oppositeCompassTurnRight == False: 
            #self.driveMotors('0','0')   #stop
            print("WE KNOW THAT WE CAN GO FRONT (LS)")
            self.driveMotors(-0.15,+0.1)
            
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
            if self.checkCoordinatesInList(possibleDirections,self.measures.x,self.measures.y) == False and self.doneDirection(removedDirections, self.measures.x, self.measures.y) == False and self.samePosition(coordinatesDone, self.measures.x, self.measures.y, self.measures.compass) == False and done == False:
                #Adicionar esta posiçao ao possibleDirections
                possibleDirections.append([self.measures.x, self.measures.y, "direita", self.measures.compass])    ####### Adicionar outra direçao a lista
                DirectionsAndTargets.append([self.measures.x, self.measures.y])
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
                    numberNodesAux = numberNodes
                    adjacente = numberNodesAux - 1
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
            if self.checkCoordinatesInList(possibleDirections,self.measures.x,self.measures.y) == False and self.doneDirection(removedDirections, self.measures.x, self.measures.y) == False and self.samePosition(coordinatesDone, self.measures.x, self.measures.y, self.measures.compass) == False and done == False:
                possibleDirections.append([self.measures.x, self.measures.y, "esquerda", self.measures.compass])   ###### Adicionar outra direcao na lista
                DirectionsAndTargets.append([self.measures.x, self.measures.y])
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
                    numberNodesAux = numberNodes
                    adjacente = numberNodesAux - 1
                    nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "D", (matrixyinicial, matrixxinicial)])
                    numberNodes = numberNodes + 1
                clearListPath = True
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
            alreadyInListDirecitonsAndTargets = False
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
        print(prev_dir)
        prev_char = self.matrix[matrixxinicial][matrixyinicial]
        print(prev_char)
        print(aux2)
        print(self.measures.y)

        self.matrix[10][24] = 'I'
        if prev_char == 'I':
            matrixyinicial = matrixyinicial +1
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


            if self.measures.compass < 120 and self.measures.compass > 60:
                print("U")
                dir = "U"
                if prev_char == ' ':
                    if dir == 'U' and prev_dir =='R':
                        matrixxinicial = matrixxinicial -1 
                        self.matrix[matrixxinicial][matrixyinicial] = '|'
                        aux = self.measures.x

            if self.measures.compass > -120 and self.measures.compass < -60:
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

            if self.measures.compass < 120 and self.measures.compass > 60:
                print("U")
                dir = "U"
                if prev_char == ' ':
                    if dir == 'U' and prev_dir =='L':
                        matrixxinicial = matrixxinicial -1 
                        self.matrix[matrixxinicial][matrixyinicial] = '|'
                        aux = self.measures.x

            if self.measures.compass > -120 and self.measures.compass < -60:
                print("D")
                dir = "D"
                if prev_char == ' ':
                    if dir == 'D' and prev_dir =='L':
                        matrixxinicial = matrixxinicial + 1 
                        self.matrix[matrixxinicial][matrixyinicial] = '|'
                        aux = self.measures.x


        if round(aux2 - self.measures.y,1) == -1 :                                                      #Cima
            if self.measures.compass < 120 and self.measures.compass > 60:
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

            if self.measures.compass < 30 and self.measures.compass > -30:
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
            if self.measures.compass > -120 and self.measures.compass < -60:
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

            if self.measures.compass < 30 and self.measures.compass > -30:
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
                        
        print("lastElementBeforeClear->", lastElementBeforeClear)
        print((matrixyinicial, matrixxinicial))
            
        print("clearListPath->", clearListPath)
        print("resetPathToNode->", resetPathToNode)
        print("numberNodes->", numberNodes)
                               
        if self.measures.time == 0:     #Evitar que se adicione a primeira posição da matriz ao caminho
            inicialCols = matrixyinicial
            inicialLines = matrixxinicial
        
        #Maneira de no inicio nao adicionar a primeira posição e dps puder adicionar tds as posiçoes incluindo as primeiras
        if self.measures.time <= 50:
            if (tuple([matrixyinicial,matrixxinicial]) not in pathToNode) and clearListPath == False and tuple([matrixyinicial,matrixxinicial]) != (inicialCols,inicialLines):
                pathToNode.append(tuple([matrixyinicial,matrixxinicial]))
        else:
            if (tuple([matrixyinicial,matrixxinicial]) not in pathToNode) and clearListPath == False:
                pathToNode.append(tuple([matrixyinicial,matrixxinicial]))  
        print("pathToNode->",pathToNode)
        
        
        if self.measures.time >= 40 and tuple([matrixyinicial,matrixxinicial]) == (inicialCols,inicialLines) and resetPathToNode == False:   #Atualizar a adjacencia da posicaçao inicial
            #SÓ PODE ENTRAR UMA VEZ
            numberNodesAux = numberNodes
            adjacente = numberNodesAux - 1
            nodes[0] = [nodes[0][0], adjacente.__str__(), pathToNode, len(pathToNode), nodes[0][4], nodes[0][5]]
            print("ALTEREI O VERTICE INICIAL")
            clearListPath = True
            resetPathToNode = True  
        
        
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
                DirectionsAndTargets.append([self.measures.x, self.measures.y])
                directionsAndTargetsMatrix.append([matrixyinicial,matrixxinicial])
                nodes.append([numberNodes.__str__(), zero.__str__(), [(matrixyinicial,matrixxinicial)], 0, "B", (matrixyinicial, matrixxinicial)])
                numberNodes = numberNodes + 1
            elif DirectionsAndTargets != [] and directionsAndTargetsMatrix != []:
                for i in range(0, len(DirectionsAndTargets)):
                    beaconInicial = False   #para evitar ele voltar a adicionar o beacon inicial qnd passa pelo inicio
                    diffX = abs(round(DirectionsAndTargets[i][0] - self.measures.x,1))
                    diffY = abs(round(DirectionsAndTargets[i][1] - self.measures.y,1))
                    xBeaconInicialDiff = abs(round(DirectionsAndTargets[0][0] - self.measures.x,1))
                    yBeaconInicialDiff = abs(round(DirectionsAndTargets[0][1] - self.measures.y,1))
                    if xBeaconInicialDiff >= 0 and xBeaconInicialDiff <= 0.6 and yBeaconInicialDiff >= 0 and yBeaconInicialDiff <= 0.6:
                        beaconInicial = True
                    if diffX >= 0 and diffX <= 1 and diffY >= 0 and diffY <= 1: #antes estava 0.9
                        alreadyInListDirecitonsAndTargets = True    #Encontrou um elemento na lista aproximado às coordenadas do x e y atual do robo
                    if i == (len(DirectionsAndTargets)-1):	#ultimo elemento
                        #print(i)
                        subX = abs(round(DirectionsAndTargets[i][0] - self.measures.x,1))   #diferença entre o ultimo elemento e o x a adicionar
                        #print(subX)
                        subY = abs(round(DirectionsAndTargets[i][1] - self.measures.y,1))   #diferença entre o ultimo elemento e o y a adicionar
                        #print(subY)
                        #print("\n")
                        #(subX >= 1 and subY >= 0 and subY <= 0.1) or (subY >= 1 and subX >= 0 and subX <= 0.1)
                        if (subX >= 1 or subY >= 1) and diffX >= 0.2 and diffY >= 0.2 and beaconInicial == False and alreadyInListDirecitonsAndTargets == False:  #horizontal/vertical                
                            DirectionsAndTargets.append([self.measures.x, self.measures.y])
                            directionsAndTargetsMatrix.append([matrixyinicial,matrixxinicial])
                            for i in range(0, len(nodes)):
                                nodePos = nodes[i][5]
                                if tuple([matrixyinicial, matrixxinicial]) == nodePos:
                                    posNodeInList = i
                            if posNodeInList != -1:
                                nodes.append([nodes[posNodeInList][0], nodes[posNodeInList][1],pathToNode, len(pathToNode), "B", (matrixyinicial, matrixxinicial)])
                            else:
                                numberNodesAux = numberNodes
                                adjacente = numberNodesAux - 1
                                nodes.append([numberNodes.__str__(), adjacente.__str__(), pathToNode, len(pathToNode), "B", (matrixyinicial, matrixxinicial)])
                                numberNodes = numberNodes + 1
                            clearListPath = True
                        #clearListPath = True
                        #resetPathToNode = True
            for element in nodes:   #Dar clear à lista se voltar a passar pela msm posição do beacon
                if element[5] == (matrixyinicial, matrixxinicial) and element[4] == 'B':
                    clearListPath = True
                    resetPathToNode = True
                    
        print("DirectionsAndTargets->", DirectionsAndTargets)
        print("directionsAndTargetsMatrix->", directionsAndTargetsMatrix)
        print("nodes->", nodes)

        if (possibleDirections == [] and self.measures.time >= 500 and sptHasBeenCalculated == False) or (self.measures.time == 5000 and sptHasBeenCalculated == False):  #Ja conheceu o mapa, entao vai calcular o caminho minimo
            for element in nodes:
                edges.append(tuple([element[0], element[1], element[3]])) 
                if element[4] == 'B':
                    beacons.append(tuple([element[0], element[1], element[3]]))
            print("edges->", edges)
            graph = Graph()
            for edge in edges:  #Criar o grafo atraves das edges
                graph.add_edge(*edge)
            print("beacons:>", beacons)
            listaAuxiliarPath = []
            # for i in range(0, len(beacons)):    #Percorre a lista dos beacons para aplicar o algoritmo
            #     print("beacons[i][0]:->", beacons[i][0])
            #     if i <= (len(beacons)-2):   #Se o i for menor que o penultimo elemento
            #         listaAuxiliarPath = listaAuxiliarPath + self.dijsktra(graph, beacons[i][0], beacons[i+1][0])
            #     if i == (len(beacons)-1): #chegou ao ultimo elemento então vai buscar o caminho do ultimo beacon ao ponto inicial
            #         listaAuxiliarPath = listaAuxiliarPath + self.dijsktra(graph, beacons[i][0], beacons[0][0])
            
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
                print("ESTOU NO ELSE FORA DA FUNÇAO") 
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
  
        print("finalPathFileAux->", finalPathFileAux)
  
        for i in range(0,len(finalPathFileAux)):    #Nao adicionar os repetidos
            if i <= (len(finalPathFileAux)-2): #percorre a lista até à penultima posiçao
                if finalPathFileAux[i] != finalPathFileAux[i+1]:
                    finalPathFile.append(finalPathFileAux[i])
            elif i ==  (len(finalPathFileAux)-1):   #Ultima posiçao         
                finalPathFile.append(finalPathFileAux[i])
                
        print("finalPathFile->", finalPathFile)
              
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
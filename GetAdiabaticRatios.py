# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 14:28:12 2023

@author: FBattini
"""

import pandas as pd
from os import listdir
import os
from eppy.modeleditor import IDF

def computeAdiabaticRatios(thisCaseStudyFolderPath, detailedFolderPath):
    
    adiabaticRatiosPath = '{}AdiabaticRatios/'.format(thisCaseStudyFolderPath)
    
    for file in os.listdir(detailedFolderPath):
        if file.endswith(".idf"):
            fname = file
            filename = os.path.splitext(file)[0].replace(".idf", "")
            idf1 = IDF(detailedFolderPath + fname)
            adiabaticRatiosDF = pd.DataFrame([])
            eastFreeArea, westFreeArea, northFreeArea, southFreeArea, roofFreeArea, floorFreeArea = 0, 0, 0, 0, 0, 0
            eastNotFreeArea, westNotFreeArea, northNotFreeArea, southNotFreeArea, roofNotFreeArea, floorNotFreeArea = 0, 0, 0, 0, 0, 0
            floorNumber = 1
            for zone in idf1.idfobjects["Zone"]:
                for surface in idf1.idfobjects["BuildingSurface:Detailed"]:
                    if surface.Zone_Name == zone.Name:
                        if surface.Outside_Boundary_Condition == "Outdoors":
                            if surface.Surface_Type == "Wall":
                                if surface.azimuth > 315 or surface.azimuth <= 45:
                                    northFreeArea += surface.area
                                if surface.azimuth > 45 and surface.azimuth <= 135:
                                    eastFreeArea += surface.area
                                if surface.azimuth > 135 and surface.azimuth <= 225:
                                    southFreeArea += surface.area
                                if surface.azimuth > 225 and surface.azimuth <= 315:   
                                    westFreeArea += surface.area
                            if surface.Surface_Type == 'Roof':
                                roofFreeArea += surface.area
                            if surface.Surface_Type == 'Floor':
                                floorFreeArea += surface.area
                        if surface.Outside_Boundary_Condition == "Ground":
                            floorFreeArea += surface.area
                        if surface.Outside_Boundary_Condition == "Adiabatic":
                            if surface.Surface_Type == "Wall":
                                if surface.azimuth > 315 or surface.azimuth <= 45:
                                    northNotFreeArea += surface.area
                                if surface.azimuth > 45 and surface.azimuth <= 135:
                                    eastNotFreeArea += surface.area
                                if surface.azimuth > 135 and surface.azimuth <= 225:
                                    southNotFreeArea += surface.area
                                if surface.azimuth > 225 and surface.azimuth <= 315:   
                                    westNotFreeArea += surface.area
                            if surface.Surface_Type == 'Roof':
                                roofNotFreeArea += surface.area
                            if surface.Surface_Type == 'Floor':
                                floorNotFreeArea += surface.area
                        # if it is in contact with another zone I don't have to increase the adiabatic ratio, so I consider it free
                        if surface.Outside_Boundary_Condition == "Surface": 
                            if surface.Surface_Type == "Wall":
                                if surface.azimuth > 315 or surface.azimuth <= 45:
                                    northFreeArea += surface.area
                                if surface.azimuth > 45 and surface.azimuth <= 135:
                                    eastFreeArea += surface.area
                                if surface.azimuth > 135 and surface.azimuth <= 225:
                                    southFreeArea += surface.area
                                if surface.azimuth > 225 and surface.azimuth <= 315:   
                                    westFreeArea += surface.area
                            if surface.Surface_Type == 'Ceiling':
                                roofFreeArea += surface.area
                            if surface.Surface_Type == 'Floor':
                                floorFreeArea += surface.area
                if northFreeArea == 0:
                    adiabaticNorth = 1
                else:
                    adiabaticNorth = northNotFreeArea/(northFreeArea + northNotFreeArea)
                if eastFreeArea == 0:
                    adiabaticEast = 1
                else:
                    adiabaticEast = eastNotFreeArea/(eastFreeArea + eastNotFreeArea)
                if southFreeArea == 0:
                    adiabaticSouth = 1
                else:
                    adiabaticSouth = southNotFreeArea/(southFreeArea + southNotFreeArea)
                if westFreeArea == 0:
                    adiabaticWest = 1
                else:
                    adiabaticWest = westNotFreeArea/(westFreeArea + westNotFreeArea)
                if roofFreeArea == 0:
                    adiabaticRoof = 1
                else:
                    adiabaticRoof = roofNotFreeArea/(roofFreeArea + roofNotFreeArea)
                if floorFreeArea == 0:
                    adiabaticFloor = 1
                else:
                    adiabaticFloor = floorNotFreeArea/(floorFreeArea + floorNotFreeArea)
                
                adiabaticRatiosDF.loc[0, 'Flr' + str(floorNumber) + 'AR_North'] = adiabaticNorth
                adiabaticRatiosDF.loc[0, 'Flr' + str(floorNumber) + 'AR_East'] = adiabaticEast
                adiabaticRatiosDF.loc[0, 'Flr' + str(floorNumber) + 'AR_South'] = adiabaticSouth
                adiabaticRatiosDF.loc[0, 'Flr' + str(floorNumber) + 'AR_West'] = adiabaticWest
                adiabaticRatiosDF.loc[0, 'Flr' + str(floorNumber) + 'AR_Roof'] = adiabaticRoof
                adiabaticRatiosDF.loc[0, 'Flr' + str(floorNumber) + 'AR_Floor'] = adiabaticFloor
    
                floorNumber += 1
                
            adiabaticRatiosDF.to_csv(adiabaticRatiosPath + filename + '.csv')
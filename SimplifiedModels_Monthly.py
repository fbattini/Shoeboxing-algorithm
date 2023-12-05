# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 16:03:48 2023

@author: FBattini
"""
# %%

import os
from eppy.modeleditor import IDF
import pandas as pd
import numpy as np

# %%

def createSimplifiedModels_Monthly(thisCaseStudyFolderPath, detailedFolderPath):

    detailedRadiationAnalysisMonthlyPath = '{}DetailedRadiationAnalysis_Monthly/'.format(thisCaseStudyFolderPath)
    dimensionsPath = '{}!Dimensions.csv'.format(thisCaseStudyFolderPath)
    adiabaticRatiosPath = '{}AdiabaticRatios/'.format(thisCaseStudyFolderPath)
    simplifiedModelsMonthlyPath = '{}Simplified_Monthly/'.format(thisCaseStudyFolderPath)
    
    dimensionsDF = pd.read_csv(dimensionsPath, index_col = 0)
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    for file in os.listdir(detailedFolderPath):
        if file.endswith(".idf"):
            fname = file
            filename = os.path.splitext(file)[0].replace(".idf", "")
            idf1 = IDF(detailedFolderPath + fname)
            # edit name
            idf1.idfobjects["Building"][0].Name = idf1.idfobjects["Building"][0].Name + "_Simplified"
            # Create window obstruction material and construction
            envelopeSummary = pd.read_csv(detailedFolderPath + filename + "Table.csv", sep='^', header=None)
            envelopeSummary = envelopeSummary.iloc[:,0].str.split(',', expand=True) # need this 2 columns because file as strange structure
            rows, cols = np.where(envelopeSummary == "Glass U-Factor [W/m2-K]")
            windowUValue_withFilm = float(envelopeSummary.iloc[rows[0]+1,cols[0]]) # find window u-value
            
            constructions = idf1.idfobjects["Construction"] # find outside material in envelope
            for construction in constructions:
                if construction.Name == "Envelope":
                    envelopeOutsideLayer = construction.Outside_Layer
            
            materials = idf1.idfobjects["Material"] # find properties of that material to apply to obstruction
            for material in materials:
                if material.Name == envelopeOutsideLayer:
                    obstructionSurfaceRoughness = material.Roughness
                    obstructionSurfaceThermalAbs = material.Thermal_Absorptance
                    obstructionSurfaceSolarAbs = material.Solar_Absorptance
                    obstructionSurfaceVisibleAbs = material.Visible_Absorptance
            
            idf1.newidfobject("Material:NoMass")
            idf1.idfobjects["Material:NoMass"][0].Name = "ObstructionSurface"
            idf1.idfobjects["Material:NoMass"][0].Roughness = obstructionSurfaceRoughness
            idf1.idfobjects["Material:NoMass"][0].Thermal_Resistance = 1/windowUValue_withFilm - 0.15 # 0.15 is the sum of internal and external resistances (with both convective and radiative parts) used also in eppy
            idf1.idfobjects["Material:NoMass"][0].Thermal_Absorptance = obstructionSurfaceThermalAbs
            idf1.idfobjects["Material:NoMass"][0].Solar_Absorptance = obstructionSurfaceSolarAbs
            idf1.idfobjects["Material:NoMass"][0].Visible_Absorptance = obstructionSurfaceVisibleAbs
            
            idf1.newidfobject("Construction")
            idf1.idfobjects["Construction"][-1].Name = "Door"
            idf1.idfobjects["Construction"][-1].Outside_Layer = "ObstructionSurface"
            # rename zones
            zones = idf1.idfobjects["Zone"]
            for zone in zones:
                zone.Name = zone.Name + "_Simplified"
                zone.Ceiling_Height = ""
                zone.Volume = ""
                zone.Floor_Area = ""
            # remove external detailed shading surfaces
            shadingsBuilding = idf1.idfobjects["Shading:Building:Detailed"]
            while len(shadingsBuilding) != 0:
                idf1.removeidfobject(shadingsBuilding[0])
            # other equipment
            otherEquipments = idf1.idfobjects["OtherEquipment"]
            for otherEquipment in otherEquipments:
                otherEquipment.Name = otherEquipment.Name + "_Simplified"
                otherEquipment.Zone_or_ZoneList_Name = otherEquipment.Zone_or_ZoneList_Name + "_Simplified"
            # infiltration
            infiltrations = idf1.idfobjects["ZoneInfiltration:DesignFlowRate"]
            for infiltration in infiltrations:
                infiltration.Name = infiltration.Name + "_Simplified"
                infiltration.Zone_or_ZoneList_Name = infiltration.Zone_or_ZoneList_Name + "_Simplified"  
            # zone control thermostat
            controlThermostats = idf1.idfobjects["ZoneControl:Thermostat"]
            for controlThermostat in controlThermostats:
                controlThermostat.Name = controlThermostat.Name + "_Simplified"
                controlThermostat.Zone_or_ZoneList_Name = controlThermostat.Zone_or_ZoneList_Name + "_Simplified"
            # System
            airSystems = idf1.idfobjects["ZoneHVAC:IdealLoadsAirSystem"]
            for airSystem in airSystems:
                airSystem.Name = airSystem.Name + "_Simplified"
                airSystem.Zone_Supply_Air_Node_Name = airSystem.Zone_Supply_Air_Node_Name + "_Simplified"
            # Equipment list
            equipmentLists = idf1.idfobjects["ZoneHVAC:EquipmentList"]
            for equipmentList in equipmentLists:
                equipmentList.Name = equipmentList.Name + "_Simplified"
                equipmentList.Zone_Equipment_1_Name = equipmentList.Zone_Equipment_1_Name + "_Simplified"
            # Equipment connections
            equipmentConnections = idf1.idfobjects["ZoneHVAC:EquipmentConnections"]
            for equipmentConnection in equipmentConnections:
                equipmentConnection.Zone_Name = equipmentConnection.Zone_Name + "_Simplified"
                equipmentConnection.Zone_Conditioning_Equipment_List_Name = equipmentConnection.Zone_Conditioning_Equipment_List_Name + "_Simplified"
                equipmentConnection.Zone_Air_Inlet_Node_or_NodeList_Name = equipmentConnection.Zone_Air_Inlet_Node_or_NodeList_Name + "_Simplified"
                equipmentConnection.Zone_Air_Node_Name = equipmentConnection.Zone_Air_Node_Name + "_Simplified"
                equipmentConnection.Zone_Return_Air_Node_or_NodeList_Name = equipmentConnection.Zone_Return_Air_Node_or_NodeList_Name + "_Simplified"
            
            # remove surfaces and windows before saving it
            surfaces = idf1.idfobjects["BuildingSurface:Detailed"]
            while len(surfaces) != 0:
                idf1.removeidfobject(surfaces[0])
            
            windows = idf1.idfobjects["FenestrationSurface:Detailed"]
            while len(windows) != 0:
                idf1.removeidfobject(windows[0])
                
            # remove envelope results file which is not needed
            idf1.removeidfobject(idf1.idfobjects["Output:Table:SummaryReports"][0])
            
            idf1.save(simplifiedModelsMonthlyPath + filename + "_Simplified.idf")
        
        """ Geometrical definition """
    for file in os.listdir(detailedFolderPath):
        if file.endswith(".idf"):
            fname = file
            filename = os.path.splitext(file)[0].replace(".idf", "")
            idf1 = IDF(simplifiedModelsMonthlyPath + filename + "_Simplified.idf")
            surfaces = idf1.idfobjects["BuildingSurface:Detailed"]
            windows = idf1.idfobjects["FenestrationSurface:Detailed"]
            zones = idf1.idfobjects["Zone"]
            
            xDimension = dimensionsDF.loc[filename,'X']
            yDimension = dimensionsDF.loc[filename,'Y']
            zDimension = dimensionsDF.loc[filename,'Z']
            floorHeights = [zDimension/len(zones) for zone in zones]
            adiabaticRatiosDF = pd.read_csv(adiabaticRatiosPath + filename + ".csv", index_col = 0)
            obstructionRatiosDF = pd.read_csv(detailedRadiationAnalysisMonthlyPath + filename + ".csv", index_col = 0)
            
            for j in range(12):
                for i in range(len(zones)):
                    northAR = adiabaticRatiosDF.iloc[0, 0+i*6]
                    eastAR  = adiabaticRatiosDF.iloc[0, 1+i*6]
                    southAR = adiabaticRatiosDF.iloc[0, 2+i*6]
                    westAR  = adiabaticRatiosDF.iloc[0, 3+i*6]
                    roofAR  = adiabaticRatiosDF.iloc[0, 4+i*6]
                    floorAR = adiabaticRatiosDF.iloc[0 ,5+i*6]
                
                    northOR = obstructionRatiosDF.iloc[j, 0+i*4]
                    eastOR  = obstructionRatiosDF.iloc[j, 1+i*4]
                    southOR = obstructionRatiosDF.iloc[j, 2+i*4]
                    westOR  = obstructionRatiosDF.iloc[j, 3+i*4]
                    
                    WWR = 0.4
                    
                    if floorAR == 0:
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'FloorNonAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Floor'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        if i == 0:
                            thisSurface.Outside_Boundary_Condition = 'Ground'
                        else:
                            thisSurface.Outside_Boundary_Condition = 'Surface'
                            thisSurface.Outside_Boundary_Condition_Object = 'RoofNonAdiabatic_' + zones[i-1].Name
                        thisSurface.Sun_Exposure = 'NoSun'
                        thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = 0
                        thisSurface.Vertex_1_Ycoordinate = 0
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = 0
                        thisSurface.Vertex_2_Ycoordinate = yDimension
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = xDimension
                        thisSurface.Vertex_3_Ycoordinate = yDimension
                        thisSurface.Vertex_3_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = xDimension
                        thisSurface.Vertex_4_Ycoordinate = 0
                        thisSurface.Vertex_4_Zcoordinate = i * floorHeights[i]
                    elif floorAR == 1:
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'FloorAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Floor'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Adiabatic'
                        thisSurface.Sun_Exposure = 'NoSun'
                        thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = 0
                        thisSurface.Vertex_1_Ycoordinate = 0
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = 0
                        thisSurface.Vertex_2_Ycoordinate = yDimension
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = xDimension
                        thisSurface.Vertex_3_Ycoordinate = yDimension
                        thisSurface.Vertex_3_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = xDimension
                        thisSurface.Vertex_4_Ycoordinate = 0
                        thisSurface.Vertex_4_Zcoordinate = i * floorHeights[i]
                    else:
                        thisSurfaceArea = xDimension*yDimension
                        thisSurfaceAdiabaticArea = thisSurfaceArea*floorAR
                        thisSurfaceHeight = yDimension
                        thisSurfaceAdiabaticBase = round(thisSurfaceAdiabaticArea/thisSurfaceHeight, 3)
                        
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'FloorAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Floor'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Adiabatic'
                        thisSurface.Sun_Exposure = 'NoSun'
                        thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = 0
                        thisSurface.Vertex_1_Ycoordinate = 0
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = 0
                        thisSurface.Vertex_2_Ycoordinate = thisSurfaceHeight
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = thisSurfaceAdiabaticBase
                        thisSurface.Vertex_3_Ycoordinate = thisSurfaceHeight
                        thisSurface.Vertex_3_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = xDimension
                        thisSurface.Vertex_4_Ycoordinate = 0
                        thisSurface.Vertex_4_Zcoordinate = i * floorHeights[i]
                        
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'FloorNonAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Floor'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        if i == 0:
                            thisSurface.Outside_Boundary_Condition = 'Ground'
                        else:
                            thisSurface.Outside_Boundary_Condition = 'Surface'
                            thisSurface.Outside_Boundary_Condition_Object = 'RoofNonAdiabatic_' + zones[i-1].Name
                            
                        thisSurface.Sun_Exposure = 'NoSun'
                        thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = thisSurfaceAdiabaticBase
                        thisSurface.Vertex_1_Ycoordinate = 0
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = thisSurfaceAdiabaticBase
                        thisSurface.Vertex_2_Ycoordinate = thisSurfaceHeight
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = xDimension
                        thisSurface.Vertex_3_Ycoordinate = thisSurfaceHeight
                        thisSurface.Vertex_3_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = xDimension
                        thisSurface.Vertex_4_Ycoordinate = 0
                        thisSurface.Vertex_4_Zcoordinate = i * floorHeights[i]
                    
                    if southAR == 0:
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'SouthNonAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Outdoors'
                        thisSurface.Sun_Exposure = 'SunExposed'
                        thisSurface.Wind_Exposure = 'WindExposed'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = 0
                        thisSurface.Vertex_1_Ycoordinate = 0
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = xDimension
                        thisSurface.Vertex_2_Ycoordinate = 0
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = xDimension
                        thisSurface.Vertex_3_Ycoordinate = 0
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = 0
                        thisSurface.Vertex_4_Ycoordinate = 0
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * floorHeights[i]  
                        
                        if southOR >= 0.01:
                            thisSurfaceCentroid = [round((thisSurface.Vertex_2_Xcoordinate - thisSurface.Vertex_1_Xcoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*southOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Shading_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Door'
                            thisWindow.Construction_Name = 'Door'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_1_Ycoordinate = 0
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_2_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_2_Ycoordinate = 0
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_3_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_3_Ycoordinate = 0
                            thisWindow.Vertex_3_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            thisWindow.Vertex_4_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_4_Ycoordinate = 0
                            thisWindow.Vertex_4_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_1_Ycoordinate = 0
                            thisWindow.Vertex_1_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            thisWindow.Vertex_2_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_2_Ycoordinate = 0
                            thisWindow.Vertex_2_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            thisWindow.Vertex_3_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_3_Ycoordinate = 0
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_4_Ycoordinate = 0
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                        else:
                            thisSurfaceCentroid = [round((thisSurface.Vertex_2_Xcoordinate - thisSurface.Vertex_1_Xcoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*southOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_1_Ycoordinate = 0
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_2_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_2_Ycoordinate = 0
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_3_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_3_Ycoordinate = 0
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_4_Ycoordinate = 0
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3) 
                    elif southAR == 1:
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'SouthAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Adiabatic'
                        thisSurface.Sun_Exposure = 'NoSun'
                        thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = 0
                        thisSurface.Vertex_1_Ycoordinate = 0
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = xDimension
                        thisSurface.Vertex_2_Ycoordinate = 0
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = xDimension
                        thisSurface.Vertex_3_Ycoordinate = 0
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = 0
                        thisSurface.Vertex_4_Ycoordinate = 0
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * floorHeights[i]
                    else:
                        thisSurfaceArea = xDimension*floorHeights[i]
                        thisSurfaceAdiabaticArea = thisSurfaceArea*southAR
                        thisSurfaceHeight = floorHeights[i]
                        thisSurfaceAdiabaticBase = round(thisSurfaceAdiabaticArea/thisSurfaceHeight, 3)
                        
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'SouthAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Adiabatic'
                        thisSurface.Sun_Exposure = 'NoSun'
                        thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = 0
                        thisSurface.Vertex_1_Ycoordinate = 0
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = thisSurfaceAdiabaticBase
                        thisSurface.Vertex_2_Ycoordinate = 0
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = thisSurfaceAdiabaticBase
                        thisSurface.Vertex_3_Ycoordinate = 0
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * thisSurfaceHeight
                        thisSurface.Vertex_4_Xcoordinate = 0
                        thisSurface.Vertex_4_Ycoordinate = 0
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * thisSurfaceHeight
                                  
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'SouthNonAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Outdoors'
                        thisSurface.Sun_Exposure = 'SunExposed'
                        thisSurface.Wind_Exposure = 'WindExposed'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = thisSurfaceAdiabaticBase
                        thisSurface.Vertex_1_Ycoordinate = 0
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = xDimension
                        thisSurface.Vertex_2_Ycoordinate = 0
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = xDimension
                        thisSurface.Vertex_3_Ycoordinate = 0
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = thisSurfaceAdiabaticBase
                        thisSurface.Vertex_4_Ycoordinate = 0
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * thisSurfaceHeight
                        
                        if southOR >= 0.01:
                            thisSurfaceCentroid = [round(thisSurfaceAdiabaticBase + (thisSurface.Vertex_2_Xcoordinate - thisSurface.Vertex_1_Xcoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*southOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Shading_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Door'
                            thisWindow.Construction_Name = 'Door'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_1_Ycoordinate = 0
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_2_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_2_Ycoordinate = 0
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_3_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_3_Ycoordinate = 0
                            thisWindow.Vertex_3_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            thisWindow.Vertex_4_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_4_Ycoordinate = 0
                            thisWindow.Vertex_4_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_1_Ycoordinate = 0
                            thisWindow.Vertex_1_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            thisWindow.Vertex_2_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_2_Ycoordinate = 0
                            thisWindow.Vertex_2_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            thisWindow.Vertex_3_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_3_Ycoordinate = 0
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_4_Ycoordinate = 0
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                        else:
                            thisSurfaceCentroid = [round(thisSurfaceAdiabaticBase + (thisSurface.Vertex_2_Xcoordinate - thisSurface.Vertex_1_Xcoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*southOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_1_Ycoordinate = 0
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_2_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_2_Ycoordinate = 0
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_3_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_3_Ycoordinate = 0
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_4_Ycoordinate = 0
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                                  
                    if eastAR == 0:
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'EastNonAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Outdoors'
                        thisSurface.Sun_Exposure = 'SunExposed'
                        thisSurface.Wind_Exposure = 'WindExposed'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = xDimension
                        thisSurface.Vertex_1_Ycoordinate = 0
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = xDimension
                        thisSurface.Vertex_2_Ycoordinate = yDimension
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = xDimension
                        thisSurface.Vertex_3_Ycoordinate = yDimension
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = xDimension
                        thisSurface.Vertex_4_Ycoordinate = 0 
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * floorHeights[i]
                        
                        if eastOR >= 0.01:
                            thisSurfaceCentroid = [round((thisSurface.Vertex_2_Ycoordinate - thisSurface.Vertex_1_Ycoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*eastOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Shading_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Door'
                            thisWindow.Construction_Name = 'Door'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = xDimension
                            thisWindow.Vertex_1_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_2_Xcoordinate = xDimension
                            thisWindow.Vertex_2_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_3_Xcoordinate = xDimension
                            thisWindow.Vertex_3_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_3_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            thisWindow.Vertex_4_Xcoordinate = xDimension
                            thisWindow.Vertex_4_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_4_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = xDimension
                            thisWindow.Vertex_1_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_1_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            thisWindow.Vertex_2_Xcoordinate = xDimension
                            thisWindow.Vertex_2_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_2_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            thisWindow.Vertex_3_Xcoordinate = xDimension
                            thisWindow.Vertex_3_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = xDimension
                            thisWindow.Vertex_4_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                        else:
                            thisSurfaceCentroid = [round((thisSurface.Vertex_2_Ycoordinate - thisSurface.Vertex_1_Ycoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*eastOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = xDimension
                            thisWindow.Vertex_1_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_2_Xcoordinate = xDimension
                            thisWindow.Vertex_2_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_3_Xcoordinate = xDimension
                            thisWindow.Vertex_3_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = xDimension
                            thisWindow.Vertex_4_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                    elif eastAR == 1:
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'EastAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Adiabatic'
                        thisSurface.Sun_Exposure = 'NoSun'
                        thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = xDimension
                        thisSurface.Vertex_1_Ycoordinate = 0
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = xDimension
                        thisSurface.Vertex_2_Ycoordinate = yDimension
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = xDimension
                        thisSurface.Vertex_3_Ycoordinate = yDimension
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = xDimension
                        thisSurface.Vertex_4_Ycoordinate = 0 
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * floorHeights[i] 
                    else:
                        thisSurfaceArea = yDimension*floorHeights[i]
                        thisSurfaceAdiabaticArea = thisSurfaceArea*eastAR
                        thisSurfaceHeight = floorHeights[i]
                        thisSurfaceAdiabaticBase = round(thisSurfaceAdiabaticArea/thisSurfaceHeight, 3)
                        
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'EastAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Adiabatic'
                        thisSurface.Sun_Exposure = 'NoSun'
                        thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = xDimension
                        thisSurface.Vertex_1_Ycoordinate = 0
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = xDimension
                        thisSurface.Vertex_2_Ycoordinate = thisSurfaceAdiabaticBase
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = xDimension
                        thisSurface.Vertex_3_Ycoordinate = thisSurfaceAdiabaticBase
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * thisSurfaceHeight
                        thisSurface.Vertex_4_Xcoordinate = xDimension
                        thisSurface.Vertex_4_Ycoordinate = 0
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * thisSurfaceHeight                
                        
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'EastNonAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Outdoors'
                        thisSurface.Sun_Exposure = 'SunExposed'
                        thisSurface.Wind_Exposure = 'WindExposed'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = xDimension
                        thisSurface.Vertex_1_Ycoordinate = thisSurfaceAdiabaticBase
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = xDimension
                        thisSurface.Vertex_2_Ycoordinate = yDimension
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = xDimension
                        thisSurface.Vertex_3_Ycoordinate = yDimension
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = xDimension
                        thisSurface.Vertex_4_Ycoordinate = thisSurfaceAdiabaticBase
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * thisSurfaceHeight
                        if eastOR >= 0.01:
                            thisSurfaceCentroid = [round(thisSurfaceAdiabaticBase + (thisSurface.Vertex_2_Ycoordinate - thisSurface.Vertex_1_Ycoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*eastOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Shading_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Door'
                            thisWindow.Construction_Name = 'Door'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = xDimension
                            thisWindow.Vertex_1_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_2_Xcoordinate = xDimension
                            thisWindow.Vertex_2_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_3_Xcoordinate = xDimension
                            thisWindow.Vertex_3_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_3_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            thisWindow.Vertex_4_Xcoordinate = xDimension
                            thisWindow.Vertex_4_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_4_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = xDimension
                            thisWindow.Vertex_1_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_1_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            thisWindow.Vertex_2_Xcoordinate = xDimension
                            thisWindow.Vertex_2_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_2_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            thisWindow.Vertex_3_Xcoordinate = xDimension
                            thisWindow.Vertex_3_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = xDimension
                            thisWindow.Vertex_4_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            
                        else:
                            thisSurfaceCentroid = [round(thisSurfaceAdiabaticBase + (thisSurface.Vertex_2_Xcoordinate - thisSurface.Vertex_1_Xcoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*eastOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = xDimension
                            thisWindow.Vertex_1_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_2_Xcoordinate = xDimension
                            thisWindow.Vertex_2_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_3_Xcoordinate = xDimension
                            thisWindow.Vertex_3_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = xDimension
                            thisWindow.Vertex_4_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                        
                    if northAR == 0:
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'NorthNonAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Outdoors'
                        thisSurface.Sun_Exposure = 'SunExposed'
                        thisSurface.Wind_Exposure = 'WindExposed'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = xDimension
                        thisSurface.Vertex_1_Ycoordinate = yDimension
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = 0
                        thisSurface.Vertex_2_Ycoordinate = yDimension
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = 0
                        thisSurface.Vertex_3_Ycoordinate = yDimension
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = xDimension
                        thisSurface.Vertex_4_Ycoordinate = yDimension 
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * floorHeights[i]
                        
                        if northOR >= 0.01:
                            thisSurfaceCentroid = [round((thisSurface.Vertex_1_Xcoordinate - thisSurface.Vertex_2_Xcoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*northOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Shading_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Door'
                            thisWindow.Construction_Name = 'Door'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_1_Ycoordinate = yDimension
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_2_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_2_Ycoordinate = yDimension
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_3_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_3_Ycoordinate = yDimension
                            thisWindow.Vertex_3_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            thisWindow.Vertex_4_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_4_Ycoordinate = yDimension
                            thisWindow.Vertex_4_Zcoordinate = round(round(thisSurfaceCentroid[1] - windowHeight/2, 3) + windowObstructedHeight, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_1_Ycoordinate = yDimension
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_2_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_2_Ycoordinate = yDimension
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_3_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_3_Ycoordinate = yDimension
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_4_Ycoordinate = yDimension
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                        else:
                            thisSurfaceCentroid = [round((thisSurface.Vertex_1_Xcoordinate - thisSurface.Vertex_2_Xcoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*northOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_1_Ycoordinate = yDimension
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_2_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_2_Ycoordinate = yDimension
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_3_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_3_Ycoordinate = yDimension
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_4_Ycoordinate = yDimension
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                    elif northAR == 1:
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'NorthAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Adiabatic'
                        thisSurface.Sun_Exposure = 'NoSun'
                        thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = xDimension
                        thisSurface.Vertex_1_Ycoordinate = yDimension
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = 0
                        thisSurface.Vertex_2_Ycoordinate = yDimension
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = 0
                        thisSurface.Vertex_3_Ycoordinate = yDimension
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = xDimension
                        thisSurface.Vertex_4_Ycoordinate = yDimension 
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * floorHeights[i]
                    else:
                        thisSurfaceArea = xDimension*floorHeights[i]
                        thisSurfaceAdiabaticArea = thisSurfaceArea*northAR
                        thisSurfaceHeight = floorHeights[i]
                        thisSurfaceAdiabaticBase = round(thisSurfaceAdiabaticArea/thisSurfaceHeight, 3)
                        
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'NorthAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Adiabatic'
                        thisSurface.Sun_Exposure = 'NoSun'
                        thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = xDimension
                        thisSurface.Vertex_1_Ycoordinate = yDimension
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = xDimension - thisSurfaceAdiabaticBase
                        thisSurface.Vertex_2_Ycoordinate = yDimension
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = xDimension - thisSurfaceAdiabaticBase
                        thisSurface.Vertex_3_Ycoordinate = yDimension
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * thisSurfaceHeight
                        thisSurface.Vertex_4_Xcoordinate = xDimension
                        thisSurface.Vertex_4_Ycoordinate = yDimension
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * thisSurfaceHeight
                        
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'NorthNonAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Outdoors'
                        thisSurface.Sun_Exposure = 'SunExposed'
                        thisSurface.Wind_Exposure = 'WindExposed'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = xDimension - thisSurfaceAdiabaticBase
                        thisSurface.Vertex_1_Ycoordinate = yDimension
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = 0
                        thisSurface.Vertex_2_Ycoordinate = yDimension
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = 0
                        thisSurface.Vertex_3_Ycoordinate = yDimension
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = xDimension - thisSurfaceAdiabaticBase
                        thisSurface.Vertex_4_Ycoordinate = yDimension
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * thisSurfaceHeight
                        
                        if northOR >= 0.01:
                            thisSurfaceCentroid = [round((thisSurface.Vertex_1_Xcoordinate - thisSurface.Vertex_2_Xcoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*northOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Shading_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Door'
                            thisWindow.Construction_Name = 'Door'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_1_Ycoordinate = yDimension
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_2_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_2_Ycoordinate = yDimension
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_3_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_3_Ycoordinate = yDimension
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_4_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_4_Ycoordinate = yDimension
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_1_Ycoordinate = yDimension
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_2_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_2_Ycoordinate = yDimension
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_3_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_3_Ycoordinate = yDimension
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_4_Ycoordinate = yDimension
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                        else:
                            thisSurfaceCentroid = [round((thisSurface.Vertex_1_Xcoordinate - thisSurface.Vertex_2_Xcoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*northOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_1_Ycoordinate = yDimension
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_2_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_2_Ycoordinate = yDimension
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_3_Xcoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_3_Ycoordinate = yDimension
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_4_Ycoordinate = yDimension
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                    
                    if westAR == 0:
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'WestNonAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Outdoors'
                        thisSurface.Sun_Exposure = 'SunExposed'
                        thisSurface.Wind_Exposure = 'WindExposed'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = 0
                        thisSurface.Vertex_1_Ycoordinate = yDimension
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = 0
                        thisSurface.Vertex_2_Ycoordinate = 0
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = 0
                        thisSurface.Vertex_3_Ycoordinate = 0
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = 0
                        thisSurface.Vertex_4_Ycoordinate = yDimension 
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * floorHeights[i]
                        
                        if westOR >= 0.01:
                            thisSurfaceCentroid = [round((thisSurface.Vertex_1_Ycoordinate - thisSurface.Vertex_2_Ycoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*westOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Shading_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Door'
                            thisWindow.Construction_Name = 'Door'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = 0
                            thisWindow.Vertex_1_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_2_Xcoordinate = 0
                            thisWindow.Vertex_2_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_3_Xcoordinate = 0
                            thisWindow.Vertex_3_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_4_Xcoordinate = 0
                            thisWindow.Vertex_4_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = 0
                            thisWindow.Vertex_1_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_2_Xcoordinate = 0
                            thisWindow.Vertex_2_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_3_Xcoordinate = 0
                            thisWindow.Vertex_3_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = 0
                            thisWindow.Vertex_4_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                        else:
                            thisSurfaceCentroid = [round((thisSurface.Vertex_1_Ycoordinate - thisSurface.Vertex_2_Ycoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*westOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = 0
                            thisWindow.Vertex_1_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_2_Xcoordinate = 0
                            thisWindow.Vertex_2_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_3_Xcoordinate = 0
                            thisWindow.Vertex_3_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = 0
                            thisWindow.Vertex_4_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                    elif westAR == 1:
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'WestAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Adiabatic'
                        thisSurface.Sun_Exposure = 'NoSun'
                        thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = 0
                        thisSurface.Vertex_1_Ycoordinate = yDimension
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = 0
                        thisSurface.Vertex_2_Ycoordinate = 0
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = 0
                        thisSurface.Vertex_3_Ycoordinate = 0
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = 0
                        thisSurface.Vertex_4_Ycoordinate = yDimension 
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * floorHeights[i]
                    else:
                        thisSurfaceArea = yDimension*floorHeights[i]
                        thisSurfaceAdiabaticArea = thisSurfaceArea*westAR
                        thisSurfaceHeight = floorHeights[i]
                        thisSurfaceAdiabaticBase = round(thisSurfaceAdiabaticArea/thisSurfaceHeight, 3)
                        
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'WestAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Adiabatic'
                        thisSurface.Sun_Exposure = 'NoSun'
                        thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = 0
                        thisSurface.Vertex_1_Ycoordinate = yDimension
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = 0
                        thisSurface.Vertex_2_Ycoordinate = yDimension - thisSurfaceAdiabaticBase
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = 0
                        thisSurface.Vertex_3_Ycoordinate = yDimension - thisSurfaceAdiabaticBase
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * thisSurfaceHeight
                        thisSurface.Vertex_4_Xcoordinate = 0
                        thisSurface.Vertex_4_Ycoordinate = yDimension
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * thisSurfaceHeight
                        
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'WestNonAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Wall'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Outdoors'
                        thisSurface.Sun_Exposure = 'SunExposed'
                        thisSurface.Wind_Exposure = 'WindExposed'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = 0
                        thisSurface.Vertex_1_Ycoordinate = yDimension - thisSurfaceAdiabaticBase
                        thisSurface.Vertex_1_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = 0
                        thisSurface.Vertex_2_Ycoordinate = 0
                        thisSurface.Vertex_2_Zcoordinate = i * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = 0
                        thisSurface.Vertex_3_Ycoordinate = 0
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = 0
                        thisSurface.Vertex_4_Ycoordinate = yDimension - thisSurfaceAdiabaticBase
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * thisSurfaceHeight
                        
                        if westOR >= 0.01:
                            thisSurfaceCentroid = [round((thisSurface.Vertex_1_Ycoordinate - thisSurface.Vertex_2_Ycoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*westOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Shading_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Door'
                            thisWindow.Construction_Name = 'Door'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = 0
                            thisWindow.Vertex_1_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_2_Xcoordinate = 0
                            thisWindow.Vertex_2_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2, 3)
                            thisWindow.Vertex_3_Xcoordinate = 0
                            thisWindow.Vertex_3_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_4_Xcoordinate = 0
                            thisWindow.Vertex_4_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = 0
                            thisWindow.Vertex_1_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_2_Xcoordinate = 0
                            thisWindow.Vertex_2_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_3_Xcoordinate = 0
                            thisWindow.Vertex_3_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = 0
                            thisWindow.Vertex_4_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                        else:
                            thisSurfaceCentroid = [round((thisSurface.Vertex_1_Ycoordinate - thisSurface.Vertex_2_Ycoordinate)/2, 3),
                                                   round(i * floorHeights[i] + floorHeights[i]/2, 3)]
                            windowHeight = floorHeights[i] - 1 # set height of window to keep 0.5 m up and down
                            windowArea = thisSurface.area*WWR
                            windowBase = windowArea/windowHeight
                            windowObstructedArea = windowArea*westOR
                            windowObstructedHeight = round(windowObstructedArea/windowBase, 3)
                            
                            idf1.newidfobject("FenestrationSurface:Detailed")
                            thisWindow = windows[-1]
                            thisWindow.Name = 'Window_' + thisSurface.Name
                            thisWindow.Surface_Type = 'Window'
                            thisWindow.Construction_Name = 'Window'
                            thisWindow.Building_Surface_Name = thisSurface.Name
                            thisWindow.Number_of_Vertices = 4
                            thisWindow.Vertex_1_Xcoordinate = 0
                            thisWindow.Vertex_1_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_1_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_2_Xcoordinate = 0
                            thisWindow.Vertex_2_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_2_Zcoordinate = round(thisSurfaceCentroid[1] - windowHeight/2 + windowObstructedHeight, 3)
                            thisWindow.Vertex_3_Xcoordinate = 0
                            thisWindow.Vertex_3_Ycoordinate = round(thisSurfaceCentroid[0] - windowBase/2, 3)
                            thisWindow.Vertex_3_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                            thisWindow.Vertex_4_Xcoordinate = 0
                            thisWindow.Vertex_4_Ycoordinate = round(thisSurfaceCentroid[0] + windowBase/2, 3)
                            thisWindow.Vertex_4_Zcoordinate = round(thisSurfaceCentroid[1] + windowHeight/2, 3)
                    
                    if roofAR == 0:
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'RoofNonAdiabatic_' + zones[i].Name
                        thisSurface.Zone_Name = zones[i].Name
                        if i + 1 == len(zones):
                            thisSurface.Surface_Type = 'Roof'
                            thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                            thisSurface.Outside_Boundary_Condition = 'Outdoors'
                            thisSurface.Sun_Exposure = 'SunExposed'
                            thisSurface.Wind_Exposure = 'WindExposed'
                        else:
                            thisSurface.Surface_Type = 'Ceiling'
                            thisSurface.Construction_Name = 'EnvelopeFlipped' # in the future differentiate this part for surfaces
                            thisSurface.Outside_Boundary_Condition = 'Surface'
                            thisSurface.Outside_Boundary_Condition_Object = 'FloorNonAdiabatic_' + zones[i+1].Name
                            thisSurface.Sun_Exposure = 'NoSun'
                            thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = 0
                        thisSurface.Vertex_1_Ycoordinate = 0
                        thisSurface.Vertex_1_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = xDimension
                        thisSurface.Vertex_2_Ycoordinate = 0
                        thisSurface.Vertex_2_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = xDimension
                        thisSurface.Vertex_3_Ycoordinate = yDimension
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = 0
                        thisSurface.Vertex_4_Ycoordinate = yDimension
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * floorHeights[i]
                    elif roofAR == 1:
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'RoofAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Ceiling'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Adiabatic'
                        thisSurface.Sun_Exposure = 'NoSun'
                        thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = 0
                        thisSurface.Vertex_1_Ycoordinate = 0
                        thisSurface.Vertex_1_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = xDimension
                        thisSurface.Vertex_2_Ycoordinate = 0
                        thisSurface.Vertex_2_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = xDimension
                        thisSurface.Vertex_3_Ycoordinate = yDimension
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = 0
                        thisSurface.Vertex_4_Ycoordinate = yDimension
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * floorHeights[i]
                    else:
                        thisSurfaceArea = xDimension*yDimension
                        thisSurfaceAdiabaticArea = thisSurfaceArea*roofAR
                        thisSurfaceHeight = yDimension
                        thisSurfaceAdiabaticBase = round(thisSurfaceAdiabaticArea/thisSurfaceHeight, 3)
                        
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'RoofAdiabatic_' + zones[i].Name
                        thisSurface.Surface_Type = 'Ceiling'
                        thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                        thisSurface.Zone_Name = zones[i].Name
                        thisSurface.Outside_Boundary_Condition = 'Adiabatic'
                        thisSurface.Sun_Exposure = 'NoSun'
                        thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = 0
                        thisSurface.Vertex_1_Ycoordinate = 0
                        thisSurface.Vertex_1_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = thisSurfaceAdiabaticBase
                        thisSurface.Vertex_2_Ycoordinate = 0
                        thisSurface.Vertex_2_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = thisSurfaceAdiabaticBase
                        thisSurface.Vertex_3_Ycoordinate = thisSurfaceHeight
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = 0
                        thisSurface.Vertex_4_Ycoordinate = thisSurfaceHeight
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * floorHeights[i]
                        
                        idf1.newidfobject("BuildingSurface:Detailed")
                        thisSurface = surfaces[-1]
                        thisSurface.Name = 'RoofNonAdiabatic_' + zones[i].Name
                        thisSurface.Zone_Name = zones[i].Name
                        if i + 1 == len(zones):
                            thisSurface.Surface_Type = 'Roof'
                            thisSurface.Construction_Name = 'Envelope' # in the future differentiate this part for surfaces
                            thisSurface.Outside_Boundary_Condition = 'Outdoors'
                            thisSurface.Sun_Exposure = 'SunExposed'
                            thisSurface.Wind_Exposure = 'WindExposed'
                        else:
                            thisSurface.Surface_Type = 'Ceiling'
                            thisSurface.Construction_Name = 'EnvelopeFlipped' # in the future differentiate this part for surfaces
                            thisSurface.Outside_Boundary_Condition = 'Surface'
                            thisSurface.Outside_Boundary_Condition_Object = 'FloorNonAdiabatic_' + zones[i+1].Name
                            thisSurface.Sun_Exposure = 'NoSun'
                            thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.Sun_Exposure = 'NoSun'
                        thisSurface.Wind_Exposure = 'NoWind'
                        thisSurface.View_Factor_to_Ground = 'autocalculate'
                        thisSurface.Number_of_Vertices = 4
                        thisSurface.Vertex_1_Xcoordinate = thisSurfaceAdiabaticBase
                        thisSurface.Vertex_1_Ycoordinate = 0
                        thisSurface.Vertex_1_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_2_Xcoordinate = xDimension
                        thisSurface.Vertex_2_Ycoordinate = 0
                        thisSurface.Vertex_2_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_3_Xcoordinate = xDimension
                        thisSurface.Vertex_3_Ycoordinate = thisSurfaceHeight
                        thisSurface.Vertex_3_Zcoordinate = (i + 1) * floorHeights[i]
                        thisSurface.Vertex_4_Xcoordinate = thisSurfaceAdiabaticBase
                        thisSurface.Vertex_4_Ycoordinate = thisSurfaceHeight
                        thisSurface.Vertex_4_Zcoordinate = (i + 1) * floorHeights[i]          
                    
                # Run Period
                if months[j] == 'January':
                    idf1.idfobjects["RunPeriod"][0].Begin_Month = 1
                    idf1.idfobjects["RunPeriod"][0].Begin_Day_of_Month = 1
                    idf1.idfobjects["RunPeriod"][0].End_Month = 1
                    idf1.idfobjects["RunPeriod"][0].End_Day_of_Month = 31
                elif months[j] == 'February':
                    idf1.idfobjects["RunPeriod"][0].Begin_Month = 1
                    idf1.idfobjects["RunPeriod"][0].Begin_Day_of_Month = 25
                    idf1.idfobjects["RunPeriod"][0].End_Month = 2
                    idf1.idfobjects["RunPeriod"][0].End_Day_of_Month = 28
                elif months[j] == 'March':
                    idf1.idfobjects["RunPeriod"][0].Begin_Month = 2
                    idf1.idfobjects["RunPeriod"][0].Begin_Day_of_Month = 21
                    idf1.idfobjects["RunPeriod"][0].End_Month = 3
                    idf1.idfobjects["RunPeriod"][0].End_Day_of_Month = 31
                elif months[j] == 'April':
                    idf1.idfobjects["RunPeriod"][0].Begin_Month = 3
                    idf1.idfobjects["RunPeriod"][0].Begin_Day_of_Month = 25
                    idf1.idfobjects["RunPeriod"][0].End_Month = 4
                    idf1.idfobjects["RunPeriod"][0].End_Day_of_Month = 30
                elif months[j] == 'May':
                    idf1.idfobjects["RunPeriod"][0].Begin_Month = 4
                    idf1.idfobjects["RunPeriod"][0].Begin_Day_of_Month = 24
                    idf1.idfobjects["RunPeriod"][0].End_Month = 5
                    idf1.idfobjects["RunPeriod"][0].End_Day_of_Month = 31
                elif months[j] == 'June':
                    idf1.idfobjects["RunPeriod"][0].Begin_Month = 5
                    idf1.idfobjects["RunPeriod"][0].Begin_Day_of_Month = 25
                    idf1.idfobjects["RunPeriod"][0].End_Month = 6
                    idf1.idfobjects["RunPeriod"][0].End_Day_of_Month = 30
                elif months[j] == 'July':
                    idf1.idfobjects["RunPeriod"][0].Begin_Month = 6
                    idf1.idfobjects["RunPeriod"][0].Begin_Day_of_Month = 24
                    idf1.idfobjects["RunPeriod"][0].End_Month = 7
                    idf1.idfobjects["RunPeriod"][0].End_Day_of_Month = 31
                elif months[j] == 'August':
                    idf1.idfobjects["RunPeriod"][0].Begin_Month = 7
                    idf1.idfobjects["RunPeriod"][0].Begin_Day_of_Month = 24
                    idf1.idfobjects["RunPeriod"][0].End_Month = 8
                    idf1.idfobjects["RunPeriod"][0].End_Day_of_Month = 31
                elif months[j] == 'September':
                    idf1.idfobjects["RunPeriod"][0].Begin_Month = 8
                    idf1.idfobjects["RunPeriod"][0].Begin_Day_of_Month = 25
                    idf1.idfobjects["RunPeriod"][0].End_Month = 9
                    idf1.idfobjects["RunPeriod"][0].End_Day_of_Month = 30
                elif months[j] == 'October':
                    idf1.idfobjects["RunPeriod"][0].Begin_Month = 9
                    idf1.idfobjects["RunPeriod"][0].Begin_Day_of_Month = 24
                    idf1.idfobjects["RunPeriod"][0].End_Month = 10
                    idf1.idfobjects["RunPeriod"][0].End_Day_of_Month = 31
                elif months[j] == 'November':
                    idf1.idfobjects["RunPeriod"][0].Begin_Month = 10
                    idf1.idfobjects["RunPeriod"][0].Begin_Day_of_Month = 25
                    idf1.idfobjects["RunPeriod"][0].End_Month = 11
                    idf1.idfobjects["RunPeriod"][0].End_Day_of_Month = 30
                elif months[j] == 'December':
                    idf1.idfobjects["RunPeriod"][0].Begin_Month = 11
                    idf1.idfobjects["RunPeriod"][0].Begin_Day_of_Month = 24
                    idf1.idfobjects["RunPeriod"][0].End_Month = 12
                    idf1.idfobjects["RunPeriod"][0].End_Day_of_Month = 31
                
                idf1.save(simplifiedModelsMonthlyPath + filename + "_" + months[j] + "_Simplified.idf")
                    
                # need to remove surfaces and windows because cycle recreates them
                surfaces = idf1.idfobjects["BuildingSurface:Detailed"]
                while len(surfaces) != 0:
                    idf1.removeidfobject(surfaces[0])
                
                windows = idf1.idfobjects["FenestrationSurface:Detailed"]
                while len(windows) != 0:
                    idf1.removeidfobject(windows[0])
            # remove base file created without modified geometry
            os.remove(simplifiedModelsMonthlyPath + filename + "_Simplified.idf")

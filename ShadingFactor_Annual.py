# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 17:26:05 2023

@author: FBattini
"""

# %%

from eppy.modeleditor import IDF
import pandas as pd
import os

# %%

def shadingFactor_Annual(fnameRad, fileRad, climate, epw, detailedRadiationAnalysisAnnualPath, baseFolderPath):
    
# %% Analyze radiation results 

    idf1 = IDF(fnameRad)
    csvFile = fnameRad.split(".")[0] + ".csv"
    resultsFile = pd.read_csv(csvFile, index_col = 0)
    resultsFile = resultsFile.filter(regex = "GLZ")
    windows = idf1.idfobjects["FenestrationSurface:Detailed"]
    zones = idf1.idfobjects["Zone"]
    for i in range(len(zones)):
        resultsFile["northRadiation_Flr"+str(i+1)], resultsFile["eastRadiation_Flr"+str(i+1)], resultsFile["southRadiation_Flr"+str(i+1)], resultsFile["westRadiation_Flr"+str(i+1)] = 0, 0, 0, 0
    areaNorthFlr1, areaEastFlr1, areaSouthFlr1, areaWestFlr1 = 0, 0, 0, 0 
    if len(zones) == 2:
        areaNorthFlr2, areaEastFlr2, areaSouthFlr2, areaWestFlr2 = 0, 0, 0, 0
    if len(zones) == 3:
        areaNorthFlr2, areaEastFlr2, areaSouthFlr2, areaWestFlr2 = 0, 0, 0, 0
        areaNorthFlr3, areaEastFlr3, areaSouthFlr3, areaWestFlr3 = 0, 0, 0, 0
    if len(zones) == 4:
        areaNorthFlr2, areaEastFlr2, areaSouthFlr2, areaWestFlr2 = 0, 0, 0, 0
        areaNorthFlr3, areaEastFlr3, areaSouthFlr3, areaWestFlr3 = 0, 0, 0, 0
        areaNorthFlr4, areaEastFlr4, areaSouthFlr4, areaWestFlr4 = 0, 0, 0, 0 
    for i in range(len(windows)):
        if windows[i].Name.upper() in resultsFile.iloc[:,i].name:
            if windows[i].azimuth > 315 or windows[i].azimuth <= 45:
                if zones[0].Name in windows[i].Name:
                    resultsFile["northRadiation_Flr1"] +=resultsFile.iloc[:,i]*windows[i].area
                    areaNorthFlr1 += windows[i].area
                if len(zones) > 1:
                    if zones[1].Name in windows[i].Name:
                        resultsFile["northRadiation_Flr2"] +=resultsFile.iloc[:,i]*windows[i].area
                        areaNorthFlr2 += windows[i].area
                    if len(zones) > 2:
                        if zones[2].Name in windows[i].Name:
                            resultsFile["northRadiation_Flr3"] +=resultsFile.iloc[:,i]*windows[i].area
                            areaNorthFlr3 += windows[i].area
                        if len(zones) > 3:
                            if zones[3].Name in windows[i].Name:
                                resultsFile["northRadiation_Flr4"] +=resultsFile.iloc[:,i]*windows[i].area
                                areaNorthFlr4 += windows[i].area
            if windows[i].azimuth > 45 and windows[i].azimuth <= 135:
                if zones[0].Name in windows[i].Name:
                    resultsFile["eastRadiation_Flr1"] +=resultsFile.iloc[:,i]*windows[i].area
                    areaEastFlr1 += windows[i].area
                if len(zones) > 1:
                    if zones[1].Name in windows[i].Name:
                        resultsFile["eastRadiation_Flr2"] +=resultsFile.iloc[:,i]*windows[i].area
                        areaEastFlr2 += windows[i].area
                    if len(zones) > 2:
                        if zones[2].Name in windows[i].Name:
                            resultsFile["eastRadiation_Flr3"] +=resultsFile.iloc[:,i]*windows[i].area
                            areaEastFlr3 += windows[i].area
                        if len(zones) > 3:
                            if zones[3].Name in windows[i].Name:
                                resultsFile["eastRadiation_Flr4"] +=resultsFile.iloc[:,i]*windows[i].area
                                areaEastFlr4 += windows[i].area
            if windows[i].azimuth > 135 and windows[i].azimuth <= 225:
                if zones[0].Name in windows[i].Name:
                    resultsFile["southRadiation_Flr1"] +=resultsFile.iloc[:,i]*windows[i].area
                    areaSouthFlr1 += windows[i].area
                if len(zones) > 1:
                    if zones[1].Name in windows[i].Name:
                        resultsFile["southRadiation_Flr2"] +=resultsFile.iloc[:,i]*windows[i].area
                        areaSouthFlr2 += windows[i].area
                    if len(zones) > 2:
                        if zones[2].Name in windows[i].Name:
                            resultsFile["southRadiation_Flr3"] +=resultsFile.iloc[:,i]*windows[i].area
                            areaSouthFlr3 += windows[i].area
                        if len(zones) > 3:
                            if zones[3].Name in windows[i].Name:
                                resultsFile["southRadiation_Flr4"] +=resultsFile.iloc[:,i]*windows[i].area
                                areaSouthFlr4 += windows[i].area
            if windows[i].azimuth > 225 and windows[i].azimuth <= 315:
                if zones[0].Name in windows[i].Name:
                    resultsFile["westRadiation_Flr1"] +=resultsFile.iloc[:,i]*windows[i].area
                    areaWestFlr1 += windows[i].area
                if len(zones) > 1:
                    if zones[1].Name in windows[i].Name:
                        resultsFile["westRadiation_Flr2"] +=resultsFile.iloc[:,i]*windows[i].area
                        areaWestFlr2 += windows[i].area
                    if len(zones) > 2:
                        if zones[2].Name in windows[i].Name:
                            resultsFile["westRadiation_Flr3"] +=resultsFile.iloc[:,i]*windows[i].area
                            areaWestFlr3 += windows[i].area
                        if len(zones) > 3:
                            if zones[3].Name in windows[i].Name:
                                resultsFile["westRadiation_Flr4"] +=resultsFile.iloc[:,i]*windows[i].area
                                areaWestFlr4 += windows[i].area
        else:
            print(windows[i].Name)
            #print("Window mismatch")
    if len(zones) == 1:
        resultsFile.iloc[:,len(windows)] = resultsFile.iloc[:,len(windows)]/areaNorthFlr1
        resultsFile.iloc[:,len(windows)+1] = resultsFile.iloc[:,len(windows)+1]/areaEastFlr1
        resultsFile.iloc[:,len(windows)+2] = resultsFile.iloc[:,len(windows)+2]/areaSouthFlr1
        resultsFile.iloc[:,len(windows)+3] = resultsFile.iloc[:,len(windows)+3]/areaWestFlr1
        radiationDF = resultsFile.iloc[:,-4*len(zones):]
    if len(zones) == 2:
        resultsFile.iloc[:,len(windows)] = resultsFile.iloc[:,len(windows)]/areaNorthFlr1
        resultsFile.iloc[:,len(windows)+1] = resultsFile.iloc[:,len(windows)+1]/areaEastFlr1
        resultsFile.iloc[:,len(windows)+2] = resultsFile.iloc[:,len(windows)+2]/areaSouthFlr1
        resultsFile.iloc[:,len(windows)+3] = resultsFile.iloc[:,len(windows)+3]/areaWestFlr1
        resultsFile.iloc[:,len(windows)+4] = resultsFile.iloc[:,len(windows)+4]/areaNorthFlr2
        resultsFile.iloc[:,len(windows)+5] = resultsFile.iloc[:,len(windows)+5]/areaEastFlr2
        resultsFile.iloc[:,len(windows)+6] = resultsFile.iloc[:,len(windows)+6]/areaSouthFlr2
        resultsFile.iloc[:,len(windows)+7] = resultsFile.iloc[:,len(windows)+7]/areaWestFlr2
        radiationDF = resultsFile.iloc[:,-4*len(zones):]
    if len(zones) == 3:
        resultsFile.iloc[:,len(windows)] = resultsFile.iloc[:,len(windows)]/areaNorthFlr1
        resultsFile.iloc[:,len(windows)+1] = resultsFile.iloc[:,len(windows)+1]/areaEastFlr1
        resultsFile.iloc[:,len(windows)+2] = resultsFile.iloc[:,len(windows)+2]/areaSouthFlr1
        resultsFile.iloc[:,len(windows)+3] = resultsFile.iloc[:,len(windows)+3]/areaWestFlr1
        resultsFile.iloc[:,len(windows)+4] = resultsFile.iloc[:,len(windows)+4]/areaNorthFlr2
        resultsFile.iloc[:,len(windows)+5] = resultsFile.iloc[:,len(windows)+5]/areaEastFlr2
        resultsFile.iloc[:,len(windows)+6] = resultsFile.iloc[:,len(windows)+6]/areaSouthFlr2
        resultsFile.iloc[:,len(windows)+7] = resultsFile.iloc[:,len(windows)+7]/areaWestFlr2
        resultsFile.iloc[:,len(windows)+8] = resultsFile.iloc[:,len(windows)+8]/areaNorthFlr3
        resultsFile.iloc[:,len(windows)+9] = resultsFile.iloc[:,len(windows)+9]/areaEastFlr3
        resultsFile.iloc[:,len(windows)+10] = resultsFile.iloc[:,len(windows)+10]/areaSouthFlr3
        resultsFile.iloc[:,len(windows)+11] = resultsFile.iloc[:,len(windows)+11]/areaWestFlr3
        radiationDF = resultsFile.iloc[:,-4*len(zones):]
    if len(zones) == 4:
        resultsFile.iloc[:,len(windows)] = resultsFile.iloc[:,len(windows)]/areaNorthFlr1
        resultsFile.iloc[:,len(windows)+1] = resultsFile.iloc[:,len(windows)+1]/areaEastFlr1
        resultsFile.iloc[:,len(windows)+2] = resultsFile.iloc[:,len(windows)+2]/areaSouthFlr1
        resultsFile.iloc[:,len(windows)+3] = resultsFile.iloc[:,len(windows)+3]/areaWestFlr1
        resultsFile.iloc[:,len(windows)+4] = resultsFile.iloc[:,len(windows)+4]/areaNorthFlr2
        resultsFile.iloc[:,len(windows)+5] = resultsFile.iloc[:,len(windows)+5]/areaEastFlr2
        resultsFile.iloc[:,len(windows)+6] = resultsFile.iloc[:,len(windows)+6]/areaSouthFlr2
        resultsFile.iloc[:,len(windows)+7] = resultsFile.iloc[:,len(windows)+7]/areaWestFlr2
        resultsFile.iloc[:,len(windows)+8] = resultsFile.iloc[:,len(windows)+8]/areaNorthFlr3
        resultsFile.iloc[:,len(windows)+9] = resultsFile.iloc[:,len(windows)+9]/areaEastFlr3
        resultsFile.iloc[:,len(windows)+10] = resultsFile.iloc[:,len(windows)+10]/areaSouthFlr3
        resultsFile.iloc[:,len(windows)+11] = resultsFile.iloc[:,len(windows)+11]/areaWestFlr3
        resultsFile.iloc[:,len(windows)+12] = resultsFile.iloc[:,len(windows)+12]/areaNorthFlr4
        resultsFile.iloc[:,len(windows)+13] = resultsFile.iloc[:,len(windows)+13]/areaEastFlr4
        resultsFile.iloc[:,len(windows)+14] = resultsFile.iloc[:,len(windows)+14]/areaSouthFlr4
        resultsFile.iloc[:,len(windows)+15] = resultsFile.iloc[:,len(windows)+15]/areaWestFlr4
        radiationDF = resultsFile.iloc[:,-4*len(zones):]
    #radiationDF.to_csv(fnameRad.split(".")[0] + "_Radiation.csv")
# %% Compute shadings 
    # get shoebox base files    
    shoeboxRadFiles = []
    for file in os.listdir(baseFolderPath):
        if file.endswith(".csv") and "Shoebox" in file and "Annual" in file:
            shoeboxRadFiles.append(file)
    # check if shoebox file is available for this climate, if yes, get it
    for shoeboxRadFile in shoeboxRadFiles:
        if climate in shoeboxRadFile:
            shoeboxRadiationFile = shoeboxRadFile
            shoeboxRadiation = pd.read_csv(baseFolderPath + '/' + shoeboxRadiationFile, index_col = 0)
    # if it is not available, create it, simulate it and get the results in the right format
    try:
        shoeboxRadiation
    except NameError:
        fname = baseFolderPath + "/ShoeboxRadiation.idf"
        idf1 = IDF(fname, epw)
        Output = idf1.idfobjects["Output:Variable"]
        Output[0].Reporting_Frequency = "Annual"
        idf1.run(output_prefix = "ShoeboxRadiation_" + climate + "_Annual", readvars=True)
        # remove simulation files
        for file in os.listdir(baseFolderPath):
            if os.path.isfile(file):
                if not file.endswith(".csv") and not file.endswith(".idf") and not file.endswith(".txt") and not file.endswith(".py"):
                    os.remove(file)
        # rename to remove "out" in name
        for file in os.listdir(baseFolderPath):
            if os.path.isfile(file):
                if climate in file and "Annual" in file:
                    os.rename(file, "ShoeboxRadiation_" + climate + "_Annual.csv")
        # postprocess results to make them ready to be used
        radiationFileToModify = pd.read_csv("ShoeboxRadiation_" + climate + "_Annual.csv")
        shoeboxRadiation = pd.DataFrame({"northRadiation": radiationFileToModify.iloc[:,4].values,
                                         "eastRadiation": radiationFileToModify.iloc[:,3].values,
                                         "southRadiation": radiationFileToModify.iloc[:,2].values,
                                         "westRadiation": radiationFileToModify.iloc[:,1].values},
                                         index = radiationFileToModify.iloc[:,0].values)
        shoeboxRadiation.to_csv("ShoeboxRadiation_" + climate + "_Annual.csv")
    # combine building and shoebox data to get shading ratios        
    buildingRadiation = radiationDF.copy()
    shadingFactor = pd.DataFrame([])
    if len(buildingRadiation.columns) > 3:
        shadingFactor["northShading_Flr1"] = 1 - (buildingRadiation.iloc[:,0]/shoeboxRadiation.iloc[:,0])
        shadingFactor["eastShading_Flr1"] = 1 - (buildingRadiation.iloc[:,1]/shoeboxRadiation.iloc[:,1])
        shadingFactor["southShading_Flr1"] = 1 - (buildingRadiation.iloc[:,2]/shoeboxRadiation.iloc[:,2])
        shadingFactor["westShading_Flr1"] = 1 - (buildingRadiation.iloc[:,3]/shoeboxRadiation.iloc[:,3])
    if len(buildingRadiation.columns) > 7:
        shadingFactor["northShading_Flr2"] = 1 - (buildingRadiation.iloc[:,4]/shoeboxRadiation.iloc[:,0])
        shadingFactor["eastShading_Flr2"] = 1 - (buildingRadiation.iloc[:,5]/shoeboxRadiation.iloc[:,1])
        shadingFactor["southShading_Flr2"] = 1 - (buildingRadiation.iloc[:,6]/shoeboxRadiation.iloc[:,2])
        shadingFactor["westShading_Flr2"] = 1 - (buildingRadiation.iloc[:,7]/shoeboxRadiation.iloc[:,3])
    if len(buildingRadiation.columns) > 11:
        shadingFactor["northShading_Flr3"] = 1 - (buildingRadiation.iloc[:,8]/shoeboxRadiation.iloc[:,0])
        shadingFactor["eastShading_Flr3"] = 1 - (buildingRadiation.iloc[:,9]/shoeboxRadiation.iloc[:,1])
        shadingFactor["southShading_Flr3"] = 1 - (buildingRadiation.iloc[:,10]/shoeboxRadiation.iloc[:,2])
        shadingFactor["westShading_Flr3"] = 1 - (buildingRadiation.iloc[:,11]/shoeboxRadiation.iloc[:,3])
    if len(buildingRadiation.columns) > 15:
        shadingFactor["northShading_Flr4"] = 1 - (buildingRadiation.iloc[:,12]/shoeboxRadiation.iloc[:,0])
        shadingFactor["eastShading_Flr4"] = 1 - (buildingRadiation.iloc[:,13]/shoeboxRadiation.iloc[:,1])
        shadingFactor["southShading_Flr4"] = 1 - (buildingRadiation.iloc[:,14]/shoeboxRadiation.iloc[:,2])
        shadingFactor["westShading_Flr4"] = 1 - (buildingRadiation.iloc[:,15]/shoeboxRadiation.iloc[:,3])
    shadingFactor.to_csv(detailedRadiationAnalysisAnnualPath + fileRad.split(".")[0] + ".csv")
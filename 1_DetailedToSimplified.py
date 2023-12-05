# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 12:03:26 2023

@author: FBattini

This code takes the detailed models .idf files and uses them to obtain what
is required to set up the simplified model
"""

# %%

import pandas as pd
import numpy as np
import scipy.optimize
import eppy
from eppy.modeleditor import IDF
import sys
import os
from os import listdir
from math import sqrt
from eppy.runner.run_functions import runIDFs
from CreateFilesForRadiationAnalysis_Annual import setUpFilesForRadiationAnalysis_Annual
from CreateFilesForRadiationAnalysis_Monthly import setUpFilesForRadiationAnalysis_Monthly
from ShadingFactor_Monthly import shadingFactor_Monthly
from ShadingFactor_Annual import shadingFactor_Annual
from IndicatorsDimensions import computeIndicatorsDimensions
from GetAdiabaticRatios import computeAdiabaticRatios
from SimplifiedModels_Annual import createSimplifiedModels_Annual
from SimplifiedModels_Monthly import createSimplifiedModels_Monthly

# %%
def make_eplaunch_options(idf):
    """Make options for run, so that it runs like EPLaunch on Windows"""
    idfversion = idf.idfobjects['version'][0].Version_Identifier.split('.')
    idfversion.extend([0] * (3 - len(idfversion)))
    idfversionstr = '-'.join([str(item) for item in idfversion])
    fname = idf.idfname
    options = {
        'ep_version':idfversionstr, # runIDFs needs the version number
        'output_prefix':os.path.basename(fname).split('.')[0],
        'output_suffix':'C',
        'output_directory':os.path.dirname(fname),
        'readvars':True,
        'expandobjects':True
               }
    return options

def main():
    # %%
    # define things for eppy and energyplus
    eppy_path = "C:/Anaconda3/Lib/site-packages/eppy"
    sys.path.append(eppy_path)
    iddfile = "C:/EnergyPlusV9-4-0/Energy+.idd"
    IDF.setiddname(iddfile)
    
    # %%
    # Define variables to access right folder
    simplificationType = 'Annual'
    num_CPUs = 2
    runSimulationLocally = True
    climate = 'Bolzano'
    caseStudy = 'Simulation'

    # Set current directory as the working directory
    baseFolderPath = os.getcwd()
    os.chdir(baseFolderPath)
    
    # Define all the required paths to folders
    thisCaseStudyFolderPath = '{}/{}/'.format(baseFolderPath, caseStudy)
    detailedFolderPath = '{}Detailed/'.format(thisCaseStudyFolderPath)
    
    # Get epw for this climate
    epw = '{}/WeatherFiles/{}.epw'.format(baseFolderPath, climate)

    # if detailed not simulated run them
    detailedCSVs = []
    for file in os.listdir(detailedFolderPath):
        if file.endswith(".csv"):
            detailedCSVs.append(file)
    if len(detailedCSVs) == 0:
        os.chdir(detailedFolderPath)
        fnames = [f for f in listdir(detailedFolderPath) if os.path.isfile(os.path.join(detailedFolderPath, f))]
        idfs =(IDF(fname, epw) for fname in fnames)
        runs = ((idf, make_eplaunch_options(idf)) for idf in idfs)
        runIDFs(runs, num_CPUs)
        for file in listdir(detailedFolderPath):
            if not file.endswith(".csv") and not file.endswith(".idf"):
                os.remove(file)
        os.chdir(baseFolderPath)
    
    # Check the folders in the case study folder to understand if it is necessary to redo the simplification process
    subfoldersOfCaseStudy = os.listdir(thisCaseStudyFolderPath)
    if "DetailedRadiation_Annual" in subfoldersOfCaseStudy:
        try:
            if len(os.listdir('{}DetailedRadiation_Annual/'.format(thisCaseStudyFolderPath))) > 0:
                detailedRadiationAnnualFiles_Done = True
            else:
                detailedRadiationAnnualFiles_Done = False
        except OSError:
            detailedRadiationAnnualFiles_Done = False
    else:
        detailedRadiationAnnualFiles_Done = False
    
    if "DetailedRadiation_Monthly" in subfoldersOfCaseStudy:
        try:
            if len(os.listdir('{}DetailedRadiation_Monthly/'.format(thisCaseStudyFolderPath))) > 0:
                detailedRadiationMonthlyFiles_Done = True
            else:
                detailedRadiationMonthlyFiles_Done = False
        except OSError:
            detailedRadiationMonthlyFiles_Done = False
    else:
        detailedRadiationMonthlyFiles_Done = False
    
    if "DetailedRadiationAnalysis_Annual" in subfoldersOfCaseStudy:
        try:
            if len(os.listdir('{}DetailedRadiationAnalysis_Annual/'.format(thisCaseStudyFolderPath))) > 0:
                detailedRadiationAnnualAnalysis_Done = True
            else:
                detailedRadiationAnnualAnalysis_Done = False
        except OSError:
            detailedRadiationAnnualAnalysis_Done = False
    else:
        detailedRadiationAnnualAnalysis_Done = False
        
    if "DetailedRadiationAnalysis_Monthly" in subfoldersOfCaseStudy:
        try:
            if len(os.listdir('{}DetailedRadiationAnalysis_Monthly/'.format(thisCaseStudyFolderPath))) > 0:
                detailedRadiationMonthlyAnalysis_Done = True
            else:
                detailedRadiationMonthlyAnalysis_Done = False
        except OSError:
            detailedRadiationMonthlyAnalysis_Done = False
    else:
        detailedRadiationMonthlyAnalysis_Done = False
        
    if "!Indicators.csv" and "!Dimensions.csv" in subfoldersOfCaseStudy:
        indicatorsDimensions_Done = True
    else:
        indicatorsDimensions_Done = False
    
    if "AdiabaticRatios" in subfoldersOfCaseStudy:
        adiabaticRatios_Done = True
    else:
        adiabaticRatios_Done = False
        
    if "Simplified_Annual" in subfoldersOfCaseStudy:
        simplifiedModelsAnnual_Done = True
    else:
        simplifiedModelsAnnual_Done = False
    
    if "Simplified_Monthly" in subfoldersOfCaseStudy:
        simplifiedModelsMonthly_Done = True
    else:
        simplifiedModelsMonthly_Done = False
    
    # %%
    
    adiabaticRatiosPath = '{}AdiabaticRatios/'.format(thisCaseStudyFolderPath)
    
    if simplificationType == "Annual":
        detailedRadiationAnnualPath = '{}DetailedRadiation_Annual/'.format(thisCaseStudyFolderPath)
        detailedRadiationAnalysisAnnualPath = '{}DetailedRadiationAnalysis_Annual/'.format(thisCaseStudyFolderPath)
        simplifiedModelsAnnualPath = '{}Simplified_Annual/'.format(thisCaseStudyFolderPath)
        # create radiation files if not done
        if not detailedRadiationAnnualFiles_Done:
            setUpFilesForRadiationAnalysis_Annual(thisCaseStudyFolderPath, detailedFolderPath)
        # run radiation files locally if required
        if runSimulationLocally and detailedRadiationAnnualFiles_Done == False:
            os.chdir(detailedRadiationAnnualPath)
            fnames = [f for f in listdir(detailedRadiationAnnualPath) if os.path.isfile(os.path.join(detailedRadiationAnnualPath, f))]
            idfs =(IDF(fname, epw) for fname in fnames)
            runs = ((idf, make_eplaunch_options(idf)) for idf in idfs)
            runIDFs(runs, num_CPUs)
            for file in listdir(detailedRadiationAnnualPath):
                if not file.endswith(".csv") and not file.endswith(".idf"):
                    os.remove(file)
            os.chdir(baseFolderPath)
        # analyze radiation results and get obstruction ratios
        if not detailedRadiationAnnualAnalysis_Done:
            # if the folder doesn't exist create it
            try:
                os.listdir(detailedRadiationAnalysisAnnualPath)
            except OSError:
                os.mkdir(detailedRadiationAnalysisAnnualPath)
            for fileRad in os.listdir(detailedRadiationAnnualPath):
                if fileRad.endswith(".idf"):
                    if os.path.isfile(detailedRadiationAnnualPath + fileRad.split(".")[0] + ".csv"):
                        fnameRad = detailedRadiationAnnualPath + fileRad
                        shadingFactor_Annual(fnameRad, fileRad, climate, epw, detailedRadiationAnalysisAnnualPath, baseFolderPath)
        # find indicators and dimensions of shoeboxes                
        if not indicatorsDimensions_Done:
            computeIndicatorsDimensions(thisCaseStudyFolderPath, detailedFolderPath)
        # find adiabatic ratios                
        if not adiabaticRatios_Done:
            # if the folder doesn't exist create it
            try:
                os.listdir(adiabaticRatiosPath)
            except OSError:
                os.mkdir(adiabaticRatiosPath)
            computeAdiabaticRatios(thisCaseStudyFolderPath, detailedFolderPath)
        # create simplified models                
        if not simplifiedModelsAnnual_Done:
            # if the folder doesn't exist create it
            try:
                os.listdir(simplifiedModelsAnnualPath)
            except OSError:
                os.mkdir(simplifiedModelsAnnualPath)
            createSimplifiedModels_Annual(thisCaseStudyFolderPath, detailedFolderPath)
            # run simplified models
            os.chdir(simplifiedModelsAnnualPath)
            fnames = [f for f in listdir(simplifiedModelsAnnualPath) if os.path.isfile(os.path.join(simplifiedModelsAnnualPath, f))]
            idfs =(IDF(fname, epw) for fname in fnames)
            runs = ((idf, make_eplaunch_options(idf)) for idf in idfs)
            runIDFs(runs, num_CPUs)
            for file in listdir(simplifiedModelsAnnualPath):
                if not file.endswith(".csv") and not file.endswith(".idf"):
                    os.remove(file)
            os.chdir(baseFolderPath)
                            
        
    elif simplificationType == "Monthly":
        detailedRadiationMonthlyPath = '{}DetailedRadiation_Monthly/'.format(thisCaseStudyFolderPath)
        detailedRadiationAnalysisMonthlyPath = '{}DetailedRadiationAnalysis_Monthly/'.format(thisCaseStudyFolderPath)
        simplifiedModelsMonthlyPath = '{}Simplified_Monthly/'.format(thisCaseStudyFolderPath)
        # create radiation files if not done
        if not detailedRadiationMonthlyFiles_Done:
            setUpFilesForRadiationAnalysis_Monthly(thisCaseStudyFolderPath, detailedFolderPath)
        # run radiation files locally if required
        if runSimulationLocally and detailedRadiationMonthlyFiles_Done == False:
            os.chdir(detailedRadiationMonthlyPath)
            fnames = [f for f in listdir(detailedRadiationMonthlyPath) if os.path.isfile(os.path.join(detailedRadiationMonthlyPath, f))]
            idfs =(IDF(fname, epw) for fname in fnames)
            runs = ((idf, make_eplaunch_options(idf)) for idf in idfs)
            runIDFs(runs, num_CPUs)
            for file in listdir(detailedRadiationMonthlyPath):
                if not file.endswith(".csv") and not file.endswith(".idf"):
                    os.remove(file)
            os.chdir(baseFolderPath)
        # analyze radiation results and get obstruction ratios
        if not detailedRadiationMonthlyAnalysis_Done:
            # if the folder doesn't exist create it
            try:
                os.listdir(detailedRadiationAnalysisMonthlyPath)
            except OSError:
                os.mkdir(detailedRadiationAnalysisMonthlyPath)
            for fileRad in os.listdir(detailedRadiationMonthlyPath):
                if fileRad.endswith(".idf"):
                    if os.path.isfile(detailedRadiationMonthlyPath + fileRad.split(".")[0] + ".csv"):
                        fnameRad = detailedRadiationMonthlyPath + fileRad
                        shadingFactor_Monthly(fnameRad, fileRad, climate, epw, detailedRadiationAnalysisMonthlyPath, baseFolderPath)
        # find indicators and dimensions of shoeboxes                
        if not indicatorsDimensions_Done:
            computeIndicatorsDimensions(thisCaseStudyFolderPath, detailedFolderPath)      
        # find adiabatic ratios                
        if not adiabaticRatios_Done:
            # if the folder doesn't exist create it
            try:
                os.listdir(adiabaticRatiosPath)
            except OSError:
                os.mkdir(adiabaticRatiosPath)
            computeAdiabaticRatios(thisCaseStudyFolderPath, detailedFolderPath)
        # create simplified models                
        if not simplifiedModelsMonthly_Done:
            # if the folder doesn't exist create it
            try:
                os.listdir(simplifiedModelsMonthlyPath)
            except OSError:
                os.mkdir(simplifiedModelsMonthlyPath)
            createSimplifiedModels_Monthly(thisCaseStudyFolderPath, detailedFolderPath)  
            # run simplified models
            os.chdir(simplifiedModelsMonthlyPath)
            fnames = [f for f in listdir(simplifiedModelsMonthlyPath) if os.path.isfile(os.path.join(simplifiedModelsMonthlyPath, f))]
            idfs =(IDF(fname, epw) for fname in fnames)
            runs = ((idf, make_eplaunch_options(idf)) for idf in idfs)
            runIDFs(runs, num_CPUs)
            for file in listdir(simplifiedModelsMonthlyPath):
                if not file.endswith(".csv") and not file.endswith(".idf"):
                    os.remove(file)
            os.chdir(baseFolderPath)

if __name__ == '__main__':
    main()
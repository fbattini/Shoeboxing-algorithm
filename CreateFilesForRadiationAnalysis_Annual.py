# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 16:03:48 2023

@author: FBattini
"""
# %%

import os
from eppy.modeleditor import IDF

# %%

def setUpFilesForRadiationAnalysis_Annual(thisCaseStudyFolderPath, detailedFolderPath):
    # set the folder in which the radiation files are going to be stored and simulated
    detailedRadiationAnnualPath = '{}DetailedRadiation_Annual/'.format(thisCaseStudyFolderPath)
    
    # if the folder does exist count if files are inside, otherwise create it and count
    try:
        radiationSimulationFiles_annual = os.listdir(detailedRadiationAnnualPath)
    except OSError:
        os.mkdir(detailedRadiationAnnualPath)
        radiationSimulationFiles_annual = os.listdir(detailedRadiationAnnualPath)
    
    if len(radiationSimulationFiles_annual) == 0:
        # loop through detailed idfs to create idfs for solar radiation
        for file in os.listdir(detailedFolderPath):
            if file.endswith(".idf"):
                fname = file
                filename = os.path.splitext(file)[0].replace(".idf", "")
                idf1 = IDF(detailedFolderPath + fname)
                
                ### Modify file to perform fast radiation analysis ###
                # Shadow Calculation
                idf1.idfobjects["ShadowCalculation"][0].Shading_Calculation_Update_Frequency = 30
                # Timestep
                idf1.idfobjects["Timestep"][0].Number_of_Timesteps_per_Hour = 1
                # Schedule typelimits
                scheduleTypeLimits = idf1.idfobjects["ScheduleTypeLimits"]
                while len(scheduleTypeLimits) != 0:
                    idf1.removeidfobject(scheduleTypeLimits[0])
                # Schedule compact
                scheduleCompact = idf1.idfobjects["Schedule:Compact"]
                while len(scheduleCompact) != 0:
                    idf1.removeidfobject(scheduleCompact[0])
                # Other equipment
                gains = idf1.idfobjects["OtherEquipment"]
                while len(gains) != 0:
                    idf1.removeidfobject(gains[0])
                # Zone infiltration
                ZoneInfiltration = idf1.idfobjects["ZoneInfiltration:DesignFlowRate"]
                while len(ZoneInfiltration) != 0:
                    idf1.removeidfobject(ZoneInfiltration[0])
                # Thermostat
                ZoneThermostat = idf1.idfobjects["ZoneControl:Thermostat"]
                while len(ZoneThermostat) != 0:
                    idf1.removeidfobject(ZoneThermostat[0])
                ThermostatSetpoint = idf1.idfobjects["ThermostatSetpoint:DualSetpoint"]
                while len(ThermostatSetpoint) != 0:
                    idf1.removeidfobject(ThermostatSetpoint[0])
                # System
                AirSystem = idf1.idfobjects["ZoneHVAC:IdealLoadsAirSystem"]
                while len(AirSystem) != 0:
                    idf1.removeidfobject(AirSystem[0])
                # Equipment list
                EquipmentList = idf1.idfobjects["ZoneHVAC:EquipmentList"]
                while len(EquipmentList) != 0:
                    idf1.removeidfobject(EquipmentList[0])
                # Equipment connections
                EquipmentConnections = idf1.idfobjects["ZoneHVAC:EquipmentConnections"]
                while len(EquipmentConnections) != 0:
                    idf1.removeidfobject(EquipmentConnections[0])
                # Summary reports
                SummaryReport = idf1.idfobjects["Output:Table:SummaryReports"]
                while len(SummaryReport) != 0:
                    idf1.removeidfobject(SummaryReport[0])
                # Output variables
                Output = idf1.idfobjects["Output:Variable"]
                while len(Output) != 0:
                    idf1.removeidfobject(Output[0])
                idf1.newidfobject("Output:Variable")
                Output[0].Variable_Name = "Surface Outside Face Incident Solar Radiation Rate per Area"
                Output[0].Reporting_Frequency = "Annual"
                # save file with new name in new folder
                idf1.save("{}{}.idf".format(detailedRadiationAnnualPath, filename))
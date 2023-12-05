# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 15:03:24 2023

@author: FBattini
"""

# %%

import pandas as pd
import os
from eppy.modeleditor import IDF
import numpy as np
from math import sqrt
import scipy.optimize

# %%

def getOneLength(x1, y1, x2, y2):
   return sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))

def findPerimeter(points):
   N = len(points)
   firstx, firsty = points[0]
   prevx, prevy = firstx, firsty
   res = 0

   for i in range(1, N):
      nextx, nexty = points[i]
      res = res + getOneLength(prevx,prevy,nextx,nexty)
      prevx = nextx
      prevy = nexty
   res = res + getOneLength(prevx,prevy,firstx,firsty)
   return res

def computeIndicatorsDimensions(thisCaseStudyFolderPath, detailedFolderPath):
    
    def equations(p):
        x, y, z = p
        return (2*(x+y)/(x*y) - perimeterAreaRatio, 1 - x/y - elongation, (2*x*y + 2*x*z + 2*y*z)/(x*y*z) - shapeFactor)

    indicatorsDF = pd.DataFrame([], columns=['EdgeRatio', 'Elongation', 'ShapeFactor'])
    dimensionsDF = pd.DataFrame([], columns=['X', 'Y', 'Z'])
    for file in os.listdir(detailedFolderPath):
        if file.endswith(".idf"):
            fname = file
            filename = os.path.splitext(file)[0].replace(".idf", "")
            idf1 = IDF(detailedFolderPath + fname)
            # get floor min and max coordinates, perimeter and area
            surfaces = idf1.idfobjects["BuildingSurface:Detailed"]
            for surface in surfaces:
                if surface.Surface_Type == 'Floor':
                    break
            verticesIndex = surface.objls.index("Number_of_Vertices")
            firstX = verticesIndex + 1  # X of first coordinate
            pts = surface.obj[firstX:]
            vertices = np.reshape(pts, (-1, 3))
            minZ = np.min(vertices[:, 2])
            vertices = vertices[:,:2]
            
            xlength = np.max(vertices[:, 0]) - np.min(vertices[:, 0])
            ylength = np.max(vertices[:, 1]) - np.min(vertices[:, 1])
            floorPerimeter = findPerimeter(vertices)
            floorArea = surface.area
            
            # get building height
            for surface in surfaces:
                if surface.Surface_Type == 'Roof':
                    break
            verticesIndex = surface.objls.index("Number_of_Vertices")
            firstX = verticesIndex + 1  # X of first coordinate
            pts = surface.obj[firstX:]
            vertices = np.reshape(pts, (-1, 3))
            maxZ = np.max(vertices[:, 2])
            
            height = maxZ - minZ
            
            # find remaining quantities
            volume = height*floorArea
            exposedSurface = floorPerimeter*height + 2*floorArea
            
            # compute indicators
            perimeterAreaRatio = floorPerimeter/floorArea
            elongation = 1 - xlength/ylength
            shapeFactor = exposedSurface/volume
            indicators = pd.DataFrame([[perimeterAreaRatio, elongation, shapeFactor]], columns=['EdgeRatio', 'Elongation', 'ShapeFactor'], index = [filename])
            indicatorsDF = pd.concat([indicatorsDF, indicators])
            
            # find shoebox's dimensions
            x, y, z = scipy.optimize.fsolve(equations, (1,1,1))
            x = float(round(x,3))
            y = float(round(y,3))
            z = round(z,2)
            dimensions = pd.DataFrame([[x, y, z]], columns=['X', 'Y', 'Z'], index = [filename])
            dimensionsDF = pd.concat([dimensionsDF, dimensions])
            
    indicatorsDF.to_csv(thisCaseStudyFolderPath + '!Indicators.csv')
    dimensionsDF.to_csv(thisCaseStudyFolderPath + '!Dimensions.csv')

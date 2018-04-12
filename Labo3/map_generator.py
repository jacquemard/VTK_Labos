#############################################
## HEIG-VD - VTK - Labo 3
## Carte Topographique en relief
## Rémi Jacquemard & Francois Quellec
## 06.04.18
#############################################

import vtk
import random
import math
import os
import numpy as np

def main():
    # Get the solutions
    file = open("altitudes.txt", "r")
    
    xSize, ySize = [int(i) for i in file.readline().split()]

    # creating geometry
    points = vtk.vtkPoints()
    altitudes = vtk.vtkIntArray()
    for x in range(xSize):
        altitude = file.readline().split()
        for y in range(ySize):
            points.InsertNextPoint(x, y, int(altitude[y])/4)
            altitudes.InsertNextValue(int(altitude[y]))
    file.close() 

    # creating dataset with implicit topology
    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(xSize, ySize, 1)
    grid.SetPoints(points)
    grid.GetPointData().SetScalars(altitudes)

    # Find min and max z
    bounds = [0]*6
    grid.GetBounds(bounds)
    minz = bounds[4]
    maxz = bounds[5]

    # Init our LUT table to find the colors
    colorTable = vtk.vtkLookupTable()
    colorTable.SetTableRange(minz, maxz)
    colorTable.Build()

    # Create a mapper and actor
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(grid)
    mapper.UseLookupTableScalarRangeOn()
    mapper.SetLookupTable(colorTable)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Create the renderer 
    ren1= vtk.vtkRenderer()
    ren1.AddActor(actor)
    ren1.SetBackground( 1, 1, 1)
    
    #Add the renderer to the window
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer( ren1 )
    renWin.SetSize( 2400, 2400 )
    renWin.Render()

   #start the interaction window and add TrackBall Style
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.SetRenderWindow(renWin)
    iren.Start()

if __name__ == '__main__':
   main()

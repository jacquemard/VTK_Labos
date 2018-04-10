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

# Check if the argument is an Integer
def isInteger(char):
    try: 
        int(char)
        return True
    except ValueError:
        return False

# Parse the input into an array with the right dimensions
def parseInput(filename):
    inputFile = open(filename, "r")
    
    dimensions = inputFile.readline().split(' ')
    width = int(dimensions[0])
    height = int(dimensions[1])

    inputTab = np.empty((height, width), 'int')

    for y in range(0, height):
        dephts = inputFile.readline().split(' ')
        for x in range(0, width):
            if isInteger(dephts[x]):
                inputTab[y][x] = dephts[x]

    inputFile.close() 
    return inputTab

#Initialise the map with points
def initPoints(inputTab):
    vtkPoints = vtk.vtkPoints()
    for y in range(0,len(inputTab)):
        for x in range(0,len(inputTab[0])):
            vtkPoints.InsertNextPoint(x, y, inputTab[y][x])
          
    return vtkPoints


def main():
    # Get the solutions
    inputTab = parseInput("altitudes.txt")
    vtkPoints = initPoints(inputTab)

    # Add the grid points to a polydata object
    inPolyData = vtk.vtkPolyData()
    inPolyData.SetPoints(vtkPoints)

    # Triangulate the grid points
    delaunay = vtk.vtkDelaunay2D()
    delaunay.SetInputData(inPolyData);
    delaunay.Update()
    outPolyData = delaunay.GetOutput()

    # Find min and max z
    bounds = [0]*6
    outPolyData.GetBounds(bounds)
    minz = bounds[4]
    maxz = bounds[5]

    # Init our LUT table to find the colors
    colorTable = vtk.vtkLookupTable()
    colorTable.SetTableRange(minz, maxz)
    colorTable.Build()

    # Init our colors array
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    colors.SetName("Colors")

    # For each point find the color with the LUT table
    for i in range(0, outPolyData.GetNumberOfPoints()):
        # Get the next point coordinates
        point = [0,0,0]
        outPolyData.GetPoint(i, point)

        # Get the associate color with the LUT
        dcolor = [0, 0, 0]
        colorTable.GetColor(point[2], dcolor);

        # Convert in the right format
        color = [0, 0, 0]
        for x in range(0,3):
            color[x] = dcolor[x] * 255

        # Add the color to the scalar
        colors.InsertNextTuple3(color[0], color[1], color[2])

    # Assign the colors to the polydata's points 
    outPolyData.GetPointData().SetScalars(colors)

    # Create a mapper and actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(outPolyData)
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

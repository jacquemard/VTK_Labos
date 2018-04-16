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
    radius = 6371009
    phi_min = 45
    phi_max = 47.5
    theta_min = 5
    theta_max = 7.5
    delta_phi = (phi_max - phi_min)/xSize
    delta_theta = (theta_max - theta_min)/ySize

    # creating geometry
    points = vtk.vtkPoints()
    altitudes = vtk.vtkIntArray()
    minz = radius * 2
    maxz = -1

    for x in range(xSize):
        altitude = file.readline().split()
        for y in range(ySize):
            #print("RotateX:", delta_phi*x + phi_min)
            #print("RotateY:", delta_theta*y + theta_min)
            z = radius + int(altitude[y])

            t = vtk.vtkTransform()

            #Place the point  
            t.RotateX(delta_phi*x + phi_min)
            t.RotateY(delta_theta*y + theta_min)
            t.Translate(0, 0, z)
            
            #Apply transformation
            p_in = [0, 0, 0, 1]
            p_out = [0, 0, 0, 1]
            t.MultiplyPoint(p_in, p_out)

            #print("p:", p_out[0], p_out[1], p_out[2])
            points.InsertNextPoint(p_out[0], p_out[1], p_out[2])

            altitudes.InsertNextValue(z)
            if(z < minz):
                minz = z
            if(z > maxz):
                maxz = z

            

    file.close() 

    # creating dataset with implicit topology
    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(xSize, ySize, 1)
    grid.SetPoints(points)
    grid.GetPointData().SetScalars(altitudes)

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

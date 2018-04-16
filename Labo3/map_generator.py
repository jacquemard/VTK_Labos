#############################################
# HEIG-VD - VTK - Labo 3
# Carte Topographique en relief
# Rémi Jacquemard & Francois Quellec
# 06.04.18
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

    altitudes_north = np.zeros(xSize, dtype=np.uint16)
    altitude_west = 0

    # creating geometry
    points = vtk.vtkPoints()
    altitudes = vtk.vtkIntArray()
    altitudes.SetNumberOfValues(xSize * ySize)

    #altitudes_xy = np.zeros([xSize, ySize], dtype=np.uint16)
    #altitudes_xy_water = np.zeros([xSize, ySize], dtype=np.uint16)
    min_alt = None
    max_alt = None

    for y in range(ySize):
        altitude = file.readline().split()
        if y % 100 == 0:
            print('Preparing y = ' + str(y))

        for x in range(xSize):
            #print("RotateX:", delta_phi*x + phi_min)
            #print("RotateY:", delta_theta*y + theta_min)
            alt = int(altitude[x])

            #altitudes_xy[x, y] = alt
            #altitudes_xy_water[x, y] = alt

            # finding water (flat land)
            '''
            if x > 0 and y > 0:
                # checking if it is the same altitude as the north and the west side
                if altitudes_xy[x - 1, y] == alt:
                    altitudes_xy_water[x - 1, y] = 0
                    altitudes_xy_water[x, y] = 0
                if altitudes_xy[x, y - 1] == alt:
                    altitudes_xy_water[x, y - 1] = 0
                    altitudes_xy_water[x, y] = 0
            ''' 

            # finding min and max altitudes
            if min_alt == None or alt < min_alt:
                min_alt = alt
            if max_alt == None or alt > max_alt:
                max_alt = alt

            #alt = altitudes_xy[x, y]
            
            z = radius + alt

            t = vtk.vtkTransform()

            # Place the point
            t.RotateX(phi_min + delta_phi*x)
            t.RotateY(theta_max - delta_theta*y)
            t.Translate(0, 0, z)

            # Apply transformation
            p_in = [0, 0, 0, 1]
            p_out = [0, 0, 0, 1]
            t.MultiplyPoint(p_in, p_out)
            

            #print("p:", p_out[0], p_out[1], p_out[2])
            points.InsertNextPoint(p_out[0], p_out[1], p_out[2])
            '''
            points.InsertNextPoint(x, y, alt)
            '''

            # Updating altitudes
            alt_water = alt
            index = y * xSize + x
            #print(alt)
            
            
            # checking for a square (unoising)
            '''
            alt_delta = 0
            if (altitudes_north[x] - alt_delta <= alt <= altitudes_north[x] + alt_delta
                and x > 0 and altitudes_north[x - 1] - alt_delta <= alt <= altitudes_north[x - 1] + alt_delta
                and altitude_west - alt_delta <= alt <= altitude_west + alt_delta):
                altitudes.SetValue((y - 1) * xSize + x, 0)
                altitudes.SetValue(index - 1, 0)
                alt_water = 0
            #'''
            
            #if altitude_west == alt:
            #    altitudes.SetValue(index - 1, 0)
            #    alt_water = 0

            

            altitudes.SetValue(index, alt_water)
            

            # Updating north and west altitudes value
            altitude_west = alt
            altitudes_north[x] = alt


    file.close()

    # creating dataset with implicit topology
    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(xSize, ySize, 1)
    grid.SetPoints(points)
    grid.GetPointData().SetScalars(altitudes)

    # Init our mapping to find the colors
    colorTable = vtk.vtkColorTransferFunction()
    colorTable.AdjustRange([min_alt, max_alt])
    colorTable.AddRGBPoint(min_alt, 0.185, 0.67, 0.29)
    colorTable.AddRGBPoint(1000, 0.839, 0.812, 0.624)
    colorTable.AddRGBPoint(2000, 0.84, 0.84, 0.84)
    colorTable.AddRGBPoint(max_alt, 1, 1, 1)
    #colorTable.SetTableRange(min_alt, max_alt)
    #colorTable.SetTableValue(min_alt, 0, 0, 0, 1)
    #colorTable.SetTableValue(max_alt, 1, 1, 1, 1)
    # Water is set to 0m (see-level) as an altitude
    colorTable.SetBelowRangeColor(0.513, 0.49, 1)
    colorTable.UseBelowRangeColorOn()
    colorTable.Build()

    # Create a mapper and actor
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(grid)
    mapper.UseLookupTableScalarRangeOn()
    mapper.SetLookupTable(colorTable)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Create the renderer
    ren1 = vtk.vtkRenderer()
    ren1.AddActor(actor)
    ren1.SetBackground(1, 1, 1)

    # Add the renderer to the window
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren1)
    renWin.SetSize(1200, 700)
    renWin.Render()

   # start the interaction window and add TrackBall Style
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.SetRenderWindow(renWin)
    iren.Start()


if __name__ == '__main__':
    main()

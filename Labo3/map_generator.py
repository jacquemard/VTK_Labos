#############################################
# HEIG-VD - VTK - Labo 3
# Carte Topographique en relief
# Rémi Jacquemard & Francois Quellec
# 18.04.18
#############################################

import vtk
import random
import math
import os
import numpy as np

# defining the sea level
sea_level = 0

# exporting a map as a png. 
export_map = False

def export_png(renWin, filename):
    """
        Used to export a single png file from a window.
        renWin: the window to capture as screenshot from
        filename: the filename to output, including a .png extension
    """

    # Creating an image filter using the window as input
    imageFilter = vtk.vtkWindowToImageFilter()
    imageFilter.SetInput(renWin)
    imageFilter.SetScale(3)
    imageFilter.SetInputBufferTypeToRGBA()
    imageFilter.Update()

    # Writing the image to the file
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(filename)
    writer.SetInputConnection(imageFilter.GetOutputPort())
    
    writer.Write()


def main():
    """
        Entry point of the app
    """

    # Importing the solutions from the file
    file = open("altitudes.txt", "r")

    # Reading the first line which contain the size of the matrix
    xSize, ySize = [int(i) for i in file.readline().split()]

    # Defining constants relating to the map
    radius = 6371009 # Earth radius
    lat_min = 45
    lat_max = 47.5
    long_min = 5
    long_max = 7.5

    # The latitudes and longitudes of each point of the matrix can be easily compute
    # using differences of latitudes/longitudes between each point
    delta_lat = (lat_max - lat_min)/ySize
    delta_long = (long_max - long_min)/xSize

    # Used to find water. At any time, we remember the altitudes from the 2 above latitudes, and the current latitude.
    # Doing so, we can find 3x3 squares which have the same altitudes. It forms a plain plane, which can be some water.
    # Using a 3x3 square denoises this detection.
    # To have a low memory allocation, we only track for 3 latitudes.
    altitudes_y3 = np.zeros([3, xSize], dtype=np.uint16)    

    # Defining geometry
    points = vtk.vtkPoints()
    # Defining altitudes of each point
    altitudeValues = vtk.vtkIntArray()
    altitudeValues.SetNumberOfValues(xSize * ySize)

    
    def compute_point(x, y, alt):
        """
            Method used to convert the x-y-z(altitude without earth radius) values from the matrix to x-y-z world coordinates
        """
        t = vtk.vtkTransform()
        t.PostMultiply()

        # Rotating the point from latitude and longitude
        t.RotateY(-lat_min + delta_lat * y)
        t.RotateZ(long_min + delta_long * x)

        # Describing the point and setting it on the x axe, at the right altitude.
        p_in = [radius + alt, 0, 0]
        p_out = [0, 0, 0]
        t.TransformPoint(p_in, p_out)

        ''' 
        # It can be done with a sphericalTransform too
        t = vtk.vtkSphericalTransform()

        # Apply transformation
        p_in = [radius + z, math.radians(lat_min + delta_lat * y), math.radians(long_min + delta_long * x)]
        p_out = [0, 0, 0]
        t.TransformPoint(p_in, p_out)
        '''

        return p_out

    # Minimum and maximum altitude found in the map
    min_alt = None
    max_alt = None

    for y in range(ySize): # Exploring each altitude from the file
        # array of altitudes of the current latitude
        altitudes = file.readline().split() 

        if y % 100 == 0:
            print('Computing y = ' + str(y))

        for x in range(xSize): # For each x value 
            alt = int(altitudes[x]) # Getting the associated altitude

            # finding min and max altitudes 
            if min_alt == None or alt < min_alt:
                min_alt = alt
            if max_alt == None or alt > max_alt:
                max_alt = alt

            # Computing world coordinates from x-y-altitude
            point = compute_point(x, y, alt)
            
            # Inserting the point to the listOfPoints
            points.InsertNextPoint(point[0], point[1], point[2])

            # Computing the index of the point from the x and y value (flattening a 2 dimension matrix to a 1 dimension one)
            index = y * xSize + x
            
            # Setting the altitude of the current point as a point scalar
            altitudeValues.SetValue(index, alt)
            
            # checking for a square 3x3 (denoising)
            altitudes_y3[2, x] = alt # updating box
            if x >= 2 and y >= 2:
                # extracting the 3x3 box
                box = altitudes_y3[...,x - 2 : x + 1]

                # Exploring the box and checking if all of the altitudes are the same             
                val = box[0, 0]
                ok = True
                for i in range(3):
                    for j in range(3):
                        if val != box[i, j]: 
                            ok = False
                            break
                    if not ok:
                        break

                if ok: # if all of the altitudes are the same, it is probably some water
                    for i in range(3):
                        for j in range(3):
                            # Updating the scalar associated with the point.
                            # We are using the '0' value, which correspond to the sea level
                            altitudeValues.SetValue((y - j) * ySize + (x - i), 0)

            # If the current altitude is below the sea-level, we can set the associated scalar as a water value
            if alt < sea_level:
                altitudeValues.SetValue(index, 0)

        # updating the 3 latitudes
        altitudes_y3[0] = altitudes_y3[1]
        altitudes_y3[1] = altitudes_y3[2]
        altitudes_y3[2] = np.zeros(xSize)

    file.close()

    # creating a dataset
    # vtkStructuredGrid has an implicit topology and take less memory than a polydata
    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(xSize, ySize, 1)
    grid.SetPoints(points)
    grid.GetPointData().SetScalars(altitudeValues)

    # Init our mapping to find the colors
    # We use a colorTranferFunction with point for different altitudes 
    colorTable = vtk.vtkColorTransferFunction()
    colorTable.AdjustRange([min_alt, max_alt]) # Adjusting range from the minimum and maximum altitudes computed before
    colorTable.AddRGBPoint(min_alt, 0.185, 0.67, 0.29) # green land
    colorTable.AddRGBPoint(1000, 0.839, 0.812, 0.624) # brown land
    colorTable.AddRGBPoint(2000, 0.84, 0.84, 0.84) # grey rock
    colorTable.AddRGBPoint(max_alt, 1, 1, 1) # white snow
    # Water is set to 0m (sea-level) as an altitude
    colorTable.SetBelowRangeColor(0.513, 0.49, 1) # blue water
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
    ren = vtk.vtkRenderer()
    ren.AddActor(actor)
    ren.SetBackground(1, 1, 1)

    # Moving the camera
    camera = vtk.vtkCamera()
    distance = 600000 # the camera will be at ~600000m above the surface
    center_high = compute_point(xSize/2, ySize/2, distance)[0:3]
    camera.SetPosition(center_high)
    center = compute_point(xSize/2, ySize/2, 0)[0:3]
    camera.SetFocalPoint(center) # looking at the center of the map
    camera.SetRoll(266)
    camera.SetClippingRange(1, 100000000)
    ren.SetActiveCamera(camera)

    # Creating a window to display the render
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetSize(900, 900)
    renWin.Render()

    # Exporting a map if we want to
    if export_map:
        export_png(renWin, str(sea_level) + "sea.png")

    # start the interaction window and add TrackBall Style
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.SetRenderWindow(renWin)
    iren.Start()

if __name__ == '__main__':
    main()
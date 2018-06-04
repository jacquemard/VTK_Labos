#############################################
# HEIG-VD - VTK - Labo 5
# Scanner d'un genou
# Rémi Jacquemard & Francois Quellec
# Mai-Juin 2018
#############################################

import vtk
import math
import numpy as np
import math
import pyproj
from datetime import datetime

# Constantes definitions
PATH_MAP = "EarthEnv-DEM90_N60E010.bil"
PATH_IMG = "glider_map.jpg"
PATH_PLANE_GPS = "vtkgps.txt"

RT90_PROJECTION = pyproj.Proj(init='epsg:3021')
GPS_PROJECTION = pyproj.Proj(init='epsg:4326')

RATIO_DEG_METERS = 6000 / 5. # meter/degrees ratio (6000 points for 5 degrees)

def convert_to_gps(x, y):
    x, y =  pyproj.transform(RT90_PROJECTION, GPS_PROJECTION, x, y)
    return (x, y)

TOP_LEFT_COORDINATES = convert_to_gps(1349340, 7022573)
TOP_RIGHT_COORDINATES = convert_to_gps(1371573, 7022967)
BOTTOM_RIGHT_COORDINATES = convert_to_gps(1371835, 7006362)
BOTTOM_LEFT_COORDINATES = convert_to_gps(1349602, 7005969)


def load_plane(width_meters, height_meters):
    file = open(PATH_PLANE_GPS, 'r')
    nbLines = int(file.readline())
    coords = []

    for line in range(0, nbLines):
        (_, x, y, z, date, time, _, _, _, _) = file.readline().split()
        x = int(x)
        y = int(y)
        z = float(z)
        date = datetime.strptime(date + ' ' + time, '%y/%d/%m %H:%M:%S')
        x, y = convert_to_gps(x, y)
        coords.append((x, y, z, date))

    points = vtk.vtkPoints()
    scalars = vtk.vtkFloatArray()
    line = vtk.vtkPolyLine()
    cells = vtk.vtkCellArray()
    polydata = vtk.vtkPolyData()

    line.GetPointIds().SetNumberOfIds(len(coords))

    prev_height = 512.5 # min height of the map
    min_scalar, max_scalar = 0, 0

    for i, (x, y, z, _) in enumerate(coords):
        plane_coords = ((x - TOP_LEFT_COORDINATES[0]) * RATIO_DEG_METERS * width_meters, (y - TOP_RIGHT_COORDINATES[1]) * RATIO_DEG_METERS * height_meters, z)
        points.InsertPoint(i, plane_coords)
        line.GetPointIds().SetId(i, i)
        scalars.InsertNextValue(prev_height-z)
        if min_scalar > prev_height-z:
            min_scalar = prev_height-z
        if max_scalar < prev_height-z:
            max_scalar = prev_height-z
        prev_height = z

    cells.InsertNextCell(line)
    polydata.SetPoints(points)
    polydata.SetLines(cells)
    polydata.GetPointData().SetScalars(scalars)

    tube = vtk.vtkTubeFilter()
    tube.SetRadius(30)
    tube.SetNumberOfSides(50)
    tube.SetInputData(polydata)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(tube.GetOutputPort())
    mapper.SetScalarRange(min_scalar/2, max_scalar/2)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    mapper.Update()

    return actor

def load_map():
    # Load the map
    file = np.fromfile(PATH_MAP, dtype=np.int16).reshape(6000, 6000)

    # Select only the desired area  TO DO CHECK THIS PART !!!
    top_bound = max(TOP_LEFT_COORDINATES[1], TOP_RIGHT_COORDINATES[1])
    bottom_bound = min(BOTTOM_RIGHT_COORDINATES[1], BOTTOM_LEFT_COORDINATES[1])
    left_bound = min(TOP_LEFT_COORDINATES[0], BOTTOM_LEFT_COORDINATES[0])
    right_bound = max(TOP_RIGHT_COORDINATES[0], BOTTOM_RIGHT_COORDINATES[0])

    top_index = int(math.floor((65 - top_bound) * RATIO_DEG_METERS))
    bot_index = int(math.floor((65 - bottom_bound) * RATIO_DEG_METERS))
    left_index = int(math.floor((left_bound - 10) * RATIO_DEG_METERS))
    right_index = int(math.floor((right_bound - 10) * RATIO_DEG_METERS))

    file = file[top_index:bot_index, left_index:right_index]

    # build the map polydata from our file
    map = vtk.vtkPolyData()
    height, width = file.shape
    print(file.shape)

    height_meters = 16700. / height # 16700 = distance between top left and bottom left GPS points in meters
    width_meters = 22000. / width # 22000 = distance between top left and top right GPS points in meters

    index_deg_ratio_x = width / (right_bound - left_bound) # matrix index/degrees ratio for x values
    index_deg_ratio_y = height / (top_bound - bottom_bound) # matrix index/degrees ratio for y values

    # Matrix indexes of four corners
    top_left_index = (int(math.floor((TOP_LEFT_COORDINATES[0] - left_index) * index_deg_ratio_x)), int(math.floor((top_index - TOP_LEFT_COORDINATES[1]) * index_deg_ratio_y)))
    top_right_index = (int(math.floor((TOP_RIGHT_COORDINATES[0] - left_index) * index_deg_ratio_x)), int(math.floor((top_index - TOP_RIGHT_COORDINATES[1]) * index_deg_ratio_y)))
    bot_right_index = (int(math.floor((BOTTOM_RIGHT_COORDINATES[0] - left_index) * index_deg_ratio_x)), int(math.floor((top_index - BOTTOM_RIGHT_COORDINATES[1]) * index_deg_ratio_y)))
    bot_left_index = (int(math.floor((BOTTOM_LEFT_COORDINATES[0] - left_index) * index_deg_ratio_x)), int(math.floor((top_index - BOTTOM_LEFT_COORDINATES[1]) * index_deg_ratio_y)))

    theta = math.atan((bot_right_index[1]) / float((width - bot_left_index[0]))) # texture angle difference

    gradient_1 = float(top_left_index[0] - bot_left_index[0]) / (top_left_index[1] - bot_left_index[1]) # the gradient of the texture's width line to the x axis
    gradient_2 = (top_left_index[1] - top_right_index[1]) / float(top_left_index[0] - top_right_index[0]) # the gradient of the texture's height line to the y axis

    text_width = (width - bot_left_index[0]) / math.cos(theta)
    text_height = (height - top_left_index[1]) / math.cos(theta)

    def getPointIndex(i, j):
        return width * i + j

    # Draw the points of the map
    points = vtk.vtkPoints()
    mapping_array = vtk.vtkFloatArray()
    mapping_array.SetNumberOfComponents(2)

    for y, row in enumerate(file):
        for x, z in enumerate(row):
            coord_x = float(width_meters * x) # transform y in meters
            coord_y = float(height_meters * y) # transform x in meters
            points.InsertNextPoint((coord_x, -coord_y, z))

            text_x = (x - (gradient_1 * y)) / math.cos(theta) - top_left_index[0] # calculates the x2 value (on texture map)
            text_y = (y - (gradient_2 * x)) / math.cos(theta) - top_left_index[1] # calculates the y2 value (on texture map)

            if text_x <= 0 or text_y <= 0 or text_x >= text_width or text_y >= text_height: # Outside the texture
                mapping_array.InsertNextTuple((0, 0))
            else:
                # weights x2 and y2 to be in the range [0, 1]
                x2 = text_x / text_width
                y2 = text_y / text_height
                mapping_array.InsertNextTuple((text_x / text_width, 1 - (text_y / (text_height))))

    map.SetPoints(points)
    map.GetPointData().SetTCoords(mapping_array) # set texture coords

    # draws the map using triangle strips
    strip = vtk.vtkCellArray()
    for y in range(0, height - 1):
        strip.InsertNextCell((width - 1) * 2)
        for x in range(0, width - 1):
            strip.InsertCellPoint(getPointIndex(y + 1, x))
            strip.InsertCellPoint(getPointIndex(y, x))
    map.SetStrips(strip)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(map)

    return mapper

def load_texture():
    image_reader = vtk.vtkJPEGReader()
    image_reader.SetFileName(PATH_IMG) # import the texture image

    texture = vtk.vtkTexture()
    texture.SetInputConnection(image_reader.GetOutputPort()) # sets the image for the texture
    texture.InterpolateOff()
    texture.RepeatOff()
    return texture


if __name__ == '__main__':
    actor = vtk.vtkActor()
    actor.SetMapper(load_map())
    actor.SetTexture(load_texture())

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.AddActor(load_plane( 22000. / 553, 16700. / 193)) # adds the plane actor
    renderer.SetBackground(0.1, 0.2, 0.4)

    # Creating a window to display the viewports
    renWin = vtk.vtkRenderWindow()
    renWin.SetSize(900, 800)
    renWin.Render()
    renWin.AddRenderer(renderer)

    # start the interaction window and add TrackBall Style
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.SetRenderWindow(renWin)
    iren.Start()

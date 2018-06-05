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

MIN_ELEVATION_LAT = 60
MIN_ELEVATION_LON = 10
COVERED_LAT_LON = 5
GRID_WIDTH = 6000
DELTA_LAT_LON = COVERED_LAT_LON / GRID_WIDTH

#RATIO_DEG_METERS = 6000 / 5. # meter/degrees ratio (6000 points for 5 degrees)

def rt90_to_gps(x, y):
    lon, lat =  pyproj.transform(RT90_PROJECTION, GPS_PROJECTION, x, y)
    return (lat, lon)

# Defining constants relating to the map
RADIUS = 6371009 # Earth radius

def gps_to_world(lat, lon, alt = 0):
    """
        Method used to convert the lat-lon-z(altitude without earth radius) values from the matrix to x-y-z world coordinates
    """
    t = vtk.vtkTransform()
    t.PostMultiply()

    # Rotating the point from latitude and longitude
    t.RotateY(lat)
    t.RotateZ(lon)

    # Describing the point and setting it on the x axe, at the right altitude.
    p_in = [RADIUS + alt, 0, 0]
    p_out = [0, 0, 0]
    t.TransformPoint(p_in, p_out)

    return p_out

def rt90_to_world(x, y, alt = 0):
    # We could have used RT90_PROJECTION(x, y), which give directly x, y, z world coordinates
    lat, lon = rt90_to_gps(x, y)
    # print("{},{}".format(lat, lon))
    p = gps_to_world(lat, lon, alt) 
    # print(p)
    return p

TOP_LEFT_COORDINATES = rt90_to_gps(1349340, 7022573)
TOP_RIGHT_COORDINATES = rt90_to_gps(1371573, 7022967)
BOTTOM_RIGHT_COORDINATES = rt90_to_gps(1371835, 7006362)
BOTTOM_LEFT_COORDINATES = rt90_to_gps(1349602, 7005969)

print("{},{},{},{}".format(TOP_LEFT_COORDINATES, TOP_RIGHT_COORDINATES, BOTTOM_LEFT_COORDINATES, BOTTOM_RIGHT_COORDINATES))

def load_plane():
    file = open(PATH_PLANE_GPS, 'r')
    nbLines = int(file.readline())
    coords = []

    # Reading the plane file line by line (position by position)
    for line in range(0, nbLines):
        # parsing plane position data
        (_, x, y, z, date, time, _, _, _, _) = file.readline().split()
        x = int(x)
        y = int(y)
        z = float(z)
        #print("{},{}".format(x, y))
        
        date = datetime.strptime(date + ' ' + time, '%y/%d/%m %H:%M:%S')
        ##x, y = convert_to_world(x, y)
        coords.append((x, y, z, date))

    points = vtk.vtkPoints()
    scalars = vtk.vtkFloatArray()
    line = vtk.vtkPolyLine()
    cells = vtk.vtkCellArray()
    polydata = vtk.vtkPolyData()

    line.GetPointIds().SetNumberOfIds(len(coords))

    prev_height = 512.5 # min height of the map

    # Tracking the max gradients of the plane to have a nice color range for the lookup table
    min_scalar, max_scalar = 0, 0

    for i, (x, y, z, _) in enumerate(coords): 
        plane_coords = rt90_to_world(x, y, z)
        #plane_coords = ((x - TOP_LEFT_COORDINATES[0]) * RATIO_DEG_METERS * width_meters, (y - TOP_RIGHT_COORDINATES[1]) * RATIO_DEG_METERS * height_meters, z)
        points.InsertNextPoint(plane_coords)
        line.GetPointIds().SetId(i, i)

        # positive or negative value, when the plane go up, respectively go down
        delta_height = prev_height - z

        scalars.InsertNextValue(delta_height)

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
    mapper.SetScalarRange(min_scalar / 2, max_scalar / 3)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    mapper.Update()

    return actor

def load_map():
    # Load the map
    map_values = np.fromfile(PATH_MAP, dtype=np.int16).reshape(GRID_WIDTH, GRID_WIDTH)

    # Select only the desired area  TO DO CHECK THIS PART !!!
    north_bound = max(TOP_LEFT_COORDINATES[0], TOP_RIGHT_COORDINATES[0])
    south_bound = min(BOTTOM_RIGHT_COORDINATES[0], BOTTOM_LEFT_COORDINATES[0])
    west_bound = min(TOP_LEFT_COORDINATES[1], BOTTOM_LEFT_COORDINATES[1])
    east_bound = max(TOP_RIGHT_COORDINATES[1], BOTTOM_RIGHT_COORDINATES[1])

    # POURQUOI CA CA MARCHE TODOOOOO +90"(73928719782301987209837)
    north_index = int(math.floor((MIN_ELEVATION_LAT + COVERED_LAT_LON - south_bound) / DELTA_LAT_LON))
    south_index = int(math.floor((MIN_ELEVATION_LAT + COVERED_LAT_LON - north_bound) / DELTA_LAT_LON))
    west_index = int(math.floor((west_bound - MIN_ELEVATION_LON) / DELTA_LAT_LON))
    east_index = int(math.floor((east_bound - MIN_ELEVATION_LON) / DELTA_LAT_LON))

    x_size = east_index - west_index + 1
    y_size = north_index - south_index + 1

    print("{}, {}, {}, {}".format(north_bound, south_bound, west_bound, east_bound))
    print("{}, {}, {}, {}".format(north_index, south_index, west_index, east_index))
 
    map_values = map_values[south_index:north_index + 1, west_index:east_index + 1]
   # map_values = map_values[north_index:south_index + 1, west_index:east_index + 1]
    
    # Defining geometry
    points = vtk.vtkPoints()

    # Array mapping the point to a texture coordinate
    # Each texture point is a tuple
    texture_coords = vtk.vtkFloatArray()
    texture_coords.SetNumberOfComponents(2)

    # exploring the values
    for i, row in enumerate(map_values):
        for j, alt in enumerate(row):
            lat = south_bound + i * DELTA_LAT_LON
            lon = west_bound + j * DELTA_LAT_LON

            #print("{},{}".format(lat, lon))
            # converting to world coordinates
            x, y, z = gps_to_world(lat, lon, alt)
            #print("{},{},{}".format(x, y, z))
            # Adding the point
            points.InsertNextPoint(x, y, z)

            # Adding the texture coordinates
            texture_coords.InsertNextTuple(((j / x_size), 1 - (i / y_size)))


    # creating a dataset
    # vtkStructuredGrid has an implicit topology and take less memory than a polydata
    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(x_size, y_size, 1)
    grid.SetPoints(points)
    grid.GetPointData().SetTCoords(texture_coords)

    # Create a mapper and actor
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(grid)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Creating the texture
    texture = load_texture()
    actor.SetTexture(texture)

    return actor

    
    '''
    

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
    '''

def load_texture():
    image_reader = vtk.vtkJPEGReader()
    image_reader.SetFileName(PATH_IMG) # import the texture image

    texture = vtk.vtkTexture()
    texture.SetInputConnection(image_reader.GetOutputPort()) # sets the image for the texture
    texture.InterpolateOff()
    texture.RepeatOff()
    return texture


if __name__ == '__main__':
    '''
    actor = vtk.vtkActor()
    actor.SetMapper(load_map())
    actor.SetTexture(load_texture())
    '''
    '''
    points = vtk.vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(0, 1, 0)
    points.InsertNextPoint(1, 0, 0)
    points.InsertNextPoint(1, 1, 0)


    mapping_array = vtk.vtkFloatArray()
    mapping_array.SetNumberOfComponents(2)
    mapping_array.InsertNextTuple((0, 0))
    mapping_array.InsertNextTuple((0, 1))
    mapping_array.InsertNextTuple((1, 0))
    mapping_array.InsertNextTuple((1, 1))

    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(2, 2, 1)
    grid.SetPoints(points)
    grid.GetPointData().SetTCoords(mapping_array)

    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(grid)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.SetTexture(load_texture())
        

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    '''
    map_actor = load_map()
    plane_actor = load_plane()
    
    renderer = vtk.vtkRenderer()
    renderer.AddActor(map_actor)
    renderer.AddActor(plane_actor) # adds the plane actor
    renderer.SetBackground(0.1, 0.2, 0.4)

    # Moving the camera
    camera = vtk.vtkCamera()
    distance = 50000 # the camera will be at ~50000m above the surface
    center_lat = BOTTOM_LEFT_COORDINATES[0] + (TOP_RIGHT_COORDINATES[0] - BOTTOM_LEFT_COORDINATES[0]) / 2
    center_lon = BOTTOM_LEFT_COORDINATES[1] + (TOP_RIGHT_COORDINATES[1] - BOTTOM_LEFT_COORDINATES[1]) / 2
    center = gps_to_world(center_lat, center_lon)
    center_high = gps_to_world(center_lat, center_lon, distance)
    camera.SetPosition(center_high)
    camera.SetFocalPoint(center) # looking at the center of the map
    camera.SetRoll(282)
    camera.SetClippingRange(1, 100000000)
    renderer.SetActiveCamera(camera)

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

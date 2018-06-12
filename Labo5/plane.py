#############################################
# HEIG-VD - VTK - Labo 5
# Plane Mapper
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

# Defining constants relating to the map
MIN_LAT = 60
MIN_LON = 10
COVERED_DEG = 5
MAX_LAT = MIN_LAT + COVERED_DEG
MAX_LON = MIN_LON + COVERED_DEG
GRID_WIDTH = 6000
DELTA_DEG = COVERED_DEG / GRID_WIDTH
EARTH_RADIUS = 6371009



# Coordinates handler functions
def rt90_to_gps(x, y):
    lon, lat =  pyproj.transform(RT90_PROJECTION, GPS_PROJECTION, x, y)
    return (lat, lon)

def gps_to_world(lat, lon, alt = 0):
    """
        Method used to convert the lat-lon-z(altitude without earth radius) values from the matrix to x-y-z world coordinates
    """
    t = vtk.vtkTransform()
    t.PostMultiply()

    # Rotating the point from latitude and longitude
    t.RotateY(lat)
    t.RotateZ(-lon)

    # Describing the point and setting it on the x axe, at the right altitude.
    p_in = [EARTH_RADIUS + alt, 0, 0]
    p_out = [0, 0, 0]
    t.TransformPoint(p_in, p_out)

    return p_out

def rt90_to_world(x, y, alt = 0):
    lat, lon = rt90_to_gps(x, y)
    p = gps_to_world(lat, lon, alt) 
    return p

TOP_LEFT_COORDINATES = rt90_to_gps(1349340, 7022573)
TOP_RIGHT_COORDINATES = rt90_to_gps(1371573, 7022967)
BOTTOM_RIGHT_COORDINATES = rt90_to_gps(1371835, 7006362)
BOTTOM_LEFT_COORDINATES = rt90_to_gps(1349602, 7005969)


def load_plane():
    file = open(PATH_PLANE_GPS, 'r')
    coords = []

    # Reading the plane file line by line (position by position)
    for line in range(0, int(file.readline())):
        # parsing plane position data
        values = file.readline().split()
        x = int(values[1])
        y = int(values[2])
        z = float(values[3])
        
        coords.append((x, y, z))

    points = vtk.vtkPoints()
    gradients = vtk.vtkFloatArray()
    lines = vtk.vtkPolyLine()
    lines.GetPointIds().SetNumberOfIds(len(coords))

    last_alt = coords[0][2] # Take the starting altitude

    # Tracking the max gradients of the plane to have a nice color range for the lookup table
    min_gradient, max_gradient = 0, 0

    for i, (x, y, alt) in enumerate(coords): 
        plane_coords = rt90_to_world(x, y, alt)
        points.InsertNextPoint(plane_coords)
        lines.GetPointIds().SetId(i, i)

        # positive or negative value, when the plane go up, respectively go down
        delta_alt = last_alt - alt
        gradients.InsertNextValue(delta_alt)

        min_gradient = last_alt-alt if (min_gradient > last_alt-alt) else min_gradient
        max_gradient = last_alt-alt if (max_gradient < last_alt-alt) else max_gradient
        last_alt = alt

    # Create a cell array to store the lines in and add the lines to it
    cells = vtk.vtkCellArray()
    cells.InsertNextCell(lines)

    # Create the associated polydata
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetLines(cells)
    polydata.GetPointData().SetScalars(gradients)

    # Create the trajectory tube
    tube = vtk.vtkTubeFilter()
    tube.SetRadius(25)
    tube.SetNumberOfSides(45)
    tube.SetInputData(polydata)

    # Finally create the mapper and add it ton an actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(tube.GetOutputPort())
    mapper.SetScalarRange(min_gradient/4, max_gradient/4)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.PickableOff()

    return actor

# Initiate the constantes for the interpolation
px = [BOTTOM_LEFT_COORDINATES[1], BOTTOM_RIGHT_COORDINATES[1], TOP_RIGHT_COORDINATES[1], TOP_LEFT_COORDINATES[1]]
py = [BOTTOM_LEFT_COORDINATES[0], BOTTOM_RIGHT_COORDINATES[0], TOP_RIGHT_COORDINATES[0], TOP_LEFT_COORDINATES[0]]

coeff = np.array([
    [1, 0, 0, 0],
    [1, 1, 0, 0], 
    [1, 1, 1, 1],
    [1, 0, 1, 0]
])
coeff_inv = np.linalg.inv(coeff)
a = np.dot(coeff_inv,px)
b = np.dot(coeff_inv,py)

# Interpolation of the texture, formula from : https://www.particleincell.com/2012/quad-interpolation/
def find_texture_coordinates(lat, lon):
    #quadratic equation coeffs, aa*mm^2+bb*m+cc=0
    aa = a[3]*b[2] - a[2]*b[3];
    bb = a[3]*b[0] -a[0]*b[3] + a[1]*b[2] - a[2]*b[1] + lon*b[3] - lat*a[3];
    cc = a[1]*b[0] -a[0]*b[1] + lon*b[1] - lat*a[1];
 
    #compute m = (-b+sqrt(b^2-4ac))/(2a)
    det = math.sqrt(bb*bb - 4*aa*cc);
    m = (-bb+det)/(2*aa);
 
    #compute l
    l = (lon-a[0]-a[2]*m)/(a[1]+a[3]*m);

    return l, m

def load_map():
    # Load the map
    map_values = np.fromfile(PATH_MAP, dtype=np.int16).reshape(GRID_WIDTH, GRID_WIDTH)

    # Select only the desired area
    north_bound = min(TOP_LEFT_COORDINATES[0], TOP_RIGHT_COORDINATES[0])
    south_bound = max(BOTTOM_RIGHT_COORDINATES[0], BOTTOM_LEFT_COORDINATES[0])
    west_bound = max(TOP_LEFT_COORDINATES[1], BOTTOM_LEFT_COORDINATES[1])
    east_bound = min(TOP_RIGHT_COORDINATES[1], BOTTOM_RIGHT_COORDINATES[1])

    north_index = int(math.floor((MAX_LAT - north_bound) / DELTA_DEG))
    south_index = int(math.floor((MAX_LAT - south_bound) / DELTA_DEG))
    west_index = int(math.floor((west_bound - MIN_LON) / DELTA_DEG))
    east_index = int(math.floor((east_bound - MIN_LON) / DELTA_DEG))

    map_values = map_values[north_index:south_index + 1, west_index:east_index + 1]
    
    # Defining geometry
    points = vtk.vtkPoints()

    # Array mapping the point to a texture coordinate
    # Each texture point is a tuple
    texture_coords = vtk.vtkFloatArray()
    texture_coords.SetNumberOfComponents(2)

    # Setting the altitude of the current point as a point scalar
    altitude_values = vtk.vtkIntArray()
    #altitudeValues.SetNumberOfValues(xSize * ySize)


    # exploring the values
    for i, row in enumerate(map_values):
        for j, alt in enumerate(row):
            lat = north_bound - i * DELTA_DEG
            lon = west_bound + j * DELTA_DEG

            # converting to world coordinates
            x, y, z = gps_to_world(lat, lon, alt)

            # Adding the point
            points.InsertNextPoint(x, y, z)

            # Adding the texture coordinates
            tcoords = find_texture_coordinates(lat, lon)
            texture_coords.InsertNextTuple((tcoords[0], tcoords[1]))
            
            # Setting the altitude of the current point as a point scalar
            altitude_values.InsertNextValue(alt)


    # creating a dataset
    # vtkStructuredGrid has an implicit topology and take less memory than a polydata
    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(east_index - west_index + 1, south_index - north_index + 1, 1)
    grid.SetPoints(points)
    grid.GetPointData().SetTCoords(texture_coords)
    grid.GetPointData().SetScalars(altitude_values)

    # Create a mapper and actor
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(grid)
    mapper.ScalarVisibilityOff()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Creating the texture
    texture = load_texture()
    actor.SetTexture(texture)

    return actor


# Load the image texture
def load_texture():
    image_reader = vtk.vtkJPEGReader()
    image_reader.SetFileName(PATH_IMG)
    texture = vtk.vtkTexture()
    texture.SetInputConnection(image_reader.GetOutputPort())
    return texture

def load_altitude_actor():
    text_actor = vtk.vtkCaptionActor2D()
    text_actor.SetCaption("")

    # Formatting
    text_actor.GetCaptionTextProperty().SetColor( 1.0, 1.0, 1.0 )
    text_actor.GetCaptionTextProperty().SetOpacity(0.9)
    text_actor.ThreeDimensionalLeaderOn()
    

    return text_actor




# Interactor
class CustomInteractor(vtk.vtkInteractorStyleMultiTouchCamera):

    def __init__(self, map_actor, text_actor, parent=None):        
        self.AddObserver("MouseMoveEvent", self.mouseMoveEvent)
        self.map_actor = map_actor
        self.text_actor = text_actor
        self.level_cutter = None
    
    def _set_level_actor(self, altitude):
        sphere = vtk.vtkSphere()
        sphere.SetCenter(0, 0, 0)
        sphere.SetRadius(altitude + EARTH_RADIUS)

        # updating the cutter
        self.level_cutter.SetCutFunction(sphere)

    def _load_level_actor(self, map_dataset):
        '''
        sphere = vtk.vtkSphere()
        sphere.SetCenter(0, 0, 0)
        sphere.SetRadius(altitude + EARTH_RADIUS)
        '''

        # creating the cutter
        self.level_cutter = vtk.vtkCutter()
        #cutter.SetCutFunction(sphere)
        self.level_cutter.SetInputData(map_dataset)

        # making it as a tube
        # using a stripper makes the tube smoother
        stripper = vtk.vtkStripper()
        stripper.SetInputConnection(self.level_cutter.GetOutputPort())
        tubeFilter = vtk.vtkTubeFilter()
        tubeFilter.SetRadius(40)
        tubeFilter.SetInputConnection(stripper.GetOutputPort())

        # creates the mapper and the actor
        mapper = vtk.vtkDataSetMapper()
        mapper.ScalarVisibilityOff()
        mapper.SetInputConnection(tubeFilter.GetOutputPort())
        level_actor = vtk.vtkActor()
        level_actor.SetMapper(mapper)
        level_actor.GetProperty().SetColor(0, 0.633, 0.91)
        self.GetDefaultRenderer().AddActor(level_actor)
        

    def mouseMoveEvent(self, obj, event):
        # picking the actor
        clickPos = self.GetInteractor().GetEventPosition()
        picker = vtk.vtkPointPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        actor_picked = picker.GetActor()
    
        if actor_picked != self.map_actor: # the map has not been picked, we do nothing
            self.OnMouseMove()
            return

        # updating the altitude text
        altitude = picker.GetDataSet().GetPointData().GetScalars().GetValue(picker.GetPointId())
        self.text_actor.SetCaption(str(altitude) + "m")
        self.text_actor.SetAttachmentPoint(picker.GetDataSet().GetPoints().GetPoint(picker.GetPointId()))
        self.GetInteractor().Render()

        # generating level line
        if(self.level_cutter == None):
            self._load_level_actor(picker.GetDataSet())  
            
        self._set_level_actor(altitude)

        self.OnMouseMove()
        return

        
        

if __name__ == '__main__':
    renderer = vtk.vtkRenderer()

    map_actor = load_map()
    renderer.AddActor(map_actor)

    plane_actor = load_plane()
    renderer.AddActor(plane_actor) 

    alt_actor = load_altitude_actor()
    renderer.AddActor(alt_actor)

    renderer.SetBackground(0.2, 0.2, 0.4)

    # Moving the camera
    camera = vtk.vtkCamera()
    distance = 50000 # the camera will be at ~50000m above the surface
    center_lat = BOTTOM_LEFT_COORDINATES[0] + (TOP_RIGHT_COORDINATES[0] - BOTTOM_LEFT_COORDINATES[0]) / 2
    center_lon = BOTTOM_LEFT_COORDINATES[1] + (TOP_RIGHT_COORDINATES[1] - BOTTOM_LEFT_COORDINATES[1]) / 2
    center = gps_to_world(center_lat, center_lon)
    center_high = gps_to_world(center_lat, center_lon, distance)
    camera.SetPosition(center_high)
    camera.SetFocalPoint(center) # looking at the center of the map
    camera.SetRoll(78.7)
    camera.SetClippingRange(1, 100000000)
    renderer.SetActiveCamera(camera)

    # Creating a window to display the viewports
    renWin = vtk.vtkRenderWindow()
    renWin.SetSize(900, 800)
    renWin.Render()
    renWin.AddRenderer(renderer)

    # start the interaction window and add TrackBall Style
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    iren.Initialize()
    style = CustomInteractor(map_actor, alt_actor)
    style.SetDefaultRenderer(renderer)
    iren.SetInteractorStyle(style)
    iren.Start()

#############################################
## HEIG-VD - VTK - Labo Cube
## Cube - The Movie
## Rémi Jacquemard
## 28.03.18
#############################################

# Imports
import vtk
import random
import math
import time

# True if we want to output the video file, False otherwise
MAKE_MOVIE = False

# We here load a unique solution from the file
# Adapted from Cube.py
def loadSolution(filename):
    solutions = []

    shapesFile = open(filename, mode='r')
    endFace = False
    currentFace = []
    currentCube = []
    for line in shapesFile:
        if line == '\n':
            if endFace: #end of a solution
                solutions.append(currentCube)
                currentCube = []
                endFace = False
                break
            else: # end of a face
                currentCube.append(currentFace)
                currentFace = []
                endFace = True

        else:
            endFace = False
            values = line.split()
            currentLine = []
            for value in values:
                currentLine.append(int(value))
            currentFace.append(currentLine)


    shapesFile.close()
    return solutions


def CreateVTKFragment():
    fragment = vtk.vtkCubeSource()
    fragment.SetXLength(1.0)
    fragment.SetYLength(1.0)
    fragment.SetZLength(1.0)
    return fragment

def CreateVTKShape(fragments):
    cubes = []

    appendFilter = vtk.vtkAppendPolyData()

    # Creating cubes and appending the Polydata
    for x, y, z in fragments:
        fragment = CreateVTKFragment()
        # the full cube is from (0, 0, 0) to (i, i, i)
        fragment.SetCenter(x + 0.5, y + 0.5, z + 0.5)
        fragment.Update()
        cubes.append(fragment)
        # Appending the cubes
        appendFilter.AddInputData(fragment.GetOutput())

    appendFilter.Update()

    return appendFilter


def CreateShapeActor(fragments):
    poly = CreateVTKShape(fragments)

    # We send it to the mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(poly.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor


def GetShapeActors(cube):
    # Getting fragments position 
    shapes = {}
    for x, l1 in enumerate(cube):
        for y, l2 in enumerate(l1):
            for z, shapeIndex in enumerate(l2):
                if(shapeIndex not in shapes):
                    shapes[shapeIndex] = {
                        'fragments': [],
                        'yMean': 0,
                        'ySum' : 0
                    }
                shapes[shapeIndex]['fragments'].append([x, y, z])
                shapes[shapeIndex]['ySum'] += y
                shapes[shapeIndex]['yMean'] = shapes[shapeIndex]['ySum'] / len(shapes[shapeIndex]['fragments'])

    # Ordering the shape to make them falling
    orderedShapes = sorted(shapes.values(), key=lambda shape:shape['yMean'])

    # Creating each shape
    actors = []
    for shape in orderedShapes:
        # Creating the actor
        a = CreateShapeActor(shape['fragments'])
        a.GetProperty().SetColor(random.random(), random.random(), random.random())
        actors.append(a)

    return actors

# Loading the shapes from the file
solutions = loadSolution("solutions.txt")
shapeModel = solutions[0] # making a video for the 1st solutions

# Creating the actors shapes
actors = GetShapeActors(shapeModel)

# Moving the actors out of the field of View
trans = vtk.vtkTransform()
trans.Translate(0, 10, 0)

for actor in actors:
    actor.SetUserTransform(trans)

# Creating a renderer 
ren = vtk.vtkRenderer()
ren.SetBackground(1, 1, 1) # White background

# Adding the actors
for actor in actors:
    ren.AddActor(actor)

# Finally we create the render window
renWin = vtk.vtkRenderWindow()

# Adding the renderer to the window

camera = vtk.vtkCamera()
camera.ParallelProjectionOn()
camera.SetParallelScale(3.5)
camera.SetPosition(7, 5, 7)
center = len(shapeModel) / 2
camera.SetFocalPoint(center, center, center)
#modifying the light to have some shadow with ParallelProjection
lightKit = vtk.vtkLightKit()
lightKit.MaintainLuminanceOn()
lightKit.AddLightsToRenderer(ren)
renWin.AddRenderer(ren)

ren.SetActiveCamera(camera)
renWin.AddRenderer(ren)

renWin.SetSize(800, 600)

# used for interaction
'''
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

iren.Initialize()
renWin.Render()
iren.Start()
'''

#
# Now we make the shapes falling
#
fps = 33
transitionTime = 2

def pos(t):
    if t > transitionTime:
        t = transitionTime
    # making them falling slower and slower
    return 1/2 * 10 * (transitionTime - t) * (transitionTime - t)

actorsToMove = actors

# creating an image filter to make a video
if MAKE_MOVIE:
    imageFilter = vtk.vtkWindowToImageFilter()
    imageFilter.SetInput(renWin)
    imageFilter.SetInputBufferTypeToRGB()
    # imageFilter.ReadFrontBufferOff()
    imageFilter.Update()

    # starting record
    writer = None
    writer = vtk.vtkOggTheoraWriter()
    writer.SetInputConnection(imageFilter.GetOutputPort())
    writer.SetFileName("Cube - The Movie.ogv")
    writer.Start()


for actor in actorsToMove:
    for i in range(transitionTime * fps):
        time.sleep(1/fps)
        renWin.Render()

        #Export a single frame into the video
        if MAKE_MOVIE:
            imageFilter.Modified()
            writer.Write()

        t = i / fps
        trans = vtk.vtkTransform()
        trans.Translate(0, pos(t), 0)

        actor.SetUserTransform(trans)
        camera.Elevation(0.04)
        camera.SetParallelScale(camera.GetParallelScale() + 0.001)


# writing the video
if MAKE_MOVIE:
    writer.End()

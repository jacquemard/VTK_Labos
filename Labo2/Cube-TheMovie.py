# First we import the VTK Python package that will make available all
# of the VTK commands to Python.
import vtk
import random
import math
import time

shapeModel = [
    [[3, 2, 2],
     [2, 2, 5],
     [5, 5, 5]],

    [[3, 0, 4],
     [3, 0, 4],
     [3, 1, 4]],
     
    [[6, 0, 4],
     [6, 6, 6],
     [1, 1, 1]]
]

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
            for z, val in enumerate(l2):
                if(val not in shapes):
                    shapes[val] = {
                        'fragments': [],
                        'yMean': 0,
                        'ySum' : 0
                    }
                shapes[val]['fragments'].append([x, y, z])
                shapes[val]['ySum'] += y
                shapes[val]['yMean'] = shapes[val]['ySum'] / len(shapes[val]['fragments'])


    # Ordering the shape to make them falling
    orderedShapes = sorted(shapes.values(), key=lambda shape:shape['yMean'])

    # Creating each shape
    actors = []
    for key, shape in shapes.items():
        # Creating the actor
        a = CreateShapeActor(shape['fragments'])
        a.GetProperty().SetColor(random.random(), random.random(), random.random())
        actors.append(a)

    return actors

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
camera.SetPosition(7, 6, 7)
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


'''
# Create the Renderer and assign actors to it. 
ren = vtk.vtkRenderer()
for actor in actors:
    ren.AddActor(actor)

ren.SetBackground(1, 1, 1)
'''

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

    return 1/2 * 9.81 * (transitionTime - t) * (transitionTime - t)

actorsToMove = actors

for actor in actorsToMove:
    for i in range(transitionTime * fps):
        time.sleep(1/fps)
        renWin.Render()

        t = i / fps
        trans = vtk.vtkTransform()
        trans.Translate(0, pos(t), 0)

        actor.SetUserTransform(trans)
        camera.Elevation(-0.03)
        camera.SetParallelScale(camera.GetParallelScale() - 0.001)

        

'''
# showing the shapes one by one
trans = vtk.vtkTransform()
trans.Translate(0, 0, 0)
for actor in actors:
    actor.SetUserTransform(trans)

# renWin.Render()
'''
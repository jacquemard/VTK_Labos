# First we import the VTK Python package that will make available all
# of the VTK commands to Python.
import vtk
import random

def CreateVTKFragment():
    fragment = vtk.vtkCubeSource()
    fragment.SetXLength(1.0)
    fragment.SetYLength(1.0)
    fragment.SetZLength(1.0)
    return fragment

shapePieces = [
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


def CreateVTKShape(fragments):
    cubes = []

    appendFilter = vtk.vtkAppendPolyData()

    # Creating cubes and appending the Polydata
    for x, y, z in fragments:
        fragment = CreateVTKFragment()
        fragment.SetCenter(x, y, z)
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
                    shapes[val] = []
                shapes[val].append([x, y, z])

    # Creating each shape
    actors = []
    for key, fragments in shapes.iteritems():
        # Creating the actor
        a = CreateShapeActor(fragments)
        a.GetProperty().SetColor(random.random(), random.random(), random.random())
        actors.append(a)

    return actors


# Create a piece within a 3x3 cube
tPiece = [
    [[True, True, True],
     [False, True, False],
     [False, False, False]],

    [[False, False, False],
     [False, False, False],
     [False, False, False]],
     
    [[False, False, False],
     [False, False, False],
     [False, False, False]]
]

def GetFragments(pieceModel):
    fragments = []
    for x, l1 in enumerate(pieceModel):
        for y, l2 in enumerate(l1):
            for z, val in enumerate(l2):
                if(val):
                    fragments.append([x, y, z])
    return fragments


'''
# Create an actor to represent the piece. 
shapeActor = CreateShapeActor(tPiece)

shapeActor.GetProperty().SetColor(0.5, 0.7, 0)
'''

# Creating the actors
actors = GetShapeActors(shapePieces)

# Create the Renderer and assign actors to it. 
ren1 = vtk.vtkRenderer()
for actor in actors:
    ren1.AddActor(actor)

ren1.SetBackground(0.1, 0.2, 0.4)

# Finally we create the render window which will show up on the screen
# We put our renderer into the render window using AddRenderer. We
# also set the size to be 300 pixels by 300.
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren1)
renWin.SetSize(300, 300)

# used for interaction
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

iren.Initialize()
renWin.Render()
iren.Start()
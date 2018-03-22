# First we import the VTK Python package that will make available all
# of the VTK commands to Python.
import vtk
import random
import math

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
                    shapes[val] = []
                shapes[val].append([x, y, z])

    # Creating each shape
    actors = []
    for key, fragments in shapes.items():
        # Creating the actor
        a = CreateShapeActor(fragments)
        a.GetProperty().SetColor(random.random(), random.random(), random.random())
        actors.append(a)

    return actors


# Creating the actors shapes
actors = GetShapeActors(shapeModel)

# Creating a renderer for each step
renderers = []

for i in range(len(actors)):
    ren = vtk.vtkRenderer()
    ren.SetBackground(1, 1, 1) # White background
    renderers.append(ren)

    # Adding i actors
    for j in range(i + 1):
        # print(i)
        ren.AddActor(actors[j])



# Finally we create the render window which will show up on the screen
# We put our renderer into the render window using AddRenderer. We
# also set the size to be 800 pixels by 600.
renWin = vtk.vtkRenderWindow()

# ---- Creating a viewport for every renderer

# Number of column to display
col = 2
row = math.ceil(len(actors)/col)
colSize = 1 / col
rowSize = 1 / row 

# Steps
for index in range(len(renderers)):
    i = index % col
    j = math.floor(index/col)

    ren = renderers[index]
    
    if index == len(renderers) - 1 :# last shape
        ren.SetViewport(i * colSize, 1 - rowSize - j * rowSize, 1, rowSize)  
    else: 
        ren.SetViewport(i * colSize, 1 - rowSize - j * rowSize, (i + 1) * colSize, 1 - j * rowSize)        

# Adding the renderer to the window and setting the same camera for everybody

camera = vtk.vtkCamera()
camera.ParallelProjectionOn()
camera.SetParallelScale(3)
camera.SetPosition(7, 6, 7)
center = len(shapeModel) / 2
camera.SetFocalPoint(center, center, center)
for ren in renderers:
    ren.SetActiveCamera(camera)
    #modifying the light to have some shadow with ParallelProjection
    lightKit = vtk.vtkLightKit()
    lightKit.MaintainLuminanceOn()
    lightKit.AddLightsToRenderer(ren)
    renWin.AddRenderer(ren)

renWin.SetSize(600, 800)

# output an image file
imageFilter = vtk.vtkWindowToImageFilter()
imageFilter.SetInput(renWin)
imageFilter.SetScale(3)
imageFilter.SetInputBufferTypeToRGBA()
imageFilter.Update()

writer = vtk.vtkPNGWriter()
writer.SetFileName("cubeSteps.png")
writer.SetInputConnection(imageFilter.GetOutputPort())
writer.Write()

# used for interaction
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

renWin.Render()
iren.Start()

# used for interaction
'''
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

iren.Initialize()
renWin.Render()
iren.Start()
'''
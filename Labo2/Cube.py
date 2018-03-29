#############################################
## HEIG-VD - VTK - Labo Cube
## Images de solutions
## Rémi Jacquemard
## 28.03.18
#############################################
import vtk
import random
import math
import os

# We here load the shapes from the file
# The solutions have been formated as it follows:
'''
5 5 1 
5 1 1 
5 6 1 

2 2 3 
0 0 3 
0 6 3 

4 2 2 
4 4 4 
6 6 3 


'''
# Where each shape is specified with a unique number. 
# Each face (front, middle, back) is seperated by a blank line
# Each solution is seperated by two blank line
# Having such a format is usefull to be generalizable. For example,
# a 3x5x2 cube is easily representable with this format. It is 
# possible to have different formats for each solution too.
# Note: The end of the file has to have 3 blank lines
def loadSolution(filename):
    solutions = []

    shapesFile = open(filename, mode='r')
    endFace = False
    currentFace = []
    currentCube = []
    for line in shapesFile:
        if line == '\n':
            if endFace: # end of a solution
                solutions.append(currentCube)
                currentCube = []
                endFace = False
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

def CreateCubeWireframeActor(fragments):
    xSize = len(fragments)
    ySize = len(fragments[0])
    zSize = len(fragments[0][0])

    #creating the source
    cubeSource = vtk.vtkCubeSource()
    cubeSource.SetBounds(0, xSize, 0, ySize, 0, zSize)

    # making an actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cubeSource.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # wireframing the actor
    actor.GetProperty().SetRepresentationToWireframe()

    return actor


# Loading the shapes from the file
solutions = loadSolution(r"C:\Users\Remi\OneDrive\HEIG\Cours\S6\VTK\VTK_Labos\Labo2\solutions.txt")

# Creating the render window
renWin = vtk.vtkRenderWindow()
renWin.SetSize(600, 800)

# Creating solutions folder if not exists
if not os.path.exists("solutions"):
    os.makedirs("solutions")

for shapeModelIndex, shapeModel in enumerate(solutions):

    # Creating the actors shapes
    actors = GetShapeActors(shapeModel)

    # Creating the cube wireframe
    wireframe = CreateCubeWireframeActor(shapeModel)

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
        
        # Adding the wireframe
        ren.AddActor(wireframe)

    # ---- Creating a viewport for each renderer
    # Number of column to display
    col = 2
    row = math.ceil(len(actors)/col)
    colSize = 1 / col
    rowSize = 1 / row 

    # Steps viewports
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
        #modifying the light to have some shadows with ParallelProjection
        lightKit = vtk.vtkLightKit()
        lightKit.MaintainLuminanceOn()
        lightKit.AddLightsToRenderer(ren)
        renWin.AddRenderer(ren)


    # output an image file
    renWin.Render()
    imageFilter = vtk.vtkWindowToImageFilter()
    imageFilter.SetInput(renWin)
    imageFilter.SetScale(3)
    imageFilter.SetInputBufferTypeToRGBA()
    imageFilter.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName("solutions/cubeSteps" + str(shapeModelIndex) + ".png")
    writer.SetInputConnection(imageFilter.GetOutputPort())
    
    writer.Write()

    # Cleaning
    for renderer in renderers:
        renWin.RemoveRenderer(renderer)
    

# rendering with interactif
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

renWin.Render()
iren.Start()

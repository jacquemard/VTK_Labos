#imports
import vtk

def createActor(filename):
    # importing file
    file = open(filename)
    xSize, ySize = [int(i) for i in file.readline().split()]

    print(xSize)
    print(ySize)

    # creating geometry
    points = vtk.vtkPoints()
    for x in range(xSize):
        for y in range(ySize):
            points.InsertNextPoint(x, y, 0)
    
    # creating dataset with implicit topology
    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(xSize, ySize, 1)
    grid.SetPoints(points)
    print(grid.GetNumberOfPoints())

    # mapping it to graphic primitives
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(grid)

    # creating an actor from it
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)



    return actor

actor = createActor("altitudes.txt")


# ---- RENDERING
ren = vtk.vtkRenderer()
ren.AddActor(actor)
ren.SetBackground(0.1, 0.2, 0.4)

renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetSize(800, 600)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

iren.Initialize()
iren.Start()

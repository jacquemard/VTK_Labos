#############################################
# HEIG-VD - VTK - Labo 4
# Scanner d'un genou
# Rémi Jacquemard & Francois Quellec
# Avril-Mai 2018
#############################################

import vtk
import math

def load_image_data():
    # Loading image data from file
    reader = vtk.vtkSLCReader()
    reader.SetFileName('vw_knee.slc')
    reader.Update()
    return reader


def define_viewports(renderers):
    # Number of column to display
    col = 2
    row = math.ceil(len(renderers)/col)
    colSize = 1 / col
    rowSize = 1 / row

    # Steps viewports
    for index in range(len(renderers)):
        i = index % col
        j = math.floor(index/col)

        ren = renderers[index]

        if index == len(renderers) - 1:  # last renderer
            ren.SetViewport(i * colSize, 1 - rowSize - j * rowSize, 1, rowSize)
        else:
            ren.SetViewport(i * colSize, 1 - rowSize - j *
                            rowSize, (i + 1) * colSize, 1 - j * rowSize)

def create_iso_dataset(input, iso_value):
    contour = vtk.vtkContourFilter()
    contour.SetInputConnection(input.GetOutputPort())
    contour.SetValue(0, iso_value)

    return contour

def create_iso_actor(input, iso_value):
    contour = create_iso_dataset(input, iso_value)
    return create_actor(contour)

def create_mapper(input):
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(skin.GetOutputPort())
    mapper.ScalarVisibilityOff()

    return mapper


def create_bone(image_data):
    return create_iso_dataset(image_data, 73)

def create_skin(image_data):
    return create_iso_dataset(image_data, 50)


def create_2(bone, skin):
    # creating the sphere clipping
    sphere = vtk.vtkSphere()
    sphere.SetRadius(60)
    sphere.SetCenter(0, 100, 100)

    # clipping
    clipper = vtk.vtkClipDataSet()
    clipper.SetClipFunction(sphere)
    clipper.SetInputConnection(skin.GetOutputPort())
    #clipper.SetValue(0)
    #clipper.Update()

    skin = clipper

    return (bone, skin)

def main():
    image_data = load_image_data()

    bone = create_bone(image_data)
    skin = create_skin(image_data) 

    val = create_2(bone, skin)
        
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(val[1].GetOutputPort())
    mapper.ScalarVisibilityOff()
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    print(image_data.GetOutput().GetDimensions())

    # ------------ RENDERING -------------

    # Creating a camera
    camera = vtk.vtkCamera()
    center = image_data.GetOutput().GetCenter()
    print(image_data.GetOutput().GetExtent())
    camera.SetPosition(center[0]/2, -450 , center[2]/2)    
    camera.SetFocalPoint(center)
    camera.Roll(-37)
    print(camera.GetRoll())

    # Creating renderers
    ren = vtk.vtkRenderer()
    ren.AddActor(actor)
    ren.SetBackground(1, 1, 1)
    ren.SetActiveCamera(camera)
    renderers = [ren]

    # Creating viewports
    viewports = define_viewports(renderers)

    # Creating a window to display the viewports
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetSize(900, 900)
    renWin.Render()

    # start the interaction window and add TrackBall Style
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.SetRenderWindow(renWin)
    iren.Start()

# -------------- MAIN --------------
if __name__ == '__main__':
    main()

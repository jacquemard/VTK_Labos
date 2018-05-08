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

'''
def create_mapper(input):
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(skin.GetOutputPort())
    mapper.ScalarVisibilityOff()

    return mapper
'''

def create_actor(input):
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(input.GetOutputPort())
    mapper.ScalarVisibilityOff()
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor

def create_bone(image_data):
    return create_iso_dataset(image_data, 73)

def create_skin(image_data):
    return create_iso_dataset(image_data, 50)


def create_renderer_2(bone, skin):
    # creating the sphere clipping
    sphere = vtk.vtkSphere()
    sphere.SetRadius(60)
    sphere.SetCenter(70, 30, 100)

    # clipping
    clipper = vtk.vtkClipDataSet()
    clipper.SetClipFunction(sphere)
    clipper.SetInputConnection(skin.GetOutputPort())
    skin = clipper

    # creating actors
    bone_actor = create_actor(bone)
    bone_actor.GetProperty().SetColor(0.94, 0.94, 0.94)

    # spliting the skin in 2 different actors for front face opacity
    frontface_actor = create_actor(skin)
    frontface_actor.GetProperty().SetColor(0.8, 0.62, 0.62)
    backface_actor = create_actor(skin)
    backface_actor.GetProperty().SetColor(0.8, 0.62, 0.62)
    backface_actor.GetProperty().FrontfaceCullingOn()
    # changing opacity of the front one
    frontface_actor.GetProperty().SetOpacity(0.6)

    # creating renderer
    ren = create_renderer([bone_actor, frontface_actor, backface_actor])
    ren.SetBackground(1, 1, 1)

    return ren

def create_renderer_3(bone, skin):
    # creating the sphere clipping
    radius = 60
    center = [70, 30, 100]
    sphere = vtk.vtkSphere()
    sphere.SetRadius(radius)
    sphere.SetCenter(center)

    # clipping
    clipper = vtk.vtkClipDataSet()
    clipper.SetClipFunction(sphere)
    clipper.SetInputConnection(skin.GetOutputPort())
    skin = clipper

    # creating actors
    bone_actor = create_actor(bone)
    bone_actor.GetProperty().SetColor(0.94, 0.94, 0.94)

    skin_actor = create_actor(skin)
    skin_actor.GetProperty().SetColor(0.8, 0.62, 0.62)

    # creating the sphere actor ----
    # sampling
    sample = vtk.vtkSampleFunction()
    sample.SetImplicitFunction(sphere)
    sample.SetSampleDimensions(50, 50, 50)
    sample.SetModelBounds(center[0]- radius, center[0] + radius, 
        center[1]- radius, center[1] + radius, center[2]- radius, center[2] + radius)
    # contouring
    sphere_actor = create_iso_actor(sample, 0)
    # design
    sphere_actor.GetProperty().SetColor(0.85, 0.8, 0.1)
    sphere_actor.GetProperty().SetOpacity(0.15)

    # creating renderer
    ren = create_renderer([bone_actor, skin_actor, sphere_actor])
    ren.SetBackground(1, 1, 1)

    return ren

'''
def create_actors(bone, skin):
    bone_actor = create_actor(bone)
    bone_actor.GetProperty().SetColor(0.94, 0.94, 0.94)

    skin_actor = create_actor(skin)
    skin_actor.GetProperty().SetColor(0.8, 0.62, 0.62)

    return (bone_actor, skin_actor)
'''

def create_renderer(actors):
    ren = vtk.vtkRenderer()

    for actor in actors:
        ren.AddActor(actor)

    return ren

def main():
    image_data = load_image_data()

    bone = create_bone(image_data)
    skin = create_skin(image_data) 

    #bone, skin = create_actors(bone, skin)     

    # bounding box
    outline = vtk.vtkOutlineFilter()
    outline.SetInputConnection(image_data.GetOutputPort())
    outline_actor = create_actor(outline) 
    outline_actor.GetProperty().SetColor(0, 0, 0)

    # ------------ RENDERING -------------

    # Creating a camera
    camera = vtk.vtkCamera()
    center = image_data.GetOutput().GetCenter() 
    camera.SetPosition(center[0] - 0.01, -450 , center[2])
    camera.SetFocalPoint(center)
    camera.Roll(-90)
    
    # Creating renderers
    renderers = [
        create_renderer_2(bone, skin),
        create_renderer_3(bone, skin)]
    for ren in renderers:
        ren.SetActiveCamera(camera)
        ren.AddActor(outline_actor)

    # Creating viewports
    viewports = define_viewports(renderers)

    # Creating a window to display the viewports
    renWin = vtk.vtkRenderWindow()
    renWin.SetSize(900, 800)
    renWin.Render()
    
    # Adding the renderers to the window
    for ren in renderers:
        renWin.AddRenderer(ren)

    # start the interaction window and add TrackBall Style
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.SetRenderWindow(renWin)
    iren.Start()

# -------------- MAIN --------------
if __name__ == '__main__':
    main()

#############################################
# HEIG-VD - VTK - Labo 4
# Scanner d'un genou
# Rémi Jacquemard & Francois Quellec
# Avril-Mai 2018
#############################################

import vtk
import math

# true if we want a low image resolution, false otherwise
low_res = False

# false if we want to open distance data from file, true if we want to write the file
write_file = True


def load_image_data():
    '''
    Used to load the knee image data. It is possible to choose if we want to downsample it with the write_file 
    boolean declared above
    '''

    # Loading image data from file
    reader = vtk.vtkSLCReader()
    reader.SetFileName('vw_knee.slc')
    reader.Update()

    spacing = reader.GetDataSpacing()

    # resampling if we want to
    if low_res:
        resample = vtk.vtkImageResample()
        resample.SetMagnificationFactors(0.2, 0.2, 0.2)
        resample.SetInputConnection(reader.GetOutputPort())
        resample.Update()
        reader = resample

    # return the space between each point too
    return (reader, spacing)


def define_viewports(renderers, ncol = 2):
    '''
    Set renderers viewports to spread them within the window
    renderers: the renderers to spread
    ncol: the number of col we want
    '''

    row = math.ceil(len(renderers)/ncol)
    colSize = 1 / ncol
    rowSize = 1 / row

    # Steps viewports
    for index in range(len(renderers)):
        i = index % ncol
        j = math.floor(index/ncol)

        ren = renderers[index]

        if index == len(renderers) - 1:  # last renderer
            ren.SetViewport(i * colSize, 1 - rowSize - j * rowSize, 1, rowSize)
        else:
            ren.SetViewport(i * colSize, 1 - rowSize - j *
                            rowSize, (i + 1) * colSize, 1 - j * rowSize)


def create_iso_dataset(input, iso_value):
    '''
    Used to create a dataset from the input using the iso_value passed as a parameter
    '''
    contour = vtk.vtkContourFilter()
    contour.SetInputConnection(input.GetOutputPort())
    contour.SetValue(0, iso_value)
    contour.Update()

    return contour


def create_iso_actor(input, iso_value):
    '''
    Used to create an actor from the input using the iso_value passed as a parameter
    '''
    contour = create_iso_dataset(input, iso_value)
    return create_actor(contour)


def create_actor(input):
    '''
    Return an newly created actor using a dataset as input
    '''
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(input.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor


def create_bone(image_data):
    '''
    create the bone from the image data
    '''
    return create_iso_dataset(image_data, 73)


def create_skin(image_data):
    '''
    create the skin from the image data
    '''
    return create_iso_dataset(image_data, 50)


# ----------------------------- RENDERERS --------------------------------
def create_renderer_1(bone, skin, spacing):
    '''
    Return the first renderer
    bone: the bone dataset
    skin: the skin dataset
    spacing: distances between points of the original data
    '''
    # creating actors
    bone_actor = create_actor(bone)
    bone_actor.GetProperty().SetColor(0.94, 0.94, 0.94)

    # creating the plane to cut the skin
    plane = vtk.vtkPlane()
    center = skin.GetOutput().GetCenter()
    # origin is set to the center
    plane.SetOrigin(center[0], center[1], center[2])
    plane.SetNormal(0, 0, 1)

    # creating the cutter
    cutter = vtk.vtkCutter()
    cutter.SetCutFunction(plane)
    size = skin.GetOutput().GetBounds()[5]
    # 19 tube, 1 centered, 9 for each side. 1 centimeter is 10 voxel height
    cutter.GenerateValues(19, -spacing[2] * 10 * 9, spacing[2] * 10 * 9)
    cutter.SetInputConnection(skin.GetOutputPort())

    # making it as a tube
    # using a stripper makes the tube smoother
    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(cutter.GetOutputPort())
    tubeFilter = vtk.vtkTubeFilter()
    tubeFilter.SetRadius(1)
    tubeFilter.SetInputConnection(stripper.GetOutputPort())

    cutter_actor = create_actor(tubeFilter)
    cutter_actor.GetProperty().SetColor(0.8, 0.62, 0.62)

    # creating renderer
    ren = create_renderer([bone_actor, cutter_actor])
    ren.SetBackground(1, 0.827, 0.824)

    return ren


def create_renderer_2(bone, skin):
    '''
    Return the second renderer
    bone: the bone dataset
    skin: the skin dataset
    '''
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
    ren.SetBackground(0.824, 1, 0.824)

    return ren

def create_renderer(actors):
    '''
    Return a new renderer where the actors (an array) passed as parameter are within
    bone: the bone dataset
    skin: the skin dataset
    '''
    ren = vtk.vtkRenderer()

    for actor in actors:
        ren.AddActor(actor)

    return ren

def create_renderer_3(bone, skin):
    '''
    Return the third renderer
    bone: the bone dataset
    skin: the skin dataset
    '''
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
    # sampling using the sphere implicit function
    sample = vtk.vtkSampleFunction()
    sample.SetImplicitFunction(sphere)
    sample.SetSampleDimensions(50, 50, 50)
    sample.SetModelBounds(center[0] - radius, center[0] + radius,
                          center[1] - radius, center[1] + radius, center[2] - radius, center[2] + radius)
    # contouring. The sphere is described by a 0 iso-value
    sphere_actor = create_iso_actor(sample, 0)
    # design
    sphere_actor.GetProperty().SetColor(0.85, 0.8, 0.1)
    sphere_actor.GetProperty().SetOpacity(0.15)

    # creating renderer
    ren = create_renderer([bone_actor, skin_actor, sphere_actor])
    ren.SetBackground(0.827, 0.824, 1)

    return ren


def create_renderer_4(bone, skin):
    '''
    Return the fourth renderer
    '''
    distanceFilter = None
    # writing to the file or open from file
    if write_file:
         # computing the distance between the bone and the skin
        distanceFilter = vtk.vtkDistancePolyDataFilter()
        distanceFilter.SetInputConnection(0, bone.GetOutputPort())
        distanceFilter.SetInputConnection(1, skin.GetOutputPort())
        distanceFilter.Update()

        # writing data
        writer = vtk.vtkPolyDataWriter()
        writer.SetInputConnection(distanceFilter.GetOutputPort())
        writer.SetFileName('bone_distances.vtk')
        writer.Update()
    else:
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName('bone_distances.vtk')
        reader.Update()

        distanceFilter = reader

    # creating bone actor
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(distanceFilter.GetOutputPort())
    mapper.SetScalarRange(
        distanceFilter.GetOutput().GetPointData().GetScalars().GetRange()[0],
        distanceFilter.GetOutput().GetPointData().GetScalars().GetRange()[1])
    # inversing colors
    table = mapper.GetLookupTable()
    table.SetHueRange(2/3, 0)
    table.Build()

    bone_actor = vtk.vtkActor()
    bone_actor.SetMapper(mapper)

    # creating renderer
    ren = create_renderer([bone_actor])
    ren.SetBackground(0.824, 0.827, 0.824)

    return ren


# -------------- MAIN --------------

def main():
    # loading image_data from file
    image_data, spacing = load_image_data()

    # creating the bone and the skin datasets
    bone = create_bone(image_data)
    skin = create_skin(image_data)

    # creating the bounding box
    outline = vtk.vtkOutlineFilter()
    outline.SetInputConnection(image_data.GetOutputPort())
    outline_actor = create_actor(outline)
    outline_actor.GetProperty().SetColor(0, 0, 0)

    # ------------ RENDERING -------------

    # Creating a camera 
    camera = vtk.vtkCamera()
    center = image_data.GetOutput().GetCenter()
    camera.SetPosition(center[0] - 0.01, -450, center[2])
    camera.SetFocalPoint(center)
    camera.Roll(-90)

    # Creating renderers
    renderers = [
        create_renderer_1(bone, skin, spacing),
        create_renderer_2(bone, skin),
        create_renderer_3(bone, skin),
        create_renderer_4(bone, skin)]
    for ren in renderers: # the same camera is used for every renderer
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


if __name__ == '__main__':
    main()

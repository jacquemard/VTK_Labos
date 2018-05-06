#############################################
# HEIG-VD - VTK - Labo 4
# Scanner d'un genou
# Rémi Jacquemard & Francois Quellec
# Avril-Mai 2018
#############################################

import vtk
import antigravity


def load_image_data():
    # Loading image data from file
    reader = vtk.vtkSLCReader()
    reader.SetFileName('vw_knee.slc')
    reader.Update()
    return reader

def main():
    image_data = load_image_data()

    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(image_data.GetOutput())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetRepresentationToWireframe()

    # ------------ RENDERING -------------
    # Creating a render
    ren = vtk.vtkRenderer()
    ren.AddActor(actor)
    ren.SetBackground(1, 1, 1)

    # Creating a window to display the render
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
import logging
import os
from typing import Annotated, Optional

import vtk

import slicer, qt
from slicer.i18n import tr as _
from slicer.i18n import translate
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
    WithinRange,
)

from slicer import vtkMRMLScalarVolumeNode

BIG_BRAIN = "Big_Brain"
IN_VIVO = "in_vivo"
EX_VIVO = "ex_vivo"

BIG_BRAIN_VOLUME_NAME = "vtkMRMLScalarVolumeNode3"
IN_VIVO_VOLUME_NAME = "vtkMRMLScalarVolumeNode1"
EX_VIVO_VOLUME_NAME = "vtkMRMLScalarVolumeNode2"

NUMBER_OF_QUESTIONS = 10
Q_MESSAGE_BOX_TITLE = "BV4 Example program"


#
# Example_Program
#


class Example_Program(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = _("Example_Program")  # TODO: make this more human readable by adding spaces
        # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.categories = ["Basvetenskap 4"]
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Christian Andersson (Karolinska Institutet)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        # _() function marks text as translatable to other languages
        self.parent.helpText = _("""
Exempelprogram skapat för student inför stationsexamination
i 3D Slicer i kursen Basvetenskap 4 på Karolinska Institutet.
\nSe mer information i <a href="...">dokumentationen</a>.
""")
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = _("""
This file was originally developed by Christian Andersson, Karolinska Institutet.
\nchristian.andersson.2@stud.ki.se
First tested by: William H. Wu, Karolinska Institutet.
""")

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#


def registerSampleData():
    """Add data sets to Sample Data module."""
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData

    iconsPath = os.path.join(os.path.dirname(__file__), "Resources/Icons")

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # Example_Program1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="Example_Program",
        sampleName="Example_Program1",
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, "Example_Program1.png"),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames="Example_Program1.nrrd",
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums="SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        # This node name will be used when the data set is loaded
        nodeNames="Example_Program1",
    )

    # Example_Program2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="Example_Program",
        sampleName="Example_Program2",
        thumbnailFileName=os.path.join(iconsPath, "Example_Program2.png"),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames="Example_Program2.nrrd",
        checksums="SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        # This node name will be used when the data set is loaded
        nodeNames="Example_Program2",
    )


#
# Example_ProgramParameterNode
#


@parameterNodeWrapper
class Example_ProgramParameterNode:
    """
    The parameters needed by module.

    inputVolume - The volume to threshold.
    imageThreshold - The value at which to threshold the input volume.
    invertThreshold - If true, will invert the threshold.
    thresholdedVolume - The output volume that will contain the thresholded volume.
    invertedVolume - The output volume that will contain the inverted thresholded volume.
    """

    inputVolume: vtkMRMLScalarVolumeNode
    imageThreshold: Annotated[float, WithinRange(-100, 500)] = 100
    invertThreshold: bool = False
    thresholdedVolume: vtkMRMLScalarVolumeNode
    invertedVolume: vtkMRMLScalarVolumeNode


#
# Example_ProgramWidget
#


class Example_ProgramWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath("UI/Example_Program.ui"))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = Example_ProgramLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # Buttons
        self.ui.pushButton_Load_Structures.connect("clicked(bool)", self.onLoadStructuresButton)

        self.ui.pushButton_Structure_1.connect("clicked(bool)", lambda: self.onStructureButton(1))
        self.ui.pushButton_Structure_2.connect("clicked(bool)", lambda: self.onStructureButton(2))
        self.ui.pushButton_Structure_3.connect("clicked(bool)", lambda: self.onStructureButton(3))
        self.ui.pushButton_Structure_4.connect("clicked(bool)", lambda: self.onStructureButton(4))
        self.ui.pushButton_Structure_5.connect("clicked(bool)", lambda: self.onStructureButton(5))
        self.ui.pushButton_Structure_6.connect("clicked(bool)", lambda: self.onStructureButton(6))
        self.ui.pushButton_Structure_7.connect("clicked(bool)", lambda: self.onStructureButton(7))
        self.ui.pushButton_Structure_8.connect("clicked(bool)", lambda: self.onStructureButton(8))
        self.ui.pushButton_Structure_9.connect("clicked(bool)", lambda: self.onStructureButton(9))
        self.ui.pushButton_Structure_10.connect("clicked(bool)", lambda: self.onStructureButton(10))

        self.ui.pushButton_Place_Structure_1.connect("clicked(bool)", lambda: self.onPlaceStructureButton(1))
        self.ui.pushButton_Place_Structure_2.connect("clicked(bool)", lambda: self.onPlaceStructureButton(2))
        self.ui.pushButton_Place_Structure_3.connect("clicked(bool)", lambda: self.onPlaceStructureButton(3))
        self.ui.pushButton_Place_Structure_4.connect("clicked(bool)", lambda: self.onPlaceStructureButton(4))
        self.ui.pushButton_Place_Structure_5.connect("clicked(bool)", lambda: self.onPlaceStructureButton(5))
        self.ui.pushButton_Place_Structure_6.connect("clicked(bool)", lambda: self.onPlaceStructureButton(6))
        self.ui.pushButton_Place_Structure_7.connect("clicked(bool)", lambda: self.onPlaceStructureButton(7))
        self.ui.pushButton_Place_Structure_8.connect("clicked(bool)", lambda: self.onPlaceStructureButton(8))
        self.ui.pushButton_Place_Structure_9.connect("clicked(bool)", lambda: self.onPlaceStructureButton(9))
        self.ui.pushButton_Place_Structure_10.connect("clicked(bool)", lambda: self.onPlaceStructureButton(10))

        self.ui.pushButton_Save_And_Quit.connect("clicked(bool)", self.onSaveAndQuitButton)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self) -> None:
        """Called when the application closes and the module widget is destroyed."""
        self.removeObservers()

    def enter(self) -> None:
        """Called each time the user opens this module."""
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        """Called each time the user opens a different module."""
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self._parameterNodeGuiTag = None
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)

    def onSceneStartClose(self, caller, event) -> None:
        """Called just before the scene is closed."""
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """Called just after the scene is closed."""
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """Ensure parameter node exists and observed."""
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.inputVolume:
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.inputVolume = firstVolumeNode

    def setParameterNode(self, inputParameterNode: Optional[Example_ProgramParameterNode]) -> None:
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
        self._parameterNode = inputParameterNode
        if self._parameterNode:
            # Note: in the .ui file, a Qt dynamic property called "SlicerParameterName" is set on each
            # ui element that needs connection.
            self._parameterNodeGuiTag = self._parameterNode.connectGui(self.ui)
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
            self._checkCanApply()

    def _checkCanApply(self, caller=None, event=None) -> None:
        if self._parameterNode and self._parameterNode.inputVolume and self._parameterNode.thresholdedVolume:
            self.ui.applyButton.toolTip = _("Compute output volume")
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = _("Select input and output volume nodes")
            self.ui.applyButton.enabled = False

    def onLoadStructuresButton(self) -> None:
        """Run processing when user clicks "Ladda in strukturer" button."""
        with slicer.util.tryWithErrorDisplay(_("Failed to compute results."), waitCursor=True):
            print("HELLO")
            student_name = self.ui.inputBox_Student_Name.text
            exam_number = self.ui.inputBox_Exam_Number.text
            ret_value = self.logic.onLoadStructuresButtonPressed(student_name, exam_number)
            if ret_value != -1:
                self.ui.inputBox_Student_Name.setEnabled(False)
                self.ui.inputBox_Exam_Number.setEnabled(False)
                self.ui.pushButton_Structure_1.setText(self.logic.structure_buttons_texts[0])
                self.ui.pushButton_Structure_2.setText(self.logic.structure_buttons_texts[1])
                self.ui.pushButton_Structure_3.setText(self.logic.structure_buttons_texts[2])
                self.ui.pushButton_Structure_4.setText(self.logic.structure_buttons_texts[3])
                self.ui.pushButton_Structure_5.setText(self.logic.structure_buttons_texts[4])
                self.ui.pushButton_Structure_6.setText(self.logic.structure_buttons_texts[5])
                self.ui.pushButton_Structure_7.setText(self.logic.structure_buttons_texts[6])
                self.ui.pushButton_Structure_8.setText(self.logic.structure_buttons_texts[7])
                self.ui.pushButton_Structure_9.setText(self.logic.structure_buttons_texts[8])
                self.ui.pushButton_Structure_10.setText(self.logic.structure_buttons_texts[9])
                self.ui.pushButton_Place_Structure_1.setText(self.logic.place_structure_buttons_texts[0])
                self.ui.pushButton_Place_Structure_2.setText(self.logic.place_structure_buttons_texts[1])
                self.ui.pushButton_Place_Structure_3.setText(self.logic.place_structure_buttons_texts[2])
                self.ui.pushButton_Place_Structure_4.setText(self.logic.place_structure_buttons_texts[3])
                self.ui.pushButton_Place_Structure_5.setText(self.logic.place_structure_buttons_texts[4])
                self.ui.pushButton_Place_Structure_6.setText(self.logic.place_structure_buttons_texts[5])
                self.ui.pushButton_Place_Structure_7.setText(self.logic.place_structure_buttons_texts[6])
                self.ui.pushButton_Place_Structure_8.setText(self.logic.place_structure_buttons_texts[7])
                self.ui.pushButton_Place_Structure_9.setText(self.logic.place_structure_buttons_texts[8])
                self.ui.pushButton_Place_Structure_10.setText(self.logic.place_structure_buttons_texts[9])

    def onStructureButton(self, number) -> None:
        """Run processing when user clicks "Apply" button."""
        with slicer.util.tryWithErrorDisplay(_("Failed to compute results."), waitCursor=True):
            self.logic.onStructureButtonPressed(number)
            self.ui.pushButton_Place_Structure_1.setText(self.logic.place_structure_buttons_texts[0])
            self.ui.pushButton_Place_Structure_2.setText(self.logic.place_structure_buttons_texts[1])
            self.ui.pushButton_Place_Structure_3.setText(self.logic.place_structure_buttons_texts[2])
            self.ui.pushButton_Place_Structure_4.setText(self.logic.place_structure_buttons_texts[3])
            self.ui.pushButton_Place_Structure_5.setText(self.logic.place_structure_buttons_texts[4])
            self.ui.pushButton_Place_Structure_6.setText(self.logic.place_structure_buttons_texts[5])
            self.ui.pushButton_Place_Structure_7.setText(self.logic.place_structure_buttons_texts[6])
            self.ui.pushButton_Place_Structure_8.setText(self.logic.place_structure_buttons_texts[7])
            self.ui.pushButton_Place_Structure_9.setText(self.logic.place_structure_buttons_texts[8])
            self.ui.pushButton_Place_Structure_10.setText(self.logic.place_structure_buttons_texts[9])

    def onPlaceStructureButton(self, number) -> None:
        """Run processing when user clicks "Apply" button."""
        with slicer.util.tryWithErrorDisplay(_("Failed to compute results."), waitCursor=True):
            self.logic.onPlaceStructureButtonPressed(number)
            self.ui.pushButton_Place_Structure_1.setText(self.logic.place_structure_buttons_texts[0])
            self.ui.pushButton_Place_Structure_2.setText(self.logic.place_structure_buttons_texts[1])
            self.ui.pushButton_Place_Structure_3.setText(self.logic.place_structure_buttons_texts[2])
            self.ui.pushButton_Place_Structure_4.setText(self.logic.place_structure_buttons_texts[3])
            self.ui.pushButton_Place_Structure_5.setText(self.logic.place_structure_buttons_texts[4])
            self.ui.pushButton_Place_Structure_6.setText(self.logic.place_structure_buttons_texts[5])
            self.ui.pushButton_Place_Structure_7.setText(self.logic.place_structure_buttons_texts[6])
            self.ui.pushButton_Place_Structure_8.setText(self.logic.place_structure_buttons_texts[7])
            self.ui.pushButton_Place_Structure_9.setText(self.logic.place_structure_buttons_texts[8])
            self.ui.pushButton_Place_Structure_10.setText(self.logic.place_structure_buttons_texts[9])

    def onSaveAndQuitButton(self) -> None:
        """Run processing when user clicks "Apply" button."""
        with slicer.util.tryWithErrorDisplay(_("Failed to compute results."), waitCursor=True):
            ret_value = self.logic.onSaveAndQuitButtonPressed()
            if ret_value != -1:
                self.ui.inputBox_Student_Name.text = ""
                self.ui.inputBox_Exam_Number.text = ""
                self.ui.inputBox_Student_Name.setEnabled(True)
                self.ui.inputBox_Exam_Number.setEnabled(True)
                self.ui.pushButton_Structure_1.setText(self.logic.structure_buttons_texts[0])
                self.ui.pushButton_Structure_2.setText(self.logic.structure_buttons_texts[1])
                self.ui.pushButton_Structure_3.setText(self.logic.structure_buttons_texts[2])
                self.ui.pushButton_Structure_4.setText(self.logic.structure_buttons_texts[3])
                self.ui.pushButton_Structure_5.setText(self.logic.structure_buttons_texts[4])
                self.ui.pushButton_Structure_6.setText(self.logic.structure_buttons_texts[5])
                self.ui.pushButton_Structure_7.setText(self.logic.structure_buttons_texts[6])
                self.ui.pushButton_Structure_8.setText(self.logic.structure_buttons_texts[7])
                self.ui.pushButton_Structure_9.setText(self.logic.structure_buttons_texts[8])
                self.ui.pushButton_Structure_10.setText(self.logic.structure_buttons_texts[9])
                self.ui.pushButton_Place_Structure_1.setText(self.logic.place_structure_buttons_texts[0])
                self.ui.pushButton_Place_Structure_2.setText(self.logic.place_structure_buttons_texts[1])
                self.ui.pushButton_Place_Structure_3.setText(self.logic.place_structure_buttons_texts[2])
                self.ui.pushButton_Place_Structure_4.setText(self.logic.place_structure_buttons_texts[3])
                self.ui.pushButton_Place_Structure_5.setText(self.logic.place_structure_buttons_texts[4])
                self.ui.pushButton_Place_Structure_6.setText(self.logic.place_structure_buttons_texts[5])
                self.ui.pushButton_Place_Structure_7.setText(self.logic.place_structure_buttons_texts[6])
                self.ui.pushButton_Place_Structure_8.setText(self.logic.place_structure_buttons_texts[7])
                self.ui.pushButton_Place_Structure_9.setText(self.logic.place_structure_buttons_texts[8])
                self.ui.pushButton_Place_Structure_10.setText(self.logic.place_structure_buttons_texts[9])

#
# Example_ProgramLogic
#


class Example_ProgramLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self) -> None:
        """Called when the logic class is instantiated. Can be used for initializing member variables."""
        ScriptedLoadableModuleLogic.__init__(self)
        self.exam_active = False
        self.structures = []
        self.current_dataset = ""
        self.answered_questions = [False] * NUMBER_OF_QUESTIONS
        self.node = None
        self.student_name = ""
        self.exam_nr = 0
        self.structure_buttons_texts = [""] * NUMBER_OF_QUESTIONS
        self.setStructureButtonsText()
        self.place_structure_buttons_texts = [""] * NUMBER_OF_QUESTIONS
        self.setPlaceStructureButtonsText()

    def getParameterNode(self):
        return Example_ProgramParameterNode(super().getParameterNode())

    def process(self,
                inputVolume: vtkMRMLScalarVolumeNode,
                outputVolume: vtkMRMLScalarVolumeNode,
                imageThreshold: float,
                invert: bool = False,
                showResult: bool = True) -> None:
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: volume to be thresholded
        :param outputVolume: thresholding result
        :param imageThreshold: values above/below this threshold will be set to 0
        :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
        :param showResult: show output volume in slice viewers
        """

        if not inputVolume or not outputVolume:
            raise ValueError("Input or output volume is invalid")

        import time

        startTime = time.time()
        logging.info("Processing started")

        # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
        cliParams = {
            "InputVolume": inputVolume.GetID(),
            "OutputVolume": outputVolume.GetID(),
            "ThresholdValue": imageThreshold,
            "ThresholdType": "Above" if invert else "Below",
        }
        cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
        # We don't need the CLI module node anymore, remove it to not clutter the scene with it
        slicer.mrmlScene.RemoveNode(cliNode)

        stopTime = time.time()
        logging.info(f"Processing completed in {stopTime-startTime:.2f} seconds")

    def reset(self):
        self.exam_active = False
        self.structures = []
        self.current_dataset = ""
        self.answered_questions = [False] * NUMBER_OF_QUESTIONS
        self.node = None
        self.student_name = ""
        self.exam_nr = 0

    def onLoadStructuresButtonPressed(self, student_name, exam_nr):
        if self.exam_active:
            qt.QMessageBox.warning(slicer.util.mainWindow(), Q_MESSAGE_BOX_TITLE,
                                   f"Kan ej ladda in strukturer medan en exam är aktiv.")
            return -1
        if len(student_name.split()) < 2:
            # Kanske även kolla att endast innehåller a-ö och mellanslag
            qt.QMessageBox.warning(slicer.util.mainWindow(), Q_MESSAGE_BOX_TITLE,
                                   f"Ange både för- och efternamn.")
            return -1
        reply = qt.QMessageBox.question(slicer.util.mainWindow(), Q_MESSAGE_BOX_TITLE,
                                        f"Har du angett rätt namn och exam nr?\nNamn: {student_name}\nExam nr: {exam_nr}",
                                        qt.QMessageBox.Yes | qt.QMessageBox.No)
        if reply == qt.QMessageBox.No:
            return -1
        self.student_name = student_name
        self.exam_nr = exam_nr
        self.retrieveStructures(int(self.exam_nr))
        if len(self.structures) != 10:
            # Måste nog göra reset då
            print(len(self.structures))
            print(self.exam_nr)
            qt.QMessageBox.warning(slicer.util.mainWindow(), Q_MESSAGE_BOX_TITLE, f"Inga strukturer kunde hittas för exam nr: {exam_nr}.")
            return -1
        self.addNodeAndControlPoints(exam_nr, student_name, self.structures)
        self.exam_active = True
        self.setStructureButtonsText(structures=self.structures)
        self.updateAnsweredQuestions()
        self.setPlaceStructureButtonsText()
        return 0

    def onStructureButtonPressed(self, number):
        if not self.exam_active:
            return -1
        self.updateAnsweredQuestions()
        self.setPlaceStructureButtonsText()
        self.changeDataset(self.structures[number - 1]["Dataset"])
        slicer.modules.markups.logic().JumpSlicesToLocation(0, 0, 0, True)
        self.node.GetDisplayNode().SetActiveControlPoint(number - 1)
        if self.checkIfControlPointExists(number):
            self.centreOnControlPoint(self.node, number - 1, self.structures[number - 1]["Dataset"])

    def onPlaceStructureButtonPressed(self, number):
        if not self.exam_active:
            return -1
        self.updateAnsweredQuestions()
        self.setPlaceStructureButtonsText()
        self.changeDataset(self.structures[number - 1]["Dataset"])
        if self.answered_questions[number - 1]:
            reply = qt.QMessageBox.question(slicer.util.mainWindow(), Q_MESSAGE_BOX_TITLE,
                                            f"Du har redan placerat ut denna struktur.\nÄr du säker på att du vill placera om den?",
                                            qt.QMessageBox.Yes | qt.QMessageBox.No)
            if reply == qt.QMessageBox.No:
                return
        self.setNewControlPoint(self.node, number - 1)

    def onSaveAndQuitButtonPressed(self):
        # Återställer fönstrena och byter till big brain vid ny användare
        if not self.exam_active:
            qt.QMessageBox.warning(slicer.util.mainWindow(), Q_MESSAGE_BOX_TITLE,
                                   f"Kan inte spara när ingen exam pågår.")
            return -1
        reply = qt.QMessageBox.question(slicer.util.mainWindow(), Q_MESSAGE_BOX_TITLE,
                                        f"Är du säker på att du vill avsluta?",
                                        qt.QMessageBox.Yes | qt.QMessageBox.No)
        if reply == qt.QMessageBox.No:
            return -1
        slicer.mrmlScene.RemoveNode(self.node)
        self.resetWindow()
        self.resetAnsweredQuestions()
        self.reset()
        self.setStructureButtonsText()
        self.setPlaceStructureButtonsText()

    def setStructureButtonsText(self, structures=None):
        for i in range(len(self.structure_buttons_texts)):
            if structures is None:
                structure_str = f"Struktur {i + 1}"
            else:
                structure_str = f"Struktur {i + 1}: {structures[i]['Structure']} i {structures[i]['Dataset']}"
            self.structure_buttons_texts[i] = structure_str

    def setPlaceStructureButtonsText(self):
        for i in range(len(self.place_structure_buttons_texts)):
            if not self.exam_active:
                structure_str = ""
            elif self.answered_questions[i]:
                structure_str = "(✓)"
            else:
                structure_str = "(X)"
            self.place_structure_buttons_texts[i] = structure_str

    def displaySelectVolume(self, a):
        layoutManager = slicer.app.layoutManager()
        for sliceViewName in layoutManager.sliceViewNames():
            view = layoutManager.sliceWidget(sliceViewName).sliceView()
            sliceNode = view.mrmlSliceNode()
            sliceLogic = slicer.app.applicationLogic().GetSliceLogic(sliceNode)
            compositeNode = sliceLogic.GetSliceCompositeNode()
            compositeNode.SetBackgroundVolumeID(str(a))

    # Byter dataset till big brain och fokuserar på koordinaterna [0, 0, 0]
    def resetWindow(self):
        self.changeDataset(BIG_BRAIN)
        slicer.modules.markups.logic().JumpSlicesToLocation(0, 0, 0, True)

    # Läser in alla rader tillhörande exam_nr
    def retrieveStructures(self, exam_nr) -> list:
        structures = {
            241: [{'Structure': 'nucleus caudatus',
                'Dataset': 'Big_Brain',
                'question': '1'},
               {'Structure': 'Mesencephalon',
                'Dataset': 'Big_Brain',
                'question': '2'},
               {'Structure': 'foramen interventriculare',
                'Dataset': 'in_vivo',
                'question': '3'},
               {'Structure': 'lobus cerebelli posterior',
                'Dataset': 'in_vivo',
                'question': '4'},
               {'Structure': 'Sulcus marginalis',
                'Dataset': 'in_vivo',
                'question': '5'},
               {'Structure': 'Nodulus',
                'Dataset': 'in_vivo',
                'question': '6'},
               {'Structure': 'Cortex piriformis',
                'Dataset': 'ex_vivo',
                'question': '7'},
               {'Structure': 'Thalamus',
                'Dataset': 'ex_vivo',
                'question': '8'},
               {'Structure': 'Tonsilla',
                'Dataset': 'ex_vivo',
                'question': '9'},
               {'Structure': 'Fasciculus longitidinalis inferior',
                'Dataset': 'Tracts_3D',
                'question': '10'}],
         242: [{'Structure': 'sulcus collateralis',
                'Dataset': 'Big_Brain',
                'question': '1'},
               {'Structure': 'Lamina terminalis',
                'Dataset': 'Big_Brain',
                'question': '2'},
               {'Structure': 'a. cerebri posterior (P4)',
                'Dataset': 'in_vivo',
                'question': '3'},
               {'Structure': 'capsula interna',
                'Dataset': 'in_vivo',
                'question': '4'},
               {'Structure': 'Colliculus superior',
                'Dataset': 'in_vivo',
                'question': '5'},
               {'Structure': 'lobus cerebelli anterior',
                'Dataset': 'in_vivo',
                'question': '6'},
               {'Structure': 'Putamen',
                'Dataset': 'in_vivo',
                'question': '7'},
               {'Structure': 'sinus sigmoideus',
                'Dataset': 'in_vivo',
                'question': '8'},
               {'Structure': 'Thalamus',
                'Dataset': 'ex_vivo',
                'question': '9'},
               {'Structure': 'Ventriculus lateralis',
                'Dataset': 'ex_vivo',
                'question': '10'}],
         243: [{'Structure': 'Nucleus accumbens',
                'Dataset': 'Big_Brain',
                'question': '1'},
               {'Structure': 'Area postrema',
                'Dataset': 'Big_Brain',
                'question': '2'},
               {'Structure': 'Operculum parietale',
                'Dataset': 'Big_Brain',
                'question': '3'},
               {'Structure': 'a. cerebri anterior',
                'Dataset': 'in_vivo',
                'question': '4'},
               {'Structure': 'aqueductus cerebri/mesencephali',
                'Dataset': 'in_vivo',
                'question': '5'},
               {'Structure': 'falx cerebri',
                'Dataset': 'in_vivo',
                'question': '6'},
               {'Structure': 'Sinus rectus',
                'Dataset': 'in_vivo',
                'question': '7'},
               {'Structure': 'Flocculus',
                'Dataset': 'ex_vivo',
                'question': '8'},
               {'Structure': 'hemispherium cerebelli',
                'Dataset': 'ex_vivo',
                'question': '9'},
               {'Structure': 'Medulla oblongata',
                'Dataset': 'ex_vivo',
                'question': '10'}],
         244: [{'Structure': 'basis pontis',
                'Dataset': 'Big_Brain',
                'question': '1'},
               {'Structure': 'a. lenticulostriatae laterales',
                'Dataset': 'in_vivo',
                'question': '2'},
               {'Structure': 'capsula externa',
                'Dataset': 'in_vivo',
                'question': '3'},
               {'Structure': 'Corpus callosum rostrum',
                'Dataset': 'in_vivo',
                'question': '4'},
               {'Structure': 'pedunculus cerebellaris inferior',
                'Dataset': 'in_vivo',
                'question': '5'},
               {'Structure': 'Ventriculus lateralis',
                'Dataset': 'in_vivo',
                'question': '6'},
               {'Structure': 'capsula extrema',
                'Dataset': 'ex_vivo',
                'question': '7'},
               {'Structure': 'Hippocampus',
                'Dataset': 'ex_vivo',
                'question': '8'},
               {'Structure': 'plexus choroideus',
                'Dataset': 'ex_vivo',
                'question': '9'},
               {'Structure': 'sulcus hypothalamicus',
                'Dataset': 'ex_vivo',
                'question': '10'}],
         245: [{'Structure': 'pyramis medullae oblongatae',
                'Dataset': 'Big_Brain',
                'question': '1'},
               {'Structure': 'Ventriculus lateralis',
                'Dataset': 'Big_Brain',
                'question': '2'},
               {'Structure': 'Mesencephalon',
                'Dataset': 'Big_Brain',
                'question': '3'},
               {'Structure': 'Cuneus',
                'Dataset': 'Big_Brain',
                'question': '4'},
               {'Structure': 'Operculum parietale',
                'Dataset': 'Big_Brain',
                'question': '5'},
               {'Structure': 'a. carotis interna',
                'Dataset': 'in_vivo',
                'question': '6'},
               {'Structure': 'Globus pallidus externa',
                'Dataset': 'in_vivo',
                'question': '7'},
               {'Structure': 'sinus cavernosus',
                'Dataset': 'in_vivo',
                'question': '8'},
               {'Structure': 'ventriculus quartus',
                'Dataset': 'ex_vivo',
                'question': '9'},
               {'Structure': 'Area tegmentalis ventralis (VTA',
                'Dataset': 'ex_vivo',
                'question': '10'}]}
        if exam_nr >= 241 and exam_nr <= 245:
            self.structures = structures[exam_nr]
        else:
            self.structures = []

    # Ändrar nuvarande dataset till specificerat dataset
    def changeDataset(self, dataset):
        if dataset.lower()  == BIG_BRAIN.lower():
            self.displaySelectVolume(BIG_BRAIN_VOLUME_NAME)
            self.current_dataset = BIG_BRAIN
        elif dataset.lower() == IN_VIVO.lower():
            self.displaySelectVolume(IN_VIVO_VOLUME_NAME)
            self.current_dataset = IN_VIVO
        elif dataset.lower() == EX_VIVO.lower():
            self.displaySelectVolume(EX_VIVO_VOLUME_NAME)
            self.current_dataset = EX_VIVO
        else:
            print(f"\nDataset: {dataset} existerar ej\n")

    # Lägger till en nod med namnet exam_nr och lägger till tillhörande control points
    # för varje struktur i structures. Namnet på varje control point blir strukturens
    # namn och beskrivningen blir vilket nummer strukturen är.
    def addNodeAndControlPoints(self, exam_nr, student_name, structures):
        node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', f"{exam_nr}_{student_name}")
        node.SetLocked(1)
        node.AddNControlPoints(10, "", [0, 0, 0])
        for _index, structure in enumerate(structures):
            try:
                index = int(structure["question"]) - 1
            except:
                index = _index
            node.SetNthControlPointLabel(index, structure["Structure"])
            node.SetNthControlPointDescription(index, f"Struktur {index + 1}")
            node.SetNthControlPointLocked(index, False)
            # Avmarkerar strukturen innan man placerat den.
            # Tar bort koordinater [0, 0, 0] för skapade punkten så att den inte är i vägen.
            node.UnsetNthControlPointPosition(index)
        self.node = node
        return node

    # Ändrar till place mode så att en ny control point kan placeras ut
    def setNewControlPoint(self, node, index):
        # Återställ control point
        node.SetNthControlPointPosition(index, 0.0, 0.0, 0.0)
        node.UnsetNthControlPointPosition(index)
        # Placera ut ny control point
        node.SetControlPointPlacementStartIndex(index)
        slicer.modules.markups.logic().StartPlaceMode(1)
        interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
        # Återgå sedan till normalt läge när klar
        interactionNode.SetPlaceModePersistence(0)
        #interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
        #interactionNode.SwitchToViewTransformMode()

        # also turn off place mode persistence if required
        #interactionNode.SetPlaceModePersistence(0)

    def checkIfControlPointExists(self, question_number):
        # Kan också kolla om den är set eller unset
        return self.answered_questions[question_number - 1]

    # Centrerar vyerna på control point
    # Hantera på ett bättre sätt i framtiden
    def centreOnControlPoint(self, node, index, dataset):
        controlPointCoordinates = node.GetNthControlPointPosition(index) # eller GetNthControlPointPositionWorld
        slicer.modules.markups.logic().JumpSlicesToLocation(controlPointCoordinates[0], controlPointCoordinates[1], controlPointCoordinates[2], True)

    def resetAnsweredQuestions(self):
        self.answered_questions = [False] * NUMBER_OF_QUESTIONS

    def updateAnsweredQuestions(self):
        self.resetAnsweredQuestions() # behövs detta?
        for i in range(self.node.GetNumberOfControlPoints()):
            controlPointCoordinates = self.node.GetNthControlPointPosition(i)
            # Kan också kolla om den är set eller unset
            if controlPointCoordinates[0] != 0.0 or controlPointCoordinates[1] != 0.0 or controlPointCoordinates[2] != 0.0:
                # Om koordinater för control point ej är [0.0, 0.0, 0.0] är frågan besvarad
                self.answered_questions[i] = True


#
# Example_ProgramTest
#


class Example_ProgramTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """Do whatever is needed to reset the state - typically a scene clear will be enough."""
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here."""
        self.setUp()
        self.test_Example_Program1()

    def test_Example_Program1(self):
        """Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData

        registerSampleData()
        inputVolume = SampleData.downloadSample("Example_Program1")
        self.delayDisplay("Loaded test data set")

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = Example_ProgramLogic()

        # Test algorithm with non-inverted threshold
        logic.process(inputVolume, outputVolume, threshold, True)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], threshold)

        # Test algorithm with inverted threshold
        logic.process(inputVolume, outputVolume, threshold, False)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], inputScalarRange[1])

        self.delayDisplay("Test passed")

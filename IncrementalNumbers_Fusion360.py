#Author-Johan Norén
#Description-Create list of incremental numbers.

import adsk.core, adsk.fusion, traceback

import os
import sys
fontToolPath = os.path.dirname(os.path.realpath(__file__))
fontToolPath = fontToolPath + "/FontTools"
if not fontToolPath in sys.path:
    sys.path.append(fontToolPath)
from fontTools import ttLib

_app = None
_ui  = None

_handlers = []

######### begin functions for Font ##################

FONT_SPECIFIER_NAME_ID = 4
FONT_SPECIFIER_FAMILY_ID = 1

#short name of a truetype font
#platformID: Windows or Mac
def shortName(font,platformID):
     name = ""
     family = ""
     for record in font['name'].names:
         if record.nameID == FONT_SPECIFIER_NAME_ID and not name and record.platformID==platformID:
             name = record.toUnicode()
         elif record.nameID == FONT_SPECIFIER_FAMILY_ID and not family and record.platformID==platformID:
             family = record.toUnicode()
         if name and family:
            break

     return name, family

def getFontList(dic):
     app = adsk.core.Application.get()
     ui = app.userInterface
     if sys.platform.startswith('win') or sys.platform.startswith('cygwin'):
            #Windows
            FontPath = os.path.join(os.environ['WINDIR'], 'Fonts')
            PlatFormID = 3
     elif sys.platform.startswith('darwin'):
            #Mac
            FontPath = '/Library/Fonts/'
            PlatFormID = 1
     else:
         if ui:
              ui.messageBox('This is an unknown OS!!')
              return

     #iterate each *.ttf font in the specific folder
     for file in os.listdir(FontPath):
        if file.lower().endswith(".ttf") or file.lower().endswith(".ttc"):
            source_file_name = FontPath+"/"+file
            tt = ttLib.TTFont(source_file_name,fontNumber=0)
            font_ori_name =  shortName(tt,PlatFormID)[1]
            #store this font to fonts map
            if not font_ori_name in dic:
                dic[font_ori_name] = source_file_name
####### end of functions for Font######################

class IncrementalNumbersInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self,args):
        try:
            eventArgs= adsk.core.InputChangedEventArgs.cast(args)
            inputs = eventArgs.inputs
            cmdInput = eventArgs.input
            
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class IncrementalNumbersExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self,args):
        try:
            cmd = args.firingEvent.sender
            inputs = cmd.commandInputs
            
            pointInput = None
            numStartInput = None
            numIncrementInput = None
            numInstancesInput = None
            numSpacingInput = None
            numHeightInput = None
            
            for inputI in inputs:
                if inputI.id == 'numStart':
                    numStartInput = inputI
                elif inputI.id == 'numIncrement':
                    numIncrementInput = inputI
                elif inputI.id == 'intInstances':
                    numInstancesInput = inputI
                elif inputI.id == 'numSpacing':
                    numSpacingInput = inputI
                elif inputI.id == 'numHeight':
                    numHeightInput = inputI
                elif inputI.id == 'sketchInput':
                    sketchInput = inputI
                elif inputI.id == 'pointInput':
                    pointInput = inputI
                elif inputI.id == 'intPrecision':
                    intPrecisionInput = inputI
                elif inputI.id == 'boolCenter':
                    boolCenterInput = inputI
                elif inputI.id == 'radioDirection':
                    radioDirection = inputI         
                elif inputI.id == 'numAngle':
                    numAngleInput = inputI
                elif inputI.id == 'dropFont':
                    dropFontInput = inputI
                elif inputI.id == 'strPrefix':
                    strPrefixInput = inputI
                elif inputI.id == 'strSufix':
                    strSufixInput = inputI    
            
            outNum = numStartInput.value
            numIncrement = numIncrementInput.value
            numInstances = numInstancesInput.value
            numSpacing = numSpacingInput.value
            numHeight = numHeightInput.value
            intPrecision = intPrecisionInput.value
            boolCenter = boolCenterInput.value
            radioDirectionSelect = radioDirection.selectedItem.name
            numAngle = numAngleInput.value            
            dropFont = dropFontInput.selectedItem.name
            strPrefix = strPrefixInput.value
            strSufix = strSufixInput.value
            
            pointSelect = pointInput.selection(0)
            sketchPoint = pointSelect.entity
            outPoint = sketchPoint.geometry            
            
            sketch = sketchPoint.parentSketch
            sketchTexts = sketch.sketchTexts

            # Do the rest                   
            for unused in range(numInstances):
                del unused
                outStr = '%.*f' % (intPrecision,outNum)                

                # Print the text                    
                sketchTextInput = sketchTexts.createInput(strPrefix + outStr  + strSufix,numHeight,outPoint)                
                sketchTextInput.angle = numAngle
                sketchTextInput.fontName = dropFont
                sketchText = sketchTexts.add(sketchTextInput)
                            
                if boolCenter == True:
                    # Get the width of the newly created text
                    boundingBox = sketchText.boundingBox
                    pMax = boundingBox.maxPoint
                    pMin = boundingBox.minPoint
                    boxWidth = pMax.x - pMin.x
                    boxHeight = pMax.y - pMin.y                
                    
                    newPos = sketchText.position
                    if radioDirectionSelect == 'X':    
                        newPos.x = newPos.x - boxWidth/2
                    elif radioDirectionSelect == 'Y':
                        newPos.y = newPos.y - boxHeight/2
                        
                    # Offset the text half the width
                    # sketchText.position.x = sketchText.position.x - boxWidth/2
                    sketchText.position = newPos
                
                
                # Increment struff
                outNum += numIncrement
                # Increment position
                if radioDirectionSelect == 'X':    
                    outPoint.x = outPoint.x + numSpacing             
                elif radioDirectionSelect == 'Y':
                    outPoint.y = outPoint.y + numSpacing
                
                
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class IncrementalNumbersCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self,args):
        try:
            # Get command
            cmd = adsk.core.Command.cast(args.command)
            
            # Connect destroyed event handler
            onDestroy = IncrementalNumbersDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # Connect input changed event handler
            onInputChanged = IncrementalNumbersInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)  
            
            # Connect execute handler
            onExecute = IncrementalNumbersExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)
            
            inputs = cmd.commandInputs            
            
            # Select startpoint
            # selectionInput = inputs.addSelectionInput('sketchInput','Select sketch','Select sketch to normalize text inside')
            # selectionInput.addSelectionFilter('Sketches')
            
            selectionInput = inputs.addSelectionInput('pointInput','Select point','Select point in sketch.')
            selectionInput.addSelectionFilter('SketchPoints')
            
            inputs.addBoolValueInput('boolCenter', 'Reference center', True, '', False)            
            
            # Startnumber
            inputs.addValueInput('numStart', 'First number', '', adsk.core.ValueInput.createByReal(0.0))
            
            # Increments
            inputs.addValueInput('numIncrement', 'Increment', '', adsk.core.ValueInput.createByReal(10.0))
            
            # Precision
            inputs.addIntegerSpinnerCommandInput('intPrecision', 'Decimal Precision', 0 , 10 , 1, 0)            
            
            # Number of instances
            inputs.addIntegerSpinnerCommandInput('intInstances', 'Instances', 1 , 1000 , 1, 2)
            # inputs.addValueInput('numInstances', 'Instances', '', adsk.core.ValueInput.createByReal(0.0))
            
            # Spacing
            inputs.addValueInput('numSpacing','Spacing','mm',adsk.core.ValueInput.createByReal(1.00))            
            
            # Prefix
            inputs.addStringValueInput('strPrefix', 'Prefix', '')            

            # Suffix
            inputs.addStringValueInput('strSufix', 'Sufix', '')            
            
            # Direction
            # Create radio button group input.
            radioButtonGroup = inputs.addRadioButtonGroupCommandInput('radioDirection', 'Direction')
            radioButtonItems = radioButtonGroup.listItems
            radioButtonItems.add("X", True)
            radioButtonItems.add("Y", False)
            # Orientation
            inputs.addAngleValueCommandInput('numAngle', 'Angle', adsk.core.ValueInput.createByString('0 degree'))
            
            # Textproperties
            # Font
            # Create dropdown input with radio style.
            fontDropInput = inputs.addDropDownCommandInput('dropFont', 'Font', adsk.core.DropDownStyles.LabeledIconDropDownStyle)
            fontDropInputItems = fontDropInput.listItems
            # dropdown3Items.add('Item 1', True, '')
            # dropdown3Items.add('Item 2', False, '')            
            fontList = {}
            getFontList(fontList)
            fontListSort = sorted(fontList.keys())
            for font in fontListSort:
                if font == 'Arial':
                    fontDropInputItems.add(font,True,'')
                else:
                    fontDropInputItems.add(font,False,'')
            
            # Size
            inputs.addValueInput('numHeight','Text height','mm',adsk.core.ValueInput.createByReal(1.20))
            
            # ...?
            
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class IncrementalNumbersDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self,args):
        try:
            adsk.terminate()
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            
def run(context):
    try:    
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        
        cmdDef = _ui.commandDefinitions.itemById('cmdIncrementalNumbers')
        if not cmdDef:
            cmdDef = _ui.commandDefinitions.addButtonDefinition('cmdIncrementalNumbers', 'Incremental Number Creator', 'Creates a series of incremental numbers in a new sketch.')
    
        onCommandCreated = IncrementalNumbersCreatedHandler()    
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        cmdDef.execute()    
        
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
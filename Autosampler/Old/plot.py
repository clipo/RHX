"""
This demo shows how Chaco and Traits can be used to easily build a data
acquisition and visualization system.

Two frames are opened: one has the plot and allows configuration of
various plot properties, and one which simulates controls for the hardware
device from which the data is being acquired; in this case, it is a mockup
random number generator whose mean and standard deviation can be controlled
by the user.
"""

# Major library imports
import random
import wx
from numpy import arange, append, array, hstack, random, zeros

# Enthought imports
from enthought.traits.api import Array, Bool, Callable, Enum, Float, HasTraits,\
   Instance, Int, Trait
from enthought.traits.ui.api import Group, HGroup, Item, View, spring, Handler
from enthought.pyface.timer.api import Timer

# Chaco imports
from enthought.chaco.chaco_plot_editor import ChacoPlotItem
import DataReadWrite

#print rcParams.keys()
dbName="TEST9"
dbDir="c:/Users/Archy/Dropbox/Rehydroxylation/"

value=DataReadWrite.openDatabase(dbDir,dbName)
runID=1
sampleLocation=1
count =0
# The max number of data points to accumulate and show in the plot
max_number_of_points = 500
max_number_of_samples=25


class Viewer(HasTraits):
   """ This class just contains the two data arrays that will be updated
   by the Controller.  The visualization/editor for this class is a
   Chaco plot.
   """

   index = []
   data = []

   plot_type = Enum("line", "scatter")

   # This "view" attribute defines how an instance of this class will
   # be displayed when .edit_traits() is called on it.  (See MyApp.OnInit()
   # below.)
   view = View(ChacoPlotItem("index", "data",
      type_trait="plot_type",
      resizable=True,
      x_label="Time",
      y_label="Weight (g)",
      color="blue",
      bgcolor="white",
      border_visible=True,
      border_width=1,
      padding_bg_color="lightgray",
      width=800,
      height=380,
      show_label=False),
      HGroup(spring, Item("plot_type", style='custom'), spring),
      resizable = True,
      buttons = ["OK"],
      width=800, height=500)


class Controller(HasTraits):
   lastcalled=1
   # A reference to the plot viewer object
   viewer = Instance(Viewer)

   currentSampleNumber=0


   def add_data_point(self, sampleNumber, newValue):
      """ Function that when called adds a new point to the existing data set and plots it.
      """

   new_val = DataReadWrite.getCrucibleWeightMeasurement(runID,sampleNumber,self.num_ticks)

   self.num_ticks += 1

   if self.currentSampleNumber < sampleNumber:
      self.currentSampleNumber=sampleNumber
      self.num_ticks=0

   data[num_ticks]=new_val
   index[num_ticks] += 1


class DemoHandler(Handler):

   def closed(self, info, is_ok):
      """ Handles a dialog-based user interface being closed by the user.
      Overridden here to stop the timer once the window is destroyed.
      """
      return

class Demo(HasTraits):
   controller = Instance(Controller)
   viewer = Instance(Viewer, ())
   timer = Instance(Timer)
   view = View(Item('controller', style='custom', show_label=False),
      Item('viewer', style='custom', show_label=False),
      handler = DemoHandler,
      resizable=True)

   def edit_traits(self, *args, **kws):

      return super(Demo, self).edit_traits(*args, **kws)

   def configure_traits(self, *args, **kws):

      return super(Demo, self).configure_traits(*args, **kws)

   def _controller_default(self):
      return Controller(viewer=self.viewer)

popup=Demo()

# wxApp used when this file is run from the command line.

class MyApp(wx.PySimpleApp):

   def OnInit(self, *args, **kw):
      viewer = Viewer()
      controller = Controller(viewer = viewer)

      # Pop up the windows for the two objects
      viewer.edit_traits()
      controller.edit_traits()

      return True




# This is called when this example is to be run in a standalone mode.
if __name__ == "__main__":
   app = MyApp()
   app.MainLoop()

# EOF

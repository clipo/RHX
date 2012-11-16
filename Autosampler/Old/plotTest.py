
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

count =0
# The max number of data points to accumulate and show in the plot



class Viewer(HasTraits):
   """ This class just contains the two data arrays that will be updated
   by the Controller.  The visualization/editor for this class is a
   Chaco plot.
   """
   max_number_of_points = 100
   max_number_of_samples=25
   index = Array
   data = Array
   num_ticks=Int(0)
   plot_type = Enum("line", "scatter")
   currentSampleNumber=1
   # This "view" attribute defines how an instance of this class will
   # be displayed when .edit_traits() is called on it.  (See MyApp.OnInit()
   # below.)
   view = View(ChacoPlotItem("index", "data",
      type_trait="plot_type",
      resizable=True,
      x_label="Time",
      y_label="Weight (g)",
      y_auto=True,
      x_auto=True,
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

   def add_data_point(self, newValue):
      """ Function that when called adds a new point to the existing data set and plots it.
      """
      self.num_ticks += 1

      # grab the existing data, truncate it, and append the new point.
      # This isn't the most efficient thing in the world but it works.
      cur_data = self.data
      new_data = hstack((cur_data[-self.max_number_of_points+1:], [newValue]))
      new_index = arange(self.num_ticks - len(new_data) + 1, self.num_ticks+0.01)

      self.index = new_index
      self.data = new_data

      return

# EOF

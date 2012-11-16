#!/usr/bin/env python
"""
Draws some x-y line and scatter plots. On the left hand plot:
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom
   history".
"""

# Major library imports
from numpy import linspace
from scipy.special import jn

import numpy as np
import matplotlib.pyplot as plt
from pylab import *

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor, Window
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, Group, View
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import View, Item
from enthought.chaco.api import Plot, ArrayPlotData
from enthought.enable.component_editor import ComponentEditor
from numpy import cos, linspace, sin

# Chaco imports
from enthought.chaco.api import ArrayPlotData, HPlotContainer, Plot
from enthought.chaco.tools.api import PanTool, ZoomTool
import DataReadWrite

#===============================================================================
# # Create the Chaco plot.
#===============================================================================


class OverlappingPlot(HasTraits):


   plot = Instance(Plot)
   traits_view = View(
      Item('plot',editor=ComponentEditor(), show_label=False),
      width=700, height=500, resizable=True, title="Chaco Plot")
   def __init__(self):
      dbName="TEST5"
      dbDir="c:/Users/Archy/Dropbox/Rehydroxylation/"

      data= []
      value=DataReadWrite.openDatabase(dbDir,dbName)
      runID=1
      sampleLocation=1
      count=0

      #super(OverlappingPlot).__init__()
      data=DataReadWrite.getCrucibleWeightOverTime(runID,sampleLocation)
      for row in data:
         count += 1
         #print row

      x = linspace(0, count, 100)
      plotdata = ArrayPlotData(x=count, y=row)
      plot = Plot(plotdata)
      plot.plot(("x", "y"), type="scatter", color="blue")
      self.plot = plot


   container = HPlotContainer()
   container.add(plot)
   #container.add(plot2)

if __name__ == "__main__":
   OverlappingPlot().configure_traits()

#--EOF---
__author__ = 'clipo'
  
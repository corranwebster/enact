#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

import numpy

from traits.api import HasTraits, Button, Array, Range, Any, Instance, Property
from traitsui.api import View, UItem
from enact.api import get_transition_manager, AttributeTransition, PlotDataTransition
from enable.api import ComponentEditor
from chaco.api import ArrayPlotData, Plot, jet

NUM_POINTS = 10000
TIME_LENGTH = 100

class EasingPlot(HasTraits):
    
    data = Array
    
    time = Range(0, TIME_LENGTH-1)
    
    current_data = Array
    
    play = Button
    
    plot_data = Instance(ArrayPlotData)

    plot = Instance(Plot)
    
    transition_manager = Any
    
    def __init__(self, *args, **kwargs):
        super(EasingPlot, self).__init__(*args, **kwargs)
        if self.transition_manager is None:
            self.transition_manager = get_transition_manager()
        self.transition_manager.heartbeat
    
    def _data_default(self):
        return numpy.random.uniform(size=(TIME_LENGTH, NUM_POINTS, 3))
    
    def _current_data_default(self):
        return self.data[self.time]
    
    def _plot_data_default(self):
        plot_data = ArrayPlotData(
            x=self.current_data[:,0],
            y=self.current_data[:,1],
            z=self.current_data[:,2]
        )
        return plot_data
    
    def _plot_default(self):
        plot = Plot(self.plot_data)
        plot.value_range.high = 1.0
        plot.value_range.low = 0.0
        plot.index_range.high = 1.0
        plot.index_range.low = 0.0
        plot.plot(('x', 'y', 'z'), type='cmap_scatter', color_mapper=jet)
        return plot

    
    def _play_fired(self):
        transition_t = AttributeTransition(
            ease='int_linear',
            obj=self,
            attr='time',
            duration=100-self.time,
            final=99
        )
        self.transition_manager.connect(transition_t)
    
    def _time_changed(self):
        self.current_data = self.data[self.time]
    
    def _current_data_changed(self):
        transition_x = PlotDataTransition(
            ease = 'ease_in',
            plot_data = self.plot_data,
            data_key = 'x',
            duration = 1.0,
            final = self.current_data[:,0],
        )
        transition_y = PlotDataTransition(
            ease = 'ease_in',
            plot_data = self.plot_data,
            data_key = 'y',
            duration = 1.0,
            final = self.current_data[:,1],
        )
        transition_z = PlotDataTransition(
            ease = 'ease_in',
            plot_data = self.plot_data,
            data_key = 'z',
            duration = 1.0,
            final = self.current_data[:,2],
        )
        self.transition_manager.connect(transition_x)
        self.transition_manager.connect(transition_y)
        self.transition_manager.connect(transition_z)
    
    view = View(
        UItem('plot', editor=ComponentEditor()),
        UItem('time'),
        UItem('play'),
        resizable=True,
    )
    
    
if __name__ == '__main__':
    plot = EasingPlot()
    plot.configure_traits()
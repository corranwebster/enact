#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

import numpy

from traits.api import HasTraits, Bool, Button, Array, Instance
from traitsui.api import View, UItem
from kiva.image import GraphicsContext
import kiva.constants
from enable.api import ComponentEditor
from enact.api import InteractiveComponent, InteractiveContext, ItemTransition, \
    TransitionManager

circle_dtype = numpy.dtype([('x', int), ('y', int), ('radius', float)])

class MouseInteraction(InteractiveContext):
    
    circles = Array
    
    random = Bool
    
    transition_manager = Instance(TransitionManager)
    
    def start(self):
        with self.gc_lock:
            gc = self.gc
            
            self.max_distance = (gc.width()**2 + gc.height()**2)**0.5
            
            gc.set_fill_color((0.5, 0.5, 0.5))
            gc.draw_rect((0, 0, gc.width(), gc.height()))
            self.last_image = GraphicsContext((gc.width(), gc.height()))        
        super(MouseInteraction, self).start()
        

    def step(self, frame_count):
        from math import pi
        gc = self.gc
        
        mouse_x, mouse_y = self.mouse.position

        x = self.circles['x']
        y = self.circles['y']
        self.circles['radius'] = ((mouse_x-x)**2 + (mouse_y-y)**2)**0.5/self.max_distance * 33
        with gc:
            # grey background
            gc.set_fill_color((0.5, 0.5, 0.5))
            gc.draw_rect((0, 0, gc.width(), gc.height()))

            # draw circles at each grid point
            gc.set_fill_color((1., 1., 1.))
            mouse_x, mouse_y = self.mouse.position
            for circle in self.circles:
                    gc.arc(circle['x'], circle['y'], circle['radius'], 0, 2*pi)
                    gc.draw_path(kiva.constants.FILL)
    
    def _gc_default(self):
        gc = GraphicsContext((256, 256))
        return gc
    
    def _circles_default(self):
        if self.random:
            return self.circle_random()
        else:
            return self.circle_grid()
    
    def _transition_manager_default(self):
        return TransitionManager(heartbeat=self.heartbeat)
    
    def _random_changed(self):
        if self.random:
            circles = self.circle_random()
        else:
            circles = self.circle_grid()
        x_transition = ItemTransition(
            ease = 'ease_in',
            obj = self.circles,
            item = 'x',
            duration = 2.5,
            final = circles['x'],
            priority = 1
        )
        y_transition = ItemTransition(
            ease = 'ease_in',
            obj = self.circles,
            item = 'y',
            duration = 2.5,
            final = circles['y'],
            priority = 1
        )
        self.transition_manager.connect(x_transition)
        self.transition_manager.connect(y_transition)
    
    def circle_grid(self):
        x, y = numpy.mgrid[10:self.gc.width():20,10:self.gc.height():20]
        x.shape = (-1,)
        y.shape = (-1,)
        circles = numpy.empty(shape=(len(x),), dtype=circle_dtype)
        circles['x'] = x
        circles['y'] = y
        return circles
        
    def circle_random(self):
        x, y = numpy.mgrid[10:self.gc.width():20,10:self.gc.height():20]
        x.shape = (-1,)
        n_circles = len(x)
        x = numpy.random.randint(0, self.gc.width(), n_circles)
        y = numpy.random.randint(0, self.gc.height(), n_circles)
        circles = numpy.empty(shape=(n_circles,), dtype=circle_dtype)
        circles['x'] = x
        circles['y'] = y
        return circles
    
    view = View('random')


class MouseView(HasTraits):
    
    start = Button
    
    component = Instance(InteractiveComponent)
    
    context = Instance(MouseInteraction, ())
    
    def _start_fired(self):
        state = self.component.animated_context.heartbeat.state
        if state == 'waiting':
            self.component.animated_context.start()
        elif state == 'paused':
            self.component.animated_context.heartbeat.state = 'running'
        else:
            self.component.animated_context.heartbeat.state = 'paused'
    
    def _component_default(self):
        return InteractiveComponent(animated_context=self.context, bounds=(256,256))
    
    view = View(
        UItem('component', editor=ComponentEditor(height=256, width=256)),
        UItem('context', style='custom'),
        UItem('start'),
        resizable=True,
    )
    
    
if __name__ == '__main__':
    example = MouseView()
    example.configure_traits()
    example.component.animated_context.heartbeat.state = 'stopping'

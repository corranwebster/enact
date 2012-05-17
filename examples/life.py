#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

import numpy

from traits.api import HasTraits, Button, Instance
from traitsui.api import View, UItem
from kiva.image import GraphicsContext
from enable.api import ComponentEditor
from enact.api import AnimatedComponent, AbstractAnimatedContext

class Life(AbstractAnimatedContext):
    
    frame_rate = 60.
    
    def start(self):
        with self.gc_lock:
            gc = self.gc
            self.board = numpy.zeros((gc.width(), gc.height(), 1), dtype='uint8')
            self.board[1:-1,1:-1] = numpy.random.randint(0,2, (gc.width()-2, gc.height()-2, 1))
            self.image_arr = numpy.empty((gc.width(), gc.height(), 3), dtype='uint8')
            self.image_arr[:,:,:] = -self.board
            self.image = GraphicsContext(self.image_arr, pix_format='rgb24')
            with gc:
                gc.draw_image(self.image)
        super(Life, self).start()
    
    def step(self, frame_count):
        neighbours = (
            self.board[:-2,:-2] + self.board[:-2,1:-1] + self.board[:-2,2:] +
            self.board[1:-1,:-2] +                     + self.board[1:-1,2:] +
            self.board[2:,:-2] + self.board[2:,1:-1] + self.board[2:,2:]
        )
        live = ((self.board[1:-1,1:-1] & (neighbours >= 2) & (neighbours <= 3)) |
            ((~self.board[1:-1,1:-1]) & (neighbours == 3)))
        self.board[1:-1,1:-1] = live
        self.image_arr[:] = -self.board

        gc = self.gc
        
        with gc:
            gc.draw_image(self.image)
    
    def _gc_default(self):
        gc = GraphicsContext((512, 512))
        return gc
        
class LifeView(HasTraits):
    
    start = Button
    
    component = Instance(AnimatedComponent)
    
    context = Instance(Life, ())
    
    def _start_fired(self):
        state = self.component.animated_context.heartbeat.state
        if state == 'waiting':
            self.component.animated_context.start()
        elif state == 'paused':
            self.component.animated_context.heartbeat.state = 'running'
        else:
            self.component.animated_context.heartbeat.state = 'paused'
    
    def _component_default(self):
        return AnimatedComponent(animated_context=self.context, bounds=(512,512))
    
    view = View(
        UItem('component', editor=ComponentEditor(height=512, width=512)),
        UItem('start'),
        resizable=True,
    )
    
    
if __name__ == '__main__':
    example = LifeView()
    example.configure_traits()
    example.component.animated_context.heartbeat.state = 'stopping'

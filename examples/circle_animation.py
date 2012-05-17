#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

from traits.api import HasTraits, Range, Button, Instance, DelegatesTo
from traitsui.api import View, UItem
from kiva.image import GraphicsContext
from enable.api import ComponentEditor
from enact.api import AnimatedComponent, AbstractAnimatedContext

class CircleAnimation(AbstractAnimatedContext):

    radius = Range(10., 30.)
    
    last_image = Instance(GraphicsContext)

    def start(self):
        with self.gc_lock:
            gc = self.gc
            gc.set_fill_color((0.5, 0.5, 0.5))
            gc.draw_rect((0, 0, gc.width(), gc.height()))
            self.last_image = GraphicsContext((gc.width(), gc.height()))
            with self.last_image:
                self.last_image.draw_image(gc)
        super(CircleAnimation, self).start()
        

    def step(self, frame_count):
        from math import sin, pi
        gc = self.gc
        radius = self.radius
        x = 128
        y = radius + 128 * abs(sin(pi*frame_count/100.))
        
        with gc:
            # grey background
            gc.set_fill_color((0.5, 0.5, 0.5))
            gc.draw_rect((0, 0, gc.width(), gc.height()))

            # copy previous image with alpha
            gc.set_alpha(0.75)
            gc.draw_image(self.last_image)
            gc.set_alpha(1.0)
            
            # draw a circle
            gc.set_fill_color((0.5, 0.5, 0.75))
            gc.set_stroke_color((1.0, 1.0, 1.0))
            gc.arc(x, y, radius, 0, 2*pi)
            gc.draw_path()
        
        with self.last_image:
            self.last_image.draw_image(gc)
    
    def _gc_default(self):
        gc = GraphicsContext((256, 256))
        return gc


class CircleView(HasTraits):
    
    start = Button
    
    component = Instance(AnimatedComponent)
    
    context = Instance(CircleAnimation, ())
    
    radius = DelegatesTo('context')
    
    def _start_fired(self):
        state = self.component.animated_context.heartbeat.state
        if state == 'waiting':
            self.component.animated_context.start()
        elif state == 'paused':
            self.component.animated_context.heartbeat.state = 'running'
        else:
            self.component.animated_context.heartbeat.state = 'paused'
    
    def _component_default(self):
        return AnimatedComponent(animated_context=self.context, bounds=(256,256))
    
    view = View(
        UItem('component', editor=ComponentEditor(height=256, width=256)),
        UItem('radius'),
        UItem('start'),
        resizable=True,
    )
    
    
if __name__ == '__main__':
    example = CircleView()
    example.configure_traits()
    example.component.animated_context.heartbeat.state = 'stopping'

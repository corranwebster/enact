#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

from traits.api import Instance, on_trait_change
from enable.api import Component

from .animated_context import AbstractAnimatedContext

class AnimatedComponent(Component):
    """ An Enable Component that displays an AnimatedContext
    
    The animated context will be stretched to fill the component.
    """
    
    animated_context = Instance(AbstractAnimatedContext)
    
    @on_trait_change('animated_context.updated')
    def context_updated(self):
        self.request_redraw()
    
    def _draw_mainlayer(self, gc, view_bounds=None, mode="normal"):
        # acquire the source gc lock before blitting to prevent animation thread
        # from writing into buffer as we draw
        with self.animated_context.gc_lock:
            source_gc = self.animated_context.gc
            with gc:
                gc.draw_image(source_gc, (0, 0, source_gc.width(),
                    source_gc.height()))
    

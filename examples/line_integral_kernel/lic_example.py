#
# Adapted from Scipy Cookbook Line Integral Convolution
#
#     http://www.scipy.org/Cookbook/LineIntegralConvolution
#
# Originally by A M Archibald
#

import numpy as np

from traits.api import HasTraits, Button, Instance
from traitsui.api import View, UItem
from kiva.image import GraphicsContext
from enable.api import ComponentEditor
from enact.api import AnimatedComponent, AbstractAnimatedContext

import lic_internal

class LineIntegralConvolution(AbstractAnimatedContext):
    
    frame_rate = 30.
    
    def start(self):
        
        width = self.gc.width()/2.
        height = self.gc.height()/2.
        
        vortex_spacing = 0.5
        extra_factor = 2.
        
        a = np.array([1,0])*vortex_spacing
        b = np.array([np.cos(np.pi/3),np.sin(np.pi/3)])*vortex_spacing
        rnv = int(2*extra_factor/vortex_spacing)
        vortices = [n*a+m*b for n in range(-rnv,rnv) for m in range(-rnv,rnv)]
        vortices = [(x,y) for (x,y) in vortices if -extra_factor<x<extra_factor and -extra_factor<y<extra_factor]
        
        
        xs = np.linspace(-1,1,width).astype(np.float32)[None,:]
        ys = np.linspace(-1,1,height).astype(np.float32)[:,None]
        
        self.vectors = np.zeros((width,height,2),dtype=np.float32)
        for (x,y) in vortices:
            rsq = (xs-x)**2+(ys-y)**2
            self.vectors[...,0] +=  (ys-y)/rsq
            self.vectors[...,1] += -(xs-x)/rsq
            
        self.texture = np.random.rand(width,height).astype(np.float32)

        super(LineIntegralConvolution, self).start()
    
    def step(self, frame_count):
        kernellen = 31
        t = frame_count/(16*5.)
        kernel = np.sin(np.arange(kernellen)*np.pi/kernellen)*(1+np.sin(2*np.pi*5*(np.arange(kernellen)/float(kernellen)+t)))

        kernel = kernel.astype(np.float32)

        image1 = lic_internal.line_integral_convolution(self.vectors,
            self.texture, kernel)
        image1.shape = (-1,)
        image = np.digitize(image1, np.linspace(0., 32., 256))
        image.shape = (self.gc.width()/2., self.gc.height()/2., 1)
        
        self.image = np.empty(image.shape[:2]+(3,), dtype='uint8')
        self.image[:,:,:] = image
        
        gc = self.gc
        
        with gc:
            gc.draw_image(self.image, (0, 0, 512, 512))
    
    def _gc_default(self):
        gc = GraphicsContext((512, 512))
        return gc
        
class LineIntegralConvolutionView(HasTraits):
    
    start = Button
    
    component = Instance(AnimatedComponent)
    
    context = Instance(LineIntegralConvolution, ())
    
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
    example = LineIntegralConvolutionView()
    example.configure_traits()
    example.component.animated_context.heartbeat.state = 'stopping'

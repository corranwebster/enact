

from traits.api import Instance
from chaco.api import ArrayPlotData

from .transition import PlotDataTransition
from .transition_manager import TransitionManager
from .package_globals import get_transition_manager

class AnimatedPlotData(ArrayPlotData):
    
    transition_manager = Instance(TransitionManager)
    
    def set_animated(self, name, new_data, ease='linear', duration=1.0):
        transition = PlotDataTransition(
                ease = 'array_'+ease,
                plot_data = self,
                data_key = name,
                duration = duration,
                final = new_data,
        )
        self.transition_manager.connect(transition)
    
    def _transition_manager_default(self):
        transition_manager = get_transition_manager()
        transition_manager.heartbeat
        return transition_manager
        
    


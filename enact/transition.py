#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
import time
import logging

from numpy import clip

from encore.events.api import BaseEventManager, get_event_manager, HeartbeatEvent
from traits.api import HasTraits, Float, Str, Instance, Any, Property, cached_property

from .easing import Easing
from .transition_manager import TransitionManager
from .package_globals import get_transition_manager

logger = logging.getLogger(__name__)


class AbstractTransition(HasTraits):
    
    event_manager = Instance(BaseEventManager)
    
    transition_manager = Instance(TransitionManager)
    
    key = Any
    
    ease = Easing
    
    start_time = Float
    
    duration = Float
    
    state = Str
    
    def start(self):
        self.start_time = time.time()
        self.event_manager.connect(HeartbeatEvent, self.listener,
            filter={'source': self.transition_manager.heartbeat})
        logging.debug('Started transition key="%s"' % repr(self.key))
    
    def stop(self):
        logging.debug('Stopping transition key="%s"' % repr(self.key))
        self.event_manager.disconnect(HeartbeatEvent, self.listener)
    
    def step(self, dt):
        pass
    
    def listener(self, event):
        dt = (event.time-self.start_time)/self.duration
        try:
            result = self.step(clip(dt, 0.0, 1.0))
        except Exception as exc:
            logger.exception(exc)
            result = 'done'
        if dt >= 1.0 or result == 'done':
            self.state = 'done'
            self.transition_manager.disconnect(self.key)
    
    def _event_manager_default(self):
        return get_event_manager()
    
    def _transition_manager_default(self):
        return get_transition_manager()


class AttributeTransition(AbstractTransition):
    
    obj = Any
    
    attr = Str
    
    initial = Any
    
    final = Any
    
    key = Property(Any, depends_on=['obj', 'attr'])
    
    def start(self):
        self.initial = getattr(self.obj, self.attr, None)
        super(AttributeTransition, self).start()
    
    def step(self, dt):
        value = self.ease_(dt, self.initial, self.final)
        setattr(self.obj, self.attr, value)
        return 'continue'
    
    def stop(self):
        super(AttributeTransition, self).stop()
        self.initial = None # drop reference, just in case
        setattr(self.obj, self.attr, self.final)
    
    @cached_property
    def _get_key(self):
        return (self.obj, self.attr)

class PlotDataTransition(AbstractTransition):
    
    plot_data = Any
    
    data_key = Str
    
    initial = Any
    
    final = Any
    
    key = Property(Any, depends_on=['plot_data', 'data_key'])
    
    def start(self):
        self.initial = self.plot_data.get_data(self.data_key)
        super(PlotDataTransition, self).start()
    
    def step(self, dt):
        value = self.ease_(dt, self.initial, self.final)
        self.plot_data.set_data(self.data_key, value)
        return 'continue'

    def stop(self):
        super(PlotDataTransition, self).stop()
        self.initial = None # drop reference, just in case
        if self.state == 'done':
            self.plot_data.set_data(self.data_key, self.final)
    
    @cached_property
    def _get_key(self):
        return (self.plot_data, self.data_key)

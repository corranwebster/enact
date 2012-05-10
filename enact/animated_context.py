#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

import sys
import time
import logging
import threading

from encore.events.api import BaseEventManager, get_event_manager, Heartbeat, \
    HeartbeatEvent
from traits.api import HasTraits, Float, Instance, Event
from kiva.image import GraphicsContext

logger = logging.getLogger(__name__)

if sys.platform == 'win32':
    accurate_time = time.clock
else:
    accurate_time = time.time

class AbstractAnimatedContext(HasTraits):
    
    #: the event manager that we use
    event_manager = Instance(BaseEventManager)
    
    #: the heartbeat for this animation.  Every animation has its own heartbeat.
    heartbeat = Instance(Heartbeat)
    
    #: the frame rate of the animation
    frame_rate = Float(30.)
    
    #: the GraphicsContext we are going to draw into
    gc = Instance(GraphicsContext)
    
    #: an event which is fired whenever the gc is updated
    updated = Event
    
    #: lock for the gc - acquire this to prevent other threads from rendering
    #: into the gc while you are using it
    gc_lock = Instance(threading.RLock, ())
    
    def start(self):
        self.start_time = accurate_time()
        self.heartbeat.serve()
        self.event_manager.connect(HeartbeatEvent, self.listener,
            filter={'source': self.heartbeat})
        logging.debug('Started animation "%s"' % self)
    
    def stop(self):
        logging.debug('Stopping animation "%s"' % self)
        self.event_manager.disconnect(HeartbeatEvent, self.listener)
    
    def step(self, frame_count):
        raise NotImplementedError
    
    def listener(self, event):
        try:
            with self.gc_lock:
                updated = self.step(event.frame)
            self.updated = updated
        except Exception as exc:
            logger.exception(exc)
            self.stop()
            raise
    
    def _event_manager_default(self):
        return get_event_manager()
    
    def _heartbeat_default(self):
        return Heartbeat(interval=1./self.frame_rate,
            event_manager=self.event_manager)
    

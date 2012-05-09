#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

import logging

from encore.events.api import Heartbeat
from traits.api import HasTraits, Dict, Instance

logger = logging.getLogger(__name__)


class TransitionManager(HasTraits):
    
    transitions = Dict
    
    heartbeat = Instance(Heartbeat)

    def connect(self, transition):
        key = transition.key
        if key in self.transitions:
            self.disconnect(key)
        self.transitions[transition.key] = transition
        transition.transition_manager = self
        logging.debug('Connected transition key="%s"' % repr(key))
        transition.start()
    
    def disconnect(self, key):
        transition = self.transitions.pop(key)
        transition.stop()
        logging.debug('Disconnected transition key="%s"' % repr(key))

    def _heartbeat_default(self):
        heartbeat = Heartbeat()
        heartbeat.serve()
        return heartbeat

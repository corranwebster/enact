#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

from traits.api import Int, Enum, Tuple, Instance, Property
from enable.api import Component

from .animated_component import AnimatedComponent
from .interactive_context import AbstractMouseState, AbstractKeyboardState

MouseButton = Enum('left', 'right', 'middle')
ModifierKeys = Enum('shift', 'alt', 'control')


class ComponentMouseState(AbstractMouseState):
    """ Class which tracks the mouse state
    
    Where state is not dynamically queryable, these variables should store the
    values from the most recent mouse event.
    """
    #: the Enable component which the state comes from
    component = Instance(Component)
    
    #: the position of the mouse in context-local coordinates
    position = Property(Tuple(Int, Int))

    def _get_position(self):
        if self.component.window is not None:
            pos = self.component.window.get_pointer_position()
            return self.component.get_relative_coords(*pos)
            

class ComponentKeyboardState(AbstractKeyboardState):
    """ Class which tracks the keyboard state
    
    Where state is not dynamically queryable, these variables should store the
    values from the most recent keyboard event.
    """
    #: the Enable component which the state comes from
    component = Instance(Component)

class InteractiveComponent(AnimatedComponent):
    
    mouse = Instance(AbstractMouseState)

    keyboard = Instance(AbstractKeyboardState)

    def _mouse_default(self):
        mouse = ComponentMouseState(component=self)
        return mouse

    def _keyboard_default(self):
        keyboard = ComponentKeyboardState(component=self)
        return keyboard

    def __init__(self, **kwargs):
        super(InteractiveComponent, self).__init__(**kwargs)
        self.animated_context.mouse = self.mouse
        self.animated_context.keyboard = self.keyboard
        
        
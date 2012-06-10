#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

from traits.api import Int, Enum, Tuple, Instance, Property
from enable.api import Component, MouseEvent, KeyEvent

from .animated_component import AnimatedComponent
from .interactive_context import AbstractMouseState, AbstractKeyboardState, \
    MouseButton, ModifierKeys


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
        else:
            return (0, 0)
            

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
    
    def dispatch(self, event, suffix):
        """ Public method for sending mouse/keyboard events to this interactor.
        Subclasses may override this to customize the public dispatch behavior.
        
        The interactive component introspects the event to update the mouse and
        keyboard state appropriately, but then follows the usual component
        dispatch, so that regular Enable tools may be used with the component.

        Parameters
        ==========
        event : enable.BaseEvent instance
            The event to dispach
        suffix : string
            The type of event that occurred.  See Interactor class docstring
            for the list of possible suffixes.
        
        """
        if isinstance(event, MouseEvent):
            self.mouse.buttons = set(button for button in MouseButton.values
                if getattr(event, button+'_down'))
            self.keyboard.modifiers = set(modifier for modifier in ModifierKeys.values
                if getattr(event, modifier+'_down'))
        elif isinstance(event, KeyEvent):
            self.keyboard.modifiers = set(modifier for modifier in ModifierKeys.values
                if getattr(event, modifier+'_down'))
            if event.event_type == 'character':
                self.keyboard.character = event.character
            elif event.event_type == 'key_pressed':
                self.keyboard.key_code = event.character
            
        self._dispatch_stateful_event(event, suffix)
        
        
        
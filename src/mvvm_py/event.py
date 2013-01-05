

class event(property):
    '''Creates a property that 'holds' an event.
The actual Event is created on demand.'''
    
    def __init__(self, backing_field):
        self.backing_field = '_{0}'.format(backing_field)
        
        def getter(slf):
            if not hasattr(slf, self.backing_field):
                setattr(slf, self.backing_field, Event())
            return getattr(slf, self.backing_field)
        
        def setter(slf, value):
            if not hasattr(slf, self.backing_field) or getattr(slf, self.backing_field) is not value:
                raise ValueError('Cannot assign to an event')
            setattr(slf, self.backing_field, value)
        
        super(event, self).__init__(getter, setter)
    #
#
            

class Event(object):
    '''Creates an event. Event handlers can be added and removed using += and -=
operators. Calling the event will call all registered handlers. Calling an
event that has no handlers simply does nothing.'''
    
    def __init__(self):
        super(Event, self).__init__()
        
        self._handlers = []
    #
    
    def __iadd__(self, handler):
        if not callable(handler):
            raise TypeError('Cannot register a non-callable as event handler')
        self._handlers.append(handler)
        return self
    #
    
    def __isub__(self, handler):
        if handler in self._handlers:
            self._handlers.remove(handler)
        return self
    #
    
    def __call__(self, *args):
        for handler in self._handlers:
            handler(*args)
    #
#
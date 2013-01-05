import inspect
import types
from event import *

from System.Windows.Input import ICommand
from System import EventArgs


class relay_command(property):
    '''Creates a property that 'holds' a RelayCommand.
The actual RelayCommand is created on demand.'''
    
    def __init__(self, execute, can_execute = None, depends_on = None):
        # The name and backing field are determined by ViewModelMetaClass:
        self.name = ''
        self.backing_field = '_'
        
        # Like bindable properties, commands can also rely on other properties. Changing those properties
        # will trigger a CanExecuteChanged event. This relies on the post-processing done in ViewModelMetaClass:
        self._depends_on = [] if depends_on is None else depends_on
        if isinstance(self._depends_on, str):
            self._depends_on = [self._depends_on]
        
        # Commands are read-only, and only create a RelayCommand if an instance doesn't have that command yet:
        def getter(slf):
            try:
                return getattr(slf, self.backing_field)
            except:
                setattr(slf, self.backing_field, RelayCommand(types.MethodType(execute, slf, type(slf)), types.MethodType(can_execute, slf, type(slf)) if can_execute is not None else None))
                return getattr(slf, self.backing_field)
        
        super(relay_command, self).__init__(getter)
    #
#

class RelayCommand(ICommand):
    
    CanExecuteChanged = event('CanExecuteChanged')
    
    def __init__(self, execute, canExecute = None):
        super(RelayCommand, self).__init__()
        
        self._execute = execute
        self._canExecute = canExecute
        
        argumentsCount = len(inspect.getargspec(self._execute).args)
        isBoundMethod = inspect.ismethod(self._execute)
        self._takesArgument = (isBoundMethod and argumentsCount == 2) or (not isBoundMethod and argumentsCount == 1)
    #
    
    def CanExecute(self, parameter):
        if self._canExecute is None:
            return True
        elif self._takesArgument:
            return self._canExecute(parameter)
        else:
            return self._canExecute()
    #
    
    def Execute(self, parameter):
        if self._takesArgument:
            self._execute(parameter)
        else:
            self._execute()
    #
    
    
    def add_CanExecuteChanged(self, value):
        self.CanExecuteChanged += value
    #
    
    def remove_CanExecuteChanged(self, value):
        self.CanExecuteChanged -= value
    #
    
    def OnCanExecuteChanged(self):
        self.CanExecuteChanged(self, EventArgs.Empty)
    #
#
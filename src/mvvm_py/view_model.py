from collections import defaultdict
from relay_command import *
from event import *

from System.ComponentModel import *


class bindable_property(property):
    '''Creates a property that fires PropertyChanged notifications when the setter is called.'''
    
    def __init__(self, get = 'default', set = 'default', depends_on = None, default = None):
        # If no getter and setter method have been given, then use a private field to store the property's value in.
        # The property name is determined by ViewModelMetaClass:
        self.name = ''
        self.backing_field = '_'
        
        # Some (typically read-only) properties depend on others, so when the other property changes, they change as well.
        # Changing a property should also fire a change notification for all depending properties. ViewModelMetaClass
        # makes sure that everything is hooked up later:
        self._depends_on = [] if depends_on is None else depends_on
        if isinstance(self._depends_on, str):
            self._depends_on = [self._depends_on]
        self._related_properties = []
        self._related_commands = []
        
        # Determine the most appropriate getter and setter:
        if get == 'default':
            def getter(slf):
                return getattr(slf, self.backing_field, default)
            #
        else:
            getter = get
        
        if set == 'default':
            def setter(slf, value):
                setattr(slf, self.backing_field, value)
                
                slf.OnPropertyChanged(self.name)
                for related_property in self._related_properties:
                    slf.OnPropertyChanged(related_property)
                for related_command in self._related_commands:
                    getattr(slf, related_command).OnCanExecuteChanged()
            #
        elif set is not None:
            def setter(slf, value):
                set(slf, value)
                
                slf.OnPropertyChanged(self.name)
                for related_property in self._related_properties:
                    slf.OnPropertyChanged(related_property)
                for related_command in self._related_commands:
                    getattr(slf, related_command).OnCanExecuteChanged()
            #
        else:
            setter = set
        
        super(bindable_property, self).__init__(getter, setter)
    #
#


class ViewModelMetaClass(type):
    '''Creates ViewModel classes and post-processes them to ensure that bindable property dependencies work properly.'''
    
    def __init__(cls, name, bases, dct):
        super(ViewModelMetaClass, cls).__init__(name, bases, dct)
        
        # Find all bindable properties in the class and update their dependencies:
        # TODO: Take care of circular dependencies!!!
        bindable_properties = {}
        related_properties = defaultdict(lambda: [])
        related_commands = defaultdict(lambda: [])
        for attribute_name in dir(cls):
            attribute = getattr(cls, attribute_name)
            
            if isinstance(attribute, bindable_property):
                attribute.name = attribute_name
                attribute.backing_field = '_{0}'.format(attribute_name)
                
                bindable_properties[attribute_name] = attribute
                for dependency in attribute._depends_on:
                    related_properties[dependency].append(attribute_name)
            elif isinstance(attribute, relay_command):
                attribute.name = attribute_name
                attribute.backing_field = '_{0}'.format(attribute_name)
                
                for dependency in attribute._depends_on:
                    related_commands[dependency].append(attribute_name)
        
        for name, related_properties in related_properties.items():
            bindable_prop = bindable_properties[name]
            bindable_prop._related_properties = related_properties
        
        for name, related_commands in related_commands.items():
            bindable_prop = bindable_properties[name]
            bindable_prop._related_commands = related_commands
    #
#


class ViewModel(INotifyPropertyChanged):
    __metaclass__ = ViewModelMetaClass
    
    PropertyChanged = event('PropertyChanged')
    
    def __init__(self):
        super(ViewModel, self).__init__()
    #
    
    def add_PropertyChanged(self, value):
        self.PropertyChanged += value
    #
    
    def remove_PropertyChanged(self, value):
        self.PropertyChanged -= value
    #
    
    def OnPropertyChanged(self, propertyName):
        self.PropertyChanged(self, PropertyChangedEventArgs(propertyName))
    #
#

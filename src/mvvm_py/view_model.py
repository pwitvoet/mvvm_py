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
                try:
                    slf._active_setters.append(self.name)
                    setattr(slf, self.backing_field, value)
                    
                    slf.OnPropertyChanged(self.name)
                    slf._handle_related_properties_and_commands(self)
                finally:
                    slf._active_setters.remove(self.name)
            #
        elif set is not None:
            def setter(slf, value):
                try:
                    slf._active_setters.append(self.name)
                    set(slf, value)
                    
                    slf.OnPropertyChanged(self.name)
                    slf._handle_related_properties_and_commands(self)
                finally:
                    slf._active_setters.remove(self.name)
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
        all_related_properties = defaultdict(lambda: [])
        all_related_commands = defaultdict(lambda: [])
        for attribute_name in dir(cls):
            attribute = getattr(cls, attribute_name)
            
            if isinstance(attribute, bindable_property):
                attribute.name = attribute_name
                attribute.backing_field = '_{0}'.format(attribute_name)
                
                bindable_properties[attribute_name] = attribute
                for dependency in attribute._depends_on:
                    all_related_properties[dependency].append(attribute_name)
            elif isinstance(attribute, relay_command):
                attribute.name = attribute_name
                attribute.backing_field = '_{0}'.format(attribute_name)
                
                for dependency in attribute._depends_on:
                    all_related_commands[dependency].append(attribute_name)
        
        for name, related_properties in all_related_properties.items():
            # Circular dependencies cause stack overflows (infinite loops), so they're not allowed:
            assert not cls._has_circular_references(all_related_properties, name), 'bindable property {!r} has a circular dependency'.format(name)
            bindable_prop = bindable_properties[name]
            bindable_prop._related_properties = related_properties
        
        for name, related_commands in all_related_commands.items():
            bindable_prop = bindable_properties[name]
            bindable_prop._related_commands = related_commands
    #
    
    def _has_circular_references(self, related_properties, property_name):
        visited_properties = []
        open_properties = [property_name]

        while len(open_properties) > 0:
            prop_name = open_properties.pop()
            visited_properties.append(prop_name)

            if prop_name in related_properties:
                for related_property in related_properties[prop_name]:
                    if related_property == property_name:
                        return True
                    elif related_property not in visited_properties and related_property not in open_properties:
                        open_properties.append(related_property)

        return False
    #
#


class ViewModel(INotifyPropertyChanged):
    __metaclass__ = ViewModelMetaClass
    
    PropertyChanged = event('PropertyChanged')
    
    def __init__(self):
        super(ViewModel, self).__init__()
        
        # A list of currently active setters is maintained, so duplicate
        # property change notifications can be avoided.
        self._active_setters = []
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
    
    def _handle_related_properties_and_commands(self, property):
        for related_property in property._related_properties:
            if related_property not in self._active_setters:
                self.OnPropertyChanged(related_property)
                self._handle_related_properties_and_commands(getattr(type(self), related_property))
        
        for related_command in property._related_commands:
            getattr(self, related_command).OnCanExecuteChanged()
    #
#
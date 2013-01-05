from event import *

from System.Collections.Specialized import *


class ObservableList(list, INotifyCollectionChanged):
    '''This is a standard list that supports collection change notifications.'''
    
    CollectionChanged = event('CollectionChanged')
    
    def __init__(self, iterable = None):
        if iterable is not None:
            super(ObservableList, self).__init__(iterable)
        else:
            super(ObservableList, self).__init__()
    #
    
    def add_CollectionChanged(self, value):
        self.CollectionChanged += value
    #
    
    def remove_CollectionChanged(self, value):
        self.CollectionChanged -= value
    #
    
    def OnCollectionChanged(self, action, added_index = None, added_items = None, removed_index = None, removed_items = None):
        if action == NotifyCollectionChangedAction.Reset:
            self.CollectionChanged(self, NotifyCollectionChangedEventArgs(action))
        elif action == NotifyCollectionChangedAction.Add:
            self.CollectionChanged(self, NotifyCollectionChangedEventArgs(action, added_items, added_index))
        elif action == NotifyCollectionChangedAction.Remove:
            self.CollectionChanged(self, NotifyCollectionChangedEventArgs(action, removed_items, removed_index))
        elif action == NotifyCollectionChangedAction.Replace:
            self.CollectionChanged(self, NotifyCollectionChangedEventArgs(action, removed_items, added_items, added_index))
        # Move action is not used
    #
    
    
    # ObservableList methods that alter the ObservableList:
    def append(self, obj):
        index = len(self)
        result = super(ObservableList, self).append(obj)
        self.OnCollectionChanged(NotifyCollectionChangedAction.Add, added_index = index, added_items = [obj])
        return result
    #
    
    def extend(self, iterable):
        index = len(self)
        result = super(ObservableList, self).extend(iterable)
        self.OnCollectionChanged(NotifyCollectionChangedAction.Add, added_index = index, added_items = iterable)
        return result
    #
    
    def insert(self, index, obj):
        result = super(ObservableList, self).insert(index, obj)
        self.OnCollectionChanged(NotifyCollectionChangedAction.Add, added_index = index, added_items = [obj])
        return result
    #
    
    def pop(self, index = None):
        result = super(ObservableList, self).pop(index)
        self.OnCollectionChanged(NotifyCollectionChangedAction.Remove, removed_index = index if index is not None else 0, removed_items = [item])
        return result
    #
    
    def remove(self, item):
        # If the list doesn't contain the value, an exception is raised and the collection change notification is never called.
        index = self.index(item)
        result = super(ObservableList, self).remove(item)
        self.OnCollectionChanged(NotifyCollectionChangedAction.Remove, removed_index = index, removed_items = [item])
        return result
    #
    
    def reverse(self):
        result = super(ObservableList, self).reverse()
        self.OnCollectionChanged(NotifyCollectionChangedAction.Reset)
        return result
    #
    
    def sort(self, comp = None, key = None, reverse = False):
        result = super(ObservableList, self).sort(cmp = comp, key = key, reverse = reverse)
        self.OnCollectionChanged(NotifyCollectionChangedAction.Reset)
        return result
    #
    
    def __iadd__(self, iterable):
        index = len(self)
        result = super(ObservableList, self).__iadd__(iterable)
        self.OnCollectionChanged(NotifyCollectionChangedAction.Add, added_index = index, added_items = iterable)
        return result
    #
    
    def __imul__(self, y):
        index = len(self)
        added_items = self * (y - 1)
        result = super(ObservableList, self).__imul__(y)
        self.OnCollectionChanged(NotifyCollectionChangedAction.Add, added_index = index, added_items = added_items)
        return result
    #
    
    def __delitem__(self, index):
        removed_item = self[index]
        result = super(ObservableList, self).__delitem__(index)
        self.OnCollectionChanged(NotifyCollectionChangedAction.Remove, removed_index = index, removed_items = [removed_item])
        return result
    #
    
    def __delslice__(self, i, j):
        removed_items = self[i:j]
        result = super(ObservableList, self).__delslice__(i, j)
        self.OnCollectionChanged(NotifyCollectionChangedAction.Remove, removed_index = i, removed_items = removed_items)
        return result
    #
    
    def __setitem__(self, index, item):
        replaced_item = self[index]
        result = super(ObservableList, self).__setitem__(index, item)
        self.OnCollectionChanged(NotifyCollectionChangedAction.Replace, added_index = index, added_items = [item], removed_index = index, removed_items = [replaced_item])
        return result
    #
    
    def __setslice__(self, i, j, iterable):
        old_items = self[i:j]
        result = super(ObservableList, self).__setslice__(i, j, iterable)
        self.OnCollectionChanged(NotifyCollectionChangedAction.Replace, added_index = i, added_items = iterable, removed_index = i, removed_items = [old_items])
        return result
    #
#

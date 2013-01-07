import clr
import wpf
import dis
from mvvm_py import *

clr.AddReferenceByPartialName("PresentationCore")
clr.AddReferenceByPartialName("PresentationFramework")
clr.AddReferenceByPartialName("WindowsBase")

from System.Windows import Application, Window


class Item(ViewModel):
    def __init__(self, name):
        super(Item, self).__init__()
        
        self.name = name
    #
    
    name = bindable_property()
    surname = bindable_property(default = '')
    age = bindable_property(default = 0)
    
    def _get_full_name(self):
        return '{} {}'.format(self.name, self.surname)
    def _set_full_name(self, full_name):
        parts = full_name.split(' ', 1)
        self.name = '' if len(parts) < 1 else parts[0]
        self.surname = '' if len(parts) < 2 else parts[1]
    full_name = bindable_property(_get_full_name, _set_full_name, depends_on = ['name', 'surname'])
    
    description = bindable_property(lambda self: '{}, {} years old'.format(self.full_name, self.age), None, depends_on = ['full_name', 'age'])
#

class MyWindowViewModel(ViewModel):
    def __init__(self):
        super(MyWindowViewModel, self).__init__()

        self.items = ObservableList()
        self.selected_item = None
        self.message = 'Hello'
    #
    
    
    # Commands:
    def _execute_rename_item_command(self, arg):
        if self.selected_item is not None:
            self.selected_item.name = arg
    #
    
    def _can_execute_rename_item_command(self, arg):
        return self.selected_item is not None
    #
    
    rename_item_command = relay_command(_execute_rename_item_command, _can_execute_rename_item_command, depends_on = ['selected_item'])
    
    add_item_command = relay_command(lambda self: self.items.append(Item('New item #{0}'.format(len(self.items) + 1))))
    delete_item_command = relay_command(lambda self: self.items.remove(self.selected_item), lambda self: self.selected_item is not None, depends_on = 'selected_item')
    sort_items_command = relay_command(lambda self: self.items.sort(key = lambda item: item.name))
    
    
    # Bindable properties:
    def _get_related_message(self):
        item_index = -1
        if self.selected_item is not None:
            item_index = self.items.index(self.selected_item)
        
        return '{0}! ({1})'.format(self.message, item_index)
    #
    
    message = bindable_property()
    related_message = bindable_property(_get_related_message, depends_on = ['message', 'selected_item'])
    selected_item = bindable_property()
#


class MyWindow(Window):
    def __init__(self):
        super(MyWindow, self).__init__()
        
        self.DataContext = MyWindowViewModel()
        self.DataContext.items.extend([Item('A'), Item('B'), Item('C'), Item('D'), Item('E')])
        self.DataContext.selected_item = self.DataContext.items[0]
        self.DataContext.selected_item.PropertyChanged += self.item_property_changed
        
        wpf.LoadComponent(self, 'example.xaml')
    #
    
    def item_property_changed(self, sender, e):
        print e.PropertyName
    #
    
    def button_clicked(self, sender, e):
        self.DataContext.message = 'clicked!'
    #
    
    def text_changed(self, sender, e):
        self.DataContext.message = sender.Text
    #
#

if __name__ == '__main__':
    Application().Run(MyWindow())
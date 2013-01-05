mvvm_py
=======

A small MVVM framework for IronPython and WPF. mvvm_py aims to reduce boilerplate code as much as possible.

Data binding
------------

With mvvm_py, a view model can be as simple as this:
```python
from mvvm_py import *

class PersonViewModel(ViewModel):
    name = bindable_property()
    surname = bindable_property()
```

```bindable_property``` creates a property with a setter that calls ```OnPropertyChanged```.
By default, the actual property values are stored in a hidden field (the name of the property with an underscore appended).
However, custom getters and setters can easily be specified:
```python
    def get_full_name(self):
        return '{0} {1}'.format(self.name, self.surname)
    def set_full_name(self, full_name):
        self.name, self.surname = full_name.split()
   
    full_name = bindable_property(get_full_name, set_full_name, depends_on = ['name', 'surname'])
```
There is no need to call ```OnPropertyChanged``` in the setter, as mvvm_py will take care of that.

Note the last argument, ```depends_on```: when either ```name``` or ```surname``` is set,
a change notification is raised for ```full_name``` as well. This makes it easier to manage 'derived' properties.

*NOTE: currently, mvvm_py does not offer a convenient way to create read-only properties.
Bindable properties created without specifying a setter will use a default setter instead.
You can, of course, use a setter that raises an error.*

Commands
--------

Commands are supported as well:
```python
    def execute_save_command(self):
        pass
   
    save_command = relay_command(execute_save_command)
```

Additionally, commands can take a parameter and a can-execute method can be specified:
```python
   def execute_delete_command(self, arg):
       pass
   def can_execute_delete_command(self, arg):
       return arg is not None
   
   delete_command = relay_command(execute_delete_command, can_execute_delete_command)
```

And, as with bindable properties, commands can also depend on other properties.
This means that whenever one of the specified properties changes, a ```CanExecuteChanged``` event is fired:
```python
    undo_command = relay_command(execute_undo_command, can_execute_undo_command, depends_on = ['name', 'surname'])
```

Observable collections
----------------------

mvvm_py comes with an ```ObservableList``` class.
This class inherits from the standard ```list``` and can be used as such.
It implements the ```INotifyCollectionChanged``` interface, so replacing or removing an item or slice or sorting the list in-place will raise an ```OnCollectionChanged``` event.
This enables views to react to changes.

Comparison with C#
------------------

In C#, assuming similar ```ViewModel``` and ```RelayCommand``` classes, you'd have to write quite a bit more boilerplate code:
```csharp
import MyFavoriteMVVMFramework;

class PersonViewModel : public ViewModel
{
    private string _name;
    public string Name
    {
        get { return _name; }
        set { _name = value; OnPropertyChanged("Name"); }
    }
    
    private string _surname;
    public string Surname
    {
        get { return _surname; }
        set { _surname = value; OnPropertyChanged("Surname"); }
    }
    
    private void ExecuteSaveCommand()
    {
    }
    
    private bool CanExecuteSaveCommand()
    {
        return true;
    }
    
    private RelayCommand _saveCommand;
    public ICommand SaveCommand
    {
        get { return _saveCommand ?? (_saveCommand = new RelayCommand(ExecuteSaveCommand, CanExecuteSaveCommand)); }
    }
}
```

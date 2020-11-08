# Apprototype
This project provide a little basic app prototype with a central application build around
Components.

### A Very simple example :

First we create a new component with it's template data. At it's instantiation the template is used to create the
StateContainer :

```Python
from AbstractApplication import *


class MainComponent(AbstractComponent):
    def __init__(self, root):
        self.data = {
            "counter": 0
        }
        
        super().__init__("Main", root)
```

Then we can add some "Action", "Mutation" or "Listener". Every method called with a _action, _mutation or _listener are
called with a different context. 
They each have a different purpose, Actions are the algorithm, Mutation are used to modify the state and only modify it,
and Listener are used to listen events.

After each action an event is sent, named like "my_method_name_action_listener".
Also, after each mutation an event is sent, named like "my_method_name_mutation_listener".

```Python
    # [...]
    def say_action(self, context, payload):
        print(payload.message)

    def count_message_action(self, context, payload):
        context.commit('Main.add_message', {})

    def add_message_mutation(self, context, payload):
        self.state.counter += 1

    def say_action_listener(self, context, payload):
        context.dispatch('Main.count_message', {})

```
DON'T FORGET TO ADD CONTEXT AND PAYLOAD PARAMETERS EVEN YOU DON'T USE THEM !

After that we can create our application class and put the main component in it.

```Python
# [...]
class Application(AbstractApplication):
    def __init__(self):
        super().__init__()

        self.use(MainComponent)


app = Application()
app.dispatch('Main.say', {'message': 'Hello World !'})
app.dispatch('Main.say', {'message': 'Hello World !'})
app.dispatch('Main.say', {'message': 'Hello World !'})
app.dispatch('Main.say', {'message': 'Hello World !'})

print(app.states.Main.counter)
```

Because we use a namespace string to call methods, you can create as many components as you need and use dispatch in it.

Example : 

```Python
# [...]
class LogComponent(AbstractComponent):
    def __init__(self, root):
        self.data = {
            "logs": []
        }

        super().__init__("Log", root)

    def add_log_action(self, context, payload):
        data_to_log = f'DATA ADDED : {payload.data}'
        context.commit('Log.add_log', {'log': data_to_log})

    def add_log_mutation(self, context, payload):
        self.state.logs.append(payload.log)

    def say_action_listener(self, context, payload):
        context.dispatch('Log.add_log', {'data': payload.message})


class Application(AbstractApplication):
    def __init__(self):
        super().__init__()

        self.use(MainComponent)
        self.use(LogComponent)


app = Application()
app.dispatch('Main.say', {'message': 'Hello World !'})
app.dispatch('Main.say', {'message': 'Hello World !'})
app.dispatch('Main.say', {'message': 'Hello World !'})
app.dispatch('Main.say', {'message': 'Hello World !'})

print(app.states.Main.counter)
print(app.states.Log.logs)
```

You'll see this in console :
```console
Hello World !
Hello World !
Hello World !
Hello World !
4
['DATA ADDED : Hello World !', 'DATA ADDED : Hello World !', 'DATA ADDED : Hello World !', 'DATA ADDED : Hello World !']
```

### About multithreading
There's a little implementation of multithreading, it can be used in two different way. 
But what you have to know is that they don't return any value.

First, use as a single and simple threaded dispatch with :
```Python
app.thread_dispatch('MyCompo.my_action', {'foo': 'bar'})
```

This just create a new temporary thread to execute dispatch.

Or you can use Queued Task Dispatch, with a little more code in instantiation of your app
```Python
class Application(AbstractApplication):
    def __init__(self):
        super().__init__()
    
        # This method create the queue, the lock, the workers and start them
        self.build_parallel_workers() 

        self.use(MainComponent)
        self.use(LogComponent)

app.task_dispatch('MyCompo.my_action', {'foo': 'bar'})
```

Task Dispatch just add your call in Task Queue. When a worker is available, it will execute the task.


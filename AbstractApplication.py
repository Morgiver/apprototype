from threading import *
from pubsub import pub
import sys


def object_container_class_builder(name):
    """
    object_container_class_builder
    This is just a builder to have ObjectContainer with different names
    """
    def constructor(self):
        pass

    def set(self, name, value):
        self.__setattr__(name, value)

    new_class = type(name, (object, ), {
        "__init__": constructor,
        "set": set
    })

    return new_class


Context = object_container_class_builder("Context")
Payload = object_container_class_builder("Payload")
ComponentsContainer = object_container_class_builder("ComponentsContainer")
StateContainer = object_container_class_builder("StateContainer")
ActionsContainer = object_container_class_builder("ActionsContainer")
MutationsContainer = object_container_class_builder("MutationsContainer")
GettersContainer = object_container_class_builder("GettersContainer")


class AbstractComponent:
    """
    AbstractComponent
    At it's creation the component will register all state, actions, getters, mutation and listener
    in the root application (with a namespace to avoid name conflict)
    """
    def __init__(self, component_name, root):
        self.component_name = component_name
        self.state = object_container_class_builder("StateContainer")()

        root.actions.set(self.component_name, ActionsContainer())
        root.mutations.set(self.component_name, MutationsContainer())
        root.getters.set(self.component_name, GettersContainer())

        actions_root = getattr(root.actions, self.component_name)
        mutations_root = getattr(root.mutations, self.component_name)
        getters_root = getattr(root.getters, self.component_name)

        for i in self.data:
            self.state.set(i, self.data[i])

        root.states.set(self.component_name, self.state)

        for method_name in dir(self):
            parts = method_name.split('_action')
            if len(parts) > 1 and len(parts) == 2 and parts[1] == '':
                actions_root.set(method_name, getattr(self, method_name))

            parts = method_name.split('_mutation')
            if len(parts) > 1 and len(parts) == 2 and parts[1] == '':
                mutations_root.set(method_name, getattr(self, method_name))

            parts = method_name.split('_listener')
            if len(parts) > 1 and len(parts) == 2 and parts[1] == '':
                root.on(f'{method_name}', getattr(self, method_name))

            parts = method_name.split('_getters')
            if len(parts) > 1 and len(parts) == 2 and parts[1] == '':
                getters_root.set(method_name, getattr(self, method_name))

    def __getattr__(self, item):
        if hasattr(self, f'{item}_getter'):
            getter = getattr(self, f'{item}_getter')
            return getter()
        else:
            return self.__getattribute__(item)


class AbstractApplication:
    def __init__(self):
        self.components = ComponentsContainer()
        self.states = StateContainer()
        self.actions = ActionsContainer()
        self.mutations = MutationsContainer()
        self.getters = GettersContainer()

    @staticmethod
    def find_method(root, method_namespace):
        """
        Will find a method with a namespace string
        :param root:
        :param method_namespace:
        :return:
        """
        parts = method_namespace.split('.')

        for i in range(len(parts)):
            if hasattr(root, parts[i]):
                root = getattr(root, parts[i])
            else:
                raise AttributeError(f"{parts[i]} doesn't exist in {method_namespace}")

        return root

    @staticmethod
    def build_payload(payload):
        """
        Will build a Payload object from a dict
        :param payload:
        :return:
        """
        if isinstance(payload, Payload):
            return payload

        p = Payload()
        for i in payload:
            p.set(i, payload[i])

        return p

    def build_context(self, c_type):
        """
        Will build a Context object for a specific context type
        :param c_type:
        :return:
        """
        c = Context()
        if c_type == 'mutation':
            c.set('states', self.states)

        if c_type == 'action':
            c.set('states', self.states)
            c.set('dispatch', self.dispatch)
            c.set('commit', self.commit)

        if c_type == 'listener':
            c.set('dispatch', self.dispatch)

        return c

    def dispatch(self, action_name, payload):
        """
        Will execute a specific action with a given namespace action string
        :param action_name:
        :param payload:
        :return:
        """
        payload = self.build_payload(payload)
        name = f'{action_name}_action'

        try:
            action = self.find_method(self.actions, name)
            result_action = action(self.build_context('action'), payload)
            event_name = name.split('.')[1]
            self.emit(f'{event_name}_listener', payload)
            return result_action
        except AttributeError as err:
            self.logger('DISPATCH_ERROR', name, err)
        except TypeError as err:
            self.logger('DISPATCH_ERROR', name, err)
        except:
            self.logger('DISPATCH_ERROR', name, sys.exc_info()[0])

    def threaded_dispatch(self, action_name, payload):
        Thread(target=self.dispatch, args=(action_name, payload)).run()

    def commit(self, mutation_name, payload):
        payload = self.build_payload(payload)
        name = f'{mutation_name}_mutation'

        try:
            mutation = self.find_method(self.mutations, name)
            if mutation:
                mutation(self.build_context('mutation'), payload)
                event_name = name.split('.')[1]
                self.emit(f'{event_name}_listener', payload)
        except AttributeError as err:
            self.logger('COMMIT_ERROR', name, err)
        except TypeError as err:
            self.logger('COMMIT_ERROR', name, err)
        except:
            self.logger('COMMIT_ERROR', name, sys.exc_info()[0])

    def on(self, event_name, callback):
        pub.subscribe(callback, event_name)

    def emit(self, event_name, payload):
        pub.sendMessage(event_name, context=self.build_context('listener'), payload=self.build_payload(payload))

    def logger(self, exc_type, name, error):
        print(f"----- Exception Throwed -----\nError when : [{exc_type}]\nNamed : [{name}]\nInformations :\n{error}\n"
              f"-----------------------------")

    def use(self, component_class):
        component_instance = component_class(self)
        self.components.set(component_instance.component_name, component_instance)
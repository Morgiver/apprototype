import sys
import asyncio
from importlib import import_module
sys.path.append('Components')


class ObjectContainer:
    def __init__(self):
        pass

    def set(self, attr_name, attr_value):
        self.__setattr__(attr_name, attr_value)


class Application:
    def __init__(self, system_arguments=[]):
        self.system_arguments = system_arguments
        self.states = ObjectContainer()
        self.mutations = ObjectContainer()
        self.actions = ObjectContainer()
        self.getters = ObjectContainer()
        self.components = ObjectContainer()
        self._mutations_events = {}

    def namespace(self, type_ns, namespace):
        root = self.states
        if type_ns == 'actions':
            root = self.actions
        elif type_ns == 'getters':
            root = self.getters
        elif type_ns == 'mutations':
            root = self.mutations

        parts = namespace.split('.')

        for i in range(len(parts)):
            if getattr(root, parts[i]):
                root = getattr(root, parts[i])

        return root

    def add_component(self, component_class):
        new_component = component_class(self)
        self.states.set(new_component.name, new_component.state)
        self.mutations.set(new_component.name, new_component.mutations)
        self.actions.set(new_component.name, new_component.actions)
        self.getters.set(new_component.name, new_component.getters)
        self.components.set(new_component.name, new_component)

        return getattr(self.components, new_component.name)

    def commit(self, namespace, value):
        try:
            mutation = self.namespace('mutations', namespace)
            mutation(self.states, value)
        except AttributeError as error:
            self.emit('Commit.AttributeError', error)

        self.emit(namespace, value)

    async def _dispatch(self, namespace, payload):
        action = self.namespace('actions', namespace)
        payload_object = ObjectContainer()

        for key in payload:
            payload_object.__setattr__(key, payload[key])

        context = ObjectContainer()
        context.set("commit", self.commit)
        context.set("states", self.states)
        context.set("dispatch", self._dispatch)

        return await action(context, payload_object)

    def dispatch(self, namespace, payload):
        return asyncio.run(self._dispatch(namespace, payload))

    def load_components(self, components_list=[]):
        for i in range(len(components_list)):
            component_name = components_list[i]
            package = import_module(f"{component_name}")
            component_class = getattr(package, f"{component_name}Component")

            self.add_component(component_class)

    def subscribe(self, mutation, method):
        if mutation not in self._mutations_events:
            self._mutations_events[mutation] = []

        self._mutations_events[mutation].append({"fn": method, "once": False})

    def subscribe_once(self, mutation, method):
        if mutation not in self._mutations_events:
            self._mutations_events[mutation] = []

        self._mutations_events[mutation].append({"fn": method, "once": True})

    def emit(self, event_name, value):
        if event_name in self._mutations_events:
            event = self._mutations_events[event_name]
            for i in range(len(event)):
                event[i]['fn'](value)
                if event[i]['once']:
                    del event[i]

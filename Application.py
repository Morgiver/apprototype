from threading import Thread, Lock
from queue import Queue
import os
import asyncio


class Context:
    def __init__(self):
        pass


class Payload:
    def __init__(self):
        pass


class AbstractComponent:
    def __init__(self, name, root):
        self.name = name
        self.root = root

        self.state = {}
        self.actions = {}
        self.mutations = {}

    async def dispatch(self, namespace, payload=Payload()):
        return await self.root.dispatch(namespace, payload)

    def dispatch_sync(self, namespace, payload=Payload()):
        return self.root.dispatch_sync(namespace, payload)

    def commit(self, namespace, payload=Payload()):
        self.root.commit(namespace, payload)

    def on(self, event_name, callback):
        self.root.on(event_name, callback)

    def emit(self, event_name, payload=Payload()):
        self.root.emit(event_name, payload)


class Worker(Thread):
    def __init__(self, root, name):
        super().__init__()

        self.name = name
        self.root = root

    def run(self):
        while True:
            self.root.lock.acquire()
            if not self.root.queue.empty():
                namespace, payload = self.root.queue.get()
                self.root.lock.release()
                self.root.dispatch_sync(namespace, payload)
            else:
                self.root.lock.release()


class RootApplication:
    def __init__(self):
        self.states = {}
        self.actions = {}
        self.mutations = {}
        self.events = {}
        self.components = {}

        # Multi Threading Attributes
        self.threads = []
        self.queue = Queue(10)
        self.lock = Lock()

        for i in range(os.cpu_count()-2):
            self.create_worker(f'Thread_{i}')

        for thread in self.threads:
            thread.start()

    def create_worker(self, name):
        new_worker = Worker(self, name)
        self.threads.append(new_worker)

    def add_worker_task(self, namespace, payload={}):
        self.lock.acquire()
        self.queue.put((namespace, payload))
        self.lock.release()

    def get_namespace(self, namespace, _space="actions"):
        parts = namespace.split('.')
        root = getattr(self, _space)

        for i in parts:
            if root[i]:
                root = root[i]

        return root

    @staticmethod
    def build_payload_object(data):
        payload = Payload()
        for i in data:
            payload.__setattr__(i, data[i])
        return payload

    async def dispatch(self, action_name, payload=Payload()):
        action = self.get_namespace(action_name)

        context = Context()
        context.__setattr__("commit", self.commit)
        context.__setattr__("dispatch", self.dispatch)

        self.emit(action_name, payload)

        return await action(context, self.build_payload_object(payload))

    def dispatch_sync(self, action_name, payload=Payload()):
        return asyncio.run(self.dispatch(action_name, payload))

    def dispatch_threaded(self, action_name, payload={}):
        self.add_worker_task(action_name, payload)

    def commit(self, mutation_name, payload=Payload()):
        mutation = self.get_namespace(mutation_name, 'mutations')
        mutation(self.states, self.build_payload_object(payload))
        self.emit(mutation_name, payload)

    def on(self, event_name, callback):
        self.events[event_name] = callback

    def emit(self, event_name, payload=Payload()):
        if event_name in self.events:
            context = Context()
            context.__setattr__("commit", self.commit)
            context.__setattr__("dispatch", self.dispatch)
            context.__setattr__("states", self.states)

            self.events[event_name](context, payload)

    def use(self, component_class):
        if issubclass(component_class, AbstractComponent):
            new_component = component_class(self)
            self.states[new_component.name] = new_component.state
            self.actions[new_component.name] = new_component.actions
            self.mutations[new_component.name] = new_component.mutations
            self.components[new_component.name] = new_component

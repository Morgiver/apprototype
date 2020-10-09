from Application import ObjectContainer


class AbstractComponent:
    def __init__(self, name, root_app):
        self.root_app = root_app
        self.name = name
        self.state = ObjectContainer()
        self.getters = ObjectContainer()
        self.actions = ObjectContainer()
        self.mutations = ObjectContainer()

        self.subscribe('initialization', self.initialization)

    def initialization(self, payload):
        pass

    def commit(self, namespace, value):
        self.root_app.commit(namespace, value)

    def dispatch(self, namespace, payload):
        return self.root_app.dispatch(namespace, payload)

    def subscribe(self, mutation, method):
        self.root_app.subscribe(mutation, method)

    def subscribe_once(self, mutation, method):
        self.root_app.subscribe_once(mutation, method)

    def emit(self, event_name, value):
        self.root_app.emit(event_name, value)


from AbstractApplication import *


class MainComponent(AbstractComponent):
    def __init__(self, root):
        self.data = {
            "counter": 0
        }

        super().__init__("Main", root)

    def say_action(self, context, payload):
        print(payload.message)

    def count_message_action(self, context, payload):
        context.commit('Main.add_message', {})

    def add_message_mutation(self, context, payload):
        self.state.counter += 1

    def say_action_listener(self, context, payload):
        context.dispatch('Main.count_message', {})


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

        self.build_parallel_workers()

        self.use(MainComponent)
        self.use(LogComponent)


app = Application()
app.dispatch('Main.say', {'message': 'Hello World !'})
app.dispatch('Main.say', {'message': 'Hello World !'})
app.dispatch('Main.say', {'message': 'Hello World !'})
app.dispatch('Main.say', {'message': 'Hello World !'})

print(app.states.Main.counter)
print(app.states.Log.logs)

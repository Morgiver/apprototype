
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

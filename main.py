from Application import *


app = Application(sys.argv, ['Main', 'Logger', 'Thread'])
app.run()
app.sync_dispatch('Main.sayHello', {'name': 'Morgiver'})

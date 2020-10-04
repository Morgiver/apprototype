from Application import *


app = Application(sys.argv)
app.load_components(['Main', 'Logger'])
app.sync_dispatch('Main.sayHello', {'name': 'Morgiver'})

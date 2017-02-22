from appJar import gui
import random # temp
import colorsys

# function called by pressing the buttons
def press(btn):
	if btn == "Cancel":
		app.stop()
	if btn == 'Submit':
		print 'User:', app.getEntry('user'), 'Pass:', app.getEntry('pass')
	else:
		app.infoBox('Help', 'Nah dawg, I can\'t help you.')

app = gui('Login Window', '400x400')
app.setBg('white')
app.setFont(14, font='Segoe UI')
app.setTitle('SneakySnake Visualiser')

# app.startLabelFrame('Login Details')
# app.addLabel("user", "Username:", 0, 5)              # Row 0,Column 0
# app.addEntry("user", 0, 1)                           # Row 0,Column 1
# app.addLabel("pass", "Password:", 1, 0)              # Row 1,Column 0
# app.addSecretEntry("pass", 1, 1)                     # Row 1,Column 1
# app.addButtons(["Submit", "Cancel"], press, 2, 0, 2) # Row 2,Column 0,Span 2

# app.setEntryFocus("user")
# app.stopLabelFrame()

# map is an NxN matrix of random values from 0 - 100
N = 20 # temp
map_gradient = [[int(random.random()*100) for i in range(N)] for j in range(N)] # temp
for i in range(N):
	# add walls
	map_gradient[0][i] = 100
	map_gradient[-1][i] = 100
	map_gradient[i][0] = 100
	map_gradient[i][-1] = 100

for i in range(len(map_gradient)):
	for k in range(len(map_gradient)):
		l = map_gradient[i][k]
		title = str(i) + "," + str(k)
		
		hex = '#%02x%02x%02x' % tuple(i * 255 for i in colorsys.hls_to_rgb((l * 1.2) / float(360), 0.6, 0.8)) #interpolate b/w red and green based on l, then convert to hex

		app.addLabel(title, '', i, k)
		app.setLabelBg(title, hex)


app.go()
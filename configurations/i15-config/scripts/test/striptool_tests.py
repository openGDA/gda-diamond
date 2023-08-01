"""To show the view, Window menu > Show Plot views > Diode Trace"""

from localStationScripts.striptool import StriptoolManager, striptool_of
striptool=StriptoolManager()

print "striptool.run(dummy1)"
striptool.run(dummy1)
print "striptool.mark_x_axis()"
plot.mark_x_axis()
sleep(2)
plot.mark_x_axis()
pos dummy1 3
plot.mark_x_axis()
sleep(2)
plot.mark_x_axis()
pos dummy1 0
plot.mark_x_axis()
sleep(2)
plot.mark_x_axis()
print "striptool.stop(dummy1)"
striptool.stop(dummy1)


print "striptool.run(prop)"
striptool.run(prop)
print "striptool.mark_x_axis()"
striptool.mark_x_axis()
print "scan dummy1 1 5 1 w 0.2 striptool.getStriptoolTimeScannable(prop) prop"
scan dummy1 1 5 1 w 0.2 striptool.getStriptoolTimeScannable(prop) prop
print "striptool.stop(prop)"
striptool.stop(prop)

print "Waiting..."
sleep(2)
print "...done"

print "with striptool_of(prop) as plot:"
with striptool_of(prop) as plot:
	# Run the following commands while monitoring the prop counter scannable
	for i in range(5):
		# add a line marking the current time
		print "plot.mark_x_axis()"
		plot.mark_x_axis()
		# Run a scan, waiting for longer between each point for each scan
		print "scan dummy1 1 5+i 1 w 0.2 plot.getStriptoolTimeScannable() prop"
		scan dummy1 1 2+i 1 w 0.2 plot.getStriptoolTimeScannable() prop

print "with striptool_of(dummy1) as plot:"
with striptool_of(dummy1) as plot:
	# Run the following commands while monitoring the prop counter scannable
	for i in range(5):
		plot.mark_x_axis(); sleep(2)
		plot.mark_x_axis(); pos dummy1 3
		plot.mark_x_axis(); sleep(2)
		plot.mark_x_axis(); pos dummy1 0
		plot.mark_x_axis(); sleep(2)
		plot.mark_x_axis()


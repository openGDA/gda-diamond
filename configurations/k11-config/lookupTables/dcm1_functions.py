from math import asin, cos

def y_in(energy):
	return "In"

def pos_bragg(energy):
	return asin(0.4/energy)

def pos_z(energy):
	bragg = pos_bragg(energy)
	return 12.7645 / cos(bragg) - 0.67396215

def pos_roll(energy):
	return 0

def pos_pitch(energy):
	return 0

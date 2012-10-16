/*-
 * Copyright © 2012 Diamond Light Source Ltd.
 *
 * This file is part of GDA.
 *
 * GDA is free software: you can redistribute it and/or modify it under the
 * terms of the GNU General Public License version 3 as published by the Free
 * Software Foundation.
 *
 * GDA is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
 * details.
 *
 * You should have received a copy of the GNU General Public License along
 * with GDA. If not, see <http://www.gnu.org/licenses/>.
 */

package gda.device.scannable;

public class GasInjectionScannablePumpOn {

	// valve pvs
	private String v1pv;
	private String v2pv;
	private String v3pv;
	private String v4pv;
	private String v5pv;
	private String v6pv;
	private String v7pv;
	private String v8pv;
	private String v9pv;

	// pressure gauge pvs
	private String p1pv;
	private String p2pv;
	private String p3pv;
	private String p4pv;
	private String p5pv;

	// pressure controller pvs
	private String pc1pv;
	private String pc2pv;

	
	// #pressure checking
	// for a given pressure gauge, while pumping is occuring, check pressure every 5 seconds, until the difference
	// between two measurements is less than or equal to 1mbar
	// before anything check if there is any bias on the ICs. If there is, ramp it down and wait until it is zero before
	// doing anything else
	// pump is left on all the time that pumping/purging sequences are being run
	private void pressureCheck(String pv){
		
	}
	
	
	// #purge cylinder lines
	// only needed if the gas type has changed since the previous fill
	// check that v1, v2, v3 are closed
	// open v4
	// pressure check p1
	// close v4
	// if Kr
	//     open v1
	//     wait 10s
	//     close v1
	// if N2
	//     open v2
	//     wait 10s
	//     close v2
	// if Ar
	//     open v3
	//     wait 10s
	//     close v3
	// open v4
	// wait 30s
	// close v4
	private void purgeCylinderLines(){
		
	}
	
	
	// #purge I0
	// repeat 3 times
	//     open v5
	//     open v6
	//     cressure check p2
	//     close v5
	//     set pressure controller 2 to 1bar
	//     set pressure controller 2 to control
	//     wait 20s
	//     set pressure controller 2 to hold
	private void purgeI0(){
		
	}
	
	
	// #fill I0
	// open v5
	// open v6
	// pressure check p2
	// close v5
	// set pressure controller 1 to target pressure
	// check v4 is closed
	// if Kr
	//     open v1
	// if N2
	//     open v2
	// if Ar
	//     open v3
	// set mode of pressure controller 1 to control
	// if cp1 or p1 rises, close v1, v2 and v3
	// open v6
	// set pressure controller 1 to hold
	// if Kr
	//     close v1
	// if N2
	//     close v2
	// if Ar
	//     close v3
	private void fillI0(){
		
	}
	
	
	// #purge IC lines
	// open v5
	// pressure check pc2
	// close v5
	// set pc2 to 1bar
	// set pc1 to control
	// wait 10s
	// set pc1 to hold
	// open v5
	// pressure check pc2
	// close v5
	private void purgeIC(){
		
	}
	
	
	// #top up helium
	// set pc2 to 1 bar
	// set pc2 to control
	// open v6
	// wait 20s
	// close v6
	// set pc2 to hold
	private void topupHelium(){
		
	}
	
	
	// #start
	// turn on pump Bl20I-EA-GIR-01:VACP1:CON 'open'
	// purge cylinder lines
	// purge I0
	// fill I0
	// purge IC lines
	// top up helium
	// turn of pump Bl20I-EA-GIR-01:VACP1:CON 'closed'
}

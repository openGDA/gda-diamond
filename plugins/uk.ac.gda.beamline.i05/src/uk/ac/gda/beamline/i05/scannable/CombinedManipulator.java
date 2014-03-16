/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i05.scannable;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableBase;
import gda.device.scannable.corba.impl.ScannableAdapter;
import gda.device.scannable.corba.impl.ScannableImpl;
import gda.factory.FactoryException;
import gda.factory.corba.util.CorbaAdapterClass;
import gda.factory.corba.util.CorbaImplClass;

import java.util.Iterator;
import java.util.List;
import java.util.Vector;

@CorbaAdapterClass(ScannableAdapter.class)
@CorbaImplClass(ScannableImpl.class)
public class CombinedManipulator extends ScannableBase {

	private List<Scannable> scannables = new Vector<Scannable>();
	private CombinedCaculator calculator;
	
	public CombinedCaculator getCalculator() {
		return calculator;
	}

	public void setCalculator(CombinedCaculator calculator) {
		this.calculator = calculator;
	}

	public List<Scannable> getScannables() {
		return new Vector<Scannable>(scannables);
	}

	public void setScannables(List<Scannable> scannables) {
		this.scannables = scannables;
		setupExtraNames();
	}

	@Override
	public void configure() throws FactoryException {
		setInputNames(new String[] {getName()});
		setupExtraNames();
	}
			
	private void setupExtraNames() {
		Vector<String> en = new Vector<String>();
		Vector<String> of = new Vector<String>();
		of.add("%5.3f"); //us
		if (scannables != null) {
			for (Scannable s : scannables) {
				en.add(s.getName());
				of.add("%5.3f");
			}
		}
		setExtraNames(en.toArray(new String[]{}));
		setOutputFormat(of.toArray(new String[]{}));
	}

	@Override
	public boolean isBusy() throws DeviceException {
		for(Scannable s : scannables) {
			if (s.isBusy()) {
				return true;
			}
		}
		return false;
	}
	
	@Override
	public void asynchronousMoveTo(Object position) throws DeviceException {
		Double doublePosition;
		
		if (position instanceof Number) {
			doublePosition = ((Number) position).doubleValue();
		} else {
			doublePosition = Double.valueOf(position.toString());
		}
		
		List<Double> demands = calculator.getDemands(doublePosition, getPositions());
		
		for (Iterator diterator = demands.iterator(), siterator = scannables.iterator(); diterator.hasNext();) {
			((Scannable) siterator.next()).asynchronousMoveTo(diterator.next());
		}
	}
	
	Vector<Double> getPositions() throws DeviceException {
		Vector<Double> pos = new Vector<Double>();
		for (Scannable s : scannables) {
			pos.add((Double) s.getPosition());
		}
		return pos;
	}
	
	@Override
	public Object getPosition() throws DeviceException {
		Vector<Double> pos = getPositions();
		Double rbv = calculator.getRBV(pos);
		pos.insertElementAt(rbv, 0);
		return pos.toArray(new Double[]{});
	}
}
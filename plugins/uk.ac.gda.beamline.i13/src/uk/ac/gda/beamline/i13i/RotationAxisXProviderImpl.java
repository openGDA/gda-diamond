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

package uk.ac.gda.beamline.i13i;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableUtils;
import gda.observable.IObserver;
import gda.observable.ObservableComponent;

import org.springframework.beans.factory.InitializingBean;

import uk.ac.gda.beamline.i13i.views.cameraview.RotationAxisXProvider;

public class RotationAxisXProviderImpl implements RotationAxisXProvider, InitializingBean{
//	private static final Logger logger = LoggerFactory.getLogger(RotationAxisXProviderImpl.class);

	ObservableComponent obsComp = new ObservableComponent();
	public static final String NEWVAL = "NEWVAL";

	Scannable offsetXScannable;
	Scannable sampleStageXScannable;
	Scannable cameraStageXScannable;
	DisplayScaleProvider displayScaleProvider;

	@Override
	public void addIObserver(IObserver anIObserver) {
		obsComp.addIObserver(anIObserver);
	}



	@Override
	public void deleteIObserver(IObserver anIObserver) {
		obsComp.deleteIObserver(anIObserver);
	}

	@Override
	public void deleteIObservers() {
		obsComp.deleteIObservers();
	}





	public Scannable getSampleStageXScannable() {
		return sampleStageXScannable;
	}



	public void setSampleStageXScannable(Scannable sampleStageXScannable) {
		this.sampleStageXScannable = sampleStageXScannable;
	}



	public Scannable getCameraStageXScannable() {
		return cameraStageXScannable;
	}



	public void setCameraStageXScannable(Scannable cameraStageXScannable) {
		this.cameraStageXScannable = cameraStageXScannable;
	}



	public DisplayScaleProvider getDisplayScaleProvider() {
		return displayScaleProvider;
	}



	public void setDisplayScaleProvider(DisplayScaleProvider displayScaleProvider) {
		this.displayScaleProvider = displayScaleProvider;
	}



	public Scannable getOffsetXScannable() {
		return offsetXScannable;
	}



	public void setOffsetXScannable(Scannable offsetXScannable) {
		this.offsetXScannable = offsetXScannable;
	}



	@Override
	public int getRotationAxisX() throws DeviceException {
		double offset = ScannableUtils.getCurrentPositionArray(offsetXScannable)[0];
		double x1 = ScannableUtils.getCurrentPositionArray(sampleStageXScannable)[0];
		double x2 = ScannableUtils.getCurrentPositionArray(cameraStageXScannable)[0];
		double dist = offset+x1-x2;
		return (int) Math.round((dist * displayScaleProvider.getPixelsPerMMInX()));
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		if(offsetXScannable == null){
			throw new Exception("offsetXScannable == null");
		}
		if(sampleStageXScannable == null){
			throw new Exception("sampleStageXScannable == null");
		}
		if(cameraStageXScannable == null){
			throw new Exception("cameraStageXScannable == null");
		}
		if(displayScaleProvider == null){
			throw new Exception("displayScaleProvider == null");
		}
		IObserver observer = new IObserver() {
			
			@Override
			public void update(Object source, Object arg) {
				obsComp.notifyIObservers(RotationAxisXProviderImpl.this, NEWVAL);
			}
		};
		offsetXScannable.addIObserver(observer);
		sampleStageXScannable.addIObserver(observer);
		cameraStageXScannable.addIObserver(observer);
		displayScaleProvider.addIObserver(observer);
	}
	
	
	
}

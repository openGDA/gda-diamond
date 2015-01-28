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

package gda.exafs.ui.composites;

import org.dawnsci.common.richbeans.components.FieldBeanComposite;
import org.dawnsci.common.richbeans.components.scalebox.NumberBox;
import org.dawnsci.common.richbeans.components.scalebox.RangeBox;
import org.dawnsci.common.richbeans.components.scalebox.ScaleBox;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;

public class FurnaceComposite extends FieldBeanComposite {
	private ScaleBox x, y, z;
	private RangeBox temperature;
	private ScaleBox tolerance;
	private ScaleBox time;

	public FurnaceComposite(Composite parent, int style) {
		super(parent, style);
		GridLayout gridLayout = new GridLayout();
		gridLayout.numColumns = 2;
		setLayout(gridLayout);

		Label temperatureLabel = new Label(this, SWT.NONE);
		temperatureLabel.setText("Temperature");

		temperature = new RangeBox(this, SWT.NONE);
		temperature.setMinimum(295);
		temperature.setMaximum(1300);
		temperature.setUnit("K");
		GridData gd_temperature = new GridData(SWT.FILL, SWT.CENTER, true, false);
		temperature.setLayoutData(gd_temperature);

		Label toleranceLabel = new Label(this, SWT.NONE);
		toleranceLabel.setText("Tolerance");

		tolerance = new ScaleBox(this, SWT.NONE);
		GridData gd_tolerance = new GridData(SWT.FILL, SWT.CENTER, true, false);
		tolerance.setLayoutData(gd_tolerance);
		tolerance.setMaximum(5);

		Label timeLabel = new Label(this, SWT.NONE);
		timeLabel.setText("Time");

		time = new ScaleBox(this, SWT.NONE);
		GridData gd_time = new GridData(SWT.FILL, SWT.CENTER, true, false);
		time.setLayoutData(gd_time);
		time.setUnit("s");
		time.setMaximum(400.0);

		Label xLabel = new Label(this, SWT.NONE);
		xLabel.setText("x");

		x = new ScaleBox(this, SWT.NONE);
		x.setMinimum(-15);
		x.setMaximum(15);
		x.setUnit("mm");
		GridData gd_x = new GridData(SWT.FILL, SWT.CENTER, true, false);
		x.setLayoutData(gd_x);

		Label yLabel = new Label(this, SWT.NONE);
		yLabel.setText("y");

		y = new ScaleBox(this, SWT.NONE);
		y.setMinimum(-20.0);
		y.setMaximum(20.0);
		GridData gd_y = new GridData(SWT.FILL, SWT.CENTER, true, false);
		y.setLayoutData(gd_y);
		y.setUnit("mm");

		Label zLabel = new Label(this, SWT.NONE);
		zLabel.setText("z");

		z = new ScaleBox(this, SWT.NONE);
		z.setMinimum(-15);
		z.setMaximum(15);
		GridData gd_z = new GridData(SWT.FILL, SWT.CENTER, true, false);
		z.setLayoutData(gd_z);
		z.setUnit("mm");
	}

	public NumberBox getX() {
		return x;
	}

	public NumberBox getY() {
		return y;
	}

	public NumberBox getZ() {
		return z;
	}

	public NumberBox getTemperature() {
		return temperature;
	}

	public ScaleBox getTolerance() {
		return tolerance;
	}

	public ScaleBox getTime() {
		return time;
	}
	
}
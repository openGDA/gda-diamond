/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.ui.composites;

import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;

import uk.ac.gda.exafs.ui.data.TimeFrame;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;
import uk.ac.gda.richbeans.components.wrappers.SpinnerWrapper;
import uk.ac.gda.richbeans.components.wrappers.TextWrapper;

public class TimeFrameComposite extends Composite {

	private TextWrapper labelWrapper;
	private ScaleBox deadTime;
	private ScaleBox liveTime;
	private SpinnerWrapper lemoIn;
	private SpinnerWrapper lemoOut;

	public TimeFrameComposite(Composite parent, int style) {
		super(parent, style);

		setLayout(new GridLayout(1, false));

		final Composite area = new Composite(this, SWT.NONE);
		area.setLayout(new GridLayout(4, false));
		area.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		Label label = new Label(area, SWT.CENTER );
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("label");
		this.labelWrapper = new TextWrapper(area, SWT.CENTER| SWT.BORDER);
		this.labelWrapper.setLayoutData(getLayout(120));
		
		label = new Label(area, SWT.CENTER);
		label = new Label(area, SWT.CENTER);

		label = new Label(area, SWT.CENTER);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("Dead Time");
		this.deadTime = new ScaleBox(area, SWT.NONE);
		deadTime.setLayoutData(getLayout(100));
		deadTime.setUnit("ms");
		deadTime.setMinimum(0);
		
		label = new Label(area, SWT.CENTER);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("Lemo In");
		this.lemoIn = new SpinnerWrapper(area, SWT.CENTER);
		lemoIn.setLayoutData(getLayout(60));
		lemoIn.setMinimum(0);
		lemoIn.setMaximum(3);
		
		label = new Label(area, SWT.CENTER);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("Live Time");
		this.liveTime = new ScaleBox(area, SWT.NONE);
		liveTime.setLayoutData(getLayout(100));
		liveTime.setUnit("ms");
		liveTime.setMinimum(0);
		
		label = new Label(area, SWT.CENTER);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("Lemo Out");
		this.lemoOut = new SpinnerWrapper(area, SWT.CENTER);
		lemoOut.setLayoutData(getLayout(60));
		lemoOut.setMinimum(0);
		lemoOut.setMaximum(3);
		
		this.pack();
	}

	private GridData getLayout(int i) {
		GridData gd = new GridData(SWT.CENTER, SWT.CENTER, false, false, 1, 1);
		gd.minimumWidth = i;
		gd.widthHint = i;
		return gd;
	}

	public void selectionChanged(TimeFrame selectedBean) {
		if (selectedBean != null) {
			String labelValue = labelWrapper.getText();
			Double deadtime = (Double) deadTime.getValue();
			Double livetime = (Double) liveTime.getValue();
			Integer lemoin = (Integer) lemoIn.getValue();
			Integer lemoout = (Integer) lemoOut.getValue();

			selectedBean.setLabel(labelValue);
			selectedBean.setDeadTime(deadtime);
			selectedBean.setLiveTime(livetime);
			selectedBean.setLemoIn(lemoin);
			selectedBean.setLemoOut(lemoout);
		}
	}

	public TextWrapper getLabel() {
		return labelWrapper;
	}

	public ScaleBox getDeadTime() {
		return deadTime;
	}

	public ScaleBox getLiveTime() {
		return liveTime;
	}

	public SpinnerWrapper getLemoIn() {
		return lemoIn;
	}

	public SpinnerWrapper getLemoOut() {
		return lemoOut;
	}

}

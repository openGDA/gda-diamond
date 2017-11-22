/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.experiment.ui;

import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.layout.LayoutConstants;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.forms.widgets.FormToolkit;

import gda.scan.TurboXasMotorParameters;
import uk.ac.gda.client.UIHelper;

/**
 * Show motor parameters for TurboXasScan in modal dialog box. <p>
 * A suitable warning message about out of range values is show at the top of the box,
 * and parameter value that are out of range are displayed in red.
 */
public class TurboXasMotorParameterInfoDialog extends Dialog {
	private FormToolkit toolkit;
	private TurboXasMotorParameters motorParameters;

	protected TurboXasMotorParameterInfoDialog(Shell parentShell) {
		super(parentShell);
		toolkit = new FormToolkit(parentShell.getDisplay());
	}

	@Override
	public void create() {
        super.create();
	}

	public void setTurboXasMotorParameters(TurboXasMotorParameters turboXasParameters) {
		this.motorParameters = turboXasParameters;
	}

	@Override
	protected Control createDialogArea(Composite parent) {

		// Get system icon and set message appropriate for valid/out of range parameters.
		boolean showWarning = !motorParameters.validateParameters();
		Image img = null;
		String message = "";
        if (showWarning) {
        	message = "Problem found with motor parameters - see values in red.";
        	img = getShell().getDisplay().getSystemImage(SWT.ICON_ERROR);

        } else {
        	message = "Motor parameters OK.";
        	img = getShell().getDisplay().getSystemImage(SWT.ICON_INFORMATION);
        }

        Composite mainComp = (Composite) super.createDialogArea(parent);
        mainComp.setLayout(new GridLayout(1, false));

        Composite iconAndMessageComp = new Composite(mainComp, SWT.NONE);
		iconAndMessageComp.setLayout(new GridLayout(2, false));

        Label imageLabel = new Label(iconAndMessageComp, SWT.NONE);
		imageLabel.setImage(img);

        Label infoLabel = new Label(iconAndMessageComp, SWT.NONE);
        infoLabel.setText(message);

        createMotorParameterInfo(mainComp);

        return mainComp;
	}

    @Override
    protected void configureShell(Shell newShell) {
        super.configureShell(newShell);
        newShell.setText("Motor parameters");
    }

	/**
	 * Add motor parameter information to the parent composite (i.e. list of motor positions, speeds for the scans etc).
	 * Invalid parameters are displayed in red (i.e. motor positions, speeds that are out of range).
	 * @param parent
	 */
	private void createMotorParameterInfo(Composite parent) {

		// Colour of text labels to indicate problematic values
		Color warningColor = parent.getDisplay().getSystemColor(SWT.COLOR_RED);

		String numFormat = "%.5g ";
		String twoNumFormat = "%.5g, %.5g ";

		Composite mainComposite = new Composite(parent, SWT.NONE);
//		mainComposite.setLayout(new GridLayout(2, false));
		GridLayoutFactory.fillDefaults().margins(20, 20).numColumns(2).spacing(30, LayoutConstants.getSpacing().y).applyTo(mainComposite);
		mainComposite.setBackground(parent.getDisplay().getSystemColor(SWT.COLOR_WHITE));

		toolkit.createLabel(mainComposite, "Start, end positions for scan energy range", SWT.FILL);
		toolkit.createLabel(mainComposite, String.format(twoNumFormat, motorParameters.getScanStartPosition(), motorParameters.getScanEndPosition()));

		toolkit.createLabel(mainComposite, "Scan range");
		Label rangeLabel = toolkit.createLabel(mainComposite, String.format(numFormat, motorParameters.getScanPositionRange()));

		toolkit.createLabel(mainComposite, "Scan step size");
		toolkit.createLabel(mainComposite, String.format(numFormat, motorParameters.getPositionStepsize()));

		toolkit.createLabel(mainComposite, "Number of readouts per scan");
		toolkit.createLabel(mainComposite, String.format("%d", motorParameters.getNumReadoutsForScan()));

		for(int i = 0; i<motorParameters.getScanParameters().getNumTimingGroups(); i++) {
			toolkit.createLabel(mainComposite, "Motor scan speed / return speed : timing group "+(i+1));
			motorParameters.setMotorParametersForTimingGroup(i);

			Composite speedComp = toolkit.createComposite(mainComposite);
			speedComp.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
			speedComp.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

			Label speedLabel = toolkit.createLabel(speedComp, String.format(numFormat+" / ", motorParameters.getScanMotorSpeed()));
			Label returnSpeedLabel = toolkit.createLabel(speedComp, String.format(numFormat, motorParameters.getReturnMotorSpeed()));

			if (!motorParameters.validMotorScanSpeed()) {
				speedLabel.setForeground(warningColor);
			}
			if (!motorParameters.validMotorReturnSpeed()) {
				returnSpeedLabel.setForeground(warningColor);
			}
		}

		toolkit.createLabel(mainComposite, "Motor start, end positions (with rampup/down)");
		Label positionLabel = toolkit.createLabel(mainComposite, String.format(twoNumFormat, motorParameters.getStartPosition(), motorParameters.getEndPosition() ));

		toolkit.createLabel(mainComposite, "Velocity ramp distance");
		toolkit.createLabel(mainComposite, String.format(numFormat, motorParameters.getMotorRampDistance()));

		toolkit.createLabel(mainComposite, "Velocity stabilisation distance");
		toolkit.createLabel(mainComposite, String.format(numFormat, motorParameters.getMotorStabilisationDistance()));

		toolkit.createLabel(mainComposite, "Motor max speed");
		toolkit.createLabel(mainComposite, String.format(numFormat, motorParameters.getMotorMaxSpeed()));

		if (!motorParameters.getMotorPositionsWithinLimits()) {
			positionLabel.setForeground(warningColor);
		}

		if (!motorParameters.validMotorScanRange()) {
			rangeLabel.setForeground(warningColor);
		}
	}
}

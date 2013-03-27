/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i13i.ADViewerImpl;

import gda.commandqueue.JythonCommandCommandProvider;
import gda.commandqueue.Queue;
import gda.device.EnumPositioner;

import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beamline.i13i.I13IBeamlineActivator;
import uk.ac.gda.client.CommandQueueViewFactory;
import uk.ac.gda.epics.adviewer.ADController;
import uk.ac.gda.epics.adviewer.composites.MJPeg;
import uk.ac.gda.epics.adviewer.views.ADViewerCompositeFactory;
import uk.ac.gda.epics.adviewer.views.MJPegView;
import uk.ac.gda.tomography.scan.editor.ScanParameterDialog;

public class I13MJPegViewCompositeFactory implements ADViewerCompositeFactory{
	private static final Logger logger = LoggerFactory.getLogger(I13MJPegViewCompositeFactory.class);

	I13MJPegViewInitialiser i13MJPegViewInitialiser;	
	
	public I13MJPegViewCompositeFactory() {
		super();
	}


	@Override
	public Composite createComposite(ADController adController, Composite parent, MJPegView mjPegView, MJPeg mJPeg) {
		if( !(adController instanceof I13ADControllerImpl)){
			throw new IllegalArgumentException("ADController must be of type I13ADControllerImpl");
		}
		final I13ADControllerImpl adControllerImpl = (I13ADControllerImpl)adController;
		Composite c = new Composite(parent, SWT.NONE);
		c.setLayout(new GridLayout(3, false));
		Composite btnLens = new Composite(c, SWT.NONE);
		GridDataFactory.swtDefaults().applyTo(btnLens);
		RowLayout layout = new RowLayout(SWT.VERTICAL);
		layout.center = true;
		btnLens.setLayout(layout);

		LensScannableComposite lensScannableComposite = new LensScannableComposite(btnLens, SWT.NONE);
		lensScannableComposite.setLensScannable((EnumPositioner) adControllerImpl.getLensScannable());
		Button showRotAxis = new Button(btnLens, SWT.PUSH);
		showRotAxis.setText("Show Rotation Axis\n and Beam Center");
		showRotAxis.addSelectionListener(new SelectionAdapter() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				try {
					i13MJPegViewInitialiser.showRotationAxis(true);
					i13MJPegViewInitialiser.showImageMarker(true);
				} catch (Exception e1) {
					logger.error("Error showing rot axis or beam center", e1);
				}
			}
		});

		Button xaxis = new Button(btnLens, SWT.NONE);
		xaxis.setImage(I13IBeamlineActivator.getImageDescriptor("icons/axes.png").createImage());

		adControllerImpl.getStagesCompositeFactory().createComposite(c, SWT.NONE, null);
		Composite btnComp = new Composite(c, SWT.NONE);
		btnComp.setLayout(layout);

		Button showNormalisedImage = new Button(btnComp, SWT.PUSH);
		showNormalisedImage.setText("Get Normalised\nImage...");
		showNormalisedImage.addSelectionListener(new SelectionAdapter() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				Dialog dlg = new Dialog(Display.getCurrent().getActiveShell()) {

					private Text outBeamX;
					private Text exposureTime;

					@Override
					protected void configureShell(Shell newShell) {
						super.configureShell(newShell);
						newShell.setText("Get Normalised Image");
					}

					@Override
					protected Control createDialogArea(Composite parent) {
						Composite cmp = new Composite(parent, SWT.NONE);
						GridDataFactory.fillDefaults().applyTo(cmp);
						cmp.setLayout(new GridLayout(2, false));
						Label lblOutOfBeam = new Label(cmp, SWT.NONE);
						lblOutOfBeam.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
						lblOutOfBeam.setText("Out of beam position/mm");
						outBeamX = new Text(cmp, SWT.BORDER);
						outBeamX.setText("0.0");
						GridData outBeamXLayoutData = new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1);
						outBeamXLayoutData.minimumWidth = 50;
						outBeamX.setLayoutData(outBeamXLayoutData);

						Label lblExposure = new Label(cmp, SWT.NONE);
						lblExposure.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
						lblExposure.setText("Exposure time/s");
						exposureTime = new Text(cmp, SWT.BORDER);
						exposureTime.setText("1.0");
						exposureTime.setLayoutData(outBeamXLayoutData);
						return cmp;
					}

					@Override
					protected void okPressed() {
						final String cmd = String.format(adControllerImpl.getShowNormalisedImageCmd(),
								outBeamX.getText(), exposureTime.getText());
						try {
							Queue queue = CommandQueueViewFactory.getQueue();
							if (queue != null) {
								queue.addToTail(new JythonCommandCommandProvider(cmd, "Running command '" + cmd + "'",
										null));
								CommandQueueViewFactory.showView();
							} else {
								throw new Exception("Queue not found");
							}
						} catch (Exception e1) {
							MJPegView.reportErrorToUserAndLog("Error showing normalised image", e1);
						}
						super.okPressed();
					}

				};
				dlg.open();
			}
		});

		Button openScanDlg = new Button(btnComp, SWT.PUSH);
		openScanDlg.setText("Start a\ntomography scan...");
		openScanDlg.addSelectionListener(new SelectionAdapter() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				ScanParameterDialog scanParameterDialog = new ScanParameterDialog(e.display.getActiveShell());
				scanParameterDialog.setBlockOnOpen(true);
				scanParameterDialog.open();
			}
		});
		
		
		i13MJPegViewInitialiser = new I13MJPegViewInitialiser(adControllerImpl, mJPeg, mjPegView);
		c.addDisposeListener(new DisposeListener() {
			
			@Override
			public void widgetDisposed(DisposeEvent e) {
				if( i13MJPegViewInitialiser != null)
					i13MJPegViewInitialiser.dispose();
			}
		});
		
		return c;

	}
}

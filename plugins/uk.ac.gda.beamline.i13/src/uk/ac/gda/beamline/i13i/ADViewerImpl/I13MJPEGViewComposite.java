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
import gda.device.scannable.DummyUnitsScannable;
import gda.rcp.views.CompositeFactory;
import gda.rcp.views.StageCompositeDefinition;
import gda.rcp.views.StageCompositeFactory;
import gda.rcp.views.TabCompositeFactory;
import gda.rcp.views.TabCompositeFactoryImpl;
import gda.rcp.views.TabFolderCompositeFactory;

import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.StringUtils;

import uk.ac.gda.beamline.i13i.I13IBeamlineActivator;
import uk.ac.gda.client.CommandQueueViewFactory;
import uk.ac.gda.client.tomo.TomoClientActivator;
import uk.ac.gda.epics.adviewer.ADController;
import uk.ac.gda.epics.adviewer.composites.MJPeg;
import uk.ac.gda.epics.adviewer.views.MJPegView;
import uk.ac.gda.tomography.scan.editor.ScanParameterDialog;

public class I13MJPEGViewComposite extends Composite {
	private static final Logger logger = LoggerFactory.getLogger(I13MJPEGViewComposite.class);

	private I13ADControllerImpl adControllerImpl;
	private LensScannableComposite lensScannableComposite;
	private I13MJPegViewInitialiser i13MJPegViewInitialiser;

	private Label lensImageLabel;

	private Button btnVertMoveOnClick;

	private Image sinogram_image;

	private Image normalizedImage_image;

	private MJPeg mJPeg;

	private Button btnHorzMoveOnClick;

	private GridData lensImageLabelGridData;

	private Button btnShowRotAxis;

	public I13MJPEGViewComposite(Composite parent, CompositeFactory cf) throws Exception {
		super(parent, SWT.NONE);
		setLayout(new GridLayout(1, false));
		Composite top = new Composite(this, SWT.NONE);
		top.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, true, false, 1, 1));
		top.setLayout(new GridLayout(2, false));
		Composite c = new Composite(top, SWT.NONE);
		c.setLayout(new GridLayout(1, false));

		if (cf == null) {
			StageCompositeFactory scf = new StageCompositeFactory();
			StageCompositeDefinition[] stageCompositeDefinitions = new StageCompositeDefinition[1];
			StageCompositeDefinition definition = new StageCompositeDefinition();
			stageCompositeDefinitions[0] = definition;
			DummyUnitsScannable scannable = new DummyUnitsScannable("test", 0.0, "mm", "mm");
			scannable.configure();
			definition.setScannable(scannable);
			definition.setStepSize(.1);
			scf.setStageCompositeDefinitions(stageCompositeDefinitions);
			TabFolderCompositeFactory tabs = new TabFolderCompositeFactory();
			TabCompositeFactoryImpl tab = new TabCompositeFactoryImpl();
			tab.setCompositeFactory(scf);
			tab.setLabel("tab");
			tabs.setFactories(new TabCompositeFactory[] { tab });
			tabs.afterPropertiesSet();
			cf = tabs;
		}
		cf.createComposite(c, SWT.NONE);

		Composite composite = new Composite(top, SWT.NONE);
		composite.setLayout(new GridLayout(1, false));
		Composite btnLens = new Composite(composite, SWT.NONE);
		btnLens.setLayout(new GridLayout(2,false));

		lensScannableComposite = new LensScannableComposite(btnLens, SWT.NONE);
		GridDataFactory.swtDefaults().applyTo(lensScannableComposite);
		lensImageLabel = new Label(btnLens, SWT.NONE);
		lensImageLabelGridData = new GridData();
		lensImageLabel.setLayoutData(lensImageLabelGridData);

		Composite composite_1 = new Composite(composite, SWT.NONE);
		composite_1.setLayout(new RowLayout(SWT.HORIZONTAL));

		Button showNormalisedImage = new Button(composite_1, SWT.PUSH);
		showNormalisedImage.setToolTipText("Get Normalised Image");

		Button openScanDlg = new Button(composite_1, SWT.PUSH);
		openScanDlg.setToolTipText("Start a tomography data scan");
		openScanDlg.addSelectionListener(new SelectionAdapter() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				try {
					ScanParameterDialog scanParameterDialog = new ScanParameterDialog(e.display.getActiveShell());
					scanParameterDialog.setBlockOnOpen(true);
					scanParameterDialog.open();
				} catch (Exception ex) {
					logger.error("Error displaying dialog", ex);
				}
			}
		});
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
					protected void createButtonsForButtonBar(Composite parent) {
						// create OK and Cancel buttons by default
						createButton(parent, IDialogConstants.OK_ID, "Run", false);
						createButton(parent, IDialogConstants.CANCEL_ID, IDialogConstants.CANCEL_LABEL, false);
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
		{
			ImageDescriptor desc = TomoClientActivator.getImageDescriptor("icons/normalisedImage.gif");
			if (desc != null) {
				normalizedImage_image = desc.createImage();
				showNormalisedImage.setImage(normalizedImage_image);
			}
			showNormalisedImage.setText("Normalised\nImage...");
		}
		{
			ImageDescriptor desc = TomoClientActivator.getImageDescriptor("icons/sinogram.gif");
			if (desc != null) {
				sinogram_image = desc.createImage();
				openScanDlg.setImage(sinogram_image);
			}
			openScanDlg.setText("Tomography\nScan...");
		}
		btnShowRotAxis = new Button(composite, SWT.CHECK);
		btnShowRotAxis.setText("Show Rotation & Image Axes");
		btnShowRotAxis.addSelectionListener(new SelectionAdapter() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				try {
					showRotationAxis();
				} catch (Exception e1) {
					logger.error("Error showing rot axis or beam center", e1);
				}
			}
		});

		Composite composite_2 = new Composite(this, SWT.NONE);
		composite_2.setLayout(new FillLayout(SWT.HORIZONTAL));
		composite_2.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true, 1, 1));
		mJPeg = new MJPeg(composite_2, SWT.NONE);
		mJPeg.showLeft(true);

		Group grpSampleMoveOn = new Group(composite, SWT.NONE);
		grpSampleMoveOn.setText("Sample Move On Click");
		grpSampleMoveOn.setLayout(new FillLayout(SWT.HORIZONTAL));
		btnVertMoveOnClick = new Button(grpSampleMoveOn, SWT.CHECK);
		btnVertMoveOnClick.setText("Move Vertical");
		btnVertMoveOnClick
				.setToolTipText("When enabled the point clicked on in the image is moved to the rotation axis position");

		btnHorzMoveOnClick = new Button(grpSampleMoveOn, SWT.CHECK);
		btnHorzMoveOnClick.setBounds(0, 0, 93, 20);
		btnHorzMoveOnClick.setText("Move Horizontal");
		btnVertMoveOnClick.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				setVertMoveOnClick();
			}
		});
		btnHorzMoveOnClick.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				setHorzMoveOnClick();
			}
		});

		// i13MJPegViewInitialiser = new I13MJPegViewInitialiser(adControllerImpl, mJPeg, mjPegView);
		addDisposeListener(new DisposeListener() {

			@Override
			public void widgetDisposed(DisposeEvent e) {
				if (i13MJPegViewInitialiser != null)
					i13MJPegViewInitialiser.dispose();
				if (sinogram_image != null) {
					sinogram_image.dispose();
					sinogram_image = null;
				}
				if (normalizedImage_image != null) {
					normalizedImage_image.dispose();
					normalizedImage_image = null;
				}
			}
		});

	}

	protected void setVertMoveOnClick() {
		if (i13MJPegViewInitialiser != null)
			i13MJPegViewInitialiser.setVertMoveOnClick(btnVertMoveOnClick.getSelection());
	}
	protected void setHorzMoveOnClick() {
		if (i13MJPegViewInitialiser != null)
			i13MJPegViewInitialiser.setHorzMoveOnClick(btnHorzMoveOnClick.getSelection());
	}

	protected void showRotationAxis() throws Exception {
		if (i13MJPegViewInitialiser != null) {
			i13MJPegViewInitialiser.showRotationAxis(btnShowRotAxis.getSelection());
			i13MJPegViewInitialiser.showImageMarker(btnShowRotAxis.getSelection());
		}
	}

	public void setADController(ADController adController, MJPegView mjPegView) {
		if (!(adController instanceof I13ADControllerImpl)) {
			throw new IllegalArgumentException("ADController must be of type I13ADControllerImpl");
		}
		adControllerImpl = (I13ADControllerImpl) adController;
		i13MJPegViewInitialiser = new I13MJPegViewInitialiser(adControllerImpl, mJPeg, mjPegView);

		lensScannableComposite.setLensScannable((EnumPositioner) adControllerImpl.getLensScannable());

		try {
			String model_RBV = adController.getAdBase().getModel_RBV();
			if (!StringUtils.isEmpty( model_RBV)) {
				model_RBV = model_RBV.replace(" ", "_");
				model_RBV = model_RBV.replace(".", "_");
				ImageDescriptor imageDescriptor = I13IBeamlineActivator.getImageDescriptor("icons/" + model_RBV
						+ "_axes.png");
				if (imageDescriptor != null) {
					lensImageLabel.setImage(imageDescriptor.createImage());
				} else{
					lensImageLabelGridData.exclude=true;
					lensImageLabel.setVisible(false);
					layout(false);
				}
			}
		} catch (Exception e) {
			logger.error("Error setting up axes image for camera", e);
		}
		mJPeg.setADController(adController);

	}

	public MJPeg getMJPeg() {
		return mJPeg;
	}
}

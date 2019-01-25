/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.view;

import java.util.Map;

import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.ProgressBar;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.dialogs.FilteredTree;
import org.eclipse.ui.dialogs.PatternFilter;

import com.google.common.collect.ImmutableMap;


/**
 * A view to provide DIAD targeted simplified access to Mapping Scan definition
 * for their Diffraction detector.
 */
public class DiffractionScanSelection extends LayoutUtilities {

	private static final Map<String, String> SHAPES_MAP = ImmutableMap.of(
			"icons/point.png", "Select Point scan",
			"icons/square.png", "Select centered Rectangular scan",
			"icons/line.png", "Select centred Line scan");

	private static final Map<String, String> DENSITY_MAP = ImmutableMap.of(
			"High", "Select High Point density",
			"Medium", "Select High Point density",
			"Low", "Select High Point density");

	private static final Map<String, String> MODES_MAP = ImmutableMap.of(
			"Continuous", "Select Continuous scan mode",
			"Snake", "Select Snake scan mode",
			"Random", "Add random offsets to scan points");

	private Composite panelComposite;

	public DiffractionScanSelection() {
	}

	@Override
	public void createPartControl(Composite parent) {
		panelComposite = addGridComposite(parent);
		panelComposite.setBackground(parent.getDisplay().getSystemColor(SWT.COLOR_WHITE));
		buildHeaderComposite(panelComposite);
		buildOuterScanComposite(panelComposite);
		buildDiffractionPathComposite(panelComposite);
		buildSavedComposite(panelComposite);
		buildScanButtonsComposite(panelComposite);

		fillGrab().applyTo(new Label(panelComposite, SWT.SEPARATOR | SWT.HORIZONTAL));
		buildStatusComposite(panelComposite);
	}

	private void buildDiffractionPathComposite(Composite parent) {
		final Composite composite = addGridComposite(parent);
		horizGrab().applyTo(composite);

		new Label(composite, SWT.NONE).setText("Diffraction Scan Path");

		final Composite content = addGridComposite(composite);
		content.setLayout(new GridLayout(4, false));

		buildPathElementComposite(content, "Shape", SHAPES_MAP, SWT.RADIO);
		buildPathElementComposite(content, "Point Density", DENSITY_MAP, SWT.RADIO);
		buildPathElementComposite(content, "Mode(s)", MODES_MAP, SWT.CHECK);

		final Composite selectionComposite = addGridComposite(content);
		fillGrab().indent(30, 0).applyTo(selectionComposite);

		final Button previewButton = new Button(selectionComposite, SWT.CHECK);
		previewButton.setToolTipText("Show your selection on screen");
		previewButton.setText("Preview");

		final StyledText summaryText = new StyledText(selectionComposite, SWT.BORDER);
		final int padding = 15;
		summaryText.setMargins(padding, padding, padding, padding);
		summaryText.setWordWrap(true);
		summaryText.setCaret(null);
		gridGrab().applyTo(summaryText);
		summaryText.setText("Rectangle 5 x 5, center 3, 3\n100 points per side (10000 total)\nStepped Snake");
	}

	private void buildPathElementComposite(final Composite parent, final String title, final Map<String, String> contentMap,  final int buttonStyle) {
		final Composite shapesComposite = addGridComposite(parent);
		new Label(shapesComposite, SWT.NONE).setText(title);

		boolean set = false;
		for(Map.Entry<String, String> entry : contentMap.entrySet()) {
			final Button button = new Button(shapesComposite, buttonStyle);
			button.setToolTipText(entry.getValue());
			if(entry.getKey().startsWith("icons/")) {
				button.setImage(getImage(entry.getKey()));
			} else {
				button.setText(entry.getKey());
			}
			fillGrab().applyTo(button);
			if(buttonStyle == SWT.RADIO && !set){
				set = true;
				button.setSelection(set);
			}
		}
	}

	private void buildSavedComposite(final Composite parent) {
		new Label(parent, SWT.NONE).setText("Saved Scan Definitions");

		final Composite savedComposite = addGridComposite(parent, SWT.BORDER);

		final PatternFilter filter = new PatternFilter();
		final FilteredTree tree = new FilteredTree(savedComposite, SWT.V_SCROLL, filter, true);
		fillGrab().applyTo(tree);

		final TreeViewer viewer = tree.getViewer();
		viewer.setContentProvider(new SavedScansContentProvider());
		viewer.setLabelProvider(new SavedScansLabelProvider());
		viewer.setInput(getViewSite());
	}

	private void buildScanButtonsComposite(final Composite parent) {
		final Composite buttonsComposite = addGridComposite(parent);
		buttonsComposite.setLayout(new GridLayout(3, false));

		final Button runButton = new Button(buttonsComposite, SWT.PUSH);
		runButton.setImage(getImage("icons/control.png"));
		runButton.setText("Run Overall Scan");

		fillGrab().applyTo(new Label(buttonsComposite,SWT.NONE));

		final Button saveButton = new Button(buttonsComposite, SWT.PUSH);
		saveButton.setImage(getImage("icons/save.png"));
	}

	private void buildStatusComposite(final Composite parent) {
		new Label(parent, SWT.NONE).setText("Status");
		final Composite statusContent = addGridComposite(parent);
		statusContent.setLayout(new GridLayout(2, true));

		Label exposureTime = new Label(statusContent, SWT.LEFT);
		exposureTime.setText("ExposureTime: 50ms");
		new Label(statusContent, SWT.LEFT);

		addGrabbingCenteredLabel(statusContent,"Current Diffraction Scan");
		addGrabbingCenteredLabel(statusContent,"Overall");

		final ProgressBar innerBar = new ProgressBar(statusContent, SWT.NONE);
		fillGrab().applyTo(innerBar);
		innerBar.setSelection(20);

		final ProgressBar outerBar = new ProgressBar(statusContent, SWT.NONE);
		outerBar.setSelection(60);
		fillGrab().applyTo(outerBar);

		addGrabbingCenteredLabel(statusContent,"Point 50 of 2000");
		addGrabbingCenteredLabel(statusContent,"Point 12 of 20");
	}

	private void buildOuterScanComposite(Composite parent) {
		final Composite composite = addGridComposite(parent);
		horizGrab().applyTo(composite);

		final Label titleLabel = new Label(composite, SWT.NONE);
		titleLabel.setText("Outer Scan Axis");

		final Composite content = addGridComposite(composite);
		content.setLayout(new GridLayout(4, false));
		horizGrab().applyTo(content);

		final Combo modeCombo = new Combo(content, SWT.READ_ONLY);
		modeCombo.setToolTipText(
				"Select the environmental parameter to vary");
		modeCombo.setItems("Temperature", "Pressure", "Strain", "Energy");
		modeCombo.select(0);
		fillGrab().indent(5, 0).applyTo(modeCombo);

		final Text scanCommandText = new Text(content, SWT.SINGLE | SWT.BORDER);
		gridGrab().applyTo(scanCommandText);
		scanCommandText.setToolTipText("Specify the scan command for the Outer Axis");

		final Button freeTextButton = new Button(content, SWT.CHECK);
		freeTextButton.setSelection(true);
		freeTextButton.setToolTipText(	"Use free text scan entry");
		freeTextButton.setText("Free");

		final Button profileButton = new Button(content, SWT.PUSH);

		profileButton.setToolTipText(	"Load a stored Scan Profile");
		profileButton.setImage(getImage("icons/open.png"));
		noGrab().indent(20, 0).applyTo(profileButton);
	}

	private void buildHeaderComposite(Composite parent) {
		final Composite composite = addGridComposite(parent);
		horizGrab().applyTo(composite);

		final Button freezeImageButton = new Button(composite, SWT.CHECK);
		freezeImageButton.setSelection(false);
		freezeImageButton.setToolTipText(	"Freeze the background live stream on the mapping view");
		freezeImageButton.setText("Freeze Background");
		fillGrab().applyTo(freezeImageButton);
	}

	@Override
	public void setFocus() {
		panelComposite.setFocus();
	}

}

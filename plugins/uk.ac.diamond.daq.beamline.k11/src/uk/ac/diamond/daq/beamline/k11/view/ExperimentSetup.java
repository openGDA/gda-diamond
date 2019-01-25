/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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


import org.eclipse.e4.core.contexts.ContextInjectionFactory;
import org.eclipse.e4.core.contexts.IEclipseContext;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.jface.wizard.WizardDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.graphics.Font;
import org.eclipse.swt.graphics.FontData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.dialogs.FilteredTree;
import org.eclipse.ui.dialogs.PatternFilter;

import uk.ac.diamond.daq.client.gui.camera.CameraConfigurationDialog;
import uk.ac.diamond.daq.experiment.ui.driver.TR6ConfigurationWizard;

/**
 * The main Experiment configuration view visible in all k11 perspectives
 */
public class ExperimentSetup extends LayoutUtilities {

	private static final int NOTES_BOX_LINES = 7;
	private static final int NOTES_BOX_HEIGHT = NOTES_BOX_LINES * 20;
	private static final int REDUCED_BUTTON_HEIGHT = 22;
	private static final int SCROLLABLE_WIDTH = 270;
	private static final int SCROLLABLE_HEIGHT = 900;
	private static final FontData BANNER_FONT_DATA = new FontData("Impact", 20, SWT.NONE);
	private static final int HEADING_SIZE = 14;

	private Composite panelComposite;

	public ExperimentSetup() {
		// TODO Auto-generated constructor stub
	}

	/**
	 * Creates the overall container for all things in the Experiment View tab
	 */
	@Override
	public void createPartControl(Composite parent) {
		parent.setBackground(parent.getDisplay().getSystemColor(SWT.COLOR_WIDGET_LIGHT_SHADOW));

		panelComposite = addGridComposite(parent);

		final Label bannerLabel = new Label(panelComposite, SWT.NONE);
		final Font bannerFont = new Font(bannerLabel.getDisplay(), BANNER_FONT_DATA);
		bannerLabel.setFont(bannerFont);
		bannerLabel.setText("DIAD");

		final Composite experimentComposite = buildExperimentComposite(panelComposite);
		buildModeComposite(experimentComposite);
		buildStageComposite(experimentComposite);
		buildConfigurationComposite(experimentComposite);
		buildPreviousExperimentsComposite(experimentComposite);
		buildFileComposite(experimentComposite);
	}

	/**
	 * Build the main scrolling container that holds the {@link Composite} that holds all the other {@link Composite}s
	 * that control the elements of the experiment
	 *
	 * @param parent	The panel {@link Composite} that covers the whole tab
	 * @return			The created content container within the scrolling panel
	 */
	private Composite buildExperimentComposite(final Composite parent) {

		final ScrolledComposite container = new ScrolledComposite(parent, SWT.H_SCROLL| SWT.V_SCROLL | SWT.BORDER);
		fillGrab().applyTo(container);

		final Composite composite = addGridComposite(container);
		container.setContent(composite);
		container.setExpandHorizontal(true);
		container.setExpandVertical(true);
		container.setMinSize(SCROLLABLE_WIDTH, SCROLLABLE_HEIGHT);                      // When the scroll bars appear

		final Label exptLabel = new Label(composite, SWT.NONE);
		exptLabel.setText("Experiment:");
		final FontData fdData = exptLabel.getFont().getFontData()[0];
		exptLabel.setFont(new Font(composite.getDisplay(), new FontData(fdData.getName(), HEADING_SIZE, SWT.BOLD)));

		final Composite content = addGridComposite(composite);

		final Label nameLabel = new Label(content, SWT.NONE);
		nameLabel.setText("Name:");

		final Text nameText = new Text(content, SWT.SINGLE);
		gridGrab().applyTo(nameText);
		nameText.setToolTipText(
				"Specify a unique name for the Experiment that can be used as an ID to link together its elements");
		nameText.setBackground(composite.getDisplay().getSystemColor(SWT.COLOR_WHITE));

		final Label sampleNameLabel = new Label(content, SWT.NONE);
		sampleNameLabel.setText("Default Sample Name:");

		final Text sampleNameText = new Text(content, SWT.SINGLE);
		gridGrab().applyTo(sampleNameText);
		sampleNameText.setToolTipText("Specify a prefix to add to all named samples");
		sampleNameText.setBackground(composite.getDisplay().getSystemColor(SWT.COLOR_WHITE));

		final Label notesLabel = new Label(content, SWT.NONE);
		notesLabel.setText("Notes:");

		final Text notesText = new Text(content, SWT.MULTI | SWT.WRAP | SWT.V_SCROLL);
		notesText.setToolTipText("Add any notes that should be saved along with other experimental data");
		gridGrab().hint(SWT.DEFAULT, NOTES_BOX_HEIGHT).applyTo(notesText);

		return content;
	}

	/**
	 * Build the {@link Composite} containing controls for selecting the experiment mode
	 *
	 * @param parent	The Experiment {@link Composite}
	 */
	private void buildModeComposite(final Composite parent) {
		final Composite composite = new Composite(parent, SWT.NONE);
		composite.setLayout(new GridLayout());
		horizGrab().applyTo(composite);

		final Label modeLabel = new Label(composite, SWT.NONE);
		modeLabel.setText("Mode:");

		final Combo modeCombo = new Combo(composite, SWT.READ_ONLY);
		modeCombo.setToolTipText(
				"Select the experiment mode to determine the controls and measurement views that will be displayed");
		modeCombo.setItems("Point and Shoot", "Particle Tracking", "Fully Automated", "Plain Tomography");
		modeCombo.select(0);
		fillGrab().indent(5, 0).applyTo(modeCombo);
	}

	/**
	 * Build the {@link Composite} containing controls for selecting the experimental stage
	 *
	 * @param parent	The Experiment {@link Composite}
	 */
	private void buildStageComposite(final Composite parent) {
		final Composite composite = addGridComposite(parent);
		horizGrab().applyTo(composite);

		final Label stageLabel = new Label(composite, SWT.NONE);
		stageLabel.setToolTipText("Select the type of stage to be used in the experiment");
		stageLabel.setText("Stage select:");

		final Composite stageButtonsComposite = new Composite(composite, SWT.NONE);
		stageButtonsComposite.setLayout(new GridLayout(3, true));
		fillGrab().applyTo(stageButtonsComposite);

		final Button environmentStageRadioButton = new Button(stageButtonsComposite, SWT.RADIO);
		environmentStageRadioButton.setSelection(true);
		environmentStageRadioButton.setToolTipText(	"Select the Environmental (e.g. TR6) stage for the experiment");
		environmentStageRadioButton.setText("Env.");
		fillGrab().applyTo(environmentStageRadioButton);
		final Button tomoStageRadioButton = new Button(stageButtonsComposite, SWT.RADIO);
		tomoStageRadioButton.setToolTipText("Select the Tomography (rotational) stage for the experiment");
		tomoStageRadioButton.setText("Tomo.");
		fillGrab().applyTo(tomoStageRadioButton);
		final Button tableStageRadioButton = new Button(stageButtonsComposite, SWT.RADIO);
		tableStageRadioButton.setText("Table");
		tableStageRadioButton.setToolTipText("Select the open Table stage for the experiment");
		fillGrab().applyTo(tableStageRadioButton);
	}

	/**
	 * Build the {@link Composite} containing controls for selecting previous experiment configurations
	 *
	 * @param parent	The Experiment {@link Composite}
	 */
	private void buildPreviousExperimentsComposite(final Composite parent) {
		final Composite composite = addGridComposite(parent);

		final Label exptLabel = new Label(composite, SWT.NONE);
		exptLabel.setText("Previous Experiments:");

		final Composite content = addGridComposite(composite);

		final PatternFilter filter = new PatternFilter();
		final FilteredTree tree = new FilteredTree(content, SWT.V_SCROLL, filter, true);
		fillGrab().applyTo(tree);

		final TreeViewer viewer = tree.getViewer();
		viewer.setContentProvider(new ExperimentTreeContentProvider());
		viewer.setLabelProvider(new ExperimentTreeLabelProvider());
		viewer.setInput(getViewSite());
	}

	/**
	 * Build the {@link Composite} containing controls for selecting the experiment configuration dialogs
	 *
	 * @param parent	The Experiment {@link Composite}
	 */
	private void buildConfigurationComposite(final Composite parent) {
		final Composite composite = addGridComposite(parent);
		horizGrab().applyTo(composite);

		final Label exptLabel = new Label(composite, SWT.NONE);
		exptLabel.setText("Configuration:");

		final Composite content = new Composite(composite, SWT.NONE);
		final GridLayout confLayout = new GridLayout();
		confLayout.verticalSpacing = 0;
		content.setLayout(confLayout);
		fillGrab().applyTo(content);

		addConfigurationDialogButton(content, "Source Adjustment");
		Button button = addConfigurationDialogButton(content, "Imaging Camera");
		button.addListener(SWT.Selection, event -> {
			try {
				CameraConfigurationDialog.show(composite.getDisplay(), getCameraConfiguration(), getLiveStreamConnection());
			} catch (Exception e) {
				log.error("Error opening camera configuration dialog", e);
			}
		});
		addConfigurationDialogButton(content, "Sample Alignment");
		addConfigurationDialogButton(content, "Diffraction Detector");

		addExperimentDriverButton(content);
	}

	private void addExperimentDriverButton(Composite content) {
		Button experimentDriverButton = addConfigurationDialogButton(content, "Environmental Experiment Driver");
		experimentDriverButton.addListener(SWT.Selection, event -> {
			TR6ConfigurationWizard tr6Wizard = ContextInjectionFactory.make(TR6ConfigurationWizard.class, getInjectionContext());
			tr6Wizard.setCalibrationScannableName("tr6_y");
			WizardDialog wizardDialog = new WizardDialog(content.getShell(), tr6Wizard);
			wizardDialog.setPageSize(tr6Wizard.getPreferredPageSize());
			wizardDialog.open();
		});

	}

	private IEclipseContext getInjectionContext() {
		return PlatformUI.getWorkbench().getActiveWorkbenchWindow().getService(IEclipseContext.class);
	}

	/**
	 * Build the {@link Composite} containing controls for loading and saving experiment configurations
	 *
	 * @param parent	The Experiment {@link Composite}
	 */
	private void buildFileComposite(final Composite parent) {

		final Composite composite =  new Composite(parent, SWT.NONE);
		composite.setLayout(new GridLayout(2, true));
		horizGrab().applyTo(composite);
		final Button loadButton = new Button(composite, SWT.PUSH);
		loadButton.setText("Load");
		loadButton.setImage(getImage("icons/open.png"));
		fillGrab().applyTo(loadButton);
		final Button saveButton = new Button(composite, SWT.PUSH);
		saveButton.setText("Save");
		saveButton.setImage(getImage("icons/save.png"));
		fillGrab().applyTo(saveButton);
	}

	/**
	 * Creates a formatted {@link Button} to form part of the Configuration "menu"
	 *
	 * @param parent	The enclosing {@link Composite}
	 * @param label		The label text for the {@link Button}
	 * @return Button   The button on the ConfigurationMenu
	 */
	private Button addConfigurationDialogButton(final Composite parent, final String label) {
		final Button button = new Button(parent, SWT.PUSH);
		fillGrab().hint(SWT.DEFAULT, REDUCED_BUTTON_HEIGHT).applyTo(button);
		button.setToolTipText(String.format("Select the %s configuration dialog", label));
		button.setText(label);
		button.setAlignment(SWT.LEFT);
		return button;
	}

	@Override
	public void setFocus() {
		panelComposite.setFocus();
	}
}


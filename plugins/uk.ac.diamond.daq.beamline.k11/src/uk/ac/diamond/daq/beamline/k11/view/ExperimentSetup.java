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

import java.util.Map;
import java.util.Map.Entry;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.dialogs.MessageDialog;
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
import org.eclipse.ui.IPerspectiveDescriptor;
import org.eclipse.ui.IPerspectiveListener;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.WorkbenchException;
import org.eclipse.ui.dialogs.FilteredTree;
import org.eclipse.ui.dialogs.PatternFilter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.common.collect.ImmutableMap;

import gda.configuration.properties.LocalProperties;
import gda.factory.Finder;
import uk.ac.diamond.daq.client.gui.camera.CameraConfigurationDialog;
import uk.ac.diamond.daq.client.gui.camera.DiffractionConfigurationDialog;
import uk.ac.diamond.daq.client.gui.camera.samplealignment.SampleAlignmentDialog;
import uk.ac.diamond.daq.experiment.api.ExperimentService;
import uk.ac.diamond.daq.experiment.ui.driver.ExperimentDriverWizard;
import uk.ac.diamond.daq.stage.StageException;
import uk.ac.diamond.daq.stage.StageGroupService;
import uk.ac.gda.client.live.stream.LiveStreamConnection;
import uk.ac.gda.client.live.stream.view.CameraConfiguration;
import uk.ac.gda.client.live.stream.view.StreamType;
import uk.ac.gda.tomography.controller.TomographyControllerException;
import uk.ac.gda.tomography.model.TomographyScanParameters;
import uk.ac.gda.tomography.scan.editor.ITomographyEditorController;
import uk.ac.gda.tomography.scan.editor.TomographyConfigurationController;
import uk.ac.gda.tomography.scan.editor.TomographySWTElements;
import uk.ac.gda.tomography.scan.editor.view.TomographyMessages;
import uk.ac.gda.tomography.service.TomographyServiceException;

/**
 * The main Experiment configuration view visible in all k11 perspectives
 */
public class ExperimentSetup extends LayoutUtilities {
	private static final Logger logger = LoggerFactory.getLogger(ExperimentSetup.class);

	private TomographyConfigurationController tomographyConfigurationController;

	private static final Map<String, String> PERSPECTIVES_MAP = ImmutableMap.of("Point and Shoot",
			"uk.ac.diamond.daq.beamline.k11.perspective.PointAndShootPerspective", "Particle Tracking",
			"uk.ac.diamond.daq.beamline.k11.perspective.PointAndShootPerspective", "Fully Automated",
			"uk.ac.diamond.daq.beamline.k11.perspective.FullyAutomatedPerspective", "Plain Tomography",
			"uk.ac.diamond.daq.beamline.k11.perspective.TomographyPerspective");

	private static final int NOTES_BOX_LINES = 7;
	private static final int NOTES_BOX_HEIGHT = NOTES_BOX_LINES * 20;
	private static final int REDUCED_BUTTON_HEIGHT = 22;
	private static final int SCROLLABLE_WIDTH = 270;
	private static final int SCROLLABLE_HEIGHT = 900;
	private static final FontData BANNER_FONT_DATA = new FontData("Impact", 20, SWT.NONE);
	private static final int HEADING_SIZE = 14;

	private static final String ENVIRONMENT_STAGE = "TR6";
	private static final String TOMOGRAPHY_STAGE = "Tomography";
	private static final String TABEL_STAGE = "Platform";

	private final StageGroupService stageGroupService;
	private final ExperimentService experimentService;
	private final DataBindingContext dbc = new DataBindingContext();
	private final IWorkbench workbench = PlatformUI.getWorkbench();
	private final IWorkbenchWindow activeWindow = workbench.getActiveWorkbenchWindow();

	private Composite panelComposite;
	private Text nameText;
	private String mode = "Point and Shoot";

	public ExperimentSetup() {
		stageGroupService = Finder.getInstance().find("diadStageGroupService");
		experimentService = Finder.getInstance().findSingleton(ExperimentService.class);
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
		buildFileComposite(TomographySWTElements.createComposite(experimentComposite, SWT.NONE, 3));
	}

	/**
	 * Build the main scrolling container that holds the {@link Composite} that holds all the other {@link Composite}s
	 * that control the elements of the experiment
	 *
	 * @param parent
	 *            The panel {@link Composite} that covers the whole tab
	 * @return The created content container within the scrolling panel
	 */
	private Composite buildExperimentComposite(final Composite parent) {
		final ScrolledComposite container = new ScrolledComposite(parent, SWT.H_SCROLL | SWT.V_SCROLL | SWT.BORDER);
		fillGrab().applyTo(container);

		final Composite composite = addGridComposite(container);
		container.setContent(composite);
		container.setExpandHorizontal(true);
		container.setExpandVertical(true);
		container.setMinSize(SCROLLABLE_WIDTH, SCROLLABLE_HEIGHT); // When the scroll bars appear

		final Label exptLabel = new Label(composite, SWT.NONE);
		exptLabel.setText("Experiment:");
		final FontData fdData = exptLabel.getFont().getFontData()[0];
		exptLabel.setFont(new Font(composite.getDisplay(), new FontData(fdData.getName(), HEADING_SIZE, SWT.BOLD)));

		final Composite content = addGridComposite(composite);

		final Label nameLabel = new Label(content, SWT.NONE);
		nameLabel.setText("Name:");

		nameText = new Text(content, SWT.SINGLE);
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
	 * @param parent
	 *            The Experiment {@link Composite}
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

		bindModeCombo(modeCombo);

		String perspectiveID = activeWindow.getActivePage().getPerspective().getId();
		setModeComboSelection(perspectiveID, modeCombo);

		activeWindow.addPerspectiveListener(new IPerspectiveListener() {
			@Override
			public void perspectiveChanged(IWorkbenchPage page, IPerspectiveDescriptor perspective, String changeId) {
				// Do nothing
			}

			/**
			 * Updates the Mode combo box when a perspective switch is triggered by another control
			 */
			@Override
			public void perspectiveActivated(IWorkbenchPage page, IPerspectiveDescriptor perspective) {
				if (!PERSPECTIVES_MAP.get(mode).equals(perspective.getId())) {
					setModeComboSelection(perspective.getId(), modeCombo);
				}
			}
		});
	}

	@SuppressWarnings("unchecked")
	private void bindModeCombo(final Combo modeCombo) {
		dbc.bindValue(WidgetProperties.selection().observe(modeCombo), BeanProperties.value("mode").observe(this));
	}

	/**
	 * Updates the mode selector combo with the new perspective Id provided is its a DIAD one
	 *
	 * @param perspectiveId
	 *            The id of the newly activated perspective
	 */
	private void setModeComboSelection(final String perspectiveId, final Combo modeCombo) {
		if (PERSPECTIVES_MAP.containsValue(perspectiveId)) {
			for (Entry<String, String> entry : PERSPECTIVES_MAP.entrySet()) {
				if (perspectiveId.equals(entry.getValue())) {
					mode = entry.getKey();
					modeCombo.setText(mode);
					break;
				}
			}
		}
	}

	/**
	 * Build the {@link Composite} containing controls for selecting the experimental stage
	 *
	 * @param parent
	 *            The Experiment {@link Composite}
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
		environmentStageRadioButton.setToolTipText("Select the Environmental (e.g. TR6) stage for the experiment");
		environmentStageRadioButton.setText("Env.");
		environmentStageRadioButton.addListener(SWT.Selection, e -> changeStageGroup(ENVIRONMENT_STAGE));
		fillGrab().applyTo(environmentStageRadioButton);
		final Button tomoStageRadioButton = new Button(stageButtonsComposite, SWT.RADIO);
		tomoStageRadioButton.setToolTipText("Select the Tomography (rotational) stage for the experiment");
		tomoStageRadioButton.setText("Tomo.");
		tomoStageRadioButton.addListener(SWT.Selection, e -> changeStageGroup(TOMOGRAPHY_STAGE));
		fillGrab().applyTo(tomoStageRadioButton);
		final Button tableStageRadioButton = new Button(stageButtonsComposite, SWT.RADIO);
		tableStageRadioButton.setText("Table");
		tableStageRadioButton.setToolTipText("Select the open Table stage for the experiment");
		tableStageRadioButton.addListener(SWT.Selection, e -> changeStageGroup(TABEL_STAGE));
		fillGrab().applyTo(tableStageRadioButton);

		String stageGroup = stageGroupService.currentStageGroup();
		if (ENVIRONMENT_STAGE.contentEquals(stageGroup)) {
			environmentStageRadioButton.setSelection(true);
		} else if (TOMOGRAPHY_STAGE.equals(stageGroup)) {
			tomoStageRadioButton.setSelection(true);
		} else if (TABEL_STAGE.equals(stageGroup)) {
			tableStageRadioButton.setSelection(true);
		}
	}

	private void changeStageGroup(String stageGroupName) {
		try {
			stageGroupService.changeStageGroup(stageGroupName);
		} catch (StageException e) {
			MessageDialog.openError(panelComposite.getShell(), "Error changes stage",
					"Unknown stage of " + stageGroupName);
		}
	}

	/**
	 * Build the {@link Composite} containing controls for selecting previous experiment configurations
	 *
	 * @param parent
	 *            The Experiment {@link Composite}
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
	 * @param parent
	 *            The Experiment {@link Composite}
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
				CameraConfigurationDialog.show(composite.getDisplay(), getLiveStreamConnection());
			} catch (Exception e) {
				logger.error("Error opening camera configuration dialog", e);
			}
		});
		button = addConfigurationDialogButton(content, "Sample Alignment");
		button.addListener(SWT.Selection, event -> {
			try {
				SampleAlignmentDialog.show(composite.getDisplay(), getLiveStreamConnection());
			} catch (Exception e) {
				MessageDialog.openError(panelComposite.getShell(), "Error",
						"Error opening sample alignment dialog" + "see log for details");
				logger.error("Error opening sample alignment dialog", e);
			}
		});
		button = addConfigurationDialogButton(content, "Diffraction Detector");
		button.addListener(SWT.Selection, event -> {
			try {
				DiffractionConfigurationDialog.show(composite.getDisplay(), getLiveStreamConnection());
			} catch (Exception e) {
				logger.error("Error opening diffrcation configuration dialog", e);
			}
		});

		addExperimentDriverButton(content);
		buildTomographyConfigurationDialog(content, composite);
	}

	private void buildTomographyConfigurationDialog(Composite content, Composite composite) {
		Button button = addConfigurationDialogButton(content, "Tomography Setup");
		button.addListener(SWT.Selection, event -> {
			try {
				if (getTomographyConfigurationController().getData() == null) {
					getTomographyConfigurationController().createNewData();
				}
				getTomographyConfigurationController().showConfigurationDialog(composite.getDisplay());
			} catch (Exception e) {
				logger.error("TODO put description of error here", e);
			}
		});
	}

	/**
	 * Returns, or instantiates if <code>null</code>, the controller associated with the tomography configuration
	 *
	 * @return
	 * @throws TomographyServiceException
	 */
	private ITomographyEditorController<TomographyScanParameters> getTomographyConfigurationController()
			throws TomographyServiceException {
		if (tomographyConfigurationController == null) {
			synchronized (BANNER_FONT_DATA) {
				if (tomographyConfigurationController == null) {
					tomographyConfigurationController = new TomographyConfigurationController();
				}
			}
		}
		return tomographyConfigurationController;
	}

	private LiveStreamConnection getLiveStreamConnection() {
		return new LiveStreamConnection(getCameraConfiguration(), StreamType.EPICS_ARRAY);
	}

	private CameraConfiguration getCameraConfiguration() {
		String cameraName = LocalProperties.get("imaging.camera.name");
		return Finder.getInstance().find(cameraName);
	}

	private void addExperimentDriverButton(Composite content) {
		Button experimentDriverButton = addConfigurationDialogButton(content, "Environmental Experiment Driver");
		experimentDriverButton.addListener(SWT.Selection, event -> {
			ExperimentDriverWizard driverWizard = new ExperimentDriverWizard(experimentService, nameText.getText());
			WizardDialog wizardDialog = new WizardDialog(content.getShell(), driverWizard);
			wizardDialog.setPageSize(driverWizard.getPreferredPageSize());
			wizardDialog.open();
		});
	}

	/**
	 * Build the {@link Composite} containing controls for loading and saving experiment configurations
	 *
	 * @param parent
	 *            The Experiment {@link Composite}
	 */
	private void buildFileComposite(final Composite parent) {
		Button load = TomographySWTElements.createButton(parent, TomographyMessages.LOAD, SWT.PUSH);
		load.setImage(getImage("icons/open.png"));
		Button save = TomographySWTElements.createButton(parent, TomographyMessages.SAVE, SWT.PUSH);
		save.setImage(getImage("icons/save.png"));
		Button run = TomographySWTElements.createButton(parent, TomographyMessages.RUN, SWT.PUSH);
		run.setImage(getImage("icons/run_small.png"));

		// THIS IS JUST A STUB UNTIL ARE AVAILABLE OTHER CONTRLLLERS (DIFFRACTION/IMAGING/OTHER...)
		run.addListener(SWT.Selection, event -> {
			try {
				getTomographyConfigurationController().runAcquisition();
			} catch (TomographyControllerException | TomographyServiceException e) {
				logger.error("TODO put description of error here", e);
			}
		});
	}

	/**
	 * Creates a formatted {@link Button} to form part of the Configuration "menu"
	 *
	 * @param parent
	 *            The enclosing {@link Composite}
	 * @param label
	 *            The label text for the {@link Button}
	 * @return Button The button on the ConfigurationMenu
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

	public String getMode() {
		return mode;
	}

	public void setMode(String mode) {
		this.mode = mode;
		try {
			String id = PERSPECTIVES_MAP.get(mode);
			workbench.showPerspective(id, activeWindow);
		} catch (WorkbenchException e) {
			logger.error("Could get get perspective for mode {} ", mode, e);
		}
	}
}

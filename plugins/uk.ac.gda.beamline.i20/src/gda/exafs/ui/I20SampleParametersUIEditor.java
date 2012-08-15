/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package gda.exafs.ui;

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.exafs.ui.composites.CryostatComposite;
import gda.exafs.ui.composites.CustomParameterComposite;
import gda.exafs.ui.composites.CustomXYZParameterComposite;
import gda.exafs.ui.composites.FurnaceComposite;
import gda.exafs.ui.composites.MicroreactorParametersComposite;
import gda.exafs.ui.composites.RoomTemperatureComposite;
import gda.exafs.ui.preferencepages.I20SampleReferenceWheelPreferencePage;
import gda.factory.Finder;
import gda.observable.IObserver;

import java.net.URL;
import java.util.Arrays;
import java.util.List;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.preference.PreferenceDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.custom.StackLayout;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Link;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.dialogs.PreferencesUtil;
import org.eclipse.ui.forms.events.ExpansionAdapter;
import org.eclipse.ui.forms.events.ExpansionEvent;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.slf4j.Logger;

import uk.ac.gda.beans.exafs.i20.CryostatParameters;
import uk.ac.gda.beans.exafs.i20.CustomParameter;
import uk.ac.gda.beans.exafs.i20.CustomXYZParameter;
import uk.ac.gda.beans.exafs.i20.FurnaceParameters;
import uk.ac.gda.beans.exafs.i20.I20SampleParameters;
import uk.ac.gda.beans.exafs.i20.MicroreactorParameters;
import uk.ac.gda.beans.exafs.i20.SampleStageParameters;
import uk.ac.gda.exafs.ui.data.ScanObjectManager;
import uk.ac.gda.richbeans.components.FieldComposite.NOTIFY_TYPE;
import uk.ac.gda.richbeans.components.selector.VerticalListEditor;
import uk.ac.gda.richbeans.components.wrappers.BooleanWrapper;
import uk.ac.gda.richbeans.components.wrappers.ComboWrapper;
import uk.ac.gda.richbeans.components.wrappers.TextWrapper;
import uk.ac.gda.richbeans.editors.DirtyContainer;
import uk.ac.gda.richbeans.editors.RichBeanEditorPart;
import uk.ac.gda.richbeans.event.ValueAdapter;
import uk.ac.gda.richbeans.event.ValueEvent;
import uk.ac.gda.richbeans.event.ValueListener;

public class I20SampleParametersUIEditor extends RichBeanEditorPart {

	private static final Logger logger = org.slf4j.LoggerFactory.getLogger(I20SampleParametersUIEditor.class);

	private Composite mainComp;
	private ComboWrapper cmbSampleEnv;
	private ScrolledComposite scrolledComposite;
	private ComboWrapper sampleWheelPosition;
	private TextWrapper descriptions;
	private TextWrapper name;
	private RoomTemperatureComposite sampleStageParameters;
	private CryostatComposite cryostatParameters;
	private FurnaceComposite furnaceParameters;
	private MicroreactorParametersComposite microreactorParameters;
	private VerticalListEditor customParameters;
	private VerticalListEditor customXYZParameters;

	private SelectionAdapter selectionListener;

	private Link elementLabel;

	private Composite complexTypesTemp;

	private StackLayout stackLayoutTemp;

	private Composite blankTempComposite;

	private BooleanWrapper useSampleWheel;

	private TextWrapper sampleName;

	public I20SampleParametersUIEditor(String path, URL mappingURL, DirtyContainer dirtyContainer, Object editingBean) {
		super(path, mappingURL, dirtyContainer, editingBean);
	}

	@Override
	protected String getRichEditorTabText() {
		return "Sample";
	}

	@Override
	public void createPartControl(final Composite parent) {

		parent.setLayout(new FillLayout());

		this.scrolledComposite = new ScrolledComposite(parent, SWT.H_SCROLL | SWT.V_SCROLL);
		scrolledComposite.setExpandHorizontal(true);
		scrolledComposite.setExpandVertical(true);

		this.mainComp = new Composite(scrolledComposite, SWT.NONE);
		GridLayout gridLayout = new GridLayout();
		gridLayout.numColumns = 1;
		mainComp.setLayout(gridLayout);

		final Composite composite = new Composite(mainComp, SWT.NONE);
		gridLayout = new GridLayout();
		gridLayout.numColumns = 1;
		composite.setLayout(gridLayout);

		createSampleDetailsGroup(composite);

		createSampleEnvironmentGroup(composite);

		if (!ScanObjectManager.isXESOnlyMode()) {
			createSampleWheelGroup(composite);
		}

		scrolledComposite.setContent(mainComp);
		mainComp.layout();
		scrolledComposite.setMinSize(mainComp.computeSize(SWT.DEFAULT, SWT.DEFAULT));
	}

	private void createSampleWheelGroup(final Composite composite) {

		final EnumPositioner sampleWheel = Finder.getInstance().find(I20SampleParameters.SAMPLE_WHEEL_NAME);

		if (sampleWheel != null) {
			sampleWheel.addIObserver(new IObserver() {
				@Override
				public void update(Object source, Object arg) {
					if (arg instanceof String[]) {
						final String[] positions = (String[]) arg;
						PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
							@Override
							public void run() {
								sampleWheelPosition.setItems(positions);
							}
						});
					}
				}
			});

			String[] positions = null;
			try {
				positions = sampleWheel.getPositions();
			} catch (DeviceException e1) {
				logger.error("Exception retrieving list of positions from sample wheel", e1);
			}
			if (positions != null) {

				final ExpandableComposite refWheelExpander = new ExpandableComposite(composite, ExpandableComposite.TWISTIE
						| ExpandableComposite.COMPACT | SWT.BORDER);
				refWheelExpander.setText("Reference Sample Wheel");

				final Composite refWheel = new Composite(refWheelExpander, SWT.NONE);
				GridLayoutFactory.fillDefaults().numColumns(2).applyTo(refWheel);
				GridDataFactory.swtDefaults().applyTo(refWheel);
				
				this.useSampleWheel = new BooleanWrapper(refWheel, SWT.NONE);
				GridDataFactory.swtDefaults().span(2, 1).applyTo(useSampleWheel);
				useSampleWheel.setText("Set reference sample");
				useSampleWheel.setValue(true);
				useSampleWheel.setToolTipText("Check the box to set the reference sample when running this experiment");
				useSampleWheel.addValueListener(new ValueListener() {
					
					@Override
					public void valueChangePerformed(ValueEvent e) {
						Boolean boxTicked = (Boolean) e.getValue();
						elementLabel.setEnabled(boxTicked);
						sampleWheelPosition.setEnabled(boxTicked);
					}
					
					@Override
					public String getValueListenerName() {
						return null;
					}
				});

				this.elementLabel = new Link(refWheel, SWT.NONE);
				elementLabel.setText("  <a>Position</a> ");
				elementLabel.setToolTipText("Open the preferences to edit the sample elements.");
				this.selectionListener = new SelectionAdapter() {
					@Override
					public void widgetSelected(SelectionEvent e) {
						openPreferences();
					}
				};
				elementLabel.addSelectionListener(selectionListener);
				elementLabel.setEnabled(false);

				sampleWheelPosition = new ComboWrapper(refWheel, SWT.BORDER);
				sampleWheelPosition.setItems(positions);
				sampleWheelPosition.setNotifyType(NOTIFY_TYPE.ALWAYS);
				sampleWheelPosition.setEnabled(false);
				
				refWheelExpander.setClient(refWheel);
				refWheelExpander.setExpanded(false);
				refWheelExpander.addExpansionListener(new ExpansionAdapter() {
					@Override
					public void expansionStateChanged(ExpansionEvent e) {
						if(!e.getState()){
							refWheelExpander.setExpanded(useSampleWheel.getValue());
						}
						refWheel.layout();
						mainComp.layout();
					}
				});
			}
		}
	}

	private void createSampleEnvironmentGroup(final Composite composite) {
		GridLayout gridLayout;
		final ExpandableComposite sampleEnvExpander = new ExpandableComposite(composite, ExpandableComposite.TWISTIE
				| ExpandableComposite.COMPACT | SWT.BORDER);
		sampleEnvExpander.setText("Sample Environment");

		final Composite sampleEnvGroup = new Composite(sampleEnvExpander, SWT.NONE);
		final GridData gd_tempControl = new GridData(SWT.FILL, SWT.CENTER, true, false);
		sampleEnvGroup.setLayoutData(gd_tempControl);
		gridLayout = new GridLayout();
		gridLayout.numColumns = 1;
		sampleEnvGroup.setLayout(gridLayout);

		cmbSampleEnv = new ComboWrapper(sampleEnvGroup, SWT.READ_ONLY);
		cmbSampleEnv.select(0);
		if (ScanObjectManager.isXESOnlyMode()) {
			cmbSampleEnv.setItems(I20SampleParameters.SAMPLE_ENV_XES);
		} else {
			cmbSampleEnv.setItems(I20SampleParameters.SAMPLE_ENV);
		}
		final GridData gd_tempType = new GridData(SWT.FILL, SWT.CENTER, true, false);
		cmbSampleEnv.setLayoutData(gd_tempType);

		this.complexTypesTemp = new Composite(sampleEnvGroup, SWT.NONE);
		this.stackLayoutTemp = new StackLayout();
		complexTypesTemp.setLayout(stackLayoutTemp);
		complexTypesTemp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

		blankTempComposite = new Composite(complexTypesTemp, SWT.NONE);

		this.sampleStageParameters = new RoomTemperatureComposite(complexTypesTemp, SWT.NONE);
		sampleStageParameters.setEditorClass(SampleStageParameters.class);

		if (!ScanObjectManager.isXESOnlyMode()) {
			this.cryostatParameters = new CryostatComposite(complexTypesTemp, SWT.NONE);
			cryostatParameters.setEditorClass(CryostatParameters.class);

			this.furnaceParameters = new FurnaceComposite(complexTypesTemp, SWT.NONE);
			furnaceParameters.setEditorClass(FurnaceParameters.class);

			this.microreactorParameters = new MicroreactorParametersComposite(complexTypesTemp, SWT.NONE);
			microreactorParameters.setEditorClass(MicroreactorParameters.class);
		}

		this.customXYZParameters = new VerticalListEditor(complexTypesTemp, SWT.NONE);
		customXYZParameters.setNameField("deviceName");
		customXYZParameters.setEditorClass(CustomXYZParameter.class);
		customXYZParameters.setEditorUI(new CustomXYZParameterComposite(customXYZParameters, SWT.NONE));
		customXYZParameters.setTemplateName("Custom XYZ Parameter");

		this.customParameters = new VerticalListEditor(complexTypesTemp, SWT.NONE);
		customParameters.setNameField("deviceName");
		customParameters.setEditorClass(CustomParameter.class);
		customParameters.setEditorUI(new CustomParameterComposite(customParameters, SWT.NONE));
		customParameters.setTemplateName("Custom Parameter");
		
		sampleEnvExpander.setClient(sampleEnvGroup);
		sampleEnvExpander.setExpanded(false);
		sampleEnvExpander.addExpansionListener(new ExpansionAdapter() {
			@Override
			public void expansionStateChanged(ExpansionEvent e) {
				if (!e.getState()) {
					if (!cmbSampleEnv.getItem(cmbSampleEnv.getSelectionIndex())
							.equals(I20SampleParameters.SAMPLE_ENV[0])) {
						sampleEnvExpander.setExpanded(true);
					}
				}

				sampleEnvExpander.layout();
				sampleEnvGroup.layout();
				mainComp.layout();
			}
		});
	}

	private void createSampleDetailsGroup(final Composite composite) {
		GridLayout gridLayout;
		final Group experimentSample = new Group(composite, SWT.NONE);
		experimentSample.setText("Sample Details");
		GridData experimentSampleGridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		experimentSampleGridData.minimumWidth = 350;
		experimentSample.setLayoutData(experimentSampleGridData);
		gridLayout = new GridLayout();
		gridLayout.numColumns = 2;
		experimentSample.setLayout(gridLayout);

		final Label filePrefixLabel = new Label(experimentSample, SWT.NONE);
		filePrefixLabel.setText("File prefix");

		name = new TextWrapper(experimentSample, SWT.BORDER);
		name.setTextLimit(5000);
		final GridData gd_name = new GridData(SWT.FILL, SWT.CENTER, true, false);
		name.setLayoutData(gd_name);

		final Label sampleNameLabel = new Label(experimentSample, SWT.NONE);
		sampleNameLabel.setText("Sample Name");

		sampleName = new TextWrapper(experimentSample, SWT.BORDER);
		sampleName.setTextLimit(5000);
		sampleName.setLayoutData(gd_name);

		final Label descriptionLabel = new Label(experimentSample, SWT.NONE);
		descriptionLabel.setLayoutData(new GridData(SWT.LEFT, SWT.TOP, false, false));
		descriptionLabel.setText("Description");

		descriptions = new TextWrapper(experimentSample, SWT.WRAP | SWT.V_SCROLL | SWT.MULTI | SWT.BORDER);
		final GridData gd_descriptions = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gd_descriptions.heightHint = 73;
		descriptions.setLayoutData(gd_descriptions);
	}

	protected void openPreferences() {
		PreferenceDialog pref = PreferencesUtil.createPreferenceDialogOn(getSite().getShell(),
				I20SampleReferenceWheelPreferencePage.ID, null, null);
		if (pref != null)
			pref.open();
	}

	@Override
	public void linkUI(final boolean isPageChange) {
		cmbSampleEnv.addValueListener(new ValueAdapter("sampleEnvironmentListener") {
			@Override
			public void valueChangePerformed(ValueEvent e) {
				updateTemperatureType(cmbSampleEnv.getSelectionIndex());
			}
		});

		super.linkUI(isPageChange);

		// Now the data will have one of the complex types so we can init the envType
		int index = initTempType();
		cmbSampleEnv.select(index);
	}

	private int initTempType() {
		final I20SampleParameters params = (I20SampleParameters) editingBean;
		final List<String> items = Arrays.asList(cmbSampleEnv.getItems());
		final int index = items.indexOf(params.getSampleEnvironment());
		updateTemperatureType(index);
		return index;
	}

	private void updateTemperatureType(final int index) {

		final I20SampleParameters params = (I20SampleParameters) editingBean;
		Control control = null;

		if (ScanObjectManager.isXESOnlyMode()) {
			Object val = null;
			switch (index) {
			case 0:
				control = blankTempComposite;
				break;
			case 1:
				control = sampleStageParameters;
				val = getRoomTemperatureParameters().getValue();
				if (val == null) {
					params.getRoomTemperatureParameters();
				}
				if (val == null) {
					val = new SampleStageParameters();
				}
				if (params.getRoomTemperatureParameters() == null) {
					params.setRoomTemperatureParameters((SampleStageParameters) val);
				}
				if (getRoomTemperatureParameters().getValue() == null) {
					getRoomTemperatureParameters().setEditingBean(val);
				}
				break;
			case 2:
				control = customXYZParameters;
				break;
			case 3:
				control = customParameters;
				break;
			default:
				break;
			}
		} else {
			Object val = null;

			switch (index) {
			case 0:
				control = blankTempComposite;
				val = "none";
				break;
			case 1:
				control = sampleStageParameters;
				val = getRoomTemperatureParameters().getValue();
				if (val == null) {
					params.getRoomTemperatureParameters();
				}
				if (val == null) {
					val = new SampleStageParameters();
				}
				if (params.getRoomTemperatureParameters() == null) {
					params.setRoomTemperatureParameters((SampleStageParameters) val);
				}
				if (getRoomTemperatureParameters().getValue() == null) {
					getRoomTemperatureParameters().setEditingBean(val);
				}
				break;
			case 2:
				control = cryostatParameters;
				val = getCryostatParameters().getValue();
				if (val == null)
					params.getCryostatParameters();
				if (val == null)
					val = new CryostatParameters();
				if (params.getCryostatParameters() == null)
					params.setCryostatParameters((CryostatParameters) val);
				if (getCryostatParameters().getValue() == null)
					getCryostatParameters().setEditingBean(val);

				break;
			case 3:
				control = furnaceParameters;
				val = getFurnaceParameters().getValue();
				if (val == null)
					params.getFurnaceParameters();
				if (val == null)
					val = new FurnaceParameters();
				if (params.getFurnaceParameters() == null)
					params.setFurnaceParameters((FurnaceParameters) val);
				if (getFurnaceParameters().getValue() == null)
					getFurnaceParameters().setEditingBean(val);
				break;
			case 4:
				control = microreactorParameters;
				val = getMicroreactorParameters().getValue();
				if (val == null)
					params.getMicroreactorParameters();
				if (val == null)
					val = new MicroreactorParameters();
				if (params.getMicroreactorParameters() == null)
					params.setMicroreactorParameters((MicroreactorParameters) val);
				if (getMicroreactorParameters().getValue() == null)
					getMicroreactorParameters().setEditingBean(val);
				break;

			case 5:
				control = customXYZParameters;
				break;
			case 6:
				control = customParameters;
				break;
			default:
				break;
			}
		}

		stackLayoutTemp.topControl = control;
		complexTypesTemp.layout();
	}

	@Override
	public void setFocus() {
	}

	public TextWrapper getDescriptions() {
		return descriptions;
	}

	public TextWrapper getName() {
		return name;
	}

	public TextWrapper getSampleName() {
		return sampleName;
	}

	public ComboWrapper getSampleWheelPosition() {
		return sampleWheelPosition;
	}

	public RoomTemperatureComposite getRoomTemperatureParameters() {
		return sampleStageParameters;
	}

	public CryostatComposite getCryostatParameters() {
		return cryostatParameters;
	}

	public FurnaceComposite getFurnaceParameters() {
		return furnaceParameters;
	}

	public MicroreactorParametersComposite getMicroreactorParameters() {
		return microreactorParameters;
	}

	public VerticalListEditor getCustomParameters() {
		return customParameters;
	}

	public VerticalListEditor getCustomXYZParameters() {
		return customXYZParameters;
	}

	public ComboWrapper getSampleEnvironment() {
		return cmbSampleEnv;
	}

	public BooleanWrapper getUseSampleWheel() {
		return useSampleWheel;
	}

	public String _testGetElementName() {
		return sampleWheelPosition.getItem(sampleWheelPosition.getSelectionIndex());
	}
}

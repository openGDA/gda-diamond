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

package gda.exafs.ui;

import java.net.URL;
import java.util.Arrays;
import java.util.List;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.preference.PreferenceDialog;
import org.eclipse.richbeans.api.event.ValueAdapter;
import org.eclipse.richbeans.api.event.ValueEvent;
import org.eclipse.richbeans.api.event.ValueListener;
import org.eclipse.richbeans.widgets.FieldComposite.NOTIFY_TYPE;
import org.eclipse.richbeans.widgets.selector.BeanSelectionEvent;
import org.eclipse.richbeans.widgets.selector.BeanSelectionListener;
import org.eclipse.richbeans.widgets.selector.VerticalListEditor;
import org.eclipse.richbeans.widgets.wrappers.BooleanWrapper;
import org.eclipse.richbeans.widgets.wrappers.ComboWrapper;
import org.eclipse.richbeans.widgets.wrappers.TextWrapper;
import org.eclipse.richbeans.widgets.wrappers.TextWrapper.TEXT_TYPE;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.custom.StackLayout;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Link;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.dialogs.PreferencesUtil;
import org.eclipse.ui.forms.events.ExpansionAdapter;
import org.eclipse.ui.forms.events.ExpansionEvent;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.slf4j.Logger;

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.exafs.ui.composites.CryostatTableComposite;
import gda.exafs.ui.composites.RoomTemperatureComposite;
import gda.exafs.ui.preferencepages.I20SampleReferenceWheelPreferencePage;
import gda.factory.Finder;
import gda.observable.IObserver;
import uk.ac.gda.beans.exafs.i20.CryostatParameters;
import uk.ac.gda.beans.exafs.i20.I20SampleParameters;
import uk.ac.gda.beans.exafs.i20.SampleStageParameters;
import uk.ac.gda.exafs.ui.data.ScanObjectManager;
import uk.ac.gda.richbeans.editors.DirtyContainer;
import uk.ac.gda.richbeans.editors.RichBeanEditorPart;

public class I20SampleParametersUIEditor extends RichBeanEditorPart {
	private static final Logger logger = org.slf4j.LoggerFactory.getLogger(I20SampleParametersUIEditor.class);
	private Composite mainComp;
	private ComboWrapper cmbSampleEnv;
	private ScrolledComposite scrolledComposite;
	private ComboWrapper sampleWheelPosition;
	private TextWrapper descriptions;
	private TextWrapper name;
	private VerticalListEditor sampleStageListEditor;
	private CryostatTableComposite cryostatComposite;
	private SelectionAdapter selectionListener;
	private Link elementLabel;
	private Composite complexTypesTemp;
	private StackLayout stackLayoutTemp;
	private Composite blankTempComposite;
	private BooleanWrapper useSampleWheel;
	private I20SampleParameters bean;
	private ExpandableComposite refWheelExpander;
	private Group sampleDetails;
	private GridData sampleDetailsGridData;
	ExpandableComposite sampleEnvExpander;

	public I20SampleParametersUIEditor(String path, URL mappingURL, DirtyContainer dirtyContainer, Object bean) {
		super(path, mappingURL, dirtyContainer, bean);
		this.bean = (I20SampleParameters)bean;
	}

	@Override
	protected String getRichEditorTabText() {
		return "Sample";
	}

	@Override
	public void createPartControl(final Composite parent) {
		parent.setLayout(new FillLayout());
		scrolledComposite = new ScrolledComposite(parent, SWT.H_SCROLL | SWT.V_SCROLL);
		scrolledComposite.setExpandHorizontal(true);
		scrolledComposite.setExpandVertical(true);
		mainComp = new Composite(scrolledComposite, SWT.NONE);
		GridLayout gridLayout = new GridLayout();
		gridLayout.numColumns = 1;
		mainComp.setLayout(gridLayout);
		Composite composite = new Composite(mainComp, SWT.NONE);
		gridLayout = new GridLayout();
		gridLayout.numColumns = 1;
		composite.setLayout(gridLayout);
		createSampleDetailsGroup(composite);
		createSampleCombo(composite);
		createSampleEnvironmentGroup(composite);
		if (!ScanObjectManager.isXESOnlyMode())
			createSampleWheelGroup(composite);
		scrolledComposite.setContent(mainComp);
		mainComp.layout();
		scrolledComposite.setMinSize(mainComp.computeSize(SWT.DEFAULT, SWT.DEFAULT));
	}

	private void createSampleWheelGroup(final Composite composite) {
		EnumPositioner sampleWheel = Finder.getInstance().find(I20SampleParameters.SAMPLE_WHEEL_NAME);
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
				refWheelExpander = new ExpandableComposite(composite, ExpandableComposite.TWISTIE
						| ExpandableComposite.COMPACT | SWT.BORDER);
				refWheelExpander.setText("Reference Sample Wheel");

				final Composite refWheel = new Composite(refWheelExpander, SWT.NONE);
				GridLayoutFactory.fillDefaults().numColumns(2).applyTo(refWheel);
				GridDataFactory.swtDefaults().applyTo(refWheel);

				useSampleWheel = new BooleanWrapper(refWheel, SWT.NONE);
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
						return "useSampleWheel listener";
					}
				});

				elementLabel = new Link(refWheel, SWT.NONE);
				elementLabel.setText("  <a>Position</a> ");
				elementLabel.setToolTipText("Open the preferences to edit the sample elements.");
				selectionListener = new SelectionAdapter() {
					@Override
					public void widgetSelected(SelectionEvent e) {
						openPreferences();
					}
				};
				elementLabel.addSelectionListener(selectionListener);
				elementLabel.setEnabled(true);

				sampleWheelPosition = new ComboWrapper(refWheel, SWT.BORDER);
				sampleWheelPosition.setItems(positions);
				sampleWheelPosition.setNotifyType(NOTIFY_TYPE.ALWAYS);
				sampleWheelPosition.setEnabled(true);

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
						scrolledComposite.setMinSize(mainComp.computeSize(SWT.DEFAULT, SWT.DEFAULT));
					}
				});
			}
			if (bean != null && bean.getUseSampleWheel())
				refWheelExpander.setExpanded(true);
		}
	}

	private void createSampleCombo(final Composite composite) {
		Group sampleEnvSelectionGroup = new Group(composite, SWT.NONE);
		sampleEnvSelectionGroup.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		sampleEnvSelectionGroup.setText("Sample Environment Type");

		GridLayout gridLayout = new GridLayout();
		gridLayout.numColumns = 2;
		sampleEnvSelectionGroup.setLayout(gridLayout);

		cmbSampleEnv = new ComboWrapper(sampleEnvSelectionGroup, SWT.READ_ONLY);
		cmbSampleEnv.select(0);

		if (ScanObjectManager.isXESOnlyMode())
			cmbSampleEnv.setItems(I20SampleParameters.SAMPLE_ENV_XES);
		else
			cmbSampleEnv.setItems(I20SampleParameters.SAMPLE_ENV);

		cmbSampleEnv.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
	}

	/**
	 * Create combo box to control sample environment to use (refactored from createSampleEnvironmentGroup)
	 * @author Iain Hall
	 * @since 6/1/2016
	 */
	private void createSampleEnvironmentGroup(final Composite composite) {

		sampleEnvExpander = new ExpandableComposite(composite, ExpandableComposite.COMPACT | SWT.BORDER);
		sampleEnvExpander.setText("Sample Environment");

		final Composite sampleEnvGroup = new Composite(sampleEnvExpander, SWT.NONE);
		GridData gd_tempControl = new GridData(SWT.FILL, SWT.CENTER, true, false);
		sampleEnvGroup.setLayoutData(gd_tempControl);
		GridLayoutFactory.fillDefaults().applyTo(sampleEnvGroup);

		complexTypesTemp = new Composite(sampleEnvGroup, SWT.NONE);
		stackLayoutTemp = new StackLayout();
		complexTypesTemp.setLayout(stackLayoutTemp);
		complexTypesTemp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

		blankTempComposite = new Composite(complexTypesTemp, SWT.NONE);

		sampleStageListEditor = new VerticalListEditor(complexTypesTemp, SWT.NONE);
		sampleStageListEditor.setTemplateName("sampleposition");
		sampleStageListEditor.setRequireSelectionPack(false);
		GridDataFactory.swtDefaults().grab(true, false).applyTo(sampleStageListEditor);
		sampleStageListEditor.setEditorClass(SampleStageParameters.class);
		sampleStageListEditor.setFieldName("sampleposition");
		sampleStageListEditor.setNameField("sample_name");

		final RoomTemperatureComposite roomTemperatureComposite = new RoomTemperatureComposite(sampleStageListEditor, SWT.NONE);
		GridDataFactory.swtDefaults().grab(true, false).applyTo(roomTemperatureComposite);
		sampleStageListEditor.setEditorUI(roomTemperatureComposite);
		sampleStageListEditor.setListEditorUI(roomTemperatureComposite);
		sampleStageListEditor.addBeanSelectionListener(new BeanSelectionListener() {
			@Override
			public void selectionChanged(BeanSelectionEvent evt) {
				roomTemperatureComposite.selectionChanged((SampleStageParameters) evt.getSelectedBean());
			}
		});

		if (!ScanObjectManager.isXESOnlyMode()) {
			cryostatComposite = new CryostatTableComposite(complexTypesTemp, SWT.NONE);
			cryostatComposite.setEditorClass(CryostatParameters.class);
		}

		sampleEnvExpander.setClient(sampleEnvGroup);
		sampleEnvExpander.setExpanded(false);
		sampleEnvExpander.addExpansionListener(new ExpansionAdapter() {
			@Override
			public void expansionStateChanged(ExpansionEvent e) {
				if (!e.getState())
					if (!cmbSampleEnv.getItem(cmbSampleEnv.getSelectionIndex()).equals(I20SampleParameters.SAMPLE_ENV[0]))
						sampleEnvExpander.setExpanded(true);
				sampleEnvExpander.layout();
				sampleEnvGroup.layout();
				mainComp.layout();
				scrolledComposite.setMinSize(mainComp.computeSize(SWT.DEFAULT, SWT.DEFAULT));
			}
		});

		if (bean != null && !bean.getSampleEnvironment().equals(I20SampleParameters.SAMPLE_ENV[0]))
			sampleEnvExpander.setExpanded(true);
	}

	private void createSampleDetailsGroup(final Composite composite) {
		GridLayout gridLayout;
		sampleDetails = new Group(composite, SWT.NONE);
		sampleDetails.setText("Sample Details");
		sampleDetailsGridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		sampleDetailsGridData.minimumWidth = 350;
		sampleDetails.setLayoutData(sampleDetailsGridData);
		gridLayout = new GridLayout();
		gridLayout.numColumns = 2;
		sampleDetails.setLayout(gridLayout);

		Label sampleNameLabel = new Label(sampleDetails, SWT.NONE);
		sampleNameLabel.setText("File Name");

		name = new TextWrapper(sampleDetails, SWT.BORDER | SWT.SINGLE);
		name.setTextType(TEXT_TYPE.FILENAME);
		name.setTextLimit(50);
		GridData gd_name = new GridData(SWT.FILL, SWT.CENTER, true, false);
		name.setLayoutData(gd_name);

		Label descriptionLabel = new Label(sampleDetails, SWT.NONE);
		descriptionLabel.setLayoutData(new GridData(SWT.LEFT, SWT.TOP, false, false));
		descriptionLabel.setText("Sample Description");

		descriptions = new TextWrapper(sampleDetails, SWT.WRAP | SWT.V_SCROLL | SWT.MULTI | SWT.BORDER);
		GridData gd_descriptions = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gd_descriptions.heightHint = 73;
		descriptions.setLayoutData(gd_descriptions);
	}

	protected void openPreferences() {
		PreferenceDialog pref = PreferencesUtil.createPreferenceDialogOn(getSite().getShell(), I20SampleReferenceWheelPreferencePage.ID, null, null);
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
		List<String> items = Arrays.asList(cmbSampleEnv.getItems());
		int index = items.indexOf(bean.getSampleEnvironment());
		updateTemperatureType(index);
		return index;
	}

	private void updateTemperatureType(final int index) {
		Composite control = null;
		sampleDetails.setVisible(true);
		sampleDetailsGridData.exclude = false;
		boolean showSampleEnvironmentDetails = false;
		if (ScanObjectManager.isXESOnlyMode()) {
			switch (index) {
			case 0:
				control = blankTempComposite;
				break;
			case 1:
				control = sampleStageListEditor;
				showSampleEnvironmentDetails = true;
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
				control = sampleStageListEditor;
				showSampleEnvironmentDetails = true;
				break;
			case 2:
				control = cryostatComposite;
				showSampleEnvironmentDetails = true;
				val = getCryostatParameters().getValue();
				if (val == null)
					bean.getCryostatParameters();
				if (val == null)
					val = new CryostatParameters();
				if (bean.getCryostatParameters() == null)
					bean.setCryostatParameters((CryostatParameters) val);
				if (getCryostatParameters().getValue() == null)
					getCryostatParameters().setEditingBean(val);
				break;
			default:
				break;
			}
		}
		sampleEnvExpander.setVisible(showSampleEnvironmentDetails);
		stackLayoutTemp.topControl = control;
		complexTypesTemp.layout();
		mainComp.layout();
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

	public ComboWrapper getSampleWheelPosition() {
		return sampleWheelPosition;
	}

	public VerticalListEditor getRoomTemperatureParameters() {
		return sampleStageListEditor;
	}

	public CryostatTableComposite getCryostatParameters() {
		return cryostatComposite;
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
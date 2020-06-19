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

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.preference.PreferenceDialog;
import org.eclipse.richbeans.api.event.ValueEvent;
import org.eclipse.richbeans.api.event.ValueListener;
import org.eclipse.richbeans.widgets.FieldComposite.NOTIFY_TYPE;
import org.eclipse.richbeans.widgets.wrappers.BooleanWrapper;
import org.eclipse.richbeans.widgets.wrappers.ComboWrapper;
import org.eclipse.richbeans.widgets.wrappers.TextWrapper;
import org.eclipse.richbeans.widgets.wrappers.TextWrapper.TEXT_TYPE;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
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
import gda.exafs.ui.preferencepages.I20SampleReferenceWheelPreferencePage;
import gda.factory.Finder;
import uk.ac.gda.beans.exafs.i20.I20SampleParameters;
import uk.ac.gda.exafs.ui.SampleParameterMotorPositionsComposite;
import uk.ac.gda.exafs.ui.data.ScanObjectManager;
import uk.ac.gda.richbeans.editors.DirtyContainer;
import uk.ac.gda.richbeans.editors.RichBeanEditorPart;

public class I20SampleParametersUIEditor extends RichBeanEditorPart {
	private static final Logger logger = org.slf4j.LoggerFactory.getLogger(I20SampleParametersUIEditor.class);
	private Composite mainComp;
	private ScrolledComposite scrolledComposite;
	private ComboWrapper sampleWheelPosition;
	private TextWrapper descriptions;
	private TextWrapper name;
	private BooleanWrapper useSampleWheel;
	private I20SampleParameters bean;
	private SampleParameterMotorPositionsComposite motorPositionComposite;

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
		createMotorComposite(composite);
		if (!ScanObjectManager.isXESOnlyMode())
			createSampleWheelGroup(composite);
		scrolledComposite.setContent(mainComp);
		mainComp.layout();
		scrolledComposite.setMinSize(mainComp.computeSize(SWT.DEFAULT, SWT.DEFAULT));
	}

	private void createMotorComposite(final Composite parent) {

		Group group = new Group(parent, SWT.NONE);
		group.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		group.setLayout(new GridLayout(1, false));
		group.setText("Motor parameters");

		motorPositionComposite = new SampleParameterMotorPositionsComposite(group, bean.getSampleParameterMotorPositions());
		motorPositionComposite.setParentEditor(this);
		motorPositionComposite.makeComposite();
	}

	private void createSampleWheelGroup(final Composite composite) {
		EnumPositioner sampleWheel = Finder.find(I20SampleParameters.SAMPLE_WHEEL_NAME);
		if (sampleWheel != null) {

			// Update sample wheel combo items if underlying scannable changes
			sampleWheel.addIObserver( (source, arg) -> {
					if (arg instanceof String[]) {
						final String[] positions = (String[]) arg;
						PlatformUI.getWorkbench().getDisplay().asyncExec( () ->	sampleWheelPosition.setItems(positions));
					}
				}
			);

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

				useSampleWheel = new BooleanWrapper(refWheel, SWT.NONE);
				GridDataFactory.swtDefaults().span(2, 1).applyTo(useSampleWheel);
				useSampleWheel.setText("Set reference sample");
				useSampleWheel.setValue(true);
				useSampleWheel.setToolTipText("Check the box to set the reference sample when running this experiment");

				Link elementLabel = new Link(refWheel, SWT.NONE);
				elementLabel.setText("  <a>Position</a> ");
				elementLabel.setToolTipText("Open the preferences to edit the sample elements.");
				elementLabel.addListener(SWT.Selection, event -> openPreferences());
				elementLabel.setEnabled(true);

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
				if (bean != null && bean.getUseSampleWheel())
					refWheelExpander.setExpanded(true);
			}
		}
	}

	private void createSampleDetailsGroup(final Composite composite) {
		GridLayout gridLayout;
		Group sampleDetailsGroup = new Group(composite, SWT.NONE);
		sampleDetailsGroup.setText("Sample Details");
		GridData sampleDetailsGridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		sampleDetailsGridData.minimumWidth = 350;
		sampleDetailsGroup.setLayoutData(sampleDetailsGridData);
		gridLayout = new GridLayout();
		gridLayout.numColumns = 2;
		sampleDetailsGroup.setLayout(gridLayout);

		Label sampleNameLabel = new Label(sampleDetailsGroup, SWT.NONE);
		sampleNameLabel.setText("File Name");

		name = new TextWrapper(sampleDetailsGroup, SWT.BORDER | SWT.SINGLE);
		name.setTextType(TEXT_TYPE.FILENAME);
		name.setTextLimit(50);
		GridData gd_name = new GridData(SWT.FILL, SWT.CENTER, true, false);
		name.setLayoutData(gd_name);

		Label descriptionLabel = new Label(sampleDetailsGroup, SWT.NONE);
		descriptionLabel.setLayoutData(new GridData(SWT.LEFT, SWT.TOP, false, false));
		descriptionLabel.setText("Sample Description");

		descriptions = new TextWrapper(sampleDetailsGroup, SWT.WRAP | SWT.V_SCROLL | SWT.MULTI | SWT.BORDER);
		GridData gd_descriptions = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gd_descriptions.heightHint = 73;
		descriptions.setLayoutData(gd_descriptions);
	}

	private void openPreferences() {
		PreferenceDialog pref = PreferencesUtil.createPreferenceDialogOn(getSite().getShell(), I20SampleReferenceWheelPreferencePage.ID, null, null);
		if (pref != null)
			pref.open();
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

	public BooleanWrapper getUseSampleWheel() {
		return useSampleWheel;
	}

	public SampleParameterMotorPositionsComposite getSampleParameterMotorPositions() {
		return motorPositionComposite;
	}
}
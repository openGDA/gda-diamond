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

package uk.ac.gda.exafs.experiment.ui;


import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.databinding.viewers.ViewersObservables;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.events.FocusAdapter;
import org.eclipse.swt.events.FocusEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.jaret.util.date.Interval;
import gda.jython.IJythonServerStatusObserver;
import gda.jython.InterfaceProvider;
import gda.scan.ScanEvent;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.alignment.ui.SampleStageMotorsComposite;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentModelHolder;
import uk.ac.gda.exafs.experiment.ui.data.SpectrumModel;
import uk.ac.gda.exafs.experiment.ui.data.TimeResolvedExperimentModel;
import uk.ac.gda.exafs.experiment.ui.data.TimingGroupUIModel;

public class TimeResolvedExperimentView extends ViewPart {

	public static final String LINEAR_EXPERIMENT_VIEW_ID = "uk.ac.gda.exafs.ui.views.linearExperimentView";

	private static Logger logger = LoggerFactory.getLogger(TimeResolvedExperimentView.class);

	protected FormToolkit toolkit;
	private DataBindingContext dataBindingCtx;

	protected Button useExternalTriggerCheckbox;

	private Button useFastShutterCheckbox;

	private Text sampleDescText;

	private Text prefixText;

	private SampleStageMotorsComposite sampleMotorsComposite;

	private ExperimentTimeBarComposite timebarViewerComposite;

	private TimingGroupSectionComposite timingGroupSectionComposite;

	@Override
	public void createPartControl(final Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		dataBindingCtx = new DataBindingContext();
		final SashForm parentComposite = new SashForm(parent, SWT.VERTICAL);
		parentComposite.SASH_WIDTH = 7;
		try {
			createSections(parentComposite);
			bind();
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
			logger.error("Unable to create controls", e);
		}
		InterfaceProvider.getScanDataPointProvider().addScanEventObserver(serverObserver);
	}

	protected void createSections(final SashForm parentComposite) {
		createExperimentPropertiesComposite(parentComposite);
		createTimeBarComposite(parentComposite);
		parentComposite.setWeights(new int[] {5, 1});
	}

	protected TimeResolvedExperimentModel getModel() {
		return ExperimentModelHolder.INSTANCE.getLinerExperimentModel();
	}

	private void bind() {
		dataBindingCtx.bindValue(
				ViewersObservables.observeSingleSelection(timingGroupSectionComposite.getGroupsTableViewer()),
				ViewersObservables.observeSingleSelection(timebarViewerComposite.getTimeBarViewer()),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						if (value != null) {
							timebarViewerComposite.getTimeBarViewer().scrollIntervalToVisible((Interval) value);
						}
						return super.doSet(observableValue, value);
					}
				},
				new UpdateValueStrategy() {
					@Override
					public IStatus validateBeforeSet(Object value) {
						TimingGroupUIModel object = null;
						if (value instanceof TimingGroupUIModel) {
							object =  (TimingGroupUIModel) value;
						} else if (value instanceof SpectrumModel) {
							object = ((SpectrumModel) value).getParent();
						}
						IStructuredSelection structuredSelection = (IStructuredSelection) timingGroupSectionComposite.getGroupsTableViewer().getSelection();
						if(!structuredSelection.isEmpty()) {
							if (value == null) {
								return Status.CANCEL_STATUS;
							}
							TimingGroupUIModel viewerObject = (TimingGroupUIModel) structuredSelection.getFirstElement();
							if (viewerObject.equals(object)) {
								return Status.CANCEL_STATUS;
							}
						}
						return Status.OK_STATUS;
					}

					@Override
					public Object convert(Object value) {
						if (value instanceof TimingGroupUIModel) {
							return super.convert(value);
						}
						else if (value instanceof SpectrumModel) {
							return super.convert(((SpectrumModel) value).getParent());
						}
						return null;
					}
				});

		// Update the filename in the model
		prefixText.addFocusListener(new FocusAdapter() {
			@Override
			public void focusLost(FocusEvent e) {
				getModel().getExperimentDataModel().setFileNamePrefix(prefixText.getText());
			}
		});
		// Update the sample description in the model
		sampleDescText.addFocusListener(new FocusAdapter() {
			@Override
			public void focusLost(FocusEvent e) {
				getModel().getExperimentDataModel().setSampleDetails(sampleDescText.getText());
			}
		});

		dataBindingCtx.bindValue(WidgetProperties.selection().observe(useFastShutterCheckbox),
				BeanProperties.value(TimeResolvedExperimentModel.USE_FAST_SHUTTER).observe(getModel()) );
	}

	protected void createExperimentPropertiesComposite(Composite parent) {
		Composite composite = new Composite(parent, SWT.None);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		composite.setLayout(UIHelper.createGridLayoutWithNoMargin(1,false));
		ScrolledForm scrolledform = toolkit.createScrolledForm(composite);
		scrolledform.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		Form form = scrolledform.getForm();
		// Moved to single column
		form.getBody().setLayout(new GridLayout(1, true));
		toolkit.decorateFormHeading(form);
		scrolledform.setText("Time-resolved studies");
		createExperimentDetailsSection(form.getBody());
		createGroupSection(form.getBody());
		form.layout();
	}

	private void createExperimentDetailsSection(Composite parent) {

		// Start stop buttons
		final Section dataCollectionSection = toolkit.createSection(parent, ExpandableComposite.NO_TITLE);
		dataCollectionSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Composite dataCollectionSectionComposite = toolkit.createComposite(dataCollectionSection, SWT.NONE);
		dataCollectionSectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));
		dataCollectionSection.setClient(dataCollectionSectionComposite);

		Composite prefixNameComposite = toolkit.createComposite(dataCollectionSectionComposite, SWT.NONE);
		prefixNameComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		prefixNameComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		Label prefixLabel = toolkit.createLabel(prefixNameComposite, "File prefix", SWT.None);
		prefixLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		prefixText = toolkit.createText(prefixNameComposite, getModel().getExperimentDataModel().getFileNamePrefix(), SWT.BORDER);
		prefixText.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		Composite sampleDescComposite = toolkit.createComposite(dataCollectionSectionComposite, SWT.NONE);
		sampleDescComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		sampleDescComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		Label sampleDescLabel = toolkit.createLabel(sampleDescComposite, "Sample details", SWT.None);
		sampleDescLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		sampleDescText = toolkit.createText(sampleDescComposite,  getModel().getExperimentDataModel().getSampleDetails(), SWT.BORDER);
		sampleDescText.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		Button startAcquicitionButton = toolkit.createButton(dataCollectionSectionComposite, "Start", SWT.PUSH);
		startAcquicitionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		startAcquicitionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					getModel().doCollection(prefixText.getText(), sampleDescText.getText());
				} catch (Exception e) {
					UIHelper.showError("Unable to scan", e.getMessage());
				}
			}
		});

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(startAcquicitionButton),
				BeanProperties.value(TimeResolvedExperimentModel.SCANNING_PROP_NAME).observe(getModel()),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return (!(boolean) value);
					}
				});

		Button stopAcquicitionButton = toolkit.createButton(dataCollectionSectionComposite, "Stop", SWT.PUSH);
		stopAcquicitionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(stopAcquicitionButton),
				BeanProperties.value(TimeResolvedExperimentModel.SCANNING_PROP_NAME).observe(getModel()));
		stopAcquicitionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				getModel().doStop();
			}
		});

		useFastShutterCheckbox = toolkit.createButton(dataCollectionSectionComposite, "Use fast shutter", SWT.CHECK);
		useFastShutterCheckbox.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		//Sample stage motors

		sampleMotorsComposite = new SampleStageMotorsComposite(parent, SWT.None, toolkit, true);
	}

	final IJythonServerStatusObserver serverObserver = new IJythonServerStatusObserver() {
		@Override
		public void update(Object theObserved, final Object changeCode) {
			Display.getDefault().asyncExec(new Runnable() {
				@Override
				public void run() {
					if (changeCode instanceof ScanEvent) {
						updateStartStopButtons((ScanEvent)changeCode);
					}
				}
			});
		}
	};

	private void updateStartStopButtons(ScanEvent changeCode) {
		switch (changeCode.getLatestStatus()) {
		case COMPLETED_AFTER_FAILURE:
		case COMPLETED_AFTER_STOP:
		case COMPLETED_EARLY:
		case NOTSTARTED:
		case FINISHING_EARLY:
		case TIDYING_UP_AFTER_FAILURE:
		case TIDYING_UP_AFTER_STOP:
		case COMPLETED_OKAY:
			getModel().setScanning(false);
			timingGroupSectionComposite.setUserControlsEnabled(true);
			break;
		case PAUSED:
		case RUNNING:
			getModel().setScanning(true);
			timingGroupSectionComposite.setUserControlsEnabled(false);
			break;
		default:
			getModel().setScanning(false);
			timingGroupSectionComposite.setUserControlsEnabled(true);
			break;
		}
	}

	private void createGroupSection(Composite parent) {
		timingGroupSectionComposite = new TimingGroupSectionComposite(parent, SWT.None, toolkit, getModel());
		timingGroupSectionComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		toolkit.paintBordersFor(timingGroupSectionComposite);
		MenuManager menuManager = new MenuManager();
		Menu menu = menuManager.createContextMenu(timingGroupSectionComposite.getGroupsTableViewer().getTable());
		// Set the MenuManager
		timingGroupSectionComposite.getGroupsTableViewer().getTable().setMenu(menu);
		getSite().registerContextMenu(menuManager, timingGroupSectionComposite.getGroupsTableViewer());
		getSite().setSelectionProvider(timingGroupSectionComposite.getGroupsTableViewer());
	}

	protected void createTimeBarComposite(Composite parent) {
		timebarViewerComposite = new ExperimentTimeBarComposite(parent, SWT.None, getModel());
		timebarViewerComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		MenuManager menuManager = new MenuManager();
		Menu menu = menuManager.createContextMenu(timebarViewerComposite.getTimeBarViewer());
		// Set the MenuManager
		timebarViewerComposite.getTimeBarViewer().setMenu(menu);
		getSite().registerContextMenu(menuManager, timebarViewerComposite.getTimeBarViewer());

	}

	@Override
	public void setFocus() {
		timebarViewerComposite.setFocus();
	}

	@Override
	public void dispose() {
		sampleMotorsComposite.dispose();
		dataBindingCtx.dispose();
		super.dispose();
	}
}

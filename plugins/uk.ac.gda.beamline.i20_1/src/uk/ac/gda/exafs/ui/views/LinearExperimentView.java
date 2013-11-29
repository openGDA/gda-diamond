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

package uk.ac.gda.exafs.ui.views;

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
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.experiment.ExperimentModelHolder;
import uk.ac.gda.exafs.ui.data.experiment.SpectrumModel;
import uk.ac.gda.exafs.ui.data.experiment.TimeResolvedExperimentModel;
import uk.ac.gda.exafs.ui.data.experiment.TimingGroupUIModel;
import de.jaret.util.date.Interval;

public class LinearExperimentView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.linearExperimentView";

	private static Logger logger = LoggerFactory.getLogger(LinearExperimentView.class);

	private FormToolkit toolkit;
	private final DataBindingContext dataBindingCtx = new DataBindingContext();
	//	private TableViewer groupsTableViewer;

	protected Button useExternalTriggerCheckbox;

	private SampleStageMotorsComposite sampleMotorsComposite;

	private ExperimentTimeBarComposite timebarViewerComposite;

	private TimingGroupSectionComposite timingGroupSectionComposite;

	@Override
	public void createPartControl(final Composite parent) {
		if (toolkit == null) {
			toolkit = new FormToolkit(parent.getDisplay());
		}
		final SashForm parentComposite = new SashForm(parent, SWT.VERTICAL);
		parentComposite.SASH_WIDTH = 7;

		try {
			createExperimentPropertiesComposite(parentComposite);
			createTimeBarComposite(parentComposite);
			bind();
			parentComposite.setWeights(new int[] {3, 1});
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
			logger.error("Unable to create controls", e);
		}
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
	}

	private void createExperimentPropertiesComposite(Composite parent) {
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

		Composite acquisitionButtonsComposite = new Composite(parent, SWT.NONE);
		GridData gridData = new GridData(SWT.FILL, SWT.BEGINNING, true, false);
		gridData.horizontalSpan = 2;
		acquisitionButtonsComposite.setLayoutData(gridData);
		acquisitionButtonsComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));
		toolkit.paintBordersFor(acquisitionButtonsComposite);

		Button startAcquicitionButton = toolkit.createButton(acquisitionButtonsComposite, "Start", SWT.PUSH);
		startAcquicitionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		startAcquicitionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					ExperimentModelHolder.INSTANCE.getLinerExperimentModel().doCollection();
				} catch (Exception e) {
					UIHelper.showError("Unable to scan", e.getMessage());
				}
			}
		});

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(startAcquicitionButton),
				BeanProperties.value(TimeResolvedExperimentModel.SCANNING_PROP_NAME).observe(ExperimentModelHolder.INSTANCE.getLinerExperimentModel()),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return (!(boolean) value);
					}
				});

		Button stopAcquicitionButton = toolkit.createButton(acquisitionButtonsComposite, "Stop", SWT.PUSH);
		stopAcquicitionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(stopAcquicitionButton),
				BeanProperties.value(TimeResolvedExperimentModel.SCANNING_PROP_NAME).observe(ExperimentModelHolder.INSTANCE.getLinerExperimentModel()));
		stopAcquicitionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				ExperimentModelHolder.INSTANCE.getLinerExperimentModel().doStop();
			}
		});

		//Sample stage motors

		sampleMotorsComposite = new SampleStageMotorsComposite(parent, SWT.None, toolkit, true);
	}

	private void createGroupSection(Composite parent) {
		timingGroupSectionComposite = new TimingGroupSectionComposite(parent, SWT.None, toolkit, ExperimentModelHolder.INSTANCE.getLinerExperimentModel());
		timingGroupSectionComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		toolkit.paintBordersFor(timingGroupSectionComposite);
	}

	private void createTimeBarComposite(Composite parent) {
		timebarViewerComposite = new ExperimentTimeBarComposite(parent, SWT.None, ExperimentModelHolder.INSTANCE.getLinerExperimentModel());
		timebarViewerComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		MenuManager menuManager = new MenuManager();
		Menu menu = menuManager.createContextMenu(timebarViewerComposite.getTimeBarViewer());
		// Set the MenuManager
		timebarViewerComposite.getTimeBarViewer().setMenu(menu);
		getSite().registerContextMenu(menuManager, timebarViewerComposite.getTimeBarViewer());
		getSite().setSelectionProvider(timebarViewerComposite.getTimeBarViewer());
	}

	@Override
	public void setFocus() {
		timebarViewerComposite.setFocus();
	}

	@Override
	public void dispose() {
		sampleMotorsComposite.dispose();
		super.dispose();
	}
}

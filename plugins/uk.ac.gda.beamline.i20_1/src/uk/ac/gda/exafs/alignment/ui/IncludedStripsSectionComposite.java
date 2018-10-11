/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.alignment.ui;

import java.beans.PropertyChangeListener;

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.databinding.viewers.ViewersObservables;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.ComboViewer;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.CCombo;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.detector.EdeDetector;
import uk.ac.gda.client.ResourceComposite;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.data.DetectorModel;

public class IncludedStripsSectionComposite extends ResourceComposite {

	private static final Logger logger = LoggerFactory.getLogger(IncludedStripsSectionComposite.class);

	private Section section;
	private final FormToolkit toolkit;
	private ComboViewer cmbFirstStripViewer;
	private ComboViewer cmbLastStripViewer;

	private Binding cmbFirstStripViewerBinding;
	private Binding cmbLastStripViewerBinding;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();


	public IncludedStripsSectionComposite(Composite parent, int style, FormToolkit toolkit) {
		super(parent, style);
		this.toolkit = toolkit;
		setupUI();
	}

	private void setupUI() {
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		section = toolkit.createSection(this, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		section.setText("Included strips");
		section.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Composite sectionComposite = toolkit.createComposite(section, SWT.NONE);
		sectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		toolkit.paintBordersFor(sectionComposite);
		section.setClient(sectionComposite);

		Composite stripsComposite = new Composite(sectionComposite, SWT.NONE);
		stripsComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, true));
		stripsComposite.setLayout(new GridLayout(4, false));

		final Label lblFirstStrip = toolkit.createLabel(stripsComposite, "First strip", SWT.NONE);
		lblFirstStrip.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		CCombo cmbFirstStrip = new CCombo(stripsComposite, SWT.BORDER | SWT.FLAT | SWT.READ_ONLY);
		cmbFirstStrip.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		cmbFirstStripViewer = new ComboViewer(cmbFirstStrip);
		cmbFirstStripViewer.setContentProvider(new ArrayContentProvider());
		cmbFirstStripViewer.setLabelProvider(new LabelProvider());
		cmbFirstStripViewer.setInput(DetectorModel.INSTANCE.getCurrentDetector().getPixels());

		Label lblLastStrip = toolkit.createLabel(stripsComposite, "Last strip", SWT.NONE);
		lblLastStrip.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		CCombo cmbLastStrip = new CCombo(stripsComposite, SWT.BORDER | SWT.FLAT | SWT.READ_ONLY);
		cmbLastStrip.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		cmbLastStripViewer = new ComboViewer(cmbLastStrip);
		cmbLastStripViewer.setContentProvider(new ArrayContentProvider());
		cmbLastStripViewer.setLabelProvider(new LabelProvider());
		cmbLastStripViewer.setInput(DetectorModel.INSTANCE.getCurrentDetector().getPixels());

		DetectorModel.INSTANCE.addPropertyChangeListener(DetectorModel.DETECTOR_CONNECTED_PROP_NAME, dectectorChangeListener);

		//TODO why the following extra 2 listeners is required to keep 2 instance of 'Included strips' in sync.
		DetectorModel.INSTANCE.addPropertyChangeListener(DetectorModel.LOWER_CHANNEL_PROP_NAME, event -> {
			cmbFirstStripViewer.setSelection(new StructuredSelection(event.getNewValue()));
		});

		DetectorModel.INSTANCE.addPropertyChangeListener(DetectorModel.UPPER_CHANNEL_PROP_NAME, event -> {
			cmbLastStripViewer.setSelection(new StructuredSelection(event.getNewValue()));
		});

		if (DetectorModel.INSTANCE.getCurrentDetector() != null) {
			bindUpperAndLowerChannelComboViewers();
		}

		if (DetectorModel.INSTANCE.getCurrentDetector() != null) {
			cmbFirstStripViewer.setSelection(new StructuredSelection(DetectorModel.INSTANCE.getCurrentDetector().getLowerChannel()));
			cmbLastStripViewer.setSelection(new StructuredSelection(DetectorModel.INSTANCE.getCurrentDetector().getUpperChannel()));
		}

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(cmbFirstStripViewer.getControl()),
				BeanProperties.value(DetectorModel.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorModel.INSTANCE));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(cmbLastStripViewer.getControl()),
				BeanProperties.value(DetectorModel.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorModel.INSTANCE));

		DetectorModel.INSTANCE.addPropertyChangeListener( event -> {
			if (event.getPropertyName().equals(DetectorModel.DETECTOR_CONNECTED_PROP_NAME)) {
				logger.debug("Updating strip combo boxes after detector change");
				updateStripCombosForDetector();
			}
		});
	}

	private void updateStripCombosForDetector() {
		final EdeDetector detector = DetectorModel.INSTANCE.getCurrentDetector();
		if (detector == null) {
			logger.warn("Cannot update upper, lower strip combo boxes - no detector has been set");
			return;
		}

		cmbLastStripViewer.setInput(detector.getPixels());
		cmbFirstStripViewer.setInput(detector.getPixels());
		cmbFirstStripViewer.setSelection(new StructuredSelection(detector.getLowerChannel()));
		cmbLastStripViewer.setSelection(new StructuredSelection(detector.getUpperChannel()));
	}

	private void bindUpperAndLowerChannelComboViewers() {
		cmbFirstStripViewerBinding = dataBindingCtx.bindValue(
				ViewersObservables.observeSingleSelection(cmbFirstStripViewer),
				BeanProperties.value(DetectorModel.LOWER_CHANNEL_PROP_NAME).observe(DetectorModel.INSTANCE));
		cmbLastStripViewerBinding = dataBindingCtx.bindValue(
				ViewersObservables.observeSingleSelection(cmbLastStripViewer),
				BeanProperties.value(DetectorModel.UPPER_CHANNEL_PROP_NAME).observe(DetectorModel.INSTANCE));
	}

	private final PropertyChangeListener dectectorChangeListener = event ->  {
		boolean detectorConnected = (boolean) event.getNewValue();
		if (detectorConnected) {
			bindUpperAndLowerChannelComboViewers();
		} else {
			if (cmbFirstStripViewerBinding != null) {
				dataBindingCtx.removeBinding(cmbFirstStripViewerBinding);
				cmbFirstStripViewerBinding.dispose();
				cmbFirstStripViewerBinding = null;
			}
			if (cmbLastStripViewerBinding != null) {
				dataBindingCtx.removeBinding(cmbLastStripViewerBinding);
				cmbLastStripViewerBinding.dispose();
				cmbLastStripViewerBinding = null;
			}
		}
	};

	@Override
	protected void disposeResource() {
		dataBindingCtx.dispose();
		DetectorModel.INSTANCE.removePropertyChangeListener(DetectorModel.DETECTOR_CONNECTED_PROP_NAME, dectectorChangeListener);
	}

}

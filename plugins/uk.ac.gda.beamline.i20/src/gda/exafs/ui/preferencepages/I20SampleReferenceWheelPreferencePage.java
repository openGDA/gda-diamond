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

package gda.exafs.ui.preferencepages;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.jface.preference.PreferencePage;
import org.eclipse.richbeans.api.binding.IBeanController;
import org.eclipse.richbeans.api.binding.IBeanService;
import org.eclipse.richbeans.widgets.selector.BeanSelectionEvent;
import org.eclipse.richbeans.widgets.selector.BeanSelectionListener;
import org.eclipse.richbeans.widgets.selector.VerticalListEditor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPreferencePage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.EditableEnumPositioner;
import gda.device.EnumPositioner;
import gda.factory.Finder;
import uk.ac.gda.beamline.i20.I20BeamlineActivator;
import uk.ac.gda.beans.exafs.i20.I20SampleParameters;
import uk.ac.gda.exafs.ExafsActivator;

public class I20SampleReferenceWheelPreferencePage extends PreferencePage implements IWorkbenchPreferencePage {
	private static final Logger logger = LoggerFactory.getLogger(I20SampleReferenceWheelPreferencePage.class);
	public static final String ID = "gda.exafs.ui.preferences.i20samplewheelPreferencePage";

	public I20SampleReferenceWheelPreferencePage() {
		setDescription("View and change the names of the filter positions");
		setPreferenceStore(ExafsActivator.getDefault().getPreferenceStore()); // Does nothing we store elements as XML.
	}

	private VerticalListEditor elementPositions;

	@Override
	protected Control createContents(Composite parent) {
		Composite main = new Composite(parent, SWT.NULL);
		GridLayout layout = new GridLayout();
		layout.numColumns = 1;
		layout.marginHeight = 0;
		layout.marginWidth = 0;
		main.setLayout(layout);
		main.setFont(parent.getFont());

		elementPositions = new VerticalListEditor(main, SWT.NONE);
		elementPositions.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false, 1, 1));
		elementPositions.setNameField("label");
		elementPositions.setEditorClass(PositionerLabelBean.class);

		final PositionerLabelComposite positionerLabelComposite = new PositionerLabelComposite(elementPositions, SWT.NONE);
		elementPositions.setEditorUI(positionerLabelComposite);
		elementPositions.setTemplateName("label");
		elementPositions.setColumnWidths(new int[] { 150 });
		elementPositions.setListWidth(400);
		elementPositions.on();

		elementPositions.addBeanSelectionListener(new BeanSelectionListener() {
			@Override
			public void selectionChanged(BeanSelectionEvent evt) {
				positionerLabelComposite.selectionChanged((PositionerLabelBean)evt.getSelectedBean());
			}
		});
		performDefaults();
		return main;
	}

	@Override
	public Point doComputeSize() {
		return new Point(600, 300);
	}

	// protected void performValidate() {
	// final SampleElements elements = new SampleElements();
	// try {
	// BeanUI.uiToBean(this, elements);
	//
	// final List<Integer> positions = new ArrayList<Integer>(Math.max(1,elements.getElementPositions().size()));
	// for (ElementPosition pos : elements.getElementPositions()) {
	// if (pos.getName()==null) {
	// setErrorMessage("There is a reference sample without a name specified.");
	// setValid(false);
	// return;
	// }
	// if (pos.getPrincipleElement()==null) {
	// setErrorMessage("The reference sample '"+pos.getName()+"' does not have an element supplied.");
	// setValid(false);
	// return;
	// }
	// if (pos.getWheelPosition()==null||pos.getWheelPosition()<1) {
	// setErrorMessage("The wheel position for '"+pos.getName()+"' is zero.");
	// setValid(false);
	// return;
	// }
	// if (positions.contains(pos.getWheelPosition())) {
	// setErrorMessage("The wheel position for '"+pos.getName()+"' is not unique.");
	// setValid(false);
	// return;
	// }
	// positions.add(pos.getWheelPosition());
	// }
	//
	// setErrorMessage(null);
	// setValid(true);
	//
	// } catch (Exception e) {
	// logger.error("Cannot validate.", e);
	// }
	// }

	/*
	 * (non-Javadoc)
	 * @see org.eclipse.jface.preference.IPreferencePage#performOk()
	 */
	@Override
	public boolean performOk() {
		try {
			final PositionerLabels elements = new PositionerLabels();

			IBeanService service = (IBeanService) I20BeamlineActivator.getService(IBeanService.class);
			IBeanController control = service.createController(this, elements);
			control.uiToBean();
			final List<String> labels = new ArrayList<>();

			for (PositionerLabelBean bean : elements.getLabels()) {
				labels.add(bean.getLabel());
			}

			EditableEnumPositioner sampleWheel = Finder.find(I20SampleParameters.SAMPLE_WHEEL_NAME);

			sampleWheel.setPositions(labels);

			return true;
		} catch (Exception e) {
			logger.error("Cannot get bean.", e);
			return false;
		}
	}

	@Override
	protected void performApply() {
		performOk();
		super.performApply();
	}

	@Override
	public boolean performCancel() {
		performDefaults();
		return super.performCancel();
	}

	@Override
	protected void performDefaults() {

		try {
			EnumPositioner sampleWheel = Finder.find(I20SampleParameters.SAMPLE_WHEEL_NAME);
			String[] labels = sampleWheel.getPositions();

			PositionerLabels elements = new PositionerLabels();

			for (String label : labels) {
				elements.addLabel(new PositionerLabelBean(label));
			}

			IBeanService service = (IBeanService) I20BeamlineActivator.getService(IBeanService.class);
			IBeanController control = service.createController(this, elements);
			control.beanToUI();
		} catch (Exception e) {
			logger.error("Cannot get defaults.", e);
		}

		// try {
		// XMLCommandHandler xmlCommandHandler =
		// ExperimentBeanManager.INSTANCE.getXmlCommandHandler(SampleElements.class);
		// final SampleElements templateParameters = (SampleElements)xmlCommandHandler.getTemplateParameters();
		// BeanUI.beanToUI(templateParameters, this);
		//
		// } catch (Exception e) {
		// logger.error("Cannot get defaults.", e);
		// }

		// // re-read the enumpositioner and reset the table
		// EnumPositioner sampleWheel = Finder.find(I20SampleParameters.SAMPLE_WHEEL_NAME);
		// String [] labels = sampleWheel.getPositions();
		//
		// elementPositions.set

		super.performDefaults();
	}

	/**
	 * @return Returns the elementPositions.
	 */
	public VerticalListEditor getElementPositions() {
		return elementPositions;
	}

	public VerticalListEditor getLabels() {
		return elementPositions;
	}

	@Override
	public void init(IWorkbench workbench) {
		// TODO Auto-generated method stub

	}

}

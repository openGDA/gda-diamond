/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.ui;

import java.net.URL;

import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.ui.composites.TimeFrameComposite;
import uk.ac.gda.exafs.ui.data.TFGParameters;
import uk.ac.gda.exafs.ui.data.TimeFrame;
import uk.ac.gda.exafs.ui.views.I20PlotViewManager;
import uk.ac.gda.richbeans.beans.BeanUI;
import uk.ac.gda.richbeans.components.FieldComposite;
import uk.ac.gda.richbeans.components.selector.BeanSelectionEvent;
import uk.ac.gda.richbeans.components.selector.BeanSelectionListener;
import uk.ac.gda.richbeans.components.selector.HorizontalListEditor;
import uk.ac.gda.richbeans.components.wrappers.BooleanWrapper;
import uk.ac.gda.richbeans.editors.DirtyContainer;
import uk.ac.gda.richbeans.editors.RichBeanEditorPart;
import uk.ac.gda.richbeans.event.ValueAdapter;
import uk.ac.gda.richbeans.event.ValueEvent;

public final class TFGParametersUIEditor extends RichBeanEditorPart {

	private static final Logger logger = LoggerFactory.getLogger(TFGParametersUIEditor.class);

	private BooleanWrapper autoRearm;
	private Composite contents;
	private HorizontalListEditor timeFramesEditor;

	public TFGParametersUIEditor(String path, URL mappingURL, DirtyContainer dirtyContainer, Object editingBean) {
		super(path, mappingURL, dirtyContainer, editingBean);
	}

	@Override
	public String getRichEditorTabText() {
		return "TFGParameters";
	}

	@Override
	public void createPartControl(Composite comp) {

		contents = new Composite(comp, SWT.NONE);
		contents.setLayout(new GridLayout(1,true));

		this.autoRearm = new BooleanWrapper(contents, SWT.NONE);
		autoRearm.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false, 1, 1));
		autoRearm.setText("Auto Re-arm");

		Group framesGroup = new Group(contents, SWT.NONE);
		framesGroup.setText("Timing Groups");
		framesGroup.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false, 1, 1));
		framesGroup.setLayout(new GridLayout(1, false));

		timeFramesEditor = new HorizontalListEditor(framesGroup, SWT.NONE);
		timeFramesEditor.setTemplateName("TimeFrame");
		timeFramesEditor.setEditorClass(TimeFrame.class);
		timeFramesEditor.setNameField("Label");
		timeFramesEditor.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		timeFramesEditor.setMinItems(1);
		timeFramesEditor.setListWidth(100);

		final TimeFrameComposite groupParameters = new TimeFrameComposite(timeFramesEditor, SWT.NONE);
		timeFramesEditor.setEditorUI(groupParameters);

		timeFramesEditor.addBeanSelectionListener(new BeanSelectionListener() {
			@Override
			public void selectionChanged(BeanSelectionEvent evt) {
				groupParameters.selectionChanged((TimeFrame) evt.getSelectedBean());
				updatePlottedPoints();
			}
		});
		
		timeFramesEditor.pack();
		
		comp.layout();
	}

	@Override
	public void setFocus() {
		if (timeFramesEditor != null) {
			timeFramesEditor.setFocus();
			updatePlottedPoints();
		}
	}

	public FieldComposite getAutoRearm() {
		return autoRearm;
	}

	public HorizontalListEditor getTimeFrames() {
		return timeFramesEditor;
	}
	
	@Override
	public void linkUI(final boolean isPageChange) {

		super.linkUI(isPageChange);

		try {
			BeanUI.addValueListener(editingBean, this, new ValueAdapter() {
				@Override
				public void valueChangePerformed(ValueEvent e) {
					getSite().getShell().getDisplay().asyncExec(new Runnable() {
						@Override
						public void run() {
							updatePlottedPoints();
						}
					});
				}
			});
		} catch (Exception e) {
			// TODO Auto-generated catch block
			logger.error("TODO put description of error here", e);
		}

		// update plot initially
		updatePlottedPoints();

	}

	private void updatePlottedPoints() {
		// TODO Auto-generated method stub
		try {
			TFGParameters scanBean = (TFGParameters) editingBean.getClass().newInstance();
			BeanUI.uiToBean(this, scanBean);
			I20PlotViewManager.getInstance().updateGraph(scanBean,getSite(), timeFramesEditor.getSelectedIndex());
		} catch (InstantiationException e) {
			// TODO Auto-generated catch block
			logger.error("TODO put description of error here", e);
		} catch (IllegalAccessException e) {
			// TODO Auto-generated catch block
			logger.error("TODO put description of error here", e);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			logger.error("TODO put description of error here", e);
		}
	}

}

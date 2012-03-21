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
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.forms.events.ExpansionAdapter;
import org.eclipse.ui.forms.events.ExpansionEvent;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.ui.composites.TimingGroupComposite;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.exafs.ui.views.I20PlotViewManager;
import uk.ac.gda.richbeans.beans.BeanUI;
import uk.ac.gda.richbeans.components.FieldComposite;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;
import uk.ac.gda.richbeans.components.selector.BeanSelectionEvent;
import uk.ac.gda.richbeans.components.selector.BeanSelectionListener;
import uk.ac.gda.richbeans.components.selector.HorizontalListEditor;
import uk.ac.gda.richbeans.components.wrappers.ComboWrapper;
import uk.ac.gda.richbeans.components.wrappers.SpinnerWrapper;
import uk.ac.gda.richbeans.editors.DirtyContainer;
import uk.ac.gda.richbeans.editors.RichBeanEditorPart;
import uk.ac.gda.richbeans.event.ValueAdapter;
import uk.ac.gda.richbeans.event.ValueEvent;

/**
 * @author rjw82
 */
public final class EdeScanParametersUIEditor extends RichBeanEditorPart {

	private static final Logger logger = LoggerFactory.getLogger(EdeScanParametersUIEditor.class);

	private SpinnerWrapper numberOfRepetitions;
	private ScaleBox delayBetweenRepetitions;

	private HorizontalListEditor timingGroups;

	private ComboWrapper outputsChoice0;
	private ComboWrapper outputsChoice1;
	private ComboWrapper outputsChoice2;
	private ComboWrapper outputsChoice3;
	private ComboWrapper outputsChoice4;
	private ComboWrapper outputsChoice5;
	private ComboWrapper outputsChoice6;
	private ComboWrapper outputsChoice7;

	private ScaleBox outputsWidth0;
	private ScaleBox outputsWidth1;
	private ScaleBox outputsWidth2;
	private ScaleBox outputsWidth3;
	private ScaleBox outputsWidth4;
	private ScaleBox outputsWidth5;
	private ScaleBox outputsWidth6;
	private ScaleBox outputsWidth7;

	private ComboWrapper edgeChoice0;
	private ComboWrapper edgeChoice1;
	private ComboWrapper edgeChoice2;
	private ComboWrapper edgeChoice3;
	private ComboWrapper edgeChoice4;
	private ComboWrapper edgeChoice5;
	private ComboWrapper edgeChoice6;
	private ComboWrapper edgeChoice7;

	private ScrolledComposite scrolledComposite;
	private ExpandableComposite outputsComposite;
	private Composite contents;
	private Group framesGroup;

	public EdeScanParametersUIEditor(String path, URL mappingURL, DirtyContainer dirtyContainer, Object editingBean) {
		super(path, mappingURL, dirtyContainer, editingBean);
	}

	@Override
	public void createPartControl(Composite comp) {

		comp.setData(this);

		scrolledComposite = new ScrolledComposite(comp, SWT.H_SCROLL | SWT.V_SCROLL);
		scrolledComposite.setExpandHorizontal(true);
		scrolledComposite.setExpandVertical(true);
		scrolledComposite.setLayout(new GridLayout(1, false));
		scrolledComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		contents = new Composite(scrolledComposite, SWT.NONE);
		contents.setLayout(new GridLayout(1, false));
		contents.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		createTimingGroupsComposite(contents);

		createOutputsComposite(contents);

		scrolledComposite.setContent(contents);
	}

	private void createTimingGroupsComposite(final Composite contents) {
		framesGroup = new Group(contents, SWT.NONE);
		framesGroup.setText("Timing Groups");
		framesGroup.setLayoutData(new GridData(SWT.FILL, SWT.TOP, false, false));
		framesGroup.setLayout(new GridLayout(1, false));

		timingGroups = new HorizontalListEditor(framesGroup, SWT.NONE);
		timingGroups.setTemplateName("TimingGroup");
		timingGroups.setEditorClass(TimingGroup.class);
		timingGroups.setNameField("Label");
		timingGroups.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false));
		timingGroups.setMinItems(1);
		timingGroups.setListWidth(100);

		final TimingGroupComposite groupParameters = new TimingGroupComposite(this, framesGroup, SWT.NONE);
		groupParameters.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, true, 1, 2));
		timingGroups.setEditorUI(groupParameters);

		timingGroups.addBeanSelectionListener(new BeanSelectionListener() {
			@Override
			public void selectionChanged(BeanSelectionEvent evt) {
				groupParameters.selectionChanged((TimingGroup) evt.getSelectedBean());
				updatePlottedPoints();
			}
		});

		framesGroup.pack();
	}

	private void createOutputsComposite(final Composite contents) {
		outputsComposite = new ExpandableComposite(contents, ExpandableComposite.COMPACT | ExpandableComposite.TWISTIE
				| SWT.BORDER);
		outputsComposite.setText("Define Output Signals");
		outputsComposite.addExpansionListener(new ExpansionAdapter() {
			@Override
			public void expansionStateChanged(ExpansionEvent e) {
				updateLayout();
			}
		});

		final Composite outputsArea = new Composite(outputsComposite, SWT.NONE);
		outputsArea.setLayout(new GridLayout(6, false));
		outputsArea.setLayoutData(new GridData(SWT.FILL, SWT.FILL, false, false));

		outputsComposite.setClient(outputsArea);

		GridData comboGridData = new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1);
		comboGridData.widthHint = 250;

		Label lbl0 = new Label(outputsArea, SWT.NONE);
		lbl0.setText("LEMO 0");
		outputsChoice0 = new ComboWrapper(outputsArea, SWT.NONE);
		outputsChoice0.setItems(EdeScanParameters.OUTPUT_TRIG_CHOICES);
		outputsChoice0.select(0);
		outputsChoice0.setLayoutData(comboGridData);
		outputsWidth0 = createDelayLabel(outputsArea);

		Label lbl1 = new Label(outputsArea, SWT.NONE);
		lbl1.setText("LEMO 1");
		outputsChoice1 = new ComboWrapper(outputsArea, SWT.NONE);
		outputsChoice1.setItems(EdeScanParameters.OUTPUT_TRIG_CHOICES);
		outputsChoice1.select(0);
		outputsChoice1.setLayoutData(comboGridData);
		outputsWidth1 = createDelayLabel(outputsArea);

		Label lbl2 = new Label(outputsArea, SWT.NONE);
		lbl2.setText("LEMO 2");
		outputsChoice2 = new ComboWrapper(outputsArea, SWT.NONE);
		outputsChoice2.setItems(EdeScanParameters.OUTPUT_TRIG_CHOICES);
		outputsChoice2.select(0);
		outputsChoice2.setLayoutData(comboGridData);
		outputsWidth2 = createDelayLabel(outputsArea);

		Label lbl3 = new Label(outputsArea, SWT.NONE);
		lbl3.setText("LEMO 3");
		outputsChoice3 = new ComboWrapper(outputsArea, SWT.NONE);
		outputsChoice3.setItems(EdeScanParameters.OUTPUT_TRIG_CHOICES);
		outputsChoice3.select(0);
		outputsChoice3.setLayoutData(comboGridData);
		outputsWidth3 = createDelayLabel(outputsArea);

		Label lbl4 = new Label(outputsArea, SWT.NONE);
		lbl4.setText("LEMO 4");
		outputsChoice4 = new ComboWrapper(outputsArea, SWT.NONE);
		outputsChoice4.setItems(EdeScanParameters.OUTPUT_TRIG_CHOICES);
		outputsChoice4.select(0);
		outputsChoice4.setLayoutData(comboGridData);
		outputsWidth4 = createDelayLabel(outputsArea);

		Label lbl5 = new Label(outputsArea, SWT.NONE);
		lbl5.setText("LEMO 5");
		outputsChoice5 = new ComboWrapper(outputsArea, SWT.NONE);
		outputsChoice5.setItems(EdeScanParameters.OUTPUT_TRIG_CHOICES);
		outputsChoice5.select(0);
		outputsChoice5.setLayoutData(comboGridData);
		outputsWidth5 = createDelayLabel(outputsArea);

		Label lbl6 = new Label(outputsArea, SWT.NONE);
		lbl6.setText("LEMO 6");
		outputsChoice6 = new ComboWrapper(outputsArea, SWT.NONE);
		outputsChoice6.setItems(EdeScanParameters.OUTPUT_TRIG_CHOICES);
		outputsChoice6.select(0);
		outputsChoice6.setLayoutData(comboGridData);
		outputsWidth6 = createDelayLabel(outputsArea);

		Label lbl7 = new Label(outputsArea, SWT.NONE);
		lbl7.setText("LEMO 7");
		outputsChoice7 = new ComboWrapper(outputsArea, SWT.NONE);
		outputsChoice7.setItems(EdeScanParameters.OUTPUT_TRIG_CHOICES);
		outputsChoice7.select(0);
		outputsChoice7.setLayoutData(comboGridData);
		outputsWidth7 = createDelayLabel(outputsArea);
	}

	private ScaleBox createDelayLabel(Composite delaysGroup) {
		ScaleBox sb = new ScaleBox(delaysGroup, SWT.NONE);
		sb.setUnit("s");
		sb.setValue(0.0);
		sb.setToolTipText("width of signal (s)");
		GridData gd = new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1);
		gd.widthHint = 100;
		sb.setLayoutData(gd);
		return sb;
	}

	public void updateLayout() {
		scrolledComposite.setMinSize(contents.computeSize(SWT.DEFAULT, SWT.DEFAULT));
		scrolledComposite.pack();
		scrolledComposite.layout();
	}

	@Override
	public String getRichEditorTabText() {
		return "EDE Scan";
	}

	@Override
	public void setFocus() {
		if (timingGroups != null) {
			timingGroups.setFocus();
			updatePlottedPoints();
		}
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
			EdeScanParameters scanBean = (EdeScanParameters) editingBean.getClass().newInstance();
			BeanUI.uiToBean(this, scanBean);
			I20PlotViewManager.getInstance().updateGraph(scanBean, getSite(), timingGroups.getSelectedIndex());
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

	public FieldComposite getNumberOfRepetitions() {
		return numberOfRepetitions;
	}

	public FieldComposite getDelayBetweenRepetitions() {
		return delayBetweenRepetitions;
	}

	public HorizontalListEditor getTimingGroups() {
		return timingGroups;
	}

	public ComboWrapper getOutputsChoice0() {
		return outputsChoice0;
	}

	public ComboWrapper getOutputsChoice1() {
		return outputsChoice1;
	}

	public ComboWrapper getOutputsChoice2() {
		return outputsChoice2;
	}

	public ComboWrapper getOutputsChoice3() {
		return outputsChoice3;
	}

	public ComboWrapper getOutputsChoice4() {
		return outputsChoice4;
	}

	public ComboWrapper getOutputsChoice5() {
		return outputsChoice5;
	}

	public ComboWrapper getOutputsChoice6() {
		return outputsChoice6;
	}

	public ComboWrapper getOutputsChoice7() {
		return outputsChoice7;
	}

	public ScaleBox getOutputsWidth0() {
		return outputsWidth0;
	}

	public ScaleBox getOutputsWidth1() {
		return outputsWidth1;
	}

	public ScaleBox getOutputsWidth2() {
		return outputsWidth2;
	}

	public ScaleBox getOutputsWidth3() {
		return outputsWidth3;
	}

	public ScaleBox getOutputsWidth4() {
		return outputsWidth4;
	}

	public ScaleBox getOutputsWidth5() {
		return outputsWidth5;
	}

	public ScaleBox getOutputsWidth6() {
		return outputsWidth6;
	}

	public ScaleBox getOutputsWidth7() {
		return outputsWidth7;
	}

	public ComboWrapper getEdgeChoice0() {
		return edgeChoice0;
	}

	public ComboWrapper getEdgeChoice1() {
		return edgeChoice1;
	}

	public ComboWrapper getEdgeChoice2() {
		return edgeChoice2;
	}

	public ComboWrapper getEdgeChoice3() {
		return edgeChoice3;
	}

	public ComboWrapper getEdgeChoice4() {
		return edgeChoice4;
	}

	public ComboWrapper getEdgeChoice5() {
		return edgeChoice5;
	}

	public ComboWrapper getEdgeChoice6() {
		return edgeChoice6;
	}

	public ComboWrapper getEdgeChoice7() {
		return edgeChoice7;
	}
}

/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.ui.composites;

import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.forms.events.ExpansionAdapter;
import org.eclipse.ui.forms.events.ExpansionEvent;
import org.eclipse.ui.forms.widgets.ExpandableComposite;

import uk.ac.gda.exafs.ui.EdeScanParametersUIEditor;
import uk.ac.gda.exafs.ui.data.TimingGroup;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;
import uk.ac.gda.richbeans.components.wrappers.BooleanWrapper;
import uk.ac.gda.richbeans.components.wrappers.SpinnerWrapper;
import uk.ac.gda.richbeans.components.wrappers.TextWrapper;
import uk.ac.gda.richbeans.event.ValueAdapter;
import uk.ac.gda.richbeans.event.ValueEvent;

/**
 * UI to define a single timing group.
 * <p>
 * A group defines a series of identical frames, each of which gives a single MCA. To improve stats without maxing out
 * the MCAs, each frame is built from a series of scans.
 * 
 * @author rjw82
 */
public final class TimingGroupComposite extends Composite {

	private TextWrapper label;
	private Text numberOfScans;
	private ScaleBox timePerScan;
	private ScaleBox timePerFrame;
	private SpinnerWrapper numberOfFrames;

	private ScaleBox preceedingTimeDelay;
	private ScaleBox delayBetweenFrames;

	private BooleanWrapper outLemo0;
	private BooleanWrapper outLemo1;
	private BooleanWrapper outLemo2;
	private BooleanWrapper outLemo3;
	private BooleanWrapper outLemo4;
	private BooleanWrapper outLemo5;
	private BooleanWrapper outLemo6;
	private BooleanWrapper outLemo7;

	private BooleanWrapper groupTrig;
	private BooleanWrapper allFramesTrig;
	private BooleanWrapper framesExclFirstTrig;
	private BooleanWrapper scansTrig;
	private SpinnerWrapper groupTrigLemo;
	private SpinnerWrapper allFramesTrigLemo;
	private SpinnerWrapper framesExclFirstTrigLemo;
	private SpinnerWrapper scansTrigLemo;
	private BooleanWrapper groupTrigRisingEdge;
	private BooleanWrapper allFramesTrigRisingEdge;
	private BooleanWrapper framesExclFirstTrigRisingEdge;
	private BooleanWrapper scansTrigRisingEdge;

	private ExpandableComposite delaysComposite;
	private ExpandableComposite outTrigComposite;
	private ExpandableComposite inTrigComposite;
	private EdeScanParametersUIEditor editor;

	public TimingGroupComposite(EdeScanParametersUIEditor edeScanParametersUIEditor, Composite parent, int style) {
		super(parent, style);

		setLayout(new GridLayout(1, false));

		editor = edeScanParametersUIEditor;

		setLayoutData(new GridData(SWT.FILL, SWT.FILL, false, false));

		createMainOptions();
		createDelays();
		createInputTriggers();
		createOutputTriggers();

		createListeners();
	}

	private void createDelays() {
		delaysComposite = new ExpandableComposite(this, ExpandableComposite.COMPACT | ExpandableComposite.TWISTIE
				| SWT.BORDER);
		delaysComposite.setText("Delays");
		delaysComposite.addExpansionListener(new ExpansionAdapter() {
			@Override
			public void expansionStateChanged(ExpansionEvent e) {
				updateLayout();
			}
		});

		final Composite delaysGroup = new Composite(delaysComposite, SWT.NONE);
		delaysGroup.setLayout(new GridLayout(2, false));
		delaysComposite.setClient(delaysGroup);

		this.preceedingTimeDelay = createDelayLabel(delaysGroup, "Before Group");
		this.delayBetweenFrames = createDelayLabel(delaysGroup, "Between Frames");

	}

	protected void updateLayout() {
		editor.updateLayout();
	}

	private ScaleBox createDelayLabel(Composite delaysGroup, String label) {
		ScaleBox scalebox = new ScaleBox(delaysGroup, SWT.NONE);
		GridData gd = new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1);
		gd.widthHint = 200;
		scalebox.setLayoutData(gd);
		scalebox.setLabel(label);
		scalebox.setUnit("s");
		scalebox.setMinimum(0.0);
		scalebox.setDecimalPlaces(6);
		scalebox.setValue(0.0);
		scalebox.setLabelWidth(120);
		return scalebox;
	}

	private void createOutputTriggers() {
		outTrigComposite = new ExpandableComposite(this, ExpandableComposite.COMPACT | ExpandableComposite.TWISTIE
				| SWT.BORDER);
		outTrigComposite.setText("Enable Output Signals");
		outTrigComposite.addExpansionListener(new ExpansionAdapter() {
			@Override
			public void expansionStateChanged(ExpansionEvent e) {
				updateLayout();
			}
		});

		final Composite tiggersGroup = new Composite(outTrigComposite, SWT.NONE);
		tiggersGroup.setLayout(new GridLayout(8, false));
		tiggersGroup.setSize(250, 160);
		tiggersGroup.setToolTipText("Outputs are defined below. They are the same for all timing groups");
		outTrigComposite.setClient(tiggersGroup);

		outLemo0 = new BooleanWrapper(tiggersGroup, SWT.NONE);
		outLemo0.setText("LEMO 0");
		outLemo1 = new BooleanWrapper(tiggersGroup, SWT.NONE);
		outLemo1.setText("LEMO 1");
		outLemo2 = new BooleanWrapper(tiggersGroup, SWT.NONE);
		outLemo2.setText("LEMO 2");
		outLemo3 = new BooleanWrapper(tiggersGroup, SWT.NONE);
		outLemo3.setText("LEMO 3");
		outLemo4 = new BooleanWrapper(tiggersGroup, SWT.NONE);
		outLemo4.setText("LEMO 4");
		outLemo5 = new BooleanWrapper(tiggersGroup, SWT.NONE);
		outLemo5.setText("LEMO 5");
		outLemo6 = new BooleanWrapper(tiggersGroup, SWT.NONE);
		outLemo6.setText("LEMO 6");
		outLemo7 = new BooleanWrapper(tiggersGroup, SWT.NONE);
		outLemo7.setText("LEMO 7");
	}

	private void createInputTriggers() {
		inTrigComposite = new ExpandableComposite(this, ExpandableComposite.COMPACT | ExpandableComposite.TWISTIE
				| SWT.BORDER);
		inTrigComposite.setText("Input Triggers");
		inTrigComposite.addExpansionListener(new ExpansionAdapter() {
			@Override
			public void expansionStateChanged(ExpansionEvent e) {
				updateLayout();
			}
		});

		final Composite tiggersGroup = new Composite(inTrigComposite, SWT.NONE);
		tiggersGroup.setLayout(new GridLayout(8, false));
		tiggersGroup.setSize(360, 160);
		inTrigComposite.setClient(tiggersGroup);

		groupTrig = new BooleanWrapper(tiggersGroup, SWT.NONE);
		groupTrig.setText("Group");
		final Label lemoLbl = new Label(tiggersGroup, SWT.NONE);
		lemoLbl.setText("LEMO");
		lemoLbl.setEnabled(false);
		groupTrigLemo = new SpinnerWrapper(tiggersGroup, SWT.BORDER | SWT.SINGLE);
		groupTrigLemo.setToolTipText("LEMO input channel for this trigger");
		groupTrigLemo.setMinimum(0);
		groupTrigLemo.setMaximum(6);
		groupTrigLemo.setEnabled(false);
		groupTrigRisingEdge = new BooleanWrapper(tiggersGroup, SWT.NONE);
		groupTrigRisingEdge.setText("Rising edge");
		groupTrigRisingEdge.setToolTipText("Trigger off the rising edge");
		groupTrigRisingEdge.setValue(true);
		groupTrigRisingEdge.setEnabled(false);
		groupTrig.addValueListener(new ValueAdapter() {

			@Override
			public void valueChangePerformed(ValueEvent e) {
				if (e.getValue() instanceof Boolean) {
					Boolean selected = (Boolean) e.getValue();
					lemoLbl.setEnabled(selected);
					groupTrigLemo.setEnabled(selected);
					groupTrigRisingEdge.setEnabled(selected);

				}

			}
		});

		framesExclFirstTrig = new BooleanWrapper(tiggersGroup, SWT.NONE);
		framesExclFirstTrig.setText("Frames (excl first)");
		final Label lemoLbl2 = new Label(tiggersGroup, SWT.NONE);
		lemoLbl2.setText("LEMO");
		lemoLbl2.setEnabled(false);
		framesExclFirstTrigLemo = new SpinnerWrapper(tiggersGroup, SWT.BORDER | SWT.SINGLE);
		framesExclFirstTrigLemo.setToolTipText("LEMO input channel for this trigger");
		framesExclFirstTrigLemo.setMinimum(0);
		framesExclFirstTrigLemo.setMaximum(6);
		framesExclFirstTrigLemo.setEnabled(false);
		framesExclFirstTrigRisingEdge = new BooleanWrapper(tiggersGroup, SWT.NONE);
		framesExclFirstTrigRisingEdge.setText("Rising edge");
		framesExclFirstTrigRisingEdge.setToolTipText("Trigger off the rising edge");
		framesExclFirstTrigRisingEdge.setValue(true);
		framesExclFirstTrigRisingEdge.setEnabled(false);
		framesExclFirstTrig.addValueListener(new ValueAdapter() {

			@Override
			public void valueChangePerformed(ValueEvent e) {
				if (e.getValue() instanceof Boolean) {
					Boolean selected = (Boolean) e.getValue();
					lemoLbl2.setEnabled(selected);
					framesExclFirstTrigLemo.setEnabled(selected);
					framesExclFirstTrigRisingEdge.setEnabled(selected);

				}

			}
		});

		allFramesTrig = new BooleanWrapper(tiggersGroup, SWT.NONE);
		allFramesTrig.setText("All frames");
		final Label lemoLbl3 = new Label(tiggersGroup, SWT.NONE);
		lemoLbl3.setText("LEMO");
		lemoLbl3.setEnabled(false);
		allFramesTrigLemo = new SpinnerWrapper(tiggersGroup, SWT.BORDER | SWT.SINGLE);
		allFramesTrigLemo.setToolTipText("LEMO input channel for this trigger");
		allFramesTrigLemo.setMinimum(0);
		allFramesTrigLemo.setMaximum(6);
		allFramesTrigLemo.setEnabled(false);
		allFramesTrigRisingEdge = new BooleanWrapper(tiggersGroup, SWT.NONE);
		allFramesTrigRisingEdge.setText("Rising edge");
		allFramesTrigRisingEdge.setToolTipText("Trigger off the rising edge");
		allFramesTrigRisingEdge.setValue(true);
		allFramesTrigRisingEdge.setEnabled(false);
		allFramesTrig.addValueListener(new ValueAdapter() {

			@Override
			public void valueChangePerformed(ValueEvent e) {
				if (e.getValue() instanceof Boolean) {
					Boolean selected = (Boolean) e.getValue();
					lemoLbl3.setEnabled(selected);
					allFramesTrigLemo.setEnabled(selected);
					allFramesTrigRisingEdge.setEnabled(selected);

				}

			}
		});

		scansTrig = new BooleanWrapper(tiggersGroup, SWT.NONE);
		scansTrig.setText("Scans");
		final Label lemoLbl4 = new Label(tiggersGroup, SWT.NONE);
		lemoLbl4.setText("LEMO");
		lemoLbl4.setEnabled(false);
		scansTrigLemo = new SpinnerWrapper(tiggersGroup, SWT.BORDER | SWT.SINGLE);
		scansTrigLemo.setToolTipText("LEMO input channel for this trigger");
		scansTrigLemo.setMinimum(0);
		scansTrigLemo.setMaximum(6);
		scansTrigLemo.setEnabled(false);
		scansTrigRisingEdge = new BooleanWrapper(tiggersGroup, SWT.NONE);
		scansTrigRisingEdge.setText("Rising edge");
		scansTrigRisingEdge.setToolTipText("Trigger off the rising edge");
		scansTrigRisingEdge.setValue(true);
		scansTrigRisingEdge.setEnabled(false);
		scansTrig.addValueListener(new ValueAdapter() {

			@Override
			public void valueChangePerformed(ValueEvent e) {
				if (e.getValue() instanceof Boolean) {
					Boolean selected = (Boolean) e.getValue();
					lemoLbl4.setEnabled(selected);
					scansTrigLemo.setEnabled(selected);
					scansTrigRisingEdge.setEnabled(selected);

				}

			}
		});

	}

	@SuppressWarnings("unused")
	private void createMainOptions() {
		Composite mainOptions = new Composite(this, SWT.NONE);
		mainOptions.setLayout(new GridLayout(6, false));

		Label swtLabel = new Label(mainOptions, SWT.NONE);
		swtLabel.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		swtLabel.setText("Name");

		this.label = new TextWrapper(mainOptions, SWT.BORDER | SWT.SINGLE);
		this.label.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		this.label.setValue("<enter name>");

		swtLabel = new Label(mainOptions, SWT.NONE);
		swtLabel.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		swtLabel.setText("Time per Frame");
		// read-only, so have a different colour to make this clear
		// this.exposure = new StyledText(this, SWT.BORDER|SWT.SINGLE|SWT.READ_ONLY);
		// timePerFrame.setBackground(this.getDisplay().getSystemColor(SWT.COLOR_WIDGET_BACKGROUND));
		// timePerFrame.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		this.timePerFrame = new ScaleBox(mainOptions, SWT.NONE);
		timePerFrame.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		timePerFrame.setUnit("s");
		timePerFrame.setMinimum(0.0);
		timePerFrame.setValue(1);

		swtLabel = new Label(mainOptions, SWT.NONE);
		swtLabel.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		swtLabel.setText("Time Per Scan");
		this.timePerScan = new ScaleBox(mainOptions, SWT.NONE);
		timePerScan.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		timePerScan.setUnit("s");
		timePerScan.setDecimalPlaces(4);
		timePerScan.setMinimum(0.00000001); // 10ns minimum
		timePerScan.setValue(0.1);


		new Label(mainOptions, SWT.NONE);
		new Label(mainOptions, SWT.NONE);

		swtLabel = new Label(mainOptions, SWT.NONE);
		swtLabel.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		swtLabel.setText("Number Of Frames");
		this.numberOfFrames = new SpinnerWrapper(mainOptions, SWT.BORDER | SWT.SINGLE);
		numberOfFrames.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		numberOfFrames.setMinimum(1);
		numberOfFrames.setValue(1);

		swtLabel = new Label(mainOptions, SWT.NONE);
		swtLabel.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		swtLabel.setText("Scans per Frame");
		this.numberOfScans = new Text(mainOptions, SWT.BORDER | SWT.SINGLE);
		numberOfScans.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		// numberOfScans.setMinimum(1);
		// numberOfScans.setValue(1);
		numberOfScans.setEnabled(false);
	}

	private void createListeners() {
		timePerFrame.addValueListener(new ValueAdapter() {
			@Override
			public void valueChangePerformed(ValueEvent e) {
				updateExposurePerFrame();
			}
		});

		timePerScan.addValueListener(new ValueAdapter() {
			@Override
			public void valueChangePerformed(ValueEvent e) {
				updateExposurePerFrame();
			}
		});
	}

	protected void updateExposurePerFrame() {
		Double timePerScan = (Double) getTimePerScan().getValue();
		Double exposure = (Double) this.timePerFrame.getValue();
		if (exposure == null) {
			this.timePerFrame.setValue(1.0);
			return;
		}

		Double numScans = (exposure / timePerScan) - 100E-9;
		numberOfScans.setText(Long.toString(Math.round(numScans)));
	}

	/**
	 * Called when the selection in the enclosing ListEditor changes.
	 * 
	 * @param selectedBean
	 */
	public void selectionChanged(TimingGroup selectedBean) {

		if (selectedBean != null) {
			String labelValue = (String) label.getValue();

			Double scanTime = (Double) timePerScan.getValue();
			Double frameTime = (Double) timePerFrame.getValue();
			Integer numFrame = (Integer) numberOfFrames.getValue();

			Double preceedingDelay = (Double) preceedingTimeDelay.getValue();
			Double delayTime = (Double) delayBetweenFrames.getValue();

			Integer groupTrigLemoValue = (Integer) groupTrigLemo.getValue();
			Integer allFramesTrigLemoValue = (Integer) allFramesTrigLemo.getValue();
			Integer framesExclFirstTrigLemoValue = (Integer) framesExclFirstTrigLemo.getValue();
			Integer scansTrigLemoValue = (Integer) scansTrigLemo.getValue();

			selectedBean.setLabel(labelValue);

			selectedBean.setTimePerScan(scanTime);
			selectedBean.setTimePerFrame(frameTime);
			selectedBean.setNumberOfFrames(numFrame);

			selectedBean.setPreceedingTimeDelay(preceedingDelay);
			selectedBean.setDelayBetweenFrames(delayTime);

			selectedBean.setGroupTrig(groupTrig.getValue());
			selectedBean.setAllFramesTrig(allFramesTrig.getValue());
			selectedBean.setFramesExclFirstTrig(framesExclFirstTrig.getValue());
			selectedBean.setScansTrig(scansTrig.getValue());

			selectedBean.setGroupTrigLemo(groupTrigLemoValue);
			selectedBean.setAllFramesTrigLemo(allFramesTrigLemoValue);
			selectedBean.setFramesExclFirstTrigLemo(framesExclFirstTrigLemoValue);
			selectedBean.setScansTrigLemo(scansTrigLemoValue);

			selectedBean.setOutLemo0(outLemo0.getValue());
			selectedBean.setOutLemo1(outLemo1.getValue());
			selectedBean.setOutLemo2(outLemo2.getValue());
			selectedBean.setOutLemo3(outLemo3.getValue());
			selectedBean.setOutLemo4(outLemo4.getValue());
			selectedBean.setOutLemo5(outLemo5.getValue());
			selectedBean.setOutLemo6(outLemo6.getValue());
			selectedBean.setOutLemo7(outLemo7.getValue());
		}

		updateExposurePerFrame();
	}

	public TextWrapper getLabel() {
		return label;
	}

	public Text getNumberOfScans() {
		return numberOfScans;
	}

	public ScaleBox getTimePerScan() {
		return timePerScan;
	}

	public ScaleBox getTimePerFrame() {
		return timePerFrame;
	}

	public SpinnerWrapper getNumberOfFrames() {
		return numberOfFrames;
	}

	public ScaleBox getPreceedingTimeDelay() {
		return preceedingTimeDelay;
	}

	public ScaleBox getDelayBetweenFrames() {
		return delayBetweenFrames;
	}

	public BooleanWrapper getOutLemo0() {
		return outLemo0;
	}

	public BooleanWrapper getOutLemo1() {
		return outLemo1;
	}

	public BooleanWrapper getOutLemo2() {
		return outLemo2;
	}

	public BooleanWrapper getOutLemo3() {
		return outLemo3;
	}

	public BooleanWrapper getOutLemo4() {
		return outLemo4;
	}

	public BooleanWrapper getOutLemo5() {
		return outLemo5;
	}

	public BooleanWrapper getOutLemo6() {
		return outLemo6;
	}

	public BooleanWrapper getOutLemo7() {
		return outLemo7;
	}

	public BooleanWrapper getGroupTrig() {
		return groupTrig;
	}

	public BooleanWrapper getAllFramesTrig() {
		return allFramesTrig;
	}

	public BooleanWrapper getFramesExclFirstTrig() {
		return framesExclFirstTrig;
	}

	public BooleanWrapper getScansTrig() {
		return scansTrig;
	}

	public SpinnerWrapper getGroupTrigLemo() {
		return groupTrigLemo;
	}

	public SpinnerWrapper getAllFramesTrigLemo() {
		return allFramesTrigLemo;
	}

	public SpinnerWrapper getFramesExclFirstTrigLemo() {
		return framesExclFirstTrigLemo;
	}

	public SpinnerWrapper getScanTrigLemo() {
		return scansTrigLemo;
	}

	public BooleanWrapper getGroupTrigRisingEdge() {
		return groupTrigRisingEdge;
	}

	public BooleanWrapper getAllFramesTrigRisingEdge() {
		return allFramesTrigRisingEdge;
	}

	public BooleanWrapper getFramesExclFirstTrigRisingEdge() {
		return framesExclFirstTrigRisingEdge;
	}

	public BooleanWrapper getScansTrigRisingEdge() {
		return scansTrigRisingEdge;
	}

}

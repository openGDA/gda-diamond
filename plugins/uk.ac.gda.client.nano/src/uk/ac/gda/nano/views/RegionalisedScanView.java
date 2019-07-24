/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.nano.views;


import java.io.File;
import java.util.Vector;

import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.List;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.jython.InterfaceProvider;
import gda.jython.JythonServerStatus;
import gda.jython.JythonStatus;
import gda.observable.IObserver;

public class RegionalisedScanView extends ViewPart implements IObserver{

	/**
	 * The ID of the view as specified by the extension.
	 */
	public static final String ID = "uk.ac.gda.nano.views.RegionalisedScanView";
	private static final Logger logger = LoggerFactory.getLogger(RegionalisedScanView.class);

	private Composite guiBase;

	RScanParameterPaser parameterParser;
	String[] motorNames, detectorNames, monitorNames;

	Composite baseComposite;

	Combo motor;
	Vector<Combo> detectors = new Vector<Combo>();
	int numberOfRegions = 0;
	Vector<Text> regionStart = new Vector<Text>();
	Vector<Text> regionStop = new Vector<Text>();
	Vector<Text> regionStep = new Vector<Text>();

	int numberOfDetectors = 0;
	Vector<Text> collectionTimes = new Vector<Text>();

	Text monitors;

	Text commandText;

	Button scanButton;
	Button stopButton;
	Button pauseButton;

	public RegionalisedScanView() {
		super();
		//To register itself to be updated by the command server
		InterfaceProvider.getJSFObserver().addIObserver(this);

		//To get the device names from xml file
		File xmlFile = new File(LocalProperties.getConfigDir()+ "templates"+ System.getProperty("file.separator") + "RegionalisedScanParameters.xml");
		parameterParser = new RScanParameterPaser(xmlFile);
		motorNames=parameterParser.getDevices("Motors");
		detectorNames=this.parameterParser.getDevices("Detectors");
		monitorNames=parameterParser.getDevices("Monitors");
		}

	/**
	 * This is a callback that will allow us
	 * to create the viewer and initialize it.
	 */
	@Override
	public void createPartControl(Composite parent) {
		parent.setLayout(new FillLayout());
//		guiBase = new Composite(parent, SWT.SCROLL_LINE);
		ScrolledComposite sbase = new ScrolledComposite(parent, SWT.H_SCROLL | SWT.V_SCROLL);

		guiBase = new Composite(sbase, SWT.NONE);

		sbase.setContent(guiBase);
		sbase.setMinSize(600, 600);
		sbase.setExpandHorizontal(true);
		sbase.setExpandVertical(true);

//		guiBase = parent;
		this.createGUI(guiBase);

	}


	/**
	 * Passing the focus request to the viewer's control.
	 */
	@Override
	public void setFocus() {
		guiBase.setFocus();
	}

	public void createGUI(Composite base) {

		GridLayout baseLayout = new GridLayout();
		baseLayout.numColumns = 1;
		base.setLayout(baseLayout);

		Group motionGroup = new Group(base, SWT.NONE);
		motionGroup.setText("Motion");
		GridData gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		motionGroup.setLayoutData(gridData);
		addMotionSetting(motionGroup);

		Group regionSettingGroup = new Group(base, SWT.NONE);
		regionSettingGroup.setText("Regions");
		gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		regionSettingGroup.setLayoutData(gridData);
		addRegionSetting(regionSettingGroup);

		Group detectorAndMonitorSettingGroup = new Group(base, SWT.NONE);
//		detectorAndMonitorSettingGroup.setText("Detectors");
		gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		detectorAndMonitorSettingGroup.setLayoutData(gridData);
		addDetectorAndMonitorSetting(detectorAndMonitorSettingGroup);

		Group scanControlGroup = new Group(base, SWT.NONE);
		scanControlGroup.setText("Scan Control");
		gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		scanControlGroup.setLayoutData(gridData);
		addScanControls(scanControlGroup);

	}

	private void addMotionSetting(Group motionGroup){
		GridLayout gridLayout = new GridLayout();
		gridLayout.numColumns = 4;
		motionGroup.setLayout(gridLayout);

		new Label(motionGroup, SWT.NONE).setText("motor");
		motor = new Combo(motionGroup, SWT.NONE);
		motor.setItems(motorNames);
		motor.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		motor.select(0);
//		motor.setText(motor.getItem(0));
	}


	private void addRegionSetting(final Group settingGroup) {
		GridLayout gridLayout = new GridLayout();
		gridLayout.numColumns = 4;
		settingGroup.setLayout(gridLayout);

		new Label(settingGroup, SWT.NONE).setText("");
		new Label(settingGroup, SWT.NONE).setText("start");
		new Label(settingGroup, SWT.NONE).setText("stop");
		new Label(settingGroup, SWT.NONE).setText("step");

		addScanRegion(settingGroup);
		addScanRegion(settingGroup);
		addScanRegion(settingGroup);
		addScanRegion(settingGroup);
		addScanRegion(settingGroup);
		addScanRegion(settingGroup);

		setScanRegion(0, 100, 190, 10);
		setScanRegion(1, 200, 399, 1);
		setScanRegion(2, 400, 600, 10);

	}

	private void addScanRegion(Group settingGroup){
		GridData gridData;

		++numberOfRegions;
		new Label(settingGroup, SWT.NONE).setText( " " + numberOfRegions );

		Text rstart = new Text(settingGroup, SWT.SINGLE | SWT.BORDER);
		gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		gridData.horizontalSpan =1;
		rstart.setLayoutData(gridData);
		regionStart.add(rstart);

		Text rstop = new Text(settingGroup, SWT.SINGLE | SWT.BORDER);
		gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		gridData.horizontalSpan =1;
		rstop.setLayoutData(gridData);
		regionStop.add(rstop);

		Text rstep = new Text(settingGroup, SWT.SINGLE | SWT.BORDER);
		gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		gridData.horizontalSpan =1;
		rstep.setLayoutData(gridData);
		regionStep.add(rstep);
	}

	private void setScanRegion(int index, double start, double stop, double step){
		regionStart.get(index).setText(Double.toString(start));
		regionStop.get(index).setText(Double.toString(stop));
		regionStep.get(index).setText(Double.toString(step));
	}

	private void addDetectorAndMonitorSetting(Group settingGroup) {
		GridLayout gridLayout = new GridLayout();
		gridLayout.numColumns = 2;
		settingGroup.setLayout(gridLayout);

		GridData gridData;
		Group detectorSettingGroup = new Group(settingGroup, SWT.NONE);
		detectorSettingGroup.setText("Detectors");
		gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		gridData.horizontalSpan =1;
		detectorSettingGroup.setLayoutData(gridData);
		addDetectorSetting(detectorSettingGroup);


		Group monitorSettingGroup = new Group(settingGroup, SWT.NONE);
		monitorSettingGroup.setText("Monitors");
		gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		gridData.horizontalSpan =1;
		monitorSettingGroup.setLayoutData(gridData);
		addMonitorSetting(monitorSettingGroup);
	}

	private void addDetectorSetting(Group settingGroup) {

		GridLayout gridLayout = new GridLayout();
		gridLayout.numColumns = 2;
		settingGroup.setLayout(gridLayout);

		new Label(settingGroup, SWT.NONE).setText("");
//		new Label(settingGroup, SWT.NONE).setText("detectors");
		new Label(settingGroup, SWT.NONE).setText("integration time in second");

		addDetector(settingGroup);
		addDetector(settingGroup);
		addDetector(settingGroup);
	}

	private void addMonitorSetting(Group settingGroup) {
		GridLayout gridLayout = new GridLayout();
		gridLayout.numColumns = 2;
		settingGroup.setLayout(gridLayout);
		GridData gridData;

		new Label(settingGroup, SWT.NONE).setText("");
//		new Label(settingGroup, SWT.NONE).setText("Monitors");
		monitors = new Text(settingGroup, SWT.SINGLE | SWT.BORDER);
		gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		gridData.horizontalSpan =3;
		monitors.setLayoutData(gridData);

		final List monitorList = new List(settingGroup, SWT.MULTI | SWT.BORDER | SWT.V_SCROLL);
		monitorList.setItems(monitorNames);

		gridData = new GridData(GridData.FILL, GridData.FILL, true, true);
		gridData.verticalSpan = 4;
		gridData.horizontalSpan =3;
		int listHeight = monitorList.getItemHeight() * 2;
		Rectangle trim = monitorList.computeTrim(0, 0, 0, listHeight);
		gridData.heightHint = trim.height;
		monitorList.setLayoutData(gridData);

		monitorList.addSelectionListener(new SelectionAdapter(){
//			@Override
//			//For single click selection
//			public void widgetSelected(SelectionEvent event){
//				String[] selected = monitorList.getSelection();
//				if (selected.length >0){
//					System.out.println("Selected: " + selected[0]);
//				}
//
//			}
			@Override
			//For double click selection
			public void widgetDefaultSelected(SelectionEvent event){
				String[] selected = monitorList.getSelection();
				if (selected.length >0){
					String m = monitors.getText();
					if ( m.isEmpty() ){
						monitors.setText(selected[0]);
					}
					else{
						monitors.setText(m + " " + selected[0]);
					}
					logger.debug("Add the monitor selection: " + selected[0]);
				}

			}
		} );

	}
/*
	class MonitorListListener extends SelectionAdapter{
		public void widgetSelected(SelectionEvent evebt){
			String[] selected = this.list.getSelection();
			if (selected.length >0){
				System.out.println("Selected: " + selected[0]);
			}

		}

	}
*/
	private void addDetector(Group settingGroup){
		++numberOfDetectors;
//		new Label(settingGroup, SWT.NONE).setText( " " + numberOfDetectors );
//		Combo nd = new Combo(settingGroup, SWT.READ_ONLY);
		Combo nd = new Combo(settingGroup, SWT.NONE);
		nd.setItems(detectorNames);
		nd.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		detectors.add(nd);

		Text ct = new Text(settingGroup, SWT.SINGLE | SWT.BORDER);
		GridData gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		ct.setLayoutData(gridData);
		this.collectionTimes.add(ct);

	}

	private void addScanControls(Group scanControlGroup) {
		GridLayout gridLayout = new GridLayout();
		gridLayout.numColumns = 4;
		scanControlGroup.setLayout(gridLayout);
		GridData gridData;

		final Button validate;
		validate = new Button(scanControlGroup, SWT.PUSH);
		validate.setText("Create Scan Command");
		gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		gridData.horizontalSpan =1;
		validate.setLayoutData(gridData);
		validate.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				commandText.setText(getScanCommand());

			}
		});

		commandText = new Text(scanControlGroup, SWT.SINGLE | SWT.BORDER);
		gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		gridData.horizontalSpan = 3;
		commandText.setLayoutData(gridData);


		this.addScanButton(scanControlGroup);
		this.addStopButton(scanControlGroup);
		this.addPauseButton(scanControlGroup);

	}

	private void addScanButton(Group controlGroup){
		scanButton = new Button(controlGroup, SWT.PUSH);
		scanButton.setText("Scan");
		GridData gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		gridData.horizontalSpan =2;
//		gridData.horizontalIndent = 10;
		scanButton.setLayoutData(gridData);
		scanButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				runScan();

			}
		});

	}

	private void addStopButton(Group controlGroup){
		stopButton = new Button(controlGroup, SWT.PUSH);
		stopButton.setText("Stop");
		GridData gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		gridData.horizontalSpan =1;
//		gridData.horizontalIndent = 10;
		stopButton.setLayoutData(gridData);
		stopButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				stopScan();
			}
		});

	}

	private void addPauseButton(Group controlGroup){
		pauseButton = new Button(controlGroup, SWT.PUSH);
		pauseButton.setText("Pause");
		GridData gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		gridData.horizontalSpan =1;
//		gridData.horizontalIndent = 10;
		pauseButton.setLayoutData(gridData);
		pauseButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				if (pauseButton.getText().equalsIgnoreCase("Pause")){
					pauseScan();
					}
				else{
					resumeScan();
				}

			}
		});

	}

	private boolean isDoubleLike(String textInput){
		boolean parseable=false;
		if ( !textInput.isEmpty() ){
			try{
				Double.parseDouble(textInput);
				parseable=true;
				}catch (NumberFormatException e){
					logger.info("Text can not be parsed to double.");
				}

		}
		return parseable;
	}

	private String getScanCommand(){
//		String scanCommand="scat testMotor1 0 10 1 dummyCounter1 0.1";
		StringBuffer scanCommand = new StringBuffer();

		//To check the regions
		String start, stop, step;
		Vector<String> regions = new Vector<String>();

		if (this.motor.getText().isEmpty()){//No regional setting
			return "No motor to scan";
		}


		for(int i=0; i< this.numberOfRegions; i++){
			start = regionStart.get(i).getText();
			stop = regionStop.get(i).getText();
			step = regionStep.get(i).getText();

			if ( isDoubleLike(start) && isDoubleLike(stop)  && isDoubleLike(step) ){
				regions.add(new String("[" + start + " " + stop+ " "+ step + "]"));
			}
			else{
				logger.info("Wrong region values.");
				continue;
			}
		}

		//To assemble the motor with regions
		if (regions.isEmpty()){//No regional setting
			return "Wrong regional settings";
		}
		scanCommand.append("rscan " + this.motor.getText() + " (");

		for(String r: regions){
			scanCommand.append(r + ", ");
		}
		if(regions.size() == 1 ) //to remove the white space but keep the comma so that is is a python tuple
			scanCommand.deleteCharAt(scanCommand.length()-1);
		else//to remove the trailing comma and white space
			scanCommand.delete(scanCommand.length()-2, scanCommand.length());

		scanCommand.append(") ");

		String dn, dt;
		//To assemble detectors
		for(int i=0; i<this.numberOfDetectors; i++){
			dn=detectors.get(i).getText();
			dt=collectionTimes.get(i).getText();
			if (dn.isEmpty())
				continue;
			if ( !isDoubleLike(dt) ){
				logger.warn("Wrong integration time");
				continue;
			}

			scanCommand.append(dn + " " + dt + " ");
		}

		//To assemble monitors
		scanCommand.append(monitors.getText());

		return scanCommand.toString();

	}

	public void runScan(){
		if( InterfaceProvider.getScanStatusHolder().getScanStatus() != JythonStatus.IDLE){
			logger.warn("Can not run scan because there is a scan running or paused");
			return;
		}
		InterfaceProvider.getCommandRunner().runCommand(commandText.getText());
		logger.info("Scan running");
	}

	public void stopScan(){
		if( InterfaceProvider.getScanStatusHolder().getScanStatus() == JythonStatus.IDLE){
			return;
		}
		InterfaceProvider.getCurrentScanController().requestFinishEarly();
		logger.info("Scan stopped");
	}

	public void pauseScan(){
		if( InterfaceProvider.getScanStatusHolder().getScanStatus() == JythonStatus.RUNNING){
			InterfaceProvider.getCurrentScanController().pauseCurrentScan();
			logger.info("Scan paused");
		}
	}

	public void resumeScan(){
		if( InterfaceProvider.getScanStatusHolder().getScanStatus() == JythonStatus.PAUSED){
			InterfaceProvider.getCurrentScanController().resumeCurrentScan();
			logger.info("Scan running");
			}
	}


	/**
	 * From the IObservers interface.
	 * @param dataSource
	 *            Object
	 * @param dataPoint
	 *            Object
	 */
	@Override
	public void update(Object dataSource, Object dataPoint) {
		if (dataPoint instanceof JythonServerStatus) {
			JythonServerStatus status = (JythonServerStatus) dataPoint;

			switch(status.scanStatus){
			case IDLE:
				Display.getDefault().syncExec(new Runnable() {
				    @Override
					public void run() {
						scanButton.setEnabled(true);
						pauseButton.setEnabled(false);
				    }
				});
				break;

			case RUNNING:
				Display.getDefault().syncExec(new Runnable() {
				    @Override
					public void run() {
						scanButton.setEnabled(false);
						pauseButton.setEnabled(true);
						pauseButton.setText("Pause");
				    }
				});

				break;

			case PAUSED:
				Display.getDefault().syncExec(new Runnable() {
				    @Override
					public void run() {
						pauseButton.setText("Resume");
				    }
				});
				break;

			}

		}
	}


}
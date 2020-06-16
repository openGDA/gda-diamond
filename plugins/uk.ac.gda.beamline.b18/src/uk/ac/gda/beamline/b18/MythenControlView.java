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

package uk.ac.gda.beamline.b18;

import java.io.IOException;
import java.io.Serializable;
import java.util.Collections;
import java.util.Iterator;
import java.util.LinkedHashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import org.eclipse.richbeans.widgets.wrappers.TextWrapper;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.ProgressBar;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.NumTracker;
import gda.data.scan.datawriter.AsciiDataWriterConfiguration;
import gda.jython.JythonServerFacade;
import gda.observable.IObservable;
import gda.observable.IObserver;
import uk.ac.diamond.scisoft.analysis.PlotServer;
import uk.ac.diamond.scisoft.analysis.PlotServerProvider;
import uk.ac.diamond.scisoft.analysis.plotclient.IUpdateNotificationListener;
import uk.ac.diamond.scisoft.analysis.plotserver.DataBean;
import uk.ac.diamond.scisoft.analysis.plotserver.GuiBean;
import uk.ac.diamond.scisoft.analysis.plotserver.GuiParameters;
import uk.ac.diamond.scisoft.analysis.plotserver.GuiPlotMode;
import uk.ac.diamond.scisoft.analysis.plotserver.GuiUpdate;
import uk.ac.diamond.scisoft.analysis.plotserver.IBeanScriptingManager;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.IPlotUI;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.PlotConsumer;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.PlotJob;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.PlotJobType;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.PlotWindow;
import uk.ac.diamond.scisoft.analysis.rcp.views.PlotViewConfig;

/**
 * Plot View is the main Analysis panel that can display any n-D scalar data it is the replacement of the Data Vector
 * panel inside the new RCP framework
 */
public class MythenControlView extends ViewPart implements IObserver, IObservable, IBeanScriptingManager,
		IUpdateNotificationListener {

	// Adding in some logging to help with getting this running
	private static final Logger logger = LoggerFactory.getLogger(MythenControlView.class);

	/**
	 * The extension point ID for 3rd party contribution
	 */
	public static final String ID = "uk.ac.diamond.scisoft.analysis.rcp.plotView";
	/**
	 * the ID of this view
	 */
	private String id;

	/**
	 * @return id
	 */
	public String getId() {
		return id;
	}

	private PlotWindow plotWindow;
	private PlotServer plotServer;
	private ExecutorService execSvc = null;
	private PlotConsumer plotConsumer = null;
	protected String plotViewName = "Plot View";
	private IPlotUI plotUI = null;
	private UUID plotID = null;
	private GuiBean guiBean = null;
	private boolean doPlotCalib;
	private Button plotCalib;
	private boolean acquired = false;
	String importCommand;
	String instantiateCommand;
	String acquireCommand;
	String plotRawCommand;
	String plotCalibCommand;
	String plotRawAndCalibCommand;
	String timeVal;
	TextWrapper time;
	private Set<IObserver> dataObservers = Collections.synchronizedSet(new LinkedHashSet<IObserver>());
	Button btnSet;
	ProgressBar progress;
	AsciiDataWriterConfiguration configuration;
	Label rawFileLocationLabel;

	/**
	 * @return plot UI
	 */
	public IPlotUI getPlotUI() {
		return plotUI;
	}

	private List<IObserver> observers = Collections.synchronizedList(new LinkedList<IObserver>());

	/**
	 * Default Constructor of the plot view
	 */

	public MythenControlView() {
		super();
		init();
	}

	/**
	 * Constructor which must be called by 3rd party extension to extension point
	 * "uk.ac.diamond.scisoft.analysis.rcp.plotView"
	 *
	 * @param id
	 */
	public MythenControlView(String id) {
		super();
		this.id = id;
		init();
	}

	private void init() {
		plotID = UUID.randomUUID();
		logger.info("Plot view uuid: {}", plotID);
		plotServer = PlotServerProvider.getPlotServer();
		plotServer.addIObserver(this);
		execSvc = Executors.newFixedThreadPool(2);
	}

	public void createMythen() {
		importCommand = "from MythenAcquisition import MythenAcquisition";
		instantiateCommand = "ma = MythenAcquisition()";
		JythonServerFacade.getInstance().runCommand(importCommand);
		try {
			Thread.sleep(250);
		} catch (InterruptedException e1) {
			e1.printStackTrace();
		}
		JythonServerFacade.getInstance().runCommand(instantiateCommand);

		try {
			Thread.sleep(250);
		} catch (InterruptedException e1) {
			e1.printStackTrace();
		}
	}

	@Override
	public void createPartControl(Composite parent) {
		createMythen();

		plotRawCommand = "ma.plotRaw()";
		plotCalibCommand = "ma.plotCalib()";
		plotRawAndCalibCommand = "ma.plotRawAndCalib()";

		parent.setLayout(new FillLayout());

		Composite composite = new Composite(parent, SWT.NONE);

		final GuiBean bean = getGUIInfo();
		plotWindow = new PlotWindow(composite, this, getViewSite().getActionBars(), this, plotViewName);
		plotWindow.setNotifyListener(this);
		plotWindow.updatePlotMode(bean);

		composite.setLayout(new GridLayout(1, false));

		GridData gridData = new GridData();

		gridData.heightHint = 500;
		gridData.widthHint = 500;

		Composite controls = new Composite(composite, SWT.NONE);
		controls.setLayout(new GridLayout(4, false));

		Label lblTime = new Label(controls, SWT.NONE);
		lblTime.setText("Acquisition Time ");

		time = new TextWrapper(controls, SWT.NONE);

		btnSet = new Button(controls, SWT.NONE);
		btnSet.setText("Acquire");

		progress = new ProgressBar(controls, SWT.NONE);

		btnSet.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				NumTracker scanNumTracker;
				try {
					scanNumTracker = new NumTracker("tmp");
					scanNumTracker.incrementNumber();
				} catch (IOException e2) {
					logger.error("Could not create NumTracker to track scan file numbers", e2);
				}

				createMythen();
				JythonServerFacade.getInstance().runCommand("from gda.data.scan.datawriter import AsciiDataWriterConfiguration");
				String header = JythonServerFacade
						.getInstance()
						.evaluateCommand(
								"str(Finder.getInstance().listFindablesOfType(AsciiDataWriterConfiguration)[0].getHeader())[1:-1]");

				JythonServerFacade.getInstance().runCommand("ma.setHeader(\"" + header + "\")");
				timeVal = time.getText();
				acquireCommand = "ma.acquire(" + timeVal + ")";
				JythonServerFacade.getInstance().runCommand(acquireCommand);
				btnSet.setEnabled(false);

				int i = 0;
				while (i<100) {
					try {
						Thread.sleep(((Integer.parseInt(timeVal)+5)*1000)/100);
					} catch (InterruptedException e1) {
						e1.printStackTrace();
					}
					progress.setSelection(i);
					i++;
				}

				progress.setSelection(100);
				plot();
				acquired = true;
				btnSet.setEnabled(true);
				progress.setSelection(0);

				String rawFileLocation = "Raw Mythen Data ="
					+ JythonServerFacade.getInstance().evaluateCommand("ma.getRawFileName()");
				rawFileLocationLabel.setText(rawFileLocation);
			}
		});

		plotCalib = new Button(controls, SWT.CHECK);
		plotCalib.setText("Use calibration");

		plotCalib.addSelectionListener(new SelectionListener() {
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}

			@Override
			public void widgetSelected(SelectionEvent e) {
				doPlotCalib = plotCalib.getSelection();
				if (acquired)
					plot();
			}
		});

		rawFileLocationLabel = new Label(composite, SWT.NONE);
		rawFileLocationLabel.setText("Raw Mythen Data not collected yet                                                                        ");

		Label calibFileLocationLabel = new Label(composite, SWT.NONE);
		String calibFileLocation = "Calibration Data ="
				+ JythonServerFacade.getInstance().evaluateCommand("ma.getCalibLocation()");
		calibFileLocationLabel.setText(calibFileLocation);

		if (id != null) {
			// process extension configuration
			logger.info("ID: {}", id);
			final PlotViewConfig config = new PlotViewConfig(id);
			plotViewName = config.getName();
			setPartName(config.getName());
		} else {
			// default to the view name
			plotViewName = getViewSite().getRegisteredName();
		}
		logger.info("View name is {}", plotViewName);
		plotConsumer = new PlotConsumer(plotServer, plotViewName);
		plotConsumer.addIObserver(this);
		execSvc.execute(plotConsumer);
		plotConsumer.addJob(new PlotJob(PlotJobType.Data));
	}

	private void plot() {
		if (doPlotCalib)
			JythonServerFacade.getInstance().runCommand(plotCalibCommand);
		else
			JythonServerFacade.getInstance().runCommand(plotRawCommand);
	}

	@Override
	public void setFocus() {
	}

	@Override
	public void update(Object theObserved, Object changeCode) {
		if (theObserved.equals(plotConsumer)) {
			if (changeCode instanceof DataBean) {
				plotWindow.processPlotUpdate((DataBean) changeCode);
				notifyDataObservers((DataBean) changeCode);
			} else if (changeCode instanceof GuiBean) {
				plotWindow.processGUIUpdate((GuiBean) changeCode);
			}
		} else {
			if (changeCode instanceof String && changeCode.equals(plotViewName)) {
				plotConsumer.addJob(new PlotJob(PlotJobType.Data));
			}
			if (changeCode instanceof GuiUpdate) {
				GuiUpdate gu = (GuiUpdate) changeCode;
				if (gu.getGuiName().contains(plotViewName)) {
					GuiBean bean = gu.getGuiData();
					UUID id = (UUID) bean.get(GuiParameters.PLOTID);
					if (id == null || plotID.compareTo(id) != 0) { // filter out own beans
						if (guiBean == null)
							guiBean = bean.copy(); // cache a local copy
						else
							guiBean.merge(bean); // or merge it
						PlotJob job = new PlotJob(PlotJobType.GUI);
						job.setGuiBean(bean);
						plotConsumer.addJob(job);
					}
				}
			}
		}
	}

	@Override
	public void addIObserver(IObserver anIObserver) {
		observers.add(anIObserver);
	}

	@Override
	public void deleteIObserver(IObserver anIObserver) {
		observers.remove(anIObserver);
	}

	@Override
	public void deleteIObservers() {
		observers.clear();

	}

	/**
	 * Allow another observer to see plot data.
	 * <p>
	 * A data observer gets an update with a data bean.
	 *
	 * @param observer
	 */
	public void addDataObserver(IObserver observer) {
		dataObservers.add(observer);
	}

	/**
	 * Remove a data observer
	 *
	 * @param observer
	 */
	public void deleteDataObserver(IObserver observer) {
		dataObservers.remove(observer);
	}

	/**
	 * Remove all data observers
	 */
	public void deleteDataObservers() {
		dataObservers.clear();
	}

	private void notifyDataObservers(DataBean bean) {
		Iterator<IObserver> iter = dataObservers.iterator();
		while (iter.hasNext()) {
			IObserver ob = iter.next();
			ob.update(this, bean);
		}
	}

	/**
	 * Get gui information from plot server
	 */
	@Override
	public GuiBean getGUIInfo() {
		getGUIState();
		return guiBean;
	}

	private void getGUIState() {
		if (guiBean == null) {
			try {
				guiBean = plotServer.getGuiState(plotViewName);
			} catch (Exception e) {
				logger.warn("Problem with getting GUI data from plot server");
			}
			if (guiBean == null)
				guiBean = new GuiBean();
		}
	}

	/**
	 * Push GUI information back to plot server
	 *
	 * @param key
	 * @param value
	 */
	@Override
	public void putGUIInfo(GuiParameters key, Serializable value) {
		getGUIState();
		guiBean.put(key, value);
		sendGUIInfo(guiBean);
	}

	/**
	 * Remove GUI information from plot server
	 *
	 * @param key
	 */
	@Override
	public void removeGUIInfo(GuiParameters key) {
		getGUIState();
		guiBean.remove(key);
		sendGUIInfo(guiBean);
	}

	@Override
	public void dispose() {
		plotWindow.dispose();
		plotConsumer.stop();
		execSvc.shutdown();
		deleteIObservers();
		deleteDataObservers();
		System.gc();
	}

	public String getPlotViewName() {
		return plotViewName;
	}

	public void updatePlotMode(final GuiPlotMode mode) {
		plotWindow.updatePlotMode(mode);
	}

	public void processPlotUpdate(DataBean dBean) {
		plotWindow.processPlotUpdate(dBean);
		notifyDataObservers(dBean);
	}

	public void processGUIUpdate(GuiBean bean) {
		plotWindow.processGUIUpdate(bean);
	}

	public PlotWindow getPlotWindow() {
		return this.plotWindow;
	}

	@Override
	public void updateProcessed() {
		if (plotConsumer != null)
			plotConsumer.dataUpdateFinished();
	}


	@Override
	public void sendGUIInfo(GuiBean guiBean) {
		guiBean.put(GuiParameters.PLOTID, plotID); // put plotID in bean
		try {
			plotServer.updateGui(plotViewName, guiBean);
		} catch (Exception e) {
			logger.warn("Problem with updating plot server with GUI data");
			e.printStackTrace();
		}
	}
}

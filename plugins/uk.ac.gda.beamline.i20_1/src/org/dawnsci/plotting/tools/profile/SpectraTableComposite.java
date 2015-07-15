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

package org.dawnsci.plotting.tools.profile;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.dawnsci.plotting.tools.profile.model.AvgRegionToolDataModel;
import org.dawnsci.plotting.tools.profile.model.SpectraRegionDataNode;
import org.dawnsci.plotting.tools.profile.model.SpectrumDataNode;
import org.dawnsci.plotting.tools.profile.model.TimeEnergyShiftingModel;
import org.dawnsci.plotting.tools.profile.model.TimeResolvedDataNode;
import org.dawnsci.plotting.tools.profile.model.TimingGroupDataNode;
import org.dawnsci.plotting.tools.profile.model.ToolPageModel;
import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.observable.IObservable;
import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.core.databinding.observable.masterdetail.IObservableFactory;
import org.eclipse.dawnsci.analysis.dataset.roi.RectangularROI;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.region.IRegion;
import org.eclipse.dawnsci.plotting.api.region.RegionUtils;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IMenuListener;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.databinding.viewers.ObservableListTreeContentProvider;
import org.eclipse.jface.databinding.viewers.ViewerProperties;
import org.eclipse.jface.dialogs.IInputValidator;
import org.eclipse.jface.dialogs.InputDialog;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.jface.viewers.TreeViewerColumn;
import org.eclipse.jface.window.Window;
import org.eclipse.jface.wizard.WizardDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.swt.widgets.ToolItem;
import org.eclipse.swt.widgets.Tree;
import org.eclipse.swt.widgets.TreeColumn;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.swtdesigner.ResourceManager;

import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.calibration.data.EnergyCalibration;
import uk.ac.gda.exafs.calibration.ui.EnergyCalibrationWizard;

public class SpectraTableComposite extends ObservableResourceComposite {

	protected static final Logger logger = LoggerFactory.getLogger(SpectraTableComposite.class);

	public static final String NEW_REGION_PROP_NAME = "newRegion";

	private final Image recalibrationIcon = ResourceManager.getImageDescriptor(TimeResolvedToolPage.class, "/icons/spectrum.png").createImage();
	private final Image exportWithExcludedCyclesIcon = ResourceManager.getImageDescriptor(TimeResolvedToolPage.class, "/icons/disks.png").createImage();
	private final Image stackoffsetChangeIcon = ResourceManager.getImageDescriptor(TimeResolvedToolPage.class, "/icons/ui-slider.png").createImage();
	private final Image timeEnergyShiftIcon = ResourceManager.getImageDescriptor(TimeResolvedToolPage.class, "/icons/chart_curve.png").createImage();
	private final Image timeEnergyShiftSelectedSpectraIcon = ResourceManager.getImageDescriptor(TimeResolvedToolPage.class, "/icons/chart_curve_link.png").createImage();
	private final Image timeEnergyShiftUseIcon = ResourceManager.getImageDescriptor(TimeResolvedToolPage.class, "/icons/chart_line.png").createImage();

	private final IObservableList selectedSpectraList = new WritableList(new ArrayList<SpectrumDataNode>(), SpectrumDataNode.class);

	private Binding selectedSpectraBinding;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private TreeViewer spectraTreeTable;

	private final ToolPageModel toolPageModel;

	private final TimeEnergyShiftingModel timeEnergyShiftingModel;

	public SpectraTableComposite(Composite parent, int style, ToolPageModel toolPageModel, TimeEnergyShiftingModel timeEnergyShiftingModel) {
		super(parent, style);
		setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		this.toolPageModel = toolPageModel;
		this.timeEnergyShiftingModel = timeEnergyShiftingModel;
		setup();
	}

	public void clearSelectedSpectraList() {
		if (selectedSpectraList != null) {
			selectedSpectraList.clear();
		}
	}

	private void setup() {
		createTootbarForSpectraTable(this);
		Tree spectraTree = new Tree(this, SWT.MULTI | SWT.BORDER | SWT.H_SCROLL | SWT.V_SCROLL);
		spectraTree.setHeaderVisible(true);
		spectraTree.setLinesVisible(true);
		spectraTree.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		spectraTreeTable = new TreeViewer(spectraTree);
		TreeColumn nameColumn = new TreeColumn(spectraTree, SWT.LEFT);
		nameColumn.setAlignment(SWT.LEFT);
		nameColumn.setText("Name");
		nameColumn.setWidth(155);
		TreeViewerColumn nameViewerColumn = new TreeViewerColumn(spectraTreeTable, nameColumn);
		nameViewerColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public Image getImage(Object element) {
				if (element instanceof SpectrumDataNode) {
					if (((SpectrumDataNode) element).isAveraged()) {
						return PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_OBJS_INFO_TSK);
					}
				}
				return super.getImage(element);
			}
		});

		TreeColumn timeColumn = new TreeColumn(spectraTree, SWT.CENTER);
		timeColumn.setAlignment(SWT.LEFT);
		timeColumn.setText("End time");
		timeColumn.setWidth(60);
		TreeViewerColumn timeViewerColumn = new TreeViewerColumn(spectraTreeTable, timeColumn);
		timeViewerColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				if (element instanceof SpectrumDataNode) {
					return DataHelper.roundDoubletoString(((SpectrumDataNode) element).getEndTime()) + " s";
				}
				return "";
			}
			@Override
			public Color getBackground(Object element) {
				if (element instanceof SpectrumDataNode) {
					if (((SpectrumDataNode) element).isAveraged()) {
						return  Display.getCurrent().getSystemColor(SWT.COLOR_YELLOW);
					}
				}
				return super.getBackground(element);
			}
		});

		spectraTreeTable.setContentProvider(new ObservableListTreeContentProvider(dataObservableFactory, null));

		final MenuManager menuManager = new MenuManager();
		Menu menu = menuManager.createContextMenu(spectraTreeTable.getTree());
		menuManager.addMenuListener(new IMenuListener() {
			@Override
			public void menuAboutToShow(IMenuManager manager) {
				menuManager.add(createPlotEveryIntervalAction);

				IStructuredSelection selection = (IStructuredSelection) spectraTreeTable.getSelection();
				if(selection.isEmpty()) {
					return;
				}

				if (isGroupsSelected(selection)) {
					// menuManager.add(zoomToGroupAction);
				}

				if (isSingleSpectrumSelected(selection)) {
					// menuManager.add(plotForEachGroupAction);
				}

				menuManager.add(createRegionAction);
				menuManager.add(createRegionAvgAction);
				menuManager.add(createRegionAvgEveryAction);
			}

			private boolean isSingleSpectrumSelected(IStructuredSelection selection) {
				return (selection.size() == 1 && selection.getFirstElement() instanceof SpectrumDataNode);
			}

			private boolean isGroupsSelected(IStructuredSelection selection) {
				Iterator<?> iterator = selection.iterator();
				while (iterator.hasNext()) {
					if (!(iterator.next() instanceof TimingGroupDataNode)) {
						return false;
					}
				}
				return true;
			}
		});
		menuManager.setRemoveAllWhenShown(true);
		spectraTreeTable.getTree().setMenu(menu);

		spectraTreeTable.setInput(toolPageModel.getTimeResolvedData());
	}

	private final IObservableFactory dataObservableFactory = new IObservableFactory() {
		@Override
		public IObservable createObservable(Object target) {
			if (target instanceof TimeResolvedDataNode) {
				return ((TimeResolvedDataNode) target).getTimingGroups();
			} else if (target instanceof TimingGroupDataNode) {
				return ((TimingGroupDataNode) target).getSpectra();
			}
			return null;
		}
	};

	public void createSpectraSelectionBinding() {
		if (selectedSpectraBinding == null) {
			selectedSpectraBinding = dataBindingCtx.bindList(ViewerProperties.multipleSelection().observe(spectraTreeTable), selectedSpectraList);
		}
	}

	public IObservableList getSelectedSpectraList() {
		return selectedSpectraList;
	}

	private void createTootbarForSpectraTable(final Composite treeParent) {
		ToolBar toolBar = new ToolBar(treeParent, SWT.HORIZONTAL);
		toolBar.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		ToolItem collapseTree = new ToolItem(toolBar, SWT.PUSH);
		collapseTree.setText("");
		collapseTree.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_TOOL_BACK));
		collapseTree.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				spectraTreeTable.collapseAll();
			}
		});

		ToolItem expendTree = new ToolItem(toolBar, SWT.PUSH);
		expendTree.setText("");
		expendTree.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_TOOL_FORWARD));
		expendTree.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				spectraTreeTable.expandAll();
			}
		});

		final ToolItem plotOnSelection = new ToolItem(toolBar, SWT.CHECK);
		plotOnSelection.setText("");
		plotOnSelection.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ELCL_SYNCED));
		plotOnSelection.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				if (plotOnSelection.getSelection()) {
					selectedSpectraList.clear();
					removeSpectraSelectionBinding();
				} else {
					createSpectraSelectionBinding();
				}
			}
		});

		final ToolItem recalibrateEnergyButton = new ToolItem(toolBar, SWT.PUSH);
		recalibrateEnergyButton.setText("");
		recalibrateEnergyButton.setImage(recalibrationIcon);
		recalibrateEnergyButton.setToolTipText("Recalibrate energy");
		recalibrateEnergyButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				WizardDialog wizardDialog = new WizardDialog(treeParent.getShell(), new EnergyCalibrationWizard(calibrationModel));
				wizardDialog.setPageSize(1024, 768);
				if (wizardDialog.open() == Window.OK) {
					if (calibrationModel.getCalibrationDetails().getCalibrationResult() != null) {
						double[] value = applyNewEnergy(calibrationModel);
						try {
							TimeResolvedToolPageHelper timeResolvedToolPageHelper = new TimeResolvedToolPageHelper();
							timeResolvedToolPageHelper.applyEnergyCalibrationToNexusFiles(toolPageModel.getDataFile(), recalibrateEnergyButton.getDisplay(), calibrationModel.getCalibrationDetails().getCalibrationResult().toString(), value);
						} catch (Exception e) {
							UIHelper.showError("Error apply energy calibration", e.getMessage());
							logger.error("Error apply energy calibration", e);
						}
					}
				}
			}
		});
		if (toolPageModel.getCyclesInfo() != null) {
			ToolItem exportCycle = new ToolItem(toolBar, SWT.PUSH);
			exportCycle.setText("");
			exportCycle.setImage(exportWithExcludedCyclesIcon);
			exportCycle.setToolTipText("Exclude cycles and save");
			exportCycle.addListener(SWT.Selection, new Listener() {
				@Override
				public void handleEvent(Event event) {
					TimeResolvedToolPageHelper timeResolvedToolPageHelper = new TimeResolvedToolPageHelper();
					timeResolvedToolPageHelper.averageCyclesAndExport(toolPageModel.getDataFile(), SpectraTableComposite.this.getDisplay(), toolPageModel.getCyclesInfo());
				}
			});
		}

		final ToolItem stackToggle = new ToolItem(toolBar, SWT.PUSH);
		stackToggle.setImage(stackoffsetChangeIcon);
		stackToggle.setToolTipText(Double.toString(toolPageModel.getTraceStack()));
		stackToggle.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				InputDialog dlg = new InputDialog(stackToggle.getDisplay().getActiveShell(), "Stack offset", "Enter new offset", Double.toString(toolPageModel.getTraceStack()), new IInputValidator() {
					@Override
					public String isValid(String newText) {
						try {
							double value = Double.parseDouble(newText);
							if (value >= 0) {
								return null;
							}
							return "Only positive number is allowed";
						} catch (NumberFormatException e) {
							return "Invalid valid";
						}
					}
				});
				if (dlg.open() ==  Window.OK) {
					toolPageModel.setTraceStack(Double.parseDouble(dlg.getValue()));
					stackToggle.setToolTipText(Double.toString(toolPageModel.getTraceStack()));
				}
			}
		});

		final ToolItem loadTimeEnergyViewToggle = new ToolItem(toolBar, SWT.CHECK);
		loadTimeEnergyViewToggle.setImage(timeEnergyShiftIcon);
		loadTimeEnergyViewToggle.setToolTipText("Show/hide time vs energy view");
		loadTimeEnergyViewToggle.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				timeEnergyShiftingModel.setLoadData(loadTimeEnergyViewToggle.getSelection());
			}
		});

		final ToolItem timeSelectedEnergyViewToggle = new ToolItem(toolBar, SWT.CHECK);
		timeSelectedEnergyViewToggle.setImage(timeEnergyShiftUseIcon);
		timeSelectedEnergyViewToggle.setToolTipText("Use selected spectra");
		timeSelectedEnergyViewToggle.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				timeEnergyShiftingModel.setUseSpectra(timeSelectedEnergyViewToggle.getSelection());
			}
		});

		final ToolItem shiftDataToggle = new ToolItem(toolBar, SWT.CHECK);
		shiftDataToggle.setImage(timeEnergyShiftSelectedSpectraIcon);
		shiftDataToggle.setToolTipText("Use shifted energy");
		shiftDataToggle.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				timeEnergyShiftingModel.setEnergyShifted(shiftDataToggle.getSelection());
			}
		});
	}

	private final EnergyCalibration calibrationModel = new EnergyCalibration();

	private final InputDialog dlg = new InputDialog(Display.getCurrent().getActiveShell(),
			"", "Enter number", "", new IInputValidator() {
		@Override
		public String isValid(String newText) {
			try {
				int avgValue = Integer.parseInt(newText);
				if (avgValue < 1) {
					return "Invalid number";
				}
			} catch(NumberFormatException e) {
				return "Not a number";
			}
			return null;
		}
	});


	private final Action createPlotEveryIntervalAction = new Action("Select spectrum for every") {
		@Override
		public void run() {
			if (dlg.open() == Window.OK) {
				int intervalToPlot = Integer.parseInt(dlg.getValue());
				int counter = 0;
				for (Object objTimingGroup : toolPageModel.getTimeResolvedData().getTimingGroups()) {
					for (Object objSpectrum : ((TimingGroupDataNode) objTimingGroup).getSpectra()) {
						SpectrumDataNode spectrumToPlot = (SpectrumDataNode) objSpectrum;
						if (counter == 0) {
							spectraTreeTable.expandAll();
							selectedSpectraList.clear();
							selectedSpectraList.add(spectrumToPlot);
						}
						else if (counter % intervalToPlot == 0) {
							selectedSpectraList.add(spectrumToPlot);
						}
						counter++;
					}
				}
			}
		}
	};

	private final Action createRegionAvgAction = new Action("Create region and average") {
		@Override
		public void run() {
			try {
				List<IRegion> regions = findSpectraAndCreateRegion();
				for (IRegion region : regions) {
					AvgRegionToolDataModel spectraRegion = new AvgRegionToolDataModel(region, toolPageModel.getTimeResolvedData());
					addRegionAction(spectraRegion);
				}
			} catch (Exception e) {
				UIHelper.showError("Unable to create regions for spectra", e.getMessage());
			}
		}
	};

	private final Action createRegionAvgEveryAction = new Action("Create region and average every...") {
		@Override
		public void run() {
			if (dlg.open() == Window.OK) {
				try {
					List<IRegion> regions = findSpectraAndCreateRegion();
					for (IRegion region : regions) {
						AvgRegionToolDataModel spectraRegion = new AvgRegionToolDataModel(region, toolPageModel.getTimeResolvedData());
						addRegionAction(spectraRegion);
						spectraRegion.setNoOfSpectraToAvg(Integer.parseInt(dlg.getValue()));
					}
				} catch (Exception e) {
					UIHelper.showError("Unable to create regions for spectra", e.getMessage());
				}
			}
		}
	};

	private final Action createRegionAction = new Action("Create region") {
		@Override
		public void run() {
			try {
				List<IRegion> regions = findSpectraAndCreateRegion();
				for (IRegion region : regions) {
					SpectraRegionDataNode spectraRegion = new SpectraRegionDataNode(region, toolPageModel.getTimeResolvedData());
					addRegionAction(spectraRegion);
				}
			} catch (Exception e) {
				UIHelper.showError("Unable to create regions for spectra", e.getMessage());
			}
		}
	};

	private void addRegionAction(SpectraRegionDataNode spectraRegion) {
		selectedSpectraList.clear();
		firePropertyChange(NEW_REGION_PROP_NAME, null, spectraRegion);
		toolPageModel.getDataImagePlotting().addRegion(spectraRegion.getRegion());
	}

	private List<IRegion> findSpectraAndCreateRegion() throws Exception {
		List<IRegion> regions = new ArrayList<IRegion>();
		if(spectraTreeTable.getSelection() instanceof IStructuredSelection) {
			IStructuredSelection selection = (IStructuredSelection) spectraTreeTable.getSelection();
			Iterator<?> iterator = selection.iterator();
			int startIndex = -1;
			int endIndex = -1;
			while (iterator.hasNext()) {
				Object object = iterator.next();
				if (object instanceof SpectrumDataNode) {
					SpectrumDataNode spectrum = (SpectrumDataNode) object;
					if (startIndex == -1) {
						startIndex = spectrum.getIndex();
						endIndex = spectrum.getIndex();
						continue;
					}
					if (spectrum.getIndex() > endIndex + 1 ) { // break in selection
						regions.add(createRegionROI(startIndex, endIndex));
						startIndex = spectrum.getIndex();
						endIndex = spectrum.getIndex();
					} else {
						endIndex = spectrum.getIndex();
					}
				}
			}
			if (startIndex != -1) {
				regions.add(createRegionROI(startIndex, endIndex));
			}
		}
		return regions;
	}


	private IRegion createRegionROI(int startIndex, int endIndex) throws Exception {
		IRegion region = createRegion();
		region.setROI(new RectangularROI(0, startIndex, 100, endIndex - startIndex + 1, 0));
		return region;
	}



	private IRegion createRegion() throws Exception {
		IPlottingSystem plotting = toolPageModel.getDataImagePlotting();
		IRegion region = plotting.createRegion(RegionUtils.getUniqueName("Region", plotting), IRegion.RegionType.YAXIS);
		region.setPlotType(plotting.getPlotType());
		region.setShowLabel(true);
		return region;
	}

	private double[] applyNewEnergy(EnergyCalibration calibrationModel) {
		int stripSize = toolPageModel.getEnergy().getSize();
		double[] value = new double[stripSize];
		for (int i = 0; i < stripSize; i++) {
			value[i] = calibrationModel.getCalibrationDetails().getCalibrationResult().value(i) / stripSize;
		}
		return value;
	}

	private void removeSpectraSelectionBinding() {
		if (selectedSpectraBinding != null) {
			dataBindingCtx.removeBinding(selectedSpectraBinding);
			selectedSpectraBinding.dispose();
			selectedSpectraBinding = null;
		}
	}

	@Override
	protected void disposeResource() {
		recalibrationIcon.dispose();
		exportWithExcludedCyclesIcon.dispose();
		stackoffsetChangeIcon.dispose();
		timeEnergyShiftIcon.dispose();
		timeEnergyShiftSelectedSpectraIcon.dispose();
		timeEnergyShiftUseIcon.dispose();
	}
}

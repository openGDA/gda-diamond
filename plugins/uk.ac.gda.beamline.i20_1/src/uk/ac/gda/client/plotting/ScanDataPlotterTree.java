/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

package uk.ac.gda.client.plotting;

import java.lang.reflect.InvocationTargetException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.apache.commons.beanutils.BeanUtils;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.dialogs.IInputValidator;
import org.eclipse.jface.dialogs.InputDialog;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.viewers.CheckStateChangedEvent;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.ICheckStateListener;
import org.eclipse.jface.viewers.IContentProvider;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.viewers.ViewerCell;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.swt.widgets.Menu;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.plotting.model.ITreeNode;
import uk.ac.gda.client.plotting.model.LineTraceProviderNode;
import uk.ac.gda.client.plotting.model.LineTraceProviderNode.TraceStyleDetails;
import uk.ac.gda.client.plotting.model.Node;
import uk.ac.gda.client.plotting.model.ScanNode;
import uk.ac.gda.exafs.plotting.model.ExperimentRootNode;

/**
 * Class to handle the TreeViewer widget used to show list of scans and plots in {@link ScanDataPlotterComposite}.
 * Refactored from {{@link ScanDataPlotterComposite}
 * @since 12/4/2018
 */
public class ScanDataPlotterTree {
	private static final Logger logger = LoggerFactory.getLogger(ScanDataPlotterTree.class);

	private final DataPlotterCheckedTreeViewer dataTreeViewer;
	private PlotHandler plotHandler;
	private final Node rootDataNode;
	private final Map<String, Color> nodeColors = new HashMap<>();
	private int maxNumberOfAcquiredSpectraToPlot = 10;
	private Composite parentComposite;

	public ScanDataPlotterTree(Composite parent, final Node rootDataNode, final IContentProvider contentProvider) {
		this.rootDataNode = rootDataNode;
		parentComposite = parent;
		dataTreeViewer = new DataPlotterCheckedTreeViewer(parent, SWT.MULTI);
		dataTreeViewer.getTree().setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		dataTreeViewer.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public void update(ViewerCell cell) {
				Node element = (Node) cell.getElement();

				cell.setText(element.getLabel());
				if (element instanceof LineTraceProviderNode) {
					LineTraceProviderNode item = ((LineTraceProviderNode) element);
					Color color = item.getTraceStyle().getColor();
					if (color != null) {
						cell.setForeground(color);
					}
					return;
				}
			}
		});

		dataTreeViewer.addCheckStateListener(new ICheckStateListener() {
			@Override
			public void checkStateChanged(CheckStateChangedEvent event) {
				Node dataNode = (Node) event.getElement();
				updateSelection(dataNode, event.getChecked());
			}

			/** traverse node tree recursively and show plots for selected node and any child nodes */
			private void updateSelection(Node dataNode, boolean checked) {
				if (dataNode.getChildren() == null) {
					plotHandler.updateDataItemNode(dataNode, checked);
				} else {
					for (Object childDataNode : dataNode.getChildren()) {
						updateSelection((Node) childDataNode, checked);
					}
				}
			}
		});

		dataTreeViewer.setContentProvider(contentProvider);
		dataTreeViewer.setInput(rootDataNode);
		setupContextMenu();
	}

	private void setupContextMenu() {
		final MenuManager menuMgr = new MenuManager();
		Menu menu = menuMgr.createContextMenu(dataTreeViewer.getControl());
		menuMgr.addMenuListener(menuManager -> {

			menuMgr.add(getLoadFromFileAction());

			if (!rootDataNode.getChildren().isEmpty()) {
				menuMgr.add(getMaxNumSpectraAction());
				menuMgr.add(getRemoveAllAction());
			}

			if (dataTreeViewer.getSelection().isEmpty() || !isSelectedOnSameNodeType(dataTreeViewer.getSelection())) {
				return;
			}

			final IStructuredSelection selection = (IStructuredSelection) dataTreeViewer.getSelection();
			if (selection.getFirstElement() instanceof ScanNode) {
				menuMgr.add(getRemoveAction());
			} else if (selection.getFirstElement() instanceof LineTraceProviderNode) {
				menuMgr.add(getChangeAppearanceAction());
			}

		});
		menuMgr.setRemoveAllWhenShown(true);

		dataTreeViewer.getControl().setMenu(menu);
	}

	/**
	 * Return Action with dialog box to allow user to set the maximum number of spectra that will be plotted during data acquisition.
	 *
	 * @return
	 * @since 28/9/2016
	 */
	private Action getMaxNumSpectraAction() {
		return new Action("Change number of plotted spectra") {
			@Override
			public void run() {
				InputDialog dlg = new InputDialog(Display.getCurrent().getActiveShell(), "Set maximum number of spectra to plot during acqusition",
						"Enter maximum number of spectra to show in plot when aquiring data", String.valueOf(maxNumberOfAcquiredSpectraToPlot),
						new IntegerValidator());
				if (dlg.open() == Window.OK) {
					// User clicked OK; update the label with the input
					Integer userInputInteger = Integer.valueOf(dlg.getValue());
					if (userInputInteger == null || userInputInteger < 1) {
						logger.info("Problem converting user input into number of spectra to plot {}", dlg.getValue());
					} else {
						maxNumberOfAcquiredSpectraToPlot = userInputInteger;
					}
				}
			}
		};
	}

	private Action getLoadFromFileAction() {
		return new Action("Load data from Nexus file...") {
			@Override
			public void run() {
				loadNexusDataFromFile();
			}
		};
	}

	public void loadNexusDataFromFile() {
		FileDialog dialog = new FileDialog(parentComposite.getShell(), SWT.OPEN|SWT.MULTI);
		dialog.setFilterNames(new String[] { "xml files", "All Files (*.*)" });
		dialog.setFilterExtensions(new String[] { "*.nxs", "*.*" });
		dialog.open();

		// Create list of full absolute path for selected files
		List<String> filenames = new ArrayList<String>();
		for (String filename : dialog.getFileNames()) {
			filenames.add(Paths.get(dialog.getFilterPath(), filename).toString());
		}
		((ExperimentRootNode) rootDataNode).update(null, filenames.toArray(new String[] {}));
	}

	private Action getRemoveAllAction() {
		return new Action("Remove All") {
			@Override
			public void run() {
				// Check with user for confirmation - to prevent accidently removing all the plots.
				boolean reallyRemoveAll = MessageDialog.openQuestion(Display.getCurrent().getActiveShell(),
						"Remove all plots", "Do you really want to remove all the plots ?");
				if (!reallyRemoveAll)
					return;
				for (Object obj : rootDataNode.getChildren()) {
					Node nodeToRemove = (Node) obj;
					if (dataTreeViewer.getChecked(nodeToRemove)) {
						dataTreeViewer.updateCheckSelection(nodeToRemove, false);
					}
				}
				rootDataNode.getChildren().clear();
			}
		};
	}

	private Action getRemoveAction() {
		return new Action("Remove") {
			@Override
			public void run() {
				final IStructuredSelection selection = (IStructuredSelection) dataTreeViewer.getSelection();
				Iterator<?> iterator = selection.iterator();
				while(iterator.hasNext()) {
					Node nodeToRemove = (Node) iterator.next();
					if (dataTreeViewer.getChecked(nodeToRemove)) {
						dataTreeViewer.updateCheckSelection(nodeToRemove, false);
					}
					rootDataNode.getChildren().remove(nodeToRemove);
				}
			}
		};
	}

	private Action getChangeAppearanceAction() {
		return new Action("Change appearance") {
			@Override
			public void run() {
				final IStructuredSelection selection = (IStructuredSelection) dataTreeViewer.getSelection();
				TraceStyleDetails traceStyle = null;
				if (selection.size() == 1) {
					traceStyle = ((LineTraceProviderNode) selection.getFirstElement()).getTraceStyle();
				}
				TraceStyleDialog dialog = new TraceStyleDialog(dataTreeViewer.getControl().getShell(), traceStyle);
				dialog.create();
				if (dialog.open() == Window.OK) {
					Iterator<?> iterator = selection.iterator();
					while(iterator.hasNext()) {
						Object selectedNode = iterator.next();
						if (selectedNode instanceof LineTraceProviderNode) {
							LineTraceProviderNode nodeToChange = (LineTraceProviderNode) selectedNode;
							try {
								TraceStyleDetails newTraceStyleDetails = new TraceStyleDetails();
								BeanUtils.copyProperties(newTraceStyleDetails, dialog.getTraceStyle());
								nodeToChange.setTraceStyle(newTraceStyleDetails);
								if (dataTreeViewer.getChecked(nodeToChange)) {
									plotHandler.removeTrace(nodeToChange.getIdentifier());
									plotHandler.addTrace(nodeToChange);
								}
								dataTreeViewer.update(nodeToChange, null);
							} catch (IllegalAccessException | InvocationTargetException e) {
								logger.error("Unable to copy properties", e);
							}
						}
					}
				}
			}
		};
	}

	private Color getTraceColor(String colorValue) {
		Color color = null;
		if (!nodeColors.containsKey(colorValue)) {
			color = UIHelper.convertHexadecimalToColor(colorValue, Display.getDefault());
			nodeColors.put(colorValue, color);
		} else {
			color = nodeColors.get(colorValue);
		}
		return color;
	}

	/**
	 * Validator used to check input in 'Max. number of spectra' dialog box).
	 */
	private static class IntegerValidator implements IInputValidator {
		/**
		 * Validates a string to make sure it's an integer > 0. Returns null for no error, or string with error message
		 *
		 * @param newText
		 * @return String
		 */
		@Override
		public String isValid(String newText) {
			Integer value = null;
			try {
				value = Integer.valueOf(newText);
			} catch (NumberFormatException nfe) {
				// swallow, value==null
			}
			if (value == null || value < 1) {
				return "Number should be an integer > 0";
			}
			return null;
		}
	}

	private boolean isSelectedOnSameNodeType(ISelection iSelection) {
		if (!(iSelection instanceof IStructuredSelection)) {
			return false;
		}
		IStructuredSelection selection = (IStructuredSelection) dataTreeViewer.getSelection();
		Object firstSelection = selection.getFirstElement();
		Iterator<?> iterator = selection.iterator();
		while (iterator.hasNext()) {
			if (iterator.next().getClass() != firstSelection.getClass()) {
				return false;
			}
		}
		return true;
	}

	public void updateCheckSelection(Object data, boolean isChecked) {
		dataTreeViewer.updateCheckSelection(data, isChecked, true);
	}

	public void updateCheckSelection(Object data, boolean isChecked, boolean fireEvent) {
		dataTreeViewer.updateCheckSelection(data, isChecked, fireEvent);
	}

	public Object[] getCheckedElements() {
		return dataTreeViewer.getCheckedElements();
	}

	public boolean getChecked(Object element) {
		return dataTreeViewer.getChecked(element);
	}

	public void expandToLevel(ITreeNode node, int level) {
		dataTreeViewer.expandToLevel(node, level);
	}

	public void setSelection(ISelection selection, boolean reveal) {
		dataTreeViewer.setSelection(selection, reveal);
	}

	public void collapseAll() {
		dataTreeViewer.collapseAll();
	}

	public void expandAll() {
		dataTreeViewer.expandAll();
	}

	public int getMaxNumberOfAcquiredSpectraToPlot() {
		return maxNumberOfAcquiredSpectraToPlot;
	}

	public void setMaxNumberOfAcquiredSpectraToPlot(int maxNumberOfAcquiredSpectraToPlot) {
		this.maxNumberOfAcquiredSpectraToPlot = maxNumberOfAcquiredSpectraToPlot;
	}

	public void setPlotHandler(PlotHandler plotHandler) {
		this.plotHandler = plotHandler;
	}

	public Viewer getTreeViewer() {
		return dataTreeViewer;
	}
}

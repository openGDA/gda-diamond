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

package uk.ac.gda.rcp.views.dashboard;

import java.beans.XMLDecoder;
import java.beans.XMLEncoder;
import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.runtime.IConfigurationElement;
import org.eclipse.core.runtime.Platform;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.util.IPropertyChangeListener;
import org.eclipse.jface.util.PropertyChangeEvent;
import org.eclipse.jface.viewers.CellEditor;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.ColumnViewerToolTipSupport;
import org.eclipse.jface.viewers.ICellModifier;
import org.eclipse.jface.viewers.IStructuredContentProvider;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.viewers.TextCellEditor;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.window.ToolTip;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.IMemento;
import org.eclipse.ui.IViewSite;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.ui.modifiers.DoubleClickModifier;

public final class DashboardView extends ViewPart {

	private class TableLabelProvider extends ColumnLabelProvider {
		private int column;

		TableLabelProvider(int col) {
			this.column = col;
		}

		@Override
		public String getText(Object element) {
			final SimpleScannableObject ob = (SimpleScannableObject) element;
			switch (column) {
			case 0:
				return ob.getScannableName();
			case 1:
				return ob.getFormattedLastPosition();
//			case 2:
//				return formatValue(ob.getMinimum(), ob.getUnit());
//			case 3:
//				return formatValue(ob.getMaximum(), ob.getUnit());
//			case 4:
//				return ob.getDescription();
			default:
				return "";
			}
		}

		@Override
		public String getToolTipText(Object element) {
			final SimpleScannableObject serverOb = (SimpleScannableObject) element;
			return serverOb.getToolTip();
		}
	}

	private static final Logger logger = LoggerFactory.getLogger(DashboardView.class);

	public static final String ID = "uk.ac.gda.rcp.views.dashboardView"; //$NON-NLS-1$

	public static final String FREQUENCY_LABEL = "update_frequency";

	private TableViewer serverViewer;

//	private TableViewerColumn maxColumn, minColumn, desColumn;

	private List<SimpleScannableObject> data;

	private Thread updater;

	protected int sleeptime;

	public void addScannableObject(SimpleScannableObject sso) {
		try {
			data.add(sso);
			serverViewer.refresh();
			((DoubleClickModifier) serverViewer.getCellModifier()).setEnabled(true);
			serverViewer.editElement(sso, 0);
		} catch (Exception ne) {
			logger.error("Cannot add object", ne);
		}
	}

	public void clearSelectedObjects() {
		final boolean ok = MessageDialog.openConfirm(getSite().getShell(), "Please confirm clear",
				"Would you like to clear all monitored objects?");
		if (!ok)
			return;
		try {
			data.clear();
			serverViewer.refresh();
		} catch (Exception ne) {
			logger.error("Cannot clear objects", ne);
		}
	}

	private CellEditor[] createCellEditors(final TableViewer tableViewer) {
		CellEditor[] editors = new CellEditor[1];
		TextCellEditor nameEd = new TextCellEditor(tableViewer.getTable());
		((Text) nameEd.getControl()).setTextLimit(60);
		// NOTE Must not add verify listener - it breaks things.
		editors[0] = nameEd;

		return editors;
	}

	private void createContentProvider() {
		serverViewer.setContentProvider(new IStructuredContentProvider() {
			@Override
			public void dispose() {
			}

			@Override
			public Object[] getElements(Object inputElement) {
				return data.toArray(); // Does not happen that often and list not large
			}

			@Override
			public void inputChanged(Viewer viewer, Object oldInput, Object newInput) {
			}
		});
	}

	private ICellModifier createModifier(final TableViewer tableViewer) {
		return new DoubleClickModifier(tableViewer) {
			@Override
			public boolean canModify(Object element, String property) {
				if (!enabled)
					return false;
				return (element instanceof SimpleScannableObject) && "Object Name".equalsIgnoreCase(property);
			}

			@Override
			public Object getValue(Object element, String property) {
				// NOTE: Only works for scannables right now which have one name
				final String name = ((SimpleScannableObject) element).getScannableName();
				return name != null ? name : "";
			}

			@Override
			public void modify(Object item, String property, Object value) {
				try {
					final SimpleScannableObject ob = (SimpleScannableObject) ((IStructuredSelection) serverViewer
							.getSelection()).getFirstElement();
					ob.setScannableName((String) value);

				} catch (Exception e) {
					logger.error("Cannot set " + property, e);

				} finally {
					setEnabled(false);
				}
				serverViewer.refresh();
			}
		};
	}

	@Override
	public void createPartControl(Composite parent) {

		final ScrolledComposite scrolledComposite = new ScrolledComposite(parent, SWT.H_SCROLL | SWT.V_SCROLL);
		scrolledComposite.setExpandHorizontal(true);
		scrolledComposite.setExpandVertical(true);

		Composite container = new Composite(scrolledComposite, SWT.NONE);
		container.setLayout(new FillLayout());
		scrolledComposite.setContent(container);

		this.serverViewer = new TableViewer(container, SWT.SINGLE | SWT.H_SCROLL | SWT.V_SCROLL | SWT.BORDER);
		serverViewer.getTable().setLinesVisible(true);
		serverViewer.getTable().setHeaderVisible(true);

		ColumnViewerToolTipSupport.enableFor(serverViewer, ToolTip.NO_RECREATE);

		final TableViewerColumn name = new TableViewerColumn(serverViewer, SWT.NONE);
		name.getColumn().setText("Name");
		name.getColumn().setWidth(150);
		name.setLabelProvider(new TableLabelProvider(0));

		final TableViewerColumn value = new TableViewerColumn(serverViewer, SWT.NONE);
		value.getColumn().setText("Value");
		value.getColumn().setWidth(150);
		value.setLabelProvider(new TableLabelProvider(1));

//		this.minColumn = new TableViewerColumn(serverViewer, SWT.NONE);
//		minColumn.getColumn().setText("Minimum");
//		minColumn.getColumn().setWidth(150);
//		minColumn.setLabelProvider(new TableLabelProvider(2));
//
//		this.maxColumn = new TableViewerColumn(serverViewer, SWT.NONE);
//		maxColumn.getColumn().setText("Maximum");
//		maxColumn.getColumn().setWidth(150);
//		maxColumn.setLabelProvider(new TableLabelProvider(3));
//
//		this.desColumn = new TableViewerColumn(serverViewer, SWT.NONE);
//		desColumn.getColumn().setText("Description");
//		desColumn.getColumn().setWidth(150);
//		desColumn.setLabelProvider(new TableLabelProvider(4));

		serverViewer.setColumnProperties(new String[] { "Object Name", "Object Value" });
		serverViewer.setCellEditors(createCellEditors(serverViewer));
		serverViewer.setCellModifier(createModifier(serverViewer));
		createContentProvider();
		serverViewer.setInput(new Object());

		getSite().setSelectionProvider(serverViewer);
		createRightClickMenu();

		Activator.getDefault().getPreferenceStore().addPropertyChangeListener(new IPropertyChangeListener() {

			@Override
			public void propertyChange(PropertyChangeEvent event) {
				if (event.getProperty().equals(FREQUENCY_LABEL)) {
					updateSleepTime();
				} 
			}
		});
	
		updateSleepTime();
		
		if (updater == null || !updater.isAlive()) {
			updater = new Thread(new Runnable() {
				
				@Override
				public void run() {
					boolean keeprunning = true;
					while(keeprunning) {
						try {
							keeprunning = true;
							refresh();
							Thread.sleep(sleeptime*1000-100);
						} catch (Exception e) {
							logger.warn("exception caugth in Dashboard Update Thread", e);
						}
					}
				}
			});
			updater.start();
		}
	}

	private void updateSleepTime() {
		int delay = Activator.getDefault().getPreferenceStore().getInt(FREQUENCY_LABEL);
		sleeptime = delay == 0 ? 2 : delay;
	}
	
	private void createRightClickMenu() {
		final MenuManager menuManager = new MenuManager();
		serverViewer.getControl().setMenu(menuManager.createContextMenu(serverViewer.getControl()));
		getSite().registerContextMenu(menuManager, serverViewer);
	}

	public void deleteSelectedObject() {
		try {
			final SimpleScannableObject ob = (SimpleScannableObject) ((IStructuredSelection) serverViewer.getSelection())
					.getFirstElement();
			data.remove(ob); // NOTE the equals method of ServerObject simply looks at the label.
			serverViewer.refresh();
		} catch (Exception ignored) {
			// Might be nothing selected.
		}
	}

	@SuppressWarnings("unchecked")
	private List<SimpleScannableObject> getDataFromXML(String textData) throws UnsupportedEncodingException {

		if (textData == null)
			return null;
		final ByteArrayInputStream stream = new ByteArrayInputStream(textData.getBytes("UTF-8"));
		XMLDecoder d = new XMLDecoder(new BufferedInputStream(stream));
		final List<SimpleScannableObject> data = (List<SimpleScannableObject>) d.readObject();
		d.close();
		return data;
	}

	/**
	 * Called to get the default list of things to monitor.
	 */
	protected List<SimpleScannableObject> getDefaultServerObjects() throws Exception {

		final List<SimpleScannableObject> data = new ArrayList<SimpleScannableObject>(5);

		IConfigurationElement[] config = Platform.getExtensionRegistry().getConfigurationElementsFor(
				"uk.ac.gda.client.dashboard.objects");

		for (IConfigurationElement e : config) {
			final String name = e.getAttribute("name");
			final SimpleScannableObject ob = new SimpleScannableObject(name);
			ob.setToolTip(e.getAttribute("tooltip"));

			data.add(ob);
		}

		return data;
	}

	private String getXMLFromData(final List<SimpleScannableObject> data) throws Exception {

		final ByteArrayOutputStream stream = new ByteArrayOutputStream();
		XMLEncoder e = new XMLEncoder(new BufferedOutputStream(stream));
		e.writeObject(data);
		e.close();

		return stream.toString("UTF-8");
	}

	@Override
	public void init(IViewSite site, IMemento memento) throws PartInitException {
		super.init(site);

		try {
			if (memento != null)
				this.data = getDataFromXML(memento.getTextData());
			if (data == null)
				this.data = getDefaultServerObjects();
		} catch (Exception ne) {
			throw new PartInitException(ne.getMessage());
		}
	}

	/**
	 * Called to refresh all the values in the table.
	 * 
	 * @param moveAmount
	 */
	public void move(final int moveAmount) {

		final int sel = serverViewer.getTable().getSelectionIndex();
		final int pos = sel + moveAmount;
		if (pos < 0 || pos > this.data.size() - 1)
			return;

		final SimpleScannableObject o = data.remove(sel);
		data.add(pos, o);

		serverViewer.refresh();
	}

	/**
	 * Called to refresh all the values in the table.
	 */
	public void refresh() {
		if (serverViewer.getControl().isDisposed())
			return;
		
		try {
			for (SimpleScannableObject sso : data) {
				sso.refresh();
			}
			Display.getDefault().syncExec(new Runnable() {
				
				@Override
				public void run() {
					if (!serverViewer.isCellEditorActive())
						serverViewer.refresh();
				}
			});
		} catch (Exception ne) {
			logger.error("Cannot refresh objects", ne);
		}
	}

	/**
	 * Used when user has too many scannables and would like to reset the view.
	 */
	public void resetSelectedObjects() {
		try {
			data.clear();
			data.addAll(getDefaultServerObjects());
			serverViewer.refresh();
		} catch (Exception ne) {
			logger.error("Cannot reset objects", ne);
		}
	}

	@Override
	public void saveState(IMemento memento) {
		try {
			memento.putTextData(getXMLFromData(data));
		} catch (Exception e) {
			logger.error("Cannot save plot bean", e);
		}
	}

	@Override
	public void setFocus() {
		if (this.serverViewer != null)
			serverViewer.getControl().setFocus();
	}
}
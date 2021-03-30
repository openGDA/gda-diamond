package uk.ac.gda.exafs.ui.composites;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.apache.commons.lang.StringUtils;
import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.IStructuredContentProvider;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.ListViewer;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.dialogs.ListDialog;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.Detector;
import gda.device.FindableObjectHolder;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.scan.ede.TimeResolvedExperiment;
import gda.scan.ede.TimeResolvedExperimentParameters;
import uk.ac.gda.exafs.experiment.ui.data.TimeResolvedExperimentModel;

/**
 * Dialog box to allow user to create a list of scannables and PVs that will be added to a {@link TimeResolvedExperiment}.
 * The functions {@link #getScannableMapFromList()}, {@link #setScannableInfoFromMap(Map)} allow the list to be set/get
 * using the same Map<name, pv> format for use directly with {@link TimeResolvedExperimentModel} and {@link TimeResolvedExperimentParameters},
 * get/set ScannablesToMonitor functions.
 */
public class ScannableListEditor extends Dialog {
	private static final Logger logger = LoggerFactory.getLogger(ScannableListEditor.class);

	private static final String SAFE_SCANNABLES_OBJECT_NAME = "safeScannablesForPositionsComposite";

	private Composite mainDialogArea;
	private Button buttonAddScannable;
	private Button buttonAddPv;
	private Button buttonRemove;
	private ListViewer listViewer;
	private String windowTitle;

	private List<ScannableInfo> scannableInfoList = new ArrayList<ScannableInfo>();

	public ScannableListEditor(Shell parentShell) {
		super(parentShell);
		windowTitle = "Edit list of Scannables";
	}

	@Override
	protected void configureShell(Shell shell) {
		super.configureShell(shell);
		shell.setText(windowTitle);
	}

	@Override
	protected Control createDialogArea(Composite parent) {
		mainDialogArea = (Composite) super.createDialogArea(parent);

		Composite composite = new Composite(mainDialogArea, SWT.NONE);
		composite.setLayout(new FillLayout());
		composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true, 1, 1));

		listViewer = new ListViewer(composite, SWT.V_SCROLL);

		listViewer.setContentProvider(new IStructuredContentProvider() {
			@Override
			public Object[] getElements(Object inputElement) {
				List list = (List) inputElement;
				return list.toArray();
			}

			@Override
			public void dispose() {
			}

			@Override
			public void inputChanged(Viewer viewer, Object oldInput, Object newInput) {
			}
		});

		listViewer.setInput(scannableInfoList);

		listViewer.setLabelProvider(new LabelProvider() {
			@Override
			public Image getImage(Object element) {
				return null;
			}

			@Override
			public String getText(Object element) {
				ScannableInfo inf = (ScannableInfo)element;
				String txt = inf.getName();
				if (!StringUtils.isEmpty(inf.getPvName())) {
					txt += "("+inf.getPvName()+")";
				}
				return txt;
			}
		});

		addButtons(mainDialogArea);
		return mainDialogArea;
	}

	@Override
	protected boolean isResizable() {
		return true;
	}

	/**
	 * Set tooltip for the 'add scannable' button according to whether list of all scannables has been generated.
	 */
	private void setTooltip() {
		if (buttonAddScannable != null && !buttonAddScannable.isDisposed()) {
			getParentShell().getDisplay().asyncExec(() ->  buttonAddScannable.setToolTipText("Select scannable to add to list..."));
		}
	}

	private void addButtons(Composite parent) {
		Composite composite = new Composite(parent, SWT.NULL);
		composite.setLayout(new GridLayout(3, true));
		composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true, 1, 1));

		buttonAddScannable = new Button(composite, SWT.PUSH);
		buttonAddScannable.setText("Add scannable");
		buttonAddScannable.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true, 1, 1));
		setTooltip();

		buttonAddPv = new Button(composite, SWT.PUSH);
		buttonAddPv.setText("Add PV");
		buttonAddPv.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true, 1, 1));

		buttonRemove = new Button(composite, SWT.PUSH);
		buttonRemove.setText("Remove");
		buttonRemove.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true, 1, 1));

		buttonAddPv.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				PVScannanableDialog scnDialog = new PVScannanableDialog(parent.getShell());
				scnDialog.create();
				scnDialog.setBlockOnOpen(true);
				scnDialog.open();

				if (scnDialog.getReturnCode()==Window.OK) {
					logger.debug("Scannable name : {}, PV name : {}", scnDialog.getName(), scnDialog.getPv());
					scannableInfoList.add(new ScannableInfo(scnDialog.getName(), scnDialog.getPv()));
					refreshListViewer();
				}
			}
		});

		buttonAddScannable.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {

				// Get name of selected scannable, add to list ...
				String result = showSelectScannableDialog(parent, getSafeScannableNames());
				if (result != null) {
					logger.debug("Scannable name : {}", result);
					scannableInfoList.add(new ScannableInfo(result));
					refreshListViewer();
				}
			}
		});

		buttonRemove.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				IStructuredSelection selection = (IStructuredSelection) listViewer.getSelection();
				ScannableInfo scnInfo = (ScannableInfo) selection.getFirstElement();
				scannableInfoList.remove(scnInfo);
				listViewer.refresh(false);
			}
		});
	}

	/**
	 * Display Dialog with list of all scannables
	 * @param parent composite
	 * @return name of the selected scannable (null if nothing selected or cancel button was pressed).
	 */
	public static String showSelectScannableDialog(Composite parent) {
		ListDialog ld = new ListDialog(parent.getShell());
		ld.setAddCancelButton(true);
		ld.setContentProvider(new ArrayContentProvider());
		ld.setLabelProvider(new LabelProvider());
		ld.setInput(getScannableNames());
		ld.setTitle("Select scannable to add");
		ld.setBlockOnOpen(true);
		ld.open();

		// Get name of selected scannable, add to list ...
		Object[] result = ld.getResult();
		if (result != null && result.length > 0) {
			return result[0].toString();
		} else {
			return null;
		}
	}

	/**
	 *
	 * @return List of Scannables that are not Detectors (sorted into alphabetical order).
	 */
	public static List<String> getScannableNames() {
		Map<String, Scannable> scannables = Finder.getFindablesOfType(Scannable.class);
		Map<String, Detector> detectors = Finder.getFindablesOfType(Detector.class);
		List<String> allScnNames = new ArrayList<>();
		if (!scannables.isEmpty()) {
			allScnNames.addAll(scannables.keySet());
		}
		// remove the detectors
		if (!detectors.isEmpty()) {
			allScnNames.removeAll(detectors.keySet());
		}
		allScnNames.sort((String s1, String s2) -> s1.compareTo(s2) );
		return allScnNames;
	}

	/**
	 *
	 * @return List of scannables that are 'safe' for user to move. (List is defined in client side object 'safeScannablesForPositionsComposite'.).
	 */
	public static List<String> getSafeScannableNames() {
		Optional<FindableObjectHolder> safeScannables = Finder.findOptionalOfType(SAFE_SCANNABLES_OBJECT_NAME, FindableObjectHolder.class);
		if (safeScannables.isPresent()) {
			FindableObjectHolder map = safeScannables.get();
			String objName = map.keySet().iterator().next();
			// return copy of the list, to avoid modifying it!
			return new ArrayList<>((List<String>) map.get(objName));
		} else {
			return Collections.emptyList();
		}
	}

	public static String showSelectScannableDialog(Composite parent, List<String> shortListOfName) {
		ListDialog ld = createSelectScannableDialog(parent, getScannableNames(), shortListOfName);
		ld.setTitle("Select scannable to add");
		ld.setBlockOnOpen(true);
		ld.open();

		// Get name of selected scannable, add to list ...
		Object[] result = ld.getResult();
		if (result != null && result.length > 0) {
			return result[0].toString();
		} else {
			return null;
		}
	}

	/**
	 * Create Dialog with list of names of scannables for user to select from. Contains a button to switch the displayed
	 * list between 'short' and 'long' lists (the short list is displayed by default if it's provided).
	 * @param parent composite
	 * @param longNameList list of scannables (typically all scannables)
	 * @param shortNameList list of scannables, can be null or empty (typically, just the frequently used scannables)
	 * @return Dialog
	 */
	public static ListDialog createSelectScannableDialog(Composite parent, List<String> longNameList, List<String> shortNameList) {
		ListDialogWithAdvanced ld = new ListDialogWithAdvanced(parent.getShell());
		ld.setAddCancelButton(true);
		ld.setContentProvider(new ArrayContentProvider());
		ld.setLongNameList(longNameList);
		ld.setInput(longNameList);
		if (shortNameList != null && !shortNameList.isEmpty()) {
			ld.setShortNameList(shortNameList);
			ld.setInput(shortNameList);
		}
		ld.setLabelProvider(new LabelProvider());
		ld.setBlockOnOpen(true);

		return ld;
	}

	public static class ListDialogWithAdvanced extends ListDialog {

		private List<String> model;
		private List<String> shortNameList = Collections.emptyList();
		private List<String> longNameList = Collections.emptyList();

		public ListDialogWithAdvanced(Shell parent) {
			super(parent);
		}

		@Override
		protected void createButtonsForButtonBar(Composite parent) {
	    	createShowAllButton(parent);
	    	super.createButtonsForButtonBar(parent);
	    }


		public void setInput(List<String> input) {
			model = new ArrayList<>(input);
			super.setInput(model);
		}

		private void createShowAllButton(Composite parent) {
			// Create checkbox to control whether all scannables are shown in the list.
			((GridLayout) parent.getLayout()).numColumns++;
			Button extraButton = new Button(parent, SWT.CHECK);
			extraButton.setText("Show all scannables");
			setButtonLayoutData(extraButton);

			extraButton.addSelectionListener(SelectionListener.widgetSelectedAdapter(event -> {
				model.clear();
				model.addAll(shortNameList);
				if (extraButton.getSelection()) {
					model.addAll(longNameList);
				}
				getTableViewer().refresh();
			}));
		}

		public void setLongNameList(List<String> allNames) {
			this.longNameList = allNames;
		}

		public void setShortNameList(List<String> safeNames) {
			this.shortNameList = safeNames;
		}
	}

	private void refreshListViewer() {
		listViewer.refresh(false);
		Point size = listViewer.getControl().computeSize(SWT.DEFAULT, mainDialogArea.getShell().getSize().y - 50);
		listViewer.getList().setSize(size);
		listViewer.getControl().pack();
		mainDialogArea.getShell().pack();
	}

	public List<ScannableInfo> getScannableInfoList() {
		return scannableInfoList;
	}

	public void setScannableInfoList(List<ScannableInfo> scannableNameList) {
		this.scannableInfoList = scannableNameList;
	}

	public Map<String,String> getScannableMapFromList() {
		Map<String,String> scannableMap = new LinkedHashMap<>();
		scannableInfoList.forEach(scnInfo -> scannableMap.put(scnInfo.getName(), scnInfo.getPvName()));
		return scannableMap;
	}

	/**
	 * Setup the scannable list using Map as stored in
	 * @param map
	 */
	public void setScannableInfoFromMap(Map<String, String> map) {
		scannableInfoList.clear();
		if (map != null) {
			map.keySet().forEach(key -> scannableInfoList.add(new ScannableInfo(key, map.get(key))));
		}
	}

	public String getWindowTitle() {
		return windowTitle;
	}

	public void setWindowTitle(String windowTitle) {
		this.windowTitle = windowTitle;
	}

	/**
	 * Dialog box to allow user to input PV and a name that will be used to create a new scannable.
	 */
	private static class PVScannanableDialog extends Dialog {
		private String name = "";
		private String pv = "";
		private Text nameText;
		private Text pvText;

		protected PVScannanableDialog(Shell parentShell) {
			super(parentShell);
		}

		@Override
		protected Control createDialogArea(Composite parent) {
			Composite mainComposite = (Composite) super.createDialogArea(parent);
			mainComposite.setLayout(new GridLayout(2, false));
			mainComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true, 1, 1));

			Label nameLabel = new Label(mainComposite, SWT.NONE);
			nameLabel.setText("Name of scannable");
			nameLabel.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, false, true, 1, 1));

			nameText = new Text(mainComposite, SWT.NONE);
			nameText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true, 1, 1));

			Label pvLabel = new Label(mainComposite, SWT.NONE);
			pvLabel.setText("PV to read value from");
			pvLabel.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, false, true, 1, 1));

			pvText = new Text(mainComposite, SWT.NONE);
			pvText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true, 1, 1));

			return mainComposite;
		}

		@Override
		protected void okPressed() {
			name = nameText.getText();
			pv = pvText.getText();
			super.okPressed();
		}

		@Override
		protected Point getInitialSize() {
			return new Point(350, 200);
		}

		@Override
		protected boolean isResizable() {
			return true;
		}

		public String getName() {
			return name;
		}

		public String getPv() {
			return pv;
		}
	}

	public static class ScannableInfo {
		private String name; // Name of scannable
		private String pvName; // PV to use for scannable (optional)

		public ScannableInfo() {
			name = "";
			pvName = "";
		}

		public ScannableInfo(String name, String pvName) {
			this.name = name;
			this.pvName = pvName;
		}

		public ScannableInfo(String name) {
			this.name = name;
			this.pvName = "";
		}

		public String getName() {
			return name;
		}

		public String getPvName() {
			return pvName;
		}

		@Override
		public String toString() {
			return "Scannable info : " + name + " (" + pvName +")";
		}
	}

	/**
	 * Useful for testing
	 * @param args
	 */
	public static void main(String[] args) {
		Display display = new Display();
		Shell shell = new Shell(display);

		shell.setLayout(new GridLayout(1, false));

		ScannableListEditor slMotorEditor = new ScannableListEditor(shell);
		slMotorEditor.create();
		slMotorEditor.open();

		shell.pack();
		shell.open();

		// Set up the event loop.
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch()) {
				// If no more entries in event queue
				display.sleep();
			}
		}
		display.dispose();
	}
}

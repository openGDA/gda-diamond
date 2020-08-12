/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import org.apache.commons.lang.StringUtils;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.dialogs.ListDialog;
import org.eclipse.ui.forms.widgets.FormToolkit;

import gda.device.Scannable;
import gda.factory.Finder;
import gda.observable.IObservable;
import gda.observable.IObserver;
import gda.observable.ObservableComponent;

public class ScannablePositionsComposite implements IObservable {

	private FormToolkit toolkit;
	private final Composite parent;
	private Text scannableToMoveTextbox;
	private Button collectMultipleSpectraButton;


	private String scannableName = "";
	private List< List<Double> > scannablePositions = Collections.emptyList();
	private boolean collectMultipleSpectra = false;

	private ObservableComponent observableComponent = new ObservableComponent();

	public ScannablePositionsComposite(Composite parent, FormToolkit toolkit) {
		this.parent = parent;
		this.toolkit = toolkit;
	}

	public void addSection() {
		toolkit.createLabel(parent, "Collect spectra at multiple positions ? ");
		collectMultipleSpectraButton = new Button(parent, SWT.CHECK);
		collectMultipleSpectraButton.setSelection(collectMultipleSpectra);
		collectMultipleSpectraButton.addListener(SWT.Selection,  e -> {
			setCollectMultipleSpectra(collectMultipleSpectraButton.getSelection());
			observableComponent.notifyIObservers(this, null);
		});

		toolkit.createLabel(parent, "Scannable to move :", SWT.None);
		scannableToMoveTextbox = toolkit.createText(parent, scannableName, SWT.BORDER);
		scannableToMoveTextbox.setEditable(false);
		GridDataFactory.swtDefaults().hint(200, SWT.DEFAULT).applyTo(scannableToMoveTextbox);

		Button selectScannableButton = toolkit.createButton(parent, "Select scannable to move...", SWT.PUSH);
		selectScannableButton.addListener(SWT.Selection, e -> selectScannable());

		Button setPositionButton = toolkit.createButton(parent, "Set positions...", SWT.PUSH);
		setPositionButton.addListener(SWT.Selection, e -> setPositions());
	}

	/**
	 * Display list dialog to select scannable from list of all available ones.
	 * Currently set scannable name is first in the list and selected when dialog is opened.
	 */
	private void selectScannable() {
		List<String> allScnNames = ScannableListEditor.getScannableNames();
		// Move selected selected scannable to top of the list,
		if (!scannableName.isEmpty() && allScnNames.contains(scannableName)) {
			allScnNames.remove(scannableName);
			allScnNames.add(0, scannableName);
		}

		List<String> shortNames = ScannableListEditor.getSafeScannableNames();
		allScnNames.removeAll(shortNames);

		ListDialog ld = ScannableListEditor.createSelectScannableDialog(parent, allScnNames, shortNames);

		// select the scannable in the list
		if (!scannableName.isEmpty()) {
			ld.setInitialElementSelections(Arrays.asList(scannableName));
			observableComponent.notifyIObservers(this, null);
		}
		ld.open();

		Object[] result =  ld.getResult();
		if (result != null && result.length>0) {
			setScannableName(result[0].toString());
		}
	}

	/**
	 * Setup list of values the scannable should be moved to
	 */
	private void setPositions() {
		Scannable scn = Finder.find(scannableName);
		if (scn == null) {
			String info = "Could not open positions editor\n";
			String message = StringUtils.isEmpty(scannableName) ?
					"No scannable has been selected" : "Scannable called '"+scannableName+" was not found";
			MessageDialog.openError(parent.getShell(), "Error", info+ message);
			return;
		}
		NumberTableEditor numberTableEditor = new NumberTableEditor(parent.getShell());
		numberTableEditor.setColumnNames(Arrays.asList(scn.getInputNames()));
		numberTableEditor.setColumnFormats(Arrays.asList(scn.getOutputFormat()));
		numberTableEditor.setTableValues(scannablePositions);
		if (numberTableEditor.open() == Window.OK) {
			scannablePositions = numberTableEditor.getTableValues();
			observableComponent.notifyIObservers(this, null);
		}
	}

	public String getScannableName() {
		return scannableName;
	}

	public void setScannableName(String scannableName) {
		this.scannableName = scannableName == null ? "" : scannableName;
		if (scannableToMoveTextbox != null && !scannableToMoveTextbox.isDisposed()) {
			scannableToMoveTextbox.setText(this.scannableName);
		}
	}

	public boolean isCollectMultipleSpectra() {
		return collectMultipleSpectra;
	}

	public void setCollectMultipleSpectra(boolean collectMultipleSpectra) {
		this.collectMultipleSpectra = collectMultipleSpectra;
		if (collectMultipleSpectraButton != null && !collectMultipleSpectraButton.isDisposed()) {
			collectMultipleSpectraButton.setSelection(collectMultipleSpectra);
		}
	}

	public List<List<Double>> getScannablePositions() {
		return scannablePositions;
	}

	public void setScannablePositions(List<List<Double>> scannablePositions) {
		if (scannablePositions == null) {
			this.scannablePositions = new ArrayList<>();
		} else {
			this.scannablePositions = new ArrayList<>(scannablePositions);
		}
	}

	public void setScannablePositionsFromList(List<Double> scannableList) {
		this.scannablePositions = new ArrayList<>();
		scannablePositions.add(scannableList);
	}

	@Override
	public void addIObserver(IObserver observer) {
		observableComponent.addIObserver(observer);

	}

	@Override
	public void deleteIObserver(IObserver observer) {
		observableComponent.deleteIObserver(observer);

	}

	@Override
	public void deleteIObservers() {
		observableComponent.deleteIObservers();
	}
}

/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction;

import java.text.DecimalFormat;
import java.util.Optional;
import java.util.function.Consumer;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.scanning.api.points.models.IScanPointGeneratorModel;
import org.eclipse.scanning.device.ui.AbstractModelEditor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Spinner;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.PlatformUI;

import gda.observable.IObservable;
import gda.observable.IObserver;
import gda.observable.ObservableComponent;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.diamond.daq.mapping.ui.diffraction.model.MutatorType;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController.RegionPathState;

/**
 * Concrete implementations should assume that {@link #setModel(ScanpathDocument)} will be called
 * before {@link #createEditorPart(Composite)}, but it may also be called after
 * so controls should update at that point.
 * <p>
 * Children should also call {@link #modelUpdated()} after their {@link ScanpathDocument} is updated.
 * <p>
 * After updating the model children may want to call {@link #updateMappingController()}
 * to reflect the new model in the mapping view.
 */
public abstract class ScanpathEditor extends AbstractModelEditor<ScanpathDocument> implements IObservable {

	private Composite composite;
	private final ObservableComponent observable = new ObservableComponent();

	private RegionAndPathController mappingController;
	private Consumer<RegionPathState> mappingUpdateListener = this::handleMappingUpdate;

	protected static final DecimalFormat DECIMAL_FORMAT = new DecimalFormat("#0.00");

	/**
	 * Used for controlling direction of data flow.
	 * <p>
	 * We return from {@link #updateMappingController()} early if set,
	 * otherwise we set it during the update.
	 * <p>
	 * Implementors are advised to do likewise while updating models from mapping events
	 */
	protected boolean handlingMappingUpdate;

	@Override
	public Composite createEditorPart(Composite parent) {
		composite = new Composite(parent, SWT.NONE);
		GridDataFactory.fillDefaults().align(SWT.FILL, SWT.FILL).grab(true, false).applyTo(composite);
		GridLayoutFactory.swtDefaults().applyTo(composite);

		initialiseMappingController();

		return composite;
	}

	protected Text createTextControls(Composite parent) {
		Text text = new Text(parent, SWT.BORDER);
		GridDataFactory.swtDefaults().hint(95, SWT.DEFAULT).applyTo(text);
		text.addModifyListener(e -> controlsToModel());
		return text;
	}

	protected Spinner createSpinner(Composite parent) {
		Spinner spinner = new Spinner(parent, SWT.NONE);
		spinner.setMinimum(3);
		spinner.setMaximum(Integer.MAX_VALUE);
		spinner.setSelection(5);
		spinner.setIncrement(1);
		spinner.addModifyListener(e -> controlsToModel());
		return spinner;
	}

	@Override
	public void dispose() {
		if (composite != null) {
			composite.dispose();
			mappingController.detachViewUpdater(mappingUpdateListener);
		}
		deleteIObservers();
	}

	protected abstract void controlsToModel();

	protected abstract void modelToControls();

	protected void updateModel(ScanpathDocument scanpathDocument) {
		setModel(scanpathDocument);
		modelUpdated();
	}


	/**
	 * The mapping controller will call this when a region or path is swapped.
	 * This will <em>not</em> be called when the existing region or path are modified.
	 * <p>
	 * Add listeners to the region and/or path in the given {@code mappingState}
	 * to track changes to their properties (remembering to remove the listeners when no longer required).
	 * <p>
	 * <em>Note:</em> to avoid partial update cycles you may wish to set {@link #handlingMappingUpdate}
	 * while updating the model from a region and/or path update. This will disable updates to the mapping controller.
	 * Just don't forget to unset it once the update is complete!
	 */
	protected abstract void handleMappingUpdate(RegionPathState mappingState);

	/**
	 * Used when updating the mapping controller
	 */
	protected abstract IMappingScanRegionShape modelToMappingRegion();

	/**
	 * Used when updating the mapping controller
	 */
	protected abstract IScanPointGeneratorModel modelToMappingPath();

	/**
	 * Call to synchronise the mapping controller after updating your model.
	 * <p>
	 * Sets {@link #handlingMappingUpdate} until the update is complete.
	 * If child implementations have listeners on mapping region and/or path,
	 * those listeners should not be active when this flag is set.
	 */
	protected void updateMappingController() {
		if (handlingMappingUpdate) return;

		handlingMappingUpdate = true;
		mappingController.getRegionSelectorListener().handleRegionChange(modelToMappingRegion());
		mappingController.changePath(modelToMappingPath());
		mappingController.updatePlotRegion();
		handlingMappingUpdate = false;
	}

	/**
	 * Call to send the new model to our observers
	 */
	protected void modelUpdated() {
		observable.notifyIObservers(this, getModel());
	}

	/**
	 * Convenience method for getting the {@link ScannableTrackDocument}
	 * corresponding to the x axis
	 */
	protected ScannableTrackDocument getXAxis() {
		return getModel().getScannableTrackDocuments().stream()
				.filter(doc -> doc.getAxis().equalsIgnoreCase("x"))
				.findFirst().orElseThrow();
	}

	/**
	 * Convenience method for getting the {@link ScannableTrackDocument}
	 * corresponding to the y axis
	 */
	protected ScannableTrackDocument getYAxis() {
		return getModel().getScannableTrackDocuments().stream()
				.filter(doc -> doc.getAxis().equalsIgnoreCase("y"))
				.findFirst().orElseThrow();
	}

	protected boolean isContinuous() {
		return getModel().getMutators().containsKey(MutatorType.CONTINUOUS.getMscanMutator());
	}

	protected boolean isAlternating() {
		return getModel().getMutators().containsKey(MutatorType.ALTERNATING.getMscanMutator());
	}

	@Override
	public void addIObserver(IObserver observer) {
		observable.addIObserver(observer);
	}

	@Override
	public void deleteIObserver(IObserver observer) {
		observable.deleteIObserver(observer);
	}

	@Override
	public void deleteIObservers() {
		observable.deleteIObservers();
	}

	private void initialiseMappingController() {
		mappingController = PlatformUI.getWorkbench().getService(RegionAndPathController.class);
		mappingController.initialise(Optional.of(mappingUpdateListener), Optional.empty());
		updateMappingController();
	}

	@Override
	public void setModel(ScanpathDocument model) {
		super.setModel(model);
		if (composite == null) {
			// controls not created yet
			return;
		}
		Display.getDefault().syncExec(this::modelToControls);
		updateMappingController();
	}

}
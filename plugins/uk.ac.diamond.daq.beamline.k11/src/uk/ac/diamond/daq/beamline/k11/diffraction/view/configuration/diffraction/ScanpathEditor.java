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

import static uk.ac.gda.ui.tool.ClientSWTElements.STRETCH;

import java.text.DecimalFormat;
import java.util.List;
import java.util.Optional;
import java.util.function.Consumer;
import java.util.stream.Stream;

import org.eclipse.scanning.api.points.models.IMapPathModel;
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
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument.Axis;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanningParametersUtils;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController.RegionPathState;
import uk.ac.gda.ui.tool.ClientSWTElements;

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

	private IMappingScanRegionShape region;
	private IMapPathModel path;

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
		composite = ClientSWTElements.innerComposite(parent, 1, true);

		initialiseMappingController();

		return composite;
	}

	protected Text createTextControls(Composite parent) {
		Text text = ClientSWTElements.numericTextBox(parent);
		text.addModifyListener(e -> controlsToModel());
		return text;
	}

	protected Spinner createSpinner(Composite parent) {
		Spinner spinner = new Spinner(parent, SWT.NONE);
		spinner.setMinimum(1);
		spinner.setMaximum(Integer.MAX_VALUE);
		spinner.setSelection(5);
		spinner.setIncrement(1);
		spinner.addModifyListener(e -> controlsToModel());
		STRETCH.applyTo(spinner);
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

	protected ScannableTrackDocument modifyAxis(ScannableTrackDocument axisToModify, double start, double stop, int points) {
		var modified = new ScannableTrackDocument(axisToModify);
		modified.setStart(start);
		modified.setStop(stop);
		modified.setPoints(points);
		return modified;
	}

	protected void updateAxes(ScannableTrackDocument updatedX, ScannableTrackDocument updatedY) {
		ScanningParametersUtils.updateAxes(getModel(), List.of(updatedX, updatedY));
		updateModel(getModel());
	}

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
	protected abstract IMapPathModel modelToMappingPath();

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

		var updatedRegion = modelToMappingRegion();
		if (region == null || !region.equals(updatedRegion)) {
			mappingController.getRegionSelectorListener().handleRegionChange(updatedRegion);
			region = updatedRegion;
		}

		var updatedPath = modelToMappingPath();
		if (path == null || !path.equals(updatedPath)) {
			mappingController.changePath(modelToMappingPath());
			path = updatedPath;
		}

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
		return ScanningParametersUtils.getAxis(getModel(), Axis.X);
	}

	/**
	 * Convenience method for getting the {@link ScannableTrackDocument}
	 * corresponding to the y axis
	 */
	protected ScannableTrackDocument getYAxis() {
		return ScanningParametersUtils.getAxis(getModel(), Axis.Y);
	}

	protected boolean isContinuous() {
		return Stream.of(getXAxis(), getYAxis()).anyMatch(ScannableTrackDocument::isContinuous);
	}

	protected boolean isAlternating() {
		return Stream.of(getXAxis(), getYAxis()).anyMatch(ScannableTrackDocument::isAlternating);
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
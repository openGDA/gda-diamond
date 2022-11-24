/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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

package uk.ac.gda.dls.client.views;

import static uk.ac.gda.dls.client.views.BatonStatusPopupMenuBuilder.showView;

import java.util.Objects;
import java.util.Optional;

import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.resource.FontDescriptor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.MouseAdapter;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.Font;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Canvas;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.swtdesigner.SWTResourceManager;

import gda.configuration.properties.LocalProperties;
import gda.jython.IBatonStateProvider;
import gda.jython.InterfaceProvider;
import gda.jython.UserMessage;
import gda.observable.IObservable;
import gda.observable.IObserver;
import uk.ac.gda.views.baton.MessageView;

final class BatonStatusComposite extends Composite {

	private static final Logger logger = LoggerFactory.getLogger(BatonStatusComposite.class);

	private static final Color BATON_HELD_COLOR = Display.getDefault().getSystemColor(SWT.COLOR_GREEN);
	private static final Color BATON_HELD_UDC_COLOR = Display.getDefault().getSystemColor(SWT.COLOR_BLUE);
	private static final Color BATON_NOT_HELD_COLOR = Display.getDefault().getSystemColor(SWT.COLOR_RED);

	private static final int MARGIN = 4;
	private static final int GRID_HINT = 40;

	private static final String BATON_HELD_TOOL_TIP = "Baton held!\nRight click open menu\nLeft click open manager";
	private static final String BATON_HELD_UDC_TOOL_TIP = "Baton held by automated client!\nRight click open menu\nLeft click open manager";
	private static final String BATON_NOT_HELD_TOOL_TIP = "Baton not held!\nRight click open menu\nLeft click open manager";

	private static final String CANNOT_CONNECT_TO_GDA_SERVER = "Cannot Connect to GDA Server";
	private static final String GDA_SERVER_IS_NOT_RESPONDING = "The GDA Server is not responding.\n\nPlease contact your GDA support engineer.";
	private static final String PROP_BATON_BANNER = "gda.beamline.baton.banner";

	private static final Display DEFAULT_DISPLAY = Display.getDefault();
	private static final UserInterfaceAsynchronously DEFAULT_DISPLAY_ASYNCH =
		DEFAULT_DISPLAY::asyncExec;

	private final IBatonStateProvider batonStateProvider;
	private final UserInterfaceAsynchronously displayAsynch;

	private AtomicColour currentColor;

	private Optional<Runnable> maybeDisposeFont = Optional.empty();

	private Canvas batonCanvas;

	private Font boldFont;
	private Label lblBanner;

	public BatonStatusComposite(Composite parent, int style, IBatonStateProvider batonStateProvision, String label) {
		super(parent, style);
		batonStateProvider = batonStateProvision;

		var ui = parent.getDisplay();
		displayAsynch = ui::asyncExec;
		var grp = prepareGroup(style, label);
		var stateColor = representBatonStateByColour(batonStateProvider);
		currentColor = new AtomicColour(stateColor);

		batonCanvas = new Canvas(grp, SWT.NONE);
		GridData gridData = new GridData(GridData.VERTICAL_ALIGN_FILL);
		gridData.widthHint = GRID_HINT;
		gridData.heightHint = GRID_HINT;
		batonCanvas.setLayoutData(gridData);

		addCanvasPaintListener(batonCanvas);
		var initialTooltip = getBatonStateTooltip(batonStateProvider);
		batonCanvas.setToolTipText(initialTooltip);
		BatonStatusPopupMenuBuilder.preparePopUpMenu(this, batonCanvas::setMenu, batonStateProvider);

		IObserver serverObserver = createServerObserver();

		try {
			var jsfObserver = InterfaceProvider.getJSFObserver();
			addObserver(jsfObserver,serverObserver);
		} catch (Exception ne) {
			DEFAULT_DISPLAY_ASYNCH.asynchronouslyExecuteOnUiThread( () -> {
				var activeShell = DEFAULT_DISPLAY.getActiveShell();
				MessageDialog.openWarning(activeShell, CANNOT_CONNECT_TO_GDA_SERVER, GDA_SERVER_IS_NOT_RESPONDING);
			});
		}

		batonCanvas.addMouseListener(new MouseAdapter() {

			@Override
			public void mouseUp(MouseEvent event) {
				if (event.button == 1) {
					try {
						PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(uk.ac.gda.views.baton.BatonView.ID);
					} catch (Exception ex) {
						logger.error("Cannot open baton manager", ex);
					}
				}
			}
		});

		String banner = LocalProperties.get(PROP_BATON_BANNER, " ");
		if (!(null==banner || banner.isEmpty()) ) {
			lblBanner = new Label(this, SWT.CENTER);
			boldFont = FontDescriptor.createFrom(lblBanner.getFont())
				.setStyle( SWT.BOLD )
				.createFont( lblBanner.getDisplay() );
			maybeDisposeFont = Optional.of(boldFont::dispose);
			lblBanner.setFont(boldFont);
			lblBanner.setText(banner);
			GridDataFactory.swtDefaults().align(SWT.CENTER, SWT.FILL).applyTo(lblBanner);
		}
	}

	@Override
	public void dispose() {
		super.dispose();
		maybeDisposeFont.ifPresent(Runnable::run);
	}

	public void setBannerProvider(IObservable provider) {
		IObserver iObserver = (source, arg) -> {
			if (arg instanceof String text) {
				lblBanner.setText(text);
			}
		};
		addObserver(provider, iObserver);
	}

	private Group prepareGroup(int style, String label) {
		GridDataFactory.fillDefaults().applyTo(this);
		GridLayoutFactory.swtDefaults().numColumns(1).applyTo(this);
		Group grp = new Group(this, style);
		GridDataFactory.fillDefaults().applyTo(grp);
		GridLayoutFactory.swtDefaults().numColumns(1).applyTo(grp);
		grp.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		grp.setText(label);
		GridLayoutFactory.swtDefaults().numColumns(1).applyTo(this);
		GridDataFactory.fillDefaults().applyTo(this);
		return grp;
	}

	private void updateBatonCanvas(String toolTipText) {
		displayAsynch.asynchronouslyExecuteOnUiThread( () -> {
			if (batonCanvas != null && !batonCanvas.isDisposed()) {
				batonCanvas.setToolTipText(toolTipText);
				batonCanvas.redraw();
				batonCanvas.update();
			}
		});
	}

	private IObserver createServerObserver() {
		return (source, arg) ->
			DEFAULT_DISPLAY_ASYNCH.asynchronouslyExecuteOnUiThread( () -> whenUpdateReceivedFromServer(arg) );
	}

	private void whenUpdateReceivedFromServer(Object arg) {
		if (arg instanceof gda.jython.batoncontrol.BatonChanged) {
			whenBatonChanges(batonStateProvider);
		}
		if (arg instanceof UserMessage) {
			ensureMessagesViewIsOpen();
		}
	}

	private void ensureMessagesViewIsOpen() {
		// Message received - ensure "Messages" view is open
		try {
			showView(MessageView.ID);
		} catch (Exception e) {
			logger.warn("Unable to open Messages view", e);
		}
	}

	private void whenBatonChanges(IBatonStateProvider batonStateProvider) {
		var stateColor = representBatonStateByColour(batonStateProvider);
		currentColor.writeCurrentColour(stateColor);
		var toolTipText = getBatonStateTooltip(batonStateProvider);
		updateBatonCanvas(toolTipText);
	}

	private void addCanvasPaintListener(Canvas canvas) {
		canvas.addPaintListener( paintEvent -> {
			GC gc = paintEvent.gc;
			gc.setAntialias(SWT.ON);
			var latestColor = currentColor.readCurrentColour();
			gc.setBackground(latestColor);
			gc.setLineWidth(1);
			Point topLeft = new Point(MARGIN, MARGIN);
			Point size = insideMarginsOf(canvas, MARGIN);
			gc.fillOval(topLeft.x, topLeft.y, size.x, size.y);
			gc.drawOval(topLeft.x, topLeft.y, size.x, size.y);
		});
	}

	private void addObserver(IObservable iObservable, IObserver iObserver) {
		if (Objects.isNull(iObservable) || Objects.isNull(iObserver)) {
			return;
		}
		iObservable.addIObserver(iObserver);
		DisposeListener releaseObserver = disposeEvent -> iObservable.deleteIObserver(iObserver);
		this.addDisposeListener(releaseObserver);
	}

	private static Point insideMarginsOf(Canvas canvas, int margin) {
		Rectangle clientArea = canvas.getClientArea();
		var delta = 2 * margin;
		return new Point(clientArea.width - delta, clientArea.height - delta);
	}

	private static String getBatonStateTooltip(IBatonStateProvider batonStateProvider) {
		if (isBatonHeld(batonStateProvider)) return BATON_HELD_TOOL_TIP;
		return isBatonHeldByUdc(batonStateProvider) ? BATON_HELD_UDC_TOOL_TIP : BATON_NOT_HELD_TOOL_TIP;
	}

	private static Color representBatonStateByColour(IBatonStateProvider batonStateProvider) {
		if (isBatonHeld(batonStateProvider)) return BATON_HELD_COLOR;
		return isBatonHeldByUdc(batonStateProvider) ? BATON_HELD_UDC_COLOR : BATON_NOT_HELD_COLOR;
	}

	private static boolean isBatonHeld(IBatonStateProvider batonStateProvider) {
		return batonStateProvider.amIBatonHolder();
	}

	private static boolean isBatonHeldByUdc(IBatonStateProvider batonStateProvider) {
		var batonHolder = batonStateProvider.getBatonHolder();
		return batonHolder != null && batonHolder.isAutomatedUser();
	}

	private static final class AtomicColour {

		private final Object synchronizationLock = new Object();

		private Color colour;

		private AtomicColour(Color initialColour) {
			writeCurrentColour(initialColour);
		}

		void writeCurrentColour(Color color) {
			synchronized (synchronizationLock) {
				colour = color;
			}
		}

		Color readCurrentColour() {
			synchronized (synchronizationLock) {
				return colour;
			}
		}
	}

	@FunctionalInterface
	interface UserInterfaceAsynchronously {
		void asynchronouslyExecuteOnUiThread(Runnable r);
	}
}

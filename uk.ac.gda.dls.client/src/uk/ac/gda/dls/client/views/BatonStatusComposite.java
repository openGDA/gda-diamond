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
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Consumer;
import java.util.function.Predicate;

import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.resource.FontDescriptor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.MouseAdapter;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Canvas;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Menu;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.StringUtils;

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

	private static final Color BATON_HELD_COLOR = getSystemColor(SWT.COLOR_GREEN);
	private static final Color BATON_HELD_UDC_COLOR = getSystemColor(SWT.COLOR_BLUE);

	private static final Color BATON_NOT_HELD_COLOR = getSystemColor(SWT.COLOR_RED);
	private static final Color STATUS_ABSENCE_COLOR = getSystemColor(SWT.COLOR_DARK_RED);

	private static final String BATON_HELD_TOOL_TIP = """
			Baton held!
			Right click open menu
			Left click open manager""";

	private static final String BATON_HELD_UDC_TOOL_TIP = """
			Baton held by automated client!
			Right click open menu
			Left click open manager""";

	private static final String BATON_NOT_HELD_TOOL_TIP = """
			Baton not held!
			Right click open menu
			Left click open manager""";

	private static final String CANNOT_CONNECT_TO_GDA_SERVER = "Cannot Connect to GDA Server.";

	private static final String GDA_SERVER_IS_NOT_RESPONDING = """
		The GDA Server is not responding.
		Please contact your GDA support engineer.""";

	private static final String PROP_BATON_BANNER = "gda.beamline.baton.banner";

	private static final String BATON_STATUS_UNAVAILABLE = """
			STATUS
			UNAVAILABLE
			""";

	private final Optional<Label> maybeLabelBanner;

	public BatonStatusComposite(Composite parent, int style, IBatonStateProvider batonStateProvision, String label) {
		super(parent, style);
		var ui = parent.getDisplay();
		var group = prepareGroup(this, style, label);
		maybeLabelBanner = maybeExtractBannerText().map(this::createBannerLabel);
		if (Objects.nonNull(batonStateProvision)) {
			prepareBatonStatusCanvas(ui, group, batonStateProvision);
		} else {
			prepareStatusUnavailableLabel(group);
		}
	}

	public void setBannerProvider(IObservable provider) {
		IObserver iObserver = (source, arg) -> {
			if (arg instanceof String argAsText) {
				Predicate<Label> excludeDisposedLabel = Predicate.not(Label::isDisposed);
				maybeLabelBanner.filter(excludeDisposedLabel)
								.ifPresent(label -> label.setText(argAsText));
			}
		};
		addObserverWithDisposalHandling(provider, iObserver);
	}

	private void prepareBatonStatusCanvas(Display ui, Group group, IBatonStateProvider batonStateProvision) {
		var canvas = new BatonStatusCanvas(group, batonStateProvision, ui::asyncExec);
		BatonStatusPopupMenuBuilder.preparePopUpMenu(this, canvas::setMenu, batonStateProvision);
	}

	private void prepareStatusUnavailableLabel(Group group) {
		var style = SWT.READ_ONLY;
		var label = new StyledText(group, style);
		label.setForeground(STATUS_ABSENCE_COLOR);
		label.setText(BATON_STATUS_UNAVAILABLE);
	}

	private void addObserverWithDisposalHandling(IObservable iObservable, IObserver iObserver) {

		if (Objects.isNull(iObservable) || Objects.isNull(iObserver)) {
			return;
		}
		iObservable.addIObserver(iObserver);
		DisposeListener releaseObserver = disposeEvent -> iObservable.deleteIObserver(iObserver);
		this.addDisposeListener(releaseObserver);
	}

	private Label createBannerLabel(String bannerText) {
		var banner = new Label(this, SWT.CENTER);
		var font = banner.getFont();
		var display = banner.getDisplay();
		var boldFont = FontDescriptor.createFrom(font)
									.setStyle(SWT.BOLD)
									.createFont(display);
		banner.addDisposeListener(e -> boldFont.dispose());
		banner.setFont(boldFont);
		banner.setText(bannerText);
		GridDataFactory.swtDefaults()
						.align(SWT.CENTER, SWT.FILL)
						.applyTo(banner);
		return banner;
	}

	static Optional<String> maybeExtractBannerText() {
		var textFromProperty = LocalProperties.get(PROP_BATON_BANNER, " ");
		return Optional.of(textFromProperty)
						.filter(StringUtils::hasLength);
	}

	static Group prepareGroup(Composite parent, int style, String label) {
		prepareAsSingleColumnWithDefaultFill(parent);
		var group = new Group(parent, style);
		prepareAsSingleColumnWithDefaultFill(group);
		var transparent = SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT);
		group.setBackground(transparent);
		group.setText(label);
		return group;
	}

	private static void prepareAsSingleColumnWithDefaultFill(Composite composite) {
		Consumer<Composite> applyFill =
			GridDataFactory.fillDefaults()::applyTo;
		Consumer<Composite> setSingleColumn  =
			GridLayoutFactory.swtDefaults()
							.numColumns(1)::applyTo;
		applyFill.andThen(setSingleColumn).accept(composite);
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

	private static Color getSystemColor(int identifier) {
		return Display.getDefault()
						.getSystemColor(identifier);
	}

	private final class BatonStatusCanvas {

		private static final int OUTLINE_LINE_WIDTH = 1;
		private static final Display DEFAULT_DISPLAY = Display.getDefault();
		private static final UiThreadAsynchExecution DEFAULT_DISPLAY_ASYNCH =
			DEFAULT_DISPLAY::asyncExec;

		private static final int PRIMARY_MOUSE_BUTTON = 1;
		private static final int CANVAS_MARGIN = 4;
		private static final int GRID_HINT = 40;

		private static final String CANNOT_OPEN_BATON_MANAGER = "Cannot open baton manager.";
		private static final String UNABLE_TO_OPEN_MESSAGES_VIEW = "Unable to open Messages view";

		private final IBatonStateProvider batonStateProvider;
		private final AtomicReference<Color> atomicColourCache;
		private final Canvas batonCanvas;
		private final UiThreadAsynchExecution uiAsynchExec;

		private BatonStatusCanvas(Group group, IBatonStateProvider batonStateProvision, UiThreadAsynchExecution displayAsynch) {
			if(batonStateProvision == null) {
				logger.error("Baton State Provider absent - Baton display will not update correctly");
			}
			batonStateProvider = batonStateProvision;
			var initialStatusColor = representBatonStateByColour(batonStateProvider);
			atomicColourCache = new AtomicReference<>(initialStatusColor);

			uiAsynchExec = displayAsynch;
			batonCanvas = new Canvas(group, SWT.NONE);

			GridData gridData = new GridData(GridData.VERTICAL_ALIGN_FILL);
			gridData.widthHint = GRID_HINT;
			gridData.heightHint = GRID_HINT;
			batonCanvas.setLayoutData(gridData);

			addCanvasPaintListener();
			addMouseListener();
			whenBatonChanges(batonStateProvision);  // initialise baton canvas state
			var serverObserver = createServerObserver();
			addServerObserverWithDisposalHandling(serverObserver);
		}

		void setMenu(Menu menu) {
			batonCanvas.setMenu(menu);
		}

		private void addServerObserverWithDisposalHandling(IObserver serverObserver) {
			try {
				var jsfObserver = InterfaceProvider.getJSFObserver();
				addObserverWithDisposalHandling(jsfObserver, serverObserver);
			} catch (Exception ne) {
				DEFAULT_DISPLAY_ASYNCH.asynchronouslyExecuteOnUiThread( () -> {
					var activeShell = DEFAULT_DISPLAY.getActiveShell();
					MessageDialog.openWarning(activeShell, CANNOT_CONNECT_TO_GDA_SERVER, GDA_SERVER_IS_NOT_RESPONDING);
				});
			}
		}

		private void whenBatonChanges(IBatonStateProvider batonStateProvider) {
			var stateColor = representBatonStateByColour(batonStateProvider);
			atomicColourCache.set(stateColor);
			var toolTipText = getBatonStateTooltip(batonStateProvider);
			updateBatonCanvas(toolTipText);
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
				logger.warn(UNABLE_TO_OPEN_MESSAGES_VIEW, e);
			}
		}

		private void updateBatonCanvas(String toolTipText) {
			uiAsynchExec.asynchronouslyExecuteOnUiThread( () -> {
				if (!batonCanvas.isDisposed()) {
					batonCanvas.setToolTipText(toolTipText);
					batonCanvas.redraw();
					batonCanvas.update();
				}
			});
		}

		private void addMouseListener() {
			batonCanvas.addMouseListener(new MouseAdapter() {

				@Override
				public void mouseUp(MouseEvent event) {
					if(PRIMARY_MOUSE_BUTTON != event.button) {
						return;
					}
					var identifiedBatonView = uk.ac.gda.views.baton.BatonView.ID;
					try {
						showView(identifiedBatonView);
					} catch (Exception exception) {
						logger.error(CANNOT_OPEN_BATON_MANAGER, exception);
					}
				}
			});
		}

		private void addCanvasPaintListener() {
			batonCanvas.addPaintListener( paintEvent -> {
				GC gc = paintEvent.gc;
				gc.setAntialias(SWT.ON);
				var latestColor = atomicColourCache.get();
				gc.setBackground(latestColor);
				gc.setLineWidth(OUTLINE_LINE_WIDTH);
				Point topLeft = new Point(CANVAS_MARGIN, CANVAS_MARGIN);
				Point size = insideMarginsOf(batonCanvas, CANVAS_MARGIN);
				gc.fillOval(topLeft.x, topLeft.y, size.x, size.y);
				gc.drawOval(topLeft.x, topLeft.y, size.x, size.y);
			});
		}

		private static Point insideMarginsOf(Canvas canvas, int margin) {
			Rectangle clientArea = canvas.getClientArea();
			var delta = 2 * margin;
			var marginX = clientArea.width - delta;
			var marginY = clientArea.height - delta;
			return new Point(marginX, marginY);
		}
	}

	@FunctionalInterface
	interface UiThreadAsynchExecution {
		void asynchronouslyExecuteOnUiThread(Runnable r);
	}
}

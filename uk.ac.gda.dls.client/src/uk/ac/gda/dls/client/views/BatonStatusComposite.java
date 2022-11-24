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

import java.util.Optional;
import java.util.function.Consumer;

import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.resource.FontDescriptor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.MouseAdapter;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.events.PaintEvent;
import org.eclipse.swt.events.PaintListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
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
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.MenuItem;
import org.eclipse.swt.widgets.MessageBox;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.swtdesigner.SWTResourceManager;

import gda.configuration.properties.LocalProperties;
import gda.jython.IBatonStateProvider;
import gda.jython.InterfaceProvider;
import gda.jython.UserMessage;
import gda.jython.batoncontrol.ClientDetails;
import gda.observable.IObservable;
import gda.observable.IObserver;
import uk.ac.gda.views.baton.MessageView;
import uk.ac.gda.views.baton.action.RefreshBatonAction;

final class BatonStatusComposite extends Composite {
	private static final Logger logger = LoggerFactory.getLogger(BatonStatusComposite.class);

	private static final Color BATON_HELD_COLOR = Display.getDefault().getSystemColor(SWT.COLOR_GREEN);
	private static final Color BATON_HELD_UDC_COLOR = Display.getDefault().getSystemColor(SWT.COLOR_BLUE);
	private static final Color BATON_NOT_HELD_COLOR = Display.getDefault().getSystemColor(SWT.COLOR_RED);
	private static final String BATON_HELD_TOOL_TIP = "Baton held!\nRight click open menu\nLeft click open manager";
	private static final String BATON_HELD_UDC_TOOL_TIP = "Baton held by automated client!\nRight click open menu\nLeft click open manager";
	private static final String BATON_NOT_HELD_TOOL_TIP = "Baton not held!\nRight click open menu\nLeft click open manager";
	private static final String PROP_BATON_BANNER = "gda.beamline.baton.banner";

	private static final String BATON_REQUESTED = "Baton requested";
	private static final String REQUESTED_BATON_FROM_UNATTENDED_CLIENT_MESSAGE =
			"You have requested the baton from an automated client.\n\nThe automated client"
			+ " is finishing the current instruction, after which you will be assigned the"
			+ " baton automatically. Thank you for your patience.";
	private static final String TAKE_MESSAGE = "You do not have enough authorisation to take the"
			+ " baton from the current holder.\n\nThe current holder is aware of your request and"
			+ " will normally release within two minutes.";
	private static final String REQUEST_MESSAGE = "The current holder is aware of your request."
			+ "\n\nNormally the baton is released within two minutes.";

	private static final Display DEFAULT_DISPLAY = Display.getDefault();
	private static final UserInterfaceAsynchronously DEFAULT_DISPLAY_ASYNCH =
		DEFAULT_DISPLAY::asyncExec;

	private final IBatonStateProvider batonStateProvider;
	private final Consumer<Runnable> displayAsyncExec;

	private Optional<Runnable> maybeDisposeFont = Optional.empty();

	private Color currentColor;
	private Canvas batonCanvas;
	private IBatonStateProvider batonState = InterfaceProvider.getBatonStateProvider();
	private Font boldFont;
	private Label lblBanner;

	private MenuItem takeBaton;
	private MenuItem passBatonToUDCClient;
	private MenuItem requestBaton;
	private MenuItem releaseBaton;
	private MenuItem openChat;

	public BatonStatusComposite(Composite parent, int style, IBatonStateProvider batonStateProvision, Display display, String label) {
		super(parent, style);
		batonStateProvider = batonStateProvision;

		GridDataFactory.fillDefaults().applyTo(this);
		GridLayoutFactory.swtDefaults().numColumns(1).applyTo(this);

		Group grp = new Group(this, style);
		GridDataFactory.fillDefaults().applyTo(grp);
		GridLayoutFactory.swtDefaults().numColumns(1).applyTo(grp);
		grp.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		grp.setText(label);

		displayAsyncExec = display::asyncExec;
		GridLayoutFactory.swtDefaults().numColumns(1).applyTo(this);
		GridDataFactory.fillDefaults().applyTo(this);

		currentColor = representBatonStateByColour(batonStateProvision);

		batonCanvas = new Canvas(grp, SWT.NONE);
		GridData gridData = new GridData(GridData.VERTICAL_ALIGN_FILL);
		gridData.widthHint = 40;
		gridData.heightHint = 40;
		batonCanvas.setLayoutData(gridData);
		batonCanvas.addPaintListener(new PaintListener() {
			@Override
			public void paintControl(PaintEvent e) {
				GC gc = e.gc;
				gc.setAntialias(SWT.ON);
				gc.setBackground(currentColor);
				gc.setLineWidth(1);
				Rectangle clientArea = batonCanvas.getClientArea();
				final int margin = 4;
				final Point topLeft = new Point(margin, margin);
				final Point size = new Point(clientArea.width - margin * 2, clientArea.height - margin * 2);
				gc.fillOval(topLeft.x, topLeft.y, size.x, size.y);
				gc.drawOval(topLeft.x, topLeft.y, size.x, size.y);
			}
		});
		var initialTooltip = getBatonStateTooltip(batonStateProvider);
		batonCanvas.setToolTipText(initialTooltip);
		batonCanvas.setMenu(createPopup(this));

		IObserver serverObserver = createServerObserver();

		try {
			var jsfObserver = InterfaceProvider.getJSFObserver();
			jsfObserver.addIObserver(serverObserver);
		} catch (Exception ne) {
			Display.getDefault().asyncExec(new Runnable() {
				@Override
				public void run() {
					MessageDialog.openWarning(Display.getDefault().getActiveShell(), "Cannot Connect to GDA Server",
							"The GDA Server is not responding.\n\nPlease contact your GDA support engineer.");
				}
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

	public void setBannerProvider(IObservable provider) {
		if (null != provider) {
			provider.addIObserver(
				(source, arg) -> {
					if (arg instanceof String) {
						lblBanner.setText((String) arg);
					}
				}
			);
		}
	}

	private void updateBatonCanvas(String toolTipText) {
		displayAsyncExec.accept(new Runnable() {

			@Override
			public void run() {
				if (batonCanvas != null && !batonCanvas.isDisposed()) {
					batonCanvas.setToolTipText(toolTipText);
					batonCanvas.redraw();
					batonCanvas.update();
				}
			}
		});
	}

	@SuppressWarnings("unused")
	private Menu createPopup(Composite parent) {

		Menu menu = new Menu(parent);

		takeBaton = new MenuItem(menu, SWT.NONE);
		takeBaton.setText("Take Baton");
		takeBaton.addSelectionListener(popupSelectionListener);

		releaseBaton = new MenuItem(menu, SWT.NONE);
		releaseBaton.setText("Release Baton");
		releaseBaton.addSelectionListener(popupSelectionListener);
		requestBaton = new MenuItem(menu, SWT.NONE);
		requestBaton.setText("Request Baton");
		requestBaton.addSelectionListener(popupSelectionListener);

		new MenuItem(menu, SWT.SEPARATOR);

		openChat = new MenuItem(menu, SWT.NONE);
		openChat.setText("Messaging");
		openChat.addSelectionListener(popupSelectionListener);

		if (udcClientExists()) {
			passBatonToUDCClient = new MenuItem(menu, SWT.NONE);
			passBatonToUDCClient.setText("Pass baton to UDC client");
			passBatonToUDCClient.addSelectionListener(popupSelectionListener);
		}

		return menu;
	}

	SelectionListener popupSelectionListener = new SelectionAdapter() {
		@Override
		public void widgetSelected(SelectionEvent event) {
			MenuItem selected = null;

			if (event.widget instanceof MenuItem) {
				selected = (MenuItem) event.widget;
			}
			else
				return;

			MessageBox messageBox = new MessageBox(PlatformUI.getWorkbench().getActiveWorkbenchWindow().getShell(), SWT.OK | SWT.ICON_WARNING);

			if (selected.equals(takeBaton) || selected.equals(requestBaton)) {
				if (!InterfaceProvider.getBatonStateProvider().requestBaton()) {
					if (InterfaceProvider.getBatonStateProvider().getBatonHolder().isAutomatedUser()) {
						messageBox.setMessage(REQUESTED_BATON_FROM_UNATTENDED_CLIENT_MESSAGE);
					} else {
						if (selected.equals(takeBaton)) {
							messageBox.setMessage(TAKE_MESSAGE);
						} else {
							messageBox.setMessage(REQUEST_MESSAGE);
						}
					}
					messageBox.setText(BATON_REQUESTED);
					messageBox.open();
				}
				RefreshBatonAction.refresh();
			}
			else if (selected.equals(releaseBaton)) {
				InterfaceProvider.getBatonStateProvider().returnBaton();
			}
			else if (selected.equals(openChat)) {
				try {
					PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(MessageView.ID);
				} catch (PartInitException e) {
					logger.error("Cannot show messages: ", e);
				}
			}
			else if (selected.equals(passBatonToUDCClient)) {
				int batonHolderIndex = InterfaceProvider.getBatonStateProvider().getBatonHolder().getIndex();
				ClientDetails[] clients = InterfaceProvider.getBatonStateProvider().getOtherClientInformation();
				int udcClientIndex = 0;
				for (ClientDetails client : clients) {
					if (client.isAutomatedUser()) {
						udcClientIndex = client.getIndex();
						break;
					}
				}
				InterfaceProvider.getBatonStateProvider().assignBaton(udcClientIndex, batonHolderIndex);
			}
		}
	};

	@Override
	public void dispose() {
		super.dispose();
		maybeDisposeFont.ifPresent(Runnable::run);
	}

	private IObserver createServerObserver() {
		return (source, arg) ->
			DEFAULT_DISPLAY_ASYNCH.asynchronouslyExecuteOnUiThread( () -> whenServerBroadcastsUpdate(arg) );
	}

	public boolean udcClientExists() {
		ClientDetails[] clients = batonState.getOtherClientInformation();
		boolean udcClientExists = false;
		for (ClientDetails client : clients) {
			if (client.isAutomatedUser()) {
				udcClientExists = true;
				break;
			}
		}
		return udcClientExists;
	}

	private void whenServerBroadcastsUpdate(Object arg) {
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
		currentColor = representBatonStateByColour(batonStateProvider);
		var toolTipText = getBatonStateTooltip(batonStateProvider);
		updateBatonCanvas(toolTipText);
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

	@FunctionalInterface
	interface UserInterfaceAsynchronously {
		void asynchronouslyExecuteOnUiThread(Runnable r);
	}
}

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

import java.util.Arrays;
import java.util.Optional;
import java.util.function.Consumer;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.MenuItem;
import org.eclipse.swt.widgets.MessageBox;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jython.IBatonStateProvider;
import gda.jython.batoncontrol.ClientDetails;
import uk.ac.gda.views.baton.MessageView;
import uk.ac.gda.views.baton.action.RefreshBatonAction;

final class BatonStatusPopupMenuBuilder {

	private static final Logger logger = LoggerFactory.getLogger(BatonStatusPopupMenuBuilder.class);

	private static final String BATON_REQUESTED = "Baton requested";

	private static final String REQUESTED_BATON_FROM_UNATTENDED_CLIENT_MESSAGE ="""
		You have requested the baton from an automated client:

		The automated client is finishing the current instruction,
		 after which you will be assigned the baton automatically.

		Thank you for your patience.""";


	private static final String TAKE_MESSAGE ="""
		You do not have enough authorisation to take the baton from the current holder.

		The current holder is aware of your request and will normally release within two minutes.""";

	private static final String REQUEST_MESSAGE = """
		The current holder is aware of your request.

		Normally the baton is released within two minutes.""";


	private final MenuItem takeBaton;
	private final MenuItem requestBaton;
	private final MenuItem releaseBaton;
	private final MenuItem openChat;
	private final Optional<MenuItem> maybePassBatonToUdcClient;
	private final Menu menu;

	private BatonStatusPopupMenuBuilder(Composite parent, IBatonStateProvider batonStateProvider) {
		menu = new Menu(parent);
		var popupSelectionListener = buildPopUpSelectionListener(batonStateProvider);
		takeBaton = new MenuItem(menu, SWT.NONE);
		takeBaton.setText("Take Baton");
		takeBaton.addSelectionListener(popupSelectionListener);
		releaseBaton = new MenuItem(menu, SWT.NONE);
		releaseBaton.setText("Release Baton");
		releaseBaton.addSelectionListener(popupSelectionListener);
		requestBaton = new MenuItem(menu, SWT.NONE);
		requestBaton.setText("Request Baton");
		requestBaton.addSelectionListener(popupSelectionListener);
		addMenuSeparator(menu);
		openChat = new MenuItem(menu, SWT.NONE);
		openChat.setText("Messaging");
		openChat.addSelectionListener(popupSelectionListener);
		maybePassBatonToUdcClient =
			Optional.of(popupSelectionListener)
					.filter(listener -> udcClientExists(batonStateProvider))
					.map( listener -> buildPassBatonToUdcMenuItem(menu, listener ));
	}

	private SelectionListener buildPopUpSelectionListener(IBatonStateProvider batonStateProvider) {
		return new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				var widget = event.widget;
				if (widget instanceof MenuItem selected) {
					var shell = getActiveWorkBenchWindow().getShell();
					var menuSelectionHandler = new MenuItemSelectionHandling(shell, batonStateProvider);
					menuSelectionHandler.menuItemSelected(selected);
				}
			}
		};
	}

	private void integrateMenu(Consumer<Menu> menuUsage) {
		menuUsage.accept(menu);
	}

	private static MenuItem buildPassBatonToUdcMenuItem(Menu menu, SelectionListener popupSelectionListener) {
		var passBatonToUdcClient = new MenuItem(menu, SWT.NONE);
		passBatonToUdcClient.setText("Pass baton to UDC client");
		passBatonToUdcClient.addSelectionListener(popupSelectionListener);
		return passBatonToUdcClient;
	}

	@SuppressWarnings("unused")
	private static void addMenuSeparator(Menu menu) {
		new MenuItem(menu, SWT.SEPARATOR);
	}

	private static int getUdcClientIndex(IBatonStateProvider batonStateProvider) {
		var noClient = 0;
		if(!udcClientExists(batonStateProvider)) return noClient;
		return Arrays.stream(batonStateProvider.getOtherClientInformation())
				.filter(ClientDetails::isAutomatedUser)
				.findFirst()
				.map(ClientDetails::getIndex)
				.orElse(noClient);
	}

	static void preparePopUpMenu(Composite parent, Consumer<Menu> canvasMenuUsage, IBatonStateProvider batonStateProvider) {
		var builder = new BatonStatusPopupMenuBuilder(parent, batonStateProvider);
		builder.integrateMenu(canvasMenuUsage);
	}

	static boolean udcClientExists(IBatonStateProvider batonStateProvider) {
		if(batonStateProvider == null) return false;
		return Arrays.stream(batonStateProvider.getOtherClientInformation())
						.anyMatch(ClientDetails::isAutomatedUser);
	}

	static IWorkbenchWindow getActiveWorkBenchWindow() {
		var workBench = PlatformUI.getWorkbench();
		return workBench.getActiveWorkbenchWindow();
	}

	static void showView(String viewId) throws PartInitException {
		var activePage = getActiveWorkBenchWindow().getActivePage();
		activePage.showView(viewId);
	}

	final class MenuItemSelectionHandling {

		private final Shell shell;
		private final IBatonStateProvider batonStateProvider;

		private MenuItemSelectionHandling(Shell shell, IBatonStateProvider batonStateProvider) {
			this.shell = shell;
			this.batonStateProvider = batonStateProvider;
		}

		private boolean isOpeningChat(MenuItem selectedItem) {
			return selectedItem.equals(openChat);
		}

		private boolean isRequestingBaton(MenuItem selectedItem) {
			return selectedItem.equals(requestBaton);
		}

		private boolean isReleasingBaton(MenuItem selectedItem) {
			return selectedItem.equals(releaseBaton);
		}

		private boolean isTakingBaton(MenuItem selectedItem) {
			return selectedItem.equals(takeBaton);
		}

		private boolean isPassingBatonToUdc(MenuItem selected) {
			return maybePassBatonToUdcClient.filter(selected::equals).isPresent();
		}

		private void handleOpeningChat() {
			try {
				showView(MessageView.ID);
			} catch (PartInitException e) {
				logger.error("Cannot show messages: ", e);
			}
		}

		private void handleReleasingBaton() {
			batonStateProvider.returnBaton();
		}

		private ClientDetails getBatonHolder() {
			return batonStateProvider.getBatonHolder();
		}

		private boolean isBatonHeldByUdc() {
			return getBatonHolder().isAutomatedUser();
		}

		private void handleGrabbingBaton(boolean takingBaton) {
			var message = takingBaton ? TAKE_MESSAGE : REQUEST_MESSAGE;
			var messageBox = new MessageBox(shell, SWT.OK | SWT.ICON_WARNING);
			if (!batonStateProvider.requestBaton()) {
				messageBox.setText(BATON_REQUESTED);
				var conditionalMessage = isBatonHeldByUdc() ? REQUESTED_BATON_FROM_UNATTENDED_CLIENT_MESSAGE : message;
				messageBox.setMessage(conditionalMessage);
				messageBox.open();
			}
			RefreshBatonAction.refresh();
		}

		private void handlePassOfBatonToUdc() {
			int batonHolderIndex = getBatonHolder().getIndex();
			int udcClientIndex = getUdcClientIndex(batonStateProvider);
			batonStateProvider.assignBaton(udcClientIndex, batonHolderIndex);
		}

		void menuItemSelected(MenuItem selected) {
			var takingBaton = isTakingBaton(selected);

			var grabbingBaton = takingBaton || isRequestingBaton(selected);
			if (grabbingBaton) {
				handleGrabbingBaton(takingBaton);
				return;
			}

			var releasingBaton = isReleasingBaton(selected);
			if (releasingBaton) {
				handleReleasingBaton();
				return;
			}

			var openingChat = isOpeningChat(selected);
			if (openingChat) {
				handleOpeningChat();
				return;
			}

			var passingBatonToUdc = isPassingBatonToUdc(selected);
			if (passingBatonToUdc) {
				handlePassOfBatonToUdc();
			}
		}
	}
}

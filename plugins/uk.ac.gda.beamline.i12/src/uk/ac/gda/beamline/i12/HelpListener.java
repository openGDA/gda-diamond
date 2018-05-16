/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i12;

import gda.observable.IObservable;
import gda.observable.IObserver;

import java.net.MalformedURLException;

import org.eclipse.core.runtime.IAdaptable;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ISetSelectionTarget;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class HelpListener {

	private static final String URL = "URL:";

	private static final Logger logger = LoggerFactory.getLogger(HelpListener.class);

	private static class URLHolder implements IAdaptable {
		private final String url;

		public URLHolder(String url) {
			this.url = url;

		}

		@Override
		public Object getAdapter(Class adapter) {
			if (java.net.URL.class.equals(adapter)) {
				try {
					return new java.net.URL(url);
				} catch (MalformedURLException e) {
					logger.error("Error attempting to create url object from string "+url, e);
				}
			}
			return null;
		}

	}

	private IObserver helpObserver = new IObserver() {

		@Override
		public void update(Object source, Object arg) {
			if (source.equals(helpObservable) && arg.toString().startsWith(URL)) {
				final String urlVal = arg.toString().substring(URL.length());
				if (PlatformUI.getWorkbench().getDisplay() != null) {
					PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {

						@Override
						public void run() {
							try {
								IViewPart showView = PlatformUI.getWorkbench().getActiveWorkbenchWindow()
										.getActivePage().showView("org.eclipse.ui.browser.view");
								if (showView instanceof ISetSelectionTarget) {
									ISetSelectionTarget tgt = (ISetSelectionTarget) showView;
									tgt.selectReveal(new StructuredSelection(new URLHolder(urlVal.replace("'", ""))));
								}

							} catch (PartInitException e) {
								logger.error("Unable to show view for org.eclipse.ui.browser.view", e);
							}
						}
					});
				}
			}
		}
	};

	private IObservable helpObservable;

	public void setHelpObservable(IObservable helpObservable) {
		this.helpObservable = helpObservable;
		if (this.helpObserver != null) {
			this.helpObservable.addIObserver(helpObserver);
		}
	}

}

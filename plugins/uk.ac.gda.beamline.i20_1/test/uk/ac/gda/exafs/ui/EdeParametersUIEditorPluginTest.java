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

package uk.ac.gda.exafs.ui;


import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import java.io.File;

import org.eclipse.core.filesystem.EFS;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.ide.FileStoreEditorInput;
import org.junit.Before;
import org.junit.Test;

import uk.ac.gda.ClientManager;
import uk.ac.gda.exafs.ui.describers.EdeScanParametersDescriber;
import uk.ac.gda.util.PackageUtils;

/**
 * Run as junit plugin test.
 */
public class EdeParametersUIEditorPluginTest {
	
	/**
	 * Force into testing mode.
	 */
	static {
		ClientManager.setTestingMode(true);
	}
	
	private EdeScanParametersEditor editor;
	private EdeScanParametersUIEditor uiEd;
	/**
	 * @throws Throwable
	 */
	@Before
	public void setUp() throws Throwable {
		ClientManager.setTestingMode(true);
		
		final IWorkbenchWindow window = PlatformUI.getWorkbench().getActiveWorkbenchWindow();
		
		final File xml = new File(PackageUtils.getTestPath(EdeParametersUIEditorPluginTest.class,"test")+"/EdeScan_Parameters.xml");
		
		final FileStoreEditorInput fileInput = new FileStoreEditorInput(EFS.getLocalFileSystem().fromLocalFile(xml));
		
		// Close the introduction page.
		this.editor = (EdeScanParametersEditor)window.getActivePage().openEditor(fileInput, EdeScanParametersDescriber.ID);
		
		this.uiEd = (EdeScanParametersUIEditor)editor.getRichBeanEditor();
	}
	

	@Test
	public final void testXML() {
		try {
			assertEquals("group1",this.uiEd.getTimingGroups().getFieldValue("label"));
		} catch (Exception e) {
			fail(e.getMessage());
		}
		
//		assertEquals("group1",this.uiEd.getDelayBetweenRepetitions().getValue());

	}
	


}

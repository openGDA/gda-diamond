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


import gda.exafs.ui.I20SampleParametersEditor;
import gda.exafs.ui.I20SampleParametersUIEditor;

import java.io.File;

import org.eclipse.core.filesystem.EFS;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.ide.FileStoreEditorInput;
import org.junit.Before;
import org.junit.Test;

import uk.ac.gda.ClientManager;
import uk.ac.gda.exafs.ui.describers.I20SampleDescriber;
import uk.ac.gda.richbeans.components.scalebox.NumberBox;
import uk.ac.gda.richbeans.components.selector.VerticalListEditor;
import uk.ac.gda.util.PackageUtils;

/**
 * Run as junit plugin test.
 */
public class I20SampleParametersUIEditorPluginTest {
	
	/**
	 * Force into testing mode.
	 */
	static {
		ClientManager.setTestingMode(true);
	}
	
	private I20SampleParametersEditor editor;
	private I20SampleParametersUIEditor uiEd;
	/**
	 * @throws Throwable
	 */
	@Before
	public void setUp() throws Throwable {
		ClientManager.setTestingMode(true);
		
		final IWorkbenchWindow window = PlatformUI.getWorkbench().getActiveWorkbenchWindow();
		
		final File xml = new File(PackageUtils.getTestPath(I20SampleParametersUIEditorPluginTest.class)+"/Sample_Parameters.xml");	
		final FileStoreEditorInput fileInput = new FileStoreEditorInput(EFS.getLocalFileSystem().fromLocalFile(xml));
	
		this.editor = (I20SampleParametersEditor)window.getActivePage().openEditor(fileInput, I20SampleDescriber.ID);
		this.uiEd = (I20SampleParametersUIEditor)editor.getRichBeanEditor();
		
		// TODO add a enumpositioner to the finder with positions Copper, Iron and Silicon
	}
	
	/**
	 * Bounds working
	 * @throws Throwable
	 */ 
	@Test
	public final void testFurnaceBounds() throws Throwable {
		
		if (!uiEd.getSampleEnvironment().getValue().equals("Furnace")) {
			throw new Exception("The configuration loaded should be furnace and is "+uiEd.getSampleEnvironment().getValue());
		}
		
		// Check bounds are ok then set them wrong and check they are red.
		checkBounds(uiEd.getFurnaceParameters().getX(), true);
		checkBounds(uiEd.getFurnaceParameters().getY(), true);
		checkBounds(uiEd.getFurnaceParameters().getZ(), true);
		checkBounds(uiEd.getFurnaceParameters().getTemperature(), true);
		checkBounds(uiEd.getFurnaceParameters().getTolerance(),   true);
		checkBounds(uiEd.getFurnaceParameters().getTime(),        true);
		
		uiEd.getFurnaceParameters().getX().setValue(16d);
		uiEd.getFurnaceParameters().getY().setValue(21d);
		uiEd.getFurnaceParameters().getZ().setValue(16d);
		uiEd.getFurnaceParameters().getTemperature().setValue(1301d);
		uiEd.getFurnaceParameters().getTolerance().setValue(6d);
		uiEd.getFurnaceParameters().getTime().setValue(401d);
		
		checkBounds(uiEd.getFurnaceParameters().getX(), false);
		checkBounds(uiEd.getFurnaceParameters().getY(), false);
		checkBounds(uiEd.getFurnaceParameters().getZ(), false);
		checkBounds(uiEd.getFurnaceParameters().getTemperature(), false);
		checkBounds(uiEd.getFurnaceParameters().getTolerance(),   false);
		checkBounds(uiEd.getFurnaceParameters().getTime(),        false);
		
		uiEd.getFurnaceParameters().getX().setValue(0d);
		uiEd.getFurnaceParameters().getY().setValue(0d);
		uiEd.getFurnaceParameters().getZ().setValue(0d);
		uiEd.getFurnaceParameters().getTemperature().setValue(295d);
		uiEd.getFurnaceParameters().getTolerance().setValue(0d);
		uiEd.getFurnaceParameters().getTime().setValue(0d);

		checkBounds(uiEd.getFurnaceParameters().getX(), true);
		checkBounds(uiEd.getFurnaceParameters().getY(), true);
		checkBounds(uiEd.getFurnaceParameters().getZ(), true);
		checkBounds(uiEd.getFurnaceParameters().getTemperature(), true);
		checkBounds(uiEd.getFurnaceParameters().getTolerance(),   true);
		checkBounds(uiEd.getFurnaceParameters().getTime(),        true);
	}
	
	/**
	 * 
	 * @throws Throwable
	 */ 
	@Test
	public final void testPIDShowsUp() throws Throwable {
		
		uiEd.getSampleEnvironment().setValue("Cryostat");
		
		// Check a few of the cyrostat parameters are active.
		final gda.exafs.ui.composites.CryostatComposite cryo = uiEd.getCryostatParameters();
		if (!cryo.getTolerance().isActivated()) throw new Exception("Crystat parameters selected but tolderance is not active.");
		if (!cryo.getTime().isActivated()) throw new Exception("Crystat parameters selected but time is not active.");
		
		cryo._testSetAdvancedActive();
		
		if (!cryo.getP().isActivated()) throw new Exception("P should be active in advanced mode!");
		if (!cryo._testIsPidTop()) throw new Exception("PID should be the visible top component.");
		
		cryo.getProfileType().setValue("Ramp");
		if (cryo._testIsPidTop()) throw new Exception("Ramp should be the visible top component.");
	}

	/**
	 * 
	 * @throws Throwable
	 */ 
	@Test
	public final void testCustomBeamList() throws Throwable {
		
		uiEd.getSampleEnvironment().setValue("Custom (XYZ)");
		
		final VerticalListEditor comp = uiEd.getCustomXYZParameters();
		comp.addBean(); // Add one from nothing.
		if (comp.getListSize()!=1) throw new Exception("Added custom XYZ parameter but did not show up!");
	}
	
//	/**
//	 * 
//	 * @throws Throwable
//	 */ 
//	@Test
//	public final void testReferenceName() throws Throwable {
////		uiEd.updateElementLabel();
//		if (!uiEd._testGetElementName().equals("Silicon")) throw new Exception("The element name is '"+uiEd._testGetElementName()+"' and should be 'Silicon'.");
//		
//		uiEd.getSampleWheelPosition().setValue(2);
//		if (!uiEd._testGetElementName().equals("Iron")) throw new Exception("The element name is '"+uiEd._testGetElementName()+"' and should be 'Iron'.");
//
//		uiEd.getSampleWheelPosition().setValue(5);
//		if (!uiEd._testGetElementName().equals("<No element>")) throw new Exception("The element name is '"+uiEd._testGetElementName()+"' and should be '<No element>'.");
//    }
	
	private void checkBounds(NumberBox x, boolean b) throws Exception {
		if (x.isValidBounds() != b) {
			throw new Exception(x.getFieldName()+" is has bounds valid = "+(!b));
		}
	}
}

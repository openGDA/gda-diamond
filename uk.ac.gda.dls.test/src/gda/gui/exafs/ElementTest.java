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

package gda.gui.exafs;

import gda.util.exafs.Element;

import org.junit.Test;

/**
 * Simply checks that various elements and edges are correct
 */
public class ElementTest {

	@Test
	public void testSymbols() throws Exception {
		checkAtomicNumber("Fe",26);
		checkAtomicNumber("Eu",63);
		checkAtomicNumber("U",92);
		checkAtomicSymbol("Fe");
		checkAtomicSymbol("Eu");
		checkAtomicSymbol("U");
		
		String[] result = Element.getSortedEdgeSymbols("Sc","U");
		if (result.length!=72) {
			throw new Exception("The element range should be of size "+72+" not "+Element.getSortedEdgeSymbols("Sc", "U").length);
		}
	}
	private void checkAtomicNumber(String element, int value) throws Exception {
		if (Element.getElement(element).getAtomicNumber()!=value) {
			throw new Exception(element+" edge should be atomic nummber "+value);
		}
	}
	
	private void checkAtomicSymbol(String element) throws Exception {
		if (!Element.getElement(element).getSymbol().equals(element)) { 
			throw new Exception(element+" edge should be named "+element);
		}
	}

	
	@Test
	public void testEdges() throws Exception {
		checkEdge("Fe","K", 7112d);
		checkEdge("Eu","L1",8052d);
		checkEdge("Eu","L2",7617d);
		checkEdge("Eu","L3",6977d);
	}
		
	private void checkEdge(String element, String edge, double value) throws Exception {
		if (Element.getElement(element).getEdgeEnergy(edge)!=value) throw new Exception(element+" "+edge+" edge should be "+value);
	}

	@Test
	public void testCoreHoles() throws Exception {
		checkCoreHole("Fe","K",1.25d);
		checkCoreHole("Eu","L1",4.91d);
		checkCoreHole("Eu","L2",4.23d);
		checkCoreHole("Eu","L3",3.91d);
	}
		
	private void checkCoreHole(String element, String edge, double value) throws Exception {
		if (Element.getElement(element).getCoreHole(edge)!=value) throw new Exception(element+" "+edge+" core hole should be "+value);
	}
	
}

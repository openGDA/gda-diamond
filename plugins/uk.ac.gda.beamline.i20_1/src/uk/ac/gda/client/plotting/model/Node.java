/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.client.plotting.model;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

import uk.ac.gda.beans.ObservableModel;

public class Node extends ObservableModel implements ITreeNode {

	private final Map<String, ITreeNode> nodeMap = new HashMap<>();
	private final IObservableList nodeList = new WritableList(new ArrayList<ITreeNode>(), ITreeNode.class);
	private final ITreeNode parent;
	private String identifier;

	public Node(ITreeNode parent) {
		this.parent = parent;
	}

	public Node(ITreeNode parent, String identifier) {
		this.parent = parent;
		this.identifier = identifier;
	}

	@Override
	public IObservableList getChildren() {
		return nodeList;
	}

	@Override
	public String getIdentifier() {
		return identifier;
	}

	public void setIdentifier(String identifier) {
		this.identifier = identifier;
	}

	@Override
	public ITreeNode getParent() {
		return parent;
	}

	@Override
	public String getLabel() {
		return toString();
	}

	public void removeChild(Node dataNode) {
		// No default implementation
	}

	public void disposeResources() {
		// Nothing to dispose
	}

	public boolean hasChild(String identifier) {
		return nodeMap.containsKey(identifier);
	}

	public ITreeNode getChild(String identifier) {
		return nodeMap.get(identifier);
	}

	public void addChildNode(ITreeNode node) {
		nodeList.add(node);
		nodeMap.put(node.getIdentifier(), node);
	}

	public void addChildNode(int index, ITreeNode node) {
		nodeList.add(index, node);
		nodeMap.put(node.getIdentifier(), node);
	}
}

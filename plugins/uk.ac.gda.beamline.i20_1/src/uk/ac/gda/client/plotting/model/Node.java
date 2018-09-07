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
import java.util.List;
import java.util.Map;

import org.apache.commons.lang.StringUtils;
import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

import uk.ac.gda.beans.ObservableModel;

public class Node extends ObservableModel implements ITreeNode {

	private final Map<String, ITreeNode> nodeMap = new HashMap<>();
	private final IObservableList<ITreeNode> nodeList = new WritableList<>(new ArrayList<>(), ITreeNode.class);
	private final ITreeNode parent;
	private String identifier;
	private String label = "";

	public void setLabel(String label) {
		this.label = label;
	}

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
		if (StringUtils.isEmpty(label)) {
			return toString();
		} else {
			return label;
		}
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

	/** Return top level root node of tree */
	public ITreeNode getRootNode() {
		ITreeNode nextNode = getParent();
		ITreeNode childNode = this;
		while(nextNode != null) {
			childNode = nextNode;
			nextNode = childNode.getParent();
		}
		return childNode;
	}

	/** Return the total number of 'end' nodes contained under this node.
    This is the number of nodes without any children (e.g. ScanDataItemNodes).
    @see #getTotalNumChildren(ITreeNode)
 * @return Number of nodes below 'startNode' that do not have any children
 */
	public int getTotalNumChildren() {
		return getTotalNumChildren(this);
	}

	/** Recursively count number of 'end' nodes contained under 'startNode'
	    This is the number of nodes without any children (e.g. ScanDataItemNodes).
	 * @param startNode
	 * @return Number of nodes below 'startNode' that do not have any children
	 */
	public static int getTotalNumChildren(ITreeNode startNode) {
		int numChildren = 0;
		for(ITreeNode node : startNode.getChildren()) {
			boolean hasChildNodes = node.getChildren() != null && !node.getChildren().isEmpty();
			if (hasChildNodes) {
				numChildren += getTotalNumChildren(node);
			} else {
				numChildren += 1;
			}
		}
		return numChildren;
	}

	/**
	 * Return list of all child nodes under 'startNode' that have class type 'clazz'.
	 * (Recursive navigation of tree).
	 * @param startNode
	 * @param clazz
	 * @return list of all child nodes under 'startNode' of specified class type.
	 */
	public static List<ITreeNode> getNodesOfType(ITreeNode startNode, Class<?> clazz) {
		List<ITreeNode> nodeList = new ArrayList<>();
		for(ITreeNode node : startNode.getChildren()) {
			if (node.getClass().equals(clazz)) {
				nodeList.add(node);
			}
			boolean hasChildNodes = node.getChildren() != null && !node.getChildren().isEmpty();
			if (hasChildNodes) {
				nodeList.addAll(getNodesOfType(node, clazz));
			}
		}
		return nodeList;
	}
}

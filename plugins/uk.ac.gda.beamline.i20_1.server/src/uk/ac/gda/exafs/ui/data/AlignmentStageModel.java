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

package uk.ac.gda.exafs.ui.data;

import com.google.gson.annotations.Expose;

import uk.ac.gda.beans.ObservableModel;

public class AlignmentStageModel extends ObservableModel {
	public static final AlignmentStageModel INSTANCE = new AlignmentStageModel();

	public static final String X_X_EYE_PROP_NAME = "xXeye";
	@Expose
	private double xXeye;
	public static final String Y_X_EYE_PROP_NAME = "yXeye";
	@Expose
	private double yXeye;

	public static final String X_SLITS_PROP_NAME = "xSlits";
	@Expose
	private double xSlits;
	public static final String Y_SLITS_PROP_NAME = "ySlits";
	@Expose
	private double ySlits;

	public static final String X_FOILS_PROP_NAME = "xFoils";
	@Expose
	private double xFoils;
	public static final String Y_FOILS_PROP_NAME = "yFoils";
	@Expose
	private double yFoils;

	public static final String X_HOLE_PROP_NAME = "xHole";
	@Expose
	private double xHole;
	public static final String Y_HOLE_PROP_NAME = "yHole";
	@Expose
	private double yHole;

	public static final String X_SHUTTER_PROP_NAME = "xShutter";
	@Expose
	private double xShutter;
	public static final String Y_SHUTTER_PROP_NAME = "yShutter";
	@Expose
	private double yShutter;

	// Hole2
	public static final String X_HOLE2_PROP_NAME = "xHole2";
	@Expose
	private double xHole2;
	public static final String Y_HOLE2_PROP_NAME = "yHole2";
	@Expose
	private double yHole2;

	// Laser
	public static final String X_LASER_PROP_NAME = "xLaser";
	@Expose
	private double xLaser;
	public static final String Y_LASER_PROP_NAME = "yLaser";
	@Expose
	private double yLaser;

	public double getxXeye() {
		return xXeye;
	}
	public void setxXeye(double xXeye) {
		this.xXeye = xXeye;
	}
	public double getyXeye() {
		return yXeye;
	}
	public void setyXeye(double yXeye) {
		this.yXeye = yXeye;
	}
	public double getxSlits() {
		return xSlits;
	}
	public void setxSlits(double xSlits) {
		this.xSlits = xSlits;
	}
	public double getySlits() {
		return ySlits;
	}
	public void setySlits(double ySlits) {
		this.ySlits = ySlits;
	}
	public double getxFoils() {
		return xFoils;
	}
	public void setxFoils(double xFoils) {
		this.xFoils = xFoils;
	}
	public double getyFoils() {
		return yFoils;
	}
	public void setyFoils(double yFoils) {
		this.yFoils = yFoils;
	}
	public double getxHole() {
		return xHole;
	}
	public void setxHole(double xHole) {
		this.xHole = xHole;
	}
	public double getyHole() {
		return yHole;
	}
	public void setyHole(double yHole) {
		this.yHole = yHole;
	}
	public double getxShutter() {
		return xShutter;
	}
	public void setxShutter(double xShutter) {
		this.xShutter = xShutter;
	}
	public double getyShutter() {
		return yShutter;
	}
	public void setyShutter(double yShutter) {
		this.yShutter = yShutter;
	}
	public double getxHole2() {
		return xHole2;
	}
	public void setxHole2(double xHole2) {
		this.xHole2 = xHole2;
	}
	public double getyHole2() {
		return yHole2;
	}
	public void setyHole2(double yHole2) {
		this.yHole2 = yHole2;
	}
	public double getxLaser() {
		return xLaser;
	}
	public void setxLaser(double xLaser) {
		this.xLaser = xLaser;
	}
	public double getyLaser() {
		return yLaser;
	}
	public void setyLaser(double yLaser) {
		this.yLaser = yLaser;
	}
}
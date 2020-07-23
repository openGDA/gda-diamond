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

package gda.util;

import java.io.FileDescriptor;
import java.lang.reflect.Field;
import java.net.Socket;
import java.net.SocketImpl;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;

/**
 * Provides a series of methods for accessing Unix functions. Mostly the starting and stopping of processes for Protein
 * Crystallography. However there are also a couple of general purpose methods e.g. for getting disk space information.
 * This class does rely upon a shared library being created and available for loading, used via JNI. The shared library
 * should be called JavaToUnix.so
 * <p>
 * A C file exists as the basis for this library and a series of corresponding makefiles. These exist in the GDA
 * directory heirarchy under gda.util.
 */

public class Unix {
	private static final Logger logger = LoggerFactory.getLogger(Unix.class);

	/**
	 *
	 */
	public static native void initFIDs();

	private static Runtime runtime = Runtime.getRuntime();

	private String xformStatusFile = null;

	private static boolean enabled = LocalProperties.check("gda.util.unix.enabled", true);

	static {
		try {
			String osName = (System.getProperty("os.name")).toLowerCase();

			if (osName.startsWith("windows") || !enabled) {
			} else {
				System.loadLibrary("JavaToUnix");
				initFIDs();
			}
		} catch (Throwable e) {
			logger.error("Error initialising Unix - check JavaToUnix.so library is correct", e);
		}
	}

	/**
	 * @return int
	 */
	public native int doRestartQ315();

	/**
	 * JNI implementation specific.
	 *
	 * @return Status code
	 */
	public native int doStartBLDaemon();

	/**
	 * JNI implementation specific.
	 *
	 * @param hostName
	 *            host name of daemon
	 * @param port
	 *            for daemon
	 * @return Status code
	 */
	public native int doStart345Daemon(String hostName, String port);

	/**
	 * JNI implementation specific.
	 *
	 * @return Status code
	 */
	public native int doEnd345Daemon();

	/**
	 * JNI implementation specific.
	 *
	 * @return Status code
	 */
	public native int doStartMarDaemon();

	/**
	 * JNI implementation specific.
	 *
	 * @return Status code
	 */
	public native int doEndMarDaemon();

	/**
	 * JNI implementation specific.
	 *
	 * @return Status code
	 */
	public native int doStartMarSimulator();

	/**
	 * JNI implementation specific.
	 *
	 * @return Status code
	 */
	public native int doEndMarSimulator();

	/**
	 * JNI implementation specific.
	 *
	 * @param port
	 *            for simulator
	 * @return Status code
	 */
	public native int doStart345Simulator(String port);

	/**
	 * JNI implementation specific.
	 *
	 * @return Status code
	 */
	public native int doStartQ4Xform();

	/**
	 * JNI implementation specific.
	 *
	 * @return Status code
	 */
	public native int doStopQ4Xform();

	/**
	 * JNI implementation specific.
	 *
	 * @return Status code
	 */
	public native int doStartPXGEN();

	/**
	 * JNI implementation specific.
	 *
	 * @return Status code
	 */
	public native int doStartAdxv();

	/**
	 * JNI implementation specific.
	 *
	 * @return Status code
	 */
	public native int doEndAdxv();

	/**
	 * JNI implementation specific.
	 *
	 * @param command
	 *            native string
	 * @return Status code
	 */
	public native int doSystem(String command);

	/**
	 * JNI implementation specific.
	 *
	 * @param path
	 *            to free memory blocks
	 * @return Status code
	 */
	public native long doGetFreeMB(String path);

	/**
	 * JNI implementation specific.
	 *
	 * @param path
	 *            to free disk blocks
	 * @return Status code
	 */
	public native int doGetDiskMB(String path);

	/**
	 * JNI implementation specific.
	 *
	 * @return Status code
	 */
	public native int doResetXformStatusFile();

	private static void start(String command) throws Exception {
		if (command != null) {
			runtime = Runtime.getRuntime();
			logger.debug("Starting " + command);
			runtime.exec(command);
		}
	}

	private static void stop(String commandIdentifier) {
		if (commandIdentifier != null) {
			String progarray[] = {
					"/bin/csh",
					"-c",
					"kill -TERM `ps -efl | grep \"" + commandIdentifier + "\" | " + "grep -v grep |  "
							+ "awk '{print $4}'`" };

			try {
				logger.debug("Stoping via identifier => " + commandIdentifier);
				(runtime.exec(progarray)).waitFor();
			} catch (Exception ex) {
				logger.debug(ex.getMessage());
			}
		}
	}

	/**
	 * Start the grip program for controlling the Rigaku MSC automatic sample changer. This can be used interactively or
	 * accepts commands as strings over a socket.
	 *
	 * @throws Exception
	 */
	public static void startGrip() throws Exception {
		start(LocalProperties.get("gda.px.gripCommand"));
		// runtime.addShutdownHook(new Thread(Unix::stopGrip));
	}

	/**
	 * Stop the grip program for controlling the Rigaku MSC automatic sample changer. This can be used interactively or
	 * accepts commands as strings over a socket.
	 */
	public static void stopGrip() {
		try {
			stop(LocalProperties.get("gda.px.gripStopString"));
		} catch (Exception ex) {
			logger.debug(ex.getMessage());
		}
	}

	/**
	 * Start the sub-process to control the Mar345 detector. This process runs as a daemon and reads commands from a
	 * file which is written by the Mar345Detector class.
	 */
	public static void start345Daemon() {
		try {
			start(LocalProperties.get("gda.px.scan345Command"));
			runtime.addShutdownHook(new Thread(Unix::stop345Daemon));
		} catch (Exception ex) {
			logger.debug(ex.getMessage());
		}
	}

	/**
	 * Stops the sub-process to control the Mar345 detector. This process runs as a daemon and reads commands from a
	 * file which is written by the Mar345Detector class.
	 */
	public static void stop345Daemon() {
		try {
			stop(LocalProperties.get("gda.px.scan345StopString"));
		} catch (Exception ex) {
			logger.debug(ex.getMessage());
		}
	}

	/**
	 * Starts a sub-process that simulates a Mar345 detector.
	 *
	 * @param port
	 *            Port that the simulated detector will listen on.
	 * @return Status code.
	 */
	public int start345Simulator(String port) {
		return (doStart345Simulator(port));
	}

	/**
	 * Starts an ADSC beamline control daemon. The specifc daemon started is determined in the C library via the Unix
	 * environment variable CCD_BLSERVER. These daemons communicate with clients, via sockets, using a standard text
	 * based protocol.
	 *
	 * @return Status code.
	 */
	public int startBLDaemon() {
		return (doStartBLDaemon());
	}

	/**
	 * Starts the MAR detector control daemon, mardc. This is the control daemon for MAR 180 and 300 image plates. It
	 * communicates with clients via text files.
	 *
	 * @return Status code.
	 */
	public int startMarDaemon() {
		return (doStartMarDaemon());
	}

	/**
	 * Stos the MAR detector control daemon, mardc. This is the control daemon for MAR 180 and 300 image plates. It
	 * communicates with clients via text files.
	 *
	 * @return Status code.
	 */
	public int endMarDaemon() {
		return (doEndMarDaemon());
	}

	/**
	 * Starts the MAR detector control daemon, mardc, in simulation mode. This is the control daemon for MAR 180 and 300
	 * image plates. Run is this way no actual detector is required. It communicates with clients via text files.
	 *
	 * @return Status code.
	 */
	public int startMarSimulator() {
		return (doStartMarSimulator());
	}

	/**
	 * Stops the MAR detector control daemon, mardc, running in simulation mode. This is the control daemon for MAR 180
	 * and 300 image plates. Run is this way no actual detector is required. It communicates with clients via text
	 * files.
	 *
	 * @return Status code.
	 */
	public int endMarSimulator() {
		return (doEndMarSimulator());
	}

	/**
	 * Starts the ADSC detector image transform daemon. This daemon converts scanned images into 2D cartesian
	 * co-ordinates.
	 *
	 * @return Status code.
	 */
	public int startQ4Xform() {
		return (doStartQ4Xform());
	}

	/**
	 * Stops the ADSC detector image transform process. This daemon converts scanned images into 2D cartesian
	 * co-ordinates.
	 *
	 * @return Status code.
	 */
	public int stopQ4Xform() {
		return (doStopQ4Xform());
	}

	/**
	 * Starts PXGEN++ based a specified by the environment variable PXGEN_COMMAND.
	 *
	 * @return Status code.
	 */
	public int startPXGEN() {
		return (doStartPXGEN());
	}

	/**
	 * Starts the ADSC image display program, adxv.
	 *
	 * @return Status code.
	 */
	public int startAdxv() {
		int status = -1;

		if (enabled)
			status = doStartAdxv();

		return status;
	}

	/**
	 * Stops the ADSC image display program, adxv.
	 *
	 * @return Status code.
	 */
	public int endAdxv() {
		int status = -1;

		if (enabled)
			status = doEndAdxv();

		return status;
	}

	/**
	 * Executes a requested Unix command.
	 *
	 * @param command
	 *            Required command.
	 * @return Status code.
	 */
	public int system(String command) {
		return (doSystem(command));
	}

	/**
	 * Gets the free disk space.
	 *
	 * @param path
	 *            Directory path of a file on the required disk.
	 * @return Free space on the disk in MBytes.
	 */
	public long getFreeMB(String path) {
		return (doGetFreeMB(path));
	}

	/**
	 * Gets the total capacity of a disk..
	 *
	 * @param path
	 *            Directory path of a file on the required disk.
	 * @return Capacity of the disk in MBytes.
	 */
	public int getDiskMB(String path) {
		return (doGetDiskMB(path));
	}

	/**
	 * Resets the Unix environment variable XFORMSTATUSFILE.
	 *
	 * @return Status code.
	 */
	public int resetXformStatusFile() {
		return (doResetXformStatusFile());
	}

	/**
	 * Gets the Unix environment variable XFORMSTATUSFILE.
	 *
	 * @return The environment variable.
	 */
	public String getXformStatusFileName() {
		return (xformStatusFile);
	}

	/**
	 * Returns the TCP state of the specified socket. Will only work on Linux,
	 * and uses reflection to access private fields - so won't work if a
	 * {@link SecurityManager} is in use and prevents access.
	 */
	public TcpSocketState getSocketState(Socket socket) {
		try {
			// Get the SocketImpl from the Socket
			final Field socketImplField = Socket.class.getDeclaredField("impl");
			socketImplField.setAccessible(true);
			final SocketImpl sockImpl = (SocketImpl) socketImplField.get(socket);

			// Get the FileDescriptor from the SocketImpl
			final Field fileDescObjectField = SocketImpl.class.getDeclaredField("fd");
			fileDescObjectField.setAccessible(true);
			final FileDescriptor fileDescObj = (FileDescriptor) fileDescObjectField.get(sockImpl);

			// Get the file descriptor number from the FileDescriptor object
			final Field fileDescNumberField = FileDescriptor.class.getDeclaredField("fd");
			fileDescNumberField.setAccessible(true);
			final int fd = (Integer) fileDescNumberField.get(fileDescObj);

			return getSocketState(fd);
		} catch (Exception e) {
			throw new RuntimeException("Unable to get socket state", e);
		}
	}

	private TcpSocketState getSocketState(int fd) {
		GetSocketStateReturn ret = new GetSocketStateReturn();
		int result = doGetSocketState(fd, ret);
		if (result != 0) {
			throw new RuntimeException(String.format("Call to doGetSocketState failed (error %d)", result));
		} else if (ret.errno == 0) {
			return TcpSocketState.fromValue(ret.state);
		} else {
			throw new RuntimeException(String.format("Could not get socket state: %s (error %d)", ret.errmsg, ret.errno));
		}
	}

	static class GetSocketStateReturn {
		int state;
		int errno;
		String errmsg;

		@Override
		public String toString() {
			return String.format("GetSocketStateReturn(state=%d, errno=%d, errmsg=%s)", state, errno, errmsg);
		}
	}

	public native int doGetSocketState(int fd, GetSocketStateReturn ret);
}

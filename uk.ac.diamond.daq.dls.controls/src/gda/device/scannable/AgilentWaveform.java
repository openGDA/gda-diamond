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

package gda.device.scannable;

import gda.device.DeviceException;
import gda.factory.Configurable;
import gda.factory.FactoryException;
import gda.factory.Findable;
import gda.util.BusyFlag;

import java.io.IOException;
import java.net.ConnectException;
import java.net.InetSocketAddress;
import java.net.SocketTimeoutException;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;
import java.nio.CharBuffer;
import java.nio.channels.SocketChannel;
import java.nio.channels.UnresolvedAddressException;
import java.nio.charset.Charset;
import java.nio.charset.CharsetDecoder;
import java.nio.charset.CharsetEncoder;
import java.util.ArrayList;
import java.util.List;
import java.util.Vector;

import org.python.core.PyList;
import org.python.core.PyNone;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Provides Ethernet communications an AgilentWaveform Generator
 * 
 * Has been developed against a 33210A not using all of its capabilities,
 * so changes are it will work with related devices as well.
 */
public class AgilentWaveform extends ScannableBase implements Configurable, Findable {

	private static final Logger logger = LoggerFactory.getLogger(AgilentWaveform.class);

	private String host = "localhost";

	private int commandPort = 5025;

	private int socketTimeOut = 100;

	private boolean connected = false;
	
	private ArrayList<String> startupCommands = new ArrayList<String>();

	private SocketChannel socketChannel;
	
    private static Charset charset = Charset.forName("US-ASCII");                                                   
    private static CharsetEncoder encoder = charset.newEncoder();  
    private static CharsetDecoder decoder = charset.newDecoder();

	private ByteBuffer bb = ByteBuffer.allocate(4096);

	private BusyFlag busyFlag = new BusyFlag();

	private static final List<String> waveforms = new Vector<String>();
	
	static {
	waveforms.add("SIN");
	waveforms.add("SQU");
	waveforms.add("RAMP");
	waveforms.add("PULS");
	waveforms.add("NOIS");
	waveforms.add("DC");
	waveforms.add("USER");
	}

	/**
	 * default constructor
	 */
	public AgilentWaveform() {
		this("aglient", "aglient");
	}

	/**
	 * Convenient constructor for scripts
	 * 
	 * @param name device name
	 * @param host device IP address or hostname
	 */
	public AgilentWaveform(String name, String host) {
		inputNames = new String[] { "function", "frequencyHz", "amplitudeVPP", "offsetV"};
		setName(name);
		setHost(host);
	}
	
	@Override
	public void configure() throws FactoryException {
		if (isConfigured()) {
			return;
		}
		connect();
		setConfigured(true);
	}

	/**
	 * Set up initial connections to socket 
	 */
	public void connect() {
		if (isConnected()) return;
		lock();
		try {
			InetSocketAddress inetAddr = new InetSocketAddress(host, commandPort);
			socketChannel = SocketChannel.open();
			socketChannel.connect(inetAddr);

			socketChannel.socket().setSoTimeout(socketTimeOut);
			socketChannel.configureBlocking(true);
			socketChannel.finishConnect();
			
			connected = true;

			cleanPipe();
			
			doStartupScript();
		} catch (UnknownHostException ex) {
			// this could be fatal as reconnect attempts are futile.
			logger.error(getName() + ": connect: " + ex.getMessage());
		} catch (UnresolvedAddressException ex) {
			logger.error(getName() + ": connect: " + ex.getMessage());
		} catch (ConnectException ex) {
			logger.debug(getName() + ": connect: " + ex.getMessage());
		} catch (IOException ix) {
			logger.error(getName() + ": connect: " + ix.getMessage());
		} finally {
			unlock();
		}
	}

	@Override
	public void reconfigure() throws FactoryException {
		reconnect();
	}

	/**
	 * Tidy existing socket streams and try to connect them again within the thread. This method is synchronized as both
	 * the main thread and run thread use this method.
	 */
	public synchronized void reconnect() {
		try {
			close();
		} catch (DeviceException e) {
			// do nothing for now
		}
		connect();
	}

	@Override
	public void close() throws DeviceException {
		connected = false;
		if (socketChannel != null) {
			try {
				socketChannel.close();
				socketChannel = null;
			} catch (IOException ex) {
				logger.error(getName() + ": disconnect: " + ex.getMessage());
				throw new DeviceException(ex.getMessage());
			}
		}
	}

	/**
	 * Returns the state of the socket connection
	 * 
	 * @return true if connected
	 */
	public boolean isConnected() {
		return connected;
	}


	/**
	 * Send command to the server.
	 * 
	 * @param msg
	 *            an unterminated command
	 * @return the reply string.
	 * @throws DeviceException
	 */
	public String processCommand(String msg) throws DeviceException {
		if (!isConnected()) {
			throw new DeviceException("not connected");
		}
		String command = msg + "\n";
		String reply = null;
		lock();
		try {
			cleanPipe();
			logger.debug(getName() + ": sent command: " + msg);
			socketChannel.write(encoder.encode(CharBuffer.wrap(command)));
			socketChannel.socket().setSoTimeout(socketTimeOut);
			socketChannel.configureBlocking(true);
			socketChannel.read(bb);
			bb.flip();
			reply = decoder.decode(bb).toString();
			
		} catch (SocketTimeoutException ex) {
			// we do not get a reply for every action
			logger.info(getName() + ": sendCommand: read timeout " + ex.getMessage());
//			throw new DeviceException("sendCommand read timeout " + ex.getMessage());
		} catch (IOException ex) {
			// treat as fatal
			connected = false;
			logger.error(getName() + ": sendCommand: " + ex.getMessage());
			throw new DeviceException("sendCommand: " + ex.getMessage());
		} finally {
			bb.clear();
			unlock();
		}
		return reply;
	}

	/**
	 * Send command to the server, not hoping for reply.
	 * 
	 * @param msg
	 *            an unterminated command
	 * @throws DeviceException
	 */
	public void sendCommand(String msg) throws DeviceException {
		if (!isConnected()) {
			throw new DeviceException("not connected");
		}
		String command = msg + "\n";
		lock();
		try {
			logger.debug(getName() + ": sent command: " + msg);
			socketChannel.write(encoder.encode(CharBuffer.wrap(command)));
			cleanPipe();
		} catch (SocketTimeoutException ex) {
			// we do not get a reply for every action
			logger.info(getName() + ": sendCommand: read timeout " + ex.getMessage());
//			throw new DeviceException("sendCommand read timeout " + ex.getMessage());
		} catch (IOException ex) {
			// treat as fatal
			connected = false;
			logger.error(getName() + ": sendCommand: " + ex.getMessage());
			throw new DeviceException("sendCommand: " + ex.getMessage());
		} finally {
			unlock();
		}
	}

	private void doStartupScript() {
		if (isConnected()) {
			for (String command : startupCommands) {
				try {
					String reply = processCommand(command);
					if (reply.startsWith("ER")) {
						throw new DeviceException("received error reply from device: " + reply);
					}
				} catch (DeviceException e) {
					logger.error("error sending command " + command + " :"+e.getMessage());
				}
			}
		}
	}

	private void lock() {
		busyFlag.getBusyFlag();
	}

	private void unlock() {
		busyFlag.freeBusyFlag();
	}

	/**
	 * Set the device host
	 * 
	 * @param host
	 */
	public void setHost(String host) {
		this.host = host;
	}

	/**
	 * @return the device host name
	 */
	public String getHost() {
		return host;
	}

	/**
	 * Set the command port
	 * 
	 * @param port
	 */
	public void setPort(int port) {
		this.commandPort = port;
	}

	/**
	 * @return the command port
	 */
	public int getPort() {
		return commandPort;
	}

	/**
	 * @param startupCommands
	 */
	public void setStartupCommands(ArrayList<String> startupCommands) {
		this.startupCommands = startupCommands;
	}

	/**
	 * @return an array list of startup commands to be processed by da.server on startup
	 */
	public ArrayList<String> getStartupCommands() {
		return startupCommands;
	}

	@Override
	public Object[] getPosition() throws DeviceException {

		String reply = processCommand("APPly?").trim();
		// remove quotes
		reply = reply.substring(1,reply.length()-2);
		String[] funcAndNumbers = reply.split(" ", 2);
		String form = funcAndNumbers[0];
		String[] posStrings = funcAndNumbers[1].split(",");
		int positionsRead = posStrings.length;
		if (3 != positionsRead) throw new DeviceException("unexpected number of measurements");
		
		Object[] positions = new Object[inputNames.length];
		positions[0] = form;
		for (int i = 0; i < posStrings.length; i++) {
			positions[i+1] = Double.parseDouble(posStrings[i]);
		}
		return positions;
	}

	@Override
	public void asynchronousMoveTo(Object position) throws DeviceException {
		
		
		if (position == null || position instanceof PyNone) {
			sendCommand("OUTPut OFF");
			return;
		}
		
		Object[] newposition;
		if (position instanceof PyList) {
			newposition = ((PyList) position).toArray();
		} else {
			newposition = (Object[]) position;
		}
		
		if (newposition.length < 2) {
			throw new DeviceException("Need at least function and frequency");
		}
		
		StringBuilder command = new StringBuilder("APPly:");
		short argno=0;
		for (Object pos: newposition) {
			switch (argno) {
			case 0:
				// form
				if (waveforms.contains(pos.toString())) {
					command.append(pos.toString());
				} else {
					throw new DeviceException("Unknown waveform: "+pos.toString());
				}
				break;
			case 2:
			case 3:
				command.append(",");
				//$FALL-THROUGH$
			case 1:
				command.append(" ");
				if ("DEF".equals(pos.toString())) {
					command.append("DEF");
				} else if (pos instanceof Number) {
					command.append(String.format("%10.3f",	((Number) pos).doubleValue()));
				} else {
					throw new DeviceException("Unknown parameter: "+pos.toString());
				}
				break;
			default:
				throw new DeviceException("more parameters than needed.");
			}
			argno++;
		}
		sendCommand(command.toString());
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	@Override
	public void setInputNames(String[] names) {
	}

	private void cleanPipe() {
		if (isConnected()) {
			lock();
			try {
				socketChannel.configureBlocking(false);
				while (socketChannel.read(bb) > 0) {
					bb.clear();
				}
				socketChannel.configureBlocking(true);
			} catch (IOException ex) {
				logger.error(getName() + ": cleanPipe: " + ex.getMessage());
				try {
					close();
				} catch (DeviceException e) {
					// we know that already
				}
			} catch (Exception ex) {
				logger.warn(getName() + ": cleanPipe: " + ex.getMessage());
			} finally {
				bb.clear();
				unlock();
			}
		}
	}
}

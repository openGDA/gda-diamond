/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

/**
 * Enumerated type for the state field.
 * 
 * @see <a href="http://git.kernel.org/?p=linux/kernel/git/torvalds/linux-2.6.git;a=blob;f=include/linux/tcp.h;hb=HEAD"><code>struct tcp_info</code> in <code>include/linux/tcp.h</code></a>
 * @see <a href="http://git.kernel.org/?p=linux/kernel/git/torvalds/linux-2.6.git;a=blob;f=include/net/tcp_states.h;hb=HEAD">state <code>enum</code> in <code>include/net/tcp_states.h</code></a>
 */
public enum TcpSocketState {
	ESTABLISHED(1),
	SYN_SENT(2),
	SYN_RECV(3),
	FIN_WAIT1(4),
	FIN_WAIT2(5),
	TIME_WAIT(6),
	CLOSE(7),
	CLOSE_WAIT(8),
	LAST_ACK(9),
	LISTEN(10),
	CLOSING(11);
	
	private int value;
	
	TcpSocketState(int value) {
		this.value = value;
	}
	
	public int getValue() {
		return value;
	}
	
	public static TcpSocketState fromValue(int value) {
		for (TcpSocketState e : values()) {
			if (e.value == value) {
				return e;
			}
		}
		throw new IllegalArgumentException("Unknown state: " + value);
	}
}

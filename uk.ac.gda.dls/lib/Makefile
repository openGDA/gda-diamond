# To rebuild the libraries run:
#   make JDK_PATH=/path/to/jdk all

JAVA_INCLUDE=$(JDK_PATH)/include

linux-x86/libJavaToUnix.so: ../JavaToUnix/Unix.h ../JavaToUnix/Unix.c
	@# the extra LFS options can be found by running `getconf LFS_CFLAGS` on a 32-bit machine
	cc -m32 -fPIC -c -DLINUX -D_REENTRANT -O -I$(JAVA_INCLUDE) -I$(JAVA_INCLUDE)/linux ../JavaToUnix/Unix.c -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64
	cc -m32 -shared -o $@ Unix.o /usr/lib/libc.so

linux-x86_64/libJavaToUnix.so: ../JavaToUnix/Unix.h ../JavaToUnix/Unix.c
	cc -m64 -fPIC -c -DLINUX -D_REENTRANT -O -I$(JAVA_INCLUDE) -I$(JAVA_INCLUDE)/linux ../JavaToUnix/Unix.c
	cc -m64 -shared -o $@ Unix.o /usr/lib64/libc.so

all: linux-x86/libJavaToUnix.so linux-x86_64/libJavaToUnix.so

clean:
	rm -f linux-{x86,x86_64}/libJavaToUnix.so

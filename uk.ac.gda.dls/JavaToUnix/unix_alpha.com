cc -c -DALPHA  -D_REENTRANT -O -pthread -I/usr/include/java -I/usr/include/java/alpha Unix.c -o Unix.o
cc -shared -pthread -o lib/alpha/JavaToUnix.so Unix.o  /usr/shlib/libc.so


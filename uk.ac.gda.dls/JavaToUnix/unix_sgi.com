cc -c -DIRIX -O -I/usr/java/include -I/usr/java/include/irix Unix.c
cc -shared -o lib/sgi/JavaToUnix.so Unix.o /usr/lib32/libc.so

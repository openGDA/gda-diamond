cc -c -DSUN -I/usr/java/include -I/usr/java/include/solaris Unix.c -o Unix.o
cc -G -o lib/sun/JavaToUnix.so Unix.o /usr/lib/libc.so

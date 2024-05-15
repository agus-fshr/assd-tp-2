CC=gcc
CFLAGS=-I.
LIBS=-lm
N=4096

main: main.c
	$(CC) -D N=$(N) -o main main.c $(CFLAGS) $(LIBS)

clean:
	rm -f main
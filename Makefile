CHARMC=/opt/sharcnet/charm++/6.2.1/bin/charmc $(OPTS)
CHARMHOME=/opt/sharcnet/charm++/6.2.1/
INCLUDES = -I$(CHARMHOME)/include
LIBS = -L$(CHARMHOME)/lib
OBJS = main.o

default: all
all: wp

wp: $(OBJS)
	$(CHARMC) -language charm++ -o wp $(OBJS) -O2

main.o: main.C main.h main.decl.h main.def.h
	$(CHARMC) -o main.o main.C -O2

main.decl.h main.h: main.ci
	$(CHARMC) main.ci

clean:
	rm -f *.decl.h *.def.h conv-host *.o wp charmrun charmrun.exe wp.exe wp.pdb wp.ilk


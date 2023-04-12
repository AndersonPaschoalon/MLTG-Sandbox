CC = g++
CFLAGS = -c -Wall -std=gnu++17  -fdiagnostics-color=always  # -Wdeprecated-declarations
LDFLAGS = -lsqlite3 -lpcap -pthread
# EXTERNAL_INCLUDES = -Iexternal_library/headers
# EXTERNAL_LDFLAGS = -Lexternal_library/bin -lmylibrary

SRCDIR = src
INCDIR = headers
OBJDIR = obj
BINDIR = bin

SOURCES = $(wildcard $(SRCDIR)/*.cpp)
OBJECTS = $(patsubst $(SRCDIR)/%.cpp,$(OBJDIR)/%.o,$(SOURCES))
EXECUTABLE = $(BINDIR)/demo-sniffer.exe
DATABASE = $(BINDIR)/*.db

all: $(EXECUTABLE)

# build the executable
$(EXECUTABLE): prebuild $(OBJECTS) 
	$(CC) $(OBJECTS) -o  $@ $(LDFLAGS) 

# build the objects
$(OBJDIR)/%.o: $(SRCDIR)/%.cpp
	$(CC) $(CFLAGS) -I$(INCDIR) $< -o $@

# any command to run before the build
prebuild:
	mkdir -p $(BINDIR)
	mkdir -p $(OBJDIR)
	rm -f $(DATABASE)
	
# clean last build
clean:
	rm -f $(OBJDIR)/*.o $(EXECUTABLE) $(OBJDIR)/*.h

# clean and build
rebuild:
	make clean
	make all


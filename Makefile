CC      = gcc
CFLAGS  = -Wall -Wextra -g -std=c99 -pthread -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE
LDFLAGS = -pthread -lrt
SRN1   ?= PES2UG25CS617
SRN2   ?= PES2UG25CS609
ZIP    ?= $(if $(SRN),$(SRN).zip,$(SRN1)_$(SRN2).zip)

TARGET  = campuscompute
SRCS    = main.c input.c scheduler.c logger.c ipc.c banker.c worker.c rlimit.c
OBJS    = $(SRCS:.c=.o)
HEADERS = common.h scheduler.h logger.h ipc.h banker.h worker.h rlimit.h

.PHONY: all run demo test clean zip deliverables help

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

run: $(TARGET)
	./$(TARGET)

demo: $(TARGET)
	./$(TARGET) --demo

test: $(TARGET)
	python3 tests/test_campuscompute.py

clean:
	rm -f $(OBJS) $(TARGET) campuscompute.log

zip: clean
	rm -f $(ZIP)
	zip -r $(ZIP) samples tests $(SRCS) $(HEADERS) Makefile
	@echo "Verifying archive integrity:"
	unzip -t $(ZIP)

deliverables: $(TARGET)
	python3 scripts/build_deliverables.py

help:
	@echo "make          build ./$(TARGET)"
	@echo "make run      start the interactive menu"
	@echo "make demo     run the integrated demonstration"
	@echo "make zip      package source and documentation into \$$SRN.zip"
	@echo "make test     run independent regression tests (Python 3)"
	@echo "make deliverables generate S01-S24 screenshots, submission PDF & ZIPs"
	@echo "make clean    remove objects, binary, and log; preserve ZIPs"
	@echo "IPC objects are removed by the program itself (./$(TARGET) --cleanup)"

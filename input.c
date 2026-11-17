#include "common.h"
#include <ctype.h>

bool parse_int(const char *text, int lo, int hi, int *out) {
  char *end;
  errno = 0;
  long v = strtol(text, &end, 10);
  if (end == text || errno == ERANGE || v < lo || v > hi)
    return false;
  while (isspace((unsigned char)*end))
    end++;
  if (*end != '\0')
    return false;
  *out = (int)v;
  return true;
}

bool read_int(const char *prompt, int lo, int hi, int *out) {
  char buf[64];
  while (1) {
    printf("%s", prompt);
    fflush(stdout);
    if (!fgets(buf, sizeof(buf), stdin))
      return false;
    bool complete = strchr(buf, '\n') != NULL || feof(stdin);
    if (!complete) {
      int c;
      while ((c = getchar()) != '\n' && c != EOF) {}
    }
    if (complete && parse_int(buf, lo, hi, out))
      return true;
    printf("  Invalid input: enter an integer from %d to %d.\n", lo, hi);
  }
}

#ifndef LOGGER_H
#define LOGGER_H

int  logger_init(void);
void logger_log(const char *message);
int  logger_shutdown(void);     /* returns number of events written to the log */
int  logger_demo(void);         /* returns 0 on success */

#endif

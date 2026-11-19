#ifndef LOGGER_H
#define LOGGER_H

int logger_init(void);
void logger_log(const char *message);
int logger_shutdown(void);
int logger_demo(void);
int logger_custom_run(void);
int logger_submit_event(void);

#endif

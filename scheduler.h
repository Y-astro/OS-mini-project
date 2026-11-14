#ifndef SCHEDULER_H
#define SCHEDULER_H

#include "common.h"

void scheduler_load_default_jobs(Job jobs[], int *n);
int  scheduler_input_jobs(Job jobs[], int *n);
void scheduler_display_jobs(const Job jobs[], int n);

/* Each returns 0 on success, 1 if there are no jobs to schedule. */
int scheduler_run_fcfs(Job jobs[], int n);
int scheduler_run_rr(Job jobs[], int n);
int scheduler_run_priority(Job jobs[], int n);
int scheduler_compare_all(const Job jobs[], int n);

#endif

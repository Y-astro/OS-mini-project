#ifndef IPC_H
#define IPC_H

int  ipc_demo(void);                /* returns 0 on success */
void ipc_cleanup(void);             /* removes only this program's shm and semaphores */
int  ipc_objects_remaining(void);   /* how many of those objects still exist */

#endif

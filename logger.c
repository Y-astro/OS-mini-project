#include "common.h"
#include "logger.h"
#include <pthread.h>
#include <time.h>

typedef struct {
    char text[LOG_MSG_LEN];
    char time[20];
    bool stop;
} LogEvent;

static LogEvent queue[LOG_QUEUE_SIZE];
static int head, tail, count;
static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t not_full = PTHREAD_COND_INITIALIZER;
static pthread_cond_t not_empty = PTHREAD_COND_INITIALIZER;

static pthread_t consumer;
static FILE *log_file;
static bool active;
static int written;

/* Producer pushes an event into the bounded buffer */
static void push(const LogEvent *ev) {
    /* Step 1: Acquire mutex lock before touching shared queue */
    pthread_mutex_lock(&lock);

    /* Step 2: If queue is full, wait on not_full (releases mutex while sleeping) */
    while (count == LOG_QUEUE_SIZE) {
        printf("  [Producer] queue full (%d/%d), waiting for consumer\n", count, LOG_QUEUE_SIZE);
        pthread_cond_wait(&not_full, &lock);
    }

    /* Step 3: Insert item into circular buffer and increment count */
    queue[tail] = *ev;
    tail = (tail + 1) % LOG_QUEUE_SIZE;
    count++;

    /* Step 4: Signal consumer that queue is not empty */
    pthread_cond_signal(&not_empty);

    /* Step 5: Release mutex lock */
    pthread_mutex_unlock(&lock);
}

/* Consumer pops an event from the bounded buffer */
static LogEvent pop(void) {
    /* Step 1: Acquire mutex lock */
    pthread_mutex_lock(&lock);

    /* Step 2: If queue is empty, wait on not_empty */
    while (count == 0) pthread_cond_wait(&not_empty, &lock);

    /* Step 3: Remove item from circular buffer and decrement count */
    LogEvent ev = queue[head];
    head = (head + 1) % LOG_QUEUE_SIZE;
    count--;

    /* Step 4: Signal waiting producers that space is now available */
    pthread_cond_signal(&not_full);

    /* Step 5: Release mutex lock */
    pthread_mutex_unlock(&lock);
    return ev;
}

static void *consume(void *arg) {
    (void)arg;
    while (1) {
        LogEvent ev = pop();
        if (ev.stop) break;
        printf("  [Consumer] [%s] %s\n", ev.time, ev.text);
        fprintf(log_file, "[%s] %s\n", ev.time, ev.text);
        fflush(log_file);
        written++;
        usleep(20000);      /* slow consumer, so the bounded queue can fill up */
    }
    return NULL;
}

int logger_init(void) {
    if (active) return 0;
    log_file = fopen(LOG_FILE_NAME, "w");
    if (!log_file) {
        perror("fopen log file");
        return -1;
    }
    head = tail = count = written = 0;
    int err = pthread_create(&consumer, NULL, consume, NULL);
    if (err != 0) {
        fprintf(stderr, "pthread_create: %s\n", strerror(err));
        fclose(log_file);
        return -1;
    }
    active = true;
    return 0;
}

void logger_log(const char *message) {
    LogEvent ev = { .stop = false };
    time_t now = time(NULL);
    struct tm tm_now;

    if (!active) return;
    localtime_r(&now, &tm_now);
    strftime(ev.time, sizeof(ev.time), "%Y-%m-%d %H:%M:%S", &tm_now);
    snprintf(ev.text, sizeof(ev.text), "%s", message);
    push(&ev);
}

int logger_shutdown(void) {
    if (!active) return written;
    LogEvent stop = { .stop = true };
    push(&stop);
    pthread_join(consumer, NULL);
    fclose(log_file);
    log_file = NULL;
    active = false;
    return written;
}

#define PRODUCERS            3
#define EVENTS_PER_PRODUCER  5

static void *produce(void *arg) {
    int id = *(int *)arg;
    char msg[LOG_MSG_LEN];
    for (int i = 1; i <= EVENTS_PER_PRODUCER; i++) {
        snprintf(msg, sizeof(msg), "Producer-%d: job event #%d", id, i);
        logger_log(msg);
    }
    return NULL;
}

int logger_demo(void) {
    pthread_t threads[PRODUCERS];
    int ids[PRODUCERS];
    int started = 0;

    printf("\n=== Producer-consumer logger (queue size %d, mutex + condition variables) ===\n", LOG_QUEUE_SIZE);
    if (logger_init() != 0) return 1;

    logger_log("Logger started");
    for (int i = 0; i < PRODUCERS; i++) {
        ids[i] = i + 1;
        if (pthread_create(&threads[i], NULL, produce, &ids[i]) != 0) break;
        started++;
    }
    for (int i = 0; i < started; i++) pthread_join(threads[i], NULL);
    logger_log("All producers finished");

    int expected = 2 + started * EVENTS_PER_PRODUCER;
    int written_events = logger_shutdown();
    printf("Producers joined, consumer joined. Events produced: %d, written to %s: %d\n",
           expected, LOG_FILE_NAME, written_events);
    return (started == PRODUCERS && written_events == expected) ? 0 : 1;
}

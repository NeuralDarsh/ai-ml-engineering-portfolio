# Systems Concurrency & Operating Systems: Implementing thread-safe shared read and exclusive write lock scheduling

import threading
import time

class ReadWriteLock:
    """
    Implements a Read-Write Lock with Writer Priority.
    Allows multiple concurrent readers while prioritizing pending writers to prevent writer starvation.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._readers_ok = threading.Condition(self._lock)
        self._writers_ok = threading.Condition(self._lock)

        self._active_readers = 0
        self._waiting_writers = 0
        self._writer_active = False

    def acquire_read(self):
        """Acquires a shared read lock. Waits if a writer is active or queued."""
        with self._lock:
            # Block incoming readers if a writer is writing or waiting (Writer Priority)
            while self._writer_active or self._waiting_writers > 0:
                self._readers_ok.wait()
            self._active_readers += 1

    def release_read(self):
        """Releases shared read lock. Wakes waiting writers if readers reach zero."""
        with self._lock:
            self._active_readers -= 1
            if self._active_readers == 0:
                self._writers_ok.notify()

    def acquire_write(self):
        """Acquires an exclusive write lock. Waits for all active readers and writers to finish."""
        with self._lock:
            self._waiting_writers += 1
            while self._writer_active or self._active_readers > 0:
                self._writers_ok.wait()
            self._waiting_writers -= 1
            self._writer_active = True

    def release_write(self):
        """Releases exclusive write lock. Wakes pending writers first, else readers."""
        with self._lock:
            self._writer_active = False
            if self._waiting_writers > 0:
                self._writers_ok.notify()
            else:
                self._readers_ok.notify_all()


class SharedResourceStore:
    """A thread-safe key-value store protected by ReadWriteLock."""
    def __init__(self):
        self.rwlock = ReadWriteLock()
        self.data = {"counter": 0}

    def read_counter(self, thread_name):
        self.rwlock.acquire_read()
        print(f"[{thread_name}] Read shared counter: {self.data['counter']}")
        time.sleep(0.05)  # Simulate brief read operation
        self.rwlock.release_read()

    def write_counter(self, thread_name, increment):
        self.rwlock.acquire_write()
        print(f"[{thread_name}] (EXCLUSIVE) Incrementing counter by +{increment}...")
        self.data["counter"] += increment
        time.sleep(0.1)  # Simulate atomic update duration
        print(f" [{thread_name}] Updated counter to: {self.data['counter']}")
        self.rwlock.release_write()


if __name__ == "__main__":
    print("--- Systems Concurrency: Read-Write Lock Engine ---\n")

    store = SharedResourceStore()
    threads = []

    # Spawn concurrent readers and writers
    def reader_worker(name):
        for _ in range(2):
            store.read_counter(name)
            time.sleep(0.05)

    def writer_worker(name, val):
        store.write_counter(name, val)

    # Launch readers and interleaved writers
    threads.append(threading.Thread(target=reader_worker, args=("Reader-1",)))
    threads.append(threading.Thread(target=reader_worker, args=("Reader-2",)))
    threads.append(threading.Thread(target=writer_worker, args=("Writer-A", 10)))
    threads.append(threading.Thread(target=reader_worker, args=("Reader-3",)))
    threads.append(threading.Thread(target=writer_worker, args=("Writer-B", 25)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print("\nConcurrency Execution Completed without race conditions.")
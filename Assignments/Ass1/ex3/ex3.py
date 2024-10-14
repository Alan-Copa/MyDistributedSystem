import threading
import random
import time

def thread_task(id):
    print(f"Hi, I'm thread {id}")
    
    sleep_time = random.randint(1, 10)
    time.sleep(sleep_time)
    
    print(f"Thread {id} slept for {sleep_time} seconds, now he wakes up.")

def main():
    threads = []
    
    for i in range(1, 4):
        thread = threading.Thread(target=thread_task, args=(i,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

    print("All threads have completed.")

if __name__ == "__main__":
    main()
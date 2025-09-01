from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import threading
import time
import asyncio
import random
from enum import Enum

app = FastAPI(title="Thread-Based Parallelism", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# نگاشت نام بخش‌های thread
THREAD_SECTION_NAMES = {
    1: "Defining a thread",
    2: "Determining the current thread",
    3: "Thread subclass",
    4: "Synchronization with Lock",
    5: "Synchronization with RLock",
    6: "Synchronization with Semaphores",
    7: "Synchronization with Barrier"
}

THREAD_SECTION_REVERSE = {v: k for k, v in THREAD_SECTION_NAMES.items()}


# مدل‌های درخواست و پاسخ
class SectionType(str, Enum):
    THREAD = "thread"


class ScenarioRequest(BaseModel):
    section_type: SectionType
    section_name: str
    scenario_number: int
    parameters: Optional[Dict[str, Any]] = None


class ScenarioResponse(BaseModel):
    section_type: str
    section_name: str
    section_number: int
    scenario_number: int
    output: List[str]
    explanation: str


@app.get("/")
async def root():
    return {"message": "Thread API is running", "sections": THREAD_SECTION_NAMES}


@app.post("/api/run-scenario", response_model=ScenarioResponse)
async def run_scenario(request: ScenarioRequest):
    try:
        if request.section_name not in THREAD_SECTION_REVERSE:
            raise HTTPException(status_code=400, detail="بخش thread یافت نشد")

        section_number = THREAD_SECTION_REVERSE[request.section_name]

        if section_number == 1:
            result = await run_thread_section1(request.scenario_number, request.parameters)
        elif section_number == 2:
            result = await run_thread_section2(request.scenario_number, request.parameters)
        elif section_number == 3:
            result = await run_thread_section3(request.scenario_number, request.parameters)
        elif section_number == 4:
            result = await run_thread_section4(request.scenario_number, request.parameters)
        elif section_number == 5:
            result = await run_thread_section5(request.scenario_number, request.parameters)
        elif section_number == 6:
            result = await run_thread_section6(request.scenario_number, request.parameters)
        elif section_number == 7:
            result = await run_thread_section7(request.scenario_number, request.parameters)
        else:
            raise HTTPException(status_code=400, detail="بخش thread یافت نشد")

        return ScenarioResponse(
            section_type=request.section_type.value,
            section_name=request.section_name,
            section_number=section_number,
            scenario_number=request.scenario_number,
            output=result["output"],
            explanation=result["explanation"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در اجرای سناریو: {str(e)}")


# توابع اجرای سناریوهای Thread
async def run_thread_section1(scenario_number: int, parameters: Optional[Dict] = None):
    """بخش 1: Defining a thread"""
    output_lines = []
    output_lock = threading.Lock()

    if scenario_number == 1:
        def worker(thread_id, lock, output):
            with lock:
                output.append(f"my_func called by thread N°{thread_id}")

        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(i, output_lock, output_lines))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        explanation = "ده thread به صورت موازی ایجاد و اجرا می‌شوند"

    elif scenario_number == 2:
        def worker(thread_id, delay, lock, output):
            time.sleep(delay)
            with lock:
                output.append(f"Thread {thread_id} finished after {delay:.1f} seconds")

        threads = []
        delays = [0.1, 0.3, 0.2, 0.5, 0.4, 0.7, 0.6, 0.9, 0.8, 1.0]
        for i in range(10):
            t = threading.Thread(target=worker, args=(i, delays[i], output_lock, output_lines))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        explanation = "ده thread با تاخیرهای مختلف ایجاد می‌شوند"

    elif scenario_number == 3:
        def worker(lock, output):
            thread_name = threading.current_thread().name
            with lock:
                output.append(f"{thread_name} is running")

        threads = []
        names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "Iota", "Kappa"]
        for name in names:
            t = threading.Thread(target=worker, name=name, args=(output_lock, output_lines))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        explanation = "ده thread با نام‌های یونانی ایجاد می‌شوند"

    else:
        raise HTTPException(status_code=400, detail="سناریو thread یافت نشد")

    return {"output": output_lines, "explanation": explanation}


async def run_thread_section2(scenario_number: int, parameters: Optional[Dict] = None):
    """بخش 2: Determining the current thread"""
    output_lines = []
    output_lock = threading.Lock()

    if scenario_number == 1:
        def function_A(lock, output):
            with lock:
                output.append("function_A-> starting")
            time.sleep(1)
            with lock:
                output.append("function_A-> exiting")

        def function_B(lock, output):
            with lock:
                output.append("function_B-> starting")
            time.sleep(0.5)
            with lock:
                output.append("function_B-> exiting")

        def function_C(lock, output):
            with lock:
                output.append("function_C-> starting")
            time.sleep(0.8)
            with lock:
                output.append("function_C-> exiting")

        thread_A = threading.Thread(target=function_A, args=(output_lock, output_lines))
        thread_B = threading.Thread(target=function_B, args=(output_lock, output_lines))
        thread_C = threading.Thread(target=function_C, args=(output_lock, output_lines))

        thread_A.start()
        thread_B.start()
        thread_C.start()

        thread_A.join()
        thread_B.join()
        thread_C.join()

        explanation = "سه تابع مختلف در threadهای جداگانه اجرا می‌شوند"

    elif scenario_number == 2:
        def worker(thread_id, lock, output):
            current_thread = threading.current_thread()
            with lock:
                output.append(f"Thread {thread_id}: Name={current_thread.name}, ID={current_thread.ident}")
            time.sleep(0.5)

        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i, output_lock, output_lines), name=f"Worker-{i}")
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        explanation = "نمایش اطلاعات thread جاری شامل نام و شناسه"

    elif scenario_number == 3:
        def daemon_worker(lock, output):
            with lock:
                output.append("Daemon thread started")
            time.sleep(2)
            with lock:
                output.append("This won't be printed!")

        def normal_worker(lock, output):
            with lock:
                output.append("Normal thread started")
            time.sleep(1)
            with lock:
                output.append("Normal thread exiting")

        daemon_thread = threading.Thread(target=daemon_worker, args=(output_lock, output_lines), daemon=True)
        normal_thread = threading.Thread(target=normal_worker, args=(output_lock, output_lines))

        daemon_thread.start()
        normal_thread.start()

        normal_thread.join()
        with output_lock:
            output_lines.append("Main thread exiting")

        explanation = "مقایسه رفتار threadهای daemon و normal"

    else:
        raise HTTPException(status_code=400, detail="سناریو thread یافت نشد")

    return {"output": output_lines, "explanation": explanation}


async def run_thread_section3(scenario_number: int, parameters: Optional[Dict] = None):
    """بخش 3: Thread subclass"""
    output_lines = []
    output_lock = threading.Lock()

    if scenario_number == 1:
        class CustomThread(threading.Thread):
            def __init__(self, thread_id, lock, output):
                super().__init__()
                self.thread_id = thread_id
                self.lock = lock
                self.output = output

            def run(self):
                with self.lock:
                    self.output.append(
                        f"--> Thread#{self.thread_id} running, belonging to process ID {threading.get_ident()}")

        threads = []
        for i in range(1, 10):
            t = CustomThread(i, output_lock, output_lines)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        explanation = "ایجاد thread با subclass و نمایش اطلاعات process"

    elif scenario_number == 2:
        class CountingThread(threading.Thread):
            def __init__(self, name, count, lock, output):
                super().__init__()
                self.name = name
                self.count = count
                self.lock = lock
                self.output = output

            def run(self):
                for i in range(self.count):
                    with self.lock:
                        self.output.append(f"{self.name}: {i}")
                    time.sleep(0.1)

        thread1 = CountingThread("Counter-A", 5, output_lock, output_lines)
        thread2 = CountingThread("Counter-B", 3, output_lock, output_lines)

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        explanation = "Threadهای شمارنده با پارامترهای مختلف"

    elif scenario_number == 3:
        class TimedThread(threading.Thread):
            def __init__(self, duration, lock, output):
                super().__init__()
                self.duration = duration
                self.lock = lock
                self.output = output
                self.result = None

            def run(self):
                start_time = time.time()
                time.sleep(self.duration)
                self.result = time.time() - start_time
                with self.lock:
                    self.output.append(f"Thread completed in {self.result:.2f} seconds")

        threads = []
        durations = [1.0, 2.0, 0.5, 1.5]
        for duration in durations:
            t = TimedThread(duration, output_lock, output_lines)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        explanation = "Threadهای زمان‌بندی شده با مدت زمان مختلف"

    else:
        raise HTTPException(status_code=400, detail="سناریو thread یافت نشد")

    return {"output": output_lines, "explanation": explanation}


async def run_thread_section4(scenario_number: int, parameters: Optional[Dict] = None):
    """بخش 4: Synchronization with Lock"""
    output_lines = []
    output_lock = threading.Lock()

    if scenario_number == 1:
        lock = threading.Lock()

        def task(thread_id, lock, output_lock, output):
            with lock:
                with output_lock:
                    output.append(f"--> Thread#{thread_id} running, belonging to process ID {threading.get_ident()}")
                time.sleep(0.5)
                with output_lock:
                    output.append(f"--> Thread#{thread_id} over")

        threads = []
        for i in range(1, 10):
            t = threading.Thread(target=task, args=(i, lock, output_lock, output_lines))
            threads.append(t)
            t.start()
            time.sleep(0.1)

        for t in threads:
            t.join()

        with output_lock:
            output_lines.append("End")
        explanation = "استفاده از Lock برای همگام‌سازی"

    elif scenario_number == 2:
        lock = threading.Lock()
        shared_list = []

        def add_to_list(thread_id, value, lock, output_lock, output):
            with lock:
                with output_lock:
                    output.append(f"Thread {thread_id} acquired lock")
                shared_list.append(value)
                time.sleep(0.2)
                with output_lock:
                    output.append(f"Thread {thread_id} added {value}, list: {shared_list}")
                    output.append(f"Thread {thread_id} released lock")

        threads = []
        for i in range(5):
            t = threading.Thread(target=add_to_list, args=(i, i * 10, lock, output_lock, output_lines))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        explanation = "همگام‌سازی دسترسی به لیست مشترک با Lock"

    elif scenario_number == 3:
        lock = threading.Lock()

        def task(thread_id, delay, lock, output_lock, output):
            with output_lock:
                output.append(f"Thread {thread_id} waiting for lock...")
            with lock:
                with output_lock:
                    output.append(f"Thread {thread_id} acquired lock")
                time.sleep(delay)
                with output_lock:
                    output.append(f"Thread {thread_id} releasing lock after {delay} seconds")

        threads = []
        delays = [1.0, 0.5, 0.8, 0.3, 0.6]
        for i, delay in enumerate(delays):
            t = threading.Thread(target=task, args=(i, delay, lock, output_lock, output_lines))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        explanation = "نمایش رفتار Lock با تاخیرهای مختلف"

    else:
        raise HTTPException(status_code=400, detail="سناریو thread یافت نشد")

    return {"output": output_lines, "explanation": explanation}


async def run_thread_section5(scenario_number: int, parameters: Optional[Dict] = None):
    """بخش 5: Synchronization with RLock"""
    output_lines = []
    output_lock = threading.Lock()

    if scenario_number == 1:
        rlock = threading.RLock()
        items_to_add = 16
        items_to_remove = 1

        def add_items(rlock, output_lock, output):
            nonlocal items_to_add
            with rlock:
                while items_to_add > 0:
                    items_to_add -= 1
                    with output_lock:
                        output.append(f"ADDED one item →{items_to_add} item to ADD")
                    time.sleep(0.1)

        def remove_items(rlock, output_lock, output):
            nonlocal items_to_remove
            with rlock:
                while items_to_remove > 0:
                    items_to_remove -= 1
                    with output_lock:
                        output.append(f"REMOVED one item →{items_to_remove} item to REMOVE")
                    time.sleep(0.1)

        with output_lock:
            output_lines.append(f"N° {16} items to ADD")
            output_lines.append(f"N° {1} items to REMOVE")

        add_thread = threading.Thread(target=add_items, args=(rlock, output_lock, output_lines))
        remove_thread = threading.Thread(target=remove_items, args=(rlock, output_lock, output_lines))

        add_thread.start()
        remove_thread.start()

        add_thread.join()
        remove_thread.join()

        explanation = "استفاده از RLock برای عملیات همزمان"

    elif scenario_number == 2:
        class SharedResource:
            def __init__(self, output_lock, output):
                self.rlock = threading.RLock()
                self.data = []
                self.output_lock = output_lock
                self.output = output

            def add_data(self, value):
                with self.rlock:
                    self.data.append(value)
                    with self.output_lock:
                        self.output.append(f"Added {value}, data: {self.data}")

            def process_data(self):
                with self.rlock:
                    if self.data:
                        value = self.data.pop(0)
                        with self.output_lock:
                            self.output.append(f"Processed {value}, remaining: {self.data}")

        resource = SharedResource(output_lock, output_lines)

        def producer():
            for i in range(5):
                resource.add_data(i)
                time.sleep(0.2)

        def consumer():
            for i in range(5):
                resource.process_data()
                time.sleep(0.3)

        prod_thread = threading.Thread(target=producer)
        cons_thread = threading.Thread(target=consumer)

        prod_thread.start()
        cons_thread.start()

        prod_thread.join()
        cons_thread.join()

        explanation = "الگوی Producer-Consumer با RLock"

    elif scenario_number == 3:
        rlock = threading.RLock()

        def recursive_function(level, rlock, output_lock, output):
            with rlock:
                if level > 0:
                    with output_lock:
                        output.append(f"Level {level}: Acquired lock")
                    recursive_function(level - 1, rlock, output_lock, output)
                    with output_lock:
                        output.append(f"Level {level}: Releasing lock")

        threading.Thread(target=recursive_function, args=(3, rlock, output_lock, output_lines)).start()
        time.sleep(1)

        explanation = "نمایش قابلیت بازگشتی RLock"

    else:
        raise HTTPException(status_code=400, detail="سناریو thread یافت نشد")

    return {"output": output_lines, "explanation": explanation}


async def run_thread_section6(scenario_number: int, parameters: Optional[Dict] = None):
    """بخش 6: Synchronization with Semaphores"""
    output_lines = []
    output_lock = threading.Lock()

    if scenario_number == 1:
        buffer = []
        MAX_ITEMS = 5
        empty = threading.Semaphore(MAX_ITEMS)
        full = threading.Semaphore(0)
        mutex = threading.Lock()

        def producer(producer_id, empty, full, mutex, output_lock, output):
            for i in range(3):
                item = random.randint(1, 1000)
                empty.acquire()
                with mutex:
                    buffer.append(item)
                    with output_lock:
                        output.append(f"Producer notify: item number {item}")
                full.release()
                time.sleep(random.uniform(2, 4))

        def consumer(consumer_id, empty, full, mutex, output_lock, output):
            for i in range(3):
                full.acquire()
                with mutex:
                    if buffer:
                        item = buffer.pop(0)
                        with output_lock:
                            output.append(f"Consumer notify: item number {item}")
                empty.release()
                time.sleep(random.uniform(1, 3))

        producers = []
        consumers = []

        for i in range(1, 21, 2):
            p = threading.Thread(target=producer, args=(i, empty, full, mutex, output_lock, output_lines))
            producers.append(p)

        for i in range(2, 21, 2):
            c = threading.Thread(target=consumer, args=(i, empty, full, mutex, output_lock, output_lines))
            consumers.append(c)

        for c in consumers:
            c.start()
            time.sleep(0.1)

        for p in producers:
            p.start()
            time.sleep(0.1)

        for p in producers:
            p.join()

        for c in consumers:
            c.join()

        explanation = "الگوی Producer-Consumer با Semaphore"

    elif scenario_number == 2:
        max_connections = 3
        connection_semaphore = threading.Semaphore(max_connections)

        def database_connection(connection_id, semaphore, output_lock, output):
            with semaphore:
                with output_lock:
                    output.append(f"Connection {connection_id}: Established")
                time.sleep(1)
                with output_lock:
                    output.append(f"Connection {connection_id}: Closed")

        threads = []
        for i in range(8):
            t = threading.Thread(target=database_connection, args=(i, connection_semaphore, output_lock, output_lines))
            threads.append(t)
            t.start()
            time.sleep(0.2)

        for t in threads:
            t.join()

        explanation = "محدود کردن تعداد اتصالات همزمان با Semaphore"

    elif scenario_number == 3:
        ticket_semaphore = threading.Semaphore(5)

        def buy_ticket(customer_id, semaphore, output_lock, output):
            if semaphore.acquire(blocking=False):
                with output_lock:
                    output.append(f"Customer {customer_id}: Ticket purchased")
                time.sleep(0.5)
                semaphore.release()
                with output_lock:
                    output.append(f"Customer {customer_id}: Done")
            else:
                with output_lock:
                    output.append(f"Customer {customer_id}: No tickets available")

        threads = []
        for i in range(10):
            t = threading.Thread(target=buy_ticket, args=(i, ticket_semaphore, output_lock, output_lines))
            threads.append(t)
            t.start()
            time.sleep(0.1)

        for t in threads:
            t.join()

        explanation = "مدیریت منابع محدود با Semaphore"

    else:
        raise HTTPException(status_code=400, detail="سناریو thread یافت نشد")

    return {"output": output_lines, "explanation": explanation}


async def run_thread_section7(scenario_number: int, parameters: Optional[Dict] = None):
    """بخش 7: Synchronization with Barrier"""
    output_lines = []
    output_lock = threading.Lock()

    if scenario_number == 1:
        num_racers = 3
        barrier = threading.Barrier(num_racers, action=lambda: output_lines.append("START RACE!!!!"))

        def racer(name, barrier, output_lock, output):
            with output_lock:
                output.append(f"{name} reached the barrier at: {time.ctime()}")
            barrier.wait()
            time.sleep(random.uniform(1.0, 3.0))
            with output_lock:
                output.append(f"{name} finished!")

        threads = []
        racers = ["Dewey", "Huey", "Louie"]

        for name in racers:
            t = threading.Thread(target=racer, args=(name, barrier, output_lock, output_lines))
            threads.append(t)
            t.start()
            time.sleep(1)

        for t in threads:
            t.join()

        with output_lock:
            output_lines.append("Race over!")
        explanation = "مسابقه با Barrier برای هماهنگی شروع"

    elif scenario_number == 2:
        num_workers = 4
        barrier = threading.Barrier(num_workers)

        def worker(worker_id, barrier, output_lock, output):
            with output_lock:
                output.append(f"Worker {worker_id}: Phase 1 started")
            time.sleep(random.uniform(0.5, 2.0))
            with output_lock:
                output.append(f"Worker {worker_id}: Waiting at barrier")
            barrier.wait()
            with output_lock:
                output.append(f"Worker {worker_id}: Phase 2 started")
            time.sleep(0.5)
            with output_lock:
                output.append(f"Worker {worker_id}: Completed")

        threads = []
        for i in range(num_workers):
            t = threading.Thread(target=worker, args=(i, barrier, output_lock, output_lines))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        explanation = "هماهنگی فازهای کاری با Barrier"

    elif scenario_number == 3:
        num_teams = 2
        players_per_team = 3
        barrier = threading.Barrier(players_per_team * num_teams)

        def player(team_id, player_id, barrier, output_lock, output):
            with output_lock:
                output.append(f"Team {team_id} Player {player_id}: Ready")
            barrier.wait()
            with output_lock:
                output.append(f"Team {team_id} Player {player_id}: Game started!")

        threads = []
        for team in range(num_teams):
            for player_num in range(players_per_team):
                t = threading.Thread(target=player, args=(team, player_num, barrier, output_lock, output_lines))
                threads.append(t)
                t.start()
                time.sleep(0.3)

        for t in threads:
            t.join()

        with output_lock:
            output_lines.append("All players started successfully!")
        explanation = "هماهنگی بازیکنان تیم‌های مختلف با Barrier"

    else:
        raise HTTPException(status_code=400, detail="سناریو thread یافت نشد")

    return {"output": output_lines, "explanation": explanation}
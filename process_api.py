from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import multiprocessing
import time
import asyncio
import random
from enum import Enum
from datetime import datetime

app = FastAPI(title="Process API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# نگاشت نام بخش‌های process
PROCESS_SECTION_NAMES = {
    1: "Spawning a process",
    2: "Naming a process",
    3: "Running processes in background",
    4: "Killing a process",
    5: "Process subclass",
    6: "Using queue for data exchange",
    7: "Synchronizing processes",
    8: "Using process pool"
}

PROCESS_SECTION_REVERSE = {v: k for k, v in PROCESS_SECTION_NAMES.items()}


# مدل‌های درخواست و پاسخ
class SectionType(str, Enum):
    PROCESS = "process"


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
    return {"message": "Process API is running", "sections": PROCESS_SECTION_NAMES}


@app.post("/api/run-scenario", response_model=ScenarioResponse)
async def run_scenario(request: ScenarioRequest):
    try:
        if request.section_name not in PROCESS_SECTION_REVERSE:
            raise HTTPException(status_code=400, detail="بخش process یافت نشد")

        section_number = PROCESS_SECTION_REVERSE[request.section_name]

        if section_number == 1:
            result = await run_process_section1(request.scenario_number, request.parameters)
        elif section_number == 2:
            result = await run_process_section2(request.scenario_number, request.parameters)
        elif section_number == 3:
            result = await run_process_section3(request.scenario_number, request.parameters)
        elif section_number == 4:
            result = await run_process_section4(request.scenario_number, request.parameters)
        elif section_number == 5:
            result = await run_process_section5(request.scenario_number, request.parameters)
        elif section_number == 6:
            result = await run_process_section6(request.scenario_number, request.parameters)
        elif section_number == 7:
            result = await run_process_section7(request.scenario_number, request.parameters)
        elif section_number == 8:
            result = await run_process_section8(request.scenario_number, request.parameters)
        else:
            raise HTTPException(status_code=400, detail="بخش process یافت نشد")

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


# توابع global برای Process
def myFunc_s1_sc1(i, lock, output):
    with lock:
        output.append(f"calling myFunc from process n°: {i}")
    time.sleep(0.1)
    for j in range(i):
        with lock:
            output.append(f"output from myFunc is :{j}")
        time.sleep(0.05)


def myFunc_s1_sc2(i, output):
    output.append(f"calling myFunc from process n°: {i}")
    for j in range(i):
        output.append(f"output from myFunc is :{j}")


def myFunc_s1_sc3(i, lock, output):
    delay = random.uniform(0.01, 0.1)
    time.sleep(delay)
    with lock:
        output.append(f"calling myFunc from process n°: {i}")
    for j in range(i):
        time.sleep(0.05)
        with lock:
            output.append(f"output from myFunc is :{j}")


def worker_s2_sc1(output):
    proc = multiprocessing.current_process()
    output.append(f"Starting process name = {proc.name}")
    time.sleep(1)
    output.append(f"Exiting process name = {proc.name}")


def task_s2_sc2(output):
    current = multiprocessing.current_process()
    output.append(f"Starting process name = {current.name}")
    time.sleep(0.5)
    output.append(f"Exiting process name = {current.name}")


def complex_task_s2_sc3(output):
    proc = multiprocessing.current_process()
    output.append(f"Starting process name = {proc.name}")
    if proc.name == "Process-2":
        proc.name = "Renamed-Process"
        output.append(f"Changed name to = {proc.name}")
    time.sleep(1)
    output.append(f"Exiting process name = {proc.name}")


def count_numbers_s3(process_name, start, end, output):
    output.append(f"Starting {process_name}")
    for i in range(start, end):
        output.append(f"---> {i}")
        time.sleep(0.1)
    output.append(f"Exiting {process_name}")


def long_running_task_s4_sc1(output):
    output.append("Task started")
    try:
        for i in range(10):
            output.append(f"Working... {i}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        output.append("Task interrupted")
    output.append("Task completed")


def infinite_task_s4_sc2(output):
    output.append("Infinite task started")
    try:
        while True:
            output.append("Still working...")
            time.sleep(0.3)
    except KeyboardInterrupt:
        output.append("Interrupted by signal")
    output.append("Task ended")


def graceful_task_s4_sc3(output):
    output.append("Graceful task started")
    for i in range(20):
        output.append(f"Processing item {i}")
        time.sleep(0.2)
        if multiprocessing.current_process().exitcode is not None:
            output.append("Received termination signal, cleaning up...")
            break
    output.append("Graceful task completed")


class MyProcess_s5_sc1(multiprocessing.Process):
    def __init__(self, process_id, output):
        super().__init__()
        self.process_id = process_id
        self.name = f"MyProcess-{process_id}"
        self.output = output

    def run(self):
        self.output.append(f"called run method by {self.name}")
        time.sleep(0.1)


class CustomProcess_s5_sc2(multiprocessing.Process):
    def __init__(self, process_id, delay, output):
        super().__init__()
        self.process_id = process_id
        self.delay = delay
        self.name = f"MyProcess-{process_id}"
        self.output = output

    def run(self):
        self.output.append(f"called run method by {self.name}")
        time.sleep(self.delay)
        self.output.append(f"{self.name} completed after {self.delay} seconds")


class AdvancedProcess_s5_sc3(multiprocessing.Process):
    def __init__(self, process_id, task_duration, output):
        super().__init__()
        self.process_id = process_id
        self.task_duration = task_duration
        self.name = f"MyProcess-{process_id}"
        self.stopped = multiprocessing.Event()
        self.output = output

    def run(self):
        self.output.append(f"called run method by {self.name}")
        start_time = time.time()
        while not self.stopped.is_set():
            time.sleep(self.task_duration)
            if time.time() - start_time > 1.0:
                break
        self.output.append(f"{self.name} finished execution")

    def stop(self):
        self.stopped.set()


def producer_s6_sc1(queue, producer_id, output):
    for i in range(5):
        item = random.randint(1, 100)
        queue.put(item)
        output.append(f"Process Producer : item {item} appended to queue {producer_id}")
        output.append(f"The size of queue is {queue.qsize()}")
        time.sleep(0.1)


def consumer_s6_sc1(queue, consumer_id, output):
    while not queue.empty():
        try:
            item = queue.get(timeout=1)
            output.append(f"Process Consumer : item {item} popped from by {consumer_id}")
            time.sleep(0.15)
        except:
            break


def worker_s6_sc2(task_queue, result_queue, worker_id, output):
    while True:
        try:
            task = task_queue.get(timeout=1)
            if task is None:
                break
            result = task * 2
            result_queue.put(result)
            output.append(f"Worker {worker_id} processed task {task} -> {result}")
            time.sleep(0.1)
        except:
            break


def priority_producer_s6_sc3(high_queue, low_queue, producer_id, output):
    for i in range(10):
        if random.random() > 0.7:
            high_queue.put(f"HIGH-{i}")
            output.append(f"Producer {producer_id} added HIGH priority item {i}")
        else:
            low_queue.put(f"LOW-{i}")
            output.append(f"Producer {producer_id} added LOW priority item {i}")
        time.sleep(0.1)


def priority_consumer_s6_sc3(high_queue, low_queue, consumer_id, output):
    count = 0
    while count < 10:
        if not high_queue.empty():
            item = high_queue.get()
            output.append(f"Consumer {consumer_id} processed {item}")
            count += 1
        elif not low_queue.empty():
            item = low_queue.get()
            output.append(f"Consumer {consumer_id} processed {item}")
            count += 1
        time.sleep(0.1)


def test_with_barrier_s7_sc1(barrier, process_name, output):
    time.sleep(0.1)
    barrier.wait()
    output.append(f"{process_name} - test_with_barrier ----> {datetime.now()}")


def test_without_barrier_s7_sc1(process_name, output):
    time.sleep(0.1)
    output.append(f"{process_name} - test_without_barrier ----> {datetime.now()}")


def shared_resource_access_s7_sc2(lock, process_name, output):
    time.sleep(0.1)
    with lock:
        current_time = datetime.now()
        output.append(f"{process_name} accessed shared resource at: {current_time}")
        time.sleep(0.05)


def independent_task_s7_sc2(process_name, output):
    time.sleep(0.1)
    output.append(f"{process_name} completed independent task at: {datetime.now()}")


def coordinated_task_s7_sc3(event, semaphore, process_name, output):
    event.wait()
    with semaphore:
        current_time = datetime.now()
        output.append(f"{process_name} started coordinated task at: {current_time}")
        time.sleep(random.uniform(0.1, 0.3))
        output.append(f"{process_name} finished coordinated task at: {datetime.now()}")


def independent_worker_s7_sc3(process_name, output):
    time.sleep(0.1)
    output.append(f"{process_name} working independently at: {datetime.now()}")


def square_s8_sc1(x):
    return x * x


def process_task_s8_sc2(x, output):
    time.sleep(0.01)
    result = x * x
    output.append(f"Processed {x} -> {result} by {multiprocessing.current_process().name}")
    return result


def complex_calculation_s8_sc3(x, output):
    time.sleep(0.02)
    result = x ** 2 + 2 * x + 1
    output.append(f"Calculated f({x}) = {result}")
    return result


# توابع اجرای سناریوهای Process
async def run_process_section1(scenario_number: int, parameters: Optional[Dict] = None):
    """بخش 1: Spawning a process"""
    output_lines = []
    manager = multiprocessing.Manager()
    shared_output = manager.list()
    output_lock = multiprocessing.Lock()

    if scenario_number == 1:
        processes = []
        for i in range(6):
            p = multiprocessing.Process(target=myFunc_s1_sc1, args=(i, output_lock, shared_output))
            processes.append(p)
            p.start()
            time.sleep(0.05)

        for p in processes:
            p.join()

        output_lines.extend(shared_output)
        explanation = "ایجاد و اجرای چندین فرآیند به صورت موازی"

    elif scenario_number == 2:
        processes = []
        for i in range(6):
            p = multiprocessing.Process(target=myFunc_s1_sc2, args=(i, shared_output))
            processes.append(p)
            p.start()
            p.join()

        output_lines.extend(shared_output)
        explanation = "ایجاد فرآیندها به صورت سریال با join کردن هر کدام"

    elif scenario_number == 3:
        processes = []
        for i in range(6):
            p = multiprocessing.Process(target=myFunc_s1_sc3, args=(i, output_lock, shared_output))
            processes.append(p)
            p.start()
            time.sleep(0.01)

        for p in processes:
            p.join()

        output_lines.extend(shared_output)
        explanation = "ایجاد فرآیندها با تاخیرهای تصادفی و استفاده از lock برای هماهنگی"

    else:
        raise HTTPException(status_code=400, detail="سناریو process یافت نشد")

    return {"output": output_lines, "explanation": explanation}


async def run_process_section2(scenario_number: int, parameters: Optional[Dict] = None):
    """بخش 2: Naming a process"""
    output_lines = []
    manager = multiprocessing.Manager()
    shared_output = manager.list()

    if scenario_number == 1:
        p1 = multiprocessing.Process(target=worker_s2_sc1, name="myFunc process", args=(shared_output,))
        p2 = multiprocessing.Process(target=worker_s2_sc1, args=(shared_output,))

        p1.start()
        p2.start()

        p1.join()
        p2.join()

        output_lines.extend(shared_output)
        explanation = "ایجاد فرآیند با نام دستی و نام پیش‌فرض"

    elif scenario_number == 2:
        processes = []
        p1 = multiprocessing.Process(target=task_s2_sc2, name="myFunc process", args=(shared_output,))
        processes.append(p1)

        for i in range(2):
            p = multiprocessing.Process(target=task_s2_sc2, args=(shared_output,))
            processes.append(p)

        for p in processes:
            p.start()
            time.sleep(0.1)

        for p in processes:
            p.join()

        output_lines.extend(shared_output)
        explanation = "ایجاد چندین فرآیند با نام‌های مختلف"

    elif scenario_number == 3:
        p1 = multiprocessing.Process(target=complex_task_s2_sc3, name="myFunc process", args=(shared_output,))
        p2 = multiprocessing.Process(target=complex_task_s2_sc3, args=(shared_output,))

        p1.start()
        p2.start()

        p1.join()
        p2.join()

        output_lines.extend(shared_output)
        explanation = "تغییر نام فرآیند در حین اجرا"

    else:
        raise HTTPException(status_code=400, detail="سناریو process یافت نشد")

    return {"output": output_lines, "explanation": explanation}


async def run_process_section3(scenario_number: int, parameters: Optional[Dict] = None):
    """بخش 3: Running processes in background"""
    output_lines = []
    manager = multiprocessing.Manager()
    shared_output = manager.list()

    if scenario_number == 1:
        p1 = multiprocessing.Process(target=count_numbers_s3,
                                     args=("NO_background_process", 5, 10, shared_output))
        p1.start()
        p1.join()

        output_lines.extend(shared_output)
        output_lines.append("Main process continues after normal process completion")
        explanation = "فرآیند عادی با انتظار برای پایان آن"

    elif scenario_number == 2:
        p1 = multiprocessing.Process(target=count_numbers_s3,
                                     args=("NO_background_process", 5, 10, shared_output))
        p2 = multiprocessing.Process(target=count_numbers_s3,
                                     args=("background_process", 0, 5, shared_output))

        p1.start()
        p2.start()
        p1.join()

        output_lines.extend(shared_output)
        output_lines.append("Main process continues without waiting for background process")
        time.sleep(1)
        explanation = "فرآیند پس‌زمینه بدون انتظار برای پایان آن"

    elif scenario_number == 3:
        p1 = multiprocessing.Process(target=count_numbers_s3,
                                     args=("NO_background_process", 5, 10, shared_output))
        p2 = multiprocessing.Process(target=count_numbers_s3,
                                     args=("background_process", 0, 5, shared_output))
        p2.daemon = True

        p1.start()
        p2.start()
        p1.join()

        output_lines.extend(shared_output)
        output_lines.append("Main process exits, daemon process will be terminated automatically")
        explanation = "فرآیند دیمون که با پایان فرآیند اصلی terminate می‌شود"

    else:
        raise HTTPException(status_code=400, detail="سناریو process یافت نشد")

    return {"output": output_lines, "explanation": explanation}


async def run_process_section4(scenario_number: int, parameters: Optional[Dict] = None):
    """بخش 4: Killing a process"""
    output_lines = []
    manager = multiprocessing.Manager()
    shared_output = manager.list()

    if scenario_number == 1:
        process = multiprocessing.Process(target=long_running_task_s4_sc1, args=(shared_output,))
        output_lines.append(f"Process before execution: {process} {process.is_alive()}")

        process.start()
        time.sleep(0.1)
        output_lines.append(f"Process running: {process} {process.is_alive()}")

        time.sleep(1)
        process.terminate()
        output_lines.append(f"Process terminated: {process} {process.is_alive()}")

        process.join()
        output_lines.append(f"Process joined: {process} {process.is_alive()}")
        output_lines.append(f"Process exit code: {process.exitcode}")

        output_lines.extend(shared_output)
        explanation = "پایان دادن به فرآیند با terminate()"

    elif scenario_number == 2:
        process = multiprocessing.Process(target=infinite_task_s4_sc2, args=(shared_output,))
        output_lines.append(f"Process before execution: {process} {process.is_alive()}")

        process.start()
        time.sleep(0.1)
        output_lines.append(f"Process running: {process} {process.is_alive()}")

        time.sleep(1)
        process.kill()
        output_lines.append(f"Process killed: {process} {process.is_alive()}")

        process.join()
        output_lines.append(f"Process joined: {process} {process.is_alive()}")
        output_lines.append(f"Process exit code: {process.exitcode}")

        output_lines.extend(shared_output)
        explanation = "پایان شدید فرآیند با kill() (معادل SIGKILL)"

    elif scenario_number == 3:
        process = multiprocessing.Process(target=graceful_task_s4_sc3, args=(shared_output,))
        output_lines.append(f"Process before execution: {process} {process.is_alive()}")

        process.start()
        time.sleep(0.1)
        output_lines.append(f"Process running: {process} {process.is_alive()}")

        time.sleep(1.5)
        process.terminate()
        output_lines.append(f"Process terminated: {process} {process.is_alive()}")

        process.join()
        output_lines.append(f"Process joined: {process} {process.is_alive()}")
        output_lines.append(f"Process exit code: {process.exitcode}")

        output_lines.extend(shared_output)
        explanation = "پایان graceful فرآیند با بررسی exitcode"

    else:
        raise HTTPException(status_code=400, detail="سناریو process یافت نشد")

    return {"output": output_lines, "explanation": explanation}


async def run_process_section5(scenario_number: int, parameters: Optional[Dict] = None):
    """بخش 5: Process subclass"""
    output_lines = []
    manager = multiprocessing.Manager()
    shared_output = manager.list()

    if scenario_number == 1:
        processes = []
        for i in range(1, 11):
            p = MyProcess_s5_sc1(i, shared_output)
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        output_lines.extend(shared_output)
        explanation = "ایجاد فرآیند با subclass پایه"

    elif scenario_number == 2:
        processes = []
        for i in range(1, 11):
            delay = i * 0.05
            p = CustomProcess_s5_sc2(i, delay, shared_output)
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        output_lines.extend(shared_output)
        explanation = "ایجاد فرآیند با تاخیرهای قابل تنظیم"

    elif scenario_number == 3:
        processes = []
        for i in range(1, 11):
            duration = random.uniform(0.1, 0.3)
            p = AdvancedProcess_s5_sc3(i, duration, shared_output)
            processes.append(p)
            p.start()

        time.sleep(0.5)
        for p in processes:
            p.stop()

        for p in processes:
            p.join()

        output_lines.extend(shared_output)
        explanation = "ایجاد فرآیند پیشرفته با قابلیت توقف"

    else:
        raise HTTPException(status_code=400, detail="سناریو process یافت نشد")

    return {"output": output_lines, "explanation": explanation}


async def run_process_section6(scenario_number: int, parameters: Optional[Dict] = None):
    """بخش 6: Using queue for data exchange"""
    output_lines = []
    manager = multiprocessing.Manager()
    shared_output = manager.list()

    if scenario_number == 1:
        queue = multiprocessing.Queue()
        p1 = multiprocessing.Process(target=producer_s6_sc1, args=(queue, "producer-1", shared_output))
        p2 = multiprocessing.Process(target=consumer_s6_sc1, args=(queue, "consumer-2", shared_output))

        p1.start()
        p2.start()

        p1.join()
        p2.join()

        output_lines.extend(shared_output)
        output_lines.append("the queue is empty")
        explanation = "مبادله داده بین فرآیندها با استفاده از Queue"

    elif scenario_number == 2:
        task_queue = multiprocessing.Queue()
        result_queue = multiprocessing.Queue()

        for i in range(10):
            task_queue.put(i)

        workers = []
        for i in range(3):
            p = multiprocessing.Process(target=worker_s6_sc2, args=(task_queue, result_queue, i + 1, shared_output))
            workers.append(p)
            p.start()

        for p in workers:
            task_queue.put(None)

        for p in workers:
            p.join()

        results = []
        while not result_queue.empty():
            results.append(result_queue.get())

        output_lines.extend(shared_output)
        output_lines.append(f"Results: {results}")
        explanation = "الگوی Worker با استفاده از Queue"

    elif scenario_number == 3:
        high_queue = multiprocessing.Queue()
        low_queue = multiprocessing.Queue()

        p1 = multiprocessing.Process(target=priority_producer_s6_sc3, args=(high_queue, low_queue, "P1", shared_output))
        p2 = multiprocessing.Process(target=priority_consumer_s6_sc3, args=(high_queue, low_queue, "C1", shared_output))

        p1.start()
        p2.start()

        p1.join()
        p2.join()

        output_lines.extend(shared_output)
        explanation = "Queue با اولویت‌بندی"

    else:
        raise HTTPException(status_code=400, detail="سناریو process یافت نشد")

    return {"output": output_lines, "explanation": explanation}


async def run_process_section7(scenario_number: int, parameters: Optional[Dict] = None):
    """بخش 7: Synchronizing processes"""
    output_lines = []
    manager = multiprocessing.Manager()
    shared_output = manager.list()

    if scenario_number == 1:
        barrier = multiprocessing.Barrier(2)
        p1 = multiprocessing.Process(target=test_with_barrier_s7_sc1, args=(barrier, "process p1", shared_output))
        p2 = multiprocessing.Process(target=test_with_barrier_s7_sc1, args=(barrier, "process p2", shared_output))
        p3 = multiprocessing.Process(target=test_without_barrier_s7_sc1, args=("process p3", shared_output))
        p4 = multiprocessing.Process(target=test_without_barrier_s7_sc1, args=("process p4", shared_output))

        p1.start()
        p2.start()
        p3.start()
        p4.start()

        p1.join()
        p2.join()
        p3.join()
        p4.join()

        output_lines.extend(shared_output)
        explanation = "هماهنگی فرآیندها با Barrier"

    elif scenario_number == 2:
        lock = multiprocessing.Lock()
        processes = []

        for i in range(2):
            p = multiprocessing.Process(target=shared_resource_access_s7_sc2,
                                        args=(lock, f"process p{i + 1}", shared_output))
            processes.append(p)
            p.start()

        for i in range(2):
            p = multiprocessing.Process(target=independent_task_s7_sc2, args=(f"process p{i + 3}", shared_output))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        output_lines.extend(shared_output)
        explanation = "هماهنگی با Lock برای دسترسی انحصاری"

    elif scenario_number == 3:
        start_event = multiprocessing.Event()
        semaphore = multiprocessing.Semaphore(2)
        processes = []

        for i in range(4):
            p = multiprocessing.Process(target=coordinated_task_s7_sc3,
                                        args=(start_event, semaphore, f"coordinated p{i + 1}", shared_output))
            processes.append(p)
            p.start()

        for i in range(2):
            p = multiprocessing.Process(target=independent_worker_s7_sc3, args=(f"independent p{i + 1}", shared_output))
            processes.append(p)
            p.start()

        time.sleep(0.5)
        output_lines.append("Starting coordinated tasks...")
        start_event.set()

        for p in processes:
            p.join()

        output_lines.extend(shared_output)
        explanation = "هماهنگی پیشرفته با Event و Semaphore"

    else:
        raise HTTPException(status_code=400, detail="سناریو process یافت نشد")

    return {"output": output_lines, "explanation": explanation}


async def run_process_section8(scenario_number: int, parameters: Optional[Dict] = None):
    """بخش 8: Using process pool"""
    output_lines = []
    manager = multiprocessing.Manager()
    shared_output = manager.list()

    if scenario_number == 1:
        with multiprocessing.Pool(processes=4) as pool:
            results = pool.map(square_s8_sc1, range(100))
            output_lines.append(f"Pool : {results}")

        explanation = "استفاده از Process Pool برای محاسبه مربع اعداد"

    elif scenario_number == 2:
        def process_task_wrapper(x):
            return process_task_s8_sc2(x, shared_output)

        num_processes = multiprocessing.cpu_count()
        output_lines.append(f"Using {num_processes} processes")

        with multiprocessing.Pool(processes=num_processes) as pool:
            async_result = pool.map_async(process_task_wrapper, range(100))
            output_lines.append("Main process is doing other work...")
            time.sleep(0.5)
            results = async_result.get()

            output_lines.append(f"Total results: {len(results)}")
            output_lines.append(f"First 10 results: {results[:10]}")
            output_lines.append(f"Last 10 results: {results[-10:]}")

        explanation = "استفاده از map_async برای اجرای غیرمسدود کننده"

    elif scenario_number == 3:
        def complex_calculation_wrapper(x):
            return complex_calculation_s8_sc3(x, shared_output)

        with multiprocessing.Pool(processes=3) as pool:
            results = list(pool.imap(complex_calculation_wrapper, range(20)))
            output_lines.append(f"All results: {results}")

        explanation = "استفاده از imap برای نتایج تدریجی"

    else:
        raise HTTPException(status_code=400, detail="سناریو process یافت نشد")

    return {"output": output_lines, "explanation": explanation}
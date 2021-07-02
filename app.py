import tkinter as tk
from tkinter import ttk
from tkinter import font
import functools
from tkinter.constants import CENTER
from modelskate import *
from json import load, dump
import serial
from time import sleep
import threading
fp = functools.partial


def _on_mouse_wheel(canv, event):
    canv.yview_scroll(-1 * int((event.delta / 120)), "units")


def create_user(RFID, name, timing):
    if RFID and name and timing:
        if session.query(User).filter_by(RFID=RFID).first() is None:
            usr = User(
                RFID=RFID,
                name=name,
                timing=timing,
            )
        else:
            usr = session.query(User).filter_by(RFID=RFID).first()
            usr.RFID = RFID
            usr.name = name
            usr.timing = timing
        session.add(usr)
        session.commit()
        if len(session.query(User).all()) > 0:
            show_users()
    else:
        print('PUSTO')


def create_action(id, gate, session):
    def enter_leave(gate):
        if not gate:
            if ((datetime.now() - session.query(Action).filter_by(user_id=id).first().action_time) / 60).seconds > session.query(User).filter_by(id=id).first().timing + 10:
                return False
            else:
                return True
        else:
            return True

    act = Action(
        user_id=id,
        action_time=datetime.now(),
        is_entry=gate,
        left_on_time=enter_leave(gate),
        isActive=True if gate else False
    )
    session.add(act)
    session.commit()
    if enter_leave(gate) == True:
        return True
    else:
        return False


lbl_width = 15
lbl_font = 20
btn_width = 10

win = tk.Tk()
win.geometry('500x700+150+150')
win.title("Main Window")
win.configure(background='white')
win.resizable(False, False)
running = True

tab_parent = ttk.Notebook(win)

tab1 = ttk.Frame(tab_parent)
tab2 = ttk.Frame(tab_parent)
tab_parent.add(tab1, text="Добавить посетителя")
tab_parent.add(tab2, text="Действия")
tab_parent.pack(expand=1, fill="both")
fr_t_usr = tk.Frame(tab1, bg='orange', bd=5)
fr_t_usr.place(relx=0.25, rely=0.015, relwidth=0.5, relheight=0.08)
fr_b_usr = tk.Frame(tab1, bg='grey', bd=5)
fr_b_usr.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.2)
fr_all_usr = tk.Frame(tab1, bg='orange', bd=5)
fr_all_usr.place(relx=0.1, rely=0.3, relwidth=0.8, relheight=0.5)
fr_t_act = tk.Frame(tab2, bg='orange', bd=5)
fr_t_act.place(relx=0.25, rely=0.015, relwidth=0.5, relheight=0.08)
fr_b_act = tk.Frame(tab2, bg='grey', bd=5)
fr_b_act.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.5)

lbl = tk.Label(fr_t_usr, text="ДОБАВИТЬ ПОСЕТИТЕЛЯ",
               width=lbl_width*2, font=(lbl_font), borderwidth=0, bg='orange')
lbl.place(x=123, y=20, anchor='center')

lbl = tk.Label(fr_b_usr, text='ИМЯ', width=lbl_width, bd=0)
lbl.grid(column=0, row=0, padx=2, pady=2)

name_ef = tk.Entry(fr_b_usr)
name_ef.grid(column=1, row=0, padx=2, pady=2)

lbl = tk.Label(fr_b_usr, text='НА ВРЕМЯ:', width=lbl_width, bd=0)
lbl.grid(column=0, row=1, padx=2, pady=2)
time_cbb = ttk.Combobox(fr_b_usr, values=[
                        'На 30 мин', 'на 60 мин'], width=lbl_width+2)
time_cbb.current(0)
time_cbb.grid(column=1, row=1, padx=2, pady=2)

lbl = tk.Label(fr_b_usr, text='RFID', width=lbl_width, bd=0)
lbl.grid(column=0, row=2, padx=2, pady=2)

rfid_ef = tk.Entry(fr_b_usr)
rfid_ef.grid(column=1, row=2, padx=2, pady=2)

name_btn = tk.Button(fr_b_usr, text='ДОБАВИТЬ',
                     command=lambda: [create_user(RFID=rfid_ef.get(), name=name_ef.get(), timing=30 if time_cbb.get() == "На 30 мин" else 60), show_users()])
name_btn.grid(column=2, row=3, padx=2, pady=2)

lbl = tk.Label(fr_t_act, text="ПОСЕТИТЕЛИ",
               width=lbl_width*2, font=(lbl_font*2), borderwidth=0, bg='orange')
lbl.place(x=123, y=20, anchor='center')


def show_users():
    col = 0
    row = 1
    try:
        for i in search_query(session, User):
            e = tk.Label(
                fr_all_usr, text=f"{session.query(User).filter_by(id=i.id).first().name} купил на: {i.timing} мин", width=lbl_width*3+8)
            e.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 1 == 0:
                row += 1
                col = 0
    except Exception as E:
        er = tk.Label(fr_all_usr, width=lbl_width,
                      text="Nothing", borderwidth=0)
        er.grid(row=5, column=0, padx=5, pady=5)
        print("exc is " + str(E))


def show_actions(session):
    col = 0
    row = 1
    try:
        for i in search_query(session, Action):
            person = session.query(User).filter_by(id=i.user_id).first()
            e = tk.Label(
                fr_b_act, text=f"{person.name} \
{'Вошел' if i.is_entry else 'Вышел'} \
в {i.action_time.strftime('%H:%M:%S')} \
куплено: {person.timing} мин \
{'' if i.is_entry else 'пробыл: ' + str(round((session.query(Action).filter_by(user_id=i.user_id).order_by(Action.id.desc()).first().action_time - session.query(Action).filter_by(user_id=i.user_id).first().action_time).seconds / 60, 2)) + ' мин' }\
{'' if i.left_on_time else 'ПРОСРОЧЕНО'}")
            e.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 1 == 0:
                row += 1
                col = 0
    except Exception as E:
        er = tk.Label(fr_b_act, width=lbl_width,
                      text="Nothing", borderwidth=0)
        er.grid(row=5, column=0, padx=5, pady=5)
        print("exc is " + str(E))


comPorts = []
serialPorts = []
try:
    with open('ports.json') as json_file:
        data = load(json_file)
        serialPorts = data
except Exception:
    a = ['COM1', 'COM2', 'COM3', 'COM4', 'COM25', '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2',
         '/dev/ttyACM3', '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3']
    with open('ports.json', 'w') as outfile:
        dump(a, outfile)
finally:
    with open('ports.json') as json_file:
        data = load(json_file)
        serialPorts = data
# ]
for port in serialPorts:
    try:
        arduino_port = serial.Serial(port, baudrate=9600,
                                     parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE,
                                     bytesize=serial.EIGHTBITS,
                                     timeout=0.04)
        comPorts.append(arduino_port)
    except Exception as E:
        print(str(E))
array1 = [-1, -1, -1, -1]


def serialThread1():
    global running, comPorts
    meta = MetaData()
    Base = declarative_base()
    engine = create_engine("sqlite:///skates.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    while running:
        sleep(0.1)
        serialThread(comPorts, session)


def serialThread(comPorts, session):
    portIndex = -1
    for comPort in comPorts:
        portIndex = portIndex + 1
        try:
            rec = str(comPort.readline())
            global array1
            for i in range(4):
                if array1[i] >= 0:
                    array1[i] = array1[i] + 1
                    if array1[i] > 10:  # счётчик
                        array1[i] = -1
                        if i == 0:
                            dev_id = "!"
                        elif i == 1:
                            dev_id = "@"
                        elif i == 2:
                            dev_id = "#"
                        else:
                            dev_id = "$"
                        comPort.write(str.encode(str(dev_id) + '*\n'))

            if len(rec) > 4:
                rec = rec.strip()
                data = rec.strip().split('#')
                if len(data) >= 2:  # was 3 and w/o =
                    # was without [2::] and -1
                    dev_id = int(str(data[1-1])[2::])
                    if dev_id in [1, 3]:
                        gate = 1
                    else:
                        gate = 0
                    RFID = data[2-1].strip().upper()[:8]  # was without -1
                    # gate = int(data[3]) #wasn't comment
                    if gate == 1:
                        rfid_ef.delete(0, tk.END)
                        rfid_ef.insert(0, RFID)
                    if RFID == "TEST" or RFID == "RESET":
                        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        # comError[portIndex] = 0
                    else:  # wasnt comment
                        if gate == 0:  # 1-come,0-leave
                            gate = False
                        else:
                            gate = True

                        # timers[index] = maxtime
                        # comError[portIndex] = 0
                        try:
                            # session = Session()
                            usr = session.query(User).filter_by(
                                RFID=RFID).first()
                            if create_action(usr.id, gate, session):
                                array1[dev_id-1] = 0

                                comPort.write(str.encode(
                                    str(dev_id) + '*\n'))
                            else:
                                print("OTKAZANO")
                                array1[dev_id-1] = 0
                            show_actions(session)
                            # setAttendace()
                            # stdNames[index].config(text=name+"\n"+group_id)

                        except Exception as ex:
                            print('PP' + str(ex))
                            print("Пользователь не найден!")
                           # stdNames[index].config(text="Aniqlanmagan")
                           # stdPhotos[index].config(image=unknownImg)
                           # stdPhotos[index].image = unknownImg
        except Exception as ex:
            # if comError[portIndex] > 60:
            #      comError[portIndex] = 0
            #      print("abort:" + str(comPorts.pop(portIndex)))
            #      reboot()
            print("Serial thread:" + str(ex))


thread = threading.Thread(target=serialThread1)
thread.start()


def on_closing():
    session.close()
    global running
    running = False
    win.destroy()


show_actions()
show_users()

win.protocol("WM_DELETE_WINDOW", on_closing)
win.mainloop()

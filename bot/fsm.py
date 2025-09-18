from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


class ScheduleChoice(StatesGroup):
    menu = State()
    choice_course = State()
    choice_parity = State()


class SubscribeChoice(StatesGroup):
    remove_sub = State()

    add_sub = State()
    choice_course_sub = State()


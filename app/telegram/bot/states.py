from aiogram.fsm.state import State, StatesGroup


class ResumeStates(StatesGroup):
    waiting_resume = State()

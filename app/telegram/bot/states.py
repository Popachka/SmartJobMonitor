from aiogram.fsm.state import State, StatesGroup


class BotStates(StatesGroup):
    main_menu = State()
    waiting_resume = State()
    processing_resume = State()

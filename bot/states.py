from aiogram.fsm.state import State, StatesGroup


class SenderStates(StatesGroup):
    awaiting_feedback_text = State()


class OwnerStates(StatesGroup):
    awaiting_reply_text = State()


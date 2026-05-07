from src.models.reply import Reply
from src.utils.validators import moderate_text

def create_reply(db, feedback_id, text):
    text = moderate_text(text)
    reply = Reply(feedback_id=feedback_id, text=text)
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply
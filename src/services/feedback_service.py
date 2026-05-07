from src.models.feedback import Feedback
from src.utils.validators import moderate_text

def create_feedback(db, box_id, text):
    text = moderate_text(text)
    fb = Feedback(box_id=box_id, text=text, status="approved")
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb
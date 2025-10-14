class Styles:
    btn_start = """
    {
        border: 1px solid gray;
        border-radius: 10px;
        background-color: rgb(217, 226, 255);
    }
    """

    btn_stop = """
    {
        border: 1px solid gray;
        border-radius: 10px;
        background-color: rgb(254, 221, 255);
    }
    """

    btn_tg_start = """
    {
        border: 1px solid gray;
        border-radius: 10px;
        background-color: rgb(231, 172, 255);
    }
    """

    btn_tg_stop = """
    {
        border: 1px solid gray;
        border-radius: 10px;
        background-color: rgb(191, 255, 94);
    }
    """
    
    @classmethod
    def active_text(cls, is_active, text_active=None):
        color = 'green' if is_active else '#804452'
        if not text_active:
            text = 'Бот активен!' if is_active else 'Бот неактивен'
        else:
            text = text_active
        return f'<html><head/><body><p><span style=" font-size:10pt; font-style:italic; color:{color};">{text}</span></p></body></html>'

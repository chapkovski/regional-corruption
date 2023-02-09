from otree.api import *


class Constants(BaseConstants):
    name_in_url = 'polar'
    players_per_group = None
    num_rounds = 1
    statement_lgbt = 'Представители ЛГБТ должны иметь такие же права на заключение брака, как и люди гетеросексуальной ориентации.'
    privacy_note = 'ВНИМАНИЕ: <b>Только вы</b> можете видеть ответ участника Б на этот вопрос. Участник Б не имеет возможности посмотреть ваши ответы на какие-либо вопросы. '
    ERR_MSG = 'Пожалуйста, перечитайте инструкции и попробуйте еще раз!'
    CQ_EGO_LABEL = 'Your bonus  (in cents):'
    CQ_ALTER_LABEL = 'Their bonus  (in cents):'
    BASIC_ENDOWMENT = 50
    EXTRA_ENDOWMENT = 50
    DICTATOR_ENDOWMENT = BASIC_ENDOWMENT + EXTRA_ENDOWMENT
    belief_bonus = 25
    formatted_belief_bonus = f'{(belief_bonus / 100):.2f}$'
    agreement_question = 'Согласны ли вы или не согласны со следующим утверждением?'
    NEXT_BTN = 'Далее'
    REQUIRED_MSG = 'Ответьте на вопрос'
    MAX_CQ_ATTEMPTS = 4
    formatter = lambda  x: 'раз' if x in [0] or x> 5 else 'раза'
    MAX_CQ_ATTEMPTS_formatted = f'{MAX_CQ_ATTEMPTS} {formatter(MAX_CQ_ATTEMPTS)}'

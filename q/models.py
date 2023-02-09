from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)
from .choices import choices

author = ' Authors: Chapkovski, Mozolyuk. HSE-Moscow.'

doc = """
Post experimental questionnaire for the interregional project.
"""


class Constants(BaseConstants):
    name_in_url = 'q'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # projection of cgtg into one data
    arkh_cg_belief = models.IntegerField()
    msk_cg_belief = models.IntegerField()
    voronezh_cg_belief = models.IntegerField()
    arkh_tg_decision = models.IntegerField()
    msk_tg_decision = models.IntegerField()
    voronezh_tg_decision = models.IntegerField()

    # some technical stuff
    dump_session_vars = models.LongStringField()
    dump_session_config = models.LongStringField()
    dump_participant_vars = models.LongStringField()
    payable = models.BooleanField()
    # time trackers block
    time_on_study = models.FloatField()
    time_on_survey = models.FloatField()
    time_total = models.FloatField()
    # time trackers block END
    # knowledge block
    knowledge_arkhangelsk_live_in = models.BooleanField()
    knowledge_arkhangelsk_family = models.BooleanField()
    knowledge_arkhangelsk_press = models.BooleanField()
    knowledge_arkhangelsk_network = models.BooleanField()
    knowledge_arkhangelsk_other = models.BooleanField()
    knowledge_arkhangelsk_none = models.BooleanField()
    knowledge_moscow_live_in = models.BooleanField()
    knowledge_moscow_family = models.BooleanField()
    knowledge_moscow_press = models.BooleanField()
    knowledge_moscow_network = models.BooleanField()
    knowledge_moscow_other = models.BooleanField()
    knowledge_moscow_none = models.BooleanField()
    knowledge_voronezh_live_in = models.BooleanField()
    knowledge_voronezh_family = models.BooleanField()
    knowledge_voronezh_press = models.BooleanField()
    knowledge_voronezh_network = models.BooleanField()
    knowledge_voronezh_other = models.BooleanField()
    knowledge_voronezh_none = models.BooleanField()
    # end of knowledge block
    #     WVS corruption block
    wvs_q112 = models.IntegerField()
    wvs_q118 = models.IntegerField()
    wvs_q120 = models.IntegerField()
    # WVS justifiability block
    wvs_q177 = models.IntegerField()
    wvs_q178 = models.IntegerField()
    wvs_q179 = models.IntegerField()
    wvs_q180 = models.IntegerField()
    wvs_q181 = models.IntegerField()

    # general risk, trust, political, religion
    general_risk = models.IntegerField(label='Укажите, пожалуйста, насколько Вы в целом любите рисковать', )
    general_trust = models.IntegerField(label="""
    Если говорить в целом, Вы считаете, что большинству людей можно доверять или нужно быть очень
    осторожными в отношениях с людьми?""", choices=choices.TRUST_CHOICES)
    religion = models.IntegerField(label="""
          Насколько сильно вы верите в существование Бога? (укажите свой ответ в диапазоне от 1 = совсем нет до 5 = очень сильно)
          """, choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    political = models.IntegerField(label="""
          Ниже представлена 7-балльная шкала, на которой политические взгляды, которых могут придерживаться люди, расположены от крайне либеральных (слева) до крайне консервативных (справа). Куда бы вы поставили себя на этой шкале?
          """, choices=range(0, 8), widget=widgets.RadioSelectHorizontal)
    # DEMOGRAPHICS
    age = models.IntegerField(label='Укажите ваш возраст:', choices=choices.AGE_CHOICES, widget=widgets.RadioSelect)
    education = models.IntegerField(
        label="Какой самый высокий уровень школы вы закончили или какую высшую степень вы получили?",
        choices=choices.EDUCATION_CHOICES, widget=widgets.RadioSelect)
    gender = models.IntegerField(label='Укажите ваш пол:',
                                 choices=choices.GENDER_CHOICES, widget=widgets.RadioSelect)
    marital = models.IntegerField(label='В настоящий момент вы:',
                                  choices=choices.MARITAL_CHOICES, widget=widgets.RadioSelect)
    employment = models.IntegerField(label='В настоящий момент вы:',
                                     choices=choices.EMPLOYMENT_CHOICES, widget=widgets.RadioSelect)
    income = models.IntegerField(
        label="Какое высказывание наиболее точно описывает финансовое положение вашей семьи?",
        choices=choices.INCOME_CHOICES,
        widget=widgets.RadioSelect()
    )
    # Demand and clarity
    demand = models.LongStringField()
    instructions_clarity = models.IntegerField(label="""
       Насколько понятными и ясными были для вас инструкции? (укажите свой ответ в диапазоне от 1 = совсем непонятны до 5 = абсолютно понятны)
       """, choices=range(1, 6), widget=widgets.RadioSelectHorizontal)

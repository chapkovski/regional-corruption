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
from markdown import markdown

import itertools
import yaml
import json
import random
from pprint import pprint
from django.db import models as djmodels

author = ' Authors: Chapkovski, Mozolyuk. HSE-Moscow.'

doc = """
Cheating game and trust game together for the interregional project.
"""


def shuffler(params):
    c = params.copy()
    random.shuffle(c)
    return c


def gen_info(player):
    """generate infos to show"""
    res = []
    params = player.participant.vars.get('params')
    regions = player.participant.vars.get('regions')
    region_names = [r.get('name') for r in regions]
    for r_position, region in enumerate(regions):
        regionname = region.get('name')
        values = region.get('values')
        for i_position, p in enumerate(params):
            t = dict(owner=player,
                     region=regionname,
                     region_position=r_position,
                     name=p.get('name'),
                     info_label=p.get('title'),
                     info_description=p.get('description'),
                     info_position=i_position,
                     value=values.get(p.get('name'))
                     )

            info_obj = Info(**t)
            res.append(info_obj)
    return dict(regions=region_names, infos=res, params=params)


class Constants(BaseConstants):
    name_in_url = 'cgtg'
    players_per_group = None
    num_rounds = 2
    apps = ['cg', 'tg']
    tg_coef = 3
    tg_endowment = 1
    tg_endowment_curr = c(tg_endowment)
    tg_endowment_cents = tg_endowment * 100
    tg_full = tg_coef * tg_endowment
    bonus_for_cg_belief = c(1)
    TRUST_CHOICES = [(0, '0$'), (tg_endowment, f'{tg_endowment}$')]
    TG_BELIEF_CHOICES = [(i / 10, f'{i / 10}$') for i in range(0, tg_full * 10, 1)]
    MAX_CQ_ATTEMPTS = 4
    ERR_MSG = 'Пожалуйста, перечитайте инструкции и попробуйте еще раз!'
    formatter = lambda x: 'раз' if x in [0] or x > 5 else 'раза'
    MAX_CQ_ATTEMPTS_formatted = f'{MAX_CQ_ATTEMPTS} {formatter(MAX_CQ_ATTEMPTS)}'
    expected_time = '20  минут'
    head_bonus = c(1)
    cg_belief_bonus = c(1)
    treatment_infos = dict(fic=['corruption', 'grp', 'pop_age', 'cpi'],
                           fin=['grp', 'pop_age', 'cpi'])
    cqbeliefchoices = [(0, '0$'),
                       (1, f'{cg_belief_bonus * 1}'),
                       (2, f'{cg_belief_bonus * 2}'),
                       (3, f'{cg_belief_bonus * 3}'),
                       ]
    cq_tg_choices = [(0, '0$'),
                     (1, '100 центов (1,00$)'),
                     (2, '150 центов (1,50$)'),
                     (3, '300 центов (3,00$)'),
                     ]
    reg_correspondence = {
        'Архангельская область': 'arkh',
        'Москва': 'msk',
        'Воронежская область': 'voronezh'
    }
    correct_cg_answers = dict(
        cq_cg_belief_1=3,
        cq_cg_belief_2=1,
        cq_cg_belief_3=0,
        cq_cg_belief_4=2,
        cq_cg_belief_solo_1=1,
        cq_cg_belief_solo_2=0,
    )
    correct_tg_answers = dict(
        cq_tg_1=2,
        cq_tg_2=0,
        cq_tg_3=1,
    )
    with open(r'./data/regions.yaml', encoding='utf-8') as file:
        regions = yaml.load(file, Loader=yaml.FullLoader)
    with open(r'./data/params.yaml', encoding='utf-8') as file:
        params = yaml.load(file, Loader=yaml.FullLoader)
        for i, j in enumerate(params):
            params[i]['description'] = markdown(j.get('description'))


class Subsession(BaseSubsession):
    treatment = models.StringField()
    solo = models.BooleanField()

    def get_cg_belief_bonus(self):
        return Constants.cg_belief_bonus

    def get_head_bonus(self):
        return Constants.head_bonus

    def creating_session(self):
        self.treatment = self.session.config.get('name')
        self.solo = self.treatment == 'return'
        apps = itertools.cycle([Constants.apps.copy(), list(reversed(Constants.apps.copy()))])
        if self.round_number == 1:
            for p in self.session.get_participants():
                p.vars['payable_round'] = random.randint(1, Constants.num_rounds)
                p.vars['regions'] = shuffler(Constants.regions)
                p.vars['params'] = shuffler(Constants.params)
                if self.treatment == 'return':
                    p.vars['appseq'] = Constants.apps.copy()
                else:
                    if self.session.config.get('randomizing_apps', True):
                        p.vars['appseq'] = next(apps)
                    else:
                        p.vars['appseq'] = Constants.apps.copy()
        infos = []
        for p in self.get_players():
            p.payable_round = p.round_number == p.participant.vars.get('payable_round')
            p.app = p.participant.vars['appseq'][p.round_number - 1]
            info = gen_info(p)
            infos.extend(info.get('infos'))
            p.r1_name, p.r2_name, p.r3_name = info.get('regions')

        Info.objects.bulk_create(infos)
        if self.treatment in ['fic', 'fin']:
            infos = Constants.treatment_infos[self.treatment]
            infos_to_update = Info.objects.filter(owner__subsession=self, name__in=infos)
            infos_to_update.update(to_show=True)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    def role(self):
        if self.subsession.treatment == 'return':
            return 'Б'
        else:
            return 'A'

    def get_regions(self):
        return [self.r1_name, self.r2_name, self.r3_name]

    def get_regional_data(self):
        regs = self.infos.filter(to_show=True).order_by('region_position', 'info_position')
        res = []
        for r in self.get_regions():
            t = dict(name=r, info=regs.filter(region=r).values())
            res.append(t)
        return res

    payable_round = models.BooleanField()
    app = models.StringField()
    cg_decision = models.BooleanField(label='У вас выпало:', )

    def cg_decision_choices(self):
        choices = [(False, 'Решка'), (True, 'Орел')]
        random.shuffle(choices)
        return choices

    def info_descriptions(self):
        r1 = self.infos.filter(to_show=True).order_by('region_position').first().region
        infos = self.infos.filter(to_show=True, region=r1).order_by('info_position')
        return infos

    r1_name = models.StringField()
    r2_name = models.StringField()
    r3_name = models.StringField()
    cg_estimate = models.IntegerField(min=0, max=100)
    r1_cg_estimate = models.IntegerField(min=0, max=100)
    r2_cg_estimate = models.IntegerField(min=0, max=100)
    r3_cg_estimate = models.IntegerField(min=0, max=100)
    r1_trust = models.IntegerField(min=0, max=Constants.tg_endowment_cents)
    r2_trust = models.IntegerField(min=0, max=Constants.tg_endowment_cents)
    r3_trust = models.IntegerField(min=0, max=Constants.tg_endowment_cents)
    trust_return = models.IntegerField(min=0, max=100,
                                       label='Какую долю (от 0% до 100%) из того, что вам пошлет участник А, вы вернете ему назад?')

    confirm_time = models.BooleanField(widget=widgets.CheckboxInput,
                                       label='Я понимаю, что расчет бонусов может занять вплоть до нескольких рабочих дней')
    confirm_block = models.BooleanField(widget=widgets.CheckboxInput,
                                        label=f'Я понимаю, что если я не смогу ответить на проверочные вопросы более чем {Constants.MAX_CQ_ATTEMPTS_formatted}, то не смогу принять дальнейшее участие в исследовании.')
    # comprehension check
    blocked = models.BooleanField(initial=False)
    cq_cg_err_counter = models.IntegerField(initial=0)
    cq_cg_belief_solo_1 = models.IntegerField(
        label='Если  50 человек из 100, принимающих участие в исследовании, назвали "Орел",  а ваша оценка была 60, какой дополнительный бонус за эту оценку вы получите?',
        choices=Constants.cqbeliefchoices, widget=widgets.RadioSelect)
    cq_cg_belief_solo_2 = models.IntegerField(
        label='Если 70 человек из 100, принимающих участие в исследовании, назвали "Орел",  а ваша оценка была 55, какой дополнительный бонус за эту оценку вы получите?',
        choices=Constants.cqbeliefchoices, widget=widgets.RadioSelect)
    cq_cg_belief_1 = models.IntegerField(
        label='Если вы верно (+/-10 единиц) угадаете, сколько людей назовут "Орел" в каждом из трех регионов, какой будет ваш суммарный дополнительный бонус за эти вопросы?',
        choices=Constants.cqbeliefchoices, widget=widgets.RadioSelect)
    cq_cg_belief_2 = models.IntegerField(
        label='Если в регионе X 50 из 100 человек, принимающих участие в исследовании, назвали "Орел",  а ваша оценка про этот регион была 60, какой дополнительный бонус за эту оценку вы получите?',
        choices=Constants.cqbeliefchoices, widget=widgets.RadioSelect)
    cq_cg_belief_3 = models.IntegerField(
        label='Если в регионе X 70 из 100 человек, принимающих участие в исследовании, назвали "Орел",  а ваша оценка про этот регион была 55, какой дополнительный бонус за эту оценку вы получите?',
        choices=Constants.cqbeliefchoices, widget=widgets.RadioSelect)
    cq_cg_belief_4 = models.IntegerField(
        label='Допустим,  вы верно (+/-10 единиц) угадали, сколько людей назовут "Орел" в 2 из 3 регионов, а в третьем регионе ваша оценка отличается больше, чем на 10 единиц. Какой будет ваш суммарный дополнительный бонус за эти вопросы?',
        choices=Constants.cqbeliefchoices, widget=widgets.RadioSelect)
    tg_err_counter = models.IntegerField(initial=0)
    cq_tg_1 = models.IntegerField(
        label='Если участник А пошлет всю начальную сумму (100 центов) участнику Б, а тот из умноженной на 3 суммы (300 центов) пошлет назад 150 центов, какой будет бонус участника А?',
        choices=Constants.cq_tg_choices, widget=widgets.RadioSelect
    )
    cq_tg_2 = models.IntegerField(
        label='Если участник А пошлет всю начальную сумму (100 центов) участнику Б, а тот из умноженной на 3 суммы (300 центов) ничего не пошлет назад, какой будет бонус участника А?',
        choices=Constants.cq_tg_choices, widget=widgets.RadioSelect
    )
    cq_tg_3 = models.IntegerField(
        label='Если участник А ничего не пошлет из начальной суммы (100 центов) участнику Б, какой будет бонус участника А?',
        choices=Constants.cq_tg_choices, widget=widgets.RadioSelect
    )
    # user agent block
    useragent_is_mobile = models.BooleanField()
    useragent_is_bot = models.BooleanField()
    useragent_browser_family = models.StringField()
    useragent_os_family = models.StringField()
    useragent_device_family = models.StringField()
    # user agent block END
    # time trackers
    time_on_cg_belief_decision = models.FloatField()
    time_on_cg_belief_quiz = models.FloatField()
    time_on_tg_decision = models.FloatField()
    time_on_tg_quiz = models.FloatField()

    # time trackers END
    def cq_cg_belief_solo_1_error_message(self, value):
        if value != Constants.correct_cg_answers['cq_cg_belief_solo_1']:
            return Constants.ERR_MSG

    def cq_cg_belief_solo_2_error_message(self, value):
        if value != Constants.correct_cg_answers['cq_cg_belief_solo_2']:
            return Constants.ERR_MSG

    def cq_cg_belief_1_error_message(self, value):
        if value != Constants.correct_cg_answers['cq_cg_belief_1']:
            return Constants.ERR_MSG

    def cq_cg_belief_2_error_message(self, value):
        if value != Constants.correct_cg_answers['cq_cg_belief_2']:
            return Constants.ERR_MSG

    def cq_cg_belief_3_error_message(self, value):
        if value != Constants.correct_cg_answers['cq_cg_belief_3']:
            return Constants.ERR_MSG

    def cq_cg_belief_4_error_message(self, value):
        if value != Constants.correct_cg_answers['cq_cg_belief_4']:
            return Constants.ERR_MSG

    def cq_tg_1_error_message(self, value):
        if value != Constants.correct_tg_answers['cq_tg_1']:
            return Constants.ERR_MSG

    def cq_tg_2_error_message(self, value):
        if value != Constants.correct_tg_answers['cq_tg_2']:
            return Constants.ERR_MSG

    def cq_tg_3_error_message(self, value):
        if value != Constants.correct_tg_answers['cq_tg_3']:
            return Constants.ERR_MSG


class Info(djmodels.Model):
    owner = djmodels.ForeignKey(to=Player, on_delete=djmodels.CASCADE, related_name="infos")
    region = models.StringField()
    region_position = models.IntegerField()
    name = models.StringField()
    info_position = models.IntegerField()
    info_label = models.StringField()
    info_description = models.StringField()
    value = models.FloatField()
    to_show = models.BooleanField()

from otree.api import Currency as c, currency_range
from ._builtin import Page as oTreePage, WaitPage
from .models import Constants
import json
import logging
from django.utils import timezone
from otree.currency import Currency, RealWorldCurrency
from datetime import datetime, date


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Currency, RealWorldCurrency)):
            if obj.get_num_decimal_places() == 0:
                return int(obj)
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)


class Page(oTreePage):
    instructions = False

    def _is_displayed(self):
        return not self.participant.vars.get('blocked') and self.is_displayed()

    def get_context_data(self, **context):
        r = super().get_context_data(**context)
        r['maxpages'] = self.participant._max_page_index
        r['page_index'] = self._index_in_pages
        r['progress'] = f'{int(self._index_in_pages / self.participant._max_page_index * 100):d}'
        r['instructions'] = self.instructions
        return r


class Demand(Page):
    def get(self):
        self.participant.vars.setdefault('survey_start_time', timezone.now())
        if self.player.time_on_study is None:
            study_start_time = self.participant.vars.get('study_start_time', timezone.now())
            self.player.time_on_study = (timezone.now() - study_start_time).total_seconds()
        return super().get()

    form_model = 'player'
    form_fields = ["demand", 'instructions_clarity']

    def before_next_page(self):
        if self.participant.vars.get('region_cg_beliefs'):
            for k, v in self.participant.vars.get('region_cg_beliefs').items():
                setattr(self.player, f'{k}_cg_belief', v)
        if self.participant.vars.get('region_tg_decisions'):
            for k, v in self.participant.vars.get('region_tg_decisions').items():
                setattr(self.player, f'{k}_tg_decision', v)


class Risk(Page):
    def post(self):
        data = json.loads(self.request.POST.get('surveyholder')).get('risk')
        if data:
            for k, v in data.items():
                setattr(self.player, k, v.get('col1'))
        return super().post()


class RegionKnowledge(Page):

    def post(self):
        data = json.loads(self.request.POST.get('surveyholder')).get('region_knowledge')

        if data:
            for k, v in data.items():
                fs = v.get('col1')
                for f in fs:
                    full_field = f'knowledge_{k}_{f}'
                    setattr(self.player, full_field, True)
        return super().post()


class WVSCorr(Page):
    def post(self):
        data = json.loads(self.request.POST.get('surveyholder'))
        if data:
            for k, v in data.items():
                setattr(self.player, k, v)
        return super().post()


class WVSJustifiability(Page):
    def post(self):
        data = json.loads(self.request.POST.get('surveyholder')).get('wvs_just')

        if data:
            for k, v in data.items():
                setattr(self.player, k, v.get('just'))
        return super().post()


class TrustNRisk(Page):

    def post(self):
        data = json.loads(self.request.POST.get('surveyholder'))
        print(data)
        if data:
            for k, v in data.items():
                setattr(self.player, k, v)
        return super().post()


class Demographics(Page):
    form_model = 'player'
    form_fields = [
        "age",
        "education",
        "gender",
        "marital",
        "employment",
        "income",
    ]

    def before_next_page(self):
        self.player.dump_session_vars = json.dumps(self.session.vars, cls=MyEncoder)
        self.player.dump_session_config = json.dumps(self.session.config, cls=MyEncoder)
        pvars = self.participant.vars.copy()
        pvars.pop('regions')
        pvars.pop('params')
        self.player.dump_participant_vars = json.dumps(pvars, cls=MyEncoder)
        self.player.payable = True
        self.participant.vars['payable_status'] = True
        total_start_time = self.participant.vars.get('study_start_time', timezone.now())
        survey_start_time = self.participant.vars['survey_start_time']
        self.player.time_total = (timezone.now() - total_start_time).total_seconds()
        self.player.time_on_survey = (timezone.now() - survey_start_time).total_seconds()


class FinalForToloka(Page):
    def is_displayed(self):
        return self.player.session.config.get('for_toloka') and not self.participant.vars.get('blocked')


page_sequence = [
    Demand,
    RegionKnowledge,
    WVSCorr,
    WVSJustifiability,
    TrustNRisk,
    Demographics,
    FinalForToloka,
]

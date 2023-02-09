from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from otree.models import Participant
from .models import Info
from otree.models import Session
from django.shortcuts import redirect, reverse
import pandas as pd




from django.utils import timezone

class PandasExport(View):
    display_name = 'Decisions export'
    url_name = 'export_decisions'
    url_pattern = fr'decisions/export'
    content_type = 'text/csv'

    def get(self, request, *args, **kwargs):
        events = Info.objects.all().values('owner__participant__code', 'owner__session__code', 'owner__round_number',
                                            'region', 'region_position', 'name', 'info_position', 'value', 'to_show'
                                            )
        df = pd.DataFrame(data=events)
        if df is not None and not df.empty:
            timestamp = timezone.now()
            curtime= timestamp.strftime('%m_%d_%Y_%H_%M_%S')
            csv_data = df.to_csv(  index=False)
            response = HttpResponse(csv_data, content_type=self.content_type)
            filename = f'decisions_{curtime}.csv'
            response['Content-Disposition'] = f'attachment; filename={filename}'
            return response
        else:
            return redirect(reverse('ExportIndex'))

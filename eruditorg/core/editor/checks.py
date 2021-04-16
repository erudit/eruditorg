from django.core.checks import Error, register

from .models import ProductionTeam


@register()
def check_production_team_exists(app_configs, **kwargs):
    errors = []
    if not ProductionTeam.objects.count():
        errors.append(
            Error(
                "There is no production team.",
                hint="You need to add a production team.",
                id="core.editor.no_production_team",
            )
        )
    return errors

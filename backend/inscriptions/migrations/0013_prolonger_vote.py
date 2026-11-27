from datetime import datetime, timezone as dt_timezone

from django.db import migrations
from django.utils import timezone

NOUVELLE_FIN = datetime(2026, 11, 28, 20, 0, tzinfo=dt_timezone.utc)
DEBUT_DEFAUT = datetime(2026, 11, 26, 8, 0, tzinfo=dt_timezone.utc)


def _aware(dt):
    return timezone.make_aware(dt, dt_timezone.utc) if timezone.is_naive(dt) else dt


def prolonger_si_horaires_en_base(apps, schema_editor):
    """Prolonge au 28 nov. 20h uniquement si un enregistrement HorairesVote existait déjà en base."""
    HorairesVote = apps.get_model("inscriptions", "HorairesVote")
    ModificationHorairesVote = apps.get_model("inscriptions", "ModificationHorairesVote")
    h = HorairesVote.objects.filter(id=1).first()
    if not h or not h.fin:
        return
    fin_avant = _aware(h.fin)
    if fin_avant >= NOUVELLE_FIN:
        return
    debut_avant = _aware(h.debut) if h.debut else DEBUT_DEFAUT
    h.fin = NOUVELLE_FIN
    h.save()
    ModificationHorairesVote.objects.create(
        par="commission",
        motif="Prolongation du scrutin jusqu'au samedi 28 novembre 2026 à 20h00.",
        debut_avant=debut_avant,
        fin_avant=fin_avant,
        debut_apres=debut_avant,
        fin_apres=NOUVELLE_FIN,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("inscriptions", "0012_bulletin_nominatif"),
    ]

    operations = [
        migrations.RunPython(prolonger_si_horaires_en_base, migrations.RunPython.noop),
    ]

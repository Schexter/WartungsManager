# Models Package für WartungsManager
# Alle Datenbank-Models werden hier importiert

from .fuelling import Fuellvorgang
from .maintenance import Wartung  
from .protocol import Handbefuellung
from .users import User, create_default_users

# Neue Kompressor-System Modelle
from .kompressor import KompressorBetrieb
from .kunden import Kunde
from .flaschen import Flasche
from .warteliste import WartelisteEintrag
from .bulk_fuelling import BulkFuellvorgang, FlascheFuellvorgang
from .wartungsintervall import Wartungsintervall
from .patronenwechsel import Patronenwechsel, PatronenwechselKonfiguration
from .patrone_erweitert import PatroneVorbereitung, PatroneEinkauf, PatroneWechselProtokoll
from .print_jobs import PrintJob, PrinterKonfiguration
# Temporär auskommentiert wegen Import-Problem:
# from .print_jobs import PrinterStatus

# Füllmanager Modelle
from .fuellmanager import FuellManager, FuellManagerSignatur, FuellVorgangErweitert, GasPreisKonfiguration

__all__ = [
    'Fuellvorgang',
    'Wartung', 
    'Handbefuellung',
    'User',
    'create_default_users',
    # Neue Modelle
    'KompressorBetrieb',
    'Kunde',
    'Flasche',
    'WartelisteEintrag',
    'BulkFuellvorgang',
    'FlascheFuellvorgang',
    'Wartungsintervall',
    'Patronenwechsel',
    'PatronenwechselKonfiguration',
    'PatroneVorbereitung',
    'PatroneEinkauf',
    'PatroneWechselProtokoll',
    # 62mm Drucker Integration
    'PrintJob',
    'PrinterKonfiguration',
    # 'PrinterStatus'  # Temporär entfernt
    # Füllmanager
    'FuellManager',
    'FuellManagerSignatur',
    'FuellVorgangErweitert',
    'GasPreisKonfiguration'
]

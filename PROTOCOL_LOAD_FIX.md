# Protocol Activation Fix - Complete Analysis

## Probleem Analyse

### Symptoom

Na het inladen van een state.json bestand toonde het programma "Active Protocol: GUI" ondanks dat de geladen configuratie een PLC protocol bevatte (bijv. "PLC S7-1500/1200/400/300/ET 200SP").

### Root Cause (Grondig Geanalyseerd)

#### Normale Flow bij Opstarten:

1. **Gebruiker selecteert protocol** via dropdown → `on_controller_changed()` aangeroepen
   - Config wordt geüpdatet: `mainConfig.plcProtocol = "PLC S7-1500/..."`
   - UI wordt aangepast (connect button enabled)
   - **GEEN protocol instantie wordt gecreëerd**

2. **Gebruiker klikt Connect button** → `on_connect_toggled()` aangeroepen
   - Zet vlag: `mainConfig.tryConnect = True`
   - **GEEN protocol instantie wordt gecreëerd**

3. **Main loop detecteert tryConnect flag** (main.py regel 146)
   - Roept `protocolManager.initialize_and_connect()` aan
   - **DIT bouwt en activeert de protocol instantie!**
   - Steps:
     ```python
     protocol_instance = protocol_manager.build_protocol_from_config(config)
     protocol_manager.activate_protocol(protocol_name, protocol_instance)
     protocol_manager.connect()
     ```

#### Probleem met Originele Load Flow:

De `_activate_protocol_after_load()` functie deed:

- ✓ Config laden
- ✓ UI synchroniseren (dropdown, IP adres, buttons)
- ✗ **GEEN protocol instantie bouwen**
- ✗ **GEEN protocol activeren in protocolManager**

**Resultaat:** protocolManager bleef leeg of had oude protocol → "Active Protocol: GUI" werd getoond

## Oplossing - Volledige Protocol Activatie

### Nieuwe `_activate_protocol_after_load()` Functie

De functie repliceert nu **EXACT** wat gebeurt bij normale opstarten:

```python
def _activate_protocol_after_load(main_window):
    # STEP 1: Sync dropdown UI
    # STEP 2: Disconnect oude connectie (indien actief)
    # STEP 3: Deactivate oude protocol in protocolManager ← NIEUW!
    config.protocolManager.deactivate()

    # STEP 4: Configure UI (enable/disable buttons)

    # STEP 5: BUILD AND ACTIVATE PROTOCOL ← KRITIEKE FIX!
    protocol_instance = protocol_manager.build_protocol_from_config(config)
    protocol_manager.activate_protocol(protocol_name, protocol_instance)

    # STEP 6-8: Update IP, labels, vat_widget
```

### Waarom Deze Fix Werkt

#### Wat `build_protocol_from_config()` doet:

```python
# Voor PLC S7:
from IO.protocols.plcS7 import plcS7
return plcS7(config.plcIpAdress, config.plcRack, config.plcSlot, network_adapter)

# Voor Logo:
from IO.protocols.logoS7 import logoS7
return logoS7(config.plcIpAdress, config.tsapLogo, config.tsapServer, network_adapter)

# Voor PLCSim API:
from IO.protocols.PLCSimAPI.PLCSimAPI import plcSimAPI
return plcSimAPI(network_adapter)
```

#### Wat `activate_protocol()` doet:

```python
def activate_protocol(self, protocol_type: str, protocol_instance: Any):
    # Disconnect oude protocol
    if self._active_protocol and self._is_connected:
        self.disconnect()

    # Activeer nieuwe protocol
    self._active_protocol = protocol_instance
    self._protocol_type = protocol_type
    self._is_connected = False

    logger.info(f"Activated protocol: {protocol_type}")
```

## Verificatie van Completeness

### Checklist - Alle Stappen Gedaan?

| Stap                              | Normale Flow (main.py)     | Load Flow (load_save.py)          | Status  |
| --------------------------------- | -------------------------- | --------------------------------- | ------- |
| Config laden                      | `main_config_data` laden   | `load_state()` laden              | ✓       |
| Dropdown sync                     | `on_controller_changed()`  | `_activate_protocol_after_load()` | ✓       |
| Oude connectie verbreken          | `on_controller_changed()`  | `_activate_protocol_after_load()` | ✓       |
| **protocolManager deactivate**    | `initialize_and_connect()` | `_activate_protocol_after_load()` | ✓ NIEUW |
| UI config (buttons)               | `on_controller_changed()`  | `_activate_protocol_after_load()` | ✓       |
| **Protocol instantie bouwen**     | `initialize_and_connect()` | `_activate_protocol_after_load()` | ✓ NIEUW |
| **Protocol activeren in manager** | `initialize_and_connect()` | `_activate_protocol_after_load()` | ✓ NIEUW |
| IP adres updaten                  | `on_controller_changed()`  | `_activate_protocol_after_load()` | ✓       |
| Label updaten                     | `on_controller_changed()`  | `_activate_protocol_after_load()` | ✓       |
| VatWidget updaten                 | `on_controller_changed()`  | `_activate_protocol_after_load()` | ✓       |

### Wat NIET wordt gedaan (opzettelijk):

- **Connectie maken** (`protocol_manager.connect()`) - Dit moet de gebruiker zelf doen via Connect button
- Dit is correct gedrag - state.json slaat NIET op of het systeem geconnecteerd was

## Logging voor Debugging

De functie heeft uitgebreide logging:

```
[LOAD] ========== ACTIVATING PROTOCOL FROM LOADED CONFIG ==========
[LOAD]   Protocol: PLC S7-1500/1200/400/300/ET 200SP, Mode: plc
[LOAD]   Dropdown synced to: PLC S7-1500/1200/400/300/ET 200SP (HIL)
[LOAD]   Disconnected old protocol
[LOAD]   Deactivated old protocol in protocolManager
[LOAD]   Building protocol instance: PLC S7-1500/1200/400/300/ET 200SP
[LOAD]   ✓✓✓ Protocol instance ACTIVATED in protocolManager: PLC S7-1500/...
[LOAD]   PLC mode - connection enabled, protocol instance created
[LOAD]   IP address: 192.168.0.1
[LOAD]   Active method label updated
[LOAD]   VatWidget controller updated
[LOAD] ========== ✓ PROTOCOL ACTIVATION COMPLETE: PLC S7-... ==========
```

## Verwachte Resultaat

Na het inladen van state.json:

1. ✓ **"Active Protocol"** label toont het correcte protocol (bijv. "PLC S7-1500/...")
2. ✓ Dropdown selectie komt overeen met geladen protocol
3. ✓ IP adres is correct ingevuld
4. ✓ Connect button is **enabled** (in PLC mode) of **disabled** (in GUI mode)
5. ✓ Protocol instantie is gebouwd en geactiveerd in `protocolManager`
6. ✓ Gebruiker kan nu op Connect klikken om daadwerkelijk te verbinden
7. ✓ Na Connect werkt IO communicatie correct met het juiste protocol

## Code Locaties

- **Protocol activatie:** `src/core/load_save.py` → `_activate_protocol_after_load()`
- **Protocol manager:** `src/core/protocolManager.py`
- **Main loop connectie:** `src/main.py` regel 146-186
- **Normale protocol selectie:** `src/gui/pages/generalSettings.py` → `on_controller_changed()`

## Testing Checklist

1. [ ] Start applicatie
2. [ ] Selecteer PLC protocol via dropdown
3. [ ] Save state naar JSON
4. [ ] Herstart applicatie
5. [ ] Load state vanuit JSON
6. [ ] Verifieer: "Active Protocol" toont correct protocol
7. [ ] Verifieer: Dropdown selectie klopt
8. [ ] Verifieer: IP adres klopt
9. [ ] Verifieer: Connect button is enabled
10. [ ] Klik Connect
11. [ ] Verifieer: Connectie werkt correct

## Samenvatting

**Voor de fix:**

- Load deed alleen UI sync
- protocolManager bleef leeg
- Active Protocol label toonde "GUI"

**Na de fix:**

- Load doet VOLLEDIGE protocol activatie
- protocolManager bevat correct protocol
- Active Protocol label toont correct protocol
- Exact dezelfde flow als normale opstarten

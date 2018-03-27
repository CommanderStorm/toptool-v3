===== Version 2.0 =====
  * Umgestaltung des Protokoll-Prozesses:
    * Protokolle online mit Etherpad schreiben (derzeit deaktiviert)
    * Nicht-Admins und Nicht-Sitzungsleitungen können sich selbst zum Protokollanten machen (wenn in Sitzungsgruppen-Einstellungen aktiviert). Erst dann können sie das Protokoll schreiben, erstellen, verschicken etc.
    * Neue Seite zum Downloaden der leeren bzw. gefüllten Protokollvorlage
    * Umgestaltung der Seite zum Erstellen des Protokolls
    * Default-Werte für Beginn und Ende der Sitzung beim Protokollerstellen-Formular setzen
  * Persönliche Einstellungen eingeführt:
    * Nutzer können die Farbe des Tools selbst ändern
    * Nutzer können die Reihenfolge der eigenen Sitzungsgruppen in der Kopfzeile und in der Übersicht selbst bearbeiten
  * Änderungen beim iCal-Abo:
    * Link mit UUID für iCal-Abo
    * Einstellung pro Sitzungsgruppe, ob iCal-Abo verwendet werden soll
    * Popup für iCal-Abo mit Möglichkeit zum Kopieren des Links
    * Nur sechs Wochen zurück Sitzungen im iCal-Abo einbinden
    * Persönliches iCal-Abo in Sitzungseinstellungen für alle zum iCal-Abo freigegebenen Sitzungsgruppen (auch mit UUID im Link)
  * Weitere neue Seiten/Funktionen:
    * Interaktive Darstellung der Tagesordnung zum Durchklicken.
    * Nutzer können ihre eigenen TOPs bis zur TOP-Deadline bearbeiten (wenn in Sitzungsgruppen-Einstellungen aktiviert)
    * Neue Seiten zum Bearbeiten und Löschen von Ämtern
    * Neue Seiten zum Anlegen, Bearbeiten und Löschen von Personen (unabhängig von Anwesenheitslisten).
      * Markierung, wenn Personen mehr als 180 Tage nicht verwendet wurden (Datenschutz).
    * Liste aller Sitzungsgruppen-Admins mit E-Mailadressen
  * Neue Einstellungen für Sitzungsgruppen und Gruppierung der Einstellungen nach Themen:
    * Gruppierung der Einstellungen nach Themen (Protokoll, Tagesordnung, Anwesenheitsliste)
      * Einstellungen für Gruppen, die deaktiviert sind, werden ausgeblendet
    * die Termine sollen als iCal-Abo veröffentlicht werden (siehe oben)
    * Anwesenheitsliste verwenden
      * Anwesenheitsliste mit Ämtern verwenden
    * Protokoll verwenden
      * Nicht-Admins können sich selbst zum Protokollanten machen (siehe oben)
      * Syntax für Anträge im Protokoll verwenden
      * Syntax für GO-Anträge im Protokoll verwenden
      * Anhänge zum Protokoll verwenden
    * Tagesordnung verwenden
      * Wer darf TOPs eintragen: Alle (auch öffentlich), alle mit Rechten für die Sitzungsgruppe oder nur Admins
      * Benutzer dürfen ihre eigenen TOPs bearbeiten (siehe oben)
      * TOP-Deadline verwenden
      * Standard-TOPs verwenden
      * TOP "Sonstiges" verwenden
      * Anhänge zu TOPs verwenden
  * Design-Verbesserungen:
    * Neues (übersichtlichers) Design der Sitzungsdetailseite
      * Aktionen zur Bearbeitung der Sitzung und des Protokools jeweils zusammengefasst
      * Aktionen mit Symbolen ergänzt
      * Links um zu TOPs zu springen
      * Einklappen von einzelnen Reitern
    * Buttons statt Dropdown-Menü für die Sprachauswahl
    * Layouts der Buttons an Gesamtlayout angepasst
    * Alle Löschen-Buttons sind rot
    * Buttons unter Formularen sind nicht mehr in Tabellen
    * Design der Tabellen verbessert und responsive gemacht
    * Jahr-Buttons für das Sitzungsarchiv gruppiert und an Layout angepasst
    * Fußzeile an Kopfzeile angepasst
    * Aktuelle Sitzungsgruppe in Kopfzeile stärker hervorheben
    * Links statt Buttons für Aktionen
    * Einheitliche Farbe für Kopf-/Fußzeile, Buttons und Links
    * WYSIWYG-Editor responsive gemacht
    * Aufzählungen durch List-Groups ersetzt.
    * Seite ohne JavaScript nutzbar machen
      * Kopfzeile ausklappen, wenn JavaScript deaktiviert ist
      * Symbole ausblenden, wenn JavaScript deaktiviert ist
  * Kleinere Änderungen:
    * Nach dem Login wird man wieder zur ursprünglichen Seite weitergeleitet
    * Übersichtsseite für Sitzungsgruppen wird übersprungen, wenn man nur Rechte für eine Gruppe hat
    * Markierung von Sitzungen in der Sitzungsübersicht, wenn man Sitzungsleitung oder Protokollant ist
    * Markierung, ob Protokoll schon genehmigt ist
    * Die TOP-Deadline kann auf durch einen Klick auf 1 Stunde bzw. 1 Tag vorher gesetzt werden.
    * Bei einer Sitzungsserie kann die TOP-Deadline auf nichts, jeweils 1 Stunde oder 1 Tag vorher gesetzt werden.
    * Nachricht für anstehende Sitzungen (statt Text in Kopfzeile)
    * Django-Admin verlinken
  * Weitere Bugfixes:
    * Die Fehler mit dem Datetime-Picker wurden behoben.
    * Die fehlerhafte Darstellung von Aufzählungen in der TOP-E-Mail wurde behoben.
    * Überprüfung bei Absendung des Formulars, ob TOP-Deadline nach dem Sitzungsbeginn liegt (genauso für Beginn und Ende von Sitzungen bzw. Sitzungsserien)
    * Nutzer ohne Rechten für eine öffentliche Sitzung können die TOP-Anhänge anschauen
    * Wenn das Generieren des Protokolls fehlschlägt, wird es nicht mehr als verfügbar angezeigt.

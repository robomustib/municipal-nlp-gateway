import spacy
import re
from typing import Dict

class MunicipalDocumentProcessor:
    """
    KI-Prototyp fuer die Stadt Essen: Intelligente Posteingangsverarbeitung.
    Fokus: Quality Gate, Datenextraktion und personalisierte Buergerkommunikation.
    """
    
    def __init__(self, model: str = "de_core_news_lg"):
        try:
            self.nlp = spacy.load(model)
        except OSError:
            print("\n[FEHLER] Bitte laden Sie das Sprachmodell vorab im Terminal:")
            print("pip install spacy")
            print(f"python -m spacy download {model}\n")
            raise

    def classify_intent(self, text: str) -> str:
        text_lower = text.lower()
        if any(word in text_lower for word in ["bauantrag", "baugenehmigung", "statik"]):
            return "FB 61 - Stadtplanung und Bauordnung"
        elif any(word in text_lower for word in ["wohngeld", "miete", "sozialhilfe"]):
            return "FB 50 - Soziales und Wohnen"
        elif any(word in text_lower for word in ["schlagloch", "laterne", "defekt"]):
            return "Ordnungsamt / Maengelmelder"
        return "Allgemeiner Service"

    def get_salutation(self, nlp_doc) -> str:
        """
        Extrahiert den Namen des Absenders fuer eine personalisierte Anrede.
        Greift auf sichere Fallbacks zurueck, falls die Daten unklar sind.
        """
        persons = [ent.text for ent in nlp_doc.ents if ent.label_ == "PER"]
        
        if not persons:
            return "Sehr geehrte(r) Buerger(in)"
        
        # Die letzte im Text genannte Person ist meist der Absender (Signatur)
        sender_name = persons[-1].split()
        
        if len(sender_name) >= 2:
            vorname = sender_name[0]
            nachname = sender_name[-1]
            
            # Simples Dictionary fuer den Prototyp zur Geschlechtserkennung
            weiblich = ["sabine", "anna", "maria", "julia", "susanne", "petra"]
            maennlich = ["thomas", "michael", "christian", "peter", "klaus", "johannes"]
            
            if vorname.lower() in weiblich:
                return f"Sehr geehrte Frau {nachname}"
            elif vorname.lower() in maennlich:
                return f"Sehr geehrter Herr {nachname}"
            else:
                # Fallback: Name ist bekannt, aber Geschlecht unklar
                return f"Guten Tag {vorname} {nachname}"
                
        return "Sehr geehrte(r) Buerger(in)"

    def extract_metadata(self, text: str, nlp_doc) -> Dict:
        az_match = re.search(r"\bAZ-\d{4}-\d{4}\b", text)
        dates_regex = re.findall(r"\b\d{2}\.\d{2}\.\d{4}\b", text)
        money_regex = re.findall(r"\b\d+(?:,\d{2})?\s*(?:Euro|€)\b", text)
        
        return {
            "aktenzeichen": az_match.group(0) if az_match else None,
            "fristen": dates_regex if dates_regex else [ent.text for ent in nlp_doc.ents if ent.label_ == "DATE"],
            "betraege": money_regex if money_regex else [ent.text for ent in nlp_doc.ents if ent.label_ == "MONEY"]
        }

    def process_email(self, sender: str, text: str) -> Dict:
        doc = self.nlp(text)
        fachbereich = self.classify_intent(text)
        metadata = self.extract_metadata(text, doc)
        salutation = self.get_salutation(doc)
        
        missing_data = []
        if not metadata["aktenzeichen"]:
            missing_data.append("Aktenzeichen (Format: AZ-JJJJ-XXXX)")
            
        if fachbereich == "FB 61 - Stadtplanung und Bauordnung" and "statik" not in text.lower() and "anlage" not in text.lower():
            missing_data.append("Geforderte Anlage (z.B. Statik-Nachweis)")

        if missing_data:
            fehlend_str = "\n- ".join(missing_data)
            return {
                "aktion": "QUALITY_GATE_REJECT",
                "output": (
                    f"[PROZESS-METRIK] Fall automatisiert abgefangen. Eingesparte Pruefzeit: ca. 5 Min.\n\n"
                    f"Von: service@essen.de\n"
                    f"An: {sender}\n"
                    f"Betreff: AW: Ihr Anliegen ({fachbereich}) - Unterlagen unvollstaendig\n\n"
                    f"{salutation},\n\n"
                    f"vielen Dank fuer Ihre Nachricht. Um Ihr Anliegen im Bereich '{fachbereich}' \n"
                    f"schnellstmoeglich bearbeiten zu koennen, fehlen uns noch folgende Angaben/Dokumente:\n\n"
                    f"- {fehlend_str}\n\n"
                    f"Bitte reichen Sie diese Informationen als Antwort auf diese E-Mail nach.\n\n"
                    f"Mit freundlichen Gruessen\nIhre digitale Stadtverwaltung Essen"
                )
            }
        else:
            fristen_str = ", ".join(metadata["fristen"]) if metadata["fristen"] else "Keine Fristen erkannt"
            betraege_str = ", ".join(metadata["betraege"]) if metadata["betraege"] else "Keine Betraege erkannt"
            urgency = "HOCH (Frist pruefen!)" if metadata["fristen"] else "Normal"
            
            return {
                "aktion": "ROUTING_SUCCESS",
                "output": (
                    f"==================================================\n"
                    f" SACHBEARBEITER-COCKPIT | NEUER EINGANG\n"
                    f"==================================================\n"
                    f" ZUSTAENDIG:    {fachbereich}\n"
                    f" PRIORITAET:    {urgency}\n"
                    f" SYSTEM-CHECK:  Alle Pflichtangaben vorhanden\n"
                    f"--------------------------------------------------\n"
                    f" ZUSAMMENFASSUNG (EXTRAHIERTE FAKTEN):\n"
                    f" - Aktenzeichen:  {metadata['aktenzeichen']}\n"
                    f" - Fristen/Daten: {fristen_str}\n"
                    f" - Betraege:      {betraege_str}\n"
                    f"=================================================="
                )
            }

if __name__ == "__main__":
    processor = MunicipalDocumentProcessor()
    
    emails = [
        {
            "absender": "sabine.mueller@mail.de",
            "text": "Guten Tag, ich habe vor drei Wochen Wohngeld beantragt. "
                    "Wann kann ich mit einer Auszahlung rechnen? Meine Miete in Hoehe von 650 Euro ist faellig. "
                    "Viele Gruesse aus Essen-Ruettenscheid. Sabine Mueller" 
        },
        {
            "absender": "architekt.schmidt@bau.de",
            "text": "Sehr geehrte Damen und Herren, anbei uebersende ich Informationen zum Bauantrag "
                    "mit dem Aktenzeichen AZ-2026-8871. Die Unterlagen reiche ich spaeter nach. "
                    "Gruss, Thomas Schmidt"
        },
        {
            "absender": "buerger123@web.de",
            "text": "Hallo, auf der Kettwiger Strasse ist ein riesiges Schlagloch, "
                    "das repariert werden muss. Mein Vorgang dazu hat das Aktenzeichen AZ-2026-1004. "
                    "Bitte beheben Sie das bis zum 28.02.2026, da sonst Unfaelle drohen. "
                    "Der Schaden betraegt sicher schon 1500 Euro."
        }
    ]

    print("\n" + "="*70)
    print(" STARTE RPA-SIMULATION: INTELLIGENTER POSTEINGANG (STADT ESSEN) ")
    print("="*70)

    for i, mail in enumerate(emails, 1):
        print(f"\n[EINGANG {i}/3] VON: {mail['absender']}")
        print("\n--- URSPRUENGLICHER FREITEXT (EINGANG) ---")
        print(f"\"{mail['text']}\"")
        print("------------------------------------------\n")
        
        ergebnis = processor.process_email(mail["absender"], mail["text"])
        
        if ergebnis["aktion"] == "QUALITY_GATE_REJECT":
            print("[SYSTEM-CHECK] UNVOLLSTAENDIG. Bearbeitung blockiert.")
            print("[AKTION] Automatische Klaerung mit Buerger initiiert:\n")
            print(ergebnis["output"])
            
        elif ergebnis["aktion"] == "ROUTING_SUCCESS":
            print("[SYSTEM-CHECK] VOLLSTAENDIG. Weiterleitung an Fachbereich.")
            print("[AKTION] Erstelle Daten-Cockpit fuer Sachbearbeitung:\n")
            print(ergebnis["output"])
            
        print("\n" + "-"*70)
        
        if i < len(emails):
            input("\n>>> Druecken Sie [ENTER] fuer das naechste Praxisbeispiel...")

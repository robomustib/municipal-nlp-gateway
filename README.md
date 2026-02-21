# KI-gestützte Posteingangsverarbeitung (RPA/NLP)
Dieser Python-Prototyp demonstriert die intelligente Vorprüfung und Automatisierung unstrukturierter Bürgeranfragen (Dunkelverarbeitung) für Kommunalverwaltungen. 
Im Fokus steht die gezielte Entlastung der Sachbearbeitung durch automatisierte Klärungsprozesse und strukturierte Datenaufbereitung (Augmented Intelligence).
Das Skript nutzt die NLP-Bibliothek spaCy (Modell: de_core_news_lg) in Kombination mit Regulären Ausdrücken (RegEx) für eine robuste und datenschutzkonforme On-Premise-Verarbeitung.

## Kernfunktionen (Module):

1. Intelligentes Routing (Intent Classification): Das System analysiert den Freitext der E-Mail mittels Natural Language Processing (NLP) und leitet das Anliegen automatisch an den korrekten Fachbereich weiter (z. B. FB 50 Soziales, FB 61 Bauordnung, Ordnungsamt).

2. Quality Gate & Personalisierte Auto-Responder: Fehlen pflichtige Metadaten (wie das Aktenzeichen oder fachspezifische Anlagen wie Statik-Nachweise), blockiert das System die Weiterleitung an die Sachbearbeitung. Stattdessen extrahiert die KI den Namen des Absenders aus dem Text (Named Entity Recognition), erkennt das Geschlecht und generiert vollautomatisch eine personalisierte, höfliche Rückfrage an die Bürgerin oder den Bürger, um die fehlenden Daten nachzufordern.

3. Gezielte Datenextraktion (Information Extraction):
Für vollständige Anfragen liest das System entscheidungsrelevante Fakten (Hard Facts) wie Datumsangaben/Fristen und Geldbeträge aus dem Text aus, um Prioritäten (z. B. "Frist prüfen") automatisch zu setzen.

4. Sachbearbeiter-Cockpit:
Die Mitarbeitenden erhalten nicht mehr den unstrukturierten Fließtext, sondern ein aufgeräumtes Daten-Briefing. Dies reduziert die initiale Prüfzeit pro Vorgang drastisch und erhöht die Prozessqualität.

## Flowchart

<img src="https://github.com/robomustib/municipal-nlp-gateway/blob/main/img/flowchart_municipal.svg" alt="Flowchart" width="50%"/>

## Beispiel

<img width="1920" height="1080" alt="grafik" src="https://github.com/user-attachments/assets/acf61ab0-94a2-4d11-8932-66a52c7225bf" />

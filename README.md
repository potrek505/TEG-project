# Projekt TEG - Eksplorator Transakcji z GraphRAG

## 🚀 Przegląd

TEG (Transaction Explorer with GraphRAG) to zaawansowany asystent finansowy AI, który łączy inteligentną analizę transakcji z zaawansowanymi możliwościami RAG (Retrieval-Augmented Generation). System wykorzystuje dynamiczne podejmowanie decyzji oparte na grafach, aby dostarczać spersonalizowane wglądy finansowe i porady oparte na danych transakcyjnych.

![Przepływ Dynamicznego Grafu RAG](./dynamic_rag_graph.png)

*System automatycznie wybiera między lekkimi zapytaniami SQL a kompleksową analizą RAG na podstawie złożoności zapytania*

## 🏗️ Architektura

TEG wykorzystuje architekturę mikrousług z trzema głównymi komponentami:

### 🤖 Serwis AI (`ai/`)
- **Dynamiczny RAG oparty na LangGraph**: Inteligentne kierowanie zapytań na podstawie analizy złożoności
- **Agent SQL**: Bezpośrednie zapytania do bazy danych dla prostych pytań transakcyjnych
- **Adaptacyjny RAG**: Zaawansowane wyszukiwanie dla złożonych zapytań analitycznych
- **Integracja z OpenAI**: GPT-4o-mini do przetwarzania języka naturalnego
- **Magazyn Wektorów FAISS**: Wydajne wyszukiwanie semantyczne

### 🌐 Serwis Backend (`backend/`)
- **API REST Flask**: Czyste interfejs API dla komunikacji z frontendem
- **Zarządzanie Konwersacjami**: Historia czatu oparta na sesjach z SQLite
- **Integracja z Serwisem AI**: Bezproblemowa komunikacja z serwisem AI
- **Trwałość Danych**: Automatyczne logowanie i pobieranie konwersacji

### 🎨 Serwis Frontend (`frontend/`)
- **Interfejs Streamlit**: Nowoczesny, responsywny interfejs webowy
- **Czat w Czasie Rzeczywistym**: Interaktywny interfejs konwersacyjny
- **Zarządzanie Sesjami**: Przeglądanie poprzednich konwersacji i tworzenie nowych sesji
- **Obsługa Wielu Sesji**: Przełączanie między różnymi kontekstami konwersacji

## 🔄 Przepływ Dynamicznego Grafu

System wykorzystuje inteligentny graf decyzyjny, który:

1. **Ocenia Złożoność Zapytania**: Określa, czy zapytanie wymaga prostego SQL czy złożonej analizy
2. **Kieruje Odpowiednio**: 
   - Lekkie zapytania → Bezpośredni Agent SQL
   - Ciężkie zapytania → Tworzy instancję RAG → Zaawansowane wyszukiwanie
3. **Optymalizuje Wydajność**: Unika niepotrzebnych obliczeń dla prostych żądań
4. **Zachowuje Kontekst**: Przechowuje stan sesji między interakcjami

## ✨ Kluczowe Funkcje

- **🧠 Inteligentne Kierowanie Zapytań**: Automatyczny wybór optymalnej strategii przetwarzania
- **💬 Interfejs Konwersacyjny**: Interakcja w języku naturalnym z danymi finansowymi
- **📊 Analiza Transakcji**: Głębokie wglądy w wzorce wydatków i trendy
- **🔍 Wyszukiwanie Semantyczne**: Znajdowanie odpowiednich transakcji w języku naturalnym
- **📈 Porady Finansowe**: Spersonalizowane rekomendacje oparte na danych
- **💾 Zarządzanie Sesjami**: Zapisywanie i ponowne odwiedzanie poprzednich konwersacji
- **🔄 Przetwarzanie w Czasie Rzeczywistym**: Natychmiastowe odpowiedzi na zapytania finansowe
- **🏗️ Projekt Mikrousług**: Skalowalna i łatwa w utrzymaniu architektura

## 🛠️ Stos Technologiczny

### AI i ML
- **LangChain**: Framework dla aplikacji LLM
- **LangGraph**: Orkiestracja przepływów pracy opartych na grafach
- **OpenAI GPT-4o-mini**: Model językowy do przetwarzania języka naturalnego
- **FAISS**: Wyszukiwanie podobieństwa wektorowego
- **SQLite**: Przechowywanie danych transakcyjnych

### Backend
- **Flask**: Framework webowy Python
- **SQLite**: Trwałość konwersacji
- **Requests**: Klient HTTP do komunikacji między serwisami

### Frontend
- **Streamlit**: Framework interaktywnych aplikacji webowych
- **Python**: Podstawowa logika aplikacji

### Infrastruktura
- **Docker**: Konteneryzacja wszystkich serwisów
- **Docker Compose**: Orkiestracja wielu serwisów
- **uv**: Szybkie zarządzanie pakietami Python

## 🚀 Szybki Start

### Wymagania
- Python 3.11+
- Menedżer pakietów uv
- Klucz API OpenAI
- Docker (opcjonalnie, do wdrożenia kontenerowego)

### 1. Klonowanie i Konfiguracja
```bash
git clone <url-repozytorium>
cd TEG-project
cp .env.example .env
# Edytuj .env swoim kluczem API OpenAI
```

### 2. Rozwój Lokalny
```bash
# Uruchom wszystkie serwisy
python main.py

# W innym terminalu, monitoruj logi
python log_manager.py follow
```

### 3. Wdrożenie Docker
```bash
# Zbuduj i uruchom wszystkie serwisy
docker-compose up -d

# Zobacz logi
docker-compose logs -f
```

### 4. Dostęp do Aplikacji
- **Frontend**: http://localhost:8501
- **API Backend**: http://localhost:50000
- **Serwis AI**: http://localhost:50001

## 📁 Struktura Projektu

```
TEG-project/
├── main.py                 # Orkiestrator projektu
├── shared_logging.py       # Scentralizowany system logowania
├── log_manager.py         # Narzędzie zarządzania logami
├── dynamic_rag_graph.png  # Wizualizacja przepływu grafu
├── docker-compose.yml     # Orkiestracja wielu serwisów
├── all_transactions.db    # Przykładowa baza danych transakcji
│
├── ai/                    # Serwis AI
│   ├── app.py            # Serwis AI Flask
│   ├── src/
│   │   ├── agents/       # Agenci SQL i ewaluacyjni
│   │   ├── graphs/       # Implementacja LangGraph
│   │   └── rags/         # Konfiguracje RAG
│   └── Dockerfile
│
├── backend/              # Serwis Backend
│   ├── app.py           # API backend Flask
│   ├── src/
│   │   ├── database.py  # Zarządzanie konwersacjami
│   │   └── call_ai_service.py  # Klient serwisu AI
│   └── Dockerfile
│
├── frontend/            # Serwis Frontend
│   ├── app.py          # Aplikacja Streamlit
│   ├── src/
│   │   ├── ui_components.py  # Komponenty UI
│   │   ├── api_client.py     # Klient backend
│   │   ├── settings.py       # Konfiguracja
│   │   └── session_state.py  # Zarządzanie stanem
│   └── Dockerfile
│
└── logs/               # Scentralizowane logowanie
    ├── main.log       # Logi procesu głównego
    ├── ai.log         # Logi serwisu AI
    ├── backend.log    # Logi serwisu backend
    ├── frontend.log   # Logi serwisu frontend
    ├── combined.log   # Wszystkie serwisy połączone
    └── errors.log     # Tylko logi błędów
```

## 📊 Przykłady Użycia

### Analiza Finansowa
```
"Pokaż mi trendy wydatków z ostatnich 3 miesięcy"
"Jakie są moje największe wydatki w tym roku?"
"Ile wydałem na restauracje?"
```

### Wyszukiwanie Transakcji
```
"Znajdź wszystkie transakcje BLIK"
"Pokaż ostatnie transakcje powyżej 500 PLN"
"Co kupiłem z Amazon w zeszłym miesiącu?"
```

### Porady Finansowe
```
"Jak mogę zmniejszyć swoje miesięczne wydatki?"
"Czy powinienem się martwić moimi wzorcami wydatków?"
"Jaki jest mój średni miesięczny dochód?"
```

## 🔧 Konfiguracja

### Zmienne Środowiskowe
- `OPENAI_API_KEY`: Twój klucz API OpenAI
- `AI_PORT`: Port serwisu AI (domyślnie: 50001)
- `BACKEND_PORT`: Port serwisu backend (domyślnie: 50000)  
- `FRONTEND_PORT`: Port serwisu frontend (domyślnie: 8501)

### Konfiguracja Bazy Danych
- `transactions_db_uri`: URI bazy danych SQLite dla transakcji
- `transactions_db`: Ścieżka do pliku bazy danych

## 📝 System Logowania

Projekt wykorzystuje scentralizowany system logowania z następującymi funkcjami:

### Pliki Logów

Wszystkie logi są przechowywane w katalogu `logs/`:

- `main.log` - Logi orkiestratora głównego
- `ai.log` - Logi serwisu AI  
- `backend.log` - Logi serwisu backend
- `frontend.log` - Logi serwisu frontend
- `combined.log` - Wszystkie serwisy połączone
- `errors.log` - Wszystkie błędy ze wszystkich serwisów

### Zarządzanie Logami

Użyj narzędzia `log_manager.py` do zarządzania logami:

```bash
# Wylistuj wszystkie pliki logów
python log_manager.py list

# Pokaż ostatnie logi ze wszystkich serwisów
python log_manager.py show

# Pokaż ostatnie logi z konkretnego serwisu
python log_manager.py show --service ai

# Pokaż tylko błędy
python log_manager.py show --errors

# Śledź logi w czasie rzeczywistym
python log_manager.py follow

# Śledź logi konkretnego serwisu
python log_manager.py follow --service backend

# Śledź tylko błędy
python log_manager.py follow --errors

# Wyczyść wszystkie pliki logów
python log_manager.py clear
```

### Funkcje

- **Automatyczna Rotacja Logów**: Pliki rotują się przy 10MB z 5 kopiami zapasowymi
- **Wiele Celów Wyjściowych**: Konsola + indywidualne pliki + połączone + błędy
- **Obsługa UTF-8**: Właściwe kodowanie dla znaków międzynarodowych
- **Zmniejszony Szum**: Logi bibliotek zewnętrznych filtrowane na poziom WARNING
- **Szczegółowe Formatowanie**: Zawiera nazwy plików i numery linii

## 🤝 Współpraca

1. Sforkuj repozytorium
2. Utwórz gałąź funkcji
3. Wprowadź swoje zmiany
4. Dodaj testy jeśli to możliwe
5. Zaktualizuj dokumentację
6. Prześlij pull request

## 📄 Licencja

Ten projekt jest licencjonowany na licencji MIT - zobacz plik LICENSE dla szczegółów.

## 🆘 Wsparcie

W przypadku pytań, problemów lub współpracy:
- Sprawdź logi używając `python log_manager.py show --errors`
- Przejrzyj punkty końcowe health API
- Upewnij się, że wszystkie zmienne środowiskowe są poprawnie skonfigurowane

---

**Zbudowane z ❤️ używając Python, LangChain i nowoczesnych technologii AI**

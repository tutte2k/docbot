# **Rapport: MDN DocBot - En AI-baserad dokumentationsassistent**

## **Sammanfattning av lösningen**
MDN DocBot är en AI-baserad webbapplikation utvecklad för att hjälpa utvecklare snabbt hitta relevant dokumentation om webbtekniker som HTML, CSS, JavaScript och Web API. Lösningen använder **semantisk sökning** via embeddings och en **AI-agent** (Ollama med modellen `smollm2:1.7b`) för att generera svar baserat på en vektorbaserad databas (Chroma).

### **Teknisk implementation**
- **Semantisk sökning**: Dokument från MDN (i JSON-format) bearbetas och delas upp i chunkar med `RecursiveCharacterTextSplitter`. Dessa lagras sedan i en vektordatabas (Chroma) med hjälp av `OllamaEmbeddings`.
- **AI-agent**: Användarens frågor jämförs mot databasen via likhetssökning, och den mest relevanta kontexten skickas till en LLM (Ollama) för generering av svar.
- **Användargränssnitt**: Ett enkelt GUI byggt med `customtkinter` och `pywinstyles` för bättre användarupplevelse.

### **Verktyg och bibliotek**
- **Embeddings**: `OllamaEmbeddings` (nomic-embed-text)
- **Vektordatabas**: `Chroma`
- **LLM**: `Ollama` (smollm2:1.7b)
- **Gränssnitt**: `customtkinter`, `Pillow`
- **Prompt Engineering**: Anpassad prompt för att förbättra precisionen i svaren.

## **Reflektion över arbetsprocessen**
### **Utmaningar och lösningar**
1. **Databearbetning**:
   - Stora JSON-filer krävde effektiv chunking och parallell bearbetning för att undvika minnesproblem.
   - Lösning: `ThreadPoolExecutor` användes för att optimera inläsningen.

2. **Semantisk sökning**:
   - Vissa frågor gav irrelevanta resultat på grund av för bred likhetssökning.
   - Förbättring: Finjustering av `chunk_size` och `chunk_overlap` för bättre kontextbevarande.

3. **AI-agentens precision**:
   - Ibland genererade modellen felaktiga svar trots korrekt kontext.
   - Lösning: Prompten optimerades med strikta instruktioner och hot om "bestraffning" för dåliga svar (en humoristisk men effektiv taktik).

### **Etiska överväganden**
- **Datakvalitet**: Endast officiella MDN-dokument användes för att undvika desinformation.
- **Transparens**: Källhänvisningar visas för användaren för att möjliggöra verifiering.
- **Användarinflytande**: Användaren kan se vilka delar av databasen som användes för att generera svaret.

## **Analys och framtida förbättringar**
### **Utvärdering av lösningen**
- **Fördelar**:
  - Snabb och relevant sökning i teknisk dokumentation.
  - Användarvänligt gränssnitt med möjlighet att kopiera svar.
  - Flexibel infrastruktur som kan skalas med fler datakällor.
- **Begränsningar**:
  - Modellen är relativt liten (`1.7B parametrar`), vilket ibland leder till mindre precisa svar.
  - Kräver lokal körning av Ollama, vilket begränsar tillgängligheten.

### **Framtida utveckling**
1. **Förbättrad semantisk sökning**:
   - Integrera fler datakällor (t.ex. Stack Overflow, GitHub-dokumentation).
   - Experimentera med andra embeddings-modeller (t.ex. OpenAI eller Cohere).

2. **Avancerad AI-agent**:
   - Implementera en multi-agent-arkitektur där en agent validerar svaren innan de presenteras.
   - Stöd för fler språk och mer konversationsbaserad interaktion.

3. **Skalbarhet och tillgänglighet**:
   - Webbaserad version med Supabase eller Pinecone för molnlagring.
   - Stöd för fler LLM:er (t.ex. Llama 3, GPT-4-turbo).

4. **Användarfeedback**:
   - Möjlighet för användare att rösta på svar för att förbättra modellen över tid.

# 🎨 FotMob Fixtures Branding Guide

Pentru a avea o iconiță oficială în Home Assistant și HACS, urmează acești pași simpli. Din motive tehnice, nu pot genera fișierele `.png` direct în repository-ul tău, dar iată tot ce ai nevoie:

### 1. Descarcă Iconițele

Alege o imagine reprezentativă (o minge de fotbal verde stilizată). Recomand aceste resurse gratuite care se potrivesc cu stilul FotMob:

- [Mingea de Fotbal Verde (Icons8)](https://icons8.com/icon/82766/soccer-ball) - Descarcă varianta PNG de 512x512.
- [Mingea de Fotbal Verde (Flaticon)](https://www.flaticon.com/free-icon/soccer_861506)

### 2. Redenumește și Pune Fișierele în Root

Salvează fișierul ales de două ori în folderul rădăcină al integrării tale (`custom_components/fotmob_fixtures/`):

- `icon.png` (recomandat 512x512 sau 1024x1024)
- `logo.png` (poate fi același fișier sau unul care conține și textul "FotMob Fixtures")

### 3. Înregistrare Oficială (Fără să clonezi tot repo-ul!)

Deoarece repo-ul `brands` este uriaș, cea mai simplă metodă de a trimite pozele este direct prin interfața GitHub (Web UI):

1. **Mergi la Fork-ul tău**: [Liionboy/brands](https://github.com/Liionboy/brands).
2. **Navighează la folderul corect**: Intră în folderul `custom_integrations`.
3. **Creează folderul tău**:
    - Apasă pe **Add file** -> **Create new file**.
    - În căsuța pentru nume, scrie exact: `fotmob_fixtures/placeholder` (scrisul `fotmob_fixtures/` va crea automat folderul).
    - Apasă **Commit changes** (nu contează ce e în fișier, îl ștergem noi după).
4. **Urcă pozele**:
    - Acum că ești în folderul `custom_integrations/fotmob_fixtures/`, apasă pe **Add file** -> **Upload files`.
    - Trage pozele `icon.png` și `logo.png` (cele pe care le-ai pregătit deja).
    - Apasă **Commit changes**.
5. **Creează Pull Request-ul**: După ce ai urcat pozele, GitHub îți va arăta un buton mare verde: **"Compare & pull request"**. Apasă-l și trimite-l către Home Assistant!

### 4. Actualizare GitHub local (Opțional)

Dacă vrei să păstrezi fișierele și în codul tău local:

```bash
git add icon.png logo.png
git commit -m "Add branding assets"
git push origin main
```

Odată ce aceste fișiere sunt pe GitHub, HACS va începe să le folosească în paginile de prezentare a repository-ului! ⚽🚀
